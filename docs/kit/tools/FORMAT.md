# The story script format

One text file per story: `docs/kit/stories/<slug>/story.txt`. No JavaScript. A writer who
has never seen the engine can write one; `python3 docs/kit/tools/build.py <slug>`
turns it into a game.

The file has a **header** (facts about the story), then **scenes** (what
happens, in order), then one **wrong card** section (what Coco says when the
wrong card is tapped). Lines starting with `#` are comments. A `#tag` at the
end of a line's modifiers is a tag, not a comment (no space before it).

## Header

```
title: Jungle Rescue English
key: jungle-rescue-english            # storage key + folder name; defaults to the folder
language: hi
minutes: 9                            # what the parent is told
audio: audio/                         # where the clips + manifest.json live, relative to the game folder
cache: v3                             # bump when clips change, so phones re-download
hints at: 8s 17s 28s                  # the hint ladder, measured from the end of the prompt
voices: COCO=Saanu, NARRATOR=Jia      # for the audio producer; ids live in tts/config.json
activities: Pull an imaginary rope | Drink real water | Dance and freeze

card FUEL: ⛽ पेट्रोल say=पेट्रोल
card BISCUIT: 🍪 Biscuit = SNACK say=biscuit     # "= SNACK": its name in cards.json when different
card FLASHLIGHT: 🔦 टॉर्च = TORCH say=टॉर्च
```

`say=` is the child's own word for the card — what the kids call it when you
hold it up ("ये क्या है?"). Several are allowed with `|`. The compiler warns when
an ask's last hint or the praise after it never says that word. If the concept
behind a card is not something the child has physically done (petrol going into
a car), teach it in one sentence *before* asking, and describe the picture on
the card in the last hint ("लाल pump, pipe लगा है") — a machine can't check
that part; read it.

Card lines are in **progress-bar order**. Every card must exist in `cards.json`
— by its own name, by the `= NAME` you give, or as that game's alias there.
A card that is not in `cards.json` is a compile error: cards are global, so it
is added to the registry first (`python3 sync_cards.py`), then used.

## Scenes

```
== scene: Elephant rescue
```

A scene is a jump point in developer mode ("Jump to scene…"). Make a new scene
wherever you would want to audition from. A scene may start with

```
on jump: bed @JR_001 @0.25
```

— beats that run **only** when jumped to (the bed the scene expects to already
be playing).

### Lines

```
COCO [excited] @JR_015 #praise: YES! FUEL! टंकी भर गई!
NARRATOR: कोको जीप में बैठा।
ELEPHANT [playfully hungry] hold 2s: मेरे पेट में चूहे दौड़ रहे हैं।
```

`SPEAKER` in capitals, then optional modifiers, then `: ` and the words.

| modifier | means |
|---|---|
| `[excited]` | performance direction for the voice (ElevenLabs v3 reads it) |
| `@JR_015` | use this existing clip id. Without it the compiler assigns one and the clip has to be generated |
| `#praise` `#joke` `#action` `#effort` … | tags a variant can filter on (see below) |
| `hold 2s` | after the clip ends, keep waiting until 2 s have passed since it started (rope pulls, freeze calls) |

Lines play one after another on the foreground channel; the next line waits
for this one to end. Speech runs at full level (iOS does not allow otherwise).

### Sounds

```
sfx ting @JR_014                      # foreground: plays, story waits
sfx torch_click @JR_120 @0.85         # overlay at 85 %, story waits for it
sfx lori_music_box @JR_144 @0.5 under # overlay at 50 %, story carries on underneath
sfx rope_creak @JR_043 hold 2s
```

The word after `sfx` is a name for the producer (`ting`, `jeep_door`); `@JR_…`
pins an existing clip. **A volume makes it an overlay** — the only way to play
a sound at less than full level, and the only way to play it under speech.

### Beds and music

