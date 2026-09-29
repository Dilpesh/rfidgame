// qa_engine.js — the engine's own behaviour, in a real headless Chromium.
// Runs against the kit build of Jungle Rescue English in the mirror.
//
//   node docs/kit/qa/qa_engine.js
//
// Checks: production mode hides the tray and never names the card; ?dev shows
// them; hint ladder (via the fast-hints variant); wrong-card rotation; leading
// zeros / second copies of a card; pause holds playback; Jump to scene starts
// where it should with the right progress; variants drop the beats they say.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = process.env.DOCS || path.resolve(__dirname, '..', '..');
const PORT = 8766, KIT = '/kit/games/jungle-rescue-english/index.html';

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
    window.__plays.push(name.split('/').pop().split('?')[0]); } return _play.apply(this, arguments); };
  const _create = URL.createObjectURL; window.__blobNames = new Map(); const _fetch = window.fetch;
  window.fetch = async function (u, o) { const r = await _fetch(u, o); const url = String(u); if (url.split('?')[0].endsWith('.mp3')) { const _b = r.blob.bind(r); r.blob = async () => { const b = await _b(); b.__url = url; return b; }; } return r; };
  URL.createObjectURL = function (b) { const u = _create(b); if (b && b.__url) window.__blobNames.set(u, b.__url); return u; };
  localStorage.setItem('storyIntro:jungle-rescue-english', '1'); localStorage.setItem('readerCheck:ok', '1'); localStorage.setItem('kahaniDevMode', '0');
`;
let pass = 0, fail = 0;
const ok = (cond, what) => { if (cond) { pass++; console.log('  ✓ ' + what); } else { fail++; console.log('  ✗ ' + what); } };
const st = (page) => page.evaluate('Kahani._state()');
const plays = (page) => page.evaluate('window.__plays');
const waitState = (page, pred, ms = 15000) => page.waitForFunction((src) => eval(src), `(function(){const s=Kahani._state();return (${pred})(s)})()`, { timeout: ms });
async function open(ctx, query = '') {
  const page = await ctx.newPage(); await page.addInitScript(INIT); page.on('pageerror', (e) => { fail++; console.log('  ✗ page error: ' + e.message); });
  await page.goto(`http://localhost:${PORT}${KIT}${query}`); return page;
}
async function start(page) { await page.click('#kStart'); await page.waitForTimeout(300); const i = await page.$('#si-go'); if (i) await i.click(); }
const scan = async (page, uid) => { await page.keyboard.type(uid); await page.keyboard.press('Enter'); };

