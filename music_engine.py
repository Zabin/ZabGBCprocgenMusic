"""
music_engine.py — Driftune's real-time procedural generation engine (IP-0001 scope: pulse
channel A only; pulse B/wave/noise land in IP-0002/IP-0003, bad-zone scoring in IP-0004).

Owns every PSG register write (GDS-03 SS1's G1 write-scope rule). Preset tables are precomputed
in Python at build time (same "compute once in Python, only cheap table lookups on-device"
discipline the reference project's music.py used for freq()/note()) and emitted as ROM data;
on-device logic is limited to a per-frame countdown and, on note-expiry, an 8-bit LFSR step plus
a couple of table lookups (R100's cycle-budget note).
"""

from gbc_lib import ROM

# ── WRAM addresses (GDS-07) ──────────────────────────────────────────
TEMPO_IDX = 0xC000
OCTAVE_IDX = 0xC001
SCALE_IDX = 0xC002
DENSITY_IDX = 0xC003
CHMIX_IDX = 0xC004
NOTE_TIMER_PA = 0xC00C
CUR_DEGREE_PA = 0xC010
LFSR_STATE = 0xC016

# ── Sound registers (I/O offsets from 0xFF00, per R100) ─────────────
NR10 = 0x10; NR11 = 0x11; NR12 = 0x12; NR13 = 0x13; NR14 = 0x14
NR50 = 0x24; NR51 = 0x25; NR52 = 0x26

# ── Preset tables (data, GDS-03 SS3/SS6) ─────────────────────────────
# 8 tempo steps: frames-per-note-step at 59.7fps ~ 60fps, spanning ~60-180 BPM quarter notes.
TEMPO_BPM = [60, 75, 90, 105, 120, 140, 160, 180]
TEMPO_TABLE = [round(3600 / bpm) for bpm in TEMPO_BPM]  # frames per quarter note

# 4 octave roots (C3..C6) — OCTAVE_IDX selects which is the walk's home octave.
OCTAVE_ROOT_HZ = [130.81, 261.63, 523.25, 1046.50]

# 4 scales, each extended to exactly 8 degrees so the on-device walk never needs
# variable-length wraparound logic (GDS-03 SS3's "shape, not values" note) — degrees beyond
# each scale's own unique pitch count continue into the next octave.
SCALE_SEMITONES = {
    'major':      [0, 2, 4, 5, 7, 9, 11, 12],
    'minor':      [0, 2, 3, 5, 7, 8, 10, 12],
    'dorian':     [0, 2, 3, 5, 7, 9, 10, 12],
    'pentatonic': [0, 2, 4, 7, 9, 12, 14, 16],
}
SCALES = ['major', 'minor', 'dorian', 'pentatonic']

# Reset-to-preset known-good state (GDS-03 SS5): major scale, mid tempo, mid octave, sparse
# density/minimal channel-mix (both currently unused by IP-0001's single-channel scope, but the
# indices are still reset so later packages' presets are already correct).
PRESET_TEMPO_IDX = 4
PRESET_OCTAVE_IDX = 1
PRESET_SCALE_IDX = 0
PRESET_DENSITY_IDX = 0
PRESET_CHMIX_IDX = 0

# Small signed scale-degree deltas the LFSR-driven walk picks from (R200 SS1's "scale-constrained
# random walk" — weighted toward staying/small steps, indexed by the LFSR's low 2 bits).
DELTA_TABLE = [0xFF, 0x00, 0x00, 0x01]  # -1, 0, 0, +1 (two's complement)

# Galois LFSR feedback polynomial (8-bit, maximal-length taps) — deterministic given a fixed
# seed (MSTR-001 C6: determinism as a testing tool, not a listening requirement).
LFSR_POLY = 0xB8
LFSR_SEED = 0xA5


def freq(hz):
    return round(2048 - 131072 / hz)


def _note_table_bytes(scale_name, octave_idx):
    """8 (freq_lo, freq_hi|trigger) pairs for one (scale, octave) combination."""
    root_hz = OCTAVE_ROOT_HZ[octave_idx]
    out = []
    for semis in SCALE_SEMITONES[scale_name]:
        f = freq(root_hz * (2 ** (semis / 12)))
        assert 0 <= f <= 2047, f"note table freq out of range: {f}"
        out += [f & 0xFF, ((f >> 8) & 0x07) | 0x80]
    return out


def _ld_hl_label(rom, label):
    """LD HL, <label address> — gbc_lib's LD_HL_nn only accepts resolved ints, so a forward
    reference to a data-table label (defined later in this same emission pass) needs a manual
    16-bit fixup, the same mechanism ROM._abs() uses for CALL/JP targets."""
    rom.emit(0x21, 0, 0)
    rom.fixups.append((rom.pos - 2, label, 'abs16'))


