# R104 — CGB Palette System (BCPS/BCPD, RGB15)

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (deferred pending `IP-0006`, now shipped and `VERIFIED`)

## 1. Purpose
Ground `visuals.py`'s `_emit_write_palette` routine and `rgb15()` color-packing helper
(`gbc_lib.py`) against the real CGB palette-RAM write protocol.

## 2. Scope
`BCPS`/`BGPI` (`0xFF68`) and `BCPD`/`BGPD` (`0xFF69`) — background palette index/data registers.
Sprite-palette registers (`OCPS`/`OCPD`, `0xFF6A`/`0xFF6B`) are out of scope — Driftune has no
sprites (`R105`).

## 3. Concepts
CGB colors are packed **RGB555**: bits 0-4 red, bits 5-9 green, bits 10-14 blue, each a 5-bit
(0-31) intensity, bit 15 unused. [Pan Docs — Palettes](https://gbdev.io/pandocs/Palettes.html).
The CGB provides 8 BG palettes (0-7) of 4 colors each, addressed indirectly through `BCPS`: bit7
sets auto-increment mode (address advances after every `BCPD` write), bits 0-5 select the target
byte (palette×8 + color×2 + hi/lo-byte) within the 64-byte BG palette RAM, and each color is
written as two sequential `BCPD` bytes (low byte then high byte) at that auto-incrementing
address. Which of the 8 BG palettes a given background tile actually uses is selected per-tile via
the CGB tilemap attribute byte in VRAM bank 1 (bits 0-2) — a tile with no explicit attribute byte
written defaults to palette 0.

### Sources
- [Pan Docs — Palettes](https://gbdev.io/pandocs/Palettes.html)
- [Pan Docs — Tile Data](https://gbdev.io/pandocs/Tile_Data.html) (cross-reference for the VRAM-bank-1 attribute-byte mechanism)

## 4. Operational Context
`gbc_lib.py`'s `rgb15(r, g, b)` (`gbc_lib.py:6-7`) packs exactly this format:
`(r & 0x1F) | ((g & 0x1F) << 5) | ((b & 0x1F) << 10)` — confirmed correct against the bit layout
above. `visuals.py`'s `_emit_write_palette` (`visuals.py:47-51`) writes `BCPS = 0x80` (bit7
auto-increment set, address 0 — BG palette 0, color 0, low byte) once, then loops each color's low
byte then high byte to `BCPD`, relying on auto-increment to advance through all 4 colors —
matching the documented protocol exactly. `visuals.py` never writes a tilemap attribute byte
(VRAM bank 1) anywhere, which is correct *because* it only ever targets BG palette 0
(`CALM_PALETTE`/`BAD_PALETTE`, both written to the same palette-0 address range) — every tile
therefore uses the CGB's own default-to-palette-0 behavior with no attribute write needed. This
was independently verified live during `IP-0006`'s `VR-0006`: driving the ROM to a
`BAD_ZONE_FLAGS`-bit3 transition and sampling rendered pixels confirmed the palette does swap
correctly (once the expected one-frame VBlank write-takes-effect-next-frame lag, `R102`, is
accounted for).

## 5. Implementation Guidance
**No change needed** for the current single-BG-palette design. If a future visualizer package
(per `BL-0001`'s pending GDS-08, or `BL-0020`'s new multi-scheme architecture question) wants
per-tile palette variety (e.g. a distinct palette per generation scheme or per channel), it must
(1) write to BG palettes 1-7 (change `BCPS`'s low 6 bits, not just relying on the `0x80`
auto-increment-from-0 pattern `_emit_write_palette` currently hardcodes) and (2) write the
corresponding tilemap attribute byte in VRAM bank 1 for each tile that should use a non-zero
palette — VRAM bank switching (`0xFF4F`, `VBK`) is itself a new mechanism this project's code
has never exercised and would need its own grounding pass before use.

## 6. Feature Mapping
FR-1120 (visualizer bad-zone-reactive palette), GDS-03 §6 (visualizer palette design intent),
`test_rom.py` (no direct `BCPD`-readback test exists — palette correctness is confirmed via
rendered-pixel sampling in `VR-0006`, not a WRAM-style assertion, since palette RAM isn't
practically readable back the way WRAM is).

## 7. Related Topics
R102 (VRAM/palette access-timing window this must write within), R103 (`LCDC`, the sibling boot
config), R208 (palette/color design conventions — still `⛔ Planned`, a design-taste topic
distinct from this one's register-protocol grounding).
