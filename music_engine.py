"""
music_engine.py — Driftune's real-time procedural generation engine.

IP-0001 scope: pulse channel A only. IP-0002 extends this to pulse B (independent melodic walk)
and the wave channel (bass/timbre role per R207's chiptune-convention finding — a distinct
octave anchor and half-rate tempo, not a second identical lead). Noise/density lands in IP-0003,
bad-zone scoring in IP-0004.

Owns every PSG register write (GDS-03 SS1's G1 write-scope rule). Preset tables are precomputed
in Python at build time (same "compute once in Python, only cheap table lookups on-device"
discipline the reference project's music.py used for freq()/note()) and emitted as ROM data;
on-device logic is limited to a per-frame countdown and, on note-expiry, an 8-bit LFSR step plus
a couple of table lookups (R100/R110's cycle-budget note).
"""

from gbc_lib import ROM
import math

# ── WRAM addresses (GDS-07) ──────────────────────────────────────────
TEMPO_IDX = 0xC000
OCTAVE_IDX = 0xC001
SCALE_IDX = 0xC002
DENSITY_IDX = 0xC003
CHMIX_IDX = 0xC004
NOTE_TIMER_PA = 0xC00C
NOTE_TIMER_PB = 0xC00D
NOTE_TIMER_WV = 0xC00E
CUR_DEGREE_PA = 0xC010
CUR_DEGREE_PB = 0xC011
CUR_DEGREE_WV = 0xC012
LFSR_STATE = 0xC016      # pulse A's own LFSR (IP-0001 name, kept for compatibility)
LFSR_STATE_PB = 0xC017   # IP-0002: pulse B's independent LFSR
LFSR_STATE_WV = 0xC018   # IP-0002: wave channel's independent LFSR
NOISE_STEP_IDX = 0xC019  # IP-0003: 0-15, position in the 16-step Euclidean pattern
NOTE_TIMER_NZ = 0xC00F   # reserved by GDS-07 SS3; IP-0003's noise-hit countdown

# IP-0004: bad-zone state (GDS-07 SS2)
BAD_ZONE_FLAGS = 0xC005      # bit0 DISSONANT, bit1 STUCK, bit2 OVERLOAD, bit3 COMBINED
DISSONANCE_SCORE = 0xC006
STALE_COUNT_PA = 0xC007
STALE_COUNT_PB = 0xC008
STALE_COUNT_WV = 0xC009
ONSET_WINDOW_COUNT = 0xC00A
ONSET_WINDOW_TICK_CTR = 0xC00B
# Scratch bytes for dissonance_tick's own intermediate semitone values (not persisted meaning
# across frames, just working storage during one tick's computation).
SEMI_PA = 0xC01A
SEMI_PB = 0xC01B
SEMI_WV = 0xC01C

# IP-1060: arpeggio state, pulse A/B only (wave keeps its plain bass role, R207) — packed one
# byte per channel: bits0-3 sub-tick countdown, bits4-5 step index (0-3, wraps via AND 0x30).
# ARP_DEGREE_SCRATCH is shared working storage (pa/pb ticks run sequentially, never concurrently
# within a frame), same "not persisted across frames" convention as SEMI_PA/PB/WV.
ARP_STATE_PA = 0xC01D
ARP_STATE_PB = 0xC01E
ARP_DEGREE_SCRATCH = 0xC01F

# IP-0004 thresholds (GDS-03 SS4, R204 SS5) — first-guess placeholders, per BL-0005's own
# deferred-tuning convention; the dissonance weight table itself is literature-grounded (R204),
# these threshold *numbers* are not yet tuned by ear.
DISSONANCE_THRESHOLD = 20      # ~60% of the 3-pair theoretical max (3 * 15 = 45)
STALE_THRESHOLD = 8            # consecutive same-degree repeats (period-1 only, MVP scope)
OVERLOAD_THRESHOLD = 20        # onset events within the ONSET_WINDOW_FRAMES window
ONSET_WINDOW_FRAMES = 32

# ── Sound registers (I/O offsets from 0xFF00, per R100/R108) ─────────
NR10 = 0x10; NR11 = 0x11; NR12 = 0x12; NR13 = 0x13; NR14 = 0x14
NR21 = 0x16; NR22 = 0x17; NR23 = 0x18; NR24 = 0x19
NR30 = 0x1A; NR31 = 0x1B; NR32 = 0x1C; NR33 = 0x1D; NR34 = 0x1E
NR41 = 0x20; NR42 = 0x21; NR43 = 0x22; NR44 = 0x23
NR50 = 0x24; NR51 = 0x25; NR52 = 0x26
WAVE_RAM = 0xFF30  # 16 bytes, 0xFF30-0xFF3F (R114)
DIV = 0x04  # free-running timer (R213 SS5) — used to randomize LFSR seeds on init/Select

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

# IP-0004: semitone (mod 12, octave-independent) per (scale, degree) — 4 scales x 8 degrees,
# for dissonance scoring (R204). Precomputed the same "compute once in Python" way as the note
# frequency tables.
SEMITONE_TABLE_DATA = [
    SCALE_SEMITONES[scale_name][degree] % 12
    for scale_name in SCALES
    for degree in range(8)
]

# 7 interval-class weights (0=unison/octave .. 6=tritone), folding inversions together (a
# standard pitch-class-set-theory simplification of R204's raw 12-entry proposal — m2/M7 both
# fold to ic=1, etc.) — ordering/magnitudes still derived from R204's Helmholtz-roughness-cited
# ordering: m2(ic1)/tritone(ic6) highest, P4/P5(ic5) lowest nonzero.
DISSONANCE_WEIGHT_BY_IC = [0, 15, 11, 3, 2, 1, 13]

