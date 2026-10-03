#!/usr/bin/env python3
"""names.py — the child's name in the stories, as a repeatable process.

The rules (tools/FORMAT.md, "The name rules"): story lines say "Captain" and are
recorded once; the child's name only ever appears in short independent lines
written as `{name}` in a script. Every such line exists twice: once said with
"Captain" (the fallback every child hears) and once per child. This tool keeps
both sides in step. The process itself is written in docs/kit/library/names/README.md.

    python3 docs/kit/tools/names.py lines                 what the {name} lines are, across every story
    python3 docs/kit/tools/names.py captain [--dry-run]   generate the once-only "Captain" clips that are missing
    python3 docs/kit/tools/names.py captain --relevel     re-level every Captain clip from its cached take (no API)
    python3 docs/kit/tools/names.py add "Rida" --hindi रिदा [--alias Ridha,Reeda]
    python3 docs/kit/tools/names.py generate rida [--dry-run]   the child's clips → library/names/rida/
    python3 docs/kit/tools/names.py generate --all [--dry-run]  every registered child in one run; ends with a
                                                          check of each pack and its test link (--story <slug>)
    python3 docs/kit/tools/names.py check rida | --all    every line has a clip, levels within the standard
    python3 docs/kit/tools/names.py list                  which children have packs, and how complete

Generation talks to ElevenLabs with the speaker's approved voice and settings
(library/voices.json), then levels each clip to the audio standard (−16 LUFS,
−2 dBTP) and measures it. Raw responses are cached beside the request, so a
re-run spends nothing on a line whose text has not changed. ELEVENLABS_API_KEY
must be in the environment; nothing here stores it.
"""
import json, os, re, shutil, subprocess, sys, unicodedata, urllib.error, urllib.parse, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..'))
LIB = os.path.join(KIT, 'library')
NAMES = os.path.join(LIB, 'names')
sys.path.insert(0, HERE)
import compile as kc  # noqa: E402

SPEECH_FILTER = 'loudnorm=I=-16:TP=-2:LRA=11,alimiter=limit=0.85:level=false'
FALLBACK = 'Captain'


# ---------- small helpers ----------
def load_json(p, default=None):
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding='utf-8'))


