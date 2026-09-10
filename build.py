#!/usr/bin/env python3
import json, base64, os

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "voice_manifest.json")) as f:
    manifest = json.load(f)

with open(os.path.join(BASE, "audio", "bg_loop.mp3"), "rb") as f:
    bg_b64 = base64.b64encode(f.read()).decode("ascii")

with open(os.path.join(BASE, "find-and-tap.html")) as f:
    html = f.read()

audio_json = json.dumps(manifest, separators=(",", ":"))

marker_start = "/*__AUDIO_DATA_JSON__*/{}/*__END_AUDIO_DATA_JSON__*/"
assert marker_start in html, "audio marker not found"
html = html.replace(marker_start, "/*__AUDIO_DATA_JSON__*/" + audio_json + "/*__END_AUDIO_DATA_JSON__*/")

assert "/*__BG_MUSIC_B64__*/" in html, "bg music marker not found"
html = html.replace("/*__BG_MUSIC_B64__*/", bg_b64)

out_path = os.path.join(BASE, "find-and-tap.built.html")
with open(out_path, "w") as f:
    f.write(html)

print("wrote", out_path, len(html), "bytes", "(~{:.2f} MB)".format(len(html) / 1024 / 1024))
