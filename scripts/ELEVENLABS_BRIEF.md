# ElevenLabs generation brief — Toy Town v2

Everything needed to generate the v2 clips, with nothing left to infer. Filenames
are exactly what the game loads: drop each result into
`docs/toy-town/audio/<ID>.mp3`.

**Do not regenerate anything not listed here.** 105 of the 130 clips are staying
as they are.

---

## 1. Before you generate anything

### Level every result to match

The game now expects **every** clip levelled. This is not optional — it is what
fixed "SFX across the story is low". After downloading each file:

```
# narration
ffmpeg -i in.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=7" -c:a libmp3lame -q:a 2 out.mp3

# sound effects: target -20 dB mean, peaks under -1.5 dBTP
ffmpeg -i in.mp3 -af volumedetect -f null -          # read mean_volume
ffmpeg -i in.mp3 -af "volume=<-20 minus mean>dB,alimiter=limit=0.85:level=false" \
       -c:a libmp3lame -q:a 2 out.mp3
```

`alimiter` **must** carry `level=false`. Without it, it auto-levels to its own
ceiling and silently undoes the gain staging — this has bitten us twice.

For a spiky effect (a click, a footstep) whose peak is already at the ceiling
while its body sits 25 dB below, compress first:

```
ffmpeg -i in.mp3 -af "acompressor=threshold=-26dB:ratio=4:attack=5:release=140:makeup=6,\
alimiter=limit=0.85:level=false" -c:a libmp3lame -q:a 2 out.mp3
```

### Check it against the phone, not the laptop

`python3 check_audio.py docs/toy-town` and listen on an actual phone, speaker
only, from two metres. A phone speaker produces almost nothing below ~450 Hz —
anything whose character lives down there will not survive.

---

## 2. Narration — `POST /v1/text-to-speech/{voice_id}`

```
POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128
xi-api-key: $ELEVENLABS_API_KEY
Content-Type: application/json

{
  "text": "<line, with its audio tag at the front>",
  "model_id": "eleven_v3",
  "voice_settings": { ... per character, below ... }
}
```

`eleven_v3` reads inline tags like `[excited]`, `[whispers]`, `[sighs]`. The
tags below are part of the text you send, not a separate field.

### Voices

| character | voice | settings |
|---|---|---|
| **Driver Uncle** | **NEW — audition needed.** Warm adult Indian man, middle-aged, gentle, slightly absent-minded. Unhurried. Must not read young: this is the one the kids disliked | `stability 0.55, similarity_boost 0.8, style 0.30, use_speaker_boost true` |
| Chuku | existing voice id — do not change | `stability 0.40, similarity_boost 0.8, style 0.45, use_speaker_boost true` |
| Narrator | existing voice id | `stability 0.50, similarity_boost 0.8, style 0.35, use_speaker_boost true` |
| Teddy | existing voice id | `stability 0.60, similarity_boost 0.8, style 0.30, use_speaker_boost true` |

Higher `stability` for Driver Uncle and Teddy keeps them steady and adult;
Chuku's lower value lets her bounce.

**Audition Driver Uncle before generating all 13.** Use this line, which has to
carry both his absent-mindedness and an adult register:

> `[warm] सब ready! बस… मेरी चाबी कहाँ है?`

Pick from at least three candidates, on the phone speaker, not headphones.

### Clips to generate

`NEW` = new words. `REVOICE` = same words, new voice. `REWRITE` = new words
replacing a joke that did not land.

#### Driver Uncle — all 13, together

| id | tag + text | why |
|---|---|---|
| S01_10 | `[warm] सब ready! बस… मेरी चाबी कहाँ है?` | REVOICE |
| S01_12 | `[matter-of-fact] बाकी आधा दूसरी जेब में है!` | REVOICE — deadpan, no wink |
| S01_OK3 | `[warm] Thank you, Captain! अब चलें?` | REVOICE |
| S02_03 | `[flustered] Oops! मेरा lunchbox सीट से टकरा गया। अँधेरे में कुछ दिख नहीं रहा!` | REVOICE |
| S02_OK2 | `[realising] अरे! ये तो मेरा lunchbox है! फिर मेरी टोपी कहाँ गई?` | REWRITE |
| S03_02 | `[cheerful] रुको! मैं अपनी टोपी से हवा करता हूँ!` | REWRITE |
| S03_04b | `[deadpan] हाँ… मेरी टोपी हवा नहीं करती। बस हिलती है।` | REWRITE — new id, see §4 |
| S03_OK1 | `[relieved] आहाहा… अब मज़ा आया!` | REVOICE |
| S03_OK3 | `[delighted] मूँछ जी! आप भी dance कर रहे हो?!` | REWRITE |
| S04_03 | `[singing badly] मैं गाना गाऊँ? ला… ला… लाआआ!` | REVOICE — commit to it; bad singing is the joke |
| S05_OK2 | `[embarrassed] Oops! Excuse me!` | REVOICE |
| S08_02 | `[proud] और मेरी lunchbox वाली टोपी भी पकड़ ली!` | REVOICE |
| DANCE_J2 | `[out of breath] मेरी मूँछ भी थक गई!` | REWRITE |

#### Chuku — existing voice, new or rewritten words only

