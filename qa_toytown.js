// qa_toytown.js - the Chuku / Toy Town Express build.
//
//   npm install playwright && node qa_toytown.js
//
// Checks: the landing page order and every tile resolving; production mode
// hiding the on-screen card grid and Next Step; cards seeded from cards.json
// and resolving with or without leading zeros; water keeping both of its
// physical cards; the screen wake lock taken on start and released on reset;
// a scan arriving mid-narration being remembered and played when the game is
// ready; and Ctrl+Shift+D toggling and persisting.
//
// The audio layer is stubbed - headless Chromium has no audio clock, so a real
// playthrough never finishes. All game logic is the shipped code.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;
const cards=JSON.parse(fs.readFileSync(ROOT+'/cards.json','utf8'));
const TYPES={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json'};
const server=http.createServer((q,r)=>{const p=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':TYPES[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const URL='http://localhost:8093/docs/toy-town/index.html';
// Headless Chromium has no audio clock, so stub the audio layer; all game logic is real.
const STUB=`
 window.__wake={requests:0,releases:0,type:null};
 Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:t=>{
   window.__wake.requests++;window.__wake.type=t;
   return Promise.resolve({released:false,addEventListener(){},release(){window.__wake.releases++;return Promise.resolve()}})}}});
 window.__stubAudio=(a)=>{
   window.__played=[];
   a.resume=async function(){this.ctx={currentTime:0,state:'running',resume:async()=>{},suspend:async()=>{}}};
   a.suspend=async function(){};
   a.play=async function(k){window.__played.push(k);await new Promise(r=>setTimeout(r,5))};
   a.loop=async function(){};a.bed=async function(){};a.fan=async function(){};
   a.music=async function(){};a.stopMusic=function(){};a.stopAll=function(){};
   a.wait=function(sec,s){return new Promise((res,rej)=>{const t=setTimeout(res,5);
     s&&s.addEventListener&&s.addEventListener('abort',()=>{clearTimeout(t);rej(new DOMException('Cancelled','AbortError'))},{once:true})})};
 };`;

(async()=>{
 await new Promise(r=>server.listen(8093,r));
 const b=await chromium.launch(); const ctx=await b.newContext();
 await ctx.addInitScript(STUB);

 console.log('=== landing page ===');
 let p=await ctx.newPage(); const e0=[]; p.on('pageerror',e=>e0.push(e.message));
 await p.goto('http://localhost:8093/docs/index.html'); await p.waitForTimeout(300);
 ok(e0.length===0,'no JS errors'+(e0.length?': '+e0.join(' | '):''));
 const tiles=await p.$$eval('.tile',els=>els.map(e=>e.getAttribute('href')));
 ok(tiles.length===7,`7 tiles (${tiles.length})`);
 ok(tiles[1]==='toy-town/index.html',`Toy Town is second (${tiles[1]})`);
 for(const h of tiles.filter(Boolean)){const r=await p.goto('http://localhost:8093/docs/'+h);
  ok(r.status()===200,`${h} resolves (${r.status()})`); await p.goBack();}
 await p.close();

 console.log('\n=== toy-town: production by default ===');
 p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto(URL); await p.waitForTimeout(500);
 ok(errs.length===0,'loads clean'+(errs.length?': '+errs.join(' | '):''));
 ok(await p.evaluate(()=>$('cards').hidden),'on-screen card grid hidden');
 ok(await p.evaluate(()=>$('next').hidden),'Next Step hidden');
 ok(await p.evaluate(()=>!$('start').hidden&&!$('reset').hidden),'Start and Reset still there');
 ok((await p.evaluate(()=>$('modePill').textContent)).includes('Card mode'),'pill says card mode');

 console.log('\n=== cards seeded from cards.json ===');
 const want=[];
 for(const v of Object.values(cards.cards)){const g=(v.games||{})['toy-town'];
   if(g&&v.uids.length) for(const u of v.uids) want.push([u,g,v.label]);}
 ok(want.length===3,`3 cards already have physical cards (${want.length})`);
 for(const [uid,id,label] of want){
   for(const form of [uid,uid.replace(/^0+/,'')]){
     const got=await p.evaluate(u=>{const q=normUid(u);
       return Object.keys(mapping).find(k=>uidList(mapping[k]).some(x=>normUid(x)===q))||null;},form);
     ok(got===id,`${label.padEnd(8)} "${form}" -> ${got} (want ${id})`);
   }
 }
 ok(await p.evaluate(()=>uidList(mapping.water).length===2),'water keeps both of its physical cards');
 ok(await p.evaluate(()=>!mapping.key||!uidList(mapping.key).length),'key has no card yet, as expected');

 console.log('\n=== wake lock + early scan ===');
 await p.evaluate(()=>window.__stubAudio(audio));
 ok(await p.evaluate(()=>window.__wake.requests===0),'no lock just from opening the page');
 await p.evaluate(()=>$('start').click());
 await p.waitForTimeout(400);
 ok(await p.evaluate(()=>window.__wake.requests>=1),'lock taken when the story starts');
 ok(await p.evaluate(()=>window.__wake.type==='screen'),'requested type is "screen"');

 const early=await p.evaluate(async()=>{
   // force a non-answering phase, then scan
   game.phase='setup';game.emit&&game.emit();
   window.scanCard('6360574');            // MUSIC
   const stashed=pendingCard;
   game.phase='waiting';game.emit&&game.emit();
   await new Promise(r=>setTimeout(r,120));
   return {stashed,after:pendingCard};
 });
 ok(early.stashed==='music',`a scan mid-narration is remembered (${early.stashed})`);
 ok(early.after===null,'and is consumed once the game can take it');

 await p.evaluate(()=>$('reset').click()); await p.waitForTimeout(200);
 ok(await p.evaluate(()=>window.__wake.releases>=1),'lock released on reset');

 console.log('\n=== Ctrl+Shift+D ===');
 await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'D',ctrlKey:true,shiftKey:true,bubbles:true})));
 await p.waitForTimeout(150);
 ok(await p.evaluate(()=>!$('cards').hidden&&!$('next').hidden),'dev controls appear');
 await p.close();
 p=await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(400);
 ok(await p.evaluate(()=>!$('cards').hidden),'choice survives a reload');
 await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'d',ctrlKey:true,shiftKey:true,bubbles:true})));
 await p.waitForTimeout(150);
 ok(await p.evaluate(()=>$('cards').hidden),'toggles back to production');
 await p.close();

 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
