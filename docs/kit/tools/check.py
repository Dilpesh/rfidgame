#!/usr/bin/env python3
"""check.py — the definition of done for a story, in one command.

    python3 docs/kit/tools/check.py <slug>            everything below
    python3 docs/kit/tools/check.py <slug> --quick    trust the manifest's measurements, don't re-measure
    python3 docs/kit/tools/check.py <slug> --play     also play it through in a headless browser (needs node + playwright)

1. Script — compile + every lint: cards in cards.json, praise and hints after
   each ask, the child's word in the last hint and the praise, the three name
   rules, the under-5 rules (library/under5-words.json), hardcoded counts.
2. Files — every clip the story uses exists; hold/freeze clips fit their hold.
3. Levels (AUDIO_STANDARD §2) — every speech clip at −16 LUFS ±1.5, true peak
   ≤ −1.5 dBTP, and all speech within 3 dB of each other (LEARNINGS 3).
4. Masking (AUDIO_STANDARD §1) — through a phone-speaker simulation, every bed
   the story plays under speech sits ≥ 20 dB below the voice in every band, at
   the volume the script plays it.
5. Optionally, a full play-through (qa/qa_play.js).

Exit code 0 only when nothing failed. Warnings are printed but do not fail.
What a machine cannot check is in tools/UNDER5_REVIEW.md — run that by hand or
by an AI before a child hears the story.
"""
import json, math, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import compile as kc  # noqa: E402

BANDS = [(80, 300), (300, 1000), (1000, 2000), (2000, 3000), (3000, 4000), (4000, 6000), (6000, 8000)]
PHONE = 'highpass=f=450:poles=2,highpass=f=450:poles=2,equalizer=f=3000:t=q:w=1.2:g=4'   # a phone loudspeaker, roughly
GAP_DB = -20.0
LUFS_TARGET, LUFS_TOL, PEAK_MAX, SPREAD_MAX = -16.0, 1.5, -1.5, 3.0


