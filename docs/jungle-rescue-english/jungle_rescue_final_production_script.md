# Jungle Rescue Patrol — Audio Production Script

**Character:** Coco  
**Audience:** 4-year-olds  
**Language:** Hindi/Hinglish  
**Target:** approximately 5–6 min with quick card responses; longer when hints or the child-paced
water break are needed
**Eight card choices:** FUEL → ROPE → BISCUIT → FIRST AID → WATER → FLASHLIGHT → BLANKET → MUSIC.

**Owner:** ElevenLabs operator / audio producer. Record dialogue, character performance, SFX and music
from this file. Scheduling, scan handling, hint timers and interruptions belong exclusively to
[jungle_rescue_playback_spec.md](jungle_rescue_playback_spec.md). This is an asset script, not a
single continuous narration: hint and alternate-response recordings are separate assets.


## GLOBAL VOICE AND RECORDING CONTRACT

This guide applies to every cue, including hints, short reactions, sneezes, laughter and humming.
A local emotion changes performance, never the character's identity.

| Voice key | Fixed character identity | Baseline delivery |
|---|---|---|
| COCO | Saanu, ElevenLabs voice ID `d9BvEI0bp2Tmdpqnjwn0`; use `voice_auditions/reference_shipped_intro.mp3` as the approved tone reference | Warm, curious, playful; clear Hindi/Hinglish; match the shipped Coco's energy and comic timing. Encouragement never sounds like a test examiner. |
| NARRATOR | Jia, ElevenLabs voice ID `ItmwhOeluca31IEX91Yk` | Warm, brisk and clear; distinct from Coco; let actions and sound jokes breathe without long dramatic pauses. |
| ELEPHANT | Vardan, ElevenLabs voice ID `bBG9wwa23659EgIkMbc1` | Child-like, affectionate and playful; retain Vardan's natural pitch. Use the approved light EQ option in `audio/elephant-rescue-test/audition-childlike-v2/manifest.json`; no pitch shifting or doubled voice layers. |
| PARROT | Munni, ElevenLabs voice ID `VOGEEZj2Kly5dP9LrQy8` | Small, bright, lightly squeaky; distress is brief and gentle, then gradually relieved and cheerful. Words remain intelligible. |
| LION | Bholu, ElevenLabs voice ID `5krdMTA5HonvWAlY2vSx` | Small child-like lion throughout: shy, vulnerable and warm. Keep Bholu's natural pitch and timing; use only gentle EQ and level control. Sneezes and snores can be comically big without turning into an adult roaring lion. |

**How to enforce consistency in ElevenLabs:** The audio operator must bind each voice key to one
approved ElevenLabs voice ID and one approved reference sample before the full recording pass.
Use that same voice ID and chosen TTS model/base settings for every cue belonging to that character.
Record the actual IDs and settings in the delivery manifest. Do not let a per-cue emotion prompt
select a new speaker. Character-specific nonverbal vocals use the same voice/reference; generic
SFX generation alone does not guarantee matching voices. Listen against the reference before
approving each batch, especially Lion, Coco's humming, and both characters' laughter.

Directions in square brackets are production notes, not guaranteed ElevenLabs control syntax.
Send only the quoted dialogue to speech generation; convey emotion controls separately for the selected model, or direct the
performer. Never narrate cue IDs, headings, labels, hints'
names, brackets, or music-generation prompts. Do not feed this whole file as one TTS request.

**Defaults:** Every speech cue names its speaker. Where no local emotion is supplied, use the
speaker's baseline. Hint delivery is kind and clear. Keep the approved Hindi/Hinglish wording,
including Captain, Pull, biscuit and लोरी. Pronounce “लोरी” with a clear long “लो”, never “लौरी”. Match repeated card names
across clips. Do not add praise, extra jokes, or improvised endings. Use the same signature
delivery for Coco's three “ये कौन करता है?!” lines.

## ASSET DELIVERY CONTRACT

- Each bold `JR_NNN` label is an immutable cue ID; explicitly named suffix effects such as
  `JR_103_jeep` are separate assets. Export cues separately as WAV files (with the split
  JR_103 and JR_129 components described below); use a
  consistent lossless PCM format and sample rate agreed with the player implementer. Do not
  join prompts, hints, correct responses or alternate responses into one long recording.
- Cue IDs identify assets, not an unconditional playlist. The companion playback file chooses
  the appropriate route. New cues receive new IDs; never renumber approved existing cues.
- Supply clean voice tracks, SFX and music separately, without baked-in hint waits or card
  response silence. Keep intentional comic pauses inside a line. Trim accidental leading
  silence, especially on freeze calls and acknowledgements.
