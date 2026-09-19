# Parked: the Carry on screens

Taken out of all five games on 2026-09-19. Both modules are still in `docs/`,
unwired — nothing loads them, `check_games.py` no longer asks for them, and
`qa_allgames.js` no longer tests them. This folder holds the suites that do.

## Why they came out

**`docs/interrupt-guard.js`** — the ⏸️ *Ready when you are / Carry on* screen.
It decides the audio has died by asking whether the AudioContext is running.
A grown-up pressing **Pause** suspends the context on purpose, which from
there is indistinguishable from a phone call killing it. So Pause was covered
by a Carry on screen within 1.5 seconds, and the only visible button replayed
the whole stop from its first line. Pausing to answer a question cost you the
scene.

**`docs/progress.js`** — the 🔖 *Carry on where you stopped?* screen on the
next page load. Sound in itself, but it is the same question asked in a second
place with a second set of rules, and answering "am I resuming?" twice is how
the first one got it wrong. Both come back together or not at all.

## What was already understood when it was parked

A half-finished fix sits in this folder's suites. It is worth reading before
rebuilding, because the diagnosis is the hard part and it is done.

* **A suspended context is not a dead one.** Every clip is an
  `AudioBufferSourceNode` and every wait is measured in `ctx.currentTime`,
  both of which freeze while suspended. `resume()` carries on mid-sentence
  with nothing lost. Only a **closed** context has really lost the clip: its
  source nodes are gone and `onended` will never fire. Replaying the stop is
  right only in that case, and the two were being treated the same.
* **A deliberate pause must be invisible to any of this.** Whatever replaces
  `interrupt-guard.js` needs to know the difference, and the game is the only
  thing that knows it — it has to be asked.
* **A discarded tab is a third case again**, and the only one the page cannot
  see happen. Android throws a backgrounded tab away — at 13-15 MB these
  pages go early — and it returns as a fresh load, so nothing in memory
  survives and no event announces it. The step has to already be on disk.
  `progress.js` writes it on `visibilitychange` and `pagehide`, which is all
  the warning there is.
* **Never resume silently.** A child who finished and wants it again must not
  be dropped at stop eight. Ask.

So there are three states, not one: *paused on purpose*, *interrupted but
recoverable*, *gone*. One screen that guesses between them is what failed.

## The suites

```
node parked/qa_progress.js   # a discarded tab comes back on the right step
node parked/qa_interrupt.js  # a phone call does not hang the story
node parked/qa_pause.js      # Pause is not a phone call  <- the bug, pinned down
```

They will fail until the modules are wired back in. `qa_pause.js` is the one
to make pass first: it models the real state machine (running / suspended /
closed) rather than stubbing it away, and it asserts what went wrong — no
Carry on screen over the Pause screen, and no replaying a stop whose audio was
only suspended.
