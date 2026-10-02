/* card-registry.js — one card registry for every story.
 *
 * A physical card means the same thing in every game. cards.json is the
 * source of truth; `python3 sync_cards.py` generates the block below from it.
 * The browser keeps ONE localStorage key for the whole site, so a card taught
 * in any game is known in all of them, and no game ever reads another game's
 * private map (the bug this replaces: jungle-rescue-english read Jungle
 * Rescue 2's "rescueGameCards" and got SNACK where it wanted BISCUIT).
 *
 * A game never sees a UID. It asks for the canonical card and maps that to its
 * own step id with its generated CARD_MAP (SNACK -> BISCUIT, TORCH ->
 * FLASHLIGHT ...), which sync_cards.py also writes, from the same file.
 *
 *   CardRegistry.lookup(raw)            -> "SNACK" | null   (raw = what the reader sent)
 *   CardRegistry.teach(raw, "SNACK")    -> adds a UID for a card, in every game at once
 *   CardRegistry.forget(raw)            -> removes a taught UID
 *   CardRegistry.uidsOf("SNACK")        -> ["6373651", "5720648"]
 *   CardRegistry.cards()                -> every canonical card, with its label
 *   CardRegistry.label("SNACK")         -> "Snack / cookie / biscuit"
 *   CardRegistry.seedVersion            -> the cards.json seed this page carries
 *
 * Seeding: on first load, and again whenever cards.json's seed_version changes,
 * the printed set is written into storage and WINS for the UIDs it names —
 * cards.json is the source of truth, so an edit there must take effect on every
 * phone. Between seeds, teach() wins, so a replacement card bought before
 * cards.json is updated still works today. UIDs taught by hand that cards.json
 * does not know are kept across re-seeds.
 *
 * Readers differ on leading zeros, case and whitespace, so everything is
 * compared on a normalised form — the same one scan-guard.js and sync_cards.py use.
 */
window.CardRegistry = (function () {
  const KEY = 'kahaniCards';

  /* __CARD_REGISTRY_START__ */
const SEED_VERSION = "2026-10-02a";
const DEFAULT = {
  "6170247": "BALLOONS",
  "6358547": "BANANA",
  "1778089577": "BANANA",
  "6375388": "BLANKET",
  "88154103": "CAKE",
  "1778512553": "CANDLE",
  "6358348": "CLAP",
  "6373847": "DANCE",
  "6375198": "DISCOBALL",
  "5688164": "FAN",
  "6374815": "FIRSTAID",
  "6359145": "FUEL",
  "6375007": "GEM",
  "6358746": "JUMP",
  "5688918": "KEY",
  "5688805": "LADDER",
  "2681159": "LAUGH",
  "5687908": "LIGHT",
  "6360778": "MANGO",
  "2692278": "MOON",
  "6360574": "MUSIC",
  "819667906": "MUSIC",
  "87959223": "PARTYCAP",
  "2696012": "PARTYHORN",
  "6358150": "PRUNERS",
  "6374623": "ROPE",
  "6373651": "SNACK",
  "5720648": "SNACK",
  "2692483": "TORCH",
  "6375577": "TORCH",
  "2690428": "WATER",
  "2682976": "WATER"
};
const LABELS = {
  BALLOONS:   "Balloons",
  BANANA:     "Banana",
  BLANKET:    "Blanket",
  CAKE:       "Cake",
  CANDLE:     "Candle",
  CAP:        "Cap & Goggles",
  CAR:        "Car",
  CLAP:       "Clap",
  DANCE:      "Dance",
  DISCOBALL:  "Disco ball",
  DOG:        "Doggy",
  ELEPHANT:   "Elephant",
  FAN:        "Fan",
  FIRSTAID:   "First aid",
  FUEL:       "Fuel",
  GEM:        "Gem",
  JUMP:       "Jump",
  KEY:        "Key",
  KITCHEN:    "Kitchen",
  LADDER:     "Ladder",
  LAUGH:      "Laugh",
  LIGHT:      "Light",
  MANGO:      "Mango",
  MOON:       "Moon",
  MUSIC:      "Speaker / Music",
  PARTYCAP:   "Birthday cap",
  PARTYHORN:  "Party horn",
  PRUNERS:    "Cutter / pruners",
  ROPE:       "Rope",
  SNACK:      "Snack / cookie / biscuit",
  TORCH:      "Torch",
  WATER:      "Water"
};
/* __CARD_REGISTRY_END__ */

  const norm = (v) => String(v == null ? '' : v).trim().toUpperCase().replace(/^0+(?=.)/, '');
  let map = null;

  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function write(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
  function save() { write(KEY, JSON.stringify(map)); }

  function load() {
    if (map) return map;
    map = {};
    try { const s = JSON.parse(read(KEY) || '{}'); if (s && typeof s === 'object') for (const u in s) map[norm(u)] = String(s[u]); }
    catch (e) { /* corrupt or private window: start from the printed set */ }
    if (read(KEY + ':seed') !== SEED_VERSION) {
      for (const u in DEFAULT) map[u] = DEFAULT[u];      // cards.json wins on a new seed
      save();
      write(KEY + ':seed', SEED_VERSION);
    }
    return map;
  }

  function lookup(raw) {
    const u = norm(raw);
    if (!u) return null;
    return load()[u] || null;
  }

  function teach(raw, card) {
    const u = norm(raw); card = String(card || '').trim().toUpperCase();
    if (!u || !card) return null;
    if (!(card in LABELS)) { console.warn('card registry: ' + card + ' is not in cards.json — add it there first'); return null; }
    load()[u] = card; save();
    return card;
  }

  function forget(raw) {
    const u = norm(raw);
    if (u in load()) { delete map[u]; save(); return true; }
    return false;
  }

  function uidsOf(card) {
    card = String(card || '').toUpperCase();
    return Object.keys(load()).filter((u) => map[u] === card);
  }

  function cards() {
    return Object.keys(LABELS).map((id) => ({ id, label: LABELS[id], uids: uidsOf(id) }));
  }

  function label(card) { return LABELS[String(card || '').toUpperCase()] || null; }

  return { lookup, teach, forget, uidsOf, cards, label, seedVersion: SEED_VERSION, key: KEY, _norm: norm, _reset() { map = null; } };
})();