- Repeated correct chimes may alias the same approved recording in the manifest; likewise
  repeated rope creaks and wrong-card boings. Every referenced cue ID must still resolve.
- Supply a delivery manifest containing cue ID, file path, type, voice key where applicable,
  actual duration, loop points where applicable, approved voice ID/model/settings, and review
  status. Do not invent duration or voice IDs before production. Playback loads this manifest.
- Loopable beds: JR_001 daytime jungle, JR_021 moving jeep/jungle, the JR_103 evening weather
  bed, and the muffled cave ambience component of JR_129. Deliver JR_103 as
  `JR_103_jeep.wav` (short run and stop), `JR_103_entry.wav` (audible wind-and-rain arrival) and
  `JR_103_bed.wav` (loopable weather under dialogue). Deliver JR_129 as `JR_129_entry.wav` (short
  entry footsteps) and `JR_129_bed.wav` (loopable sheltered ambience). Its manifest entry must
  name both components and their durations/loop points. JR_150 is a short departing/fading
  scene transition, not an endless bed.
- JR_144 lori music and JR_145 Coco humming align to the same ten-second interval. JR_160 is
  a twenty-second dance loop. JR_163 and JR_166 freeze calls must each fit within three seconds.
  Deliver exact edited lengths; a generation prompt alone cannot enforce these durations.
- Keep dialogue intelligible; the stomach growl and gulps should be identifiable without
  startling the child. No SFX may resemble a wrong answer when Coco, rather than the child,
  makes a mistake. Mix relationships below are guidance; the player controls live ducking.
- Final listen-through: confirm every spoken word, voice identity, clipped endings, music seams,
  freeze starts, and sound-joke clarity. Preserve breathing and natural laughter.

---

## INTRODUCTION — JOIN THE JUNGLE RESCUE TEAM

**JR_001 · SFX** `jungle_day_ambience` — loop softly, duck under speech

**JR_002 · COCO** `[bright, close, playful]`
> हैलो, मैं हूँ कोको। आज हम जंगल बचाओ टीम बनेंगे।

**JR_003 · COCO** `[hopeful, inviting]`
> जंगल में हमारे कई दोस्त मुसीबत में हैं और हमें उन्हें बचाना है। क्या तुम Captain बनकर मेरी मदद करोगे?

**JR_004 · COCO** `[delighted, encouraging]`
> Yes! Great! अब Captain और कोको मिलकर सारे animals को बचा लेंगे।

**JR_005 · COCO** `[warm, story-telling]`
> जल्दी चलो, हमारी जंगल रेस्क्यू जीप तैयार है।

**JR_006 · SFX** `jeep_door` — quick door/open movement

**JR_007 · NARRATOR** `[warm, brisk]`
> कोको जीप में बैठा, स्टीयरिंग पकड़ी, चाबी घुमाई।

**JR_008 · SFX** `key_turn`, immediately followed by `engine_cough` — two short comic coughs

**JR_009 · COCO** `[surprised, amused]`
> ओह, ये स्टार्ट क्यों नहीं हो रही है? हम्म, जीप की टंकी खाली है।

**JR_010 · COCO** `[curious, clear]`
> Captain, टंकी खाली है! इसमें क्या डालें कि जीप चल पड़े?


---

# INTERACTION 01 — FUEL


### HINT 1

**JR_011 · COCO** `[clear, warm]`
> अपने सामने वाले cards को देखो... इनमें Jeep को चलाने वाली कोई चीज़ है क्या?

### HINT 2

**JR_012 · COCO** `[clear, warm]`
> जिससे गाड़ी की tank भरती है, वही card ढूँढो.

### RESCUE HINT

**JR_013 · COCO** `[clear, warm]`
> FUEL वाला card scan करो.

### CORRECT — FUEL

**JR_014 · SFX** `ting_ting`

**JR_015 · COCO**
> YES! FUEL! टंकी भर गई!

**JR_016 · SFX** Fuel pouring — short, clear fill sound after the acknowledgement

**JR_017 · SFX** Engine starts

**JR_018 · COCO**
> जंगल रेस्क्यू टीम चलो!

### FUEL — OPTIONAL REPEAT RESPONSE ASSETS

**JR_019 · SFX** One soft liquid-overflow bloop; funny, small, not an alarm.

**JR_020 · COCO** `[comic surprise, affectionate]`
> ओहो! बस करो, Captain! Fuel तो overflow हो जाएगा!

---

# SCENE 02 — ELEPHANT RESCUE

**JR_021 · SFX** Jeep driving + jungle ambience

**JR_022 · NARRATOR** `[bouncy, curious]`
> जीप जंगल के अंदर गई। बड़े-बड़े पेड़, छोटी-छोटी नदियाँ, उछलती-कूदती जीप!

