#!/usr/bin/env python3
"""library.py — the shared sound and voice library every story can use.

docs/kit/library/manifest.json lists every shared clip with a description you can
search, so before anyone opens ElevenLabs the question "do we already have a …?"
has an answer. A story uses a library clip by name — `sfx ting`, `bed jungle_day`,
`COCO @lib:great_job: Great job!` — and the engine plays it from docs/kit/library/.

    python3 docs/kit/tools/library.py list
    python3 docs/kit/tools/library.py find soft chime correct
    python3 docs/kit/tools/library.py uses                          # which stories use which clip
    python3 docs/kit/tools/library.py add path/to.mp3 --id ting --type sfx \\
        --desc "two-note glass chime, the 'correct card' sound" --tags chime,correct,bright
    python3 docs/kit/tools/library.py promote jungle-rescue-english JR_014 --id ting \\
        --desc "…" --tags chime,correct                             # lift a clip out of a game into the library

`add` copies the file in (never moves it), `promote` copies a clip out of a game's
audio folder and keeps its measured loudness, duration, voice and text. Both bump
the library version so phones re-download only what changed. Nothing is ever
deleted here; retire a clip by adding "retired" to its tags.
"""
import json, os, re, shutil, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..'))
LIB = os.path.join(KIT, 'library')
MANIFEST = os.path.join(LIB, 'manifest.json')
FOLDER = {'sfx': 'sfx', 'voice': 'voice', 'speech': 'voice', 'music': 'music', 'bed': 'music'}


def load():
    if not os.path.exists(MANIFEST):
        return {'version': 'lib-0', 'clips': {}}
    return json.load(open(MANIFEST, encoding='utf-8'))


def save(lib):
    today = datetime.date.today().isoformat()
    m = re.match(r'^lib-(\d{4}-\d{2}-\d{2})([a-z])$', lib.get('version', ''))
    if m and m.group(1) == today:
        lib['version'] = f'lib-{today}{chr(ord(m.group(2)) + 1)}'
    else:
        lib['version'] = f'lib-{today}a'
    os.makedirs(LIB, exist_ok=True)
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(lib, f, ensure_ascii=False, indent=1)
    print(f'✓ library {lib["version"]}: {len(lib["clips"])} clips')


def duration_of(path):
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                             capture_output=True, text=True, check=True).stdout.strip()
        return round(float(out), 3)
    except Exception:
        pass
    try:                                   # no ffprobe: ffmpeg (or the imageio wheel) can tell us too
        import shutil, re as _re
        ff = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
        if not ff:
            import imageio_ffmpeg; ff = imageio_ffmpeg.get_ffmpeg_exe()
        r = subprocess.run([ff, '-hide_banner', '-i', path, '-f', 'null', '-'], capture_output=True, text=True)
        m = _re.search(r'Duration:\s+(\d+):(\d+):([\d.]+)', r.stderr)
        if m: h, mi, s = m.groups(); return round(int(h) * 3600 + int(mi) * 60 + float(s), 3)
    except Exception:
        return None
    return None


def check_id(lib, cid):
    if not re.match(r'^[a-z][a-z0-9_]*$', cid):
        sys.exit(f'✗ id "{cid}": lowercase letters, digits and _ only (it is typed into scripts)')
    if cid in lib['clips']:
        sys.exit(f'✗ {cid} is already in the library: {lib["clips"][cid]["description"]}')


def opt(args, name, default=None, required=False):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args):
            return args[i + 1]
    if required:
        sys.exit(f'✗ {name} is required')
    return default


def cmd_list(lib, args):
    for cid, c in sorted(lib['clips'].items(), key=lambda kv: (kv[1].get('type', ''), kv[0])):
        extra = f' · {c["spoken_text"]}' if c.get('spoken_text') else ''
        print(f'{cid:<22} {c.get("type", ""):<6} {c.get("duration_seconds", "?"):>6}s  {c["description"]}{extra}')
        if c.get('tags'): print(f'{"":<22} tags: {", ".join(c["tags"])}')


def cmd_find(lib, args):
    words = [w.lower() for w in args if not w.startswith('--')]
    if not words:
        sys.exit('✗ find needs some words: python3 library.py find soft chime')
    hits = []
    for cid, c in lib['clips'].items():
        hay = ' '.join([cid.replace('_', ' '), c.get('description', ''), ' '.join(c.get('tags', [])), c.get('spoken_text', ''), c.get('type', '')]).lower()
        score = sum(2 if w in c.get('tags', []) else 1 for w in words if w in hay)
        if score: hits.append((score, cid, c))
    if not hits:
        print('nothing in the library matches — this one has to be made'); return
    for score, cid, c in sorted(hits, key=lambda h: -h[0]):
        extra = f' · "{c["spoken_text"]}"' if c.get('spoken_text') else ''
        print(f'{cid:<22} {c.get("type", ""):<6} {c.get("duration_seconds", "?"):>6}s  {c["description"]}{extra}')


