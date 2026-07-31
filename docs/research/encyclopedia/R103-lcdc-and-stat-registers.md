# R103 — LCDC/STAT Registers

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (deferred pending `IP-0006`, now shipped and `VERIFIED`)

## 1. Purpose
Ground `visuals.py`'s single `LCDC` write (`init_visuals`, `LCDC=0x91`) against the register's
real bit layout, and record why `STAT` is unused by this project.

## 2. Scope
`LCDC` (`0xFF40`, LCD Control) and `STAT` (`0xFF41`, LCD Status).

## 3. Concepts
`LCDC` bit-by-bit: bit7 LCD/PPU enable, bit6 window tilemap area select (`9800`/`9C00`), bit5
window enable, bit4 BG/window tile-data area select (`8800` signed / `8000` unsigned addressing),
bit3 BG tilemap area select, bit2 OBJ size (8x8/8x16), bit1 OBJ enable, bit0 (DMG: BG/window
enable; **CGB: BG/window priority** — a CGB-specific reinterpretation, not a simple on/off).
[Pan Docs — LCD Control](https://gbdev.io/pandocs/LCDC.html). `STAT` (`0xFF41`): bits 0-1 report
the current PPU mode (0-3, read-only), bit 2 is the LYC=LY coincidence flag, bits 3-6 are
per-source STAT-interrupt enables (HBlank/VBlank/OAM/LYC), bit 7 is unused. A documented DMG
hardware quirk causes the STAT interrupt to sometimes fire spuriously when writing to `STAT`
during OAM scan/HBlank/VBlank or on an LY=LYC match — a CGB-in-CGB-mode consideration this
project doesn't need to work around since it never uses STAT interrupts at all. [Pan Docs — LCD
Status Registers](https://gbdev.io/pandocs/STAT.html).

### Sources
- [Pan Docs — LCD Control](https://gbdev.io/pandocs/LCDC.html)
- [Pan Docs — LCD Status Registers](https://gbdev.io/pandocs/STAT.html)

## 4. Operational Context
`visuals.py:72` writes `LCDC = 0x91` = `1001_0001`: bit7 (LCD on) + bit4 (BG tile data at `0x8000`,
unsigned addressing — matching `VRAM_TILE_DATA = 0x8000` and `TILE_OFF=0`/`TILE_ON=1`'s use as
direct unsigned tile indices) + bit0 (BG/window enable — CGB bit0's "priority" reinterpretation is
irrelevant here since no BG-priority-vs-OBJ conflict exists, Driftune has no sprites, `R105`).
Bits 1-3/5-6 all clear: no OBJs, no window layer — both correctly unused, since the visualizer is
BG-tilemap-only. `test_rom.py` T9.1 independently confirms this exact byte value
(`LCDC & 0xFF == 0x91`) at boot. `STAT` is never written or read anywhere in the tree — confirmed
by grep across `music_engine.py`/`build_rom.py`/`visuals.py`/`input_map.py` — consistent with the
project using only the VBlank interrupt (`IE` bit0, `R110`), never a STAT-sourced interrupt.

## 5. Implementation Guidance
**No change needed.** If a future package ever wants the window layer (bit5) or OBJs (bit1/bit2)
— e.g. a more elaborate visualizer per `BL-0001`'s still-pending GDS-08 — `LCDC`'s existing
`0x91` base value composes cleanly with those additional bits (`OR` them in, don't replace the
whole byte, to avoid accidentally reintroducing the CGB bit0 priority ambiguity). `STAT`-based
interrupts (mode-3-entry, LYC) are a reasonable future upgrade **only** if a package needs
mid-scanline timing precision `R102`'s VBlank-window budget can't provide — not needed for
anything currently planned.

## 6. Feature Mapping
FR-1120 (visualizer boot init), `test_rom.py` T9.1.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `visuals.py`'s shipped `LCDC = 0x91` configuration (LCD on, BG tile data at `0x8000` unsigned addressing, BG display on) in `build_visuals_init_asm`, asserted by `test_rom.py` `T9.1`.

## 7. Related Topics
R102 (PPU mode timing `STAT`'s mode bits report), R104 (CGB palette, the other half of the
visualizer's boot config), R105 (OBJs — why bit1/bit2 stay clear), R110 (interrupt model — why
`STAT` interrupts are unused).
