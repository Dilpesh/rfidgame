#!/usr/bin/env python3
"""Build natural/light Vardan comparisons from the same revised biscuit takes."""
import json
import subprocess
import wave

from generate_elephant_rescue_test import OUT, RAW, LIGHT_FILTER, parse_cues
from make_elephant_treatment import ffmpeg, measure


def main():
    folder = OUT / "audition-childlike-v2"
    folder.mkdir(exist_ok=True)
    ids = [f"JR_{n:03d}" for n in (62, 63, 64, 65)]
    texts = parse_cues()
    metadata = {"purpose": "Natural and light-EQ Vardan audition; identical updated takes",
                "voice_id": "bBG9wwa23659EgIkMbc1",
                "spoken_text": {cue: texts[cue][1] for cue in ids}, "options": {}}
    for variant in ("natural", "light"):
        graph, inputs, segments = [], [], []
        processing = LIGHT_FILTER if variant == "light" else "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false"
        for index, cue in enumerate(ids):
            source = RAW / f"{cue}_v2.mp3"
            if not source.is_file():
                raise FileNotFoundError(source)
            inputs += ["-i", str(source)]
            graph.append(f"[{index}:a]{processing},aformat=sample_rates=44100:channel_layouts=mono[a{index}]")
            segments.append(f"[a{index}]")
            if index < 3:
                graph.append(f"anullsrc=r=44100:cl=mono:d=0.45[g{index}]")
                segments.append(f"[g{index}]")
        graph.append("".join(segments) + "concat=n=7:v=0:a=1[out]")
        path = folder / f"elephant_{variant}.wav"
        subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", *inputs,
                        "-filter_complex", ";".join(graph), "-map", "[out]", "-ar", "44100",
                        "-ac", "1", "-c:a", "pcm_s16le", str(path)], check=True)
        lufs, peak = measure(path)
        with wave.open(str(path)) as audio:
            length = audio.getnframes() / audio.getframerate()
        metadata["options"][variant] = {"file": path.name, "filter": processing,
                                          "duration_seconds": round(length, 3),
                                          "integrated_lufs": lufs, "true_peak_dbfs": peak}
        print(variant, metadata["options"][variant], flush=True)
    (folder / "manifest.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
