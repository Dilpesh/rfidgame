# Engine: right / wrong tap sounds — applied 3 Oct 2026 (Dilpesh: magic_sparkle = right, boing = wrong; "keep both")

`original/kahani.js` = before (fbf7403c), `modified/kahani.js` = live (e5460c7b).

| tap | sound, at once | then |
|---|---|---|
| right card | `lib:tap_correct` (magic_sparkle with its 0.2 s silent lead-in and silent tail cut, 1.3 s) — the story waits for it | the story's own sound (crunch, candle pop, whistle, click) → "YES! …" |
| wrong card | `lib:boing` — waits for it | the story's warm redirect |
| while Coco talks | `lib:tap` tick (unchanged) | the tap is remembered as before |

- A story's own `sfx magic_sparkle` right after an ask, and `sfx boing` at the start of a wrong-card
  response, are dropped by the engine at load — nothing plays twice, and the other games need no rebuild
  (Jungle Rescue's `sfx boing @JR_179/181/183` are dropped the same way; its redirect lines stay).
- A story can name other sounds with `correctSound` / `wrongSound` in story.json; default as above.
- Tested in headless Chromium against the Bobo build: wrong → boing once → wrong_1; right → tap_correct →
  "YES! Cake!" (no magic_sparkle); a tap during the success line → tick. No page errors.
- `kahani.js?v=` bumped to e5460c7b in the 4 kit games' index.html by hand (nfc.js tags kept).
