#!/usr/bin/env python3
"""Generate the Elephant Rescue review batch, JR_021 through JR_071."""

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
OUT = HERE / "audio" / "elephant-rescue-test"
RAW = OUT / "raw"
MODEL = "eleven_v3"
FORMAT = "mp3_44100_128"
REVISED_CUES = {"JR_062", "JR_063", "JR_064", "JR_065"}
LIGHT_FILTER = "highpass=f=80,equalizer=f=500:t=q:w=1:g=1.2,loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false"
VOICE_IDS = {
    "COCO": "d9BvEI0bp2Tmdpqnjwn0",
    "NARRATOR": "ItmwhOeluca31IEX91Yk",
    "ELEPHANT": "bBG9wwa23659EgIkMbc1",
}
VOICE_SETTINGS = {
    "COCO": {"stability": 0.40, "similarity_boost": 0.78, "style": 0.28,
             "use_speaker_boost": True},
    "NARRATOR": {"stability": 0.56, "similarity_boost": 0.78, "style": 0.12,
                 "use_speaker_boost": True},
    "ELEPHANT": {"stability": 0.42, "similarity_boost": 0.78, "style": 0.30,
                 "use_speaker_boost": True},
}
SPEECH = {
    "JR_022": ("NARRATOR", "[bouncy and curious]"),
    "JR_026": ("COCO", "[surprised and comic]"),
    "JR_028": ("COCO", "[concerned and reassuring]"),
    "JR_029": ("NARRATOR", "[brisk and physical]"),
    "JR_030": ("COCO", "[effortful and rhythmic]"),
    "JR_033": ("NARRATOR", "[comic surprise]"),
    "JR_034": ("COCO", "[funny signature voice]"),
    "JR_035": ("COCO", "[small embarrassed laugh, recovering quickly]"),
    "JR_036": ("COCO", "[clear and warm]"),
    "JR_037": ("COCO", "[clear and warm]"),
    "JR_038": ("COCO", "[clear and warm]"),
    "JR_039": ("COCO", "[clear and warm]"),
    "JR_041": ("COCO", "[bright and encouraging]"),
    "JR_042": ("COCO", "[playful and encouraging]"),
    "JR_044": ("COCO", "[clear and warm]"),
    "JR_046": ("COCO", "[comically breathless, bouncing on pull and gul]"),
    "JR_048": ("COCO", "[relieved and happy]"),
    "JR_049": ("COCO", "[proud and impressed]"),
    "JR_050": ("ELEPHANT", "[relieved and grateful]"),
    "JR_052": ("COCO", "[curious surprise]"),
    "JR_053": ("ELEPHANT", "[playfully hungry]"),
    "JR_054": ("COCO", "[amused]"),
    "JR_055": ("COCO", "[warm and inviting]"),
    "JR_056": ("COCO", "[clear and warm]"),
    "JR_057": ("COCO", "[clear and warm]"),
    "JR_058": ("COCO", "[clear and warm]"),
    "JR_060": ("COCO", "[bright]"),
    "JR_062": ("ELEPHANT", "[surprised]"),
    "JR_063": ("ELEPHANT", "[hopeful and cheeky]"),
    "JR_064": ("ELEPHANT", "[playfully pleading]"),
    "JR_065": ("ELEPHANT", "[playfully overwhelmed]"),
    "JR_067": ("COCO", "[gentle and clear]"),
    "JR_068": ("COCO", "[helpful and unhurried]"),
    "JR_069": ("COCO", "[clear and kind]"),
    "JR_071": ("COCO", "[gentle and helpful]"),
}
REUSED = {
    "JR_027": "old_sfx_elephant.mp3",
    "JR_031": "shipped_mud.mp3",
    "JR_040": "shipped_ting.mp3",
    "JR_059": "shipped_ting.mp3",
    "JR_061": "old_sfx_munch.mp3",
    "JR_070": "shipped_boing.mp3",
}
SFX = {
    "JR_021": {
        "text": "A small rescue jeep driving gently along a bumpy path through a friendly daytime jungle, light engine movement, soft leaves and distant birds, playful and safe, no voices, no music. Seamless loop.",
        "duration_seconds": 12.0, "loop": True,
    },
    "JR_023": {
        "text": "One soft small-jeep suspension bump, a gentle cushioned thump, playful and safe, no engine bed, no voices, no music.",
        "duration_seconds": 0.6,
    },
    "JR_024": {
        "text": "One slightly bigger small-jeep suspension bump with a very brief loose rattle, comic and safe, no crash, no voices, no music.",
        "duration_seconds": 0.8,
    },
    "JR_025": {
        "text": "A quick playful double-bump from a small jeep suspension, two clear soft thumps in rhythm, no crash, no voices, no music.",
        "duration_seconds": 0.9,
    },
    "JR_032": {
        "text": "One short whimsical wooden comedy boink after a character slips, silly and harmless, clearly different from a wrong-answer buzzer, no voices, no music.",
        "duration_seconds": 0.6,
    },
    "JR_043": {
        "text": "One short thick rope strain and creak during a strong pull, physical effort but safe, no snapping, no voices, no music.",
        "duration_seconds": 0.9,
    },
    "JR_047": {
        "text": "A big final rope pull followed by a friendly elephant releasing from sticky mud with one wet suction pop and small mud movement, successful and comic, no voices, no music.",
        "duration_seconds": 1.8,
    },
    "JR_051": {
        "text": "Clearly identifiable large friendly elephant belly growl: rounded low-mid stomach rumble followed by a short bubbly gurgle, funny and hungry, not a roar, not an engine, no scary bass, no voices, no music.",
        "duration_seconds": 2.4,
    },
}


