#!/usr/bin/env python3
"""relevel.py — bring clips that miss the standard to −16 LUFS / −2 dBTP, without touching the original.

    python3 docs/kit/tools/relevel.py <slug>                 every speech clip the story uses that is off standard
    python3 docs/kit/tools/relevel.py <slug> JR_036 JR_050   only these
    python3 docs/kit/tools/relevel.py library                the shared library's speech clips
    python3 docs/kit/tools/relevel.py library hint_music_1

A levelled copy is written to audio/levelled/<cue>.mp3 (or library/levelled/<id>.mp3);
the manifest entry points at the copy and records the original under `source_file`
(and `levelled_from`), so the recording itself is never modified. Levelling is the
same measured-gain method every generator uses (tools/names.py: render_levelled).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import names as nm    # noqa: E402
import compile as kc  # noqa: E402

TOL, PEAK_MAX = 1.5, -1.5


def off_standard(lufs, peak):
    return lufs is None or abs(lufs + 16.0) > TOL or (peak is not None and peak > PEAK_MAX)


def relevel_entry(base, manifest, cid, out_sub, force):
    c = manifest.get(cid)
    if not isinstance(c, dict) or not c.get('file') or c.get('type') not in ('speech', 'voice'):   # the library says 'voice'
        return None
    src = os.path.join(base, c['file'])
    if not os.path.exists(src): return f'{cid}: file missing'
    lufs, peak, _ = nm.measure(src)
    if not force and not off_standard(lufs, peak):
        return None
    dest_rel = f'{out_sub}/{cid}.mp3'; dest = os.path.join(base, dest_rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    nm.render_levelled(src, dest, None)
    l2, p2, d2 = nm.measure(dest)
    c.setdefault('levelled_from', c['file']); c.setdefault('source_file', c['file'])
    c.update({'file': dest_rel, 'integrated_lufs': l2, 'true_peak_dbfs': p2, 'levelled': 'measured gain, tools/relevel.py'})
    if d2: c['duration_seconds'] = d2
    return f'{cid}: {lufs} → {l2} LUFS, peak {p2} dBTP'


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    target, only, force = argv[1], [a for a in argv[2:] if not a.startswith('--')], '--force' in argv
    if target == 'library':
        base = os.path.join(KIT, 'library'); mp = os.path.join(base, 'manifest.json')
        lib = nm.load_json(mp); manifest = lib['clips']
        ids = only or [k for k, c in manifest.items() if c.get('type') in ('speech', 'voice')]
        done = 0
        for cid in ids:
            r = relevel_entry(base, manifest, cid, 'levelled', force)
            if r: print('  ' + r); done += 1
        if done:
            lib['version'] = nm.bump(lib.get('version', '')); nm.write_json(mp, lib)
        print(f'✓ library: {done} clips re-levelled' if done else '✓ library: every speech clip is on standard')
        return 0
    slug = target
    st, errors, warnings = kc.compile_story(os.path.join(KIT, 'stories', slug, 'story.txt'))
    base = os.path.normpath(os.path.join(KIT, 'games', slug, st.get('audioDir', 'audio/')))
    mp = os.path.join(base, 'manifest.json'); manifest = nm.load_json(mp)
    ids = only or [cid for cid in st['clips'] if not cid.startswith('lib:') and isinstance(manifest.get(cid), dict) and manifest[cid].get('type') == 'speech']
    done = 0
    for cid in ids:
        r = relevel_entry(base, manifest, cid, 'levelled', force)
        if r: print('  ' + r); done += 1
    if done: nm.write_json(mp, manifest)
    print(f'✓ {slug}: {done} clips re-levelled — now: python3 docs/kit/tools/build.py {slug}' if done else f'✓ {slug}: every speech clip is on standard')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
