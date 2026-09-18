// qa_hinglish.js - regression test for the Hinglish Jungle Rescue build and
// the landing page ordering. Run from the repo root:
//
//     npm install playwright && node qa_hinglish.js
//
// Checks: every tile resolves and sits in the intended order; the embedded
// build loads clean with all 85 cues; every physical card maps to the right
// step with and without leading zeros; a card the story does not use resolves
// to nothing; and the screen wake lock is taken on start and released on stop.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = __dirname;
const cards = JSON.parse(fs.readFileSync(ROOT + '/cards.json', 'utf8')).cards;
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => e ? (res.writeHead(404), res.end())
    : (res.writeHead(200, {'Content-Type':'text/html'}), res.end(d)));
});
let fails = 0;
const ok = (c, m) => { console.log((c?'  PASS  ':'  FAIL  ')+m); if(!c) fails++; };
const STUB = `window.__wake={requests:0,releases:0,type:null};
 Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:t=>{
  window.__wake.requests++;window.__wake.type=t;
  return Promise.resolve({released:false,addEventListener(){},
    release(){window.__wake.releases++;this.released=true;return Promise.resolve()}})}}});`;

(async () => {
  await new Promise(r => server.listen(8097, r));
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.addInitScript(STUB);

  console.log('=== landing page ===');
  let p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.goto('http://localhost:8097/docs/index.html');
  await p.waitForTimeout(400);
  ok(errs.length === 0, 'no JS errors' + (errs.length ? ': '+errs.join(' | ') : ''));
  const tiles = await p.$$eval('.tile', els => els.map(e => ({
    href: e.getAttribute('href'), title: (e.querySelector('.meta h2,.meta h3,h2,h3')||{}).textContent })));
  ok(tiles.length === 6, `6 tiles rendered (${tiles.length})`);
  ok(tiles[0].href === 'jungle-rescue-hinglish/index.html', `first tile is the new build (${tiles[0].href})`);
  ok(tiles[4].href === 'jungle-rescue/index.html', `fifth tile is the old one (${tiles[4].href})`);
  ok(!tiles[5].href, 'last tile is the coming-soon placeholder');
  for (const t of tiles.filter(t => t.href)) {
    const r = await p.goto('http://localhost:8097/docs/' + t.href);
    ok(r.status() === 200, `${t.href} resolves (${r.status()})`);
    await p.goBack();
  }
  await p.close();

  console.log('\n=== jungle-rescue-hinglish ===');
  p = await ctx.newPage();
  const e2 = []; p.on('pageerror', e => e2.push(e.message));
  await p.goto('http://localhost:8097/docs/jungle-rescue-hinglish/index.html');
  await p.waitForTimeout(1200);
  ok(e2.length === 0, 'loads with no JS errors' + (e2.length ? ': '+e2.join(' | ') : ''));
  ok(await p.evaluate(() => Object.keys(media).length) === 85, '85 audio cues embedded');

  // every physical card this game uses must resolve, with and without leading zeros
  const expect = [];
  for (const v of Object.values(cards)) {
    const gid = (v.games||{})['jungle-rescue-hinglish'];
    if (gid) for (const u of v.uids) expect.push([u, gid, v.label]);
  }
  ok(expect.length === 12, `12 physical cards map into this game (${expect.length})`);
  for (const [uid, gid, label] of expect) {
    for (const form of [uid, uid.replace(/^0+/,'')]) {
      const got = await p.evaluate(u => {
        const q = normUid(u);
        const hit = Object.entries(mapping).find(([,v]) => uidList(v).some(x => normUid(x) === q));
        return hit ? hit[0] : null;
      }, form);
      ok(got === gid, `${label.padEnd(16)} "${form}" -> ${got} (want ${gid})`);
    }
  }
  ok(await p.evaluate(() => {
    const q = normUid('0006170247');   // balloons - not a card in this story
    return !Object.entries(mapping).find(([,v]) => uidList(v).some(x => normUid(x) === q));
  }), 'a card this story does not use resolves to nothing');

  // wake lock
  ok(await p.evaluate(() => window.__wake.requests === 0), 'no lock just from opening the page');
  await p.evaluate(() => { try { start(); } catch(e) {} });
  await p.waitForTimeout(800);
  ok(await p.evaluate(() => window.__wake.requests >= 1), 'lock requested when the story starts');
  ok(await p.evaluate(() => window.__wake.type === 'screen'), 'requested type is "screen"');
  await p.evaluate(() => { try { stop(); } catch(e) {} });
  await p.waitForTimeout(400);
  ok(await p.evaluate(() => window.__wake.releases >= 1), 'lock released on stop/reset');
  await p.close();

  await browser.close(); server.close();
  console.log(fails ? `\n${fails} FAILURES` : '\nALL PASS');
  process.exit(fails ? 1 : 0);
})();
