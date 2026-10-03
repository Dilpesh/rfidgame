# Kit: "too early:" on an ask — proposal, 3 Oct 2026. Not applied.

Why (kids' play, 3 Oct): Coco says "उठाओ और सर पर पहन लो!", the kid taps the Birthday Cap card at once,
the engine remembers that tap and accepts it the moment the ask starts → the cap is never worn.

Change (opt-in, per ask; every existing ask behaves as before):
- `compile.py`: new ask line `too early: <beat>` (any beat: a COCO line, `wait 3s`…), stored as `tooEarly`.
- `kahani.js` (runAsk): if the card was tapped before the ask *and* the ask has `too early:` lines, the tap
  does not count; Coco says those lines (taps during them don't count either), then the prompt and hints.
  Without `too early:` → unchanged (an early tap counts at once).
- `FORMAT.md`: documented.

Tested: compile of gulbul / jungle-rescue-english / night-drive unchanged; Bobo proposal compiles with no new
warnings. Headless Chromium with the Bobo proposal: cap tapped during the wear instruction → not accepted
(story waits, hint plays); cap tapped after the ask → sparkle → whistle → "Woohoo! Birthday cap ready!".
(`test-story.json` = the compiled Bobo proposal used for the test.)

To apply: copy modified/{kahani.js,compile.py,FORMAT.md}; bump kahani.js?v= in the 4 games' index.html by hand.
