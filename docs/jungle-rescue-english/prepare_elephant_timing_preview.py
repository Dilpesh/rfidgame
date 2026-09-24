#!/usr/bin/env python3
"""Render current/proposed joke timing from existing recordings; no API calls.

All source cues remain unchanged. Times refer to decoded audio, so silence
already inside each source is retained unless explicitly trimmed below.
"""

import hashlib
import json
import subprocess
import wave
from pathlib import Path

from make_elephant_treatment import ffmpeg, measure

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "audio" / "elephant-rescue-test"
OUT = SOURCE / "timing-preview"


def seconds(path):
    result = subprocess.run(
        [ffmpeg(), "-v", "error", "-i", str(path), "-ac", "1", "-ar", "44100",
         "-f", "s16le", "-"], capture_output=True, check=True)
    return len(result.stdout) / (44100 * 2)


def event(cue, start, duration, gain=1):
    return {"cue": cue, "start": round(start, 6), "duration": duration, "gain": gain}


def sequence(ids, lengths, variant, pauses=None, trims=None):
    cursor = 0
    events = []
    pauses, trims = pauses or {}, trims or {}
    for number in ids:
        cue = f"JR_{number:03d}"
        length = trims.get(cue, lengths[cue]) if variant == "proposed" else lengths[cue]
        events.append(event(cue, cursor, length))
        cursor += length
        if variant == "proposed":
            cursor += pauses.get(cue, 0)
    return events


def render(name, events):
    command = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y"]
    for item in events:
        command += ["-i", str(SOURCE / f"{item['cue']}.mp3")]
    graph = []
    for index, item in enumerate(events):
        graph.append(
            f"[{index}:a]aformat=sample_rates=44100:channel_layouts=mono,"
            f"atrim=end={item['duration']:.6f},asetpts=PTS-STARTPTS,"
            f"volume={item['gain']},adelay={round(item['start'] * 44100)}S[a{index}]")
    labels = "".join(f"[a{i}]" for i in range(len(events)))
    graph.append(f"{labels}amix=inputs={len(events)}:duration=longest:normalize=0,"
                 "alimiter=limit=0.89:level=false:latency=true[out]")
    target = OUT / f"{name}.wav"
    command += ["-filter_complex", ";".join(graph), "-map", "[out]", "-ac", "1",
                "-ar", "44100", "-c:a", "pcm_s16le", str(target)]
    subprocess.run(command, check=True)
    lufs, peak = measure(target)
    if peak > -0.8:
        raise ValueError(f"Peak exceeded preview limit: {name}: {peak}")
    with wave.open(str(target), "rb") as recording:
        length = recording.getnframes() / recording.getframerate()
    print(f"{name}: {length:.2f}s", flush=True)
    return {"file": target.name, "duration_seconds": round(length, 3),
            "integrated_lufs": lufs, "true_peak_dbfs": peak, "events": events}


def main():
    OUT.mkdir(exist_ok=True)
    groups = {
        "trampoline": [22, 23, 24, 25, 26, 27],
        "mud": [29, 30, 31, 32, 33, 34, 35],
        "stomach": [50, 51, 52, 53, 54, 55],
        "balloon": [61, 65, 66],
    }
    cue_ids = {f"JR_{n:03d}" for ids in groups.values() for n in ids} | {"JR_046", "JR_047", "JR_048"}
    lengths = {cue: seconds(SOURCE / f"{cue}.mp3") for cue in cue_ids}
    hashes = {cue: hashlib.sha256((SOURCE / f"{cue}.mp3").read_bytes()).hexdigest()
              for cue in cue_ids}
    results = {}
    for name, ids in groups.items():
        for variant in ("current", "proposed"):
            pauses = {"JR_026": 1.2, "JR_029": 0.8, "JR_054": 0.6, "JR_065": 0.3}
            events = sequence(ids, lengths, variant, pauses, {"JR_052": 1.32})
            if name == "mud" and variant == "proposed":
                # Sound of impact starts first; narration explains while the
                # lower-volume effect continues. Voices never overlap.
                splat = events[2]["start"]
                events[2]["gain"] = 0.5
                events[3]["gain"] = 0.5
                events[4]["start"] = round(splat + 0.4, 6)
                for index in (5, 6):
                    events[index]["start"] = round(events[index - 1]["start"] + events[index - 1]["duration"], 6)
            results[f"{name}_{variant}"] = render(f"{name}_{variant}", events)
    results["pull_reference"] = render("pull_reference", sequence([46, 47, 48], lengths, "current"))
    manifest = {
        "purpose": "Preview of joke timing only; source cues and production specifications unchanged",
        "source_hashes": hashes,
        "changes": {
            "trampoline": "Add 1.20s after JR_026 before the Elephant trumpet.",
            "mud": "Add 0.80s after JR_029 before the count. Narrator JR_033 starts 0.40s after splat begins. Splat/boink at half amplitude underneath; speech remains sequential. Preserve catchphrase tail. Overlap remains an audition only.",
            "stomach": "JR_052 excerpt ends at 1.32s, removing trailing quiet after the question. Retain growl tail and internal JR_054 pause; add 0.60s after JR_054.",
            "balloon": "Add 0.30s after JR_065 before JR_066 laughter; performance unchanged.",
            "pull": "Unchanged reference; timing edits cannot replace the requested acting contrast.",
        },
        "mix": "Identical dry cue gains for A/B except ducked mud effects. No ambience; no browser loading gaps. 44.1kHz mono PCM WAV.",
        "clips": results,
    }
    # Assert editing stayed in this preview directory.
    for cue, digest in hashes.items():
        if hashlib.sha256((SOURCE / f"{cue}.mp3").read_bytes()).hexdigest() != digest:
            raise ValueError(f"Source unexpectedly changed: {cue}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
