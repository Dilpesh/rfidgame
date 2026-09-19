# Backlog

Things to do later, and things that are working and should be kept. Raised by
Dilpesh, 14 Sep 2026. Nothing here is started.

---

## 1. Handle accidental card scans

**The problem.** A card brushing the reader, a card left resting on it, or a
kid waving two cards at once all register as real scans. Right now a stray
scan during a step is treated as a wrong answer, so Coco tells them to try
again for something they never did.

**What's already there.** During narration, a *correct* card is queued and a
*wrong* card is ignored, so mid-line taps are already forgiving. The gap is
between lines, when the game is waiting.

**What done looks like**

- Ignore a repeat of the same UID within ~1.5 s (a card resting on the reader
  fires continuously on some readers).
- Ignore an empty or too-short read.
- Consider a short dead time right after a correct scan, so the kid's hand
  pulling back doesn't fire a second card.
- A stray *wrong* card while waiting should probably be a gentle nudge, not a
  full "wrong card" line — the current one is funny the first time and
  tiresome the fourth.

**Effort:** small, all in `handleScan`. Worth doing before the next play test.

---

## 2. Wake lock on by default

Wake lock is now wired into all four games (14 Sep). What's left is the part
that isn't in our control:

- The browser only grants it over **https or localhost**. Opening the file
  directly does nothing. → Get GitHub Pages live so there is an https URL to
  play from.
- iPhone needs **iOS 16.4+**. Below that the game plays but the screen sleeps.
- **Open question:** is a fallback worth it for unsupported phones? The usual
  trick is a tiny looping muted video, which is ugly but works. Decide after
  seeing whether it actually bites on the phones in the house.

Also worth considering: a visible "screen is staying awake" indicator, so it's
obvious when it *isn't* working rather than discovering it mid-story.

---

## 3. English stories need an Indian accent — or go Hinglish

**The problem.** Find & Tap is in English, and the English doesn't sit right.

**Two directions, and they're not exclusive**

- **Indian-accented English.** Re-record the English lines in his own voice,
  same pipeline as the Hindi ones (see `AUDIO_STANDARD.md`). Most faithful,
  costs a recording session per story.
- **Mixed Hindi-English (Hinglish).** Write stories the way the kids actually
  hear language at home — Hindi sentence structure with English nouns
  ("torch उठाओ!", "banana कहाँ है?"). Probably the more natural fit, and it
  doubles as gentle English exposure.

**Decide first:** is English a separate track of stories, or does every story
carry a language switch? That answer changes how the cards and the card
printouts work, so settle it before building the next story.

---

## 4. Feedback after every card — keep this

**Not a task. A principle that's working.** Every scan gets an immediate
response: a sound, then Coco reacting. The kids know instantly that the card
landed, which is what keeps them going.

Rules to carry into every new story:

- Never let a scan pass silently. A sound within ~200 ms, always.
- The reaction should name what they did, not just say "correct".
- Wrong cards get warmth, not correction.

Anything that adds a pause between the tap and the response is a regression,
however good the reason.

---

## 5. Kids' names in the story — A/B test it

**The idea.** Have Coco use the kids' names instead of the generic "Kishu
Mishu" — "शाबाश, <name>!" at the moments that already have a reaction.

**Why it needs testing, not just building.** It could land beautifully or it
could break the spell — a story where a character knows your name is either
magic or uncanny, and with two kids there's a fairness problem if one name
comes up more than the other.

**How to actually test it**

- Two versions of the *same* story, names on and names off.
- Alternate across sessions rather than running them back to back — the second
  play of anything is always flatter.
- Watch for: do they look up when named? Do they ask for that version again?
- Keep it cheap to build: names only in the handful of celebration lines, so
  a new name is a few clips, not a re-record.

**Note:** this needs per-name recordings, so the name list has to be fixed
before recording. Worth checking whether it also needs a settings screen.

---

## Carried over from earlier

- **Name the site.** "Kahani Cards" was suggested and is used in the README,
  but not decided. Changes the landing page title, tab title and README.
- **Turn on GitHub Pages** (main → /docs). Blocks item 2.
- **15 optional card-name retakes** for Jungle Rescue — sheet is in
  `~/Downloads/jungle game/recording-rescue/retake/`.
- **Find & Tap build pipeline is inconsistent.** `build.py` reads
  `find-and-tap/index.html` and writes `index.built.html`; `.src.html` has two
  placeholder markers, the playable file has one. Flagged, untouched — worth
  straightening out before Find & Tap is edited again.
- **Stale `~/Downloads/jungle game/moon-game.html`** still has the old loud
  ambience values. Patch it or rename it so it can't be played by mistake.

---

## 6. The Hinglish build's embedded audio

`docs/jungle-rescue-hinglish/` ships as one 17 MB HTML file with all 85 cues
base64'd inside it. It works, and for now that's fine — but it has costs worth
knowing:

- **First load downloads all 17 MB** before anything plays. Fine on wifi,
  slow on a patchy mobile connection.
- **`check_audio.py` can't read it** — there's no `audio/` folder. Its beds
  had to be extracted from the `media` object to be checked, and one of them
  (`dayAmb`) was failing when it arrived.
- **Every edit costs 17 MB in git history**, forever.

Not urgent. If it becomes one, splitting the audio back out into an `audio/`
folder would fix all three at once and bring it in line with the other stories.

---

## 7. Printable card labels for the Hinglish build

Every other story has a `cards.html` at CR80 (54 x 85.6 mm), portrait, for
sticking on the physical cards. The Hinglish build has none. It reuses the
same ten cards as Jungle Rescue 2, so the existing labels work — this is only
needed if its card names ever diverge.

---

---

## 10. Find & Tap is outside the shared runtime

Every other story loads `scan-guard`, `reader-check` and `story-intro`.
Find & Tap has none of them, and `check_games.py` records
that as an explicit exception rather than letting it pass quietly.

The reason is its build: it ships as a 1.2 MB single file generated by
`build.py`, and that pipeline is already inconsistent (it reads one filename
and writes another; the source has two placeholder markers and the playable
file has one). Editing the built file by hand would be undone by the next
rebuild. Fix the pipeline first, then add the four modules to the source and
rebuild.

---

## 11. Rebuild resuming, as one thing

Both Carry on screens came out on 2026-09-19 — `docs/interrupt-guard.js` fired
on a deliberate Pause and then replayed the stop, and `docs/progress.js` asked
the same question a second way on the next page load. Both modules are still in
`docs/`, unwired; their suites are in `parked/`.

What it has to get right, which the parked work already establishes:

* **Pause is not an interruption.** The game is the only thing that knows the
  difference, so it has to be asked, not guessed at from the AudioContext.
* **Suspended is not closed.** A suspended context resumes mid-sentence with
  nothing lost; only a closed one has really lost the clip and needs the stop
  replayed.
* **A discarded tab announces nothing** — the step must already be on disk
  before the page goes, and the offer to resume comes on the next load.
* **Never resume silently.** Ask, and offer starting over.

One decision, one screen, three states. `parked/qa_pause.js` is the test to
make pass first; `parked/README.md` has the full account.
