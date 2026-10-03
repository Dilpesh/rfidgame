# Gulbul Pandey — kit script proposal (1 Oct 2026)

`story.txt` here is the v2 script converted to the kit format with all 20 decisions from
`claude/review-gulbul-pandey.md` (project doc) applied. Nothing in the repo was changed;
`../story.txt` is still the untouched template copy.

## To apply

```
cd ~/Documents/Game/rfidgame
cp docs/kit/stories/gulbul-pandey/claude/story.txt docs/kit/stories/gulbul-pandey/story.txt
# add the five cards from claude/cards-additions.json to cards.json (uids from the physical cards), then:
python3 sync_cards.py
python3 docs/kit/tools/build.py gulbul-pandey --check
```

Checked on a scratch mirror with those five cards present: compiles — 6 scenes, 122 clips
(98 lines to generate, 24 sounds to find, 6 from the library). Two warnings remain on purpose:

- `line 45: gendered verb (बनोगे)` — "क्या तुम हमारे Detective बनोगे?" kept by decision (pt 3).
- `about 60 s of listening before the SNACK ask` — estimated from word counts; 4 s of it is the
  clap (doing, not listening). Re-read once real clip lengths exist; if it is over, the second
  Gadbad exchange (after the Elephant ack) is the cut.

## Three places the kit cannot do what the script said — adapted, flagged

1. **Bike as a wrong card (pt 9).** The engine has one global wrong-card rotation and no
   per-ask response to a specific card. Adapted: the Inspector tries the bike himself
   (wobble → thud → "हवलदार जी तो गिर गए! धड़ाम!"), then asks for the gaadi. Same joke, no
   BIKE card. The card-triggered version needs `wrong BIKE:` blocks inside `ask` (engine +
   compiler change → a `docs/claude/<topic>/` proposal if wanted).
2. **Biscuit or Banana (pt 2 of v2).** One card per `ask`. Written as Biscuit only
   (SNACK, say=biscuit). "Either" needs `ask SNACK | BANANA` with a per-card success line.
3. **Bedroom redirect (pt 8).** No BEDROOM card; a wrong tap gets the global line and hint 1
   at 8 s is the bedroom redirect ("Bedroom में तो खाना बन रहा था…").

## Things to know

- `fallback name: Detective` (a header key compile.py already supports) makes every `{name}`
  line's fallback "…, Detective!". That is why the praise block and the two attention lines
  are **not** pinned to `@lib:` (those clips say "Captain"). `names.py captain` will
  generate the Detective versions for this story; child packs add the names as usual.
- Shared cues pinned by id so they play identically every time: `@gadbad_tag`,
  `@gadbad_fix`, `@kaun_karta` (×4), `@dog_bark`, `@dog_pant_bark`. They have no clip yet;
  `generate.py` should make them — if it refuses a pinned id, say so and I'll switch them to
  library ids.
- The name lint only gender-checks COCO/NARRATOR and `{name}` lines, so INSPECTOR story
  lines are **not** checked for -ोगे. Worth a one-line compile.py change later (a
  `child-facing speakers:` header). Everything here was read by hand; the only gendered
  line is the one kept on purpose.
- Hints are one beat each, so Munmun's "और वो ऐसी आवाज़ करता है…" before the trumpet is
  dropped; hint 2 of the Elephant ask is the trumpet alone.
- Voices in the header are suggestions: INSPECTOR=Saanu (most dialogue), MUNMUN=Munni,
  ELEPHANT=Vardan, DOG=Bholu, HAVALDAR=Jia. Bholu carries the lion EQ in voices.json —
  give DOG its own entry.
- Beds: `jungle_day @0.2` under the garden scene only. The house scenes have no bed —
  add one (room tone / clock) if the silence between lines reads as dead on the phone.
- Sounds to find (24): phone_ring, phone_beep, sparkle, brass_sting, slide_whistle_wobble,
  thud (loud end of the band — it is the joke), siren_engine, doorbell_door_creak,
  mystery_sting, elephant_snore, munch_crunch, dog_bark, dog_pant_bark,
  footsteps_cloth_rustle, discovery_chime, police_whistle_drums; from the library: tap,
  ting, boing, clap, elephant_trumpet, dance_loop.
- Before printing cards: hold up CAP, CAR, ELEPHANT, DOG, KITCHEN and ask "ये क्या है?" —
  the `say=` lists are my guesses; replace with the kids' words.

## Decisions 1 Oct (evening) and the voice audition

- Biscuit only (no banana) — done. Card words stay plain English — done (`say=` simplified).
- Dance music: the library's `dance_loop` (the 20 s freeze-dance loop already used in other stories) — no new music.
- Bike scene: **decided — option A.** The Inspector tries the bike himself (wobble → thud → "हवलदार जी तो गिर गए! धड़ाम!"), then asks for the gaadi. No BIKE card, no engine change.
- Voices (picked 1 Oct: Inspector Saanu, Munmun Jia, Dog Chintu — Voice Library aPE0uHZbwrQVPMm3ihPH, add to your voices first — Havaldar Bholu; Elephant stays Vardan): `voices-additions.json` has the four rows `library/voices.json → speakers` needs (INSPECTOR, MUNMUN, DOG,
  HAVALDAR), each pointing at an approved voice. To choose by ear first:
  `ELEVENLABS_API_KEY=… python3 docs/kit/stories/gulbul-pandey/claude/audition.py` → `claude/auditions/index.html`
  (one script line per character in each of the five approved voices, all levelled alike). `--list` prints every
  voice in the ElevenLabs library; `--voice Name=id` adds one as a candidate. Then set the `voice_id`s in
  `voices-additions.json`, paste the rows into `voices.json`, and `generate.py` can run.
