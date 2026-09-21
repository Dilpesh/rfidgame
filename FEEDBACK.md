# Feedback from playing with the kids

Jot a line here after a session — one bullet, no formatting needed, and don't
worry about whether it's an audio problem or a script problem. Working out
which is my job. What helps most is the exact moment ("the meow", "after the
water instruction") and what you saw them do, not just what you thought.

Status: **open** · **fixed** · **needs new audio** (costs ElevenLabs credits)
· **won't fix** (with a reason)

---

## Session — 2026-09-21 · Toy Town + Jungle Rescue, both kids

Overall: Jungle Rescue more engaging. Ups and downs in Toy Town — some laughs,
some lost interest.

### Audio levels

| | what | status |
|---|---|---|
| 1 | SFX across the story too low | **fixed** — 38 effects levelled to −20 dB; they spanned 36 dB. Blanket 0.55 attenuation removed |
| 2 | Clap louder | **fixed** — in the same pass |
| 3 | Train SFX louder | **fixed** — same |
| 4 | Key / engine-start unclear | **fixed (level)** — key_turn was 20 dB under the voice, now ~8 dB louder with compression. **May still need new audio** if it's the sound itself, not the level |
| 5 | Dance music low, rhythm not building | **fixed** — beat no longer ducks to nothing; beatless time in the dance 43.9s → 24.2s |
| 6 | Jungle Rescue has more energy | **mostly fixed** — it was ~3 dB; master gain 0.8 → 1.0. Last ~1.2 dB needs the 168 narration files renormalised |

### Sound effects that are wrong, not just quiet

| | what | status |
|---|---|---|
| 7 | Meow sounds like a train | **needs new audio** — confirmed: `horn_meow` and `horn_train_soft` are within ~1 dB of each other in every band below 1.2 kHz, and neither has a train horn's low end. They are effectively the same sound, so the "train or cat?" joke has no contrast to land on |
| 8 | Train starting / key turning don't read | **needs new audio** — see 4; the level is fixed, the sounds may still not say "key turns → engine catches" |

### Jokes not landing

| | what | status |
|---|---|---|
| 9 | "तुम train हो या बिल्ली?" | blocked on 7 — the joke is fine, the sounds are identical |
| 10 | "हवा थोड़ी कम है, हाथ की exercise ज़्यादा" (fan) | **open** — needs rewriting |
| 11 | "मैं तुम्हारी seat सँभाल के रखता हूँ" (water) | **open** — and: say nothing after sending them for water, just wait |
| 12 | "खर्र्र… biscuit… खर्र्र…" / "ये signal की आवाज़ है?" (Teddy) | **open** — needs rewriting |

### Structure

| | what | status |
|---|---|---|
| 13 | Opening should give the child a job: Chuku introduces herself, the driver needs help, "Captain, will you help?" — then they board | **open** |
| 14 | Acknowledge the child after every card? | **open** — see below |
| 15 | Driver's voice | **open** — needs a decision on what to change it to |

---

## Standing questions

**Acknowledgement after every card.** Recommendation: acknowledge every time,
praise sparingly. An acknowledgement is the world changing because of them
("Teddy woke up!", "the elephant is free!"); praise is about them ("shabaash,
very good"). Jungle Rescue is nearly all the first kind, which is likely why it
doesn't wear out. Generic praise on every one of nine stops stops being heard,
costs time — the thing they lost patience with — and shifts attention from the
story to being approved of. So: a ting plus an in-world consequence every time,
and explicit praise kept for the ones that cost real effort (the water trip, the
dance, anything found only after hints). That gives the intensity-by-task
scaling without it becoming wallpaper.
