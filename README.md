# Find & Tap — project files

This is the "Find & Tap" RFID scavenger-hunt game built for a 4-year-old:
a phone-down, ears-only game where a voice asks for a color or shape and
the kid taps the matching RFID card on a USB-C keyboard-emulation reader.

## What to actually use

**`find-and-tap.html`** is the whole game — a single self-contained HTML
file with all narration audio and background music embedded inside it.
Just open it in a browser (double-click it, or upload it to any static
host). No build step, no server, no dependencies.

This is the same file published as the "Find & Tap" Claude Artifact.

## The rest (source / how it was built)

- `find-and-tap.src.html` — the page source *before* the audio is baked
  in (has `/*__AUDIO_DATA_JSON__*/` and `/*__BG_MUSIC_B64__*/`
  placeholders). Edit this file to change game logic, wording, colors,
  or layout.
- `build.py` — reads `voice_manifest.json` + `audio/bg_loop.mp3`, embeds
  them as base64 data URIs into `find-and-tap.src.html`, and writes the
  final `find-and-tap.html`. Run `python3 build.py` after changing
  either the source or the audio.
- `voice_manifest.json` — the 15 narration clips (human-recorded, sent
  by the user) as base64 + duration, keyed by line name (`intro`,
  `card_red`, `correct_1`, etc.). This is what `build.py` embeds.
- `audio_human/` — the actual voice recordings (normalized, mono,
  24kHz, mp3), the source `voice_manifest.json` is built from.
- `audio/bg_loop.mp3` (+ `gen_music.py`) — the procedurally generated
  background music loop (not a licensed track — synthesized from
  scratch, so no licensing concerns).
- `qa.js` — a Playwright script that drives the game end-to-end
  (mapping cards, playing all 8, checking persistence) to catch
  regressions before publishing. Run with `node qa.js` (needs
  `npm install playwright` and a Chromium binary).

## If you want a human voice for a missing line

`correct_3` ("Woohoo! You did it!") was never recorded, so the game
currently rotates only between `correct_1` and `correct_2`. To add it:
record/generate that line, drop it in as `audio_human/correct_3.mp3`,
add it to `voice_manifest.json` (or just re-run
`gen_manifest_human.py` if you add the file there), re-run
`build.py`, and add `"correct_3"` back into the `CORRECT_LINES` array
in the page's `<script>`.

## Card mapping

Card-to-tag mapping is stored in the browser's local storage on
whichever phone runs the game (not baked into this file) — that's
done once through the game's own Setup screen after opening it.
