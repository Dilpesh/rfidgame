#!/usr/bin/env python3
"""rekey.py — give every current clip id its OWN audio file, matching existing audio by spoken text.

    python3 docs/kit/tools/rekey.py <slug> [--dry-run] [--baseline <git-rev>]

Clip ids are numbered by position in the script, so adding or removing a line shifts every later id.
rekey.py finds, for each current speech clip, audio that already exists for the SAME TEXT (tags and
spaces ignored) and saves a copy under the clip's own file name (generated/<id>.mp3, or
names-captain/<id>.mp3 for {name} lines). Because each id owns its file, a later generate.py can never
overwrite another clip's audio (the old version of this tool re-pointed ids at old file names, and
generate.py then clobbered them).

Where audio is looked up:  (1) the current manifest, but only entries whose file is not shared with another id
and whose measured length matches the manifest (so audio that was overwritten is never trusted);
(2) with --baseline <rev> (e.g. HEAD), the manifest and audio files as committed in git — use it to
recover audio that was damaged. Lines with no matching audio are left out of the manifest, so
`generate.py` / `names.py captain` make exactly those. Entries for ids no longer in the script are
removed from the manifest (a backup, manifest.json.before-rekey, is written once and the files stay on
disk). Run it after every script edit and after sounds.py, before names.py captain / generate.py.
"""
import os, sys, json, re, copy, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(KIT, '..', '..'))
sys.path.insert(0, HERE)
import compile as kc  # noqa: E402
import names as nm    # noqa: E402

def norm(t): return re.sub(r'\[[^\]]*\]|\s+', '', t or '')

def git_show(rev, path):
    r = subprocess.run(['git', '-C', ROOT, 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def main(argv):
    if len(argv) < 2 or argv[1].startswith('--'): print(__doc__); return 2
    slug = argv[1]; dry = '--dry-run' in argv
    base = argv[argv.index('--baseline') + 1] if '--baseline' in argv else None
    try: st, errors, warnings = kc.compile_story(os.path.join(KIT, 'stories', slug, 'story.txt'))
    except kc.CompileError as e: print(f'✗ {e}'); return 1
    adir = os.path.join(KIT, 'games', slug, 'audio'); mp = os.path.join(adir, 'manifest.json')
    if not os.path.exists(mp): print('nothing to rekey (no manifest yet)'); return 0
    m = json.load(open(mp, encoding='utf-8'))
    pool = {}   # normalised text -> (entry, bytes, where)
    claims = {}
    for k, v in m.items():
        if isinstance(v, dict) and v.get('file'): claims.setdefault(v['file'], []).append(k)
    for k, v in m.items():                                   # (1) trusted current audio
        if not (isinstance(v, dict) and v.get('file') and v.get('spoken_text')): continue
        p = os.path.join(adir, v['file'])
        own = os.path.splitext(os.path.basename(v['file']))[0] == k
        if not os.path.exists(p) or not (own or len(claims[v['file']]) == 1): continue   # shared file = one was overwritten
        d = nm.measure(p)[2]
        if d and v.get('duration_seconds') and abs(d - v['duration_seconds']) < .25:
            pool.setdefault(norm(v['spoken_text']), (v, open(p, 'rb').read(), f'disk:{k}'))
    if base:                                                 # (2) committed audio
        rel = os.path.relpath(adir, ROOT)
        raw = git_show(base, f'{rel}/manifest.json')
        bm = json.loads(raw) if raw else {}
        for k, v in bm.items():
            if not (isinstance(v, dict) and v.get('file') and v.get('spoken_text')): continue
            b = git_show(base, f'{rel}/{v["file"]}')
            if b: pool.setdefault(norm(v['spoken_text']), (v, b, f'{base}:{k}'))
    new_m = {k: v for k, v in m.items() if not (isinstance(v, dict) and k.startswith('BOBO_') or (isinstance(v, dict) and v.get('type') == 'speech'))}
    writes, todo, kept = [], [], 0
    for cid, c in st['clips'].items():
        if c['kind'] != 'speech' or cid.startswith('lib:'): continue
        hit = pool.get(norm(c['text']))
        if not hit: todo.append((cid, c['text'][:60])); continue
        e = copy.deepcopy(hit[0]); sub = 'names-captain' if c.get('nameText') else 'generated'
        e['file'] = f'{sub}/{cid}.mp3'; e['remapped_from'] = hit[2]
        writes.append((cid, e, hit[1])); kept += 1
    for cid, t in todo: print(f'  NEW     {cid}  {t}')
    print(f'{kept} clips matched to existing audio · {len(todo)} lines genuinely new (generate.py / names.py captain will make them)')
    if dry: return 0
    bak = mp + '.before-rekey'
    if not os.path.exists(bak): shutil.copy(mp, bak)
    for cid, e, data in writes:                              # all bytes were read above; now write
        dest = os.path.join(adir, e['file']); os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'wb').write(data)
        d = nm.measure(dest)[2]
        if d: e['duration_seconds'] = d
        new_m[cid] = e
    json.dump(new_m, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('✓ manifest rebuilt — every clip owns its own file'); return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
