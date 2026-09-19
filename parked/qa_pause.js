// qa_pause.js - pressing Pause is not a phone call.
//
//     npm install playwright && node qa_pause.js
//
// Pause suspends the AudioContext, which from interrupt-guard.js looks exactly
// like a call killing the audio: within 1.5s it covered the Pause screen with
// "Carry on", and carrying on replayed the whole stop from its first line.
// A grown-up pausing to answer a question lost the scene.
//
// What must hold now:
//   * Pause shows no Carry on screen, however long you leave it
//   * Resume carries on where it was - the stop is not re-entered
//   * a REAL interruption still offers Carry on
//   * carrying on from a merely suspended context continues mid-sentence
//   * carrying on from a CLOSED one replays the stop, because the clip is gone
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const T={'.html':'text/html','.js':'text/javascript','.css':'text/css'};
const server=http.createServer((q,r)=>{const p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':T[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};

// An audio stub that models the real state machine, because the bug IS the
// state machine: suspended is recoverable in place, closed is not.
const STUB=`Object.defineProperty(navigator,'wakeLock',{configurable:true,
  value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 window.__stubTT=a=>{
  a.ctx=null;
  a.resume=async function(){if(this.ctx&&this.ctx.state==='closed')this.ctx=null;
    if(!this.ctx)this.ctx={state:'running',currentTime:0};this.ctx.state='running'};
  a.running=function(){return !!(this.ctx&&this.ctx.state==='running')};
  a.suspend=async function(){if(this.ctx)this.ctx.state='suspended'};
  a.now=function(){return this.ctx?this.ctx.currentTime:0};
  a.play=async()=>{};a.loop=async()=>{};a.bed=async()=>{};a.fan=async()=>{};
  a.music=async()=>{};a.stopMusic=()=>{};a.stopAll=()=>{};
  a.wait=()=>new Promise(r=>setTimeout(r,5));};`;
const type=async(p,s)=>{for(const ch of s) await p.evaluate(c=>document.dispatchEvent(new KeyboardEvent('keydown',{key:c,bubbles:true})),ch);
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true})));};
const vis=async(p,hidden)=>p.evaluate(h=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>h});
  Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>h?'hidden':'visible'});
  document.dispatchEvent(new Event('visibilitychange'))},hidden);

(async()=>{
 await new Promise(r=>server.listen(8090,r));
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 await ctx.addInitScript(STUB);
 const p=await ctx.newPage(); const errs=[];
 p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://localhost:8090/docs/toy-town/index.html');
 await p.waitForTimeout(700);
 await p.evaluate(()=>window.__stubTT(audio));
 // count every re-entry of a stop, so "it replayed the scene" is measurable
 await p.evaluate(()=>{window.__enters=0;const e=game.enter.bind(game);
   game.enter=i=>{window.__enters++;return e(i)}});

 await p.evaluate(()=>$('start').click()); await p.waitForTimeout(400);
 if(await p.$('#storyIntro')){await p.evaluate(()=>document.querySelector('#si-go').click());await p.waitForTimeout(400)}
 if(await p.$('#readerCheck')){await type(p,'0006360574');await p.waitForTimeout(1400)}
 await p.waitForTimeout(600);
 ok(await p.evaluate(()=>game.active),'story running');
 await p.evaluate(()=>{game.index=3;game.emit()});
 const enters0=await p.evaluate(()=>window.__enters);

 // ---- a grown-up presses Pause ----
 console.log('\n-- Pause --');
 await p.evaluate(()=>$('pause').click());
 await p.waitForTimeout(3500);                      // two full health polls
 ok(await p.evaluate(()=>game.paused),'the story is paused');
 ok(await p.evaluate(()=>!audio.running()),'and the audio really is suspended');
 ok(await p.$('#carryOn')===null,'no Carry on screen over the Pause screen');

 // ---- and Resume ----
 await p.evaluate(()=>$('pause').click()); await p.waitForTimeout(600);
 ok(await p.evaluate(()=>!game.paused),'Resume unpauses');
 ok(await p.evaluate(()=>game.index)===3,'still on the same stop');
 ok(await p.evaluate(()=>window.__enters)===enters0,'and the stop was NOT replayed');

 // ---- a real phone call, context survives ----
 console.log('\n-- a call, audio suspended --');
 const e1=await p.evaluate(()=>window.__enters);
 await vis(p,true); await p.waitForTimeout(300);
 await p.evaluate(()=>{audio.ctx.state='suspended'});
 await vis(p,false); await p.waitForTimeout(500);
 ok(await p.$('#carryOn')!==null,'Carry on IS offered');
 await p.evaluate(()=>document.querySelector('#igBtn').click()); await p.waitForTimeout(800);
 ok(await p.$('#carryOn')===null,'it closes');
 ok(await p.evaluate(()=>game.active&&!game.paused),'story running again');
 ok(await p.evaluate(()=>window.__enters)===e1,'it carried on mid-sentence, no replay');
 ok(await p.evaluate(()=>game.index)===3,'same stop');

 // ---- a call that KILLED the context ----
 console.log('\n-- a call, audio context closed --');
 const e2=await p.evaluate(()=>window.__enters);
 await vis(p,true); await p.waitForTimeout(300);
 await p.evaluate(()=>{audio.ctx.state='closed'});
 await vis(p,false); await p.waitForTimeout(500);
 ok(await p.$('#carryOn')!==null,'Carry on is offered');
 await p.evaluate(()=>document.querySelector('#igBtn').click()); await p.waitForTimeout(900);
 ok(await p.evaluate(()=>window.__enters)>e2,'the stop IS replayed - the clip was lost');
 ok(await p.evaluate(()=>game.index)===3,'and it replays THAT stop, not the first');
 ok(await p.evaluate(()=>game.active&&!game.paused),'story running again');

 ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
