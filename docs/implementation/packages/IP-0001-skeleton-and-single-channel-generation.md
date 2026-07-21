# IP-0001 — Skeleton build chain + single-channel (pulse A) generation + headless harness bootstrap

| Field | Content |
|---|---|
| **ID** | IP-0001 |
| **Feature(s)** | FEAT-1000 (partial — pulse A only), FEAT-1010 (all 6 input controls, full mapping), FEAT-1020 (Select reset, scoped to fields that exist), FEAT-1050 (bootstrap: T1-T5) |
| **Traces to** | FR-1000, FR-1010 (pulse A only), FR-1020-FR-1060 (full), FR-1070 (scoped), GDS-03 SS1-SS3/SS5, GDS-07 |
| **Owner** | `08-code-implementation` |
| **Status** | **VERIFIED** ([VR-0001](../verification/VR-0001-skeleton-and-single-channel-generation.md), same-session exception user-accepted 2026-07-21) |
| **Files touched** | `gbc_lib.py` (reused verbatim, no changes), `music_engine.py` (new), `input_map.py` (new), `build_rom.py` (new), `test_rom.py` (new) |
| **Scope** | Sound hardware init (NR50/51/52, pulse A base registers); `init_engine`/reset-to-preset for the 5 parameter indices + pulse A's own state; `engine_tick`'s per-frame countdown + LFSR-driven scale-constrained walk + table-lookup note generation for pulse A only; `apply_input`'s full 6-control edge-triggered mapping (only `TEMPO_IDX`/`SCALE_IDX` audibly affect anything yet — `OCTAVE_IDX` does audibly affect pulse A; `DENSITY_IDX`/`CHMIX_IDX` are wired and tested for their own index behavior but have no consumer until IP-0002/0003) |
| **Explicit non-scope** | Pulse B, wave, noise channels (IP-0002/0003); bad-zone scoring (IP-0004); visualizer (IP-0006) |
| **Acceptance criteria** | ROM builds to 32768 bytes with a valid header; boots to a state where pulse A is audibly generating and changing over time; all 6 input controls edit exactly their own parameter index and no other; Select returns the tested indices to their known-good preset; `test_rom.py` T1-T5 all pass |
| **Test evidence** | `test_rom.py`, 32/32 checks pass (T1.1-T1.5, T2.1-T2.5, T3.1-T3.3, T4.1-T4.7 x2, T5.1-T5.5) |
| **G5 gate** | ✅ `python3 build_rom.py <path>` → exactly 32768 bytes, valid header; ✅ `python3 test_rom.py` → 32/32 |
| **Findings surfaced** | R100 correction: `NR13`/`NR14` frequency bits are write-only, unusable for test/visualizer readback — the WRAM mirror is the only readable source for pitch/parameter state (already reflected in `docs/research/R100-gbc-sound-hardware.md`'s "Confirmed during IP-0001" section); GDS-07 gained two addenda (`JOY_CUR`/`JOY_NEW`/`LFSR_STATE`/`VBLANK_FLAG`) discovered necessary during implementation, added in place per the pipeline's live-doc discipline. |
| **Open items carried forward** | IP-0002 (pulse B + wave), IP-0003 (noise + density wiring), IP-0004 (bad-zone), IP-0005 (full reset), IP-0006 (visualizer) — see the Master Build Plan. |
| **Verification note** | Built and tested within the same session/agent that authored it, not a fresh independent session — per the reference project's own stated best practice ("verification ideally in a fresh session for independence"), this package is `COMPLETE` (G5 green, its own tests pass) but **not yet `VERIFIED`** in the pipeline's formal sense; `09-package-verification` should re-run this package's checks independently before it's marked `VERIFIED`. This is recorded honestly rather than self-certifying, per G2 (status honesty). |
| **Authorization** | Covered by the Master Build Plan's standing note: the project owner's original instruction to reach working code this session, treated as G3 authorization for this first foundation package. |
