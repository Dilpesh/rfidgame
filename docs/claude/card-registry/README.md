# Shared card registry — proposal package

**Status: proposal. Nothing in the repo was modified.** Everything here is a copy;
you decide what to keep. Written 25 Sep 2026 from the QA of `docs/jungle-rescue-english`; rebased on the file as of 11:55 (cache tag `jr-bed-6`) so `original/` matches the repo; the `docs/claude/production-mode` package carries a `modified+registry/` copy with both changes in one file.

## The problem it fixes

`jungle-rescue-english` read its cards from `localStorage['rescueGameCards']` — Jungle
Rescue 2's key, on the same site — and only filled in gaps. JR2 had already written
`6373651 → SNACK` and `6374815 → FIRSTAID`, so on any phone that had ever opened JR2,
both biscuit cards and the first-aid card came back as "wrong card".

## The rule it implements

**A card means the same thing in every game.** Cards are global; a story only says
which of them it uses. `cards.json` stays the single source of truth.

- `docs/card-registry.js` (new, shared runtime like `scan-guard.js`): ONE localStorage
  key for the whole site, `kahaniCards`, seeded from a block `sync_cards.py` writes
  into it. `CardRegistry.lookup(raw)` → canonical card (`SNACK`); `teach(raw, card)`
  adds a UID for every game at once; `cards()` / `label()` for listing the deck.
- A game on the registry never sees a UID. It gets a generated `CARD_MAP`
  (registry card → its own id: `SNACK → BISCUIT` here) between its existing
  `__CARD_UIDS_START__/END__` markers, and maps `lookup()` through it.
- Seeding: on a new `seed_version`, `cards.json` wins for the UIDs it names (an
  edit there must reach every phone). Between seeds, `teach()` wins. UIDs taught by
  hand that `cards.json` does not know survive a re-seed. Old per-game keys are
  left untouched and ignored — you confirmed every card is in `cards.json`.
- A new story that needs a card `cards.json` does not have fails in
  `sync_cards.py` with the card named, until it is added there. That is the
  "ask to add it to the global thing" step.

## What is in this folder

| path | what |
|---|---|
| `new/docs/card-registry.js` | the shared module → `docs/card-registry.js` |
| `new/qa_registry.js` | its test, and the test for every game on it → repo root |
| `original/` + `modified/` | untouched and changed copies of the four files below |
| `preview/index.html` | one page linking a side-by-side diff of each change; `.diff` files beside it |

Changed files, and why:

| file | change |
|---|---|
| `docs/jungle-rescue-english/index.html` | loads `../card-registry.js`; `DEFAULT_UIDS`/`SEED_VERSION`/`uidToCard`/`rescueGameCards` gone; `CARD_MAP` block; `cardOf()` resolves a scan through the registry; `loadCards()` now only reports a missing module or an unmapped card |
| `sync_cards.py` | writes the registry block into `docs/card-registry.js`; games in `REGISTRY_GAMES` get a `CARD_MAP` block instead of `DEFAULT_UIDS`; `deck_of()` learns this game's `CARD_ORDER` (the old regex never matched it, so a missing card went unreported); `verify()` names a card that is not in the global registry and checks a registry game actually loads the module; other games generated exactly as before |
| `check_games.py` | new gate row `card registry` (`CardRegistry.lookup`); the six unmigrated games are excused **by name** with the reason written down, so the gate says who is still off it |
| `LEARNINGS.md` | learning 21, the registry in the shared-runtime table, `qa_registry.js` in the verify list |

## How to apply

From the repo root, once you have read the previews:

```
cp docs/claude/card-registry/new/docs/card-registry.js docs/card-registry.js
cp docs/claude/card-registry/new/qa_registry.js qa_registry.js
cp docs/claude/card-registry/modified/sync_cards.py sync_cards.py
cp docs/claude/card-registry/modified/check_games.py check_games.py
cp docs/claude/card-registry/modified/LEARNINGS.md LEARNINGS.md
cp docs/claude/card-registry/modified/docs/jungle-rescue-english/index.html docs/jungle-rescue-english/index.html
```

Then verify:

```
python3 sync_cards.py --check     # expect: all games up to date  (the blocks are pre-generated)
python3 check_games.py            # expect: every story carries every learning; six excused by name
node qa_registry.js               # expect: ALL PASS  (needs playwright, like the other qa_*.js)
node qa_allgames.js               # unchanged games still pass
```

`git diff` after the copies should match `preview/*.diff` exactly.

## What was verified before handing this over

- The modified `sync_cards.py` and `check_games.py` were run against a mirror of the
  real repo (all seven games + shared modules) with these files in place:
  `all games up to date`, and the gate passes with the six older games excused.
- `node qa_registry.js`: 26/26 — the module alone (108 lookups in every UID form,
  seed / re-seed / teach / forget / storage-blocked), and `jungle-rescue-english`
  with a pre-polluted `rescueGameCards` key: both Snack cards → `BISCUIT`,
  first aid → `FIRST_AID`, a keyboard scan reaches the story as `BISCUIT`, JR2's key untouched.
- The earlier full-story browser run (intro → reader check → all eight questions →
  dance → done) repeated against the modified game: same results as before the change.

## Not in this package (next milestones)

- **M2** `moon`, `jungle-rescue` — same uid→card shape, mechanical.
- **M3** `banana-rescue` (alias arrays), `jungle-rescue-hinglish` (card→[uid], the benchmark: conservative),
  `toy-town-v2`; then `toy-town` last, since it is the A/B control.
- **M4** delete the per-game shapes from `sync_cards.py`, retire `qa_cards.js` into `qa_registry.js`,
  and a Teach screen that calls `CardRegistry.teach()` (no game currently on the registry has one).
- The other findings from the QA report (production mode, iOS volume, lion-scene beds, preloading…) are untouched here.
