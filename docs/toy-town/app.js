const $=id=>document.getElementById(id);
const CARDS=[['key','🔑','KEY'],['light','💡','LIGHT'],['fan','🌀','FAN'],['water','💧','WATER'],['music','🎵','MUSIC'],['biscuit','🍪','BISCUIT']];
/* ===== CARD UIDS - generated from cards.json by sync_cards.py, do not edit ===== */
/* __CARD_UIDS_START__ */
const SEED_VERSION = "2026-10-03c";
const DEFAULT_UIDS = {
  "5720648":   "biscuit",
  "6373651":   "biscuit",
  "819771714": "biscuit",
  "5688164":   "fan",
  "5688918":   "key",
  "5687908":   "light",
  "6360574":   "music",
  "819667906": "music",
  "2682976":   "water",
  "2690428":   "water"
};
/* __CARD_UIDS_END__ */

// Readers differ on leading zeros, case and stray whitespace, and a card can
// have two physical copies (water and torch do), so every entry is a list.
const normUid=v=>String(v==null?'':v).trim().toUpperCase().replace(/^0+(?=.)/,'');
const uidList=v=>(Array.isArray(v)?v:[v]).filter(Boolean);
let mapping={};
try{const m=JSON.parse(localStorage.getItem('chukuCardMap')||'{}');
 for(const k in m)mapping[k]=uidList(m[k])}catch{}
// Seed the printed cards once per browser, and again when the printed set
// changes. Anything taught by hand always wins.
try{
 if(localStorage.getItem('chukuCardMap:seed')!==SEED_VERSION){
  for(const u in DEFAULT_UIDS){const card=DEFAULT_UIDS[u];
   const cur=uidList(mapping[card]);
   if(!cur.some(x=>normUid(x)===normUid(u)))cur.push(u);
   mapping[card]=cur}
  localStorage.setItem('chukuCardMap:seed',SEED_VERSION);
  localStorage.setItem('chukuCardMap',JSON.stringify(mapping));
 }
}catch{/* private window - game still works, cards just need teaching */}

let teaching=null,wedge='',lastKey=0;
const audio=new ChukuAudio(CHUKU_STORY.dialogue);

/* ---- keep the screen awake ----
   The phone lies face down through three 20-second dance rounds with nobody
   touching it. Needs https or localhost; over file:// the browser refuses. */
let wakeLock=null;
async function keepAwake(on){
 try{
  if(!('wakeLock' in navigator)){if(on)console.warn('wake lock unsupported here - set the phone auto-lock to Never');return}
  if(on){if(wakeLock)return;wakeLock=await navigator.wakeLock.request('screen');wakeLock.addEventListener('release',()=>{wakeLock=null})}
  else if(wakeLock){const w=wakeLock;wakeLock=null;await w.release()}
 }catch(e){wakeLock=null;console.warn('wake lock refused: '+e.message)}
}

/* ---- production vs developer mode ----
   Production is the default and all the kids see: Start, Pause, Reset and
   physical cards. The on-screen card grid and Next Step are developer tools -
   left visible, a kid taps through the whole story and never touches a card.
   Ctrl+Shift+D toggles; the choice is remembered. */
let devMode=false;
try{devMode=localStorage.getItem('chukuDevMode')==='1'}catch{}
function applyMode(){
 document.body.classList.toggle('devmode',devMode);
 $('cards').hidden=!devMode;
 $('next').hidden=!devMode;
 $('cardHelp').textContent=devMode?'Listen, think, then tap a card.':'Listen, think, then scan your card.';
 const pill=$('modePill');
 if(pill){pill.textContent=devMode?'Developer mode - Ctrl+Shift+D to leave':'Card mode - scan a card to play';
  pill.className=devMode?'modepill devactive':'modepill'}
}
function setDevMode(on){devMode=!!on;try{localStorage.setItem('chukuDevMode',devMode?'1':'0')}catch{};applyMode()}
document.addEventListener('keydown',e=>{
 if((e.ctrlKey||e.metaKey)&&e.shiftKey&&(e.key==='D'||e.key==='d')){e.preventDefault();setDevMode(!devMode)}
});
// A mouse-clicked button keeps focus, and the reader's Enter would fire it
// again - pressing Reset mid-story. Drop focus after any click.
document.addEventListener('click',e=>{const b=e.target.closest('button');if(b)b.blur()});

