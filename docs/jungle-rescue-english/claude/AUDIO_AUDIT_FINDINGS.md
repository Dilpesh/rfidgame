# Jungle Rescue English — audio engineering audit (phone-speaker suitability)

Date: 2026-09-25. Measured with ffmpeg on the Mac, on the 187 production files
that `audio/manifest.json` references (0 missing). Phone-speaker band test =
`check_audio.py` method from AUDIO_STANDARD.md §1, run against every bed and
overlay at the volume `index.html` actually plays it. **No original file was
modified.** Full per-file numbers: `measurements_all_187_files.json`.

## Findings, worst first

### 1. Lion-scene beds fail the phone test (blocker)
`JR_103_bed` (0.26 under JR_104–128) and `JR_129_bed` (0.18 under JR_130–149)
are 91 % high-frequency (crickets). Gap bed-vs-voice through the phone sim:

| band | JR_103_bed | JR_129_bed | need |
|---|---|---|---|
| 3–4 kHz | −20.0 | −19.8 | ≤ −20 |
| 4–6 kHz | −7.6 | −6.7 | ≤ −20 |
| 6–8 kHz | −1.9 | −1.5 | ≤ −20 |

Same failure as the moon story's night bed. Neither has the §2 bed chain applied
and neither has a measurement in the manifest. → proposed fix in `modified/`.

### 2. Daytime bed JR_001 is effectively silent, and the manifest is wrong about it
File on disk: −43.9 LUFS, true peak −31 dBFS, stereo, 87 % HF. Manifest says
−15.9 LUFS / −5.4 dBFS. At 0.23–0.28 it is ≈ −55 LUFS — inaudible. It "passes"
only because nothing is there. EQ-ing it (tried) leaves −60 LUFS: nothing left.
Not fixable from this file; needs a new low-mid source (wind, distant birds,
no crickets) or no day bed at all. Nothing proposed.

### 3. Overlays that start on top of a spoken line mask its first word
`playOverlayCue` fires an effect at the same instant as the line:
JR_120 @0.85 + JR_119 @0.25 under JR_121 "YES! FLASHLIGHT!" (JR_120 is +2.1 dB
*louder* than the voice at 6–8 kHz); JR_138 @0.35 under JR_140 "YES! BLANKET!";
JR_158 @0.35 under JR_159 "YES! MUSIC!". Worst gaps −3 to −10 dB. EQ-ing the
effects does not fix it (tried: still −12 to −16 dB) — bright reward sounds are
supposed to be bright. The fix is timing, not files: play effect, ~150 ms,
then the line. → demonstrated in `ab/flashlight_*` (code change, not applied).

### 4. Dance music under the dance calls is borderline
JR_160 at 0.62×0.60 under JR_161/164/167/168: 14–19 dB under the voice at
3–8 kHz (need 20). Low-mid track, so low risk; judge on the phone.

### 5. The "find the card" hint lines are the quietest lines in the game
Narration spans −14.8 … −20.7 LUFS (median −16.4; target −16 ± ~1.5).
Quiet: JR_155 −19.2, JR_056 −18.9, JR_036 −18.1, JR_157 −18.1, JR_116 −18.0,
JR_050 −17.8, JR_135/JR_140/JR_161 −17.6. JR_143 (−20.7) is the lullaby and is
meant to be soft. Loud side JR_108 −14.8, JR_102/028/075/093 ≈ −15.1 (ok).
→ level-matched copies in `modified/`.

### 6. Peaks, channels, encoding
- Narration true peaks all ≤ −1.5 dBFS ✔
- Hot effects (target ≤ −1.4): JR_152_clap **+0.1** (clipped in file; manifest
  says −1.0 / −15.2 LUFS, file is −17.0), JR_016 −0.2, JR_019 −0.3, JR_017 −0.4,
  JR_174 −0.5, JR_006 −0.9, JR_120 −1.2, JR_150 −1.2, JR_153 −1.3, JR_061 −1.3.
- Stereo instead of mono: JR_001, JR_074, JR_112, JR_152_clap (downmix is clean).
- VBR re-encodes not matching manifest: JR_054 (174 kbps, TP −1.6 vs −2.4),
  JR_062 (234 kbps, −16.6 LUFS vs manifest −18.8, TP −1.5 vs the −2.0 its own
  recorded filter would give). Re-encoded after the manifest was written.
- JR_112.mp3: −10.4 LUFS stereo −0.3 dBFS, loudest file in the folder, **not
  referenced by index.html** (spec reuses JR_106_lion). Stale orphan.
- Manifest has no measurements for JR_103_entry/bed, JR_129_entry/bed, JR_106_lion.
- All 44.1 kHz; no head/tail silence issues (JR_036/069/092 have 0.3 s lead-in).

### 7. iOS: `HTMLMediaElement.volume` is ignored on iPhone
Every level in the game (beds 0.18–0.28, overlays 0.25–0.85, the 0.60 duck under
dance calls) is set via `audio.volume`; there is no Web Audio / GainNode in
index.html. iOS Safari pins `volume` to 1.0. On an iPhone the lion beds play at
full level — 4 to 10 dB *above* the voice at 4–8 kHz — and JR_120 lands at 1.0 on
top of "YES! FLASHLIGHT!". Android Chrome honours `volume`. Verify on a real
iPhone; the fix is a GainNode per element (works on iOS), which is a code change.

### What is fine
JR_021 (elephant intro bed, 0.18): worst gap −35 dB ✔. Effects played *between*
lines (holdEffect JR_043/045, JR_106_lion roar, stings) are where brightness
belongs ✔. Cue files all present, all mono 128 k except noted ✔.

## Lesson for AUDIO_STANDARD.md (proposed, not written there)
- A crickets bed cannot be rescued by EQ into an *audible* phone bed: after the
  §2 chain JR_103_bed is −45 LUFS. The standard's design (bed audible between
  lines at AMB_BASE, nearly gone under speech at AMB_DUCK) needs **ducking in
  code**; this game plays beds at one constant volume, so pick beds with
  low-mid content (wind, drone, frogs, distant owl) and no crickets.
- Reward effects must be *sequenced* before the line, never overlaid on it.
- Manifest loudness must be re-measured from the file that ships, not the raw.
- Any per-element `volume` is a no-op on iOS → measure beds at 1.0 as well.