**JR_023 · SFX** Jeep bump 1 — soft suspension thump

**JR_024 · SFX** Jeep bump 2 — bigger, with a brief rattle

**JR_025 · SFX** Jeep bump 3 — quick playful double-bump; keep the beat moving

**JR_026 · COCO** `[surprised, comic, louder than the bumps]`
> वो! ये रोड है या ट्रैम्पोलीन?

**JR_027 · SFX** Elephant call — clear friendly trumpet, not frightening

**JR_028 · COCO** `[concerned, reassuring]`
> अरे! एलिफेंट दादा एक बड़े मड्डी गड्ढे में फँसे हैं। चिंता मत करो, कोको सुपर रेस्क्यू आ गया!

**JR_029 · NARRATOR** `[brisk, physical]`
> कोको ने एलिफेंट दादा को खींचा।

**JR_030 · COCO** `[effortful, rhythmic]`
> एक, दो, तीन!

**JR_031 · SFX** Mud splat — wet comic landing

**JR_032 · SFX** One short comic boink immediately after the splat. Distinct from the wrong-card sound;
this is Coco's funny accident, not feedback on the child's answer.

**JR_033 · NARRATOR** `[comic surprise]`
> और कोको खुद मड में गिर गया!

**JR_034 · COCO** `[same recurring funny signature voice; immediate after the mistake]`
> ये कौन करता है?!

**JR_035 · COCO** `[small embarrassed laugh, quickly recovering]`
> ओके, नया प्लान चाहिए.

---

# INTERACTION 02 — ROPE

### ASK

**JR_036 · COCO** `[clear, warm]`
> Captain, हमें कोई लंबी चीज़ चाहिए जिससे एलिफेंट दादा को अपनी तरफ खींच सकें। क्या हमारे पास ऐसी कोई चीज़ है?

### HINT 1 ASSET

**JR_037 · COCO** `[clear, warm]`
> अपने cards को देखो... कोई लंबी चीज़ दिख रही है जिससे हम खींच सकें?

### HINT 2 ASSET

**JR_038 · COCO** `[clear, warm]`
> इसे पकड़कर किसी चीज़ को अपनी तरफ खींचा जा सकता है.

### RESCUE HINT ASSET

**JR_039 · COCO** `[clear, warm]`
> ROPE वाला card scan करो.

### CORRECT — ROPE

**JR_040 · SFX** `ting_ting`

**JR_041 · COCO**
> YES! ROPE! रस्सी मिल गई। अब एलिफेंट दादा को बाहर निकालने में कोको की मदद करो।

### PHYSICAL ACTION

**JR_042 · COCO** `[playful, encouraging]`
> Captain, बैठे-बैठे रस्सी खींचने का नाटक करो। Pull!

**JR_043 · SFX** Rope creak — one short effort sound.

**JR_044 · COCO** `[clear, warm]`
> फिर से। Pull!

**JR_045 · SFX** Rope creak — one short effort sound.

**JR_046 · COCO** `[comically breathless, funny voice; bounce on Pull / गुल]`
> एक आखिरी बार। Pull, pull… अरे, pull-pull करते-करते दिमाग़ की बत्ती गुल हो गई!

**JR_047 · SFX** Big pull + mud release

**JR_048 · COCO**
> यस, एलिफेंट दादा बाहर आ गए.

**JR_049 · COCO** `[proud, impressed]`
> वाह Captain! तुमने कितना ज़ोर लगाया!

**JR_050 · ELEPHANT** `[relieved, grateful]`
> Thank you, Captain!

---

## ELEPHANT GETS HUNGRY

**JR_051 · SFX** Elephant stomach growl — clearly a belly sound: a large, rounded low-mid rumble with a
short bubbly gurgle at the end; no roar, engine tone, or scary bass. Leave a small clean gap before
Coco speaks so the child can identify the sound.

**JR_052 · COCO**
> ये क्या था?

**JR_053 · ELEPHANT**
> मेरे पेट में भूख से चूहे दौड़ रहे हैं।

**JR_054 · COCO** `[playful; speak the exact scripted words and finish "रहे हैं" clearly; no ad-lib after the line]`
> सिर्फ़ दौड़ नहीं रहे हैं... कूद भी रहे हैं!

**PLAYBACK:** Hold an 800 ms reaction beat after JR_054 before presenting the BISCUIT prompt.

---

# INTERACTION 03 — BISCUIT FEEDING GAME

**AUDIO SET:** One first-bite acknowledgement, one reusable crunch, four separate Elephant lines,
and one laughter cue. Feeding order and additional-tap handling are in the playback specification.

