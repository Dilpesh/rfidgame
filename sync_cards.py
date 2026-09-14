#!/usr/bin/env python3
"""Push the physical RFID card UIDs from cards.json into every game.

    python3 sync_cards.py            # write
    python3 sync_cards.py --check    # verify only, non-zero if out of date

cards.json is the single source of truth. Add a card (or a second card for
the same thing) there, bump "seed_version", and run this. Each game keeps a
generated block between markers; nothing else in the game is touched.

A card may have several UIDs — Dilpesh has two water cards and two torch
cards, and either one must work.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
START, END = "/* __CARD_UIDS_START__ */", "/* __CARD_UIDS_END__ */"


def norm(u):
    """Match the games' normUid(): trim, uppercase, drop leading zeros."""
    return str(u).strip().upper().lstrip("0") or "0"


def load():
    with open(os.path.join(ROOT, "cards.json"), encoding="utf-8") as f:
        return json.load(f)


def uid_map_for(cards, game):
    """normalised uid -> the card id that game uses."""
    out = {}
    for _canon, v in cards.items():
        if game not in v.get("games", {}):
            continue
        for u in v["uids"]:
            out[norm(u)] = v["games"][game]
    return out


def block_for(cards, game, seed):
    m = uid_map_for(cards, game)
    lines = [f'const SEED_VERSION = "{seed}";',
             "const DEFAULT_UIDS = {"]
    width = max((len(u) for u in m), default=0)
    for u in sorted(m, key=lambda x: (m[x], x)):
        lines.append(f'  "{u}":{" " * (width - len(u))} "{m[u]}",')
    if len(lines) > 2:
        lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    return "\n".join(lines)


def splice(path, new_block, check):
    s = open(path, encoding="utf-8").read()
    i, j = s.find(START), s.find(END)
    if i < 0 or j < 0:
        sys.exit(f"{path}: missing generated-block markers")
    cur = s[i + len(START):j].strip("\n")
    if cur == new_block:
        return False
    if check:
        return True
    open(path, "w", encoding="utf-8").write(
        s[:i + len(START)] + "\n" + new_block + "\n" + s[j:])
    return True


def banana(path, cards, check):
    """The banana game predates the shared engine: it keeps per-card alias
    arrays instead of a uid->card map. Same data, different shape."""
    s = open(path, encoding="utf-8").read()
    m = re.search(r"^const ids=\{.*?\};?$", s, re.M)
    if not m:
        sys.exit(f"{path}: could not find the ids map")
    existing = dict(re.findall(r"([A-Z]+):\[([^\]]*)\]", m.group(0)))
    parts = []
    for card, raw in existing.items():
        words = [a.strip().strip("'") for a in raw.split(",") if a.strip()]
        words = [w for w in words if not w.isdigit() or len(w) <= 4]  # keep dev ids
        uids = [norm(u) for _c, v in cards.items()
                if v.get("games", {}).get("banana-rescue") == card
                for u in v["uids"]]
        for u in uids:
            if u not in words:
                words.append(u)
        parts.append(f"{card}:[" + ",".join(f"'{w}'" for w in words) + "]")
    new = "const ids={" + ",".join(parts) + "};"
    if new == m.group(0):
        return False
    if check:
        return True
    open(path, "w", encoding="utf-8").write(s[:m.start()] + new + s[m.end():])
    return True


def main():
    check = "--check" in sys.argv
    d = load()
    cards, seed = d["cards"], d["seed_version"]
    changed = []
    for game in ("moon", "jungle-rescue"):
        p = os.path.join(ROOT, "docs", game, "index.html")
        if splice(p, block_for(cards, game, seed), check):
            changed.append(game)
    p = os.path.join(ROOT, "docs", "banana-rescue", "index.html")
    if banana(p, cards, check):
        changed.append("banana-rescue")

    total = sum(len(v["uids"]) for v in cards.values())
    dupes = {k: v["uids"] for k, v in cards.items() if len(v["uids"]) > 1}
    print(f"{len(cards)} cards, {total} physical UIDs")
    for k, v in dupes.items():
        print(f"  {k}: {len(v)} cards -> {', '.join(v)}")
    if check:
        print("OUT OF DATE: " + ", ".join(changed) if changed else "all games up to date")
        return 1 if changed else 0
    print("updated: " + ", ".join(changed) if changed else "no changes needed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
