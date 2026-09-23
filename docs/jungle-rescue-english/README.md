# Jungle Rescue English

This folder is the isolated working home for the original Jungle Rescue Patrol production script.

Baseline source: `jungle_rescue_final_production_script.md`, copied from the supplied production output on 22 September 2026.

## Current handoff

| File | Recipient | Responsibility |
|---|---|---|
| [Audio production script](jungle_rescue_final_production_script.md) | ElevenLabs operator / audio producer | Exact spoken words, global character voices, per-cue emotions, SFX, music prompts and recording deliverables |
| [Playback specification](jungle_rescue_playback_spec.md) | Game developer / ChatGPT implementing the player | Which cue to play, card states, hint timers, what can interrupt, repeat scans, water break, lori, dance and completion |

The two files share stable `JR_NNN` cue IDs. The audio file owns creative content; the playback
file owns runtime behavior. The producer delivers separate audio assets and a manifest of actual
paths, durations and approved voice settings. The developer uses that manifest to implement the
playback specification. This handoff does not itself generate audio or implement `index.html`.

Global voice direction is enforced by one approved voice ID and reference sample per character,
fixed generation settings recorded in the manifest, and listening checks against those samples.
Bracketed directions change delivery, not identity, and are never read aloud.

Workflow:

1. Make one focused story change at a time.
2. Review the diff with `git diff`.
3. Ask the user before committing. Once approved, commit that change separately with a specific message on the story branch; merge only after approval.
4. Keep audio, game code, and script changes in separate commits when they are independent.

The existing `docs/jungle-rescue` build remains unchanged. This folder is the English story source and review history for the new work.
