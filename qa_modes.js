// qa_modes.js - production vs developer mode in the Hinglish build.
// Run from the repo root:  npm install playwright && node qa_modes.js
//
// Production is the default and the only thing the kids see: Start, Reset and
// physical RFID cards. This checks the on-screen card buttons and every other
// dev control are genuinely unreachable, that a keyboard-wedge scan still
// works with them hidden, and that Ctrl+Shift+D toggles and persists both ways.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = __dirname;
const server = http.createServer((req,res)=>{const p=path.join(ROOT,decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p,(e,d)=>e?(res.writeHead(404),res.end()):(res.writeHead(200,{'Content-Type':'text/html'}),res.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m); if(!c)fails++;};
const URL='http://localhost:8096/docs/jungle-rescue-hinglish/index.html';
const DEVIDS=['readerBtn','teachBtn','devBtn','nextBtn'];
const vis = p => p.evaluate(ids => Object.fromEntries(ids.map(i =>
  [i, !document.getElementById(i).classList.contains('hidden')])), DEVIDS);

(async () => {
  await new Promise(r=>server.listen(8096,r));
  const b = await chromium.launch(); const ctx = await b.newContext();
  await ctx.addInitScript(`window.__wake={requests:0,releases:0};
    Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:()=>{window.__wake.requests++;
      return Promise.resolve({released:false,addEventListener(){},release(){window.__wake.releases++;return Promise.resolve()}})}}});`);

  console.log('=== fresh browser: production by default ===');
  let p = await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(URL); await p.waitForTimeout(900);
  ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.join(' | '):''));
  let v = await vis(p);
  ok(DEVIDS.every(i=>!v[i]), `every dev control hidden (${JSON.stringify(v)})`);
  ok(await p.evaluate(()=>document.getElementById('devPanel').classList.contains('hidden')),'tap-card panel hidden');
  ok(await p.evaluate(()=>document.getElementById('devCards').offsetParent===null),'on-screen card buttons not reachable');
  ok(await p.evaluate(()=>!document.getElementById('startBtn').classList.contains('hidden')),'Start is still there');
  ok(await p.evaluate(()=>!document.getElementById('resetBtn').classList.contains('hidden')),'Reset is still there');
  ok((await p.evaluate(()=>document.getElementById('modePill').textContent)).includes('Card mode'),'pill says card mode');

  console.log('\n=== RFID still works in production ===');
  await p.evaluate(()=>{try{start()}catch(e){}}); await p.waitForTimeout(600);
  const got = await p.evaluate(()=>{ const seen=[]; const orig=window.choose;
    window.choose=c=>{seen.push(c);return Promise.resolve()};
    for(const ch of '0006359145') document.dispatchEvent(new KeyboardEvent('keydown',{key:ch,bubbles:true}));
    document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    window.choose=orig; return seen; });
  ok(got.length===1 && got[0]==='fuel', `wedge scan of the fuel card reached the game as "${got[0]}"`);

  console.log('\n=== Ctrl+Shift+D ===');
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'D',ctrlKey:true,shiftKey:true,bubbles:true})));
  await p.waitForTimeout(200);
  v = await vis(p);
  ok(DEVIDS.every(i=>v[i]), 'dev controls appear');
  ok((await p.evaluate(()=>document.getElementById('modePill').textContent)).includes('Developer'),'pill says developer mode');
  ok(!(await p.evaluate(()=>{const w=[];for(const ch of 'D')w.push(ch);return document.getElementById('scanInput').value})),'shortcut did not leak into the scan box');
  await p.close();

  console.log('\n=== choice persists across a reload ===');
  p = await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(700);
  v = await vis(p);
  ok(DEVIDS.every(i=>v[i]), 'still in developer mode after reload');
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'d',ctrlKey:true,shiftKey:true,bubbles:true})));
  await p.waitForTimeout(200);
  v = await vis(p);
  ok(DEVIDS.every(i=>!v[i]), 'lowercase d toggles back to production too');
  await p.close();

  p = await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(700);
  v = await vis(p);
  ok(DEVIDS.every(i=>!v[i]), 'production sticks after another reload');
  await p.close();

  await b.close(); server.close();
  console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
  process.exit(fails?1:0);
})();
