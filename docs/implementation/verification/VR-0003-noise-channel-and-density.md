# VR-0003 — Verification Report: IP-0003

- **Package:** IP-0003 — Noise channel + density wiring
- **Commit verified:** `504deda` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Result:** ✅ **VERIFIED**

## Independence note

Fresh session (continuing from this session's `IP-0002` verification, run #7). This session did
not implement `IP-0003` — it was authored in the earlier run #1/3/4/5/6 session — so independence
is intact; the rule blocks verifying a package in the same session that implemented *that*
package, not chaining multiple independent verifications together.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `_emit_noise_gen`: fixed 16-step grid, `DENSITY_IDX` selects `k` from `DENSITY_K` | `music_engine.py:331-388` (routine), `music_engine.py:142` (`DENSITY_K = [2,3,4,5,6,8,10,12]`) | PASS |
| Pattern precomputed per-`k` via Euclidean bucket-boundary approximation, stored as 16 unpacked 0/1 bytes/level | `music_engine.py:149-158` (`_euclidean_pattern`), `music_engine.py:566-568` (`noise_pattern_table` emission, one 16-byte block per `DENSITY_K` entry) — independently re-computed `_euclidean_pattern(k)` for all 8 `k` values in a Python REPL: each produces exactly `k` onsets out of 16 steps, matching `sum(pattern) == k` for every entry | PASS |
| Percussive envelope (`NR42=0xF2`) + 15-bit hiss width (`NR43=0x41`) | `music_engine.py:359-360` | PASS |
| `NOISE_STEP_TABLE` derives 16th-note step duration from the tempo table (`/4`, floor 1) | `music_engine.py:146` (`NOISE_STEP_TABLE = [max(1, round(t/4)) for t in TEMPO_TABLE]`); independently recomputed: `[15,12,10,8,8,6,6,5]` for `TEMPO_TABLE=[60,48,40,34,30,26,22,20]` — matches | PASS |
| `test_rom.py` T7 (density driven to both extremes, monotonic scaling confirmed) + full regression green | See Test run and Non-default-parameter drive below | PASS |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, fixed size, valid header | `python3 build_rom.py <path>` | 32768 bytes; title `DRIFTUNE`, CGB flag `0x80`, cart type `0x00` — independently re-read |
| Full suite green | `python3 test_rom.py` | **60 PASS, 0 FAIL out of 60** (T7 specifically: T7.setup×2, T7.0.1/0.2, T7.7.1/7.2, T7.3 all PASS — density 0 → 138 active-frames/600, density 7 → 563 active-frames/600) |

## Non-default-parameter live drive (this skill's own additional requirement)

`test_rom.py` T7 already drives `DENSITY_IDX` to both extremes (0 and 7) — the standard this
skill's own prior VRs (e.g. VR-0001's tempo-extremes drive) have used, and by itself sufficient.
This run went one step further and drove a **mid-range value T7 never touches** (`DENSITY_IDX=3`,
`k=5`, reached via 3 B-taps from the boot preset), independent of the suite, reading `NR52` bit 3
(channel 4 active) the same way T7 does:

- `DENSITY_IDX=3` (`k=5`) → **357** active-frames/600 — falls strictly between density 0's 138
  and density 7's 563, confirming the scaling is monotonic across the range, not just at its two
  endpoints (a pattern-table indexing bug that only manifested at intermediate `k` values would
  not have been caught by T7's extremes-only fixture).
- `NR52` read back `0xFF` throughout — no channel dropped out at the mid density.

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1010 (noise-channel portion — the fourth and last channel, completing "all 4 channels") | `music_engine.py:331-388` (`_emit_noise_gen`) | `test_rom.py` T7.0.1/0.2, T7.7.1/7.2 (both density extremes), T7.3 (monotonic scaling); this run's own mid-density live drive above | PASS |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention VR-0001/VR-0002 established, this table is the RTM-equivalent audit for IP-0003's
requirement.

## Scope audit

Files touched per the package doc: `music_engine.py` only. Confirmed by reading the noise-related
code in full — `_emit_noise_gen`, `DENSITY_K`, `NOISE_STEPS`, `NOISE_STEP_TABLE`,
`_euclidean_pattern`, and the `noise_pattern_table`/`NOISE_STEP_TABLE` emission in
`build_engine_asm` — no excursion into `build_rom.py`, `input_map.py`, `gbc_lib.py`,
`visuals.py`, or `tiles.py` found. (As with IP-0002, `music_engine.py` also carries later
packages' code — IP-0004's `ONSET_WINDOW_COUNT` bookkeeping and IP-0007's overload-recovery
doubling are interleaved into `_emit_noise_gen`'s body, each independently attributable by its
own inline comment tag — not an IP-0003 scope excursion.)

## Findings

None new.

## Verdict

`IP-0003` satisfies every Definition of Done item, both permanent gates, and its traced
requirement, with independent re-derivation of every claim — including a live, non-default
(`DENSITY_IDX=3`, a mid-range value the existing suite's fixture never drives) drive of the ROM
confirming monotonic onset scaling holds between, not just at, the tested extremes.
**Advancing to `VERIFIED`.**
