// qa_readercheck.js - the reader check and its OTG guidance.
//   npm install playwright && node qa_readercheck.js
// Steps through the before-you-start screen first, since that now comes ahead
// of the reader check. Audio is stubbed - headless Chromium has no audio clock.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;
const T={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json'};
const server=http.createServer((q,r)=>{const p=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':T[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const URL='http://localhost:8091/docs/toy-town/index.html';
const STUB=`Object.defineProperty(navigator,'wakeLock',{configurable:true,
  value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 window.__stub=a=>{a.resume=async function(){this.ctx={currentTime:0,state:'running',resume:async()=>{},suspend:async()=>{}}};
  a.play=async()=>{};a.loop=async()=>{};a.bed=async()=>{};a.fan=async()=>{};a.music=async()=>{};
  a.stopMusic=()=>{};a.stopAll=()=>{};a.wait=()=>new Promise(r=>setTimeout(r,5));};`;
const type=async(p,s)=>{for(const ch of s) await p.evaluate(c=>document.dispatchEvent(new KeyboardEvent('keydown',{key:c,bubbles:true})),ch);
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true})));};
(async()=>{
 await new Promise(r=>server.listen(8091,r));
 const b=await chromium.launch();

 console.log('=== reader works ===');
 let ctx=await b.newContext(); await ctx.addInitScript(STUB);
 let p=await ctx.newPage(); const e1=[]; p.on('pageerror',e=>e1.push(e.message));
 await p.goto(URL); await p.waitForTimeout(500); await p.evaluate(()=>window.__stub(audio));
 ok(e1.length===0,'loads clean'+(e1.length?': '+e1.join(' | '):''));
 ok(await p.evaluate(()=>!ReaderCheck.known()),'fresh browser has not confirmed a reader');
 await p.evaluate(()=>$('start').click()); await p.waitForTimeout(250);
 await p.evaluate(()=>document.querySelector('#si-go')?.click()); await p.waitForTimeout(250);
 ok(await p.$('#readerCheck')!==null,'the check appears instead of starting the story');
 ok(await p.evaluate(()=>!game.active),'the story has NOT started yet');
 await type(p,'5688918');                       // the real key card
 await p.waitForTimeout(1500);
 ok(await p.$('#readerCheck')===null,'a real scan dismisses it');
 ok(await p.evaluate(()=>ReaderCheck.known()),'and it is remembered for this browser');
 ok(await p.evaluate(()=>game.active),'the story started');
 await p.close();
 p=await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(400);
 await p.evaluate(()=>window.__stub(audio));
 await p.evaluate(()=>$('start').click()); await p.waitForTimeout(300);
 await p.evaluate(()=>document.querySelector('#si-go')?.click()); await p.waitForTimeout(250);
 ok(await p.$('#readerCheck')===null,'never asked again on this browser');
 await p.close(); await ctx.close();

 console.log('\n=== reader does not respond ===');
 ctx=await b.newContext(); await ctx.addInitScript(STUB);
 p=await ctx.newPage(); const e2=[]; p.on('pageerror',e=>e2.push(e.message));
 await p.goto(URL); await p.waitForTimeout(500); await p.evaluate(()=>window.__stub(audio));
 await p.evaluate(()=>$('start').click()); await p.waitForTimeout(250);
 await p.evaluate(()=>document.querySelector('#si-go')?.click()); await p.waitForTimeout(250);
 ok(await p.$('#readerCheck')!==null,'the check appears');
 await p.waitForTimeout(12500);                  // let it time out
 const help=await p.evaluate(()=>document.querySelector('#readerCheck')?.innerText||'');
 ok(/No card came through/.test(help),'it explains rather than just failing');
 ok(!/Turn on OTG/.test(help),'no OTG step on a desktop browser, where OTG is meaningless');
 ok(/cable|adapter/i.test(help),'and names the charge-only cable as a likely culprit');
 ok(/Try again/.test(help),'offers Try again');
 // the escape hatch must actually let a child play
 await p.evaluate(()=>[...document.querySelectorAll('#readerCheck .rc-btn')].find(b=>/without a reader/.test(b.textContent)).click());
 await p.waitForTimeout(400);
 ok(await p.$('#readerCheck')===null,'"play without a reader" closes it');
 ok(await p.evaluate(()=>!$('cards').hidden),'and turns the on-screen cards on, so the story is still playable');
 ok(await p.evaluate(()=>game.active),'the story starts');
 ok(e2.length===0,'no JS errors'+(e2.length?': '+e2.join(' | '):''));
 await p.close(); await ctx.close();

 console.log('\n=== on an Android phone ===');
 ctx=await b.newContext({userAgent:'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36',
   viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 await ctx.addInitScript(STUB+`
   Object.defineProperty(navigator,'userAgentData',{configurable:true,
     value:{getHighEntropyValues:async()=>({model:'22101316C'})}});`);   // a Redmi model
 p=await ctx.newPage(); const e3=[]; p.on('pageerror',e=>e3.push(e.message));
 await p.goto(URL); await p.waitForTimeout(500); await p.evaluate(()=>window.__stub(audio));
 const d=await p.evaluate(()=>ReaderCheck._device());
 ok(d.android===true,'detected as Android');
 ok(d.model==='22101316C',`real model read via client hints despite the frozen UA (${d.model})`);
 await p.evaluate(()=>$('start').click()); await p.waitForTimeout(250);
 await p.evaluate(()=>document.querySelector('#si-go')?.click()); await p.waitForTimeout(250);
 await p.waitForTimeout(12500);
 const h2=await p.evaluate(()=>document.querySelector('#readerCheck')?.innerText||'');
 ok(/Settings/.test(h2)&&/OTG/.test(h2),'tells them to search Settings for OTG');
 ok(/search box/.test(h2),'and points at the Settings search box, which works on every skin');
 ok(/ten minutes/.test(h2),'warns that OTG switches itself back off');
 ok(/Xiaomi/.test(h2)&&/realme/.test(h2)&&/vivo/.test(h2)&&/Samsung/.test(h2),
    'lists where OTG lives on every common brand, so an unrecognised phone is still helped');
 ok(e3.length===0,'no JS errors'+(e3.length?': '+e3.join(' | '):''));
 // the overlay must fit a phone screen
 const box=await p.evaluate(()=>{const b=document.querySelector('#readerCheck .rc-box').getBoundingClientRect();
   return {w:Math.round(b.width),h:Math.round(b.height),vw:innerWidth,vh:innerHeight}});
 ok(box.w<=box.vw && box.h<=box.vh,`overlay fits a 390x844 phone (${box.w}x${box.h})`);
 await p.close(); await ctx.close();

 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
