"""
wram_constants.py — shared WRAM constants for engine-state fields multiple modules need to
reference (IP-8020, BL-0065).

Dependency-free by design (imports nothing) so both `music_engine.py` (the canonical owner of
these fields' runtime behavior) and `visuals.py` (a read-only consumer that must not import
`music_engine.py`, to keep the module import graph acyclic — GDS-03 SS1) can import from here
without creating a cycle. Extracted from a prior state where `visuals.py` re-declared these 11
values as local plain ints, duplicated from `music_engine.py` by hand with no mechanism
preventing drift (BL-0065).
"""

# ── Parameter indices (GDS-07 SS5) ────────────────────────────────────
TEMPO_IDX = 0xC000
OCTAVE_IDX = 0xC001
SCALE_IDX = 0xC002
DENSITY_IDX = 0xC003
CHMIX_IDX = 0xC004

# ── Bad-zone combined-flags byte (GDS-07 SS4a) ────────────────────────
BAD_ZONE_FLAGS = 0xC005  # bit0 DISSONANT, bit1 STUCK, bit2 OVERLOAD, bit3 COMBINED

# ── Boot-preset values for the 5 parameter indices above (GDS-03 SS5) ─
PRESET_TEMPO_IDX = 4
PRESET_OCTAVE_IDX = 1
PRESET_SCALE_IDX = 0
PRESET_DENSITY_IDX = 0
PRESET_CHMIX_IDX = 0
