# R100 — GBC Sound Hardware Encyclopedia

> **Superseded 2026-07-21** — split into per-topic files with citations under
> `docs/research/encyclopedia/`: [R107](encyclopedia/R107-joypad-input.md) (joypad, not originally
> covered here), [R108](encyclopedia/R108-apu-sound-channels.md) (this file's own APU content,
> re-grounded), [R109](encyclopedia/R109-cartridge-header.md) (header, not originally covered
> here), [R110](encyclopedia/R110-interrupts-and-timing.md) (interrupts, not originally covered
> here). Retained verbatim below, not deleted, per the pipeline's relocate-don't-delete discipline.

- **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored, 2026-07-21 (grounds GDS-01/03/07)
- **Grounds:** GDS-03 (channel-assignment architecture, input-mapping register targets),
  GDS-07 (WRAM mirror of engine state), the verification harness (register addresses to assert on).

Driftune's core hardware surface is the GBC's four-channel PSG (the DMG/CGB audio processing
unit, unchanged between the two — CGB adds no new channels, only the double-speed CPU mode,
which is out of scope for v1). All register addresses below are I/O-mapped at `0xFF10`–`0xFF3F`
and directly readable/writable in PyBoy as `pb.memory[addr]`, exactly like the reference
project's LCDC read at `test_rom.py:316` — confirmed against that project's own harness, not
assumed.

## Channel 1 — Pulse A (with frequency sweep)

| Reg | Addr | Bits | Purpose |
|---|---|---|---|
| NR10 | `0xFF10` | `-PPP NSSS` | Sweep period (`PPP`), direction (`N`: 0=up,1=down), shift (`SSS`) |
| NR11 | `0xFF11` | `DDLL LLLL` | Duty (`DD`: 12.5/25/50/75%), length load (`LLLLLL`, write-only) |
| NR12 | `0xFF12` | `VVVV APPP` | Initial volume (`VVVV`), envelope direction (`A`), envelope period (`PPP`) |
| NR13 | `0xFF13` | `FFFF FFFF` | Frequency low 8 bits |
| NR14 | `0xFF14` | `TL-- -FFF` | Trigger (`T`, write 1 to restart), length-enable (`L`), frequency high 3 bits |

## Channel 2 — Pulse B (identical to Channel 1, no sweep)

| Reg | Addr | Purpose |
|---|---|---|
| NR21 | `0xFF16` | Duty + length load |
| NR22 | `0xFF17` | Volume envelope |
| NR23 | `0xFF18` | Frequency low |
| NR24 | `0xFF19` | Trigger / length-enable / frequency high |

## Channel 3 — Wave (arbitrary 4-bit waveform)

