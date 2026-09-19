# Physical card list

24 things, 27 physical cards.

Cards with more than one physical copy — any of them works, everywhere:

- **Torch** — 0002692483, 0006375577
- **Water** — 0002690428, 0002682976
- **Snack / cookie / biscuit** — 0006373651, 0005720648

Source of truth is `cards.json`. After editing it, bump `seed_version` and run
`python3 sync_cards.py`, which refuses to pass if any game asks for a card that has none.

| UID (as the reader types it) | Card | Used by |
|---|---|---|
| `0006170247` | Balloons | Jungle Rescue 2: BALLOONS |
| `0006358547` | Banana | Monkey & Moon: BANANA / Banana Rescue: BANANA |
| `0006375388` | Blanket | Jungle Rescue (Hinglish): blanket / Jungle Rescue 2: BLANKET |
| `0006358348` | Clap | Monkey & Moon: CLAP / Banana Rescue: CLAP |
| `0006358150` | Cutter / pruners | Jungle Rescue 2: PRUNERS |
| `0006373847` | Dance | Monkey & Moon: DANCE / Banana Rescue: DANCE |
| `0006375198` | Disco ball | Jungle Rescue 2: DISCOBALL |
| `0005688164` | Fan | Toy Town: fan |
| `0006374815` | First aid | Jungle Rescue (Hinglish): firstaid / Jungle Rescue 2: FIRSTAID |
| `0006359145` | Fuel | Jungle Rescue (Hinglish): fuel / Jungle Rescue 2: FUEL |
| `0006375007` | Gem | Jungle Rescue 2: GEM |
| `0006358746` | Jump | Monkey & Moon: JUMP / Banana Rescue: JUMP |
| `0005688918` | Key | Toy Town: key |
| `0005688805` | Ladder | Jungle Rescue (Hinglish): ladder / Banana Rescue: LADDER / Jungle Rescue 2: LADDER |
| `0002681159` | Laugh | Monkey & Moon: LAUGH / Banana Rescue: LAUGH |
| `0005687908` | Light | Toy Town: light |
| `0006360778` | Mango | Jungle Rescue (Hinglish): mango / Jungle Rescue 2: MANGO |
| `0002692278` | Moon | Monkey & Moon: MOON / Banana Rescue: MOON |
| `0006360574` | Music | Toy Town: music / Jungle Rescue (Hinglish): music / Jungle Rescue 2: MUSIC |
| `0002696012` | Party horn | Banana Rescue: PARTY / Jungle Rescue 2: PARTYHORN |
| `0006374623` | Rope | Jungle Rescue (Hinglish): rope / Banana Rescue: ROPE / Jungle Rescue 2: ROPE |
| `0006373651` | Snack / cookie / biscuit (1 of 2) | Toy Town: biscuit / Jungle Rescue (Hinglish): snack / Jungle Rescue 2: SNACK |
| `0005720648` | Snack / cookie / biscuit (2 of 2) | Toy Town: biscuit / Jungle Rescue (Hinglish): snack / Jungle Rescue 2: SNACK |
| `0002692483` | Torch (1 of 2) | Jungle Rescue (Hinglish): flashlight / Monkey & Moon: TORCH / Banana Rescue: TORCH / Jungle Rescue 2: FLASHLIGHT |
| `0006375577` | Torch (2 of 2) | Jungle Rescue (Hinglish): flashlight / Monkey & Moon: TORCH / Banana Rescue: TORCH / Jungle Rescue 2: FLASHLIGHT |
| `0002690428` | Water (1 of 2) | Toy Town: water / Jungle Rescue (Hinglish): water / Monkey & Moon: WATER / Banana Rescue: WATER / Jungle Rescue 2: WATER |
| `0002682976` | Water (2 of 2) | Toy Town: water / Jungle Rescue (Hinglish): water / Monkey & Moon: WATER / Banana Rescue: WATER / Jungle Rescue 2: WATER |

## Per game

### Toy Town — 6 cards

| In-game name | Card | UID(s) |
|---|---|---|
| `biscuit` | Snack / cookie / biscuit | 0006373651, 0005720648 |
| `fan` | Fan | 0005688164 |
| `key` | Key | 0005688918 |
| `light` | Light | 0005687908 |
| `music` | Music | 0006360574 |
| `water` | Water | 0002690428, 0002682976 |

### Jungle Rescue (Hinglish) — 10 cards

| In-game name | Card | UID(s) |
|---|---|---|
| `blanket` | Blanket | 0006375388 |
| `firstaid` | First aid | 0006374815 |
| `flashlight` | Torch | 0002692483, 0006375577 |
| `fuel` | Fuel | 0006359145 |
| `ladder` | Ladder | 0005688805 |
| `mango` | Mango | 0006360778 |
| `music` | Music | 0006360574 |
| `rope` | Rope | 0006374623 |
| `snack` | Snack / cookie / biscuit | 0006373651, 0005720648 |
| `water` | Water | 0002690428, 0002682976 |

### Monkey & Moon — 8 cards

| In-game name | Card | UID(s) |
|---|---|---|
| `BANANA` | Banana | 0006358547 |
| `CLAP` | Clap | 0006358348 |
| `DANCE` | Dance | 0006373847 |
| `JUMP` | Jump | 0006358746 |
| `LAUGH` | Laugh | 0002681159 |
| `MOON` | Moon | 0002692278 |
| `TORCH` | Torch | 0002692483, 0006375577 |
| `WATER` | Water | 0002690428, 0002682976 |

### Banana Rescue — 11 cards

| In-game name | Card | UID(s) |
|---|---|---|
| `BANANA` | Banana | 0006358547 |
| `CLAP` | Clap | 0006358348 |
| `DANCE` | Dance | 0006373847 |
| `JUMP` | Jump | 0006358746 |
| `LADDER` | Ladder | 0005688805 |
| `LAUGH` | Laugh | 0002681159 |
| `MOON` | Moon | 0002692278 |
| `PARTY` | Party horn | 0002696012 |
| `ROPE` | Rope | 0006374623 |
| `TORCH` | Torch | 0002692483, 0006375577 |
| `WATER` | Water | 0002690428, 0002682976 |

### Jungle Rescue 2 — 15 cards

| In-game name | Card | UID(s) |
|---|---|---|
| `BALLOONS` | Balloons | 0006170247 |
| `BLANKET` | Blanket | 0006375388 |
| `DISCOBALL` | Disco ball | 0006375198 |
| `FIRSTAID` | First aid | 0006374815 |
| `FLASHLIGHT` | Torch | 0002692483, 0006375577 |
| `FUEL` | Fuel | 0006359145 |
| `GEM` | Gem | 0006375007 |
| `LADDER` | Ladder | 0005688805 |
| `MANGO` | Mango | 0006360778 |
| `MUSIC` | Music | 0006360574 |
| `PARTYHORN` | Party horn | 0002696012 |
| `PRUNERS` | Cutter / pruners | 0006358150 |
| `ROPE` | Rope | 0006374623 |
| `SNACK` | Snack / cookie / biscuit | 0006373651, 0005720648 |
| `WATER` | Water | 0002690428, 0002682976 |

