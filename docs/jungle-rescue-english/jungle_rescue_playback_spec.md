# Jungle Rescue — Playback and Interaction Specification

**Owner:** Player developer / ChatGPT implementing the game.
**Companion:** [Audio Production Script](jungle_rescue_final_production_script.md).
**Status:** Implementation handoff, not executable player code. No index.html, RFID firmware,
audio assets or ElevenLabs account configuration is changed by these documents.

The audio script owns wording, speakers, performance and sound design. This file owns state,
cue selection, silence, interruption, timers, card acceptance and completion. Use cue IDs from
the audio script instead of searching dialogue text. Read both files when implementing.

## 1. Runtime and asset contract

Load the audio producer's manifest. Each JR_NNN reference must resolve to approved audio
(or to an explicit shared-file alias). Use real measured durations, never word-count estimates.
The manifest records each character's fixed voice ID/model/settings for audit; the player
plays the approved recordings and must not regenerate or choose voices dynamically.

Missing assets block starting a production session with an operator-visible error. Do not skip
required dialogue or insert a made-up replacement. Preload the next scene, all active hints and
corrections, and the complete dance before their use. Failed playback pauses progression and
shows an operator recovery action; it never silently declares an interaction successful.

Maintain: current state, scene epoch/token, expected card, accepted flag, biscuit bite count,
hint index, active-wait clock, current audio handle, pending response if any, and fuel gag flags.
Only one foreground speech stream plays at a time. Background beds/music are separate streams.

Every async audio callback and timer carries its state/epoch token. Leaving a state invalidates
its old callbacks and cancels its timers. Stop/restart clears pending scans, counters and queues.
Do not let an old hint or onended handler advance a new scene.

## 2. Card input: a physical presentation, not repeated reader polling

Map known RFID UIDs to these eight semantic cards through the game's card registry:
FUEL, ROPE, BISCUIT, FIRST_AID, WATER, FLASHLIGHT, BLANKET, MUSIC.
FIRST_AID is the implementation key; the spoken/card label remains FIRST AID.
Biscuit is the sole food choice in this story. No Mango, Snack or Ladder step is added.

A fresh tap means a card was absent, then presented. A held card yields exactly one event,
even when the reader sends its UID repeatedly or the next state starts. Removal followed by
presentation enables another event; moving to a new state does not reset physical presence.
Discard repeated reports of the same uninterrupted presentation. Do not substitute a one-second
timer for actual removal: a held card would otherwise feed Elephant repeatedly.

The reader adapter must supply presence/removal, or a documented and hardware-verified
equivalent based on its polling behavior. If it cannot distinguish re-presentation, fix that
adapter before enabling the four-bite game. The UI simulator should emit the same logical
presentation/removal events. Do not invent hardware capabilities.

Unknown UIDs are ignored without speech, count changes or hint resets. Recognized wrong cards
receive corrections only in active question states. During narrative, success playback, action,
lori, dance and ending states, scans have no effect except the two narrowly defined pending-tap
windows below. Never save an early scan for an unrelated future question.

## 3. Shared question, hint and interruption rules

1. Arm the expected card immediately before the prompt clip starts. If a fresh correct card
   arrives during that prompt, accept it once and let the prompt finish; then play success.
   Do not start hints. This avoids cutting a question mid-word while preserving a quick answer.
   Ignore wrong cards during the prompt so they cannot interrupt the setup.
2. If unanswered, start the active-wait clock at the prompt's end. Hint offsets are cumulative:
   8, 17 and 28 seconds from that point, not three successive wait durations.
3. Correct cards during silence, a hint or wrong-card feedback win immediately. Stop hint/
   correction speech and its effect with a short click-free audio cut, cancel all hint timers,
   lock acceptance and begin the success sequence once. Never finish an obsolete correction.
4. Otherwise hints finish naturally. Hint speech counts toward the active-wait clock; hints
   never overlap each other. If a due hint finds foreground speech busy, start it at the next
   safe speech boundary; never stack multiple overdue hints back-to-back.
5. Wrong-card feedback can play only in quiet waiting time. Pick one global variant without
   immediately repeating the last variant. Allow at most one correction before hint 1, one
   between hints 1/2, one between hints 2/3, and one after hint 3. Ignore additional wrong taps
   in that interval. Correct taps remain active throughout.
6. Pause the active-wait clock during wrong-card feedback; resume its remaining time afterwards.
   Do not reset it to zero. Wrong taps while a hint/correction is playing do not queue audio.
   If a hint is already due, the hint takes priority over a new wrong-card correction.
7. After the rescue hint, wait quietly for a correct card. Do not auto-answer, skip the card,
   endlessly repeat rescue instructions or treat silence as failure.
8. Once success starts, no scan restarts it or advances an extra step. The next question arms
   only when its own prompt begins. Only that question's fresh presentations can answer it.
