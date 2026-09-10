#!/usr/bin/env python3
import subprocess, os, base64, json

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(BASE, "audio_human")

TEXTS = {
    "intro": "Hi there! Let's play a fun finding game! Listen carefully, and go find the card I ask for.",
    "card_red": "Can you find something that is red?",
    "card_blue": "Now, find something blue!",
    "card_yellow": "Look around... can you find something yellow?",
    "card_green": "Where is something green? Go find it!",
    "card_circle": "Can you find the circle?",
    "card_square": "Now let's find the square!",
    "card_triangle": "Where is the triangle? Go find it!",
    "card_star": "Can you find the star?",
    "correct_1": "Yay! You found it! Great job!",
    "correct_2": "Wonderful! That's exactly right!",
    "retry_1": "Hmm, not quite. Try again!",
    "retry_2": "Almost! Look one more time!",
    "outro": "Wow, you found everything! You are amazing! Great job today!",
    "setup_hint": "Scan a card now to assign it.",
}

manifest = {}
for key, text in TEXTS.items():
    path = os.path.join(AUDIO, f"{key}.mp3")
    dur = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.decode().strip()
    duration_ms = int(float(dur) * 1000)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    manifest[key] = {"text": text, "b64": b64, "duration_ms": duration_ms}
    print(f"{key}: {duration_ms}ms, {len(b64)} b64 bytes")

with open(os.path.join(BASE, "voice_manifest.json"), "w") as f:
    json.dump(manifest, f)

print("\ntotal keys:", len(manifest))
