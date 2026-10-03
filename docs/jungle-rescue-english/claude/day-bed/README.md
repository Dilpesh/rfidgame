# Point 2 — daytime bed JR_001 (preview only, nothing applied)

JR_001 is the day-jungle bed: it starts the intro (0.28) and runs under the
elephant/rope/biscuit/first-aid stretch (JR_028–093 at 0.25) and after the
water break (JR_097–102 at 0.23). On disk it is −43.9 LUFS → inaudible.
The manifest's −15.9 LUFS matches `audio_candidates/old_sfx_jungle_day.mp3`
exactly, so that file is almost certainly the bed the manifest was written
for, before "shipped_dayAmb" was copied over it.

original/JR_001.mp3            as shipped, −43.9 LUFS, 18 s, stereo, 87 % HF
modified/JR_001_F_present.mp3  old_sfx_jungle_day, highpass 90 Hz, fades, mono, 50 s, −19.5 LUFS
modified/JR_001_G_subtle.mp3   same at −6 dB, −25.5 LUFS

Phone band test (worst gap; need ≤ −20):
  F @0.25 under JR_028–093: −20.5 PASS    F @0.28 under intro: −19.9 (80–300 Hz only, a band the phone barely plays)
  G @0.25: −26.5 PASS                      G @0.28: passes with margin

ab/ — elephant scene JR_028→JR_035 as the game plays it, bed at 0.25, narration identical:
  elephant_scene_A_current_bed.mp3   (today: effectively no background)
  elephant_scene_F_present.mp3
  elephant_scene_G_subtle.mp3

To adopt: copy the chosen file to audio/intro-fuel-test/JR_001.mp3, set its
duration_seconds / integrated_lufs / true_peak_dbfs / source_file in the
manifest, bump v=jr-bed-5 → 6 in index.html.
