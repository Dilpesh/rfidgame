# Point 7 — iPhone ignores audio.volume (preview, nothing applied)

Confirmed on the phone 2026-09-25 with phone-volume-check: "play at 1.0" and
"play at 0.26 via audio.volume" were the same loudness; 0.26 through a Web
Audio gain node was quieter. So on iPhone every bed, overlay and the dance
duck in the game currently plays at full volume.

Files
- original_index.html   the game as committed today (byte copy)
- patched_index.html    the proposed game: all levels routed through a gain node
- changes.diff          exactly what differs (11 small edits + one helper block)
- index.html            patched_index.html plus <base href="../../"> so it can be
                        opened from THIS folder and still find ../../audio/ and
                        the shared ../*.js. Deploy the whole docs/ (or repo) and open
                        docs/jungle-rescue-english/claude/ios-volume-fix/index.html
                        on the phone. Do not copy this one over the real index.html.

What changed
- helper: audioCtx() / setVol(el,v) / getVol(el). setVol connects the element
  to a GainNode once and sets the gain; the element's own volume is set to 1
  so Android does not attenuate twice. If Web Audio is unavailable it falls
  back to el.volume, i.e. today's behaviour.
- every `x.volume = v` for beds, overlays, standalone SFX and the dance track
  became setVol(x, v); the crossfade reads getVol(old).
- the AudioContext is created/resumed on the first tap (begin() and any
  pointerdown), which iOS requires before it will make sound.
- narration (playFile) is untouched.

What to check on the phone (iPhone first, then Android if you have one)
1. Start the game, get to the elephant scene: the day bed should now sit under
   Coco the way it did in elephant_scene_G_subtle.mp3, not on top of him.
2. Lion scene: the night bed should match lion_scene_E_CHOSEN.mp3.
3. FLASHLIGHT: torch click, then "YES! FLASHLIGHT!" — click should not be a blast.
4. Dance party: music should dip while Coco calls the moves, then come back.
5. Nothing silent: if any sound is missing entirely, that is the AudioContext
   not being unlocked — tell me which sound and on which phone.