def cmd_uses(lib, args):
    uses = {cid: [] for cid in lib['clips']}
    stories = os.path.join(KIT, 'stories')
    for slug in sorted(os.listdir(stories)):
        p = os.path.join(stories, slug, 'story.json')
        if not os.path.exists(p): continue
        for cue in json.load(open(p, encoding='utf-8')).get('clips', {}):
            if cue.startswith('lib:') and cue[4:] in uses: uses[cue[4:]].append(slug)
        tap = json.load(open(p, encoding='utf-8')).get('tapSound')
        if tap and tap.startswith('lib:') and tap[4:] in uses and slug not in uses[tap[4:]]: uses[tap[4:]].append(slug)
    for cid, slugs in sorted(uses.items()):
        print(f'{cid:<22} {", ".join(slugs) if slugs else "—"}')
    print('(stories are counted from their last build)')


def entry_from(args, kind, src_meta=None):
    e = dict(src_meta or {})
    e.pop('file', None); e.pop('review_status', None); e.pop('source_file', None); e.pop('_lib', None)
    e['type'] = kind
    e['description'] = opt(args, '--desc', required=True)
    tags = opt(args, '--tags', '')
    e['tags'] = [t.strip() for t in tags.split(',') if t.strip()]
    if opt(args, '--text'): e['spoken_text'] = opt(args, '--text')
    if opt(args, '--voice'): e['voice'] = opt(args, '--voice')
    if opt(args, '--volume'): e['volume'] = float(opt(args, '--volume'))
    if kind in ('bed', 'music') and '--loop' in args: e['loop'] = True
    if kind == 'bed': e['bed'] = True; e['loop'] = True
    e['added'] = datetime.date.today().isoformat()
    return e


def cmd_add(lib, args):
    src = args[0] if args and not args[0].startswith('--') else sys.exit('✗ add needs a file')
    cid = opt(args, '--id', required=True); kind = opt(args, '--type', 'sfx')
    check_id(lib, cid)
    if kind not in FOLDER: sys.exit(f'✗ --type must be one of {", ".join(FOLDER)}')
    e = entry_from(args, kind)
    dest_rel = f'{FOLDER[kind]}/{cid}.mp3'
    os.makedirs(os.path.join(LIB, FOLDER[kind]), exist_ok=True)
    dest = os.path.join(LIB, dest_rel)
    if os.path.abspath(src) != os.path.abspath(dest):
        shutil.copy(src, dest)
    e['file'] = dest_rel; e['source'] = os.path.relpath(src, KIT) if os.path.exists(src) else src
    d = duration_of(os.path.join(LIB, dest_rel))
    if d: e['duration_seconds'] = d
    lib['clips'][cid] = e; save(lib)
    print(f'  {cid} ← {src}')


def cmd_promote(lib, args):
    if len(args) < 2: sys.exit('✗ promote <slug> <cue> --id <id> --desc "…"')
    slug, cue = args[0], args[1]
    cid = opt(args, '--id', required=True)
    check_id(lib, cid)
    sj = os.path.join(KIT, 'stories', slug, 'story.json')
    story = json.load(open(sj, encoding='utf-8')) if os.path.exists(sj) else {}
    audio_dir = os.path.normpath(os.path.join(KIT, 'games', slug, story.get('audioDir', 'audio/')))
    manifest = json.load(open(os.path.join(audio_dir, 'manifest.json'), encoding='utf-8'))
    src_meta = dict(manifest.get(cue) or {})
    part = opt(args, '--part')                      # e.g. --part jeep_file for a split cue
    if part:
        if not src_meta.get(part): sys.exit(f'✗ {cue} has no {part}')
        src_meta = {'file': src_meta[part], 'type': 'sfx', 'duration_seconds': src_meta.get(part.replace('_file', '_duration_seconds'))}
    if not src_meta or not src_meta.get('file'):
        sys.exit(f'✗ {cue} has no file in {slug}\'s manifest')
    kind = opt(args, '--type') or ('bed' if src_meta.get('bed') else {'speech': 'voice'}.get(src_meta.get('type'), src_meta.get('type', 'sfx')))
    if kind not in FOLDER: kind = 'sfx'
    e = entry_from(args, kind, src_meta)
    dest_rel = f'{FOLDER[kind]}/{cid}.mp3'
    os.makedirs(os.path.join(LIB, FOLDER[kind]), exist_ok=True)
    shutil.copy(os.path.join(audio_dir, src_meta['file']), os.path.join(LIB, dest_rel))
    e['file'] = dest_rel; e['source'] = f'{slug}:{cue}'
    if 'duration_seconds' not in e:
        d = duration_of(os.path.join(LIB, dest_rel))
        if d: e['duration_seconds'] = d
    lib['clips'][cid] = e; save(lib)
    print(f'  {cid} ← {slug} {cue} ({src_meta["file"]})')


def main(argv):
    if len(argv) < 2 or argv[1] not in ('list', 'find', 'uses', 'add', 'promote'):
        print(__doc__); return 2
    lib = load()
    {'list': cmd_list, 'find': cmd_find, 'uses': cmd_uses, 'add': cmd_add, 'promote': cmd_promote}[argv[1]](lib, argv[2:])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
