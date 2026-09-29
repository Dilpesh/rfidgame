#!/usr/bin/env python3
"""compile.py — turn a readable story script into story.json for the shared engine.

    python3 docs/kit/tools/compile.py docs/kit/stories/<slug>/story.txt            # writes story.json beside it
    python3 docs/kit/tools/compile.py docs/kit/stories/<slug>/story.txt --check    # lint only, no output
    python3 docs/kit/tools/compile.py docs/kit/stories/<slug>/story.txt --clips    # print the clip list (for TTS)
    python3 docs/kit/tools/compile.py docs/kit/stories/<slug>/story.txt --suggest  # …with library matches for clips still to make

The script format is documented in docs/kit/tools/FORMAT.md. This file has no opinion about
audio or the browser: it only produces the JSON the engine (docs/kit/engine/kahani.js) reads,
plus the list of clips a story needs so tts/generate.py knows what to make.

The compiler also enforces the STORY_CRAFT rules that can be checked mechanically —
every ask has praise after it, no hardcoded counts in a line, jokes are tagged so a
variant can drop them — and refuses a card that is not in cards.json (the registry is
the source of truth: a new card is added there first).
"""
import copy, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))          # docs/kit/tools
KIT = os.path.abspath(os.path.join(HERE, '..'))             # docs/kit
REPO = os.path.abspath(os.path.join(KIT, '..', '..'))       # the repo root: only cards.json is read from here

TIME_RE = re.compile(r'^(\d+(?:\.\d+)?)(ms|s|m)$')
SPEAKER_RE = re.compile(r'^([A-Z][A-Z0-9_]*)(\s+.*?)?:\s(.*)$')   # COCO [tag] @id #tag: text
ID_RE = re.compile(r'@([A-Za-z0-9_.:/-]+)')
TAG_RE = re.compile(r'#([a-z][a-z0-9-]*)')
VOL_RE = re.compile(r'@(0?\.\d+|1(?:\.0+)?)\b')
EMO_RE = re.compile(r'\[([^\]]*)\]')
HOLD_RE = re.compile(r'\bhold\s+(\d+(?:\.\d+)?(?:ms|s|m))')


class CompileError(Exception):
    pass


def ms(tok, line_no=0):
    m = TIME_RE.match(tok)
    if not m:
        raise CompileError(f'line {line_no}: cannot read time "{tok}" (use 800ms, 1.5s or 3m)')
    n, unit = float(m.group(1)), m.group(2)
    return int(n * {'ms': 1, 's': 1000, 'm': 60000}[unit])


def parse_modifiers(mods, line_no):
    """Pull @id, [emotion], #tags, @volume, hold N, under/wait out of the text between the
    keyword and the colon. Returns a dict; anything left over is an error."""
    out = {'tags': []}
    rest = mods or ''
    m = EMO_RE.search(rest)
    if m:
        out['emotion'] = m.group(1).strip()
        rest = rest[:m.start()] + rest[m.end():]
    m = HOLD_RE.search(rest)
    if m:
        out['hold'] = ms(m.group(1), line_no)
        rest = rest[:m.start()] + rest[m.end():]
    m = VOL_RE.search(rest)
    if m:
        out['volume'] = float(m.group(1))
        rest = rest[:m.start()] + rest[m.end():]
    m = ID_RE.search(rest)
    if m:
        out['id'] = m.group(1)
        rest = rest[:m.start()] + rest[m.end():]
    out['tags'] = TAG_RE.findall(rest)
    rest = TAG_RE.sub('', rest)
    for word in rest.split():
        if word in ('under', 'wait', 'crossfade', 'nowait'):
            out[word] = True
        else:
            raise CompileError(f'line {line_no}: unknown modifier "{word}"')
    return out


