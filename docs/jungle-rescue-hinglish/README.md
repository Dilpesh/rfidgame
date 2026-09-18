# Jungle Rescue — deployment build

## Deploy
Unzip this package and upload index.html to the root of any static web host. No build command, backend, environment variables, or ElevenLabs API key is needed. If your host asks for a publish directory, select the folder containing index.html.

You can also open index.html directly in a browser for a local preview. Click Start Game to enable audio, and keep the device volume on.

## Included
- All 85 audio cues embedded in index.html; playback makes no ElevenLabs requests and spends no credits.
- Full rescue story and touch-card controls.
- Water reminders with increasing intervals (30 seconds, 60 seconds, then 120 seconds).
- A minute of dance music with freeze breaks.
- Next Step control to skip ahead, and Reset to restart.

## RFID cards
A keyboard-wedge RFID reader can send a card UID followed by Enter. Use Teach Cards to map your physical cards. Card mappings are saved in this browser for this site; teach them again when moving from a local preview to a deployed domain or using another browser/device.

## Quick deployment check
Open the deployed URL, click Start Game, and confirm the intro is audible. Tap Fuel to advance to the elephant rescue. Check Next Step and Reset. The single HTML file is about 17 MB because it contains the audio; the first load may take a moment on slower connections.
