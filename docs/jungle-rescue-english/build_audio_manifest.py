#!/usr/bin/env python3
"""Combine the reviewed scene manifests into the player manifest."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
AUDIO = HERE / "audio"
SCENES = (
    "intro-fuel-test",
    "elephant-rescue-test",
    "parrot-rescue-test",
    "lion-rescue-test",
    "celebration-test",
)


def main():
    combined = {
        "_build": {
            "story": "Jungle Rescue English",
            "scenes": list(SCENES),
            "source": "scene manifests generated beside each audio batch",
        }
    }
    for scene in SCENES:
        source = AUDIO / scene / "manifest.json"
        data = json.loads(source.read_text(encoding="utf-8"))
        for cue_id, entry in data.items():
            if cue_id.startswith("_"):
                continue
            combined[cue_id] = entry
            if cue_id in {"JR_001", "JR_021"}:
                combined[cue_id]["volume"] = 0.18
            if entry.get("type") != "split_sfx":
                continue
            combined[f"{cue_id}_entry"] = {
                "file": entry["entry_file"],
                "type": "sfx",
                "source_split_cue": cue_id,
            }
            combined[f"{cue_id}_bed"] = {
                "file": entry["bed_file"],
                "type": "sfx",
                "bed": True,
                "loop": True,
                "source_split_cue": cue_id,
                "volume": 0.26 if cue_id == "JR_103" else 0.18,
            }
            combined[cue_id]["bed_volume"] = 0.26 if cue_id == "JR_103" else 0.18
    target = AUDIO / "manifest.json"
    target.write_text(json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {target} with {len(combined) - 1} cues")


if __name__ == "__main__":
    main()
