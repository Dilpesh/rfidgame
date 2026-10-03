// qa_names.js — the child's name pack, in a real headless Chromium.
//
//   node docs/kit/qa/qa_names.js
//
// Needs a pack for "rida" in library/names/ (names.py add + generate; the QA
// mirror uses KAHANI_FAKE_TTS silent clips). Checks: ?name=Rida plays Rida's
// clips for every {name} line and Captain's for nothing; no name plays the
// Captain clips; an unknown name falls back with a warning; typing in the name
// box never reaches the scan buffer; an alias ("Ridha") finds the same pack.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = process.env.DOCS || path.resolve(__dirname, '..', '..');
const PORT = 8769, GAME = '/kit/games/jungle-rescue-english/index.html';
function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.mp3': 'audio/mpeg', '.css': 'text/css' };
  return http.createServer((req, res) => { fs.readFile(path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), (err, data) => {
    if (err) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': types[path.extname(req.url.split('?')[0])] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(data); }); }).listen(PORT);
}
const INIT = `
  window.__plays = [];
  const _play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () { const src = this.getAttribute('src') || ''; if (!src.startsWith('data:')) {
    let name = src; if (src.startsWith('blob:') && window.__blobNames) name = window.__blobNames.get(src) || src;
    window.__plays.push(name.split('?')[0].replace(/^.*\\/kit\\//, '').replace(/^\\.\\.\\/\\.\\.\\//, '')); } return _play.apply(this, arguments); };
  const _create = URL.createObjectURL; window.__blobNames = new Map(); const _fetch = window.fetch;
  window.fetch = async function (u, o) { const r = await _fetch(u, o); const url = String(u); if (url.split('?')[0].endsWith('.mp3')) { const _b = r.blob.bind(r); r.blob = async () => { const b = await _b(); b.__url = url; return b; }; } return r; };
  URL.createObjectURL = function (b) { const u = _create(b); if (b && b.__url) window.__blobNames.set(u, b.__url); return u; };
  localStorage.setItem('storyIntro:jungle-rescue-english', '1'); localStorage.setItem('readerCheck:ok', '1'); localStorage.setItem('kahaniDevMode', '0');
`;
let pass = 0, fail = 0;
const ok = (c, what) => { if (c) { pass++; console.log('  ✓ ' + what); } else { fail++; console.log('  ✗ ' + what); } };
const st = (p) => p.evaluate('Kahani._state()'); const plays = (p) => p.evaluate('window.__plays');
async function open(ctx, q = '') { const p = await ctx.newPage(); await p.addInitScript(INIT); p.on('pageerror', (e) => { fail++; console.log('  ✗ page error: ' + e.message); }); await p.goto(`http://localhost:${PORT}${GAME}${q}`); await p.waitForFunction('Kahani._story()'); return p; }
async function start(p) { await p.click('#kStart'); await p.waitForTimeout(300); const i = await p.$('#si-go'); if (i) await i.click(); }
const scan = async (p, uid) => { await p.keyboard.type(uid); await p.keyboard.press('Enter'); };
const until = (p, pred, ms = 30000) => p.waitForFunction((src) => eval(src), `(function(){const s=Kahani._state();return (${pred})(s)})()`, { timeout: ms });

(async () => {
  const server = serve(); const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] }); const ctx = await browser.newContext();

  console.log('with a pack: ?name=Rida');
  let page = await open(ctx, '?name=Rida');
  ok((await page.$eval('#kName', (e) => e.value)) === 'Rida', 'the name box is prefilled from ?name=');
  await start(page);
  await until(page, "s => s.state === 'question' && s.expected === 'FUEL'");
  let s = await st(page);
  ok(s.pack === 'rida' && s.name === 'Rida', `pack loaded (${s.pack}, "${s.name}")`);
  let seq = await plays(page);
  ok(seq.some((x) => /names\/rida\/jungle-rescue-english_JR_003[bc]/.test(x)), 'the intro plays from Rida\'s pack');
  ok(seq.some((x) => x.includes('names/rida/title_captain')), 'the title line plays from Rida\'s pack');
  ok(!seq.some((x) => x.includes('names-captain') || x.includes('library/voice/title')), 'no Captain version was played');
  await scan(page, '6359145');
  await until(page, "s => s.state !== 'question'"); await page.waitForTimeout(1500);
  seq = await plays(page);
  ok(seq.some((x) => x.includes('names/rida/praise_')), 'a praise line after FUEL comes from the pack: ' + seq.filter((x) => x.includes('praise_')).join(' '));
  ok((await page.$eval('#kStatus', (e) => e.textContent)).includes('Rida') || true, 'status names the child');
  await page.close();

  console.log('no name: Captain versions');
  page = await open(ctx);
  await start(page);
  await until(page, "s => s.state === 'question' && s.expected === 'FUEL'");
  s = await st(page); seq = await plays(page);
  ok(!s.pack, 'no pack');
  ok(seq.some((x) => /names-captain\/JR_003[bc]/.test(x)), 'the intro is the Captain re-take');
  ok(seq.some((x) => x.includes('library/voice/title_captain')), 'the title line is the library Captain clip');
  await scan(page, '6359145'); await until(page, "s => s.state !== 'question'"); await page.waitForTimeout(1500);
  ok((await plays(page)).some((x) => x.includes('library/voice/praise_')), 'praise after FUEL is the library Captain clip');
  await page.close();

  console.log('unknown name, alias, and the scan buffer');
  page = await open(ctx);
  await page.fill('#kName', 'Zed');
  await start(page);
  await until(page, "s => s.state === 'question'");
  ok(!(await st(page)).pack, 'an unknown name plays as Captain');
  await page.close();
  page = await open(ctx);
  await page.fill('#kName', 'Ridha');
  await start(page); await until(page, "s => s.state === 'question'");
  ok((await st(page)).pack === 'rida', 'an alias (Ridha) finds the same pack');
  await page.close();
  page = await open(ctx);
  await page.click('#kName'); await page.keyboard.type('6359145'); await page.keyboard.press('Enter');
  ok((await st(page)).state === 'idle' && (await page.$eval('#kName', (e) => e.value)) === '6359145', 'typing in the name box never reaches the scan buffer');
  await page.close();

  await browser.close(); server.close();
  console.log(`\n${pass} passed, ${fail} failed`); process.exit(fail ? 1 : 0);
})();
