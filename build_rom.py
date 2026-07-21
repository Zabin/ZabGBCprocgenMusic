#!/usr/bin/env python3
"""
build_rom.py — Driftune master build script.

Assembles gbc_lib's generic ROM class + music_engine.py (generation) + input_map.py (steering) +
visuals.py (visualizer) into a valid GBC ROM. No RGBDS or external assembler, same discipline as
the reference project's own build_rom.py.

Usage: python3 build_rom.py <output.gbc>
"""
import sys

from gbc_lib import ROM
from music_engine import (
    build_engine_asm, _wave_table_bytes,
    NR10, NR11, NR12, NR21, NR22, NR30, NR31, NR32, NR50, NR51, NR52, WAVE_RAM,
)
from input_map import build_input_asm
from visuals import build_visuals_init_asm, build_visuals_update_asm

VBLANK_FLAG = 0xC060


def build(rom: ROM):
    # RST vectors — unused, same convention as the reference project (RETI stub so a stray
    # interrupt/RST doesn't crash rather than being reachable code).
    for a in range(0x0000, 0x0040):
        rom.data[a] = 0xD9

    # VBlank ISR: set VBLANK_FLAG, same main-loop-synchronization convention as the reference
    # project's asm_game.py.
    rom.seek(0x0040)
    rom.PUSH_AF()
    rom.LD_A_n(1); rom.LD_nn_A(VBLANK_FLAG)
    rom.POP_AF(); rom.RETI()

    for a in (0x0048, 0x0050, 0x0058, 0x0060):
        rom.seek(a); rom.RETI()

    # Entry point
    rom.seek(0x0100)
    rom.NOP(); rom.JP('main')

    rom.seek(0x0150)
    rom.label('main')
    rom.LD_SP_nn(0xFFFE)
    rom.DI()

    # Sound hardware init (R100/R108): power on, full volume both sides, all channels panned to
    # both, per-channel duty/envelope/DAC state set once — channel-specific register state that
    # isn't part of the per-note write (frequency registers only, per music_engine.engine_tick).
    rom.LD_A_n(0x80); rom.LDH_n_A(NR52)   # master power on
    rom.LD_A_n(0x77); rom.LDH_n_A(NR50)   # max L/R master volume, Vin off
    rom.LD_A_n(0xFF); rom.LDH_n_A(NR51)   # every channel panned to both sides

    rom.LD_A_n(0x80); rom.LDH_n_A(NR10)   # pulse A: no frequency sweep
    rom.LD_A_n(0x80); rom.LDH_n_A(NR11)   # pulse A: 50% duty
    rom.LD_A_n(0xF3); rom.LDH_n_A(NR12)   # pulse A: volume 15, decreasing envelope, period 3

    rom.LD_A_n(0x80); rom.LDH_n_A(NR21)   # pulse B: 50% duty (IP-0002)
    rom.LD_A_n(0xF3); rom.LDH_n_A(NR22)   # pulse B: same envelope shape as pulse A

    rom.LD_A_n(0x80); rom.LDH_n_A(NR30)   # wave: DAC power on (IP-0002, R114)
    rom.LD_A_n(0x20); rom.LDH_n_A(NR32)   # wave: 100% output level (bits 6-5 = 01)
    for i, b in enumerate(_wave_table_bytes()):
        rom.LD_A_n(b); rom.LD_nn_A(WAVE_RAM + i)   # copy the precomputed waveform into Wave RAM

    rom.CALL('init_engine')
    rom.CALL('init_visuals')

    rom.LD_A_n(0x01); rom.LD_nn_A(0xFFFF)  # IE: VBlank only
    rom.EI()

    rom.label('main_loop')
    rom.HALT()
    rom.LD_A_nn(VBLANK_FLAG); rom.OR_A()
    rom.JR_Z('main_loop')
    rom.XOR_A(); rom.LD_nn_A(VBLANK_FLAG)

    rom.CALL('read_joypad')
    rom.CALL('apply_input')
    rom.CALL('engine_tick')
    rom.CALL('update_visuals')

    rom.JR('main_loop')

    build_engine_asm(rom)
    build_input_asm(rom)
    build_visuals_init_asm(rom)
    build_visuals_update_asm(rom)

    rom.resolve()
    rom.set_header("DRIFTUNE", cart=0x00, rsize=0x00, ramsize=0x00)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 build_rom.py <output.gbc>")
        sys.exit(1)
    rom = ROM()
    build(rom)
    with open(sys.argv[1], 'wb') as f:
        f.write(rom.data)
    print(f"Wrote {sys.argv[1]}: {len(rom.data)} bytes")


if __name__ == '__main__':
    main()