class Story:
    def __init__(self):
        self.meta = {}
        self.cards = []          # [{id,label,icon,registry}]
        self.scenes = []
        self.wrong = []
        self.variants = {}
        self.blocks = {}         # == block NAME: reusable beats, expanded by "use NAME"
        self.library = load_library()
        self.auto_ids = set()
        self.clips = {}          # cue id -> {speaker,text,emotion,kind,scene}
        self.auto_n = 0
        self.warnings = []

    def new_id(self, scene_i, kind):
        self.auto_n += 1
        key = (self.meta.get('key') or 'story').upper().replace('-', '_')
        cid = f'{key}_S{scene_i:02d}_{self.auto_n:03d}_{kind}'
        self.auto_ids.add(cid)          # a clip nobody has made yet
        return cid


def split_lines(text):
    """Yield (line_no, indent, content) skipping blanks and comment lines."""
    for i, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        # strip a trailing "  # comment" — but keep #tags (no space before them)
        content = re.sub(r'\s+#\s.*$', '', raw.rstrip())
        indent = len(raw) - len(raw.lstrip(' '))
        yield i, indent, content.strip()


def parse_header(story, line_no, line):
    if ':' not in line:
        raise CompileError(f'line {line_no}: header line needs "key: value"')
    key, _, val = line.partition(':')
    key, val = key.strip().lower(), val.strip()
    if key.startswith('card '):
        cid = key[5:].strip().upper()
        reg = None
        if '=' in val:
            val, reg = [s.strip() for s in val.split('=', 1)]
        parts = val.split(None, 1)
        icon, label = (parts[0], parts[1]) if len(parts) == 2 else ('🎴', parts[0])
        story.cards.append({'id': cid, 'icon': icon, 'label': label, 'registry': (reg or cid).upper()})
    elif key == 'activities':
        story.meta['activities'] = [s.strip() for s in val.split('|') if s.strip()]
    elif key == 'hints at':
        story.meta['hintDelays'] = [ms(t, line_no) for t in val.split()]
    elif key == 'voices':
        story.meta['voices'] = dict(p.strip().split('=', 1) for p in val.split(',') if '=' in p)
    elif key == 'minutes':
        story.meta['minutes'] = int(val)
    elif key == 'tap sound':
        m = ID_RE.search(val)
        if not m:
            raise CompileError(f'line {line_no}: tap sound needs an @id, e.g. tap sound: @lib:tap')
        story.meta['tapSound'] = m.group(1)
    else:
        story.meta[key] = val


def split_name(rest):
    """'jeep_door @JR_006 @0.5' -> ('jeep_door', '@JR_006 @0.5'); a leading word that is not a
    modifier is the producer's name for the sound."""
    rest = (rest or '').strip()
    if rest and not rest.startswith(('@', '[', '#')) and rest.split()[0] not in ('under', 'wait', 'crossfade', 'hold', 'nowait'):
        name = rest.split()[0]
        return name, rest[len(name):].strip()
    return None, rest


