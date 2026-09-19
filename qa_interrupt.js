// qa_interrupt.js - the before-you-start screen and surviving a phone call.
//   npm install playwright && node qa_interrupt.js
// Simulates a call: hide the page, come back, and check the story resumes on
// the same step with audio actually replaying; then kills the audio context
// outright and checks the watchdog rebuilds it.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const T={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json'};
const server=http.createServer((q,r)=>{const p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':T[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const URL='http://localhost:8089/docs/toy-town/index.html';
const STUB=`Object.defineProperty(navigator,'wakeLock',{configurable:true,
  value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 window.__stub=a=>{window.__played=[];
  a.__state='running';
  a.resume=async function(){if(this.__state==='closed'){this.buffers.clear()}this.__state='running';this.ctx={currentTime:0,state:'running'}};
  a.running=function(){return this.__state==='running'};
  a.suspend=async function(){this.__state='suspended';if(this.ctx)this.ctx.state='suspended'};
  a.play=async function(k){window.__played.push(k);await new Promise(r=>setTimeout(r,5))};
  a.loop=async()=>{};a.bed=async()=>{};a.fan=async()=>{};a.music=async()=>{};
  a.stopMusic=()=>{};a.stopAll=()=>{};a.wait=()=>new Promise(r=>setTimeout(r,5));};`;
(async()=>{
 await new Promise(r=>server.listen(8089,r));
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 await ctx.addInitScript(STUB);
 const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto(URL); await p.waitForTimeout(500);
 await p.evaluate(()=>window.__stub(audio));
 ok(errs.length===0,'loads clean'+(errs.length?': '+errs.join(' | '):''));

 console.log('\n=== the before-you-start screen ===');
 await p.evaluate(()=>$('start').click()); await p.waitForTimeout(300);
 ok(await p.$('#storyIntro')!==null,'shows before anything else');
 ok(await p.evaluate(()=>!game.active),'the story has not started');
 const t=await p.evaluate(()=>document.querySelector('#storyIntro').innerText);
 for(const c of ['KEY','LIGHT','FAN','WATER','MUSIC','BISCUIT'])
   ok(t.includes(c),`lists the ${c} card`);
 ok(/you have two/.test(t),'notes that water has two cards');
 ok(/cookie card/.test(t),'notes the biscuit is the cookie card');
 for(const a of ['Dance','drink','Clap','Tiptoe']) ok(t.includes(a),`warns about: ${a}`);
 ok(/unwell|just after a meal|settling down/.test(t),'tells a parent when to skip it');
 ok(/13 minutes/.test(t),'says how long it takes');
 await p.screenshot({path:'/home/claude/tt/intro.png'});
 // start it
 await p.evaluate(()=>document.querySelector('#si-go').click()); await p.waitForTimeout(300);
 ok(await p.$('#storyIntro')===null,'closes on Start');
 // reader check comes next
 ok(await p.$('#readerCheck')!==null,'then the reader check');
 await p.evaluate(()=>[...document.querySelectorAll('#readerCheck .rc-btn')].find(b=>/without a reader/.test(b.textContent)).click());
 await p.waitForTimeout(600);
 ok(await p.evaluate(()=>game.active),'story running');

 console.log('\n=== a phone call arrives ===');
 const before=await p.evaluate(()=>game.index);
 await p.evaluate(()=>{ Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});
   Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});
   document.dispatchEvent(new Event('visibilitychange')); });
 await p.waitForTimeout(400);
 ok(await p.evaluate(()=>game.paused),'the story pauses and the audio stops');
 await p.evaluate(()=>{ Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'visible'});
   Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
   document.dispatchEvent(new Event('visibilitychange')); });
 await p.waitForTimeout(400);
 ok(await p.$('#carryOn')!==null,'coming back offers one big Carry on button');
 const co=await p.evaluate(()=>document.querySelector('#carryOn').innerText);
 ok(/Nothing is lost/.test(co),'and reassures that nothing is lost');
 await p.evaluate(()=>window.__played=[]);
 await p.evaluate(()=>document.querySelector('#coBtn').click());
 await p.waitForTimeout(900);
 ok(await p.$('#carryOn')===null,'the overlay closes');
 ok(await p.evaluate(()=>!game.paused&&game.active),'the story is running again');
 ok(await p.evaluate(()=>game.index)===before,`still on the same step (${before})`);
 ok(await p.evaluate(()=>window.__played.length>0),'and it replays that step rather than sitting silent');

 console.log('\n=== the call killed the audio context outright ===');
 await p.evaluate(()=>{audio.__state='closed';if(audio.ctx)audio.ctx.state='closed';});
 await p.waitForTimeout(2200);                       // the watchdog polls every 1.5s
 ok(await p.$('#carryOn')!==null,'the watchdog notices even with no visibilitychange');
 await p.evaluate(()=>document.querySelector('#coBtn').click());
 await p.waitForTimeout(900);
 ok(await p.evaluate(()=>audio.running()),'the context is rebuilt');
 ok(await p.evaluate(()=>game.active&&!game.paused),'and the story carries on');
 ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.join(' | '):''));

 console.log('\n=== "do not show again" ===');
 await p.evaluate(()=>{StoryIntro.forget('toy-town');});
 const p2=await ctx.newPage(); await p2.goto(URL); await p2.waitForTimeout(400);
 await p2.evaluate(()=>window.__stub(audio));
 await p2.evaluate(()=>$('start').click()); await p2.waitForTimeout(300);
 ok(await p2.$('#storyIntro')!==null,'shown again after forgetting');
 await p2.evaluate(()=>document.querySelector('#si-skip').click()); await p2.waitForTimeout(400);
 const p3=await ctx.newPage(); await p3.goto(URL); await p3.waitForTimeout(400);
 await p3.evaluate(()=>window.__stub(audio));
 await p3.evaluate(()=>$('start').click()); await p3.waitForTimeout(300);
 ok(await p3.$('#storyIntro')===null,'and stays hidden after do-not-show-again');

 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
