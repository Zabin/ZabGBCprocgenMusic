"""
visuals.py — Driftune's minimal generative visualizer (IP-0006), extended by IP-1110
(FS-111/ADS-104, settings & control visibility).

Read-only consumer of engine state (FR-1120, GDS-03 SS1): reads NR52's per-channel active bits,
BAD_ZONE_FLAGS' combined bit, and (IP-1110) TEMPO_IDX/OCTAVE_IDX/SCALE_IDX/DENSITY_IDX/CHMIX_IDX;
never writes a PSG register or an engine-state field. A template-based design (R205 SS5): a fixed
tile set, animated by rewriting which tile shows at fixed BG positions and which BG palette colors
are active — cheaper than per-pixel procedural rendering and a natural fit for GBC's tile/palette
hardware.
"""

from gbc_lib import ROM
from wram_constants import (TEMPO_IDX, OCTAVE_IDX, SCALE_IDX, DENSITY_IDX, CHMIX_IDX,
                             BAD_ZONE_FLAGS, PRESET_TEMPO_IDX, PRESET_OCTAVE_IDX,
                             PRESET_SCALE_IDX, PRESET_DENSITY_IDX, PRESET_CHMIX_IDX)
from tiles import _tile_off_bytes, _tile_on_bytes, _bar_tile_bytes, CALM_PALETTE, BAD_PALETTE

LCDC = 0x40
BCPS = 0x68
BCPD = 0x69

TILEMAP_BASE = 0x9800   # BG tilemap, 32x32 tile indices
VRAM_TILE_DATA = 0x8000  # tile pixel data, unsigned addressing (LCDC bit 4 = 1)

# Tilemap cells for the 4 channel-activity indicators (top-left corner of the screen).
CHANNEL_CELLS = [TILEMAP_BASE + 0, TILEMAP_BASE + 1, TILEMAP_BASE + 2, TILEMAP_BASE + 3]

# IP-1110: 5 new tilemap cells for the settings-indicator row, one per base control, in the fixed
# order tempo/octave/scale/density/channel-mix. TILEMAP_BASE+4..+8 confirmed free by grepping
# build_rom.py/music_engine.py/gbc_lib.py for any other 0x98xx reference — nothing else touches
# the tilemap besides CHANNEL_CELLS above.
SETTINGS_CELLS = [TILEMAP_BASE + 4, TILEMAP_BASE + 5, TILEMAP_BASE + 6, TILEMAP_BASE + 7,
                   TILEMAP_BASE + 8]

TILE_OFF = 0  # blank tile index
TILE_ON = 1   # filled tile index
TILE_BAR_BASE = 2  # IP-1110: tile indices 2-9 are bar-height glyphs, fill levels 0-7

# IP-1110: the 5 settings-indicator source WRAM fields, read-only, same fixed order as
# SETTINGS_CELLS. Imported from wram_constants (IP-8020, BL-0065) rather than duplicated —
# visuals.py stays a read-only consumer with no import of music_engine.py (GDS-03 SS1);
# wram_constants.py is dependency-free, so importing it doesn't reintroduce that cycle.
SETTINGS_SOURCES = [TEMPO_IDX, OCTAVE_IDX, SCALE_IDX, DENSITY_IDX, CHMIX_IDX]

# IP-1110: boot-preset values for each of the 5 settings sources, used to pre-initialize
# SETTINGS_CELLS so the very first rendered frame is already correct (FS-111's Implementation
# Task 3), not left blank until the first update_visuals call.
SETTINGS_PRESETS = [PRESET_TEMPO_IDX, PRESET_OCTAVE_IDX, PRESET_SCALE_IDX, PRESET_DENSITY_IDX,
                    PRESET_CHMIX_IDX]

NR52 = 0xFF26
LY = 0xFF44   # PPU current-scanline register; 144-153 is VBlank (R102)

