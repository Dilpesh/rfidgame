# Learnings checklist

Everything the earlier games taught us, in one list, with where each was
learned and how to verify it. **Run this against every new story before the
kids see it.**

Last audited: 19 Sep 2026. The column shows the newest story,
`docs/toy-town/` (Chuku & the Toy Town Express).

| # | Learning | Toy Town |
|---|---|---|
| 1 | Screen wake lock, re-taken on `visibilitychange`, released at the end | ✅ added |
| 2 | Background bed ≥20 dB under the narration in **every** band on a phone | ✅ fixed |
| 3 | Narration at −16 LUFS, all clips within ~3 dB, no clipping | ⚠️ 8.8 dB spread, no clipping |
| 4 | Card UIDs normalised — leading zeros, case, whitespace | ✅ added |
| 5 | A card may have several physical copies (water, torch) | ✅ added |
| 6 | Cards pre-seeded, so a fresh browser needs no teaching | ⚠️ 2 of 6 — four cards have no UID yet |
| 7 | Production mode is RFID-only; dev tools behind a shortcut | ✅ added |
| 8 | The reader's Enter must not re-fire the last-clicked button | ✅ fixed |
| 9 | A scan during narration is remembered, not dropped | ✅ added |
| 10 | Feedback within ~200 ms of every scan, always | ✅ already |
| 11 | Wrong-card lines are warm and rotate | ✅ already |
| 12 | Physical movement built into the story | ✅ already |
| 13 | Action first, card second (the water step) | ✅ already |
| 14 | Landing page links to `<slug>/index.html`, never a bare folder | ✅ |
| 15 | No hardcoded counts in UI text | ✅ |
| 16 | Printable card labels, portrait, picture-dominant | ✅ added |
| 17 | Ignore a repeat of the same UID within ~1.5 s | ✅ all five |
| 18 | Survive a phone call — one big Carry on, nothing lost | ✅ all five |
| 19 | Show the cards and the physical activities before starting | ✅ all five |

---

## The shared runtime

These are no longer things each story remembers to do. They live in `docs/`
and every story loads them:

| file | what it stops happening |
|---|---|
| `scan-guard.js` | a card left on the reader firing over and over |
| `reader-check.js` | a dead reader silently doing nothing |
| `story-intro.js` | a parent finding out mid-scene that there is jumping |

`interrupt-guard.js` and `progress.js` are **parked** — still in `docs/`, but
nothing loads them. See `parked/README.md` and learning 20.

**`python3 check_games.py` is the gate.** It fails if any story is missing any
of them. An exception has to be written down in that file, with a reason —
there is no silent pass. Run it before shipping a new story, along with
`node qa_allgames.js`, which proves the wiring actually works rather than
merely being present.

---

## 1. Screen wake lock

Kids put the phone down and listen; a long music break is plenty of time for
the screen to lock and the audio to stop. Take the lock on start, **re-take it
on `visibilitychange`** (coming back from a lock screen drops it), release it
at the end.

Needs https or localhost — it silently does nothing over `file://`.
Verify: `node qa_wakelock.js`, and `qa_modes.js` for the Hinglish build.

## 2. Masking is spectral, not level

The one that cost the most to find. A bed can be far quieter overall and still
bury the narration, because phone speakers reproduce almost nothing below
~450 Hz — where Hindi speech lives — and reproduce 3–8 kHz very well, which is
where crickets, shakers and chimes live.

**Never diagnose "background too loud" by turning the volume down.** Measure
the bands. `python3 check_audio.py docs/<story>` does it; the bar is 20 dB,
target 25–30.

Caught it twice: the moon crickets (+4.2 dB *louder* than the voice at 6–8 kHz)
and `dayAmb` in this brand-new build (−17.8 dB, failing). Both now pass.

## 3. Narration levelling

−16 LUFS integrated, peaks ≤ −1 dBFS, and every clip within about 3 dB of
every other so nobody reaches for the volume.

**loudnorm's one-pass mode is wrong for short clips.** It needs ~3 seconds to
judge a programme. Run through it, this build's 15 hint lines came out as low
as −44.7 LUFS — effectively silent — while the long lines landed perfectly.
Measure each clip, then apply a constant gain instead. `alimiter` also
auto-levels to its ceiling unless you pass `level=false`, which will quietly
undo your gain staging.

Verify: `python3 tts/master_embedded.py <file> --check` reports spread, peak
and clipping without writing anything.

## 4–6. Cards

Readers differ on leading zeros, case and stray whitespace, so compare on a
normalised form. A card can have two physical copies — water and torch do — so
every mapping is a **list**, and teaching a card **adds** a UID rather than
replacing the printed one. Seed the printed set so a fresh browser starts
ready. `cards.json` is the source of truth; `python3 sync_cards.py` pushes it
into all four games and `node qa_cards.js` verifies.

## 7. Production vs developer

