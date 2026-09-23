#!/usr/bin/env python3
"""Make reversible, loudness-matched A/B auditions for Vardan's Elephant voice.

The main voice stays at its original pitch. A quiet, slightly lower-pitched
body layer adds roundness; no pitch-shifted layer replaces the clear speech.
Run this only for auditions, not final JR_NNN production assets.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from generate_voice_auditions import duration


HERE = Path(__file__).resolve().parent
OUT = HERE / "voice_auditions"
SOURCE = OUT / "elephant_vardan_playful.mp3"
DRY = OUT / "elephant_vardan_levelmatched.mp3"
TREATED = OUT / "elephant_vardan_treated.mp3"


def ffmpeg():
    explicit = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if explicit:
        return explicit
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def render(source, target, filter_args):
    if target.exists():
        print(f"Existing: {target.name}; skipping")
        return
    command = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
               *filter_args, "-ac", "1", "-ar", "44100", "-b:a", "128k", str(target)]
    subprocess.run(command, check=True)
    print(f"Rendered: {target.name}")


def measure(path):
    command = [ffmpeg(), "-hide_banner", "-nostats", "-i", str(path),
               "-af", "ebur128=peak=true", "-f", "null", "-"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    loudness = re.search(r"Integrated loudness:\s+I:\s+(-?[\d.]+) LUFS", result.stderr)
    peak = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+) dBFS", result.stderr)
    if not loudness or not peak:
        raise ValueError(f"Could not measure {path.name}")
    return float(loudness.group(1)), float(peak.group(1))


def main():
    if not SOURCE.is_file():
        raise SystemExit(f"Missing source: {SOURCE}")
    dry_filter = "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95"
    treated_filter = (
        "[0:a]asplit=2[clear0][body0];"
        "[clear0]highpass=f=110,equalizer=f=600:t=q:w=1.1:g=2,"
        "equalizer=f=2500:t=q:w=0.9:g=1.5[clear];"
        "[body0]asetrate=41454,aresample=44100,atempo=1.0638298,"
        "highpass=f=350,lowpass=f=950,volume=0.12[body];"
        "[clear][body]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
    )
    render(SOURCE, DRY, ["-af", dry_filter])
    render(SOURCE, TREATED, ["-filter_complex", treated_filter, "-map", "[out]"])
    original_duration = duration(SOURCE)
    for target in (DRY, TREATED):
        if abs(duration(target) - original_duration) > 0.08:
            raise ValueError(f"Duration drifted: {target.name}")
    dry_loudness, dry_peak = measure(DRY)
    treated_loudness, treated_peak = measure(TREATED)
    if abs(dry_loudness - treated_loudness) > 0.3:
        raise ValueError("Comparison is not loudness matched")
    if max(dry_peak, treated_peak) > -1.3:
        raise ValueError("Comparison has excessive true peak")
    manifest = {
        "purpose": "Elephant Vardan treatment A/B only; not final JR_NNN cues",
        "source_file": SOURCE.name,
        "source_duration_seconds": original_duration,
        "comparison": [
            {"file": DRY.name, "duration_seconds": duration(DRY),
             "integrated_lufs": dry_loudness, "true_peak_dbfs": dry_peak,
             "processing": "loudness match only", "filter": dry_filter},
            {"file": TREATED.name, "duration_seconds": duration(TREATED),
             "integrated_lufs": treated_loudness, "true_peak_dbfs": treated_peak,
             "processing": "light warmth EQ, quiet detuned body layer, then loudness match",
             "filter": treated_filter,
             "note": "The clear main voice remains at original pitch; the body layer uses a simple pitch shift and stays quiet."},
        ],
        "output_format": "44.1 kHz mono MP3, 128 kbps",
    }
    target = OUT / "elephant_treatment_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
