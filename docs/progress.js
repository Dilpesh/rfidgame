/* progress.js — a story that survives leaving the app.
 *
 * The bug this fixes: a phone answering a call, opening WhatsApp, or simply
 * being idle will throw a background tab away. These pages are 13-15 MB, so
 * Android is quick about it. Coming back reloads the page from scratch and
 * nothing in any game remembered where the child had got to — nine minutes in,
 * back to "Start". InterruptGuard cannot help: by then the page is gone.
 *
 * So the step is written to localStorage as it changes, and on the next load
 * the grown-up is offered the choice: carry on, or start again. Nothing is
 * restored silently — a child who has finished and wants it again must not be
 * dropped back at stop eight.
 *
 * Progress.track({
 *   key       'moon'            storage key, one per story
 *   total     9                 number of steps
 *   at()      -> 4 | null       current step, or null when no story is running
 *   label(i)  -> '🔦 TORCH'     what to call step i on the button
 *   resume(i) -> puts the story back at step i; may be async. Runs from a tap,
 *                so audio may be started here.
 * })
 *
 * at() is the whole contract: while it returns a number the story is running
 * and gets saved; the moment it returns null after running, the story has
 * ended (finished or reset) and the save is dropped. A page that is discarded
 * never reaches that moment, which is exactly why its save survives.
 */
window.Progress = (function () {
  const KEY = (k) => 'kahani:progress:' + k;
  const MAX_AGE = 12 * 60 * 60 * 1000;   // yesterday's story is not worth resuming

  function read(key) {
    try {
      const r = JSON.parse(localStorage.getItem(KEY(key)) || 'null');
      if (!r || typeof r.i !== 'number') return null;
      if (Date.now() - (r.t || 0) > MAX_AGE) { clear(key); return null; }
      return r;
    } catch (e) { return null; }
  }
  function save(key, i, total) {
    try { localStorage.setItem(KEY(key), JSON.stringify({ i: i, total: total, t: Date.now() })); }
    catch (e) { /* private window — the story still plays, it just won't resume */ }
  }
  function clear(key) { try { localStorage.removeItem(KEY(key)); } catch (e) {} }

  function offer(cfg, saved) {
    const i = saved.i, total = cfg.total || saved.total || 0;
    let label = '';
    try { label = (cfg.label && cfg.label(i)) || ''; } catch (e) {}

    const el = document.createElement('div');
    el.id = 'pgResume';
    el.innerHTML =
      '<div class="pg-box">' +
        '<div style="font-size:42px">🔖</div>' +
        '<h2 style="margin:8px 0 4px;font-size:21px">Carry on where you stopped?</h2>' +
        '<p style="margin:0 0 14px;color:#4a5a66">The story was left part way through. ' +
          'Nothing is lost.</p>' +
        (label ? '<div class="pg-at"><span style="font-size:13px;color:#7d8c97">You stopped at</span>' +
                 '<div style="font-size:19px;font-weight:800;margin-top:2px">' + label + '</div>' +
                 (total ? '<span style="font-size:13px;color:#7d8c97">step ' + (i + 1) +
                          ' of ' + total + '</span>' : '') + '</div>' : '') +
        '<button id="pg-go">▶ Carry on</button>' +
        '<button id="pg-fresh">Start from the beginning</button>' +
      '</div>';
    Object.assign(el.style, { position: 'fixed', inset: '0', zIndex: '9996', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: '18px',
      background: 'rgba(12,16,20,.66)', backdropFilter: 'blur(3px)',
      font: '15px/1.55 system-ui,-apple-system,sans-serif' });
    const css = document.createElement('style');
    css.textContent =
      '#pgResume .pg-box{background:#fff;color:#16202a;border-radius:22px;padding:26px 22px;' +
        'max-width:360px;width:100%;text-align:center;box-shadow:0 24px 60px rgba(0,0,0,.3)}' +
      '#pgResume .pg-at{background:#f4f7f5;border-radius:14px;padding:12px;margin:0 0 16px}' +
      '#pgResume .pg-at span{display:block}' +
      '#pgResume button{width:100%;border:0;border-radius:14px;font:inherit;cursor:pointer}' +
      '#pgResume #pg-go{padding:16px;font-size:18px;font-weight:800;background:#173f28;color:#fff}' +
      '#pgResume #pg-fresh{margin-top:8px;padding:10px;font-size:13px;background:none;' +
        'color:#8c9aa4;text-decoration:underline}';
    el.appendChild(css);
    document.body.appendChild(el);

    el.querySelector('#pg-go').onclick = async () => {
      el.remove();
      try { await cfg.resume(i); }
      catch (e) { console.warn('resume failed: ' + e.message); clear(cfg.key); }
    };
    el.querySelector('#pg-fresh').onclick = () => { el.remove(); clear(cfg.key); };
  }

  function track(cfg) {
    if (!cfg || !cfg.key || typeof cfg.at !== 'function') return;
    let last = null, running = false;

    const tick = () => {
      let i = null;
      try { i = cfg.at(); } catch (e) { return; }
      if (typeof i === 'number' && i >= 0) {
        running = true;
        if (i !== last) { last = i; save(cfg.key, i, cfg.total); }
      } else if (running) {
        // The story ended on this page — finished, or reset by hand.
        running = false; last = null; clear(cfg.key);
      }
    };
    setInterval(tick, 1200);

    // The one that actually matters. A tab being discarded gets no warning
    // beyond this, so write the moment the page goes away.
    const flush = () => { if (running && last !== null) save(cfg.key, last, cfg.total); };
    document.addEventListener('visibilitychange', () => { if (document.hidden) { tick(); flush(); } });
    window.addEventListener('pagehide', flush);

    const ask = () => {
      const saved = read(cfg.key);
      if (!saved || saved.i <= 0) return;   // step 0 is the beginning — nothing to offer
      if (typeof cfg.resume !== 'function') return;
      offer(cfg, saved);
    };
    if (document.body) ask();
    else document.addEventListener('DOMContentLoaded', ask);
  }

  return { track: track, clear: clear, read: read, save: save };
})();
