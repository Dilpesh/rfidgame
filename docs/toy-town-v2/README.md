# Chuku — Toy Town Express

A Hinglish audio adventure using six cards: KEY, LIGHT, FAN, WATER, MUSIC, BISCUIT.

## Deploy
Upload the complete contents of this folder to any static host. Keep `index.html`, JavaScript, CSS, and `audio/` together. No build command, backend, API key, or runtime ElevenLabs access is required. All audio generation is a one-time production step; playing the game spends no generation credits.

For a direct local preview, use the separately supplied standalone HTML, which embeds all files and audio. The folder version uses fetch to load MP3s and should be served over HTTP(S), rather than opened with a file:// URL.

## Play
Click Start Game to enable browser audio. Listen, think, then tap an on-screen card or present a taught RFID card. The route is key → light → fan → music → dance → water → Teddy → switch-off memory game → finale.

Music runs for three 20-second rounds, with freeze breaks. Water reminders wait 30 seconds, then 60 seconds, then 120 seconds between reminders. The final puzzle accepts either switch first and waits 10 seconds before hinting about whatever remains on.

Pause freezes audio and timers. Returning from another tab requires Resume. Next Step skips the current step and stops its audio/hints. Reset returns to the beginning. These controls do not erase your card mappings.

## RFID
Open Grown-up controls, select Teach for a card, and scan its UID followed by Enter. Teach all six cards. Mapping lives in this browser for this site, so a new deployed domain/device may need teaching again. A UID may map to one card only. The game also exposes `window.scanCard(uid)` for hardware integrations.

## Audio and script
Voices: Jia (Narrator), Munni (Chuku), Vardan (Driver), Bholu (Teddy). All dialogue uses the approved kid character casting. MP3 filenames match script cue IDs. The recording manifest lists speaker, emotion, and dialogue; the production script contains SFX, pauses, music, and hint directions.

Use ordinary device volume controls and the in-game volume slider. No microphone, camera, or child personal information is required.

## Rebuild locally without AI credits

From the project folder, run `python3 local_rebuild.py`. It runs the game tests, verifies every MP3, and recreates the standalone HTML and both ZIP files. This deterministic rebuild does not contact OpenAI or ElevenLabs and consumes no credits.
