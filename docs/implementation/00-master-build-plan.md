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
| IP-0007 | Autonomous bad-zone avoidance/recovery (no input required) + Select reframed as reset-and-randomize | FEAT-1030 (extended) | **VERIFIED** ([IP-0007](packages/IP-0007-autonomous-recovery-and-randomize.md), 60/60 tests; [VR-0007](verification/VR-0007-autonomous-recovery-and-randomize.md), fresh-session independent verification — `BL-0017` filed, Medium-High) |
| IP-0008+ | Extended headless test coverage per package (rode along with each package above, not a separate late pass) | FEAT-1050 | ONGOING — 60/60 across T1-T10 |

**MVP milestone reached 2026-07-21** (run #5): all six original Foundation-bucket packages
`COMPLETE`. **Extended same day** (run #6, `IP-0007`): the project owner directed that bad-zone
recovery be autonomous, not Select-only — implemented and tested, 60/60 checks, an 8000+ frame
stress run confirming both entry into and self-recovery from a bad zone with no input. IP-0002
through IP-0007 were self-tested in the same session that authored them (the user authorized
"accept single session limitations just this once" for the MVP push, `BL-0012`) — independent
verification via `09-package-verification` is owed for each, one per fresh session, same as
`IP-0001` originally was before its own independent verification (`VR-0001`). **All 7 Foundation
packages are now independently `VERIFIED`** ([VR-0002](verification/VR-0002-pulse-b-and-wave-channel.md),
[VR-0003](verification/VR-0003-noise-channel-and-density.md),
[VR-0004](verification/VR-0004-bad-zone-detection.md),
[VR-0005](verification/VR-0005-full-reset-scope.md),
[VR-0006](verification/VR-0006-minimal-visualizer.md),
[VR-0007](verification/VR-0007-autonomous-recovery-and-randomize.md), all the same genuinely
fresh session, `IP-0001` verified separately per `VR-0001`). **`10-integration-review` completed**
([report](../reviews/integration-review-foundation-bucket.md)) with 2 findings: `BL-0019` (High —
channel-mix has no consumer) and `BL-0018` (Low-Medium — GDS-07 doc gap); `BL-0017` re-surfaced.
Recommend against `11-release-readiness` until `BL-0019` is remediated and re-verified.

## Technical Work Breakdown (TWBS) — Foundation-bucket remediation tranche

See [`01-technical-work-breakdown.md`](01-technical-work-breakdown.md) for the full verb-inventory
and supersession-sweep rationale. Two bug-remediation packages, `IP-9xx0` series (no owning FS —
both cite their `BL-xxxx` directly per this skill's ID convention):

| IP | Package | BL cited | Status |
|---|---|---|---|
| IP-9010 | Channel-mix gating — wire `CHMIX_IDX` to an actual channel-activity-mask table | `BL-0019` (High) | **NOT STARTED** — fully specified, [package](packages/IP-9010-channel-mix-gating.md) written; **not `READY`, no G3 authorization on record** |
| IP-9020 | Overload threshold recalibration — `OVERLOAD_THRESHOLD`/`ONSET_WINDOW_FRAMES` | `BL-0017` (Medium-High) | **NOT STARTED** — fully specified, [package](packages/IP-9020-overload-threshold-recalibration.md) written; **not `READY`, no G3 authorization on record** |

Both depend only on already-`VERIFIED` code (no dependency on each other — see the TWBS's
sequencing note for the session-hygiene recommendation to build `IP-9010` first, not a technical
requirement). Neither is `READY` in the stage-07 sense used elsewhere on this plan, since that
label is reserved for "dependencies `VERIFIED`" — these packages' blocker is **G3 authorization**,
not a dependency.

## Technical Work Breakdown (TWBS) — Sound Design Techniques (`FS-106`, `BL-0024`)

See [`01-technical-work-breakdown.md`](01-technical-work-breakdown.md) for the full verb-inventory,
supersession-sweep, and split rationale.

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1060 | Arpeggio + duty-cycle variation | FR-1130, FR-1160 | **VERIFIED** — [package](packages/IP-1060-arpeggio-and-duty-cycle.md), [VR-1060](verification/VR-1060-arpeggio-and-duty-cycle.md): 65/65 tests, non-default `OCTAVE_IDX=3`/`SCALE_IDX=2` independently re-driven, 8200-frame stress run clean |
| IP-1061 | Vibrato + portamento | FR-1140, FR-1150 | **COMPLETE** — [package](packages/IP-1061-vibrato-and-portamento.md), 65/65 tests, 8000+ frame stress run clean; verification pending |

**G3 authorization for `IP-1060`/`IP-1061`**: the user's request that filed `BL-0024` — "Iterating
the pipeline skill run through to implantation the concepts in R216... Iterate until they are all
in a committed and pushed ROM" — is explicit, direct authorization to build and verify this
specific, scoped feature. Recorded here as the basis, distinct from and not extending to
`IP-9010`/`IP-9020`, which remain separately unauthorized (see below).

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
silently). **`IP-9010`/`IP-9020` are not authorized** — no user go-ahead is on record for either;
both require an explicit per-package go-ahead before `08-code-implementation` may build them.
**`IP-1060`/`IP-1061` ARE authorized** — the user's own `BL-0024`-filing request explicitly
directed the pipeline to carry the R216 sound-design-techniques feature through implementation
and verification ("iterate until... committed and pushed"), recorded as the per-package go-ahead
for these two packages specifically.