def write_json(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def normalize_key(text):
    """What the player does to whatever a parent types."""
    text = unicodedata.normalize('NFC', str(text or '')).strip().lower()
    return re.sub(r"[\s.\-_'’]+", '', text)


def slugify(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    if not s:
        sys.exit('✗ give the slug yourself for a non-Latin name: --slug rida')
    return s


def ffmpeg():
    """ffmpeg from PATH, $FFMPEG, or the imageio-ffmpeg wheel (pip3 install imageio-ffmpeg)."""
    p = os.environ.get('FFMPEG') or shutil.which('ffmpeg')
    if p: return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit('✗ ffmpeg not found — brew install ffmpeg, or pip3 install imageio-ffmpeg')


def measure(path):
    r = subprocess.run([ffmpeg(), '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    lufs = re.search(r'Integrated loudness:\s+I:\s+(-?[\d.]+) LUFS', r.stderr)
    peak = re.search(r'True peak:\s+Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    dur = re.search(r'Duration:\s+(\d+):(\d+):([\d.]+)', r.stderr)
    if not (lufs and peak and dur):
        return None, None, None
    h, m, s = dur.groups()
    return float(lufs.group(1)), float(peak.group(1)), round(int(h) * 3600 + int(m) * 60 + float(s), 3)


def render_levelled(src, dst, extra_filter=None):
    """Level a clip to the standard: −16 LUFS integrated, true peak ≤ −2 dBTP.

    Not with loudnorm: ffmpeg's loudnorm is unreliable on clips under ~3 s (a two-second
    "Good job, Captain!" came out at −18, and 4.4's two-pass mode at −58). Instead: measure
    integrated loudness with ebur128 (reliable at any length), apply that gain as a plain
    volume change, hold the true peak with a limiter, measure again and trim once more."""
    pre = (extra_filter + ',') if extra_filter else ''
    tmp = dst + '.rendering.mp3'
    def render(gain_db):
        af = f'{pre}volume={gain_db:.2f}dB,alimiter=limit=0.79:attack=5:release=50:level=false'   # 0.79 ≈ −2 dBFS
        subprocess.run([ffmpeg(), '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-af', af, '-ac', '1', '-ar', '44100', '-b:a', '128k', tmp], check=True)
    lufs, peak, _ = measure(src) if not extra_filter else (None, None, None)
    if extra_filter or lufs is None:
        render(0.0); lufs, peak, _ = measure(tmp)
        if lufs is None: os.replace(tmp, dst); return
        render(-16.0 - lufs)
    else:
        render(-16.0 - lufs)
    lufs2, peak2, _ = measure(tmp)
    if lufs2 is not None and abs(lufs2 + 16.0) > 0.3:          # the limiter took some back: trim once more
        base = (-16.0 - lufs) if not extra_filter else (-16.0 - lufs)
        render(base + (-16.0 - lufs2))
    os.replace(tmp, dst)


def request_audio(url, key, body):
    req = urllib.request.Request(url, json.dumps(body, ensure_ascii=False).encode('utf-8'),
                                 {'xi-api-key': key, 'content-type': 'application/json', 'accept': 'audio/mpeg'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'ElevenLabs HTTP {e.code}: {e.read().decode("utf-8", "replace")[:300]}')
    except urllib.error.URLError as e:
        raise RuntimeError(f'could not reach api.elevenlabs.io ({e.reason}) — on a corporate network run this from a shell that can')
    if not data.startswith((b'ID3', b'\xff\xfb', b'\xff\xf3', b'\xff\xf2')):
        raise RuntimeError('ElevenLabs did not return an MP3')
    return data


def synth(raw_dir, stem, speaker, text, direction, key, dry_run):
    """One clip: cached raw request → levelled mp3 → measurements. Returns (status, entry|None)."""
    voices = load_json(os.path.join(LIB, 'voices.json')) or sys.exit('✗ library/voices.json missing')
    v = voices['speakers'].get(speaker) or sys.exit(f'✗ no voice for {speaker} in library/voices.json')
    tag = f'[{direction}] ' if direction else ''
    body = {'text': tag + text, 'model_id': voices.get('model_id', 'eleven_v3'), 'voice_settings': v['voice_settings']}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{v['voice_id']}?output_format={voices.get('output_format', 'mp3_44100_128')}"
    os.makedirs(raw_dir, exist_ok=True)
    raw, rec = os.path.join(raw_dir, stem + '.mp3'), os.path.join(raw_dir, stem + '.request.json')
    if os.path.exists(raw) and load_json(rec) == body:
        status = 'cached'
    elif dry_run:
        return 'would generate', None
    elif os.environ.get('KAHANI_FAKE_TTS'):
        # for the QA runs only: a silent clip in place of the API, so the wiring can be tested without a key
        subprocess.run([ffmpeg(), '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono', '-t', '0.5', '-c:a', 'libmp3lame', '-b:a', '64k', raw], check=True)
        write_json(rec, body); status = 'generated (FAKE)'
    else:
        if not key:
            sys.exit('✗ ELEVENLABS_API_KEY is not set in this shell')
        open(raw, 'wb').write(request_audio(url, key, body))
        write_json(rec, body)
        status = 'generated'
    entry = {'type': 'speech', 'voice': speaker, 'voice_id': v['voice_id'], 'model_id': body['model_id'],
             'voice_settings': v['voice_settings'], 'spoken_text': text, 'performance_tag': tag.strip(),
             'review_status': 'test', 'generated': datetime.date.today().isoformat()}
    return status, (entry, raw, v.get('filter'))


# ---------- the line list ----------
def story_slugs():
    d = os.path.join(KIT, 'stories')
    return [s for s in sorted(os.listdir(d)) if os.path.exists(os.path.join(d, s, 'story.txt')) and not s.startswith('_')]


def name_lines():
    """Every {name} line, from the library manifest (shared lines) and every story script.
    Returns [{key, cue, scope, speaker, direction, captain_text, name_text, file_dir, file}]"""
    out, seen = [], set()
    lib = kc.load_library()
    for lid, c in lib.items():
        if c.get('name_text'):
            out.append({'key': lid, 'cue': 'lib:' + lid, 'scope': 'library', 'speaker': c.get('voice', 'COCO'),
                        'direction': (c.get('performance_tag') or '').strip('[] '), 'captain_text': c.get('spoken_text', ''),
                        'name_text': c['name_text'], 'file_dir': LIB, 'file': c.get('file')})
            seen.add('lib:' + lid)
    for slug in story_slugs():
        try:
            st, errors, warnings = kc.compile_story(os.path.join(KIT, 'stories', slug, 'story.txt'))
        except kc.CompileError as e:
            print(f'⚠ {slug}: {e}'); continue
        audio_dir = os.path.normpath(os.path.join(KIT, 'games', slug, st.get('audioDir', 'audio/')))
        manifest = load_json(os.path.join(audio_dir, 'manifest.json'), {})
        for cid, c in st['clips'].items():
            if not c.get('nameText') or cid in seen:
                continue
            seen.add(cid)
            if cid.startswith('lib:'):
                # a library line the script uses but the library does not have yet
                out.append({'key': cid[4:], 'cue': cid, 'scope': 'library', 'speaker': c['speaker'], 'direction': c.get('emotion', ''),
                            'captain_text': c['text'], 'name_text': c['nameText'], 'file_dir': LIB, 'file': None})
            else:
                m = manifest.get(cid) or {}
                out.append({'key': f'{slug}:{cid}', 'cue': cid, 'scope': slug, 'speaker': c['speaker'], 'direction': c.get('emotion', ''),
                            'captain_text': c['text'], 'name_text': c['nameText'], 'file_dir': audio_dir, 'file': m.get('file')})
    return out


def cmd_lines(args):
    lines = name_lines()
    if not lines:
        print('no {name} lines in any story yet'); return
    print(f'{len(lines)} name lines · {sum(len(l["name_text"]) for l in lines)} characters per child\n')
    for l in lines:
        have = '✓' if l['file'] and os.path.exists(os.path.join(l['file_dir'], l['file'])) else '–'
        print(f'{have} {l["key"]:<36} {l["speaker"]:<8} [{l["direction"]}]  {l["captain_text"]}')
    print('\n✓ = the "Captain" clip exists · – = run: python3 docs/kit/tools/names.py captain')


# ---------- once: the Captain versions ----------
def cmd_captain(args):
    dry = '--dry-run' in args; relevel = '--relevel' in args
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    lib_path = os.path.join(LIB, 'manifest.json')
    lib = load_json(lib_path, {'version': 'lib-0', 'clips': {}})
    if 'clips' not in lib: lib = {'version': 'lib-0', 'clips': lib}
    changed_lib = False; done = 0
    for l in name_lines():
        if l['file'] and os.path.exists(os.path.join(l['file_dir'], l['file'])) and not relevel:
            continue
        if l['scope'] == 'library':
            stem = l['key']; dest_rel = f'voice/{stem}.mp3'; raw_dir = os.path.join(LIB, 'raw')
        else:
            stem = l['cue']; dest_rel = f'names-captain/{stem}.mp3'; raw_dir = os.path.join(l['file_dir'], 'raw')
        status, made = synth(raw_dir, stem, l['speaker'], l['captain_text'], l['direction'], key, dry)
        print(f'  {status:<15} {l["key"]:<36} {l["captain_text"]}')
        if not made:
            done += 1; continue
        entry, raw, flt = made
        dest = os.path.join(l['file_dir'], dest_rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
        render_levelled(raw, dest, flt)
        lufs, peak, secs = measure(dest)
        entry.update({'file': dest_rel, 'duration_seconds': secs, 'integrated_lufs': lufs, 'true_peak_dbfs': peak,
                      'name_text': l['name_text'], 'description': entry.get('description') or f'name line (Captain version): {l["captain_text"]}',
                      'tags': ['name', 'captain']})
        if lufs is not None and (abs(lufs + 16) > 1.5 or peak > -1.5):
            print(f'    !! {stem} measures {lufs} LUFS / {peak} dBTP — outside the standard')
        if l['scope'] == 'library':
            lib['clips'][l['key']] = entry; changed_lib = True
        else:
            mp = os.path.join(l['file_dir'], 'manifest.json'); m = load_json(mp, {})
            m[l['cue']] = entry; write_json(mp, m)
        done += 1
    if changed_lib:
        lib['version'] = bump(lib.get('version', ''))
        write_json(lib_path, lib)
    print(f'{"would generate" if dry else "generated"} {done} Captain clips' if dry or done else '✓ every Captain clip exists')


def bump(version):
    today = datetime.date.today().isoformat()
    m = re.match(r'^lib-(\d{4}-\d{2}-\d{2})([a-z])$', version)
    return f'lib-{today}{chr(ord(m.group(2)) + 1)}' if m and m.group(1) == today else f'lib-{today}a'


# ---------- per child ----------
def names_registry():
    return load_json(os.path.join(NAMES, 'names.json'), {'children': []})


def cmd_add(args):
    if not args or args[0].startswith('--'):
        sys.exit('✗ names.py add "Rida" --hindi रिदा [--alias Ridha,Reeda] [--slug rida]')
    display = args[0]
    hindi = opt(args, '--hindi') or sys.exit('✗ --hindi is required: how the name is SAID, in Devanagari (ElevenLabs reads this)')
    slug = opt(args, '--slug') or slugify(display)
    aliases = [a.strip() for a in (opt(args, '--alias') or '').split(',') if a.strip()]
    reg = names_registry()
    if any(c['slug'] == slug for c in reg['children']):
        sys.exit(f'✗ {slug} is already registered')
    reg['children'].append({'slug': slug, 'display': display, 'devanagari': hindi, 'aliases': aliases, 'added': datetime.date.today().isoformat()})
    write_json(os.path.join(NAMES, 'names.json'), reg)
    rebuild_index(reg)
    print(f'✓ {display} registered as {slug} (said "{hindi}")\n  next: python3 docs/kit/tools/names.py generate {slug}')


def rebuild_index(reg):
    keys, packs = {}, {}
    for c in reg['children']:
        ks = {normalize_key(c['display']), normalize_key(c['devanagari']), c['slug']} | {normalize_key(a) for a in c.get('aliases', [])}
        ks.discard('')
        for k in ks:
            if k in keys and keys[k] != c['slug']:
                sys.exit(f'✗ "{k}" would match both {keys[k]} and {c["slug"]}')
            keys[k] = c['slug']
        packs[c['slug']] = {'display': c['display'], 'devanagari': c['devanagari']}
    write_json(os.path.join(NAMES, 'index.json'), {'_comment': 'generated by names.py from names.json; the player lowercases the typed name, strips spaces/dots/hyphens and looks it up here', 'keys': keys, 'packs': packs})


def billed_chars(l, child):
    """What ElevenLabs charges for one line: the performance tag is sent too."""
    tag = f'[{l["direction"]}] ' if l['direction'] else ''
    return len(tag + l['name_text'].replace('{name}', child['devanagari']))


def generate_child(child, lines, key, dry, relevel):
    """Every {name} line for one child. Returns (counts, characters spent / to spend)."""
    slug = child['slug']
    out = os.path.join(NAMES, slug); raw_dir = os.path.join(out, 'raw')
    pack = load_json(os.path.join(out, 'manifest.json'), {'_child': {'display': child['display'], 'devanagari': child['devanagari']}, 'clips': {}})
    pack['_child'] = {'display': child['display'], 'devanagari': child['devanagari']}
    counts, spend = {}, 0
    for l in lines:
        text = l['name_text'].replace('{name}', child['devanagari'])
        stem = re.sub(r'[^A-Za-z0-9_-]+', '_', l['key'])
        status, made = synth(raw_dir, stem, l['speaker'], text, l['direction'], key, dry)
        counts[status] = counts.get(status, 0) + 1
        if status != 'cached':
            spend += billed_chars(l, child)
        print(f'  {status:<15} {l["key"]:<36} {text}')
        if not made:
            continue
        entry, raw, flt = made
        dest = os.path.join(out, stem + '.mp3')
        if status.startswith('generated') or relevel or not os.path.exists(dest):
            render_levelled(raw, dest, flt)
        lufs, peak, secs = measure(dest)
        entry.update({'file': stem + '.mp3', 'duration_seconds': secs, 'integrated_lufs': lufs, 'true_peak_dbfs': peak})
        if lufs is not None and (abs(lufs + 16) > 1.5 or peak > -1.5):
            print(f'    !! {stem} measures {lufs} LUFS / {peak} dBTP — outside the standard')
        pack['clips'][l['key']] = entry
    if not dry:
        pack['version'] = datetime.date.today().isoformat()
        write_json(os.path.join(out, 'manifest.json'), pack)
    return counts, spend


def check_child(slug, lines, quiet=False):
    """Every line has a clip and measures within the standard. Returns (ok, missing, off_level)."""
    pack = load_json(os.path.join(NAMES, slug, 'manifest.json'), {'clips': {}})
    ok = bad = off = 0
    for l in lines:
        e = pack['clips'].get(l['key'])
        p = e and os.path.join(NAMES, slug, e['file'])
        if not e or not os.path.exists(p):
            if not quiet: print(f'✗ {l["key"]}: no clip')
            bad += 1; continue
        lufs, peak = e.get('integrated_lufs'), e.get('true_peak_dbfs')
        level_ok = lufs is None or (abs(lufs + 16) <= 1.5 and peak <= -1.5)
        off += 0 if level_ok else 1
        if not quiet: print(f'✓ {l["key"]:<36} {e.get("duration_seconds", "?"):>6}s  {lufs} LUFS{"" if level_ok else "  !! level"}')
        ok += 1
    return ok, bad, off


def cmd_generate(args):
    """generate <slug> | generate --all   [--dry-run] [--relevel] [--story bobo-birthday]"""
    dry = '--dry-run' in args; relevel = '--relevel' in args
    story = opt(args, '--story') or 'bobo-birthday'
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip() or None
    reg = names_registry()['children']
    if '--all' in args:
        children = reg
        if not children:
            sys.exit('✗ no children registered — names.py add first')
    else:
        slug = args[0] if args and not args[0].startswith('--') else sys.exit('✗ names.py generate <slug> | --all  [--dry-run] [--relevel]')
        children = [next((c for c in reg if c['slug'] == slug), None) or sys.exit(f'✗ {slug} not registered — names.py add first')]
    lines = name_lines()
    if not dry and not key and not os.environ.get('KAHANI_FAKE_TTS'):
        # spend nothing, change nothing, if the key is missing — say so before the first line
        todo = [c['slug'] for c in children if check_child(c['slug'], lines, quiet=True)[1]]
        if todo:
            sys.exit(f'✗ ELEVENLABS_API_KEY is not set in this shell — nothing was generated ({", ".join(todo)} still need clips)')
    summary, total, failed = [], 0, []
    for c in children:
        print(f'\n— {c["display"]} ({c["devanagari"]}) —')
        try:
            counts, spend = generate_child(c, lines, key, dry, relevel)
        except RuntimeError as e:
            # cached takes survive; a re-run picks up where this stopped, free for what is done
            print(f'  ✗ stopped: {e}'); failed.append(c['slug']); counts, spend = {'failed': 1}, 0
        total += spend
        summary.append((c, counts, spend))
    print('\n' + '=' * 72)
    if dry:
        for c, counts, spend in summary:
            print(f'{c["slug"]:<12} {c["display"]:<12} {c["devanagari"]:<10} ' + ' · '.join(f'{v} {k}' for k, v in counts.items()) + f'  ·  {spend} characters')
        print(f'TOTAL: {total} characters (ElevenLabs credits) across {len(summary)} child(ren). Nothing was generated.')
        return
    all_good = True
    for c, counts, spend in summary:
        ok, bad, off = check_child(c['slug'], lines, quiet=True)
        good = not bad and not off and c['slug'] not in failed
        all_good &= good
        verdict = '✓' if good else '✗'
        print(f'{verdict} {c["display"]:<12} {c["devanagari"]:<10} {ok}/{len(lines)} clips, {bad} missing, {off} off-level, {spend} chars spent'
              f'\n    http://localhost:8000/docs/kit/games/{story}/index.html?dev&name={urllib.parse.quote(c["display"])}')
    print(f'TOTAL: {total} characters spent.')
    print('✓ ALL PACKS COMPLETE — listen to each on a phone speaker' if all_good
          else '✗ SOME PACKS INCOMPLETE — run the same command again (finished lines are cached and cost nothing)')
    if not all_good:
        sys.exit(1)


def cmd_check(args):
    if '--all' in args:
        slugs = [c['slug'] for c in names_registry()['children']]
    else:
        slugs = [args[0]] if args else sys.exit('✗ names.py check <slug> | --all')
    lines = name_lines(); failing = 0
    for slug in slugs:
        if len(slugs) > 1: print(f'\n— {slug} —')
        if not os.path.exists(os.path.join(NAMES, slug, 'manifest.json')):
            print(f'✗ no pack for {slug}'); failing += 1; continue
        ok, bad, off = check_child(slug, lines)
        print(f'{ok} clips ok, {bad} missing' + (f', {off} outside the loudness standard' if off else ''))
        failing += 1 if bad or off else 0
    if failing:
        sys.exit(1)


def cmd_list(args):
    reg = names_registry(); need = len(name_lines())
    if not reg['children']:
        print('no children registered yet — names.py add "Rida" --hindi रिदा'); return
    for c in reg['children']:
        pack = load_json(os.path.join(NAMES, c['slug'], 'manifest.json'), {'clips': {}})
        print(f'{c["slug"]:<12} {c["display"]:<12} {c["devanagari"]:<10} {len(pack["clips"])}/{need} clips')


def opt(args, name):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args): return args[i + 1]
    return None


def main(argv):
    cmds = {'lines': cmd_lines, 'captain': cmd_captain, 'add': cmd_add, 'generate': cmd_generate, 'check': cmd_check, 'list': cmd_list}
    if len(argv) < 2 or argv[1] not in cmds:
        print(__doc__); return 2
    cmds[argv[1]](argv[2:])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
