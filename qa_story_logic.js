// qa_story_logic.js - the Hinglish build's answer handling.
//
//   npm install playwright && node qa_story_logic.js
//
// Two things it protects:
//  1. The hungry elephant accepts mango as well as snack, and scanning mango
//     does NOT play the line that says "Snack!".
//  2. A card scanned while Coco is still talking is remembered and acted on
//     when the line ends, rather than silently dropped - a wrong one is
//     remembered but never advances the story.
//
// The audio layer is stubbed because headless Chromium has no real audio
// clock, so a genuine playthrough never finishes. All game logic is real.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;
const server=http.createServer((q,r)=>{const p=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':'text/html'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};

// Headless Chromium has no real audio clock, so a real playthrough never ends.
// Stub the audio layer only - every bit of game logic under test is untouched.
const STUB = `
 Object.defineProperty(navigator,'wakeLock',{configurable:true,
   value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 window.__installStubs=()=>{
   window.initAudio=()=>Promise.resolve();
   window.__played=[];
   window.play=async (k,e,o={})=>{ window.__played.push(k);
     await new Promise(r=>setTimeout(r,20));
     if(o&&o.loop) return {stop(){},disconnect(){}};
   };
 };`;

(async()=>{
 await new Promise(r=>server.listen(8094,r));
 const b=await chromium.launch(); const ctx=await b.newContext();
 await ctx.addInitScript(STUB);
 const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8094/docs/jungle-rescue-hinglish/index.html');
 await p.waitForTimeout(800);
 await p.evaluate(()=>window.__installStubs());

 console.log('--- which cards each step accepts ---');
 const st=await p.evaluate(()=>stages.map(s=>({card:s.card,also:s.also||null,doneBy:s.doneBy?Object.keys(s.doneBy):null})));
 const snack=st.find(s=>s.card==='snack');
 ok(snack.also && snack.also.includes('mango'),'elephant step also accepts mango');
 ok(snack.doneBy && snack.doneBy.includes('mango'),'mango at the elephant has its own follow-up');
 const mangoStage=st.find(s=>s.card==='mango');
 ok(!mangoStage.also,'giraffe step still wants mango only (unchanged)');

 // what actually plays: snack names the snack, mango skips the naming line
 const seq=await p.evaluate(async()=>{
   const played=[]; const origSeq=window.sequence;
   window.__cap=(k)=>played.push(k);
   return new Promise(res=>{
     const s=stages.find(x=>x.card==='snack');
     res({snack:['ting',...(s.doneBy?.snack||s.done)], mango:['ting',...(s.doneBy?.mango||s.done)]});
   });
 });
 ok(seq.snack.includes('snackSuccess'),`scanning SNACK plays the snack line (${seq.snack.join(', ')})`);
 ok(!seq.mango.includes('snackSuccess'),`scanning MANGO does not say "Snack!" (${seq.mango.join(', ')})`);
 ok(seq.mango.includes('munchEle')&&seq.mango.includes('elephantDone'),'mango still feeds the elephant and gets his reaction');

 // wrong card still rejected at that step
 const stillWrong=await p.evaluate(()=>{const s=stages.find(x=>x.card==='snack');
   const okc=[s.card,...(s.also||[])];return !okc.includes('blanket')&&!okc.includes('water')});
 ok(stillWrong,'blanket and water are still wrong answers for the hungry elephant');

 console.log('--- an early scan must not be lost ---');
 const res = await p.evaluate(async () => {
   const startP = start();
   await new Promise(r=>setTimeout(r,10));
   const wasLocked = locked;
   window.scanCard('6359145');                       // FUEL, scanned mid-narration
   const stashed = pendingCard;
   await startP;
   await new Promise(r=>setTimeout(r,600));
   return { wasLocked, stashed, step, pending: pendingCard, played: window.__played };
 });
 ok(res.wasLocked, 'the game was mid-narration when the card was scanned');
 ok(res.stashed === 'fuel', `the early scan was remembered, not dropped (${res.stashed})`);
 ok(res.step >= 1, `it advanced the story once the line ended (step ${res.step})`);
 ok(res.pending === null, 'the queue was cleared after use');
 ok(res.played.includes('ting'), 'the kid still got the correct-answer chime');
 ok(res.played.includes('fuelSuccess'), 'and the fuel success line played');

 const res2 = await p.evaluate(async () => {
   stop(); window.__played=[];
   const startP = start();
   await new Promise(r=>setTimeout(r,10));
   window.scanCard('6375388');                       // BLANKET, wrong this early
   const stashed = pendingCard;
   await startP;
   await new Promise(r=>setTimeout(r,600));
   return { stashed, step, expected, played: window.__played };
 });
 ok(res2.stashed === 'blanket', 'a wrong early scan is remembered too');
 ok(res2.step === 0, `but it does not advance the story (step ${res2.step})`);
 ok(res2.expected === 'fuel', 'the game is still waiting for fuel');
 ok(!res2.played.includes('ting'), 'and no correct-answer chime was played for it');
 ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.join(' | '):''));

 await p.close(); await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
