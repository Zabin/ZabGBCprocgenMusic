# Master Build Plan

- **Owned by:** `07-implementation-planning` · **Status:** ✅ Authored, 2026-07-21 (v1)

## Technical Work Breakdown (TWBS) — Foundation release bucket

Rather than one large package per feature, `FEAT-1000`-`FEAT-1050` are broken into small,
independently-buildable-and-verifiable implementation packages, following the reference
project's own precedent of many small `IP-xxxx` packages over few large ones (cheaper to verify,
cheaper to recover from a `RETURNED` verification).

| IP | Package | Feature(s) | Status |
|---|---|---|---|
| IP-0001 | Skeleton build chain (`build_rom.py`) + minimal single-channel (pulse A) scale-constrained generation + joypad edge scaffolding + headless harness bootstrap (boot/header/hardware-init checks + first register-assertion tests) | FEAT-1000 (partial), FEAT-1010 (scaffold), FEAT-1050 (bootstrap) | **VERIFIED** ([VR-0001](verification/VR-0001-skeleton-and-single-channel-generation.md), 32/32 tests) |
| IP-0002 | Extend generation to pulse B + wave channel (scale-constrained walk + wave-as-bass role) | FEAT-1000, FEAT-1010 | **VERIFIED** ([IP-0002](packages/IP-0002-pulse-b-and-wave-channel.md), 60/60 tests; [VR-0002](verification/VR-0002-pulse-b-and-wave-channel.md), fresh-session independent verification) |
| IP-0003 | Noise channel (Euclidean-gated hits) + density preset table wiring | FEAT-1000 | **VERIFIED** ([IP-0003](packages/IP-0003-noise-channel-and-density.md), 60/60 tests; [VR-0003](verification/VR-0003-noise-channel-and-density.md), fresh-session independent verification) |
| IP-0004 | Bad-zone detection (dissonance + stale + overload scoring, combined flag) | FEAT-1030 | **VERIFIED** ([IP-0004](packages/IP-0004-bad-zone-detection.md), 60/60 tests; [VR-0004](verification/VR-0004-bad-zone-detection.md), fresh-session independent verification) |
| IP-0005 | Reset-to-preset (Select) | FEAT-1020 | **VERIFIED** ([IP-0005](packages/IP-0005-full-reset-scope.md), 60/60 tests; [VR-0005](verification/VR-0005-full-reset-scope.md), fresh-session independent verification — closed `BL-0014`) |
| IP-0006 | Minimal visualizer (tile/palette reacting to NR52 + bad-zone flag) | FEAT-1040 | **VERIFIED** ([IP-0006](packages/IP-0006-minimal-visualizer.md), 60/60 tests; [VR-0006](verification/VR-0006-minimal-visualizer.md), fresh-session independent verification — `BL-0016` filed) |
| IP-0007 | Autonomous bad-zone avoidance/recovery (no input required) + Select reframed as reset-and-randomize | FEAT-1030 (extended) | **COMPLETE** ([IP-0007](packages/IP-0007-autonomous-recovery-and-randomize.md), 60/60 tests; verification pending) |
| IP-0008+ | Extended headless test coverage per package (rode along with each package above, not a separate late pass) | FEAT-1050 | ONGOING — 60/60 across T1-T10 |

**MVP milestone reached 2026-07-21** (run #5): all six original Foundation-bucket packages
`COMPLETE`. **Extended same day** (run #6, `IP-0007`): the project owner directed that bad-zone
recovery be autonomous, not Select-only — implemented and tested, 60/60 checks, an 8000+ frame
stress run confirming both entry into and self-recovery from a bad zone with no input. IP-0002
through IP-0007 were self-tested in the same session that authored them (the user authorized
"accept single session limitations just this once" for the MVP push, `BL-0012`) — independent
verification via `09-package-verification` is owed for each, one per fresh session, same as
`IP-0001` originally was before its own independent verification (`VR-0001`). **IP-0002 through
IP-0006 are now independently `VERIFIED`** ([VR-0002](verification/VR-0002-pulse-b-and-wave-channel.md),
[VR-0003](verification/VR-0003-noise-channel-and-density.md),
[VR-0004](verification/VR-0004-bad-zone-detection.md),
[VR-0005](verification/VR-0005-full-reset-scope.md),
[VR-0006](verification/VR-0006-minimal-visualizer.md), all the same genuinely fresh session) —
IP-0007 remains owed.

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
