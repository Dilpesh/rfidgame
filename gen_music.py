#!/usr/bin/env python3
"""Procedurally generate a gentle, loopable ambient background bed for a
kids' scavenger-hunt game: a soft sustained pad chord under a slow,
warm pentatonic marimba-style arpeggio. No external assets/licensing
concerns - fully synthesized.
"""
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SR = 24000
LOOP_SECONDS = 8.0
N = int(SR * LOOP_SECONDS)

t = np.linspace(0, LOOP_SECONDS, N, endpoint=False)


def note_freq(semitones_from_c4):
    return 261.63 * (2 ** (semitones_from_c4 / 12))


def adsr(n_samples, sr, attack, decay, sustain_level, release, hold):
    total = n_samples
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    h = max(total - a - d - r, 0)
    env = np.concatenate([
        np.linspace(0, 1, max(a, 1)),
        np.linspace(1, sustain_level, max(d, 1)),
        np.full(h, sustain_level),
        np.linspace(sustain_level, 0, max(r, 1)),
    ])
    if len(env) < total:
        env = np.pad(env, (0, total - len(env)))
    else:
        env = env[:total]
    return env


def soft_tone(freq, n_samples, sr, detune_cents=6):
    tt = np.arange(n_samples) / sr
    d = 2 ** (detune_cents / 1200)
    wave = (
        np.sin(2 * np.pi * freq * tt)
        + 0.6 * np.sin(2 * np.pi * freq * d * tt)
        + 0.6 * np.sin(2 * np.pi * freq / d * tt)
    )
    return wave / 2.2


def pluck_tone(freq, n_samples, sr):
    tt = np.arange(n_samples) / sr
    # triangle-ish via odd harmonics for a soft marimba/glockenspiel color
    wave = (
        np.sin(2 * np.pi * freq * tt)
        + 0.35 * np.sin(2 * np.pi * freq * 3 * tt)
        + 0.15 * np.sin(2 * np.pi * freq * 5 * tt)
    )
    return wave / 1.5


# ---- pad: sustained C major triad (C4, E4, G4), whole 8s loop, gentle swell ----
pad = np.zeros(N)
for semis in (0, 4, 7, 12):  # C E G C(oct)
    freq = note_freq(semis)
    tone = soft_tone(freq, N, SR)
    pad += tone
pad_env = adsr(N, SR, attack=1.6, decay=0.6, sustain_level=0.85, release=1.6, hold=True)
pad = pad * pad_env
pad = pad / np.max(np.abs(pad)) * 0.5

# ---- pluck arpeggio: gentle pentatonic pattern over the 8s loop ----
# C major pentatonic relative semitones: C D E G A (0,2,4,7,9), plus octave
pattern_semis = [0, 4, 7, 11 - 12 + 12, 9, 7, 4, 0]  # C E G B(oct-ish)->use A instead below
pattern_semis = [0, 4, 7, 12, 9, 7, 4, 2]  # C E G C A G E D  (pentatonic-flavored, resolves home)
n_notes = len(pattern_semis)
note_dur = LOOP_SECONDS / n_notes

left = np.zeros(N)
right = np.zeros(N)
for i, semis in enumerate(pattern_semis):
    start = int(i * note_dur * SR)
    dur_samples = int(note_dur * SR * 1.35)  # slight overlap/ring for warmth
    dur_samples = min(dur_samples, N - start)
    freq = note_freq(semis)
    tone = pluck_tone(freq, dur_samples, SR)
    env = adsr(dur_samples, SR, attack=0.01, decay=0.25, sustain_level=0.0, release=note_dur * 1.1, hold=False)
    voice = tone * env * 0.5
    pan = 0.5 + 0.35 * np.sin(2 * np.pi * i / n_notes)  # gentle stereo movement
    left[start:start + dur_samples] += voice * (1 - pan)
    right[start:start + dur_samples] += voice * pan

mix_l = left + pad
mix_r = right + pad
peak = max(np.max(np.abs(mix_l)), np.max(np.abs(mix_r)), 1e-9)
target_peak = 0.65
mix_l = mix_l / peak * target_peak
mix_r = mix_r / peak * target_peak

# equal-power crossfade of the loop seam so the repeat is click-free
xf = int(0.35 * SR)
fade_in = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2
fade_out = np.cos(np.linspace(0, np.pi / 2, xf)) ** 2
for ch in (mix_l, mix_r):
    tail = ch[-xf:].copy()
    head = ch[:xf].copy()
    ch[:xf] = head * fade_in + tail * fade_out
    ch[-xf:] = ch[:xf]  # mirror so end matches new start exactly -> seamless loop

stereo = np.stack([mix_l, mix_r], axis=1)
stereo_i16 = np.clip(stereo * 32767, -32768, 32767).astype(np.int16)

import wave
out_wav = os.path.join(BASE, "audio", "bg_loop.wav")
with wave.open(out_wav, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(stereo_i16.tobytes())

print("wrote", out_wav, os.path.getsize(out_wav), "bytes")
