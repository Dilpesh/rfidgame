# Under-5 review — the checks a machine can't run

`check.py` measures levels, masking, lengths, forbidden words and the clock.
This is the rest: read the script (`stories/<slug>/story.txt`) with a specific
four-year-old in mind, before any clip is generated and again before a child
hears it. Paste this file and the script into any AI thread and ask for the
review; it is written to be answered puzzle by puzzle.

## For every ask (card)

1. **Is the concept lived?** Has this child physically done the thing the card
   stands for — drunk water, felt a blanket, switched on a torch? If not
   (petrol into a car), does the story *teach it in one sentence before asking*,
   with a body metaphor (Jeep का पेट खाली है)? An untaught invisible concept fails.
2. **Is the ask recognition, not recall?** "Find the पेट्रोल" is recognition;
   "what should we put in?" is a riddle. Under-5s recognise far better than they
   recall. The first ask of the story must be recognition — the child has won
   nothing yet.
3. **Is the word the child's word?** Hold up the card and ask "ये क्या है?" —
   whatever they say is the word Coco uses everywhere (prompt, last hint, praise,
   the printed label). `say=` on the card line should match it.
4. **Does the last hint describe the picture?** Colour and shape of what is on
   the card ("लाल pump, pipe लगा है", "सफ़ेद डब्बा, लाल plus"), so a child who
   didn't follow the words can still match the picture.
5. **Is the praise formula complete?** Name the card, name the child (or
   Captain), say what changed: "YES! पेट्रोल! Jeep का पेट भर गया!" then a name
   line.

## For every joke

6. **Can a four-year-old *see* it?** A physical event (Coco falls in the mud,
   grabs a tail in the dark, the elephant inhales a biscuit) lands. Cut on sight:
   an adult concession ("fair point"), a wink at hidden intent, a running gag
   that needs the child to remember an earlier scene, wordplay, sarcasm.
7. **Does the child need to know Coco misunderstood?** Literal-minded
   four-year-olds take "मैं ढूँढता हूँ आपकी पूँछ" as a real lost tail. If the
   joke depends on spotting a misunderstanding, make it physical instead.
8. **Then stop talking.** After an instruction ("पहले पानी पियो, फिर card"), no
   tail clause, no wink. Say it, stop.

## For the whole story

9. **Something must land every 30 seconds** — a joke, an effect, praise or an
   action. `check.py` warns on the clock; you judge whether what lands is
   actually felt.
10. **Nothing longer than a minute before an ask.** Long narration is where
    they wander off. Move the ask earlier and put the reward after it.
11. **Actions first, card second.** Tell them to do the thing, then bring the
    card once it's done, so nobody is rushed.
12. **The name every minute**, only in independent lines, never mid-sentence;
    everything to the child gender-neutral. (`check.py` enforces; you check it
    still sounds like Coco.)
13. **Language register.** Hinglish the child hears at home; English words only
    the ones they already own (card, biscuit, music, torch). No idioms unless
    the kids have laughed at one.
14. **The printed card and the spoken word agree.** If the script now says
    दवाई का डब्बा and the card prints दवा पेटी, one of them changes.

## Report format

Per card, worst first: verdict (fails / word only / watch / safe), the issue in
one line, the fix as the exact replacement line(s). Then jokes, then pacing.
End with what needs new audio and what is a script-only change. Nothing in the
repo is changed by a review.
