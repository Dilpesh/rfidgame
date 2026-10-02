#!/usr/bin/env python3
"""sounds.py — make every sound a story still needs, with ElevenLabs text-to-sound-effects,
level it to the effects standard and add it to the shared library under the name the
script already uses. The general form of gulbul-pandey/claude/gen_sfx.py, for any story.

    python3 docs/kit/tools/sounds.py <slug> --suggest      # what's missing, and library clips that may already fit
    python3 docs/kit/tools/sounds.py <slug> --dry-run      # what would be generated, with the prompt each one gets
    python3 docs/kit/tools/sounds.py <slug>                # generate the missing ones (ELEVENLABS_API_KEY in the shell)
    python3 docs/kit/tools/sounds.py <slug> --only cap_flies_off,fireworks

How a sound gets its prompt: docs/kit/stories/<slug>/sounds.json, if it exists —
    { "cap_flies_off": { "prompt": "…", "seconds": 1.5, "loud": true, "desc": "…", "tags": "whoosh,cap" } }
— otherwise the name itself ("cap_flies_off" → "cap flies off, cartoon sound effect for a children's
story, dry, no music, no voices", 2 s). So a story with well-named sounds needs no sounds.json at all;
write one only where the name is not enough.

Levels: effects sit about 7 dB under the voice (−23 LUFS, −2 dBTP); "loud": true → −21 (a joke sound).
Levelled by measured gain, not loudnorm (unreliable on short clips).
Raw responses are cached in docs/kit/games/<slug>/audio/sfx-raw/, so a re-run spends nothing on a sound
whose prompt has not changed. A sound already in the library is skipped. Nothing here deletes anything:
to replace a sound later, generate it again with a new prompt or `library.py add` a better file.
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import compile as kc  # noqa: E402
import names as nm    # noqa: E402

API = 'https://api.elevenlabs.io/v1/sound-generation'
MUSIC_API = 'https://api.elevenlabs.io/v1/music'   # used for specs with "music": true (a bed or music loop)


def prompt_for(name, spec):
    if spec.get('prompt'): return spec['prompt']
    words = name.replace('_', ' ').replace('-', ' ')
    return f"{words}, cartoon sound effect for a children's story, dry, no music, no voices"


def level_sfx(src, dst, target, hp=80):
    """Level a sound effect to `target` LUFS with a plain gain (ebur128 measurement + volume + limiter at
    -2 dBTP, one trim pass). Not loudnorm: ffmpeg's loudnorm is unreliable on clips under ~3 s (see
    names.render_levelled), which is how a 1.5 s cap whoosh came out quiet. Returns (lufs, peak)."""
    lufs, _, _ = nm.measure(src)
    gain = (target - lufs) if lufs is not None else 0.0
    tmp = dst + '.rendering.mp3'
    for _ in range(2):
        af = f'highpass=f={hp},volume={gain:.2f}dB,alimiter=limit=0.79:attack=5:release=50:level=false'
        subprocess.run([nm.ffmpeg(), '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-af', af,
                        '-ac', '1', '-ar', '44100', '-b:a', '128k', tmp], check=True)
        l2, pk, _ = nm.measure(tmp)
        if l2 is None or abs(l2 - target) <= 0.7: break
        gain += target - l2
    os.replace(tmp, dst)
    return l2, pk


def main(argv):
    if len(argv) < 2 or argv[1].startswith('--'):
        print(__doc__); return 2
    slug = argv[1]; dry = '--dry-run' in argv; suggest = '--suggest' in argv
    only = set((nm.opt(argv, '--only') or '').split(',')) - {''}
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    src = os.path.join(KIT, 'stories', slug, 'story.txt')
    try:
        st, errors, warnings = kc.compile_story(src)
    except kc.CompileError as e:
        print(f'✗ {e}'); return 1
    specs = nm.load_json(os.path.join(KIT, 'stories', slug, 'sounds.json'), {}) or {}
    lib = nm.load_json(os.path.join(KIT, 'library', 'manifest.json'), {}) or {}
    clips = lib.get('clips', lib) if isinstance(lib, dict) else {}
    missing = {}
    for cid, c in st['clips'].items():
        if c['kind'] == 'speech' or c.get('library'): continue
        name = c.get('name') or cid
        if name in clips: continue
        missing.setdefault(name, c['kind'])
    if not missing:
        print('✓ every sound the story needs is in the library'); return 0
    if suggest:
        print(f'{len(missing)} sounds not in the library yet:')
        for name in missing:
            words = [w for w in name.replace('-', '_').split('_') if len(w) > 2]
            hits = [(k, v) for k, v in clips.items() if v.get('type', v.get('kind')) in ('sfx', 'music', 'bed', None)
                    and any(w in (k + ' ' + str(v.get('description', '')) + ' ' + ','.join(v.get('tags', []))).lower() for w in words)]
            print(f'  {name:<22} ' + (' / '.join(f'{k} ({v.get("description", "")[:40]})' for k, v in hits[:3]) if hits else '— nothing similar; will be generated'))
        print('To reuse a library clip, write its name in story.txt (sfx clap); otherwise run without --suggest.')
        return 0
    raw_dir = os.path.join(KIT, 'games', slug, 'audio', 'sfx-raw'); os.makedirs(raw_dir, exist_ok=True)
    lev_dir = os.path.join(KIT, 'games', slug, 'audio', 'sfx-in'); os.makedirs(lev_dir, exist_ok=True)
    made = 0
    for name, kind in missing.items():
        if only and name not in only: continue
        spec = specs.get(name, {})
        prompt = prompt_for(name, spec); secs = float(spec.get('seconds', 2.0)); loud = bool(spec.get('loud'))
        is_music = bool(spec.get('music'))
        if is_music:
            body = {'prompt': prompt, 'music_length_ms': int(secs * 1000), 'model_id': 'music_v1'}
        else:
            body = {'text': prompt, 'duration_seconds': secs, 'prompt_influence': float(spec.get('influence', 0.5))}
        raw = os.path.join(raw_dir, name + '.mp3'); rec = raw + '.request.json'
        if os.path.exists(raw) and os.path.getsize(raw) > 0 and nm.load_json(rec) == body:
            status = 'cached'
        elif dry:
            print(f'  would generate {name:<22} {secs:>4}s {"loud " if loud else "     "}"{prompt}"'); continue
        else:
            if not key: sys.exit('✗ ELEVENLABS_API_KEY is not set in this shell')
            req = urllib.request.Request(MUSIC_API if is_music else API, data=json.dumps(body).encode(),
                                         headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
            try:
                data = urllib.request.urlopen(req, timeout=120).read()
            except urllib.error.HTTPError as e:
                print(f'  ✗ {name}: ElevenLabs HTTP {e.code}: {e.read().decode("utf-8", "replace")[:200]}' + ('  — music is not available on this plan/key: download a loop and `library.py add <file> --id ' + name + ' --type bed --volume 0.25 --desc "…"`' if is_music else '')); continue
            open(raw, 'wb').write(data); nm.write_json(rec, body); status = 'generated'
        lev = os.path.join(lev_dir, name + '.mp3'); target = float(spec.get('lufs', -16 if is_music else (-21 if loud else -23)))
        got = level_sfx(raw, lev, target)
        desc = spec.get('desc') or name.replace('_', ' ')
        tags = spec.get('tags') or ','.join(w for w in name.split('_') if len(w) > 2)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'library.py'), 'add', lev, '--id', name, '--type', 'sfx' if kind == 'sfx' else kind] + (['--volume', str(spec['volume'])] if spec.get('volume') else []) + [
                            '--desc', f'{desc} (ElevenLabs sound-generation for {slug}; replace with a better file any time)',
                            '--tags', tags + ',generated'], capture_output=True, text=True)
        print(f'  {status:<10} {name:<22} {got[0]} LUFS / {got[1]} dBTP → library' + ('' if r.returncode == 0 else f'  ✗ {(r.stderr or r.stdout).strip()[:160]}'))
        made += r.returncode == 0
    if dry: print('(dry run — nothing generated)')
    elif made: print(f'✓ {made} sounds added to the library — now: python3 docs/kit/tools/build.py {slug}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
