#!/usr/bin/env python3
"""
Measure the horn takes and say which pair actually contrasts.

    python3 tts/pick_horns.py                 # report + recommendation
    python3 tts/pick_horns.py --install       # level the winners into the game

The whole point of these two sounds is that they are DIFFERENT. The pair
currently in the game measures within about 1 dB of each other in every band
below 1.2 kHz, which is why "तुम train हो या बिल्ली?" cannot land - the cat and
the train make the same noise, so there is nothing to laugh at.

A laptop speaker will not tell you this. It rolls off the low end, which is
exactly the band the difference lives in. Hence measuring.

Acceptance, from scripts/ELEVENLABS_BRIEF.md:
  * the TRAIN must be at least 12 dB louder than the CAT in 60-400 Hz
  * the CAT must be at least 6 dB louder than the TRAIN in 1200-4000 Hz
  * neither may be near silent - both must reach -20 dB mean after levelling
"""
import argparse, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAKES = HERE / "out" / "horns"
GAME = HERE.parent / "docs" / "toy-town-v2" / "audio"
BANDS = [(60, 400), (400, 1200), (1200, 4000)]
LOW, HIGH = 0, 2


def mean_db(path, lo=None, hi=None):
    af = "volumedetect"
    if lo is not None:
        af = "highpass=f=%d,lowpass=f=%d,%s" % (lo, hi, af)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                        "-af", af, "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", r.stderr)
    return float(m.group(1)) if m else None


def profile(path):
    return [mean_db(path, lo, hi) for lo, hi in BANDS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true",
                    help="level the best pair and copy into docs/toy-town-v2/audio")
    a = ap.parse_args()

    if not TAKES.is_dir():
        print("No takes yet. Run: python3 tts/make_horns.py")
        return 1
    cats = sorted(TAKES.glob("horn_meow_take*.mp3"))
    trains = sorted(TAKES.glob("horn_train_soft_take*.mp3"))
    if not cats or not trains:
        print("Need takes of both. Found %d cat, %d train." % (len(cats), len(trains)))
        return 1

    print("%-28s %9s %9s %9s" % ("take", "60-400", "400-1.2k", "1.2k-4k"))
    prof = {}
    for p in cats + trains:
        prof[p] = profile(p)
        print("%-28s %8.1f %9.1f %9.1f" % (p.name, *prof[p]))

    # The best pair is the one whose difference is largest where it matters.
    best, score = None, -1e9
    for c in cats:
        for t in trains:
            low = prof[t][LOW] - prof[c][LOW]        # train should dominate down low
            high = prof[c][HIGH] - prof[t][HIGH]     # cat should dominate up high
            s = min(low, 12) + min(high, 6)          # cap, so one axis cannot carry it
            if s > score:
                best, score = (c, t, low, high), s

    c, t, low, high = best
    print("\nBest pair:")
    print("  cat   %s" % c.name)
    print("  train %s" % t.name)
    print("  train is %+.1f dB vs the cat in 60-400 Hz   (need >= +12)   %s"
          % (low, "PASS" if low >= 12 else "FAIL"))
    print("  cat   is %+.1f dB vs the train in 1.2-4 kHz  (need >= +6)    %s"
          % (high, "PASS" if high >= 6 else "FAIL"))

    if low < 12 or high < 6:
        print("\nNot enough contrast yet. These two would sound like the same thing again.")
        print("Generate more takes - it is the cheap part:")
        print("  python3 tts/make_horns.py --takes 6")
        return 1

    print("\nBoth pass. Listen to them back to back before installing:")
    print("  ffmpeg -i %s -i %s -filter_complex '[0][1]concat=n=2:v=0:a=1' -y /tmp/horns.mp3"
          % (c.name, t.name))

    if not a.install:
        print("\nHappy with them?  python3 tts/pick_horns.py --install")
        return 0

    for src, name in ((c, "horn_meow"), (t, "horn_train_soft")):
        m = mean_db(src)
        gain = -20.0 - m
        dst = GAME / (name + ".mp3")
        tmp = TAKES / ("_lvl_" + name + ".mp3")
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                        "-i", str(src),
                        "-af", "volume=%.2fdB,alimiter=limit=0.85:level=false" % gain,
                        "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True)
        shutil.copyfile(tmp, dst)
        tmp.unlink()
        print("installed %-18s %+.1f dB -> %.1f dB mean" % (name, gain, mean_db(dst)))

    print("\nIn docs/toy-town-v2/audio only. The original toy-town is untouched.")
    print("Tell Claude and the gates get re-run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
