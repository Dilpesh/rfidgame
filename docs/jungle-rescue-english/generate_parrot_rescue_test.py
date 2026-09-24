#!/usr/bin/env python3
"""Generate the Parrot Rescue review batch, JR_072–JR_102.

Each cue stays separate for the game's card, hint and water-break states.
Raw requests and their parameters are kept so reruns do not spend credits.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

from generate_elephant_rescue_test import (
    FORMAT, MODEL, SCRIPT, VOICE_IDS, VOICE_SETTINGS, parse_cues, request_audio,
)
from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio" / "parrot-rescue-test"
RAW = OUT / "raw"
VOICE_IDS = {**VOICE_IDS, "PARROT": "VOGEEZj2Kly5dP9LrQy8"}
VOICE_SETTINGS = {
    **VOICE_SETTINGS,
    "PARROT": {"stability": 0.45, "similarity_boost": 0.78,
               "style": 0.30, "use_speaker_boost": True},
}
SPEECH = {
    "JR_073": ("COCO", "[bright transition]"),
    "JR_075": ("PARROT", "[briefly hurt, gentle and childlike]"),
    "JR_077": ("COCO", "[concerned and gentle]"),
    "JR_078": ("COCO", "[warm and reassuring]"),
    "JR_079": ("COCO", "[curious, clear card invitation]"),
    "JR_080": ("COCO", "[clear and warm]"),
    "JR_081": ("COCO", "[clear and warm]"),
    "JR_082": ("COCO", "[clear and warm]"),
    "JR_084": ("COCO", "[happy, clear, unhurried; complete the final word]"),
    "JR_086": ("COCO", "[gentle relief]"),
    "JR_088": ("PARROT", "[hopeful and tentative]"),
    "JR_089": ("COCO", "[encouraging, rhythmic]"),
    "JR_091": ("PARROT", "[delighted, bright]"),
    "JR_093": ("PARROT", "[tired and thirsty, not distressed]"),
    "JR_094": ("COCO", "[caring, clear water-break instruction]"),
    "JR_095": ("COCO", "[kind and unhurried reminder]"),
    "JR_097": ("COCO", "[warm welcome back]"),
    "JR_099": ("PARROT", "[surprised and happy]"),
    "JR_101": ("PARROT", "[joyful, calling as she flies away]"),
    "JR_102": ("COCO", "[delighted transition]"),
}
REVISED_SPEECH = {"JR_084": {"raw_name": "JR_084_v2",
                              "tail": " [small relieved breath]"}}
NONVERBAL = {
    "JR_074_parrot": ("PARROT", "[a tiny hurt chirp] चूँ!"),
    "JR_092": ("PARROT", "[one tiny happy bird chirp] चूँ!"),
}
SFX = {
    "JR_072": ("A very short cheerful rescue jeep departure from a stationary jungle scene: light engine swish, one soft happy suspension bump, then stop. No speech, no music, no crash.", 1.3),
    "JR_074_branch": ("Leaves rustle briefly on one low tree branch as a small bird shifts there. Gentle, close and safe. No bird vocal, no voices, no music.", 0.9),
    "JR_076": ("A small bird attempts to flap an injured wing: one uneven soft wing flap, a tiny comic feather squeak, then silence. Gentle and not scary. No bird vocal, no voices, no music.", 1.3),
    "JR_085": ("A small first aid kit clicks open, soft rustle of a clean bandage being taken out. Gentle, tidy and reassuring. No sparkle, no voices, no music.", 1.4),
    "JR_087": ("A little bandage winds once around a bird wing with soft fabric rustle, followed by one short bright magical healing sparkle. No voices, no music.", 1.6),
    "JR_090": ("Small bird wing test: two tentative uneven flaps followed by one clear strong happy flap. A gentle physical improvement, no bird vocal, no voices, no music.", 2.1),
    "JR_098": ("Close, clearly identifiable drinking effect: a little water poured into a cup, then exactly three separated cartoon bird swallows, glug ... glug ... GULP. Three distinct rounded throat gulps with the third slightly bigger. No splashing over the swallows, no bird vocal, no speech, no music.", 4.4),
    "JR_100": ("A small happy bird flaps its wings three times, getting stronger, then takes off with one short joyful airy whoosh. No bird vocal, no voices, no music.", 2.0),
}


def api_asset(name, body, url, key):
    path = RAW / f"{name}.mp3"
    record = RAW / f"{name}.request.json"
    if path.exists():
        if not record.exists() or json.loads(record.read_text(encoding="utf-8")) != body:
            raise ValueError(f"Cached request changed for {name}; use a new revision filename")
        print(f"Existing raw/{name}.mp3", flush=True)
        return path
    data = request_audio(url, key, body)
    path.write_bytes(data)
    record.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated raw/{name}.mp3", flush=True)
    return path


def speech_asset(name, role, text, tag, key):
    revision = REVISED_SPEECH.get(name, {})
    raw_name = revision.get("raw_name", name)
    body = {"text": f"{tag} {text}{revision.get('tail', '')}", "model_id": MODEL,
            "voice_settings": VOICE_SETTINGS[role]}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[role]}?output_format={FORMAT}"
    raw = api_asset(raw_name, body, url, key)
    if name in REVISED_SPEECH:
        alternatives = OUT / "alternatives"
        alternatives.mkdir(exist_ok=True)
        earlier = OUT / f"{name}.mp3"
        archive = alternatives / f"{name}_first_take.mp3"
        if earlier.exists() and not archive.exists():
            shutil.copyfile(earlier, archive)
    # Scribe verified the complete final "गई" at 4.18 s. Remove the later
    # generated breath while keeping only a brief clean tail after the word.
    normalize_to(raw, OUT / f"{name}.mp3", speech=True,
                 trim_seconds=4.36 if name == "JR_084" else None)


def normalize_to(source, target, speech=False, trim_seconds=None):
    # Reuse the same loudness targets as the approved earlier review batches.
    filter_string = ("loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false"
                     if speech else
                     "loudnorm=I=-20:TP=-4:LRA=11,alimiter=limit=0.63:level=false")
    if trim_seconds is not None:
        filter_string = (f"atrim=end={trim_seconds},asetpts=N/SR/TB,"
                         f"afade=t=out:st={trim_seconds-0.12}:d=0.12," + filter_string)
    temporary = OUT / f".{target.stem}.rendering.mp3"
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source), "-af", filter_string, "-ac", "1",
                    "-ar", "44100", "-b:a", "128k", str(temporary)], check=True)
    os.replace(temporary, target)


def sfx_asset(name, prompt, seconds, key):
    body = {"text": prompt, "model_id": "eleven_text_to_sound_v2",
            "duration_seconds": seconds, "prompt_influence": 0.8, "loop": False}
    url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
    raw = api_asset(name, body, url, key)
    normalize_to(raw, OUT / f"{name}.mp3")


def concatenate(parts, target):
    # FFmpeg joins the separately rendered branch rustle and matching Munni chirp.
    inputs = []
    for part in parts:
        inputs.extend(["-i", str(part)])
    graph = "".join(f"[{index}:a]aresample=44100,asetpts=N/SR/TB[a{index}];"
                    for index in range(len(parts)))
    graph += "".join(f"[a{index}]" for index in range(len(parts)))
    graph += f"concat=n={len(parts)}:v=0:a=1[out]"
    temporary = OUT / f".{target.stem}.rendering.mp3"
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    *inputs, "-filter_complex", graph, "-map", "[out]",
                    "-ac", "1", "-ar", "44100", "-b:a", "128k", str(temporary)],
                   check=True)
    os.replace(temporary, target)


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    parsed = parse_cues()
    for cue_id, (role, tag) in SPEECH.items():
        actual_role, spoken = parsed[cue_id]
        if role != actual_role:
            raise ValueError(f"{cue_id}: script speaker changed")
        speech_asset(cue_id, role, spoken, tag, key)
    for name, (role, text) in NONVERBAL.items():
        speech_asset(name, role, text, "[small bird voice]", key)
    for name, (prompt, seconds) in SFX.items():
        sfx_asset(name, prompt, seconds, key)
    alternatives = OUT / "alternatives"
    alternatives.mkdir(exist_ok=True)
    concatenate([OUT / "JR_074_branch.mp3", OUT / "JR_074_parrot.mp3"],
                alternatives / "JR_074_new.mp3")
    # The user prefers the shipped hurt cue. Keep its timing and sound intact.
    legacy_hurt = HERE / "audio_candidates" / "shipped_parrotFall.mp3"
    if not legacy_hurt.is_file():
        raise FileNotFoundError(legacy_hurt)
    shutil.copyfile(legacy_hurt, OUT / "JR_074.mp3")
    chime = HERE / "audio" / "elephant-rescue-test" / "JR_040.mp3"
    for cue_id in ("JR_083", "JR_096"):
        shutil.copyfile(chime, OUT / f"{cue_id}.mp3")
    manifest = {}
    for number in range(72, 103):
        cue_id = f"JR_{number:03d}"
        path = OUT / f"{cue_id}.mp3"
        if not path.is_file():
            raise FileNotFoundError(path)
        lufs, peak = measure(path)
        entry = {"file": f"parrot-rescue-test/{path.name}",
                 "duration_seconds": duration(path), "integrated_lufs": lufs,
                 "true_peak_dbfs": peak, "review_status": "test"}
        if cue_id in SPEECH:
            role, tag = SPEECH[cue_id]
            entry.update({"type": "speech", "voice": role, "voice_id": VOICE_IDS[role],
                          "model_id": MODEL, "voice_settings": VOICE_SETTINGS[role],
                          "spoken_text": parsed[cue_id][1], "performance_tag": tag,
                          "source_file": f"raw/{REVISED_SPEECH.get(cue_id, {}).get('raw_name', cue_id)}.mp3"})
            if cue_id in REVISED_SPEECH:
                entry["production_note"] = "Second take completes गई (Scribe: 3.96–4.18 s); generated breath removed at 4.36 s. No extra scripted words."
        else:
            entry["type"] = "character_nonverbal" if cue_id == "JR_092" else "sfx"
            if cue_id in ("JR_083", "JR_096"):
                entry["alias_of"] = "JR_040"
            if cue_id == "JR_074":
                entry.update({"source_file": "audio_candidates/shipped_parrotFall.mp3",
                              "source_key": "parrotFall",
                              "reuse_reason": "User preferred the shipped Parrot hurt effect.",
                              "alternative_file": "alternatives/JR_074_new.mp3"})
            if cue_id == "JR_092":
                entry.update({"voice": "PARROT", "voice_id": VOICE_IDS["PARROT"],
                              "model_id": MODEL, "source_file": "raw/JR_092.mp3"})
        manifest[cue_id] = entry
    manifest["_batch"] = {"name": "Parrot Rescue production test",
                          "range": "JR_072–JR_102", "format": FORMAT,
                          "script": SCRIPT.name,
                          "note": "Separate FIRST AID and WATER interactions; review MP3s, not final lossless delivery."}
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved Parrot Rescue manifest", flush=True)


if __name__ == "__main__":
    main()
