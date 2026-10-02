// qa_nfc.js — the Phone NFC mode of Bobo की Birthday Party, in a real headless Chromium
// with a fake NDEFReader (Chromium on a laptop has no NFC).
//
//   node docs/kit/games/bobo-birthday/qa_nfc.js        (DOCS=<docs dir> to point elsewhere)
//
// The fake phone hands over serials the way Chrome on Android does (hex, "c2:23:db:30"),
// built from the real cards.json numbers, so this checks the conversion against the
// cards Dilpesh actually has: no teaching is needed for any of the five Bobo cards.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
function findDocs() { let d = __dirname; for (let i = 0; i < 8; i++) { if (fs.existsSync(path.join(d, 'kit', 'engine', 'kahani.js'))) return d; d = path.dirname(d); } return null; }
const ROOT = process.env.DOCS || findDocs();
if (!ROOT) { console.log('✗ could not find docs/kit — set DOCS=<path to docs>'); process.exit(2); }
const PORT = 8772, GAME = process.env.GAME_PATH || '/kit/games/bobo-birthday/index.html';
// laptop number → the hex serial Chrome reports for that card (bytes reversed back)
const phoneSerial = (dec) => { let n = BigInt(dec); const b = []; for (let i = 0; i < 4; i++) { b.push(Number(n & 255n)); n >>= 8n; }
  return b.map((x) => x.toString(16).padStart(2, '0')).join(':'); };
const LAPTOP = { MUSIC: '0819667906', CAKE: '0088154103', CANDLE: '1778512553', PARTYCAP: '0087959223', BANANA: '1778089577' };
const TAG = Object.fromEntries(Object.entries(LAPTOP).map(([k, v]) => [k, phoneSerial(v)]));
const STRAY = '04:ff:ee:dd:cc:bb:99';

function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.mp3': 'audio/mpeg', '.css': 'text/css' };
  return http.createServer((req, res) => {
    fs.readFile(path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': types[path.extname(req.url.split('?')[0])] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(data);
    });
  }).listen(PORT);
}
const INIT = `localStorage.setItem('storyIntro:bobo-birthday', '1'); localStorage.setItem('kahaniDevMode', '0');`;
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
const untilQuestion = (page) => page.waitForFunction(() => { const s = Kahani._state(); return s.state === 'question' && s.expected; }, null, { timeout: 120000 }).then(() => st(page));
const untilNotQuestion = (page) => page.waitForFunction(() => Kahani._state().state !== 'question', null, { timeout: 15000 }).catch(() => {});

async function open(browser, { nfc, query = '' } = {}) {
  const ctx = await browser.newContext(); const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.addInitScript(INIT);
  if (nfc) await page.addInitScript(FAKE_NFC(nfc));
  await page.goto(`http://localhost:${PORT}${GAME}${query}`);
  await page.waitForFunction('Kahani._story() && document.getElementById("kNfc")', null, { timeout: 10000 }).catch(() => {
    console.log('✗ the served game has no Phone NFC button — copy modified/index.html and new/nfc.js into docs/kit/games/bobo-birthday/ first'); process.exit(2); });
  return { ctx, page, errors };
}