def parse_beat(story, scene_i, line_no, line, ctx):
    """One beat line -> dict. ctx = 'scene' | 'ask' | 'wrong'."""
    low = line.lower()
    first = line.split(None, 1)[0].lower() if line.split() else ''

    if first == 'wait':
        return {'op': 'wait', 'ms': ms(line.split()[1], line_no), 'line': line_no}
    if first == 'bed':
        mods = line[3:].strip()
        if mods.lower() == 'stop':
            return {'op': 'bed', 'stop': True, 'line': line_no}
        name, mods = split_name(mods)
        m = parse_modifiers(mods, line_no)
        cue = m.get('id') or (f'lib:{name}' if name in story.library else None) or story.new_id(scene_i, 'bed')
        story.clips.setdefault(cue, {'kind': 'bed', 'name': name, 'scene': scene_i, 'library': cue.startswith('lib:')})
        b = {'op': 'bed', 'cue': cue, 'line': line_no}
        if 'volume' in m: b['volume'] = m['volume']
        if m.get('crossfade'): b['crossfade'] = True
        return b
    if first == 'music':
        rest = line[5:].strip()
        if rest.lower() == 'stop':
            return {'op': 'music', 'stop': True, 'line': line_no}
        if rest.lower().startswith('at '):
            return {'op': 'music', 'at': ms(rest.split()[1], line_no) / 1000, 'line': line_no}
        name, rest = split_name(rest)
        m = parse_modifiers(rest, line_no)
        cue = m.get('id') or (f'lib:{name}' if name in story.library else None) or story.new_id(scene_i, 'music')
        story.clips.setdefault(cue, {'kind': 'music', 'name': name, 'scene': scene_i, 'library': cue.startswith('lib:')})
        return {'op': 'music', 'cue': cue, 'line': line_no}
    if first == 'play':
        m = parse_modifiers(line[4:].strip(), line_no)
        if 'id' not in m:
            raise CompileError(f'line {line_no}: play needs an @id')
        return {'op': 'play', 'cue': m['id'], 'tags': m['tags'], 'line': line_no}
    if first == 'sfx':
        rest = line[3:].strip()
        # "sfx jeep_door" (no @) names a sound the producer still has to make
        name, rest = split_name(rest)
        m = parse_modifiers(rest, line_no)
        cue = m.get('id') or (f'lib:{name}' if name in story.library else None) or story.new_id(scene_i, 'sfx')
        b = {'op': 'sfx', 'cue': cue, 'tags': m['tags'], 'line': line_no}
        if 'volume' in m:
            b['channel'] = 'overlay'
            b['volume'] = m['volume']
            b['wait'] = not m.get('under')
        else:
            b['channel'] = 'fg'
            b['wait'] = True
            if m.get('under'):
                raise CompileError(f'line {line_no}: "under" needs a volume, e.g. sfx @X @0.4 under')
        if 'hold' in m: b['hold'] = m['hold']
        story.clips.setdefault(cue, {'kind': 'sfx', 'name': name, 'scene': scene_i, 'library': cue.startswith('lib:')})
        if name and not story.clips[cue].get('name'):
            story.clips[cue]['name'] = name
        return b

    m = SPEAKER_RE.match(line)
    if m:
        speaker, mods, text = m.group(1), m.group(2), m.group(3).strip()
        mm = parse_modifiers(mods, line_no)
        cue = mm.get('id') or story.new_id(scene_i, speaker)
        b = {'op': 'say', 'cue': cue, 'speaker': speaker, 'text': text, 'tags': mm['tags'], 'line': line_no}
        if 'emotion' in mm: b['emotion'] = mm['emotion']
        if 'hold' in mm: b['hold'] = mm['hold']
        if '{name}' in text:
            # a per-child line: the clip pinned here is the "Captain" version every child hears
            # without a pack; a name pack supplies the same cue id said with the child's name.
            # "{name}" becomes "Captain" in that version — or write both wordings yourself:
            #   COCO: अब से तुम हो — मेरे Captain! || अब से तुम हो — Captain {name}!
            b['name'] = True
            if 'name' not in b['tags']: b['tags'].append('name')
            if ' || ' in text:
                captain_text, name_text = [t.strip() for t in text.split(' || ', 1)]
            else:
                captain_text, name_text = text.replace('{name}', story.meta.get('fallback name', 'Captain')), text
            if '{name}' not in name_text:
                raise CompileError(f'line {line_no}: the part after || must contain {{name}}')
            b['text'] = captain_text
            b['nameText'] = name_text
        story.clips.setdefault(cue, {'kind': 'speech', 'speaker': speaker, 'text': b['text'],
                                     'emotion': mm.get('emotion', ''), 'scene': scene_i, 'library': cue.startswith('lib:'),
                                     **({'nameText': b['nameText']} if b.get('name') else {})})
        return b
    raise CompileError(f'line {line_no}: cannot read "{line}"')