9. Explicit pause stops audio and freezes timers and musical position. Resume from that position;
   no catch-up burst of timers. Ignore scans during pause; retain reader-presence tracking.
   Do not infer speech, movement or drinking from elapsed time or a card alone.

Exceptions: WATER uses its own reminders, BISCUIT uses the request windows below, and the
departure-only FUEL joke is an optional branch. These override shared rules only where specified.

## 4. Main route and cue map

Ranges below mean the listed cue IDs in ascending order, skipping nothing inside that range.
Start loopable beds without waiting for them to end; all other cues finish before the next cue
unless an overlap, fixed action pause or pending-response boundary is explicitly specified.
Hints, alternatives and reusable assets are never played just because they appear in file order.

| State | Narrative leading into prompt | Prompt / expected card | Hints 1, 2, rescue | Success and onward route |
|---|---|---|---|---|
| INTRO / FUEL | JR_001–JR_009 | JR_010 / FUEL | JR_011, JR_012, JR_013 | JR_014–JR_018; optional fuel branch; Elephant approach |
| ELEPHANT / ROPE | JR_021–JR_035 | JR_036 / ROPE | JR_037, JR_038, JR_039 | JR_040–JR_054, including pretend pulls; hold 800 ms after JR_054; Biscuit question |
| BISCUIT | None; hunger already established | JR_055 / BISCUIT | JR_056, JR_057, JR_058 for first bite only | Four-bite branch in section 6; JR_072–JR_078; First Aid question |
| FIRST_AID | Parrot introduction is included above | JR_079 / FIRST_AID | JR_080, JR_081, JR_082 | JR_083–JR_093; Water question |
| WATER | None | JR_094 / WATER | JR_095 reminders only | JR_096–JR_114; Flashlight question |
| FLASHLIGHT | Lion introduction is included above | JR_115 / FLASHLIGHT | JR_116, JR_117, JR_118 | Immediate JR_120 switch click and JR_121 acknowledgement, with JR_119 chime under them; then JR_122–JR_132; Blanket question. JR_133 is retired. |
| BLANKET | Leaf attempt is included above | JR_134 / BLANKET | JR_135, JR_136, JR_137 | Immediate JR_140 with JR_138 under it, then JR_139, JR_141–JR_143; लोरी, JR_147–JR_149; JR_150–JR_153; Music question. JR_146 is retired. |
| MUSIC | Celebration invitation is included above | JR_154 / MUSIC | JR_155, JR_156, JR_157 | JR_158, JR_159; timed dance; final ceremony |

The fuel, flashlight and blanket prompts are their existing story lines: no second ASK clip
is added. The route has eight card choices and eleven successful physical presentations:
one each for seven other cards and four BISCUIT presentations.

Intro: allow 1.5 seconds after JR_003 before JR_004. No speech recognition is required.
Elephant approach: allow 1.2 seconds after JR_026 (trampoline joke) before JR_027,
and 0.8 seconds after JR_029 (Coco pulls) before JR_030 (एक, दो, तीन).
These are runtime waits after the clip ends, not silence added to the source cue.
For FIRST AID only, a correct card during JR_082 is accepted immediately but JR_082 finishes
before JR_083 begins, so the spoken card name is never cut off by the chime. After JR_084,
allow a 0.25-second quiet beat before JR_085's bandage sound. The approved JR_084 recording
has a complete final word and a short clean tail. Both boundaries keep the
acknowledgement intelligible; neither adds a new card or hint.
Pulls: play JR_043 after JR_042 and JR_045 after JR_044; each pull gets a two-second action
interval from the preceding call's end, containing its short creak. Then continue. JR_046
contains the approved final Pull/gul joke, followed by JR_047 and the success/praise.

Use the same approved ting-ting file for correct-chime cues JR_014, JR_040, JR_059, JR_083,
JR_096, JR_119, JR_138 and JR_158. The additional three Biscuit bites use the crunch instead.

## 5. Departure-only repeated FUEL branch

Do not introduce an extra mandatory fuel scan.

- Open a one-use repeat window when JR_015 begins after the first FUEL success.
- A fresh FUEL re-presentation during JR_015–JR_018 sets one pending gag flag. Finish these
  cues normally; no cutting, simultaneous dialogue or additional success acknowledgement.
- After JR_018, if the flag is set, play JR_019 then JR_020 immediately. Otherwise allow a
  maximum two-second quiet departure window over low jungle ambience for one fresh FUEL tap.
- If tapped in that window, play JR_019 then JR_020; otherwise continue without the gag.
- At the first gag trigger or the window's expiry, close the window permanently. Ignore further
  scans during the gag. Do not append a neutral tick or queue another gag.
- Begin JR_021 after that branch ends. FUEL can never trigger overflow in later scenes:
  during later questions it is simply a wrong card; during narrative it is ignored.
