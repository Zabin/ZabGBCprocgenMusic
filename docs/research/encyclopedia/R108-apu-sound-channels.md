# R108 — APU Channels & Register Map

- **Tier:** R100 (GBC hardware/SM83) · **Owned by:** `02-research-gbc-hardware`
- **Status:** ✅ Authored 2026-07-21 · **Supersedes:** `docs/research/R100-gbc-sound-hardware.md`
  (retained as a superseded pointer, not deleted)

## 1. Purpose

Driftune's entire product is real-time PSG generation — this is the single most load-bearing
hardware topic in the project. Every register write `music_engine.py` makes must be correct, and
every "what's the engine doing" read the visualizer or a test performs must respect what the APU
actually allows to be read back.

## 2. Scope

The four-channel PSG (DMG/CGB — CGB adds no new channels, only double-speed CPU mode, out of
scope for v1): pulse A (with sweep), pulse B, wave, noise; the mixing/power registers; the
frequency-register encoding; and what's read-only vs. write-only.

## 3. Concepts

- **Channel 1 (Pulse A):** `NR10` (`0xFF10`) sweep, `NR11` (`0xFF11`) duty+length,
  `NR12` (`0xFF12`) volume envelope, `NR13`/`NR14` (`0xFF13`/`0xFF14`) frequency+trigger.
  **Channel 2 (Pulse B)** is identical minus sweep: `NR21`-`NR24` (`0xFF16`-`0xFF19`).
- **Channel 3 (Wave):** `NR30` (`0xFF1A`) DAC power, `NR31` (`0xFF1B`) length (8-bit, longer than
  the pulse channels' 6-bit), `NR32` (`0xFF1C`) output level (`00` mute/`01` 100%/`10` 50%/`11`
  25%, no envelope), `NR33`/`NR34` frequency+trigger, and 16 bytes of **Wave RAM**
  (`0xFF30`-`0xFF3F`, 32 4-bit samples) — live-rewritable while the channel plays, Driftune's
  timbre lever for this channel.
- **Channel 4 (Noise):** `NR41` (`0xFF20`) length, `NR42` (`0xFF21`) envelope, `NR43` (`0xFF22`)
  clock shift/LFSR width/divisor, `NR44` (`0xFF23`) trigger. No pitch register — width bit
  (15-bit "hiss" vs. 7-bit "metallic") is the audible timbre switch.
- **Global:** `NR50` (`0xFF24`) master L/R volume, `NR51` (`0xFF25`) per-channel L/R panning
  enable, `NR52` (`0xFF26`) master power (bit 7) + **per-channel active status** (bits 0-3,
  read-only, auto-clears when a channel's length timer expires) [gbdev.io/pandocs/Audio_Registers.html](https://gbdev.io/pandocs/Audio_Registers.html).
- **Frequency encoding** (channels 1/2/3): `register = round(2048 - 131072/hz)` for ch1/2,
  `round(2048 - 65536/hz)` for ch3 (one octave lower per register value) — an 11-bit value split
  across the low byte and the low 3 bits of the high byte, with bit 7 of the high byte the
  trigger. [gbdev.io/pandocs/Audio_details.html](https://gbdev.io/pandocs/Audio_details.html)

### Sources
- [Pan Docs — Audio Registers](https://gbdev.io/pandocs/Audio_Registers.html)
- [Pan Docs — Audio Details](https://gbdev.io/pandocs/Audio_details.html)
- [gbdev.gg8.se — Sound Controller](https://gbdev.gg8.se/wiki/articles/Sound_Controller)

## 4. Operational Context

**Confirmed empirically during `IP-0001`** (PyBoy 2.7.0, `sound_emulated=True`): `NR13`/`NR23`/
`NR33` (frequency low byte) and the frequency-high bits of `NR14`/`NR24`/`NR34` are **write-only**
— reading them back does not return the last-written value. Only `NR52`'s per-channel active
bits and a channel's own readable control bits (e.g. length-enable) are meaningfully readable.
This matches Pan Docs' framing of `NR52` as the status register and the frequency registers as
control-only — Driftune's own empirical test (`test_rom.py` T3, see `IP-0001`'s package doc)
independently reproduces this, so it is doubly confirmed rather than taken from documentation
alone.

## 5. Implementation Guidance

- **`music_engine.py` must treat the WRAM engine-state mirror (GDS-07) as the only readable
  source of "what note/parameter is active"** — never attempt to read `NR13`/`NR14`/etc. back for
  this purpose; this is already how `engine_tick`/`test_rom.py` are built (confirmed, not a
  change).
- **`NR52` is the correct signal for "is this channel making sound right now"** for both the
  visualizer (GDS-08, pending) and `test_rom.py` — already the pattern in use.
- **Channel 3's Wave RAM being live-rewritable** is the concrete mechanism for a future timbre
  parameter (`IP-0002`): swapping in a different 32-sample waveform table addresses MSTR-001 C7
  ("all four channels used") for the wave channel beyond just pitch, without new registers.
- **Channel 4 has no pitch register** — `IP-0003`'s noise-channel design must drive it purely via
  `NR43`'s clock/width/divisor and `NR42`'s envelope/length, gated by Euclidean onset timing
  (R202), not via any frequency table lookup (there is none to look up).

## 6. Feature Mapping

FR-1010 (register writes for all four channels), GDS-03 SS1/SS2 (module layout, main loop),
GDS-07 (WRAM mirror rationale), `IP-0002`/`IP-0003` (pulse B/wave/noise generation, not yet
authored).


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED — the project's most load-bearing topic.** Grounds every PSG register write in `music_engine.py` and `build_rom.py`'s sound init: `NR10`-`NR52` layout, the four channels' control/frequency/envelope semantics, and the write-only frequency registers that are the direct reason GDS-07's WRAM state mirror exists as a first-class design artifact. Requirements: `FR-1000`/`FR-1010`. Tested across `T2`/`T3`/`T6`/`T7`/`T12`.

## 7. Related Topics

R110 (interrupt-driven tick timing that gates when these registers get written), R204 (bad-zone
dissonance scoring reads the WRAM mirror this topic establishes as authoritative, not these
registers), R207 (chiptune channel-role conventions for how pulse/wave/noise are typically used).
