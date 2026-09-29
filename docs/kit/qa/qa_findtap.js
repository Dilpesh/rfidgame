// qa_findtap.js — Find & Tap on the engine, in a real headless Chromium.
//
//   node docs/kit/qa/qa_findtap.js
//
// The old game is random (shuffled order, random praise), so there is no
// clip-for-clip parity run; instead Math.random is pinned and the run checks
// the rules: intro, the background loop, every card asked exactly once in a
// shuffled order, a praise line after each, wrong cards get the retry lines in
// rotation, a card that does not come is asked again at 8 s, the outro last,
// progress 8/8, and the colours-only variant asks for four cards.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = process.env.DOCS || path.resolve(__dirname, '..', '..');
const PORT = 8767, GAME = '/kit/games/find-and-tap/index.html';
const UID = { RED: '9000001', BLUE: '9000002', YELLOW: '9000003', GREEN: '9000004', CIRCLE: '9000005', SQUARE: '9000006', TRIANGLE: '9000007', STAR: '9000008' };

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
    window.__plays.push(name.split('/').pop().split('?')[0].replace('.mp3', '') + (this.loop ? '(loop)' : '')); } return _play.apply(this, arguments); };
  const _create = URL.createObjectURL; window.__blobNames = new Map(); const _fetch = window.fetch;
  window.fetch = async function (u, o) { const r = await _fetch(u, o); const url = String(u); if (url.split('?')[0].endsWith('.mp3')) { const _b = r.blob.bind(r); r.blob = async () => { const b = await _b(); b.__url = url; return b; }; } return r; };
  URL.createObjectURL = function (b) { const u = _create(b); if (b && b.__url) window.__blobNames.set(u, b.__url); return u; };
  // a pinned, still-scrambling random so the run is repeatable
  let seed = 7; Math.random = () => { seed = (seed * 9301 + 49297) % 233280; return seed / 233280; };
  localStorage.setItem('storyIntro:find-and-tap', '1'); localStorage.setItem('readerCheck:ok', '1'); localStorage.setItem('kahaniDevMode', '0');
`;
let pass = 0, fail = 0;
const ok = (c, what) => { if (c) { pass++; console.log('  ✓ ' + what); } else { fail++; console.log('  ✗ ' + what); } };
const st = (p) => p.evaluate('Kahani._state()');
const plays = (p) => p.evaluate('window.__plays');
const waitState = (p, pred, ms = 20000) => p.waitForFunction((src) => eval(src), `(function(){const s=Kahani._state();return (${pred})(s)})()`, { timeout: ms });
async function open(ctx, q = '') { const p = await ctx.newPage(); await p.addInitScript(INIT); p.on('pageerror', (e) => { fail++; console.log('  ✗ page error: ' + e.message); }); await p.goto(`http://localhost:${PORT}${GAME}${q}`); await p.waitForFunction('Kahani._story()'); return p; }
async function start(p) { await p.click('#kStart'); await p.waitForTimeout(300); const i = await p.$('#si-go'); if (i) await i.click(); }
const scan = async (p, uid) => { await p.keyboard.type(uid); await p.keyboard.press('Enter'); };

(async () => {
  const server = serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const ctx = await browser.newContext();

  console.log('a full game');
  let page = await open(ctx);
  await start(page);
  const asked = []; let wrongDone = false, hintDone = false; const t0 = Date.now();
  while (Date.now() - t0 < 120000) {
    const s = await st(page);
    if (s.state === 'done') break;
    if (s.state === 'question' && s.expected) {
      asked.push(s.expected);
      if (!wrongDone) { wrongDone = true; const other = Object.keys(UID).find((c) => c !== s.expected); await scan(page, UID[other]); await page.waitForTimeout(900); const other2 = Object.keys(UID).find((c) => c !== s.expected && c !== other); await scan(page, UID[other2]); await page.waitForTimeout(900); }
      else if (!hintDone) { hintDone = true; await page.waitForTimeout(9000); }
      await scan(page, UID[s.expected]);
      await waitState(page, "s => s.state !== 'question'"); await page.waitForTimeout(200);
      continue;
    }
    await page.waitForTimeout(100);
  }
  const seq = await plays(page), s = await st(page);
  ok(s.state === 'done', 'reaches the end');
  ok(seq[0] === 'bg_loop(loop)' && seq[1] === 'intro', 'background loop, then the intro: ' + seq.slice(0, 2).join(' '));
  ok(asked.length === 8 && new Set(asked).size === 8, 'every card asked exactly once: ' + asked.join(' '));
  ok(asked.join() !== 'RED,BLUE,YELLOW,GREEN,CIRCLE,SQUARE,TRIANGLE,STAR', 'in a shuffled order');
  const prompts = seq.filter((x) => x.startsWith('card_'));
  ok(prompts.length === 9, 'nine prompts: eight asks plus one repeat at 8 s (' + prompts.length + ')');
  const i0 = seq.indexOf('card_' + asked[0].toLowerCase());
  ok(seq[i0 + 1] === 'retry_1' && seq[i0 + 2] === 'retry_2', 'two wrong cards get the two retry lines in turn: ' + seq.slice(i0, i0 + 4).join(' '));
  const i1 = seq.indexOf('card_' + asked[1].toLowerCase());
  ok(seq[i1 + 1] === 'card_' + asked[1].toLowerCase(), 'a card that does not come is asked for again');
  const praise = seq.filter((x) => x.startsWith('correct_'));
  ok(praise.length === 8 && praise.includes('correct_1') && praise.includes('correct_2'), 'a praise line after each card, both lines in use: ' + praise.join(' '));
  ok(seq[seq.length - 1] === 'outro', 'the outro is last');
  ok(s.progressDone === 8, 'progress 8/8');
  await page.close();

  console.log('colours-only variant');
  page = await open(ctx, '?v=colours-only');
  const n = await page.evaluate("(function(){let n=0;const walk=b=>b.forEach(x=>{if(x.op==='ask')n++;if(Array.isArray(x.beats))walk(x.beats)});Kahani._story().scenes.forEach(s=>walk(s.beats));return n})()");
  ok(n === 4, 'four asks instead of eight');
  await page.close();

  await browser.close(); server.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
