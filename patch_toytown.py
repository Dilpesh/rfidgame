#!/usr/bin/env python3
"""Re-apply everything we add on top of a fresh Toy Town deploy.

    python3 patch_toytown.py docs/chuku_toy_town_deploy

The deploy folder arrives as a clean build each time, with none of the work
from earlier rounds in it. Rather than redo it by hand and hope, this applies
it all with assertions: if a base file has changed shape, it fails loudly
instead of silently skipping a fix.

Idempotent — running it twice changes nothing.
"""
import os, re, sys

# ---------------------------------------------------------------- audio.js --
AUDIO = [
 ("music ducks further under speech",
  "base*.25",
  # measured: at .25 the dance music sat 17.1 dB under the narration at 6-8 kHz
  # on a phone, inside the 20 dB bar. .15 measures -21.6 dB. AUDIO_STANDARD.md §1
  "base*.15"),
 ("audio context can be rebuilt after a call",
  " async resume(){if(!this.ctx){",
  " // A phone call can leave the context suspended, 'interrupted' (iOS) or closed.\n"
  " // A closed one can never be revived: build a fresh one and drop the decoded\n"
  " // buffers with it, since they belong to the old context.\n"
  " running(){return this.ctx&&this.ctx.state==='running'}\n"
  " async resume(){\n"
  "  if(this.ctx&&this.ctx.state==='closed'){this.ctx=null;this.buffers.clear();this.sources.clear();this.beds={}}\n"
  "  if(!this.ctx){"),
]

# --------------------------------------------------------------- index.html --
INDEX = [
 ("load the shared helpers",
  '<script src="story.js"></script>',
  '<script src="../reader-check.js"></script><script src="../story-intro.js"></script>'
  '<script src="story.js"></script>'),
 ("mode pill",
  '<div class="transport">',
  '<div class="modepill" id="modePill">Card mode - scan a card to play</div><div class="transport">'),
]

CSS_ADD = """
/* mode pill: which mode a grown-up has the game in */
.modepill{display:inline-flex;align-items:center;gap:7px;margin:0 0 10px;padding:7px 12px;
  border-radius:999px;background:rgba(0,0,0,.08);font-size:12px;font-weight:700;letter-spacing:.02em}
.modepill.devactive{background:#efe7fb;color:#4c2f7a}
"""


def patch(path, edits, label):
    s = open(path, encoding="utf-8").read()
    done = []
    for name, old, new in edits:
        if new in s:
            done.append(name + " (already)")
            continue
        n = s.count(old)
        if n != 1:
            sys.exit("%s: '%s' matched %d times — the build has changed shape, "
                     "check it by hand" % (label, name, n))
        s = s.replace(old, new)
        done.append(name)
    open(path, "w", encoding="utf-8").write(s)
    return done


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = sys.argv[1].rstrip("/")
    root = os.path.dirname(os.path.abspath(__file__))
    for f in ("app.js", "audio.js", "index.html", "style.css"):
        if not os.path.exists(os.path.join(d, f)):
            sys.exit("%s: not a Toy Town deploy folder (no %s)" % (d, f))

    print("audio.js   :", ", ".join(patch(os.path.join(d, "audio.js"), AUDIO, "audio.js")))
    print("index.html :", ", ".join(patch(os.path.join(d, "index.html"), INDEX, "index.html")))

    css = open(os.path.join(d, "style.css"), encoding="utf-8").read()
    if ".modepill" not in css:
        open(os.path.join(d, "style.css"), "a", encoding="utf-8").write(CSS_ADD)
        print("style.css  : mode pill")
    else:
        print("style.css  : mode pill (already)")

    # app.js carries far too much to re-derive by string surgery — cards, modes,
    # wake lock, scan queueing, interruption recovery, the intro and reader
    # hooks. The maintained copy lives in the repo; take it wholesale, but only
    # after checking the build's own app.js is still the one it was written
    # against.
    keep = os.path.join(root, "docs", "toy-town", "app.js")
    incoming = os.path.join(d, "app.js")
    ours = open(keep, encoding="utf-8").read() if os.path.exists(keep) else ""
    theirs = open(incoming, encoding="utf-8").read()
    if "pendingCard" in theirs:
        print("app.js     : already patched")
    elif not ours or "pendingCard" not in ours:
        sys.exit("app.js: no patched copy to carry over from docs/toy-town/app.js")
    else:
        for marker in ("const CARDS=[", "const audio=new ChukuAudio", "window.scanCard="):
            if marker not in theirs:
                sys.exit("app.js: the build no longer contains %r — re-derive the "
                         "patches by hand rather than clobbering it" % marker)
        open(incoming, "w", encoding="utf-8").write(ours)
        print("app.js     : carried over the maintained copy")

    print("\nNow: mv the folder to docs/toy-town, keep cards.html, then")
    print("  python3 sync_cards.py && python3 tts/master_embedded.py --check  (if embedded)")


if __name__ == "__main__":
    main()
