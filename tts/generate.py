#!/usr/bin/env python3
"""Generate the story narration with ElevenLabs.

    export ELEVENLABS_API_KEY=sk_...

    python3 tts/generate.py voices                 # what voices your account has
    python3 tts/generate.py audition <id> [<id>..] # same 3 lines in each voice
    python3 tts/generate.py cost                   # characters and credits, spends nothing
    python3 tts/generate.py build moon             # every clip -> tts/out/moon/
    python3 tts/generate.py build moon --dry-run   # no API calls, silent files, proves the wiring
    python3 tts/generate.py install moon           # swap into the game, backing up what's there

Nothing here overwrites your own recordings until you run `install`, and that
keeps a timestamped backup. Generated clips go through the same mastering
chain as the human ones (see AUDIO_STANDARD.md) - a raw TTS clip is clean but
not phone-ready, and will vanish under the ambience on a phone speaker.
"""
import json, os, sys, subprocess, hashlib, urllib.request, urllib.error, shutil, time, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTS  = os.path.join(ROOT, "tts")
SRC  = os.path.join(ROOT, "scripts", "source")
DOCS = os.path.join(ROOT, "docs")
OUT  = os.path.join(TTS, "out")
API  = "https://api.elevenlabs.io"

SHEETS = ["retake.json", "rescue-bridges.json", "rescue-story.json", "moon.json"]

# AUDIO_STANDARD.md section 2 - narration chain. Presence lift where a phone
# speaker is efficient, then levelled to -16 LUFS like every other clip.
MASTER = ("highpass=f=110,"
          "equalizer=f=1500:t=q:w=1.0:g=2.5,"
          "equalizer=f=2800:t=q:w=0.9:g=4.5,"
          "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=180:makeup=2,"
          "loudnorm=I=-16:TP=-1.5:LRA=11,"
          "alimiter=limit=0.95")


def cfg():
    return json.load(open(os.path.join(TTS, "config.json"), encoding="utf-8"))


def key(required=True):
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not k and required:
        sys.exit("ELEVENLABS_API_KEY is not set.\n"
                 "  export ELEVENLABS_API_KEY=sk_...   (get one at elevenlabs.io > profile > API keys)")
    return k


def lines():
    """clip filename -> Hindi line, from the same sheets the scripts use."""
    out = {}
    for s in SHEETS:
        p = os.path.join(SRC, s)
        if not os.path.exists(p):
            continue
        for row in json.load(open(p, encoding="utf-8")):
            if len(row) >= 4 and row[0] not in out:
                out[row[0]] = row[3]
    return out


def clips_for(game):
    aud = os.path.join(DOCS, game, "audio")
    if not os.path.isdir(aud):
        sys.exit("no such story: %s" % game)
    L = lines()
    got = sorted(f for f in os.listdir(aud)
                 if f.startswith("vo_") and f.endswith(".mp3") and f in L)
    return [(f, L[f]) for f in got]


def api(path, method="GET", body=None, raw=False):
    req = urllib.request.Request(API + path, method=method)
    req.add_header("xi-api-key", key())
    if body is not None:
        req.add_header("Content-Type", "application/json")
        body = json.dumps(body).encode("utf-8")
    try:
        with urllib.request.urlopen(req, body, timeout=120) as r:
            return r.read() if raw else json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        sys.exit("ElevenLabs said %s for %s\n  %s" % (e.code, path, detail))
    except urllib.error.URLError as e:
        sys.exit("could not reach ElevenLabs: %s" % e.reason)


def speak(text, voice, c, dest, dry=False):
    """One clip: generate, then master. Returns False if it was already there."""
    stamp = hashlib.sha1(
        ("%s|%s|%s|%s" % (text, voice, c["model_id"],
                          json.dumps(c["voice_settings"], sort_keys=True))).encode()
    ).hexdigest()[:12]
    marker = dest + ".stamp"
    if os.path.exists(dest) and os.path.exists(marker) and \
       open(marker).read().strip() == stamp:
        return False                      # unchanged since last run - don't re-spend credits

    # raw download goes to a scratch file outside the repo, so a failed run
    # never leaves half-finished audio sitting next to the good clips
    fd, tmp = tempfile.mkstemp(suffix=".raw.mp3")
    os.close(fd)
    if dry:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "anullsrc=r=44100:cl=mono", "-t",
                        "%.2f" % max(1.0, len(text) / 9.0),
                        "-c:a", "libmp3lame", "-b:a", "128k", tmp], check=True)
    else:
        audio = api("/v1/text-to-speech/%s?output_format=%s" % (voice, c["output_format"]),
                    "POST",
                    {"text": text, "model_id": c["model_id"],
                     "voice_settings": c["voice_settings"]},
                    raw=True)
        open(tmp, "wb").write(audio)

    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", MASTER,
                    "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k",
                    "-ar", "44100", dest], check=True)
    try:
        os.remove(tmp)
    except OSError:
        pass
    open(marker, "w").write(stamp)
    return True


