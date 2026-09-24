#!/usr/bin/env python3
"""Generate the Lion Rescue review batch, JR_103–JR_149.

The script supplies exact words and cue order; the playback specification owns
the two card waits, cave transition and concurrent ten-second lori tracks.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from generate_elephant_rescue_test import (
    FORMAT, MODEL, SCRIPT, VOICE_IDS, VOICE_SETTINGS, parse_cues, request_audio,
)
from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio" / "lion-rescue-test"
RAW = OUT / "raw"
VOICE_IDS = {**VOICE_IDS, "LION": "5krdMTA5HonvWAlY2vSx"}
VOICE_SETTINGS = {
    **VOICE_SETTINGS,
    "LION": {"stability": 0.44, "similarity_boost": 0.78,
             "style": 0.30, "use_speaker_boost": True},
}
LION_FILTER = (
    "highpass=f=90,lowpass=f=8000,"
    "equalizer=f=280:t=q:w=1.2:g=1,"
    "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false"
)
RAW_REVISIONS = {
    "JR_104": "JR_104_v2", "JR_110": "JR_110_v2",
    # Reuse the approved short cub-lion sound from the entrance reveal for the tail-joke reaction.
    "JR_112": "JR_106_lion", "JR_115": "JR_115_v2",
    "JR_116": "JR_116_v2", "JR_117": "JR_117_v2",
    "JR_128": "JR_128_v2",
    "JR_132": "JR_132_v2", "JR_143": "JR_143_v3",
    "JR_145": "JR_145_v3", "JR_148": "JR_148_v2",
    "JR_149": "JR_149_v2", "JR_126": "JR_126_v2",
    "JR_147_snore_series": "JR_147_snore_series_v1",
}
RETIRED = {"JR_133", "JR_146", "JR_148"}
SPEECH = {
    "JR_104": ("NARRATOR", "[hushed and adventurous]"),
    "JR_106": ("LION", "[two heavy but harmless childlike sneezes; edit the first two from the existing take]"),
    "JR_107": ("COCO", "[whispering, nervous but playful]"),
    "JR_108": ("LION", "[small and embarrassed]"),
    "JR_109": ("COCO", "[surprised]"),
    "JR_110": ("LION", "[worried but gentle]"),
    "JR_111": ("COCO", "[confident, then uncertain]"),
    "JR_113": ("COCO", "[nervous, trying to sound brave]"),
    "JR_115": ("COCO", "[rubbing head, urgent but playful]"),
    "JR_116": ("COCO", "[clear and warm]"),
    "JR_117": ("COCO", "[clear and warm]"),
    "JR_118": ("COCO", "[clear and warm]"),
    "JR_121": ("COCO", "[relieved and bright]"),
    "JR_123": ("COCO", "[surprised and relieved]"),
    "JR_125": ("NARRATOR", "[warm]"),
    "JR_127": ("LION", "[shivering, small and childlike]"),
    "JR_128": ("NARRATOR", "[warm and reassuring; the lion still feels cold inside]"),
    "JR_130": ("COCO", "[helpful and confident]"),
    "JR_132": ("COCO", "[comic self-mockery right after the leaf tears, then caring]"),
    "JR_134": ("COCO", "[clear and inviting]"),
    "JR_135": ("COCO", "[clear and warm]"),
    "JR_136": ("COCO", "[clear and warm]"),
    "JR_137": ("COCO", "[clear and warm]"),
    "JR_140": ("COCO", "[warm acknowledgement]"),
    "JR_141": ("NARRATOR", "[tender]"),
    "JR_142": ("LION", "[cozy, relieved, childlike]"),
    "JR_143": ("COCO", "[tender and empathetic, slower and noticeably softer; invite the child warmly; pronounce लोरी as लो-री]"),
    "JR_149": ("COCO", "[giggling, quiet whisper]"),
}
NONVERBAL = {
    "JR_139_lion": ("LION", "[one relieved cozy sigh] आह..."),
    "JR_145": ("COCO", "[sing a tender original three-note descending लोरी very softly to help a little lion sleep; calm, caring and unhurried; tiny breaths between phrases] ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला... ला..."),
}
SFX = {
    "JR_103_jeep_alt": ("A little open-top four-wheel-drive jeep drives toward us over an uneven dirt road: distinct throaty engine purr, wheels rolling and crunching gravel, slight suspension rattle. It slows to a stop nearby and the motor cuts out cleanly. Friendly adventure-story sound, realistic, not a modern sedan or toy car. No horn, crash, voices, music or jungle ambience.", 4.0, False),
    "JR_103_entry": ("A distinct child-safe nighttime jungle wind gust moves through tree leaves as a gentle rain begins. The gust swells close and clearly for two seconds, then settles, with quiet crickets underneath. Establish a windy evening immediately. No thunder, no frightening howl, no voices, no music.", 3.0, False),
    "JR_103_bed": ("Seamless loop of windy evening jungle atmosphere for a child's story: continuous soft wind moving through leaves, light steady rain, and a few quiet crickets. Wind remains recognizable in pauses but the bed stays gentle beneath speech. No thunder, no voices, no music.", 12.0, True),
    "JR_105": ("A few leaves rustle quietly behind a large rock in an evening jungle, brief and close, curious but safe. No creature vocal, no voices, no music.", 1.1, False),
    "JR_114": ("A small character trips on a tree root: one little scuff and soft padded comedy thud, harmless and funny, no scream, no voices, no music.", 1.0, False),
    "JR_120": ("A heavy handheld flashlight switch clicks on, immediately followed by a brief bright electronic beam hum that fades. Friendly and clear, no voices, no music.", 1.2, False),
    "JR_122": ("A short, gentle flashlight beam sweeps across a dark rock: one light airy whoosh, playful and safe, no sci-fi laser, no voices, no music.", 0.7, False),
    "JR_126": ("One brief, gentle cool breeze brushes leaves near a jungle cave at night. A soft airy whoosh and light leaf flutter only. No teeth chatter, no animal voice, no rain, no music, not frightening.", 1.3, False),
    "JR_129_entry": ("Three small gentle footsteps move from wet evening jungle into a dry cave. Outdoor wind and rain rapidly become muffled behind them. Cozy and safe, no echo, no voices, no music.", 2.0, False),
    "JR_129_bed": ("Seamless loop inside a dry sheltered jungle cave at night: barely audible calm air and very muffled distant rain outside. Warm, cozy, quiet, no dripping inside, no echo, no voices, no music.", 12.0, True),
    "JR_131": ("A large dry leaf crinkles as it is lifted, then tears cleanly in half with one crisp funny rip. No other impacts, no voices, no music.", 1.5, False),
    "JR_132_sting": ("A tiny playful two-note comic mistake sting, like a soft pluck followed by a shorter bouncy pluck. Child-safe, light and funny, clearly after a harmless silly mistake. No wrong-answer buzzer, no alarm, no voice, no music, no ambience.", 0.8, False),
    "JR_139_fabric": ("A thick soft blanket unfurls and settles over a small childlike lion with one gentle fabric rustle. No voice, no sigh, no music.", 1.2, False),
    "JR_147_settle": ("A small sleepy animal nestles comfortably into a blanket on a dry cave floor, one soft fabric and body settling movement. No snore, no voice, no music.", 0.8, False),
    "JR_147_snore_series": ("Three clearly distinct sleepy snoring breaths from the same small lion cub. First a funny nasal inhaling rasp and warm rumbling exhale, second a slightly bigger comic snore, third softer and fading as the cub falls deeply asleep. Natural uneven rhythm, each snore recognizable on laptop speakers. No words, no music, no other animals, no adult roar.", 6.0, False),
}
AUDITION_SFX = {
    # Retained solely so the user can hear the earlier effect in isolation.
    "JR_106_lion": ("One short, unmistakable lion cub vocal immediately after three big sneezes: a small rounded chesty 'rrr-ow' with a gentle, playful tail. It belongs to a young lion hiding behind a rock, curious and a little embarrassed. Natural animal sound, not a human voice, not a cat meow, no words, no adult lion attack roar, no harsh start, no music or ambience.", 1.3, False),
    "JR_112": ("A young lion cub's single grumpy, comical mini-roar in response to someone offering to find his tail: a clear low 'grrr-ROW' with a quick firm onset and rounded finish. Recognizably a lion, small and child-friendly, annoyed rather than scary. Natural animal vocal only; no human words, no meow, no adult attack roar, no distortion, no thunder, no music or ambience.", 1.4, False),
}
REUSED = {"JR_119": "../elephant-rescue-test/JR_040.mp3",
          "JR_124": "../../audio_candidates/shipped_owl.mp3",
          "JR_138": "../elephant-rescue-test/JR_040.mp3"}
MUSIC_PROMPT = (
    "An original gentle ten-second instrumental lullaby for a four-year-old's jungle story. "
    "Soft warm music-box notes, very simple slow three-note motif, spacious and soothing, "
    "subtle warm pad, no percussion, no singing, no words, no recognizable traditional tune. "
    "Leave clear room for a separate childlike voice humming over it. End with a soft sustained note."
)


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


def render(source, target, filter_string, complex_filter=False):
    temporary = OUT / f".{target.stem}.rendering.mp3"
    cmd = [ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source)]
    if complex_filter:
        cmd += ["-filter_complex", filter_string, "-map", "[out]"]
    else:
        cmd += ["-af", filter_string]
    cmd += ["-ac", "1", "-ar", "44100", "-b:a", "128k", str(temporary)]
    subprocess.run(cmd, check=True)
    os.replace(temporary, target)


def speech_asset(name, role, words, tag, key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_IDS[role]}?output_format={FORMAT}"
    raw_name = RAW_REVISIONS.get(name, name)
    record = RAW / f"{raw_name}.request.json"
    if record.exists():
        # Preserve reviewed older takes, but do not send free-form directions in new TTS text.
        body = json.loads(record.read_text(encoding="utf-8"))
        if name != "JR_106" and not body.get("text", "").endswith(words):
            raise ValueError(f"{raw_name}: cached speech no longer matches the script")
    else:
        dialogue = re.sub(r"^\[[^\]]+\]\s*", "", words)
        body = {"text": dialogue, "model_id": MODEL,
                "voice_settings": VOICE_SETTINGS[role]}
    raw = api_asset(raw_name, body, url, key)
    if name == "JR_106":
        # The approved three-sneeze Bholu take has a clean gap after sneeze two.
        render(raw, OUT / "JR_106.mp3",
               LION_FILTER + ",atrim=end=2.33,asetpts=PTS-STARTPTS,"
               "afade=t=out:st=2.17:d=0.16")
    elif role == "LION":
        render(raw, OUT / f"{name}.mp3", LION_FILTER)
    elif name == "JR_145":
        # Keep a separate ten-second Coco vocal stem; never bake it into music.
        alternatives = OUT / "alternatives"
        alternatives.mkdir(exist_ok=True)
        first_take = OUT / "JR_145.mp3"
        archive = alternatives / "JR_145_short_first_take.mp3"
        if first_take.exists() and not archive.exists():
            shutil.copyfile(first_take, archive)
        render(raw, OUT / "JR_145.mp3",
               "apad=whole_dur=10,atrim=end=10,asetpts=N/SR/TB,"
               "afade=t=out:st=9.65:d=0.35,"
               "highpass=f=130,lowpass=f=6500,"
               "loudnorm=I=-23:TP=-4:LRA=11,alimiter=limit=0.65:level=false,"
               "afade=t=in:st=0:d=0.3,volume=1.3")
    elif name == "JR_143":
        render(raw, OUT / f"{name}.mp3",
               "loudnorm=I=-20:TP=-3:LRA=11,alimiter=limit=0.72:level=false")
    else:
        render(raw, OUT / f"{name}.mp3",
               "loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false")


def sfx_asset(name, prompt, seconds, loop, key):
    body = {"text": prompt, "model_id": "eleven_text_to_sound_v2",
            "duration_seconds": seconds, "prompt_influence": 0.8, "loop": loop}
    url = f"https://api.elevenlabs.io/v1/sound-generation?output_format={FORMAT}"
    raw = api_asset(RAW_REVISIONS.get(name, name), body, url, key)
    sfx_filter = (
        "loudnorm=I=-22:TP=-4:LRA=11,alimiter=limit=0.63:level=false" if loop else
        "afade=t=in:st=0:d=0.06,loudnorm=I=-17:TP=-3:LRA=11,alimiter=limit=0.75:level=false" if name == "JR_106_lion" else
        "loudnorm=I=-18:TP=-3:LRA=11,alimiter=limit=0.75:level=false" if name in ("JR_147_snore_series", "JR_103_entry") else
        "loudnorm=I=-20:TP=-4:LRA=11,alimiter=limit=0.63:level=false"
    )
    render(raw, OUT / f"{name}.mp3", sfx_filter)


def music_asset(key):
    body = {"prompt": MUSIC_PROMPT, "music_length_ms": 10000,
            "model_id": "music_v2", "force_instrumental": True}
    url = "https://api.elevenlabs.io/v1/music?output_format=mp3_48000_192"
    raw = api_asset("JR_144", body, url, key)
    render(raw, OUT / "JR_144.mp3",
           "apad=whole_dur=10,atrim=end=10,asetpts=N/SR/TB,"
           "afade=t=out:st=9.65:d=0.35,"
           "loudnorm=I=-24:TP=-5:LRA=11,alimiter=limit=0.56:level=false,"
           "afade=t=in:st=0:d=0.3,volume=1.3")


def concatenate(parts, target):
    inputs = []
    for part in parts:
        inputs += ["-i", str(part)]
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


def assemble_three_snores():
    """Edit three distinct breaths; the sound model alone did not keep three beats."""
    series = OUT / "JR_147_snore_series.mp3"
    render(series, OUT / "JR_147_snore_1.mp3",
           "atrim=start=0:end=1.6,asetpts=PTS-STARTPTS,"
           "loudnorm=I=-19:TP=-3:LRA=11,alimiter=limit=0.7:level=false")
    render(series, OUT / "JR_147_snore_2.mp3",
           "atrim=start=3.2:end=5.0,asetpts=PTS-STARTPTS,"
           "loudnorm=I=-17.5:TP=-3:LRA=11,alimiter=limit=0.7:level=false")
    render(RAW / "JR_147_snore_v2.mp3", OUT / "JR_147_snore_3.mp3",
           "atrim=start=0:end=1.8,asetpts=PTS-STARTPTS,"
           "loudnorm=I=-22:TP=-4:LRA=11,alimiter=limit=0.6:level=false")
    gap = OUT / "JR_147_gap.mp3"
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "0.22", "-ac", "1", "-ar", "44100", "-b:a", "128k",
                    str(gap)], check=True)
    concatenate([OUT / "JR_147_settle.mp3", OUT / "JR_147_snore_1.mp3", gap,
                 OUT / "JR_147_snore_2.mp3", gap, OUT / "JR_147_snore_3.mp3"],
                OUT / "JR_147.mp3")


def main():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(exist_ok=True)
    previous = OUT / "alternatives" / "review_before_light_lion"
    if not previous.exists():
        previous.mkdir(parents=True)
        for source in OUT.glob("JR_*.mp3"):
            shutil.copyfile(source, previous / source.name)
        if (OUT / "manifest.json").exists():
            shutil.copyfile(OUT / "manifest.json", previous / "manifest.json")
    parsed = parse_cues()
    for cue_id, (role, tag) in SPEECH.items():
        actual_role, text = parsed[cue_id]
        if role != actual_role:
            raise ValueError(f"{cue_id}: script speaker changed")
        speech_asset(cue_id, role, text, tag, key)
    for name, (role, text) in NONVERBAL.items():
        speech_asset(name, role, text, "[natural character voice]", key)
    for name, (prompt, seconds, loop) in SFX.items():
        sfx_asset(name, prompt, seconds, loop, key)
    for name, (prompt, seconds, loop) in AUDITION_SFX.items():
        # These two reviewed sounds are reused verbatim; they are copied below and
        # must not be regenerated against their original request records.
        if name in {"JR_106_lion", "JR_112"}:
            continue
        sfx_asset(name, prompt, seconds, loop, key)
    entrance_roar = OUT / "intro-roar-auditions" / "roar_a.mp3"
    if not entrance_roar.is_file():
        raise FileNotFoundError(f"Build entrance roar A first: {entrance_roar}")
    shutil.copyfile(entrance_roar, OUT / "JR_106_lion.mp3")
    selected_jeep = OUT / "jeep-auditions" / "jeep_d_layered_engine.mp3"
    if not selected_jeep.is_file():
        raise FileNotFoundError(f"Build the selected Jeep D audition first: {selected_jeep}")
    shutil.copyfile(selected_jeep, OUT / "JR_103_jeep.mp3")
    music_asset(key)
    for cue_id, path in REUSED.items():
        source = (OUT / path).resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        if cue_id == "JR_124":
            render(source, OUT / f"{cue_id}.mp3",
                   "loudnorm=I=-20:TP=-4:LRA=11,alimiter=limit=0.63:level=false")
        else:
            shutil.copyfile(source, OUT / f"{cue_id}.mp3")
    concatenate([OUT / "JR_139_fabric.mp3", OUT / "JR_139_lion.mp3"],
                OUT / "JR_139.mp3")
    assemble_three_snores()
    manifest = {}
    for number in range(103, 150):
        cue_id = f"JR_{number:03d}"
        if cue_id in RETIRED:
            manifest[cue_id] = {"type": "retired", "review_status": "retired",
                                "reason": "Removed from playback after child-experience review"}
            continue
        if cue_id in ("JR_103", "JR_129"):
            entry_path = OUT / f"{cue_id}_entry.mp3"
            bed_path = OUT / f"{cue_id}_bed.mp3"
            split_entry = {
                "type": "split_sfx", "review_status": "test",
                "entry_file": f"lion-rescue-test/{entry_path.name}",
                "bed_file": f"lion-rescue-test/{bed_path.name}",
                "entry_duration_seconds": duration(entry_path),
                "bed_duration_seconds": duration(bed_path),
                "bed_loop": True,
            }
            if cue_id == "JR_103":
                jeep_path = OUT / "JR_103_jeep.mp3"
                split_entry["jeep_file"] = f"lion-rescue-test/{jeep_path.name}"
                split_entry["jeep_duration_seconds"] = duration(jeep_path)
                split_entry["jeep_source_file"] = "lion-rescue-test/jeep-auditions/jeep_d_layered_engine.mp3"
                split_entry["jeep_components"] = ["engine_drive", "tire_gravel", "brake_engine_off"]
                split_entry["jeep_selection"] = "D — approved by user"
            manifest[cue_id] = split_entry
            continue
        path = OUT / f"{cue_id}.mp3"
        if not path.is_file():
            raise FileNotFoundError(path)
        lufs, peak = measure(path)
        entry = {"file": f"lion-rescue-test/{path.name}",
                 "duration_seconds": duration(path), "integrated_lufs": lufs,
                 "true_peak_dbfs": peak, "review_status": "test"}
        if cue_id in SPEECH:
            role, tag = SPEECH[cue_id]
            raw_name = RAW_REVISIONS.get(cue_id, cue_id)
            source_request = json.loads((RAW / f"{raw_name}.request.json").read_text(encoding="utf-8"))
            entry.update({"type": "speech", "voice": role, "voice_id": VOICE_IDS[role],
                          "model_id": source_request["model_id"],
                          "voice_settings": source_request["voice_settings"],
                          "spoken_text": parsed[cue_id][1], "performance_tag": tag,
                          "source_file": f"raw/{raw_name}.mp3"})
            if role == "LION":
                entry["character_filter"] = LION_FILTER
        elif cue_id in ("JR_106", "JR_139", "JR_145", "JR_147"):
            entry["type"] = "character_nonverbal"
        elif cue_id == "JR_144":
            entry.update({"type": "music", "model_id": "music_v2",
                          "source_file": "raw/JR_144.mp3",
                          "exact_runtime_seconds": 10.0})
        else:
            entry["type"] = "sfx"
        if cue_id in ("JR_119", "JR_138"):
            entry["alias_of"] = "JR_040"
        if cue_id == "JR_124":
            entry["source_file"] = "audio_candidates/shipped_owl.mp3"
        if cue_id == "JR_139":
            entry["components"] = ["JR_139_fabric.mp3", "JR_139_lion.mp3"]
        if cue_id == "JR_145":
            entry.update({"voice": "COCO", "voice_id": VOICE_IDS["COCO"],
                          "model_id": MODEL, "source_file": "raw/JR_145_v3.mp3",
                          "exact_runtime_seconds": 10.0})
        if cue_id == "JR_147":
            entry.update({"intended_character": "LION", "model_id": "eleven_text_to_sound_v2",
                          "components": ["JR_147_settle.mp3", "JR_147_snore_1.mp3",
                                         "JR_147_gap.mp3", "JR_147_snore_2.mp3",
                                         "JR_147_gap.mp3", "JR_147_snore_3.mp3"],
                          "source_files": ["raw/JR_147_snore_series_v1.mp3",
                                           "raw/JR_147_snore_v2.mp3"]})
        manifest[cue_id] = entry
    manifest["JR_106"]["source_edit"] = "First two sneezes from raw/JR_106.mp3; trimmed in a silent gap after sneeze two."
    manifest["JR_106_lion"] = {
        "file": "lion-rescue-test/JR_106_lion.mp3", "type": "sfx",
        "intended_character": "LION", "review_status": "selected_for_route",
        "source_file": "intro-roar-auditions/roar_a.mp3",
        "placement": "immediately after the second sneeze and before JR_107",
    }
    sting_path = OUT / "JR_132_sting.mp3"
    sting_lufs, sting_peak = measure(sting_path)
    manifest["JR_132_sting"] = {
        "file": "lion-rescue-test/JR_132_sting.mp3", "type": "sfx",
        "review_status": "test", "duration_seconds": duration(sting_path),
        "integrated_lufs": sting_lufs, "true_peak_dbfs": sting_peak,
        "placement": "immediately after JR_132's spoken Ye kon karta hai line",
    }
    manifest["JR_112_huff"] = {"type": "retired", "review_status": "retired",
                                "reason": "Generic effect did not match Bholu's voice"}
    for cue_id in ("JR_103_jeep_alt",):
        path = OUT / f"{cue_id}.mp3"
        lufs, peak = measure(path)
        manifest[cue_id] = {
            "file": f"lion-rescue-test/{path.name}",
            "type": "sfx_audition",
            "review_status": "audition_only" if cue_id == "JR_103_jeep_alt" else "retired_from_route",
            "duration_seconds": duration(path), "integrated_lufs": lufs,
            "true_peak_dbfs": peak, "model_id": "eleven_text_to_sound_v2",
            "source_file": f"raw/{RAW_REVISIONS.get(cue_id, cue_id)}.mp3",
        }
    manifest["JR_106_lion"] = {
        "file": "lion-rescue-test/JR_106_lion.mp3", "type": "sfx",
        "intended_character": "LION", "review_status": "selected_for_route",
        "source_file": "intro-roar-auditions/roar_a.mp3",
        "placement": "immediately after the second sneeze and before JR_107",
    }
    manifest["_batch"] = {"name": "Lion Rescue production test",
                          "range": "JR_103–JR_149", "format": FORMAT,
                          "script": SCRIPT.name,
                          "note": "Review MP3s; 10-second separate lori stems; childlike Bholu Lion with light natural-pitch treatment pending approval."}
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved Lion Rescue manifest", flush=True)


if __name__ == "__main__":
    main()