# Reset-to-preset known-good state (GDS-03 SS5): major scale, mid tempo, mid octave, sparse
# density/minimal channel-mix (density/channel-mix indices reset even though IP-0001/0002 don't
# yet consume them for behavior, so later packages' presets are already correct).
PRESET_TEMPO_IDX = 4
PRESET_OCTAVE_IDX = 1
PRESET_SCALE_IDX = 0
PRESET_DENSITY_IDX = 0
PRESET_CHMIX_IDX = 0

# Small signed scale-degree deltas the LFSR-driven walk picks from (R201's "scale-constrained
# random walk" — weighted toward staying/small steps, indexed by the LFSR's low 2 bits).
DELTA_TABLE = [0xFF, 0x00, 0x00, 0x01]  # -1, 0, 0, +1 (two's complement)

# Galois LFSR feedback polynomial (8-bit, maximal-length taps) — deterministic given a fixed
# seed (MSTR-001 C6: determinism as a testing tool, not a listening requirement). Each channel
# gets its own seed so the three melodic walks decorrelate rather than moving in lockstep
# (R203's voice-leading/masking-risk finding).
LFSR_POLY = 0xB8
LFSR_SEED_PA = 0xA5
LFSR_SEED_PB = 0x5A
LFSR_SEED_WV = 0x3C

# ── Channel generation parameters (IP-0002/IP-0004/IP-1060/IP-9010) ──
# name, note_timer, cur_degree, lfsr_state, lfsr_seed, freq_lo_reg, freq_hi_reg,
# octave_delta (subtracted from OCTAVE_IDX, floored at 0), tempo_mult (note duration multiplier),
# stale_count (IP-0004 repetition counter), duty_reg (IP-1060, None if not varied),
# arp_state (IP-1060 packed arpeggio WRAM byte, None if this channel doesn't arpeggiate),
# dac_reg (IP-9010: the register whose DAC/envelope power this channel's channel-mix gate
# toggles — NR12/NR22 envelope-volume for pulse A/B, NR30 DAC-power bit for wave; writing 0
# there silences the channel and clears its NR52 bit within this same onset), dac_on (the value
# restored when this channel's mix bit is active — matches this channel's boot-time envelope/DAC
# value exactly, so re-enabling produces identical tone to a fresh boot), bit_index (this
# channel's bit position in CHMIX_MASKS/NR52 — pa=0, pb=1, wv=2, matching NR52's own channel-bit
# order, per BL-0019/IP-9010's package doc)
CHANNELS = [
    ('pa', NOTE_TIMER_PA, CUR_DEGREE_PA, LFSR_STATE,    LFSR_SEED_PA, NR13, NR14, 0, 1, STALE_COUNT_PA, NR11, ARP_STATE_PA, NR12, 0xF3, 0),
    ('pb', NOTE_TIMER_PB, CUR_DEGREE_PB, LFSR_STATE_PB, LFSR_SEED_PB, NR23, NR24, 0, 1, STALE_COUNT_PB, NR21, ARP_STATE_PB, NR22, 0xF3, 1),
    # Wave channel: bass/timbre role (R207 finding, BL-0008) — anchored one octave index lower
    # (floored at 0) and half the note rate (tempo_mult=2), matching bass lines moving less often
    # than melody. The wave-channel frequency formula is itself one octave lower than the pulse
    # formula for an identical register value (R108/R114), so reusing the pulse note tables
    # as-is on NR33/NR34 gives an *additional* free octave drop on top of the octave_delta below.
    # No duty cycle (wave has no duty concept) and no arpeggio (IP-1060: keeps its plain
    # sustained bass role rather than fast pitch-cycling, a deliberate scope choice).
    ('wv', NOTE_TIMER_WV, CUR_DEGREE_WV, LFSR_STATE_WV, LFSR_SEED_WV, NR33, NR34, -1, 2, STALE_COUNT_WV, None, None, NR30, 0x80, 2),
]

# IP-9010 (BL-0019): channel-mix gating — an 8-entry table of 4-bit masks, one per CHMIX_IDX
# preset, indexed the same way as every other preset table (GDS-03 SS6). bit0=pulse A,
# bit1=pulse B, bit2=wave, bit3=noise — matching NR52's own channel-bit order for a direct,
# low-risk lookup (no remapping needed anywhere a mask bit is tested against an NR52 bit).
# Preset 0 (PRESET_CHMIX_IDX) MUST be "all 4 active" (0b1111) — every pre-existing test (T2/T3/
# T6/T7/T9) assumes all channels active at boot/reset. The remaining 7 presets explore useful
# combinations (GDS-03 SS3's own example: "a channel-mix preset using only the two pulse
# channels" is preset 1 below) — first-guess placeholders, not tuned by ear, same convention as
# every other untuned preset table (BL-0005's existing disposition covers this). Every entry is
# deliberately nonzero (Risks section, IP-9010 package doc) — an all-silent preset would leave
# the engine audibly dead with no recovery path short of Select.
CHMIX_MASKS = [
    0b1111,  # 0: all four (preset default — required, see above)
    0b0011,  # 1: pulse A + pulse B (GDS-03 SS3's own example)
    0b0101,  # 2: pulse A + wave
    0b1001,  # 3: pulse A + noise
    0b0110,  # 4: pulse B + wave
    0b1100,  # 5: wave + noise
    0b0111,  # 6: pulse A + pulse B + wave (no noise)
    0b1011,  # 7: pulse A + pulse B + noise (no wave)
]