- Pausing and restarting use the shared state lifecycle; an old pending gag cannot leak into
  a resumed different scene or new story session.

## 6. Four-bite Biscuit game

Each accepted fresh presentation is exactly one bite. The first request is “बस एक?”
with questioning emphasis. Bites three and four do not announce their numbers;
all four presentations and the four-bite limit remain unchanged.

| Accepted bite | Audio |
|---|---|
| 1 | JR_059 correct chime → JR_060 identification → JR_061 crunch → JR_062 Elephant request |
| 2 | JR_061 crunch → JR_063 Elephant request |
| 3 | JR_061 crunch → JR_064 Elephant request |
| 4 | JR_061 crunch → JR_065 balloon joke → JR_066 laughter |

Bite acceptance is locked during the chime, identification and crunch. Re-arm the next bite
at the START of JR_062, JR_063 or JR_064. A fresh BISCUIT presented during that request is
accepted into a single pending-bite slot; finish the current request and then play the next
crunch. Never cut Elephant's request or queue two bites. Wrong cards during the request are
ignored. Additional scans while a pending bite is reserved are ignored.

If no pending bite exists when the request ends, wait for BISCUIT with a fresh 8/17/28-second
schedule using JR_067, JR_068, JR_069. These explain re-tapping the same card rather than making
the child solve the food choice again. Correct cards during these hints interrupt as usual.

For all Biscuit waiting states, use JR_070 then JR_071 instead of a random global correction.
Apply the shared correction limit and timer policy. A correction never changes the bite count.

After accepting bite four, close feeding before JR_065 begins. Its joke and laugh play in full,
with no fifth bite, new hints or queued corrections. Continue with JR_072. No real food is required.

## 7. Water break

JR_094 explicitly asks the child to drink and then tap WATER. Arm WATER as its prompt begins;
a correct tap during the prompt is latched and processed after the prompt ends. Do not enforce
an artificial drinking-duration test or claim to have observed drinking.

After the prompt, stop foreground speech and effects and mute the ambience. Wait quietly.
Play JR_095 at 30 seconds, 60 seconds, then 180, 300, 420 seconds and so on, measured from
the end of JR_094, excluding explicit player pauses. There are no normal hints and no timeout.
A correct WATER presentation immediately cancels/cuts reminders and starts JR_096.

Ignore all other cards quietly in this special break; do not use global corrections or the fuel
joke while the child is away. After WATER success, restore low daytime ambience beneath the
Parrot farewell, then crossfade to evening with JR_103: play its short jeep run-and-stop cue,
then its clearly audible wind-and-rain entry; continue its quieter loopable weather bed beneath
the opening dialogue. Play JR_106's two Bholu sneezes, then the selected entrance roar A
(JR_106_lion), immediately before JR_109. Coco's JR_107 and JR_108 play before this roar;
it is the child's first Lion clue and must come before Coco recognizes Lion King. After
Coco's tail remark in JR_111,
play the reused `JR_106_lion` grumpy Lion roar as cue JR_112, then JR_113. Do not play a spoken “अरे” in JR_112;
the earlier Bholu take is retired from this route.
JR_098 contains the pour and three gulps;
never cut its third gulp with the next line.

## 8. Shelter, ambience and lori

JR_128 resolves Lion's lost-way problem. JR_129 takes him into his dry cave BEFORE the leaf/
Blanket attempt. On entry, replace outdoor evening weather with the muffled sheltered component
of JR_129: start JR_129_bed.wav while playing JR_129_entry.wav, then advance when the entry
footsteps finish while the bed continues. Do not leave a second loud outdoor-rain bed playing
underneath it. Do not imply
rain is falling onto the sleeping Lion.

On a correct FLASHLIGHT tap, start JR_120's switch click immediately alongside the beginning
of JR_121 “YES! FLASHLIGHT!”, and mix JR_119's small correct chime quietly under them.
Do not wait for the spoken acknowledgement to finish before the switch sound. Advance to
JR_122 onward after the acknowledgement and the switch effect both finish. Ease the windy bed slightly as the flashlight
reveals the way; do not start a second background music track. The cave sound makes the later
location change. After JR_132, play the short `JR_132_sting` comic mistake SFX, then do not play
the retired JR_133 shiver; continue to JR_134.
Use the same immediate-acknowledgement pattern for BLANKET: JR_140 begins as soon as the card
is accepted, JR_138 chimes quietly underneath, and JR_139 fabric follows the spoken response.

After JR_143, play JR_144 (लोरी music) and JR_145 (Coco humming) together for exactly ten seconds.
This is one combined ten-second interval, not twenty seconds. Both assets are required for this
route; child's participation is optional. No voice detection, new card, retries or stronger
conditional praise is needed. Mix Coco's humming gently into the music. Keep the combined ten-second
mix close to the level of JR_143's soft spoken invitation, with a short fade at each end. Coco's
humming alone remains softer than spoken dialogue so the child has room to join in.

