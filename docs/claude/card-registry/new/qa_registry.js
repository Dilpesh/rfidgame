// qa_registry.js - the shared card registry, and every game that reads through it.
//
//     npm install playwright && node qa_registry.js
//
// Reads cards.json, so it stays correct as cards are added. Three things it protects:
//  1. docs/card-registry.js itself: seeds from cards.json on first load, re-seeds
//     when the seed version changes (cards.json wins), keeps hand-taught cards,
//     and resolves every UID in every form a reader sends it.
//  2. Each game in REGISTRY_GAMES resolves every physical card to the id that
//     story uses, through the registry and its generated CARD_MAP.
//  3. The bug that started this: a browser that has played Jungle Rescue 2 has
//     "rescueGameCards" with SNACK / FIRSTAID in it. A registry game must not
//     read that. It is asserted for jungle-rescue-english, which once did.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = __dirname;
const cardsFile = JSON.parse(fs.readFileSync(ROOT + '/cards.json', 'utf8'));
const cards = cardsFile.cards, SEED = cardsFile.seed_version;
const T = {'.html':'text/html','.js':'text/javascript','.json':'application/json'};
// a blank page on the same origin, so the module can be tested alone with real localStorage
const BLANK = '<!doctype html><script src="/docs/card-registry.js"></script>';
const server = http.createServer((q, r) => { if (q.url === '/__registry.html') { r.writeHead(200, {'Content-Type':'text/html'}); return r.end(BLANK); }
  const p = path.join(ROOT, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(p, (e, d) => e ? (r.writeHead(404), r.end()) : (r.writeHead(200, {'Content-Type': T[path.extname(p)] || 'application/octet-stream'}), r.end(d))); });
let fails = 0; const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fails++; };

// game -> how it exposes "what card did this UID become" (kept per game so a
// migrated game only needs one line here)
const REGISTRY_GAMES = {
  'jungle-rescue-english': { resolve: 'cardOf' },
};
// the old per-game key, as Jungle Rescue 2 writes it on the same origin
const JR2 = {"6170247":"BALLOONS","6375388":"BLANKET","6375198":"DISCOBALL","6374815":"FIRSTAID","2692483":"FLASHLIGHT","6375577":"FLASHLIGHT","6359145":"FUEL","6375007":"GEM","5688805":"LADDER","6360778":"MANGO","6360574":"MUSIC","2696012":"PARTYHORN","6358150":"PRUNERS","6374623":"ROPE","5720648":"SNACK","6373651":"SNACK","2682976":"WATER","2690428":"WATER"};
const forms = u => [u, u.replace(/^0+/, ''), ' ' + u + ' ', u.toLowerCase()];
const STUB = `Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});`;

