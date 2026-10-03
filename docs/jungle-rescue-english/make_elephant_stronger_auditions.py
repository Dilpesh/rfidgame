#!/usr/bin/env python3
"""Make two stronger adult-to-Elephant auditions from approved dialogue.

The source is an expressive adult Ravi TTS take, not Vardan or a child voice.
Run without --generate to inspect the plan; --generate creates only missing
assets and never charges again for existing ones.
"""

import argparse
import json
import os
import subprocess

from generate_voice_auditions import OUT, SETTINGS, duration, make_take
from make_elephant_treatment import ffmpeg, measure


VOICE_ID = "FF20guQVlAWTxmSRcTSk"  # Ravi, adult Hindi voice
TEXT = (
    "[playfully hungry] मेरे पेट में भूख से चूहे दौड़ रहे हैं।\n\n"
    "[eagerly] बस एक!\n\n"
    "[mischievously] बस दो... थोड़ा और दो!\n\n"
    "[comic surprise] चार! बस करो, Captain! इतना खाऊँगा तो balloon बनकर उड़ जाऊँगा!"
)
SOURCE = OUT / "elephant_ravi_directed_source.mp3"
DRY = OUT / "elephant_ravi_directed_levelmatched.mp3"
BIG = OUT / "elephant_ravi_big_warm.mp3"
TRUNKY = OUT / "elephant_ravi_trunky_playful.mp3"
DRY_FILTER = "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95,volume=-0.4dB"
BIG_FILTER = (
    "[0:a]asplit=2[lead0][body0];"
    "[lead0]asetrate=42336,aresample=44100,atempo=1.0416667,"
    "highpass=f=95,equalizer=f=560:t=q:w=1:g=3,"
    "equalizer=f=1000:t=q:w=1:g=1.5,"
    "equalizer=f=2500:t=q:w=0.9:g=2[lead];"
    "[body0]asetrate=38808,aresample=44100,atempo=1.136364,"
    "highpass=f=350,lowpass=f=1000,volume=0.18[body];"
    "[lead][body]amix=inputs=2:duration=first:normalize=0,"
    "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
)
TRUNKY_FILTER = (
    "[0:a]asplit=2[lead0][trunk0];"
    "[lead0]highpass=f=105,equalizer=f=700:t=q:w=1:g=2,"
    "equalizer=f=1000:t=q:w=1:g=3.5,"
    "equalizer=f=2500:t=q:w=0.9:g=2.5[lead];"
    "[trunk0]asetrate=40131,aresample=44100,atempo=1.09901,"
    "highpass=f=470,lowpass=f=1550,equalizer=f=900:t=q:w=0.5:g=5,"
    "volume=0.23[trunk];"
    "[lead][trunk]amix=inputs=2:duration=first:normalize=0,"
    "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
)


def render(target, filter_args):
    if target.exists():
        print(f"Existing: {target.name}; skipping")
        return
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(SOURCE),
                    *filter_args, "-ac", "1", "-ar", "44100", "-b:a", "128k", str(target)],
                   check=True)
    print(f"Rendered: {target.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true")
    args = parser.parse_args()
    print(f"Adult Ravi expressive Elephant audition: {len(TEXT)} characters, 2 local treatments")
    if not args.generate:
        return
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        raise SystemExit("ELEVENLABS_API_KEY is not set")
    OUT.mkdir(exist_ok=True)
    if SOURCE.exists():
        print(f"Existing: {SOURCE.name}; skipping charged generation", flush=True)
    else:
        print(f"Generating: {SOURCE.name}", flush=True)
        make_take(key, VOICE_ID, TEXT, SOURCE)
    render(DRY, ["-af", DRY_FILTER])
    render(BIG, ["-filter_complex", BIG_FILTER, "-map", "[out]"])
    render(TRUNKY, ["-filter_complex", TRUNKY_FILTER, "-map", "[out]"])
    source_duration = duration(SOURCE)
    metrics = {}
    for target in (DRY, BIG, TRUNKY):
        if abs(duration(target) - source_duration) > 0.12:
            raise ValueError(f"Duration drifted: {target.name}")
        lufs, peak = measure(target)
        if peak > -1.3:
            raise ValueError(f"Excessive true peak: {target.name}")
        metrics[target.name] = {"duration_seconds": duration(target),
                                "integrated_lufs": lufs, "true_peak_dbfs": peak}
    if max(item["integrated_lufs"] for item in metrics.values()) - min(
            item["integrated_lufs"] for item in metrics.values()) > 0.4:
        raise ValueError("Audition levels differ too much")
    manifest = {
        "purpose": "Adult-to-Elephant character auditions only; not final JR_NNN cues",
        "source_voice": "Ravi",
        "source_voice_id": VOICE_ID,
        "source_model": "eleven_v3",
        "source_voice_settings": SETTINGS,
        "source_text_with_performance_tags": TEXT,
        "source_cues": ["JR_053", "JR_062", "JR_063", "JR_065"],
        "source_file": SOURCE.name,
        "options": [
            {"file": DRY.name, "label": "Adult source, level matched", "filter": DRY_FILTER, **metrics[DRY.name]},
            {"file": BIG.name, "label": "Big and warm", "filter": BIG_FILTER, **metrics[BIG.name]},
            {"file": TRUNKY.name, "label": "Trunky and playful", "filter": TRUNKY_FILTER, **metrics[TRUNKY.name]},
        ],
        "note": "These local filters modify an adult source voice. They do not use Vardan or any child voice. Keep animal calls separate from the words.",
    }
    target = OUT / "elephant_stronger_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
