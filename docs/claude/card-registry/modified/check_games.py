#!/usr/bin/env python3
"""Every story must carry every learning. This is the gate.

    python3 check_games.py            # report, non-zero if anything is missing
    python3 check_games.py --list     # just the requirements

Run it before shipping a new story. A game that is missing something fails
here rather than in a child's hands. Exceptions have to be written down, with
a reason, in EXCEPTIONS below - there is no silent pass.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")

# name -> (what it is, how to spot it)
REQUIRED = [
 ("wake lock",        "the screen must not sleep mid-story",
  r"wakeLock"),
 ("scan guard",       "a card left on the reader must not fire over and over",
  r"ScanGuard\.(wrap|wrapGlobal)"),
 ("reader check",     "a dead reader must explain itself, not just do nothing",
  r"ReaderCheck\.run"),
 ("before-you-start", "cards needed, and what the child will be asked to do",
  r"StoryIntro\.show"),
 ("enter key fix",    "the reader's Enter must not re-fire a focused button",
  r"preventDefault"),
 ("card registry",    "cards are global: read them through docs/card-registry.js, never a private map",
  r"CardRegistry\.lookup"),
]

# Parked on purpose, 2026-09-19. The Carry on screens went out of all five
# games: interrupt-guard.js fired on a deliberate Pause (it cannot tell a
# suspended AudioContext from a dead one) and carrying on replayed the stop.
# docs/interrupt-guard.js and docs/progress.js are still in the repo, unwired.
# When they come back as one piece, move these two lines back into REQUIRED.
PARKED = [
 ("interrupt guard",  "a phone call must not hang the story",
  r"InterruptGuard\.watch"),
 ("resume",           "a tab thrown away by the phone must not restart the story",
  r"Progress\.track"),
]

# game -> requirement -> why it is allowed to be missing
# The shared card registry (docs/card-registry.js) went into
# jungle-rescue-english first. The other games still keep their own uid map and
# move over one at a time; each is excused here until it does, so the gate
# names exactly who is still off it.
_NOT_ON_REGISTRY_YET = "still on its own uid map; migrate to card-registry.js (next: moon, jungle-rescue)"

EXCEPTIONS = {
 "find-and-tap": {
   "scan guard": "built artifact; its source pipeline needs fixing first (BACKLOG 10)",
   "reader check": "built artifact; same",
   "before-you-start": "built artifact; same",
   "card registry": "colours and shapes, not the shared card deck",
 },
 "moon":                   {"card registry": _NOT_ON_REGISTRY_YET},
 "jungle-rescue":          {"card registry": _NOT_ON_REGISTRY_YET},
 "banana-rescue":          {"card registry": _NOT_ON_REGISTRY_YET},
 "jungle-rescue-hinglish": {"card registry": _NOT_ON_REGISTRY_YET},
 "toy-town":               {"card registry": _NOT_ON_REGISTRY_YET + " — the A/B control, last"},
 "toy-town-v2":            {"card registry": _NOT_ON_REGISTRY_YET},
}

# a deck that legitimately reuses another story's printed labels
CARDS_REUSE = {
 "jungle-rescue-hinglish": "uses Jungle Rescue 2's ten cards, already labelled",
 "toy-town": "has its own cards.html for the three new cards",
 "find-and-tap": "colours and shapes, not the shared card deck",
 "banana-rescue": "uses cards already labelled in the Moon and Jungle Rescue sheets",
}


def source_of(game):
    d = os.path.join(DOCS, game)
    out = []
    for f in sorted(os.listdir(d)):
        if f.endswith((".js", ".html")):
            out.append(open(os.path.join(d, f), encoding="utf-8", errors="replace").read())
    return "\n".join(out)


def main():
    if "--list" in sys.argv:
        for n, why, _ in REQUIRED:
            print("  %-18s %s" % (n, why))
        return 0
    games = sorted(g for g in os.listdir(DOCS)
                   if os.path.isdir(os.path.join(DOCS, g))
                   and os.path.exists(os.path.join(DOCS, g, "index.html")))
    width = max(len(g) for g in games)
    names = [n for n, _, _ in REQUIRED]
    print(" " * (width + 2) + "  ".join(n[:9].ljust(9) for n in names))
    gaps, excused = [], []
    for g in games:
        src = source_of(g)
        row = []
        for name, why, pat in REQUIRED:
            ok = re.search(pat, src) is not None
            ex = EXCEPTIONS.get(g, {}).get(name)
            if ok:
                row.append("yes")
            elif ex:
                row.append("--")
                excused.append((g, name, ex))
            else:
                row.append("MISSING")
                gaps.append((g, name, why))
        print(g.ljust(width + 2) + "  ".join(c.ljust(9) for c in row))

    print()
    if excused:
        print("Excused, on purpose:")
        for g, n, why in excused:
            print("  %-22s %-18s %s" % (g, n, why))
        print()
    if gaps:
        print("MISSING:")
        for g, n, why in gaps:
            print("  %-22s %-18s %s" % (g, n, why))
        print("\nAdd it, or write the reason into EXCEPTIONS in this file.")
        return 1
    print("Every story carries every learning.")
    print("Parked, not checked: " + ", ".join(n for n, _, _ in PARKED) +
          " (see the note in this file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
