THE GREAT BANANA RESCUE — Production V2

Run:
- Serve this folder from your static web server and open index.html.
- Audio is fully local; no ElevenLabs API or expiring URLs are required.

Modes:
1. Card Reader Mode (default / production)
   - Developer controls and typed UID input are hidden.
   - Keyboard-wedge RFID readers are supported: the reader types the UID and sends Enter.
   - Programmatic integrations can call: window.scanCard(uid)

2. Developer Mode
   - Click the "Developer Mode" button at the top-right, OR press Ctrl/Command + Shift + D.
   - Shows typed UID input, test card IDs, and Jump to Scene controls.
   - The selected mode is remembered in localStorage.

Programmatic mode controls:
- window.setBananaRescueMode('reader')
- window.setBananaRescueMode('developer')
- window.getBananaRescueMode()

Current temporary test UIDs:
1001 Moon
1002 Torch
1003 Banana
1004 Rope
1005 Ladder
1006 Jump
1007 Clap
1008 Laugh
1009 Dance
1010 Water
1011 Party Horn

Before physical RFID deployment:
- Replace the temporary IDs in the `ids` object in index.html with the actual card UIDs.
- If your reader is not keyboard-emulating, call window.scanCard(uid) from your reader bridge.

Final Review Mode has been removed from this production build.


PRODUCTION V3 — TEACH CARDS
---------------------------
Modes:
- Card Reader Mode: normal child gameplay.
- Teach Cards Mode: click Teach Cards, choose the logical card, then scan the physical RFID card. Mapping is stored in browser localStorage.
- Developer Mode: manual test IDs and scene jumping.

Teach Cards data is browser/device-local. Clearing browser site data will remove learned UIDs.
Existing developer IDs 1001-1011 continue to work for testing.
