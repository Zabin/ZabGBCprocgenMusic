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

## 7. Addendum — 2026-07-26: VRAM/ROM Budget for Visual Evolution (`BL-0034`, hardware half)

Closes the remaining half of `BL-0034` (Visual Evolution) — [R222](R222-visual-evolution-conventions.md)
(design half, `02-research-game-design`) recommends extending Driftune's existing 2-entry palette
table (`CALM_PALETTE`/`BAD_PALETTE`) with more swap-only theme palettes rather than adding new
tile art. This addendum grounds what that actually costs, using this project's own established
budget-instrumentation method (`ADR-0002`: `rom.pos` read directly from a `build_rom.build()` run).

**Palette-table ROM cost is negligible against measured headroom.** Each existing palette table is
4 colors × 2 bytes (`rgb15()`, §3 above) = **8 bytes**; two tables (`CALM_PALETTE`/`BAD_PALETTE`)
cost 16 bytes total in the current ROM. Measured total ROM usage after all 12 shipped R1-R4
packages: **3419/32768 bytes (10.4%), 29349 bytes free** (`ADR-0002`). Adding, say, 6 more 8-byte
theme palettes (day/night/seasonal/holiday, per R222 §5's own recommendation) costs **48 bytes** —
under 0.2% of the *free* headroom, not the total budget. This is not close to a constraint by any
measure.

**Tile-budget headroom is even less of a constraint.** `visuals.py` currently defines exactly 2
tiles (`TILE_OFF`/`TILE_ON`, `visuals.py:23-24`), each the standard 2bpp 16-byte format (R303) —
32 bytes of tile pixel data written into VRAM at boot. CGB's unsigned tile-addressing mode
(`LCDC` bit 4 = 1, already how Driftune configures it, `visuals.py:72`) supports 256 tile indices
per VRAM bank at `0x8000`-`0x8FFF`/`0x9000`-`0x97FF` (4096 bytes of tile-data capacity per bank,
2 banks = 8192 bytes total VRAM tile-data space) [Pan Docs — Tile
Data](https://gbdev.io/pandocs/Tile_Data.html) (already cited above). Driftune uses 2 of 256
possible tile slots in bank 0 alone — R222's own "palette-only, no new tiles" recommendation means
this headroom isn't even needed for the visual-evolution feature itself, but confirms it would be
available if a future increment wanted new tile art too.

**The one genuine new-mechanism cost is *simultaneous* per-tile palette variety, not swap-only
theming — and R222's design already avoids needing it.** §5 above already established that using
more than BG palette 0 requires (1) writing to `BCPS`/`BCPD` at a non-zero palette-select offset
and (2) writing a VRAM-bank-1 tilemap attribute byte per tile that should use a non-zero palette,
which in turn requires `VBK` (`0xFF4F`) bank switching — "a new mechanism this project's code has
never exercised" (§5). R222's recommended design (swap all of BG palette 0's contents for a new
theme, the same mechanism `_emit_write_palette` already uses for calm/bad-zone) deliberately never
needs this — every theme still writes to palette-0 exclusively, sequentially replacing its
contents, exactly like the shipped calm/bad-zone swap already does. **This is the key finding**:
visual evolution as R222 scoped it is a pure ROM-data-table extension (negligible cost, no new
mechanism); only a *future* design wanting several palettes active on-screen *at once* (not just
swapped over time) would need the genuinely new VRAM-bank/tilemap-attribute mechanism this
addendum flags as real, non-trivial work.

### Addendum sources
- [Pan Docs — Tile Data](https://gbdev.io/pandocs/Tile_Data.html) (tile-data VRAM capacity,
  already cited §3 above)
- Project-internal: `ADR-0002` (docs/architecture/adr/) — the `rom.pos`-instrumentation ROM-budget
  measurement method and its result (10.4% used, 29349 bytes free) this addendum reuses directly;
  `visuals.py` (current tile/palette definitions, read directly, not cited externally).

## 8. Implementation Guidance (addendum)
- **A future visual-evolution package should add palette tables only** (more 8-byte `rgb15()`
  arrays, following `CALM_PALETTE`/`BAD_PALETTE`'s exact pattern) and a selection index (an
  existing engine parameter or R221's future valence-arousal derivation) choosing which table
  `_emit_write_palette` writes — no new tiles, no `VBK` bank switching, no tilemap attribute
  bytes. This is the cheapest-possible implementation path and the one R222 already recommends.
- **Do not reach for BG palettes 1-7 / VRAM bank 1 / `VBK` switching for visual evolution** unless
  a future design genuinely needs multiple palettes rendering *simultaneously* on different tiles
  (e.g. per-channel-color-coded tiles) — that is real, ungrounded-until-then new-mechanism work,
  correctly out of scope for the swap-only theming R222 recommends.
- **Re-measure ROM budget the same way** (`rom.pos` post-build, per `ADR-0002`) before and after
  any future visual-evolution package ships, to keep the budget-tracking discipline this project
  has now established for cart-shape decisions consistent across all future content additions.

## 7. Related Topics
R102 (VRAM/palette access-timing window this must write within), R103 (`LCDC`, the sibling boot
config), R208 (palette/color design conventions — still `⛔ Planned`, a design-taste topic
distinct from this one's register-protocol grounding).
