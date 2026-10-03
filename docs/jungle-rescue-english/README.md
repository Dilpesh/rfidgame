# Jungle Rescue English

This folder is the isolated working home for the original Jungle Rescue Patrol production script.

Baseline source: `jungle_rescue_final_production_script.md`, copied from the supplied production output on 22 September 2026.

## Current handoff

| File | Recipient | Responsibility |
|---|---|---|
| [Audio production script](jungle_rescue_final_production_script.md) | ElevenLabs operator / audio producer | Exact spoken words, global character voices, per-cue emotions, SFX, music prompts and recording deliverables |
| [Playback specification](jungle_rescue_playback_spec.md) | Game developer / ChatGPT implementing the player | Which cue to play, card states, hint timers, what can interrupt, repeat scans, water break, lori, dance and completion |
| [Game player](index.html) | Game developer | Browser playback and card-reader flow |
| [Legacy audio preview](audio_reuse_preview.html) | Audio review | Play 23 older sound candidates and export Use / Edit / Replace choices; the MP3s are in `audio_candidates/` |
| [Audio reuse audit](audio_reuse_audit.md) | Audio producer | Candidate-to-cue mapping and reuse limitations |
| [Saved audio review](audio_reuse_review.json) | Audio producer | The producer's exported choices for all 23 legacy clips |
| [Voice audition preview](voice_audition_preview.html) | Voice casting | Compare Vardan Elephant and Bholu Lion with their character treatments |
| [Introduction and Fuel audio test](intro_fuel_audio_preview.html) | Story/audio review | Play the opening in child-experience order, test hints, scan success and the optional repeat-Fuel joke |
| [Introduction and Fuel test manifest](audio/intro-fuel-test/manifest.json) | Audio producer / developer | Partial JR_001–JR_020 delivery data with exact files, measured durations, levels, voices and settings |
| [Elephant Rescue audio test](elephant_rescue_audio_preview.html) | Story/audio review | Play JR_021–JR_071 in child-experience order, including ROPE pulls and all four BISCUIT taps |
| [Elephant joke timing comparison](elephant_joke_timing_preview.html) | Story/audio review | Four current/proposed timing comparisons and the unchanged Pull–गुल reference; source cues remain unchanged |
| [Elephant Rescue test manifest](audio/elephant-rescue-test/manifest.json) | Audio producer / developer | Partial JR_021–JR_071 delivery data, including selected Vardan processing and measured audio properties |
| [Parrot Rescue audio test](parrot_rescue_audio_preview.html) | Story/audio review | Play JR_072–JR_102 from Elephant departure through FIRST AID and the WATER return; the shipped Hinglish hurt effect is selected |
| [Parrot Rescue test manifest](audio/parrot-rescue-test/manifest.json) | Audio producer / developer | Partial JR_072–JR_102 review assets, including Munni Parrot, card hints, and three-gulp water effect |
| [Lion Rescue audio test](lion_rescue_audio_preview.html) | Story/audio review | Hear two Bholu sneezes and the selected angry “अरे — A”, compare two Jeep sounds, review अंधेरा pronunciation, immediate FLASHLIGHT response and balanced लोरी; the removed lion SFX has a separate sound-only control |
| [Jeep sound lab](jeep_sound_lab.html) | Story/audio review | D is selected for JR_103; compare its separate engine/tire/stop mix against C and the archived earlier candidates, alone or before the unchanged Lion-scene weather and narrator |
| [Lion entrance roar preview](lion_intro_roar_preview.html) | Story/audio review | Compare the current no-roar Lion introduction with two gentle roar auditions after Coco recognizes Lion King; no roar has been added to the full scene |
| [Lion Rescue audio QA](lion_rescue_audio_qa.md) | Story/audio review | Transcription and cue-flow checks; listening decisions still pending |
| [Lion Rescue test manifest](audio/lion-rescue-test/manifest.json) | Audio producer / developer | Partial JR_103–JR_149 review assets, including Bholu Lion, split cave ambience and separate लोरी stems |
| [Saved voice review](voice_auditions/casting_review.json) | Voice casting | User selections: Coco = Saanu, Narrator = Jia, Parrot = Munni; the first Elephant and Lion takes were rejected |
| [Current casting decisions](voice_auditions/casting_decisions.json) | Audio producer | Selected voice IDs for all five roles |
| [Subtle character treatments](voice_auditions/selected_character_treatments_manifest.json) | Audio producer | Archived first treatment, rejected as too subtle |
| [Earlier bold character treatments](voice_auditions/bold_character_treatments_manifest.json) | Audio producer | Archived Lion and Elephant experiments; both bold processing chains were superseded after robotic-sound feedback |
| [Child-like Elephant audition](elephant_rescue_audio_preview.html#elephant-audition) | Voice review | Same revised biscuit lines in natural Vardan and light EQ; no lowered pitch or doubled layers |
| [Elephant round 2 auditions](voice_auditions/elephant_round2_manifest.json) | Voice casting | Source Vardan audition |
| [Adult Elephant treatment auditions](voice_auditions/elephant_stronger_manifest.json) | Audio producer | Archived adult Ravi experiment, superseded by Vardan selection |
| [Earlier adult Elephant treatment](voice_auditions/elephant_adult_treatment_manifest.json) | Audio producer | Archived flat-source experiment that did not establish Elephant identity |
| [Earlier Vardan treatment A/B](voice_auditions/elephant_treatment_manifest.json) | Audio producer | Archived experiment; no treatment approved |
| [Voice casting feedback](voice_auditions/feedback.md) | Voice casting | Why the first Elephant and Lion auditions were rejected and what remains to review |

The two files share stable `JR_NNN` cue IDs. The audio file owns creative content; the playback
file owns runtime behavior. The producer delivers separate audio assets and a manifest of actual
paths, durations and approved voice settings. The developer uses that manifest to implement the
playback specification. The player is in `index.html`; approved final `JR_NNN` audio and its
delivery manifest have not been installed yet.

Global voice direction is enforced by one approved voice ID and reference sample per character,
fixed generation settings recorded in the manifest, and listening checks against those samples.
Bracketed directions change delivery, not identity, and are never read aloud.
The confirmed Coco voice is Saanu (`d9BvEI0bp2Tmdpqnjwn0`); match the original shipped intro's
energy and tone during the final recording pass. Narrator is Jia (`ItmwhOeluca31IEX91Yk`),
and Parrot is Munni (`VOGEEZj2Kly5dP9LrQy8`). Elephant is Vardan (`bBG9wwa23659EgIkMbc1`)
and Kid Lion is Bholu (`5krdMTA5HonvWAlY2vSx`). The revised Lion review uses light EQ at
natural pitch; this treatment and the revised bedtime cues await listening approval.
Elephant uses the approved light EQ at natural pitch. The revised biscuit dialogue and
the 1.2-second trampoline / 0.8-second pre-count pauses are approved.
Check intelligibility on a child’s playback device. Keep one
distinct voice per character.

Workflow:

1. Make one focused story change at a time.
2. Review the diff with `git diff`.
3. Ask the user before committing. Once approved, commit that change separately with a specific message on the story branch; merge only after approval.
4. Keep audio, game code, and script changes in separate commits when they are independent.

The existing `docs/jungle-rescue` build remains unchanged. This folder is the English story source and review history for the new work.