def build_engine_asm(rom: ROM) -> dict:
    """Emits data tables + init/tick/reset routines. Returns a patch dict (unused for now,
    kept for parity with the reference project's build_game_asm return-shape convention)."""
    patches = {}

    # ── init_engine (boot init AND Select-reset target, GDS-03 SS5) ──
    rom.label('init_engine')
    rom.LD_A_n(PRESET_TEMPO_IDX); rom.LD_nn_A(TEMPO_IDX)
    rom.LD_A_n(PRESET_OCTAVE_IDX); rom.LD_nn_A(OCTAVE_IDX)
    rom.LD_A_n(PRESET_SCALE_IDX); rom.LD_nn_A(SCALE_IDX)
    rom.LD_A_n(PRESET_DENSITY_IDX); rom.LD_nn_A(DENSITY_IDX)
    rom.LD_A_n(PRESET_CHMIX_IDX); rom.LD_nn_A(CHMIX_IDX)
    rom.XOR_A(); rom.LD_nn_A(CUR_DEGREE_PA)
    rom.LD_A_n(1); rom.LD_nn_A(NOTE_TIMER_PA)  # fire the first note on the very next tick
    rom.LD_A_n(LFSR_SEED); rom.LD_nn_A(LFSR_STATE)
    rom.RET()

    # ── lfsr_step: Galois LFSR, one step, new state left in A ────────
    rom.label('lfsr_step')
    rom.LD_A_nn(LFSR_STATE)
    rom.SRL_A()
    rom.JR_NC('ls_noxor')
    rom.XOR_n(LFSR_POLY)
    rom.label('ls_noxor')
    rom.LD_nn_A(LFSR_STATE)
    rom.RET()

    # ── engine_tick: called once per frame from the main loop ────────
    rom.label('engine_tick')
    rom.LD_A_nn(NOTE_TIMER_PA)
    rom.DEC_A()
    rom.LD_nn_A(NOTE_TIMER_PA)
    rom.OR_A()
    rom.JR_NZ('et_done')

    # Time for the next note: step CUR_DEGREE_PA by an LFSR-picked signed delta.
    rom.CALL('lfsr_step')
    rom.AND_n(0x03)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'delta_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_B_A()                       # B = signed delta
    rom.LD_A_nn(CUR_DEGREE_PA)
    rom.ADD_A_B()
    rom.AND_n(0x07)
    rom.LD_nn_A(CUR_DEGREE_PA)

    # table_idx = SCALE_IDX*4 + OCTAVE_IDX  (0-15)
    rom.LD_A_nn(SCALE_IDX)
    rom.ADD_A_A(); rom.ADD_A_A()
    rom.LD_B_A()
    rom.LD_A_nn(OCTAVE_IDX)
    rom.ADD_A_B()
    rom.ADD_A_A()                      # *2 -> pointer-table byte offset
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'ptr_table')
    rom.ADD_HL_BC()
    rom.LD_E_HL(); rom.INC_HL(); rom.LD_D_HL()
    rom.LD_H_D(); rom.LD_L_E()          # HL = the (scale, octave) note table's own address

    rom.LD_A_nn(CUR_DEGREE_PA)
    rom.ADD_A_A()                      # *2 (2 bytes/entry)
    rom.LD_C_A(); rom.LD_B_n(0)
    rom.ADD_HL_BC()
    rom.LD_A_HL(); rom.LDH_n_A(NR13)
    rom.INC_HL()
    rom.LD_A_HL(); rom.LDH_n_A(NR14)

    # Reload NOTE_TIMER_PA from the tempo table.
    rom.LD_A_nn(TEMPO_IDX)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'tempo_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_nn_A(NOTE_TIMER_PA)

    rom.label('et_done')
    rom.RET()

    # ── Data tables ───────────────────────────────────────────────────
    rom.label('delta_table')
    rom.emit(*DELTA_TABLE)

    rom.label('tempo_table')
    rom.emit(*TEMPO_TABLE)

    note_table_labels = []
    for si, scale_name in enumerate(SCALES):
        for oi in range(len(OCTAVE_ROOT_HZ)):
            lbl = f'note_tbl_{si}_{oi}'
            rom.label(lbl)
            rom.emit(*_note_table_bytes(scale_name, oi))
            note_table_labels.append(lbl)

    rom.label('ptr_table')
    for lbl in note_table_labels:
        rom._abs(lbl)  # 2-byte pointer, fixed up in rom.resolve()

    return patches
