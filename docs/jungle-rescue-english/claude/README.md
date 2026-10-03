# claude/ — audit, proposals and A/B files (nothing here is used by the game)

`index.html` and `audio/` were **not** touched. Everything below is a copy or a
new file. Delete this folder and the game is exactly as before.

- `AUDIO_AUDIT_FINDINGS.md` — the audit, worst first, plus the lessons.
- `preview.html` — open in a browser: every proposed change, the original next
  to the modified version, measurements, and the exact ffmpeg command used.
- `original/` — untouched copies of the 11 files a change is proposed for.
- `modified/` — the proposed versions (same names). To adopt one, copy it over
  the file in `audio/…/` and update its manifest numbers.
- `ab/` — phone test files. Copy to the phone, play from the speaker, screen
  down, 2 m away:
  - `lion_scene_A_original_bed.mp3` vs `lion_scene_B_eq_bed.mp3` — JR_103 → JR_114
    exactly as the game sequences them, bed looping at 0.26. Only the bed differs;
    the narration is byte-identical in both (both −17.1 LUFS integrated).
  - `flashlight_A_effect_over_voice.mp3` vs `flashlight_B_effect_then_voice.mp3` —
    the FLASHLIGHT reward: A = effect fired on top of the line (as the game does
    now), B = effect first, 150 ms, then the line. No bed in either. A's true
    peak is +0.1 dBFS: that clipping is what the game does today too.
- `measurements_all_187_files.json` — LUFS, true peak, LRA, channels, bitrate,
  duration, HF share, head/tail silence for every production file, alongside
  the manifest's own numbers.

## How the modified files were made

Beds (`JR_103_bed`, `JR_129_bed`):
```
ffmpeg -i original/JR_xxx_bed.mp3 \
  -af "highshelf=f=1500:g=-20,lowpass=f=4500,highpass=f=90,volume=4dB,alimiter=limit=0.9:level=false" \
  -c:a libmp3lame -b:a 128k -ar 44100 -ac 1 modified/JR_xxx_bed.mp3
```
(Standard chain is g=−17 / lowpass 5500, which passes at −22.8 dB; −20 / 4500
gives the 25 dB margin the standard asks for, +4 dB puts back what the EQ took
while still passing at −24.3 / −23.6.)

Hint lines (`JR_036 050 056 116 135 140 155 157 161`): gain to −16 LUFS, limiter at
−1.4 dBFS: `-af "volume=<−16 − measured>dB,alimiter=limit=0.85:level=false"`. They
land at −16.5 … −16.8 because the limiter catches a few peaks; durations unchanged.
