#!/usr/bin/env python3
"""audition_laugh.py — three candidates for a laugh right after "…मेरी cap उड़ गई! Woooosh!", levelled identically, to play
on the phone (speaker only, screen down, two metres) before anything goes into the story or the library.

    python3 docs/kit/stories/bobo-birthday/claude/audition_laugh.py --dry-run     # show the three prompts
    python3 docs/kit/stories/bobo-birthday/claude/audition_laugh.py               # ELEVENLABS_API_KEY in the shell

Writes claude/ab/laugh_A/B/C.mp3 (the sound alone) and laugh_A/B/C_in_story.mp3 (cap sound → Coco's
line → the laugh, as the game plays it) + ab/laugh.html — nothing is
added to the library or the story. All three are levelled to the same −23 LUFS (the effects standard) so
the louder one does not simply win. Raw takes are cached in claude/ab/raw/, so a re-run spends nothing;
`--again A` makes a fresh take of one candidate (it needs a changed prompt or --again to re-spend).
Tell me which letter; it goes into the library as cap_laugh and the story plays it after the line.
"""
import os, sys, json, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(KIT, 'tools'))
import names as nm      # noqa: E402
import sounds as sd     # noqa: E402

TARGET = -23
CANDIDATES = {
 'A': ('a group of small children giggling and laughing happily together, short burst of genuine kids laughter, starts immediately with no silence, dry, no music', 'kids giggling together'),
 'B': ('a cheeky cartoon monkey chuckling, quick playful hee-hee-hee laugh, comedic, starts immediately with no silence, dry, no music, no words', 'cartoon monkey hee-hee'),
 'C': ('a short burst of a small happy audience laughing, children and parents, warm living-room laughter, starts immediately with no silence, dry, no music', 'small audience laugh'),
}
SECS = 2.0
CAP = os.path.join(KIT, 'library', 'sfx', 'cap_flies_off_2.mp3')
LINE = os.path.join(KIT, 'games', 'bobo-birthday', 'audio', 'generated', 'BOBO_BIRTHDAY_S03_023_COCO.mp3')

def in_story(laugh, out):
    """cap sound → Coco's joke line → 150 ms → the laugh, each at the level the game plays it."""
    import subprocess
    subprocess.run([nm.ffmpeg(), '-loglevel', 'error', '-y', '-i', CAP, '-i', LINE, '-i', laugh, '-filter_complex',
                    '[0:a]aresample=44100,aformat=channel_layouts=mono[a];[1:a]aresample=44100,aformat=channel_layouts=mono[b];'
                    '[2:a]aresample=44100,aformat=channel_layouts=mono,adelay=150[c];[a][b][c]concat=n=3:v=0:a=1[o]',
                    '-map', '[o]', '-b:a', '128k', out], check=True)


def main(argv):
    dry = '--dry-run' in argv
    again = set((argv[argv.index('--again') + 1] if '--again' in argv else '').upper().split(',')) - {''}
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    ab = os.path.join(HERE, 'ab'); raw_dir = os.path.join(ab, 'raw'); os.makedirs(raw_dir, exist_ok=True)
    rows = []
    for letter, (prompt, label) in CANDIDATES.items():
        body = {'text': prompt, 'duration_seconds': SECS, 'prompt_influence': 0.6}
        raw = os.path.join(raw_dir, f'laugh_{letter}.mp3'); rec = raw + '.request.json'
        cached = os.path.exists(raw) and os.path.getsize(raw) > 0 and nm.load_json(rec) == body and letter not in again
        if dry:
            print(f'  {letter}  {label:<24} {"(cached)" if cached else "would generate"}  "{prompt[:70]}…"'); continue
        if not cached:
            if not key: sys.exit('✗ ELEVENLABS_API_KEY is not set in this shell')
            req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(),
                                         headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
            try: data = urllib.request.urlopen(req, timeout=120).read()
            except urllib.error.HTTPError as e:
                print(f'  ✗ {letter}: ElevenLabs HTTP {e.code}: {e.read().decode("utf-8", "replace")[:200]}'); continue
            open(raw, 'wb').write(data); nm.write_json(rec, body)
        out = os.path.join(ab, f'laugh_{letter}.mp3')
        lufs, peak = sd.level_sfx(raw, out, TARGET)
        _, _, secs = nm.measure(out)
        rows.append((letter, label, lufs, peak, secs))
        print(f'  {letter}  {label:<24} {secs}s  {lufs} LUFS / {peak} dBTP  → ab/laugh_{letter}.mp3')
        in_story(out, os.path.join(ab, f'laugh_{letter}_in_story.mp3'))
    if dry or not rows: return 0
    html = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Laugh audition</title>',
            '<body style="font-family:system-ui;max-width:30em;margin:1em auto;padding:0 1em"><h2>Bobo — laugh after the cap flies off</h2>',
            '<p>Phone, speaker only, two metres. All three at the same level. The second player is the moment as the game plays it.</p>']
    for letter, label, lufs, peak, secs in rows:
        html.append(f'<p><b>{letter}</b> — {label} ({secs}s, {lufs} LUFS)<br><audio controls src="laugh_{letter}.mp3"></audio><br>in the story: <audio controls src="laugh_{letter}_in_story.mp3"></audio></p>')
    open(os.path.join(ab, 'laugh.html'), 'w', encoding='utf-8').write('\n'.join(html))
    print('✓ now play the three on your phone, then tell me A, B or C (ab/laugh.html plays them)')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