def parse_body(story, lines):
    """lines: list of (line_no, indent, content) after the header."""
    i = 0
    n = len(lines)

    def block(start, min_indent):
        """Collect the beats indented more than min_indent starting at `start`."""
        nonlocal i
        beats = []
        while i < n:
            line_no, indent, content = lines[i]
            if indent <= min_indent or content.startswith('== '):
                break
            beats.append(parse_line(line_no, indent, content))
        return beats

    def parse_line(line_no, indent, content):
        nonlocal i
        i += 1
        scene_i = len(story.scenes)
        first = content.split(None, 1)[0].lower()
        if first == 'ask':
            rest = content[3:].strip()
            m = parse_modifiers(' '.join(rest.split()[1:]), line_no)
            card = rest.split()[0].upper()
            if card not in [c['id'] for c in story.cards]:
                raise CompileError(f'line {line_no}: ask {card}: no "card {card}:" line in the header')
            ask = {'op': 'ask', 'card': card, 'prompt': None, 'hints': [], 'afterPrompt': [],
                   'remind': None, 'tags': m['tags'], 'line': line_no}
            for b in block(i, indent):
                k = b.get('_askpart')
                if k == 'prompt': ask['prompt'] = b['beat']
                elif k == 'hint': ask['hints'].append(b['beat'])
                elif k == 'after': ask['afterPrompt'].append(b['beat'])
                elif k == 'remind': ask['remind'] = b['beat']
                else:
                    raise CompileError(f'line {b.get("line")}: inside "ask" only prompt / hint / after prompt / remind lines are allowed')
            return ask
        if first == 'prompt':
            rest = content[6:].strip()
            if rest.lower() == 'none':
                return {'_askpart': 'prompt', 'beat': None, 'line': line_no}
            return {'_askpart': 'prompt', 'beat': parse_beat(story, scene_i, line_no, rest, 'ask'), 'line': line_no}
        if first == 'hint':
            return {'_askpart': 'hint', 'beat': parse_beat(story, scene_i, line_no, content[4:].strip(), 'ask'), 'line': line_no}
        if content.lower().startswith('after prompt:'):
            return {'_askpart': 'after', 'beat': parse_beat(story, scene_i, line_no, content.split(':', 1)[1].strip(), 'ask'), 'line': line_no}
        if first == 'remind':
            # remind COCO @JR_095 at 30s 60s 3m: text
            mm = re.match(r'^remind\s+(.*?)\s+at\s+((?:\S+\s+)*?\S+):\s(.*)$', content, re.S)
            if not mm:
                raise CompileError(f'line {line_no}: remind SPEAKER @id at 30s 60s 3m: text')
            head, times, text = mm.groups()
            beat = parse_beat(story, scene_i, line_no, f'{head}: {text}', 'ask')
            return {'_askpart': 'remind', 'beat': {'beat': beat, 'at': [ms(t, line_no) for t in times.split()]}, 'line': line_no}
        if content.lower() == 'together:':
            return {'op': 'together', 'beats': block(i, indent), 'line': line_no}
        if content.lower() == 'shuffle:':
            return {'op': 'shuffle', 'beats': block(i, indent), 'line': line_no}
        if content.lower() == 'one of:':
            return {'op': 'oneof', 'beats': block(i, indent), 'line': line_no}
        if first == 'use':
            name = content[3:].strip()
            if name not in story.blocks:
                raise CompileError(f'line {line_no}: no "== block {name}" defined above this line')
            return {'op': 'group', 'tags': [], 'block': name, 'beats': copy.deepcopy(story.blocks[name]), 'line': line_no}
        if content.lower().startswith('tap window'):
            mm = re.match(r'^tap window\s+(\S+)\s+([A-Z_]+):$', content)
            if not mm:
                raise CompileError(f'line {line_no}: tap window 2s CARD:')
            return {'op': 'tapwindow', 'ms': ms(mm.group(1), line_no), 'card': mm.group(2), 'beats': block(i, indent), 'line': line_no}
        if first in ('group', 'group:'):
            mm = re.match(r'^group(?:\s+(.*?))?:$', content)
            if not mm:
                raise CompileError(f'line {line_no}: group: or group #tag:')
            m = parse_modifiers(mm.group(1) or '', line_no)
            return {'op': 'group', 'tags': m['tags'], 'beats': block(i, indent), 'line': line_no}
        if first == 'duck':
            b = parse_beat(story, scene_i, line_no, content[4:].strip(), 'scene')
            b['op'] = 'duck'
            return b
        if content.lower().startswith('on jump:'):
            return {'_onjump': parse_beat(story, scene_i, line_no, content.split(':', 1)[1].strip(), 'scene'), 'line': line_no}
        return parse_beat(story, scene_i, line_no, content, 'scene')

    while i < n:
        line_no, indent, content = lines[i]
        if not content.startswith('== '):
            raise CompileError(f'line {line_no}: expected a "== scene: ..." heading before this line')
        head = content[3:].strip()
        i += 1
        if head.lower().startswith('scene:'):
            title = head.split(':', 1)[1].strip()
            scene = {'id': f's{len(story.scenes) + 1:02d}', 'title': title, 'onJump': [], 'beats': []}
            story.scenes.append(scene)
            for b in block(i, -1):
                if '_onjump' in b:
                    scene['onJump'].append(b['_onjump'])
                elif '_askpart' in b:
                    raise CompileError(f'line {b["line"]}: this line belongs under an "ask" (indent it)')
                else:
                    scene['beats'].append(b)
        elif head.lower().startswith('block '):
            name = head[6:].strip()
            story.blocks[name] = [b for b in block(i, -1) if '_askpart' not in b and '_onjump' not in b]
        elif head.lower().startswith('wrong card'):
            variant = []
            while i < n and not lines[i][2].startswith('== '):
                ln, ind, c = lines[i]
                if c == '--':
                    if variant: story.wrong.append(variant)
                    variant = []
                    i += 1
                    continue
                variant.append(parse_beat(story, 0, ln, c, 'wrong'))
                i += 1
            if variant: story.wrong.append(variant)
        else:
            raise CompileError(f'line {line_no}: unknown section "== {head}"')


