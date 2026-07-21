# VR-0007 — Verification Report: IP-0007

- **Package:** IP-0007 — Autonomous bad-zone avoidance/recovery + Select randomization
- **Commit verified:** `504deda` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Result:** ✅ **VERIFIED** (with one significant new finding — see below)

## Independence note

Same session as runs #7-#11 (this session has implemented none of IP-0002-0007). Independence
intact. This is the last package in the tranche owed independent verification.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Dissonant (bit0) override: pulls the channel's degree toward tonic instead of the LFSR-picked delta | `music_engine.py:228-244` (`gt_dis_zero_*`/override to `B=0xFF` pull-down, or hold at 0 if already there) | PASS (see live drive below) |
| Stuck (bit1) override: forces movement if the (possibly-overridden) delta is still 0 | `music_engine.py:246-253` | PASS (code-reviewed; consistent with T10's macro recovery result) |
| Overload (bit2): reload doubled again at timer-reload for pitched channels and noise | `music_engine.py:313-323` (pitched), `music_engine.py:375-383` (noise) | PASS as *coded* — **but see the reachability finding below** |
| `init_engine` reseeds each channel's LFSR from `DIV` XOR a fixed per-channel constant, zero-guarded, on both boot and Select | `music_engine.py:514-523` | PASS |
| Two `JR`→`JP_NZ` fixes at the early-exit guards (out-of-range once routines lengthened) | `music_engine.py:208` (`_emit_channel_gen`), `music_engine.py:340` (`_emit_noise_gen`) — both `JP_NZ`, confirmed `gbc_lib.py:170` emits the absolute-range `0xC2` opcode, not a relative `JR` | PASS |
| `test_rom.py` T10 (new) + full regression green | See Test run below | PASS |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, fixed size, valid header | `python3 build_rom.py <path>` | 32768 bytes; title `DRIFTUNE`, CGB flag `0x80` |
| Full suite green | `python3 test_rom.py` | **60 PASS, 0 FAIL out of 60** (T10.1/T10.2 both PASS) |

## Non-default-parameter live drives (this skill's own additional requirement)

Two independent live drives, beyond what T10's macro-level "eventually recovers" check covers:

**1. Confirms the dissonance pull-toward-tonic mechanism directly** (not just its aggregate
effect): sampled every `CUR_DEGREE_PA` change over an 8000-frame run, splitting deltas by whether
`BAD_ZONE_FLAGS` bit0 (DISSONANT) was set at the moment of the prior onset:
- Deltas following a DISSONANT-flagged onset: **51/51 were exactly `-1`** (100% pull-toward-tonic,
  zero exceptions) — the LFSR-picked delta is being unconditionally overridden as designed.
- Deltas overall (unconditional): a mix, `{-1: 98, 1: 42}` — confirming the override is a real,
  discriminating behavior change, not an artifact of the random walk's own bias.

**2. Attempted to independently trigger OVERLOAD (bit2) and confirm the reload-doubling** — this
is where the live drive surfaced a real, previously-undetected finding (below): drove
`DENSITY_IDX` to its maximum (`7`, `k=12`) and ran 6000 frames watching `BAD_ZONE_FLAGS` bit2 —
**it never set, even once.** Computed the theoretical ceiling independently in a Python REPL:
at the fastest tempo (`TEMPO_TABLE[7]=20`) *and* max density (`k=12`) simultaneously — a
combination the engine can't even reach at once since tempo and density are independently
player-set, so this is already a generous upper bound — the maximum possible onsets in one
32-frame `ONSET_WINDOW_FRAMES` window is:
`2×(32/20)` [pulse A+B] `+ 32/40` [wave, half-rate] `+ (32/5)/16×12` [noise] `≈ 8.8`,
**well under `OVERLOAD_THRESHOLD=20`.** This matches the empirical observation exactly — `bit2`
has never been observed set anywhere in this session's testing (VR-0004's own live drive, T8's
2000-frame runs, T10's 8000-frame stress evidence in the package doc, and this run's dedicated
6000-frame max-density attempt all show `flags seen` never including bit2, `0x04`, in any
combination).

