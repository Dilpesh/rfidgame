#!/usr/bin/env python3
"""Make reversible Elephant Vardan and Lion Bholu character auditions.

The clear speech stays dominant. Quiet shaped layers add body/texture; animal
calls are placed before speech, never over words. These are audition previews,
not final JR_NNN exports. Existing output files are never overwritten.
"""

import json
import subprocess
from pathlib import Path

from generate_voice_auditions import duration
from make_elephant_treatment import ffmpeg, measure


HERE = Path(__file__).resolve().parent
OUT = HERE / "voice_auditions"
SOURCES = {
    "ELEPHANT": OUT / "elephant_vardan_playful.mp3",
    "LION": OUT / "lion_bholu.mp3",
}
OUTPUTS = {
    "ELEPHANT": OUT / "elephant_vardan_character.mp3",
    "LION": OUT / "lion_bholu_character.mp3",
}
CALLS = {
    "ELEPHANT": HERE / "audio_candidates" / "old_sfx_elephant.mp3",
    "LION": OUT / "lion_cub_soft_call.mp3",
}
CONTEXT = {
    "ELEPHANT": OUT / "elephant_vardan_character_with_call.mp3",
    "LION": OUT / "lion_bholu_character_with_call.mp3",
}
FILTERS = {
    "ELEPHANT": (
        "[0:a]asplit=2[clear0][body0];"
        "[clear0]asetrate=43218,aresample=44100,atempo=1.020408,"
        "highpass=f=105,equalizer=f=650:t=q:w=1:g=2.5,"
        "equalizer=f=950:t=q:w=1:g=2.5,"
        "equalizer=f=2500:t=q:w=0.9:g=2[clear];"
        "[body0]asetrate=37485,aresample=44100,atempo=1.176471,"
        "highpass=f=380,lowpass=f=1050,volume=0.20[body];"
        "[clear][body]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
    ),
    "LION": (
        "[0:a]asplit=2[clear0][throat0];"
        "[clear0]highpass=f=120,equalizer=f=630:t=q:w=1:g=1.5,"
        "equalizer=f=2400:t=q:w=0.9:g=2[clear];"
        "[throat0]asetrate=41454,aresample=44100,atempo=1.06383,"
        "highpass=f=420,lowpass=f=1500,volume=2,"
        "asoftclip=type=tanh:threshold=0.35:oversample=4,"
        "volume=0.11[throat];"
        "[clear][throat]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11,alimiter=limit=0.95[out]"
    ),
}


def render_voice(role):
    source, target = SOURCES[role], OUTPUTS[role]
    if target.exists():
        print(f"Existing: {target.name}; skipping")
        return
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(source), "-filter_complex", FILTERS[role], "-map", "[out]",
                    "-ac", "1", "-ar", "44100", "-b:a", "128k", str(target)], check=True)
    print(f"Rendered: {target.name}")


def render_context(role):
    call, voice, target = CALLS[role], OUTPUTS[role], CONTEXT[role]
    if not call.is_file():
        print(f"No call yet for {role}; voice-only audition is ready")
        return False
    if target.exists():
        print(f"Existing: {target.name}; skipping")
        return True
    graph = (
        "[0:a]aformat=channel_layouts=mono,loudnorm=I=-21:TP=-3:LRA=11[call];"
        "anullsrc=r=44100:cl=mono:d=0.25[gap];"
        "[1:a]anull[voice];"
        "[call][gap][voice]concat=n=3:v=0:a=1[out]"
    )
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(call), "-i", str(voice), "-filter_complex", graph,
                    "-map", "[out]", "-ac", "1", "-ar", "44100", "-b:a", "128k", str(target)],
                   check=True)
    print(f"Rendered: {target.name}")
    return True


def main():
    for role, source in SOURCES.items():
        if not source.is_file():
            raise SystemExit(f"Missing selected source for {role}: {source}")
        render_voice(role)
    manifest = {
        "purpose": "Character-voice treatment auditions only; not final JR_NNN cues",
        "cast": {"ELEPHANT": {"voice": "Vardan", "voice_id": "bBG9wwa23659EgIkMbc1"},
                 "LION": {"voice": "Bholu", "voice_id": "5krdMTA5HonvWAlY2vSx"}},
        "roles": {},
        "note": "The clear speech stays dominant. Listen on the child's phone speaker before approving treatment. Animal call clips are separate from words in production.",
    }
    for role in SOURCES:
        source, target = SOURCES[role], OUTPUTS[role]
        if abs(duration(target) - duration(source)) > 0.12:
            raise ValueError(f"Duration drifted: {role}")
        lufs, peak = measure(target)
        if peak > -1.3:
            raise ValueError(f"Excessive true peak: {role}")
        has_context = render_context(role)
        manifest["roles"][role] = {
            "source_file": source.name,
            "treated_file": target.name,
            "duration_seconds": duration(target),
            "integrated_lufs": lufs,
            "true_peak_dbfs": peak,
            "filter": FILTERS[role],
            "animal_call_file": str(CALLS[role].relative_to(HERE)) if role == "ELEPHANT" else CALLS[role].name,
            "context_preview_file": CONTEXT[role].name if has_context else None,
        }
    target = OUT / "selected_character_treatments_manifest.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target}")


if __name__ == "__main__":
    main()
