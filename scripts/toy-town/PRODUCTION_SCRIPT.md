# Chuku: Toy Town Express
## Production script v2 — Hinglish interactive audio adventure

Status: implemented audio production build. Delivered with 168 local MP3 assets, explicit per-line emotion sheet, and playable game.
Audience assumption: ages 3–6, with an adult available. Six physical cards: KEY, LIGHT, FAN, WATER, MUSIC, BISCUIT. Touch controls use the same logic.
Duration target: approximately 8–12 minutes, depending on choices and water break; never impose a completion deadline.

## 1. Characters and performance

- N — Narrator: warm, playful guide; clear Hinglish, unhurried questions. Never ridicule the child.
- C — Chuku: expressive little train; confident about silly things, delighted when the Captain helps. Pronounce “Chuk-koo.”
- D — Driver Uncle: gentle, absent-minded comic character. His mistakes cause the jokes, not danger.
- T — Teddy: sleepy and affectionate; three short appearances/lines.

“Yeh kaun karta hai?!” is Chuku’s amused, affectionate aside on a SEPARATE audio line. Use three times: pocket sandwich, dancing moustache, Teddy’s excuse. Do not use it for a child’s card choice. Leave about 0.8 seconds after each punchline. No laugh track.
Only text inside quotation marks is spoken. Brackets are production directions, never TTS input. Record every labeled line as a separate clean speech asset using its ID; retain speaker and exact script in the manifest. Hindi is written in Devanagari for pronunciation consistency; keep familiar English words natural. Audition “Chuku,” “Captain,” “Toy Town,” and code-switching before batch production.

## 2. Audio and interaction rules

### What we learned from Jungle Rescue and will retain

1. All transitions need actual recordings. Previously missing journey/setup clips caused an abrupt jump into Coco falling in mud. Validate every referenced speech/SFX/music asset before release; text-only placeholders do not count as complete audio.
2. Start Game must unlock/resume browser audio within the click. Repeated Start clicks cannot start parallel stories.
3. Correct card: short familiar bright TING, then action SFX, then consequence/dialogue. Wrong card: soft comic BOING, kind response, same question stays active. Never a harsh buzzer.
4. The old regular hints were scheduled at 8, 17, and 28 seconds after the prompt. This script improves that to completion-based delays below, so a long hint never collides with another.
5. Keep the approved water delay sequence: 30 seconds, then 60, then 120, capped at 120 seconds between reminders. Count each delay after the preceding reminder finishes. No timeout or auto-advance.
6. Keep 60 seconds of dance music in three 20-second rounds, plus freeze breaks. Give children real time to enjoy the music.
7. Correct scans cancel hints immediately. Speech never overlaps speech; feedback never competes with the next scene.
8. Next Step stops current speech, SFX, music, hints, and waits before entering the next step. Reset also clears scene state. Cancel stale asynchronous callbacks so they cannot restart old audio.
9. Keep local playback possible, with every asset packaged or embedded. No runtime ElevenLabs request or API key. Preserve the original MP3s separately for future editing.
10. RFID UID+Enter and on-screen cards share one handler; Teach Cards mappings persist per browser/site. Re-teach on a new deployed origin if needed.

### Standard hint schedule — revised for this story

Unlock cards after the final question finishes; optionally play ready_soft. Then wait 10 seconds → H1. After H1 finishes, wait 15 seconds → H2. After H2 finishes, wait 20 seconds → H3. If still waiting, repeat H3 every 45 seconds after its previous playback ends. No hint during narration, action feedback, freeze breaks, or scene changes. Stop hint timers while the game is paused.

A correct card during a hint cuts off that hint and succeeds immediately. During wrong feedback, accept a correct card immediately; ignore other repeated wrong scans until the response ends. After wrong feedback, resume at the next hint level with a fresh full delay; do not reset to H1 or immediately fire overdue hints. After three distinct wrong attempts, offer H3 at the next available speech gap. Do not queue scans during locked setup/success/dance narration. Never silently retain an early scan for the next scene.

Use a per-card repeat guard (~1 second) and require reader removal/new presentation where supported. A held card must not retrigger dialogue. Unknown UID: use unknown_card; do not label the physical card “wrong.”

### Mix direction