### ASK

**JR_055 · COCO** `[warm, inviting]`
> एलिफेंट दादा को भूख लगी है! Captain, क्या हमारे पास कुछ खाने के लिए है?

### HINT 1 ASSET

**JR_056 · COCO** `[clear, warm]`
> अपने cards में खाने वाली चीज़ ढूँढो।

### HINT 2 ASSET

**JR_057 · COCO** `[clear, warm]`
> कुछ खाने वाला card?

### RESCUE HINT ASSET

**JR_058 · COCO** `[clear, warm]`
> BISCUIT वाला card tap करो।

### BISCUIT — ACKNOWLEDGEMENT AND EATING ASSETS

**JR_059 · SFX** `ting_ting` — use the shared correct chime recording.

**JR_060 · COCO** `[bright]`
> YES! BISCUIT!

**JR_061 · SFX** One big, happy biscuit crunch; reusable recording with a clean start and end.

### BITE 1

**JR_062 · ELEPHANT** `[playfully incredulous; emphasise एक, rising question; no scolding]`
> बस एक?

### BITE 2

**JR_063 · ELEPHANT** `[hopeful, cheeky]`
> बस दो? थोड़ा और दो, कोको!

### BITE 3

**JR_064 · ELEPHANT** `[playfully pleading]`
> कोको, मेरा पेट देखो... बहुत भूख लगी है! और खिलाओ।

### BITE 4

**JR_065 · ELEPHANT** `[playfully overwhelmed; quick ओके, ओके, then surprised balloon image]`
> ओके, ओके, बस करो! और खाऊँगा तो balloon बन जाऊँगा!

**JR_066 · SFX** Elephant gives a short, warm belly laugh; Coco joins with a giggle. About two seconds
total, natural character laughter, no canned laugh track. Match the established character voices.

### BISCUIT — ADDITIONAL-BITE HINT ASSETS

**JR_067 · COCO** `[gentle, clear]`
> Captain, वही BISCUIT वाला card फिर से tap करो।

**JR_068 · COCO** `[helpful, unhurried]`
> BISCUIT वाला card हटाओ, फिर दोबारा tap करो।

**JR_069 · COCO** `[clear, kind]`
> BISCUIT वाला card फिर से tap करो।

### BISCUIT — WRONG-CARD RESPONSE ASSET

**JR_070 · SFX** Shared soft wrong-card boing; distinct from Coco's accident boink.

**JR_071 · COCO** `[gentle, helpful]`
> दादा को biscuit चाहिए। BISCUIT try करो।

## STORY TRANSITION — CONTINUE TO THE NEXT RESCUE

**JR_072 · SFX** Short jeep transition; one cheerful bump as the jeep moves on

**JR_073 · COCO** `[bright transition]`
> एलिफेंट दादा safe! Jungle Rescue Team, next mission!

---

# SCENE 03 — PARROT RESCUE
**JR_074 · SFX** Branch rustle, then a small distressed parrot cry

**JR_075 · PARROT** `[squeaky, crying, in pain but not frightening]`
> आह! ओह! मेरा wing hurt हो गया!

**JR_076 · SFX** Uneven wing flap; one wing flutters, the other gives a tiny squeak

**JR_077 · COCO** `[concerned, gentle]`
> अरे पैरट जी! आपका एक wing flap कर रहा है, दूसरा आराम कर रहा है।

**JR_078 · COCO** `[warm, reassuring]`
> चिंता मत करो, पैरट जी! Captain और मैं आपकी मदद करेंगे।

---

# INTERACTION 04 — FIRST AID

### ASK

**JR_079 · COCO**
> चोट लगने पर हमें ऐसी चीज़ चाहिए जिसमें bandage और medicine जैसी चीज़ें होती हैं। Captain, क्या हमारे पास कुछ ऐसा है?

### HINT 1 ASSET

**JR_080 · COCO** `[clear, warm]`
> अपने cards को देखो... चोट लगने पर काम आने वाली चीज़ ढूँढो.

### HINT 2 ASSET

**JR_081 · COCO** `[clear, warm]`
> इसमें bandage जैसी चीज़ें रखी होती हैं.

### RESCUE HINT ASSET

**JR_082 · COCO** `[clear, warm]`
> FIRST AID वाला card scan करो.

### CORRECT — FIRST AID

**JR_083 · SFX** `ting_ting`

**JR_084 · COCO**
> YES! FIRST AID! पट्टी और medicine मिल गई।

**JR_085 · SFX** Bandage / treatment

**JR_086 · COCO**
> पैरट का wing अब safe है। पट्टी लग गई!

