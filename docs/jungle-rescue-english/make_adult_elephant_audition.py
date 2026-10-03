#!/usr/bin/env python3
"""Audition a character treatment of the existing adult Ravi Elephant take.

This is local audio processing only. No new speech is generated, the spoken
words do not change, and no voice is cast by running the script.
"""

import json
import subprocess
from pathlib import Path

from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "voice_auditions"
SOURCE = OUT / "elephant_ravi.mp3"
CALL = HERE / "audio_candidates" / "old_sfx_elephant.mp3"
DRY = OUT / "elephant_adult_ravi_levelmatched.mp3"
CHARACTER = OUT / "elephant_adult_ravi_character.mp3"
WITH_CALL = OUT / "elephant_adult_ravi_character_with_call.mp3"
DRY_FILTER = "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95"
CHARACTER_FILTER = (
    "[0:a]asplit=2[clear0][body0];"
    "[clear0]highpass=f=100,equalizer=f=650:t=q:w=1:g=2.5,"
    "equalizer=f=1000:t=q:w=1.2:g=1.5,"
    "equalizer=f=2500:t=q:w=0.9:g=2[clear];"
    "[body0]asetrate=39690,aresample=44100,atempo=1.111111,"
    "highpass=f=400,lowpass=f=1050,volume=0.16[body];"
    "[clear][body]amix=inputs=2:duration=first:normalize=0,"
    "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
)


def run(command, target):
    if target.exists():
        print(f"Existing: {target.name}; skipping")
        return
    subprocess.run(command, check=True)
    print(f"Rendered: {target.name}")


def main():
    if not SOURCE.is_file() or not CALL.is_file():
        raise SystemExit("Missing adult source or approved Elephant call")
    common = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y"]
    output = ["-ac", "1", "-ar", "44100", "-b:a", "128k"]
    run([*common, "-i", str(SOURCE), "-af", DRY_FILTER, *output, str(DRY)], DRY)
    run([*common, "-i", str(SOURCE), "-filter_complex", CHARACTER_FILTER,
         "-map", "[out]", *output, str(CHARACTER)], CHARACTER)
    call_filter = (
        "[0:a]aformat=channel_layouts=mono,loudnorm=I=-21:TP=-3:LRA=11[call];"
        "anullsrc=r=44100:cl=mono:d=0.25[gap];"
        "[1:a]anull[voice];"
        "[call][gap][voice]concat=n=3:v=0:a=1[out]"
    )
    run([*common, "-i", str(CALL), "-i", str(CHARACTER),
         "-filter_complex", call_filter, "-map", "[out]", *output, str(WITH_CALL)], WITH_CALL)
    original_duration = duration(SOURCE)
    for target in (DRY, CHARACTER):
        if abs(duration(target) - original_duration) > 0.08:
            raise ValueError(f"Duration drifted: {target.name}")
    dry_lufs, dry_peak = measure(DRY)
    character_lufs, character_peak = measure(CHARACTER)
    if abs(dry_lufs - character_lufs) > 0.3:
        raise ValueError("Voice-only comparison is not loudness matched")
    if max(dry_peak, character_peak) > -1.3:
        raise ValueError("Comparison has excessive true peak")
    manifest = {
        "purpose": "Adult-voice Elephant treatment audition only; not final JR_NNN cues",
        "source_voice": "Ravi",
        "source_voice_id": "FF20guQVlAWTxmSRcTSk",
        "source_file": SOURCE.name,
        "source_cues": ["JR_053", "JR_062", "JR_063", "JR_065"],
        "approved_elephant_call": str(CALL.relative_to(HERE)),
        "options": [
            {"file": DRY.name, "type": "adult voice, loudness matched", "duration_seconds": duration(DRY),
             "integrated_lufs": dry_lufs, "true_peak_dbfs": dry_peak, "filter": DRY_FILTER},
            {"file": CHARACTER.name, "type": "adult voice with light Elephant character treatment",
             "duration_seconds": duration(CHARACTER), "integrated_lufs": character_lufs,
             "true_peak_dbfs": character_peak, "filter": CHARACTER_FILTER},
            {"file": WITH_CALL.name, "type": "treated voice after approved Elephant call",
             "duration_seconds": duration(WITH_CALL), "filter": call_filter},
        ],
        "note": "The adult source was a previous flat TTS audition. Processing adds body but cannot create a more expressive performance; a newly acted adult take may improve the result.",
    }
    target = OUT / "elephant_adult_treatment_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
