# Jungle Rescue audio reuse audit

This is a source-asset audit for the current `JR_001`–`JR_184` production script. It is not the delivery manifest and does not mark any cue as approved. Final reuse requires a listening check on a phone speaker, edit to the cue's timing, and a check against the script's sound direction. Keep source files untouched.

Open [audio_reuse_preview.html](audio_reuse_preview.html) to hear the 23 self-contained candidate clips and export your Use / Edit / Replace choices. The adjacent `audio_candidates/` folder contains copies of the legacy audio, prepared by `prepare_audio_reuse_preview.py`; it is separate from final production `audio/`.

## Listening review received 23 September 2026

The user exported [audio_reuse_review.json](audio_reuse_review.json) from the preview: **12 Use, 1 Edit / mix, 8 Replace, 2 unreviewed**. Treat “Use” as approval of the *source sound*, not approval of an unedited final `JR_NNN` file.

| Choice | Source clips | Current cue plan |
|---|---|---|
| Use | `old_sfx_jungle_day`, `shipped_engineCough`, `shipped_ting`, `old_sfx_fuel`, `old_sfx_engine`, `old_sfx_elephant`, `shipped_mud`, `old_sfx_munch`, `shipped_munchEle`, `old_sfx_magic`, `shipped_nightAmb`, `shipped_boing` | Retain as source candidates for `JR_001`, `JR_008`, correct chimes, `JR_016`, `JR_017`, `JR_027`/`JR_162`, `JR_031`, `JR_061`, `JR_087`, `JR_103`, wrong-card boings. |
| Edit / mix | `shipped_owl` | Edit into a gentle comic `JR_124`. |
| Replace | `shipped_elephant`, `shipped_rope`, `shipped_stomach`, `old_sfx_glug`, `shipped_gulp`, `old_sfx_flashlight`, `shipped_flashlight`, `shipped_dance` | Do not install as final cues; source new sounds for the corresponding moments. |
| Selected reuse | `shipped_dayAmb` | Selected for `JR_001` daytime jungle ambience in the current English story; keep its short loop under dialogue. |
| Unreviewed | `old_sfx_disco` | Celebration comparison only; not installed as story-wide ambience. |

Production edits still needed for the accepted sources: add the key turn before the engine cough, shorten the fuel pour, check the day ambience loop seam, combine the healing sparkle with a bandage wrap, and build the evening rain/wind transition around the approved night ambience. Both munch clips were marked Use for `JR_061`; keep both available until the biscuit-bite edit decides whether to use one repeatable crunch or two alternating takes. The rejected dance loop means `JR_160` needs new music even though the legacy clip had the right nominal length.

## Available legacy audio

- `../jungle-rescue/audio/`: 60 standalone MP3s from an older Jungle Rescue card flow.
- `../jungle-rescue-hinglish/index.html`: 85 base64-embedded MP3 clips from the build the children played. Its audio is not present as standalone files. See `scripts/jungle-rescue-hinglish-AS-SHIPPED.md` for the stage and duration inventory.
- The two sets are separate recordings; none of the checked embedded effect files is byte-identical to a standalone MP3.

## Best candidates for reuse

| Current cue | Existing source | Why it may work | Check or edit before use |
|---|---|---|---|
| `JR_001` | `../jungle-rescue/audio/sfx_jungle_day.mp3` | Daytime jungle ambience | Test the loop seam and ducking; source is 50.1 s MP3. |
| `JR_016` | `../jungle-rescue/audio/sfx_fuel.mp3` | Fuel going into a tank | Trim the 6.1 s source to a short, clear fill after Coco's acknowledgement. |
| `JR_017` | `../jungle-rescue/audio/sfx_engine.mp3` | Jeep engine start | Check the 3.1 s source against the opening's comic engine cough. |
| `JR_027` and possibly `JR_162` | `../jungle-rescue/audio/sfx_elephant.mp3` or embedded `elephant` | Friendly elephant trumpet | Check that it is gentle, recognizable and short enough over dance music. |
| `JR_031` | Embedded `mud` | Comic mud landing | Check that the splat is distinct from a wrong-card sound. |
| `JR_014`, `JR_040`, `JR_059`, `JR_083`, `JR_096`, `JR_119`, `JR_138`, `JR_158` | Embedded `ting` | One shared acknowledgement chime | Compare with the specified `ting_ting`; use one approved recording for all eight cue IDs. |
| `JR_061` | `../jungle-rescue/audio/sfx_munch.mp3` or embedded `munchEle` | Biscuit crunch | Check that a single crisp bite reads clearly and can repeat without a clipped tail. |
| `JR_070`, `JR_179`, `JR_181`, `JR_183` | Embedded `boing` | Short playful boing | The wrong-card boing must stay distinct from Coco's own accident sound (`JR_032`). |
| `JR_098` | `../jungle-rescue/audio/sfx_glug.mp3` or embedded `gulp` | Water gulps | Current cue also needs a glass pour and three clearly separated, escalating gulps; edit or combine. |
| `JR_120` | `../jungle-rescue/audio/sfx_flashlight.mp3` or embedded `flashlight` | Switch click | Current cue additionally needs a soft beam hum; combine if the click works. |
| `JR_124` | Embedded `owl` | Short owl sound | Check that it feels comic and gentle. |
| `JR_087` | `../jungle-rescue/audio/sfx_magic.mp3` | Healing sparkle layer | Combine with a separate bandage-wrap sound. |

The existing `sfx_disco.mp3` is 72.3 s. The embedded `dance` is **20.01 s**, so it is a strong `JR_160` candidate if listening confirms the right energy, a seamless loop, a strong restart beat and a tempo compatible with the scripted freeze calls. The existing generic snore does not establish the script's child-like Lion identity; record or design `JR_147` to match the approved Lion voice. The old night ambience lacks the current rain-and-wind transition, so `JR_103` needs a new mix.

## Dialogue

Do not bulk-copy legacy speech. The old standalone narration uses a different card flow (including balloons, gem and giraffe), while the embedded build includes the child's former name, giraffe and mango. The current production script is generic, uses biscuit and has shorter, separately timed prompt/hint/acknowledgement cues. An individual old line is reusable only if its **spoken words, character identity, emotional direction, and edit boundaries** match the current cue exactly after listening. None has been approved on that basis yet.

## Delivery rule

The current script requests individual `JR_NNN.wav` PCM assets and an `audio/manifest.json` with measured durations and voice settings. The sources above are MP3s. Converting MP3 to WAV can satisfy the player's file format but cannot restore quality lost in the original encode. Preserve source provenance in the manifest; accept each edited candidate by listening and technical QA before copying it into `audio/`.
