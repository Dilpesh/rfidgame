# Tasks

Ordered by priority. **Top is next.** Move things with `python3 task.py top T7`.

```
python3 task.py                      the list
python3 task.py add "..." --story toy-town-v2 --size S
python3 task.py top T7   /  bottom T7
python3 task.py state T7 built
python3 task.py done T7
```

**The states matter more than the order.** A thing gets written into
`STORY_CRAFT.md` and from then on it reads as handled — when in fact no story
has it yet. So these are deliberately different:

| state | means |
|---|---|
| `idea` | noticed, not decided |
| `decided` | we know what to change |
| `written` | the words or the spec exist — a craft rule, a brief, a script |
| `built` | it is in the code or the audio |
| `shipped` | pushed, live |
| `verified` | played with the kids and it worked |
| `parked` | deliberately not now, reason in BACKLOG.md |

Six of the items below are `written` and not `built`. That is the gap this
list exists to keep visible.

| id | what | state | story | size | added |
|---|---|---|---|---|---|
| T1 | Acknowledge every correct card — name the card, name the child, say what changed | written | toy-town-v2 | M | 2026-09-21 |
| T2 | Praise after real effort only — the water trip and the dance | written | toy-town-v2 | S | 2026-09-21 |
| T3 | Re-voice Driver Uncle — all 13 lines together, one new adult voice | written | toy-town-v2 | M | 2026-09-21 |
| T4 | New opening — "क्या तुम मेरे Captain बनोगे?", with a gap to answer | written | toy-town-v2 | M | 2026-09-21 |
| T5 | Record the six rewritten jokes — fan, Teddy snore, softness check, paratha, moustache ticket, sandwich battery | written | toy-town-v2 | M | 2026-09-21 |
| T6 | Wire S03_04b into stop 2 once its audio exists | decided | toy-town-v2 | S | 2026-09-21 |
| T7 | Rhyme and repeated sound — in STORY_CRAFT §3b; not yet in any story | written | all | M | 2026-09-21 |
| T8 | Re-record key_turn / engine_wake / train_sneeze as one readable sequence | decided | toy-town-v2 | S | 2026-09-21 |
| T10 | Normalise the 168 narration clips to −16 LUFS, the last ~1.2 dB vs Jungle Rescue | decided | toy-town-v2 | M | 2026-09-21 |
| T11 | Jungle Rescue: cut "Fair point", Coco's food running gag, and the water-guard wink | decided | jungle-rescue-hinglish | S | 2026-09-21 |
| T12 | Jungle Rescue: bring its effects up ~3 dB | idea | jungle-rescue-hinglish | S | 2026-09-21 |
| T13 | check_audio.py does not actually check toy-town — it looks for audio/narration/ | idea | tooling | M | 2026-09-21 |
| T14 | Rebuild resuming as one thing — three states, not one (BACKLOG 11) | parked | all | L | 2026-09-19 |
| T15 | Find & Tap is outside the shared runtime; fix its build pipeline first (BACKLOG 10) | parked | find-and-tap | L | 2026-09-19 |
| T16 | English stories need an Indian accent, or go Hinglish (BACKLOG 3) | idea | all | L | 2026-09-14 |
| T17 | A/B the kids' names in the story (BACKLOG 5) | idea | all | M | 2026-09-14 |
| T18 | Printable card labels for the Hinglish build (BACKLOG 7) | idea | jungle-rescue-hinglish | S | 2026-09-14 |
| T9 | Trim "तुमने बिजली भी बचाई!" — a civic idea a four-year-old has no hook for | decided | toy-town-v2 | S | 2026-09-21 |

## Done
