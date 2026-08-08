# R114 — Wave Channel Programming

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 1, item 9 ("Wave channel programming"); Phase 5,
  item 58 ("Wave channel sample creation")

## 1. Purpose
Concrete implementation guidance for `IP-0002`'s wave channel, beyond R108's register-map-level
description — this is the "how to actually program it" companion.

## 2. Scope
Wave RAM layout/format, DAC power sequencing, and the live-rewrite technique for timbre.

## 3. Concepts
- **Wave RAM** (`0xFF30`-`0xFF3F`, 16 bytes) holds 32 4-bit samples, **two samples packed per
  byte** (high nibble played first) [Pan Docs — Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html).
  A full cycle of the waveform plays once per "frequency period," so pitch and timbre are
  independently controllable: frequency (`NR33`/`NR34`) sets how fast the 32-sample cycle repeats,
  Wave RAM's contents set what shape it repeats.
- **DAC power** (`NR30` bit 7) must be on for the channel to produce any output at all — distinct
  from `NR52`'s own master/channel-active bits (R108 SS3).
- **Output level** (`NR32`) is a static 0/100/50/25% attenuation, no envelope — unlike the pulse/
  noise channels, volume shaping for the wave channel must come from Wave RAM's own sample values
  (e.g. a naturally-decaying waveform shape) or from switching between precomputed waveform tables
  of different apparent loudness, not from an envelope register.
- **Precomputed waveform shapes** are the standard technique (this project's R108 SS5 already
  names it): a handful of 16-byte tables (e.g. a near-sine shape, a near-square/pulse-like shape
  for contrast with the two real pulse channels, a sawtooth-ish shape, a deliberately noisy/gritty
  shape) stored in ROM, one DMA'd/copied into Wave RAM when the wave-channel "timbre" parameter
  changes.

### Sources
- [Pan Docs — Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html)
- [Pan Docs — Audio Details](https://gbdev.io/pandocs/Audio_details.html)

## 4. Operational Context
Not yet implemented (`IP-0002`).

## 5. Implementation Guidance
- **Give the wave channel a bass/timbre role, not a copy of pulse B's melody** — per R207's own
  finding (`BL-0008`): anchor its octave lower, and/or slow its note-timer, distinct from pulse
  A/B's home range.
- **Concrete data plan**: 3-4 precomputed 16-byte Wave RAM tables in ROM (e.g. `WAVE_SINE`,
  `WAVE_PULSE25`, `WAVE_SAW`), a `TIMBRE_IDX` WRAM byte (new field, not yet in GDS-07 — a
  candidate addition for `IP-0002`'s own GDS-07 addendum), copied into `0xFF30`-`0xFF3F` via a
  16-byte `memcpy`-style loop whenever it changes (cheap — happens only on a parameter change, not
  every tick, same "expensive only on change" discipline R108/R110 already establish).
- **DAC must be powered (`NR30` bit 7 = 1) before the channel can be heard** — `IP-0002`'s init
  sequence must set this once, analogous to `IP-0001`'s pulse-A `NR12` boot-time write.

## 6. Feature Mapping
`IP-0002` (wave channel, not yet authored).


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `music_engine.py`'s `_wave_table_bytes()` and the Wave RAM copy in `build_rom.py`'s init, plus the wave channel's one-octave-lower frequency formula that gives the bass voice its register placement (`IP-0002`). Requirement: `FR-1010`. Domain role recorded in [GDS-04 §2](../../architecture/04-domain-model.md).

## 7. Related Topics
R108 (register map), R111 (retrigger-corruption erratum, confirmed not applicable to CGB), R207
(the bass-role recommendation this topic assumes).
