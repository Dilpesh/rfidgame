#!/usr/bin/env python3
"""Generate a small, reproducible ElevenLabs cast audition from approved cue text.

Run without arguments to see the exact source cues and total characters.
Run with --generate to create missing MP3s. Existing clips are never regenerated.
Requires ELEVENLABS_API_KEY in the environment; the key is never saved here.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "jungle_rescue_final_production_script.md"
OUT = HERE / "voice_auditions"
MODEL = "eleven_v3"
SETTINGS = {"stability": 0.5, "similarity_boost": 0.75, "style": 0, "use_speaker_boost": True}
OUTPUT_FORMAT = "mp3_44100_128"
REFERENCE_TEXT = (
    "हैलो किशु मिशु! मैं हूँ कोको। आज हम जंगल बचाओ टीम बनेंगे! "
    "जंगल में हमारे कई दोस्त मुसीबत में हैं, और हमें उन्हें बचाना है!"
)
SAANU_VOICE_ID = "d9BvEI0bp2Tmdpqnjwn0"

# IDs were listed from the user's ElevenLabs account on 23 September 2026.
# Two options per role; the final five-character cast must use distinct IDs.
TAKES = (
    ("COCO", "Vardan", "bBG9wwa23659EgIkMbc1", ("JR_002", "JR_003", "JR_026")),
    ("COCO", "Bholu", "5krdMTA5HonvWAlY2vSx", ("JR_002", "JR_003", "JR_026")),
    ("NARRATOR", "Jia", "ItmwhOeluca31IEX91Yk", ("JR_007", "JR_022", "JR_033")),
    ("NARRATOR", "Aashish", "8ISgMxQsDzugFB0wA3Gb", ("JR_007", "JR_022", "JR_033")),
    ("ELEPHANT", "Ravi", "FF20guQVlAWTxmSRcTSk", ("JR_053", "JR_062", "JR_063", "JR_065")),
    ("ELEPHANT", "Aashish", "8ISgMxQsDzugFB0wA3Gb", ("JR_053", "JR_062", "JR_063", "JR_065")),
    ("PARROT", "Munni", "VOGEEZj2Kly5dP9LrQy8", ("JR_075", "JR_091", "JR_099")),
    ("PARROT", "Saanu", "d9BvEI0bp2Tmdpqnjwn0", ("JR_075", "JR_091", "JR_099")),
    ("LION", "Bholu", "5krdMTA5HonvWAlY2vSx", ("JR_108", "JR_110", "JR_127", "JR_142")),
    ("LION", "Munni", "VOGEEZj2Kly5dP9LrQy8", ("JR_108", "JR_110", "JR_127", "JR_142")),
)


def script_cues():
    source = SCRIPT.read_text(encoding="utf-8")
    sections = re.split(r"(?=\*\*JR_\d+ ·)", source)
    cues = {}
    for section in sections:
        match = re.match(r"\*\*(JR_\d+) · ([A-Z]+)", section)
        if match:
            lines = [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("> ")]
            if lines:
                cues[match.group(1)] = (match.group(2), " ".join(lines))
    return cues


def duration(path):
    result = subprocess.run(["afinfo", str(path)], capture_output=True, text=True, check=True)
    match = re.search(r"estimated duration: ([\d.]+) sec", result.stdout)
    if not match:
        raise ValueError(f"No audio duration: {path}")
    return round(float(match.group(1)), 3)


def legacy_reference():
    source = (HERE.parent / "jungle-rescue-hinglish" / "index.html").read_text(encoding="utf-8")
    match = re.search(r"const media=(\{.*?\});", source, flags=re.DOTALL)
    if not match:
        raise ValueError("Cannot find shipped audio in old index.html")
    data = base64.b64decode(json.loads(match.group(1))["intro"], validate=True)
    target = OUT / "reference_shipped_intro.mp3"
    if target.exists() and target.read_bytes() != data:
        raise ValueError(f"Existing reference changed: {target}")
    target.write_bytes(data)
    return target


def make_take(key, voice_id, text, path):
    body = json.dumps({"text": text, "model_id": MODEL, "voice_settings": SETTINGS}, ensure_ascii=False).encode("utf-8")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format={OUTPUT_FORMAT}"
    request = urllib.request.Request(url, body, {
        "xi-api-key": key,
        "content-type": "application/json",
        "accept": "audio/mpeg",
    }, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=150) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"ElevenLabs HTTP {error.code}: {detail}") from error
    if not data.startswith((b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        raise ValueError(f"Response did not look like MP3 for {path.name}")
    path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="Generate missing ElevenLabs takes")
    args = parser.parse_args()
    cues = script_cues()
    plan = []
    for role, name, voice_id, ids in TAKES:
        for cue_id in ids:
            actual_role, _ = cues[cue_id]
            if actual_role != role:
                raise ValueError(f"{cue_id} changed speaker to {actual_role}")
        text = "\n\n".join(cues[cue_id][1] for cue_id in ids)
        plan.append({
            "role": role, "option": name, "voice_id": voice_id, "cue_ids": list(ids),
            "text": text, "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "file": f"{role.lower()}_{name.lower()}.mp3",
        })
    total = sum(len(item["text"]) for item in plan)
    print(f"{len(plan)} takes, {total} characters, model {MODEL}; no generation without --generate")
    for item in plan:
        print(f"  {item['role']:<8} {item['option']:<8} {len(item['text']):>3} chars -> {item['file']}")
    if not args.generate:
        return
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(exist_ok=True)
    reference = legacy_reference()
    print(f"Legacy Coco reference: {reference.name}", flush=True)
    comparison = OUT / "coco_saanu_reference_text.mp3"
    if comparison.exists():
        print(f"Existing: {comparison.name}; skipping charged generation", flush=True)
    else:
        print(f"Generating: {comparison.name}", flush=True)
        make_take(key, SAANU_VOICE_ID, REFERENCE_TEXT, comparison)
    for item in plan:
        path = OUT / item["file"]
        if path.exists():
            print(f"Existing: {path.name}; skipping charged generation", flush=True)
        else:
            print(f"Generating: {path.name}", flush=True)
            make_take(key, item["voice_id"], item["text"], path)
        item["duration_seconds"] = duration(path)
    confirmed_cast = {
        "COCO": {"voice": "Saanu", "voice_id": SAANU_VOICE_ID,
                 "reference_file": reference.name,
                 "note": "User confirmed the original Coco voice is Saanu; match the shipped clip's energy and tone."}
    }
    review_path = OUT / "casting_review.json"
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8"))
        for choice in review["results"]:
            if choice["role"] == "COCO" or choice["choice"] == "Neither":
                continue
            take = next((item for item in plan if item["role"] == choice["role"]
                         and item["option"] == choice["choice"]
                         and item["voice_id"] == choice["voice_id"]), None)
            if take is None:
                raise ValueError(f"Review choice does not match an audition: {choice}")
            confirmed_cast[choice["role"]] = {
                "voice": take["option"], "voice_id": take["voice_id"], "reference_file": take["file"]
            }
    manifest = {
        "purpose": "voice auditions only; these are not production JR_NNN cues",
        "model_id": MODEL, "voice_settings": SETTINGS, "output_format": OUTPUT_FORMAT,
        "script": SCRIPT.name,
        "confirmed_cast": confirmed_cast,
        "legacy_reference": {"file": reference.name, "duration_seconds": duration(reference),
                             "note": "Old shipped intro may contain obsolete personalized wording; voice comparison only."},
        "saanu_reference_comparison": {
            "file": comparison.name, "voice_id": SAANU_VOICE_ID,
            "text": REFERENCE_TEXT, "duration_seconds": duration(comparison),
            "note": "The same old opening words for voice comparison only; not a current production cue.",
        },
        "takes": plan,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {OUT / 'manifest.json'}", flush=True)


if __name__ == "__main__":
    main()
