#!/usr/bin/env python3
"""replace_bed.py <file.mp3> <library-id> [--volume 0.25] — swap the audio of an existing library bed.
Levels it to -16 LUFS (music standard), re-encodes, keeps the id, so no story needs editing.
    python3 docs/kit/tools/replace_bed.py ~/Downloads/song.mp3 birthday_bg --volume 0.25
"""
import sys, os, json, subprocess, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import names as nm   # its ffmpeg() also finds the imageio-ffmpeg wheel when ffmpeg is not on PATH
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.path.abspath(os.path.join(HERE, '..', 'library'))
if len(sys.argv) < 3: print(__doc__); sys.exit(2)
src = os.path.expanduser(sys.argv[1]); cid = sys.argv[2]
vol = float(sys.argv[sys.argv.index('--volume') + 1]) if '--volume' in sys.argv else None
mp = os.path.join(LIB, 'manifest.json'); lib = json.load(open(mp, encoding='utf-8'))
e = lib['clips'].get(cid) or sys.exit(f'✗ {cid} is not in the library (use library.py add)')
if not os.path.exists(src): sys.exit(f'✗ file not found: {src}')
dest = os.path.join(LIB, e['file']); tmp = dest + '.tmp.mp3'
subprocess.run([nm.ffmpeg(), '-y', '-loglevel', 'error', '-i', src, '-af', 'loudnorm=I=-16:TP=-2:LRA=11', '-ar', '44100', '-ac', '2', '-b:a', '128k', tmp], check=True)
os.replace(tmp, dest)
_, _, d = nm.measure(dest)
e['duration_seconds'] = round(d, 2); e['source'] = os.path.basename(src); e['tags'] = [t for t in e.get('tags', []) if t != 'generated']
e['description'] = f'birthday song instrumental bed, background under the birthday wish (replaced with a downloaded track; from {os.path.basename(src)})'
if vol is not None: e['volume'] = vol
import library as _lib   # same version scheme as every other library change
lib['clips'][cid] = e; _lib.save(lib)
print(f'✓ {cid}: {d:.1f}s, -16 LUFS, bed volume {e.get("volume")}')