def parse_cues():
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
        url, json.dumps(body, ensure_ascii=False).encode("utf-8"),
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


def write_once(path, data):
    if path.exists():
        print(f"Existing: {path.relative_to(OUT)}; skipping charged generation", flush=True)
        return
    path.write_bytes(data)
    print(f"Generated: {path.relative_to(OUT)}", flush=True)


def copy_once(source, target):
    if target.exists():
        if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(source.read_bytes()).digest():
            raise ValueError(f"Existing reused asset changed: {target}")
        return
    shutil.copyfile(source, target)


def render_filter(source, target, audio_filter):
    temporary = OUT / f".{target.stem}.rendering.mp3"
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                    "-af", audio_filter, "-ac", "1", "-ar", "44100", "-b:a", "128k",
                    str(temporary)], check=True)
    os.replace(temporary, target)


def normalize(source, target, speech=False):
    if speech:
        render_filter(source, target,
                      "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false")
    else:
        render_filter(source, target,
                      "loudnorm=I=-20:TP=-4:LRA=11,alimiter=limit=0.63:level=false")


def make_speech(key, parsed):
    for cue_id, (role, tag) in SPEECH.items():
        actual_role, spoken = parsed[cue_id]
        if role != actual_role:
            raise ValueError(f"{cue_id} speaker changed from {role} to {actual_role}")
        raw = RAW / f"{cue_id}{'_v2' if cue_id in REVISED_CUES else ''}.mp3"
        body = {"text": f"{tag} {spoken}", "model_id": MODEL,
                "voice_settings": VOICE_SETTINGS[role]}
        request_record = raw.with_suffix('.request.json')
        if raw.exists() and cue_id in REVISED_CUES:
            if not request_record.exists() or json.loads(request_record.read_text()) != body:
                raise ValueError(f"Cached text changed for {cue_id}; use a new revision filename")
        if not raw.exists():
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[role]}?output_format={FORMAT}"
            write_once(raw, request_audio(url, key, body))
            request_record.write_text(json.dumps(body, ensure_ascii=False, indent=2) + '\n')
        else:
            print(f"Existing: raw/{raw.name}; skipping charged generation", flush=True)
        target = OUT / f"{cue_id}.mp3"
        if role == "ELEPHANT":
            render_filter(raw, target, LIGHT_FILTER)
        else:
            normalize(raw, target, speech=True)


def make_laughter(key):
    requests = {
        "JR_066_elephant": ("ELEPHANT", "[warm belly laugh] Ha-ha-ha!"),
        "JR_066_coco": ("COCO", "[short natural giggle] ही-ही!"),
    }
    for name, (role, text) in requests.items():
        raw = RAW / f"{name}.mp3"
        if not raw.exists():
            body = {"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS[role]}
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[role]}?output_format={FORMAT}"
            write_once(raw, request_audio(url, key, body))
    elephant = OUT / "JR_066_elephant_light.mp3"
    render_filter(RAW / "JR_066_elephant.mp3", elephant, LIGHT_FILTER)
    graph = (
        "[0:a]atrim=0:2.1,afade=t=out:st=1.75:d=0.35,volume=0.9[e];"
        "[1:a]atrim=0:1.3,afade=t=out:st=0.95:d=0.35,adelay=650,volume=0.7[c];"
        "[e][c]amix=inputs=2:duration=longest:normalize=0,"
        "loudnorm=I=-18:TP=-3:LRA=11,alimiter=limit=0.72:level=false[out]"
    )
    temporary = OUT / ".JR_066.rendering.mp3"
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(elephant), "-i", str(RAW / "JR_066_coco.mp3"),
                    "-filter_complex", graph, "-map", "[out]", "-ac", "1", "-ar", "44100",
                    "-b:a", "128k", str(temporary)], check=True)
    os.replace(temporary, OUT / "JR_066.mp3")