```
bed @JR_001                # loop, at the volume in the manifest
bed @JR_001 @0.25          # loop at 25 %
bed @JR_129_bed @0.18 crossfade   # fade from the current bed over ~0.7 s
bed stop

music @JR_160              # start the dance track (its own channel, manifest volume)
duck COCO @JR_161: Elephant dance!   # a line spoken over the music, music ducked to 30 %
music at 10s               # wait until the track reaches 10 s (stall-proof)
music stop
```

### Waiting, grouping

```
wait 1.5s          # or 800ms
together:          # everything indented plays at once; story waits for the longest
  sfx torch_click @JR_120 @0.85
  sfx ting @JR_119 @0.25
group #joke:       # a block a variant can drop as one unit
  sfx stomach_growl @JR_051
  COCO: ये क्या था?
```

### Random order, random pick, reusable blocks

```
shuffle:                 # the blocks inside play in a fresh random order every game
  group:
    ask RED
      prompt NARRATOR @card_red: Can you find something that is red?
    use praise
  group:
    ask BLUE
      …
one of:                  # exactly one of the lines inside, chosen at random
  NARRATOR @correct_1 #praise: Yay! You found it!
  NARRATOR @correct_2 #praise: Wonderful! That's exactly right!
```

A `== block NAME` section (anywhere above its first use) holds beats that
`use NAME` pastes in — the praise block above is written once and used after
every ask. This is how Find & Tap is written: eight asks in a `shuffle:`, each
followed by `use praise`.

### Asking for a card

```
ask ROPE
  prompt COCO [clear and warm] @JR_036: Captain, हमें कोई लंबी चीज़ चाहिए…
  hint COCO @JR_037: अपने cards को देखो…
  hint COCO @JR_038: इसे पकड़कर किसी चीज़ को खींचा जा सकता है.
  hint COCO @JR_039: ROPE वाला card scan करो.
sfx ting @JR_040
COCO @JR_041 #praise: YES! ROPE! रस्सी मिल गई।
```

The story stops at `ask` until the card is tapped. Hints play at the ladder
times if nothing has been tapped. A wrong card gets one of the wrong-card
responses (rotating). The beats after the `ask` are what happens on success —
the compiler warns if none of the next five is tagged `#praise` (STORY_CRAFT §2:
name the card, name the child, say what changed).

Also inside an ask:

```
  prompt none                          # no prompt (asking for the same card again)
  after prompt: bed stop               # beats that run once the prompt has finished
  remind COCO @JR_095 at 30s 60s 3m 5m 7m: Captain, Coco यहीं wait कर रहा है…
```

`remind` is for the water break: a gentle line at those times, as long as the
card has not come.

### An optional tap

```
tap window 2s FUEL:
  sfx overflow_bloop @JR_019
  COCO @JR_020 #joke: ओहो! बस करो, Captain!
```

For 2 s after this point, tapping FUEL plays the block once; otherwise the story
carries on. (The fuel-overflow gag.)

### Playing a cue "as the manifest says"

```
play @JR_103
```

For legacy split cues whose manifest entry starts a bed and plays parts. New
stories do not need it.

## The shared library

`docs/kit/library/` holds sounds and lines every story can use, each with a
description you can search:

```
python3 docs/kit/tools/library.py find soft chime          # is there one already?
python3 docs/kit/tools/library.py list
```

In a script, a bare name that matches a library id uses it — `sfx ting`,
`sfx boing`, `bed jungle_day @0.25` — and so does an explicit `@lib:ting`.
A shared spoken line is pinned the same way:

```
COCO @lib:great_job_en #praise: Yay! You found it! Great job!
```

Anything not in the library and not pinned is a clip still to be made;
`compile.py … --suggest` prints library matches next to each of those. When a
new clip turns out to be reusable, lift it into the library instead of copying
the file: `library.py promote <slug> <cue> --id <name> --desc "…" --tags a,b`.

A header line `tap sound: @lib:tap` names the soft tick played when a card is
tapped while Coco is still talking (LEARNINGS 9–10). The tap is remembered: if
it is the card the next question wants, the question is answered as soon as it
arms; a wrong one is never punished and never advances the story.