# IP-9030 (BL-0069): permanent diagnostic recording LY at ENTRY to update_visuals, so the
# per-frame VBlank budget this routine depends on is measurable rather than merely believed.
# Measured (R101 SS8.5): HALT wakes at LY=144 every frame, and read_joypad+apply_input+
# engine_tick alone consume through LY=152-153 before this routine even starts -- so the value
# recorded here is expected to sit at the very edge of VBlank (144-153) on every frame, idle
# included, not only on frames with heavy input work. This is one more duplicated plain-int WRAM
# constant on the debt BL-0065 already tracks -- deliberate, not a new pattern.
VIS_ENTRY_LY = 0xC061


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

    # Tile 0 (off) at VRAM_TILE_DATA, tile 1 (on) immediately after, then (IP-1110) 8 more
    # bar-height glyphs (fill levels 0-7) at tile indices 2-9.
    rom.LD_HL_nn(VRAM_TILE_DATA)
    tile_bytes = _tile_off_bytes() + _tile_on_bytes()
    for n in range(8):
        tile_bytes += _bar_tile_bytes(n)
    for b in tile_bytes:
        rom.LD_A_n(b); rom.LD_HLI_A()

    # Clear the 4 channel-activity cells to TILE_OFF.
    for addr in CHANNEL_CELLS:
        rom.LD_A_n(TILE_OFF); rom.LD_nn_A(addr)

    # IP-1110: pre-initialize the 5 settings-indicator cells to their boot-preset fill levels,
    # so the first rendered frame is already correct (FS-111 Implementation Task 3).
    for addr, preset in zip(SETTINGS_CELLS, SETTINGS_PRESETS):
        rom.LD_A_n(TILE_BAR_BASE + preset); rom.LD_nn_A(addr)

    _emit_write_palette(rom, CALM_PALETTE)

    rom.LD_A_n(0x91); rom.LDH_n_A(LCDC)  # LCD on, BG tile data 0x8000 (unsigned), BG display on
    rom.RET()


def build_visuals_update_asm(rom: ROM):
    """Called once per frame from the main loop (after engine_tick): read-only reaction to NR52
    + BAD_ZONE_FLAGS, no engine-state writes (FR-1120)."""
    rom.label('update_visuals')

    # IP-9030: record LY at the very top of this routine, before any of this frame's visualizer
    # work runs -- this measures what read_joypad/apply_input/engine_tick already spent, which is
    # the falsifiable question (does the budget hold), not how far this routine's own writes run
    # (v1 tried a tail probe and it read a flat, uninformative value in the clean build; see
    # IP-9030's own Risks field for why entry was chosen over the tail).
    rom.LDH_A_n(LY & 0xFF); rom.LD_nn_A(VIS_ENTRY_LY)

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

    # IP-1110: settings-row update runs last. An earlier version of this comment claimed that on
    # the exact frame Select is pressed, apply_input's init_engine reset costs enough extra CPU
    # that this block's VRAM writes for that frame are silently dropped. That claim was falsified
    # 2026-07-31 (BL-0069, IP-9030): PyBoy applies no PPU-mode gating to VRAM writes at all, so no
    # write is ever dropped, and a WRAM mirror of each write matches VRAM on every frame of every
    # class -- what looked like a Select-frame display lag was a pb.tick() mid-frame sampling
    # artifact, uniform across every frame class including idle ones (R308 SS8.5, R101 SS8.5).
    # The real, measured finding: read_joypad+apply_input+engine_tick alone consume roughly 9 of
    # VBlank's 10 scanlines before this routine starts, so it runs against about one remaining
    # scanline on every frame -- see VIS_ENTRY_LY above, which exists to make that margin
    # measurable. Placing this block last keeps the channel-activity/palette writes at their
    # original position; moving it earlier was tried during IP-1110's own implementation and
    # instead made the *channel-activity* writes intermittently miss the boot-preset render on
    # ordinary no-input frames -- re-explained the same way, by sampling position rather than by
    # write acceptance, but the empirical ordering choice itself stands unchanged.
    _emit_update_settings_row(rom)

    rom.RET()


def _emit_update_settings_row(rom):
    """IP-1110 (FS-111/ADS-104): read-only settings-indicator update, purely additive — never
    touches CHANNEL_CELLS, TILE_OFF/TILE_ON, or the palette-write routine (FR-1370). For each of
    the 5 base controls, reads its WRAM byte directly as the bar-tile fill level (0-7 for
    TEMPO_IDX/DENSITY_IDX/CHMIX_IDX, 0-3 for OCTAVE_IDX/SCALE_IDX — FS-111 Open Question 1
    resolved: all 5 share the same 8-level tile set, the narrower-range controls simply never
    exceed half-full) and writes the corresponding tile-pattern index to SETTINGS_CELLS."""
    for source, addr in zip(SETTINGS_SOURCES, SETTINGS_CELLS):
        rom.LD_A_nn(source)
        rom.ADD_A_n(TILE_BAR_BASE)
        rom.LD_nn_A(addr)
