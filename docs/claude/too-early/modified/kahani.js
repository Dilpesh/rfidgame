/* kahani.js — the story engine every game shares.
 *
 * A game folder is ten lines of HTML that load this file and a story.json
 * (compiled from stories/<slug>/story.txt by storykit/compile.py). Everything a
 * story used to carry in its own index.html lives here once:
 *
 *   - iOS Safari audio: a fixed pool of <audio> elements authorised inside the
 *     start tap, a 50 ms silent unlock, Web Audio gain for levels (iOS pins
 *     element.volume to 1.0), every clip prefetched into memory as blob URLs
 *   - screen wake lock, re-taken on visibilitychange, released at the end
 *   - the question machine: arm a card, prompt, hint ladder (8/17/28 s by
 *     default), warm rotating wrong-card lines, reminders, tap windows
 *   - pause / resume that holds clips, beds, overlays and timed waits
 *   - beds (loops) with crossfade, overlays with volume, a dance track with
 *     ducking and a stall-proof "wait until the music reaches N seconds"
 *   - the card registry (card-registry.js when present, else the UIDs the
 *     compiler copied from cards.json), scan-guard, reader-check, story-intro
 *   - production mode (no tray, no card named) with developer mode behind
 *     Ctrl+Shift+D / ?dev: log, Next cue, Jump to scene, variant picker
 *   - variants: ?v=<name> filters tagged beats at load, same audio
 *   - the shared library: a cue "lib:<id>" resolves to docs/kit/library/, so a
 *     chime, a bed or a "Great job!" recorded once serves every story
 *   - early scans (LEARNINGS 9–10): a tap while Coco is talking gets a sound at
 *     once and, if it is the card the next question wants, counts when it arms
 *
 * The audio machinery is a straight port of the ios-volume-fix-standalone
 * build of Jungle Rescue English (build ios-standalone-13), which is the copy
 * that was beaten into shape on an iPhone. Do not "tidy" it without re-testing
 * on a phone.
 *
 * Usage:  Kahani.boot({ story: 'story.json' })
 */
