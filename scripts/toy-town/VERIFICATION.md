# Build verification

- 168 MP3 files decode successfully after local level balancing; 756.2 seconds of unique audio.
- 159 new generations completed. Reported generation cost: 8,102.39 credits, excluding earlier auditions. Nine existing clips reused.
- State-machine tests cover all card choices, both switch-off orders, targeted hints, water reminder timing, three 20-second dance rounds, and interruption/reset cancellation.
- Browser checks: Start unlocks WebAudio with nonzero output signal; opening narration and SFX advance; wrong-card and correct-card sounds trigger; Pause suspends audio; Resume continues; Next changes scene; Reset stops playback.
- Physical RFID reader and device speaker output have not been independently tested.

## Included audio
130 dialogue clips, 33 effects/ambiences, two music tracks, three reused feedback sounds. No API key or generation call is included in the deployed game.

Standalone HTML passed embedded-asset checks. Direct file:// browser automation was blocked by the browser URL policy, so interactive browser checks used the HTTP-served folder build.

## September 19 audio revision

- Replaced both cat-like/train horn effects with clear, friendly toy-train sounds.
- Replaced the quiet burp with a louder child-safe cartoon burp and raised its playback gain.
- Re-recorded the sandwich punchline as one playful, mock-surprised Chuku line: "जेब में आधा sandwich?! ये कौन करता है?!".
- Raised the continuous fan layer from 0.06 to 0.14 gain for mobile speakers. Browser verification confirmed the fan state stays ON and the WebAudio output remains active after the FAN card.
