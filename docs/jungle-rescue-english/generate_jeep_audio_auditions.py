#!/usr/bin/env python3
"""Build focused, reversible Lion-scene Jeep auditions without changing JR_103."""

import json
import os
import subprocess
from pathlib import Path

from generate_elephant_rescue_test import FORMAT, request_audio
from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio" / "lion-rescue-test" / "jeep-auditions"
RAW = OUT / "raw"
ELEPHANT_JEEP = HERE / "audio" / "elephant-rescue-test" / "JR_021.mp3"
LION_AUDIO = HERE / "audio" / "lion-rescue-test"
PROMPTS = {
    "engine_drive": (
        "Close, dry field recording of a small open-top four-wheel-drive Jeep's gasoline engine "
        "running while it moves slowly. Clearly audible low-mid four-cylinder combustion chug, "
        "a slight rev and mechanical vibration; it must sound like a real off-road vehicle engine "
        "throughout. No tires, gravel, birds, voices, music, horn, other cars, or ambient jungle.",
        4.0,
    ),
    "tire_gravel": (
        "Close recording of four thick off-road Jeep tires rolling steadily across a dry dirt "
        "track with small stones. Rhythmic gravel crunch and light loose-chassis rattle for three "
        "seconds. No engine, voices, footsteps, music, horn, or background ambience.",
        3.0,
    ),
    "brake_engine_off": (
        "One realistic small Jeep arrival and stop, heard close: tires slow and gently crunch "
        "gravel, a brief soft brake squeak, suspension settles, then the petrol engine winds down "
        "and switches fully off with a short mechanical click. Clear final silence. No horn, "
        "crash, voices, music, birds, or jungle ambience.",
        1.7,
    ),
}


def raw_asset(name, prompt, seconds, key):
    path = RAW / f"{name}.mp3"
    body = {"text": prompt, "model_id": "eleven_text_to_sound_v2",
            "duration_seconds": seconds, "prompt_influence": 0.85, "loop": False}
    record = RAW / f"{name}.request.json"
    if path.is_file():
        if json.loads(record.read_text(encoding="utf-8")) != body:
            raise ValueError(f"Cached request changed for {name}; use a revision name")
        print(f"Existing {name}", flush=True)
        return path
    url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
    path.write_bytes(request_audio(url, key, body))
    record.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {name}", flush=True)
    return path


def mix(inputs, filter_graph, target):
    command = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y"]
    for source in inputs:
        command += ["-i", str(source)]
    command += ["-filter_complex", filter_graph, "-map", "[out]", "-ac", "1",
                "-ar", "44100", "-b:a", "128k", str(target)]
    subprocess.run(command, check=True)


def main():
    if not ELEPHANT_JEEP.is_file():
        raise FileNotFoundError(ELEPHANT_JEEP)
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    RAW.mkdir(parents=True, exist_ok=True)
    sources = {name: raw_asset(name, *spec, key)
               for name, spec in PROMPTS.items()}

    # C keeps the same moving-Jeep texture the child heard in the Elephant scene.
    c = OUT / "jeep_c_story_continuity.mp3"
    mix([ELEPHANT_JEEP, sources["brake_engine_off"]],
        "[0:a]atrim=start=0.3:end=3.5,asetpts=PTS-STARTPTS,volume=1.15,"
        "afade=t=out:st=2.6:d=0.6[drive];"
        "[1:a]adelay=2550,volume=0.95[stop];"
        "[drive][stop]amix=inputs=2:duration=longest:normalize=0,"
        "loudnorm=I=-18:TP=-3:LRA=11,alimiter=limit=0.75:level=false,"
        "volume=1.2,alimiter=limit=0.75:level=false[out]", c)

    # D uses separately controllable engine, tires and stop to make the Jeep legible.
    d = OUT / "jeep_d_layered_engine.mp3"
    mix([sources["engine_drive"], sources["tire_gravel"], sources["brake_engine_off"]],
        "[0:a]atrim=end=3.5,asetpts=PTS-STARTPTS,volume=1.15,"
        "afade=t=out:st=2.8:d=0.7[engine];"
        "[1:a]atrim=end=3.0,asetpts=PTS-STARTPTS,volume=0.50,"
        "adelay=300,afade=t=out:st=2.7:d=0.3[gravel];"
        "[2:a]adelay=2750,volume=0.95[stop];"
        "[engine][gravel][stop]amix=inputs=3:duration=longest:normalize=0,"
        "loudnorm=I=-18:TP=-3:LRA=11,alimiter=limit=0.75:level=false,"
        "volume=1.3,alimiter=limit=0.75:level=false[out]", d)

    manifest = {
        "purpose": "Jeep-only auditions for the Lion scene; no candidate is selected for JR_103",
        "candidates": {},
        "components": {name: {"file": f"raw/{name}.mp3", "prompt": prompt,
                              "duration_seconds": seconds}
                       for name, (prompt, seconds) in PROMPTS.items()},
    }
    for letter, path, description in [
        ("C", c, "Existing Elephant-scene Jeep texture plus a distinct stop"),
        ("D", d, "New close engine, rolling gravel and distinct stop layered separately"),
    ]:
        loudness, peak = measure(path)
        manifest["candidates"][letter] = {
            "file": path.name, "description": description,
            "duration_seconds": duration(path), "integrated_lufs": loudness,
            "true_peak_dbfs": peak, "review_status": "audition_only",
        }
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved Jeep auditions", flush=True)


if __name__ == "__main__":
    main()
