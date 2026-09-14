// qa_cards.js — verifies every physical RFID card resolves to the right step
// in every game, with and without leading zeros. Run from the repo root:
//
//     npm install playwright && node qa_cards.js
//
// Reads cards.json, so it stays correct as cards are added. Audio 404s are
// expected and harmless here — this tests card resolution, not playback.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = __dirname;
const cards = JSON.parse(fs.readFileSync(ROOT + '/cards.json', 'utf8')).cards;

const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => e ? (res.writeHead(404), res.end()) :
    (res.writeHead(200, {'Content-Type': p.endsWith('.html') ? 'text/html' : 'application/octet-stream'}), res.end(d)));
});

let fails = 0;
const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fails++; };

// what each game should resolve each physical UID to
function expected(game) {
  const out = [];
  for (const v of Object.values(cards)) {
    const id = (v.games || {})[game];
    if (id) for (const u of v.uids) out.push([u, id, v.label]);
  }
  return out;
}

(async () => {
  await new Promise(r => server.listen(8099, r));
  const browser = await chromium.launch();

  for (const game of ['moon', 'jungle-rescue']) {
    console.log('\n=== ' + game + ' ===');
    const page = await browser.newPage();
    page.on('pageerror', e => { console.log('  JS ERROR: ' + e.message); fails++; });
    await page.goto(`http://localhost:8099/docs/${game}/index.html`);
    await page.waitForTimeout(600);

    const s = await page.evaluate(() => ({
      total: CARDS.length, taught: taughtCount(),
      mapped: Object.keys(uidToCard).length,
      stored: Object.keys(JSON.parse(localStorage.getItem(STORE) || '{}')).length,
      seed: localStorage.getItem(STORE + ':seed'),
    }));
    ok(s.taught === s.total, `every card taught on first load (${s.taught}/${s.total})`);
    ok(s.stored === s.mapped && s.stored > 0, `seeded into localStorage (${s.stored} uids)`);
    ok(s.seed === '2026-09-14a', `seed version recorded (${s.seed})`);

    for (const [uid, id, label] of expected(game)) {
      for (const form of [uid, uid.replace(/^0+/, ''), ' ' + uid + ' ']) {
        const got = await page.evaluate(u => uidToCard[normUid(u)] || null, form);
        ok(got === id, `${label.padEnd(16)} "${form}" -> ${got} (want ${id})`);
      }
    }

    // a real keyboard-wedge scan: digits then Enter must not be swallowed
    const first = expected(game)[0];
    const resolved = await page.evaluate(async (u) => {
      const seen = [];
      const orig = window.handleScan;
      window.handleScan = (raw) => { seen.push(uidToCard[normUid(raw)] || raw); };
      for (const ch of u) window.dispatchEvent(new KeyboardEvent('keydown', { key: ch }));
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));
      window.handleScan = orig;
      return seen;
    }, first[0]);
    ok(resolved.length === 1 && resolved[0] === first[1],
       `keyboard scan of ${first[0]} reaches handleScan as ${first[1]} (got ${JSON.stringify(resolved)})`);
    await page.close();
  }

  // banana-rescue keeps per-card alias arrays instead
  console.log('\n=== banana-rescue ===');
  const page = await browser.newPage();
  page.on('pageerror', e => { console.log('  JS ERROR: ' + e.message); fails++; });
  await page.goto('http://localhost:8099/docs/banana-rescue/index.html');
  await page.waitForTimeout(600);
  for (const [uid, id, label] of expected('banana-rescue')) {
    for (const form of [uid, uid.replace(/^0+/, '')]) {
      const got = await page.evaluate(([c, u]) => uidMatches(c, u), [id, form]);
      ok(got === true, `${label.padEnd(16)} "${form}" matches ${id}`);
    }
  }
  // and must NOT match a different card
  const cross = await page.evaluate(() => uidMatches('MOON', '0002690428'));
  ok(cross === false, 'a water card does not open the moon step');
  await page.close();

  await browser.close(); server.close();
  console.log(fails ? `\n${fails} FAILURES` : '\nALL PASS');
  process.exit(fails ? 1 : 0);
})();
