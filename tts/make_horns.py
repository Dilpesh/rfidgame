#!/usr/bin/env python3
"""
Generate the cat and the train for Toy Town v2, several takes of each.

    python3 tts/make_horns.py                 # 4 takes of each, into tts/out/horns/
    python3 tts/make_horns.py --takes 6
    python3 tts/make_horns.py --only cat

Why this exists: the joke is "तुम train हो या बिल्ली?" and the two sounds
currently in the game measure within about 1 dB of each other in every band
below 1.2 kHz. They are, to an ear, the same sound. No rewrite can save a
contrast joke whose two halves are identical, so both get replaced together.

Sound generation is cheap and variable. Take several, then run
`python3 tts/pick_horns.py` which measures them and tells you which pair
actually contrasts - the ear is a poor judge of this on a laptop.

Standard library only. Key is found exactly the way tts/eleven.py finds it.
"""
import argparse, json, sys, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eleven import load_key                                    # same key discovery

API = "https://api.elevenlabs.io/v1/sound-generation"
OUT = HERE / "out" / "horns"

# Two prompts per sound, so a take that misses one framing may catch the other.
# The cat must live high and have NO low end; the train must have real weight
# underneath. That difference is the joke.
SOUNDS = {
    "horn_meow": {
        "duration": 1.2,
        "prompts": [
            "A cartoon cat meow, bright and comic, rising then falling in pitch, "
            "slightly indignant, like a toy cat. Clean, close, no background, no reverb.",
            "A single playful kitten meow, high and clear, cheeky, cartoon style. "
            "No music, no room echo, no other sounds.",
        ],
    },
    "horn_train_soft": {
        "duration": 1.2,
        "prompts": [
            "A small friendly steam train horn, two soft notes, warm and round, "
            "low pitched, gentle not shrill. Clean, close, no background.",
            "A toy locomotive whistle, deep and mellow, two short warm blasts, "
            "friendly and inviting. No background, no reverb.",
        ],
    },
}
INFLUENCE = [0.35, 0.6, 0.8]      # low = freer, high = obeys the prompt literally


def generate(key, prompt, seconds, influence):
    body = json.dumps({
        "text": prompt,
        "duration_seconds": seconds,
        "prompt_influence": influence,
    }).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "xi-api-key": key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--takes", type=int, default=4, help="takes per sound (default 4)")
    ap.add_argument("--only", choices=["cat", "train"], help="just one of them")
    ap.add_argument("--key")
    a = ap.parse_args()

    key, where = load_key(a.key)
    if not key:
        print("No API key found. See tts/eleven.py for where it looks.")
        return 1
    print("key from %s" % where)

    want = dict(SOUNDS)
    if a.only == "cat":
        want.pop("horn_train_soft")
    elif a.only == "train":
        want.pop("horn_meow")

    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for name, spec in want.items():
        for i in range(a.takes):
            prompt = spec["prompts"][i % len(spec["prompts"])]
            infl = INFLUENCE[i % len(INFLUENCE)]
            path = OUT / ("%s_take%d.mp3" % (name, i + 1))
            try:
                audio = generate(key, prompt, spec["duration"], infl)
            except urllib.error.HTTPError as e:
                print("  %-28s FAILED http %s %s" % (path.name, e.code,
                                                     e.read()[:160].decode("utf-8", "replace")))
                continue
            except Exception as e:
                print("  %-28s FAILED %s" % (path.name, e))
                continue
            path.write_bytes(audio)
            made += 1
            print("  %-28s %6.1f KB   influence %.2f" % (path.name, len(audio) / 1024, infl))
            time.sleep(0.4)

    print("\n%d takes in %s" % (made, OUT))
    print("Now run:  python3 tts/pick_horns.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
