# Engine: one tap tick on every card tap (proposal, 3 Oct 2026). Not applied.

Asked by Dilpesh: every tap acknowledged with the same tick, right or wrong, in the core engine.

Today `lib:tap` plays only when a card is tapped *while Coco is talking*. In a question, a right card goes
straight to the story's reward sound and a wrong one to the boing; on-screen taps during narration get
no sound at all.

Change (`kit/engine/kahani.js`, 3 lines — see original/ and modified/):
1. `acceptCard`: play the tap tick first, at 50 %, for every tap that reaches it (reader or screen,
   right or wrong). Not for an 'early' accept — that card was already ticked when it was scanned.
2. `boot`: if a story names no tap sound, use `lib:tap` — the tick is part of the engine.

Result: tap → tick at once → then the story's reward sound + "YES! Candle!" (right) or boing + redirect (wrong).
The tick is an overlay; nothing waits for it, so no delay is added.

Affects every kit game: bobo-birthday, gulbul-pandey, jungle-rescue-english, night-drive (all already
have `tap sound: @lib:tap`). find-and-tap is a legacy build and not on this engine.

To apply: copy modified/kahani.js over kit/engine/kahani.js; update the `kahani.js?v=` tag in each
game's index.html by sed (do NOT rebuild: build.py drops the nfc.js tag in bobo-birthday and
night-drive); check_games.py; test on the phone.
Note: `lib:tap` is described in the library as a synthetic placeholder — a nicer tick can replace the
file later without touching any story.
