#!/usr/bin/env python3
"""Generate the first production-audio test: Introduction plus Fuel.

Creates separate JR_NNN MP3 assets and a partial manifest in
audio/intro-fuel-test/. Existing generated assets are never charged again.
This is a review batch; approved files can later be promoted to lossless final
delivery assets.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "jungle_rescue_final_production_script.md"
OUT = HERE / "audio" / "intro-fuel-test"
RAW = OUT / "raw"
MODEL = "eleven_v3"
FORMAT = "mp3_44100_128"
VOICE_IDS = {
    "COCO": "d9BvEI0bp2Tmdpqnjwn0",
    "NARRATOR": "ItmwhOeluca31IEX91Yk",
}
VOICE_SETTINGS = {
    "COCO": {"stability": 0.40, "similarity_boost": 0.78, "style": 0.28,
             "use_speaker_boost": True},
    "NARRATOR": {"stability": 0.56, "similarity_boost": 0.78, "style": 0.12,
                 "use_speaker_boost": True},
}
SPEECH = {
    "JR_002": ("COCO", "[bright and playful]"),
    "JR_003": ("COCO", "[hopeful and inviting]"),
    "JR_004": ("COCO", "[delighted and encouraging]"),
    "JR_005": ("COCO", "[warm storytelling]"),
    "JR_007": ("NARRATOR", "[warm and brisk]"),
    "JR_009": ("COCO", "[surprised and amused]"),
    "JR_010": ("COCO", "[curious and clear]"),
    "JR_011": ("COCO", "[kind and clear]"),
    "JR_012": ("COCO", "[kind and clear]"),
    "JR_013": ("COCO", "[kind and clear]"),
    "JR_015": ("COCO", "[excited]"),
    "JR_018": ("COCO", "[energetic rallying call]"),
    "JR_020": ("COCO", "[comic surprise and affection]"),
}
REUSED = {
    "JR_001": "old_sfx_jungle_day.mp3",
    "JR_014": "shipped_ting.mp3",
    "JR_016": "old_sfx_fuel.mp3",
    "JR_017": "old_sfx_engine.mp3",
}
SFX_REQUESTS = {
    "JR_006": {
        "text": "Quick light rescue jeep door opening: handle click, short friendly door movement, one neat stop. No engine, no horn, no voices, no music.",
        "duration_seconds": 1.2,
    },
    "JR_008_key": {
        "text": "A car ignition key turns once with a small mechanical click and a brief starter attempt. No running engine, no horn, no voices, no music.",
        "duration_seconds": 0.8,
    },
    "JR_019": {
        "text": "One tiny bubbly liquid overflow bloop, cute and comic, like one drop popping over a container rim. Not an alarm, no voices, no music.",
        "duration_seconds": 0.7,
    },
}


def cues():
    source = SCRIPT.read_text(encoding="utf-8")
    result = {}
    for section in re.split(r"(?=\*\*JR_\d+ ·)", source):
        match = re.match(r"\*\*(JR_\d+) · ([A-Z]+)", section)
        if not match:
            continue
        lines = [line.strip()[2:] for line in section.splitlines()
                 if line.strip().startswith("> ")]
        if lines:
            result[match.group(1)] = (match.group(2), " ".join(lines))
    return result


def request_audio(url, key, body):
    request = urllib.request.Request(
        url,
        json.dumps(body, ensure_ascii=False).encode("utf-8"),
        {"xi-api-key": key, "content-type": "application/json", "accept": "audio/mpeg"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"ElevenLabs HTTP {error.code}: {detail}") from error
    if not data.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        raise ValueError("ElevenLabs response was not an MP3")
    return data


def write_once(path, data):
    if path.exists():
        print(f"Existing: {path.name}; skipping charged generation")
        return
    path.write_bytes(data)
    print(f"Generated: {path.name}")


def copy_once(source, target):
    if target.exists():
        if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(source.read_bytes()).digest():
            raise ValueError(f"Existing reused asset changed: {target}")
        return
    shutil.copyfile(source, target)


def preserve_existing_raw(cue_id):
    """Migrate the first generated review files into the raw-source folder once."""
    raw = RAW / f"{cue_id}.mp3"
    derived = OUT / f"{cue_id}.mp3"
    if not raw.exists() and derived.exists():
        shutil.copyfile(derived, raw)
    return raw


def normalize(source, target, integrated_lufs, true_peak):
    """Create a level-matched review derivative while keeping source untouched."""
    temporary = OUT / f".{target.stem}.normalizing.mp3"
    # MP3 encoding can overshoot sharp effects; leave extra headroom for short SFX.
    limiter = 0.72 if integrated_lufs <= -18 else 0.90
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                    "-af", f"loudnorm=I={integrated_lufs}:TP={true_peak}:LRA=11,alimiter=limit={limiter}:level=false",
                    "-ac", "1", "-ar", "44100", "-b:a", "128k", str(temporary)], check=True)
    os.replace(temporary, target)


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    parsed = cues()
    for cue_id in SPEECH:
        role, tag = SPEECH[cue_id]
        actual_role, spoken = parsed[cue_id]
        if actual_role != role:
            raise ValueError(f"{cue_id} speaker changed from {role} to {actual_role}")
        raw = preserve_existing_raw(cue_id)
        if not raw.exists():
            body = {"text": f"{tag} {spoken}", "model_id": MODEL,
                    "voice_settings": VOICE_SETTINGS[role]}
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[role]}?output_format={FORMAT}"
            write_once(raw, request_audio(url, key, body))
        else:
            print(f"Existing: raw/{raw.name}; skipping charged generation")
        normalize(raw, OUT / f"{cue_id}.mp3", -16, -1.5)

    candidates = HERE / "audio_candidates"
    copy_once(candidates / REUSED["JR_001"], OUT / "JR_001.mp3")
    for cue_id in ("JR_014", "JR_016", "JR_017"):
        normalize(candidates / REUSED[cue_id], OUT / f"{cue_id}.mp3", -18, -2)

    for cue_id, item in SFX_REQUESTS.items():
        raw = preserve_existing_raw(cue_id)
        if not raw.exists():
            body = {"text": item["text"], "model_id": "eleven_text_to_sound_v2",
                    "duration_seconds": item["duration_seconds"], "prompt_influence": 0.8,
                    "loop": False}
            url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
            write_once(raw, request_audio(url, key, body))
        else:
            print(f"Existing: raw/{raw.name}; skipping charged generation")

    # Combine the newly generated key turn with the approved engine-cough asset.
    engine_cough = candidates / "shipped_engineCough.mp3"
    raw_jr008 = preserve_existing_raw("JR_008")
    if not raw_jr008.exists():
        graph = (
            "[0:a]aformat=channel_layouts=mono,loudnorm=I=-20:TP=-3:LRA=11[key];"
            "anullsrc=r=44100:cl=mono:d=0.06[gap];"
            "[1:a]aformat=channel_layouts=mono,loudnorm=I=-18:TP=-2:LRA=11[cough];"
            "[key][gap][cough]concat=n=3:v=0:a=1[out]"
        )
        subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                        "-i", str(RAW / "JR_008_key.mp3"), "-i", str(engine_cough),
                        "-filter_complex", graph, "-map", "[out]", "-ac", "1", "-ar", "44100",
                        "-b:a", "128k", str(raw_jr008)], check=True)

    normalize(RAW / "JR_006.mp3", OUT / "JR_006.mp3", -18, -2)
    normalize(raw_jr008, OUT / "JR_008.mp3", -18, -2)
    normalize(RAW / "JR_019.mp3", OUT / "JR_019.mp3", -18, -2)

    manifest = {}
    for cue_id in ["JR_001", "JR_002", "JR_003", "JR_004", "JR_005", "JR_006", "JR_007",
                   "JR_008", "JR_009", "JR_010", "JR_011", "JR_012", "JR_013", "JR_014",
                   "JR_015", "JR_016", "JR_017", "JR_018", "JR_019", "JR_020"]:
        path = OUT / f"{cue_id}.mp3"
        if not path.is_file():
            raise FileNotFoundError(path)
        lufs, peak = measure(path)
        item = {"file": f"intro-fuel-test/{path.name}",
                "duration_seconds": duration(path), "integrated_lufs": lufs,
                "true_peak_dbfs": peak, "review_status": "test"}
        if cue_id in SPEECH:
            role, tag = SPEECH[cue_id]
            item.update({"type": "speech", "voice": role, "voice_id": VOICE_IDS[role],
                         "model_id": MODEL, "voice_settings": VOICE_SETTINGS[role],
                         "spoken_text": parsed[cue_id][1], "performance_tag": tag})
        else:
            item["type"] = "sfx"
        if cue_id == "JR_001":
            item.update({"bed": True, "loop": True})
        manifest[cue_id] = item
    manifest["_batch"] = {
        "name": "Introduction and Fuel production test",
        "format": FORMAT,
        "script": SCRIPT.name,
        "note": "Review MP3 batch. Approved final delivery will use the production asset contract.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    print(f"Saved {OUT / 'manifest.json'}")


if __name__ == "__main__":
    main()
