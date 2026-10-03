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
   `python3 docs/kit/tools/names.py captain`
   Shared lines land in `library/voice/`, story ones in
   `games/<slug>/audio/names-captain/`, levelled and measured. Add `--dry-run`
   to see what it would spend first.
4. `python3 docs/kit/tools/build.py <slug>`, then listen on the phone with no
   name typed.
5. Every child who already has a pack now needs the new line:
   `names.py generate --all` — only the new line is spent per child, the rest
   is cached.

## Every time new children come — one prompt, one run

The ElevenLabs key is already exported in the Mac's Terminal profile, so no
command here carries it. If it is missing, the run says so before spending
anything.

1. **Prompt Claude** with the names (one or ten): *"Add name packs: Rida,
   Aarav, …"*. Claude checks `names.py list`, picks the Devanagari the way each
   name is **said** (not the certificate spelling) plus the aliases a parent
   might type, registers them straight away (`names.py add` — free, and easy to
   fix), and replies with a table of spellings, the `--dry-run` cost, and the
   one command. Matching ignores case, spaces, dots and hyphens; the tool
   refuses an alias that already points at another child.
2. **Read the table.** Wrong spelling → say so, Claude fixes `names.json`
   (free). Right → run, in Terminal on the Mac:
   ```
   cd ~/Documents/Game/rfidgame && python3 docs/kit/tools/names.py generate --all
   ```
   It makes every registered child's missing clips (finished ones are cached
   and cost nothing), levels and measures them, checks every pack, and ends
   with one line per child — clips, level, characters spent, test link — and
   `✓ ALL PACKS COMPLETE`. A failure mid-way (network, quota): run the same
   command again; it resumes for free.
3. **Say "done".** Claude runs `names.py check --all` and commits the packs.
4. Listen to each child's clips on a phone speaker before the child does. The
   name is the part ElevenLabs is most likely to mangle; if one is wrong, fix
   the Devanagari (`names.json`), delete that child's `raw/*.request.json`, and
   run step 2 again.
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

- Per child today: 26 clips (every `{name}` line in every story), about 1,150–1,200
  characters including the performance tags ElevenLabs is sent — one credit per
  character. `generate --all --dry-run` gives the exact total. Ten children ≈ 12,000.
- Never put the key in the repo, a script or a chat. It lives in the Terminal
  environment only (exported in the shell profile), so commands never include it.
- Devanagari spelling decides pronunciation. Keep a note beside odd names.
