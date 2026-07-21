# memory.md — Runtime Notes & Debug Log

## Current Build Status

`IP-0001` scope only: pulse A channel generation, full input mapping, scoped Select reset,
headless verification bootstrap. ROM builds at exactly 32768 bytes; **32/32 `test_rom.py`
checks pass** (headless PyBoy 2.7.0, repo-relative paths — `python3 build_rom.py <out.gbc>` then
`python3 test_rom.py` from the repo root).

### Last verified working (PyBoy 2.7.0 headless test, 2026-07-21)

- Boot → sound hardware init → pulse A generating within ~90 frames (GBC boot-ROM logo time)
- Scale-constrained LFSR-driven random walk on pulse A (major scale, `TEMPO_IDX=4`,
  `OCTAVE_IDX=1` preset)
- All 6 input controls edit exactly their own parameter index, edge-triggered
- Select resets tested indices + pulse A state to preset, unconditionally

## WRAM Quick Reference (authoritative table: GDS-07)

| Range | Content |
|---|---|
| `0xC000`-`0xC004` | `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` |
| `0xC005`-`0xC00B` | Bad-zone state (flags/scores/counters) — **not yet implemented, IP-0004** |
| `0xC00C`-`0xC00F` | Per-channel note timers (pulse A live; B/wave/noise reserved) |
| `0xC010`-`0xC012` | Per-channel current scale-degree (pulse A live; B/wave reserved) |
| `0xC013`-`0xC015` | Per-channel history ring-buffer heads — **not yet implemented, IP-0004** |
| `0xC016` | `LFSR_STATE` |
| `0xC020`-`0xC037` | Per-channel history ring buffers — **not yet implemented, IP-0004** |
| `0xC050`-`0xC052` | `JOY_PREV`/`JOY_CUR`/`JOY_NEW` |
| `0xC060` | `VBLANK_FLAG` |

## Joypad Bit Map (JOY_CUR/JOY_NEW — active HIGH)

Reused verbatim from the reference project's own convention:
```
bit 0 = A        bit 4 = RIGHT
bit 1 = B        bit 5 = LEFT
bit 2 = SELECT   bit 6 = UP
bit 3 = START    bit 7 = DOWN
```

## Sound register quick reference

`NR52` (`0xFF26`) bit 7 = master power, bit 0 = channel-1(pulse A)-active — the only reliably
readable "is audio happening" signal (see `docs/research/R100-gbc-sound-hardware.md`'s
"Confirmed during IP-0001" section: `NR13`/`NR14`'s frequency bits are **write-only**, do not
attempt to read them back in a test or from the future visualizer — read the WRAM mirror instead).

## Emulator Test Command

```python
from pyboy import PyBoy
pb = PyBoy('Driftune.gbc', window='null', sound_emulated=True)   # repo-relative
pb.set_emulation_speed(0)
```

`test_rom.py` derives `ROM_PATH` repo-relative from its own location, builds the ROM itself
(`build_rom()` helper), and deletes the built ROM at the end of a run — no manual cleanup needed.
**Boot takes ~90 frames** before cartridge code starts running (GBC boot-ROM logo animation) —
`test_rom.py`'s `BOOT_FRAMES` constant encodes this; any new test reading boot-time state must
wait at least that long first (discovered the hard way during `IP-0001` — see its own package doc).
