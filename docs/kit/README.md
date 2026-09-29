# docs/kit — stories as text, one shared engine

Everything new lives in this folder. The old games in `docs/<slug>/` are not
touched by anything here; the only thing the kit reads from outside itself is
`cards.json` at the repo root (cards are global, by decision).

```
docs/kit/
  engine/      kahani.js + kahani.css — the story-free player; its own copies of
               scan-guard.js, reader-check.js, story-intro.js, card-registry.js
  tools/       build.py, compile.py, check.py, library.py, names.py, generate.py, FORMAT.md, UNDER5_REVIEW.md
  library/     shared sounds and lines + manifest.json with searchable descriptions
  stories/     one folder per story: story.txt, variants/*.txt (+ story.json, clips.json after a build)
  games/       built output, one folder per story: index.html, story.json, audio/
  qa/          qa_parity.js, qa_engine.js — both run in a real headless Chromium
```

Deployed, a kit game is at `/kit/games/<slug>/` — e.g.
`taptales.netlify.app/kit/games/jungle-rescue-english/`, beside the old games.

## The loop for a new story

```
cp -r docs/kit/stories/_template docs/kit/stories/<slug>     # write story.txt (tools/FORMAT.md)
python3 docs/kit/tools/build.py <slug> --check               # lint: cards in cards.json, praise + hints
                                                             # after every ask, no hardcoded counts
python3 docs/kit/tools/compile.py docs/kit/stories/<slug>/story.txt --clips
                                                             # what to record: id, speaker, direction, text
# audio lands in docs/kit/games/<slug>/audio/ with its manifest.json (check_audio.py as usual)
python3 docs/kit/tools/build.py <slug>                       # -> docs/kit/games/<slug>/
```

Lines pinned to an existing clip (`@JR_036`) cost nothing. A variant is a
five-line file in `stories/<slug>/variants/` and costs no audio at all; open the
game with `?v=<name>` or pick it from the developer-mode dropdown (Ctrl+Shift+D on
a laptop, `?dev` on the phone).

## Jungle Rescue English — the proof

`stories/jungle-rescue-english/story.txt` is the `ios-volume-fix-standalone`
build (ios-standalone-13) rewritten as a script, every line pinned to its
existing clip. `games/jungle-rescue-english/audio/` is a copy of that build's
188 clips and manifest (14 MB).

`qa/qa_parity.js` opens the original and the kit game side by side, plays both
the same way (every card, a wrong card on ROPE, a 9 s silence on FIRST AID so a
hint fires, the fuel-overflow gag) and records every `HTMLMediaElement.play()`:
**161 plays, identical sequence, constant ~0.5 s start offset, no drift.**
`qa/qa_engine.js`: 24 checks — production mode (no tray, card never named), the
dev toggle, hint ladder, wrong-card rotation, leading-zero UIDs, pause, jump to
scene with the right progress and bed, each variant dropping exactly what it says.

Not yet done: listening on the iPhone. Same clips, same order, same audio code —
but nothing is called done until it has been heard on a phone speaker from two
metres.

Variants shipped: `praise-after-effort`, `no-jokes`, `half-jokes`, `fewer-taps`
(the elephant eats in two bites), `fast-hints`.

## Find & Tap — the second story

`stories/find-and-tap/story.txt`: the same fifteen human-voice clips
(`audio_human/`) and background loop, now in `games/find-and-tap/audio/` with a
manifest. The eight asks sit in a `shuffle:` block so the order is fresh every
game, and `use praise` pastes a `one of:` block that picks one of the two praise
lines. Two things changed on purpose: a card that does not come is asked for
again at 8 / 17 / 28 s (the old game had a Replay button), and wrong-card lines
rotate rather than pick at random. `qa/qa_findtap.js` (11 checks) plays a whole
game with a pinned random. Variant: `colours-only`.

Its eight cards (RED … STAR) must be in `cards.json` — the old game kept them in
its own storage on the phone. `build.py` refreshes the seed block of
`engine/card-registry.js` from `cards.json` on every build, so once they are
added there every kit game knows them.

## The shared library — `library/`

Sounds and lines every story can use, with descriptions you can search before
opening ElevenLabs: `python3 docs/kit/tools/library.py find soft chime`. A script
uses one by name (`sfx ting`, `bed jungle_day`, `COCO @lib:great_job_en: …`) and
the engine plays it from `docs/kit/library/`, so a chime or a "Great job!"
recorded once serves every story and is prefetched only by the stories that use
it. `library.py promote <slug> <cue> --id … --desc …` lifts a clip out of a game
into the library, keeping its measured loudness. Seeded with 13: the correct
chime, the wrong-card boing, the day and night jungle beds, the clap, the party
whistle, the dance loop, Find & Tap's four English praise / retry lines and its
soft background loop, and `tap` — a synthetic soft tick for early taps (replace
it with a nicer one whenever).

Early taps (LEARNINGS 9–10) are now handled by the engine: a card tapped while
Coco is still talking gets the tap sound at once and is remembered; if it is
the card the next question wants, the question is answered the moment it arms
(the prompt is skipped); a wrong one is never punished and never advances the
story. `tap sound: @lib:tap` in a script's header turns the sound on.

