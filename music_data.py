"""
music_data.py — Driftune's curated musical building blocks: scale/tempo/style/song/motif/
valence tables (IP-8030, BL-0089).

Pure content module: every scale/tempo/style/song/motif/valence table previously declared
inline in music_engine.py, moved verbatim (byte-for-byte identical values). Genuinely
dependency-free per this package's own Definition of Done (imports nothing from
music_engine.py/visuals.py/input_map.py/build_rom.py/gbc_lib.py/wram_constants.py/test_rom.py —
imports nothing at all, in fact). STYLE_TABLE's and SONG_TABLE's own rows were always defined in
terms of the shipped default preset (PRESET_TEMPO_IDX=4, PRESET_DENSITY_IDX=0,
PRESET_SCALE_IDX=0, wram_constants.py) — rather than importing wram_constants.py (which the DoD
above bars from this module), those three literal values are substituted directly below, with
this comment as the cross-reference; the values are compile-time constants, so substituting them
is a pure, meaning-preserving relocation, not a hardcoded guess. Verified identical: wram_constants.py's PRESET_TEMPO_IDX/PRESET_SCALE_IDX/PRESET_DENSITY_IDX = 4/0/0 exactly.
"""

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

# Small signed scale-degree deltas the LFSR-driven walk picks from (R201's "scale-constrained
# random walk" — weighted toward staying/small steps, indexed by the LFSR's low 2 bits).
DELTA_TABLE = [0xFF, 0x00, 0x00, 0x01]  # -1, 0, 0, +1 (two's complement)

# IP-1120: VALENCE is a fixed lookup keyed by SCALE_IDX (0-3) -- a lookup table is definitionally
# a fixed one-to-one mapping (FR-1400). Illustrative first-guess placement values, not tuned by
# ear (BL-0005-class deferral, same as every other untuned preset/threshold this project has
# shipped) -- a future 09-content-review pass, once R9 gives this a real consumer, is the right
# place to retune.
VALENCE_TABLE = [10, 6, 12, 4]

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
# (4, 0, 0, ...) below = (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, ...) —
# substituted as literals per this module's own docstring note (wram_constants.py import barred
# by the DoD; values verified identical: 4/0/0).
STYLE_TABLE = [
    (4, 0, 0, 0x00),  # 0: default
    (6, 6, 2, 0x01),                                                 # 1: Techno/Chiptune-Driving
    (1, 0, 3, 0xFF),                                                 # 2: Ambient/Lo-Fi
    (3, 3, 0, 0x01),                                                 # 3: Holiday
    (4, 0, 0, 0x00),  # 4: default (unassigned)
    (4, 0, 0, 0x00),  # 5: default (unassigned)
    (4, 0, 0, 0x00),  # 6: default (unassigned)
    (4, 0, 0, 0x00),  # 7: default (unassigned)
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
    (4, 0, 1800 & 0xFF, (1800 >> 8) & 0xFF),  # 0: INTRO (matches shipped default) - ~30s
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
