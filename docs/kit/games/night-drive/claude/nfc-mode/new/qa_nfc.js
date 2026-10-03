// qa_nfc.js — the Phone NFC mode of Coco की Night Drive, in a real headless Chromium
// with a fake NDEFReader (Chromium on a laptop has no NFC).
//
//   node docs/kit/games/night-drive/qa_nfc.js            (DOCS=<docs dir> to point elsewhere)
//
// Checks: a browser without Web NFC shows the NFC button disabled and the RFID start
// still works; with NFC, one tap starts the story and skips the reader check; an
// unknown tag is ignored outside developer mode and teachable inside it; a taught
// tag is accepted, a taught tag for another card gets "Try another card"; the same
// tag resting on the phone counts once (scan guard); a tap while Coco talks is an
// early scan; the permission prompt path needs a second tap; a refused permission
// leaves the welcome page usable; and, with four taught tags, the whole story plays
// to the end by NFC alone.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
// docs/ is found by walking up from wherever this file sits (the game folder, or the claude/ package)
function findDocs() { let d = __dirname; for (let i = 0; i < 8; i++) { if (fs.existsSync(path.join(d, 'kit', 'engine', 'kahani.js'))) return d; d = path.dirname(d); } return null; }
const ROOT = process.env.DOCS || findDocs();
if (!ROOT) { console.log('✗ could not find docs/kit — set DOCS=<path to docs>'); process.exit(2); }
const PORT = 8771, GAME = '/kit/games/night-drive/index.html';
const TAG = { FUEL: '04:A1:B2:C3:D4:E5:01', TORCH: '04:A1:B2:C3:D4:E5:02', WATER: '04:A1:B2:C3:D4:E5:03', MUSIC: '04:A1:B2:C3:D4:E5:04', STRAY: '04:FF:EE:DD:CC:BB:99' };

function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.mp3': 'audio/mpeg', '.css': 'text/css' };
  return http.createServer((req, res) => {
    fs.readFile(path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': types[path.extname(req.url.split('?')[0])] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(data);
    });
  }).listen(PORT);
}
const INIT = `
  window.__plays = [];
  const _play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () { const src = this.getAttribute('src') || ''; if (!src.startsWith('data:')) {
    let name = src; if (src.startsWith('blob:') && window.__blobNames) name = window.__blobNames.get(src) || src;
    const parts = name.split('?')[0].split('/'); window.__plays.push((parts.includes('library') ? 'lib/' : '') + parts.pop().replace('.mp3', '')); } return _play.apply(this, arguments); };
  const _create = URL.createObjectURL; window.__blobNames = new Map(); const _fetch = window.fetch;
  window.fetch = async function (u, o) { const r = await _fetch(u, o); const url = String(u); if (url.split('?')[0].endsWith('.mp3')) { const _b = r.blob.bind(r); r.blob = async () => { const b = await _b(); b.__url = url; return b; }; } return r; };
  URL.createObjectURL = function (b) { const u = _create(b); if (b && b.__url) window.__blobNames.set(u, b.__url); return u; };
  localStorage.setItem('storyIntro:night-drive', '1'); localStorage.setItem('kahaniDevMode', '0');
`;
// a fake Web NFC: mode 'granted' resolves at once, 'prompt' after 4 s (the user reading Chrome's
// permission sheet), 'denied' rejects with NotAllowedError. window.__tap(serial) delivers a reading.
const FAKE_NFC = (mode) => `
  window.__nfc = { mode: '${mode}', readers: [], scans: 0 };
  class NDEFReader extends EventTarget {
    constructor() { super(); window.__nfc.readers.push(this); }
    scan() { window.__nfc.scans++; const m = window.__nfc.mode;
      if (m === 'denied') { const e = new Error('NFC permission request denied.'); e.name = 'NotAllowedError'; return Promise.reject(e); }
      if (m === 'prompt') return new Promise((r) => setTimeout(r, 4000));
      return Promise.resolve(); }
  }
  window.NDEFReader = NDEFReader;
  window.__tap = (serial) => { const r = window.__nfc.readers[window.__nfc.readers.length - 1]; if (!r) throw new Error('no reader');
    const ev = new Event('reading'); ev.serialNumber = serial; ev.message = { records: [] }; r.dispatchEvent(ev); };
`;
let pass = 0, fail = 0;
const ok = (cond, what) => { if (cond) { pass++; console.log('  ✓ ' + what); } else { fail++; console.log('  ✗ ' + what); } };
const st = (page) => page.evaluate('Kahani._state()');
const tap = (page, serial) => page.evaluate((s) => window.__tap(s), serial);
const text = (page, sel) => page.$eval(sel, (e) => e.textContent).catch(() => '');
const untilQuestion = (page, card) => page.waitForFunction((c) => { const s = Kahani._state(); return s.state === 'question' && s.expected === c; }, card, { timeout: 120000 });
const untilNotQuestion = (page) => page.waitForFunction(() => Kahani._state().state !== 'question', null, { timeout: 15000 }).catch(() => {});

