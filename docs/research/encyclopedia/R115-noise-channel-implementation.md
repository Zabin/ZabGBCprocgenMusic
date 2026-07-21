# R115 — Noise Channel Implementation

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 1, item 10 ("Noise channel implementation");
  Phase 5, item 59 ("Noise channel percussion")

## 1. Purpose
Concrete implementation guidance for `IP-0003`'s noise channel, beyond R108's register-map
description.

## 2. Scope
LFSR clock/width/divisor programming and percussion-role sound design.

## 3. Concepts
- `NR43`'s three fields — clock shift (`SSSS`), LFSR width (`W`), clock divisor (`DDD`) — jointly
  set the noise channel's internal LFSR clock rate; there is no pitch register, only this rate and
  the width mode [Pan Docs — Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html).
- **Width mode** (`W` bit): 0 = 15-bit LFSR (longer period, "hiss"-like, more natural-sounding
  noise), 1 = 7-bit LFSR (short period, repeats faster, reads as more "metallic"/tonal). This is
  the channel's only real timbre axis (R108 SS3) — a genuinely discrete, audible switch rather
  than something needing interpolation.
- **Conventional role**: percussion — chiptune composition convention (R207) uses the noise
  channel for drum-like hits, not sustained tones; "static... formed into bursts" standing in for
  drums/impacts is the standard framing [GB Studio Central — Tracker Lesson 1](https://gbstudiocentral.com/tips/gb-studio-tracker-lesson-1-terminology-and-basics-of-the-game-boy-sound-chip/).

### Sources
- [Pan Docs — Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html)
- [GB Studio Central — Tracker Lesson 1](https://gbstudiocentral.com/tips/gb-studio-tracker-lesson-1-terminology-and-basics-of-the-game-boy-sound-chip/)

## 4. Operational Context
Not yet implemented (`IP-0003`).

## 5. Implementation Guidance
- **Gate noise-channel onsets off the Euclidean bit pattern R202 recommends for `DENSITY_IDX`** —
  each `1` bit in the pattern triggers a short noise hit (`NR44` trigger), each `0` bit is silence,
  consistent with GDS-03 SS3's "Euclidean-gated noise hits" framing.
- **Use a short envelope with fast decay** (`NR42`, decreasing, short period) for a percussive
  "hit" feel rather than a sustained noise drone — matches the percussion-role convention above.
- **7-bit width mode is the better default** for a rhythmic/percussive role (shorter, more
  clearly-pitched-feeling repeats read as more "drum-like" than the longer 15-bit hiss mode,
  which reads more as ambient texture) — a concrete, testable starting choice for `IP-0003`'s FS,
  not a final tuning decision (still subject to `BL-0005`'s deferred listening pass).

## 6. Feature Mapping
`IP-0003` (noise channel, not yet authored), R202 (Euclidean density this topic's onset gating
depends on).

## 7. Related Topics
R108 (register map), R202 (density/rhythm generation), R204 (channel-overload scoring includes
noise-channel onset events).