def parse_variant(text, name):
    v = {'name': name, 'exclude': [], 'keepAlways': [], 'keepEvery': {}, 'set': {}}
    for line_no, indent, content in split_lines(text):
        key, _, val = content.partition(':')
        key, val = key.strip().lower(), val.strip()
        if key == 'name': v['name'] = val
        elif key == 'exclude': v['exclude'] += val.split()
        elif key == 'keep':
            m = re.match(r'^(\S+)\s+every\s+(\d+)$', val)
            if m: v['keepEvery'][m.group(1)] = int(m.group(2))
            else: v['keepAlways'] += val.split()
        elif key == 'hints at': v['set']['hintDelays'] = [ms(t, line_no) for t in val.split()]
        elif key == 'note': v['note'] = val
        else:
            raise CompileError(f'variant {name} line {line_no}: unknown key "{key}"')
    return v


def load_library():
    """docs/kit/library/manifest.json — sounds and lines shared by every story."""
    p = os.path.join(KIT, 'library', 'manifest.json')
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding='utf-8'))
    return d.get('clips', d)


def load_registry():
    p = os.path.join(REPO, 'cards.json')
    if not os.path.exists(p):
        return None
    return json.load(open(p, encoding='utf-8'))


def norm_uid(u):
    return re.sub(r'^0+(?=.)', '', str(u).strip().upper())


def resolve_cards(story, registry, errors):
    """Every story card must exist in cards.json (registry name, or a games[] alias)."""
    uids = {}
    if registry is None:
        story.warnings.append('cards.json not found at the repo root — no UIDs embedded; the game will rely on card-registry.js')
        return uids
    key = story.meta.get('key')
    reg = registry['cards']
    for c in story.cards:
        hit = None
        if c['registry'] in reg:
            hit = c['registry']
        else:
            for rname, r in reg.items():
                if r.get('games', {}).get(key, '').upper() == c['id']:
                    hit = rname
                    break
        if not hit:
            errors.append(f'card {c["id"]}: not in cards.json (add it there first — cards are global). '
                          f'Say "card {c["id"]}: icon Label = REGISTRY_NAME" if it has another name there.')
            continue
        c['registry'] = hit
        for u in reg[hit].get('uids', []):
            uids[norm_uid(u)] = c['id']
    story.meta['seedVersion'] = registry.get('seed_version', '')
    return uids