Then skip retired JR_146 and play JR_147 settling plus three clearly audible snores →
a short 0.35-second beat → JR_149 closing joke. The extra post-snore acknowledgement JR_148
is retired so the child's final memory is the stronger snore joke.
Lion does not speak after he is declared asleep. Continue with JR_150 departure, fading the cave
bed and remaining snore; rain/wind subside as the team returns to the jeep. Avoid layering a
second full snore in JR_150: it carries only the soft departing sound/tail.

Maintain one location ambience at a time. During questions, an unobtrusive bed may continue;
during jokes and hints, duck it for speech. JR_021 moving-jeep sound replaces JR_001 at departure,
then crossfades back to quiet JR_001 once Elephant's distress is heard at JR_027. Later jeep
transitions are short one-shots, not engines that continue beneath rescues.

## 9. Dance: exact shared audio clock

Start the dance immediately after JR_159; t=0 is the first strong beat of JR_160.
Schedule using the audio playback clock, not chained browser timeouts that drift.
All movement calls count inside their rounds. Preload every cue. Duck music enough for speech
without losing its beat; no speech or effects are baked into the loop.

| Time from dance start | Event |
|---|---|
| 0 s | Start JR_160; then JR_161 Elephant movement call over the beat |
| 10 s | JR_162 trumpet over music |
| 20 s | Stop music exactly with first syllable of JR_163: “Freeze!” |
| 20–23 s | Three-second freeze INCLUDING JR_163 |
| 23 s | Restart JR_160 on its strong opening beat; JR_164 Parrot call |
| 33 s | JR_165 parrot effect over music |
| 43 s | Stop music exactly with first syllable of JR_166: “Freeze!” |
| 43–46 s | Three-second freeze INCLUDING JR_166 |
| 46 s | Restart JR_160 on strong beat; JR_167 Captain dance call |
| 56 s | JR_168 cheek joke followed by JR_169 giggle, within this round |
| 66 s | End third loop; JR_170 resolving sting; begin closing as its tail fades |

Freeze calls must finish inside their three-second slots. Reject or re-edit an overlong recording
rather than truncate a word or silently lengthen the freeze. JR_168 plus JR_169 must finish before
66 seconds. Exactly 60 seconds of dance music and six seconds of freeze; no third freeze.
All card scans are ignored. Seated movement, watching and silence all progress normally.

## 10. Final ceremony and COMPLETE

After the resolving sting, play JR_171, JR_172; allow two seconds for the optional team response.
Then JR_173; allow two seconds for the optional high-five; then JR_174–JR_178.
Do not infer or wait indefinitely for speech or a gesture. Mark COMPLETE only after JR_178 ends.
Stop all remaining beds, timers and pending callbacks. Later card scans cannot restart the story.

## 11. Global wrong-card cue pairs

Use only during active ordinary question waits, under section 3's limits:
JR_179 → JR_180; JR_181 → JR_182; JR_183 → JR_184.
Keep the boing separate from the voice so success can stop either immediately.
Biscuit and Water exceptions take priority. Corrections never punish, remove progress or praise
the wrong answer. Do not play them during narrative, actions, lori, dance or final ceremony.

## 12. Handoff acceptance checks

The implementer must exercise these cases with the final asset manifest and reader adapter:

- Fast answers during every prompt are retained and acknowledged once at its end.
- A correct answer during each hint/correction cuts obsolete feedback and cancels later hints.
- Holding a card through several seconds and state transitions never counts as another tap.
- Removal and re-presentation during an Elephant request reserves only the next bite;
  scans during crunches do not queue bites. Four bites produce four crunches and one chime.
- Ignoring “बस एक!” leads to the explicit same-card hint; a held card still cannot feed twice.
- Multiple wrong cards cannot indefinitely delay a hint or stack correction voices.
- FUEL repeat produces at most one departure gag; later FUEL scans never trigger overflow.
- Water stays quiet except its reminders and resumes only on WATER; no fixed drinking test.
- Lion reaches shelter; the ten-second lori precedes his sleepy line, snore and acknowledgement.
- Pausing during a wait, pending Biscuit request, departure gag or dance preserves coherent state;
  stop/restart invalidates old audio callbacks and never replays stale hints.
- Dance stops/restarts at the exact audio-clock boundaries; its calls fit the allocated slots.
- Completion leaves no looping bed, input response, reminder or pending narration.
- Every cue ID resolves; speaker identities match the approved references, and per-line directions
  and music-generation prompts are never spoken as story dialogue.

This document specifies behavior. Passing these checks requires an implemented player and actual
audio; creating this specification alone does not constitute a successful runtime test.
