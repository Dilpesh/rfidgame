# Decisions log

What we agreed to change, when, and whether it is actually in a story yet.
`TASKS.md` is what is next; this is what was settled and why.

---

# 2026-09-21 morning — pacing and audio, before the kids played

Driven by measurement against Jungle Rescue, not by taste.

## Built and live

| # | decision | why |
|---|---|---|
| 1 | **Toy Town opening 59s → 40s**, no line cut — the pocket gag moved to after the KEY card | 59s before a child could act; Jungle Rescue asks at 38s |
| 2 | **All 38 sound effects levelled to −20 dB mean** | they spanned 36 dB; `key_turn` sat 20 dB under the voice, so the key did not turn on a phone |
| 3 | **Blanket 0.55 attenuation on effects removed** → every clip plays at 1.0 | with the files levelled it had nothing left to do |
| 4 | **Master gain 0.8 → 1.0** | Jungle Rescue runs 1.0; this was most of the ~3 dB energy difference |
| 5 | **Dance music no longer takes the SFX cut**; bed 0.5 → 0.85, duck 0.15 → 0.35 | the beat fell to ≈−43 LUFS under every dance call — inaudible |
| 6 | **FREEZE decoded before the music is cut**, and the groove returns before "jump back in" | the silence used to arrive before the word; beatless dance 43.9s → 24.2s |
| 7 | **Fourth hint 45s → 25s** | 45 seconds of silence for a stuck child |
| 8 | **Silence after the water instruction** — "मैं तुम्हारी जगह संभालता हूँ" cut | a child walking to the kitchen cannot hear a joke |
| 9 | **New cat and train horn** | the pair measured 1.1 dB apart below 400 Hz — the same sound, so the joke could not land. Now 17.7 dB apart |
| 10 | **Dance length left alone** — three full rounds, 113.5s | cut waiting, not doing |
| 11 | **Water reminders left at 30/60/120s** | asked for explicitly |

## Decided about how we work

| # | decision |
|---|---|
| 12 | **Interruption handling parked.** Both Carry on screens removed — the pause screen was being hijacked, and resuming replayed the stop. Three states, not one: paused on purpose / interrupted but recoverable / page gone |
| 13 | **Toy Town v2 ships beside the original**, not over it, so the A/B has one variable |
| 14 | **Feedback split per story**, `feedback/<slug>.md`, with `STORY_CRAFT.md` for what is true of every story |
| 15 | **Level two clips before asking anyone to choose between them** — a before/after went out 9 dB apart, which made the comparison worthless |
| 16 | **A task list with states**, because "written into STORY_CRAFT" was reading as done |

## Written, not built

| # | decision |
|---|---|
| 17 | Acknowledgement after every card; praise only after real effort |
| 18 | New opening — the child is *asked* to be Captain |
| 19 | Driver Uncle re-voiced — 13 lines, together |
| 20 | Six rewritten jokes *(three of these were later cancelled — see the evening)* |

---

# 2026-09-21 evening — after both kids played

The first session with real children, and the most valuable input so far.

## The correction

| # | decision | why |
|---|---|---|
| 21 | **Three joke cuts cancelled** — आलू पराठे की खुशबू, मूँछ जी… ticket, battery से sandwich | all three landed. The audit classified by *mechanism* (metaphor, delayed inference, social role) instead of asking whether the joke is drawable. All three are drawable |
| 22 | **The rule is the drawing test, not the mechanism.** A metaphor is fine when its vehicle is food, a body, or an object behaving like a person | what actually failed has no picture: degree ("हवा थोड़ी-सी… exercise ज़्यादा"), abstract domains, concessions ("Fair point.") |

## New craft rules, true of every story

| # | decision |
|---|---|
| 23 | **Something must land every 30 seconds** — a joke, an effect, or appreciation. Measured after: 5 of Jungle Rescue's 10 scenes break this; the giraffe goes **58s** with nothing |
| 24 | **Ask for the card in the same breath as naming the need** — the child picks up the LIGHT card the moment light is mentioned, then has to wait |
| 25 | **The ending is what they remember** — appreciation, then a joke. Jungle Rescue's celebration has **zero** sound effects across 44s |
| 26 | **Mess and dirt are reliable** — "muddy / गंदा" got the single biggest laugh of the night |
| 27 | **Repetition is the strongest device we have** — "ये कौन करता है?!" worked for both kids. Use a catchphrase 3–4 times, identical every time |
| 28 | **Rhyme and repeated sound** on the card ask, the acknowledgement, and anything physical |

## Toy Town — decided, not yet built

| # | decision |
|---|---|
| 29 | **Cut "bonus"** — both kids asked what it means |
| 30 | **Fan SFX much louder**; better train-entry and engine-start sounds |
| 31 | **Cut "मेरा horn भी तुमसे सुर सीख रहा है"** — both kids |
| 32 | **The meow still did not land** even with the new sound — needs rethinking, not re-generating |
| 33 | **Water honesty check** — if WATER is tapped instantly, once: "अरे! तुम गए ही नहीं!" |
| 34 | **Fewer, more recognisable cards**; better card images |
| 35 | **Chuku's voice stays** — it gets a laugh on its own |
| 36 | Investigate the long pauses after "छुक-छुक… चलो!" and after "Robot की battery रुक गई!" |
| 37 | **Un-park resuming** — a kid switched away and nothing resumed |

## Jungle Rescue — the decision

| # | decision |
|---|---|
| 38 | **Rewrite from scratch**, cost no object, new cards and effects allowed |
| 39 | **Cards 10 → 9**, all already printed. FIRST AID and BLANKET dropped — the "doctor" bit was not landing and the blanket scene was flat |
| 40 | **New scene: मेंढक जी की हिचकी**, using the CLAP card — physical, noisy, rhyming, where the story used to sag |
| 41 | **The giraffe scene rebuilt** so the ladder is the punchline: she speaks slowly because her voice must travel up, and Coco climbs it all to reach her knee |
| 42 | **Two repeated devices added**: the rally "जंगल बचाओ टीम… तैयार?!" and the mess cry "गंदा! गंदा! बहुत गंदा!" |
| 43 | **"खींचो, खींचो… दिमाग़ की बत्ती गुल!"** — replaces "pull, pull, pull", which got no laugh |
| 44 | **Kept because they laughed**: the trampoline line, the elephant's trumpet, the mud, Coco falling |
| 45 | **Cut**: "Fair point.", "मैं Elephant हूँ.", "एक छोटा bite मेरे लिए", "निकालो और ऊपर", the water wink, the whole first-aid bit |
| 46 | **An SFX under the jeep at the very start** — the opening runs on narration alone |

---

## Where each thing lives

`STORY_CRAFT.md` 21–28 · `feedback/toy-town-v2.md` 29–37 ·
`scripts/jungle-rescue-v2.md` 38–46 · `AUDIO_STANDARD.md` 15 ·
`TASKS.md` everything not yet built · `parked/README.md` 12