Speech stays clearly in front. Ambient loops should initially sit about 18–24 dB below speech; music under speech about 12–18 dB below. These are starting mix relationships, not calibrated device-volume limits. Duck smoothly during speech and audition on phone and tablet speakers. Keep horn, bonk, click, and high-five soft; no sudden loud brake screeches. Use short fades to avoid clicks. Freeze music should stop perceptibly at “FREEZE,” using a tiny fade. Do not bake ambience into voice files.

## 3. Full performance script

### S01 — All aboard: find the key

[BG: bg_station_day. No music under the first greeting. Cards locked.]
S01_01 N: “अरे वाह! हमारे Captain आ गए! Welcome to Toy Town Station!”
S01_02 C: “मैं हूँ Chuku—तुम्हारी Toy Town Express! छोटी-सी train, बड़ी-बड़ी मस्ती!”
S01_03 C: “Captain, मेरा शानदार horn सुनो!”
[SFX: horn_meow. Pause 0.7 seconds.]
S01_04 N: “Chuku! तुम train हो या बिल्ली?”
S01_05 C: “Oops! Wrong button!”
[SFX: horn_train_soft.]
S01_06 N: “आज हम Teddy से मिलने Toy Town जा रहे हैं।”
S01_07 T: “मैं वहाँ welcome करूँगा! और इस बार बिल्कुल नहीं सोऊँगा!”
[Short playful transition sting; Teddy's line is a brief story cutaway, not a live call.]
S01_08 D: “सब ready! बस… मेरी चाबी कहाँ है?”
[SFX: pocket_rustle, followed by rubber_duck once.]
S01_09 N: “Driver Uncle ने जेब चेक की। एक मोज़ा… एक rubber duck… और आधा sandwich!”
S01_10 C [playful, mock-surprised, teasing]: “जेब में आधा sandwich?! ये कौन करता है?!”
[Pause 0.8 seconds.]
S01_12 D: “बाकी आधा दूसरी जेब में है!”
[Pause 0.8 seconds.]
S01_13 N: “लेकिन engine अभी भी locked है। Captain, तुम्हारे पास कुछ है जो इसे खोल सके?”
[UNLOCK; expect KEY.]
S01_H1 N: “हम्म… engine का ताला खोलना है।”
S01_H2 N: “ताला खोलने के लिए किस चीज़ को घुमाते हैं?”
S01_H3 N: “चाबी वाला KEY card tap करके देखो।”
[Correct: correct_ting → key_turn → engine_wake → train_sneeze.]
S01_OK1 N: “Engine start हुआ… या Chuku को छींक आई?”
S01_OK2 C: “Engine भी start हो गया! और ये छोटी-सी छींक तो bonus थी!”
S01_OK3 D: “Thank you, Captain! अब चलें?”
S01_OK4 C: “Toy Town, हम आ रहे हैं! छुक-छुक… चलो!”
[Crossfade station into bg_train_roll over 2 seconds.]

### S02 — Inside the dim coach: light on

S02_01 N: “दरवाज़े बंद, सब अपनी जगह! Chuku धीरे-धीरे station से निकला। चलो, अंदर वाले coach को देखें।”
S02_02 C: “अरे! इस coach की lights तो अभी जली ही नहीं!”
[SFX: soft_bonk + little toy squeak, not a painful impact.]
S02_03 D: “Oops! मेरा lunchbox सीट से टकरा गया। अँधेरे में कुछ दिख नहीं रहा!”
S02_04 N: “Captain, ऐसा क्या करें कि सब साफ़-साफ़ दिखने लगे?”
[UNLOCK; expect LIGHT.]
S02_H1 N: “अँधेरे में हमें उजाला चाहिए।”
S02_H2 N: “दीवार वाला कौन-सा switch उजाला करता है?”
S02_H3 N: “LIGHT वाला card tap करो।”
[Correct: correct_ting → switch_click → light_sparkle. Set lightOn=true.]
S02_OK1 N: “आहा! अब सब दिख रहा है! लेकिन… Driver Uncle! आपके सिर पर lunchbox क्यों है?”
S02_OK2 D: “अच्छा! तभी मेरी टोपी से आलू पराठे की खुशबू आ रही थी!”
[Pause 0.8 seconds.]
S02_OK3 C: “वाह, Captain! तुमने तो lunchbox वाली टोपी भी पकड़ ली!”
S02_OK4 N: “Driver Uncle ने lunchbox सीट पर रखा, और असली टोपी पहन ली। Chuku आगे बढ़ा।”

### S03 — A very warm coach: fan on

[Continue train background. No heat sound needed.]
S03_01 C: “उफ़्फ़! इस coach में तो गर्मी है!”
S03_02 D: “मैं अपनी टोपी से हवा कर लेता हूँ।”
[SFX: two soft cloth flaps.]
S03_03 D: “हवा थोड़ी-सी… हाथ की exercise ज़्यादा!”
S03_04 N: “Captain, ऐसी हवा कैसे आए जो हम सब तक पहुँचे?”
[UNLOCK; expect FAN.]
S03_H1 N: “हमें ठंडी-ठंडी हवा चाहिए।”
S03_H2 N: “ऊपर कौन-सी चीज़ घूमकर हवा देती है?”
S03_H3 N: “FAN वाला card tap करो।”
[Correct: correct_ting → switch_click → fan_start; fade in bg_fan_low. Set fanOn=true.]
S03_OK1 D: “आहाहा… अब मज़ा आया!”
S03_OK2 N: “देखो! हवा में Driver Uncle की मूँछ हिल रही है!”
S03_OK3 D: “मूँछ जी! Dance बाद में। पहले अपना ticket दिखाइए!”
S03_OK4 C: “अपनी मूँछ से ticket माँग रहे हैं! ये कौन करता है?!”
[Pause 0.8 seconds.]
S03_OK5 N: “Captain ने हवा चला दी। अब सब आराम से बैठ सकते हैं!”

### S04 — Music choice and a full dance party

S04_01 N: “थोड़ी देर बाद Chuku पहुँचा Masti Stop पर। यहाँ एक छोटा-सा dance break!”
[SFX: brake_soft → station_bell. Fade train roll out. Train is parked for dancing; fan remains low.]
S04_02 C: “मेरे पहिए तो रुक गए… लेकिन मेरी मस्ती नहीं!”
S04_03 D: “मैं गाना गाऊँ? ला… ला… लाआआ!”
[Driver singing is speech performance, about 2 seconds, deliberately silly but gentle.]
S04_04 C: “अरे! मेरा horn भी तुमसे सुर सीख रहा है!”
S04_05 N: “Captain, हमारी dance party कैसे शुरू होगी?”
[UNLOCK; expect MUSIC.]
S04_H1 N: “Dance करने का मन है। बस धुन की कमी है!”
S04_H2 N: “तुम्हारे cards में party वाली चीज़ कौन-सी है?”
S04_H3 N: “MUSIC वाला card tap करो।”
[Correct: correct_ting → party_sting. Lock cards for dance.]
S04_OK1 N: “Party time! अपने आसपास थोड़ी जगह देख लो। खड़े होकर या बैठे-बैठे, मेरे साथ dance करो!”

[ROUND 1: music_dance_loop plays for exactly 20 seconds. Speech overlays with music ducking; its duration is INCLUDED in the 20 seconds.]
DANCE_01 C: “अपने हाथों को train के पहियों जैसे घुमाओ! छुक-छुक, छुक-छुक!”
[At music time 10 seconds.]
DANCE_02 N: “अब shoulders हिलाओ! छोटी train… बड़ी मस्ती!”
[At 20 seconds stop music as freeze word begins.]
DANCE_F1 N: “FREEZE! अपनी funny statue बनाओ!”
[After line ends, hold silence 3 seconds; fan very low.]
DANCE_J1 C: “Driver Uncle! आपकी मूँछ अभी भी dance कर रही है!”
DANCE_GO1 N: “और… फिर से dance!”

[ROUND 2: 20 seconds of music.]
DANCE_03 N: “अब jelly जैसा wobble-wobble! अपने हाथों से भी कर सकते हो!”
[At 10 seconds.]
DANCE_04 C: “ऊपर हाथ… नीचे हाथ… और funny robot!”
[At 20 seconds stop music.]
DANCE_F2 N: “FREEZE! Robot की battery रुक गई!”
[After line ends, hold 3 seconds.]
DANCE_J2 D: “मेरी battery तो sandwich से चलती है!”
DANCE_GO2 C: “Last round, Captain! अपना favourite dance!”

[ROUND 3: 20 seconds of music.]
DANCE_05 N: “अब तुम्हारी बारी! हमें अपना dance सिखाओ!”
[At 10 seconds.]
DANCE_06 C: “वाह! ये तो Captain वाला special dance है!”
[At 20 seconds stop music.]
DANCE_F3 N: “और… आख़िरी FREEZE!”
[After line ends, hold 3 seconds.]
S04_END1 C: “मेरे पहिए भी ताली बजाना चाहते हैं!”
[SFX: short_applause.]
S04_END2 N: “क्या मस्त dance था! Chuku अभी Masti Stop पर ही है। थोड़ा आराम कर लें।”
[Stay parked at Masti Stop; soft station/fan background. Total MUSIC = 60 seconds; dialogue/freeze gaps add time. No scans or inactivity hints during dance.]

### S05 — Water break after dancing

S05_01 N: “इतना dance किया! अब छोटा-सा water break। Captain, आराम से थोड़ा पानी पी लो। हम यहीं wait करेंगे।”
S05_02 C: “मैं तुम्हारी जगह संभालता हूँ! Driver Uncle, Captain की सीट पर sandwich मत रखना!”
S05_03 N: “जब पानी पीकर वापस आ जाओ, तो WATER वाला card tap कर देना। तभी हमें पता चलेगा कि तुम ready हो।”
[UNLOCK; expect WATER. Keep soft station/fan bed; no dripping loop and no ticking/countdown.]
S05_R1 N: “अगर पानी पी लिया हो, तो आराम से वापस आओ और WATER वाला card tap कर देना।”
S05_R2 C: “Captain, हम यहीं हैं! पानी पी लिया हो तो WATER वाला card tap कर देना।”
[30 seconds → R1; 60 seconds after R1 → R2; then alternate every 120 seconds after playback. No regular hints.]
[Correct: correct_ting.]
S05_OK1 N: “Welcome back, Captain! Driver Uncle भी अपना पानी पी लें।”
[SFX: sip_glug, then tiny polite_burp.]
S05_OK2 D: “Oops! Excuse me!”
S05_OK3 C: “अरे! ये मेरा horn नहीं था!”
[Pause 0.8 seconds.]
S05_OK4 N: “सब अपनी जगह वापस! Chuku फिर चल पड़ा। Toy Town अब पास है।”
[Resume bg_train_roll and fade station background out; keep fan low.]
[Do not infer actual drinking from a card scan; no required quantity or gulping challenge.]

### S06 — Teddy's biscuit dream

[SFX: brake_soft. Stop train loop; start bg_trackside_soft; fan continues quietly.]
S06_01 C: “अरे, आगे कौन है? आराम से रुकते हैं!”
[SFX: teddy_snore once.]
S06_02 N: “Teddy! तुम तो welcome करने वाले थे! यहाँ पटरी के बीच कैसे सो गए?”
S06_03 T: “खर्र्र… biscuit… खर्र्र…”
S06_04 C: “ये signal की आवाज़ है?”
S06_05 N: “Signal biscuit के सपने थोड़ी देखता है!”
[Pause 0.8 seconds.]
S06_06 N: “Captain, Teddy की नाक कुछ yummy ढूँढ रही है। हमारे पास उसके लिए क्या है?”
[UNLOCK; expect BISCUIT. Repeat short snore no more than every 12 seconds; never over speech or hints.]
S06_H1 N: “Teddy को कोई खाने वाली चीज़ चाहिए।”
S06_H2 N: “कुछ छोटा और crunchy… जिसे वह चबा सके।”
S06_H3 N: “BISCUIT वाला card tap करो।”
[Correct: stop snore timer → correct_ting → teddy_sniff.]
S06_OK1 T: “हूँ? Biscuit? मैं जाग गया!”
S06_OK2 N: “Teddy उठकर platform की bench पर बैठ गया। अब उसे biscuit देते हैं।”
[SFX: teddy_steps → biscuit_crunch.]
S06_OK3 T: “मैं सो नहीं रहा था! बस पटरी की softness check कर रहा था!”
S06_OK4 C: “पटरी पर softness check?! ये कौन करता है?!”
[Pause 0.8 seconds.]
S06_OK5 N: “तो result क्या आया?”
S06_OK6 T: “Bed better है!”
S06_OK7 N: “Teddy ने हाथ हिलाया। रास्ता clear! Chuku धीरे-धीरे station में दाखिल हुआ।”
[Brief train_roll bridge → arrival_chime → bg_station_day. No unresolved jump from sleeping to rolling out of the way.]

### S07 — Arrived: remember BOTH switches

S07_01 C: “Toy Town! हमारी मस्ती वाली journey पूरी!”
S07_02 N: “Chuku park हो गया। Driver Uncle ने engine बंद किया।”
[SFX: engine_off. Engine off does not automatically switch off coach light/fan in this story.]
S07_04 N: “लेकिन Captain… बाहर जाने से पहले कुछ OFF करना बाकी है।”
[UNLOCK immediately after this line; accept LIGHT or FAN in either order. Start with lightOn=true, fanOn=true. Leave fan background softly audible. No extra spoken clue: wait a full 10 seconds for independent recall.]

[State-aware hints: at every hint trigger inspect which switches remain ON. If BOTH remain on, use the BOTH set below. If only FAN remains on, use S07_FAN_H1/H2/H3. If only LIGHT remains on, use S07_LIGHT_H1/H2/H3. If neither remains on, cancel hints and finish.]
S07_H1 N: “हमने journey में क्या-क्या ON किया था?”
S07_H2 C: “मेरे coach में अभी भी हवा चल रही है… और उजाला भी है!”
S07_H3 N: “LIGHT और FAN वाले cards, एक-एक करके tap करो।”
[H1 only after 10 seconds of waiting; H2 15 seconds after H1 ends; H3 20 seconds after H2 ends. After a successful first switch, play its feedback and restart a full 10-second wait before the remaining switch's H1. Never reuse a BOTH hint when only one switch remains on.]

[If FAN is first: correct_ting → switch_click → fan_stop; fanOn=false.]
S07_F_FIRST C: “Fan OFF! मेरी हवा वाली party ख़त्म। Captain, अभी एक चीज़ बाकी है!”
[Restart hint schedule for remaining light only.]
S07_LIGHT_H1 N: “अब coach में उजाला कौन कर रहा है?”
S07_LIGHT_H2 N: “हवा बंद है। अब light को बंद करना है।”
S07_LIGHT_H3 N: “LIGHT वाला card tap करो।”

[If LIGHT is first: correct_ting → switch_click; lightOn=false. No total black screen; keep station/window glow.]
S07_L_FIRST C: “Lights OFF! बाहर station का उजाला है। लेकिन अंदर अभी एक चीज़ चल रही है!”
[Restart hint schedule for remaining fan only.]
S07_FAN_H1 N: “सुनो… whoosh-whoosh! हवा कहाँ से आ रही है?”
S07_FAN_H2 N: “Light बंद है। अब fan को बंद करना है।”
S07_FAN_H3 N: “FAN वाला card tap करो।”

[Second required card: correct_ting → matching switch SFX; no FIRST dialogue. Update flag, cancel hints, then play S07_BOTH.]
S07_BOTH N: “दोनों OFF! Captain, तुम्हें दोनों चीज़ें याद रहीं। तुमने बिजली भी बचाई!”

[Repeated already-off FAN: neutral_tick, no state change, no success advance.]
S07_REPEAT_F C: “Fan तो already सो गया—श्श्श! अब light की बारी है।”
[Repeated already-off LIGHT: neutral_tick, no state change.]
S07_REPEAT_L C: “Light तो already OFF है! अब fan की बारी है।”
[These responses are not wrong-card failures. Never switch an item back ON during this ending.]

### S08 — Finale and horn callback

[Fade fan/train completely out. Start music_finale low.]
S08_01 N: “Captain! तुमने Chuku को चलाया, coach में उजाला और हवा की, dance किया, water break लिया, और Teddy को जगाया!”
S08_02 D: “और मेरी lunchbox वाली टोपी भी पकड़ ली!”
S08_03 C: “सबसे ज़रूरी—तुमने याद रखा कि आखिर में दोनों switches OFF करने हैं!”
S08_04 N: “अपने लिए तालियाँ!”
[SFX: short_applause. Leave 3 seconds for real clapping.]
S08_05 C: “Captain, ready for a high-five?”
[Pause 2 seconds.]
S08_06 C: “एक… दो… तीन!”
[SFX: highfive_soft.]
S08_07 C: “Lights OFF… fan OFF… Captain TOP!”
S08_08 N: “Goodbye, Chuku!”
[SFX: horn_meow, softer than opening.]
S08_09 N: “Chukuuu!”
S08_10 C: “क्या? ये मेरा goodbye वाला horn है!”
[Pause 0.8 seconds.]
S08_11 N: “Bye, Captain! अगली adventure में मिलेंगे!”
[Music rises gently for 4 seconds then fades. Set complete. No hints, no automatic restart.]

## 4. Unexpected-card dialogue and routing

Use wrong_boing once, then ONE response. Never stack contextual and generic responses. Keep accepted state unchanged. Do not let entertaining wrong responses become longer than success payoffs.

W_KEY_BISCUIT C: “Engine biscuit नहीं खाता… Driver Uncle खा लेंगे! लेकिन engine अभी locked है।”
W_DARK_MUSIC C: “Party तो हो जाएगी… पर dancers दिखेंगे कैसे? पहले थोड़ा उजाला!”
W_HEAT_WATER N: “पानी पीना अच्छा idea है! अभी पूरे coach में हवा भी चाहिए।”
W_TEDDY_KEY C: “Teddy में keyhole नहीं है! उसकी नाक तो कुछ yummy ढूँढ रही है।”
W_OFF_MUSIC C: “एक और party? अगली बार! पहले दोनों switches को आराम दें।”
W_GENERAL_1 N: “ये चीज़ बाद में काम आ सकती है। अभी एक और card सोचकर देखो।”
W_GENERAL_2 C: “हम्म… इससे अभी काम नहीं बना। एक और idea try करें?”
W_GENERAL_3 N: “कोई बात नहीं, Captain। सवाल सुनो और फिर एक card चुनो।”
UNKNOWN_CARD N: “मुझे ये card पहचान में नहीं आया। Captain, बड़े helper से इसे check करवा लें।”
W_WATER N: “अभी water break है। पानी पीकर वापस आ गए हो तो WATER वाला card tap करो।”

Priority: unknown UID → UNKNOWN_CARD (neutral_tick); already-off ending item → its repeat line (neutral_tick); contextual pair above → that line; any other wrong known card → cycle W_GENERAL_1/2/3, except water uses W_WATER. Wrong attempts during water restart the next water-reminder interval without making it shorter. No automatic advancing because a hint or error limit was reached.

## 5. Complete non-speech asset list

Generate/record only after audio production is authorized. Reuse suitable approved Jungle Rescue assets where appropriate, after listening for consistent level and style. Names below are target filenames, not claims that these assets exist.

| ID | Sound direction | Approx. duration / use |
|---|---|---|
| bg_station_day | Gentle toy station atmosphere, distant birds, no intelligible speech/horns | 20–30s seamless loop |
| bg_train_roll | Soft rhythmic toy train clack, warm low mechanical bed, no whistle | 20–30s seamless loop |
| bg_fan_low | Gentle fan air, no harsh hiss or rattling | 15–20s seamless loop |
| bg_trackside_soft | Quiet outdoors, faint birds, no approaching real train | 20–30s seamless loop |
| ready_soft | Optional subtle wooden pop indicating cards now active | 0.2s; consistent, quieter than success |
| correct_ting | Bright friendly bell confirmation | 0.4–0.7s; every accepted card |
| wrong_boing | Gentle rubbery descending boing, playful, never alarming | 0.4–0.6s |
| neutral_tick | Soft acknowledgment for unknown/already-completed input | 0.2–0.3s |
| horn_meow | Cute short catlike toy horn; no distressed animal | 0.8–1.2s; opening/finale |
| horn_train_soft | Rounded miniature “pooon,” no blast | 0.8–1.2s |
| pocket_rustle | Cloth pocket rummage | 1.5–2s |
| rubber_duck | One soft squeak | 0.3–0.5s |
| playful_transition | Tiny whimsical xylophone flourish for Teddy cutaway | 1s |
| key_turn | Key entering lock, turning, gentle click | 0.8–1.2s |
| engine_wake | Toy engine starts with happy chug, no racing-car rev | 2s |
| train_sneeze | Comedic mechanical “a-choo,” not loud | 0.8s |
| soft_bonk | Hollow padded toy-box knock | 0.3s |
| toy_squeak | Small comic squeak after bonk | 0.3s |
| switch_click | Clear soft switch click, used for light/fan | 0.2–0.4s |
| light_sparkle | Short magical rising glimmer, distinct from correct_ting | 0.8s |
| cloth_flaps | Two hat-fanning swishes | 1.2s |
| fan_start | Fan gently accelerates; leads into loop | 1.5–2s |
| fan_stop | Fan slows to silence | 1.5–2s |
| sip_glug | Two relaxed water sips, not prolonged gulping | 1.2–1.8s |
| polite_burp | Tiny cartoon burp; spoken excuse recorded separately | 0.4s |
| brake_soft | Gentle toy train deceleration, no screech | 1.5–2s |
| station_bell | Small single station bell | 0.8s |
| party_sting | Bright percussion/xylophone party pickup | 1–1.5s |
| music_dance_loop | Original cheerful instrumental, approximately 108 BPM, playful percussion, bass, xylophone; no lyrics, horns, whistles, freeze cues or dramatic drops | 20s seamless loop, replay 3 times |
| short_applause | Warm small-group claps, no shouted speech | 2–3s |
| teddy_snore | Funny short “khrr-phew,” gentle and non-frightening | 2s; scheduled one-shot |
| teddy_sniff | Two inquisitive cartoon sniffs | 0.8–1s |
| teddy_steps | Soft plush footsteps | 1–1.5s |
| biscuit_crunch | Friendly small crunches, no exaggerated mouth sounds | 1.5–2s |
| arrival_chime | Cheerful two-note station arrival | 1–1.5s |
| engine_off | Toy engine winding down softly | 1.5s |
| music_finale | Warm instrumental ending theme related to dance melody, soft bells and gentle percussion | 45–60s bed; loopable or extendable for final VO |
| highfive_soft | Soft cartoon handclap, not a sharp slap | 0.3–0.5s |

No continuous score is needed in every problem scene: the train/fan beds provide continuity and leave room for voices. Use the written pauses instead of filling every gap with SFX.

## 6. State and control specification

Sequence: KEY → LIGHT ON → FAN ON → MUSIC choice → DANCE → WATER → BISCUIT → BOTH OFF → FINALE.

Start state: engineOn=false, lightOn=false, fanOn=false, no active expected card. KEY success sets engineOn=true. LIGHT and FAN successes set respective flags. Arrival explicitly sets engineOn=false. In BOTH OFF, accepted set equals only the switches still on. Complete when both flags false. Do not implement these as unrestricted toggles in all scenes.

Next Step targets the next item in the sequence, including separate MUSIC choice and DANCE. On jump, atomically stop all audio/timers and set the destination's canonical state: S02 has engine on; S03 adds light on; S04 onward has light/fan on; S07 has engine off and both coach switches on; S08 has all off. Enter destination setup once and restore correct background. Jumping from dance enters the water break; jumping from water enters Teddy; jumping from the off puzzle enters the finale with both off. Disable Next in finale/completion. Next is an adult preview control, not a child puzzle solution.

Reset cancels audio, decode callbacks, timers, scheduled SFX and pending waits, clears progress, and returns to Start. Keep taught mappings. Pause, if implemented, freezes timers/music position and resumes without duplicated prompts. Backgrounding/resuming must not trigger a burst of overdue hints. Suspend hint timers on hidden tab and offer explicit Resume if audio was interrupted.

## 7. Production checklist before calling the game ready

- Manifest includes every labeled speech line above and every referenced non-speech cue; speaker, filename, text, duration, and scene are recorded. No missing file silently skipped.
- Listen to every clip and check beginning/end truncation, Hindi pronunciation, speaker consistency and laugh pauses. Keep direction text out of generated speech.
- Verify Start produces audible narration on supported target browsers/devices; verify actual speaker playback as well as software audio signal.
- Play the complete sequence normally at least once. Check key-to-coach, dance-to-water, water-to-Teddy, and Teddy-to-arrival transitions.
- Test all six cards in every waiting state, plus unknown UID, duplicate scans, correct scan during hint, rapid wrong scans, and correct scan during wrong feedback.
- Check LIGHT→FAN and FAN→LIGHT off orders, and repeat taps of an already-off item. Final praise must play once only.
- Verify regular hint progression, water 30/60/120 timing, no overlapping voices, and hints cease immediately after success.
- Confirm three actual 20-second music rounds, all three freezes, and no clipped movement instruction at a boundary.
- Test Next and Reset during setup, decoding, hints, water wait, wrong feedback, dance and finale. No old scene may resume afterward.
- Check embedded offline build without network; check hosted separate-assets build for missing paths if producing that format. Retain an MP3 ZIP independent of the build.
- Deliver script, cue manifest, source MP3s, final deployment ZIP and a short verification note. Do not describe script completion as completed audio/game testing.
