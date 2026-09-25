# Production mode — proposal package

**Status: proposal. Nothing in the repo was modified.** One file changes,
`docs/jungle-rescue-english/index.html`; one test is added. Written 25 Sep 2026 from
the QA report, on the file as of 11:55 (cache tag `jr-bed-6`).

## What the kids saw, and what they will see

Before: once Coco asked a question, the screen showed the wanted card's picture and
"Fuel वाला card tap करो", plus eight tappable card buttons — in reader mode too. A child
could tap ⛽ on the phone and never touch a card. "Play on screen" sat on the welcome
page, and the debug log popped up on the first scan.

After (production, the default): the welcome page has one **Start** button. During a
question the screen shows 🎧 "Coco की बात सुनो… फिर card लाओ", the progress bar, and
nothing else — no picture, no card name, no buttons. The clue is Coco's, in audio, with
hints at 8/17/28 s as before. The status line says "Waiting for a card…" instead of
"Waiting for Fuel." The log stays hidden.

The on-screen tray (all eight cards, still without saying which one) appears only when:

- the parent chose **Play on screen** — a developer-mode button now, or
- the reader check ended in **play without a reader** (same fallback Moon and Toy Town have).

## Developer mode

Reachable two ways, and remembered in the browser either way:

- laptop: **Ctrl+Shift+D** toggles it (the shortcut never reaches the scan buffer;
  keys with Ctrl/Cmd/Alt are ignored by the reader path now);
- phone: open the page with **`?dev`** (or `?dev=1`) once — it stays on across
  reloads until you open it with **`?dev=0`**.

A small line at the bottom says "Developer mode" while it is on. It shows: Play on
screen, the card tray during questions, Next cue, and the log.

## Which copy to apply

| copy | when |
|---|---|
| `modified/docs/jungle-rescue-english/index.html` | you have **not** applied `docs/claude/card-registry/` |
| `modified+registry/docs/jungle-rescue-english/index.html` | you **have** applied the card-registry package — this is both changes in one file |

`preview/index.html` links a side-by-side diff of each. Then:

```
cp docs/claude/production-mode/new/qa_modes_english.js .
node qa_modes_english.js          # expect ALL PASS (needs playwright, like the other qa_*.js)
node qa_allgames.js               # unchanged
```

## Verified before handing over

- `node qa_modes_english.js`: 33/33 on `modified/`, and again on `modified+registry/`
  (with `node qa_registry.js` 26/26 on that one). Covers: production shows Start only,
  tray and wanted card never appear in reader mode, log hidden after a scan, a wedge
  scan still reaches the game, Ctrl+Shift+D on and off without leaking into the scan
  buffer, `?dev` / `?dev=0` remembered across reloads, Play on screen shows the tray
  and a tap advances the story, "play without a reader" turns the tray on without
  turning developer mode on.
- The full-story browser run from the QA report still reaches Mission complete on the
  modified file.

## Not changed here

Reset / Pause, the missing preload, the spec divergences, and the iOS volume
question are separate items from the QA report.
