# Toy Town — script changes for v2

Written to be read before anything is generated. Nothing here has cost a credit
yet. Lines marked **NEW** need recording; everything else is existing audio,
reused as-is.

---

## 1. Voices

| character | now | change |
|---|---|---|
| **Chuku** | adult-ish | **a child's voice.** She is the one who asks the Captain for help, so she should sound like a kid asking a friend, not a grown-up assigning a task |
| **Driver Uncle** | reads kiddish | **a warm adult male voice.** He is the one who needs help — he has to sound like a grown-up who has genuinely lost his keys |
| Narrator | — | unchanged |
| Teddy | — | unchanged (sleepy, slow) |

**Cost before you commit to this:** Chuku has **41 lines / 192 seconds** across
the whole story and Driver Uncle **13 lines / 41 seconds**. Changing their
voices means re-recording all 54, not just the new ones — about **4 minutes of
audio**. The alternative is to change them only from here on, which would make
the same character sound like two people, so it isn't really an alternative.

---

## 2. The opening

The problem is not length, it's that nothing is asked of the child for 40
seconds. The fix is to give them a job in the first fifteen, and let the rest
of the scene be the reward for saying yes.

The child is asked to *become* the Captain rather than being told they already
are — and the horn joke, which worked, moves to right after they accept.

| id | speaker | line | |
|---|---|---|---|
| S01_01 | Chuku | हैलो! मैं हूँ Chuku — Toy Town Express! छोटी-सी train, बड़ी-बड़ी मस्ती! | **NEW** |
| S01_02 | Chuku | पर आज एक problem है… मुझे चलाने के लिए चाहिए एक Captain. क्या तुम मेरे Captain बनोगे? | **NEW** |
| *(1.5s)* | | *space for them to answer out loud* | |
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

Then the KEY card is asked for — at about **15 seconds** in, rather than 40.

The pocket gag (sock, rubber duck, half a sandwich) already moved to *after*
the key is found, in the pacing commit. It stays there.

---

## 3. The two horns

This is the one that cannot be fixed by writing. Measured: `horn_meow` and
`horn_train_soft` are within about 1 dB of each other in every frequency band
below 1.2 kHz — they are effectively the same sound — and neither has a train
horn's low end. The joke is "that's a cat, not a train", and both make the
same noise, so there is nothing to laugh at.

- **`horn_meow`** — an unmistakable cartoon cat. Bright, 700–1500 Hz, a rising
  then falling "meeeow", slightly indignant. Must sound nothing like a horn.
- **`horn_train_soft`** — a real train horn. Fundamental down at 150–300 Hz,
  two notes, warm not shrill. Must sound nothing like a cat.

If those two are right, S01_05 lands with no rewriting at all.

---

## 4. The fan joke

Currently Driver Uncle fans himself with his cap and says "हवा थोड़ी-सी… हाथ की
exercise ज़्यादा!" — a wordplay about effort versus output, which needs an adult's
sense of irony. Under-fives don't have one yet.

What does work at this age is someone being visibly, comically bad at something.
So the joke becomes the cap being useless, out loud:

| id | speaker | line | |
|---|---|---|---|
| S03_01 | Chuku | उफ़्फ़! इस coach में तो गर्मी है! | reuse |
| S03_02 | Driver Uncle | रुको! मैं अपनी टोपी से हवा करता हूँ! | **NEW** |
| `cloth_flaps` | | | reuse |
| S03_03 | Chuku | Driver Uncle… आपकी टोपी की हवा आपकी मूँछ तक भी नहीं पहुँची! | **NEW** |
| S03_04 | Driver Uncle | हाँ… मेरी टोपी हवा नहीं करती। बस हिलती है। | **NEW** |
| S03_05 | Narrator | Captain, ऐसी हवा कैसे आए जो हम सब तक पहुँचे? | reuse (S03_04) |

The moustache is already the payoff after the fan starts ("देखो! हवा में Driver
Uncle की मूँछ हिल रही है!"), so setting it up here makes the reward land too.

---

## 5. Teddy's snore

"खर्र्र… biscuit… खर्र्र…" → "ये signal की आवाज़ है?" asks the child to know that
signals make a sound and that this isn't one. Two steps of knowledge for a
joke that pays once.

The funnier version is simpler: Teddy is talking in his sleep about food, and
everyone can hear it.

| id | speaker | line | |
|---|---|---|---|
| `brake_soft` | | | reuse |
| S06_01 | Chuku | अरे, आगे कौन है? आराम से रुकते हैं! | reuse |
| `teddy_snore` | | | reuse |
| S06_02 | Narrator | Teddy! तुम तो welcome करने वाले थे! पटरी के बीच में कैसे सो गए? | reuse |
| S06_03 | Teddy | खर्र्र… और एक biscuit… खर्र्र… और एक… | **NEW** |
| S06_04 | Chuku | सोते-सोते biscuit खा रहा है! | **NEW** |
| S06_05 | Narrator | Captain, Teddy की नाक कुछ yummy ढूँढ रही है। हमारे पास उसके लिए क्या है? | reuse (S06_06) |

"सोते-सोते biscuit खा रहा है" is a thing a four-year-old can picture
immediately, and it sets up S06_OK1 ("हूँ? Biscuit? मैं जाग गया!") properly.

---

## 6. Water break — already done, no audio needed

Applied on the branch. The scene said:

> इतना dance किया! अब छोटा-सा water break… *(instruction)*
> **मैं तुम्हारी जगह संभालता हूँ! Driver Uncle, Captain की सीट पर sandwich मत रखना!**
> जब पानी पीकर वापस आ जाओ, तो WATER वाला card tap कर देना।

The middle line is cut. A child walking to the kitchen cannot hear a joke, and
it was the line that did not land anyway. Now: the instruction, how to come
back, then **silence** until they return. The first reminder is 30 seconds
later and unchanged.

---

## 7. What this costs

| | lines | notes |
|---|---|---|
| Chuku re-voiced | 41 | whole story, not just new lines |
| Driver Uncle re-voiced | 13 | whole story |
| Genuinely new lines | 10 | of which 8 are Chuku or Driver Uncle anyway |
| New sound effects | 2 | the meow and the train horn |
| Reused unchanged | ~76 | Narrator and Teddy, untouched |

So it is really one decision: **re-voice Chuku and Driver Uncle, or don't.** If
yes, the new lines are nearly free on top. If no, the two horns alone are worth
generating — they fix a joke without touching a single word.
