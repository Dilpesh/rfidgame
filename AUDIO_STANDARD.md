# Kahani Cards — Audio Standard

**Read this before producing audio for any new story.** It is the accumulated
set of rules that took several rounds of debugging to work out. Every rule
here exists because something actually went wrong.

Portable by design: paste this whole file into Claude, ChatGPT or Gemini at
the start of any session where you are making story audio.

---

## 0. The one-line summary

Kids listen on a **phone speaker, laid face-down, at arm's length, in a room
with other noise.** That device — not your laptop — is the target. Master
everything for it and verify against it.

---

## 1. The rule that matters most: masking is spectral, not level

A background bed can be far quieter than the narration *overall* and still
bury it, if its energy sits in the bands the narration doesn't occupy — and
those bands are the ones small speakers reproduce best.

**Phone speakers produce almost nothing below ~450 Hz.** Hindi narration
lives at 300–1000 Hz. Crickets, birds, shakers, hi-hats and chimes live at
3–8 kHz. So on a phone the voice loses its whole home band and the bed loses
nothing.

Real numbers from the moon story:

| | share of energy above 3 kHz |
|---|---|
| Night-jungle crickets bed | 14% |
| Hindi narration | 2% |

Which produced this, measured through a phone-speaker simulation:

| band | bed vs voice, before | after fixing |
|---|---|---|
| 1000–2000 Hz | −18.9 dB | −30.7 dB |
| 2000–3000 Hz | −11.2 dB | −28.6 dB |
| 4000–6000 Hz | −9.7 dB | −32.2 dB |
| 6000–8000 Hz | **+4.2 dB (bed LOUDER)** | −30.8 dB |

**Never diagnose "too loud" by turning the volume down.** Lowering a
high-frequency bed moves it down in every band equally; it never moves it out
of the band where speech is absent. Measure the bands.

### Acceptance criterion

> Through the phone-speaker simulation, with the bed at its ducked volume,
> the bed must sit **at least 20 dB below the narration in every band** from
> 80 Hz to 8 kHz. Target 25–30 dB.

---

## 2. Processing chains

### Ambience / background bed

```
ffmpeg -i bed_raw.mp3 \
  -af "highshelf=f=1500:g=-17,lowpass=f=5500,highpass=f=90" \
  -c:a libmp3lame -b:a 128k -ar 44100 bed.mp3
```

Tune `g` and the lowpass until the acceptance criterion in §1 passes. Beds
that are already low-mid (daytime jungle, wind, low drone) may need little
or nothing — measure first, don't cut reflexively.

Prefer beds without crickets, cicadas, shakers, bells, chimes or tambourine.

### Narration (every `vo_*.mp3`)

```
ffmpeg -i vo_raw.mp3 -af "\
highpass=f=110,\
equalizer=f=1500:t=q:w=1.0:g=2.5,\
equalizer=f=2800:t=q:w=0.9:g=4.5,\
acompressor=threshold=-20dB:ratio=2.5:attack=8:release=180:makeup=2,\
loudnorm=I=-16:TP=-1.5:LRA=11,\
alimiter=limit=0.95" \
  -c:a libmp3lame -b:a 128k -ar 44100 vo.mp3
```

The two `equalizer` bells are the presence lift. They put energy at 1.5 and
2.8 kHz — precisely where a phone speaker is efficient — without changing
the 300–1000 Hz body, so the clip sounds the same on a laptop.

### Targets to hit

| property | target | why |
|---|---|---|
| Integrated loudness | −16 LUFS | consistent line to line |
| True peak | ≤ −1.4 dBFS | no clipping after MP3 encode |
| Spread across all clips | within ~3 dB | no line makes kids reach for volume |
| Sample rate / bitrate | 44.1 kHz / 128 kbps mono | small enough for GitHub Pages |
| Duration after processing | **must equal duration before** | a change means a filter resampled or trimmed |

### Character voices

Narrator (Coco) is pitched up from a 34-year-old male voice. Animals are
pitched further so they read as animals, not as a man doing a voice.
`rubberband` with formant preservation, not naive speed change.

---

## 3. Per-story checklist

Run through this before the kids ever hear it.

- [ ] One-take recording split on silence, then each segment mapped to its
      script line and **verified by ASR** — never by eye or by order alone.
      (sherpa-onnx Whisper small works for Hindi.)
- [ ] Denoised (`arnndn` / RNNoise) — every clip at 35+ dB SNR.
- [ ] Narration chain from §2 applied to all `vo_*.mp3`.
- [ ] Bed chain from §2 applied, then §1 acceptance criterion **measured and
      passing** (≥20 dB gap in every band, phone simulation).
- [ ] Ducking set: `AMB_DUCK ≈ 0.12` while speaking, `AMB_BASE ≈ 0.38`
      between scenes. These are correct only once the bed is EQ'd — they
      cannot rescue an un-EQ'd bed.
- [ ] SFX that play *under* narration (`under:` beats) checked against the
      same criterion — they are beds too.
- [ ] SFX that play *between* lines may be full-range and bright; that is
      where sparkle belongs.
- [ ] No recording artefacts left in: false starts, "scaan… scan", page
      turns, breaths at the head of a clip.
- [ ] Durations unchanged vs. the pre-processed files.
- [ ] Every `*.mp3` referenced in `index.html` exists in `audio/`.
- [ ] JS syntax check on the inline `<script>` passes.
- [ ] **Listen on an actual phone, speaker only, screen down, from 2 metres.**
      Nothing replaces this. The laptop will lie to you.

---

## 4. The verification script

`check_audio.py` lives in the repo root. Run it on any story folder:

```
python3 check_audio.py docs/moon
python3 check_audio.py docs/<new-story>
```

It exits non-zero on failure, so it works as a pre-commit gate.

A music track that plays **on its own**, with no narration over it (the
banana story's 30-second dance break), is exempt — it is not a bed. Only
audio that runs underneath speech is measured. Declare a real bed as
`const AMBIENCE = "..."` in `index.html` and the script finds it;
otherwise pass the file as a second argument.

Full source, so you can paste it into any tool:

```python
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
```

---

## 5. Mistakes already made — don't repeat them

| what happened | the lesson |
|---|---|
| Renamed beat field to `vo` but `say()` still read `item.audio` → every line fell back to robotic TTS | Test against the **real** function. A test that stubs the thing under test passes while the game is broken. |
| Spent a round lowering `AMB_BASE`/`AMB_DUCK` on a bed that was too *bright*, not too loud | Measure bands before changing levels. |
| "Fine on laptop, unintelligible on phone" | The laptop is not the target device and will not reveal this class of bug. |
| A file transfer reported success but the bytes on disk were unchanged | Verify writes afterwards — `md5`, `grep`, byte count. |
| A blanket find-and-replace hit a `let` declaration and broke the page | Replace at specific call sites, never blanket. |

---

## 6. File layout for a new story

```
docs/<story-slug>/
  index.html          the game (self-contained except audio/)
  cards.html          printable card labels, CR80 54 x 85.6 mm, portrait
  audio/
    vo_*.mp3          narration, processed per section 2
    sfx_*.mp3         effects
    <bed>.mp3         ambience, EQ'd and measured per section 1
    _original_backup/ pre-processing originals (gitignored)
```

Then add a tile to the `GAMES` array in `docs/index.html`. Link to
`<story-slug>/index.html`, **not** `<story-slug>/` — a bare folder link shows
a directory listing on `file://`.
