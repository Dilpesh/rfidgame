#!/usr/bin/env python3
"""audition.py — one sample line per character, in every candidate voice, levelled alike so they can be compared.

    ELEVENLABS_API_KEY=… python3 docs/kit/stories/gulbul-pandey/claude/audition.py
    ELEVENLABS_API_KEY=… python3 …/audition.py --list                 # print every voice in your ElevenLabs library (name + id)
    ELEVENLABS_API_KEY=… python3 …/audition.py --voice Pinky=abc123    # add a candidate from that list (repeatable)
    python3 …/audition.py --dry-run                                     # what it would spend
    …/audition.py --character DOG --voices Chintu                       # only this character, only these voices (comma-separated)
    …/audition.py --character INSPECTOR --voices Saanu --stability 0.25 --style 0.6 --tag v3   # expressive settings + v3-style tags
    …/audition.py --character MUNMUN --text "[panicked] Inspector साहब! …"                      # your own line (tags inline)

Writes claude/auditions/<CHARACTER>__<voice>.mp3 and index.html (play them side by side; phone, speaker only).
Raw API responses are cached beside their request, so re-runs cost nothing for unchanged lines.
Candidates by default: the five approved voices in library/voices.json plus Chintu (Voice Library, add it to your voices first). Everything is levelled to the
audio standard (−16 LUFS) — never compare un-levelled clips (how-we-work.md).
"""
import json, os, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(KIT, 'tools'))
import names as nm  # noqa: E402

LINES = {  # speaker → (direction, sample text) — lines from the script
    'INSPECTOR': ('boastful, funny deep voice', 'Hello! मेरा नाम है… Inspector Gulbul Pandey! Team! Doctor Munmun का box ढूँढना है!'),
    'MUNMUN':    ('worried, but lively',        'Inspector साहब! मैं Doctor Munmun बोल रही हूँ। मेरा box मिल नहीं रहा! अरे… Bedroom में!'),
    'DOG':       ('playful, cute',               'हाँ! मुझे कुछ तो पता है! पर मेरा अभी DANCE करने का बहुत मन कर रहा है!'),
    'HAVALDAR':  ('surprised',                   'ओहो! Inspector साहब… ये किसका phone आ रहा है?'),
}

LINES_V3 = {  # the same lines written with ElevenLabs v3 audio tags placed before the words they colour
    'INSPECTOR': ('booming, proud', '[booming, proud] Hello! [dramatically] मेरा नाम है… [shouts] INSPECTOR GULBUL PANDEY! [excited] Team! Doctor Munmun का box ढूँढना है!'),
    'MUNMUN':    ('panicked, breathless', '[panicked, breathless] Inspector साहब! Inspector साहब! [gasps] मेरा box… मेरा box मिल नहीं रहा! [giggles] अरे… Bedroom में!'),
    'DOG':       ('excited, bouncy', '[excited, bouncy] हाँ! हाँ! मुझे कुछ तो पता है! [laughs] पर मेरा अभी DANCE करने का बहुत मन कर रहा है!'),
    'HAVALDAR':  ('dazed', '[dazed, groaning] ऊऊऊह… [surprised] Inspector साहब… ये किसका phone आ रहा है?'),
}

