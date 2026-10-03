# Bobo की Birthday Party — kit script (2 Oct 2026, evening)

`story.txt` is Dilpesh's finalised script, line for line, with only the eight changes he approved
on 2 Oct (listed at the top of story.txt). Nothing in the repo was changed; everything new is in
this folder. `script.md` is the same script rendered for reading (`python3 render_script.py`
regenerates it after any edit of story.txt).

Compile-checked on a scratch mirror with the three new cards present: **5 scenes, 65 clips —
14 from the library, 50 lines to generate, 15 sounds to find (8 already in the library).**
Seven lint warnings, all of them his decisions: करोगे / गाओगे (gendered, kept), the name inside
two long sentences (kept), two of his own lines over 25 words, and the riddle first ask.

## To apply

```
cd ~/Documents/Game/rfidgame
# 1. cards: paste CAKE, CANDLE, PARTYCAP from claude/cards-additions.json into cards.json;
#    relabel MUSIC "Speaker / Music" and add "bobo-birthday": "SPEAKER" to its games; fill uids
python3 sync_cards.py
# 2. script
cp docs/kit/stories/bobo-birthday/claude/story.txt docs/kit/stories/bobo-birthday/story.txt
python3 docs/kit/tools/build.py bobo-birthday --check
# 3. audio (ElevenLabs key in the Terminal on the Mac)
#    ORDER MATTERS: sounds first. Clip ids are numbered by position, and a sound that is not in the
#    library yet takes a number — once it is added, every later id shifts by one. (Bobo hit this on 2 Oct:
#    43 clips were generated before the sounds existed; the manifest was re-keyed by text, old keys kept.)
ELEVENLABS_API_KEY=… python3 docs/kit/tools/sounds.py bobo-birthday    # the 8 sounds (ElevenLabs sound-generation → library)
ELEVENLABS_API_KEY=… python3 docs/kit/tools/names.py captain          # the 6 name lines, Captain version
ELEVENLABS_API_KEY=… python3 docs/kit/tools/generate.py bobo-birthday  # the other 37 lines
python3 docs/kit/tools/build.py bobo-birthday
python3 check_audio.py docs/kit/games/bobo-birthday
# 4. phone, speaker only, screen down, two metres → kids → feedback/bobo-birthday.md
```

## The name — where it is said, and what it costs per child

Six lines carry the child's name (fallback "Captain"): the intro, "पर पता है {name}?",
"Make a wish {name}… अब गहरी साँस लो…", "Let's DANCE, {name}!", "{name}, clap with me!",
"Thank you so much, {name}, for helping me plan Bobo's birthday!" — plus the four praise lines,
which every child pack already has. Where the name sentence sat inside a longer speech it is its
own line, so only that sentence is per-child; the words are unchanged.

**319 characters per child** (`names.py generate <child>`), about ₹5–6 at ElevenLabs' Creator
rate ($22 per 100k characters) — effectively nothing; the Captain versions are the same 319
characters once. Praise lines: 0 new characters.

## Praise

"Praise every time" for this story, by decision: `use praise` after each of the five acks, from the
library pool (Amazing / Good job / Excellent work / You are absolutely right, {name}!). The
"praise only when the child solved it alone" version is parked as a readable draft in
`drafts/praise-only-when-solved-alone.txt` — it needs an engine + compiler addition, so it is not
built; move it into story.txt only once that exists and he likes it.

## Things to know

- **Hints** are at the standard 8 / 17 / 28 s; after the third the engine is silent (repeating the
  last hint would be an engine change affecting every story — not done).
- **Sounds (8 new)** are generated, not hunted: `tools/sounds.py <slug>` (new, general — the Gulbul
  `gen_sfx.py` made reusable) reads the prompts from `stories/bobo-birthday/sounds.json`, calls
  ElevenLabs sound-generation, levels each to −23 LUFS (−21 for cap_flies_off, the joke) and adds it
  to the library under the name the script uses. `--suggest` first shows library clips that may
  already fit; `--dry-run` shows the prompts. A later story with well-named sounds needs no
  sounds.json at all. From the library: tap, magic_sparkle, party_whistle, dance_loop, music_end_flourish,
  bg_soft_loop (the "soft, happy background rhythm" under the song, at 16 %), clap, boing.
- **Dance:** `dance_loop` (20 s) with "Let's DANCE…", "Hands up in the air!", "Spin around! Keep
  moving!" ducked over it, as in the draft.
- **The song.** Two lines are directed "[singing to the Happy Birthday tune]". ElevenLabs v3 may
  chant rather than sing — fine for the kids; if a line comes out flat, retry once with
  `[singing]` at the front of the text. "Happy Birthday to You" is public domain.
- **Card naming test before printing:** hold up CAKE, CANDLE, PARTYCAP and the new Speaker print and
  ask "ये क्या है?" — `say=` has my guesses (cake / candle / cap|टोपी / speaker|music).
- **The physical cap prop** stays, as in the draft: a real paper birthday cap on the table.
- Only COCO speaks. `voices-additions.json` is empty on purpose.
