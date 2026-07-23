# R102 — PPU Modes, VBlank & VRAM/OAM Access Timing

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (deferred pending `IP-0006`'s visualizer landing — now shipped and independently `VERIFIED`,
  `VR-0006` — this topic grounds its already-shipped VBlank-gating design)

## 1. Purpose
Ground `visuals.py`'s VRAM/tilemap/palette write timing against the real PPU access-timing
contract — confirming the already-shipped design (writes issued from the main loop right after
waking from `HALT` on the VBlank interrupt) is genuinely safe, not merely accidentally so.

## 2. Scope
The PPU's four per-scanline modes and when VRAM/OAM/CGB-palette registers are CPU-writable.

## 3. Concepts
The PPU cycles through four modes per scanline: **Mode 2 (OAM scan)**, **Mode 3 (pixel
transfer/"HDraw")**, **Mode 0 (HBlank)**, repeating for 144 visible lines, then **Mode 1
(VBlank)** for 10 scanlines' worth of time before the next frame starts. During Mode 2, OAM is
locked to the CPU; during Mode 3, both VRAM and OAM are locked (CPU writes are ignored, reads
return undefined data, typically `$FF`). VRAM becomes CPU-writable during Mode 0 (HBlank) and
Mode 1 (VBlank); OAM becomes writable during Mode 0 and Mode 1 as well. [Pan Docs — Accessing VRAM
and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html). CGB palette registers (`BCPS`/
`BCPD`, see `R104`) follow the same VRAM-class access restriction — they are part of the PPU's
color-RAM path, not directly CPU-RAM, so writing them outside HBlank/VBlank risks the same
ignored-write hazard.

### Sources
- [Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html)
- [Pan Docs — OAM](https://gbdev.io/pandocs/OAM.html)
- [mgba-emu gbdoc — Open Game Boy Documentation Project](https://mgba-emu.github.io/gbdoc/) (cross-reference for mode-timing figures)

## 4. Operational Context
`build_rom.py`'s `main_loop` (`build_rom.py:75-85`) `HALT`s the CPU until the VBlank interrupt
sets `VBLANK_FLAG` (the ISR at `0x0040`, GDS-07 §8), then runs `engine_tick`/`update_visuals`
synchronously in the same wake — meaning every VRAM/tilemap write (`visuals.py:61-73`'s
`init_visuals` tile-data/tilemap setup at boot) and every per-frame write
(`visuals.py:76-103`'s `update_visuals` tilemap-cell and `BCPS`/`BCPD` palette writes) executes
at the very start of the VBlank window — the one period where both VRAM and the CGB palette
registers are guaranteed CPU-accessible for the whole ~10-scanline duration. `10-integration-review`'s
Foundation-bucket report already confirmed this pattern is correct by inspection (see
`docs/reviews/integration-review-foundation-bucket.md`, Dimension 2); this topic supplies the
hardware citation that inspection was implicitly relying on.

## 5. Implementation Guidance
**No change needed.** `visuals.py`'s `update_visuals` must continue to be called only from the
VBlank-gated `main_loop` path (never from an arbitrary point mid-frame) — if a future package
ever adds a second call site for VRAM/palette writes (e.g. a mid-frame effect), it must either
also be VBlank-gated or explicitly justify writing during Mode 0 HBlank (much narrower window,
~200 T-states per scanline, insufficient for `update_visuals`'s current ~40-byte palette write
budget spread across two 8-color writes). **Do not** move any VRAM/tilemap/palette write earlier
in the frame than the post-`HALT` wake point — that is the one invariant this topic exists to
protect.

## 6. Feature Mapping
FR-1120 (visualizer, read-only + correctly-timed writes), NFR-1010 (per-frame budget — the VBlank
window's actual duration is part of that budget), GDS-07 §8 (`VBLANK_FLAG` synchronization
mechanism).

## 7. Related Topics
R103 (`LCDC`/`STAT`, the registers that report/configure PPU mode), R104 (CGB palette registers,
subject to the same access-timing rule), R110 (interrupt model — the VBlank ISR itself), R308
(performance budgeting).
