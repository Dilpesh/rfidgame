#!/usr/bin/env python3
"""Copy selected legacy clips into this story's self-contained review folder.

This only prepares MP3 previews. It never changes the old games or installs
assets into the production audio/manifest.json.
"""

import base64
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "audio_candidates"
STANDALONE = HERE.parent / "jungle-rescue" / "audio"
SHIPPED_HTML = HERE.parent / "jungle-rescue-hinglish" / "index.html"

STANDALONE_NAMES = (
    "sfx_jungle_day.mp3",
    "sfx_fuel.mp3",
    "sfx_engine.mp3",
    "sfx_elephant.mp3",
    "sfx_munch.mp3",
    "sfx_glug.mp3",
    "sfx_flashlight.mp3",
    "sfx_magic.mp3",
    "sfx_disco.mp3",
)
EMBEDDED_KEYS = (
    "dayAmb",
    "engineCough",
    "ting",
    "elephant",
    "mud",
    "rope",
    "stomach",
    "munchEle",
    "gulp",
    "flashlight",
    "owl",
    "boing",
    "dance",
    "nightAmb",
    "elephantSetup",
)


def write_once(path: Path, data: bytes) -> None:
    if path.exists():
        existing = hashlib.sha256(path.read_bytes()).digest()
        incoming = hashlib.sha256(data).digest()
        if existing != incoming:
            raise SystemExit(f"Refusing to overwrite changed candidate: {path}")
        return
    path.write_bytes(data)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name in STANDALONE_NAMES:
        source = STANDALONE / name
        if not source.is_file():
            raise SystemExit(f"Missing source: {source}")
        write_once(OUT / f"old_{name}", source.read_bytes())

    page = SHIPPED_HTML.read_text(encoding="utf-8")
    match = re.search(r"const media=(\{.*?\});", page, flags=re.DOTALL)
    if not match:
        raise SystemExit(f"Could not find embedded audio in {SHIPPED_HTML}")
    media = json.loads(match.group(1))
    for key in EMBEDDED_KEYS:
        write_once(
            OUT / f"shipped_{key}.mp3",
            base64.b64decode(media[key], validate=True),
        )

    print(f"Prepared {len(STANDALONE_NAMES) + len(EMBEDDED_KEYS)} candidates in {OUT}")


if __name__ == "__main__":
    main()
