#!/usr/bin/env python3
"""build_bobo_cards.py — the five printable cards for "Bobo Ki Birthday Party!".

Reuses the shared card system in docs/claude/cards/build_cards.py (same bold outline-and-flat-colour
style, same ISO 7810 ID-1 / CR80 portrait size, 54 x 85.6 mm) and adds the three pictures that did not
exist yet: CAKE, CANDLE and PARTYCAP. BANANA and the speaker/music card (the existing MUSIC picture)
are reused as they are, so they match the cards already printed for other stories.

    python3 build_bobo_cards.py            # writes bobo-cards.html next to this file
    node render_bobo.js                    # PNG per card (print-ready 300 dpi), contact sheet, A4 PDF
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, '..', '..', '..', '..', '..', 'claude', 'cards')):
    if os.path.exists(os.path.join(p, 'build_cards.py')): sys.path.insert(0, p); break
import build_cards as bc
g = bc.g

bc.ICONS["CAKE"] = g('''
  <rect x="6" y="86" width="88" height="8" rx="4" fill="#B0BEC5"/>
  <rect x="12" y="58" width="76" height="28" rx="6" fill="#F7C97B"/>
  <path d="M12 68 Q22 76 32 68 T52 68 T72 68 T88 68" stroke="#fff" stroke-width="5"/>
  <path d="M24 60 H76 V42 Q76 36 70 36 H30 Q24 36 24 42 Z" fill="#FF8FB1"/>
  <path d="M24 42 Q24 32 32 32 H68 Q76 32 76 42 V46 Q72 55 66 46 Q62 52 58 46 Q52 56 46 46 Q40 52 36 46 Q30 54 24 46 Z" fill="#fff"/>
  <circle cx="50" cy="23" r="8" fill="#E63946"/>
  <path d="M50 15 Q52 8 59 6" stroke="#2F8F4E" stroke-width="5"/>
  <path d="M22 78 l5 -3 M40 80 l5 3 M58 78 l5 -3 M74 80 l5 3" stroke="#E63946" stroke-width="4"/>
  <path d="M31 77 l5 3 M49 79 l5 -3 M67 80 l5 3" stroke="#3FA9F5" stroke-width="4"/>
''')

bc.ICONS["CANDLE"] = g('''
  <!-- glow -->
  <path d="M28 20 L20 15 M72 20 L80 15 M24 36 L14 36 M76 36 L86 36" stroke="#F0A500" stroke-width="5"/>
  <!-- holder -->
  <rect x="30" y="88" width="40" height="7" rx="3.5" fill="#B0BEC5"/>
  <!-- stick -->
  <rect x="39" y="46" width="22" height="44" rx="3" fill="#4FC3F7"/>
  <path d="M39 60 L61 54 M39 74 L61 68 M39 88 L61 82" stroke="#fff" stroke-width="5"/>
  <rect x="39" y="46" width="22" height="44" rx="3" fill="none"/>
  <!-- wick and flame -->
  <path d="M50 46 V38" stroke-width="5"/>
  <path d="M50 6 C64 20 66 32 50 40 C34 32 36 20 50 6 Z" fill="#FFB300"/>
  <path d="M50 20 C57 28 57 34 50 37 C43 34 43 28 50 20 Z" fill="#FFE066" stroke="none"/>
''')

bc.ICONS["PARTYCAP"] = g('''
  <path d="M39.3 34 L60.7 34 L65.2 44 L34.8 44 Z" fill="#FFD84D" stroke="none"/>
  <path d="M28.5 58 L71.5 58 L75.9 68 L24.1 68 Z" fill="#FFD84D" stroke="none"/>
  <path d="M50 12 L86 84 H14 Z" fill="none"/>
  <path d="M50 12 L86 84 H14 Z" fill="#8E5CF7" stroke="none"/>
  <path d="M39.3 34 L60.7 34 L65.2 44 L34.8 44 Z" fill="#FFD84D" stroke="none"/>
  <path d="M28.5 58 L71.5 58 L75.9 68 L24.1 68 Z" fill="#FFD84D" stroke="none"/>
  <circle cx="52" cy="52" r="2.6" fill="#fff" stroke="none"/>
  <circle cx="40" cy="76" r="2.6" fill="#fff" stroke="none"/>
  <circle cx="62" cy="78" r="2.6" fill="#fff" stroke="none"/>
  <path d="M50 12 L86 84 H14 Z"/>
  <rect x="10" y="82" width="80" height="11" rx="5.5" fill="#FF6FA3"/>
  <circle cx="50" cy="11" r="8" fill="#FFD84D"/>
''')

bc.ICONS["BLANKET"] = g('''
  <!-- a sleepy child tucked in under a striped blanket, folded down at the top: nothing else looks like this -->
  <rect x="12" y="6" width="76" height="42" rx="16" fill="#fff"/>
  <circle cx="50" cy="29" r="19" fill="#F2C29B"/>
  <path d="M32 26 Q33 8 50 8 Q67 8 68 26 Q58 17 50 20 Q42 17 32 26 Z" fill="#5B3A1E"/>
  <path d="M39 31 q3.5 3.5 7 0 M54 31 q3.5 3.5 7 0" stroke-width="2.4"/><path d="M45 39 q5 3.5 10 0" stroke-width="2.4"/>
  <path d="M8 50 Q18 42 30 48 T54 48 T78 48 T92 50 V88 Q92 95 85 95 H15 Q8 95 8 88 Z" fill="#3FA9F5"/>
  <path d="M8 50 Q18 42 30 48 T54 48 T78 48 T92 50 V62 Q80 68 66 62 T38 62 T8 62 Z" fill="#FFD84D"/>
  <path d="M13 76 H87 M13 88 H87" stroke="#fff" stroke-width="5.5"/>
  <path d="M8 50 Q18 42 30 48 T54 48 T78 48 T92 50 V88 Q92 95 85 95 H15 Q8 95 8 88 Z" fill="none"/>
  <path d="M8 62 Q23 68 38 62 T66 62 T92 62" fill="none" stroke-width="4"/>
''')

bc.ICONS["SPEAKER"] = g('''
  <!-- a real loudspeaker: box, small tweeter on top, big woofer below -->
  <rect x="6" y="10" width="50" height="82" rx="8" fill="#37424D"/>
  <circle cx="31" cy="30" r="9" fill="#8FA3B0"/>
  <circle cx="31" cy="30" r="3.5" fill="#37424D" stroke-width="4"/>
  <circle cx="31" cy="67" r="19" fill="#8FA3B0"/>
  <circle cx="31" cy="67" r="9" fill="#37424D" stroke-width="5"/>
  <circle cx="31" cy="67" r="2.5" fill="#F0A500" stroke="none"/>
  <!-- sound -->
  <path d="M64 72 q6 8 0 16 M72 66 q10 14 0 28" stroke="#F0A500" stroke-width="6"/>
  <!-- music note -->
  <path d="M73 46 V16 L91 11 V40" stroke-width="6"/>
  <ellipse cx="66" cy="48" rx="7.5" ry="6" fill="#E63946"/>
  <ellipse cx="83.5" cy="42" rx="7.5" ry="6" fill="#E63946"/>
''')
bc.LABELS.update({"CAKE": ("केक", "CAKE"), "CANDLE": ("मोमबत्ती", "CANDLE"),
                  "PARTYCAP": ("टोपी", "BIRTHDAY CAP"), "SPEAKER": ("स्पीकर", "SPEAKER"), "BLANKET": ("कंबल", "BLANKET")})
bc.TILE.update({"CAKE": "#FFE9F1", "CANDLE": "#FFF3D6", "PARTYCAP": "#F1E9FF", "SPEAKER": bc.TILE["MUSIC"]})

ORDER = ["CAKE", "BANANA", "CANDLE", "PARTYCAP", "SPEAKER", "BLANKET"]     # story order, then the spare BLANKET

# English larger than Hindi: Hindi 5.4 mm, English 7 mm (long names scale down so they stay on one line)
bc.PAGE = (bc.PAGE.replace("--hi:8mm; --en:3.6mm;", "--hi:5.4mm; --en:7mm;")
           .replace("--hi:7.4mm; --en:3.3mm;", "--hi:5mm; --en:6.4mm;")
           .replace(".en { font-size:var(--en); font-weight:800; letter-spacing:.5mm;", ".en { font-size:var(--en); font-weight:900; letter-spacing:.3mm;")
           .replace(".en.long { letter-spacing:.2mm; font-size:calc(var(--en) * .86); }", ".en.long { letter-spacing:.1mm; font-size:calc(var(--en) * .78); }")
           .replace("  .en.long {", "  .en { height:calc(var(--en) * 1.3); line-height:calc(var(--en) * 1.3); display:flex; align-items:center; justify-content:center; }\n  .en.long {")
           .replace(".hi { font-size:var(--hi); font-weight:900; line-height:1.15; letter-spacing:.1mm; }", ".hi { font-size:var(--hi); font-weight:700; height:calc(var(--hi) * 1.5); line-height:calc(var(--hi) * 1.5); letter-spacing:.1mm; }"))
page = (bc.PAGE.replace("Card labels — every card, every story", "Bobo Ki Birthday Party — 6 cards")
        .replace("every card, for every story (24 cards)", "Bobo Ki Birthday Party (6 cards)")
        .replace("Print all 24", "Print all 6").replace("One sheet for the whole deck.", "The five Bobo cards, plus a spare blanket card."))
out = os.path.join(HERE, "bobo-cards.html")
open(out, "w", encoding="utf-8").write(page.replace("__CARDS__", "".join(bc.card(c) for c in ORDER)))
print("wrote", out, "—", ", ".join(ORDER))