(async () => {
  await new Promise(r => server.listen(8097, r));
  const b = await chromium.launch();

  console.log('=== docs/card-registry.js on its own ===');
  let ctx = await b.newContext(); await ctx.addInitScript(STUB);
  let p = await ctx.newPage(); const e1 = []; p.on('pageerror', e => e1.push(e.message));
  await p.goto('http://localhost:8097/__registry.html');
  await p.waitForTimeout(200);
  ok(e1.length === 0, 'loads clean' + (e1.length ? ': ' + e1.join(' | ') : ''));
  ok(await p.evaluate(s => CardRegistry.seedVersion === s, SEED), `carries cards.json's seed version (${SEED})`);
  let n = 0, bad = [];
  for (const [canon, v] of Object.entries(cards)) for (const u of v.uids) for (const f of forms(u)) {
    n++; const got = await p.evaluate(x => CardRegistry.lookup(x), f); if (got !== canon) bad.push(`${JSON.stringify(f)} -> ${got} (want ${canon})`);
  }
  ok(bad.length === 0, `every UID resolves in every form (${n} lookups)` + (bad.length ? ': ' + bad.slice(0, 3).join('; ') : ''));
  ok(await p.evaluate(() => CardRegistry.lookup('0009999999') === null && CardRegistry.lookup('') === null), 'an unknown or empty read is null');
  ok(await p.evaluate(() => CardRegistry.cards().length) === Object.keys(cards).length, `cards() lists all ${Object.keys(cards).length} cards`);
  ok(await p.evaluate(() => CardRegistry.label('SNACK')) === cards.SNACK.label, 'labels come from cards.json');
  const st = await p.evaluate(k => ({ seed: localStorage.getItem(k + ':seed'), n: Object.keys(JSON.parse(localStorage.getItem(k))).length }), 'kahaniCards');
  ok(st.seed === SEED && st.n === Object.values(cards).reduce((a, v) => a + v.uids.length, 0), `seeded into ONE key, kahaniCards (${st.n} uids, seed ${st.seed})`);
  // teach: adds a uid, refuses a card cards.json does not know
  ok(await p.evaluate(() => CardRegistry.teach('0001112223', 'snack') === 'SNACK' && CardRegistry.lookup('1112223') === 'SNACK'), 'teach() adds a UID for an existing card');
  ok(await p.evaluate(() => CardRegistry.teach('0001112224', 'UNICORN') === null && CardRegistry.lookup('1112224') === null), 'teach() refuses a card that is not in cards.json');
  ok(await p.evaluate(() => CardRegistry.uidsOf('SNACK').length) === cards.SNACK.uids.length + 1, 'uidsOf() sees the taught one too');
  // between seeds, teach wins; on a new seed, cards.json wins but taught extras stay
  await p.evaluate(() => CardRegistry.teach('6373651', 'WATER'));            // a mistake taught by hand
  await p.close(); p = await ctx.newPage(); await p.goto('http://localhost:8097/__registry.html'); await p.waitForTimeout(200);
  ok(await p.evaluate(() => CardRegistry.lookup('6373651') === 'WATER'), 'between seeds a taught card wins over the printed set');
  await p.evaluate(() => localStorage.setItem('kahaniCards:seed', 'older'));
  await p.close(); p = await ctx.newPage(); await p.goto('http://localhost:8097/__registry.html'); await p.waitForTimeout(200);
  ok(await p.evaluate(() => CardRegistry.lookup('6373651') === 'SNACK'), 'on a new seed cards.json wins back');
  ok(await p.evaluate(() => CardRegistry.lookup('1112223') === 'SNACK'), 'a hand-taught extra UID survives the re-seed');
  ok(await p.evaluate(() => CardRegistry.forget('1112223') && CardRegistry.lookup('1112223') === null), 'forget() removes it');
  await p.close(); await ctx.close();

  // storage unavailable: still works from the printed set
  ctx = await b.newContext(); await ctx.addInitScript(STUB + `Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}});`);
  p = await ctx.newPage(); const e2 = []; p.on('pageerror', e => e2.push(e.message));
  await p.goto('http://localhost:8097/__registry.html'); await p.waitForTimeout(200);
  ok(e2.length === 0 && await p.evaluate(() => CardRegistry.lookup('0006373651') === 'SNACK'), 'with storage blocked (private window) the printed set still resolves');
  await p.close(); await ctx.close();

  for (const [game, how] of Object.entries(REGISTRY_GAMES)) {
    console.log('\n=== ' + game + ' ===');
    // a browser that has played Jungle Rescue 2: its private key must be ignored
    ctx = await b.newContext(); await ctx.addInitScript(STUB + `localStorage.setItem('rescueGameCards',${JSON.stringify(JSON.stringify(JR2))});localStorage.setItem('rescueGameCards:seed','${SEED}');`);
    p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto(`http://localhost:8097/docs/${game}/index.html`); await p.waitForTimeout(600);
    ok(errs.length === 0, 'loads clean' + (errs.length ? ': ' + errs.join(' | ') : ''));
    ok(await p.evaluate(() => !!window.CardRegistry), 'loads ../card-registry.js');
    ok(await p.evaluate(() => typeof CARD_MAP === 'object' && !('DEFAULT_UIDS' in window) && !/rescueGameCards|localStorage/.test(String(window.loadCards))), 'keeps no private uid map and never reads localStorage itself');
    const deck = await p.evaluate(() => CARD_ORDER.slice());
    const mapped = await p.evaluate(() => Object.values(CARD_MAP));
    ok(deck.every(id => mapped.includes(id)), `every card the story asks for is mapped from a registry card (${deck.join(', ')})`);
    let m = 0; const badm = [];
    for (const v of Object.values(cards)) { const id = (v.games || {})[game]; if (!id) continue;
      for (const u of v.uids) for (const f of forms(u)) { m++; const got = await p.evaluate(([fn, x]) => window[fn](x), [how.resolve, f]); if (got !== id) badm.push(`${v.label} ${JSON.stringify(f)} -> ${got} (want ${id})`); } }
    ok(badm.length === 0, `every physical card resolves to this story's id, JR2's key present or not (${m} lookups)` + (badm.length ? ': ' + badm.slice(0, 3).join('; ') : ''));
    ok(await p.evaluate(fn => window[fn]('0006373651') === 'BISCUIT' && window[fn]('0005720648') === 'BISCUIT', how.resolve), 'both Snack cards are BISCUIT here — the bug this replaces');
    ok(await p.evaluate(fn => window[fn]('0006374815') === 'FIRST_AID', how.resolve), 'the first-aid card is FIRST_AID here');
    ok(await p.evaluate(fn => window[fn]('0006360778') === null, how.resolve), 'a card this story does not use (mango) resolves to nothing, not a wrong id');
    // and the reader path: digits then Enter reach the game's handler as the story id
    const seen = await p.evaluate(async () => { const out = []; const orig = window.acceptCard; window.acceptCard = (c) => out.push(c);
      for (const ch of '0006373651') document.dispatchEvent(new KeyboardEvent('keydown', { key: ch, bubbles: true }));
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
      await new Promise(r => setTimeout(r, 50)); window.acceptCard = orig; return out; });
    ok(seen.length === 1 && seen[0] === 'BISCUIT', `a keyboard-wedge scan of the snack card reaches the story as BISCUIT (got ${JSON.stringify(seen)})`);
    ok(await p.evaluate(() => localStorage.getItem('rescueGameCards') !== null && JSON.parse(localStorage.getItem('rescueGameCards'))['6373651'] === 'SNACK'), "Jungle Rescue 2's own key is left exactly as it was");
    await p.close(); await ctx.close();
  }

  await b.close(); server.close();
  console.log(fails ? `\n${fails} FAILURES` : '\nALL PASS');
  process.exit(fails ? 1 : 0);
})();