**JR_087 · SFX** Small bandage wrap, then one bright healing sparkle

**JR_088 · PARROT** `[hopeful]`
> Thank you, Captain! अब मैं wing हिला कर देखूँ?

**JR_089 · COCO** `[encouraging]`
> हाँ! धीरे-धीरे—एक, दो, flap!

**JR_090 · SFX** Two uneven flaps, then one successful strong flap

**JR_091 · PARROT** `[delighted]`
> फड़फड़! अब मेरा wing चल रहा है!

**JR_092 · SFX** Tiny happy parrot chirp

**JR_093 · PARROT** `[tired, thirsty]`
> लेकिन मेरी चोंच सूख गई है। मुझे पानी चाहिए।

---

# INTERACTION 05 — WATER BREAK

**JR_094 · COCO**
> इतने rescue missions के बाद Captain को भी थोड़ी प्यास लगी होगी। पहले तुम जाकर थोड़ा असली पानी पियो। पानी पीकर वापस आना और WATER वाला card tap करना।

### WATER — RETURN REMINDER ASSET

**JR_095 · COCO** `[clear, warm]`
> Captain, Coco यहीं wait कर रहा है। पानी पीकर आओ और WATER वाला card tap कर देना।

### CORRECT — WATER

**JR_096 · SFX** `ting_ting`

**JR_097 · COCO**
> Welcome back, Captain! अब पैरट को भी थोड़ा water देते हैं।

**JR_098 · SFX** Glass pour, then three clearly separated, louder parrot gulps: **glug... glug... GULP!**
Raise the gulp SFX about 2–3 dB over the quiet water bed, while keeping it below speech. The
three swallows should be identifiable as drinking, not splashing.

**JR_099 · PARROT** `[surprised, happy]`
> ओहो! पानी मिलते ही मेरी चोंच खुश हो गई!

**JR_100 · SFX** Wings strengthen: flap-flap-flap, then a joyful takeoff whoosh

**JR_101 · PARROT** `[joyful, flying away]`
> मैं उड़ सकता हूँ! Bye-bye, Captain!

**JR_102 · COCO** `[delighted transition]`
> देखो, पैरट फुर्र से उड़ गया! Jungle Rescue Team, चलो आगे!

---

# SCENE 04 — LION

**JR_103 · SFX** A clearly identifiable rescue jeep engine runs on a dirt track, tires crunch on
gravel, then the jeep brakes and the engine stops. Then an audible, child-safe gust
of night wind moves through the trees as light rain begins. Continue a quieter evening jungle
bed with crickets, wind and rain under the dialogue. Deliver separate `JR_103_jeep`,
`JR_103_entry` and loopable `JR_103_bed` assets; do not extend the engine under the scene.

**JR_104 · NARRATOR** `[hushed, adventurous; pronounce अंधेरे clearly as अन-धे-रे]`
> रेस्क्यू जीप घने जंगलों के बीच आकर रुकी। सूरज ढल चुका था और पेड़-पौधे अंधेरे में अजीब साए जैसे लग रहे थे।

**JR_105 · SFX** Rustling leaves behind a big rock

**JR_106 · LION** `[small child-like lion voice; two heavy but harmless sneezes, not frightening]`
> आ... छी! आ... छी!

**JR_106_lion · SFX** `[selected entrance roar A]` Immediately before Coco says “अरे! यह तो Lion King
की आवाज़ है!” A short, shy, rounded young-lion roar gives the child the clue first; keep it
friendly and below a startling level.

**JR_107 · COCO** `[whispering, nervous but playful]`
> Captain... उस बड़ी rock के पीछे कोई छुपा है!

**JR_108 · LION** `[small, embarrassed voice]`
> ह-हेलो? कोई है वहाँ?

**JR_109 · COCO** `[surprised]`
> अरे! यह तो Lion King की आवाज़ है! आप rock के पीछे क्या कर रहे हैं?

**JR_110 · LION** `[worried, gentle; pronounce अंधेरा clearly as अन-धे-रा]`
> कोको... मैं यहाँ रास्ता भूल गया हूँ। और यहाँ इतना अंधेरा है कि मुझे अपनी पूँछ भी दिखाई नहीं दे रही!

**JR_111 · COCO** `[confident, then uncertain]`
> फ़िक्र मत करो! मैं ढूँढता हूँ आपकी पूँछ।

**JR_112 · SFX — reuse `JR_106_lion`** `[short grumpy little-lion roar]` Immediately after Coco says he will find
the tail. The roar is a comic protest from Lion King; use no spoken “अरे” in this moment.

**JR_113 · COCO** `[nervous, trying to sound brave]`
> मेरा मतलब... मैं कुछ करता हूँ... ओह!