async function open(browser, { nfc, query = '', teach = {} } = {}) {
  const ctx = await browser.newContext(); const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.addInitScript(INIT);
  if (nfc) await page.addInitScript(FAKE_NFC(nfc));
  await page.goto(`http://localhost:${PORT}${GAME}${query}`);
  await page.waitForFunction('Kahani._story() && document.getElementById("kNfc")', null, { timeout: 10000 }).catch(() => {
    console.log('✗ the served game has no Phone NFC button — copy modified/index.html and new/nfc.js into docs/kit/games/night-drive/ first'); process.exit(2); });
  for (const [serial, canon] of Object.entries(teach)) await page.evaluate(([s, c]) => CardRegistry.teach(s, c), [serial, canon]);
  return { ctx, page, errors };
}

(async () => {
  const server = serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  console.log('A. a browser without Web NFC (iPhone Safari, a laptop)');
  {
    const { ctx, page, errors } = await open(browser, { nfc: null });
    ok(await page.$eval('#kNfc', (b) => b.disabled), 'the Phone NFC button is there but disabled');
    ok(/Chrome on Android/.test(await text(page, '#kNfcLine')), 'and says why: ' + (await text(page, '#kNfcLine')).trim());
    ok((await text(page, '#kStart')).includes('RFID'), 'the engine start is labelled "Start · RFID reader"');
    await page.evaluate(() => localStorage.setItem('readerCheck:ok', '1'));
    await page.click('#kStart'); await page.waitForTimeout(800);
    ok((await st(page)).state !== 'idle', 'RFID start still starts the story (engine path untouched)');
    ok(!errors.length, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
    await ctx.close();
  }

  console.log('B. Phone NFC, permission already granted: start, teach, answer');
  {
    const { ctx, page, errors } = await open(browser, { nfc: 'granted' });
    await page.evaluate(() => localStorage.removeItem('readerCheck:ok'));
    await page.click('#kNfc'); await page.waitForTimeout(800);
    ok(await page.evaluate('window.__nfc.scans') === 1, 'NDEFReader.scan() was called inside the tap');
    ok((await st(page)).state !== 'idle', 'one tap starts the story');
    ok(!(await page.$('#readerCheck')), 'the reader check overlay is skipped');
    ok(await page.evaluate(() => localStorage.getItem('readerCheck:ok')) === null, 'and nothing about the reader was written to storage');
    ok(await page.$eval('#kNfc', (b) => b.disabled) && await page.$eval('#kStart', (b) => b.disabled), 'both start buttons are disabled once playing');

    await untilQuestion(page, 'FUEL');
    await tap(page, TAG.FUEL); await page.waitForTimeout(300);
    let s = await st(page);
    ok(s.state === 'question' && s.progressDone === 0, 'an unknown tag outside developer mode does not count');
    ok(/developer mode/.test(await text(page, '#kNfcPlayLine')), 'and the line says to teach it in developer mode');
    ok(await page.$eval('#kNfcTeach', (e) => e.classList.contains('hide')), 'no teach panel outside developer mode');

    await page.evaluate(() => Kahani.setDevMode(true));
    ok(!(await page.$eval('#kNfcTaught', (e) => e.classList.contains('hide'))), 'developer mode shows the taught-tags list');
    await page.waitForTimeout(1600);                                   // past the scan guard's repeat window
    await tap(page, TAG.FUEL); await page.waitForTimeout(300);
    ok(!(await page.$eval('#kNfcTeach', (e) => e.classList.contains('hide'))), 'in developer mode the unknown tag opens the teach panel');
    const choices = await page.$$eval('#kNfcTeach button[data-canon]', (bs) => bs.map((b) => b.dataset.canon));
    ok(choices.join(' ') === 'FUEL TORCH WATER MUSIC', 'offering the four registry cards of this story: ' + choices.join(' '));
    await page.click('#kNfcTeach button[data-canon="FUEL"]'); await page.waitForTimeout(400);
    s = await st(page);
    ok(s.state !== 'question' && s.progressDone === 1, 'teaching it as FUEL counts it at once (progress 1/4)');
    ok(await page.evaluate((t) => CardRegistry.lookup(t), TAG.FUEL) === 'FUEL', 'the serial is in the shared card registry');
    ok(JSON.stringify(await page.evaluate('NightDriveNFC.taught()')) === JSON.stringify({ [TAG.FUEL]: 'FUEL' }), 'and in the taught list for cards.json');
    ok(/04:A1:B2:C3:D4:E5:01.*FUEL/.test(await text(page, '#kNfcTaught')), 'which the developer line shows');

    // a tap while Coco is talking is an early scan, and the same tag resting on the phone counts once
    await page.waitForFunction(() => Kahani._state().state === 'narrative', null, { timeout: 30000 });
    const before = (await page.evaluate('window.__plays')).filter((p) => p === 'lib/tap').length;
    await page.waitForTimeout(300);
    await tap(page, TAG.FUEL); await tap(page, TAG.FUEL); await page.waitForTimeout(400);
    const after = (await page.evaluate('window.__plays')).filter((p) => p === 'lib/tap').length;
    ok((await st(page)).earlyScan === 'FUEL', 'a known tag while Coco talks is remembered as an early scan');
    ok(after - before === 1, 'the same tag twice in a row is one tap (tap sound played once)');

    await untilQuestion(page, 'FLASHLIGHT');
    await page.waitForTimeout(1600);
    await tap(page, TAG.FUEL); await page.waitForTimeout(400);
    s = await st(page);
    ok(s.state === 'question' && /another card/i.test(await text(page, '#kStatus')), 'a taught tag for the wrong card gets "Try another card"');
    await page.waitForTimeout(1600);
    await tap(page, TAG.TORCH); await page.waitForTimeout(300);
    await page.click('#kNfcTeach button[data-canon="TORCH"]'); await page.waitForTimeout(400);
    s = await st(page);
    ok(s.progressDone === 2, 'a tag taught as TORCH answers the FLASHLIGHT question (registry name → story card)');
    ok(!errors.length, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
    await ctx.close();
  }

  console.log('C. the first-time permission prompt (scan resolves after 4 s)');
  {
    const { ctx, page } = await open(browser, { nfc: 'prompt' });
    await page.click('#kNfc'); await page.waitForTimeout(500);
    ok(await page.$eval('#kNfc', (b) => b.disabled), 'the button waits while Chrome asks');
    ok((await st(page)).state === 'idle', 'the story does not start behind the prompt');
    await page.waitForTimeout(4200);
    ok(!(await page.$eval('#kNfc', (b) => b.disabled)) && /tap to start/i.test(await text(page, '#kNfc')), 'after the prompt the button says "tap to start"');
    ok((await st(page)).state === 'idle', 'still idle until that second tap');
    await page.click('#kNfc'); await page.waitForTimeout(800);
    ok((await st(page)).state !== 'idle', 'the second tap starts the story');
    ok(await page.evaluate('window.__nfc.scans') === 1, 'without a second scan()');
    await ctx.close();
  }

  console.log('D. permission refused');
  {
    const { ctx, page } = await open(browser, { nfc: 'denied' });
    await page.click('#kNfc'); await page.waitForTimeout(500);
    ok((await st(page)).state === 'idle', 'the story does not start');
    ok(/not allowed/i.test(await text(page, '#kNfcLine')), 'the line explains: ' + (await text(page, '#kNfcLine')).trim());
    ok(!(await page.$eval('#kNfc', (b) => b.disabled)) && !(await page.$eval('#kStart', (b) => b.disabled)), 'both start buttons are usable again');
    await page.evaluate(() => localStorage.setItem('readerCheck:ok', '1'));
    await page.click('#kStart'); await page.waitForTimeout(800);
    ok((await st(page)).state !== 'idle', 'so the RFID reader can be chosen instead');
    await ctx.close();
  }

  console.log('E. the whole story by NFC, four taught tags, production mode');
  {
    const { ctx, page, errors } = await open(browser, { nfc: 'granted', teach: { [TAG.FUEL]: 'FUEL', [TAG.TORCH]: 'TORCH', [TAG.WATER]: 'WATER', [TAG.MUSIC]: 'MUSIC' } });
    const story = await page.evaluate('Kahani._story()');
    const tagOf = {}; story.cards.forEach((c) => { tagOf[c.id] = TAG[c.registry]; });
    await page.click('#kNfc'); await page.waitForTimeout(500);
    const asked = []; let gagDone = false; const t0 = Date.now();
    while (Date.now() - t0 < 8 * 60 * 1000) {
      const s = await st(page);
      if (s.state === 'done') break;
      if (s.tapWindow && !gagDone) { gagDone = true; await tap(page, tagOf[s.tapWindow]); await page.waitForTimeout(300); continue; }
      if (s.state === 'question' && s.expected) {
        asked.push(s.expected); await page.waitForTimeout(300);
        await tap(page, tagOf[s.expected]); await untilNotQuestion(page); await page.waitForTimeout(200); continue;
      }
      await page.waitForTimeout(100);
    }
    const s = await st(page);
    ok(s.state === 'done', `reached the end in ${Math.round((Date.now() - t0) / 1000)} s · asked ${asked.join(' ')} · progress ${s.progressDone}/${story.cards.length}`);
    ok(await page.$eval('#kTapGrid', (e) => e.classList.contains('hide')), 'the on-screen card tray never appeared (production mode)');
    ok(!errors.length, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
    await ctx.close();
  }

  await browser.close(); server.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