def main(argv):
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    dry = '--dry-run' in argv
    voices = nm.load_json(os.path.join(KIT, 'library', 'voices.json'))
    if '--list' in argv:
        if not key: sys.exit('✗ ELEVENLABS_API_KEY is not set')
        req = urllib.request.Request('https://api.elevenlabs.io/v1/voices', headers={'xi-api-key': key})
        for v in json.load(urllib.request.urlopen(req))['voices']:
            print(f"{v['name']:<24} {v['voice_id']}  {v.get('labels', {})}")
        return 0
    cands = {s['name']: (s['voice_id'], s['voice_settings']) for s in voices['speakers'].values()}
    cands.setdefault('Chintu', ('aPE0uHZbwrQVPMm3ihPH', {'stability': 0.42, 'similarity_boost': 0.78, 'style': 0.30, 'use_speaker_boost': True}))  # Dilpesh's pick for the Dog (Voice Library)
    default_settings = {'stability': 0.45, 'similarity_boost': 0.78, 'style': 0.30, 'use_speaker_boost': True}
    for i, a in enumerate(argv):
        if a == '--voice' and i + 1 < len(argv):
            name, vid = argv[i + 1].split('=', 1); cands[name] = (vid, default_settings)
    def opt(flag):
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None
    only_chars = set((opt('--character') or '').upper().split(',')) - {''}
    global LINES
    if opt('--tag') == 'v3': LINES = LINES_V3
    if opt('--text'):
        ch = (opt('--character') or 'INSPECTOR').upper().split(',')[0]
        LINES = {ch: ('', opt('--text'))}
    stab, style = opt('--stability'), opt('--style')
    suffix = ''
    if stab or style:
        suffix = f"_s{stab or 'x'}_y{style or 'x'}"
        for k, (vid, st_) in list(cands.items()):
            st2 = dict(st_)
            if stab: st2['stability'] = float(stab)
            if style: st2['style'] = float(style)
            cands[k] = (vid, st2)
    if opt('--tag') == 'v3': suffix += '_v3tags'
    if opt('--text'): suffix += '_text'
    only_voices = set((opt('--voices') or '').split(',')) - {''}
    if only_chars: LINES_SEL = {k: v for k, v in LINES.items() if k in only_chars}
    else: LINES_SEL = LINES
    if only_voices: cands = {k: v for k, v in cands.items() if k in only_voices}
    if not LINES_SEL or not cands: sys.exit('✗ nothing matches --character / --voices (characters: ' + ', '.join(LINES) + ')')
    out = os.path.join(HERE, 'auditions'); raw_dir = os.path.join(out, 'raw'); os.makedirs(raw_dir, exist_ok=True)
    rows = []
    for speaker, (direction, text) in LINES_SEL.items():
        for vname, (vid, settings) in cands.items():
            stem = f'{speaker}__{vname}{suffix}'
            body = {'text': (f'[{direction}] {text}' if direction and not text.startswith('[') else text), 'model_id': voices.get('model_id', 'eleven_v3'), 'voice_settings': settings}
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}?output_format={voices.get('output_format', 'mp3_44100_128')}"
            raw, rec = os.path.join(raw_dir, stem + '.mp3'), os.path.join(raw_dir, stem + '.request.json')
            if os.path.exists(raw) and nm.load_json(rec) == body: status = 'cached'
            elif dry: status = 'would generate'
            else:
                if not key: sys.exit('✗ ELEVENLABS_API_KEY is not set in this shell')
                open(raw, 'wb').write(nm.request_audio(url, key, body)); nm.write_json(rec, body); status = 'generated'
            print(f'  {status:<15} {stem}')
            if status != 'would generate':
                dest = os.path.join(out, stem + '.mp3'); nm.render_levelled(raw, dest, None)
                lufs, peak, secs = nm.measure(dest); rows.append((speaker, vname, stem + '.mp3', lufs, secs))
    if rows:
        html = ['<!doctype html><meta charset="utf-8"><title>Gulbul Pandey — voice auditions</title>',
                '<style>body{font-family:sans-serif;max-width:720px;margin:2em auto}h2{margin-top:2em}div{margin:.4em 0}</style>',
                '<h1>Voice auditions</h1><p>Phone, speaker only, screen down, two metres. All clips levelled to −16 LUFS.</p>']
        for speaker in LINES_SEL:
            html.append(f'<h2>{speaker} — <i>{LINES[speaker][1]}</i></h2>')
            for s, v, f, lufs, secs in rows:
                if s == speaker: html.append(f'<div><b>{v}</b> ({secs}s, {lufs} LUFS) <audio controls preload="none" src="{f}"></audio></div>')
        open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write('\n'.join(html))
        print(f'✓ {out}/index.html — open it, or copy the mp3s to the phone')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
