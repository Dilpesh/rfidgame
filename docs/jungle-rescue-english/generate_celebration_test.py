#!/usr/bin/env python3
"""Generate the final Celebration batch, JR_150 through JR_184.

Speech, sound effects and music are kept as separate cues so the player can
pause for the Music card, duck the dance loop under movement calls, and stop
the beat cleanly for each freeze command.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from generate_elephant_rescue_test import (
    FORMAT, MODEL, VOICE_IDS, VOICE_SETTINGS, parse_cues, request_audio,
)
from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio" / "celebration-test"
RAW = OUT / "raw"
SFX_MODEL = "eleven_text_to_sound_v2"

VOICE_IDS = {**VOICE_IDS, "PARROT": "VOGEEZj2Kly5dP9LrQy8"}
VOICE_SETTINGS = {
    **VOICE_SETTINGS,
    "PARROT": {"stability": 0.45, "similarity_boost": 0.78,
                "style": 0.30, "use_speaker_boost": True},
}

SPEECH = {
    "JR_151": ("NARRATOR", "[warm, relieved]"),
    "JR_152": ("COCO", "[proud, delighted]"),
    "JR_154": ("COCO", "[eager, playful]"),
    "JR_155": ("COCO", "[gently encouraging]"),
    "JR_156": ("COCO", "[playful, helpful]"),
    "JR_157": ("COCO", "[clear, kind]"),
    "JR_159": ("COCO", "[excited]"),
    "JR_161": ("COCO", "[bouncy, inviting]"),
    "JR_163": ("COCO", "[playful, clear]"),
    "JR_164": ("COCO", "[bright, rhythmic]"),
    "JR_166": ("COCO", "[funny, clear]"),
    "JR_167": ("COCO", "[puffed cheeks, funny release]"),
    "JR_168": ("COCO", "[puffs cheeks again; laughing at himself]"),
    "JR_171": ("COCO", "[warm, proud; gently catching his breath]"),
    "JR_172": ("COCO", "[inviting, joyful]"),
    "JR_173": ("COCO", "[playful]"),
    "JR_175": ("COCO", "[comic surprise]"),
    "JR_177": ("COCO", "[laughing, affectionate]"),
    "JR_180": ("COCO", "[playfully surprised, encouraging]"),
    "JR_182": ("COCO", "[light, encouraging]"),
    "JR_184": ("COCO", "[curious, supportive]"),
}

SFX = {
    "JR_150": ("The last soft snore of a small sleeping lion fades in the distance as a few gentle footsteps move toward a rescue jeep. Light rain eases and evening wind fades. One continuous child-safe transition, no voices, no music, no loud engine.", 4.0, False),
    "JR_153": ("Two playful little child footsteps or shoe taps on firm ground: tap-tap, close and clear, comic but gentle. No voice, no music, no jungle ambience.", 0.8, False),
    "JR_165": ("A short happy parrot chirp followed by two quick wing flutters during a children's dance. Bright, friendly and clearly a parrot, no words, no music, no distress.", 1.2, False),
    "JR_170": ("A short bright resolving instrumental sting for a preschool jungle victory dance, using a playful marimba hook, crisp handclap and light dhol-style drum. Clean joyful ending with a gentle tail. No voice, no animal call, no long fade.", 2.0, False),
    "JR_174": ("One friendly close high-five clap, soft and satisfying for a child's celebration. No voices, no music, no echo.", 0.7, False),
    "JR_178": ("A short warm triumphant ending sting for a preschool jungle rescue, bright marimba and soft handclap resolving cleanly, followed by one friendly small jeep horn. No voice, no long fade, no frightening sound.", 2.2, False),
}

# These particular sources were marked Use by the user in audio_reuse_review.json.
# Keep the approved source selection, rather than spending credits to recreate it.
REUSED = {
    "JR_158": (HERE / "audio" / "elephant-rescue-test" / "JR_040.mp3", "JR_040", "approved shipped correct chime"),
    "JR_162": (HERE / "audio" / "elephant-rescue-test" / "JR_027.mp3", "JR_027", "approved older elephant call"),
    "JR_169": (HERE / "audio" / "elephant-rescue-test" / "raw" / "JR_066_coco.mp3", "JR_066_coco", "Coco giggle from reviewed Elephant batch"),
    "JR_176": (HERE / "audio" / "elephant-rescue-test" / "JR_031.mp3", "JR_031", "established approved mud sound for the closing callback"),
    "JR_179": (HERE / "audio" / "elephant-rescue-test" / "JR_070.mp3", "JR_070", "approved shipped soft boing"),
    "JR_181": (HERE / "audio" / "elephant-rescue-test" / "JR_070.mp3", "JR_070", "approved shipped soft boing"),
    "JR_183": (HERE / "audio" / "elephant-rescue-test" / "JR_070.mp3", "JR_070", "approved shipped soft boing"),
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


def render(source, target, audio_filter):
    temporary = OUT / f".{target.stem}.rendering.mp3"
    subprocess.run([
        ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-af", audio_filter, "-ac", "1", "-ar", "44100", "-b:a", "128k", str(temporary),
    ], check=True)
    os.replace(temporary, target)


def speech_asset(name, role, tag, spoken, key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[role]}?output_format={FORMAT}"
    body = {"text": f"{tag} {spoken}", "model_id": MODEL,
            "voice_settings": VOICE_SETTINGS[role]}
    raw = api_asset(name, body, url, key)
    audio_filter = "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false"
    # The generated takes contain long silence after the final spoken word.
    if name == "JR_151":
        audio_filter += ",atrim=end=6.35,asetpts=PTS-STARTPTS"
    elif name == "JR_168":
        audio_filter += ",atrim=end=4.08,asetpts=PTS-STARTPTS"
    render(raw, OUT / f"{name}.mp3", audio_filter)


def sfx_asset(name, prompt, seconds, loop, key):
    body = {"text": prompt, "model_id": SFX_MODEL,
            "duration_seconds": seconds, "prompt_influence": 0.8, "loop": loop}
    url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
    raw = api_asset(name, body, url, key)
    filt = ("afade=t=in:st=0:d=0.05,loudnorm=I=-18:TP=-3:LRA=11,"
            "alimiter=limit=0.72:level=false")
    if name == "JR_170":
        filt += ",atrim=end=1.35,asetpts=PTS-STARTPTS"
    render(raw, OUT / f"{name}.mp3", filt)


def edit_goodbye_sting():
    """Use the dance resolution again, followed promptly by the generated jeep horn."""
    source_sting = OUT / "JR_170.mp3"
    source_horn = RAW / "JR_178.mp3"
    target = OUT / "JR_178.mp3"
    temporary = OUT / ".JR_178.rendering.mp3"
    graph = (
        "[0:a]apad=pad_dur=0.18[a];"
        "[1:a]atrim=start=0.92:end=1.72,asetpts=PTS-STARTPTS[b];"
        "[a][b]concat=n=2:v=0:a=1,"
        "loudnorm=I=-18:TP=-3:LRA=11,alimiter=limit=0.72:level=false[out]"
    )
    subprocess.run([
        ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(source_sting), "-i", str(source_horn),
        "-filter_complex", graph, "-map", "[out]",
        "-ac", "1", "-ar", "44100", "-b:a", "128k", str(temporary),
    ], check=True)
    os.replace(temporary, target)


def reuse_assets():
    OUT.mkdir(parents=True, exist_ok=True)
    for cue_id, (source, _alias, _reason) in REUSED.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target = OUT / f"{cue_id}.mp3"
        if cue_id == "JR_169":
            render(source, target,
                   "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false")
        else:
            shutil.copyfile(source, target)
        print(f"Reused {cue_id} from {source.name}", flush=True)


def music_asset(key):
    prompt = (
        "Create an exuberant jungle rescue victory dance for preschool children. Target 120 BPM in "
        "4/4, bright major key, with an immediate strong first beat and full dancing energy from the "
        "first second. Use a bouncy clearly audible kick, crisp friendly handclaps, playful dhol-style "
        "hand drums, rounded bass with audible midrange, and a short catchy marimba melody that repeats. "
        "Instrumental only, no vocals, chants, spoken words, animal calls or environmental sounds. Keep "
        "the arrangement uncluttered, with no slow intro, internal pause, breakdown, tempo change or "
        "fade-out. Make a 20-second loop that joins smoothly back to its strong opening beat without a "
        "closing cadence."
    )
    body = {"prompt": prompt, "music_length_ms": 20000,
            "model_id": "music_v2", "force_instrumental": True}
    url = "https://api.elevenlabs.io/v1/music?output_format=mp3_48000_192"
    raw = api_asset("JR_160", body, url, key)
    render(raw, OUT / "JR_160.mp3",
           "atrim=end=20,asetpts=PTS-STARTPTS,loudnorm=I=-24:TP=-5:LRA=11,"
           "alimiter=limit=0.60:level=false")


def manifest_for(parsed, partial=False):
    manifest = {}
    for cue_id, (role, tag) in SPEECH.items():
        path = OUT / f"{cue_id}.mp3"
        if partial and not path.is_file():
            continue
        lufs, peak = measure(path)
        manifest[cue_id] = {
            "file": f"celebration-test/{path.name}", "type": "speech",
            "duration_seconds": duration(path), "integrated_lufs": lufs,
            "true_peak_dbfs": peak, "review_status": "test", "voice": role,
            "voice_id": VOICE_IDS[role], "model_id": MODEL,
            "voice_settings": VOICE_SETTINGS[role],
            "spoken_text": parsed[cue_id][1], "performance_tag": tag,
            "source_file": f"raw/{cue_id}.mp3",
        }
    for cue_id in SFX:
        path = OUT / f"{cue_id}.mp3"
        if partial and not path.is_file():
            continue
        lufs, peak = measure(path)
        manifest[cue_id] = {
            "file": f"celebration-test/{path.name}",
            "type": "music" if cue_id == "JR_170" else "sfx",
            "duration_seconds": duration(path), "integrated_lufs": lufs,
            "true_peak_dbfs": peak, "review_status": "test",
            "model_id": SFX_MODEL, "source_file": f"raw/{cue_id}.mp3",
        }
        if cue_id == "JR_178":
            manifest[cue_id]["components"] = ["JR_170.mp3", "raw/JR_178.mp3"]
            manifest[cue_id]["production_edit"] = "Dance resolving hook, then trimmed jeep horn."
    for cue_id, (source, alias, reason) in REUSED.items():
        path = OUT / f"{cue_id}.mp3"
        lufs, peak = measure(path)
        manifest[cue_id] = {
            "file": f"celebration-test/{path.name}", "type": "sfx",
            "duration_seconds": duration(path), "integrated_lufs": lufs,
            "true_peak_dbfs": peak, "review_status": "reused_source",
            "alias_of": alias, "source_file": str(source.relative_to(HERE)),
            "reuse_reason": reason,
        }
    music = OUT / "JR_160.mp3"
    if music.is_file():
        lufs, peak = measure(music)
        manifest["JR_160"] = {
            "file": "celebration-test/JR_160.mp3", "type": "music",
            "duration_seconds": duration(music), "integrated_lufs": lufs,
            "true_peak_dbfs": peak, "review_status": "test", "loop": True,
            "volume": 0.62, "exact_runtime_seconds": 20.0, "model_id": "music_v2",
            "source_file": "raw/JR_160.mp3",
        }
    manifest["_batch"] = {"name": "Jungle Rescue Celebration production test",
                          "range": "JR_150–JR_184", "format": FORMAT,
                          "script": "jungle_rescue_final_production_script.md",
                          "note": "Partial local reuse only" if partial else "Speech, effects and dance music remain separate for deterministic freeze timing."}
    return manifest


def main():
    reuse_only = "--reuse-only" in sys.argv[1:]
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    required_raw = [RAW / f"{cue_id}.mp3" for cue_id in (*SPEECH, *SFX, "JR_160")]
    if not key and not reuse_only and any(not path.is_file() for path in required_raw):
        raise SystemExit("ELEVENLABS_API_KEY is needed for missing raw audio")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    reuse_assets()
    parsed = parse_cues()
    if reuse_only:
        (OUT / "manifest.json").write_text(
            json.dumps(manifest_for(parsed, partial=True), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        print("Saved partial Celebration manifest with approved local sounds", flush=True)
        return
    for cue_id, (role, tag) in SPEECH.items():
        speech_asset(cue_id, role, tag, parsed[cue_id][1], key)
    for cue_id, (prompt, seconds, loop) in SFX.items():
        sfx_asset(cue_id, prompt, seconds, loop, key)
    edit_goodbye_sting()
    music_asset(key)
    (OUT / "manifest.json").write_text(
        json.dumps(manifest_for(parsed), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("Saved Celebration manifest", flush=True)


if __name__ == "__main__":
    main()