def walk(beats, fn):
    for b in beats:
        fn(b)
        for k in ('beats',):
            if isinstance(b.get(k), list): walk(b[k], fn)
        if b.get('op') == 'ask':
            for h in b['hints']: fn(h)
            if b['prompt']: fn(b['prompt'])
            for a in b['afterPrompt']: fn(a)
            if b['remind']: fn(b['remind']['beat'])


# ---- the name rules (Dilpesh, 29 Sep 2026) ----
# Verb endings that agree with the child's gender. A line to the child must not use them.
GENDERED = re.compile(r'\S*?(?:ोगे|ोगी|ओगे|ओगी|ेगा|ेगी)(?=[\s?!।.,]|$)')
GENDER_OK_WORDS = {'होगी', 'होगा', 'लगेगी', 'लगेगा', 'बनेगा', 'बनेगी', 'जाएगा', 'जाएगी', 'चलेगी', 'चलेगा', 'मिलेगा', 'मिलेगी', 'करेगा', 'करेगी', 'देखेगा', 'देखेगी'}
NAME_GAP_S = 60
NAME_LINE_MAX_WORDS = 6


def speech_seconds(text):
    """A rough length for a line nobody has recorded yet: Hindi/Hinglish at ~13 chars/s."""
    return 0.4 + len(text) / 13.0


def lint_names(story, durations):
    """1. no gendered verb endings in a line to the child;
       2. the child's name only in short independent sentences ({name} at the start or end, ≤ 6 words);
       3. a #name line at least every 60 s along the quick-tap path (water break excluded)."""
    warn = story.warnings.append
    beats_all = []
    walk([b for s in story.scenes for b in s['beats']], lambda b: beats_all.append(b))
    for b in beats_all:
        if b.get('op') not in ('say', 'duck'): continue
        text = b.get('nameText') or b['text']
        if b['speaker'] in ('COCO', 'NARRATOR') or b.get('name'):
            hits = [h for h in GENDERED.findall(text) if h.strip('?!।.') not in GENDER_OK_WORDS]
            if hits:
                warn(f'line {b["line"]}: gendered verb to the child ({", ".join(hits)}) — write it neutral: तैयार हो / गाओ / करो (name rule 1)')
        if b.get('name') and 'intro' not in (b.get('tags') or []):      # the #intro line may be long
            words = [w for w in text.split() if re.search(r'[\w\u0900-\u097F]', w)]
            at_edge = text.startswith('{name}') or text.rstrip('!?।. ').endswith('{name}')
            if len(words) > NAME_LINE_MAX_WORDS or not at_edge:
                warn(f'line {b["line"]}: {{name}} must be its own short sentence, name first or last, ≤ {NAME_LINE_MAX_WORDS} words '
                     f'(name rule 2) — got {len(words)} words')
    # rule 3: walk the quick-tap timeline
    t = [0.0]; last = [None]; first = [True]; music0 = [0.0]
    def dur(cue, text=''):
        d = durations.get(cue)
        return float(d) if d else speech_seconds(text or '')
    def run(beats):
        for b in beats:
            op = b['op']
            if op in ('say', 'duck', 'play'):
                if b.get('name'):
                    if last[0] is not None and t[0] - last[0] > NAME_GAP_S:
                        warn(f'line {b["line"]}: {int(t[0] - last[0])} s since the child was last named — add an independent name line before this (name rule 3)')
                    last[0] = t[0]
                t[0] += dur(b['cue'], b.get('text', ''))
                if b.get('hold'): t[0] += max(0, b['hold'] / 1000 - dur(b['cue'], b.get('text', '')))
            elif op == 'sfx':
                if b.get('wait', True): t[0] += dur(b['cue'], '') if b['cue'] in durations else 1.0
                if b.get('hold'): t[0] += max(0, b['hold'] / 1000 - 1.0)
            elif op == 'wait': t[0] += b['ms'] / 1000
            elif op == 'music':
                if 'at' in b: t[0] = max(t[0], music0[0] + b['at'])
                elif b.get('cue'): music0[0] = t[0]
            elif op == 'together': t[0] += 1.0
            elif op in ('group', 'shuffle'): run(b['beats'])
            elif op == 'oneof':
                if b['beats']: run(b['beats'][:1])
            elif op == 'tapwindow': t[0] += b['ms'] / 1000
            elif op == 'ask':
                if b['prompt']: run([b['prompt']])
                t[0] += 3.0                       # the child finds the card
                if b.get('remind'): last[0] = t[0] if last[0] is not None else None   # a child-paced break resets the clock
    for sc in story.scenes: run(sc['beats'])
    if last[0] is None and any(b.get('name') for b in beats_all) is False and beats_all:
        warn('no {name} lines at all — the child is never named (name rule 3)')
    elif last[0] is not None and t[0] - last[0] > NAME_GAP_S:
        warn(f'end of story: {int(t[0] - last[0])} s since the child was last named (name rule 3)')