def cmd_voices():
    d = api("/v1/voices")
    vs = d.get("voices", [])
    print("%-26s %-24s %s" % ("voice_id", "name", "labels"))
    for v in vs:
        lab = v.get("labels") or {}
        print("%-26s %-24s %s" % (v.get("voice_id", "")[:26], (v.get("name") or "")[:24],
                                  ", ".join("%s=%s" % kv for kv in sorted(lab.items()))[:70]))
    print("\n%d voices. Add more from the ElevenLabs Voice Library first "
          "(filter by Hindi or Indian accent), then re-run this." % len(vs))


def cmd_cost():
    c = cfg()
    total = 0
    for game in ("moon", "jungle-rescue"):
        n = sum(len(t) for _, t in clips_for(game))
        total += n
        print("%-15s %2d clips   %5d characters" % (game, len(clips_for(game)), n))
    print("\nOne full pass of both stories: %d characters ≈ %d credits." % (total, total))
    print("Auditioning 3 voices costs about %d more."
          % (3 * sum(len(l) for l in c["audition_lines"])))
    print("Re-running only regenerates clips whose text or voice changed.")


def cmd_audition(voice_ids):
    c = cfg()
    if not voice_ids:
        sys.exit("give me one or more voice ids: python3 tts/generate.py audition <id> <id>")
    d = os.path.join(TTS, "auditions")
    os.makedirs(d, exist_ok=True)
    text = "  ".join(c["audition_lines"])
    for v in voice_ids:
        dest = os.path.join(d, "%s.mp3" % v)
        speak(text, v, c, dest)
        print("wrote %s" % os.path.relpath(dest, ROOT))
    print("\nListen to these ON A PHONE SPEAKER, not your laptop. Then put the "
          "winner in tts/config.json as default_voice.")


def cmd_build(game, dry):
    c = cfg()
    voice = c.get("default_voice", "").strip()
    if not voice and not dry:
        sys.exit("tts/config.json has no default_voice yet - audition some first.")
    d = os.path.join(OUT, game)
    os.makedirs(d, exist_ok=True)
    made = skipped = 0
    for fn, text in clips_for(game):
        v = c.get("per_clip_voice", {}).get(fn, voice) or "dry"
        if speak(text, v, c, os.path.join(d, fn), dry):
            made += 1
            print("  %s  %s" % ("(silent)" if dry else "generated", fn))
        else:
            skipped += 1
    print("\n%s: %d generated, %d already current -> %s"
          % (game, made, skipped, os.path.relpath(d, ROOT)))
    if dry:
        print("DRY RUN - these are silent files. The pipeline ran, no credits spent.")
    else:
        print("Compare against your own recordings before installing.")


def cmd_install(game):
    src = os.path.join(OUT, game)
    dst = os.path.join(DOCS, game, "audio")
    if not os.path.isdir(src):
        sys.exit("nothing built for %s yet" % game)
    files = [f for f in sorted(os.listdir(src)) if f.endswith(".mp3")]
    if not files:
        sys.exit("no clips in %s" % src)
    back = os.path.join(dst, "_human_backup_" + time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(back)
    for f in files:
        cur = os.path.join(dst, f)
        if os.path.exists(cur):
            shutil.copy2(cur, os.path.join(back, f))
        shutil.copy2(os.path.join(src, f), cur)
    print("installed %d clips into %s" % (len(files), os.path.relpath(dst, ROOT)))
    print("your recordings are safe in %s" % os.path.relpath(back, ROOT))
    print("\nNow re-run the audio check:  python3 check_audio.py docs/%s" % game)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "voices":
        cmd_voices()
    elif cmd == "cost":
        cmd_cost()
    elif cmd == "audition":
        cmd_audition(a[1:])
    elif cmd == "build":
        if len(a) < 2:
            sys.exit("which story? moon | jungle-rescue")
        cmd_build(a[1], "--dry-run" in a)
    elif cmd == "install":
        if len(a) < 2:
            sys.exit("which story? moon | jungle-rescue")
        cmd_install(a[1])
    else:
        sys.exit(__doc__)