| Reg | Addr | Purpose |
|---|---|---|
| NR30 | `0xFF1A` | Bit 7: DAC power (channel on/off at the DAC level, distinct from NR52's status bit) |
| NR31 | `0xFF1B` | Length load (write-only, 8-bit — longer than the pulse channels' 6-bit) |
| NR32 | `0xFF1C` | Output level: `00`=mute, `01`=100%, `10`=50%, `11`=25% (no envelope; static level only) |
| NR33/NR34 | `0xFF1D`/`0xFF1E` | Frequency low / trigger+length-enable+frequency high (same shape as ch1/2) |
| Wave RAM | `0xFF30`–`0xFF3F` | 16 bytes = 32 4-bit samples, played in order at a rate derived from the frequency register; **rewritable live** while the channel plays, the standard trick for wavetable-style timbre changes |

Wave RAM being live-rewritable is Driftune's main timbral lever for Channel 3 — the generator can
swap in a different 32-sample waveform (a handful of precomputed shapes: sine-ish, saw-ish,
square-ish, a noisy/gritty one) as a "timbre" parameter, distinct from Channels 1/2's duty-cycle
only options.

## Channel 4 — Noise (LFSR-driven, no fixed pitch)

| Reg | Addr | Bits | Purpose |
|---|---|---|---|
| NR41 | `0xFF20` | `--LL LLLL` | Length load |
| NR42 | `0xFF21` | `VVVV APPP` | Volume envelope, same shape as ch1/2 |
| NR43 | `0xFF22` | `SSSS WDDD` | Clock shift (`SSSS`), LFSR width (`W`: 0=15-bit/hiss, 1=7-bit/metallic), clock divisor (`DDD`) |
| NR44 | `0xFF23` | `TL-- ----` | Trigger, length-enable |

No frequency register in the pitched sense — NR43's shift/divisor set the LFSR clock rate, and
the width bit is a genuinely audible timbre switch (metallic vs. hiss), which is a natural,
cheap, discrete "parameter" for a generator to flip rather than something needing interpolation.

## Global control registers

| Reg | Addr | Bits | Purpose |
|---|---|---|---|
| NR50 | `0xFF24` | `VVVN NNNN` | Vin-panning bits (unused here) + left/right master volume (0–7 each) |
| NR51 | `0xFF25` | `4321 4321` | Per-channel left/right panning enable — **this is where "which channels are active" and stereo placement both live**; a channel with both bits clear is silent regardless of its own registers |
| NR52 | `0xFF26` | `P--- 4321` | Bit 7: master power (must be set before any channel writes take effect); bits 0-3 (read-only): each channel's own "currently playing" status, auto-clears when a channel's length timer expires |

**NR52's per-channel status bits are the single most useful thing for both the visualizer and the
test harness**: they report live "is this channel making sound right now" without the reader
needing to track envelope/length state itself. GDS-08 (visualizer) should read `NR52` (and
`NR51` for panning) directly as its primary "what's active" signal, and the test harness should
assert on it the same way.

## Frequency register math

For channels 1, 2, and 3, the same encoding applies (reference project's `music.py:freq()` is
this exact formula, reused as-is):

```
register_value = round(2048 - 131072 / hz)     # channels 1/2
register_value = round(2048 - 65536  / hz)     # channel 3 (one octave lower for the same register value)
```

`register_value` is an 11-bit quantity split across the low byte (`NR13`/`NR23`/`NR33`) and the
low 3 bits of the high byte (`NR14`/`NR24`/`NR34`), with bit 7 of the high byte as the trigger
bit. This project's engine works in the same "register value" domain the reference project's
`freq()` produces, not raw Hz, to keep pitch generation and quantization-to-scale arithmetic cheap
(integer register deltas, not floating point on SM83).

## Cycle-budget considerations for real-time generation (grounds GDS-06 NFRs)

The reference project's ISR-driven per-frame budget (VBlank + a fixed-length main loop, ~59.7Hz)
is the same budget Driftune's generation routine must fit inside, alongside the existing
per-frame work (joypad poll, visualizer tile/palette writes). Generation logic that runs **every
frame** (deciding "does anything change this tick") should be cheap (a handful of table lookups
and comparisons); the actual "pick the next note" computation only needs to run when a channel's
current note/duration actually expires, which is far less often than once per frame at any
musically sensible tempo (a quarter note at 120 BPM is ~30 frames) — this asymmetry is what makes
real-time on-device generation tractable on SM83 at all, and should be named explicitly as a
design constraint at GDS-03/GDS-06 rather than discovered as a performance bug later.

## Confirmed during `IP-0001` implementation (empirical corrections to this document)

- **`NR13`/`NR23`/`NR33` (frequency low byte) and the frequency-high bits of `NR14`/`NR24`/`NR34`
  are write-only** — reading them back (via `pb.memory[addr]` in PyBoy 2.7.0, matching real GBC
  hardware behavior) does **not** return the last-written value; only `NR52`'s per-channel active
  bits and a channel's readable control bits (e.g. `NR14` bit 6, length-enable) are meaningfully
  readable. **This confirms GDS-00/GDS-07's own rationale for a WRAM engine-state mirror** — it
  is not redundant with the PSG registers, it is the *only* place a test (or the visualizer) can
  read "what note/parameter is currently active" from. Any future test design must assert via the
  WRAM mirror for pitch/parameter state and via `NR52` only for channel-active/on-off state —
  never via frequency-register readback.
- `pb.memory[addr]` reads hardware I/O registers correctly with `sound_emulated=True`
  (PyBoy 2.7.0) — confirmed by `NR52`'s active-channel bits responding correctly; the previously
  open question about `sound_emulated` is resolved, no further action needed.

## Open items for later research passes

- Whether the noise channel's LFSR width bit is audible enough at short lengths to serve as a
  reliable "channel personality" parameter, or needs a minimum-duration floor — a
  `08-content-authoring`/`09-content-review`-stage listening judgment call, not resolvable from
  hardware docs alone.
