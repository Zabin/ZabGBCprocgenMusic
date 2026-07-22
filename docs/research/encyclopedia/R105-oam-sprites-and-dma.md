# R105 — OAM, Sprites & OAM DMA

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (kept brief — Driftune has no sprites and none are planned; see §5)

## 1. Purpose
Record why this topic stays out of scope, with real citations, rather than leaving a bare
`⛔ Planned` row — so a future agent evaluating whether to add OBJs has the actual hardware
contract in front of them instead of re-deriving it.

## 2. Scope
OAM (Object Attribute Memory, `0xFE00`-`0xFE9F`, 40 4-byte sprite entries) and the OAM DMA
transfer mechanism (`0xFF46`).

## 3. Concepts
Each OAM entry is Y position, X position, tile index, and an attribute byte (priority, Y/X flip,
DMG palette select, and — CGB-only — VRAM bank + one of 8 OBJ palettes). Writing `0xFF46` with a
source-address high byte launches a DMA transfer copying `0x9F` bytes from `XX00`-`XX9F` (ROM or
RAM) to OAM (`0xFE00`-`0xFE9F`); the transfer takes 160 microseconds (80 in CGB double-speed)
during which the CPU can access only HRAM (`0xFF80`-`0xFFFE`) — any routine that triggers the DMA
must either busy-wait from HRAM or otherwise ensure nothing outside HRAM executes during the
window. [Pan Docs — OAM](https://gbdev.io/pandocs/OAM.html); [Pan Docs — OAM DMA
Transfer](https://gbdev.io/pandocs/OAM_DMA_Transfer.html).

### Sources
- [Pan Docs — OAM](https://gbdev.io/pandocs/OAM.html)
- [Pan Docs — OAM DMA Transfer](https://gbdev.io/pandocs/OAM_DMA_Transfer.html)

## 4. Operational Context
Driftune's visualizer (`visuals.py`) is entirely BG-tilemap-based — 4 fixed BG cells + a palette
swap, per `R103`'s confirmation that `LCDC` bits 1-2 (OBJ enable/size) stay clear. `OAM`/`0xFF46`
are never referenced anywhere in the tree (confirmed by grep across `music_engine.py`/
`build_rom.py`/`visuals.py`/`input_map.py`).

## 5. Implementation Guidance
**No sprites are planned for this project** — GDS-03's visualizer design (tile/palette reacting
to `NR52`/bad-zone state, R205) and MSTR-001's own scope commitments never call for moving,
independently-animated objects; the BG-tilemap approach already covers the four-channel-indicator
concept cleanly. **If a future package does want sprites** (e.g. a more elaborate visualizer, an
`FS-xxx` explicitly proposing OBJ-based animation): (1) the OAM DMA routine must run from a
callable placed in the low `0xFF80`-`0xFFFE` HRAM region — `build_rom.py` has no HRAM-resident
code today and would need one added; (2) the DMA must be triggered from the same VBlank-gated
window `R102` establishes for VRAM writes, since OAM has the identical access-timing restriction;
(3) this topic should be revisited and expanded with real per-attribute-byte guidance once that
package is scoped — this entry is deliberately not exhaustive given there is currently nothing to
implement against.

## 6. Feature Mapping
None currently — no FR/NFR references sprites or OAM.

## 7. Related Topics
R102 (VRAM/OAM access-timing rule OAM DMA shares), R103 (`LCDC` OBJ-enable bits), R110 (interrupt
model — HRAM-only execution during DMA has implications for ISR design if ever combined).
