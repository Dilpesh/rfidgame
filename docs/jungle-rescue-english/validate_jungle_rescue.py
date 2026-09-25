#!/usr/bin/env python3
"""Static production checks for the Jungle Rescue English player."""

import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "jungle_rescue_final_production_script.md"
PLAYER = HERE / "index.html"
MANIFEST = HERE / "audio" / "manifest.json"
EXPECTED_INTERACTION_ONLY = {"JR_070", "JR_071", "JR_112", "JR_179", "JR_181", "JR_183"}


def cue_ids(text):
    return list(dict.fromkeys(re.findall(r"JR_\d{3}(?:_[A-Za-z0-9]+)?", text)))


def report(kind, message, failures):
    print(f"{kind}: {message}")
    if kind == "ERROR":
        failures.append(message)


def main():
    script_text = SCRIPT.read_text(encoding="utf-8")
    player_text = PLAYER.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    script_cues = list(dict.fromkeys(re.findall(r"^\*\*(JR_\d{3}(?:_[A-Za-z0-9]+)?)", script_text, re.MULTILINE)))
    player_cues = cue_ids(player_text)
    failures = []

    for cue_id, entry in manifest.items():
        if cue_id.startswith("_") or not isinstance(entry, dict):
            continue
        for field in ("file", "entry_file", "bed_file", "jeep_file"):
            if field in entry and not (HERE / "audio" / entry[field]).is_file():
                report("ERROR", f"{cue_id} {field} is missing: {entry[field]}", failures)

    missing_player_assets = sorted(set(player_cues) - set(manifest))
    if missing_player_assets:
        report("ERROR", "player cues missing from manifest: " + ", ".join(missing_player_assets), failures)

    missing_script_assets = sorted(set(script_cues) - set(manifest))
    if missing_script_assets:
        report("ERROR", "script cues missing from manifest: " + ", ".join(missing_script_assets), failures)

    retired_script = {cue_id for cue_id, entry in manifest.items()
                      if isinstance(entry, dict) and entry.get("type") == "retired"}
    missing_script_route = sorted(set(script_cues) - set(player_cues) - EXPECTED_INTERACTION_ONLY - retired_script)
    if missing_script_route:
        report("ERROR", "script cues absent from player route: " + ", ".join(missing_script_route), failures)

    retired = {cue_id for cue_id, entry in manifest.items()
               if isinstance(entry, dict) and entry.get("type") == "retired"}
    used_retired = sorted(retired & set(player_cues))
    if used_retired:
        report("ERROR", "retired cues still referenced by player: " + ", ".join(used_retired), failures)

    sequence_calls = re.findall(r"playSequence\(\s*\[[^\]]*\](?:\s*,\s*([^\)]+))?\s*\)", player_text)
    missing_tokens = sum(1 for token in sequence_calls if not token or not token.strip())
    if missing_tokens:
        report("ERROR", f"{missing_tokens} playSequence call(s) have no state token", failures)

    play_bed = re.search(r"function playBed\(id\).*?\n", player_text)
    if not play_bed or "c.volume" not in play_bed.group(0):
        report("ERROR", "playBed does not take its level from the manifest", failures)

    for cue_id in ("JR_001", "JR_021"):
        entry = manifest.get(cue_id, {})
        if not isinstance(entry.get("volume"), (int, float)):
            report("ERROR", f"{cue_id} has no manifest volume", failures)

    if not failures:
        print("PASS: Jungle Rescue English static checks")
        return 0
    print(f"FAIL: {len(failures)} issue(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