## Findings

| Finding | Severity | Owner |
|---|---|---|
| **`OVERLOAD_THRESHOLD=20` is mathematically unreachable under the engine's own generation-rate ceiling (~8.8 onsets/32-frame window at the *maximum* tempo and density simultaneously).** This means `BAD_ZONE_FLAGS` bit2 (OVERLOAD) can never actually be set by the shipped ROM — `FR-1100` ("sets bit2 when the count exceeds the overload threshold") is implemented correctly in code but can never be satisfied in practice, and `IP-0007`'s own overload-driven reload-doubling recovery logic (`music_engine.py:313-323,375-383`) is consequently dead code that can never execute. This is a stronger, now-quantified version of what `BL-0005` already flagged more vaguely as "OVERLOAD_THRESHOLD... unchanged disposition, first-guess placeholder" — this run supplies the concrete ceiling that proves it's not merely untuned but *structurally* unreachable at any valid tempo/density combination, not just the default. No test currently asserts OVERLOAD triggering (T8/T10 check DISSONANT/STUCK/COMBINED but never bit2 specifically), so the gap was undetected until this live, non-default-parameter drive. | **Medium-High** (a documented requirement/feature is silently non-functional under all reachable engine states — not cosmetic, though also not a crash/data-corruption risk; the dissonant/stuck recovery paths, the ones most likely to matter perceptually, are unaffected and independently confirmed working above) | `08-code-implementation`/`07-implementation-planning` — this needs an actual threshold recalibration (e.g. `OVERLOAD_THRESHOLD` around `5`-`6` given the computed `~8.8` ceiling at max settings, or `ONSET_WINDOW_FRAMES` widened), not just a doc reword; a small remediation package, not a documentation fix like `BL-0013`/`BL-0016` |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| MSTR-001 C5 (v1.1, autonomous recovery) | `music_engine.py:228-326` (dissonant/stuck overrides + overload doubling) | T10.1/T10.2; this run's dissonance-delta live drive (100% pull-toward-tonic) | PASS |
| GDS-01 loop item 4 / GDS-03 §5 (amended, Select reset-and-randomize) | `music_engine.py:514-523` (`DIV`-seeded reload) | T5.5 (revised for randomized seeds, "one-DELTA_TABLE-step-from-reset" shape check) | PASS |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention prior VRs established, this table is the RTM-equivalent audit. `FR-1100`'s cell should
be understood as "code-complete, practically unreachable" per the new finding above — a nuance
this project's still-unauthored RTM will need to capture explicitly once written, not silently
mark green.

## Scope audit

Files touched per the package doc: `music_engine.py` only. Confirmed the dissonant/stuck/overload
overrides are all inside `_emit_channel_gen`/`_emit_noise_gen` (the same shared-routine pattern
already confirmed in VR-0002/VR-0003/VR-0004), and the `DIV`-reseeding is inside `init_engine`.
No excursion into `build_rom.py`, `input_map.py`, `gbc_lib.py`, or `visuals.py` found.

## Verdict

`IP-0007` satisfies its Definition of Done as *coded* — every claimed mechanism exists, is
correctly implemented, and (for dissonant/stuck) independently confirmed live to actually change
behavior as designed — both permanent gates pass, and the package's own already-known finding
(`BL-0015`, the bit3 transient) remains accurately characterized. The verification did surface one
new, more significant finding: the overload-recovery half of this package's own claimed behavior
is currently unreachable given `IP-0004`'s threshold constants, discovered specifically because
this run drove a non-default parameter (max density) live rather than trusting T8/T10's green
results, which never exercise bit2 at all. This does not fail `IP-0007` — the doubling logic is
correctly coded and will function the moment the threshold is recalibrated — but it is a real
functional gap, not merely cosmetic, and is recorded as such rather than downgraded to match
`BL-0005`/`BL-0013`'s doc-coherence framing. **Advancing to `VERIFIED`; this completes independent
verification of the full 7-package Foundation tranche.**
