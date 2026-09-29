// qa_play.js — play any kit story straight through in a headless Chromium.
//
//   node docs/kit/qa/qa_play.js <slug> [variant]
//
// Taps the right card whenever a question arms (using the UIDs the compiler
// put in story.json), fires any tap window once, and reports: whether the story
// reached the end, how long it took, every clip played in order, and anything
// the engine logged as missing or refused. Use it on every new story before the
// phone, and on every variant.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = process.env.DOCS || path.resolve(__dirname, '..', '..');
const PORT = 8768;
const slug = process.argv[2], variant = process.argv[3] || '';
if (!slug) { console.log('usage: node qa_play.js <slug> [variant]'); process.exit(2); }

function serve() {
  const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.mp3': 'audio/mpeg', '.css': 'text/css' };
  return http.createServer((req, res) => {
    fs.readFile(path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': types[path.extname(req.url.split('?')[0])] || 'application/octet-stream', 'Cache-Control': 'no-store' }); res.end(data);
    });
  }).listen(PORT);
}
const INIT = (key) => `
  window.__plays = [];
  const _play = HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play = function () { const src = this.getAttribute('src') || ''; if (!src.startsWith('data:')) {
    let name = src; if (src.startsWith('blob:') && window.__blobNames) name = window.__blobNames.get(src) || src;
    const parts = name.split('?')[0].split('/'); window.__plays.push((parts.includes('library') ? 'lib/' : '') + parts.pop().replace('.mp3', '') + (this.loop ? '(loop)' : '')); } return _play.apply(this, arguments); };
  const _create = URL.createObjectURL; window.__blobNames = new Map(); const _fetch = window.fetch;
  window.fetch = async function (u, o) { const r = await _fetch(u, o); const url = String(u); if (url.split('?')[0].endsWith('.mp3')) { const _b = r.blob.bind(r); r.blob = async () => { const b = await _b(); b.__url = url; return b; }; } return r; };
  URL.createObjectURL = function (b) { const u = _create(b); if (b && b.__url) window.__blobNames.set(u, b.__url); return u; };
  localStorage.setItem('storyIntro:${key}', '1'); localStorage.setItem('readerCheck:ok', '1'); localStorage.setItem('kahaniDevMode', '1');
`;

(async () => {
  const story = JSON.parse(fs.readFileSync(path.join(ROOT, 'kit', 'games', slug, 'story.json'), 'utf8'));
  const uidOf = {}; for (const [u, c] of Object.entries(story.uids)) if (!uidOf[c]) uidOf[c] = u;
  const missingUid = story.cards.map((c) => c.id).filter((c) => !uidOf[c]);
  if (missingUid.length) { console.log('✗ no UID in cards.json for: ' + missingUid.join(', ')); process.exit(1); }
  const server = serve();
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage(); const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.addInitScript(INIT(story.key));
  await page.goto(`http://localhost:${PORT}/kit/games/${slug}/index.html${variant ? '?v=' + variant : ''}`);
  await page.waitForFunction('Kahani._story()');
  await page.click('#kStart'); await page.waitForTimeout(300); const i = await page.$('#si-go'); if (i) await i.click();
  const st = () => page.evaluate('Kahani._state()');
  const scan = async (uid) => { await page.keyboard.type(uid); await page.keyboard.press('Enter'); };
  const asked = []; let gagDone = false; const t0 = Date.now();
  while (Date.now() - t0 < 10 * 60 * 1000) {
    const s = await st();
    if (s.state === 'done') break;
    if (s.tapWindow && !gagDone) { gagDone = true; await scan(uidOf[s.tapWindow]); await page.waitForTimeout(300); continue; }
    if (s.state === 'question' && s.expected) {
      asked.push(s.expected); await page.waitForTimeout(300);
      await scan(uidOf[s.expected]);
      await page.waitForFunction(() => Kahani._state().state !== 'question', null, { timeout: 15000 }).catch(() => {});
      await page.waitForTimeout(200); continue;
    }
    await page.waitForTimeout(100);
  }
  const s = await st(), plays = await page.evaluate('window.__plays');
  const logText = await page.$eval('#kLog', (e) => e.textContent).catch(() => '');
  const bad = logText.split('\n').filter((l) => /missing|could not|refused|error/i.test(l) && !/silent unlock/.test(l));
  await browser.close(); server.close();
  console.log(`${story.title}${variant ? ' · variant ' + variant : ''}`);
  console.log(`${s.state === 'done' ? '✓' : '✗'} ${s.state === 'done' ? 'reached the end' : 'stopped in state ' + s.state} in ${Math.round((Date.now() - t0) / 1000)} s · ${asked.length} cards asked (${asked.join(' ')}) · progress ${s.progressDone}/${story.cards.length}`);
  console.log(`${plays.length} clips played: ${plays.join(' ')}`);
  if (bad.length) { console.log('✗ engine log:'); bad.forEach((l) => console.log('  ' + l)); }
  if (errors.length) { console.log('✗ page errors:'); errors.forEach((l) => console.log('  ' + l)); }
  process.exit(s.state === 'done' && !bad.length && !errors.length ? 0 : 1);
})();
