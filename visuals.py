"""
visuals.py — Driftune's minimal generative visualizer (IP-0006).

Read-only consumer of engine state (FR-1120, GDS-03 SS1): reads NR52's per-channel active bits
and BAD_ZONE_FLAGS' combined bit; never writes a PSG register or an engine-state field. A
template-based design (R205 SS5): a fixed 2-tile set (off/on), animated by rewriting which tile
shows at 4 fixed BG positions (one per channel) and which BG palette colors are active — cheaper
than per-pixel procedural rendering and a natural fit for GBC's tile/palette hardware.
"""

from gbc_lib import ROM, rgb15

LCDC = 0x40
BCPS = 0x68
BCPD = 0x69

TILEMAP_BASE = 0x9800   # BG tilemap, 32x32 tile indices
VRAM_TILE_DATA = 0x8000  # tile pixel data, unsigned addressing (LCDC bit 4 = 1)

# Tilemap cells for the 4 channel-activity indicators (top-left corner of the screen).
CHANNEL_CELLS = [TILEMAP_BASE + 0, TILEMAP_BASE + 1, TILEMAP_BASE + 2, TILEMAP_BASE + 3]

TILE_OFF = 0  # blank tile index
TILE_ON = 1   # filled tile index

BAD_ZONE_FLAGS = 0xC005  # music_engine.BAD_ZONE_FLAGS (kept as a plain int to avoid a circular
                          # import — visuals.py is a read-only consumer, GDS-03 SS1)
NR52 = 0xFF26


def _tile_off_bytes():
    return [0x00] * 16  # solid color index 0 (background) for all 8 rows


def _tile_on_bytes():
    return [0xFF, 0xFF] * 8  # solid color index 3 (brightest palette slot) for all 8 rows


# Two BG palette-0 color sets (R205 SS5's "2-3 restrained tones" guidance): calm (blue/green)
# vs. bad-zone (red), swapped each frame based on BAD_ZONE_FLAGS bit3 — the visualizer's only
# reaction to bad-zone state for this minimal v1 pass (a distinct tile/animation reacting to
# bad-zone, beyond a color swap, is a reasonable IP-0006+/backlog follow-up, not built here).
CALM_PALETTE = [rgb15(0, 0, 0), rgb15(0, 8, 16), rgb15(4, 16, 24), rgb15(10, 28, 20)]
BAD_PALETTE = [rgb15(0, 0, 0), rgb15(16, 0, 0), rgb15(24, 4, 4), rgb15(31, 10, 6)]


def _emit_write_palette(rom, colors):
    rom.LD_A_n(0x80); rom.LDH_n_A(BCPS)  # auto-increment, start at byte 0 (BG palette 0, color 0)
    for c in colors:
        rom.LD_A_n(c & 0xFF); rom.LDH_n_A(BCPD)
        rom.LD_A_n((c >> 8) & 0xFF); rom.LDH_n_A(BCPD)


def build_visuals_init_asm(rom: ROM):
    """Called once at boot (from build_rom.py's init sequence): tile data, tilemap, palette,
    LCD on. Kept as a separate routine (not folded into music_engine.init_engine) since it is
    never re-run on a Select reset — the visualizer's own state (which tile is shown) is
    recomputed fresh every frame by update_visuals, not something a reset needs to restore."""
    rom.label('init_visuals')

    # Tile 0 (off) at VRAM_TILE_DATA, tile 1 (on) immediately after.
    rom.LD_HL_nn(VRAM_TILE_DATA)
    for b in _tile_off_bytes() + _tile_on_bytes():
        rom.LD_A_n(b); rom.LD_HLI_A()

    # Clear the 4 indicator cells to TILE_OFF.
    for addr in CHANNEL_CELLS:
        rom.LD_A_n(TILE_OFF); rom.LD_nn_A(addr)

    _emit_write_palette(rom, CALM_PALETTE)

    rom.LD_A_n(0x91); rom.LDH_n_A(LCDC)  # LCD on, BG tile data 0x8000 (unsigned), BG display on
    rom.RET()


def build_visuals_update_asm(rom: ROM):
    """Called once per frame from the main loop (after engine_tick): read-only reaction to NR52
    + BAD_ZONE_FLAGS, no engine-state writes (FR-1120)."""
    rom.label('update_visuals')

    rom.LDH_A_n(NR52 & 0xFF)   # NR52 is 0xFF26; LDH_A_n takes the 0xFF00 offset (0x26)
    rom.LD_B_A()               # B = NR52 (bits 0-3 = channel active status)

    for i, addr in enumerate(CHANNEL_CELLS):
        rom.LD_A_B()
        rom.AND_n(1 << i)
        rom.JR_Z(f'uv_off_{i}')
        rom.LD_A_n(TILE_ON); rom.LD_nn_A(addr)
        rom.JR(f'uv_done_{i}')
        rom.label(f'uv_off_{i}')
        rom.LD_A_n(TILE_OFF); rom.LD_nn_A(addr)
        rom.label(f'uv_done_{i}')

    rom.LD_A_nn(BAD_ZONE_FLAGS)
    rom.BIT_b_A(3)
    rom.JR_Z('uv_calm')
    _emit_write_palette(rom, BAD_PALETTE)
    rom.JR('uv_palette_done')
    rom.label('uv_calm')
    _emit_write_palette(rom, CALM_PALETTE)
    rom.label('uv_palette_done')

    rom.RET()
