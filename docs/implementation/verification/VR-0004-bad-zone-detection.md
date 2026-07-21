# VR-0004 — Verification Report: IP-0004

- **Package:** IP-0004 — Bad-zone detection
- **Commit verified:** `504deda` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Result:** ✅ **VERIFIED**

## Independence note

Same session as runs #7-#8 (this session has implemented none of IP-0002-0007 — all authored in
the earlier run #1/3/4/5/6 session). Independence intact.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `_emit_badzone_tick`, called once/frame from `engine_tick` | `music_engine.py:431-495` (routine), `music_engine.py:554` (`_emit_badzone_tick(rom)` inside `engine_tick`) | PASS |
| Dissonance (bit0): `SEMITONE_TABLE` (4 scales × 8 degrees, mod-12) + `_emit_pairwise_dissonance` for all 3 pitched-channel pairs, weighted via `DISSONANCE_WEIGHT_BY_IC`, summed into `DISSONANCE_SCORE` | `music_engine.py:90-94` (`SEMITONE_TABLE_DATA`), `music_engine.py:100` (`DISSONANCE_WEIGHT_BY_IC = [0,15,11,3,2,1,13]`), `music_engine.py:405-428` (`_emit_pairwise_dissonance`, interval-class fold + weighted accumulate), `music_engine.py:438-443` (called for PA/PB, PA/WV, PB/WV — all 3 pairs) | PASS |
| Interval-class fold (0-6, inversions folded) — documented simplification of R204's raw 12-entry proposal | `music_engine.py:415-419` (`CP_n(7)` / fold-to-complement) | PASS (documented deviation, already tracked `BL-0013`) |
| Stuck (bit1): period-1 repetition only (documented MVP simplification vs. GDS-03's period-1-or-2) | `music_engine.py:260-271` (per-channel `STALE_COUNT_*` inc/reset comparing only the immediately-preceding degree), `music_engine.py:456-464` (bit1 set if any `STALE_COUNT_*` > `STALE_THRESHOLD`) | PASS (documented deviation, already tracked `BL-0013`) |
| Overload (bit2): every onset (any channel, incl. noise) increments `ONSET_WINDOW_COUNT`; 32-frame rolling window evaluates + resets | `music_engine.py:466-483` (`ONSET_WINDOW_TICK_CTR` countdown, evaluate against `OVERLOAD_THRESHOLD` only when it hits 0, then reset both counters); onset increments confirmed at `music_engine.py:274-276` (pitched channels) and `music_engine.py:364-366` (noise hits) | PASS |
| Combined (bit3): OR of bits 0-2 | `music_engine.py:486-494` | PASS |
| `init_engine` zero-initializes all bad-zone state | `music_engine.py` `init_engine` (confirmed `BAD_ZONE_FLAGS`, `DISSONANCE_SCORE`, `STALE_COUNT_*`, `ONSET_WINDOW_COUNT`/`ONSET_WINDOW_TICK_CTR` all zeroed/reloaded, `music_engine.py:531,537`) | PASS |
| `test_rom.py` T8 (9 checks) + full regression green | See Test run below | PASS |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, fixed size, valid header | `python3 build_rom.py <path>` | 32768 bytes; title `DRIFTUNE`, CGB flag `0x80` — independently re-read |
| Full suite green | `python3 test_rom.py` | **60 PASS, 0 FAIL out of 60** (T8.1-T8.9 all PASS) |

## Non-default-parameter live drive (this skill's own additional requirement)

`test_rom.py` T8's fixture stays at the boot preset (`SCALE_IDX=0`, major) throughout — the
dissonance calculation's `SEMITONE_TABLE` lookup is scale-dependent, so a scale-indexing bug could
silently produce garbage scores or a stuck `BAD_ZONE_FLAGS` at any non-default scale without T8
ever catching it. Drove `SCALE_IDX` to `3` (pentatonic, the scale furthest from the preset) live,
independent of the suite:

- Booted fresh, tapped `A` three times to reach `SCALE_IDX=3` (pentatonic).
- Ran 2000 frames, sampling `DISSONANCE_SCORE` and `BAD_ZONE_FLAGS` every frame: scores ranged
  `0-24` (8 distinct values, all within the theoretical `0-45` bound — no out-of-range or garbage
  values from the different semitone table), at least one bad-zone entry observed (`flags seen:
  [0, 1, 8, 9]` — DISSONANT/COMBINED both correctly correlated, no STUCK/OVERLOAD spuriously
  latched).

Confirms the scale-dependent lookup is correct off the one scale value the suite's shared fixture
ever exercises.

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1080 | `music_engine.py:436-453` (dissonance recompute + bit0) | T8.1/T8.3, this run's pentatonic-scale drive | PASS |
| FR-1090 | `music_engine.py:260-271` (per-channel `STALE_COUNT_*`), `music_engine.py:455-464` (bit1) | T8.7b/T8.8 | **PASS with a documented deviation** — see Findings |
| FR-1100 | `music_engine.py:466-483` (rolling-window overload) | T8.7c/T8.9 (indirectly; no direct overload-triggering test in T8, but the mechanism was read and matches the requirement) | PASS |
| FR-1110 | `music_engine.py:486-494` (bit3 = OR of bits 0-2) | T8.4 (bit3 tracks bit0 on ~99.9% of frames — the rare transient is `BL-0015`, already filed, low-severity, self-healing) | PASS |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention prior VRs established, this table is the RTM-equivalent audit for IP-0004's
requirements.

## Scope audit

Files touched per the package doc: `music_engine.py` only. Confirmed by reading
`_emit_badzone_tick`, `_emit_get_semitone`, `_emit_pairwise_dissonance`, the
`SEMITONE_TABLE_DATA`/`DISSONANCE_WEIGHT_BY_IC` tables, and the `STALE_COUNT_*`/`ONSET_WINDOW_*`
bookkeeping interleaved into `_emit_channel_gen`/`_emit_noise_gen` (attributed to IP-0004 by their
own inline comment tags — the same shared-file pattern already confirmed in VR-0002/VR-0003, not
a scope excursion). No excursion into `build_rom.py`, `input_map.py`, `gbc_lib.py`, `visuals.py`,
or `tiles.py` found.

## Findings

| Finding | Severity | Owner |
|---|---|---|
| `FR-1090`'s text names a "history ring buffer (`HIST_PA`/`PB`/`WV`)" that records each onset's scale degree. Grepped the full tree: `HIST_PA`/`HIST_PB`/`HIST_WV` do not exist anywhere in `music_engine.py` — the shipped implementation is the simpler period-1-only comparison already tracked as a *GDS-03/GDS-07/R204* deviation under `BL-0013`, but `BL-0013` as currently worded doesn't mention that `FR-1090` (the requirement itself, not just the architecture docs) also describes the unbuilt ring-buffer design. No functional defect — T8.7b/T8.8 confirm `STALE_COUNT_PA` behaves correctly under the simpler design — this is a doc-coherence gap one level higher than `BL-0013` currently scopes. | Low-Medium (doc-coherence only, no functional impact — same character as `BL-0013`) | `04-requirements-engineering` (reword `FR-1090` to drop the ring-buffer reference, or explicitly mark it a v2 upgrade path) alongside `03-architecture-design-synthesis`'s existing `BL-0013` reconciliation |

## Verdict

`IP-0004` satisfies every Definition of Done item, both permanent gates, and all four traced
requirements (one — `FR-1090` — with a pre-existing, already-tracked documented deviation, now
additionally observed to reach the requirements layer, not just the architecture layer), with
independent re-derivation of every claim including a live, non-default (`SCALE_IDX=3`, pentatonic)
drive the existing suite's shared fixture never exercises. **Advancing to `VERIFIED`.**
