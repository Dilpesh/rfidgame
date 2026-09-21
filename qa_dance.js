// qa_dance.js - the dance has a beat under it.
//
//     node qa_dance.js            (from the repo root; needs ffprobe)
//
// Runs the real Toy Town engine against a clock with a fake audio device, so
// the dance can be TIMED rather than guessed at. What it checks:
//
//   * the dance is still three full rounds and the same length - the fix was
//     never meant to shorten it
//   * the music is playing under the dance calls, instead of ducking to
//     nothing exactly when a child is being told to move
//   * "FREEZE!" is decoded BEFORE the music is cut, so the shout and the
//     silence land together - in musical statues the silence is the cue
//   * the only beatless stretches are the freeze holds and the ending
const fs=require('fs'),cp=require('child_process'),path=require('path');
const TT=path.join(__dirname,'docs','toy-town');
const raw=fs.readFileSync(path.join(TT,'story.js'),'utf8');
const STORY=JSON.parse(raw.slice(raw.indexOf('{'),raw.lastIndexOf('}')+1));
const ChukuGame=require(path.join(TT,'engine.js'));
let fails=0; const ok=(c,m)=>{console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)fails++;};
const D={};
const dur=k=>D[k]??(D[k]=(()=>{try{return parseFloat(cp.execSync(
  `ffprobe -v error -show_entries format=duration -of csv=p=0 ${JSON.stringify(path.join(TT,'audio',k+'.mp3'))}`
).toString())||0}catch{return 0}})());

(async()=>{
 let t=0,ev=[],decoded=new Set();
 const audio={
  dialogue:STORY.dialogue, beds:{}, now:()=>t, check(){},
  async buffer(k){decoded.add(k);ev.push({t,k,type:'decode'})},
  async play(k){const d=dur(k);ev.push({t,d,k,type:'clip',music:!!this.beds.music});t+=d},
  async music(k){this.beds.music={};ev.push({t,k,type:'music-on'})},
  stopMusic(){delete this.beds.music;ev.push({t,type:'music-off'})},
  stopAll(){this.stopMusic()}, async bed(){}, async fan(){},
  wait:async s=>{t+=s}, async resume(){}, async suspend(){}, running:()=>true,
 };
 const g=new ChukuGame(STORY,audio,()=>{});
 await g.dance({aborted:false,addEventListener(){},removeEventListener(){}});

 const rounds=ev.filter(e=>e.type==='music-on').length;
 ok(rounds===3,`three rounds of music (${rounds})`);
 ok(Math.abs(t-113.5)<1.5,`the dance is still ~113s long, not shortened (${t.toFixed(1)}s)`);

 // beatless windows
 let gaps=[],last=null,on=false;
 for(const e of ev){
  if(e.type==='music-on'){if(!on&&last!==null)gaps.push([last,e.t]);on=true}
  if(e.type==='music-off'){on=false;last=e.t}
 }
 if(!on&&last!==null)gaps.push([last,t]);
 const silent=gaps.reduce((a,[x,y])=>a+(y-x),0);
 console.log('  beatless: '+gaps.map(([x,y])=>`${x.toFixed(1)}-${y.toFixed(1)}s`).join(', '));
 ok(silent<30,`under 30s of the dance has no music (${silent.toFixed(1)}s of ${t.toFixed(1)}s)`);

 // the dance CALLS - the lines telling a child to move - must have the beat
 const calls=ev.filter(e=>e.type==='clip'&&/^DANCE_(0|J|GO)/.test(e.k));
 const withBeat=calls.filter(e=>e.music).length;
 ok(withBeat===calls.length,`every dance call has the beat under it (${withBeat}/${calls.length})`);

 // and the freeze calls must NOT - the silence is the game
 const freezes=ev.filter(e=>e.type==='clip'&&/^DANCE_F/.test(e.k));
 ok(freezes.length===3&&freezes.every(e=>!e.music),'the freeze calls play into silence');

 // decode before the cut, so the shout is not late
 let late=[];
 for(const f of freezes){
  const dec=ev.find(e=>e.type==='decode'&&e.k===f.k);
  const cut=ev.filter(e=>e.type==='music-off'&&e.t<=f.t).pop();
  if(!dec||!cut||dec.t>cut.t) late.push(f.k);
 }
 ok(late.length===0,'each FREEZE is decoded before the music is cut'+(late.length?': '+late.join(', '):''));

 console.log(fails?`\n${fails} FAILURES`:'\nALL PASS');
 process.exit(fails?1:0);
})();
