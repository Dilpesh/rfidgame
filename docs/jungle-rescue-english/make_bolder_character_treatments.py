#!/usr/bin/env python3
"""Render a clearly audible second-round Vardan/Bholu treatment audition."""

import json
import subprocess
from pathlib import Path

from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "voice_auditions"
JOBS = {
    "ELEPHANT": {
        "source": "elephant_vardan_playful.mp3",
        "output": "elephant_vardan_character_bold.mp3",
        "filter": (
            "[0:a]asplit=2[main0][body0];"
            "[main0]asetrate=39690,aresample=44100,atempo=1.111111,"
            "highpass=f=85,equalizer=f=280:t=q:w=1:g=4,"
            "equalizer=f=2800:t=q:w=1:g=1[main];"
            "[body0]asetrate=33075,aresample=44100,atempo=1.333333,"
            "highpass=f=180,lowpass=f=650,volume=0.36[body];"
            "[main][body]amix=inputs=2:duration=first:normalize=0,"
            "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
        ),
    },
    "LION": {
        "source": "lion_bholu.mp3",
        "output": "lion_bholu_character_bold.mp3",
        "filter": (
            "[0:a]asplit=2[main0][growl0];"
            "[main0]asetrate=40572,aresample=44100,atempo=1.086956,"
            "highpass=f=95,equalizer=f=350:t=q:w=1:g=3,"
            "equalizer=f=2600:t=q:w=1:g=1[main];"
            "[growl0]asetrate=35280,aresample=44100,atempo=1.25,"
            "highpass=f=200,lowpass=f=900,volume=2,"
            "asoftclip=type=tanh:threshold=0.35:oversample=4,"
            "volume=0.25[growl];"
            "[main][growl]amix=inputs=2:duration=first:normalize=0,"
            "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
        ),
    },
}


def main():
    manifest = {"purpose": "Second-round bolder character auditions; not final JR_NNN cues", "roles": {}}
    for role, job in JOBS.items():
        source, output = OUT / job["source"], OUT / job["output"]
        if not source.is_file():
            raise FileNotFoundError(source)
        if not output.exists():
            subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                            "-filter_complex", job["filter"], "-map", "[out]", "-ac", "1", "-ar", "44100",
                            "-b:a", "128k", str(output)], check=True)
        if abs(duration(output) - duration(source)) > 0.15:
            raise ValueError(f"Duration drifted for {role}")
        lufs, peak = measure(output)
        if peak > -1.2:
            raise ValueError(f"Peak too high for {role}: {peak}")
        manifest["roles"][role] = {"source_file": source.name, "treated_file": output.name,
                                   "duration_seconds": duration(output), "integrated_lufs": lufs,
                                   "true_peak_dbfs": peak, "filter": job["filter"]}
        print(f"{role}: {output.name}, {lufs} LUFS, {peak} dBTP")
    (OUT / "bold_character_treatments_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
