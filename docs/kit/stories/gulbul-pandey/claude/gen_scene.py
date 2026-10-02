#!/usr/bin/env python3
"""gen_scene.py — generate the speech for ONE scene of Gulbul Pandey, so you listen and fix before spending on the next.

    python3 docs/kit/stories/gulbul-pandey/claude/gen_scene.py 1 --dry-run   # what scene 1 would spend
    python3 docs/kit/stories/gulbul-pandey/claude/gen_scene.py 1             # generate scene 1 (its cue ids start S01_)
    python3 docs/kit/stories/gulbul-pandey/claude/gen_scene.py list          # scenes and how many lines each still needs

Scene numbers are the S0n in the cue ids (1 = Phone call … 6 = कपड़ों का clue). Name lines ({name}) are not
made here — they come from `names.py captain`, once, for the whole story. Shared cues pinned by id
(gadbad_tag, gadbad_fix, kaun_karta) belong to the scene where they first appear.
"""
import os, sys, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(KIT, 'tools')); import compile as kc  # noqa
SLUG = 'gulbul-pandey'
st, errors, warnings = kc.compile_story(os.path.join(KIT, 'stories', SLUG, 'story.txt'))
mp = os.path.join(KIT, 'games', SLUG, 'audio', 'manifest.json')
manifest = json.load(open(mp)) if os.path.exists(mp) else {}
# scene of each cue: first scene whose beats mention it (pinned shared cues included)
scene_of = {}
def walk(beats, i):
    for b in beats:
        if b.get('cue') and b['cue'] not in scene_of: scene_of[b['cue']] = i
        for k in ('beats', 'hints', 'afterPrompt'):
            if isinstance(b.get(k), list): walk([x if not isinstance(x, dict) or 'beat' not in x else x['beat'] for x in b[k]], i)
        if isinstance(b.get('prompt'), dict): walk([b['prompt']], i)
for i, sc in enumerate(st['scenes']): walk(sc['beats'], i)
speech = {cid: c for cid, c in st['clips'].items() if c.get('kind') == 'speech' and not cid.startswith('lib:') and not c.get('nameText')}
by_scene = {}
for cid in speech: by_scene.setdefault(scene_of.get(cid, 0), []).append(cid)
arg = sys.argv[1] if len(sys.argv) > 1 else 'list'
if arg == 'list':
    for i, sc in enumerate(st['scenes']):
        ids = by_scene.get(i, []); todo = [c for c in ids if not (manifest.get(c) or {}).get('file')]
        print(f"scene {i+1}: {sc.get('title','')[:28]:<30} {len(ids):>3} lines, {len(todo):>3} still to generate")
    sys.exit(0)
n = int(arg); ids = by_scene.get(n - 1, [])
if not ids: sys.exit(f'✗ no speech lines in scene {n}')
cmd = [sys.executable, os.path.join(KIT, 'tools', 'generate.py'), SLUG, '--only', ','.join(ids)] + [a for a in sys.argv[2:] if a.startswith('--')]
print(f"scene {n}: {len(ids)} lines → generate.py --only …"); sys.exit(subprocess.call(cmd))
