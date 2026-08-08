"""
input_map.py — Driftune's joypad edge-detection and input->parameter mapping (GDS-03 SS3).

Never writes a PSG register or a note-generation field directly — only the parameter indices
(TEMPO_IDX/OCTAVE_IDX/SCALE_IDX/DENSITY_IDX/CHMIX_IDX) `music_engine.py` itself reads, plus
calling `init_engine` for the Select reset (FR-1070). This keeps exactly one writer per hardware
surface (GDS-03 SS1).
"""

from gbc_lib import ROM
from music_engine import _emit_begin_blend
from wram_constants import TEMPO_IDX, OCTAVE_IDX, SCALE_IDX, DENSITY_IDX, CHMIX_IDX

# ── WRAM addresses (GDS-07 SS5) ───────────────────────────────────────
JOY_PREV = 0xC050
JOY_CUR = 0xC051
JOY_NEW = 0xC052

# ── Joypad register + bit layout (reused verbatim from the reference project's own
# read_joypad convention, documented in its memory.md — active-HIGH after the CPL) ──
P1 = 0x00
J_A, J_B, J_SELECT, J_START = 0, 1, 2, 3
J_RIGHT, J_LEFT, J_UP, J_DOWN = 4, 5, 6, 7


def build_input_asm(rom: ROM):
    # ── read_joypad: same two-nibble-read + CPL convention as the reference project's
    # asm_game.py:read_joypad, reused near-verbatim (it is already fully generic hardware
    # access, not game-specific) ──
    rom.label('read_joypad')
    rom.LD_A_nn(JOY_CUR); rom.LD_nn_A(JOY_PREV)

    rom.LD_A_n(0x10); rom.LDH_n_A(P1)
    rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1)
    rom.AND_n(0x0F); rom.LD_B_A()

    rom.LD_A_n(0x20); rom.LDH_n_A(P1)
    rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1); rom.LDH_A_n(P1)
    rom.AND_n(0x0F); rom.SWAP_A()
    rom.OR_B()
    rom.CPL()
    rom.LD_nn_A(JOY_CUR)

    rom.LD_A_n(0x30); rom.LDH_n_A(P1)

    rom.LD_A_nn(JOY_PREV); rom.CPL(); rom.LD_B_A()
    rom.LD_A_nn(JOY_CUR); rom.AND_B()
    rom.LD_nn_A(JOY_NEW)
    rom.RET()

    # ── apply_input: one control -> one parameter step, edge-triggered (FR-1020..1070) ──
    rom.label('apply_input')

    # IP-1120 (roadmap R7): the 4 calls below pass extra_call='mood_update' -- TEMPO_IDX/
    # DENSITY_IDX/SCALE_IDX each feed AROUSAL/VALENCE (ADS-105/FS-112). OCTAVE_IDX (Right/Left)
    # does not feed either formula, so those two calls omit extra_call.
    _step_on_bit(rom, J_UP, TEMPO_IDX, +1, 0x07, 'ai_up', extra_call='mood_update')
    _step_on_bit(rom, J_DOWN, TEMPO_IDX, -1, 0x07, 'ai_down', extra_call='mood_update')
    _step_on_bit(rom, J_RIGHT, OCTAVE_IDX, +1, 0x03, 'ai_right')
    _step_on_bit(rom, J_LEFT, OCTAVE_IDX, -1, 0x03, 'ai_left')
    _step_on_bit(rom, J_A, SCALE_IDX, +1, 0x03, 'ai_a', extra_call='mood_update')
    _step_on_bit(rom, J_B, DENSITY_IDX, +1, 0x07, 'ai_b', extra_call='mood_update')

    # Start: step CHMIX_IDX (FR-1060), then begin a blend toward the newly-selected preset's
    # style (IP-1130, roadmap R8, amends FR-1240 — SCALE_IDX still applies the same frame;
    # TEMPO_IDX/DENSITY_IDX/DUTY_BIAS now glide over the following frames instead of landing
    # instantly, not gated to the next onset either way, unlike CHMIX_MASKS's channel-mix/scheme
    # half, FR-1190). Inlined rather than reusing _step_on_bit so the blend only begins on the
    # actual edge, not every frame.
    rom.LD_A_nn(JOY_NEW)
    rom.BIT_b_A(J_START)
    rom.JR_Z('ai_start')
    rom.LD_A_nn(CHMIX_IDX)
    rom.INC_A()
    rom.AND_n(0x07)
    rom.LD_nn_A(CHMIX_IDX)
    _emit_begin_blend(rom)
    rom.label('ai_start')

    # Select: unconditional reset to the known-good preset (FR-1070), regardless of bad-zone
    # state — init_engine (music_engine.py) is both the boot-init and the reset target.
    rom.LD_A_nn(JOY_NEW)
    rom.BIT_b_A(J_SELECT)
    rom.JR_Z('ai_no_select')
    rom.CALL('init_engine')
    rom.label('ai_no_select')

    rom.RET()


def _step_on_bit(rom, bit, addr, delta, mask, skip_label, extra_call=None):
    """If JOY_NEW's `bit` is set, step the byte at `addr` by +-1 and wrap to `mask`
    (mask must be 2**n - 1 so INC/DEC + AND wraps correctly in both directions).

    IP-1120 (roadmap R7): `extra_call`, if given, is called strictly inside the edge-taken
    branch (after the write, before `skip_label`) — never after the label, since apply_input
    itself runs every frame and a call placed after the label would run unconditionally,
    violating NFR-1170's zero-added-per-frame-cost contract."""
    rom.LD_A_nn(JOY_NEW)  # re-read each time since intervening ops clobber A
    rom.BIT_b_A(bit)
    rom.JR_Z(skip_label)
    rom.LD_A_nn(addr)
    if delta > 0:
        rom.INC_A()
    else:
        rom.DEC_A()
    rom.AND_n(mask)
    rom.LD_nn_A(addr)
    if extra_call is not None:
        rom.CALL(extra_call)
    rom.label(skip_label)