**JR_114 · SFX** Coco trips over a tree root + soft comedy thud

**JR_115 · COCO** `[rubbing head, urgent but playful; pronounce अंधेरा clearly as अन-धे-रा]`
> अरे! इतना अंधेरा है कि मेरी नाक भी नहीं दिख रही! Captain, हमें तुरंत रोशनी चाहिए, वरना हम सब टकरा जाएँगे!

---

# INTERACTION 06 — FLASHLIGHT


### HINT 1 ASSET

**JR_116 · COCO** `[clear, warm; pronounce अंधेरे clearly as अन-धे-रे]`
> अपने cards में देखो... कोई ऐसी चीज़ है जो अंधेरे में तेज़ रोशनी दे सके?

### HINT 2 ASSET

**JR_117 · COCO** `[clear, warm; pronounce अंधेरे clearly as अन-धे-रे]`
> इसे ON करते ही अंधेरे में रास्ता साफ़ दिखने लगता है।

### RESCUE HINT ASSET

**JR_118 · COCO** `[clear, warm]`
> FLASHLIGHT वाला card scan करो!

### CORRECT — FLASHLIGHT

**JR_119 · SFX** `ting_ting`, quietly underneath the beginning of JR_121. Never delay Coco's
acknowledgement for this sound.

**JR_120 · SFX** Heavy flashlight click + bright beam hum, start at the correct card tap under
Coco's immediate acknowledgement. Do not wait for him to finish “YES! FLASHLIGHT!”. The
windy bed eases slightly as the beam reveals the way; the cave entrance later changes location.

**JR_121 · COCO**
> YES! FLASHLIGHT!

**JR_122 · SFX** Gentle short beam-sweep whoosh. The owl reveal is carried by Coco's next line;
no visual display is required.

**JR_123 · COCO** `[surprised, relieved]`
> वाह! रोशनी होते ही सब दिखने लगा! ...और rock के ऊपर वो उल्लू भी!

**JR_124 · SFX** Owl hoot — soft, comic

**JR_125 · NARRATOR** `[warm]`
> टॉर्च की रोशनी में Lion King rock के पीछे से बाहर आए। पर वो थोड़े काँप रहे थे।

**JR_126 · SFX** One brief cool breeze and soft leaf flutter outdoors. No teeth-chatter effect; Lion's own voice carries the cold.

**JR_127 · LION** `[shivering]`
> रोशनी के लिए शुक्रिया... पर रात की हवा बहुत ठंडी है। Brrr!

**JR_128 · NARRATOR** `[warm, reassuring; the cave is shelter, but Lion still feels cold]`
> रोशनी में Lion King को अपनी गुफा दिख गई। कोको उन्हें अंदर ले गया, लेकिन Lion King को अब भी बहुत ठंड लग रही थी।

**JR_129 · SFX** A few gentle footsteps enter a dry cave; rain and wind become muffled outside.
Keep the space cozy, not echoing or frightening.

**JR_130 · COCO** `[helpful, confident]`
> रुकिए Lion King, मैं आपको इस बड़े सूखे पत्ते से ढकता हूँ!

**JR_131 · SFX** Dry leaf crinkles, then rips in half

**JR_132 · COCO** `[comic self-mockery immediately after the leaf rips; then caring]`
> अरेरे... पत्ता तो फट गया! पत्ते से ठंड रोकने चला था... ये कौन करता है?!

**JR_132_sting · SFX** `[tiny playful two-note comic pluck]` Immediately after Coco finishes
“ये कौन करता है?!” Keep it light and short; never sound like a wrong-answer buzzer.

---

# INTERACTION 07 — BLANKET

*JR_133 is retired. Play no Lion vocal after Coco's leaf joke; continue to JR_134.*

**JR_134 · COCO** `[clear, inviting]`
> Captain, हमें Lion King के लिए कोई soft और गर्म चीज़ चाहिए जिसे उन्हें ओढ़ा सकें!


### HINT 1 ASSET

**JR_135 · COCO** `[clear, warm]`
> अपने cards में देखो... कोई soft चीज़ ढूँढो जो ठंड से बचाए।

### HINT 2 ASSET

**JR_136 · COCO** `[clear, warm]`
> रात को सोते समय हम इसे अपने ऊपर ओढ़कर warm महसूस करते हैं।

### RESCUE HINT ASSET

**JR_137 · COCO** `[clear, warm]`
> BLANKET वाला card scan करो!

### CORRECT — BLANKET

**JR_138 · SFX** `ting_ting`, quietly underneath the beginning of JR_140. Never delay Coco's
acknowledgement for this sound.