## Wrong card

```
== wrong card
sfx boing @JR_179
COCO @JR_180: ओहो! ये वाला काम नहीं करेगा। Captain, एक और card try करो!
--
sfx boing @JR_181
COCO @JR_182: ऊप्स! हमें कोई और चीज़ चाहिए। Captain, फिर से सोचो!
```

Variants separated by `--`, used in rotation. At least one is required.

## Variants — `docs/kit/stories/<slug>/variants/<name>.txt`

A variant changes **which tagged beats play**, never the audio, so one set of
clips serves every experiment. Open the game with `?v=<name>`, or pick it from
the developer-mode dropdown.

```
name: Fewer jokes, praise only after effort
exclude: joke              # drop every beat (or group) tagged #joke
exclude: praise
keep: effort               # …but keep beats tagged #effort even when they are also #praise
keep: joke every 2         # keep the 1st, 3rd, 5th… #joke beat
hints at: 6s 12s 20s       # a different hint ladder
note: for the 4-year-olds who lose the thread
```

A dropped `ask` (tag the ask itself) removes the question; the beats after it
still play, so tag the praise that belongs to it too, or put ask + praise in a
`group`.

## The name rules (every story, every change)

Decided 29 Sep 2026. The compiler warns when a script breaks them.

1. **Write to the child gender-neutral.** No verb endings that agree with the
   child's gender (करोगे / करोगी, गाओगे…). Use forms that don't agree: "तैयार
   हो?", "साथ गाओ", "करो". Coco talking about himself (धोऊँगा) is fine.
2. **The child's name only in short independent sentences.** `{name}` goes in
   its own line of at most six words with the name first or last — "शाबाश,
   {name}!", "{name}, देखो!" — never inside a story sentence. Story lines say
   "Captain" and are recorded once. The one exception is the intro line, tagged
   `#intro`. Every `{name}` line is recorded once with "Captain" (the fallback
   every child hears) and once per child with the name.
3. **The child is named at least every 60 seconds.** Measured along the
   quick-tap path with the real clip lengths; the water break doesn't count.
   Close a gap with an independent name line (praise after a card, "{name},
   देखो!" before a reveal), not by editing a story line.

Praise lines are the natural carriers: after every card's "YES! …" line put
`use praise`, a `one of:` pool of "Amazing, {name}!", "Good job, {name}!",
"Excellent work, {name}!", "You are absolutely right, {name}!".

How `{name}` compiles: the line's clip is the **Captain** version — `{name}`
read as "Captain" — and a child's pack supplies the same cue said with the
name. When the two wordings differ, write both: `अब से तुम हो — मेरे Captain!
|| अब से तुम हो — Captain {name}!` (Captain version, then the child's). Tag the
intro `#intro` so rule 2's length limit doesn't apply to it. Shared name lines
are `@lib:…` and live in the library; `names.py lines` lists every one across
the stories, `names.py captain` records the Captain versions, `names.py
generate <child>` the child's. The process is in `library/names/README.md`.

## What the compiler checks

- every card is in `cards.json`
- every `ask` is followed by a `#praise` line, and has hints
- no hardcoded counts in a line ("तीन cards") — LEARNINGS 15
- a `== wrong card` section exists
- listed cards are actually asked for
- the three name rules above: gendered verbs, `{name}` only in short independent
  lines, and no more than 60 s between name lines

`python3 docs/kit/tools/generate.py <slug>` makes every speech line the story
still needs (ElevenLabs, the speaker's approved voice from `library/voices.json`,
levelled to the standard) and adds it to the manifest; sounds are listed for
`library.py add`.

`python3 docs/kit/tools/compile.py docs/kit/stories/<slug>/story.txt --clips` prints every
clip the story needs with speaker, direction and text — the list the audio
producer (or `tts/generate.py`) works from. Clips pinned with `@` to an
existing manifest entry cost nothing.
