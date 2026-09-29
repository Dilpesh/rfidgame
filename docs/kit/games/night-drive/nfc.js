/* nfc.js — "Phone NFC" mode for Coco की Night Drive. This story only.
 *
 * The engine (../../engine/kahani.js) is shared by every kit story and is not
 * touched. This file is loaded by night-drive/index.html alone and bolts a
 * second way of answering onto the welcome page:
 *
 *   Start · RFID reader   the engine's own start — the 125 kHz reader typing UIDs
 *   Start · Phone NFC     the phone's NFC antenna reads 13.56 MHz tags (NTAG213 …)
 *                         through Web NFC, and every tag serial is handed to the
 *                         engine exactly as a reader keystroke would be
 *
 * How a tag becomes a card (decision, 30 Sep 2026: teach by serial only):
 *   - a tag's serial number is looked up in the card registry
 *     (card-registry.js — the same one the RFID cards live in, one localStorage
 *     key for the whole site, so a tag taught here is known in every kit game)
 *   - an unknown tag in developer mode (?dev, or Ctrl+Shift+D) shows a small
 *     "which card is this?" panel; pick one and the serial is taught with
 *     CardRegistry.teach() and counted at once
 *   - an unknown tag outside developer mode is ignored with a status line
 *   - the serials taught on this phone are listed in developer mode with a Copy
 *     button, so they can go into cards.json later (cards are global)
 *
 * What the engine sees: Kahani.handleScan(serial), wrapped in ScanGuard, so
 * early scans, tap windows, wrong-card lines and the progress bar all behave as
 * for a reader. The engine's reader check is skipped for this play (no keyboard
 * wedge to test); nothing about it is written to storage.
 *
 * Limits that are the platform's, not ours:
 *   - Web NFC exists only in Chrome (and Chromium browsers) on Android, on a
 *     secure origin (https, or localhost). iPhone Safari cannot read NFC tags
 *     from a web page at all — that needs a native app. The button is shown
 *     disabled with the reason on such phones.
 *   - NDEFReader.scan() must be called inside a user tap, and the first time
 *     Chrome asks "Allow NFC?". If that prompt takes longer than a few seconds
 *     the tap's activation has expired for audio, so the story is not started
 *     behind the prompt; the button says "tap again" and the second tap starts it.
 *   - Reading pauses while the page is hidden; Chrome resumes it when the page
 *     is visible again.
 *   - The 125 kHz cards cannot be read by a phone and the NFC tags cannot be
 *     read by the 125 kHz reader: NFC mode needs its own set of tags.
 */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const TAUGHT_KEY = 'nightDriveNfcTags';           // {serial: CANON} — only what was taught here, for cards.json later
  const FAST_MS = 3000;                            // permission already granted: scan() resolves well within this

  const supported = 'NDEFReader' in window;
  const secure = window.isSecureContext;
  let reader = null, scanning = false, ready = false, guarded = null, lastUnknown = null;

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const isDev = () => { const d = $('kDevLine'); return !!d && !d.classList.contains('hide'); };
  const story = () => (window.Kahani && Kahani._story && Kahani._story()) || null;
  const storyCards = () => (story() ? story().cards : []);
  const inStory = (canon) => storyCards().some((c) => c.registry === canon);
  const label = (canon) => { const c = storyCards().find((x) => x.registry === canon); return c ? `${c.icon} ${c.label}` : canon; };

  function say(msg, cls) {
    // the welcome line before the story starts, the play-panel line after
    const el = $('kWelcome') && !$('kWelcome').classList.contains('hide') ? $('kNfcLine') : $('kNfcPlayLine');
    if (!el) return;
    el.textContent = msg; el.className = 'status ' + (cls || '');
    el.classList.toggle('hide', !msg);
  }

  /* ───────── taught serials (for cards.json) ───────── */
  const readTaught = () => { try { return JSON.parse(localStorage.getItem(TAUGHT_KEY) || '{}') || {}; } catch (e) { return {}; } };
  const writeTaught = (m) => { try { localStorage.setItem(TAUGHT_KEY, JSON.stringify(m)); } catch (e) {} };
  function renderTaught() {
    const el = $('kNfcTaught'); if (!el) return;
    const m = readTaught(); const serials = Object.keys(m);
    el.classList.toggle('hide', !isDev());
    if (!serials.length) { el.innerHTML = '<span class="muted">No NFC tags taught on this phone yet.</span>'; return; }
    const byCard = {}; serials.forEach((s) => { (byCard[m[s]] = byCard[m[s]] || []).push(s); });
    el.innerHTML = `<span class="muted">NFC tags taught on this phone (for cards.json):</span> ` +
      serials.map((s) => `<code>${esc(s)}</code> → ${esc(m[s])}`).join(' · ') +
      ` <button id="kNfcCopy" style="padding:4px 10px;font-size:12px">Copy</button>`;
    $('kNfcCopy').onclick = () => {
      const text = JSON.stringify(byCard, null, 2);
      const done = () => { $('kNfcCopy').textContent = 'Copied'; setTimeout(() => { if ($('kNfcCopy')) $('kNfcCopy').textContent = 'Copy'; }, 1500); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, () => window.prompt('Copy this:', text));
      else window.prompt('Copy this:', text);
    };
  }

  /* ───────── the teach panel (developer mode only) ───────── */
  function showTeach(serial) {
    const p = $('kNfcTeach'); if (!p) return;
    p.innerHTML = `<div class="muted">New tag <code>${esc(serial)}</code> — which card is it?</div>
      <div class="tapgrid" style="margin-top:10px">${storyCards().map((c) =>
        `<button class="card tap" data-canon="${esc(c.registry)}"><span class="icon">${c.icon}</span><small>${esc(c.label)}</small></button>`).join('')}</div>
      <div class="actions"><button id="kNfcIgnore">Ignore this tag</button></div>`;
    p.classList.remove('hide');
    p.querySelectorAll('button[data-canon]').forEach((b) => { b.onclick = () => teach(serial, b.dataset.canon); });
    $('kNfcIgnore').onclick = () => { p.classList.add('hide'); lastUnknown = null; say(''); };
  }
  function hideTeach() { const p = $('kNfcTeach'); if (p) p.classList.add('hide'); }
  function teach(serial, canon) {
    const ok = window.CardRegistry && CardRegistry.teach(serial, canon);
    if (!ok) { say(`Could not teach ${serial} as ${canon} — is it in cards.json?`, 'error'); return; }
    const m = readTaught(); m[serial] = canon; writeTaught(m); renderTaught();
    hideTeach(); lastUnknown = null;
    say(`Taught: ${serial} is ${label(canon)}.`, 'ok');
    guarded(serial);                                   // it counts right now, like any scan
  }

  /* ───────── a tag was read ───────── */
  function onReading(ev) {
    const serial = String(ev.serialNumber || '').trim().toUpperCase();
    if (!serial) { say('That tag has no serial number — try another tag.', 'warn'); return; }
    const canon = window.CardRegistry ? CardRegistry.lookup(serial) : null;
    if (canon && inStory(canon)) { hideTeach(); say(''); guarded(serial); return; }
    if (canon) { say(`That tag is ${canon}, which this story does not use.`, 'warn'); return; }
    lastUnknown = serial;
    if (isDev()) { say(`Unknown tag ${serial}.`, 'warn'); showTeach(serial); }
    else say('Unknown tag — teach it in developer mode (?dev).', 'warn');
  }
  function onReadingError() { say("Couldn't read that tag — hold it still against the back of the phone.", 'warn'); }

  /* ───────── starting ───────── */
  function explain(e) {
    const n = (e && e.name) || '';
    if (n === 'NotAllowedError') return 'NFC was not allowed. Check Chrome › Site settings › NFC for this site, then try again.';
    if (n === 'NotSupportedError') return 'NFC is off or not available on this phone. Turn NFC on in the phone settings and try again.';
    if (n === 'NotReadableError') return 'The NFC antenna is busy (another app?) — close it and try again.';
    if (n === 'AbortError') return 'NFC scan stopped.';
    return 'NFC could not start: ' + (e && (e.message || n) || 'unknown error');
  }

  function install() {
    const start = $('kStart'); if (!start || $('kNfc')) return;
    const engineStart = start.onclick;                  // the engine's begin('reader'), captured once
    if (typeof engineStart !== 'function') return;
    start.textContent = 'Start · RFID reader';

    const nfc = document.createElement('button');
    nfc.id = 'kNfc'; nfc.className = 'primary'; nfc.textContent = 'Start · Phone NFC';
    start.insertAdjacentElement('afterend', nfc);

    const line = document.createElement('div'); line.id = 'kNfcLine'; line.className = 'status hide';
    $('kWelcomeStatus').insertAdjacentElement('afterend', line);

    const play = $('kPlay');
    const playLine = document.createElement('div'); playLine.id = 'kNfcPlayLine'; playLine.className = 'status hide';
    const teachPanel = document.createElement('div'); teachPanel.id = 'kNfcTeach'; teachPanel.className = 'wanted hide';
    const taught = document.createElement('div'); taught.id = 'kNfcTaught'; taught.className = 'muted small hide';
    $('kTapGrid').insertAdjacentElement('afterend', teachPanel);
    teachPanel.insertAdjacentElement('afterend', playLine);
    $('kDevLine').insertAdjacentElement('beforebegin', taught);
    renderTaught();
    // the dev line toggles when developer mode does; mirror it for the taught list
    new MutationObserver(renderTaught).observe($('kDevLine'), { attributes: true, attributeFilter: ['class'] });

    if (!supported || !secure) {
      nfc.disabled = true;
      say(!secure ? 'Phone NFC needs an https address (or localhost) — open the game from taptales.netlify.app.'
                  : 'Phone NFC needs Chrome on Android. iPhone Safari cannot read NFC tags from a web page.', 'warn');
      return;
    }

    guarded = window.ScanGuard ? ScanGuard.wrap(Kahani.handleScan) : Kahani.handleScan;

    const startStory = () => {
      if (window.ReaderCheck) ReaderCheck.known = () => true;   // this play answers with the phone, not the reader
      start.disabled = true; nfc.disabled = true;
      say('');
      engineStart();
    };

    nfc.onclick = () => {
      if (ready) { startStory(); return; }                      // second tap after the permission prompt
      if (scanning) return;
      scanning = true; nfc.disabled = true; start.disabled = true;
      say('Starting NFC… allow it if Chrome asks.');
      const t0 = performance.now();
      let p;
      try {
        reader = new NDEFReader();
        reader.addEventListener('reading', onReading);
        reader.addEventListener('readingerror', onReadingError);
        p = reader.scan();                                      // inside the tap, as Web NFC requires
      } catch (e) { p = Promise.reject(e); }
      p.then(() => {
        ready = true;
        if (performance.now() - t0 < FAST_MS) { startStory(); return; }   // no prompt: the tap is still fresh for audio
        nfc.disabled = false; start.disabled = true;
        nfc.textContent = 'NFC ready — tap to start';
        say('NFC is on. Tap the button once more to start the story.', 'ok');
      }).catch((e) => {
        scanning = false; ready = false; reader = null;
        nfc.disabled = false; start.disabled = false;
        say(explain(e), 'error');
      });
    };
  }

  // Kahani.boot() renders the welcome panel after story.json arrives; wait for it.
  if ($('kStart')) install();
  else new MutationObserver((_, o) => { if ($('kStart')) { o.disconnect(); install(); } }).observe(document.body, { childList: true, subtree: true });

  window.NightDriveNFC = { supported, secure, _reading: onReading, _ready: () => ready, _scanning: () => scanning, _lastUnknown: () => lastUnknown, taught: readTaught };
})();
