#!/usr/bin/env python3
"""Generate only the second-round Elephant voice auditions.

Run without arguments to inspect the exact generation plan. Run with --generate
to create missing MP3s; existing takes are never regenerated.
"""

import argparse
import json
import os
from generate_voice_auditions import MODEL, OUTPUT_FORMAT, OUT, SETTINGS, duration, make_take


TAKES = (
    {
        "name": "Vardan — bouncy and hungry",
        "voice_id": "bBG9wwa23659EgIkMbc1",
        "file": "elephant_vardan_playful.mp3",
        "text": (
            "[playfully] मेरे पेट में भूख से चूहे दौड़ रहे हैं।\n\n"
            "[excited] बस एक!\n\n"
            "[mischievously] बस दो... थोड़ा और दो!\n\n"
            "[surprised] चार! बस करो, Captain! इतना खाऊँगा तो balloon बनकर उड़ जाऊँगा!"
        ),
    },
    {
        "name": "Bholu — gentle and cheeky",
        "voice_id": "5krdMTA5HonvWAlY2vSx",
        "file": "elephant_bholu_playful.mp3",
        "text": (
            "[warmly] मेरे पेट में भूख से चूहे दौड़ रहे हैं।\n\n"
            "[eagerly] बस एक!\n\n"
            "[mischievously] बस दो... थोड़ा और दो!\n\n"
            "[laughing] चार! बस करो, Captain! इतना खाऊँगा तो balloon बनकर उड़ जाऊँगा!"
        ),
    },
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    print(f"Elephant round 2: {len(TAKES)} takes, {sum(len(t['text']) for t in TAKES)} characters")
    for take in TAKES:
        print(f"  {take['name']}: {take['file']} ({len(take['text'])} characters)")
    if not args.generate:
        return
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(exist_ok=True)
    manifest_takes = []
    for take in TAKES:
        path = OUT / take["file"]
        if path.exists():
            print(f"Existing: {path.name}; skipping charged generation", flush=True)
        else:
            print(f"Generating: {path.name}", flush=True)
            make_take(key, take["voice_id"], take["text"], path)
        manifest_takes.append({**take, "duration_seconds": duration(path)})
    manifest = {
        "purpose": "Second-round Elephant auditions only; not final JR_NNN cues",
        "feedback": "Ravi and Aashish sounded too adult and flat",
        "source_cues": ["JR_053", "JR_062", "JR_063", "JR_065"],
        "model_id": MODEL,
        "voice_settings": SETTINGS,
        "output_format": OUTPUT_FORMAT,
        "takes": manifest_takes,
    }
    target = OUT / "elephant_round2_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