// Kids tap the card the moment they spot it, long before Chuku stops talking.
// Remember that scan and play it the instant the game is ready, so their tap
// is never silently swallowed.
let pendingCard=null;
const canAnswer=g=>g.active&&!g.paused&&['waiting','hint','wrong'].includes(g.phase);
function queueOrChoose(card){
 if(canAnswer(game)){pendingCard=null;game.run(()=>game.choose(card));return}
 if(game.active)pendingCard=card;
}

function render(g){document.body.classList.toggle('playing',g.active);$('start').disabled=g.active;$('pause').disabled=!g.active;$('pause').textContent=g.paused?'▶ Resume':'Ⅱ Pause';$('next').disabled=!g.active||g.index>=8||g.paused;
 const can=g.active&&!g.paused&&['waiting','hint','wrong'].includes(g.phase);document.querySelectorAll('.card').forEach(b=>b.disabled=!can);
 $('sceneTitle').textContent=g.phase==='idle'?'Hello, Captain!':g.phase==='complete'?'Captain TOP!':g.scene.name;
 $('caption').textContent=g.caption||'Press Start Game and meet Chuku.';$('speaker').textContent=g.speaker||'Your adventure buddy';
 $('progress').textContent=g.active?`STOP ${g.index+1} OF 9 · ${g.scene.name.toUpperCase()}`:g.phase==='complete'?'ADVENTURE COMPLETE':'YOUR ADVENTURE AWAITS';
 $('lamps').textContent=g.scene.id==='off'?'':`💡 ${g.light?'ON':'OFF'}   🌀 ${g.fan?'ON':'OFF'}`;
 $('sceneIcon').textContent=g.phase==='freeze'?'🧊':g.scene.icon;
 $('status').textContent=g.paused?'Paused — press Resume when ready.':g.phase==='error'?g.error:can?(g.scene.id==='water'?'Take your time. Tap WATER when you return.':'Your turn, Captain!') :g.phase==='dance'?`Dance round ${g.round} of 3!`:g.phase==='freeze'?'Hold your funny pose!':g.phase==='complete'?'Play again whenever you like.':g.active?'Listen to your crew…':'Ready when you are.';
 document.body.classList.toggle('paused',g.paused);document.body.classList.toggle('moving',g.active&&!g.paused&&[1,2].includes(g.index));document.body.classList.toggle('freeze',g.phase==='freeze');document.body.classList.toggle('dark',g.index===1&&!g.light);
 $('log').textContent=g.events.slice(-30).map(e=>`${e.time.toFixed(1)} ${e.type}: ${e.value}`).join('\n');
 $('status').dataset.phase=g.phase;$('status').dataset.scene=g.scene.id;
 if(g.phase==='complete'||!g.active)keepAwake(false);
 if(pendingCard&&canAnswer(g)){const c=pendingCard;pendingCard=null;setTimeout(()=>game.run(()=>game.choose(c)),0)}
}
for(const [k,icon,label]of CARDS){const b=document.createElement('button');b.className='card';b.dataset.card=k;b.innerHTML=`<span>${icon}</span><b>${label}</b>`;b.disabled=true;b.onclick=()=>game.run(()=>game.choose(k));$('cards').appendChild(b)}
const game=new ChukuGame(CHUKU_STORY,audio,render);
const startNow=()=>{pendingCard=null;keepAwake(true);game.run(()=>game.start())};
// In card mode the only way through the story is a physical card, so a reader
// that isn't talking to the phone leaves a child stuck with no explanation.
// Check it once per browser before the first story, and offer on-screen cards
// as the way out rather than a dead end.
// What the story will actually ask a child to do, so a parent can decide
// before it begins rather than mid-scene.
const ACTIVITIES=['Dance for three rounds, with freeze breaks',
 'Go and drink a real glass of water, then come back',
 'Clap, stretch and stand up to turn things on and off',
 'Tiptoe quietly past a sleeping Teddy'];
