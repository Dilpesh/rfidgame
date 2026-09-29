# The child's name — the process

Coco says the child's name only in short independent lines (the name rules in
`tools/FORMAT.md`). Every such line exists twice: once said with **"Captain"**
— the version every child hears when there is no pack — and once **per child**.
Story lines never change per child. This file is the checklist; `tools/names.py`
does the work.

## Once, when a story gains or changes a `{name}` line

1. Write the line in the script as its own short sentence:
   `COCO [warm] @lib:praise_amazing #praise: Amazing, {name}!`
   Shared lines (praise, "देखो!", the title) are `@lib:…`; a story-specific
   one (the intro) is a normal cue. `build.py <slug> --check` tells you if the
   line breaks a rule.
2. See what's missing: `python3 docs/kit/tools/names.py lines`
   (– means no Captain clip yet).
3. Make the Captain versions — in a Terminal on the Mac, where the key lives:
   `ELEVENLABS_API_KEY=… python3 docs/kit/tools/names.py captain`
   Shared lines land in `library/voice/`, story ones in
   `games/<slug>/audio/names-captain/`, levelled and measured. Add `--dry-run`
   to see what it would spend first.
4. `python3 docs/kit/tools/build.py <slug>`, then listen on the phone with no
   name typed.
5. Every child who already has a pack now needs the new line:
   `names.py generate <slug>` for each — only the new line is spent, the rest
   is cached.

## Every time a new child comes

1. Register the name. The Devanagari is what ElevenLabs is given — spell it the
   way it is **said**, not the way it is written on a certificate:
   `python3 docs/kit/tools/names.py add "Rida" --hindi रिदा --alias Ridha,Reeda`
   Aliases are what a parent might type; matching ignores case, spaces, dots
   and hyphens. The tool refuses an alias that already points at another child.
2. Generate (Terminal on the Mac, key in the environment; `--dry-run` first):
   `ELEVENLABS_API_KEY=… python3 docs/kit/tools/names.py generate rida`
   About 290 characters per child today (9 clips). Clips go to
   `library/names/rida/` with a manifest; raw API responses are cached beside
   their request, so a re-run costs nothing for unchanged lines.
3. `python3 docs/kit/tools/names.py check rida` — every line has a clip and
   measures within the standard (−16 LUFS ±1.5, peak ≤ −1.5 dBTP).
4. Listen to all nine on a phone speaker before a child does. The name is the
   part ElevenLabs is most likely to mangle; if one is wrong, fix the Devanagari
   (`names.json`), delete that clip's `raw/*.request.json`, generate again.
5. Play: type the name on the welcome page (or open with `?name=Rida`). The
   status line says "Playing for Rida"; an unknown name says so and plays as
   Captain. Nothing is stored on the phone; the name is typed every time.

`python3 docs/kit/tools/names.py list` shows every child and how complete
their pack is. `qa/qa_names.js` proves the wiring.

## What a pack is

```
library/names/
  names.json          the register: slug, display, devanagari, aliases
  index.json          generated: typed name → slug (the player reads this)
  rida/
    manifest.json     one entry per name line, keyed like the script cue
                      ("praise_amazing", "jungle-rescue-english:JR_003b")
    praise_amazing.mp3 … raw/
```

The engine loads the index at Start, finds the pack, and for this play only
swaps each `{name}` cue's clip for the child's. A story that gains a new name
line tomorrow simply has one more entry to generate.

## Costs and limits

- Per child: 9 clips, ~290 characters, ~15 s of audio — one ElevenLabs credit
  per character.
- Never put the key in the repo, a script or a chat. It lives in the Terminal
  environment only.
- Devanagari spelling decides pronunciation. Keep a note beside odd names.
