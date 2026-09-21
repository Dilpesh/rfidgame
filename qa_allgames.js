// qa_allgames.js - the shared runtime, across every card story.
//
//     npm install playwright && node qa_allgames.js
//
// For each game, in a phone-sized browser: the shared modules load and every
// hook finds its target (a missing one warns rather than silently doing
// nothing); the before-you-start screen appears, then the reader check, then
// the story; and the scan guard, exercised through the reader path the child
// actually uses, lets a real scan through while dropping an immediate repeat
// and a one-character read.
//
// The phone-call checks moved to parked/qa_interrupt.js when the Carry on
// screens came out of the games. See BACKLOG.
//
// Audio is stubbed - headless Chromium has no audio device, so clips would
// never fire 'ended' and no story would ever advance.
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
const GAMES=[
 ['moon','moon','startGame()','started'],
 ['jungle-rescue','jungle-rescue','startGame()','started'],
 ['banana-rescue','banana-rescue','start()','!!current'],
 ['jungle-rescue-hinglish','jungle-rescue-hinglish','handle(start())','active'],
 ['toy-town','toy-town',"$('start').click()",'game.active'],
 ['toy-town-v2','toy-town-v2',"$('start').click()",'game.active'],
];
const type=async(p,s)=>{for(const ch of s) await p.evaluate(c=>document.dispatchEvent(new KeyboardEvent('keydown',{key:c,bubbles:true})),ch);
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true})));};
(async()=>{
 await new Promise(r=>server.listen(8087,r));
 const b=await chromium.launch();
 for (const [name,slug,startExpr,activeExpr] of GAMES){
  console.log('\n=== '+name+' ===');
  const ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await ctx.addInitScript(STUB);
  const p=await ctx.newPage(); const errs=[],warns=[];
  p.on('pageerror',e=>errs.push(e.message));
  p.on('console',m=>{if(m.type()==='warning'&&/not wired|no .*\(\) to guard/.test(m.text()))warns.push(m.text())});
  await p.goto('http://localhost:8087/docs/'+slug+'/index.html'); await p.waitForTimeout(700);
  if(slug.startsWith('toy-town')) await p.evaluate(()=>window.__stubTT(audio));
  ok(errs.length===0,'loads clean'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
  for(const api of ['ScanGuard','ReaderCheck','StoryIntro'])
    ok(await p.evaluate(a=>!!window[a],api),`${api} present`);
  ok(warns.length===0,'every hook found its target'+(warns.length?': '+warns[0]:''));

  // --- intro, then reader check, then the story ---
  await p.evaluate(e=>eval(e),startExpr); await p.waitForTimeout(500);
  ok(await p.$('#storyIntro')!==null,'before-you-start screen appears');
  await p.evaluate(()=>document.querySelector('#si-go').click()); await p.waitForTimeout(500);
  ok(await p.$('#readerCheck')!==null,'then the reader check');
  await type(p,'0006360574'); await p.waitForTimeout(1400);
  ok(await p.$('#readerCheck')===null,'a scan dismisses it');
  await p.waitForTimeout(700);
  ok(await p.evaluate(e=>{try{return !!eval(e)}catch(x){return false}},activeExpr),'story running');

  // --- the scan guard, on the real entry point, with the story running ---
  const before=await p.evaluate(()=>({...ScanGuard.stats}));
  await type(p,'0006359145'); await type(p,'0006359145');     // same card twice, fast
  await p.waitForTimeout(80);
  await type(p,'x');                                          // noise, not a card
  const after=await p.evaluate(()=>({...ScanGuard.stats}));
  ok(after.passed-before.passed>=1,`a real scan gets through (${after.passed-before.passed})`);
  ok(after.repeat-before.repeat>=1 || after.bounce-before.bounce>=1,
     `the immediate repeat is ignored (repeat ${after.repeat-before.repeat}, bounce ${after.bounce-before.bounce})`);
  ok(after.tooShort-before.tooShort>=1,'a one-character read is ignored');

  ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.slice(0,2).join(' | '):''));
  await p.close(); await ctx.close();
 }
 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
