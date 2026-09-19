// qa_progress.js - the story survives the page being thrown away.
//
//     npm install playwright && node qa_progress.js
//
// Android discards a backgrounded tab and the page comes back as a fresh
// load. For each game: start it, move a few steps in, send the page to the
// background (which is all the warning a discard gives), reload from scratch,
// and check the grown-up is offered Carry on - and that carrying on lands on
// the step they left, not the first one. Then check Start from the beginning
// really does clear it, and that a story which ENDS leaves nothing behind.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const T={'.html':'text/html','.js':'text/javascript','.css':'text/css'};
const server=http.createServer((q,r)=>{const p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':T[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const STUB=`Object.defineProperty(navigator,'wakeLock',{configurable:true,
  value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 const RA=window.Audio; window.Audio=function(s){const a=new RA();a.play=()=>{setTimeout(()=>a.dispatchEvent(new Event('ended')),5);return Promise.resolve()};return a};
 window.speechSynthesis&&(window.speechSynthesis.speak=u=>{setTimeout(()=>u.onend&&u.onend(),5)});
 window.__stubTT=a=>{a.resume=async function(){this.ctx={currentTime:0,state:'running'};this.__ok=true};
   a.running=function(){return this.__ok!==false};a.suspend=async function(){};
   a.play=async()=>{};a.loop=async()=>{};a.bed=async()=>{};a.fan=async()=>{};a.music=async()=>{};
   a.stopMusic=()=>{};a.stopAll=()=>{};a.wait=()=>new Promise(r=>setTimeout(r,5));};`;

// slug, key, how to start, is it running, put it on step N, which step is it on, a step worth stopping at
const GAMES=[
 ['moon','moon','startGame()','started','stepIdx=3','stepIdx',3],
 ['jungle-rescue','jungle-rescue','startGame()','started','stepIdx=4','stepIdx',4],
 ['banana-rescue','banana-rescue','start()','!!current',"waitFor('LADDER')",
   "order.indexOf(current)",4],
 ['jungle-rescue-hinglish','jungle-rescue-hinglish','handle(start())','active','step=3','step',3],
 ['toy-town','toy-town',"$('start').click()",'game.active','game.index=3','game.index',3],
];
const type=async(p,s)=>{for(const ch of s) await p.evaluate(c=>document.dispatchEvent(new KeyboardEvent('keydown',{key:c,bubbles:true})),ch);
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true})));};
const hide=async p=>{await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});
  Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});document.dispatchEvent(new Event('visibilitychange'))});};
const ev=(p,e)=>p.evaluate(x=>{try{return eval(x)}catch(err){return '<'+err.message+'>'}},e);

(async()=>{
 await new Promise(r=>server.listen(8088,r));
 const b=await chromium.launch();
 for (const [slug,key,startExpr,activeExpr,setStep,readStep,want] of GAMES){
  console.log('\n=== '+slug+' ===');
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await ctx.addInitScript(STUB);
  const p=await ctx.newPage(); const errs=[];
  p.on('pageerror',e=>errs.push(e.message));
  const load=async()=>{await p.goto('http://localhost:8088/docs/'+slug+'/index.html');
    await p.waitForTimeout(700);
    if(slug==='toy-town') await p.evaluate(()=>window.__stubTT(audio));};

  await load();
  ok(await p.evaluate(()=>!!window.Progress),'Progress present');

  // start the story properly, the way a parent does
  await p.evaluate(e=>eval(e),startExpr); await p.waitForTimeout(400);
  if(await p.$('#storyIntro')){await p.evaluate(()=>document.querySelector('#si-go').click());await p.waitForTimeout(400)}
  if(await p.$('#readerCheck')){await type(p,'0006360574');await p.waitForTimeout(1400)}
  await p.waitForTimeout(600);
  ok(await ev(p,activeExpr)===true,'story running');

  // a few steps in, then the phone takes the tab away
  await p.evaluate(e=>eval(e),setStep);
  await p.waitForTimeout(1500);                 // the tracker's poll
  await hide(p); await p.waitForTimeout(200);
  const saved=await p.evaluate(k=>Progress.read(k),key);
  ok(saved && saved.i===want,`step ${want} written (${saved?saved.i:'nothing'})`);

  // ---- the discard: a brand new page, nothing in memory ----
  errs.length=0;
  await load();
  ok(errs.length===0,'reloads clean'+(errs.length?': '+errs[0]:''));
  const offer=await p.$('#pgResume');
  ok(offer!==null,'Carry on is offered after the reload');
  if(offer){
   const label=await p.evaluate(()=>document.querySelector('#pgResume .pg-at').textContent);
   ok(/\S/.test(label),'it names the step: '+label.replace(/\s+/g,' ').trim());
   ok(await ev(p,activeExpr)!==true,'and nothing has started behind it');
   await p.evaluate(()=>document.querySelector('#pg-go').click());
   await p.waitForTimeout(1500);
   ok(await p.$('#pgResume')===null,'it closes');
   ok(await ev(p,activeExpr)===true,'story running again');
   const at=await ev(p,readStep);
   ok(at===want,`and on step ${want}, not the first (${at})`);
   ok(errs.length===0,'no JS errors resuming'+(errs.length?': '+errs[0]:''));
  }

  // ---- Start from the beginning really does ----
  await p.evaluate(e=>eval(e),setStep); await p.waitForTimeout(1500); await hide(p);
  await load();
  if(await p.$('#pg-fresh')){
   await p.evaluate(()=>document.querySelector('#pg-fresh').click());
   await p.waitForTimeout(200);
   ok(await p.evaluate(k=>Progress.read(k),key)===null,'Start from the beginning clears it');
  } else ok(false,'second offer did not appear');

  // ---- a story that ENDS leaves nothing to resume ----
  await p.evaluate(e=>eval(e),startExpr); await p.waitForTimeout(400);
  if(await p.$('#storyIntro')){await p.evaluate(()=>document.querySelector('#si-go').click());await p.waitForTimeout(400)}
  if(await p.$('#readerCheck')){await type(p,'0006360574');await p.waitForTimeout(1400)}
  await p.evaluate(e=>eval(e),setStep); await p.waitForTimeout(1400);
  ok(await p.evaluate(k=>!!Progress.read(k),key),'a running story is saved');
  await p.evaluate(s=>{ // end it the way finishing or Reset does
    if(s==='banana-rescue'){current=null;return}
    if(s==='toy-town'){game.active=false;return}
    if(s==='jungle-rescue-hinglish'){active=false;return}
    started=false;
  },slug);
  await p.waitForTimeout(1500);
  ok(await p.evaluate(k=>Progress.read(k),key)===null,'a finished story leaves nothing behind');

  await p.close(); await ctx.close();
 }
 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
