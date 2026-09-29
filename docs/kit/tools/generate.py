#!/usr/bin/env python3
"""generate.py — make the clips a story still needs, with ElevenLabs.

    python3 docs/kit/tools/generate.py <slug> [--dry-run] [--only JR_143b,JR_200]

For every speech line in docs/kit/stories/<slug>/story.txt that has no clip in
docs/kit/games/<slug>/audio/manifest.json: send the text with the line's direction
([tender, inviting] → the v3 audio tag) to the speaker's approved voice
(library/voices.json), level the result to the audio standard (−16 LUFS, −2 dBTP),
measure it, and add it to the manifest under audio/generated/<cue>.mp3.

Lines pinned to an existing clip cost nothing. Library lines (`@lib:…`) are not
made here: `library.py add` for a sound, `names.py captain` for a name line.
Sounds (sfx / bed / music) are listed but not generated — find or make those
and `library.py add` them. Raw responses are cached beside their request, so a
re-run spends nothing on a line whose text has not changed. ELEVENLABS_API_KEY
must be in the environment; nothing here stores it.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import compile as kc  # noqa: E402
import names as nm    # noqa: E402  (synth, render_levelled, measure)


def main(argv):
    if len(argv) < 2 or argv[1].startswith('--'):
        print(__doc__); return 2
    slug = argv[1]; dry = '--dry-run' in argv
    only = set((nm.opt(argv, '--only') or '').split(',')) - {''}
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    src = os.path.join(KIT, 'stories', slug, 'story.txt')
    try:
        st, errors, warnings = kc.compile_story(src)
    except kc.CompileError as e:
        print(f'✗ {e}'); return 1
    audio_dir = os.path.normpath(os.path.join(KIT, 'games', slug, st.get('audioDir', 'audio/')))
    mp = os.path.join(audio_dir, 'manifest.json')
    manifest = nm.load_json(mp, {'_build': {'story': st['title']}})
    todo, sounds = [], []
    for cid, c in st['clips'].items():
        if cid.startswith('lib:') or (only and cid not in only):
            continue
        e = manifest.get(cid)
        if e and any(e.get(k) for k in ('file', 'bed_file', 'jeep_file')):
            continue
        (todo if c['kind'] == 'speech' else sounds).append((cid, c))
    if not todo and not sounds:
        print('✓ every clip the story needs exists'); return 0
    counts = {}
    for cid, c in todo:
        if c.get('nameText'):
            print(f'  name line       {cid:<14} → names.py captain'); continue
        status, made = nm.synth(os.path.join(audio_dir, 'raw'), cid, c['speaker'], c['text'], c.get('emotion', ''), key, dry)
        counts[status] = counts.get(status, 0) + 1
        print(f'  {status:<15} {cid:<14} {c["speaker"]:<9} {c["text"]}')
        if not made:
            continue
        entry, raw, flt = made
        dest_rel = f'generated/{cid}.mp3'; dest = os.path.join(audio_dir, dest_rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        nm.render_levelled(raw, dest, flt)
        lufs, peak, secs = nm.measure(dest)
        entry.update({'file': dest_rel, 'duration_seconds': secs, 'integrated_lufs': lufs, 'true_peak_dbfs': peak})
        if lufs is not None and (abs(lufs + 16) > 1.5 or peak > -1.5):
            print(f'    !! {cid} measures {lufs} LUFS / {peak} dBTP — outside the standard')
        manifest[cid] = entry
    if not dry and counts:
        nm.write_json(mp, manifest)
    for cid, c in sounds:
        print(f'  sound to find   {cid:<14} {c["kind"]:<6} {c.get("name") or ""}  → library.py find …, then library.py add')
    print(' · '.join(f'{v} {k}' for k, v in counts.items()) or '')
    if not dry and counts:
        print(f'✓ manifest updated — now: python3 docs/kit/tools/build.py {slug}; python3 check_audio.py docs/kit/games/{slug}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