**JR_140 · COCO**
> YES! BLANKET! यह blanket कितना soft और warm है!

**JR_139 · SFX** Soft fabric rustle + warm cozy sigh, after Coco's acknowledgement.

**JR_141 · NARRATOR** `[tender]`
> कोको ने बड़े प्यार से वो blanket Lion King को ओढ़ा दिया।

**JR_142 · LION** `[small child-like lion voice; cozy, relieved]`
> अहाहा... अब आया ना मज़ा! इतनी गर्मी... इतना आराम...

**JR_143 · COCO** `[tender and empathetic, softer and slower than ordinary dialogue; invite the child warmly]`
> Captain, Lion King को आराम से सुलाने के लिए एक छोटी सी लोरी गाएँ? तुम मेरे साथ गाओगे?

**JR_144 · MUSIC** Ten-second original instrumental लोरी with gentle music-box tones. No lyrics or familiar
tune. Leave room for Coco and the child; end on a warm sustained note.

**JR_145 · COCO — HUMMING PERFORMANCE** `[tender, empathetic, lullaby-like; noticeably softer than Coco's dialogue; ten seconds]`
Record a simple original “ला-ला-ला” melody in Coco's established voice, with little breathing gaps
so the child can join. Deliver as a separate vocal stem aligned to the lori music. Do not speak
these directions. The humming is required; the child may sing, hum or listen.

*JR_146 is retired. The लोरी now leads directly into the Lion settling and snoring.*

**JR_147 · SFX** Lion settles in, then snores three times with a natural comic rhythm: the
first clear, the second a little bigger, the third softer as he falls deeper asleep. Each snore
must be identifiable on laptop speakers. Leave a short beat before Coco speaks.

**JR_149 · COCO** `[giggling, quiet whisper]`
> लो! हमारी लोरी सुनते-सुनते Lion King तो खर्राटे लेने लगे! Mission successful!

---

# SCENE 05 — CELEBRATION

**JR_150 · SFX** Lion's last soft snore fades behind the team; gentle footsteps towards the jeep.
Rain eases and wind fades. Keep all speech clear.

**JR_151 · NARRATOR** `[warm, relieved]`
> बारिश थम गई। Lion King को सोने देकर टीम जीप के पास लौट आई।

**JR_152 · COCO** `[proud, delighted]`
> Captain, हमने दोस्तों की मदद कर दी! अब हमारी पार्टी!

**JR_153 · SFX** Coco's two playful foot taps: tap-tap. No dance music yet.

**JR_154 · COCO** `[eager, playful]`
> मेरे पैर तो नाचने लगे! पर धुन कहाँ है? Captain, नाचने के लिए क्या बजाएँ?

---

# INTERACTION 08 — MUSIC


### HINT 1 ASSET

**JR_155 · COCO** `[gently encouraging]`
> पार्टी में नाचने के लिए धुन चाहिए।

### HINT 2 ASSET

**JR_156 · COCO** `[playful, helpful]`
> गाना बजाने वाला card ढूँढो।

### RESCUE HINT ASSET

**JR_157 · COCO** `[clear, kind]`
> MUSIC वाला card tap करो।

### CORRECT — MUSIC

**JR_158 · SFX** `ting_ting`

**JR_159 · COCO** `[excited]`
> YES! MUSIC!

**AUDIO NOTE:** MUSIC acknowledgement is a separate voice clip. The dance beat and movement calls
are delivered separately for the player to assemble.
---

# DANCE PARTY

**DELIVERY:** Separate movement calls, freeze calls, animal effects, giggle and dance music.
Each freeze voice clip must fit within three seconds and have no leading silence. Runtime
round lengths, overlaps and stop/restart scheduling are in the playback specification.

### ELEVENLABS MUSIC PROMPT — DANCE LOOP

**JR_160 · MUSIC** One reusable 20-second instrumental loop; target 120 BPM, 4/4. Keep Coco dialogue,
animal effects and freeze commands as separate cues.

**GENERATION PROMPT — MUSIC ONLY; DO NOT NARRATE:**

> Create an exuberant jungle rescue victory dance for preschool children. Target 120 BPM in
> 4/4, bright major key, with an immediate strong first beat and full dancing energy from the
> first second. Use a bouncy, clearly audible kick, crisp friendly handclaps, playful dhol-style
> hand drums, rounded bass with audible midrange, and a short catchy marimba melody that repeats
> so children can anticipate it. Make the groove irresistible for side-to-side swaying, flapping
> arms and clapping. Add small playful percussion fills while keeping the pulse steady. Joyful,
> cheeky, triumphant and physically lively. Instrumental only, no vocals, chants, spoken words,
> animal calls or environmental sounds. Keep the arrangement uncluttered enough for a separate
> child character's Hindi/Hinglish instructions to be clearly heard over it. No slow intro,
> gradual build, internal pauses, breakdown, tempo change or fade-out; no harsh cymbals, piercing
> bells, frightening hits or heavy sub-bass. Make a 20-second loop that joins smoothly back to
> its strong opening beat, without a closing cadence. The game will insert the freeze breaks.

