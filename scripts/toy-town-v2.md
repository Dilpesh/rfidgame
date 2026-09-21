# Toy Town — script changes for v2

Nothing here has been generated. Lines marked **NEW** need recording; the rest
is existing audio, reused untouched.

---

## 1. Voices — only one changes

| character | lines | decision |
|---|---|---|
| **Driver Uncle** | 13 (41s) | **new voice.** A warm, gentle adult man, a bit absent-minded. Not performed as a child |
| Chuku | 41 | **unchanged** |
| Narrator | 71 | unchanged |
| Teddy | 5 | unchanged |

Re-voicing Driver Uncle alone costs 13 lines. All 13 must be redone together,
including the ones whose words are not changing, or he will sound like two
different people across the story.

---

## 2. The opening

The problem was never length. Nothing was asked of the child for 40 seconds.
Now they are asked to *become* the Captain in the first fifteen, and the rest
of the scene is the reward for saying yes.

| id | speaker | line | |
|---|---|---|---|
| S01_01 | Chuku | हैलो! मैं हूँ Chuku — Toy Town Express! छोटी-सी train, बड़ी-बड़ी मस्ती! | **NEW** |
| S01_02 | Chuku | पर आज एक problem है… मुझे चलाने के लिए चाहिए एक Captain. क्या तुम मेरे Captain बनोगे? | **NEW** |
| *(1.5s)* | | *room for them to answer out loud* | |
| S01_03 | Narrator | अरे वाह! हमें Captain मिल गया! | **NEW** |
| `station_bell` | | | reuse |
| S01_04 | Chuku | तो Captain, सबसे पहले मेरा शानदार horn सुनो! | **NEW** |
| `horn_meow` | | | **NEW sfx** |
| S01_05 | Narrator | Chuku! तुम train हो या बिल्ली? | reuse |
| S01_06 | Chuku | Oops! ग़लत button! | **NEW** |
| `horn_train_soft` | | | **NEW sfx** |
| S01_07 | Chuku | ये रहा असली वाला! | **NEW** |
| S01_08 | Narrator | आज हम Teddy से मिलने Toy Town जा रहे हैं। | reuse |
| S01_09 | Teddy | मैं वहाँ welcome करूँगा! और इस बार बिल्कुल नहीं सोऊँगा! | reuse |
| S01_10 | Driver Uncle | सब ready! बस… मेरी चाबी कहाँ है? | **NEW** (voice) |
| S01_11 | Chuku | Captain! Driver Uncle की चाबी खो गई। तुम्हारे पास कुछ है जो engine खोल दे? | **NEW** |

The KEY card is asked for at about **15 seconds**, not 40. The pocket gag
already moved to after the key is found.

---

## 3. The two horns

Not fixable by writing. `horn_meow` and `horn_train_soft` measure within about
1 dB of each other in every band below 1.2 kHz — the same sound — and neither
has a train horn's low end. "That's a cat, not a train" cannot land when the
cat and the train are identical. Prompts are in `ELEVENLABS_BRIEF.md`.

---

## 4. Jokes that need an adult's head

A 3–5 year old takes language literally, cannot yet hold two facts apart in
time to connect them, and does not know the social rules a joke is violating.
What does work: physical absurdity, bodily noises, someone being visibly bad at
something, exaggeration, and repetition of a phrase they can join in with.

Every joke in the story, audited against that.

### Cut or rewrite

| id | what it is now | why it fails | replacement |
|---|---|---|---|
| S03_03 | हवा थोड़ी-सी… हाथ की exercise ज़्यादा! | **irony** — states the opposite of the point and expects you to invert it | **Chuku:** Driver Uncle… आपकी टोपी की हवा आपकी मूँछ तक भी नहीं पहुँची!<br>**Driver Uncle:** हाँ… मेरी टोपी हवा नहीं करती। बस हिलती है। |
| S06_04, S06_05 | ये signal की आवाज़ है? / Signal biscuit के सपने थोड़ी देखता है! | **needs a norm first** — that signals make a sound, then a negation on top | **Teddy:** खर्र्र… और एक biscuit… खर्र्र… और एक…<br>**Chuku:** सोते-सोते biscuit खा रहा है! |
| S06_OK3 | मैं सो नहीं रहा था! बस पटरी की softness check कर रहा था! | the *lie* works at this age; **"softness check"** is a quality-testing idea | मैं सो नहीं रहा था! बस… मेरी आँखें आराम कर रही थीं! |
| S06_OK4 | पटरी पर softness check?! ये कौन करता है?! | follows the above | आँखें आराम कर रही थीं?! ये कौन करता है?! |
| S06_OK5, S06_OK6 | तो result क्या आया? / Bed better है! | **"result"** frames it as a report on an experiment | *cut OK5.* **Teddy:** अब मैं bed पर ही सोऊँगा! |
| S02_OK2 | अच्छा! तभी मेरी टोपी से आलू पराठे की खुशबू आ रही थी! | **delayed inference** — explains an earlier smell using a fact revealed later | अरे! ये तो मेरा lunchbox है! फिर मेरी टोपी कहाँ गई? |
| S03_OK3 | मूँछ जी! Dance बाद में। पहले अपना ticket दिखाइए! | talking to his moustache is fine; **checking its ticket** is bureaucracy humour | मूँछ जी! आप भी dance कर रहे हो?! |
| S03_OK4 | अपनी मूँछ से ticket माँग रहे हैं! ये कौन करता है?! | follows the above | अपनी मूँछ से बात कर रहे हैं! ये कौन करता है?! |
| DANCE_J2 | मेरी battery तो sandwich से चलती है! | **metaphor** — food standing in for a battery | मेरी मूँछ भी थक गई! |

### Keep — these already work

| id | why |
|---|---|
| S01_10 / S01_12 | half a sandwich in **each** pocket. Concrete, physical, absurd |
| S02_OK1 | a lunchbox worn as a hat. Purely visual |
| S05_OK2 / S05_OK3 | a burp mistaken for a horn. Bodily and immediate — the strongest joke in the story |
| S04_03 | Driver Uncle singing badly. Being bad at something is the surest laugh at this age |
| S01_OK1 | engine starting, or Chuku sneezing? Two concrete sounds confused |
| W_KEY_BISCUIT | engines don't eat biscuits, Driver Uncle will. Concrete |
| **"ये कौन करता है?!"** | the catchphrase. Repetition is a gift at this age — they will start saying it with you. Use it every time, never vary it |
| DANCE_F2 | the robot's battery stopping. A freeze game, not a metaphor |

### Not a joke, but wasted on them

`S07_BOTH` ends "तुमने बिजली भी बचाई!" — saving electricity is a civic idea a
four-year-old has no hook for, and it is the last thing said before the finale.
Recommend ending on "तुम्हें दोनों चीज़ें याद रहीं!" and stopping there. No new
audio: the line just gets trimmed or re-recorded shorter.

---

## 5. Water break — done, no audio needed

Applied. "मैं तुम्हारी जगह संभालता हूँ! Driver Uncle, Captain की सीट पर sandwich मत
रखना!" is cut. The child gets the instruction, how to come back, then
**silence** until they return. First reminder unchanged at 30s.

---

## 6. What this costs

| | count |
|---|---|
| Driver Uncle re-voiced | 13 lines |
| New Chuku lines (existing voice) | 6 |
| New Narrator lines | 1 |
| Rewritten lines (Chuku / Teddy / Driver Uncle) | 8 |
| New sound effects | 2 |
| Reused untouched | ~105 |

Roughly **30 clips**, against 130 in the story.
