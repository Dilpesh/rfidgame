/* interrupt-guard.js — surviving a phone call.
 *
 * Every one of these games waits on an audio clip finishing. A call suspends
 * the audio — sometimes kills it outright — and that finish event never comes,
 * so the story waits forever and every scan is ignored. That is the hang.
 *
 * A browser will not restart audio without a tap, so a button is unavoidable.
 * What this does is make it one big obvious button, put the card they are
 * looking for on it, and lose nothing.
 *
 * InterruptGuard.watch({
 *   active()      -> is a story running right now
 *   onHide()      -> optional: called when the page goes away (silence things)
 *   healthy()     -> optional: false if the audio has died even while visible
 *   onCarryOn()   -> put the story back on its feet; may be async
 *   nextCard()    -> optional {icon,label} to show on the button
 * })
 */
window.InterruptGuard = (function () {
  let overlay = null, cfg = null;

  function ask() {
    if (overlay || !cfg || !cfg.active()) return;
    const card = (cfg.nextCard && cfg.nextCard()) || null;
    const el = document.createElement('div');
    el.id = 'carryOn';
    el.innerHTML =
      '<div class="ig-box">' +
        '<div style="font-size:44px">⏸️</div>' +
        '<h2 style="margin:10px 0 4px;font-size:21px">Ready when you are</h2>' +
        '<p style="margin:0 0 16px;color:#4a5a66">The story waited for you. Nothing is lost.</p>' +
        (card ? '<div class="ig-card"><span style="font-size:13px;color:#7d8c97">Looking for</span>' +
                '<div style="font-size:34px;line-height:1.2">' + (card.icon || '🎴') + '</div>' +
                '<b style="font-size:16px">' + (card.label || '') + '</b></div>' : '') +
        '<button id="igBtn">▶ Carry on</button>' +
      '</div>';
    Object.assign(el.style, { position: 'fixed', inset: '0', zIndex: '9998', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: '18px',
      background: 'rgba(12,16,20,.66)', backdropFilter: 'blur(3px)',
      font: '15px/1.55 system-ui,-apple-system,sans-serif' });
    const css = document.createElement('style');
    css.textContent =
      '#carryOn .ig-box{background:#fff;color:#16202a;border-radius:22px;padding:26px 22px;' +
        'max-width:360px;width:100%;text-align:center;box-shadow:0 24px 60px rgba(0,0,0,.3)}' +
      '#carryOn .ig-card{background:#f4f7f5;border-radius:14px;padding:10px;margin:0 0 16px}' +
      '#carryOn #igBtn{border:0;border-radius:14px;padding:16px 22px;font:inherit;font-size:18px;' +
        'font-weight:800;cursor:pointer;background:#173f28;color:#fff;width:100%}';
    el.appendChild(css);
    document.body.appendChild(el);
    overlay = el;
    el.querySelector('#igBtn').onclick = async () => {
      el.remove(); overlay = null;
      try { await cfg.onCarryOn(); } catch (e) { console.warn('carry on failed: ' + e.message); }
    };
  }

  function watch(o) {
    cfg = o;
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) { if (cfg.active() && cfg.onHide) cfg.onHide(); return; }
      if (cfg.active()) ask();
    });
    // Some interruptions never fire visibilitychange — the audio just stops.
    if (cfg.healthy) setInterval(() => {
      if (cfg.active() && !overlay && !cfg.healthy()) ask();
    }, 1500);
  }

  return { watch, ask, showing: () => !!overlay };
})();