(async () => {
  const server = serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });

  console.log('0. phone serial → laptop number');
  {
    const { ctx, page } = await open(browser, { nfc: 'granted' });
    const c = await page.evaluate(() => BoboNFC.candidates('C2:23:DB:30'));
    ok(c[0] === '0819667906', 'the Speaker card C2 23 DB 30 (from the phone screenshot) → 0819667906, as the laptop shows');
    ok(await page.evaluate(() => CardRegistry.lookup(BoboNFC.candidates('c2:23:db:30')[0])) === 'MUSIC', 'which the card registry knows as MUSIC (the Speaker card)');
    for (const [canon, s] of Object.entries(TAG)) ok(await page.evaluate((x) => { for (const k of BoboNFC.candidates(x)) { const v = CardRegistry.lookup(k); if (v) return v; } return null; }, s) === canon, `${canon}: phone ${s} → ${LAPTOP[canon]} → ${canon}`);
    await ctx.close();
  }

  console.log('A. a browser without Web NFC (iPhone Safari, a laptop)');
  {
    const { ctx, page, errors } = await open(browser, { nfc: null });
    ok(await page.$eval('#kNfc', (b) => b.disabled), 'the Phone NFC button is there but disabled');
    ok(/Chrome on Android/.test(await text(page, '#kNfcLine')), 'and says why');
    await page.evaluate(() => localStorage.setItem('readerCheck:ok', '1'));
    await page.click('#kStart'); await page.waitForTimeout(800);
    ok((await st(page)).state !== 'idle', 'Start · RFID reader still starts the story (engine path untouched)');
    ok(!errors.length, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
    await ctx.close();
  }

  console.log('B. Phone NFC: one tap starts; real cards answer with no teaching; unknown tag teaching');
  {
    const { ctx, page, errors } = await open(browser, { nfc: 'granted' });
    await page.evaluate(() => localStorage.removeItem('readerCheck:ok'));
    await page.click('#kNfc'); await page.waitForTimeout(800);
    ok(await page.evaluate('window.__nfc.scans') === 1, 'NDEFReader.scan() was called inside the tap');
    ok((await st(page)).state !== 'idle', 'one tap starts the story');
    ok(!(await page.$('#readerCheck')), 'the reader check is skipped');
    let s = await untilQuestion(page);
    const first = s.expected;
    const story = await page.evaluate('Kahani._story()');
    const reg = (id) => (story.cards.find((c) => c.id === id) || {}).registry || id;
    await tap(page, STRAY); await page.waitForTimeout(300);
    s = await st(page);
    ok(s.state === 'question' && s.progressDone === 0, 'an unknown tag outside developer mode does not count');
    ok(/developer mode/.test(await text(page, '#kNfcPlayLine')), 'and the line says to teach it in developer mode');
    const wrong = Object.keys(TAG).find((k) => k !== reg(first));
    await page.waitForTimeout(1600);
    await tap(page, TAG[wrong]); await page.waitForTimeout(400);
    ok((await st(page)).state === 'question' && /another card/i.test(await text(page, '#kStatus')), `a real card for the wrong answer (${wrong}) gets "Try another card"`);
    await page.waitForTimeout(1600);
    await tap(page, TAG[reg(first)]); await page.waitForTimeout(400);
    ok((await st(page)).progressDone === 1, `the real ${reg(first)} card answers ${first} straight away (no teaching)`);

    await page.evaluate(() => Kahani.setDevMode(true));
    await page.waitForTimeout(1600);
    await tap(page, STRAY); await page.waitForTimeout(300);
    ok(!(await page.$eval('#kNfcTeach', (e) => e.classList.contains('hide'))), 'in developer mode an unknown tag opens the teach panel');
    const expectKey = await page.evaluate((x) => BoboNFC.teachKey(x), STRAY);
    ok(/^\d+$/.test(expectKey), `it will be taught under a reader-style number (${expectKey}), ready for cards.json`);
    await page.click('#kNfcTeach button[data-canon="CAKE"]'); await page.waitForTimeout(300);
    ok(await page.evaluate((k) => CardRegistry.lookup(k), expectKey) === 'CAKE', 'teaching it stores that number in the shared card registry');
    ok(JSON.stringify(await page.evaluate('BoboNFC.taught()')) === JSON.stringify({ [expectKey]: 'CAKE' }), 'and in the taught list for Copy');
    ok(!errors.length, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
    await ctx.close();
  }

  console.log('C. the first-time permission prompt');
  {
    const { ctx, page } = await open(browser, { nfc: 'prompt' });
    await page.click('#kNfc'); await page.waitForTimeout(500);
    ok((await st(page)).state === 'idle', 'the story does not start behind the prompt');
    await page.waitForTimeout(4200);
    ok(/tap to start/i.test(await text(page, '#kNfc')), 'after the prompt the button says "tap to start"');
    await page.click('#kNfc'); await page.waitForTimeout(800);
    ok((await st(page)).state !== 'idle', 'the second tap starts the story');
    await ctx.close();
  }

  console.log('D. permission refused');
  {
    const { ctx, page } = await open(browser, { nfc: 'denied' });
    await page.click('#kNfc'); await page.waitForTimeout(500);
    ok((await st(page)).state === 'idle' && /not allowed/i.test(await text(page, '#kNfcLine')), 'the story does not start and the line explains why');
    ok(!(await page.$eval('#kStart', (b) => b.disabled)), 'Start · RFID reader is usable again');
    await ctx.close();
  }

  console.log('E. the whole story by phone NFC with the real cards, production mode');
  {
    const { ctx, page, errors } = await open(browser, { nfc: 'granted' });
    const story = await page.evaluate('Kahani._story()');
    const tagOf = {}; story.cards.forEach((c) => { tagOf[c.id] = TAG[c.registry]; });
    await page.click('#kNfc'); await page.waitForTimeout(500);
    const asked = []; const windows = new Set(); const t0 = Date.now();
    while (Date.now() - t0 < 10 * 60 * 1000) {
      const s = await st(page);
      if (s.state === 'done') break;
      if (s.tapWindow && !windows.has(s.tapWindow + s.progressDone)) { windows.add(s.tapWindow + s.progressDone); await tap(page, tagOf[s.tapWindow]); await page.waitForTimeout(1600); continue; }
      if (s.state === 'question' && s.expected) {
        asked.push(s.expected); await page.waitForTimeout(1600);
        await tap(page, tagOf[s.expected]); await untilNotQuestion(page); await page.waitForTimeout(200); continue;
      }
      await page.waitForTimeout(100);
    }
    const s = await st(page);
    ok(s.state === 'done', `reached the end in ${Math.round((Date.now() - t0) / 1000)} s · asked ${asked.join(' ')} · progress ${s.progressDone}/${story.cards.length}`);
    ok(!errors.length, 'no page errors' + (errors.length ? ': ' + errors.join(' | ') : ''));
    await ctx.close();
  }

  await browser.close(); server.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