const CARD_NOTES={water:'you have two',biscuit:'your cookie card'};
const readerThen=go=>{
 if(!devMode && window.ReaderCheck && !ReaderCheck.known()){
  ReaderCheck.run({onWorking:go, onSkip:()=>{setDevMode(true);go()}});return}
 go()};
$('start').onclick=()=>{
 if(window.StoryIntro && !StoryIntro.seen('toy-town')){
  StoryIntro.show({key:'toy-town',title:'Chuku & the Toy Town Express',minutes:13,
   cards:CARDS.map(([id,icon,label])=>({icon,label,note:CARD_NOTES[id]||''})),
   activities:ACTIVITIES,
   onStart:()=>readerThen(startNow)});
  return}
 readerThen(startNow)};$('next').onclick=()=>{pendingCard=null;game.run(()=>game.next())};$('reset').onclick=()=>{teaching=null;pendingCard=null;keepAwake(false);game.reset()};$('pause').onclick=()=>game.run(()=>{if(game.paused){keepAwake(true);return game.resume()}keepAwake(false);return game.pause()});
$('adult').onclick=()=>{$('adultPanel').hidden=!$('adultPanel').hidden};
$('volume').oninput=e=>{audio.volume=Number(e.target.value);if(audio.master)audio.master.gain.setTargetAtTime(Number(e.target.value),audio.now(),.05)};


function teachUI(){const box=$('teach');box.replaceChildren();for(const[k,icon,label]of CARDS){const b=document.createElement('button');b.textContent=icon+' Teach '+label+(uidList(mapping[k]).length?' ✓ ('+uidList(mapping[k]).length+')':'');b.onclick=()=>{game.reset();teaching=k;$('teachStatus').textContent='Scan your '+label+' card now.';$('uid').focus()};box.appendChild(b)}}
window.scanCard=uid=>{uid=String(uid).trim();if(!uid)return;if(teaching){const q=normUid(uid);for(const k in mapping)mapping[k]=uidList(mapping[k]).filter(x=>normUid(x)!==q);const cur=uidList(mapping[teaching]);cur.push(uid);mapping[teaching]=cur;teaching=null;try{localStorage.setItem('chukuCardMap',JSON.stringify(mapping));$('teachStatus').textContent='Card saved for this browser.'}catch{$('teachStatus').textContent='Card works for this session; browser storage is unavailable.'}teachUI();return}const q=normUid(uid);const card=Object.keys(mapping).find(k=>uidList(mapping[k]).some(x=>normUid(x)===q));queueOrChoose(card||'unknown')};
// a card left on the reader fires repeatedly on some readers
window.ScanGuard && ScanGuard.wrapGlobal('scanCard');
$('uid').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();window.scanCard(e.target.value);e.target.value=''}};
document.addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey)return;if(e.target&&e.target.matches&&e.target.matches('input,textarea,select'))return;if(!game.active&&!teaching)return;if(Date.now()-lastKey>1000)wedge='';lastKey=Date.now();if(e.key==='Enter'){e.preventDefault();window.scanCard(wedge);wedge=''}else if(e.key.length===1)wedge+=e.key});

/* Interruption handling (the Carry on screens) is parked - see BACKLOG.
   docs/interrupt-guard.js and docs/progress.js are still in the repo,
   unwired, to be rebuilt as one piece. */


teachUI();applyMode();
setInterval(()=>{if(!audio.analyser)return;const d=new Float32Array(audio.analyser.fftSize);audio.analyser.getFloatTimeDomainData(d);$('status').dataset.rms=Math.sqrt(d.reduce((a,v)=>a+v*v,0)/d.length).toFixed(6);$('status').dataset.audio=audio.ctx.state},300);
