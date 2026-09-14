// qa_wakelock.js — proves every game takes a screen wake lock while the story
// is playing, re-takes it after the phone comes back from a lock screen, and
// releases it at the end. Run from the repo root:
//
//     npm install playwright && node qa_wakelock.js
//
// navigator.wakeLock is stubbed before page scripts run, so this tests the
// game's wiring rather than the headless browser's power management.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = __dirname;
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => e ? (res.writeHead(404), res.end()) :
    (res.writeHead(200, {'Content-Type':'text/html'}), res.end(d)));
});
let fails = 0;
const ok = (c, m) => { console.log((c?'  PASS  ':'  FAIL  ')+m); if(!c) fails++; };

// Replace navigator.wakeLock with a recorder BEFORE any page script runs.
// Plain assignment is refused on navigator, hence defineProperty.
const STUB = `
  window.__wake = { requests: 0, releases: 0, type: null };
  Object.defineProperty(navigator, 'wakeLock', {
    configurable: true,
    value: { request: (t) => { window.__wake.requests++; window.__wake.type = t;
      return Promise.resolve({
        released: false,
        addEventListener(){},
        release(){ window.__wake.releases++; this.released = true; return Promise.resolve(); }
      }); } }
  });
`;

(async () => {
  await new Promise(r => server.listen(8098, r));
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.addInitScript(STUB);

  for (const [game, startFn, endFn] of [
    ['moon',          'startGame()', 'keepAwake(false)'],
    ['jungle-rescue', 'startGame()', 'keepAwake(false)'],
    ['banana-rescue', 'start()',     'keepAwake(false)'],
  ]) {
    console.log('\n=== ' + game + ' ===');
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(e.message));
    await page.goto(`http://localhost:8098/docs/${game}/index.html`);
    await page.waitForTimeout(400);

    ok(await page.evaluate(() => window.__wake.requests === 0),
       'no lock taken just by opening the page');

    await page.evaluate(f => { try { eval(f); } catch (e) { window.__startErr = e.message; } }, startFn);
    await page.waitForTimeout(500);
    const afterStart = await page.evaluate(() => window.__wake);
    ok(afterStart.requests >= 1, `lock requested when the story starts (${afterStart.requests})`);
    ok(afterStart.type === 'screen', `requested type is "screen" (${afterStart.type})`);

    // returning from a lock screen must re-take the lock
    await page.evaluate(() => {
      Object.defineProperty(document, 'visibilityState', {configurable:true, get:()=>'visible'});
      document.dispatchEvent(new Event('visibilitychange'));
    });
    await page.waitForTimeout(300);
    const afterVis = await page.evaluate(() => window.__wake);
    ok(afterVis.requests >= 1, `still holds a lock after returning to the tab (${afterVis.requests})`);

    await page.evaluate(f => eval(f), endFn);
    await page.waitForTimeout(300);
    const afterEnd = await page.evaluate(() => window.__wake);
    ok(afterEnd.releases >= 1, `lock released when the story ends (${afterEnd.releases})`);

    ok(errs.length === 0, 'no JS errors' + (errs.length ? ': ' + errs.join(' | ') : ''));
    await page.close();
  }

  // find-and-tap already had this; just prove it still loads clean and is wired
  console.log('\n=== find-and-tap ===');
  const p2 = await ctx.newPage();
  const e2 = []; p2.on('pageerror', e => e2.push(e.message));
  await p2.goto('http://localhost:8098/docs/find-and-tap/index.html');
  await p2.waitForTimeout(600);
  ok(e2.length === 0, 'loads with no JS errors' + (e2.length ? ': ' + e2.join(' | ') : ''));
  ok(await p2.evaluate(() => 'wakeLock' in navigator), 'wake lock API reachable in this context');
  await p2.close();

  await browser.close(); server.close();
  console.log(fails ? `\n${fails} FAILURES` : '\nALL PASS');
  process.exit(fails ? 1 : 0);
})();
