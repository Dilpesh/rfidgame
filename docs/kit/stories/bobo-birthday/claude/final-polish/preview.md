# Bobo — final polish — applied 3 Oct 2026 (approved). story.txt = this story.txt.

- `story.original.txt` = current story.txt (md5 508ba4f0eecdf8013261edc8fb3c2db5)
- `story.txt` = with the changes below (md5 69fdbd2a8754ff4421749a52dadecde2)
- Lint: no new warnings; 63 → 67 clips. 38 unchanged lines pinned to their existing audio (checked text-identical); 7 new lines, none collide with existing ids.

| # | what | before | after |
|---|---|---|---|
| 1 | Song | Happy birthday, Bobo~ Happy birthday, Bobo~ | Happy birthday to you! Happy birthday, dear Bobo! |
| 2 | Ending | — | kit standard goodbye, added by the compiler to every story: "अगली story में फिर मिलेंगे, {name}!" (lib:goodbye) |
| 4a | Banana order | crunch → "Yum! Yummy banana! अब आई ना असली birthday energy!" → praise | crunch → "Yum! Yummy banana!" → praise → "अब आई ना असली birthday energy!" |
| 4b | Praise pool | Bobo's own blocks | the kit standard blocks (docs/kit/standards.txt): Amazing / Good job / Excellent work / Correct choice / बिल्कुल सही |
| 5 | Candle | "…फूँक मारो!" → 1.5 s → blow | → 0.8 s → blow (the blow sound has no silence at its start) |

Why 1: the tune's name line is "Happy birthday dear ___". Singing "Happy birthday, Bobo" to that tune leaves
one beat empty and the model fills it — the extra "b…" before Bobo. Writing the real lyric fills the beat.

New lines to generate (7): S00_001 Correct choice {name}, S00_002 बिल्कुल सही {name}, S05_006 Bye-bye {name}
→ `names.py captain` (and each child's name pack); S02_003, S02_004, S04_005, S05_007 → `generate.py`.
"Hands-on" praise after the cap (praise_action) is unchanged. praise_right stays in the library
(Jungle Rescue English uses it).

**Ids:** the 3 new story lines are pinned to fresh ids S02_101, S02_102, S04_103 (an auto id had collided with the bridge line). 38 lines verified against their audio, 0 wrong.
To generate: names.py captain (3 library lines) · generate.py bobo-birthday (3 lines).

**3 Oct, later:** kids' giggle after the cap joke — `sfx cap_laugh` (A of 3, `claude/audition_laugh.py`, library cap_laugh, −23 LUFS), pause after it 1.5 → 0.6 s. Before: `story.before-laugh.txt`. Right/wrong tap sounds are now in the engine (docs/claude/tap-sounds/).