def reuse_old_muddy_pronunciation():
    """Use the approved old Coco delivery without its obsolete following lines."""
    source = HERE / "audio_candidates" / "shipped_elephantSetup.mp3"
    if not source.is_file():
        raise FileNotFoundError(f"Run prepare_audio_reuse_preview.py first: {source}")
    alternatives = OUT / "alternatives"
    alternatives.mkdir(exist_ok=True)
    generated = OUT / "JR_028.mp3"
    comparison = alternatives / "JR_028_new_v3.mp3"
    if generated.is_file() and not comparison.exists():
        shutil.copyfile(generated, comparison)
    temporary = OUT / ".JR_028.legacy-excerpt.mp3"
    audio_filter = (
        "atrim=start=0.72:end=9.35,asetpts=N/SR/TB,"
        "afade=t=in:st=0:d=0.04,afade=t=out:st=8.35:d=0.28,"
        "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false"
    )
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                    "-af", audio_filter, "-ac", "1", "-ar", "44100", "-b:a", "128k",
                    str(temporary)], check=True)
    os.replace(temporary, generated)


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    # Preserve the earlier script/treatment together before replacing derivatives.
    archive = OUT / "archive-before-childlike-v2"
    if not archive.exists():
        archive.mkdir()
        for name in ["manifest.json", "JR_050.mp3", "JR_053.mp3", "JR_062.mp3",
                     "JR_063.mp3", "JR_064.mp3", "JR_065.mp3", "JR_066.mp3"]:
            if (OUT / name).exists():
                shutil.copyfile(OUT / name, archive / name)
    parsed = parse_cues()
    make_speech(key, parsed)
    reuse_old_muddy_pronunciation()

    for cue_id, item in SFX.items():
        raw = RAW / f"{cue_id}.mp3"
        if not raw.exists():
            body = {"text": item["text"], "model_id": "eleven_text_to_sound_v2",
                    "duration_seconds": item["duration_seconds"], "prompt_influence": 0.8,
                    "loop": item.get("loop", False)}
            url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
            write_once(raw, request_audio(url, key, body))
        if cue_id == "JR_021":
            normalize(raw, OUT / f"{cue_id}.mp3", speech=False)
        else:
            normalize(raw, OUT / f"{cue_id}.mp3", speech=False)

    candidates = HERE / "audio_candidates"
    for cue_id, name in REUSED.items():
        normalize(candidates / name, OUT / f"{cue_id}.mp3", speech=False)
    copy_once(OUT / "JR_043.mp3", OUT / "JR_045.mp3")
    make_laughter(key)

    manifest = {}
    for number in range(21, 72):
        cue_id = f"JR_{number:03d}"
        path = OUT / f"{cue_id}.mp3"
        if not path.is_file():
            raise FileNotFoundError(path)
        lufs, peak = measure(path)
        entry = {"file": f"elephant-rescue-test/{path.name}",
                 "duration_seconds": duration(path), "integrated_lufs": lufs,
                 "true_peak_dbfs": peak, "review_status": "test"}
        if cue_id in SPEECH:
            role, tag = SPEECH[cue_id]
            entry.update({"type": "speech", "voice": role, "voice_id": VOICE_IDS[role],
                          "model_id": MODEL, "voice_settings": VOICE_SETTINGS[role],
                          "spoken_text": parsed[cue_id][1], "performance_tag": tag,
                          "character_treatment": "light EQ, natural pitch (audition)" if role == "ELEPHANT" else None,
                          "source_file": f"raw/{cue_id}{'_v2' if cue_id in REVISED_CUES else ''}.mp3"})
            if role == "ELEPHANT":
                entry["filter"] = LIGHT_FILTER
            if cue_id == "JR_028":
                entry.update({"model_id": "legacy shipped recording",
                              "voice_settings": None,
                              "source_file": "audio_candidates/shipped_elephantSetup.mp3",
                              "source_key": "elephantSetup",
                              "source_excerpt_seconds": {"start": 0.72, "end": 9.35},
                              "reuse_reason": "User preferred the original muddy गड्ढे pronunciation; excerpt ends before the old continuation."})
        else:
            entry["type"] = "character_laughter" if cue_id == "JR_066" else "sfx"
        if cue_id == "JR_021":
            entry.update({"bed": True, "loop": True})
        if cue_id == "JR_045":
            entry["alias_of"] = "JR_043"
        manifest[cue_id] = entry
    manifest["_batch"] = {
        "name": "Elephant Rescue production test",
        "range": "JR_021–JR_071", "format": FORMAT, "script": SCRIPT.name,
        "note": "Revision 2: approved biscuit wording and light natural-pitch Vardan treatment without doubled voice layers. Assets remain review MP3s.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    print(f"Saved {OUT / 'manifest.json'}", flush=True)


if __name__ == "__main__":
    main()
