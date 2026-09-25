/* scan-guard.js — ignoring accidental scans.
 *
 * A card left resting on the reader fires over and over on some readers. A
 * child sweeping a handful of cards past it fires three in a row. Both look
 * to the game like deliberate answers, and a wrong one costs the child a
 * "not that one" they did not earn.
 *
 * Three rules, cheapest first:
 *   - a read shorter than 3 characters is noise, not a card
 *   - the SAME card again within repeatMs is the same tap, not a new one
 *   - ANY card within minGapMs is a bounce — nobody swaps cards that fast
 *
 * ScanGuard.wrap(fn)            -> a guarded copy of a scan handler
 * ScanGuard.wrapGlobal('name')  -> guards window.<name> in place
 * ScanGuard.stats               -> {passed, repeat, bounce, tooShort}
 */
window.ScanGuard = (function () {
  const REPEAT_MS = 1500;   // same card again
  const MIN_GAP_MS = 250;   // any card again
  const MIN_LEN = 3;

  const stats = { passed: 0, repeat: 0, bounce: 0, tooShort: 0 };
  const norm = (v) => String(v == null ? '' : v).trim().toUpperCase().replace(/^0+(?=.)/, '');

  function wrap(fn, o) {
    o = o || {};
    const repeatMs = o.repeatMs == null ? REPEAT_MS : o.repeatMs;
    const minGap = o.minGapMs == null ? MIN_GAP_MS : o.minGapMs;
    let lastUid = null, lastAt = 0;
    return function (raw) {
      const uid = norm(raw);
      const now = Date.now();
      if (uid.length < MIN_LEN) { stats.tooShort++; return; }
      if (uid === lastUid && now - lastAt < repeatMs) { stats.repeat++; return; }
      if (lastUid !== null && now - lastAt < minGap) { stats.bounce++; return; }
      lastUid = uid; lastAt = now; stats.passed++;
      return fn.apply(this, arguments);
    };
  }

  function wrapGlobal(name, o) {
    const fn = window[name];
    if (typeof fn !== 'function') { console.warn('scan guard: no ' + name + '() to guard'); return false; }
    if (fn.__guarded) return true;
    const g = wrap(fn, o);
    g.__guarded = true;
    window[name] = g;
    return true;
  }

  return { wrap, wrapGlobal, stats, _norm: norm };
})();