COUNT_WORDS = re.compile(r'\b(\d+|एक|दो|तीन|चार|पाँच|पांच|छह|सात|आठ|नौ|दस)\s+(cards?|कार्ड|animals?|दोस्त|friends?|stops?)\b', re.I)


def lint(story, errors):
    """The STORY_CRAFT rules that a machine can check. Warnings, not errors, unless noted."""
    # The story as the child hears it: every scene in order, groups opened up.
    def flatten(beats, out):
        for b in beats:
            if b.get('op') in ('group', 'shuffle', 'oneof', 'together'):
                flatten(b['beats'], out)
            else:
                out.append(b)
        return out
    timeline = flatten([b for s in story.scenes for b in s['beats']], [])
    for j, b in enumerate(timeline):
        if b.get('op') != 'ask':
            continue
        # praise must follow every ask: one of the next few beats carries #praise
        following = timeline[j + 1:j + 6]
        if not any('praise' in (f.get('tags') or []) for f in following):
            story.warnings.append(f'line {b["line"]}: ask {b["card"]} has no #praise line within the next 5 beats '
                                  f'(STORY_CRAFT §2: name the card, name the child, say what changed)')
        if not b['hints'] and not b['remind']:
            story.warnings.append(f'line {b["line"]}: ask {b["card"]} has no hints (the 8/17/28 s ladder has nothing to say)')
    every = []
    walk([b for s in story.scenes for b in s['beats']], lambda b: every.append(b))
    for b in every:
        if b.get('op') in ('say', 'duck') and COUNT_WORDS.search(b['text']):
            story.warnings.append(f'line {b["line"]}: hardcoded count in a line ("{COUNT_WORDS.search(b["text"]).group(0)}") — LEARNINGS 15')
    for cid in list(story.clips) + ([story.meta['tapSound']] if story.meta.get('tapSound') else []):
        if cid.startswith('lib:') and cid[4:] not in story.library:
            if story.clips.get(cid, {}).get('nameText'):
                errors.append(f'{cid}: name line not recorded yet — python3 docs/kit/tools/names.py captain (see library/names/README.md)')
            else:
                errors.append(f'{cid}: not in docs/kit/library/manifest.json (python3 docs/kit/tools/library.py find <words>)')
    if not story.wrong:
        errors.append('no "== wrong card" section: the engine needs at least one warm wrong-card response')
    if not story.scenes:
        errors.append('no scenes')
    for c in story.cards:
        asked = []
        walk([b for s in story.scenes for b in s['beats']], lambda b: asked.append(b['card']) if b.get('op') == 'ask' else None)
        if c['id'] not in asked:
            story.warnings.append(f'card {c["id"]} is listed but never asked for')


