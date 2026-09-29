// qa_parity.js — proves the engine plays Jungle Rescue English exactly as the
// hand-written standalone build does.
//
// Both pages are driven the same way in a real (headless) Chromium: wait for a
// question, tap the card (a wrong one first on ROPE, a 9 s pause for a hint on
// FIRST AID, the fuel-overflow gag when its window opens), and record every
// HTMLMediaElement.play() — file name and whether it loops. The two recordings
// must be identical, clip for clip, in order. Timing is compared loosely.
//
//   node docs/kit/qa/qa_parity.js            (serves a mirror of docs/ on :8765; DOCS=path to override)
//
// The mirror's audio folder holds silent clips of the same names, so the run
// takes ~3 minutes instead of 9 and works without the real 90 MB of audio.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const ROOT = process.env.DOCS || path.resolve(__dirname, '..', '..');
const PORT = 8765;
const ORIGINAL = `/jungle-rescue-english/claude/ios-volume-fix-standalone/index.html`;
const KIT = `/kit/games/jungle-rescue-english/index.html?v=classic`;   // the story without the 29 Sep name lines
const UIDS = { FUEL: ['6359145'], ROPE: ['6374623'], BISCUIT: ['6373651', '5720648'], FIRST_AID: ['6374815'],
  WATER: ['2690428', '2682976'], FLASHLIGHT: ['2692483', '6375577'], BLANKET: ['6375388'], MUSIC: ['6360574'] };

function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.mp3': 'audio/mpeg', '.css': 'text/css' };
  return http.createServer((req, res) => {
    const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    fs.readFile(p, (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
      res.end(data);
    });
  }).listen(PORT);
}

const INIT = `
  window.__plays = []; window.__t0 = performance.now();
  const _play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () {
    const src = this.getAttribute('src') || this.src || '';   // not currentSrc: it lags behind on a reused element
    if (!src.startsWith('data:')) {
      // blob: URLs hide the file name; the pages map cached blobs back to their url
      let name = src;
      if (src.startsWith('blob:') && window.__blobNames) name = window.__blobNames.get(src) || src;
      window.__plays.push({ file: name.split('/').pop().split('?')[0], loop: this.loop, t: Math.round(performance.now() - window.__t0) });
    }
    return _play.apply(this, arguments);
  };
  const _create = URL.createObjectURL;
  window.__blobNames = new Map();
  // record which fetch produced which blob: wrap fetch so the blob's url is known
  const _fetch = window.fetch;
  window.fetch = async function (u, o) { const r = await _fetch(u, o); const url = String(u);
    if (url.split('?')[0].endsWith('.mp3')) { const _blob = r.blob.bind(r); r.blob = async () => { const b = await _blob(); b.__url = url; return b; }; }
    return r; };
  URL.createObjectURL = function (b) { const u = _create(b); if (b && b.__url) window.__blobNames.set(u, b.__url); return u; };
  localStorage.setItem('storyIntro:jungle-rescue-english', '1');
  localStorage.setItem('readerCheck:ok', '1');
`;

async function drive(page, url, getState, label) {
  await page.addInitScript(INIT);
  await page.goto(`http://localhost:${PORT}${url}`);
  if (url === KIT) await page.waitForFunction('Kahani._story()');
  await page.click(url === KIT ? '#kStart' : '#readerMode');
  await page.waitForTimeout(300);
  const intro = await page.$('#si-go'); if (intro) await intro.click();   // the story-intro screen, if shown
  const scan = async (uid) => { await page.keyboard.type(uid); await page.keyboard.press('Enter'); };
  const seen = new Set(); let copy = 0, wrongDone = false, hintDone = false, gagDone = false, biscuits = 0;
  const t0 = Date.now();
  while (Date.now() - t0 < 6 * 60 * 1000) {
    const s = await page.evaluate(getState);
    if (s.state === 'done') return { ms: Date.now() - t0 };
    if (s.gag && !gagDone) { gagDone = true; await scan(UIDS.FUEL[0]); await page.waitForTimeout(300); continue; }
    if (s.state === 'question' && s.expected) {
      const card = s.expected;
      if (card === 'ROPE' && !wrongDone) { wrongDone = true; await scan(UIDS.WATER[0]); await page.waitForTimeout(1500); continue; }
      if (card === 'FIRST_AID' && !hintDone) { hintDone = true; await page.waitForTimeout(9500); }   // hint 1 at 8 s
      if (card === 'BISCUIT') { await page.waitForTimeout(400); }                                   // let the prompt/biscuit line finish
      const uids = UIDS[card]; await scan(uids[copy++ % uids.length]);
      await page.waitForFunction((st) => { const x = eval(st); return !(x.state === 'question'); }, getState, { timeout: 10000 }).catch(() => {});
      await page.waitForTimeout(300);
      continue;
    }
    await page.waitForTimeout(100);
  }
  throw new Error(label + ': did not finish in 6 minutes; state=' + JSON.stringify(await page.evaluate(getState)));
}

(async () => {
  const server = serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext();
  const [pA, pB] = [await ctx.newPage(), await ctx.newPage()];
  const stOrig = `({state: state, expected: expected, gag: fuelGagOpen})`;
  const stKit = `(function(){const s=Kahani._state();return {state:s.state, expected:s.expected, gag:s.tapWindow==='FUEL'}})()`;
  const errors = [];
  for (const p of [pA, pB]) p.on('pageerror', (e) => errors.push(e.message));
  const [a, b] = await Promise.all([drive(pA, ORIGINAL, stOrig, 'original'), drive(pB, KIT, stKit, 'kit')]);
  const playsA = await pA.evaluate('window.__plays'), playsB = await pB.evaluate('window.__plays');
  await browser.close(); server.close();

  // JR_003 → JR_003b and JR_143 → JR_143b are the gender-neutral re-takes of the same lines
  const seq = (p) => p.map((x) => x.file.replace(/^JR_(003|143)b\.mp3$/, 'JR_$1.mp3') + (x.loop ? '(loop)' : ''));
  const sa = seq(playsA), sb = seq(playsB);
  let first = -1; for (let i = 0; i < Math.max(sa.length, sb.length); i++) if (sa[i] !== sb[i]) { first = i; break; }
  console.log(`original: ${sa.length} plays in ${Math.round(a.ms / 1000)} s · kit: ${sb.length} plays in ${Math.round(b.ms / 1000)} s`);
  if (errors.length) console.log('page errors:', errors);
  if (first < 0) {
    // loose timing check: each play should start within 1.5 s of its twin
    let worst = 0; for (let i = 0; i < sa.length; i++) worst = Math.max(worst, Math.abs(playsA[i].t - playsB[i].t));
    console.log(`✓ identical sequence of ${sa.length} plays; worst timing drift ${worst} ms`);
    fs.writeFileSync(path.join(__dirname, 'parity_sequence.txt'), sa.map((s, i) => `${String(playsA[i].t).padStart(7)}  ${String(playsB[i].t).padStart(7)}  ${s}`).join('\n'));
    process.exit(errors.length ? 1 : 0);
  } else {
    console.log(`✗ first difference at play #${first}`);
    for (let i = Math.max(0, first - 4); i < first + 6; i++) console.log(`${i === first ? '>>' : '  '} ${String(sa[i]).padEnd(28)} | ${sb[i]}`);
    process.exit(1);
  }
})();
