#!/usr/bin/env python3
"""Push the physical RFID card UIDs from cards.json into every game.

    python3 sync_cards.py            # write
    python3 sync_cards.py --check    # verify only, non-zero if out of date

cards.json is the single source of truth. Add a card (or a second card for
the same thing) there, bump "seed_version", and run this. Each game keeps a
generated block between markers; nothing else in the game is touched.

A card may have several UIDs — Dilpesh has two water cards and two torch
cards, and either one must work.

The shared registry
-------------------
A card means the same thing in every game, so the UIDs live in ONE place in
the browser too: docs/card-registry.js keeps a single localStorage key for the
whole site, seeded from the block this script writes into it. A game on the
registry never sees a UID — it gets only a small generated CARD_MAP
(registry card -> the id that story uses, e.g. SNACK -> BISCUIT), also written
from cards.json. Games are moved onto the registry one at a time; the ones
listed in REGISTRY_GAMES are on it, the rest still get the older per-game
uid -> card block.

A new story that needs a card that is not in cards.json fails here, with the
card named, until it is added to cards.json under a canonical name. That is
the rule: cards are global; a story only says which of them it uses.
"""
import json, re, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
START, END = "/* __CARD_UIDS_START__ */", "/* __CARD_UIDS_END__ */"
REG_START, REG_END = "/* __CARD_REGISTRY_START__ */", "/* __CARD_REGISTRY_END__ */"
REGISTRY_FILE = os.path.join("docs", "card-registry.js")

# Games that read cards through docs/card-registry.js. Add a game here when it
# is migrated; it then gets a CARD_MAP block instead of a DEFAULT_UIDS block.
REGISTRY_GAMES = ("jungle-rescue-english",)


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


def registry_block(cards, seed):
    """The block inside docs/card-registry.js: every physical UID -> its
    canonical card, plus the labels, so a game can list the deck by name."""
    uids = {}
    for canon, v in cards.items():
        for u in v["uids"]:
            uids[norm(u)] = canon
    lines = [f'const SEED_VERSION = "{seed}";', "const DEFAULT = {"]
    width = max((len(u) for u in uids), default=0)
    for u in sorted(uids, key=lambda x: (uids[x], x)):
        lines.append(f'  "{u}":{" " * (width - len(u))} "{uids[u]}",')
    if len(lines) > 2:
        lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    lines.append("const LABELS = {")
    width = max((len(c) for c in cards), default=0)
    for canon in sorted(cards):
        lines.append(f'  {canon}:{" " * (width - len(canon))} {json.dumps(cards[canon]["label"], ensure_ascii=False)},')
    if len(cards):
        lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    return "\n".join(lines)


def map_block_for(cards, game):
    """A registry game's block: registry card -> the id that story uses."""
    m = {canon: v["games"][game] for canon, v in cards.items()
         if game in v.get("games", {})}
    lines = ["// registry card -> this story's card. Generated from cards.json by",
             "// sync_cards.py; the UIDs themselves live in ../card-registry.js.",
             "const CARD_MAP = {"]
    width = max((len(c) for c in m), default=0)
    for canon in sorted(m):
        lines.append(f'  {canon}:{" " * (width - len(canon))} "{m[canon]}",')
    if m:
        lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    return "\n".join(lines)


def splice(path, new_block, check, start=START, end=END):
    s = open(path, encoding="utf-8").read()
    i, j = s.find(start), s.find(end)
    if i < 0 or j < 0:
        sys.exit(f"{path}: missing generated-block markers")
    cur = s[i + len(start):j].strip("\n")
    if cur == new_block:
        return False
    if check:
        return True
    open(path, "w", encoding="utf-8").write(
        s[:i + len(start)] + "\n" + new_block + "\n" + s[j:])
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


def hinglish(path, cards, check):
    """The Hinglish build embeds its audio, and keeps card -> [uid] under
    lowercase ids. Same data, a third shape. The placeholder 1001-1010 ids it
    shipped with are dropped - the on-screen buttons call the step directly,
    so nothing needs them."""
    s = open(path, encoding="utf-8").read()
    m = re.search(r"^const defaultUids=\{.*?\};$", s, re.M)
    if not m:
        sys.exit("%s: could not find defaultUids" % path)
    out = {}
    for _c, v in cards.items():
        gid = v.get("games", {}).get("jungle-rescue-hinglish")
        if gid:
            out[gid] = [norm(u) for u in v["uids"]]
    new_line = "const defaultUids=" + json.dumps(out, separators=(",", ":")) + ";"
    if new_line == m.group(0):
        return False
    if check:
        return True
    open(path, "w", encoding="utf-8").write(s[:m.start()] + new_line + s[m.end():])
    return True


