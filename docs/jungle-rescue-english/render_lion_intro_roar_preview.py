#!/usr/bin/env python3
"""Render contiguous Lion entrance comparison clips; never changes production cues."""

import json
import subprocess
from pathlib import Path

from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
LION = HERE / "audio" / "lion-rescue-test"
OUT = LION / "intro-roar-auditions"
BEFORE_ROAR = ["JR_105", "JR_106"]
AFTER_ROAR = ["JR_107", "JR_108", "JR_109"]


def silence(path, seconds):
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(seconds),
                    "-ac", "1", "-ar", "44100", "-b:a", "128k", str(path)], check=True)


def render(name, roar=None):
    parts = [LION / f"{cue}.mp3" for cue in BEFORE_ROAR]
    if roar:
        parts += [OUT / "gap_before.mp3", OUT / f"roar_{roar}.mp3",
                  OUT / "gap_after.mp3"]
    parts += [LION / f"{cue}.mp3" for cue in AFTER_ROAR]
    parts.append(LION / "JR_110.mp3")
    bed = LION / "JR_103_bed.mp3"
    command = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y"]
    for part in parts:
        command += ["-i", str(part)]
    command += ["-stream_loop", "-1", "-i", str(bed)]
    graph = "".join(
        f"[{i}:a]aresample=44100,asetpts=N/SR/TB,volume={'1.26' if roar and part.name == f'roar_{roar}.mp3' else '1'}[p{i}];"
        for i, part in enumerate(parts)
    )
    graph += "".join(f"[p{i}]" for i in range(len(parts)))
    graph += f"concat=n={len(parts)}:v=0:a=1[fg];"
    graph += f"[{len(parts)}:a]volume=0.12[bed];"
    graph += "[fg][bed]amix=inputs=2:duration=first:normalize=0,"
    graph += "alimiter=limit=0.85:level=false[out]"
    target = OUT / f"entrance_{name}.mp3"
    command += ["-filter_complex", graph, "-map", "[out]", "-ac", "1",
                "-ar", "44100", "-b:a", "128k", str(target)]
    subprocess.run(command, check=True)
    loudness, peak = measure(target)
    return {"file": target.name, "duration_seconds": duration(target),
            "integrated_lufs": loudness, "true_peak_dbfs": peak,
            "roar": roar, "bed_gain": 0.12,
            "review_status": "audition_only"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    silence(OUT / "gap_before.mp3", 0.18)
    silence(OUT / "gap_after.mp3", 0.22)
    comparisons = {"baseline": render("baseline"),
                   "roar_a": render("roar_a", "a"),
                   "roar_b": render("roar_b", "b")}
    (OUT / "comparison_manifest.json").write_text(
        json.dumps({"purpose": "Single-file Lion introduction listening comparison",
                    "placement": "after JR_109, before JR_110",
                    "production_route_changed": False,
                    "clips": comparisons}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("Rendered three Lion entrance comparisons", flush=True)


if __name__ == "__main__":
    main()
