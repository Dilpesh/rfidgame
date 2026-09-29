#!/usr/bin/env python3
"""build.py — one command from a story script to a playable game folder.

    python3 docs/kit/tools/build.py <slug>                 # docs/kit/stories/<slug>/story.txt -> docs/kit/games/<slug>/
    python3 docs/kit/tools/build.py <slug> --out <folder>  # write to docs/kit/games/<folder>/ instead
    python3 docs/kit/tools/build.py <slug> --check         # compile + lint + missing-clip report, write nothing

Everything stays inside docs/kit/. What it does, in order:
  1. compiles docs/kit/stories/<slug>/story.txt (+ variants/*.txt) into story.json — lint runs here
  2. reads the audio manifest the story points at (docs/kit/games/<slug>/audio/manifest.json
     by default) and lists every clip the story needs that the manifest does not have yet
  3. writes docs/kit/games/<slug>/index.html (a few lines: the engine + the story) and story.json

It only ever writes index.html, story.json and a .kahani marker into the game folder;
the audio/ folder beside them is yours. It refuses a game folder it did not create.
"""
import hashlib, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))          # docs/kit/tools
KIT = os.path.abspath(os.path.join(HERE, '..'))             # docs/kit
sys.path.insert(0, HERE)
import compile as kc  # noqa: E402

TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="../../engine/kahani.css?v={css}">
</head>
<body>
<div id="kahani"></div>
<script src="../../engine/scan-guard.js?v={shared}"></script>
<script src="../../engine/reader-check.js?v={shared}"></script>
<script src="../../engine/story-intro.js?v={shared}"></script>
<script src="../../engine/card-registry.js?v={registry}"></script>
<script src="../../engine/kahani.js?v={engine}"></script>
<script>Kahani.boot({{ story: 'story.json' }});</script>
</body>
</html>
"""


def missing_clips(out, story_dir):
    """Clips the story references that the manifest at audioDir does not have."""
    audio_dir = os.path.normpath(os.path.join(story_dir, out['audioDir']))
    mpath = os.path.join(audio_dir, 'manifest.json')
    if not os.path.exists(mpath):
        return None, list(out['clips'].keys())
    manifest = json.load(open(mpath, encoding='utf-8'))
    missing = []
    for cid in out['clips']:
        if cid.startswith('lib:'):
            continue                      # the compiler already checked the library has it
        c = manifest.get(cid)
        if not c:
            missing.append(cid); continue
        if isinstance(c, dict) and not any(c.get(k) for k in ('file', 'bed_file', 'jeep_file', 'entry_file')):
            missing.append(cid)
    return mpath, missing


def refresh_registry(registry):
    """Rewrite the seed block of docs/kit/engine/card-registry.js from cards.json, the same
    way sync_cards.py does for the old games — so a card added to cards.json is known to every
    kit game (and teachable) without touching anything outside docs/kit."""
    path = os.path.join(KIT, 'engine', 'card-registry.js')
    if registry is None or not os.path.exists(path):
        return False
    src = open(path, encoding='utf-8').read()
    start, end = '/* __CARD_REGISTRY_START__ */', '/* __CARD_REGISTRY_END__ */'
    if start not in src or end not in src:
        return False
    uids = {}
    for name, c in registry['cards'].items():
        for u in c.get('uids', []):
            uids[kc.norm_uid(u)] = name
    labels = {name: c.get('label', name.title()) for name, c in registry['cards'].items()}
    width = max(len(n) for n in labels) + 1
    block = (start + '\nconst SEED_VERSION = ' + json.dumps(registry.get('seed_version', '')) + ';\n'
             + 'const DEFAULT = ' + json.dumps(dict(sorted(uids.items(), key=lambda kv: kv[1])), indent=2) + ';\n'
             + 'const LABELS = {\n' + ',\n'.join(f'  {n + ":":<{width + 1}} {json.dumps(l)}' for n, l in sorted(labels.items())) + '\n};\n' + end)
    new = src[:src.index(start)] + block + src[src.index(end) + len(end):]
    if new != src:
        open(path, 'w', encoding='utf-8').write(new)
        return True
    return False


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    slug = argv[1]
    flags = argv[2:]
    out_name = flags[flags.index('--out') + 1] if '--out' in flags else slug
    check = '--check' in flags

    src = os.path.join(KIT, 'stories', slug, 'story.txt')
    if not os.path.exists(src):
        print(f'✗ no docs/kit/stories/{slug}/story.txt'); return 1
    durations = {}
    mp = os.path.join(KIT, 'games', out_name, 'audio', 'manifest.json')
    if os.path.exists(mp):
        for cid, c in json.load(open(mp, encoding='utf-8')).items():
            if isinstance(c, dict) and c.get('duration_seconds'): durations[cid] = c['duration_seconds']
    try:
        out, errors, warnings = kc.compile_story(src, durations=durations)
    except kc.CompileError as e:
        print(f'✗ {e}'); return 1
    for w in warnings: print(f'⚠ {w}')
    for e in errors: print(f'✗ {e}')
    if errors:
        return 1
    print(f'✓ {out["title"]}: {len(out["scenes"])} scenes, {len(out["clips"])} clips, {len(out["variants"])} variants')
    if not check and refresh_registry(kc.load_registry()):
        print('✓ docs/kit/engine/card-registry.js refreshed from cards.json')

    game_dir = os.path.join(KIT, 'games', out_name)
    mpath, missing = missing_clips(out, game_dir)
    speech = [c for c in missing if out['clips'][c]['kind'] == 'speech']
    sfx = [c for c in missing if out['clips'][c]['kind'] != 'speech']
    shared = sum(1 for c in out['clips'].values() if c.get('library'))
    if shared:
        print(f'✓ {shared} clips come from the shared library')
    if mpath is None:
        print(f'⚠ no manifest at {out["audioDir"]}manifest.json — every clip still has to be made')
    if missing:
        print(f'⚠ {len(missing)} clips not in the manifest yet: {len(speech)} lines to generate, {len(sfx)} sounds to find')
        print(f'  python3 docs/kit/tools/compile.py docs/kit/stories/{slug}/story.txt --clips   # the list, with text and speaker')
    else:
        print('✓ every clip the story needs is in the manifest')

    if check:
        return 0

    marker = os.path.join(game_dir, '.kahani')
    # audio/ may already be there (it usually is); only a game we did not write is protected
    if os.path.exists(os.path.join(game_dir, 'index.html')) and not os.path.exists(marker):
        print(f'✗ docs/kit/games/{out_name}/ exists and was not built by this kit — pass --out <new-folder> or move it aside'); return 1
    os.makedirs(game_dir, exist_ok=True)
    # every engine file is loaded with a hash of its contents, so a phone never keeps an old engine after a deploy
    eng = os.path.join(KIT, 'engine')
    h = lambda *names: hashlib.md5(b''.join(open(os.path.join(eng, n), 'rb').read() for n in names)).hexdigest()[:8]
    with open(os.path.join(game_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(TEMPLATE.format(lang=out['language'], title=out['title'].replace('<', '&lt;'),
                                css=h('kahani.css'), engine=h('kahani.js'), registry=h('card-registry.js'),
                                shared=h('scan-guard.js', 'reader-check.js', 'story-intro.js')))
    with open(os.path.join(game_dir, 'story.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(marker, 'w') as f:
        f.write(f'built by docs/kit/tools/build.py from docs/kit/stories/{slug}/story.txt\n')
    # keep a copy beside the script too, so git diffs show what the engine will read,
    # and the clip list the audio producer / tts works from
    shutil.copy(os.path.join(game_dir, 'story.json'), os.path.join(KIT, 'stories', slug, 'story.json'))
    with open(os.path.join(KIT, 'stories', slug, 'clips.json'), 'w', encoding='utf-8') as f:
        json.dump([{'id': cid, **c, 'missing': cid in missing} for cid, c in out['clips'].items()], f, ensure_ascii=False, indent=1)
    print(f'✓ wrote docs/kit/games/{out_name}/index.html + story.json')
    print(f'  open docs/kit/games/{out_name}/index.html?dev on a laptop, or /kit/games/{out_name}/ on the phone')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