def compile_story(path, variants_dir=None, durations=None):
    text = open(path, encoding='utf-8').read()
    story = Story()
    lines = list(split_lines(text))
    body_start = next((k for k, (_, _, c) in enumerate(lines) if c.startswith('== ')), len(lines))
    for line_no, indent, content in lines[:body_start]:
        parse_header(story, line_no, content)
    if 'key' not in story.meta:
        story.meta['key'] = os.path.basename(os.path.dirname(os.path.abspath(path)))
    if 'title' not in story.meta:
        raise CompileError('header needs "title:"')
    if not story.cards:
        raise CompileError('header needs at least one "card NAME: icon Label" line')
    parse_body(story, lines[body_start:])

    for cid in story.auto_ids:
        if cid in story.clips: story.clips[cid]['auto'] = True
    errors = []
    uids = resolve_cards(story, load_registry(), errors)
    lint(story, errors)
    durs = dict(durations or {})
    for lid, l in story.library.items():
        if l.get('duration_seconds') and f'lib:{lid}' not in durs: durs[f'lib:{lid}'] = l['duration_seconds']
    lint_names(story, durs)

    variants_dir = variants_dir or os.path.join(os.path.dirname(os.path.abspath(path)), 'variants')
    if os.path.isdir(variants_dir):
        for f in sorted(os.listdir(variants_dir)):
            if f.endswith('.txt'):
                name = f[:-4]
                story.variants[name] = parse_variant(open(os.path.join(variants_dir, f), encoding='utf-8').read(), name)

    out = {
        'format': 'kahani-story/1',
        'title': story.meta['title'],
        'heading': story.meta.get('heading', story.meta['title']),
        'key': story.meta['key'],
        'language': story.meta.get('language', 'hi'),
        'minutes': story.meta.get('minutes', 10),
        'audioDir': story.meta.get('audio', 'audio/'),
        'cacheTag': story.meta.get('cache', 'v1'),
        'hintDelays': story.meta.get('hintDelays', [8000, 17000, 28000]),
        'activities': story.meta.get('activities', []),
        'cards': story.cards,
        'uids': uids,
        'seedVersion': story.meta.get('seedVersion', ''),
        'wrong': story.wrong,
        'scenes': story.scenes,
        'variants': story.variants,
        'clips': story.clips,
        'voices': story.meta.get('voices', {}),
        'tapSound': story.meta.get('tapSound'),
        'libraryDir': story.meta.get('library', '../../library/'),
    }
    return out, errors, story.warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    path = argv[1]
    flags = set(argv[2:])
    try:
        out, errors, warnings = compile_story(path)
    except CompileError as e:
        print(f'✗ {e}'); return 1
    for w in warnings: print(f'⚠ {w}')
    for e in errors: print(f'✗ {e}')
    if errors:
        return 1
    if '--clips' in flags or '--suggest' in flags:
        library = load_library()
        for cid, c in out['clips'].items():
            where = 'library' if c.get('library') else ('TO MAKE' if c.get('auto') else 'pinned')
            if c['kind'] == 'speech':
                print(f'{cid}\t{where}\t{c["speaker"]}\t{c.get("emotion","")}\t{c["text"]}')
            else:
                print(f'{cid}\t{where}\t{c["kind"].upper()}\t\t{c.get("name") or ""}')
            if '--suggest' in flags and where == 'TO MAKE':
                words = set(re.findall(r'[a-z]+', ((c.get('name') or '') + ' ' + (c.get('text') or '')).lower().replace('_', ' ')))
                hits = []
                for lid, l in library.items():
                    hay = ' '.join([lid, l.get('description', ''), ' '.join(l.get('tags', [])), l.get('spoken_text', '')]).lower().replace('_', ' ')
                    score = sum(1 for w in words if len(w) > 2 and w in hay)
                    if score: hits.append((score, lid, l.get('description', '')))
                for score, lid, desc in sorted(hits, reverse=True)[:3]:
                    print(f'\t\t↳ library has {lid}: {desc}')
        return 0
    if '--check' in flags:
        print(f'✓ {out["title"]}: {len(out["scenes"])} scenes, {sum(1 for _ in out["clips"])} clips, {len(out["variants"])} variants')
        return 0
    dest = os.path.join(os.path.dirname(os.path.abspath(path)), 'story.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'✓ wrote {os.path.relpath(dest)}: {len(out["scenes"])} scenes, {len(out["clips"])} clips, {len(out["variants"])} variants')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