# IP-1060: arpeggio-as-polyphony (R216) — a period-4 up/down offset pattern (root, third, fifth,
# third, within the active scale's 8-degree table) avoids needing a mod-3 counter (SM83 has no
# division; a period-4 cycle wraps with a plain AND, R302). First-guess placeholder rate/shape,
# not tuned by ear (BL-0005's existing disposition covers this).
ARPEGGIO_OFFSETS = [0, 2, 4, 2]
ARP_SUBTICK_RELOAD = 6  # frames per chord-tone

# IP-1060: duty-cycle variation (R216) — NR11/NR21 whole-byte values (length bits stay 0, unused,
# same as the existing fixed-duty boot init), one per CUR_DEGREE mod 4.
DUTY_BY_DEGREE = [0x00, 0x40, 0x80, 0xC0]  # 12.5% / 25% / 50% / 75%

# ── Noise/density (IP-0003, R202/R115) ───────────────────────────────
# 8 density steps: k onsets distributed across a fixed n=16-step grid (a 16th-note bar at the
# current tempo) via Euclidean spacing (R202) — DENSITY_IDX selects k.
DENSITY_K = [2, 3, 4, 5, 6, 8, 10, 12]
NOISE_STEPS = 16

# Per-tempo 16th-note step duration (quarter-note frames / 4, floor at 1 frame).
NOISE_STEP_TABLE = [max(1, round(t / 4)) for t in TEMPO_TABLE]


def _euclidean_pattern(k, n=NOISE_STEPS):
    """k onsets spread as evenly as possible across n steps (R202's Toussaint-cited approach):
    an onset at step i whenever floor(i*k/n) advances past the previous step's bucket."""
    pattern = []
    prev_bucket = -1
    for i in range(n):
        bucket = (i * k) // n
        pattern.append(1 if bucket != prev_bucket else 0)
        prev_bucket = bucket
    return pattern


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


def _wave_table_bytes():
    """16 bytes = 32 4-bit samples (R114), a simple sine-ish shape — high nibble played first.
    A single precomputed shape is enough for IP-0002's MVP scope; more shapes (a switchable
    timbre parameter) are an IP-0002+/backlog candidate (R114 SS5), not built here."""
    samples = [round(7.5 + 7.5 * math.sin(2 * math.pi * i / 32)) for i in range(32)]
    samples = [max(0, min(15, s)) for s in samples]
    out = []
    for i in range(0, 32, 2):
        out.append((samples[i] << 4) | samples[i + 1])
    return out


def _ld_hl_label(rom, label):
    """LD HL, <label address> — gbc_lib's LD_HL_nn only accepts resolved ints, so a forward
    reference to a data-table label (defined later in this same emission pass) needs a manual
    16-bit fixup, the same mechanism ROM._abs() uses for CALL/JP targets."""
    rom.emit(0x21, 0, 0)
    rom.fixups.append((rom.pos - 2, label, 'abs16'))


