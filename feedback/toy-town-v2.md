# Toy Town Express — v2 (test) — feedback

`docs/toy-town-v2` · the retuned copy, running beside the original so the two
can be played back to back

Nothing here is a different story. Same words, same voices, same 9 stops. What
changed: pacing and audio. See `feedback/toy-town.md` for where each change
came from.

---

## What is different from the original

| | original | v2 |
|---|---|---|
| Before a child can touch a card | 59s | **40s** — no line cut, the pocket gag moved to after the KEY |
| Sound effect levels | 36 dB spread, some 20 dB under the voice | **all at −20 dB**, `key_turn` ~8 dB more body |
| Effects playback gain | 0.55 | **1.0** |
| Master gain | 0.8 | **1.0** |
| Dance beat under the calls | drops to ≈−43 LUFS | **stays**, ducked to 0.35 not 0.15 |
| Beatless time in the dance | 43.9s of 113.5s | **24.2s** — same three rounds, same length |
| FREEZE | music stops, *then* the word | **land together** |
| Fourth hint | 45s | **25s** |
| After the water instruction | a joke | **silence** |

Unchanged on purpose: the water reminders (still 30 / 60 / 120s — asked to be
left alone, though `STORY_CRAFT.md` now suggests 30 / 45 / 75), the dance
length, every line of narration, every voice.

## Not in v2, though it was recommended

**Acknowledgement after a correct card.** Still absent — at stop 0 and stop 3
the child hears only sound effects. Drafted in `ELEVENLABS_BRIEF.md` §3b.

This makes the first session a clean comparison: v2 differs from the original
*only* in pacing and audio, so anything you see is attributable to those.

---

## Sessions

### (add after the first play)

Worth watching, since these are what changed:

- Do they touch a card in the first 20 seconds, or still drift during the opening?
- During the dance — does the beat keep going under Chuku's instructions, and does "FREEZE!" land *with* the music stopping?
- When the key turns, can you hear it from where you are sitting?
- After the water instruction, does the silence feel right, or like something broke?

---

## 2026-09-21 · played with both kids — the first real session

The single most useful session so far. Two children, different reactions,
recorded separately because the disagreements matter as much as the agreements.

### Landed

| what | kid 1 | kid 2 |
|---|---|---|
| Half a sandwich in each pocket | ✅ | |
| **आलू पराठे की खुशबू** (lunchbox on the head → the smell) | ✅ | |
| Lunchbox worn as a hat — "सिर पे lunchbox" | | ✅ |
| **मूँछ** — the moustache dancing | ✅ | ✅ |
| **मूँछ जी… ticket दिखाइए** | | ✅ |
| **मेरी battery तो sandwich से चलती है** | | ✅ |
| "मेरे पहिए भी ताली बजाना चाहते हैं" | | ✅ |
| **"ये कौन करता है?!"** — the catchphrase | ✅ | ✅ |
| Chuku's voice itself gets a laugh | | ✅ |

**Three of these I had marked for removal.** The आलू पराठा smell, the
moustache's ticket and the sandwich battery all landed. See the correction
written into `STORY_CRAFT.md` §3 — the audit was too aggressive and the
taxonomy was wrong.

**"ये कौन करता है?!" is the strongest thing in the story** and works for both
kids. Use it three or four times, always in the same funny voice.

### Did not land

| what | note |
|---|---|
| **"ये छोटी-सी छींक तो bonus थी"** | *"bonus क्या होता है?"* — both kids. The word is not known. Cut it |
| **The meow** | still did not land even with the new sound. Needs rethinking, not just re-generating |
| Teddy's snore / "खर्र्र… biscuit…" | confirmed again |
| **"मेरा horn भी तुमसे सुर सीख रहा है"** | both kids |
| "टोपी से हवा" and the line after it | |
| The exercise line | |
| Engine start | "can be better" |
| **तुम doctor कब बने?** | *filed here provisionally — there is no doctor line in Toy Town, so this is probably Jungle Rescue's first-aid scene. Confirm.* |
| Overall | kid 2: **"the story itself is not catchy"** |

### Sound

- **Fan SFX weak or absent** — both kids. Loudest single complaint
- Train entering Toy Town station — SFX not good
- Water break needs more volume and a better SFX
- Engine start could be clearer

### Pacing and bugs

- **Long pause after "Toy Town, हम आ रहे हैं! छुक-छुक… चलो!"** — unexplained, needs investigating
- **Long pause after "Robot की battery रुक गई!"** (DANCE_F2)
- **Still too much gap between the music starting and the dancing**
- **A kid switched away mid-story and it did not resume** — this is the parked
  interrupt guard, and it cost a real session. See `TASKS.md` T14
- Neither kid danced the first time; one danced later

### Structure

- **The kid did not realise he was the Captain.** Confirms the opening rewrite
  — he has to be *asked*, not told
- **The card ask comes too late.** The moment light is mentioned the kid picks
  up the LIGHT card and then waits. Name the need and ask for the card in the
  same breath
- **The ending must be strong** — it is what he remembers. Appreciation plus a
  joke
- **Too many cards.** Stick to a small, easily recognisable set
- **Card images could be better**

### Ideas worth building

- **Water break honesty check.** If the WATER card is tapped instantly, say
  "अरे! तुम गए ही नहीं! पहले जाकर पानी पियो, फिर आना." Once only — if they still
  do not go, let it be