window.Kahani = (function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const norm = (v) => String(v == null ? '' : v).trim().toUpperCase().replace(/^0+(?=.)/, '');
  const params = new URLSearchParams(location.search);

  /* ─────────────────────────── state ─────────────────────────── */
  let story = null, manifest = {}, AUDIO_DIR = 'audio/', CACHE_TAG = 'v1', LIB_DIR = '../../library/', LIB_TAG = 'lib1';
  let mode = 'reader', state = 'idle', expected = null, epoch = 0;
  let hintTimers = [], reminderTimers = [], bedFadeTimer = null, hintIndex = 0, wrongVariant = 0;
  let audio = null, audioFinish = null, bedAudio = null, danceAudio = null, currentCueId = '';
  const overlays = new Set();
  let pendingAsk = null;          // {card, resolve}
  let earlyScan = null;           // {card, at}: a card scanned while Coco was still talking (LEARNINGS 9–10)
  const EARLY_SCAN_MS = 10000;
  const UNLISTED = '__unlisted__';   // any card not in this story's header
  let tapWindow = null;           // {card, fire}
  let cardMap = {}, uidToCard = {}, inputBuffer = '';
  let progressDone = 0, wakeLock = null, sceneCursor = 0, runToken = 0;
  const cardsDone = new Set();                             // distinct cards accepted: the progress bar
  let devMode = false, variantName = '';
  let childName = '', pack = null;       // the name pack in play, if any (library/names/<slug>/)
  const DEV_KEY = 'kahaniDevMode';

  const log = (s, cls = '') => {
    const el = $('kLog'); if (!el) return;
    if (devMode) el.classList.remove('hide');
    el.innerHTML += `<span class="${cls}">${new Date().toLocaleTimeString()} ${s}</span>\n`;
    el.scrollTop = el.scrollHeight;
  };
  const setStatus = (s, cls = '') => { const el = $('kStatus'); if (el) { el.textContent = s; el.className = 'status ' + cls; } };
  const assetUrl = (file, tag) => location.protocol === 'file:' ? file : file + (file.includes('?') ? '&' : '?') + tag;

  /* ───────────────────── pause / resume ───────────────────── */
  // Pauses whatever is sounding, and holds any cue or timed wait that is about to
  // start until Resume. Sequences block naturally because a paused clip never fires 'ended'.
  let gamePaused = false, resumeWaiters = [];
  const untilResumed = () => gamePaused ? new Promise((r) => resumeWaiters.push(r)) : Promise.resolve();
  const wait = (ms) => new Promise((resolve) => setTimeout(() => untilResumed().then(resolve), ms));
  function pausables() { return [audio, bedAudio, danceAudio, ...overlays].filter(Boolean); }
  function pauseGame() {
    if (gamePaused || state === 'idle' || state === 'done') return;
    gamePaused = true;
    pausables().forEach((a) => { if (!a.paused) { a.__resume = true; try { a.pause(); } catch (e) {} } });
    if ('speechSynthesis' in window) speechSynthesis.pause();
    const b = $('kPause'); if (b) { b.textContent = '▶ Resume'; b.setAttribute('aria-pressed', 'true'); }
    setStatus('Paused. Tap Resume to continue.');
  }
  function resumeGame() {
    if (!gamePaused) return;
    gamePaused = false; audioCtx();
    pausables().forEach((a) => { if (a.__resume) { a.__resume = false; a.play().catch(() => {}); } });
    if ('speechSynthesis' in window) speechSynthesis.resume();
    const b = $('kPause'); if (b) { b.textContent = '⏸ Pause'; b.setAttribute('aria-pressed', 'false'); }
    const w = resumeWaiters; resumeWaiters = []; w.forEach((r) => r());
  }

  /* ───────────────────── manifest & prefetch ───────────────────── */
  let manifestLoaded = null;
  function loadManifest() {
    if (manifestLoaded) return manifestLoaded;
    manifestLoaded = (async () => {
      try { const r = await fetch(AUDIO_DIR + 'manifest.json', { cache: 'no-store' }); if (r.ok) manifest = await r.json(); }
      catch (e) { log('Audio manifest not installed yet; the player will fall back to speech.', 'warn'); }
      await loadLibrary();
      prefetchClips();
    })();
    return manifestLoaded;
  }
  function cueEntry(id) { const v = manifest[id]; return typeof v === 'string' ? { file: v } : v || {}; }
  // A game's clips live in its own audio/; shared clips (lib:…) live in docs/kit/library/.
  const fileUrl = (c, key = 'file') => c[key] ? (c._lib ? LIB_DIR + c[key] : AUDIO_DIR + c[key]) : '';
  async function loadLibrary() {
    try {
      const r = await fetch(LIB_DIR + 'manifest.json', { cache: 'no-store' }); if (!r.ok) return;
      const lib = await r.json(); const clips = lib.clips || lib; LIB_TAG = lib.version || LIB_TAG;
      for (const [id, c] of Object.entries(clips)) if (c && typeof c === 'object') manifest['lib:' + id] = Object.assign({}, c, { _lib: true });
    } catch (e) { log('shared library not reachable; lib: clips will fall back to speech', 'warn'); }
  }
  function cueText(id, beat) {
    return (beat && beat.text) || (story.clips[id] && story.clips[id].text) || cueEntry(id).spoken_text || '';
  }
  function speechFallback(text) {
    if (!('speechSynthesis' in window) || !text) return;
    const u = new SpeechSynthesisUtterance(text); u.lang = story.language === 'hi' ? 'hi-IN' : story.language || 'hi-IN'; u.rate = .92;
    speechSynthesis.speak(u);
  }
  // iOS Safari authorises sound per <audio> ELEMENT, inside a tap. A fixed pool is created and
  // played silently inside the start tap, then reused forever.
  const POOL = { fg: null, bed: [], ovl: [], dance: null, unlocked: false };
  function mkEl() { const a = new Audio(); a.preload = 'auto'; return a; }
  function poolInit() { if (POOL.fg) return; POOL.fg = mkEl(); POOL.bed = [mkEl(), mkEl()]; POOL.ovl = [mkEl(), mkEl(), mkEl(), mkEl()]; POOL.dance = mkEl(); }
  function poolAll() { return [POOL.fg, ...POOL.bed, ...POOL.ovl, POOL.dance]; }
  function reuseEl(el, src) { el.onended = el.onerror = null; try { el.pause(); } catch (e) {} el.loop = false; el.src = cachedSrc(src); el.load(); return el; }
  function releaseEl(el) { if (!el) return; el.onended = el.onerror = null; try { el.pause(); } catch (e) {} el.removeAttribute('src'); try { el.load(); } catch (e) {} }
  function takeOverlay(src) { poolInit(); let el = POOL.ovl.find((a) => !overlays.has(a)) || POOL.ovl.find((a) => a.paused || a.ended) || POOL.ovl[0]; overlays.delete(el); return reuseEl(el, src); }
  function takeBed(src) { poolInit(); const el = POOL.bed.find((a) => a !== bedAudio) || POOL.bed[0]; return reuseEl(el, src); }
  // Every production clip is fetched in story order in the background as soon as the manifest is
  // known, kept in memory as blob URLs; the pooled players read from memory.
  const clipCache = new Map(); let prefetchStarted = false, prefetchDone = 0, prefetchTotal = 0;
  function clipsReady(ids) {
    const keys = ids.map((i) => fileUrl(cueEntry(i))).filter(Boolean);
    return new Promise((r) => { const t = setInterval(() => { if (keys.every((k) => clipCache.has(k))) { clearInterval(t); r(); } }, 50); });
  }
  function cachedSrc(url) { return clipCache.get(url.split('?')[0]) || url; }
  async function prefetchClips() {
    if (prefetchStarted || !Object.keys(manifest).length) return; prefetchStarted = true;
    // prefetch with the same versioned URL playback uses, so a bumped cache tag really re-downloads
    const list = []; const seen = new Set(); const add = (u) => { if (u && !seen.has(u)) { seen.add(u); list.push(u); } };
    const used = new Set(); story.scenes.forEach((sc) => walk(sc.beats, (b) => { if (b.cue) used.add(b.cue); if (b.prompt && b.prompt.cue) used.add(b.prompt.cue); (b.hints || []).forEach((h) => used.add(h.cue)); }));
    story.wrong.forEach((v) => v.forEach((b) => { if (b.cue) used.add(b.cue); })); [story.tapSound, story.correctSound, story.wrongSound].forEach((c) => { if (c) used.add(c); });
    // story order first, so the intro is ready soonest; then the rest of the game's manifest; library clips only if the story uses them
    firstCues().forEach((id) => { const c = cueEntry(id); ['jeep_file', 'entry_file', 'bed_file', 'file'].forEach((k) => add(fileUrl(c, k))); });
    for (const [k, c] of Object.entries(manifest)) { if (k === '_build' || !c || typeof c !== 'object') continue; if (c._lib && !used.has(k)) continue; for (const key of ['jeep_file', 'entry_file', 'bed_file', 'file']) add(fileUrl(c, key)); }
    prefetchTotal = list.length; const t0 = performance.now();
    let i = 0; const worker = async () => { while (i < list.length) { const u = list[i++]; try { const r = await fetch(assetUrl(u, 'v=' + (u.startsWith(LIB_DIR) ? LIB_TAG : CACHE_TAG))); if (r.ok) { clipCache.set(u, URL.createObjectURL(await r.blob())); prefetchDone++; } } catch (e) {} } };
    await Promise.all([worker(), worker(), worker()]);
    log(`prefetched ${prefetchDone}/${prefetchTotal} clips in ${Math.round((performance.now() - t0) / 1000)} s`);
  }
  // The child's name: typed on the welcome page (never stored), or ?name=. A pack is a folder
  // library/names/<slug>/ with one clip per {name} line; each replaces the "Captain" clip of the
  // same cue for this play only. No pack, or any failure → today's story, "Captain".
  async function loadNamePack(typed) {
    childName = ''; pack = null;
    const key = normName(typed); if (!key) return null;
    try {
      const idx = await (await fetch(LIB_DIR + 'names/index.json', { cache: 'no-store' })).json();
      const slug = idx.keys && idx.keys[key]; if (!slug) { log(`no name pack for "${typed}" — playing as Captain`, 'warn'); return null; }
      const p = await (await fetch(LIB_DIR + `names/${slug}/manifest.json`, { cache: 'no-store' })).json();
      const clips = p.clips || {}; let n = 0; const urls = [];
      story.scenes.forEach((sc) => walk(sc.beats, (b) => applyPackTo(b, clips, slug, urls, () => n++)));
      story.wrong.forEach((v) => v.forEach((b) => applyPackTo(b, clips, slug, urls, () => n++)));
      pack = { slug, display: (p._child && p._child.display) || typed }; childName = pack.display;
      log(`name pack ${slug}: ${n} lines for ${childName}`, 'ok'); prefetchUrls(urls);
      return pack;
    } catch (e) { log(`name pack failed (${e && e.message}); playing as Captain`, 'warn'); return null; }
  }
  function applyPackTo(b, clips, slug, urls, count) {
    const each = (x) => { if (!x || !x.name || !x.cue) return; const k = x.cue.startsWith('lib:') ? x.cue.slice(4) : story.key + ':' + x.cue; const e = clips[k]; if (!e || !e.file) return;
      manifest[x.cue] = Object.assign({}, cueEntry(x.cue), e, { _lib: true, file: `names/${slug}/${e.file}` }); urls.push(LIB_DIR + `names/${slug}/${e.file}`); count(); };
    each(b); if (b.prompt) each(b.prompt); (b.hints || []).forEach(each); if (b.remind) each(b.remind.beat); (b.afterPrompt || []).forEach(each);
  }
  const normName = (t) => String(t || '').normalize('NFC').trim().toLowerCase().replace(/[\s.\-_'’]+/g, '');
  async function prefetchUrls(list) {
    for (const u of list) { if (clipCache.has(u)) continue; try { const r = await fetch(assetUrl(u, 'v=' + LIB_TAG)); if (r.ok) clipCache.set(u, URL.createObjectURL(await r.blob())); } catch (e) {} }
  }
  function firstCues() {
    const out = []; const s = story.scenes[0]; if (!s) return out;
    walk(s.beats, (b) => { if (b.cue && out.length < 3) out.push(b.cue); });
    return out;
  }

  /* ───────────────────── players ───────────────────── */
  function playFile(file, opts = {}) {
    if (audioFinish) audioFinish();
    if (audio) { releaseEl(audio); audio = null; }
    const source = assetUrl(file, 'v=' + (file.startsWith(LIB_DIR) ? LIB_TAG : CACHE_TAG)); poolInit();
    const player = reuseEl(POOL.fg, source); audio = player;
    const cueId = currentCueId;
    return new Promise((resolve) => {
      let done = false, retried = false;
      const finish = () => { if (done) return; done = true; player.onended = player.onerror = null; if (audio === player) audio = null; if (audioFinish === finish) audioFinish = null; resolve(); };
      audioFinish = finish;
      const fallback = () => { const text = opts.text || cueText(cueId); if (text) speechFallback(text); };
      const retry = () => {
        if (done) return;
        if (!retried) { retried = true; player.src = assetUrl(file, 'retry=' + Date.now()); player.load(); player.play().catch((e) => { log(`could not play ${file}: ${e && e.name} ${e && e.message}`, 'error'); fallback(); finish(); }); return; }
        log(`could not play ${file}`, 'error'); fallback(); finish();
      };
      player.onended = finish; player.onerror = retry;
      if (devMode) { const t0 = performance.now(); player.onplaying = () => log(`${file.split('/').pop()} started after ${Math.round(performance.now() - t0)} ms${clipCache.has(file.split('?')[0]) ? ' (cached)' : ' (network)'}`); }
      player.play().catch((e) => { log(`play refused ${file.split('/').pop()}: ${e && e.name} ${e && e.message}`, 'warn'); retry(e); });
    });
  }
  // iOS Safari ignores HTMLMediaElement.volume, so levels go through a Web Audio gain node.
  let actx = null; const gainNodes = new WeakMap();
  function audioCtx() { if (!actx) { const AC = window.AudioContext || window.webkitAudioContext; if (AC) { try { actx = new AC(); } catch (e) { actx = null; } } } if (actx && actx.state === 'suspended') actx.resume().catch(() => {}); return actx; }
  function setVol(el, v) { const ctx = audioCtx(); if (!ctx) { el.volume = v; return; } let g = gainNodes.get(el); if (!g) { try { const src = ctx.createMediaElementSource(el); g = ctx.createGain(); src.connect(g); g.connect(ctx.destination); gainNodes.set(el, g); } catch (e) { el.volume = v; return; } } el.volume = 1; g.gain.value = v; }
  function getVol(el) { const g = gainNodes.get(el); return g ? g.gain.value : el.volume; }
  document.addEventListener('pointerdown', () => audioCtx(), { capture: true, passive: true });

  function playOverlayCue(id, volume = .35) {
    if (gamePaused) return; const c = cueEntry(id); if (!c.file) { log(`overlay ${id} missing from manifest`, 'warn'); return; }
    const effect = takeOverlay(fileUrl(c)); setVol(effect, volume); overlays.add(effect);
    const done = () => { overlays.delete(effect); effect.onended = null; effect.onerror = null; }; effect.onended = done; effect.onerror = done; effect.play().catch(done);
  }
  function playOverlayCueAndWait(id, volume = .35) {
    const c = cueEntry(id); if (!c.file) { log(`overlay ${id} missing from manifest`, 'warn'); return Promise.resolve(); }
    const effect = takeOverlay(fileUrl(c)); setVol(effect, volume); overlays.add(effect);
    return new Promise((resolve) => { const done = () => { overlays.delete(effect); effect.onended = null; effect.onerror = null; resolve(); }; effect.onended = done; effect.onerror = done; effect.play().catch(done); });
  }
  // iOS Safari only lets a page start sound from inside a tap: play a 50 ms silent clip
  // synchronously inside the tap to unlock every pooled element.
  const SILENT_MP3 = 'data:audio/mpeg;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//NwwAAAAAAAAAAAAEluZm8AAAAPAAAABAAAAR8Aubm5ubm5ubm5ubm5ubm5ubm5ubm5ubm50dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0ejo6Ojo6Ojo6Ojo6Ojo6Ojo6Ojo6Ojo6Oj/////////////////////////////////AAAAAExhdmM1OC4xMwAAAAAAAAAAAAAAACQCcQAAAAAAAAEfOUBsQwAAAAAAAAAAAAAAAAD/8xDEAAAAA0gAAAAATEFNRTMuMTAwVVVVVf/zEsQNAAADSAAAAABVVVVVVVVVVVVVVVVVVf/zEMQbAAADSAAAAABVVVVVVVVVVVVVVVVV//MQxCgAAANIAAAAAFVVVVVVVVVVVVVVVVU=';
  function unlockAudio() {
    poolInit(); log('kahani engine 1 · ' + navigator.userAgent.slice(0, 60)); let okc = 0, bad = 0;
    poolAll().forEach((el) => { if (!el.paused) return; try { el.src = SILENT_MP3; el.load(); el.play().then(() => { okc++; if (okc + bad === poolAll().length) log(`silent unlock: ${okc} elements authorised`, 'ok'); }).catch((e) => { bad++; log(`silent unlock refused: ${e && e.name}`, 'error'); }); } catch (e) { bad++; } });
    const c = audioCtx(); log('audio context: ' + (c ? c.state : 'none')); POOL.unlocked = true;
  }
  function playBedFile(file, volume = .18) {
    const prev = bedAudio; const source = assetUrl(file, 'v=' + (file.startsWith(LIB_DIR) ? LIB_TAG : CACHE_TAG)); bedAudio = takeBed(source); releaseEl(prev);
    bedAudio.loop = true; setVol(bedAudio, volume);
    bedAudio.onerror = () => log(`could not play background ${file}`, 'error');
    bedAudio.play().catch((e) => log(`could not start background ${file}: ${e && e.name} ${e && e.message}`, 'error'));
    return Promise.resolve();
  }
  function crossfadeBedFile(file, volume = .18) {
    if (bedFadeTimer) { clearInterval(bedFadeTimer); bedFadeTimer = null; }
    const old = bedAudio; const source = assetUrl(file, 'v=' + (file.startsWith(LIB_DIR) ? LIB_TAG : CACHE_TAG)); const next = takeBed(source); next.loop = true; setVol(next, 0); bedAudio = next;
    next.onerror = () => log(`could not play background ${file}`, 'error'); next.play().catch(() => log(`could not start background ${file}`, 'error'));
    return new Promise((resolve) => { let step = 0; bedFadeTimer = setInterval(() => { step++; setVol(next, volume * step / 8); if (old) setVol(old, Math.max(0, getVol(old) * (8 - step) / 8)); if (step >= 8) { clearInterval(bedFadeTimer); bedFadeTimer = null; if (old) releaseEl(old); resolve(); } }, 90); });
  }
  function playBed(id, volume) {
    const c = cueEntry(id); if (!c.file) { log(`bed ${id} missing from manifest`, 'warn'); return Promise.resolve(); }
    const v = typeof volume === 'number' ? volume : c.volume;
    if (typeof v !== 'number') { log(`bed ${id} has no volume (give one in the script: bed @${id} @0.2)`, 'error'); return Promise.resolve(); }
    return playBedFile(fileUrl(c), v);
  }
  // A cue played "as the manifest says": beds loop, split cues start their bed and play their parts.
  async function playCue(id, opts = {}) {
    await untilResumed(); currentCueId = id;
    const c = cueEntry(id);
    if (c.type === 'split_sfx') {
      if (c.bed_file) playBedFile(fileUrl(c, 'bed_file'), c.bed_volume);
      if (c.jeep_file) await playFile(fileUrl(c, 'jeep_file'));
      if (c.entry_file) return playFile(fileUrl(c, 'entry_file'));
      return;
    }
    if (c.bed || c.loop) return playBed(id);
    if (!c.file) { log(`cue ${id} missing from manifest`, 'warn'); speechFallback(opts.text || cueText(id)); return; }
    return playFile(fileUrl(c), opts);
  }
  function stopBed() { if (bedFadeTimer) { clearInterval(bedFadeTimer); bedFadeTimer = null; } if (bedAudio) { bedAudio.pause(); bedAudio.currentTime = 0; bedAudio = null; } }
  function stopDanceTrack() { if (danceAudio) { releaseEl(danceAudio); danceAudio = null; } }
  function stopForeground() { const active = audio; if (audioFinish) audioFinish(); if (active) { active.onended = active.onerror = null; active.pause(); active.currentTime = 0; if (audio === active) audio = null; } }
  function stopAudio() { stopForeground(); stopDanceTrack(); for (const effect of overlays) releaseEl(effect); overlays.clear(); if ('speechSynthesis' in window) speechSynthesis.cancel(); }
  function clearTimers() { hintTimers.forEach(clearTimeout); hintTimers = []; reminderTimers.forEach(clearTimeout); reminderTimers = []; }
  function invalidate() {
    epoch++; clearTimers(); stopAudio(); expected = null;
    if (pendingAsk) { const p = pendingAsk; pendingAsk = null; p.resolve(-1); }
    if (tapWindow) { const t = tapWindow; tapWindow = null; t.cancel(); }
  }

  /* ───────────────────── dance track ───────────────────── */
  async function startDanceTrack(id) {
    const cue = cueEntry(id);
    if (!cue.file || typeof cue.volume !== 'number') { setStatus('Dance music is missing. Please try again later.', 'error'); log(`music ${id}: no file or volume in manifest`, 'error'); return null; }
    stopDanceTrack(); poolInit(); danceAudio = reuseEl(POOL.dance, fileUrl(cue)); danceAudio.__cue = id; setVol(danceAudio, cue.volume);
    try { await danceAudio.play(); return danceAudio; } catch (e) { stopDanceTrack(); setStatus('Dance music could not play. Please try again.', 'error'); return null; }
  }
  function waitForDanceTime(track, seconds, token) {
    // Resolves true when the music reaches `seconds`. Never hangs: a stalled track is nudged once,
    // and after seconds+6 s of wall-clock (pauses excluded) it gives up and moves on.
    return new Promise((resolve) => {
      let last = -1, stuckSince = 0, elapsed = 0, nudged = false;
      const timer = setInterval(() => {
        if (gamePaused) return;
        if (token !== epoch || danceAudio !== track) { clearInterval(timer); log(`dance wait stopped: ${token !== epoch ? 'story moved on' : 'track replaced'}`, 'warn'); resolve(false); return; }
        if (track.error) { clearInterval(timer); log(`dance track error ${track.error.code}`, 'error'); resolve(false); return; }
        if (track.ended || track.currentTime >= seconds) { clearInterval(timer); resolve(true); return; }
        elapsed += 25;
        if (track.currentTime !== last) { last = track.currentTime; stuckSince = 0; } else { stuckSince += 25; }
        if (stuckSince >= 1500 && !nudged) { nudged = true; log(`dance track stalled at ${track.currentTime.toFixed(1)} s; nudging`, 'warn'); track.play().catch((e) => log('nudge refused: ' + (e && e.name), 'error')); }
        if (elapsed >= (seconds + 6) * 1000) { clearInterval(timer); log(`dance wait timed out at ${track.currentTime.toFixed(1)} s; moving on`, 'warn'); resolve(true); }
      }, 25);
    });
  }

  /* ───────────────────── the interpreter ───────────────────── */
  // Runs beats in order. Returns the token the caller should continue with (an
  // ask hands back a NEW epoch once the card is accepted), or -1 when the story
  // moved on underneath us (dev jump, restart) and the caller must stop.
  async function runBeats(beats, token) {
    for (const b of beats) {
      if (token !== epoch) return -1;
      token = await runBeat(b, token);
      if (token < 0 || token !== epoch) return -1;
    }
    return token;
  }
  async function playHeld(beat, token, fn) {
    const started = performance.now(); await fn();
    if (beat.hold && token === epoch) { const remaining = beat.hold - (performance.now() - started); if (remaining > 0) await wait(remaining); }
  }
  async function runBeat(b, token) {
    switch (b.op) {
      case 'say':
        await playHeld(b, token, () => playCue(b.cue, { text: b.text })); return token;
      case 'play':
        await playCue(b.cue); return token;
      case 'sfx':
        if (b.channel === 'overlay') {
          if (b.wait) await playHeld(b, token, () => playOverlayCueAndWait(b.cue, b.volume));
          else playOverlayCue(b.cue, b.volume);
        } else await playHeld(b, token, () => playCue(b.cue));
        return token;
      case 'bed':
        if (b.stop) { stopBed(); return token; }
        if (b.crossfade) { const c = cueEntry(b.cue); if (c.file) await crossfadeBedFile(fileUrl(c), typeof b.volume === 'number' ? b.volume : c.volume); else log(`bed ${b.cue} missing`, 'warn'); return token; }
        await playBed(b.cue, b.volume); return token;
      case 'wait':
        await wait(b.ms); return token;
      case 'together':
        await Promise.all(b.beats.map((x) => runBeat(x, token))); return token;
      case 'group':
        return runBeats(b.beats, token);
      case 'shuffle': {                                   // the same beats, in a fresh random order each play
        const order = b.beats.slice(); for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
        return runBeats(order, token);
      }
      case 'oneof':                                       // one of the beats, at random
        return b.beats.length ? runBeat(b.beats[Math.floor(Math.random() * b.beats.length)], token) : token;
      case 'music':
        if (b.stop) { stopDanceTrack(); return token; }
        if (typeof b.at === 'number') { if (danceAudio) await waitForDanceTime(danceAudio, b.at, token); return token; }
        await startDanceTrack(b.cue); return token;
      case 'duck': {
        const track = danceAudio;
        if (track) { const full = cueEntry(track.__cue).volume; setVol(track, full * .30); await playCue(b.cue, { text: b.text }); if (danceAudio === track && !track.ended) setVol(track, full); }
        else await playCue(b.cue, { text: b.text });
        return token;
      }
      case 'tapwindow':
        return runTapWindow(b, token);
      case 'ask':
        return runAsk(b, token);
      default:
        log(`unknown beat ${b.op}`, 'error'); return token;
    }
  }
  // An optional tap: for `ms` after this point, tapping `card` plays the beats once
  // (the fuel-overflow gag); otherwise the story simply carries on.
  function runTapWindow(b, token) {
    return new Promise((resolve) => {
      let open = true;
      const close = () => { open = false; clearTimeout(timer); if (tapWindow && tapWindow.owner === b) tapWindow = null; };
      const timer = setTimeout(() => { if (open) { close(); resolve(token); } }, b.ms);
      tapWindow = { owner: b, card: b.card, cancel: () => { close(); resolve(-1); },
        fire: async () => { if (!open) return; close(); const t = await runBeats(b.beats, token); resolve(t); } };
    });
  }
  // The question machine (a port of arm / scheduleHints / acceptCard).
  function runAsk(b, token) {
    return new Promise((resolve) => {
      invalidate(); state = 'question'; expected = b.card; hintIndex = 0; renderWanted(b.card);
      setStatus(`Waiting for ${cardInfo(b.card).label}.`);
      const t = epoch; pendingAsk = { card: b.card, resolve };
      const early = earlyScan; earlyScan = null;
      const tooEarly = b.tooEarly || [];
      const soon = early && early.card === b.card && performance.now() - early.at < EARLY_SCAN_MS;
      if (soon && !tooEarly.length) {
        log(`early scan of ${b.card} accepted`); setTimeout(() => { if (t === epoch) acceptCard(b.card, 'early'); }, 0); return;
      }
      // An ask with "too early:" lines (an action comes first — wear the cap): a tap made before the
      // ask does not count; Coco says those lines (taps during them do not count either), then asks.
      const first = soon ? (async () => {
        log(`early scan of ${b.card} — too early, not accepted`); state = 'narrative';
        for (const x of tooEarly) { if (t !== epoch) return; await runBeat(x, t); }
        if (t === epoch) { state = 'question'; earlyScan = null; }
      })() : Promise.resolve();
      first.then(() => (t === epoch && b.prompt ? runBeat(b.prompt, t) : undefined)).then(async () => {
        if (t !== epoch) return;
        for (const a of b.afterPrompt) { await runBeat(a, t); if (t !== epoch) return; }
        scheduleHints(b.hints, t);
        if (b.remind) b.remind.at.forEach((delay) => reminderTimers.push(setTimeout(() => { if (t === epoch && state === 'question') runBeat(b.remind.beat, t); }, delay)));
      });
    });
  }
  function scheduleHints(hints, token) {
    clearTimers();
    story.hintDelays.forEach((ms, i) => {
      if (!hints[i]) return;
      hintTimers.push(setTimeout(async () => { if (token !== epoch || state !== 'question' || hintIndex > i) return; hintIndex = i + 1; setStatus('Coco is helping…'); await runBeat(hints[i], token); }, ms));
    });
  }
  function acceptCard(card, source = 'reader') {
    if (state === 'done' || state === 'idle') return;
    // Right card → the sparkle (the story waits for it, then plays its own reward sound and line);
    // wrong card → the boing (then the story's warm redirect). A tap while Coco is talking is silent
    // and remembered (Dilpesh, 3 Oct: the tick was inaudible on a phone, removed).
    if (state === 'question' && card === expected) {
      clearTimers(); stopForeground(); epoch++; state = 'success'; expected = null; hideQuestion();
      setStatus(`Accepted ${cardInfo(card).label}.`);
      cardsDone.add(card); progressDone = cardsDone.size; setProgress(progressDone);
      const p = pendingAsk; pendingAsk = null; const t = epoch;
      if (p) playOverlayCueAndWait(story.correctSound, 1).then(() => p.resolve(t));
      return;
    }
    if (state === 'question') {
      setStatus('Try another card.', 'warn');
      if (!story.wrong.length) { playOverlayCue(story.wrongSound, 1); return; }
      const variant = story.wrong[wrongVariant++ % story.wrong.length]; const t = epoch;
      (async () => {
        await playOverlayCueAndWait(story.wrongSound, 1);
        for (const x of variant) { if (t !== epoch || state !== 'question') return; await runBeat(x, t); }
      })();
      return;
    }
  }
  function handleScan(raw) {
    const uid = norm(raw); if (!uid) return;
    // A card this story doesn't list (another game's card, an extra/decoy card on the table) is a
    // wrong card: during a question it gets the boing and the warm redirect (Dilpesh, 3 Oct).
    const card = lookupCard(raw) || UNLISTED; log(`scan ${uid} → ${card === UNLISTED ? 'not in this story (wrong card)' : card}`);
    if (tapWindow && card === tapWindow.card) { tapWindow.fire(); return; }
    if (state === 'narrative' || state === 'success') {
      // Coco is still talking: remember the tap (silently since 3 Oct — no tick; story.tapSound is null). If it is the card the next question wants, it counts when the question arms;
      // a wrong one is never punished and never advances the story.
      earlyScan = { card, at: performance.now() };
      if (story.tapSound) playOverlayCue(story.tapSound, .5);
      setStatus('Got it — listen…');
      return;
    }
    acceptCard(card, 'reader');
  }

  /* ───────────────────── running the story ───────────────────── */
  async function runFrom(sceneIndex, token) {
    for (let i = sceneIndex; i < story.scenes.length; i++) {
      if (token !== epoch) return;
      sceneCursor = i; state = state === 'question' ? state : 'narrative';
      const label = $('kScene'); if (label && !label.dataset.done) label.textContent = story.scenes[i].title;
      token = await runBeats(story.scenes[i].beats, token);
      if (token < 0) return;
    }
    finish();
  }
  async function startStory() {
    unlockAudio(); if (gamePaused) resumeGame(); state = 'narrative'; setStatus(pack ? `Starting — for ${childName}…` : 'Starting…'); cardsDone.clear(); progressDone = 0; setProgress(0); earlyScan = null;
    const token = ++epoch; await loadManifest();
    await Promise.race([clipsReady(firstCues()), wait(4000)]);
    await takeWakeLock();
    runFrom(0, token);
  }
  async function finish() {
    state = 'done'; const label = $('kScene'); if (label) { label.textContent = 'Mission complete'; label.dataset.done = '1'; }
    setStatus('Mission complete. Bye-bye, Captain!'); stopBed();
    if (wakeLock) { try { await wakeLock.release(); } catch (e) {} wakeLock = null; }
  }
  async function takeWakeLock() {
    if ('wakeLock' in navigator) { try { wakeLock = await navigator.wakeLock.request('screen'); } catch (e) { log('Wake lock unavailable; keep the screen awake manually.', 'warn'); } }
  }
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && state !== 'idle' && state !== 'done' && 'wakeLock' in navigator) navigator.wakeLock.request('screen').then((w) => { wakeLock = w; }).catch(() => {});
  });
  // Developer mode: jump straight to a scene. Resets the story state and runs the
  // scene's "on jump:" beats (usually the bed it expects) before the scene itself.
  async function devJump(i) {
    const scene = story.scenes[i]; if (!scene) return;
    invalidate(); stopBed(); stopDanceTrack(); if (gamePaused) resumeGame(); hideQuestion(); unlockAudio(); earlyScan = null;
    state = 'narrative'; setStatus('Jumped to: ' + scene.title); log('dev jump → ' + scene.title);
    // progress = the cards already asked for before this scene
    cardsDone.clear(); for (let s = 0; s < i; s++) walk(story.scenes[s].beats, (b) => { if (b.op === 'ask') cardsDone.add(b.card); });
    progressDone = cardsDone.size; setProgress(progressDone);
    const token = ++epoch;
    if (!manifest || !Object.keys(manifest).length) await loadManifest();
    for (const b of scene.onJump) { await runBeat(b, token); if (token !== epoch) return; }
    runFrom(i, token);
  }
  function walk(beats, fn) { for (const b of beats) { fn(b); if (Array.isArray(b.beats)) walk(b.beats, fn); } }

  /* ───────────────────── variants ───────────────────── */
  // A variant never touches audio: it decides which tagged beats play.
  //   exclude: joke          drop every beat tagged #joke
  //   keep: effort           ...but keep beats tagged #effort even if excluded
  //   keep: joke every 2     keep the 1st, 3rd, 5th… #joke beat
  //   hints at: 6s 12s 20s   a different hint ladder
  function applyVariant(v) {
    if (!v) return;
    const excl = new Set(v.exclude || []), keep = new Set(v.keepAlways || []), every = v.keepEvery || {}, counts = {};
    const drop = (b) => {
      const tags = b.tags || [];
      if (tags.some((t) => keep.has(t))) return false;
      if (tags.some((t) => excl.has(t))) return true;
      for (const t of tags) if (every[t]) { counts[t] = (counts[t] || 0) + 1; if ((counts[t] - 1) % every[t] !== 0) return true; }
      return false;
    };
    const filter = (beats) => { const out = []; for (const b of beats) { if (drop(b)) continue; if (Array.isArray(b.beats)) b.beats = filter(b.beats); out.push(b); } return out; };
    story.scenes.forEach((s) => { s.beats = filter(s.beats); });
    if (v.set && v.set.hintDelays) story.hintDelays = v.set.hintDelays;
    log(`variant: ${v.name}`);
  }

  /* ───────────────────── cards ───────────────────── */
  function cardInfo(id) { return story.cards.find((c) => c.id === id) || { id, label: id, icon: '🎴' }; }
  function loadCards() {
    cardMap = {}; story.cards.forEach((c) => { cardMap[c.registry] = c.id; cardMap[c.id] = c.id; });
    uidToCard = {}; Object.entries(story.uids || {}).forEach(([u, c]) => { uidToCard[norm(u)] = c; });
    if (!window.CardRegistry) {
      // the registry's storage key, so a card taught in any game is known here too
      try { const s = JSON.parse(localStorage.getItem('kahaniCards') || '{}'); for (const u in s) { const c = cardMap[String(s[u]).toUpperCase()]; if (c) uidToCard[norm(u)] = c; } } catch (e) {}
    }
  }
  function lookupCard(raw) {
    // the registry (taught cards included) first; then the UIDs the compiler copied from cards.json
    if (window.CardRegistry) { const canon = CardRegistry.lookup(raw); if (canon && cardMap[canon]) return cardMap[canon]; }
    return uidToCard[norm(raw)] || null;
  }

  /* ───────────────────── UI ───────────────────── */
  function render() {
    const root = $('kahani') || document.body;
    root.innerHTML = `
      <main class="k-main">
        <div class="eyebrow">${esc(story.title)}</div>
        <h1>${esc(story.heading || story.title)}</h1>
        <section id="kWelcome" class="panel">
          <h2>Ready to play?</h2>
          <p class="muted">About ${story.minutes} minutes · ${story.cards.length} cards</p>
          <label class="muted small" for="kName">Child's name (optional — Coco will use it if there are recordings)</label>
          <input id="kName" type="text" autocomplete="off" autocapitalize="words" placeholder="e.g. Rida" value="${esc(params.get('name') || '')}">
          <div class="actions"><button class="primary" id="kStart">Start</button><button id="kScreen" class="hide">Play on screen (developer)</button></div>
          <div id="kWelcomeStatus" class="status"></div>
        </section>
        <section id="kPlay" class="panel hide" aria-live="polite">
          <div class="eyebrow" id="kScene"></div>
          <div id="kStatus" class="status">Starting…</div>
          <div class="progress"><i id="kBar"></i></div>
          <div id="kQuestion" class="wanted hide"><span class="icon" id="kWantIcon">🎧</span><strong id="kWantLabel">Listen…</strong></div>
          <div id="kTapGrid" class="tapgrid hide"></div>
          <div class="actions"><button id="kPause" aria-pressed="false">⏸ Pause</button><button id="kNext" class="hide">Next cue</button><select id="kJump" class="hide" aria-label="Jump to scene"></select><select id="kVariant" class="hide" aria-label="Variant"></select></div>
          <div id="kLog" class="log hide"></div>
          <div id="kDevLine" class="muted small hide">Developer mode · Ctrl+Shift+D or ?dev=0 to leave</div>
        </section>
      </main>`;
    $('kStart').onclick = () => begin('reader'); $('kScreen').onclick = () => begin('screen');
    $('kPause').onclick = () => (gamePaused ? resumeGame() : pauseGame());
    $('kNext').onclick = () => { if (devMode) { stopForeground(); setStatus('Skipped to the next cue.'); } };
    $('kJump').innerHTML = '<option value="">Jump to scene…</option>' + story.scenes.map((s, i) => `<option value="${i}">${esc(s.title)}</option>`).join('');
    $('kJump').onchange = (e) => { const v = e.target.value; e.target.value = ''; if (v !== '') devJump(+v); };
    const names = Object.keys(story.variants || {});
    $('kVariant').innerHTML = '<option value="">Variant: none</option>' + names.map((n) => `<option value="${n}"${n === variantName ? ' selected' : ''}>Variant: ${esc(story.variants[n].name || n)}</option>`).join('');
    $('kVariant').onchange = (e) => { const u = new URL(location.href); if (e.target.value) u.searchParams.set('v', e.target.value); else u.searchParams.delete('v'); location.href = u.toString(); };
    renderTapGrid(); applyDevMode();
  }
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function setProgress(n) { const bar = $('kBar'); if (bar) bar.style.width = Math.round(n / story.cards.length * 100) + '%'; }
  // Production mode never says which card is wanted; the child listens to the story.
  function renderWanted(card) {
    const c = cardInfo(card); $('kQuestion').classList.remove('hide');
    if (devMode) { $('kWantIcon').textContent = c.icon; $('kWantLabel').textContent = `${c.label} (dev)`; }
    else { $('kWantIcon').textContent = '🎧'; $('kWantLabel').textContent = 'Coco की बात सुनो… फिर card लाओ'; }
    if (mode === 'screen' || devMode) $('kTapGrid').classList.remove('hide');
  }
  function renderTapGrid() {
    $('kTapGrid').innerHTML = story.cards.map((c) => `<button class="card tap" data-card="${c.id}"><span class="icon">${c.icon}</span><small>${esc(c.label)}</small></button>`).join('');
    $('kTapGrid').querySelectorAll('button').forEach((b) => { b.onclick = () => { const card = b.dataset.card; if (tapWindow && card === tapWindow.card) tapWindow.fire(); else acceptCard(card, 'screen'); }; });
  }
  function hideQuestion() { $('kQuestion').classList.add('hide'); $('kTapGrid').classList.add('hide'); }
  function applyDevMode() {
    ['kScreen', 'kNext', 'kJump', 'kVariant', 'kDevLine'].forEach((id) => $(id).classList.toggle('hide', !devMode));
    if (!devMode) $('kLog').classList.add('hide');
  }
  function setDevMode(on) { devMode = !!on; try { localStorage.setItem(DEV_KEY, devMode ? '1' : '0'); } catch (e) {} applyDevMode(); log(devMode ? 'developer mode on' : 'developer mode off'); }
  function begin(modeName) {
    unlockAudio(); mode = modeName; loadCards();
    const typed = ($('kName') && $('kName').value) || ''; if ($('kName')) $('kName').blur();
    const ready = loadManifest().then(() => loadNamePack(typed)).then(() => { if (pack) setStatus(`Playing for ${childName}.`); else if (typed.trim()) setStatus(`No recordings for "${typed.trim()}" yet — playing as Captain.`, 'warn'); });
    const go = () => ready.then(() => {
      $('kWelcome').classList.add('hide'); $('kPlay').classList.remove('hide');
      if (mode === 'reader' && window.ReaderCheck && !ReaderCheck.known()) ReaderCheck.run({ onWorking: startStory, onSkip: () => { mode = 'screen'; startStory(); } }); else startStory();
    });
    if (window.StoryIntro && !StoryIntro.seen(story.key)) StoryIntro.show({ key: story.key, title: story.title, minutes: story.minutes, cards: story.cards.map((c) => ({ icon: c.icon, label: c.label })), activities: story.activities, onStart: go });
    else go();
  }

  /* ───────────────────── input ───────────────────── */
  function wireInput() {
    const guarded = window.ScanGuard ? ScanGuard.wrap(handleScan) : handleScan;
    window.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) { e.preventDefault(); setDevMode(!devMode); return; }
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;   // the name box, not the reader
      if (e.ctrlKey || e.metaKey || e.altKey) return;             // never leaks into the scan buffer
      if (e.key === 'Enter') { e.preventDefault(); const v = inputBuffer; inputBuffer = ''; if (v) guarded(v); }
      else if (e.key.length === 1) inputBuffer += e.key;
    });
    document.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) setTimeout(() => b.blur(), 0); });
  }

  /* ───────────────────── boot ───────────────────── */
  async function boot(opts = {}) {
    if (typeof opts.story === 'string') { const r = await fetch(opts.story, { cache: 'no-store' }); story = await r.json(); } else story = opts.story;
    AUDIO_DIR = story.audioDir || 'audio/'; CACHE_TAG = story.cacheTag || 'v1'; LIB_DIR = story.libraryDir || '../../library/';
    story.tapSound = null;   // no tick (Dilpesh, 3 Oct: inaudible on a phone) — a story's "tap sound:" line is ignored
    story.correctSound = story.correctSound || 'lib:tap_correct';   // right card: the sparkle, trimmed to start at once
    story.wrongSound = story.wrongSound || 'lib:boing';             // wrong card
    // The engine now plays these itself, so a story's own copy right after an ask (sfx magic_sparkle)
    // or at the start of a wrong-card response (sfx boing) is dropped — nothing plays twice, and
    // games built before this need no rebuild.
    const named = (b, n) => b && b.op === 'sfx' && (b.cue === 'lib:' + n || ((story.clips || {})[b.cue] || {}).name === n);
    story.scenes.forEach((sc) => { for (let i = sc.beats.length - 1; i > 0; i--) if (sc.beats[i - 1].op === 'ask' && named(sc.beats[i], 'magic_sparkle')) sc.beats.splice(i, 1); });
    story.wrong = story.wrong.map((v) => (named(v[0], 'boing') ? v.slice(1) : v));
    if (params.has('dev')) devMode = params.get('dev') !== '0'; else { try { devMode = localStorage.getItem(DEV_KEY) === '1'; } catch (e) {} }
    if (params.has('dev')) { try { localStorage.setItem(DEV_KEY, devMode ? '1' : '0'); } catch (e) {} }
    variantName = params.get('v') || '';
    if (variantName && story.variants && story.variants[variantName]) applyVariant(story.variants[variantName]);
    else if (variantName) console.warn('no such variant: ' + variantName);
    render(); wireInput(); loadManifest();
  }

  return { boot, acceptCard, handleScan, devJump, setDevMode,
    // for tests
    _state: () => ({ state, expected, epoch, progressDone, sceneCursor, devMode, variant: variantName, paused: gamePaused, hintIndex, tapWindow: tapWindow ? tapWindow.card : null, earlyScan: earlyScan && earlyScan.card, name: childName, pack: pack && pack.slug, scenes: story && story.scenes.length }),
    _story: () => story };
})();