## Coco की Night Drive — a story with no new audio

`stories/night-drive/story.txt`: four cards (fuel, flashlight, water, music),
about three and a half minutes plus the water break, and **every one of its 60
clips is `@lib:…`** — the reusable Jungle Rescue lines were lifted into the
library first (`library.py promote`, 57 of them), then the story was written
from the library alone. Its game folder has an empty audio manifest; the engine
plays everything from `library/`. `?v=short` drops the second dance round and
the jokes. This is the template for "do we already have it?": write the line,
run `compile.py … --suggest`, and only what has no match goes to ElevenLabs.

`qa/qa_play.js <slug> [variant]` plays any kit story straight through and
prints the clips in order plus anything the engine logged as missing — run it
on every new story and every variant before the phone.

## The under-5 review, applied (29 Sep)

The review in the project (`claude/under5-review-jungle-rescue-english.md`) is
in the script: the cards are asked for in the child's own words (पेट्रोल, रस्सी,
दवाई का डब्बा, टॉर्च, music/गाना — `say=` on each card line, which the compiler
now checks in the last hint and the praise); the fuel scene teaches before it
asks and the last hint describes the picture; the parrot scene says पंख and
प्यास; the lion scene asks for the torch right after the lion speaks, with a
physical tail joke (Coco grabs the tail in the dark) instead of the misheard
one; "overflow" is "छलक जाएगा". 25 lines re-said under new ids (`JR_010b`…),
the old clips untouched in the folder. `generate.py jungle-rescue-english`
makes them.

`qa_parity.js` now builds its reference from `qa/parity_script.txt` — the kit
script as first committed, before the review — into `games/_parity/` (ignored
by git), so the cue-for-cue proof against the original stays alive while the
real script moves on.

## The child's name

Story lines say "Captain" and are recorded once; the child's name comes in
short independent lines (`{name}` in the script — praise after every card,
"{name}, देखो!" before a reveal, the intro), at least every 60 s. Each such line
is recorded once with "Captain" (`names.py captain`) and once per child
(`names.py add`, `names.py generate`); the engine swaps the clips for the play
when a name is typed on the welcome page or given as `?name=`, and falls back to
Captain otherwise. Nothing is stored on the phone. `library/names/README.md` is
the checklist; `qa/qa_names.js` proves it. Jungle Rescue English carries 9 name
lines (11 praise points, 4 attention lines, intro + title) and the
gender-neutral re-takes JR_003b / JR_143b; `?v=classic` is the story without
them, which is what `qa_parity.js` now compares against the original.

`tools/generate.py <slug>` is the ElevenLabs step for any other line a story
still needs; `library/voices.json` holds the approved voice and settings per
speaker so new clips match the old.

## Definition of done — `tools/check.py <slug>`

One command runs everything a machine can check before a child hears a story:
the script lint (cards, praise, hints, the child's word, the three name rules,
the under-5 rules from `library/under5-words.json`: forbidden words, line and
prompt length, the first ask names its card, ≤ 60 s of listening before an
ask, something landing every 30 s); every clip exists and fits its hold; every
speech clip at −16 LUFS ±1.5 and ≤ −1.5 dBTP with all speech within 3 dB; and
every bed the story plays under speech ≥ 20 dB below the voice in all seven
bands through a phone-speaker simulation, at the volume the script plays it.
`--quick` trusts the manifest's measurements; `--play` adds a browser
play-through. Exit 0 only when nothing failed. About 8 s for a story.

What a machine can't judge — is the concept lived, is the ask recognition or a
riddle, can a four-year-old *see* the joke — is `tools/UNDER5_REVIEW.md`: a
checklist to run by hand or by any AI thread against the script, answered
puzzle by puzzle. Then the phone, speaker only, two metres.

First real run (Night Drive, 29 Sep): masking passes in every band for both
beds; four library clips measure 1.5–3 dB quiet (hint_torch_1, hint_music_1,
hint_music_3, dance_elephant) and the spread is 3.9 dB — inherited from the
Jungle Rescue clips they came from.

## Running the checks

```
cd docs/kit/qa && node qa_engine.js        # ~1 minute
cd docs/kit/qa && node qa_parity.js        # ~3 minutes, needs the old standalone build in docs/
cd docs/kit/qa && node qa_findtap.js       # ~1 minute
cd docs/kit/qa && node qa_play.js night-drive [short]
cd docs/kit/qa && node qa_names.js         # needs a pack for "rida" (KAHANI_FAKE_TTS=1 names.py generate rida for a silent one)
```

Both need `playwright` on the path (`npm i -g playwright`, Chromium installed).
They serve `docs/` on a local port and use the real audio, so the parity run
takes as long as the story does with silent taps.

## Not in here yet

- `tts/generate.py` reading `stories/<slug>/clips.json` directly
- a `kahani` row in `check_games.py` (kit games load the shared runtime from
  `docs/kit/engine/`, which that gate does not know about)
- resuming stays parked, as in the standalone
- the child's name is a build option (per-name clips), not a runtime dial
- the other stories: `moon`, `banana-rescue`, `jungle-rescue`, then
  `jungle-rescue-hinglish` last (the benchmark); `toy-town-v2` as a variant of
  `toy-town` instead of a folder
