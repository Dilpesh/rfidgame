#!/usr/bin/env python3
"""Regenerate the human-readable story scripts from the shipped games.

    python3 scripts/make_scripts.py

The game files are the source of truth for ORDER (which card, which clip, in
what sequence). The sheets in scripts/source/ are the source of truth for the
Hindi WORDS and the performance direction. This joins the two, so a printed
script can never drift from what the game actually plays.

Where two sheets disagree about a clip, the first listed in SHEETS wins. That
order was settled by measuring the shipped audio: predicted reading time from
each variant was compared against the clip's real duration, and the winner
matched within ~1.5 s while the loser was out by 2-10 s.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SRC  = os.path.join(ROOT, "scripts", "source")
OUT  = os.path.join(ROOT, "scripts")

SHEETS = ["retake.json", "rescue-bridges.json", "rescue-story.json", "moon.json"]

STORIES = [
    ("moon", "The Monkey & the Moon — full script", "चाँद चोर बंदर",
     "A naughty monkey has stolen the moon. Coco and the kids go and get it back."),
    ("jungle-rescue", "Jungle Rescue Patrol — full script", "जंगल बचाओ टीम",
     "Captain Coco and the kids fuel the jeep and rescue five animals in trouble."),
]


def load_sheets():
    txt, direction = {}, {}
    for s in SHEETS:
        p = os.path.join(SRC, s)
        if not os.path.exists(p):
            continue
        for row in json.load(open(p, encoding="utf-8")):
            if len(row) < 4 or row[0] in txt:
                continue
            txt[row[0]], direction[row[0]] = row[3], row[2]
    return txt, direction


def grab(src, name):
    """Pull one top-level `const NAME = [...]` / `{...}` literal out of the page."""
    i = src.find("const %s = " % name)
    if i < 0:
        return None
    j = src.index("=", i) + 1
    while src[j] in " \n":
        j += 1
    open_c = src[j]
    close_c = {"[": "]", "{": "}"}[open_c]
    depth, k, instr = 0, j, None
    while k < len(src):
        ch = src[k]
        if instr:
            if ch == "\\":
                k += 2
                continue
            if ch == instr:
                instr = None
        elif ch in "\"'`":
            instr = ch
        elif ch == open_c:
            depth += 1
        elif ch == close_c:
            depth -= 1
            if depth == 0:
                return src[j:k + 1]
        k += 1
    return None


def read_game(game, names):
    src = open(os.path.join(DOCS, game, "index.html"), encoding="utf-8").read()
    parts = []
    for n in names:
        b = grab(src, n)
        if b is not None:
            parts.append("o.%s = %s;" % (n, b))
    js = "var o = {};\n" + "\n".join(parts) + "\nconsole.log(JSON.stringify(o));"
    tmp = os.path.join(OUT, ".dump.js")
    open(tmp, "w", encoding="utf-8").write(js)
    r = subprocess.run(["node", tmp], capture_output=True, text=True)
    os.remove(tmp)
    if r.returncode:
        sys.exit("could not read %s:\n%s" % (game, r.stderr[:800]))
    return json.loads(r.stdout)


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


TXT, DIR = load_sheets()


def render(game, title, native, blurb):
    d = read_game(game, ["CARDS", "STEPS", "INTRO", "WRONG", "WARMUP_TEXT"])
    aud = os.path.join(DOCS, game, "audio")
    ico = {c["id"]: c.get("ico", "") for c in d["CARDS"]}
    hi  = {c["id"]: c.get("hi", "")  for c in d["CARDS"]}
    en  = {c["id"]: c.get("en", "")  for c in d["CARDS"]}
    total, missing = [0.0], []

    def beat(b, L):
        if b.get("sfx"):
            L.append("- 🔊 sound effect — `%s`" % b["sfx"])
        if b.get("under"):
            L.append("- 🎵 music under the line — `%s`" % b["under"])
        vo = b.get("vo") or b.get("audio")
        if not vo:
            if b.get("text"):
                L += ["", "> " + b["text"], ""]
            return
        p = os.path.join(aud, vo)
        s = dur(p) if os.path.exists(p) else None
        if s:
            total[0] += s
        line = TXT.get(vo) or b.get("text")
        if not line:
            missing.append(vo)
        L.append("- 🗣 **`%s`**%s" % (vo, "  ·  %.1fs" % s if s else "  ·  _(file missing)_"))
        if DIR.get(vo):
            L.append("  - _direction:_ " + DIR[vo])
        L += ["", "  > " + (line or "**— no script text found —**"), ""]

    L = ["# " + title, "", "**%s**" % native, "", blurb, "", "",
         "> Hindi lines below are exactly what is recorded in the shipped game.",
         "> Card cues show what the kids have to find. Play order is top to bottom.",
         "", "---", "", "## Opening", ""]
    for b in d["INTRO"]:
        beat(b, L)
    L += ["---", ""]

    for n, st in enumerate(d["STEPS"], 1):
        cid = st["card"]
        head = "## Step %d — %s **%s** card" % (n, ico.get(cid, ""), en.get(cid, cid))
        if hi.get(cid):
            head += "  (%s)" % hi[cid]
        if st.get("alt"):
            head += "  _or %s_" % ", ".join(en.get(a, a) for a in st["alt"])
        L += [head, "", "*The kids have to find the %s card.*" % en.get(cid, cid).lower(), ""]
        for b in st["seq"]:
            beat(b, L)
        L += ["---", ""]

    L += ["## When the wrong card is scanned", "",
          "Played in turn, so the same joke doesn't repeat back to back.", ""]
    for b in d["WRONG"]:
        beat(b, L)

    if d.get("WARMUP_TEXT"):
        L += ["---", "", "## Warm-up round — Coco names each card", "",
              "Before the story starts, the kids scan each card once and Coco names it.",
              "Each has its own recording, loaded as `vo_card_<card>.mp3`.", "",
              "| Card | What Coco says | Clip |", "|---|---|---|"]
        for k, v in d["WARMUP_TEXT"].items():
            fn = "vo_card_%s.mp3" % k.lower()
            fp = os.path.join(aud, fn)
            s = dur(fp) if os.path.exists(fp) else None
            L.append("| %s %s | %s | `%s` · %s |" %
                     (ico.get(k, ""), en.get(k, k), v, fn, "%.1fs" % s if s else "**missing**"))
        L.append("")

    L.insert(5, "**%d card steps · %d different cards · %.0f min of narration**\n"
             % (len(d["STEPS"]), len(d["CARDS"]), total[0] / 60))
    open(os.path.join(OUT, game + ".md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("%-15s %2d steps · %.1f min narration · %d clips with no script text%s"
          % (game, len(d["STEPS"]), total[0] / 60, len(missing),
             " " + str(missing) if missing else ""))


if __name__ == "__main__":
    for a in STORIES:
        render(*a)