| id | tag + text | why |
|---|---|---|
| S01_01 | `[excited] हैलो! मैं हूँ Chuku — Toy Town Express! छोटी-सी train, बड़ी-बड़ी मस्ती!` | NEW |
| S01_02 | `[hopeful] पर आज एक problem है… मुझे चलाने के लिए चाहिए एक Captain. क्या तुम मेरे Captain बनोगे?` | NEW — the invitation. Must sound like asking a friend, not assigning a job. End on a real question |
| S01_04 | `[proud] तो Captain, सबसे पहले मेरा शानदार horn सुनो!` | NEW |
| S01_06 | `[embarrassed] Oops! ग़लत button!` | NEW |
| S01_07 | `[proud] ये रहा असली वाला!` | NEW |
| S01_11 | `[urgent] Captain! Driver Uncle की चाबी खो गई। तुम्हारे पास कुछ है जो engine खोल दे?` | NEW |
| S03_03 | `[amused] Driver Uncle… आपकी टोपी की हवा आपकी मूँछ तक भी नहीं पहुँची!` | REWRITE |
| S03_OK4 | `[delighted disbelief] अपनी मूँछ से बात कर रहे हैं! ये कौन करता है?!` | REWRITE — **the catchphrase must sound identical every time it appears.** Same pitch, same rhythm, so they can join in |
| S06_04 | `[delighted] सोते-सोते biscuit खा रहा है!` | REWRITE |

#### Narrator

| id | tag + text | why |
|---|---|---|
| S01_03 | `[warm, delighted] अरे वाह! हमें Captain मिल गया!` | NEW — lands right after the child says yes. Warm, not triumphant |

#### Teddy

| id | tag + text | why |
|---|---|---|
| S06_03 | `[sleepy, mumbling] खर्र्र… और एक biscuit… खर्र्र… और एक…` | REWRITE — genuinely half-asleep, trailing off |
| S06_OK3 | `[defensive] मैं सो नहीं रहा था! बस… मेरी आँखें आराम कर रही थीं!` | REWRITE |
| S06_OK6 | `[sheepish] अब मैं bed पर ही सोऊँगा!` | REWRITE |

---

## 3. Sound effects — `POST /v1/sound-generation`

```
POST https://api.elevenlabs.io/v1/sound-generation
xi-api-key: $ELEVENLABS_API_KEY
Content-Type: application/json

{ "text": "<prompt>", "duration_seconds": <n>, "prompt_influence": 0.6 }
```

Raise `prompt_influence` toward 0.8 if a result drifts off-brief; drop toward
0.3 if it sounds stiff. Generate several takes and pick — these are cheap.

### The two that matter

| file | duration | prompt | must |
|---|---|---|---|
| `horn_meow` | 1.2s | *A cartoon cat meow, bright and comic, rising then falling in pitch, slightly indignant, like a toy cat. Clean, no background, no reverb.* | Energy centred **700–1500 Hz**. **Nothing below 400 Hz.** If it has any low rumble it will read as a horn again and the joke dies |
| `horn_train_soft` | 1.2s | *A small friendly steam train horn, two soft notes, warm and round, low pitched, gentle not shrill. Clean, no background.* | Fundamental **150–300 Hz** with real weight underneath. This is what makes it *not* the cat |

Check the contrast before accepting them:

```
for f in horn_meow horn_train_soft; do
  for r in "60 400" "400 1200" "1200 4000"; do set -- $r
    ffmpeg -i $f.mp3 -af "highpass=f=$1,lowpass=f=$2,volumedetect" -f null - 2>&1 \
      | grep mean_volume
  done
done
```

The train must be **at least 12 dB louder than the meow in 60–400 Hz**. If it is
not, they will sound like the same thing again — which is exactly the bug.

### The key and engine sequence

Currently unclear even after levelling. Three clips that must tell one story:
*key goes in and turns → engine catches → engine runs.*

| file | duration | prompt |
|---|---|---|
| `key_turn` | 1.0s | *A small metal key sliding into a lock and turning, two distinct clicks, close and crisp, no background.* |
| `engine_wake` | 2.0s | *A small toy train engine starting: a brief crank, then catching and settling into a steady gentle chug. Friendly, not industrial. No background.* |
| `train_sneeze` | 1.0s | *A cartoon sneeze from a small train — a short puff of steam turning into an "achoo", comic and soft.* |

They play back to back, so audition them **in sequence**, not one at a time:

```
ffmpeg -i key_turn.mp3 -i engine_wake.mp3 -i train_sneeze.mp3 \
  -filter_complex "[0][1][2]concat=n=3:v=0:a=1" -y /tmp/seq.mp3
```

If you cannot hear the key turn *before* the engine catches, the key clip is
still wrong.

### Optional, if credits allow

| file | duration | prompt |
|---|---|---|
| `clap` (`short_applause`) | 3.0s | *A small group of children clapping happily, close, warm, no room echo.* Current one reads thin |
| `station_bell` | 1.5s | *A single soft Indian railway platform bell, warm and round, one strike with a short tail.* Used at the new "we have a Captain!" moment |

---

## 4. One code change after generating

`S03_04b` is a new clip id. `docs/toy-town/story.js` needs it inserted into
stop 2's `setup`, and `S03_04` (the narrator's "ऐसी हवा कैसे आए…") stays last so
the scene still ends on the question. Tell me when the audio exists and I will
wire it, re-run `qa_dance.js` and `check_games.py`, and confirm nothing else
moved.

---

## 5. Checklist

- [ ] Audition ≥3 Driver Uncle voices on a phone speaker; record the winning id
- [ ] Generate the 13 Driver Uncle lines in one pass with the same voice + settings
- [ ] Generate 6 Chuku, 1 Narrator, 3 Teddy clips with their **existing** voices
- [ ] Generate `horn_meow` + `horn_train_soft`; verify ≥12 dB separation in 60–400 Hz
- [ ] Generate `key_turn`, `engine_wake`, `train_sneeze`; audition concatenated
- [ ] Level every file (narration −16 LUFS, effects −20 dB mean, `level=false`)
- [ ] Drop into `docs/toy-town/audio/`, tell me, I wire `S03_04b` and re-run the gates
- [ ] Play it to the kids and write what happened in `FEEDBACK.md`