def _emit_channel_gen(rom, suffix, note_timer, cur_degree, lfsr_state, nr_freq_lo, nr_freq_hi,
                       octave_delta, tempo_mult, stale_count, duty_reg=None, portamento=False,
                       dac_reg=None, dac_on=None, bit_index=None):
    """One channel's note-generation routine: countdown -> (on expiry) LFSR-picked scale-degree
    step -> table lookup -> register write -> timer reload -> IP-0004 stale/onset-window
    bookkeeping. Parameterized so pulse A/B and the wave channel share one Python-level
    implementation (GDS-03 SS1's "one job per file" applied at the routine level, not just the
    file level) even though each emits its own SM83 bytes.

    IP-9010 (BL-0019): dac_reg/dac_on/bit_index gate this channel's frequency/duty writes on
    CHMIX_MASKS[CHMIX_IDX]'s bit_index bit. Stale/onset-window bookkeeping above this check
    always runs regardless of the mix — an excluded channel's internal walk/repetition state
    keeps evolving so it resumes musically-appropriate the moment its mix bit re-enables, per
    the package doc's own task 2. Dissonance scoring (_emit_pairwise_dissonance) deliberately
    still reads every pitched channel's cur_degree unconditionally, mix-excluded or not — a
    documented choice (not the package's alternate "skip excluded channels" option), because
    each channel's own melodic walk keeps evolving while muted (per the paragraph above) and
    letting dissonance scoring track that evolution means a channel that gets re-included lands
    back in a harmonically-current position rather than a stale one frozen at mute-time; this
    trades a small, bounded inaccuracy (a muted channel's silent degree can influence
    BAD_ZONE_FLAGS) for that continuity. Flagged to the backlog, not silently decided."""
    rom.label(f'gen_tick_{suffix}')
    rom.LD_A_nn(note_timer)
    rom.DEC_A()
    rom.LD_nn_A(note_timer)
    rom.OR_A()
    rom.JP_NZ(f'gt_done_{suffix}')

    rom.LD_A_nn(cur_degree)
    rom.LD_D_A()                       # D = old degree (IP-0004 stale-repetition comparison)
    if portamento:
        # IP-1061: stash the pre-onset degree so the trigger write below can start this note at
        # the *old* pitch (retriggered) rather than jumping straight to the new one — arp_tick,
        # which already ran earlier this same frame using the still-old CUR_DEGREE, and which
        # will run again next frame using the now-updated CUR_DEGREE, is what actually carries
        # the pitch the rest of the way to the target — see engine_tick's call order and this
        # routine's own onset write below. ARP_DEGREE_SCRATCH is safe to reuse here: arp_tick's
        # own use of it this frame is already complete by the time gen_tick runs (engine_tick
        # calls arp_tick before gen_tick), and this stash is both written and consumed within
        # this same gen_tick call, before arp_tick touches it again next frame.
        rom.LD_nn_A(ARP_DEGREE_SCRATCH)

    # LFSR step (inlined per-channel so each channel's state stays independent).
    rom.LD_A_nn(lfsr_state)
    rom.SRL_A()
    rom.JR_NC(f'gt_noxor_{suffix}')
    rom.XOR_n(LFSR_POLY)
    rom.label(f'gt_noxor_{suffix}')
    rom.LD_nn_A(lfsr_state)

    rom.AND_n(0x03)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'delta_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_B_A()                       # B = signed delta

    # IP-0007: autonomous bad-zone avoidance/recovery — no user input required (Select is now
    # only a manual override, not the only way out). If DISSONANT, override the LFSR-picked delta
    # with a deterministic pull toward the tonic (degree 0): every channel gravitating toward the
    # same pitch class directly lowers the interval-based dissonance score each tick until it
    # clears. If STUCK and the (possibly-overridden) delta is still 0, force a step so a repeated
    # note can't persist even at the tonic.
    rom.LD_A_nn(BAD_ZONE_FLAGS)
    rom.BIT_b_A(0)
    rom.JR_Z(f'gt_no_dis_{suffix}')
    rom.LD_A_nn(cur_degree)
    rom.OR_A()
    rom.JR_Z(f'gt_dis_zero_{suffix}')
    rom.LD_B_n(0xFF)                   # pull down toward tonic (-1)
    rom.JR(f'gt_no_dis_{suffix}')
    rom.label(f'gt_dis_zero_{suffix}')
    rom.LD_B_n(0x00)                   # already at tonic — hold
    rom.label(f'gt_no_dis_{suffix}')

    rom.LD_A_nn(BAD_ZONE_FLAGS)
    rom.BIT_b_A(1)
    rom.JR_Z(f'gt_no_stuck_{suffix}')
    rom.LD_A_B()
    rom.OR_A()
    rom.JR_NZ(f'gt_no_stuck_{suffix}')
    rom.LD_B_n(0x01)                   # force movement to break the repeat
    rom.label(f'gt_no_stuck_{suffix}')

    rom.LD_A_nn(cur_degree)
    rom.ADD_A_B()
    rom.AND_n(0x07)
    rom.LD_nn_A(cur_degree)

    # IP-0004 (R204 SS4b, MVP-scoped to period-1 repetition only — see BL note in the package
    # doc): same degree as last onset -> increment STALE_COUNT; otherwise reset it to 0.
    rom.CP_D()
    rom.JR_NZ(f'gt_stale_reset_{suffix}')
    rom.LD_A_nn(stale_count)
    rom.INC_A()
    rom.LD_nn_A(stale_count)
    rom.JR(f'gt_stale_done_{suffix}')
    rom.label(f'gt_stale_reset_{suffix}')
    rom.XOR_A()
    rom.LD_nn_A(stale_count)
    rom.label(f'gt_stale_done_{suffix}')

    # IP-0004: this is an onset event — count it toward the channel-overload window.
    rom.LD_A_nn(ONSET_WINDOW_COUNT)
    rom.INC_A()
    rom.LD_nn_A(ONSET_WINDOW_COUNT)

    # IP-9010 (BL-0019): channel-mix gating. Test CHMIX_MASKS[CHMIX_IDX]'s bit for this channel
    # *before* computing the note-table address (HL is free here — the table-address computation
    # below needs it fresh regardless of which branch is taken, so no stash/restore is needed).
    # Muted: force this channel's DAC/envelope off (guarantees NR52 reads inactive within this
    # same onset, not merely "stopped retriggering" — the package doc's own non-negotiable DoD
    # point) and skip straight to the timer-reload section, bypassing the frequency/duty writes
    # entirely. Active: restore this channel's boot-time DAC/envelope value (idempotent if it was
    # already on) and fall through into the existing note-table addressing/write code unchanged.
    if dac_reg is not None:
        rom.LD_A_nn(CHMIX_IDX)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'chmix_masks_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()
        rom.BIT_b_A(bit_index)
        rom.JR_Z(f'gt_muted_{suffix}')
        rom.LD_A_n(dac_on)
        rom.LDH_n_A(dac_reg)
        rom.JR(f'gt_unmuted_{suffix}')
        rom.label(f'gt_muted_{suffix}')
        rom.XOR_A()
        rom.LDH_n_A(dac_reg)
        rom.JR(f'gt_reload_{suffix}')
        rom.label(f'gt_unmuted_{suffix}')

    # effective_octave = OCTAVE_IDX (+ octave_delta, floored at 0); table_idx = SCALE_IDX*4 + that
    rom.LD_A_nn(SCALE_IDX)
    rom.ADD_A_A(); rom.ADD_A_A()
    rom.LD_B_A()
    rom.LD_A_nn(OCTAVE_IDX)
    if octave_delta == -1:
        rom.OR_A()
        rom.JR_Z(f'gt_oct0_{suffix}')
        rom.DEC_A()
        rom.label(f'gt_oct0_{suffix}')
    rom.ADD_A_B()
    rom.ADD_A_A()                      # *2 -> pointer-table byte offset
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'ptr_table')
    rom.ADD_HL_BC()
    rom.LD_E_HL(); rom.INC_HL(); rom.LD_D_HL()
    rom.LD_H_D(); rom.LD_L_E()          # HL = the (scale, octave) note table's own address

    # IP-1061: portamento channels trigger this onset at the *old* degree (identical to the new
    # one when the degree didn't change, so this is safe unconditionally) — arp_tick carries the
    # pitch the rest of the way to the new target over the following frame(s), per this routine's
    # own portamento stash above.
    rom.LD_A_nn(ARP_DEGREE_SCRATCH if portamento else cur_degree)
    rom.ADD_A_A()                      # *2 (2 bytes/entry)
    rom.LD_C_A(); rom.LD_B_n(0)
    rom.ADD_HL_BC()
    rom.LD_A_HL(); rom.LDH_n_A(nr_freq_lo)
    rom.INC_HL()
    rom.LD_A_HL(); rom.LDH_n_A(nr_freq_hi)

    # IP-1060: duty-cycle variation (R216) — pulse A/B only (duty_reg is None for the wave
    # channel, which has no duty concept). Re-reads cur_degree fresh rather than reusing the
    # value already consumed above, since it was not preserved in a register across the
    # intervening table-lookup arithmetic.
    if duty_reg is not None:
        rom.LD_A_nn(cur_degree)
        rom.AND_n(0x03)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'duty_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()
        rom.LDH_n_A(duty_reg)

    if dac_reg is not None:
        rom.label(f'gt_reload_{suffix}')

    # Reload the timer from the tempo table (doubled for a half-rate channel, e.g. the wave bass).
    rom.LD_A_nn(TEMPO_IDX)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'tempo_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    if tempo_mult == 2:
        rom.ADD_A_A()

    # IP-0007: OVERLOAD recovery — space this channel's onsets out further (double the reload
    # again) so the rolling onset-window count naturally drops below threshold on its own,
    # without needing Select.
    rom.LD_B_A()
    rom.LD_A_nn(BAD_ZONE_FLAGS)
    rom.BIT_b_A(2)
    rom.JR_Z(f'gt_no_overload_slow_{suffix}')
    rom.LD_A_B()
    rom.ADD_A_A()
    rom.LD_B_A()
    rom.label(f'gt_no_overload_slow_{suffix}')
    rom.LD_A_B()
    rom.LD_nn_A(note_timer)

    rom.label(f'gt_done_{suffix}')
    rom.RET()


