class ChukuAudio {
 constructor(dialogue){this.dialogue=dialogue;this.volume=.8;this.ctx=null;this.buffers=new Map();this.sources=new Set();this.beds={};this.speechCount=0}
 now(){return this.ctx?.currentTime||0}
 // A phone call can leave the context suspended, 'interrupted' (iOS) or closed.
 // A closed one can never be revived: build a fresh one and drop the decoded
 // buffers with it, since they belong to the old context.
 running(){return this.ctx&&this.ctx.state==='running'}
 async resume(){
  if(this.ctx&&this.ctx.state==='closed'){this.ctx=null;this.buffers.clear();this.sources.clear();this.beds={}}
  if(!this.ctx){this.ctx=new (window.AudioContext||window.webkitAudioContext)();this.master=this.ctx.createGain();this.master.gain.value=this.volume;this.analyser=this.ctx.createAnalyser();this.master.connect(this.analyser);this.analyser.connect(this.ctx.destination)}await this.ctx.resume()}
 suspend(){return this.ctx?.suspend()}
 check(s){if(s.aborted)throw new DOMException('Cancelled','AbortError')}
 async buffer(key){if(!this.buffers.has(key)){this.buffers.set(key,(async()=>{let bytes;if(typeof CHUKU_MEDIA!=='undefined'){if(!CHUKU_MEDIA[key])throw Error('Missing audio: '+key);bytes=Uint8Array.from(atob(CHUKU_MEDIA[key]),c=>c.charCodeAt(0)).buffer}else{const r=await fetch('audio/'+key+'.mp3');if(!r.ok)throw Error('Could not load '+key);bytes=await r.arrayBuffer()}return this.ctx.decodeAudioData(bytes)})().catch(e=>{this.buffers.delete(key);throw e}))}return this.buffers.get(key)}
 duck(){for(const [k,n]of Object.entries(this.beds)){const base=k==='music'?.5:k==='fan'?.14:.07;const v=k==='music'&&this.speechCount?base*.15:base;n.g.gain.setTargetAtTime(v,this.now(),.08)}}
 async node(key,s,loop=false){this.check(s);let b;try{b=await this.buffer(key)}catch(e){this.check(s);throw e}this.check(s);const n=this.ctx.createBufferSource(),g=this.ctx.createGain();n.buffer=b;n.loop=loop;n.connect(g);g.connect(this.master);g.gain.value=this.dialogue[key]?1:key==='polite_burp'?1:.55;const rec={n,g,key};this.sources.add(rec);return rec}
 async play(key,s){const rec=await this.node(key,s);this.check(s);const speech=!!this.dialogue[key];if(speech){this.speechCount++;this.duck()}return new Promise((resolve,reject)=>{let settled=false;const finish=error=>{if(settled)return;settled=true;s.removeEventListener('abort',cancel);this.sources.delete(rec);rec.n.disconnect();rec.g.disconnect();if(speech){this.speechCount--;this.duck()}error?reject(error):resolve()};const cancel=()=>{try{rec.n.stop()}catch{}finish(new DOMException('Cancelled','AbortError'))};s.addEventListener('abort',cancel,{once:true});rec.n.onended=()=>finish();rec.cancel=cancel;rec.n.start()})}
 async loop(slot,key,s){this.stopSlot(slot);if(!key)return;const rec=await this.node(key,s,true);this.check(s);const cancel=()=>{try{rec.n.stop()}catch{}this.sources.delete(rec);rec.n.disconnect();rec.g.disconnect();s.removeEventListener('abort',cancel);if(this.beds[slot]===rec)delete this.beds[slot]};rec.cancel=cancel;s.addEventListener('abort',cancel,{once:true});this.beds[slot]=rec;this.duck();rec.n.start()}
 bed(key,s){return this.loop('bed',key,s)}
 fan(on,s){return this.loop('fan',on?'bg_fan_low':null,s)}
 music(key,s){return this.loop('music',key,s)}
 stopSlot(slot){this.beds[slot]?.cancel()}
 stopMusic(){this.stopSlot('music')}
 stopAll(){for(const rec of [...this.sources]){if(rec.cancel)rec.cancel();else{try{rec.n.stop()}catch{}rec.n.disconnect();rec.g.disconnect();this.sources.delete(rec)}}this.beds={}}
 wait(seconds,s){this.check(s);const end=this.now()+seconds;return new Promise((resolve,reject)=>{const cleanup=()=>{clearInterval(t);s.removeEventListener('abort',cancel)};const cancel=()=>{cleanup();reject(new DOMException('Cancelled','AbortError'))};const t=setInterval(()=>{if(this.now()>=end){cleanup();resolve()}},30);s.addEventListener('abort',cancel,{once:true});if(seconds<=0){cleanup();resolve()}})}
}
