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
from wram_constants import (TEMPO_IDX, OCTAVE_IDX, SCALE_IDX, DENSITY_IDX, CHMIX_IDX,
                             BAD_ZONE_FLAGS, PRESET_TEMPO_IDX, PRESET_OCTAVE_IDX,
                             PRESET_SCALE_IDX, PRESET_DENSITY_IDX, PRESET_CHMIX_IDX)

# ── WRAM addresses (GDS-07) ──────────────────────────────────────────
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

# IP-0004: bad-zone state (GDS-07 SS2) — BAD_ZONE_FLAGS imported above (IP-8020, BL-0065)
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

# IP-1070: Scheme E (combinable generation schemes, BL-0020/ADS-100) per-channel motif-step
# scratch, one byte per pitched channel — tracks each channel's current position (0-7) in its
# assigned motif when running Scheme E. Placed at 0xC038-0xC03A: confirmed free against GDS-07 —
# 0xC020-0xC037 is the reserved-but-unused ring-buffer range (BL-0013), not touched; 0xC038-0xC04F
# is genuine unused headroom before JOY_PREV at 0xC050.
MOTIF_STEP_PA = 0xC038
MOTIF_STEP_PB = 0xC039
MOTIF_STEP_WV = 0xC03A

# IP-1080: Genre-aware style presets (roadmap R5, ADS-101) — a per-style duty-cycle timbre
# offset, added to the existing (cur_degree & 0x03) duty-table index at the duty-write site
# below, then re-masked (wrap, not clamp). Placed at 0xC03B: 0xC038-0xC03A is IP-1070's
# MOTIF_STEP_PA/PB/WV; 0xC03B-0xC04F remains genuine unused headroom before JOY_PREV at 0xC050.
DUTY_BIAS = 0xC03B

# IP-1090 (BL-0010, ADS-102): which row of the now-multi-variant MOTIF_TABLE is currently active
# for Scheme E's motif lookup — a single shared byte (v1 scope: today's only shipped Scheme-E-
# assigning preset activates the scheme on exactly one channel at a time, ADS-102 SS9). Placed at
# 0xC03C: 0xC03B is IP-1080's DUTY_BIAS; 0xC03C-0xC04F remains genuine unused headroom before
# JOY_PREV at 0xC050.
MOTIF_VARIANT_IDX = 0xC03C

# IP-1100 (roadmap R6, ADS-103): autonomous song-form phase-cycling state — which of SONG_TABLE's
# 4 phases is active, and how many frames remain in it (16-bit, to reach genuinely multi-minute
# phase durations without an awkward sub-frame-counting workaround). Placed at 0xC03D-0xC03F:
# 0xC03C is IP-1090's MOTIF_VARIANT_IDX; 0xC03D-0xC04F remains genuine unused headroom before
# JOY_PREV at 0xC050.
SONG_STATE = 0xC03D
SONG_STATE_TIMER_LO = 0xC03E
SONG_STATE_TIMER_HI = 0xC03F

# IP-1120 (roadmap R7, ADS-105/FS-112): derived valence-arousal mood pair, recomputed only at the
# 6 write sites that can change TEMPO_IDX/DENSITY_IDX/SCALE_IDX (never per-frame -- NFR-1170's
# zero-added-per-frame-cost contract, a direct response to IP-9030's VBlank-budget measurement).
# No visualizer/input consumer yet -- groundwork for roadmap R9, separately blocked.
AROUSAL = 0xC068
VALENCE = 0xC069

# IP-1120: VALENCE is a fixed lookup keyed by SCALE_IDX (0-3) -- a lookup table is definitionally
# a fixed one-to-one mapping (FR-1400). Illustrative first-guess placement values, not tuned by
# ear (BL-0005-class deferral, same as every other untuned preset/threshold this project has
# shipped) -- a future 09-content-review pass, once R9 gives this a real consumer, is the right
# place to retune.
VALENCE_TABLE = [10, 6, 12, 4]

