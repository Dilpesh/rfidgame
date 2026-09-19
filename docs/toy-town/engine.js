/* Chuku state machine. Sound and clock adapters keep cancellation testable. */
class ChukuGame {
 constructor(story,audio,render=()=>{}){this.story=story;this.audio=audio;this.render=render;this.serial=0;this.ctrl=null;this.hintCtrl=null;this.responseCtrl=null;this.active=false;this.paused=false;this.phase='idle';this.index=0;this.light=false;this.fan=false;this.hintLevel=0;this.waterLevel=0;this.wrongCount=0;this.wrongCycle=0;this.seen=new Map();this.events=[];this.emit()}
 get scene(){return this.story.scenes[this.index]}
 emit(){this.render(this);}
 record(type,value){this.events.push({type,value,time:this.audio.now()});if(this.events.length>200)this.events.shift()}
 check(s){if(s.aborted)throw new DOMException('Cancelled','AbortError')}
 async run(fn){try{await fn()}catch(e){if(e.name==='AbortError')return;this.stop();this.phase='error';this.error=e.message;this.emit()}}
 stopExtras(){this.hintCtrl?.abort();this.responseCtrl?.abort();this.hintCtrl=null;this.responseCtrl=null}
 stop(){this.serial++;this.ctrl?.abort();this.stopExtras();this.audio.stopAll();this.active=false;this.paused=false;this.phase='idle';this.seen.clear();this.emit()}
 reset(){this.stop();this.index=0;this.light=false;this.fan=false;this.caption='';this.error='';this.emit()}
 async start(){if(this.active)return;this.stop();this.active=true;this.index=0;this.wrongCycle=0;this.events=[];const serial=this.serial;await this.audio.resume();if(!this.active||serial!==this.serial)return;await this.enter(0)}
 async next(){if(!this.active||this.index>=8)return;await this.enter(this.index+1)}
 async enter(index){this.ctrl?.abort();this.stopExtras();this.audio.stopAll();this.ctrl=new AbortController();const s=this.ctrl.signal;this.active=true;this.index=index;this.phase='setup';this.hintLevel=0;this.waterLevel=0;this.wrongCount=0;this.seen.clear();this.caption='';this.light=index>=2&&index<8;this.fan=index>=3&&index<8;this.emit();
 const bed=index===0||index>=3&&index<=5||index>=7?'bg_station_day':index===6?'bg_trackside_soft':'bg_train_roll';
 await this.audio.bed(bed,s);this.check(s);if(this.fan)await this.audio.fan(true,s);this.check(s);
 if(index===4){await this.dance(s);this.check(s);return this.enter(5)}
 if(index===8){await this.audio.music('music_finale',s);this.check(s)}
 await this.sequence(this.scene.setup,s);this.check(s);
 if(index===8){this.audio.stopAll();this.active=false;this.phase='complete';this.caption='See you on the next adventure, Captain!';this.emit();return}
 this.waitForCard();
 }
 async sequence(items,s){for(const item of items){this.check(s);if(typeof item==='string'){this.caption=this.story.dialogue[item]?.text||this.caption;this.speaker=this.story.dialogue[item]?.speaker||this.speaker;this.record('cue',item);this.emit();await this.audio.play(item,s)}else if(item.wait)await this.audio.wait(item.wait,s);else if(item.bed)await this.audio.bed(item.bed,s);else if('fan'in item){this.fan=item.fan;await this.audio.fan(item.fan,s);this.emit()}else if('light'in item){this.light=item.light;this.emit()}}this.check(s)}
 expected(){if(this.scene.id==='off')return ['light','fan'].filter(k=>this[k]);return this.scene.card?[this.scene.card]:[]}
 waitForCard(){this.phase='waiting';this.emit();this.scheduleHint()}
 hintPrefix(){if(this.scene.id!=='off')return this.scene.hint;if(this.light&&this.fan)return 'S07';return this.light?'S07_LIGHT':'S07_FAN'}
 hintDelay(){return this.scene.id==='water'?[30,60,120][Math.min(this.waterLevel,2)]:[10,15,20,45][Math.min(this.hintLevel,3)]}
 scheduleHint(){this.hintCtrl?.abort();const c=new AbortController();this.hintCtrl=c;const s=c.signal;const delay=this.hintDelay();this.record('hint-scheduled',delay);this.run(async()=>{await this.audio.wait(delay,s);this.check(s);if(this.phase!=='waiting')return;this.phase='hint';this.emit();let cue;
 if(this.scene.id==='water'){cue='S05_R'+(this.waterLevel%2+1);this.waterLevel++}else{cue=this.hintPrefix()+'_H'+Math.min(this.hintLevel+1,3);this.hintLevel++}
 await this.sequence([cue],s);this.check(s);this.phase='waiting';this.emit();this.scheduleHint()})}
 async choose(card){if(!this.active||this.paused||!['waiting','hint','wrong'].includes(this.phase))return;
 const good=this.expected().includes(card);if(this.phase==='wrong'&&!good)return;
 const now=this.audio.now();if(this.seen.has(card)&&now-this.seen.get(card)<1)return;this.seen.set(card,now);
 this.stopExtras();const c=new AbortController();this.responseCtrl=c;const s=c.signal;
 if(!good){this.phase='wrong';this.emit();let cue;let signal='wrong_boing';
 if(card==='unknown'){cue='UNKNOWN_CARD';signal='neutral_tick'}
 else if(this.scene.id==='off'&&['light','fan'].includes(card)&&!this[card]){cue=card==='fan'?'S07_REPEAT_F':'S07_REPEAT_L';signal='neutral_tick'}
 else{const pair=this.scene.id+':'+card;cue={'key:biscuit':'W_KEY_BISCUIT','light:music':'W_DARK_MUSIC','fan:water':'W_HEAT_WATER','teddy:key':'W_TEDDY_KEY','off:music':'W_OFF_MUSIC'}[pair]||(this.scene.id==='water'?'W_WATER':'W_GENERAL_'+(this.wrongCycle++%3+1));this.wrongCount++}
 await this.sequence([signal,cue],s);this.check(s);if(this.wrongCount>=3&&this.scene.id!=='water'){await this.sequence([this.hintPrefix()+'_H3'],s);this.hintLevel=3;this.wrongCount=0}
 this.check(s);this.waitForCard();return}
 this.phase='success';this.emit();this.record('correct',card);await this.sequence(['correct_ting'],s);this.check(s);
 if(this.scene.id==='off'){this[card]=false;await this.sequence(['switch_click'],s);if(card==='fan'){await this.audio.fan(false,s);await this.sequence(['fan_stop'],s)}this.emit();
 if(this.light||this.fan){await this.sequence([card==='fan'?'S07_F_FIRST':'S07_L_FIRST'],s);this.check(s);this.hintLevel=0;this.wrongCount=0;this.waitForCard();return}
 await this.sequence(['S07_BOTH'],s);this.check(s);return this.enter(8)}
 await this.sequence(this.scene.done,s);this.check(s);await this.enter(this.index+1)
 }
 async dance(s){await this.sequence(['S04_OK1'],s);for(let round=0;round<3;round++){
 this.phase='dance';this.round=round+1;this.emit();await this.audio.music('music_dance_loop',s);this.check(s);const started=this.audio.now();this.record('dance-start',round+1);
 await this.sequence(['DANCE_0'+(round*2+1)],s);await this.audio.wait(Math.max(0,10-(this.audio.now()-started)),s);
 await this.sequence(['DANCE_0'+(round*2+2)],s);await this.audio.wait(Math.max(0,20-(this.audio.now()-started)),s);
 this.audio.stopMusic();this.record('dance-stop',round+1);this.phase='freeze';this.emit();await this.sequence(['DANCE_F'+(round+1),{wait:3}],s);
 if(round<2)await this.sequence(['DANCE_J'+(round+1),'DANCE_GO'+(round+1)],s)
 }await this.sequence(['S04_END1','short_applause','S04_END2'],s)}
 async pause(){if(!this.active||this.paused)return;this.paused=true;await this.audio.suspend();this.emit()}
 async resume(){await this.audio.resume();this.paused=false;this.emit()}
}
if(typeof module!=='undefined')module.exports=ChukuGame;
