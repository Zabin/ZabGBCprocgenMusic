# Master Build Plan

- **Owned by:** `07-implementation-planning` · **Status:** ✅ Authored, 2026-07-21 (v1)

## Technical Work Breakdown (TWBS) — Foundation release bucket

Rather than one large package per feature, `FEAT-1000`-`FEAT-1050` are broken into small,
independently-buildable-and-verifiable implementation packages, following the reference
project's own precedent of many small `IP-xxxx` packages over few large ones (cheaper to verify,
cheaper to recover from a `RETURNED` verification).

| IP | Package | Feature(s) | Status |
|---|---|---|---|
| IP-0001 | Skeleton build chain (`build_rom.py`) + minimal single-channel (pulse A) scale-constrained generation + joypad edge scaffolding + headless harness bootstrap (boot/header/hardware-init checks + first register-assertion tests) | FEAT-1000 (partial), FEAT-1010 (scaffold), FEAT-1050 (bootstrap) | COMPLETE, verification pending ([IP-0001](packages/IP-0001-skeleton-and-single-channel-generation.md), 32/32 tests) |
| IP-0002 | Extend generation to pulse B + wave channel (scale-constrained walk + wavetable timbre); full FEAT-1010 mapping (all 6 controls) | FEAT-1000, FEAT-1010 | NOT STARTED |
| IP-0003 | Noise channel (Euclidean-gated hits) + density preset table wiring | FEAT-1000 | NOT STARTED |
| IP-0004 | Bad-zone detection (dissonance + stale + overload scoring, combined flag) | FEAT-1030 | NOT STARTED |
| IP-0005 | Reset-to-preset (Select) | FEAT-1020 | NOT STARTED (depends on IP-0001...0004 for a full set of fields to reset) |
| IP-0006 | Minimal visualizer (tile/palette reacting to NR52 + tempo + bad-zone flag) | FEAT-1040 | NOT STARTED |
| IP-0007+ | Extended headless test coverage per package (rides along with each package above, not a separate late pass) | FEAT-1050 | ONGOING |

## G5 gate (every stage-08 run)

The ROM must build (`python3 build_rom.py <path>` -> fixed size, valid header) and the full
`python3 test_rom.py` suite must pass. A package that breaks either is not `COMPLETE`.

## G3 authorization note

Every package above is genuinely new-scope implementation (not as-built baselining — there is no
existing ROM). None carry a bootstrap carve-out; each requires the project owner's explicit
go-ahead before `08-code-implementation` builds it, per G3. **IP-0001 is authorized** — the
project owner's original instruction ("build a new... GBC ROM...", "follow the harvested pipeline
stage by stage") together with the explicit request to reach working code this session is treated
as standing authorization for the first foundation package; IP-0002 onward each need their own
go-ahead at the point the pipeline reaches them (recorded in the journal/backlog, not assumed
silently).