(async () => {
  const server = serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext();

  console.log('production mode');
  let page = await open(ctx);
  await start(page);
  await waitState(page, "s => s.state === 'question'");
  ok(await page.$eval('#kTapGrid', (e) => e.classList.contains('hide')), 'tray hidden in reader mode');
  ok(!/fuel/i.test(await page.$eval('#kWantLabel', (e) => e.textContent)), 'the wanted card is not named');
  ok(await page.$eval('#kJump', (e) => e.classList.contains('hide')), 'no jump menu');
  await page.keyboard.press('Control+Shift+D');
  ok((await st(page)).devMode === true, 'Ctrl+Shift+D turns developer mode on');
  ok(!(await page.$eval('#kJump', (e) => e.classList.contains('hide'))), 'jump menu appears');
  await page.keyboard.press('Control+Shift+D');
  ok((await st(page)).devMode === false, '…and off again; nothing leaked into the scan buffer');
  await scan(page, '0006359145');
  await waitState(page, "s => s.state !== 'question'");
  ok((await st(page)).progressDone === 1, 'a UID with leading zeros is normalised (FUEL accepted, progress 1/8)');
  await page.close();

  console.log('hint ladder (fast-hints variant: 5/10/15 s) and wrong-card rotation');
  page = await open(ctx, '?v=fast-hints');
  await start(page);
  await waitState(page, "s => s.state === 'question' && s.expected === 'FUEL'");
  const before = (await plays(page)).length;
  await page.waitForTimeout(17000);
  const after = (await plays(page)).slice(before);
  ok(after.join(',').replace(/b\.mp3/g, '.mp3') === 'JR_011.mp3,JR_012.mp3,JR_013.mp3', 'three hints, in order, at the variant\'s times: ' + after.join(' '));
  ok((await st(page)).hintIndex === 3, 'hint index 3');
  const w0 = (await plays(page)).length;
  await scan(page, '2690428'); await page.waitForTimeout(1200);   // WATER: wrong
  await scan(page, '6374623'); await page.waitForTimeout(1200);   // ROPE: wrong
  await scan(page, '6375388'); await page.waitForTimeout(1200);   // BLANKET: wrong
  const wrong = (await plays(page)).slice(w0);
  ok(wrong.join(',') === 'JR_179.mp3,JR_180.mp3,JR_181.mp3,JR_182.mp3,JR_183.mp3,JR_184.mp3', 'wrong cards rotate through the three responses: ' + wrong.join(' '));
  ok((await st(page)).state === 'question', 'still waiting for FUEL');
  await scan(page, '6359145');
  await waitState(page, "s => s.state !== 'question'");
  ok((await st(page)).progressDone === 1, 'FUEL accepted after the wrong ones');
  await page.close();

  console.log('pause / resume');
  page = await open(ctx);
  await start(page);
  await page.waitForTimeout(1500);
  await page.click('#kPause');
  const p0 = (await plays(page)).length; await page.waitForTimeout(2500);
  ok((await st(page)).paused === true && (await plays(page)).length === p0, 'nothing new plays while paused');
  await page.click('#kPause'); await page.waitForTimeout(1500);
  ok((await st(page)).paused === false && (await plays(page)).length > p0, 'playback continues after resume');
  await page.close();

  console.log('jump to scene (developer mode)');
  page = await open(ctx, '?dev');
  await start(page); await page.waitForTimeout(800);
  await page.selectOption('#kJump', '9');   // Dance party
  await page.waitForTimeout(1500);
  const s9 = await st(page); const jp = await plays(page);
  ok(s9.sceneCursor === 9 && s9.progressDone === 8, `jumped to scene 10 with progress 8/8 (got scene ${s9.sceneCursor + 1}, progress ${s9.progressDone})`);
  ok(jp[jp.length - 2] === 'JR_158.mp3' || jp.includes('JR_158.mp3'), 'the dance scene starts with its chime JR_158');
  await page.selectOption('#kJump', '6');   // Lion: flashlight found — on jump: bed JR_103_bed
  await page.waitForTimeout(800);
  const jp2 = await plays(page);
  ok(jp2.slice(-6).includes('JR_103_bed.mp3'), 'on-jump bed plays for the flashlight scene: ' + jp2.slice(-6).join(' '));
  ok((await st(page)).progressDone === 6, 'progress 6/8 once the flashlight is found');
  ok(!(await page.$eval('#kTapGrid', (e) => e.classList.contains('hide'))) || (await st(page)).state !== 'question', 'tray visible in dev mode when asking');
  await page.close();

  console.log('early scans (LEARNINGS 9–10): a tap while Coco talks is acknowledged and remembered');
  page = await open(ctx);
  await start(page);
  await page.waitForTimeout(1200);                               // intro narration, no question armed yet
  ok((await st(page)).state === 'narrative', 'Coco is talking');
  const e0 = (await plays(page)).length;
  await scan(page, '6359145');                                   // FUEL, early
  await page.waitForTimeout(300);
  const e1 = await plays(page);
  ok(e1.slice(e0).includes('tap.mp3'), 'the tap gets a sound at once: ' + e1.slice(e0).join(' '));
  ok((await st(page)).earlyScan === 'FUEL', 'and is remembered');
  await waitState(page, "s => s.progressDone === 1", 20000);
  const e2 = await plays(page);
  ok(!e2.includes('JR_010.mp3') && !e2.includes('JR_010b.mp3'), 'when the FUEL question arms it is answered at once — the prompt never plays');
  ok(e2.includes('JR_015.mp3') || e2.includes('JR_015b.mp3') || (await st(page)).state !== 'question', 'praise follows as usual');
  // a wrong early tap: WATER during the fuel-success narration
  await scan(page, '2690428'); await page.waitForTimeout(200);
  ok((await st(page)).earlyScan === 'WATER', 'a wrong early tap is remembered too, silently');
  await waitState(page, "s => s.state === 'question' && s.expected === 'ROPE'", 40000);
  await page.waitForTimeout(300);
  ok((await plays(page)).includes('JR_036.mp3'), '…but never advances: the ROPE question asks normally');
  ok((await st(page)).progressDone === 1, 'progress unchanged by the wrong early tap');
  await page.close();

  console.log('variants filter tagged beats (same audio)');
  const count = async (q, tag, op) => { const p = await open(ctx, q); await p.waitForFunction('Kahani._story()'); const n = await p.evaluate(`(function(){let n=0;const walk=b=>b.forEach(x=>{if(${op ? `x.op==='${op}'` : `(x.tags||[]).includes('${tag}')`})n++;if(Array.isArray(x.beats))walk(x.beats)});Kahani._story().scenes.forEach(s=>walk(s.beats));return n})()`); await p.close(); return n; };
  const jokes = await count('', 'joke'), noJokes = await count('?v=no-jokes', 'joke'), halfJokes = await count('?v=half-jokes', 'joke');
  ok(jokes > 10 && noJokes === 0, `no-jokes drops every #joke beat (${jokes} → ${noJokes})`);
  ok(halfJokes === Math.ceil(jokes / 2), `half-jokes keeps every other one (${jokes} → ${halfJokes})`);
  const praise = await count('', 'praise'), praiseEffort = await count('?v=praise-after-effort', 'praise');
  ok(praise > 5 && praiseEffort === 2, `praise-after-effort keeps only the two #effort lines (${praise} → ${praiseEffort})`);
  const asks = await count('', null, 'ask'), fewer = await count('?v=fewer-taps', null, 'ask');
  ok(asks === 11 && fewer === 9, `fewer-taps drops the two middle biscuit asks (${asks} → ${fewer})`);
  page = await open(ctx, '?v=fast-hints'); await page.waitForFunction('Kahani._story()'); ok((await page.evaluate('Kahani._story().hintDelays')).join() === '5000,10000,15000', 'fast-hints sets the ladder'); await page.close();

  await browser.close(); server.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
