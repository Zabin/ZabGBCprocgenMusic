# R303 — 2bpp Tile Encoding & Palette Data Formats

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored
  2026-07-22 (deferred pending `IP-0006` — "no tile data exists yet"; `IP-0006` has since shipped
  and is independently `VERIFIED`, `visuals.py`'s tile bytes now ground this topic directly)

## 1. Purpose
Ground `visuals.py`'s `_tile_off_bytes`/`_tile_on_bytes` helpers against the real 2bpp tile
encoding, confirming the already-shipped tile data is correctly formed (not merely
accidentally-correct because the two tiles happen to be solid colors).

## 2. Scope
The Game Boy/GBC 2-bits-per-pixel tile format (16 bytes = one 8×8 tile). Palette *data format*
(how a color is encoded) is covered by `R104`; this topic covers tile *pixel* data only.

## 3. Concepts
Each tile is 16 bytes: one row = one pair of bytes ("bitplanes"), 8 rows total. Within a row-pair,
the **first byte holds the low bit** of every pixel's 2-bit color index, the **second byte holds
the high bit**; bit 7 of each byte is the leftmost pixel, bit 0 the rightmost. A pixel's color
index is therefore `(high_bit << 1) | low_bit`, i.e. `0b00`=index 0, `0b11`=index 3. [Pan Docs —
Tile Data](https://gbdev.io/pandocs/Tile_Data.html); [Huderlem — Gameboy 2BPP Graphics
Format](https://www.huderlem.com/demos/gameboy2bpp.html) (worked byte-level example, cross-checked
against Pan Docs' own description).

### Sources
- [Pan Docs — Tile Data](https://gbdev.io/pandocs/Tile_Data.html)
- [Huderlem — Gameboy 2BPP Graphics Format (worked example)](https://www.huderlem.com/demos/gameboy2bpp.html)

## 4. Operational Context
`visuals.py:31-32`: `_tile_off_bytes()` returns `[0x00] * 16` — both bitplanes 0 for all 8 rows,
i.e. color index 0 (`0b00`) for every pixel: a fully "off" (background-color) tile. `visuals.py:35-36`:
`_tile_on_bytes()` returns `[0xFF, 0xFF] * 8` — both bitplane bytes `0xFF` for all 8 rows, i.e.
color index 3 (`0b11`, both bits set) for every pixel: a fully "on" (brightest-palette-slot) tile.
Both are correctly formed per the encoding above — confirmed by direct calculation, not merely by
the existing `test_rom.py` T9 suite's behavioral pass (T9 checks which tile *index* is shown
where, via `NR52` correlation, not the tile *pixel data*'s own byte-level correctness — this
topic is the missing piece that closes that gap).

## 5. Implementation Guidance
**No change needed** — both tiles are correctly encoded solid-color tiles, the simplest possible
case (uniform bit pattern per row needs no worked-example row-by-row derivation, unlike an
arbitrary pixel-art tile would). **For any future tile beyond a solid color** (e.g. a more
elaborate visualizer per `BL-0001`'s pending GDS-08, or per-scheme indicator art if `BL-0020`'s
multi-scheme architecture work lands): each row must be authored as an explicit `(low_byte,
high_byte)` pair, with each bit position corresponding to one pixel's low/high index bit — get
this wrong and pixels silently render as the wrong color index rather than failing to build (no
build-time validation exists for tile-data correctness, unlike `gbc_lib.py`'s label/fixup
mechanism, `R302`). Recommend: for non-trivial pixel art, generate tile bytes from an explicit
per-pixel index array (a small Python helper, same "compute the byte layout in Python, emit
the result" pattern `_wave_table_bytes()` already uses for Wave RAM) rather than hand-writing hex
bytes directly, to make the intended pixel pattern legible in the source and reduce transcription
errors.

## 6. Feature Mapping
FR-1120 (visualizer), `IP-0006` (the tile data this topic grounds).

## 7. Related Topics
R104 (CGB palette — the color *values* these tile indices select between), R205 (visualizer
design convention — template-based tile animation), R302 (the codegen pattern class this
project's other "compute bytes in Python, emit the result" helpers, like `_wave_table_bytes`,
also follow).
