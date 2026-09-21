# Chuku & the Toy Town Express — feedback

`docs/toy-town` · Hinglish · the original, deliberately left unchanged

Changes from this feedback went into **`docs/toy-town-v2`**, which runs beside
it so the two can be compared. This file records what was noticed here; see
`feedback/toy-town-v2.md` for how the retuned copy performs.

---

## 2026-09-21 · played with both kids

Overall: less engaging than Jungle Rescue. Some laughs, some lost interest.

### Audio levels

| # | what | status |
|---|---|---|
| 1 | SFX across the story too low | **fixed in v2** — 38 effects levelled to −20 dB; they spanned 36 dB. Blanket 0.55 attenuation removed |
| 2 | Clap louder | **fixed in v2** |
| 3 | Train SFX louder | **fixed in v2** |
| 4 | Key / engine-start unclear | **level fixed in v2** — `key_turn` was 20 dB under the voice, now ~8 dB more body. May still need new audio if the sound itself is wrong |
| 5 | Dance music low, rhythm not building | **fixed in v2** — beat no longer ducks to nothing; beatless time 43.9s → 24.2s |
| 6 | Jungle Rescue has more energy | **mostly fixed in v2** — ~3 dB; master gain 0.8 → 1.0. Last ~1.2 dB needs the 168 narration files renormalised |

### Sound effects that are wrong, not just quiet

| # | what | status |
|---|---|---|
| 7 | Meow sounds like a train | **needs new audio** — `horn_meow` and `horn_train_soft` measure within ~1 dB of each other in every band below 1.2 kHz, and neither has a train horn's low end. The "train or cat?" joke has no contrast to land on |
| 8 | Train starting / key turning don't read | **needs new audio** — level is fixed; the sounds may still not say "key turns → engine catches" |

### Jokes

All audited against `STORY_CRAFT.md` §3. Replacements written in
`scripts/toy-town-v2.md`.

| # | what | status |
|---|---|---|
| 9 | "तुम train हो या बिल्ली?" | **blocked on 7** — the joke is fine, the sounds are identical |
| 10 | "हवा थोड़ी-सी, हाथ की exercise ज़्यादा" | **rewritten, needs recording** — irony |
| 11 | "मैं तुम्हारी seat सँभाल के रखता हूँ" | **cut in v2** — and nothing is said after the water instruction now |
| 12 | "खर्र्र… biscuit… खर्र्र…" / "ये signal की आवाज़ है?" | **rewritten, needs recording** — replaced with "सोते-सोते biscuit खा रहा है!", which was liked |
| 13 | "पटरी की softness check" / "तो result क्या आया?" | **rewritten, needs recording** — testing-and-reporting framing |
| 14 | "तभी मेरी टोपी से आलू पराठे की खुशबू" | **rewritten, needs recording** — delayed inference |
| 15 | "मूँछ जी! पहले अपना ticket दिखाइए!" | **rewritten, needs recording** — talking to the moustache stays, the ticket goes |
| 16 | "मेरी battery तो sandwich से चलती है!" | **rewritten, needs recording** — metaphor |

### Structure

| # | what | status |
|---|---|---|
| 17 | 59 seconds before a child can touch a card | **fixed in v2** — 40s, no line cut; the pocket gag moved to after the KEY card |
| 18 | Opening should give the child a job: "क्या तुम मेरे Captain बनोगे?" | **written, needs recording** — `scripts/toy-town-v2.md` §2 |
| 19 | No acknowledgement after a correct card | **open** — at stop 0 and stop 3 nothing is said at all. Five acknowledgements and two praises drafted in `ELEVENLABS_BRIEF.md` §3b. **Not in v2** |
| 20 | Driver Uncle's voice reads kiddish | **open** — 13 lines, all to be re-recorded together with one new adult voice |
| 21 | "तुमने बिजली भी बचाई!" ends the last stop | **open** — saving electricity is a civic idea a four-year-old has no hook for, and it is the last thing before the finale |
