#!/usr/bin/env python3
"""Master the audio inside a self-contained build that has no audio/ folder.

    python3 tts/master_embedded.py docs/jungle-rescue-hinglish/index.html
    python3 tts/master_embedded.py <file> --check      # report only, write nothing

A build that embeds its cues as base64 can't be fixed by check_audio.py or the
rest of the pipeline, so this does it in place: pull every cue out of the
`media` object, run it through the right AUDIO_STANDARD.md chain for its kind,
and put it back.

Three kinds, three chains:
  speech  - presence lift and -16 LUFS, so every line lands the same on a phone
  effect  - levelled a little under the narration, left bright
  bed     - anything that plays UNDER narration; left alone here because it
            needs measuring, not a blanket filter (see check_audio.py)
"""
import base64, json, os, re, subprocess, sys, tempfile, statistics

# Shaping only - levelling is done separately, by measured gain.
#
# loudnorm's one-pass dynamic mode is wrong for this material: it needs about
# three seconds to judge a programme, and these cues include 15 hint lines
# under 3 s. Run through it they came out as low as -44.7 LUFS - effectively
# silent - while the long lines landed perfectly. So measure each clip, then
# apply a constant gain, which behaves the same at any length.
SPEECH_EQ = ("highpass=f=110,"
             "equalizer=f=1500:t=q:w=1.0:g=2.5,"
             "equalizer=f=2800:t=q:w=0.9:g=4.5,"
             "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=180:makeup=2")
EFFECT_EQ = "anull"
TARGET = {"speech": -16.0, "effect": -18.0}

# Cues that are sounds rather than speech. Everything else is treated as speech.
EFFECT_CUES = {
    "fuel", "rope", "ladder", "firstaid", "flashlight", "engine", "engineCough",
    "mud", "stomach", "munchEle", "munchGir", "gulp", "owl", "snore", "boing",
    "ting", "dance", "freeze", "elephant", "elephantFree", "parrotFall",
    "parrotFly", "highfive",
}
BED_CUES = {"dayAmb", "nightAmb"}


def measure(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    i = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', r.stderr)
    t = re.search(r'"input_tp"\s*:\s*"(-?[\d.]+)"', r.stderr)
    return (float(i.group(1)) if i else None, float(t.group(1)) if t else None)


def report(label, rows):
    if not rows:
        return
    L = [r[0] for r in rows if r[0] is not None]
    T = [r[1] for r in rows if r[1] is not None]
    print("  %-22s %3d clips   median %6.1f LUFS   spread %4.1f dB   "
          "peak %+5.1f dBFS   %d clipping"
          % (label, len(rows), statistics.median(L), max(L) - min(L), max(T),
             sum(1 for t in T if t > 0)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    check = "--check" in sys.argv
    if not args:
        sys.exit(__doc__)
    path = args[0]
    s = open(path, encoding="utf-8").read()
    m = re.search(r"const media=(\{.*?\});", s, re.S)
    if not m:
        sys.exit("%s: no embedded `media` object found" % path)
    media = json.loads(m.group(1))
    print("%s: %d cues embedded" % (path, len(media)))

    tmp = tempfile.mkdtemp()
    before = {"speech": [], "effect": [], "bed": []}
    after = {"speech": [], "effect": [], "bed": []}
    out = {}
    changed = 0

    for k, b64 in media.items():
        kind = "bed" if k in BED_CUES else ("effect" if k in EFFECT_CUES else "speech")
        src = os.path.join(tmp, k + ".mp3")
        open(src, "wb").write(base64.b64decode(b64))
        before[kind].append(measure(src))
        if kind == "bed" or check:
            out[k] = b64
            after[kind].append(before[kind][-1])
            continue
        eq = SPEECH_EQ if kind == "speech" else EFFECT_EQ
        # pass 1: how loud is it after shaping?
        shaped = os.path.join(tmp, k + ".eq.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", eq,
                        "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", shaped],
                       check=True)
        lufs, _ = measure(shaped)
        gain = 0.0 if lufs is None else max(-24.0, min(24.0, TARGET[kind] - lufs))
        # pass 2: shape, apply that gain, catch any peak it creates
        dst = os.path.join(tmp, k + ".out.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                        "%s,volume=%.2fdB,alimiter=limit=0.85:level=false" % (eq, gain),
                        "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", dst],
                       check=True)
        after[kind].append(measure(dst))
        out[k] = base64.b64encode(open(dst, "rb").read()).decode()
        changed += 1

    print("\nbefore:")
    for kind in ("speech", "effect", "bed"):
        report(kind, before[kind])
    if check:
        print("\n--check: nothing written.")
        return 0
    print("\nafter:")
    for kind in ("speech", "effect", "bed"):
        report(kind, after[kind])

    new = "const media=" + json.dumps(out, separators=(",", ":")) + ";"
    open(path, "w", encoding="utf-8").write(s[:m.start()] + new + s[m.end():])
    print("\nre-embedded %d cues (%d beds left alone - measure those with "
          "check_audio.py logic instead)" % (changed, len(before["bed"])))
    print("new file size: %.1f MB" % (os.path.getsize(path) / 1e6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