def _emit_arpeggio_tick(rom, suffix, arp_state, cur_degree, nr_freq_lo, nr_freq_hi):
    """IP-1060 arpeggio + IP-1061 vibrato, R216: runs every frame, independent of the channel's
    own note-timer. Packed arp_state byte: bits0-3 arpeggio sub-tick countdown, bits4-5 arpeggio
    step (0-3, wraps via AND 0x30), bits6-7 vibrato phase (0-3, advances every frame via a plain
    ADD 0x40 — 2 bits overflow harmlessly out of the byte with no effect on bits0-5). The
    chord-tone step only *advances* on sub-tick expiry, but the frequency register is *rewritten*
    every frame regardless (vibrato needs every-frame updates even between arpeggio steps) —
    arpeggio's own base note (from the current step) plus vibrato's tiny +-1 low-byte wobble
    (phase 0 -> +1, phase 2 -> -1, phases 1/3 -> no change; a deliberate scope reduction from a
    true frequency-domain LFO, R216's own description — the SM83 opcode set this project uses has
    no ADC/SBC for safe multi-byte carry-chain arithmetic beyond single ±1 steps, so the wobble is
    kept to the smallest safe unit; an octave-boundary low-byte wrap without a hi-byte carry is a
    rare, self-healing one-frame edge case, same character as BL-0015's already-accepted
    COMBINED-bit transient) are combined into one write, with the trigger bit clear (no
    retrigger) so envelope/duty continue undisturbed — same non-retriggering technique as
    IP-1060's original arpeggio-only write."""
    rom.label(f'arp_tick_{suffix}')

    # Vibrato phase advances every frame, unconditionally (bits6-7).
    rom.LD_A_nn(arp_state)
    rom.ADD_A_n(0x40)
    rom.LD_nn_A(arp_state)

    # Arpeggio countdown/step: the step only advances on sub-tick expiry; the write below always
    # happens regardless of which branch runs.
    rom.LD_A_nn(arp_state)
    rom.DEC_A()
    rom.LD_nn_A(arp_state)
    rom.AND_n(0x0F)
    rom.JP_NZ(f'arp_no_advance_{suffix}')

    rom.LD_A_nn(arp_state)
    rom.AND_n(0xC0)                    # keep vibrato-phase bits, drop the just-zeroed countdown
    rom.LD_D_A()                       # D = vibrato-phase bits (stashed across the OR below)
    rom.LD_A_nn(arp_state)
    rom.ADD_A_n(0x10)
    rom.AND_n(0x30)                    # A = new_step << 4 (wrapped 3->0)
    rom.OR_D()                         # combine with the stashed vibrato-phase bits
    rom.OR_n(ARP_SUBTICK_RELOAD)
    rom.LD_nn_A(arp_state)
    rom.label(f'arp_no_advance_{suffix}')

    # Compute this frame's base note from the *current* step (freshly read — whether or not it
    # just advanced above) and CUR_DEGREE.
    rom.LD_A_nn(arp_state)
    rom.AND_n(0x30)
    rom.SRL_A(); rom.SRL_A(); rom.SRL_A(); rom.SRL_A()   # A = current step (0-3)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'arpeggio_offsets_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()                      # A = ARPEGGIO_OFFSETS[step]
    rom.LD_B_A()
    rom.LD_A_nn(cur_degree)
    rom.ADD_A_B()
    rom.AND_n(0x07)
    rom.LD_nn_A(ARP_DEGREE_SCRATCH)    # stash effective_degree (D/E about to be reused below)

    # (scale, octave) note-table base address -> HL, same pattern as _emit_channel_gen's own
    # lookup, octave_delta=0 always (only pulse A/B arpeggiate, neither has an octave offset).
    rom.LD_A_nn(SCALE_IDX)
    rom.ADD_A_A(); rom.ADD_A_A()
    rom.LD_B_A()
    rom.LD_A_nn(OCTAVE_IDX)
    rom.ADD_A_B()
    rom.ADD_A_A()
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'ptr_table')
    rom.ADD_HL_BC()
    rom.LD_E_HL(); rom.INC_HL(); rom.LD_D_HL()
    rom.LD_H_D(); rom.LD_L_E()

    rom.LD_A_nn(ARP_DEGREE_SCRATCH)
    rom.ADD_A_A()
    rom.LD_C_A(); rom.LD_B_n(0)
    rom.ADD_HL_BC()
    rom.LD_A_HL(); rom.LD_E_A()        # E = base lo byte (not written yet — vibrato may adjust it)
    rom.INC_HL()
    rom.LD_A_HL()
    rom.AND_n(0x07)                    # clear the trigger bit and any unused high bits
    rom.LD_D_A()                       # D = base hi byte (0-7)

    # IP-1061 vibrato: read the phase bits fresh and apply the +-1/none adjustment to E (lo),
    # carrying into D (hi) only on an actual 8-bit overflow/underflow (JP_C/JP_NC-gated, exact
    # SM83 carry/borrow semantics — not a two's-complement guess).
    rom.LD_A_nn(arp_state)
    rom.AND_n(0xC0)
    rom.JP_Z(f'vib_up_{suffix}')
    rom.CP_n(0x80)
    rom.JP_Z(f'vib_down_{suffix}')
    rom.JP(f'vib_write_{suffix}')

    rom.label(f'vib_up_{suffix}')
    rom.LD_A_E()
    rom.ADD_A_n(1)
    rom.LD_E_A()
    rom.JP_NC(f'vib_write_{suffix}')
    rom.LD_A_D(); rom.INC_A(); rom.LD_D_A()
    rom.JP(f'vib_write_{suffix}')

    rom.label(f'vib_down_{suffix}')
    rom.LD_A_E()
    rom.SUB_n(1)
    rom.LD_E_A()
    rom.JP_NC(f'vib_write_{suffix}')
    rom.LD_A_D(); rom.DEC_A(); rom.LD_D_A()

    rom.label(f'vib_write_{suffix}')
    rom.LD_A_E(); rom.LDH_n_A(nr_freq_lo)
    rom.LD_A_D(); rom.AND_n(0x07); rom.LDH_n_A(nr_freq_hi)
    rom.RET()


