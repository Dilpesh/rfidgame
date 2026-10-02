/* nfc.js — "Phone NFC" mode for Bobo की Birthday Party. This story only.
 *
 * A copy of night-drive/nfc.js (30 Sep 2026) with one addition: the phone's tag
 * serial is converted to the number the laptop's USB reader types, so every card
 * already in cards.json works on the phone with no teaching.
 *
 * The engine (../../engine/kahani.js) is shared by every kit story and is not
 * touched. This file is loaded by bobo-birthday/index.html alone and adds a
 * second way of answering to the welcome page:
 *
 *   Start · RFID reader   the engine's own start — the USB reader typing card numbers
 *   Start · Phone NFC     the phone's NFC antenna reads the same 13.56 MHz cards
 *                         through Web NFC, and each card is handed to the engine
 *                         exactly as a reader keystroke would be
 *
 * Phone serial → laptop number (3 Oct 2026):
 *   Chrome gives the tag's ID as hex bytes, e.g. "c2:23:db:30" (the Speaker card).
 *   The USB reader types the same 4 bytes read the other way round, as a 10-digit
 *   decimal: 30 DB 23 C2 → 0819667906, which is what cards.json holds. Dilpesh
 *   confirmed that number on the laptop for this card. So for a tag we try, in order:
 *     1. bytes reversed → decimal   (the laptop reader's way — every card in cards.json)
 *     2. bytes as read  → decimal   (in case another reader model does it this way)
 *     3. the hex serial itself      (tags taught on a phone before this conversion)
 *   and hand the engine the first one the card registry knows.
 *
 * Unknown tag: in developer mode (?dev) a "which card is this?" panel teaches it
 * with CardRegistry.teach(), under the laptop-style number (rule 1), so the Copy
 * list can go straight into cards.json and the same card then works on the laptop
 * too. Outside developer mode an unknown tag is ignored with a status line.
 *
 * Limits that are the platform's, not ours:
 *   - Web NFC exists only in Chrome on Android, on https (GitHub Pages and Netlify
 *     are fine; a laptop's http://192.168… address is not). iPhone Safari cannot
 *     read NFC from a web page — that needs the native app. The button is shown
 *     disabled with the reason on such phones.
 *   - NDEFReader.scan() must be called inside a user tap, and the first time Chrome
 *     asks "Allow NFC?". If that takes more than a few seconds the tap no longer
 *     counts for audio, so the button says "tap to start" and a second tap starts it.
 *   - While the page is scanning, Chrome gets the tag, not Android's NFC app. Before
 *     Start · Phone NFC is tapped (or with the screen off) Android's own
 *     "Scan result / Empty tag" screen still appears — that is expected.
 *   - Reading pauses while the page is hidden; Chrome resumes it when it is visible.
 *   - A card with no text on it is normal: only its ID is used.
 */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const TAUGHT_KEY = 'boboBirthdayNfcTags';           // {serial: CANON} — only what was taught here, for cards.json later
  const FAST_MS = 3000;                            // permission already granted: scan() resolves well within this

  const supported = 'NDEFReader' in window;
  const secure = window.isSecureContext;
  let reader = null, scanning = false, ready = false, guarded = null, lastUnknown = null;

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  /* ───────── phone serial → the number the laptop reader types ───────── */
  const bytesOf = (serial) => {
    const hex = String(serial || '').replace(/[^0-9a-f]/gi, '');
    if (!hex || hex.length % 2) return null;
    const out = []; for (let i = 0; i < hex.length; i += 2) out.push(parseInt(hex.slice(i, i + 2), 16));
    return out;
  };
  const decimal = (bytes) => { let n = 0n; for (const b of bytes) n = n * 256n + BigInt(b); return n.toString(); };
  const pad10 = (d) => (d.length < 10 ? '0'.repeat(10 - d.length) + d : d);
  function candidates(serial) {
    const hex = String(serial || '').trim().toUpperCase();
    const b = bytesOf(hex);
    if (!b) return hex ? [hex] : [];
    const reversed = pad10(decimal(b.slice().reverse()));
    const asRead = pad10(decimal(b));
    return [...new Set([reversed, asRead, hex])];
  }
  // the key a new tag is taught under: the laptop-style number, so it fits cards.json as it is
  const teachKey = (serial) => candidates(serial)[0] || '';

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
    let key = null, canon = null;
    if (window.CardRegistry) for (const c of candidates(serial)) { const k = CardRegistry.lookup(c); if (k) { key = c; canon = k; break; } }
    if (canon && inStory(canon)) { hideTeach(); say(''); guarded(key); return; }
    if (canon) { say(`That tag is ${canon}, which this story does not use.`, 'warn'); return; }
    const k = teachKey(serial);
    lastUnknown = k;
    if (isDev()) { say(`Unknown tag ${serial} (reader number ${k}).`, 'warn'); showTeach(k); }
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
      say(!secure ? 'Phone NFC needs an https address (or localhost) — open the game from its https address (GitHub Pages or Netlify).'
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

  window.BoboNFC = { candidates, teachKey, supported, secure, _reading: onReading, _ready: () => ready, _scanning: () => scanning, _lastUnknown: () => lastUnknown, taught: readTaught };
})();
