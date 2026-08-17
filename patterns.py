"""
patterns.py — Driftune's Euclidean rhythm-pattern generation and density/step-timing data
(IP-8030, BL-0089).

Pure content module: the noise/density Euclidean-rhythm machinery previously declared inline in
music_engine.py, moved verbatim (byte-for-byte identical values, identical algorithm). Per this
package's own Definition of Done, dependency-free of music_engine.py/visuals.py/input_map.py/
build_rom.py/gbc_lib.py/wram_constants.py/test_rom.py — but NOISE_STEP_TABLE's own definition
was always derived from TEMPO_TABLE (per-tempo step duration), which this same package moves to
music_data.py; importing that one value from a sibling content module (not from music_engine.py/
visuals.py/input_map.py/build_rom.py) preserves the acyclic-import invariant GDS-03 §1 protects
— music_data.py does not import from patterns.py, so no cycle is introduced.
"""

from music_data import TEMPO_TABLE

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