def _emit_noise_gen(rom):
    """Noise channel (IP-0003, R115/R202): a fixed 16-step Euclidean pattern, k selected by
    DENSITY_IDX, gates short percussive noise hits. No LFSR/pitch walk — the noise channel has
    no frequency register (R108/R115); its only generative axis here is onset timing."""
    rom.label('gen_tick_nz')
    rom.LD_A_nn(NOTE_TIMER_NZ)
    rom.DEC_A()
    rom.LD_nn_A(NOTE_TIMER_NZ)
    rom.OR_A()
    rom.JP_NZ('gt_done_nz')

    rom.LD_A_nn(NOISE_STEP_IDX)
    rom.INC_A()
    rom.AND_n(0x0F)
    rom.LD_nn_A(NOISE_STEP_IDX)

    # pattern_table offset = DENSITY_IDX*16 + NOISE_STEP_IDX
    rom.LD_B_A()                       # B = step_idx
    rom.LD_A_nn(DENSITY_IDX)
    rom.SLA_A(); rom.SLA_A(); rom.SLA_A(); rom.SLA_A()   # *16
    rom.ADD_A_B()
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'noise_pattern_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_D_A()                       # D = this step's pattern-hit bit, stashed (IP-9010 needs
                                        # A/B/C/HL free below for the CHMIX_MASKS lookup)

    # IP-9010 (BL-0019): channel-mix gating, noise's bit3. Muted: force NR42's DAC off
    # (guarantees NR52 reads inactive within this same note-cycle even if a previous hit left the
    # channel playing/decaying) and skip the hit check entirely — no phantom onset counted for a
    # channel that made no sound. Active: fall through to the existing pattern-hit logic
    # unchanged, using the stashed pattern bit in D.
    rom.LD_A_nn(CHMIX_IDX)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'chmix_masks_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.BIT_b_A(3)
    rom.JR_Z('gt_nz_muted')

    rom.LD_A_D()
    rom.OR_A()
    rom.JR_Z('gt_nz_no_hit')

    rom.LD_A_n(0xF2); rom.LDH_n_A(NR42)   # volume 15, decreasing envelope, fast period (percussive)
    rom.LD_A_n(0x41); rom.LDH_n_A(NR43)   # clock shift 4, 15-bit ("hiss") width, divisor 1
    rom.LD_A_n(0xC0); rom.LDH_n_A(NR44)   # trigger, length disabled

    # IP-0004: an actual noise hit (not just a step advance) is an onset event too.
    rom.LD_A_nn(ONSET_WINDOW_COUNT)
    rom.INC_A()
    rom.LD_nn_A(ONSET_WINDOW_COUNT)

    rom.JR('gt_nz_no_hit')
    rom.label('gt_nz_muted')
    rom.XOR_A(); rom.LDH_n_A(NR42)         # force DAC off — guarantee inactive in NR52
    rom.label('gt_nz_no_hit')
    rom.LD_A_nn(TEMPO_IDX)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'noise_step_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()

    # IP-0007: OVERLOAD recovery, same mechanism as the pitched channels.
    rom.LD_B_A()
    rom.LD_A_nn(BAD_ZONE_FLAGS)
    rom.BIT_b_A(2)
    rom.JR_Z('gt_nz_no_overload_slow')
    rom.LD_A_B()
    rom.ADD_A_A()
    rom.LD_B_A()
    rom.label('gt_nz_no_overload_slow')
    rom.LD_A_B()
    rom.LD_nn_A(NOTE_TIMER_NZ)

    rom.label('gt_done_nz')
    rom.RET()


def _emit_get_semitone(rom, cur_degree_addr, dest_addr):
    """semitone = SEMITONE_TABLE[SCALE_IDX*8 + cur_degree], stored to dest_addr (IP-0004)."""
    rom.LD_A_nn(SCALE_IDX)
    rom.SLA_A(); rom.SLA_A(); rom.SLA_A()   # *8
    rom.LD_B_A()
    rom.LD_A_nn(cur_degree_addr)
    rom.ADD_A_B()
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'semitone_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_nn_A(dest_addr)


def _emit_pairwise_dissonance(rom, semi_a_addr, semi_b_addr, suffix):
    """Interval class (0-6, inversions folded) between two semitone scratch values, weighted
    via DISSONANCE_WEIGHT_BY_IC and accumulated into DISSONANCE_SCORE (IP-0004, R204)."""
    rom.LD_A_nn(semi_b_addr)
    rom.LD_C_A()
    rom.LD_A_nn(semi_a_addr)
    rom.SUB_C()                        # A = semi_a - semi_b (mod 256)
    rom.JR_NC(f'dt_nowrap_{suffix}')
    rom.ADD_A_n(12)
    rom.label(f'dt_nowrap_{suffix}')
    rom.CP_n(7)                        # fold >6 to its complement (interval-class simplification)
    rom.JR_C(f'dt_nofold_{suffix}')
    rom.LD_B_A()
    rom.LD_A_n(12)
    rom.SUB_B()
    rom.label(f'dt_nofold_{suffix}')
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'dissonance_weight_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_B_A()
    rom.LD_A_nn(DISSONANCE_SCORE)
    rom.ADD_A_B()
    rom.LD_nn_A(DISSONANCE_SCORE)


def _emit_badzone_tick(rom):
    """Recomputes DISSONANCE_SCORE (3 pitched-channel pairs), evaluates the STUCK condition
    (any channel's STALE_COUNT over threshold), manages the rolling onset-overload window, and
    combines all three into BAD_ZONE_FLAGS bit3 (IP-0004, GDS-03 SS4)."""
    rom.label('badzone_tick')
    rom.XOR_A(); rom.LD_nn_A(DISSONANCE_SCORE)

    _emit_get_semitone(rom, CUR_DEGREE_PA, SEMI_PA)
    _emit_get_semitone(rom, CUR_DEGREE_PB, SEMI_PB)
    _emit_get_semitone(rom, CUR_DEGREE_WV, SEMI_WV)
    _emit_pairwise_dissonance(rom, SEMI_PA, SEMI_PB, 'papb')
    _emit_pairwise_dissonance(rom, SEMI_PA, SEMI_WV, 'pawv')
    _emit_pairwise_dissonance(rom, SEMI_PB, SEMI_WV, 'pbwv')

    # bit0 DISSONANT
    rom.LD_A_nn(DISSONANCE_SCORE)
    rom.CP_n(DISSONANCE_THRESHOLD + 1)
    rom.JR_C('bz_not_dissonant')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.OR_n(0x01); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.JR('bz_dissonant_done')
    rom.label('bz_not_dissonant')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.AND_n(0xFE); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.label('bz_dissonant_done')

    # bit1 STUCK — any channel's STALE_COUNT over threshold
    for stale_addr in (STALE_COUNT_PA, STALE_COUNT_PB, STALE_COUNT_WV):
        rom.LD_A_nn(stale_addr)
        rom.CP_n(STALE_THRESHOLD + 1)
        rom.JR_NC('bz_stuck_yes')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.AND_n(0xFD); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.JR('bz_stuck_done')
    rom.label('bz_stuck_yes')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.OR_n(0x02); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.label('bz_stuck_done')

    # bit2 OVERLOAD — rolling window: evaluate + reset only when the window elapses
    rom.LD_A_nn(ONSET_WINDOW_TICK_CTR)
    rom.DEC_A()
    rom.LD_nn_A(ONSET_WINDOW_TICK_CTR)
    rom.OR_A()
    rom.JR_NZ('bz_window_done')

    rom.LD_A_nn(ONSET_WINDOW_COUNT)
    rom.CP_n(OVERLOAD_THRESHOLD + 1)
    rom.JR_C('bz_no_overload')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.OR_n(0x04); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.JR('bz_overload_done')
    rom.label('bz_no_overload')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.AND_n(0xFB); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.label('bz_overload_done')

    rom.XOR_A(); rom.LD_nn_A(ONSET_WINDOW_COUNT)
    rom.LD_A_n(ONSET_WINDOW_FRAMES); rom.LD_nn_A(ONSET_WINDOW_TICK_CTR)
    rom.label('bz_window_done')

    # bit3 COMBINED = bit0 OR bit1 OR bit2
    rom.LD_A_nn(BAD_ZONE_FLAGS)
    rom.AND_n(0x07)
    rom.JR_Z('bz_combined_clear')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.OR_n(0x08); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.JR('bz_combined_done')
    rom.label('bz_combined_clear')
    rom.LD_A_nn(BAD_ZONE_FLAGS); rom.AND_n(0xF7); rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.label('bz_combined_done')
    rom.RET()


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
    for (suffix, note_timer, cur_degree, lfsr_state, lfsr_seed, *_rest, duty_reg,
         arp_state, _dac_reg, _dac_on, _bit_index) in CHANNELS:
        rom.XOR_A(); rom.LD_nn_A(cur_degree)
        rom.LD_A_n(1); rom.LD_nn_A(note_timer)     # fire the first note on the very next tick
        # IP-0007: randomize each channel's melodic walk seed from the free-running DIV
        # register (R213 SS5) XORed with a fixed per-channel constant (so channels still
        # decorrelate from each other even on the rare frame DIV reads identically) — this is
        # the "randomize" half of Select's reset/randomize role (GDS-03 SS5 amended). A Galois
        # LFSR must never be seeded to 0 (it would stay 0 forever), so a zero result is forced
        # to a fixed nonzero fallback.
        rom.LDH_A_n(DIV)
        rom.XOR_n(lfsr_seed)
        rom.OR_A()
        rom.JR_NZ(f'ie_seed_ok_{suffix}')
        rom.LD_A_n(1)
        rom.label(f'ie_seed_ok_{suffix}')
        rom.LD_nn_A(lfsr_state)
        # IP-1060: reset arpeggio state — countdown reloaded (not zeroed, avoiding an
        # underflow-on-first-tick edge case the way NOTE_TIMER's own "prime to 1" convention
        # already avoids it), step index back to 0.
        if arp_state is not None:
            rom.LD_A_n(ARP_SUBTICK_RELOAD); rom.LD_nn_A(arp_state)
    rom.XOR_A(); rom.LD_nn_A(NOISE_STEP_IDX)
    rom.LD_A_n(1); rom.LD_nn_A(NOTE_TIMER_NZ)

    # IP-0004: bad-zone state starts clean — no dissonance/stuck/overload carried across a reset.
    rom.XOR_A()
    rom.LD_nn_A(BAD_ZONE_FLAGS)
    rom.LD_nn_A(DISSONANCE_SCORE)
    rom.LD_nn_A(STALE_COUNT_PA)
    rom.LD_nn_A(STALE_COUNT_PB)
    rom.LD_nn_A(STALE_COUNT_WV)
    rom.LD_nn_A(ONSET_WINDOW_COUNT)
    rom.LD_A_n(ONSET_WINDOW_FRAMES)
    rom.LD_nn_A(ONSET_WINDOW_TICK_CTR)
    rom.RET()

    # ── engine_tick: called once per frame from the main loop ────────
    # IP-1061: arp_tick runs BEFORE gen_tick, deliberately — on an onset frame this means
    # arp_tick still sees the pre-onset CUR_DEGREE (writing the outgoing note's continued
    # arpeggio/vibrato), then gen_tick's own onset write lands last this frame using the *old*
    # degree (portamento's retrigger start point, see _emit_channel_gen's own comment); next
    # frame, arp_tick runs first again, now seeing the just-updated CUR_DEGREE, carrying the
    # pitch the rest of the way to the new target. This ordering is what actually produces the
    # multi-frame glide — reordering these two calls would collapse it back to an instant jump.
    rom.label('engine_tick')
    for (suffix, *_rest, duty_reg, arp_state, _dac_reg, _dac_on, _bit_index) in CHANNELS:
        if arp_state is not None:
            rom.CALL(f'arp_tick_{suffix}')
    for (suffix, *_rest) in CHANNELS:
        rom.CALL(f'gen_tick_{suffix}')
    rom.CALL('gen_tick_nz')
    rom.CALL('badzone_tick')
    rom.RET()

    for (suffix, note_timer, cur_degree, lfsr_state, _seed, nr_lo, nr_hi, oct_delta, tempo_mult,
         stale_count, duty_reg, arp_state, dac_reg, dac_on, bit_index) in CHANNELS:
        _emit_channel_gen(rom, suffix, note_timer, cur_degree, lfsr_state, nr_lo, nr_hi,
                           oct_delta, tempo_mult, stale_count, duty_reg,
                           portamento=(arp_state is not None),
                           dac_reg=dac_reg, dac_on=dac_on, bit_index=bit_index)
        if arp_state is not None:
            _emit_arpeggio_tick(rom, suffix, arp_state, cur_degree, nr_lo, nr_hi)
    _emit_noise_gen(rom)
    _emit_badzone_tick(rom)

    # ── Data tables ───────────────────────────────────────────────────
    rom.label('delta_table')
    rom.emit(*DELTA_TABLE)

    rom.label('tempo_table')
    rom.emit(*TEMPO_TABLE)

    rom.label('noise_step_table')
    rom.emit(*NOISE_STEP_TABLE)

    rom.label('noise_pattern_table')
    for k in DENSITY_K:
        rom.emit(*_euclidean_pattern(k))

    rom.label('semitone_table')
    rom.emit(*SEMITONE_TABLE_DATA)

    rom.label('dissonance_weight_table')
    rom.emit(*DISSONANCE_WEIGHT_BY_IC)

    rom.label('wave_table')
    rom.emit(*_wave_table_bytes())

    rom.label('arpeggio_offsets_table')
    rom.emit(*ARPEGGIO_OFFSETS)

    rom.label('duty_table')
    rom.emit(*DUTY_BY_DEGREE)

    rom.label('chmix_masks_table')
    rom.emit(*CHMIX_MASKS)

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
