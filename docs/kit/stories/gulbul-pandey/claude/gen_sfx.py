#!/usr/bin/env python3
"""gen_sfx.py — make the sound effects Gulbul Pandey still needs with ElevenLabs text-to-sound-effects,
level them, and add them to the shared library under the names story.txt already uses.

    ELEVENLABS_API_KEY=… python3 docs/kit/stories/gulbul-pandey/claude/gen_sfx.py --dry-run
    ELEVENLABS_API_KEY=… python3 docs/kit/stories/gulbul-pandey/claude/gen_sfx.py
    …/gen_sfx.py --only dog_bark,thud          # a subset; re-running skips sounds the library already has

Each sound is cached in claude/sfx-in/raw/ so a re-run spends nothing. Effects are levelled to the
effects target (about 7 dB under the voice: −23 LUFS) except the ones marked loud (−21: the thud is the joke).
Replace any of them later with a better file via library.py add — nothing here is final.
"""
import os, sys, json, subprocess, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); KIT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(KIT, 'tools')); import names as nm  # noqa
SFX = {  # id: (prompt, seconds, loud?, description, tags)
 'phone_ring':            ('old-fashioned telephone bell ringing twice, bright mechanical bell, dry, no room', 3.5, False, 'old telephone bell, two rings', 'phone,ring,bell'),
 'phone_beep':            ('single short electronic beep, phone pick-up tone', 0.6, False, 'single short beep, phone pick-up', 'beep,phone'),
 'brass_sting':           ('cartoon dramatic brass sting, dun dun DUN, three notes, comedic suspense', 2.5, False, 'cartoon dun-dun-DUN brass sting', 'sting,brass,dramatic,funny'),
 'slide_whistle_wobble':  ('cartoon slide whistle falling down then a wobbly boing, comedic fall', 1.8, False, 'slide whistle falling + wobble', 'slide,whistle,fall,funny'),
 'thud':                  ('big cartoon body fall thud on a wooden floor, dry, no reverb, punchy', 1.0, True, 'big cartoon fall thud, dry and punchy', 'thud,fall,funny'),
 'siren_engine':          ('police siren wee-woo twice then a car engine revving and driving away, cartoon style', 4.5, False, 'police siren ×2 then car drives off', 'siren,police,car,engine'),
 'doorbell_door_creak':   ('house doorbell ding dong, then a long slow wooden door creak opening', 3.5, False, 'doorbell ding-dong then door creak', 'doorbell,door,creak'),
 'mystery_sting':         ('short gentle mystery sting, curious pizzicato strings, hmm what is this, playful not scary', 1.8, False, 'gentle curious mystery sting', 'sting,mystery,curious'),
 'dog_bark':              ('friendly medium-sized dog barking twice, clear happy woof woof, no growl, dry', 1.8, False, 'friendly dog, two clear barks', 'dog,bark,animal'),
 'dog_pant_bark':         ('happy dog panting excitedly with one small playful woof', 2.5, False, 'happy dog panting + one small woof', 'dog,pant,animal'),
 'footsteps_cloth_rustle':('quick footsteps indoors on a floor, then a towel or cloth being lifted and rustled', 3.5, False, 'quick indoor footsteps then cloth rustle', 'footsteps,cloth,rustle'),
 'police_whistle_drums':  ('two crisp police whistle blasts then a short marching snare drum roll ending cleanly', 4.5, False, 'two whistle blasts + marching snare roll', 'whistle,drums,march,outro'),
}
def main(argv):
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    dry = '--dry-run' in argv
    only = set((argv[argv.index('--only') + 1] if '--only' in argv else '').split(',')) - {''}
    lib = nm.load_json(os.path.join(KIT, 'library', 'manifest.json')) or {}
    have = set(lib.get('clips', lib).keys()) if isinstance(lib, dict) else set()
    raw_dir = os.path.join(HERE, 'sfx-in', 'raw'); os.makedirs(raw_dir, exist_ok=True)
    for sid, (prompt, secs, loud, desc, tags) in SFX.items():
        if only and sid not in only: continue
        if sid in have: print(f'  in library     {sid}'); continue
        raw = os.path.join(raw_dir, sid + '.mp3'); rec = raw + '.request.json'
        body = {'text': prompt, 'duration_seconds': secs, 'prompt_influence': 0.5}
        if os.path.exists(raw) and nm.load_json(rec) == body: status = 'cached'
        elif dry: print(f'  would generate {sid:<24} {secs}s  "{prompt[:60]}"'); continue
        else:
            if not key: sys.exit('✗ ELEVENLABS_API_KEY is not set in this shell')
            req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', data=json.dumps(body).encode(),
                                         headers={'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg'})
            open(raw, 'wb').write(urllib.request.urlopen(req, timeout=120).read()); nm.write_json(rec, body); status = 'generated'
        lev = os.path.join(HERE, 'sfx-in', sid + '.mp3')
        target = -21 if loud else -23
        subprocess.run([nm.ffmpeg(), '-loglevel', 'error', '-y', '-i', raw, '-af', f'highpass=f=120,loudnorm=I={target}:TP=-2:LRA=11', '-ar', '44100', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '128k', lev], check=True)
        r = subprocess.run([sys.executable, os.path.join(KIT, 'tools', 'library.py'), 'add', lev, '--id', sid, '--type', 'sfx', '--desc', desc + ' (ElevenLabs sound-generation, placeholder until replaced)', '--tags', tags + ',generated'], capture_output=True, text=True)
        print(f'  {status:<14} {sid:<24} → library' + ('' if r.returncode == 0 else f'  ✗ {r.stderr.strip()[:120]}'))
    print('done — now: python3 docs/kit/tools/build.py gulbul-pandey')
if __name__ == '__main__': main(sys.argv[1:])
