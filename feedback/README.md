# Feedback, one file per story

After a session with the kids, open the file for the story you played and add
bullets. The exact moment ("the meow", "after the water instruction") and what
you saw them **do** — not what you thought of it. Working out whether it is a
level problem, a script problem or a code problem is Claude's job.

One file per game folder in `docs/`, created the first time there is something
to record:

```
feedback/toy-town.md               Chuku & the Toy Town Express
feedback/toy-town-v2.md            the retuned copy running beside it
feedback/jungle-rescue-hinglish.md Jungle Rescue Patrol
```

Not written yet, because nothing has been noticed about them: `moon`,
`banana-rescue`, `jungle-rescue`, `find-and-tap`.

Status on each item: **open** · **fixed** · **needs new audio** · **won't fix**
(with a reason).

## The rule that makes this worth doing

When something noticed in one story turns out to be true of **every** story, it
gets promoted into `STORY_CRAFT.md` and the story file keeps only the specific
instance. That is how the acknowledgement formula got there — it was noticed in
Jungle Rescue, found missing in Toy Town, and is now a rule for everything we
write next.

Three standing documents, and what belongs in each:

| file | what goes in it |
|---|---|
| `STORY_CRAFT.md` | how to **write** a story — jokes, acknowledgement, pacing, the first minute |
| `AUDIO_STANDARD.md` | how the audio must **measure** — levels, beds, ffmpeg chains |
| `LEARNINGS.md` | how the code must **behave** — wake lock, scan guard, interruptions |