**MIX / EDIT:** Energy comes from the groove, not extra volume. Duck music just enough to hear
Coco and retain the beat throughout movement calls. Briefly duck the melody for animal effects;
avoid stacking effects over speech. Verify the generated tempo, duration and loop seam before
use; the prompt alone does not guarantee exact timing. Reuse the same musical hook in the resolving sting and final goodbye sting when possible.

**COCO DELIVERY FOR ELEVENLABS:** Keep Coco's familiar kid-like voice. Smile audibly, lead with
rhythm, and give “Elephant dance”, “Parrot dance” and “Freeze” clear playful emphasis without
shouting. Make the freeze calls short and mischievous, not stern. The puff is
Coco's own silly sound, followed by a natural little giggle. After dancing, soften into sincere
thanks, then brighten for the muddy-hand joke. Directions are not spoken text.

### ROUND 1 — 20 SEC

**JR_161 · COCO** `[bouncy, inviting]`
> Elephant dance! हाथ की सूँड़ बनाओ — इधर, उधर! बैठे-बैठे भी!

**JR_162 · SFX** one friendly elephant trumpet over the beat.

**JR_163 · COCO** `[playful, clear]`
> Freeze! मूर्ति बन जाओ!

### ROUND 2 — 20 SEC

**JR_164 · COCO** `[bright, rhythmic]`
> Parrot dance! हाथों के पंख — फड़फड़, फड़फड़!

**JR_165 · SFX** a short happy parrot chirp and flutter over the beat.

**JR_166 · COCO** `[funny, clear]`
> Freeze! गाल फुलाओ!

### ROUND 3 — 20 SEC

**JR_167 · COCO** `[puffed cheeks, funny release]`
> पुफ्फ! अब Captain वाला dance! हाथ हिलाओ या ताली बजाओ!

**JR_168 · COCO** `[puffs his cheeks again; laughing at himself]`
> अरे! मेरे गाल फिर से गुब्बारे बन गए! पुफ्फ!

**JR_169 · SFX** Short natural Coco giggle, matching Coco's established voice.

**JR_170 · MUSIC** Short resolving sting using the dance melody, with a clean ending and a gentle tail.

---

# FINAL HERO CEREMONY

**JR_171 · COCO** `[warm, proud; gently catching his breath]`
> Captain, तुम्हारी मदद से हमारे दोस्त फिर खुश हैं। Thank you, Captain!

**JR_172 · COCO** `[inviting, joyful]`
> हाथ ऊपर! साथ बोलो — हम हैं जंगल बचाओ टीम!

**JR_173 · COCO** `[playful]`
> मेरी तरफ हवा में high-five!

**JR_174 · SFX** One friendly high-five clap.

**JR_175 · COCO** `[comic surprise]`
> अरे! मेरे हाथ पर अभी भी कीचड़ है!

**JR_176 · SFX** One short sticky mud squelch as Coco opens his hand.

**JR_177 · COCO** `[laughing, affectionate]`
> ये कौन करता है?! पहले हाथ धोऊँगा! Bye-bye, Captain!

**JR_178 · SFX** Short warm ending sting, then one friendly jeep horn.

**AUDIO NOTE:** Reuse the established mud sound and Coco's comic delivery. These ending jokes
remain approved but have not been child-tested; verify their performance in the recorded listen-through.
---

# GLOBAL WRONG-CARD RESPONSES

Record all three variants separately. Selection belongs to the playback specification.

### WRONG 1

**JR_179 · SFX** Funny soft boing

**JR_180 · COCO** `[playfully surprised, encouraging]`
> ओहो! ये वाला काम नहीं करेगा। Captain, एक और card try करो!

---

### WRONG 2

**JR_181 · SFX** Boing

**JR_182 · COCO** `[light, encouraging]`
> ऊप्स! हमें कोई और चीज़ चाहिए। Captain, फिर से सोचो!

---

### WRONG 3

**JR_183 · SFX** Boing

**JR_184 · COCO** `[curious, supportive]`
> हम्म... ये नहीं। Captain, दूसरा card try करो!

---

## Final card sequence

**FUEL → ROPE → BISCUIT → FIRST AID → WATER → FLASHLIGHT → BLANKET → MUSIC**
