# Kit standards — applied 3 Oct 2026 (approved by Dilpesh)

`original/` = the files before, `modified/` = what is now live.

1. **Tap tick on every tap** (`kit/engine/kahani.js`): every card tap — right or wrong, reader or screen —
   plays `lib:tap` at once (overlay, no delay). Stories without a "tap sound:" get `lib:tap` anyway.
   `kahani.js?v=` bumped to fbf7403c in the 4 kit games' index.html by hand (not rebuilt, so the
   nfc.js tag in Bobo and Night Drive stays).
2. **Standard praise** (`kit/standards.txt`, read by `compile.py`): `use praise` / `use praise_action`
   in a story that does not define the block gets the kit's pool — Amazing / Good job / Excellent work /
   Correct choice / बिल्कुल सही (action: the first three). "You are absolutely right" is out of the
   standard. Stories with their own block (Jungle Rescue, Gulbul, find-and-tap) are unchanged.
3. **Standard goodbye**: every story ends with `lib:goodbye` — "अगली story में फिर मिलेंगे, {name}!" —
   unless its last scene already says bye-bye / फिर मिलेंगे (Jungle Rescue, Night Drive: skipped) or
   the header says `goodbye: off`. Gulbul gets it on its next build.
4. **Ack-before-praise check**: more than 8 words between a card tap and its praise → warning
   ("say the card, praise, then the rest"). Jungle Rescue English: 3 warnings (BISCUIT, FIRST_AID, WATER).
5. **One id = one line** (error): two different lines on one clip id is refused. Found while doing this:
   an auto id for the new Bobo song landed on the pinned bridge line's id — the song would have played
   the bridge audio with no warning. No other story has a collision.
6. `_template/story.txt` uses the standard praise.

To record once (library, shared by every story): `names.py captain` → praise_correct_choice,
praise_bilkul_sahi, goodbye (dry run: exactly these 3). Then each child's pack: `names.py generate <child>`.