Production is the default and shows only Start, Reset, and physical cards. If
on-screen card buttons are visible, a kid will tap through the whole story and
never touch a card. Dev tools sit behind `Ctrl+Shift+D`.

Moon and Jungle Rescue 2 deliberately *offer* an on-screen card tray as a
fallback when no reader is connected — and when they do, the correct answer is
always among the six.

## 8. The reader's Enter key

A mouse-clicked button keeps focus, and the reader's Enter fires it again.
This reset teaching on every scan once; here it would have hit **Reset**
mid-story. Blur after any click, and `preventDefault()` on the reader's Enter.

## 9–11. Responding to a scan

Never let a scan pass silently — a sound within ~200 ms, always. A *correct*
card scanned while Coco is still talking is remembered and acted on when the
line ends; a wrong one is remembered but never advances the story. Wrong-card
lines are warm, never corrective, and rotate so the joke doesn't repeat.

## 12–13. The kids' side

Build physical movement in — clap, jump, dance, drink water. And tell them to
do the action **first** and only bring the card once it's done, so they aren't
rushed.

## 14–15. Small things that bite

Link to `<slug>/index.html`; a bare folder link shows a directory listing on
`file://`. And never hardcode a count in UI text — "All 9 cards are taught"
survived long after the deck grew to 15.

## 16–17. Open

- **No printable card labels** for the Hinglish build — it reuses Jungle
  Rescue 2's ten cards, so those labels already cover it. Toy Town has its own
  `cards.html` for its four new cards; Moon and Jungle Rescue have theirs.
  Toy Town's are **portrait**, with a switch at the top of the sheet: 50 × 80 mm
  inset (default, ~2 mm clearance so a hand-cut label never overhangs and
  peels) or exactly 54 × 85.6 mm, ISO 7810 ID-1 / CR80, the real card size.
  The picture takes 55% of the height and the words sit at the bottom for the
  grown-up — the kids can't read; the drawing is the card. Moon and Jungle
  Rescue are still the older 82 × 50 landscape.

  **Check the page, not just the card.** Four portrait cards across measured
  perfectly at 54 mm each and still did not fit A4's ~190 mm printable width.
  Print to PDF and look at the page.
- **No duplicate-scan guard** in any game. A card resting on the reader fires
  repeatedly on some readers. See `BACKLOG.md` item 1.

---

## Verifying a new story

```
python3 sync_cards.py                 # push card UIDs into it
python3 check_audio.py docs/<slug>    # bed vs narration, per band
node qa_cards.js                      # every card resolves everywhere
node qa_wakelock.js                   # screen stays awake
node qa_hinglish.js                   # tiles, links, embedded build
node qa_modes.js                      # production really is RFID-only
node qa_story_logic.js                # accepted answers, early scans
node qa_allgames.js                   # the shared runtime, in every game
```

Then listen on an actual phone, speaker only, screen down, from two metres.
Nothing replaces that.

## 18. Telling a parent what they're in for

`docs/story-intro.js` shows, before the first Start: every card the story
needs — generated from that game's own deck so it cannot drift — and what the
story will physically ask of the child, with a line about when to save it for
later. Nobody should find out mid-scene that there is jumping.

## 19–20. Resuming: three states, not one — and why it is parked

Two screens were built for this and both came out again on 2026-09-19. The
diagnosis is worth more than the code was, so:

A story can stop for three different reasons, and they need three different
answers:

| what happened | what the audio did | the right answer |
|---|---|---|
| a grown-up pressed **Pause** | context suspended, on purpose | do nothing; their Resume button is the tap |
| a **phone call** | context suspended, or `'interrupted'` on iOS | one tap, then carry on **mid-sentence** |
| the **tab was discarded** | the whole page is gone | ask on the next load, from what is on disk |

`interrupt-guard.js` asked one question — *is the AudioContext running?* — and
so could not tell the first row from the second. Pause was covered by a Carry
on screen within 1.5 seconds, and the only visible button replayed the whole
stop. Pausing to answer a question cost you the scene.

**A suspended context is not a dead one.** Clips are `AudioBufferSourceNode`s
and waits are measured in `ctx.currentTime`; both freeze while suspended, so
`resume()` continues exactly where it stopped. Only a **closed** context has
lost the clip — its source nodes are gone and `onended` will never fire — and
only then is replaying the stop the lesser evil. Treating the two alike is
what turned a one-tap recovery into a restart.

**A discarded tab is the third case, and the only one nothing announces.**
Android throws a backgrounded tab away and it returns as a fresh load — at
13-15 MB these pages go early. No event fires, nothing in memory survives, so
the step has to already be on disk: written on `visibilitychange` and
`pagehide`, which is all the warning there is. And never restored silently — a
child who finished and wants it again must not be dropped at stop eight.

Both modules are still in `docs/`, unwired, with their test suites in
`parked/`. `parked/qa_pause.js` models the real state machine rather than
stubbing it away and pins the bug; it is the one to make pass first. See
`parked/README.md`.
