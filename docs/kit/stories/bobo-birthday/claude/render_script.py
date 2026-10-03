#!/usr/bin/env python3
"""Render story.txt as a readable production script (script.md). Usage: python3 render_script.py"""
import re, os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'story.txt'), encoding='utf-8').read().splitlines()
out = []
meta = {}
hints = ['8 s', '17 s', '28 s']
LINE = re.compile(r'^(\s*)(prompt |hint |duck )?([A-Z]+)((?:\s+\[[^\]]*\]|\s+@\S+|\s+#\S+|\s+hold \S+)*)\s*:\s*(.*)$')
def name(t):
    if '||' in t: t = t.split('||')[1].strip()
    return t.replace('{name}', '**[NAME]**')
def say(sp, mods, text, kind=''):
    d = re.search(r'\[([^\]]*)\]', mods or '')
    dirn = f' *({d.group(1)})*' if d else ''
    lib = ' `library clip`' if '@lib:' in (mods or '') else ''
    return f'**{sp}**{dirn}: {name(text)}{lib}'
hint_i = 0
for raw in src:
    line = raw.rstrip()
    if not line or line.lstrip().startswith('#'): continue
    s = line.strip()
    m = re.match(r'^(title|minutes|activities|voices|hints at):\s*(.*)$', s)
    if m: meta[m.group(1)] = m.group(2); continue
    if re.match(r'^(key|language|audio|cache|tap sound):', s): continue
    m = re.match(r'^card (\w+):\s*(\S+)\s+(.*?)(?:\s*=\s*\w+)?(?:\s+say=(\S+))?$', s)
    if m: meta.setdefault('cards', []).append(f'{m.group(2)} {m.group(3)} (kids say: {m.group(4) or "?"})'); continue
    if s.startswith('== block praise'):
        out.append('\n### Praise pool — one of these, at random, after every card\n'); continue
    if s.startswith('== scene:'):
        out.append(f'\n## {s.split(":",1)[1].strip()}\n'); continue
    if s.startswith('== wrong card'):
        out.append('\n## Wrong card (rotating)\n'); continue
    if s == '--': out.append('—'); continue
    if s == 'one of:': continue
    if s.startswith('ask '):
        out.append(f'\n> ⏸ **WAITS FOR THE {s[4:]} CARD**'); hint_i = 0; continue
    if s.startswith('sfx '):
        n = s.split()[1]; out.append(f'🔊 *{n.replace("_"," ")}*'); continue
    if s.startswith('wait '): out.append(f'⏱ *(silence {s[5:]})*'); continue
    if s.startswith('music at '): out.append(f'🎵 *(music keeps playing to {s[9:]})*'); continue
    if s.startswith('music stop'): out.append('🎵 *music ends*'); continue
    if s.startswith('music '): out.append(f'🎵 **MUSIC STARTS** — *{s[6:]}* (library)'); continue
    if s == 'use praise': out.append('⭐ *praise line with the child\'s name (pool above)*'); continue
    if s == 'together:': out.append('*(at the same time:)*'); continue
    m = LINE.match(line)
    if m:
        indent, kind, sp, mods, text = m.groups()
        if kind == 'prompt ': out.append(f'> {say(sp, mods, text)}')
        elif kind == 'hint ':
            lab = hints[hint_i] if hint_i < 3 else '?'; hint_i += 1
            out.append(f'> ↳ *hint at {lab}:* {say(sp, mods, text)}')
        elif kind == 'duck ': out.append(f'🎵 {say(sp, mods, text)} *(over the music)*')
        else: out.append(say(sp, mods, text))
        continue
    out.append(f'`{s}`')
hdr = [f'# {meta.get("title","")} — production script', '',
       f'*~{meta.get("minutes","?")} min · hints at {meta.get("hints at","")} after each ask · voices: {meta.get("voices","")}*', '',
       '**Cards on the table (progress-bar order):** ' + ' · '.join(meta.get('cards', [])), '',
       '**Props:** a real paper birthday cap on the table.', '',
       '**How to read this:** **[NAME]** = the child\'s name (Captain when there is no name pack). ⏸ = the story stops until that card is tapped; the hints play only while nothing is tapped. 🔊 = sound effect. ⭐ = a praise line from the pool. Text in *(italics)* is the voice direction, not spoken.', '',
       f'**Activities:** {meta.get("activities","")}', '']
open(os.path.join(here, 'script.md'), 'w', encoding='utf-8').write('\n'.join(l if (l.startswith('#') or not l) else l + '  ' for l in hdr + out) + '\n')
print('script.md written')
