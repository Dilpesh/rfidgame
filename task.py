#!/usr/bin/env python3
"""
The task list. Small on purpose.

    python3 task.py                          # the list, highest priority first
    python3 task.py add "rhyme in Toy Town" --story toy-town-v2 --size S
    python3 task.py top T12                  # move to the top
    python3 task.py bottom T12
    python3 task.py state T12 built          # move it along
    python3 task.py done T12
    python3 task.py show T12

Order in TASKS.md IS the priority - top is next. Nothing to sort, nothing to
argue with.

The states exist because of one specific failure: a thing gets written into
STORY_CRAFT.md, and from then on it reads as handled, when in fact no story has
it yet. So "written down" and "a child has heard it" are different states and
the list will not let them blur.

    idea      noticed, not decided
    decided   we know what to change
    written   the words or the spec exist (STORY_CRAFT, a brief, a script)
    built     it is in the code or the audio, on a branch or main
    shipped   pushed, live
    verified  played with the kids and it worked
    parked    deliberately not now, with a reason
"""
import argparse, datetime, re, sys
from pathlib import Path

FILE = Path(__file__).resolve().parent / "TASKS.md"
STATES = ["idea", "decided", "written", "built", "shipped", "verified", "parked"]
ROW = re.compile(r"^\|\s*(T\d+)\s*\|(.*)\|\s*$")


def load():
    rows, head, tail, seen = [], [], [], False
    for line in FILE.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            seen = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
        elif seen and line.strip().startswith("|") is False and rows:
            tail.append(line)
        elif not seen:
            head.append(line)
        else:
            tail.append(line)
    return head, rows, tail


def save(head, rows, tail):
    out = head + ["| " + " | ".join(r) + " |" for r in rows] + tail
    FILE.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def find(rows, tid):
    for i, r in enumerate(rows):
        if r[0].upper() == tid.upper():
            return i
    print("No such task: %s" % tid)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add"); a.add_argument("what"); a.add_argument("--story", default="—")
    a.add_argument("--size", default="M", choices=["S", "M", "L"])
    a.add_argument("--state", default="idea", choices=STATES)
    a.add_argument("--bottom", action="store_true")
    for c in ("top", "bottom", "done", "show"):
        p = sub.add_parser(c); p.add_argument("id")
    s = sub.add_parser("state"); s.add_argument("id"); s.add_argument("to", choices=STATES)
    args = ap.parse_args()

    head, rows, tail = load()

    if args.cmd is None:
        w = max((len(r[1]) for r in rows), default=20)
        print("%-5s %-9s %-14s %-4s %s" % ("id", "state", "story", "size", "what"))
        for r in rows:
            mark = "  " if r[2] not in ("verified",) else "ok"
            print("%-5s %-9s %-14s %-4s %s" % (r[0], r[2], r[3], r[4], r[1]))
        print("\n%d open. Top of the list is next." % len(rows))
        return 0

    if args.cmd == "add":
        n = max([int(r[0][1:]) for r in rows] + [0]) + 1
        row = ["T%d" % n, args.what, args.state, args.story, args.size,
               datetime.date.today().isoformat()]
        rows = rows + [row] if args.bottom else [row] + rows
        save(head, rows, tail)
        print("added %s at the %s" % (row[0], "bottom" if args.bottom else "top"))
        return 0

    i = find(rows, args.id)
    if args.cmd == "top":
        rows.insert(0, rows.pop(i)); print("%s moved to the top" % args.id.upper())
    elif args.cmd == "bottom":
        rows.append(rows.pop(i)); print("%s moved to the bottom" % args.id.upper())
    elif args.cmd == "state":
        rows[i][2] = args.to; print("%s -> %s" % (args.id.upper(), args.to))
    elif args.cmd == "done":
        r = rows.pop(i)
        tail.append("- %s **%s** — %s (%s)" % (datetime.date.today().isoformat(),
                                               r[0], r[1], r[3]))
        print("%s done, moved to the log" % r[0])
    elif args.cmd == "show":
        print(" | ".join(rows[i])); return 0
    save(head, rows, tail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
