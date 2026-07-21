# memory.md — Runtime Notes & Debug Log

## Current Build Status

MVP (Foundation release bucket, `IP-0001`-`IP-0007`): 4-channel generative engine (pulse A/B,
wave-as-bass, Euclidean-gated noise), full input mapping, bad-zone detection with **autonomous
avoidance/recovery** (no input required) + full-state Select reset-and-randomize, minimal
tile/palette visualizer. ROM builds at exactly 32768 bytes; **60/60 `test_rom.py` checks pass**
(headless PyBoy 2.7.0, repo-relative paths — `python3 build_rom.py <out.gbc>` then
`python3 test_rom.py` from the repo root). 8000+ frame stress run with continuous input churn:
no hangs, bad-zone entry and self-recovery both observed.

### Last verified working (PyBoy 2.7.0 headless test, 2026-07-21)

- Boot → sound hardware init (all 4 channels) → visualizer init (LCD on) within ~90 frames
- Pulse A/B independent scale-constrained LFSR walks (different seeds, decorrelated); wave
  channel same mechanism, anchored an octave lower + half note-rate (bass role)
- Noise channel: 16-step Euclidean pattern sized by `DENSITY_IDX`, gates short percussive hits
- Bad-zone: `DISSONANCE_SCORE` recomputed every frame from 3 pitched-channel pairs; `STALE_COUNT_*`
  per channel; rolling onset-window overload counter; combined into `BAD_ZONE_FLAGS` bit3
- Autonomous recovery (IP-0007): dissonant → next step pulled toward tonic; stuck → step forced;
  overloaded → note-timer reload doubled again — all without input, confirmed self-healing over a
  4000+ frame run (`test_rom.py` T10)
- All 6 input controls edit exactly their own parameter index, edge-triggered; `DENSITY_IDX`
  measurably changes noise-onset rate end to end
- Select resets every channel + all bad-zone counters to preset, unconditionally, same-frame, AND
  reseeds each channel's LFSR from `DIV` (0xFF04) XORed with a per-channel constant (zero-seed
  guarded) — "reset and randomize," not the same fixed sequence every press
- Visualizer: 4 tiles track `NR52`'s per-channel active bits; palette swaps calm/bad-zone colors

## WRAM Quick Reference (authoritative table: GDS-07 + IP-0002/0003/0004 addenda)

| Range | Content |
|---|---|
| `0xC000`-`0xC004` | `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` (`CHMIX_IDX` wired, not yet consumed) |
| `0xC005` | `BAD_ZONE_FLAGS` (bit0 DISSONANT, bit1 STUCK, bit2 OVERLOAD, bit3 COMBINED) |
| `0xC006` | `DISSONANCE_SCORE` |
| `0xC007`-`0xC009` | `STALE_COUNT_PA`/`PB`/`WV` |
| `0xC00A`/`0xC00B` | `ONSET_WINDOW_COUNT` / `ONSET_WINDOW_TICK_CTR` |
| `0xC00C`-`0xC00F` | `NOTE_TIMER_PA`/`PB`/`WV`/`NZ` |
| `0xC010`-`0xC012` | `CUR_DEGREE_PA`/`PB`/`WV` |
| `0xC016`-`0xC018` | `LFSR_STATE` (PA) / `LFSR_STATE_PB` / `LFSR_STATE_WV` |
| `0xC019` | `NOISE_STEP_IDX` (0-15) |
| `0xC01A`-`0xC01C` | `SEMI_PA`/`PB`/`WV` (dissonance-tick scratch, not persisted meaning across frames) |
| `0xC050`-`0xC052` | `JOY_PREV`/`JOY_CUR`/`JOY_NEW` |
| `0xC060` | `VBLANK_FLAG` |

Unused/reserved from GDS-07 but not yet consumed: `0xC013`-`0xC015` (history ring-buffer heads —
superseded by the simpler period-1-only `STALE_COUNT_*` design, see `IP-0004`'s package doc),
`0xC020`-`0xC037` (ring buffers — same).

## Joypad Bit Map (JOY_CUR/JOY_NEW — active HIGH)

Reused verbatim from the reference project's own convention:
```
bit 0 = A        bit 4 = RIGHT
bit 1 = B        bit 5 = LEFT
bit 2 = SELECT   bit 6 = UP
bit 3 = START    bit 7 = DOWN
```

## Sound register quick reference

`NR52` (`0xFF26`) bits 0-3 = channel 1-4 active — the only reliably readable "is audio happening"
signal (frequency registers are write-only, confirmed empirically — see
`docs/research/encyclopedia/R108-apu-sound-channels.md`). Noise channel has no frequency register
at all (R108/R115) — only onset timing is generative for it.

## Visualizer quick reference

`LCDC` (`0xFF40`) = `0x91` (LCD on, BG tile data at `0x8000`, BG display on). 4 tile-indicator
cells at `0x9800`-`0x9803` (BG tilemap top-left), one per channel, tile 0 = off / tile 1 = on.
BG palette 0 swaps between calm (blue/green) and bad-zone (red) color sets via `BCPS`/`BCPD`
every frame based on `BAD_ZONE_FLAGS` bit3.

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
wait at least that long first.
