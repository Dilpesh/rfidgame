# How to adopt the chosen changes (nothing here has been applied)

Decision 2026-09-25: lion beds → option E (moon-story night bed + faint EQ'd
crickets). Flashlight reward → effect first, then the line.

## 1. Lion beds (audio files)
`claude/modified/JR_103_bed.mp3` and `claude/modified/JR_129_bed.mp3` are the
same 42.03 s file (−25.8 LUFS, 300 ms fades for a clean loop). Built from
`docs/moon/audio/sfx_night_jungle.mp3` + `claude/candidates`' EQ'd crickets at 0.5.
Phone band test at in-game volume: JR_103_bed @0.26 worst −20.6 dB PASS,
JR_129_bed @0.18 worst −22.0 dB PASS (originals: −1.9 / −1.5 FAIL).

    cp claude/modified/JR_103_bed.mp3 audio/lion-rescue-test/JR_103_bed.mp3
    cp claude/modified/JR_129_bed.mp3 audio/lion-rescue-test/JR_129_bed.mp3

Then in `audio/manifest.json` change `bed_duration_seconds` from 12.042 to
42.031 on JR_103 and JR_129, and add to JR_103_bed / JR_129_bed:
`"duration_seconds": 42.031, "integrated_lufs": -25.8, "source_file":
"docs/moon/audio/sfx_night_jungle.mp3 + EQ'd crickets"`. Bump the cache tag
`v=jr-bed-4` → `v=jr-bed-5` in index.html (playBedFile / crossfadeBedFile) so
phones don't keep the old bed.

## 2. Flashlight (and the two identical cases) — index.html timing
Effect must finish before the line starts. Three call sites:

line 225, flashlightSuccess — replace
    playOverlayCue('JR_120',.85);playOverlayCue('JR_119',.25);await playCue('JR_121',{});
with
    await Promise.all([playFile(AUDIO_DIR+cueEntry('JR_120').file,{}),playFile(AUDIO_DIR+cueEntry('JR_119').file,{})]);await wait(150);if(token!==epoch)return;await playCue('JR_121',{});

  (if playFile can't run two at once because it tracks a single `audio`, use
  two `new Audio` elements with volume .85 / .25 and await both `onended` —
  i.e. a `playOverlayCueAndWait(id,vol)` that returns the promise.)

line 226, blanketSuccess — replace
    playOverlayCue('JR_138',.35);await playSequence(['JR_140',
with
    await playOverlayCueAndWait('JR_138',.35);await wait(150);await playSequence(['JR_140',

line 262, musicSuccess — replace
    playOverlayCue('JR_158',.35);await playCue('JR_159');
with
    await playOverlayCueAndWait('JR_158',.35);await wait(150);await playCue('JR_159');

Note these overlay volumes are ignored on iPhone (see AUDIO_AUDIT_FINDINGS §7);
that is unchanged by this edit.

## 3. Hint lines (optional, not yet auditioned on the phone)
`claude/modified/JR_036 050 056 116 135 140 155 157 161.mp3` are gain-only lifts to
≈ −16.5 LUFS. Copy over the same names under audio/… and update their
integrated_lufs / true_peak_dbfs in the manifest from measurements_all_187_files.json.
