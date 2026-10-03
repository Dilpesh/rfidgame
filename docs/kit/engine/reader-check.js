/* reader-check.js — "is the card reader actually working?"
 *
 * There is no way for a web page to ask Android whether OTG is on:
 *   - WebHID is not supported on Android at all (Chrome, Samsung Internet, none).
 *   - WebUSB is supported, but it filters out protected interface classes, and a
 *     keyboard-wedge RFID reader is HID — so it is invisible there too.
 *   - intent: deep links into Settings are blocked by mobile browsers.
 *
 * So we test the thing that actually matters instead: ask for a card, and see
 * whether any keystrokes arrive. That catches OTG being off, a dead cable, an
 * unpowered hub and a broken reader alike — without caring which it was.
 *
 * Usage:  ReaderCheck.run({ onWorking(){}, onSkip(){} })
 *         ReaderCheck.known()   -> true if this browser has scanned before
 */
window.ReaderCheck = (function () {
  const KEY = 'readerCheck:ok';
  const WAIT_MS = 12000;

  const known = () => { try { return localStorage.getItem(KEY) === '1'; } catch { return false; } };
  const remember = () => { try { localStorage.setItem(KEY, '1'); } catch {} };

  /* Chrome froze the Android model in the UA string to "K", but the real model
     is still available through client hints, same-origin, with no prompt. */
  async function device() {
    const ua = navigator.userAgent || '';
    if (!/Android/i.test(ua)) return { android: false, brand: '' };
    let model = '';
    try {
      const d = await navigator.userAgentData?.getHighEntropyValues(['model']);
      model = d?.model || '';
    } catch {}
    const hay = (model + ' ' + ua).toLowerCase();
    const brand =
      /xiaomi|redmi|poco|mi\s/.test(hay) ? 'xiaomi' :
      /realme/.test(hay)                 ? 'realme' :
      /oppo|cph\d/.test(hay)             ? 'oppo'   :
      /vivo|iqoo/.test(hay)              ? 'vivo'   :
      /samsung|sm-[a-z]/.test(hay)       ? 'samsung':
      /oneplus|\bkb2|\ble2/.test(hay)    ? 'oneplus': '';
    return { android: true, brand, model };
  }

  /* Brand detection from a web page is only half-reliable. Samsung, OPPO,
     OnePlus and Pixel put something recognisable in the model string, but
     Xiaomi's are bare codes like "22101316C" that name nothing — and Xiaomi is
     the most likely phone to need this. So the brand is a highlight, never the
     instruction: the Settings search box is what everyone is told to use, and
     the common paths are listed for all of them regardless.

     Paths are described as "usually" on purpose. Every Android skin moves them
     between versions, and a confidently wrong path is worse than none. */
  const PATHS = [
    ['xiaomi',  'Xiaomi, Redmi, POCO',  'Additional settings → OTG'],
    ['realme',  'realme',               'Additional settings → OTG'],
    ['oppo',    'OPPO',                 'Additional settings → OTG'],
    ['vivo',    'vivo, iQOO',           'More settings → OTG'],
    ['oneplus', 'OnePlus',              'System settings → OTG storage'],
    ['samsung', 'Samsung',              'usually no switch — it is always on'],
  ];

  function overlay(html) {
    const el = document.createElement('div');
    el.id = 'readerCheck';
    el.innerHTML =
      '<div class="rc-box" role="dialog" aria-modal="true" aria-label="Card reader check">' + html + '</div>';
    Object.assign(el.style, {
      position: 'fixed', inset: '0', zIndex: '9999', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: '18px',
      background: 'rgba(12,16,20,.62)', backdropFilter: 'blur(3px)',
      font: '15px/1.55 system-ui, -apple-system, sans-serif'
    });
    Object.assign(el.querySelector('.rc-box').style, {
      background: '#fff', color: '#16202a', borderRadius: '20px', padding: '22px',
      maxWidth: '420px', width: '100%', boxShadow: '0 24px 60px rgba(0,0,0,.3)',
      maxHeight: '86vh', overflowY: 'auto'
    });
    document.body.appendChild(el);
    return el;
  }

  const btn = (label, primary) =>
    `<button class="rc-btn" data-primary="${!!primary}" style="border:0;border-radius:12px;padding:12px 16px;
      font:inherit;font-weight:700;cursor:pointer;margin:6px 6px 0 0;
      background:${primary ? '#173f28' : '#e8eceb'};color:${primary ? '#fff' : '#16202a'}">${label}</button>`;

  async function run(opts = {}) {
    const onWorking = opts.onWorking || (() => {});
    const onSkip = opts.onSkip || (() => {});
    const dev = await device();

    const el = overlay(
      '<h2 style="margin:0 0 6px;font-size:19px">Tap any card on the reader</h2>' +
      '<p style="margin:0 0 14px;color:#4a5a66">Just checking the reader is awake. Any card will do.</p>' +
      '<div id="rc-dot" style="font-size:44px;text-align:center;margin:8px 0 14px">🎴</div>' +
      '<div id="rc-wait" style="text-align:center;color:#7d8c97;font-size:13px">Listening…</div>' +
      '<div id="rc-actions" style="margin-top:8px">' + btn('Skip — play without a reader') + '</div>'
    );

    let buf = '', last = 0, done = false, timer;
    const finish = (worked) => {
      if (done) return; done = true;
      clearTimeout(timer);
      document.removeEventListener('keydown', onKey, true);
      if (worked) {
        remember();
        el.querySelector('.rc-box').innerHTML =
          '<div style="font-size:44px;text-align:center">✅</div>' +
          '<h2 style="margin:8px 0 4px;font-size:19px;text-align:center">Reader is working</h2>' +
          '<p style="margin:0;text-align:center;color:#4a5a66">You will not be asked again on this phone.</p>';
        setTimeout(() => { el.remove(); onWorking(); }, 1100);
      } else {
        showHelp(el, dev, onSkip);
      }
    };

    function onKey(e) {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const now = Date.now();
      if (now - last > 1000) buf = '';
      last = now;
      if (e.key === 'Enter') { if (buf.length >= 3) finish(true); buf = ''; return; }
      if (e.key.length === 1) {
        buf += e.key;
        // some readers send no Enter at all — a fast burst of characters is enough
        if (buf.length >= 6) finish(true);
      }
    }
    document.addEventListener('keydown', onKey, true);
    el.querySelector('.rc-btn').onclick = () => { finish(null); el.remove(); onSkip(); };
    timer = setTimeout(() => finish(false), WAIT_MS);
  }

  function showHelp(el, dev, onSkip) {
    const rows = PATHS.map(([id, name, where]) => {
      const me = id === dev.brand;
      return '<li style="margin:2px 0;' + (me ? 'font-weight:700;color:#16202a' : 'color:#6b7a85') + '">' +
             name + ' — <span style="font-weight:400">' + where + '</span>' +
             (me ? ' &nbsp;<span style="font-size:11px;background:#e6f0e9;padding:2px 6px;border-radius:6px">your phone</span>' : '') +
             '</li>';
    }).join('');

    el.querySelector('.rc-box').innerHTML =
      '<h2 style="margin:0 0 8px;font-size:19px">No card came through</h2>' +
      '<p style="margin:0 0 14px;color:#4a5a66">Nothing reached the phone, so the reader is not talking to it yet. ' +
      'Three things to try, quickest first:</p>' +
      '<ol style="margin:0 0 12px;padding-left:20px">' +
      (dev.android
        ? '<li style="margin-bottom:10px"><b>Turn on OTG.</b> Open <b>Settings</b>, tap the <b>search box</b> at the ' +
          'top and type <b>OTG</b>. Turn on whatever it finds. Many phones switch it back off by themselves after ' +
          'about ten minutes idle, so do this just before you play.' +
          '<ul style="margin:8px 0 0;padding-left:18px;font-size:13px;list-style:none">' +
          '<li style="color:#8c9aa4;margin-bottom:3px">Where it usually lives:</li>' + rows + '</ul></li>'
        : '') +
      '<li style="margin-bottom:10px"><b>Reseat the reader.</b> Unplug it and plug it back in. Many phones only ' +
      'notice an OTG device at the moment it is connected.</li>' +
      '<li><b>Try another cable or adapter.</b> Plenty of USB-C adapters are charge-only and carry no data at all' +
      (dev.android ? ' — this is the most common culprit after OTG itself.' : '.') + '</li>' +
      '</ol>' +
      '<p style="margin:0 0 4px;color:#4a5a66">Then come back and tap a card again.</p>' +
      '<div style="margin-top:10px">' + btn('Try again', true) + btn('Play without a reader') + '</div>';
    const [again, skip] = el.querySelectorAll('.rc-btn');
    again.onclick = () => { el.remove(); run({ onWorking: () => location.reload(), onSkip }); };
    skip.onclick = () => { el.remove(); onSkip(); };
  }

  return { run, known, _device: device };
})();
