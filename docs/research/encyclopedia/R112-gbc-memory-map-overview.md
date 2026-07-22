# R112 — GBC Hardware Architecture Overview / Memory Map & Banking

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (was deferred as "no gap yet — single 32KB bank, no MBC in use"; still true, authored now as an
  orientation topic tying R101/R106/R107-R115 together rather than staying an index-only stub)

## 1. Purpose
Give one orientation-level map of the full `0x0000`-`0xFFFF` address space Driftune's code
touches, cross-linking to the detailed topics that ground each region, so a new agent doesn't
have to reconstruct the whole-address-space picture from seven separate topic files.

## 2. Scope
The full 16-bit address space as this specific ROM (32KB, no MBC, no CGB WRAM/VRAM banking in
use) actually occupies it — not a general survey of every possible cartridge configuration.

## 3. Concepts
`0x0000`-`0x7FFF` (32KB): ROM, entirely fixed (no bank switching — cart type `0x00`, `R106`) —
Driftune's whole program plus data tables lives here, laid out sequentially by `build_rom.py`.
`0x8000`-`0x9FFF` (8KB): VRAM — tile data + BG tilemap, bank 0 only (Driftune never touches
`VBK`/`0xFF4F` to switch to VRAM bank 1, `R104`). `0xA000`-`0xBFFF`: cartridge RAM window — entirely
unused (no MBC/SRAM, `R106`). `0xC000`-`0xDFFF` (8KB): Work RAM (WRAM), bank 0 only in this
project (CGB's switchable-bank-1-7 WRAM feature is unused) — this is where every engine-state
byte GDS-07 documents lives (`0xC000`-`0xC01C` engine/bad-zone/generation state, `0xC050`-`0xC052`
joypad state, `0xC060` `VBLANK_FLAG`). `0xFE00`-`0xFE9F`: OAM, unused (`R105`, no sprites).
`0xFF00`-`0xFF7F`: I/O registers — `P1`/`JOYP` (`R107`), the four APU channel register blocks
(`R108`), `LCDC`/`STAT` (`R103`), `BCPS`/`BCPD` (`R104`), `DIV` (`R213`'s reseed source), `IE`.
`0xFF80`-`0xFFFE`: HRAM — unused (no OAM DMA routine needed, `R105`). [Pan Docs — Memory
Map](https://gbdev.io/pandocs/Memory_Map.html).

### Sources
- [Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html)

## 4. Operational Context
Every address constant across `music_engine.py`/`input_map.py`/`visuals.py`/`build_rom.py` falls
inside one of the regions above; `10-integration-review`'s Foundation-bucket report (Dimension 2)
independently confirmed no WRAM address collisions and that GDS-07's own reserved-but-unused
ring-buffer range (`0xC013`-`0xC015`, `0xC020`-`0xC037`, tracked `BL-0013`) and the six addresses
GDS-07 doesn't yet document (`BL-0018`) both stay within the WRAM region as expected — nothing in
either finding involves a region *boundary* violation, only intra-WRAM documentation gaps.

## 5. Implementation Guidance
**No change needed** for the current single-bank, no-MBC design (`R101`/`R106` already cover why).
This topic's actual utility is as a map for evaluating *future* scope changes: (1) if `BL-0020`'s
multi-scheme architecture work needs meaningfully more ROM-resident data (new scheme tables,
per-scheme presets) and threatens to exceed 32KB, this is the topic to revisit first — bank
switching would require picking an MBC (`R106`) and reworking `build_rom.py`'s single-bank layout
assumption; (2) if a future package wants CGB WRAM bank 1 (for more scratch state than the current
`0xC000`-`0xC060` block leaves room for) or VRAM bank 1 (for CGB tile attributes, `R104`), both
require writing `SVBK`/`VBK` respectively — neither register is referenced anywhere in the tree
today.

## 6. Feature Mapping
GDS-07 (the WRAM map this topic's §3 orients against), MSTR-001 C2 (32KB/no-MBC scope
commitment).

## 7. Related Topics
R101 (instruction/cycle costs — irrelevant to banking but the sibling "no gap yet, simple design"
topic), R104 (VRAM banking), R105 (OAM — unused region), R106 (MBC/SRAM — the banking mechanism
itself), R107/R108/R110 (the I/O-region registers this project actually uses), R109 (cartridge
header, the ROM/RAM-size bytes that would change if banking were ever adopted).
