# Writing a story for Kishu Mishu

Everything we have learned about what works for a 3–5 year old, in a form you
can run a finished script through before a single line is recorded.

This is the **writing** rule set. Two siblings:

- `AUDIO_STANDARD.md` — how the audio must measure (bed vs narration, ffmpeg chains)
- `LEARNINGS.md` — how the code must behave (wake lock, scan guard, interruptions)

Feedback from actual play sessions lives in `feedback/<story>.md`, one per
story. When something there turns out to be true of **every** story, it gets
promoted into this file and the story file keeps only the specific instance.

---

## 1. The first minute decides everything

**A child must be able to act within 30 seconds.** Not be told the plot, not be
introduced to the cast — *act*. Toy Town made them listen for 59 seconds before
the first card and lost them; Jungle Rescue asks at 38 and holds them.

**Give them a job, do not assign them one.** "अरे वाह! हमारे Captain आ गए!"
tells a child they already are something. "मुझे चलाने के लिए चाहिए एक Captain.
क्या तुम मेरे Captain बनोगे?" asks, leaves a 1.5s gap, and lets them say yes out
loud. The second one buys you the next ten minutes.

**Charm is a reward, not a toll.** Anything delightful that is not needed to
understand the ask — a running gag, a character's backstory — moves to *after*
the card is found. Toy Town's pocket gag went from blocking the door to being
the prize, and cost nothing.

---

## 2. Acknowledgement and praise

These are different things and they are not interchangeable.

**Acknowledge every single success. Three parts, in this order:**

1. **Name the card** — "YES! Snack!"
2. **Name the child, or their role** — "Great job, Kishu Mishu!" / "शाबाश Captain!"
3. **Say what changed in the world** — "Elephant Dada के लिए खाना मिल गया!"

Jungle Rescue does all three every time. Toy Town did only the third, and at two
stops said nothing at all — a child brought the right card and heard a click.
That is the single biggest difference between the two stories.

**Say it the same way every time.** Same words, same rhythm, same pitch. A
three-year-old will start shouting "YES! KEY!" with you, and that is worth more
than any individual joke.

**Praise only where effort was spent.** Not every stop. Praise belongs to:

- a physical task — going to drink real water, three rounds of dancing
- a card found only after hints
- the end of the story

Everything else gets the acknowledgement and moves on. Generic praise on every
stop stops being heard by the fourth one, costs seconds you cannot spare, and
quietly shifts their attention from the story to being approved of.

**Never praise the child for being clever.** Praise what they did: "तुम सच में
पानी पीकर आए", "तुमने पूरे तीन round dance किया".

---

## 3. Jokes a 3–5 year old can actually have

At this age they take language literally, cannot hold two facts apart in time
and connect them, and do not know the social rules a joke is breaking.

### Cut on sight

| shape | example that failed |
|---|---|
| **Irony / understatement** | "हवा थोड़ी-सी… हाथ की exercise ज़्यादा!" |
| **Metaphor** | "मेरी battery तो sandwich से चलती है!" |
| **Needs a norm known first** | "ये signal की आवाज़ है?" — needs to know signals make a sound |
| **Social-role humour** | "मूँछ जी! पहले अपना ticket दिखाइए!" — ticket inspection |
| **Framing as testing or reporting** | "पटरी की softness check", "तो result क्या आया?" |
| **Delayed inference** | "तभी मेरी टोपी से आलू पराठे की खुशबू आ रही थी!" — explains an earlier fact with a later one |
| **Running gag across scenes** | "Coco को इस jungle में खाना मिलने वाला नहीं है" — needs them to remember two scenes ago |
| **A wink at hidden intent** | "और Water को guard करूँगा. Coco… बस guard." |
| **Adult concession** | "Fair point." |

### Keep and write more of

| shape | example that worked |
|---|---|
| **Physical absurdity** | half a sandwich in **each** pocket |
| **Visual absurdity** | a lunchbox worn as a hat |
| **Bodily sounds** | a burp mistaken for a train horn — the strongest joke we have |
| **Being visibly bad at something** | Driver Uncle singing "ला… ला… लाआआ!" |
| **Immediate cause and effect** | sneeze right as the engine starts |
| **Concrete category error** | "Engine biscuit नहीं खाता… Driver Uncle खा लेंगे!" |
| **A repeated catchphrase** | "ये कौन करता है?!" — never vary it |

### The test

**Could a four-year-old draw the joke?** If the funny part is a picture, it
works. If it is a relationship between two ideas, it does not.

**Does the joke need a sentence of explanation?** Then it is for you, not them.

**Is a character talking to an object?** Fine — kids do it themselves. Is the
character talking to it *in a social role*? Not fine.

---

## 4. Pacing and silence

**Hint ladder: about 10 / 15 / 20 / 25 seconds.** Never leave a stuck child in
silence for 45 seconds. Water breaks are the exception — 30 / 45 / 75 — because
they are genuinely away from the phone.

**After sending a child out of the room, stop talking.** Give the instruction,
say how to come back, then silence. They cannot hear a joke from the kitchen,
and returning to more talking is not a welcome. Both stories had a wink here;
both cut it.

**No scripted pauses under one second.** They are not heard as beats, only as
seams. The gap between two clips is already long enough.

**Fewer, longer takes beat many short ones.** Toy Town plays 72 narration clips
where Jungle Rescue plays 37, and every boundary is a small stutter while the
next buffer decodes. Write a scene as two long lines, not six short ones.

**Never shorten a dance or a physical game to save time.** Cut waiting, not
doing. The dance is the part they came for.

---

## 5. Sound

Full spec in `AUDIO_STANDARD.md`. What the *writer* needs to know:

**If a joke depends on two sounds being different, they must measure
different.** Toy Town's "train हो या बिल्ली?" could never land because the cat
and the train were within 1 dB of each other in every band below 1.2 kHz. Write
the contrast into the brief and test it before accepting the clips.

**Every sound effect at one level.** Toy Town's spanned 36 dB, so half of them
vanished on a phone; Jungle Rescue's span 6 dB and it is why it sounds better.
Levelling is not polish, it is whether the key turning is audible at all.

**Music is not a sound effect.** Do not attenuate it with them, and never duck
it to nothing under a dance instruction — the beat is what they are moving to.

**Write for a phone speaker at two metres, screen down.** It produces almost
nothing below 450 Hz. A sound whose character lives down there will not exist.

---

## 6. Running the filter over a finished script

- [ ] Can a child act within 30 seconds? Where exactly is the first ask?
- [ ] Is the child *invited* into a role, with a gap to answer?
- [ ] Does every success name the card, name the child, and say what changed?
- [ ] Is the acknowledgement worded identically every time?
- [ ] Is praise present **only** after real effort? Count them — more than three in a story is too many
- [ ] Every joke run past §3. For each: could a four-year-old draw it?
- [ ] Any joke that spans two scenes? Cut it
- [ ] After any instruction that sends them away — silence?
- [ ] Any scripted pause under 1s? Delete
- [ ] Longest gap a stuck child can face — under 30s?
- [ ] Any joke that depends on two sounds differing? Write the measurable contrast into the audio brief
- [ ] Is the catchphrase used every time it could be, unchanged?
- [ ] Read the whole thing aloud at a four-year-old's pace. Where do you get bored? So will they
