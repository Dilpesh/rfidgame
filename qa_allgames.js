// qa_allgames.js - the before-you-start screen and phone-call recovery, across
// every game that has them. Run from the repo root:
//
//     npm install playwright && node qa_allgames.js
//
// For each game: the shared helpers load, the hooks find their targets (a
// missing one warns rather than silently doing nothing), the intro screen
// lists that game's own cards and activities, the story starts after it, and
// hiding then returning offers a Carry on that names the card they need and
// leaves the story running.
//
// Audio is stubbed: headless Chromium has no audio device, so clips would
// never fire 'ended' and no story would ever advance.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const T={'.html':'text/html','.js':'text/javascript','.css':'text/css'};
const server=http.createServer((q,r)=>{const p=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':T[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const STUB=`Object.defineProperty(navigator,'wakeLock',{configurable:true,
  value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 // no audio device in headless: make every clip finish instantly
 const RA=window.Audio; window.Audio=function(src){const a=new RA();a.play=()=>{setTimeout(()=>a.dispatchEvent(new Event('ended')),5);return Promise.resolve()};return a};
 window.speechSynthesis&&(window.speechSynthesis.speak=u=>{setTimeout(()=>u.onend&&u.onend(),5)});`;

// game -> [how to press start, how to tell a story is running]
const GAMES=[
 ['moon',            'moon',                  "startGame()",  "started"],
 ['jungle-rescue',   'jungle-rescue',         "startGame()",  "started"],
 ['banana-rescue',   'banana-rescue',         "start()",      "!!current"],
 ['jungle-rescue-hinglish','jungle-rescue-hinglish',"handle(start())","active"],
];
(async()=>{
 await new Promise(r=>server.listen(8088,r));
 const b=await chromium.launch();
 for (const [name,slug,startExpr,activeExpr] of GAMES){
  console.log('\n=== '+name+' ===');
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await ctx.addInitScript(STUB);
  const p=await ctx.newPage(); const errs=[],warns=[];
  p.on('pageerror',e=>errs.push(e.message));
  p.on('console',m=>{if(m.type()==='warning'&&/not wired/.test(m.text()))warns.push(m.text())});
  await p.goto('http://localhost:8088/docs/'+slug+'/index.html');
  await p.waitForTimeout(700);
  ok(errs.length===0,'loads clean'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
  ok(await p.evaluate(()=>!!window.InterruptGuard),'interrupt guard loaded');
  ok(await p.evaluate(()=>!!window.StoryIntro),'story intro loaded');
  ok(warns.length===0,'the hooks found their targets'+(warns.length?': '+warns[0]:''));

  await p.evaluate(e=>eval(e),startExpr);
  await p.waitForTimeout(500);
  const shown=await p.$('#storyIntro')!==null;
  ok(shown,'before-you-start screen appears');
  if(shown){
   const t=await p.evaluate(()=>document.querySelector('#storyIntro').innerText);
   ok(/drink/i.test(t),'warns about fetching a real glass of water');
   ok(/Dance|Jump|Clap/i.test(t),'and about the moving-about bits');
   ok(/unwell|just after a meal|settling down/.test(t),'tells a parent when to skip it');
   const n=await p.evaluate(()=>document.querySelectorAll('#storyIntro .si-card').length);
   ok(n>0,`lists ${n} cards`);
   await p.screenshot({path:'/home/claude/all/'+slug+'.png'});
   await p.evaluate(()=>document.querySelector('#si-go').click());
   await p.waitForTimeout(900);
  }
  const running=await p.evaluate(e=>{try{return !!eval(e)}catch(x){return false}},activeExpr);
  ok(running,'story starts after it');

  // a call arrives
  await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});
    Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});
    document.dispatchEvent(new Event('visibilitychange'))});
  await p.waitForTimeout(300);
  await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
    Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'visible'});
    document.dispatchEvent(new Event('visibilitychange'))});
  await p.waitForTimeout(400);
  const co=await p.$('#carryOn');
  ok(co!==null,'coming back offers Carry on');
  if(co){
   const txt=await p.evaluate(()=>document.querySelector('#carryOn').innerText);
   ok(/Looking for/.test(txt),`and names the card they need (${(txt.split('\\n').filter(Boolean).slice(-2)[0]||'').trim()})`);
   await p.evaluate(()=>document.querySelector('#igBtn').click());
   await p.waitForTimeout(700);
   ok(await p.$('#carryOn')===null,'it closes');
   ok(await p.evaluate(e=>{try{return !!eval(e)}catch(x){return false}},activeExpr),'and the story is still running');
  }
  ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
  await p.close(); await ctx.close();
 }
 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