def deck_of(game, path):
    """The card ids a game's own code actually asks for."""
    s = open(path, encoding="utf-8").read()
    if game == "banana-rescue":
        m = re.search(r"const order=\[([^\]]+)\]", s)
        return set(m.group(1).replace("'", "").split(",")) if m else set()
    if game == "jungle-rescue-hinglish":
        m = re.search(r"^const cards=\[.*?\];$", s, re.M)
        return set(re.findall(r"\['([a-z]+)',", m.group(0))) if m else set()
    if game in ("toy-town", "toy-town-v2"):
        s = open(os.path.join(os.path.dirname(path), "app.js"), encoding="utf-8").read()
        m = re.search(r"^const CARDS=\[.*?\];$", s, re.M)
        return set(re.findall(r"\['([a-z]+)',", m.group(0))) if m else set()
    if game == "jungle-rescue-english":
        # the deck is the CARD_ORDER list; the old pattern below never matched
        # this game, so a missing card went unreported
        m = re.search(r"^const CARD_ORDER\s*=\s*\[(.*?)\];", s, re.M)
        return set(re.findall(r"'([A-Z_]+)'", m.group(1))) if m else set()
    return set(re.findall(r'\{ id:"([A-Z]+)"', s))


def verify(cards):
    """Every card a game asks for must have at least one physical UID, or the
    kids will scan it and nothing will happen. Also catches two cards sharing
    a UID, which would make one of them unreachable."""
    problems = []
    seen = {}
    for canon, v in cards.items():
        for u in v["uids"]:
            n = norm(u)
            if n in seen and seen[n] != canon:
                problems.append("UID %s is on both %s and %s" % (u, seen[n], canon))
            seen[n] = canon
    for game in sorted({g for v in cards.values() for g in v.get("games", {})}):
        path = os.path.join(ROOT, "docs", game, "index.html")
        if not os.path.exists(path):
            problems.append("%s: mapped in cards.json but docs/%s/ does not exist"
                            % (game, game))
            continue
        mapped = {v["games"][game] for v in cards.values()
                  if game in v.get("games", {}) and v["uids"]}
        unmapped = {v["games"][game] for v in cards.values()
                    if game in v.get("games", {}) and not v["uids"]}
        missing = deck_of(game, path) - mapped
        for cid in sorted(missing):
            if cid in unmapped:
                why = " (no UID yet)"
            elif game in REGISTRY_GAMES:
                why = (" — not in the global registry. Add it to cards.json under a "
                       "canonical name (or map an existing card to it under \"games\")")
            else:
                why = " (not in cards.json)"
            problems.append("%s: card %s has no physical card%s" % (game, cid, why))
    reg = os.path.join(ROOT, REGISTRY_FILE)
    if REGISTRY_GAMES and not os.path.exists(reg):
        problems.append("%s is missing, and %s read their cards through it"
                        % (REGISTRY_FILE, ", ".join(REGISTRY_GAMES)))
    for game in REGISTRY_GAMES:
        path = os.path.join(ROOT, "docs", game, "index.html")
        if os.path.exists(path) and "card-registry.js" not in open(path, encoding="utf-8").read():
            problems.append("%s: listed in REGISTRY_GAMES but does not load ../card-registry.js" % game)
    return problems


def main():
    check = "--check" in sys.argv
    d = load()
    cards, seed = d["cards"], d["seed_version"]
    changed = []
    # the shared registry first: every UID, once, for every game on it
    p = os.path.join(ROOT, REGISTRY_FILE)
    if os.path.exists(p) and splice(p, registry_block(cards, seed), check, REG_START, REG_END):
        changed.append("card-registry")
    for game in REGISTRY_GAMES:
        p = os.path.join(ROOT, "docs", game, "index.html")
        if os.path.exists(p) and splice(p, map_block_for(cards, game), check):
            changed.append(game)
    # games not yet on the registry keep their own uid -> card block
    for game in ("moon", "jungle-rescue"):
        p = os.path.join(ROOT, "docs", game, "index.html")
        if os.path.exists(p) and splice(p, block_for(cards, game, seed), check):
            changed.append(game)
    # toy-town is a multi-file build: its markers live in app.js
    # toy-town-v2 is the retuned copy that runs beside the original, so the same
    # printed cards have to reach both.
    for tt in ("toy-town", "toy-town-v2"):
        p = os.path.join(ROOT, "docs", tt, "app.js")
        if os.path.exists(p) and splice(p, block_for(cards, tt, seed), check):
            changed.append(tt)
    p = os.path.join(ROOT, "docs", "banana-rescue", "index.html")
    if banana(p, cards, check):
        changed.append("banana-rescue")
    p = os.path.join(ROOT, "docs", "jungle-rescue-hinglish", "index.html")
    if os.path.exists(p) and hinglish(p, cards, check):
        changed.append("jungle-rescue-hinglish")

    total = sum(len(v["uids"]) for v in cards.values())
    dupes = {k: v["uids"] for k, v in cards.items() if len(v["uids"]) > 1}
    print(f"{len(cards)} cards, {total} physical UIDs")
    for k, v in dupes.items():
        print(f"  {k}: {len(v)} cards -> {', '.join(v)}")
    print("on the shared registry: " + (", ".join(REGISTRY_GAMES) or "none yet"))
    problems = verify(cards)
    if problems:
        print("\nNOT PLAYABLE YET:")
        for p2 in problems:
            print("  - " + p2)
    if check:
        print("OUT OF DATE: " + ", ".join(changed) if changed else "all games up to date")
        return 1 if (changed or problems) else 0
    print("updated: " + ", ".join(changed) if changed else "no changes needed")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
