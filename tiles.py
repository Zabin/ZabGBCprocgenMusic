"""
tiles.py — Driftune's visualizer tile pixel art and BG palette data (IP-8030, BL-0089).

Pure content module: tile-pixel-byte generators and palette color tables consumed by
visuals.py. Dependency-free per this package's own Definition of Done (imports nothing from
music_engine.py/visuals.py/input_map.py/build_rom.py/gbc_lib.py/wram_constants.py/test_rom.py)
— the module-decomposition shape GDS-03/GDS-09 always described, restored here (see GDS-09 §1's
now-superseded finding). `visuals.py`'s original palette definitions built each color via
gbc_lib's `rgb15(r, g, b)` helper; since the DoD bars importing gbc_lib.py from this module, a
private local copy of that same 2-line pure bit-packing formula is kept below rather than either
importing gbc_lib.py or hardcoding the packed integers as unexplained magic numbers — the
computed values are unchanged (verified: rgb15(0,8,16)=0x4100, rgb15(0,0,0)=0x0, etc., identical
to gbc_lib.rgb15's own output).
"""


def _rgb15(r, g, b):
    return (r & 0x1F) | ((g & 0x1F) << 5) | ((b & 0x1F) << 10)


def _tile_off_bytes():
    return [0x00] * 16  # solid color index 0 (background) for all 8 rows


def _tile_on_bytes():
    return [0xFF, 0xFF] * 8  # solid color index 3 (brightest palette slot) for all 8 rows


def _bar_tile_bytes(n):
    """IP-1110: an 8x8 2bpp glyph with the bottom n rows filled (color index 3) and the
    remaining 8-n rows blank (color index 0) — a "how full is this" shape, no text/font
    rendering needed (ADS-104 SS3)."""
    rows = []
    for row in range(8):
        filled = row >= (8 - n)
        rows.extend([0xFF, 0xFF] if filled else [0x00, 0x00])
    return rows


# Two BG palette-0 color sets (R205 SS5's "2-3 restrained tones" guidance): calm (blue/green)
# vs. bad-zone (red), swapped each frame based on BAD_ZONE_FLAGS bit3 — the visualizer's only
# reaction to bad-zone state for this minimal v1 pass (a distinct tile/animation reacting to
# bad-zone, beyond a color swap, is a reasonable IP-0006+/backlog follow-up, not built here).
CALM_PALETTE = [_rgb15(0, 0, 0), _rgb15(0, 8, 16), _rgb15(4, 16, 24), _rgb15(10, 28, 20)]
BAD_PALETTE = [_rgb15(0, 0, 0), _rgb15(16, 0, 0), _rgb15(24, 4, 4), _rgb15(31, 10, 6)]
