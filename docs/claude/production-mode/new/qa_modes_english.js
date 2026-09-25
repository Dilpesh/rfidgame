// qa_modes_english.js - production vs developer mode in docs/jungle-rescue-english.
//   npm install playwright && node qa_modes_english.js
//
// Production is the default and the only thing the kids see: Start, then the
// physical cards. This checks that in reader mode the on-screen card tray and
// the wanted card never appear, that the log stays hidden, that the tray DOES
// appear when playing on screen or after "play without a reader", and that
// developer mode is reachable from a laptop (Ctrl+Shift+D) and a phone (?dev)
// and remembered across reloads. Audio is stubbed - headless Chromium has no
// audio device, so nothing would ever finish playing.
const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=__dirname;
const T={'.html':'text/html','.js':'text/javascript','.json':'application/json'};
const server=http.createServer((q,r)=>{const p=path.join(ROOT,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(p,(e,d)=>e?(r.writeHead(404),r.end()):(r.writeHead(200,{'Content-Type':T[path.extname(p)]||'application/octet-stream'}),r.end(d)));});
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const URL='http://localhost:8095/docs/jungle-rescue-english/index.html';
const STUB=`Object.defineProperty(navigator,'wakeLock',{configurable:true,value:{request:()=>Promise.resolve({released:false,addEventListener(){},release(){return Promise.resolve()}})}});
 class FA extends EventTarget{constructor(s){super();this.src=s||'';this.volume=1;this.loop=false;this.onended=null;this.onerror=null;this.error=null;this.ended=false;this.currentTime=0}
   load(){}pause(){}play(){if(!this.loop)setTimeout(()=>{this.ended=true;this.onended&&this.onended(new Event('ended'))},5);return Promise.resolve()}}
 window.Audio=FA; if(window.speechSynthesis)window.speechSynthesis.speak=u=>setTimeout(()=>u.onend&&u.onend(),5);`;
const type=async(p,s)=>{for(const ch of s) await p.evaluate(c=>document.dispatchEvent(new KeyboardEvent('keydown',{key:c,bubbles:true})),ch);
  await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true})));};
const shown=(p,id)=>p.evaluate(i=>{const e=document.getElementById(i);return !!e&&!e.classList.contains('hide')&&e.offsetParent!==null},id);
const untilQuestion=async(p,ms=8000)=>{const t=Date.now();while(Date.now()-t<ms){if(await p.evaluate(()=>state==='question'))return true;await p.waitForTimeout(40);}return false;};
const startReader=async(p)=>{await p.evaluate(()=>document.getElementById('readerMode').click());await p.waitForTimeout(250);
  await p.evaluate(()=>document.querySelector('#si-go')?.click());await p.waitForTimeout(250);};

