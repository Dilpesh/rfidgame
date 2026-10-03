# Bobo की Birthday Party — length cut (proposal, 3 Oct 2026)

**Applied 3 Oct** — `../../story.txt` is now this proposal (md5 508ba4f0eecdf8013261edc8fb3c2db5); the version before is `../../story.txt.bak-2026-10-03-before-length-cut` (= story.original.txt). Dance music: **C** → new library clip `dance_loop_phone` (volume 1.0; `dance_loop` unchanged). Song bed stays at 25 % for now; singing line unchanged.

- `story.original.txt` — untouched copy of story.txt as it was today (md5 9758c82e34e8cb261f5a92358c9f8190)
- `story.txt` — the same with the changes below (md5 508ba4f0eecdf8013261edc8fb3c2db5)
- Lint (`compile.py --check`): one warning fewer (करोगे in the song intro), no new warnings; 66 → 63 clips.
- **Every unchanged line is pinned to its current clip id** (`@BOBO_BIRTHDAY_…`). Clip ids are numbered by position and the manifest is matched by id only, so removing a line would otherwise shift every later id and play old audio under the wrong lines, silently. Checked: 35 lines map to clips whose text matches exactly; the 5 changed lines get new ids not in the manifest.

Durations are measured from the clips already generated; new ones are estimates.

| # | where | before | after | saves |
|---|---|---|---|---|
| 1 | Speaker scene, opening | Cake ready, banana खा लिया, candles blow हो गईं, और birthday cap भी पहन ली! अब birthday party की जान बाकी है… धन-टना-टन… Music! (12.1 s) | वाह, party लगभग ready है! पर party में और क्या चाहिए, जिससे सब dance करें? धन-टना-टन… Music! (~6 s) | ~6 s |
| 2 | Cap instruction | अब देखो, तुम्हारी table पर एक real Birthday Cap रखी है। पहले उस cap को उठाओ और अपने सर पर पहन लो! पहन लिया? (11.2 s) | देखो, table पर एक real Birthday Cap रखी है! उसे उठाओ और सर पर पहन लो! (~5 s; the 3 s wait stays) | ~6 s |
| 3 | Candles | Bobo five साल का हो गया, तो five candles! (3.6 s) + Look! One, two, three, four… FIVE candles! (5.8 s) | चलो, Bobo के साथ candles बुझाते हैं — ज़ोर से फूँक मारो! (~4 s) → 1.5 s → blow-out → "Poof!" | ~5 s |
| 4 | Ending | What an amazing birthday party! Thank you so much! You are such a hero! (5.8 s) | What an amazing birthday party! You are such a hero! (~4 s) | ~2 s |
| 5 | Song intro | Now, क्या तुम मेरे साथ Bobo को birthday wish करोगे? चलो मिलकर गाते हैं और clap करते हैं! (6.7 s) | चलो, Bobo को birthday wish करके clap करते हैं! (~3.5 s) | ~3 s |

**Total ≈ 22 s** (fast run ~3 min 20 s → ~3 min). Kept as they are, by decision: the riddle asks, the banana lines, "Great! तो चलो…".


## Dance and birthday song (asked 3 Oct)

**Dance — new shape (in story.txt):** "Let's DANCE, {name}!" said clearly *before* the music →
9 s of dance → "Spin around! Keep moving!" (ducked) → dance to 19 s → flourish. Removed: the
banana-energy line (7.4 s) and "Hands up in the air!". Both kept lines reuse existing audio.
Now the music is ducked ~13 of its 19 s; after, ~2 s.

**Music level — not in story.txt yet, pick from `ab/index.html`:** on a phone (above 450 Hz) the
dance music is −28 vs the voice at −17, and the birthday bed at 25 % is −32 under singing at −19.

- Dance: B = full volume (−24), C = full volume + phone EQ (−20). The story syntax has no
  per-story music volume, so either needs a new library clip (e.g. `dance_loop_phone`, volume 1.0;
  `dance_loop` itself is shared and stays).
- Song bed: `bed birthday_bg @0.25` → `@0.5` (B) or `@0.7` (C) — one number in story.txt.

**Singing line:** same voice as every other line (Saanu, same voice id and settings); the
difference is v3 singing at stability 0.4. The text is clean ("Happy birthday, Bobo~ Happy
birthday, Bobo~") — the extra syllable is the model, likely stretching at the `~`. Not changed.

## To apply (once he says so)

```
cp docs/kit/stories/bobo-birthday/claude/length-cut/story.txt docs/kit/stories/bobo-birthday/story.txt
python3 docs/kit/tools/build.py bobo-birthday --check     # lists the 5 new lines to generate (candle, cap, Speaker bridge, song intro, ending)
# ElevenLabs on the Mac, scene by scene: generate.py bobo-birthday — only the missing lines
python3 docs/kit/tools/build.py bobo-birthday
```
Old clips are not deleted.
