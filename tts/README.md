# Switching the narration to ElevenLabs

Four steps. Nothing touches your own recordings until the last one, and even
then they're backed up.

## 1. Get a key

Sign up at elevenlabs.io, then **profile → API keys → create**. In your shell:

```
export ELEVENLABS_API_KEY=sk_...
```

Put that line in `~/.zshrc` so it survives a new terminal. Never commit the
key — it is not in this repo and must not be.

**Cost.** Both stories together are about **4,100 characters ≈ 4,100 credits**
— roughly 7 minutes of audio. Check it yourself any time with
`python3 tts/generate.py cost`, which spends nothing. The free tier is 10k
credits/month but has no commercial licence and may not include API access;
Starter is $6/month for 30k, which is plenty for iterating. Regenerating only
re-spends on clips whose text or voice actually changed.

## 2. Pick a voice — do this before generating anything

Open the ElevenLabs **Voice Library**, filter for Hindi or Indian accent, and
add two or three you like to your account. Then:

```
python3 tts/generate.py voices                    # prints the ids on your account
python3 tts/generate.py audition <id> <id> <id>   # same 3 lines in each voice
```

You get `tts/auditions/<id>.mp3`. **Listen on a phone speaker, not your
laptop** — a voice that sounds warm on a laptop can turn thin and shrill on a
phone, and the phone is where the kids hear it.

Put the winner in `tts/config.json` as `default_voice`.

## 3. Build a story

```
python3 tts/generate.py build moon
python3 tts/generate.py build jungle-rescue
```

Clips land in `tts/out/<story>/`, not in the game. Every clip is mastered with
the same chain as your own recordings (`AUDIO_STANDARD.md` section 2) — raw
TTS is clean but not phone-ready, and unmastered it will disappear under the
ambience on a phone.

Add `--dry-run` to exercise the whole pipeline with silent files and spend
nothing. Useful after editing the script text.

Play `tts/out/moon/vo_hello.mp3` against `docs/moon/audio/vo_hello.mp3` before
going further. This is the moment to change your mind cheaply.

## 4. Install

```
python3 tts/generate.py install moon
python3 check_audio.py docs/moon
```

Your recordings are copied to `docs/moon/audio/_human_backup_<timestamp>/`
first. To go back, copy them out of there.

---

## Tuning

`tts/config.json`:

- **`voice_settings.stability`** — lower is more expressive and more variable;
  higher is flatter and more consistent. 0.45 is a starting point for a
  storyteller. Kids' stories usually want it lower than you'd expect.
- **`voice_settings.style`** — pushes the voice toward the emotion in the
  text. Too high gets hammy.
- **`per_clip_voice`** — give a character its own voice. The lion, the parrot
  and the monkey are the obvious candidates:

  ```json
  "per_clip_voice": {
    "vo_lion_1.mp3": "<a deeper voice id>",
    "vo_lion_2.mp3": "<a deeper voice id>"
  }
  ```

- **`model_id`** — `eleven_multilingual_v2` is the safe default for Hindi.
  `eleven_v3` has more emotional range. `eleven_flash_v2_5` is fast but
  flatter, and speed doesn't matter here since you generate once.

## Worth thinking about before you commit

Your kids know your voice. Coco *is* you, pitched up. A synthetic Coco is a
different thing, not a better version of the same thing — so audition it on
them, not just on yourself. A middle path that keeps what's yours: your voice
for Coco, ElevenLabs for the animal characters and for the English stories,
where the accent was the actual problem.

---

## Sound effects and music from the same key

`tts/assets.json` lists every effect in both stories with a prompt and a
duration. Edit the prompts, then:

```
python3 tts/generate.py sfx moon --dry-run   # exercise it, spend nothing
python3 tts/generate.py sfx moon             # generate for real
python3 check_audio.py docs/moon             # verify the beds
```

Same key, same `tts/out/<story>/` folder, same `install` step.

**The manifest knows which files are beds.** It read `AMBIENCE` and every
`under:` beat out of the games, so `sfx_night_jungle.mp3`, `sfx_jungle_day.mp3`
and `sfx_dance.mp3` are marked `"bed": true`. Those get the high-shelf cut and
a lower level, because they play underneath narration. Everything else stays
full-range and bright — between lines is where sparkle belongs.

The bed chain is deliberately more conservative than the one hand-tuned for
your night-jungle file, because what a generator returns is unknown. It was
verified against white noise — harsher than any real ambience — and still put
the bed 22.7 dB under the narration on a phone. `check_audio.py` remains the
gate.

**Prompt hints that matter here.** Say what you *don't* want: the existing
prompts carry "no crickets or cicadas" and "no cymbals or shakers" for exactly
the reason the moon game needed rescuing. Set `"loop": true` on anything that
has to tile seamlessly. For a music track rather than an effect, add
`"music": true` and it goes to the music endpoint instead.

## Emotion in the narration

Switch `model_id` to `eleven_v3` in `tts/config.json` and you can direct
delivery inline in the script text:

```
[excited] शाबाश! [laughs] तुम सच में जंगल के हीरो हो!
```

Tags cover emotions (`[curious]`, `[mischievously]`), delivery (`[whispers]`,
`[shouts]`) and non-verbal sounds (`[laughs]`, `[sighs]`). They go in the line
text in `scripts/source/*.json`, so the printed script shows the direction too.
