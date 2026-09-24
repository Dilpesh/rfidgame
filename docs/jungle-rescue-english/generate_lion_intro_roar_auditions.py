#!/usr/bin/env python3
"""Generate short Lion King entrance-roar auditions without changing the story route."""

import json
import os
import subprocess
from pathlib import Path

from generate_elephant_rescue_test import FORMAT, request_audio
from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio" / "lion-rescue-test" / "intro-roar-auditions"
RAW = OUT / "raw"
CUES = {
    "roar_a": (
        "One unmistakable but gentle young lion roar from nearby: a rounded chesty growl rises "
        "into a small warm 'rawwr' and fades cleanly. The lion has just been recognized by a "
        "friend; he is shy and safe, not attacking. Natural feline lion resonance, no human "
        "voice or words, no cat meow, no harsh scream, no adult jungle attack, no thunder or music.",
        1.35,
    ),
    "roar_b": (
        "A young Lion King gives one brief proud but child-friendly roar: low soft rumble, "
        "clearly leonine open-mouthed 'rrraow', then a friendly short tail. Distinct lion sound "
        "that reads on a laptop speaker, expressive but not loud or frightening. No human "
        "speech, no generic dog growl, no house-cat meow, no attack, no music or ambience.",
        1.5,
    ),
}


def generate(name, prompt, seconds, key):
    body = {"text": prompt, "model_id": "eleven_text_to_sound_v2",
            "duration_seconds": seconds, "prompt_influence": 0.9, "loop": False}
    raw = RAW / f"{name}.mp3"
    record = RAW / f"{name}.request.json"
    if raw.is_file():
        if json.loads(record.read_text(encoding="utf-8")) != body:
            raise ValueError(f"Changed request for {name}; use a new revision name")
        print(f"Existing {name}", flush=True)
    else:
        url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
        raw.write_bytes(request_audio(url, key, body))
        record.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")
        print(f"Generated {name}", flush=True)
    target = OUT / f"{name}.mp3"
    subprocess.run([
        ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw),
        "-af", "afade=t=in:st=0:d=0.07,loudnorm=I=-17.5:TP=-4:LRA=11,"
               "alimiter=limit=0.63:level=false,volume=0.75",
        "-ac", "1", "-ar", "44100", "-b:a", "128k", str(target),
    ], check=True)
    loudness, peak = measure(target)
    return {"file": target.name, "source_file": f"raw/{name}.mp3",
            "prompt": prompt, "duration_seconds": duration(target),
            "integrated_lufs": loudness, "true_peak_dbfs": peak,
            "review_status": "audition_only"}


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    RAW.mkdir(parents=True, exist_ok=True)
    assets = {name: generate(name, *spec, key) for name, spec in CUES.items()}
    manifest = {"purpose": "After-Coco-recognizes-Lion entrance SFX auditions only; no script or route change",
                "placement": "after JR_109, before JR_110",
                "assets": assets}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)
                                       + "\n", encoding="utf-8")
    print("Saved Lion entrance roar auditions", flush=True)


if __name__ == "__main__":
    main()
