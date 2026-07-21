# Driftune — Developer Guide

## Development pipeline (read this first for any non-trivial change)

This project is driven by a documentation-driven-development skill pipeline, harvested and
adapted from a separate reference project — see [`.claude/skills/README.md`](.claude/skills/README.md)
(stages, iteration loops, hard rules G1–G5) and
[`docs/pipeline/pipeline-journal.md`](docs/pipeline/pipeline-journal.md)/[`backlog.md`](docs/pipeline/backlog.md)
for where things stand. The default entry point is the `00-pipeline-manager` skill ("run the
pipeline skill"); new features/bugs enter via `00-intake`, never by side-channel edits.

## Architecture Overview

Each file has ONE job. Edit only what you need.

```
gbc_lib.py       — ROM class (assembler opcodes) + color math + header writing (reused verbatim
                    from the reference project — nothing game/music-specific lives here)
music_engine.py  — all sound-channel generation logic, preset/table data, PSG register writes
input_map.py     — joypad edge detection + the input->parameter mapping (never writes PSG regs)
build_rom.py     — master build: imports all modules, lays out ROM sections, patches pointers
test_rom.py      — headless PyBoy verification harness (drives button sequences, asserts on
                    sound registers + WRAM engine state)
```

Planned, not yet written: `visuals.py` (tile/palette animation reacting to engine state — IP-0006).

### Data layout, WRAM map

Authoritative source: [`docs/architecture/07-data-model.md`](docs/architecture/07-data-model.md)
(GDS-07). Quick orientation only: parameter indices at `0xC000`-`0xC004` (tempo/octave/scale/
density/channel-mix), bad-zone state at `0xC005`-`0xC00B` (not yet implemented — IP-0004),
per-channel generation state at `0xC00C`+, joypad state at `0xC050`-`0xC052`, `LFSR_STATE` at
`0xC016`, `VBLANK_FLAG` at `0xC060`. **No SRAM** — this project makes no save/battery commitment
(MSTR-001 C2).

### Input mapping (GDS-03 SS3)

| Input | Parameter |
|---|---|
| D-pad Up/Down | Tempo step +/- |
| D-pad Right/Left | Octave step +/- |
| A | Next scale/mode |
| B | Next density preset |
| Start | Next channel-mix preset |
| Select | Reset to known-good preset (unconditional) |

All edge-triggered (rising edge only — holding does not repeat).

## How to Change Things

### Tune a preset table or threshold
Edit the relevant table in `music_engine.py` (`TEMPO_BPM`, `OCTAVE_ROOT_HZ`, `SCALE_SEMITONES`,
`DELTA_TABLE`, the `PRESET_*` constants) — no other file needs to change; `build_rom.py`
regenerates everything from these tables at build time.

### Add a new scale/mode
Add an entry to `SCALE_SEMITONES` and `SCALES` in `music_engine.py` (exactly 8 semitone-offset
entries, extending into the next octave past each scale's own unique pitch count, per GDS-03
SS3's "always 8 degrees" convention) — `SCALE_IDX`'s wrap mask (`0x03` today, 4 scales) must be
widened if the list grows past a power-of-two boundary; check `input_map.py`'s `_step_on_bit`
call for `SCALE_IDX`.

### Add a new sound channel's generation (pulse B / wave / noise)
See `music_engine.py`'s `engine_tick` for the pulse-A pattern (countdown → LFSR delta → table
lookup → register write → timer reload) — the next package (`IP-0002`) extends this same shape to
pulse B and the wave channel with their own `NOTE_TIMER_*`/`CUR_DEGREE_*` WRAM fields (already
reserved in GDS-07).

## Known Good Behavior (IP-0001 — self-tested, not yet independently verified)

- ROM builds to exactly 32768 bytes, valid GBC header, cart type ROM-only (no battery)
- Boots, powers on sound hardware, pulse A channel active and audibly generating within ~90
  frames (GBC boot-ROM logo animation time — confirmed empirically, see `test_rom.py`'s
  `BOOT_FRAMES`)
- Pulse A performs a scale-constrained random walk (major scale, mid octave/tempo preset by
  default), producing varying notes over time
- All 6 input controls (D-pad x4, A, B, Start) edit exactly their own parameter index, edge-
  triggered, wrapping correctly
- Select unconditionally resets tested parameters + pulse A's own state to the known-good preset

32/32 `test_rom.py` checks pass. See `docs/implementation/packages/IP-0001-...md` for exact scope
and what's explicitly not built yet (pulse B/wave/noise, bad-zone detection, visualizer).

## Known Issues

None currently reproducing. See [`docs/pipeline/backlog.md`](docs/pipeline/backlog.md) for the
live list of open items (nothing here is a stale snapshot).
