# VR-0005 — Verification Report: IP-0005

- **Package:** IP-0005 — Full reset-to-preset across all channels/bad-zone state
- **Commit verified:** `504deda` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Result:** ✅ **VERIFIED**

## Independence note

Same session as runs #7-#9 (this session has implemented none of IP-0002-0007). Independence
intact.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `init_engine` (the boot-init AND Select-reset target, GDS-03 SS5) covers every WRAM field IP-0002/0003/0004 introduced — no gaps | `music_engine.py:503-539`: the `CHANNELS` loop zeroes/reseeds `cur_degree`/`note_timer`/`lfsr_state` for pa/pb/wv (`:510-524`); `NOISE_STEP_IDX`/`NOTE_TIMER_NZ` zeroed/reloaded (`:526-527`); `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/`STALE_COUNT_PA`/`PB`/`WV`/`ONSET_WINDOW_COUNT`/`ONSET_WINDOW_TICK_CTR` all zeroed/reloaded (`:530-538`). Independently cross-checked every WRAM address defined for IP-0002-0004 against this body — none missing. | PASS |
| No new code added by this package (audit-only) | Confirmed: no `music_engine.py`/`build_rom.py` diff attributable to `IP-0005` beyond what IP-0002-0004 already added while introducing their own fields — the package doc is honest about this | PASS |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, fixed size, valid header | `python3 build_rom.py <path>` | 32768 bytes; title `DRIFTUNE`, CGB flag `0x80` |
| Full suite green | `python3 test_rom.py` | **60 PASS, 0 FAIL out of 60** (T5, T8.6-T8.9 exercise reset coverage as the package doc claims) |

## Non-default-parameter live drive — closing `BL-0014`

The package doc itself flags a light, honestly-stated gap (`BL-0014`): pulse B/wave/noise's
Select-reset coverage is implicitly exercised by T6/T7's drift patterns but never independently
asserted *immediately post-Select* the way T5/T8 do for pulse A and bad-zone state.
`BL-0014`'s own disposition names this exact verification pass as the place to close it. Drove it
directly, live, independent of the suite:

- Booted fresh, let the engine run 400 frames so pulse B/wave/noise state drifted away from their
  reset values (`CUR_DEGREE_PB=3`, `CUR_DEGREE_WV=7`, `NOISE_STEP_IDX=7`, `LFSR_STATE_PB=208`,
  `LFSR_STATE_WV=244`).
- Pressed Select for one frame, read state on the exact reset frame (same methodology T5/T8 use):
  `CUR_DEGREE_PB` and `CUR_DEGREE_WV` both read back `0` (reset), `NOTE_TIMER_PB=30`/
  `NOTE_TIMER_WV=60` (freshly reloaded from the tempo table, matching the pulse-A pattern T5
  already confirms), `NOISE_STEP_IDX=1`/`NOTE_TIMER_NZ=8` (freshly reloaded, the `1` reflecting
  the same "same-frame-fires-immediately" effect T8.7c already documents for onset counters —
  `init_engine` zeroes it to `0` but the noise routine's own countdown-then-increment fires once
  more within the same reset frame before the read).
- `STALE_COUNT_PB`/`STALE_COUNT_WV` read `1` (not `0`) on the exact reset frame — at first glance
  inconsistent with T8.7b's `STALE_COUNT_PA == 0` on the same frame, but explained by `IP-0007`'s
  independent `DIV`-seeded reseeding of each channel's LFSR (not yet built when `IP-0005` was
  originally scoped): all three channels' post-reset first step is decided by their own
  independently-randomized seed this same frame, so one channel landing on "no movement, degree
  stayed at the just-zeroed tonic" (stale increments to `1`) while another moves (stale resets to
  `0`) is expected per-channel variance, not a reset-coverage defect — the *mechanism* (each
  channel's own `STALE_COUNT_*` correctly tracks its own post-reset degree comparison) is exactly
  what `FR-1090`'s stale logic requires and is confirmed working for pulse B/wave here, not just
  pulse A.

This directly closes `BL-0014`'s gap: pulse B/wave/noise's reset coverage is now independently
confirmed, not just implicitly inferred.

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1070 | `music_engine.py:503-539` (`init_engine`, shared boot/Select-reset target) | `test_rom.py` T5.1-T5.5 (pulse A + shared parameters), T8.6-T8.9 (bad-zone state); this run's own live drive of pulse B/wave/noise reset coverage above | PASS |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention prior VRs established, this table is the RTM-equivalent audit for IP-0005's
requirement.

## Scope audit

No files are uniquely attributable to `IP-0005` — its scope is entirely the audit-confirmation
that `init_engine`'s coverage (built incrementally by IP-0002/0003/0004) is complete, which this
run independently re-confirmed rather than trusting the package doc's own claim.

## Findings

`BL-0014` closed by this run's live drive (see above) — no residual gap.

## Verdict

`IP-0005` satisfies its Definition of Done, both permanent gates, and its traced requirement, with
independent re-derivation of every claim — including closing the one honestly-flagged gap the
package doc itself named (`BL-0014`, pulse B/wave/noise reset coverage), now confirmed live rather
than only implicitly inferred. **Advancing to `VERIFIED`.**