# IP-0004 thresholds (GDS-03 SS4, R204 SS5) — first-guess placeholders, per BL-0005's own
# deferred-tuning convention; the dissonance weight table itself is literature-grounded (R204),
# these threshold *numbers* are not yet tuned by ear.
DISSONANCE_THRESHOLD = 20      # ~60% of the 3-pair theoretical max (3 * 15 = 45)
STALE_THRESHOLD = 8            # consecutive same-degree repeats (period-1 only, MVP scope)
# IP-9020 (BL-0017): OVERLOAD_THRESHOLD=20 was mathematically unreachable — VR-0007 computed the
# engine's own *average* onset-rate ceiling (2*(W/tempo_reload) [pa+pb] + W/(2*tempo_reload)
# [wave, half-rate] + (W/noise_step_interval)/16*density_k [noise]) across the full tempo/density
# preset grid: 3.17 at the default preset (tempo=4, density=0) up to 8.8 at the absolute max
# (tempo=7, density=7) — every combination stays under 9, so 20 could never fire. That average-
# rate formula understates the real *peak* count a fixed, window-aligned counter can see, though:
# deterministic periodic onsets can phase-align near a window boundary and briefly double up, so
# this package empirically measured the actual peak ONSET_WINDOW_COUNT (not just the analytical
# average) across representative presets before picking a value — default peaks at 6 (not the
# ~3 the average formula suggests), a realistic-high (not maximal) tempo=6/density=5 combination
# peaks at 8, and the absolute max peaks at 11. Recalibrated to 7 (triggers when the count
# exceeds it, i.e. reaches 8): comfortably above the default preset's own empirically-measured
# peak (no spurious triggering), reachable at realistic-high combinations well short of the
# absolute max, per the package's "reachable during genuinely dense play" goal.
OVERLOAD_THRESHOLD = 7         # onset events within the ONSET_WINDOW_FRAMES window
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
# PRESET_* values imported above (IP-8020, BL-0065).

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
# order, per BL-0019/IP-9010's package doc), scheme_bit (IP-1070: this channel's Scheme-select bit
# in CHMIX_MASKS's spare bits 4-6 — pa=4, pb=5, wv=6, per ADS-100 SS2/ADR-0001), scheme_state
# (IP-1070: packed per-channel WRAM byte — bits0-3 this channel's own Euclidean-pattern step
# (0-15, independent of the noise channel's own NOISE_STEP_IDX), bits4-6 its current motif step
# (0-7); bit7 unused)
CHANNELS = [
    ('pa', NOTE_TIMER_PA, CUR_DEGREE_PA, LFSR_STATE,    LFSR_SEED_PA, NR13, NR14, 0, 1, STALE_COUNT_PA, NR11, ARP_STATE_PA, NR12, 0xF3, 0, 4, MOTIF_STEP_PA),
    ('pb', NOTE_TIMER_PB, CUR_DEGREE_PB, LFSR_STATE_PB, LFSR_SEED_PB, NR23, NR24, 0, 1, STALE_COUNT_PB, NR21, ARP_STATE_PB, NR22, 0xF3, 1, 5, MOTIF_STEP_PB),
    # Wave channel: bass/timbre role (R207 finding, BL-0008) — anchored one octave index lower
    # (floored at 0) and half the note rate (tempo_mult=2), matching bass lines moving less often
    # than melody. The wave-channel frequency formula is itself one octave lower than the pulse
    # formula for an identical register value (R108/R114), so reusing the pulse note tables
    # as-is on NR33/NR34 gives an *additional* free octave drop on top of the octave_delta below.
    # No duty cycle (wave has no duty concept) and no arpeggio (IP-1060: keeps its plain
    # sustained bass role rather than fast pitch-cycling, a deliberate scope choice). Wave DOES
    # get Scheme E (IP-1070) — ADS-100's own example names a Scheme-E wave bass motif explicitly.
    ('wv', NOTE_TIMER_WV, CUR_DEGREE_WV, LFSR_STATE_WV, LFSR_SEED_WV, NR33, NR34, -1, 2, STALE_COUNT_WV, None, None, NR30, 0x80, 2, 6, MOTIF_STEP_WV),
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
# IP-1070 (BL-0020): bits 4-6 (spare in every preset above) now carry per-channel Scheme-select
# bits (pa=bit4, pb=bit5, wv=bit6; 0=Scheme W, 1=Scheme E) — packed into the same byte per
# ADR-0001, at zero additional preset-table cost. Preset 6 assigns Scheme E to the wave channel
# (bit6 set) alongside pulse A/B still on Scheme W — ADS-100 SS4's own worked example ("a wave
# channel on Scheme E reads as a recognizable repeating bass motif against pulse A/B's freer
# Scheme-W drift"). Every other preset leaves bits4-6 clear (all-Scheme-W) — first-guess
# placeholder assignment, not tuned by ear, same convention as every other untuned preset data
# (BL-0005's disposition covers this). Preset 0 (boot/Select default) MUST stay all-Scheme-W
# (bits4-6 clear) — FS-107's own State Changes field requires no regression to the shipped
# default listening experience.
CHMIX_MASKS = [
    0b1111,  # 0: all four active, all Scheme W (preset default — required, see above)
    0b0011,  # 1: pulse A + pulse B (GDS-03 SS3's own example)
    0b0101,  # 2: pulse A + wave
    0b1001,  # 3: pulse A + noise
    0b0110,  # 4: pulse B + wave
    0b1100,  # 5: wave + noise
    0b1000111,  # 6: pulse A + pulse B + wave active; wave on Scheme E (bit6 set)
    0b1011,  # 7: pulse A + pulse B + noise (no wave)
]

# IP-1080: Genre-aware style presets (roadmap R5, ADS-101/FS-108) — a second table, independent
# of CHMIX_MASKS above (ADS-101 SS2's "two tables stay independent" design), keyed by the same
# CHMIX_IDX index. Each row: (tempo_idx, density_idx, scale_idx, duty_bias). Applied immediately
# (not gated to next onset, unlike CHMIX_MASKS's channel-mix/scheme half — FR-1240) by
# _emit_apply_style, called right after CHMIX_IDX is stepped on a Start press.
# Index 0 MUST match the shipped default preset exactly (PRESET_TEMPO_IDX/PRESET_SCALE_IDX/
# PRESET_DENSITY_IDX, duty_bias=0) — FR-1260, no regression to current boot/reset behavior.
# Indices 1-3 carry the three named v1 styles (FR-1250, ADS-101 SS3, first-guess placeholder
# values per this project's standing untuned-preset convention, BL-0005):
#   1: Techno/Chiptune-Driving — fast tempo, dense Euclidean percussion, dorian mode, bright duty.
#   2: Ambient/Lo-Fi — slow tempo, sparse density, pentatonic mode, soft duty (the "anchor" style,
#      deliberately closest to the shipped default's overall character).
#   3: Holiday — moderate tempo, moderate-steady density, major mode, bright duty (R219 SS8's
#      "cheapest genre-style addition" finding: major/moderate-tempo/steady-density/bright-timbre
#      all map directly onto these four fields).
# Indices 4-7 default to index 0's row until a future content-authoring pass assigns a 4th+ style
# (BL-0039) — every index has a defined, non-arbitrary row, not an unreviewed combination.
STYLE_TABLE = [
    (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, 0x00),  # 0: default
    (6, 6, 2, 0x01),                                                 # 1: Techno/Chiptune-Driving
    (1, 0, 3, 0xFF),                                                 # 2: Ambient/Lo-Fi
    (3, 3, 0, 0x01),                                                 # 3: Holiday
    (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, 0x00),  # 4: default (unassigned)
    (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, 0x00),  # 5: default (unassigned)
    (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, 0x00),  # 6: default (unassigned)
    (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, 0x00),  # 7: default (unassigned)
]

# IP-1100 (roadmap R6, ADS-103): autonomous song-form phase table — 4 rows of (tempo_idx,
# density_idx, duration_lo, duration_hi), duration in frames (16-bit, ~60fps) so a full cycle
# genuinely spans multiple minutes per R6's own framing. First-guess placeholder values/durations,
# not tuned by ear (BL-0005's standing disposition). IP-1100's own explicit decision (package
# Implementation Task 5), REVISED from this package's own initial draft after discovering it broke
# 10 pre-existing tests that assume boot/Select-reset lands exactly on PRESET_TEMPO_IDX/
# PRESET_DENSITY_IDX: phase 0 (INTRO) DOES match the shipped default preset exactly — the same
# no-regression discipline STYLE_TABLE/MOTIF_TABLE's own index-0 rows already established, applied
# here too rather than treated as an exception.
SONG_TABLE = [
    (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, 1800 & 0xFF, (1800 >> 8) & 0xFF),  # 0: INTRO (matches shipped default) - ~30s
    (4, 4, 1800 & 0xFF, (1800 >> 8) & 0xFF),  # 1: BUILD - 120 BPM, k=6, ~30s
    (6, 6, 1200 & 0xFF, (1200 >> 8) & 0xFF),  # 2: PEAK  - 160 BPM, k=10, ~20s
    (3, 2, 1800 & 0xFF, (1800 >> 8) & 0xFF),  # 3: BREAKDOWN - 105 BPM, k=4, ~30s
]
N_SONG_PHASES = 4

# IP-1060: arpeggio-as-polyphony (R216) — a period-4 up/down offset pattern (root, third, fifth,
# third, within the active scale's 8-degree table) avoids needing a mod-3 counter (SM83 has no
# division; a period-4 cycle wraps with a plain AND, R302). First-guess placeholder rate/shape,
# not tuned by ear (BL-0005's existing disposition covers this).
ARPEGGIO_OFFSETS = [0, 2, 4, 2]
ARP_SUBTICK_RELOAD = 6  # frames per chord-tone

# IP-1060: duty-cycle variation (R216) — NR11/NR21 whole-byte values (length bits stay 0, unused,
# same as the existing fixed-duty boot init), one per CUR_DEGREE mod 4.
DUTY_BY_DEGREE = [0x00, 0x40, 0x80, 0xC0]  # 12.5% / 25% / 50% / 75%

# IP-1070 (BL-0020, ADS-100 SS5): Scheme E's fixed motif — one shared 8-entry table of *absolute*
# scale-degree targets (0-7, not deltas), a short recognizable up/down phrase distinct from
# ARPEGGIO_OFFSETS' period-4 chord pattern. Absolute targets (rather than deltas) keep the
# on-device math a plain SUB (target - old_degree, wrapping mod 256, then masked mod 8 exactly
# like every other degree write) instead of needing signed accumulation across steps. One shared
# table for all 3 pitched channels (not per-channel/per-scale-degree-set) — FR-1210 requires only
# "a fixed... motif," not multiple selectable ones; a right-sized first version, not a ceiling.
# First-guess placeholder shape, not tuned by ear (BL-0005's existing disposition covers this).
#
# IP-1090 (BL-0010, ADS-102): extended from a single 8-entry row into N_VARIANTS=4 rows of 8
# bytes each (variant index * 8 + motif_step). Row 0 is byte-identical to the original shipped
# sequence (FR-1300's no-regression requirement); rows 1-3 are new hand-composed variants sharing
# row 0's start/end degree (0...7) with differing middle contour, so a variant switch reads as
# development of the same phrase rather than an unrelated new one (IP-1090's own Risks section) —
# first-guess placeholder shapes, not tuned by ear, same BL-0005 disposition as row 0.
MOTIF_TABLE = [
    0, 2, 4, 5, 4, 2, 0, 7,   # variant 0: original shipped sequence (unchanged)
    0, 2, 4, 5, 4, 3, 0, 7,   # variant 1: softer descent (5->3 instead of 5->2 at step 5)
    0, 2, 5, 5, 4, 2, 0, 7,   # variant 2: reaches the 5th one step earlier (step 2, not 3)
    0, 3, 4, 5, 4, 2, 0, 7,   # variant 3: steps to the 4th via the 3rd instead of direct 2->4
]
N_VARIANTS = 4

# IP-1090 (BL-0010, ADS-102, R211 SS8): weighted selection of the next motif variant, drawn only
# at motif-cycle-boundary frames (the motif-step counter wrapping 7->0). Shaped exactly like
# DELTA_TABLE — signed deltas *relative to the current variant index*, indexed by 2 LFSR-derived
# bits, most entries 0 (retain the current variant) with one entry +1 (advance to the next
# variant, wrapped mod N_VARIANTS) — directly implementing R214 SS8's "short but interesting,
# recurrence dominates, switches are occasional" constraint. First-guess placeholder weighting
# (3-in-4 retain), not tuned by ear (BL-0042, same BL-0005-style disposition).
MOTIF_VARIANT_SELECTOR = [0x00, 0x00, 0x00, 0x01]

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


def _emit_apply_style(rom):
    """IP-1080 (roadmap R5, ADS-101/FS-108): reads STYLE_TABLE[CHMIX_IDX]'s 4-byte row
    (tempo_idx, density_idx, scale_idx, duty_bias) and writes each value into
    TEMPO_IDX/DENSITY_IDX/SCALE_IDX/DUTY_BIAS — called from input_map.py's Start-press handler
    immediately after CHMIX_IDX is stepped, so a style change applies the same frame as the press
    (FR-1240), unlike CHMIX_MASKS's channel-mix/scheme half (next onset, FR-1190)."""
    rom.LD_A_nn(CHMIX_IDX)
    rom.ADD_A_A(); rom.ADD_A_A()   # *4 (row width)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'style_table')
    rom.ADD_HL_BC()
    rom.LD_A_HLI(); rom.LD_nn_A(TEMPO_IDX)
    rom.LD_A_HLI(); rom.LD_nn_A(DENSITY_IDX)
    rom.LD_A_HLI(); rom.LD_nn_A(SCALE_IDX)
    rom.LD_A_HL();  rom.LD_nn_A(DUTY_BIAS)


def _emit_channel_gen(rom, suffix, note_timer, cur_degree, lfsr_state, nr_freq_lo, nr_freq_hi,
                       octave_delta, tempo_mult, stale_count, duty_reg=None, portamento=False,
                       dac_reg=None, dac_on=None, bit_index=None,
                       scheme_bit=None, scheme_state=None):
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

    # IP-1070 (BL-0020): scheme check. CHMIX_MASKS[CHMIX_IDX]'s scheme_bit picks this channel's
    # note-selection strategy for this onset — bit set means Scheme E (branch below), clear means
    # Scheme W (fall through to the existing LFSR-delta path unchanged). D (old degree, stashed
    # above) is never touched by either path, so the shared stale-count comparison further down
    # still sees the correct pre-onset value regardless of which scheme ran.
    if scheme_bit is not None:
        rom.LD_A_nn(CHMIX_IDX)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'chmix_masks_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()
        rom.BIT_b_A(scheme_bit)
        rom.JR_NZ(f'gt_schemee_{suffix}')

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

    if scheme_bit is not None:
        # IP-1090: JP not JR — the Scheme-E block below (extended with variant-selection logic)
        # is now too long for JR's signed 8-bit relative range.
        rom.JP(f'gt_delta_ready_{suffix}')

        # IP-1070: Scheme E — advance this channel's own Euclidean-pattern step (bits0-3 of
        # scheme_state), independent of the noise channel's own NOISE_STEP_IDX (each Scheme-E
        # channel gets its own pattern position, same "independent per channel" convention every
        # other per-channel walk/LFSR state already follows).
        rom.label(f'gt_schemee_{suffix}')
        rom.LD_A_nn(scheme_state)
        rom.LD_C_A()                   # C = old packed state
        rom.AND_n(0x0F)
        rom.INC_A()
        rom.AND_n(0x0F)                # A = new euclid step (0-15, wrapped)
        rom.LD_B_A()                   # B = new euclid step
        rom.LD_A_C()
        rom.AND_n(0xF0)                # keep motif-step bits (+ unused bit7)
        rom.OR_B()
        rom.LD_nn_A(scheme_state)      # write back: euclid step advanced, motif step unchanged

        # pattern_table offset = DENSITY_IDX*16 + new_euclid_step — same keying _emit_noise_gen
        # already uses; this reuses that table's data, not a new one.
        rom.LD_A_nn(DENSITY_IDX)
        rom.SLA_A(); rom.SLA_A(); rom.SLA_A(); rom.SLA_A()   # *16
        rom.ADD_A_B()
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'noise_pattern_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()
        rom.OR_A()
        rom.JR_Z(f'gt_e_nohit_{suffix}')

        # Pattern hit — a real onset. Advance motif step (bits4-6, wrap mod 8) and look up the
        # motif's absolute target degree (0-7) for this step.
        rom.LD_A_nn(scheme_state)
        rom.LD_C_A()
        rom.AND_n(0x70)
        rom.ADD_A_n(0x10)
        rom.AND_n(0x70)                # A = new motif-step bits, still shifted into position
        rom.LD_B_A()
        rom.LD_A_C()
        rom.AND_n(0x8F)                # clear old motif-step bits (keep euclid bits0-3 + bit7)
        rom.OR_B()
        rom.LD_nn_A(scheme_state)      # write back: motif step advanced too

        # IP-1090 (BL-0010, ADS-102): cycle-boundary check — B still holds the new motif-step
        # bits, shifted into position (0x00, 0x10, ..., 0x70); zero means the step just wrapped
        # from 7 back to 0, a full motif cycle just completed. Only on that exact frame, draw a
        # new MOTIF_VARIANT_IDX; every other frame this block is a no-op (FR-1280).
        rom.PUSH_BC()
        rom.LD_A_B()
        rom.OR_A()
        rom.JR_NZ(f'gt_e_novariant_{suffix}')

        # Cycle boundary: step this channel's own LFSR once (otherwise idle while running
        # Scheme E — the LFSR-step code above is skipped entirely via this branch's own
        # JR_NZ to gt_schemee_{suffix}), so this introduces no new randomness source, only a
        # new use of the existing one (NFR-1110). 2 bits index MOTIF_VARIANT_SELECTOR; the
        # resulting signed delta is added to MOTIF_VARIANT_IDX and wrapped mod N_VARIANTS via
        # AND 0x03 — the same signed-delta/wrap idiom DELTA_TABLE's own consumer already uses.
        rom.LD_A_nn(lfsr_state)
        rom.SRL_A()
        rom.JR_NC(f'gt_e_novariant_noxor_{suffix}')
        rom.XOR_n(LFSR_POLY)
        rom.label(f'gt_e_novariant_noxor_{suffix}')
        rom.LD_nn_A(lfsr_state)
        rom.AND_n(0x03)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'motif_variant_selector')
        rom.ADD_HL_BC()
        rom.LD_A_HL()                  # A = signed variant delta (0x00 retain, 0x01 advance)
        rom.LD_C_A()
        rom.LD_A_nn(MOTIF_VARIANT_IDX)
        rom.ADD_A_C()
        rom.AND_n(0x03)                # wrap mod N_VARIANTS=4
        rom.LD_nn_A(MOTIF_VARIANT_IDX)

        rom.label(f'gt_e_novariant_{suffix}')
        rom.POP_BC()                   # restore B = new motif-step bits, shifted (unclobbered)

        rom.LD_A_B()
        rom.SRL_A(); rom.SRL_A(); rom.SRL_A(); rom.SRL_A()   # A = motif_step (0-7)
        rom.LD_C_A(); rom.LD_B_n(0)
        # IP-1090: variant-relative offset — motif_table_base + MOTIF_VARIANT_IDX*8 + motif_step,
        # replacing the old fixed-base lookup (variant 0 == the pre-IP-1090 base, so this reduces
        # to the original lookup exactly when MOTIF_VARIANT_IDX is 0 — FR-1300's no-regression
        # guarantee).
        rom.LD_A_nn(MOTIF_VARIANT_IDX)
        rom.SLA_A(); rom.SLA_A(); rom.SLA_A()   # *8 (row width)
        rom.ADD_A_C()
        rom.LD_C_A()
        _ld_hl_label(rom, 'motif_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()                  # A = target absolute degree (0-7)
        rom.SUB_D()                    # A = target - old_degree — added back to old_degree and
                                        # masked mod 8 further down, this reproduces exactly
                                        # `target & 7` regardless of the numeric range of A here
        rom.LD_B_A()                   # B = signed delta achieving that same masked result
        rom.JR(f'gt_delta_ready_{suffix}')

        # No pattern hit this check — not an onset. Skip straight to the short (noise-style)
        # reload interval; no degree change, no stale/onset-window bookkeeping, no register
        # write — the channel simply keeps sounding whatever it was already playing.
        rom.label(f'gt_e_nohit_{suffix}')
        rom.JP(f'gt_e_reload_val_{suffix}')

        rom.label(f'gt_delta_ready_{suffix}')

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
    # IP-1080 (roadmap R5): the style-driven DUTY_BIAS is added to the degree-derived index
    # before the table lookup, then re-masked with the same AND 0x03 wrap the index already
    # used — DUTY_BIAS is 0 for the default style/preset 0, so this is a no-op until a
    # non-default style is selected (FR-1260's non-regression, satisfied by construction).
    if duty_reg is not None:
        rom.LD_A_nn(cur_degree)
        rom.AND_n(0x03)
        rom.LD_B_A()
        rom.LD_A_nn(DUTY_BIAS)
        rom.ADD_A_B()
        rom.AND_n(0x03)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'duty_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()
        rom.LDH_n_A(duty_reg)

    if dac_reg is not None:
        rom.label(f'gt_reload_{suffix}')

    # IP-1070: a Scheme-E channel reloads with the same fast, density-driven interval the noise
    # channel already uses (NOISE_STEP_TABLE), so its Euclidean-pattern step gets checked often
    # enough to express the pattern — not the normal per-tempo note reload. Re-derives the scheme
    # bit (cheap, HL is free here) rather than threading a flag through every intervening branch.
    if scheme_bit is not None:
        rom.LD_A_nn(CHMIX_IDX)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'chmix_masks_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()
        rom.BIT_b_A(scheme_bit)
        rom.JR_NZ(f'gt_e_reload_val_{suffix}')

    # Reload the timer from the tempo table (doubled for a half-rate channel, e.g. the wave bass).
    rom.LD_A_nn(TEMPO_IDX)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'tempo_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    if tempo_mult == 2:
        rom.ADD_A_A()

    if scheme_bit is not None:
        rom.JR(f'gt_reload_valready_{suffix}')

        rom.label(f'gt_e_reload_val_{suffix}')
        rom.LD_A_nn(TEMPO_IDX)
        rom.LD_C_A(); rom.LD_B_n(0)
        _ld_hl_label(rom, 'noise_step_table')
        rom.ADD_HL_BC()
        rom.LD_A_HL()

        rom.label(f'gt_reload_valready_{suffix}')

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
    combines all three into BAD_ZONE_FLAGS bit3 (IP-0004, GDS-03 SS4).

    IP-9010 (BL-0019) design decision, explicitly documented per that package's own named risk:
    this unconditionally scores all 3 pitched-channel pairs regardless of CHMIX_IDX exclusion —
    a channel silenced by the channel-mix gate still counts toward DISSONANCE_SCORE. Deliberate,
    not an oversight: each channel's melodic walk (and therefore its scale degree) keeps running
    even while excluded, per this same package's requirement that internal state stay consistent
    across exclusion/re-inclusion; treating an inaudible-but-still-walking channel as tonally
    "not there" would be a second, independent behavior change to IP-0004's already-`VERIFIED`
    bad-zone scoring, riding along with an unrelated remediation, adding untested surface to a
    subsystem no test currently varies by mix preset. No DoD item for this package requires
    excluding silenced channels from scoring."""
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


def _emit_song_tick(rom):
    """IP-1100 (roadmap R6, ADS-103): autonomous song-form phase cycling, entirely independent of
    bad-zone recovery (IP-0007) and Scheme-E motif-variant selection (IP-1090) — this routine
    never reads or writes BAD_ZONE_FLAGS/DISSONANCE_SCORE/STALE_COUNT_*/ONSET_WINDOW_COUNT/
    CUR_DEGREE_*/MOTIF_VARIANT_IDX/scheme_state, so no ordering dependency with either mechanism
    exists (ADS-103 SS2). Decrements a 16-bit frame counter each tick (standard decrement-with-
    borrow: if the low byte is 0 before decrementing, the high byte is decremented first); on the
    counter reaching zero, advances SONG_STATE (wrap mod N_SONG_PHASES) and overwrites
    TEMPO_IDX/DENSITY_IDX to the new phase's target values — the same coordinated-overwrite
    contract IP-1080's _emit_apply_style already established for those two fields, just
    autonomously triggered by this countdown rather than a Start press."""
    rom.label('song_tick')
    rom.LD_A_nn(SONG_STATE_TIMER_LO)
    rom.OR_A()
    rom.JR_NZ('st_dec_lo_only')
    rom.LD_A_nn(SONG_STATE_TIMER_HI)
    rom.DEC_A()
    rom.LD_nn_A(SONG_STATE_TIMER_HI)
    rom.label('st_dec_lo_only')
    rom.LD_A_nn(SONG_STATE_TIMER_LO)
    rom.DEC_A()
    rom.LD_nn_A(SONG_STATE_TIMER_LO)

    # Transition only when both bytes have reached zero.
    rom.OR_A()
    rom.JR_NZ('st_no_transition')
    rom.LD_A_nn(SONG_STATE_TIMER_HI)
    rom.OR_A()
    rom.JR_NZ('st_no_transition')

    rom.LD_A_nn(SONG_STATE)
    rom.INC_A()
    rom.AND_n(N_SONG_PHASES - 1)
    rom.LD_nn_A(SONG_STATE)

    rom.LD_A_nn(SONG_STATE)
    rom.SLA_A(); rom.SLA_A()   # *4 (row width)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'song_table')
    rom.ADD_HL_BC()
    rom.LD_A_HLI(); rom.LD_nn_A(TEMPO_IDX)
    rom.LD_A_HLI(); rom.LD_nn_A(DENSITY_IDX)
    rom.LD_A_HLI(); rom.LD_nn_A(SONG_STATE_TIMER_LO)
    rom.LD_A_HL();  rom.LD_nn_A(SONG_STATE_TIMER_HI)

    # IP-1120 (roadmap R7): recompute AROUSAL/VALENCE after this transition's TEMPO_IDX/
    # DENSITY_IDX overwrite -- strictly inside the transition branch, never on the no-transition
    # path, since song_tick itself runs every frame (called unconditionally from engine_tick) and
    # an unconditional recompute here would violate NFR-1170's zero-added-per-frame-cost contract.
    rom.CALL('mood_update')

    rom.label('st_no_transition')
    rom.RET()


def _emit_mood_update(rom):
    """IP-1120 (roadmap R7, ADS-105/FS-112): recomputes AROUSAL/VALENCE from the current
    TEMPO_IDX/DENSITY_IDX/SCALE_IDX values. Called only from the 6 write sites that can change
    those inputs (never per-frame — NFR-1170) — see music_engine.py's and input_map.py's own call
    sites for the full enumeration."""
    rom.label('mood_update')
    # AROUSAL = TEMPO_IDX + DENSITY_IDX (max 7+7=14, fits the required 0-15 range, no overflow).
    rom.LD_A_nn(TEMPO_IDX)
    rom.LD_B_A()
    rom.LD_A_nn(DENSITY_IDX)
    rom.ADD_A_B()
    rom.LD_nn_A(AROUSAL)

    # VALENCE = VALENCE_TABLE[SCALE_IDX] — same indexed-lookup idiom as delta_table/
    # chmix_masks_table (LD index into C, zero B, load HL with the table's base, ADD_HL_BC, read).
    rom.LD_A_nn(SCALE_IDX)
    rom.LD_C_A(); rom.LD_B_n(0)
    _ld_hl_label(rom, 'valence_table')
    rom.ADD_HL_BC()
    rom.LD_A_HL()
    rom.LD_nn_A(VALENCE)
    rom.RET()


def build_engine_asm(rom: ROM):
    """Emits data tables + init/tick/reset routines."""

    # ── init_engine (boot init AND Select-reset target, GDS-03 SS5) ──
    rom.label('init_engine')
    rom.LD_A_n(PRESET_TEMPO_IDX); rom.LD_nn_A(TEMPO_IDX)
    rom.LD_A_n(PRESET_OCTAVE_IDX); rom.LD_nn_A(OCTAVE_IDX)
    rom.LD_A_n(PRESET_SCALE_IDX); rom.LD_nn_A(SCALE_IDX)
    rom.LD_A_n(PRESET_DENSITY_IDX); rom.LD_nn_A(DENSITY_IDX)
    rom.LD_A_n(PRESET_CHMIX_IDX); rom.LD_nn_A(CHMIX_IDX)
    # IP-1080: DUTY_BIAS resets to 0 (STYLE_TABLE[0]'s own value, FR-1260) — TEMPO_IDX/
    # DENSITY_IDX/SCALE_IDX are already set to STYLE_TABLE[0]'s exact values by the three
    # PRESET_* writes just above, so no separate _emit_apply_style call is needed here.
    rom.XOR_A(); rom.LD_nn_A(DUTY_BIAS)
    # IP-1090 (BL-0010, ADS-102): MOTIF_VARIANT_IDX resets to 0 (variant 0, the pre-IP-1090
    # shipped sequence) on both boot and Select-reset — the same reset trigger that already
    # zeroes each channel's scheme_state below (which resets the motif-step counter to 0 too),
    # keeping a reset fully deterministic: variant 0, step 0 (FS-109's own Open Question 4).
    rom.XOR_A(); rom.LD_nn_A(MOTIF_VARIANT_IDX)
    # IP-1100 (roadmap R6, ADS-103): SONG_STATE resets to phase 0 (INTRO) on both boot and
    # Select-reset, with SONG_STATE_TIMER reloaded from SONG_TABLE[0]'s own duration.
    # SONG_TABLE[0]'s tempo_idx/density_idx match PRESET_TEMPO_IDX/PRESET_DENSITY_IDX exactly (see
    # SONG_TABLE's own comment), so the TEMPO_IDX/DENSITY_IDX writes just above are not disturbed
    # — a reset always returns to a deterministic, known-good starting phase with no regression to
    # existing boot/reset behavior.
    rom.XOR_A(); rom.LD_nn_A(SONG_STATE)
    rom.LD_A_n(SONG_TABLE[0][0]); rom.LD_nn_A(TEMPO_IDX)
    rom.LD_A_n(SONG_TABLE[0][1]); rom.LD_nn_A(DENSITY_IDX)
    rom.LD_A_n(SONG_TABLE[0][2]); rom.LD_nn_A(SONG_STATE_TIMER_LO)
    rom.LD_A_n(SONG_TABLE[0][3]); rom.LD_nn_A(SONG_STATE_TIMER_HI)

    # IP-1120 (roadmap R7): recompute AROUSAL/VALENCE from the now-final TEMPO_IDX/DENSITY_IDX/
    # SCALE_IDX values -- placed here because every write to those three addresses in this
    # routine has already landed (SCALE_IDX at PRESET_SCALE_IDX above; TEMPO_IDX/DENSITY_IDX at
    # their final SONG_TABLE[0] overwrite just above, not the earlier PRESET_* write). Serves
    # both the boot path and the Select-reset path, since both call this same label.
    rom.CALL('mood_update')

    for (suffix, note_timer, cur_degree, lfsr_state, lfsr_seed, *_rest, duty_reg,
         arp_state, _dac_reg, _dac_on, _bit_index, _scheme_bit, scheme_state) in CHANNELS:
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
        # IP-1070: zero this channel's packed Scheme-E state (Euclidean step + motif step) —
        # same audit discipline IP-0005 already established for every other per-channel field.
        rom.XOR_A(); rom.LD_nn_A(scheme_state)
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
    for (suffix, *_rest, duty_reg, arp_state, _dac_reg, _dac_on, _bit_index,
         _scheme_bit, _scheme_state) in CHANNELS:
        if arp_state is not None:
            rom.CALL(f'arp_tick_{suffix}')
    for (suffix, *_rest) in CHANNELS:
        rom.CALL(f'gen_tick_{suffix}')
    rom.CALL('gen_tick_nz')
    rom.CALL('badzone_tick')
    rom.CALL('song_tick')
    rom.RET()

    for (suffix, note_timer, cur_degree, lfsr_state, _seed, nr_lo, nr_hi, oct_delta, tempo_mult,
         stale_count, duty_reg, arp_state, dac_reg, dac_on, bit_index,
         scheme_bit, scheme_state) in CHANNELS:
        _emit_channel_gen(rom, suffix, note_timer, cur_degree, lfsr_state, nr_lo, nr_hi,
                           oct_delta, tempo_mult, stale_count, duty_reg,
                           portamento=(arp_state is not None),
                           dac_reg=dac_reg, dac_on=dac_on, bit_index=bit_index,
                           scheme_bit=scheme_bit, scheme_state=scheme_state)
        if arp_state is not None:
            _emit_arpeggio_tick(rom, suffix, arp_state, cur_degree, nr_lo, nr_hi)
    _emit_noise_gen(rom)
    _emit_badzone_tick(rom)
    _emit_song_tick(rom)
    _emit_mood_update(rom)

    # ── Data tables ───────────────────────────────────────────────────
    rom.label('delta_table')
    rom.emit(*DELTA_TABLE)
    rom.label('valence_table')
    rom.emit(*VALENCE_TABLE)

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

    rom.label('motif_table')
    rom.emit(*MOTIF_TABLE)

    rom.label('motif_variant_selector')
    rom.emit(*MOTIF_VARIANT_SELECTOR)

    rom.label('style_table')
    for row in STYLE_TABLE:
        rom.emit(*row)

    rom.label('song_table')
    for row in SONG_TABLE:
        rom.emit(*row)

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
