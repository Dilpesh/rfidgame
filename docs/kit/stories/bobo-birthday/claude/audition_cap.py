#!/usr/bin/env python3
"""audition_cap.py — three candidates for the Bobo "cap flies off" sound, levelled identically, to play
on the phone (speaker only, screen down, two metres) before anything goes into the story or the library.

    python3 docs/kit/stories/bobo-birthday/claude/audition_cap.py --dry-run     # show the three prompts
    python3 docs/kit/stories/bobo-birthday/claude/audition_cap.py               # ELEVENLABS_API_KEY in the shell

Writes claude/ab/cap_A.mp3, cap_B.mp3, cap_C.mp3 (+ ab/index.html to play them side by side) — nothing is
added to the library or the story. All three are levelled to the same −21 LUFS (the joke sound's target) so
the louder one does not simply win. Raw takes are cached in claude/ab/raw/, so a re-run spends nothing;
`--again A` makes a fresh take of one candidate (it needs a changed prompt or --again to re-spend).
Tell me which letter; it goes into the library as cap_flies_off_2 (the old clip stays) and the story switches.
"""
import os, sys, json, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(KIT, 'tools'))
import names as nm      # noqa: E402
import sounds as sd     # noqa: E402

TARGET = -21
CANDIDATES = {
 'A': ('cartoon slide whistle rising fast then a cheeky pop, a hat popping off a head, comedic, starts immediately with no silence, dry, no music, no voices', 'slide whistle up + pop'),
 'B': ('loud cartoon boing, then a fast spinning whirr, then a soft fluffy flump landing, a hat bouncing off, comedic, starts immediately, dry, no music, no voices', 'boing + spin + flump'),
 'C': ('strong gust of wind whoosh with fluttering cloth, then a hat landing with a soft thud on the floor, starts immediately, punchy, dry, no music, no voices', 'gust of wind + thud'),
}
SECS = 2.0

def main(argv):
    dry = '--dry-run' in argv
    again = set((argv[argv.index('--again') + 1] if '--again' in argv else '').upper().split(',')) - {''}
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    ab = os.path.join(HERE, 'ab'); raw_dir = os.path.join(ab, 'raw'); os.makedirs(raw_dir, exist_ok=True)
    rows = []
    for letter, (prompt, label) in CANDIDATES.items():
        body = {'text': prompt, 'duration_seconds': SECS, 'prompt_influence': 0.6}
        raw = os.path.join(raw_dir, f'cap_{letter}.mp3'); rec = raw + '.request.json'
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
        out = os.path.join(ab, f'cap_{letter}.mp3')
        lufs, peak = sd.level_sfx(raw, out, TARGET)
        _, _, secs = nm.measure(out)
        rows.append((letter, label, lufs, peak, secs))
        print(f'  {letter}  {label:<24} {secs}s  {lufs} LUFS / {peak} dBTP  → ab/cap_{letter}.mp3')
    if dry or not rows: return 0
    html = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Cap sound audition</title>',
            '<body style="font-family:system-ui;max-width:30em;margin:1em auto;padding:0 1em"><h2>Bobo — cap flies off</h2>',
            '<p>Phone, speaker only, two metres. All three at the same level.</p>']
    for letter, label, lufs, peak, secs in rows:
        html.append(f'<p><b>{letter}</b> — {label} ({secs}s, {lufs} LUFS)<br><audio controls src="cap_{letter}.mp3"></audio></p>')
    open(os.path.join(ab, 'index.html'), 'w', encoding='utf-8').write('\n'.join(html))
    print('✓ now play the three on your phone, then tell me A, B or C (ab/index.html plays them in a row)')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
