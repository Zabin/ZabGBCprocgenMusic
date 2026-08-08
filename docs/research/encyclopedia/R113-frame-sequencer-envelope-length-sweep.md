# R113 — Frame Sequencer: Envelope, Length Counter & Sweep Timing

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 1, items 11 ("Hardware envelopes"), 12
  ("Frequency sweep"), 13 ("Length counters")

## 1. Purpose
Ground precise envelope/length/sweep timing, which `IP-0001` sets once at boot (a static
envelope on pulse A) but does not yet vary — needed before any package makes envelope/length
itself a generative parameter.

## 2. Scope
The internal **frame sequencer** that clocks all three sub-units, and each sub-unit's own rate.

## 3. Concepts
- A **frame sequencer**, internal to the APU, steps every 8192 T-cycles (512 Hz) and, depending
  on which of its 8 steps it's on, clocks the length counter, envelope, and/or sweep units
  [gbdev.gg8.se — Gameboy sound hardware](https://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware).
- **Length counter**: ticks at 256 Hz (every other frame-sequencer step: 0, 2, 4, 6) when enabled
  (`NR14`/`NR24`/`NR34`/`NR44` bit 6) — this is what makes `NR52`'s per-channel active bit
  auto-clear on its own, already the mechanism R108 SS4 relies on for "is this channel active."
- **Volume envelope**: ticked internally at 64 Hz; the actual volume step happens every N of
  those ticks, where N is the envelope's own configured period (`NR12`/`NR22`/`NR42` low 3 bits) —
  a period of 0 disables the envelope entirely (static volume, `IP-0001`'s current pulse-A
  configuration: period 3, decreasing).
- **Sweep** (pulse A only): also clocked from specific frame-sequencer steps, shifts the
  frequency register by a configurable amount at a configurable period — `IP-0001` disables sweep
  entirely (`NR10 = 0x80`, sweep period 0).
- **Per-channel processing order** (signal flow): Square 1 is Sweep → Timer → Duty → Length →
  Envelope → Mixer; Square 2 skips Sweep; Wave is Timer → Wave → Length → (static) Volume →
  Mixer; Noise is Timer → LFSR → Length → Envelope → Mixer [gbdev.gg8.se, same source].

### Sources
- [gbdev.gg8.se — Gameboy sound hardware](https://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware)
- [Pan Docs — Audio Details](https://gbdev.io/pandocs/Audio_details.html)
- [NightShade's Blog — Game Boy Sound Emulation](https://nightshade256.github.io/2021/03/27/gb-sound-emulation.html)

## 4. Operational Context
`music_engine.py`'s `NR12` write (`0xF3` = volume 15, decreasing envelope, period 3) is a one-time
boot-time constant, never varied — this topic's timing facts aren't yet load-bearing on shipped
code, but will be the moment envelope shape becomes a generative/steerable parameter.

## 5. Implementation Guidance
- **If a future package wants a per-note "pluck" envelope feel to vary** (e.g. as a texture
  parameter alongside `CHMIX_IDX`), it can simply write a different `NR12`/`NR22`/`NR42` value
  per note-onset — no new mechanism needed, this is a data change on an already-existing write
  path.
- **The auto-clearing length-counter mechanism (256 Hz) means a note automatically stops sounding
  after its length expires, unless length is disabled** (`NR14` bit 6 = 0, `IP-0001`'s current
  choice via not setting length data — every trigger effectively free-runs). Any future change to
  actually set a length value must account for this auto-stop, or a note could silently cut off
  mid-generation if the engine assumes it plays until the next `engine_tick`-driven retrigger.

## 6. Feature Mapping
Not yet consumed — informs any future envelope/sweep-as-parameter feature (no `IP-xxxx` yet).


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds the envelope/duty register values `build_rom.py`'s sound init writes (`NR12`/`NR22` `0xF3`, `NR42`'s fast-decay percussion envelope) and the frame-sequencer timing discipline `music_engine.py`'s per-note writes must respect. Requirements: `FR-1010`/`FR-1170`. Named as a standing constraint in [GDS-06 §2](../../architecture/06-non-functional-requirements.md).

## 7. Related Topics
R108 (register map these units live inside), R110 (the VBlank-frame cadence vs. this internal
512Hz frame-sequencer cadence — two independent clocks in the same system, not to be confused).