(async()=>{
 await new Promise(r=>server.listen(8095,r));
 const b=await chromium.launch();

 console.log('=== fresh browser: production by default ===');
 let ctx=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}); await ctx.addInitScript(STUB);
 let p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.goto(URL); await p.waitForTimeout(500);
 ok(errs.length===0,'no JS errors'+(errs.length?': '+errs.join(' | '):''));
 ok(await shown(p,'readerMode')&&(await p.evaluate(()=>document.getElementById('readerMode').textContent.trim()))==='Start','welcome shows one Start button');
 ok(!await shown(p,'screenMode'),'"Play on screen" is not offered');
 ok(!await shown(p,'nextCue')&&!await shown(p,'modePill'),'no developer controls');
 await startReader(p);
 ok(await p.$('#readerCheck')!==null,'reader check appears');
 await type(p,'0006360574'); await p.waitForTimeout(1500);
 ok(!await shown(p,'log'),'the log stays hidden after a scan');
 ok(await untilQuestion(p),'reaches the first question');
 const q=await p.evaluate(()=>({icon:document.getElementById('wantIcon').textContent,label:document.getElementById('wantLabel').textContent,status:document.getElementById('storyStatus').textContent}));
 ok(!/⛽|Fuel|FUEL/.test(q.icon+q.label+q.status),`nothing on screen names the wanted card (${q.icon} "${q.label}" / "${q.status}")`);
 ok(!await shown(p,'tapGrid'),'the on-screen card tray is hidden in reader mode');
 ok(await p.evaluate(()=>document.getElementById('bar').style.width!==''),'progress bar is still there');
 // a wedge scan still works with everything hidden
 const got=await p.evaluate(async()=>{const seen=[];const o=window.acceptCard;window.acceptCard=c=>seen.push(c);
   for(const ch of '0006359145')document.dispatchEvent(new KeyboardEvent('keydown',{key:ch,bubbles:true}));
   document.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));await new Promise(r=>setTimeout(r,50));window.acceptCard=o;return seen;});
 ok(got.length===1&&got[0]==='FUEL',`a wedge scan of the fuel card still reaches the game (${JSON.stringify(got)})`);

 console.log('\n=== Ctrl+Shift+D on a laptop ===');
 await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'D',ctrlKey:true,shiftKey:true,bubbles:true}))); await p.waitForTimeout(150);
 ok(await shown(p,'nextCue')&&await shown(p,'modePill')&&await shown(p,'log'),'developer controls appear');
 ok(await shown(p,'tapGrid'),'…and the tray, since a question is open');
 ok(await p.evaluate(()=>inputBuffer===''),'the shortcut did not leak into the scan buffer');
 await p.evaluate(()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'d',ctrlKey:true,shiftKey:true,bubbles:true}))); await p.waitForTimeout(150);
 ok(!await shown(p,'nextCue')&&!await shown(p,'tapGrid')&&!await shown(p,'log'),'lowercase d toggles back, tray and log hide again');
 await p.close();

 console.log('\n=== ?dev on a phone, remembered across reloads ===');
 p=await ctx.newPage(); await p.goto(URL+'?dev'); await p.waitForTimeout(400);
 ok(await shown(p,'screenMode')&&await shown(p,'modePill'),'?dev turns developer mode on');
 await p.close(); p=await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(400);
 ok(await shown(p,'screenMode'),'still on after a reload without ?dev');
 await p.close(); p=await ctx.newPage(); await p.goto(URL+'?dev=0'); await p.waitForTimeout(400);
 ok(!await shown(p,'screenMode')&&!await shown(p,'modePill'),'?dev=0 turns it off');
 await p.close(); p=await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(400);
 ok(!await shown(p,'screenMode'),'and production sticks after another reload');
 await p.close(); await ctx.close();

 console.log('\n=== play on screen (developer) shows the tray and works ===');
 ctx=await b.newContext(); await ctx.addInitScript(STUB);
 p=await ctx.newPage(); const e2=[]; p.on('pageerror',e=>e2.push(e.message));
 await p.goto(URL+'?dev'); await p.waitForTimeout(400);
 await p.evaluate(()=>document.getElementById('screenMode').click()); await p.waitForTimeout(250);
 await p.evaluate(()=>document.querySelector('#si-go')?.click()); await p.waitForTimeout(250);
 ok(await p.$('#readerCheck')===null,'no reader check when playing on screen');
 ok(await untilQuestion(p),'reaches the first question');
 ok(await shown(p,'tapGrid')&&(await p.evaluate(()=>document.querySelectorAll('#tapGrid button').length))===8,'tray with all 8 cards is shown');
 ok(!/⛽|Fuel/.test(await p.evaluate(()=>document.getElementById('wantIcon').textContent+document.getElementById('wantLabel').textContent)),'…but still without saying which one');
 await p.evaluate(()=>document.querySelector('#tapGrid [data-card="FUEL"]').click()); await p.waitForTimeout(100);
 ok(await p.evaluate(()=>state==='success'),'tapping the right card on screen advances the story');
 ok(e2.length===0,'no JS errors');
 await p.close(); await ctx.close();

 console.log('\n=== reader does not respond: "play without a reader" turns the tray on ===');
 ctx=await b.newContext(); await ctx.addInitScript(STUB);
 p=await ctx.newPage(); await p.goto(URL); await p.waitForTimeout(400);
 await startReader(p);
 ok(await p.$('#readerCheck')!==null,'reader check appears'); await p.waitForTimeout(12500);
 const btn=await p.evaluate(()=>{const b=[...document.querySelectorAll('#readerCheck .rc-btn')].find(b=>/without a reader/.test(b.textContent));if(b){b.click();return true}return false});
 ok(btn,'offers "play without a reader"');
 ok(await untilQuestion(p),'story starts');
 ok(await shown(p,'tapGrid'),'the tray is on, so the story is still playable');
 ok(!await shown(p,'nextCue'),'but this is not developer mode');
 await p.close(); await ctx.close();

 await b.close(); server.close();
 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
