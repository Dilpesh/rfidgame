#!/usr/bin/env python3
"""Generate A/B replacements for Elephant-scene jeep bumps and rope effort."""

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio" / "elephant-rescue-test" / "alternatives"
RAW = OUT / "raw"
FORMAT = "mp3_44100_128"
REQUESTS = {
    "bump_a_1": ("A real small jeep rolls over one low rounded dirt-road hump: muted tire thump and soft suspension compression and rebound. Gentle, child-friendly, no crash, no horn, no voice, no music.", 0.7),
    "bump_a_2": ("A real small jeep rolls over a medium rounded dirt-road hump: firmer tire thump, clear suspension compression and rebound, and one tiny cabin rattle. Safe, no crash, no horn, no voice, no music.", 0.9),
    "bump_a_3": ("A real small jeep crosses two rounded dirt-road humps quickly: two clear tire-and-suspension thumps with a playful bounce and brief cabin rattle. Safe, no crash, no horn, no voice, no music.", 1.2),
    "bump_b_1": ("One soft playful rescue-jeep bounce over a jungle path bump: rubber tire thud followed by a light suspension wobble. Warm cartoon realism, no spring boing, no crash, no voice, no music.", 0.7),
    "bump_b_2": ("One bigger playful rescue-jeep bounce over a jungle path bump: deeper rubber tire thud, suspension wobble, short harmless body rattle. Warm cartoon realism, no spring boing, no crash, no voice, no music.", 0.9),
    "bump_b_3": ("A quick double rescue-jeep bounce over two jungle path bumps: two rhythmic rubber tire thuds and a funny suspension wobble. Warm cartoon realism, no spring boing, no crash, no voice, no music.", 1.2),
    "rope_a": ("A thick natural rope is pulled tight by several people: one short textured fibre strain and sturdy tension creak. Clear physical effort, no snapping, no wood, no voice, no music.", 0.9),
    "rope_b": ("A thick rescue rope goes taut during one strong tug: short low rope tension groan with a little gritty fibre movement. Strong but safe, no snapping, no wood, no voice, no music.", 0.9),
}


def request_audio(key, text, seconds):
    body = {"text": text, "model_id": "eleven_text_to_sound_v2",
            "duration_seconds": seconds, "prompt_influence": 0.9, "loop": False}
    request = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}",
        json.dumps(body).encode("utf-8"),
        {"xi-api-key": key, "content-type": "application/json", "accept": "audio/mpeg"},
        method="POST")
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"ElevenLabs HTTP {error.code}: {detail}") from error
    if not data.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        raise ValueError("ElevenLabs response was not an MP3")
    return data


def normalize(source, target):
    temporary = OUT / f".{target.stem}.rendering.mp3"
    audio_filter = "loudnorm=I=-20:TP=-4:LRA=11,alimiter=limit=0.63:level=false"
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                    "-af", audio_filter, "-ac", "1", "-ar", "44100", "-b:a", "128k",
                    str(temporary)], check=True)
    os.replace(temporary, target)


def sequence(option):
    target = OUT / f"bump_{option}_sequence.mp3"
    graph = (
        "[0:a]aformat=channel_layouts=mono[a0];"
        "anullsrc=r=44100:cl=mono:d=0.16[g0];"
        "[1:a]aformat=channel_layouts=mono[a1];"
        "anullsrc=r=44100:cl=mono:d=0.16[g1];"
        "[2:a]aformat=channel_layouts=mono[a2];"
        "[a0][g0][a1][g1][a2]concat=n=5:v=0:a=1[out]"
    )
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(OUT / f"bump_{option}_1.mp3"),
                    "-i", str(OUT / f"bump_{option}_2.mp3"),
                    "-i", str(OUT / f"bump_{option}_3.mp3"),
                    "-filter_complex", graph, "-map", "[out]", "-ac", "1", "-ar", "44100",
                    "-b:a", "128k", str(target)], check=True)


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    manifest = {"purpose": "Replacement auditions only; current production-test SFX remain unchanged",
                "model_id": "eleven_text_to_sound_v2", "options": {}}
    for name, (prompt, seconds) in REQUESTS.items():
        raw = RAW / f"{name}.mp3"
        if not raw.exists():
            raw.write_bytes(request_audio(key, prompt, seconds))
            print(f"Generated: raw/{raw.name}", flush=True)
        else:
            print(f"Existing: raw/{raw.name}; skipping charged generation", flush=True)
        target = OUT / f"{name}.mp3"
        normalize(raw, target)
        lufs, peak = measure(target)
        manifest["options"][name] = {"file": target.name, "prompt": prompt,
                                      "duration_seconds": duration(target),
                                      "integrated_lufs": lufs, "true_peak_dbfs": peak}
    for option in ("a", "b"):
        sequence(option)
        target = OUT / f"bump_{option}_sequence.mp3"
        lufs, peak = measure(target)
        manifest["options"][f"bump_{option}_sequence"] = {
            "file": target.name, "parts": [f"bump_{option}_{n}.mp3" for n in (1, 2, 3)],
            "duration_seconds": duration(target), "integrated_lufs": lufs,
            "true_peak_dbfs": peak, "preview_only": True}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    print(f"Saved {OUT / 'manifest.json'}", flush=True)


if __name__ == "__main__":
    main()
