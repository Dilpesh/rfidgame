#!/usr/bin/env python3
"""Kahani Cards audio check — see AUDIO_STANDARD.md section 1.

    python3 check_audio.py docs/moon
    python3 check_audio.py docs/banana-rescue audio/music/banana_dance_music.mp3

Measures, through a phone-speaker simulation, how far the background bed sits
below the narration in every band. A bed that is quieter overall can still
bury speech if its energy is high-frequency, which is exactly what phone
speakers reproduce best.
"""
import subprocess, re, os, sys, math

BANDS = [(80,300),(300,1000),(1000,2000),(2000,3000),
         (3000,4000),(4000,6000),(6000,8000)]
# approximation of a phone loudspeaker: no bass below ~450 Hz, presence bump
PHONE = ("highpass=f=450:poles=2,highpass=f=450:poles=2,"
         "equalizer=f=3000:t=q:w=1.2:g=4")
DUCK_VOLUME = 0.12          # must match AMB_DUCK in index.html
REQUIRED_GAP_DB = -20.0     # bed must be at least this far below the voice


def band_energy(files, pre="", phone=True):
    out = []
    for lo, hi in BANDS:
        chain = ",".join(c for c in [
            pre,
            PHONE if phone else "",
            f"highpass=f={lo}:poles=2,highpass=f={lo}:poles=2,"
            f"lowpass=f={hi}:poles=2,lowpass=f={hi}:poles=2",
        ] if c)
        total, n = 0.0, 0
        for fn in files:
            p = subprocess.run(
                ["ffmpeg","-v","info","-i",fn,"-af",chain+",volumedetect",
                 "-f","null","-"], capture_output=True, text=True)
            m = re.search(r"mean_volume: (-?[\d.]+) dB", p.stderr)
            if m:
                total += 10 ** (float(m.group(1)) / 10); n += 1
        out.append(10 * math.log10(total / n) if n else float("nan"))
    return out


def find_narration(aud):
    """Every narration clip: vo_*.mp3 anywhere, or all of a narration/ folder."""
    hits = []
    for root, dirs, files in os.walk(aud):
        dirs[:] = [d for d in dirs if not d.startswith("_")]
        for f in files:
            if not f.endswith(".mp3"):
                continue
            if f.startswith("vo_") or os.path.basename(root) == "narration":
                hits.append(os.path.join(root, f))
    return sorted(hits)


def find_bed(story, aud, html):
    m = re.search(r'AMBIENCE\s*=\s*"([^"]+)"', html)
    if m:
        return os.path.join(aud, m.group(1))
    # Deliberately NOT guessing at audio/music/*: a track that plays on its
    # own (a dance break with no narration over it) is exempt from this
    # check. Only a bed that actually runs under speech counts — declare it
    # as AMBIENCE, or pass it on the command line.
    return None


def main():
    story = sys.argv[1] if len(sys.argv) > 1 else "."
    aud = os.path.join(story, "audio")
    html = open(os.path.join(story, "index.html"), encoding="utf-8").read()

    bed = os.path.join(story, sys.argv[2]) if len(sys.argv) > 2 \
        else find_bed(story, aud, html)
    voice = find_narration(aud)

    if not voice:
        sys.exit(f"no narration clips found under {aud}")
    if not bed or not os.path.exists(bed):
        print(f"narration clips: {len(voice)}")
        print("no continuous ambience bed found — nothing to measure.")
        print("If this story does play music under narration, pass it:")
        print(f"    python3 check_audio.py {story} audio/music/<file>.mp3")
        return 0

    print(f"bed: {os.path.relpath(bed, story)}   narration clips: {len(voice)}\n")
    v = band_energy(voice)
    b = band_energy([bed], f"volume={DUCK_VOLUME}")

    print(f"{'band':>13} {'voice dB':>9} {'bed dB':>8} {'gap':>8}")
    worst = -999.0
    for (lo, hi), vv, bb in zip(BANDS, v, b):
        gap = bb - vv
        worst = max(worst, gap)
        flag = "  <-- FAIL" if gap > REQUIRED_GAP_DB else ""
        print(f"{lo:5}-{hi:<6} {vv:9.1f} {bb:8.1f} {gap:+8.1f}{flag}")

    ok = worst <= REQUIRED_GAP_DB
    print(f"\nworst-case gap: {worst:+.1f} dB   "
          f"(need {REQUIRED_GAP_DB:+.0f} dB or lower)")
    print("PASS — bed stays under the voice on a phone" if ok else
          "FAIL — EQ the bed down (see AUDIO_STANDARD.md section 2)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