def ffmpeg():
    import shutil
    p = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if p: return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def measure(path):
    r = subprocess.run([ffmpeg(), '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    lufs = re.search(r'Integrated loudness:\s+I:\s+(-?[\d.]+) LUFS', r.stderr)
    peak = re.search(r'True peak:\s+Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    dur = re.search(r'Duration:\s+(\d+):(\d+):([\d.]+)', r.stderr)
    d = None
    if dur:
        h, m, s = dur.groups(); d = int(h) * 3600 + int(m) * 60 + float(s)
    return (float(lufs.group(1)) if lufs else None, float(peak.group(1)) if peak else None, d)


def band_rms(path, lo, hi, gain_db=0.0):
    """RMS level (dB) of one file in one band, through the phone simulation."""
    af = f'{PHONE},highpass=f={lo}:poles=2,lowpass=f={hi}:poles=2,volume={gain_db}dB,astats=measure_perchannel=none:measure_overall=RMS_level'
    r = subprocess.run([ffmpeg(), '-hide_banner', '-nostats', '-i', path, '-af', af, '-f', 'null', '-'], capture_output=True, text=True)
    m = re.findall(r'RMS level dB:\s+(-?[\d.]+|-inf)', r.stderr)
    if not m: return None
    v = m[-1]
    return -120.0 if v == '-inf' else float(v)


def main(argv):
    if len(argv) < 2 or argv[1].startswith('--'):
        print(__doc__); return 2
    slug = argv[1]; quick = '--quick' in argv; play = '--play' in argv
    fails, warns = [], []
    say = lambda s: print(s)

    # 1. script
    src = os.path.join(KIT, 'stories', slug, 'story.txt')
    game_dir = os.path.join(KIT, 'games', slug)
    try:
        durations = {}
        mp = os.path.join(game_dir, 'audio', 'manifest.json')
        manifest = json.load(open(mp, encoding='utf-8')) if os.path.exists(mp) else {}
        for cid, c in manifest.items():
            if isinstance(c, dict) and c.get('duration_seconds'): durations[cid] = c['duration_seconds']
        out, errors, warnings = kc.compile_story(src, durations=durations)
    except kc.CompileError as e:
        print(f'✗ script: {e}'); return 1
    say(f'\n1. script — {out["title"]}: {len(out["scenes"])} scenes, {len(out["clips"])} clips')
    for w in warnings: say(f'   ⚠ {w}'); warns.append(w)
    for n in out.get('_notes', []): say(f'   · {n}')
    for e in errors: say(f'   ✗ {e}'); fails.append(e)

    # 2. files
    lib = kc.load_library(); lib_dir = os.path.join(KIT, 'library')
    audio_dir = os.path.normpath(os.path.join(game_dir, out['audioDir']))
    def entry(cid):
        if cid.startswith('lib:'):
            c = lib.get(cid[4:]); return (c, lib_dir) if c else (None, None)
        c = manifest.get(cid); return (c, audio_dir) if isinstance(c, dict) else (None, None)
    speech, beds, missing = [], {}, []
    holds = []
    def walk(beats, fn):
        for b in beats:
            fn(b)
            if isinstance(b.get('beats'), list): walk(b['beats'], fn)
            if b.get('op') == 'ask':
                if b['prompt']: fn(b['prompt'])
                for h in b['hints']: fn(h)
                for a in b['afterPrompt']: fn(a)
                if b['remind']: fn(b['remind']['beat'])
    def see(b):
        cid = b.get('cue');
        if not cid: return
        c, base = entry(cid)
        if not c or not any(c.get(k) for k in ('file', 'bed_file', 'jeep_file')):
            missing.append(cid); return
        if b['op'] == 'bed' and not b.get('stop'):
            vol = b.get('volume') if isinstance(b.get('volume'), (int, float)) else c.get('volume')
            beds[cid] = (os.path.join(base, c['file']), vol)
        elif b['op'] in ('say', 'duck') or (b['op'] == 'sfx' and c.get('type') == 'speech'):
            speech.append((cid, os.path.join(base, c['file']), c))
        elif b['op'] == 'play' and c.get('type') == 'split_sfx' and c.get('bed_file'):
            beds[cid + '/bed'] = (os.path.join(base, c['bed_file']), c.get('bed_volume'))
        if b.get('hold') and c.get('duration_seconds') and c['duration_seconds'] > b['hold'] / 1000 + 0.05:
            holds.append(f'{cid} is {c["duration_seconds"]} s but the script holds only {b["hold"] / 1000} s')
    for sc in out['scenes']: walk(sc['beats'], see)
    for v in out['wrong']: walk(v, see)
    nofile = [cid for cid, p, c in speech if not os.path.exists(p)] + [k for k, (p, v) in beds.items() if not os.path.exists(p)]
    say(f'\n2. files — {len(speech)} speech clips, {len(beds)} beds, {len(missing)} not in any manifest, {len(nofile)} manifest entries without a file')
    for m in missing: say(f'   ✗ {m}: no clip'); fails.append(m)
    for m in nofile: say(f'   ✗ {m}: file missing on disk'); fails.append(m)
    for h in holds: say(f'   ✗ {h}'); fails.append(h)
    if not ffmpeg():
        say('\n   ffmpeg not found — levels and masking skipped'); quick = True

    # 3. levels
    say(f'\n3. levels — target {LUFS_TARGET} LUFS ±{LUFS_TOL}, peak ≤ {PEAK_MAX} dBTP, spread ≤ {SPREAD_MAX} dB')
    seen = set(); vals = []
    for cid, p, c in speech:
        if cid in seen or not os.path.exists(p): continue
        seen.add(cid)
        if quick or not ffmpeg():
            lufs, peak = c.get('integrated_lufs'), c.get('true_peak_dbfs')
        else:
            lufs, peak, _ = measure(p)
        if lufs is None:
            say(f'   ⚠ {cid}: could not measure'); warns.append(cid); continue
        vals.append(lufs)
        bad = []
        if abs(lufs - LUFS_TARGET) > LUFS_TOL: bad.append(f'{lufs} LUFS')
        if peak is not None and peak > PEAK_MAX: bad.append(f'peak {peak} dBTP')
        if bad: say(f'   ✗ {cid}: {", ".join(bad)}'); fails.append(cid)
    if vals:
        spread = max(vals) - min(vals)
        line = f'   {len(vals)} clips measured: {min(vals):.1f} … {max(vals):.1f} LUFS, spread {spread:.1f} dB'
        if spread > SPREAD_MAX: say(line + f'  ✗ spread over {SPREAD_MAX} dB'); fails.append('spread')
        else: say(line + '  ✓')

    # 4. masking
    if beds and not quick and ffmpeg():
        say(f'\n4. masking — bed vs voice through a phone speaker, must be ≤ {GAP_DB:+.0f} dB in every band')
        sample = [p for cid, p, c in speech if os.path.exists(p)][:12]       # a dozen speech clips is a fair average
        for lo, hi in BANDS:
            v = [band_rms(p, lo, hi) for p in sample]; v = [x for x in v if x is not None]
            vdb = 10 * math.log10(sum(10 ** (x / 10) for x in v) / len(v)) if v else None
            for key, (bp, vol) in beds.items():
                if not os.path.exists(bp): continue
                gain = 20 * math.log10(vol) if vol and vol > 0 else 0.0
                bdb = band_rms(bp, lo, hi, gain)
                if vdb is None or bdb is None: continue
                gap = bdb - vdb
                flag = '✓' if gap <= GAP_DB else '✗'
                say(f'   {flag} {lo:>5}–{hi:<5} Hz  {key:<18} bed {bdb:7.1f}  voice {vdb:7.1f}  gap {gap:+6.1f} dB')
                if gap > GAP_DB: fails.append(f'{key} {lo}-{hi}')
    elif beds:
        say('\n4. masking — skipped (--quick or no ffmpeg)')

    # 5. play
    if play:
        say('\n5. play-through')
        r = subprocess.run(['node', os.path.join(KIT, 'qa', 'qa_play.js'), slug], capture_output=True, text=True)
        say('   ' + '\n   '.join(r.stdout.strip().splitlines()[:3]))
        if r.returncode: fails.append('play-through')

    say(f'\n{"✓ PASS" if not fails else "✗ FAIL"} — {len(fails)} failed, {len(warns)} warnings. Then: listen on a phone, speaker only, from two metres; and tools/UNDER5_REVIEW.md.')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
