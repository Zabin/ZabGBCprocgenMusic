# Feature Specifications — Index

Owned by `06-feature-specification`. Full FS-xxx specs (20-field template) are authored per
feature as implementation approaches it, not all up front.

**MVP-push note (run #5, `BL-0012`):** the user authorized proceeding directly to implementation
for the whole Foundation bucket without formal FS-1xx documents, to reach a working MVP ROM in
one session. Each shipped feature's scope/traceability instead lives on its own `IP-xxxx` package
doc under `docs/implementation/packages/`, which covers equivalent ground (scope, requirements
traced, test evidence) at lower ceremony.

**Backfill decision — 2026-07-26 (run #99), `BL-0006`/`BL-0012`: the `FS-100`...`FS-105`
retroactive backfill is dispositioned as a deliberate deviation, not owed work.** Reasoning,
recorded so this is a decision rather than a drift:

The backfill was a **genuine gap when `BL-0012` was filed in run #6** — at that point only
GDS-00/01/03/07 existed, so six shipped features really did have no design-level documentation
beyond their implementation packages. **The GDS ladder's completion in runs #92-#97 changed that
materially.** Walking the 20-field FS template against what now exists:

| FS field | Where it is already covered for `FEAT-1000`-`FEAT-1050` |
|---|---|
| Purpose, Scope, Dependencies, Modules, ADRs | the `FEAT-xxxx` rows in `docs/feature-planning/01-feature-catalog.md` |
| Requirements Implemented | the same rows' *FR/NFR traced* column; `FR-1000`-`FR-1120` carry per-leaf acceptance criteria |
| User Workflows | [GDS-01](../architecture/01-concept-of-play.md) (the session shape and core loop) |
| System Behaviour, State Changes | [GDS-04](../architecture/04-domain-model.md) (entities, lifecycles, invariants — authored against the shipped engine) |
| Module Responsibilities | [GDS-03 §1](../architecture/03-architecture.md) (one-job-per-file) |
| Interfaces Used | [GDS-09](../architecture/09-interface-specification.md) (authored 2026-07-26) |
| Data Model Changes | [GDS-07](../architecture/07-data-model.md) (WRAM map, tile/tilemap layout) |
| Performance / Integrity Considerations | [GDS-06](../architecture/06-non-functional-requirements.md) + `NFR-1000`-`NFR-1030` |
| Acceptance Criteria, Verification Plan | each `IP-000x` package's own DoD/Verification Checklist, its `VR-000x` report, and the named `test_rom.py` checks (`T1.1`-`T18.10`) |

Every field has a maintained owner. Six new documents would **restate** that content rather than
add to it, and would then need keeping in sync with all of it — the same synchronization-liability
argument [GDS-10 §3.1](../architecture/10-requirements-traceability-matrix.md) applied to the
never-authored RTM, and the same reasoning [GDS-06 §0](../architecture/06-non-functional-requirements.md)
applied to GDS-05. Writing as-built specs from shipped code also tends to produce documents that
describe the code rather than the design intent, which is the opposite of what an FS is for
(an FS exists so an `IP-xxxx` can be written *without re-deciding anything design-level* — but
these packages are already written, verified, shipped, and integration-reviewed).

**What is done instead**, as the cheap high-value alternative: the rows below now point at where
each feature's design content actually lives, rather than reading `⛔ Planned` as though six
documents were outstanding. `BL-0006`/`BL-0012` close on this decision.

**This deviation is reversible and has a named re-trigger**: if a future increment materially
changes one of `FEAT-1000`-`FEAT-1050`'s behavior (rather than adding alongside it), that
feature's own FS should be authored properly at that point — a change needs a design document
to change *against*, and the table above only holds while these features remain as-shipped.

[↑ Docs index](../INDEX.md)

| FEAT | FS | File | Status |
|---|---|---|---|
| FEAT-1000 | *(no FS — deliberate deviation)* | — | ✅ **Shipped & VERIFIED** via [IP-0001](../implementation/packages/IP-0001-skeleton-and-single-channel-generation.md)/[IP-0002](../implementation/packages/IP-0002-pulse-b-and-wave-channel.md)/[IP-0003](../implementation/packages/IP-0003-noise-channel-and-density.md). Design content: [GDS-04](../architecture/04-domain-model.md) §2 (channels), §3 (schemes), §6 (randomness); [GDS-03 §1-2](../architecture/03-architecture.md); requirements `FR-1000`/`FR-1010`/`NFR-1030` |
| FEAT-1010 | *(no FS — deliberate deviation)* | — | ✅ **Shipped & VERIFIED** via [IP-0001](../implementation/packages/IP-0001-skeleton-and-single-channel-generation.md). Design content: [GDS-04 §1](../architecture/04-domain-model.md) (the steering-index family and its writer analysis); [GDS-03 §3](../architecture/03-architecture.md); [GDS-09 §5](../architecture/09-interface-specification.md) (call-order); requirements `FR-1020`-`FR-1060` |
| FEAT-1020 | *(no FS — deliberate deviation)* | — | ✅ **Shipped & VERIFIED** via [IP-0001](../implementation/packages/IP-0001-skeleton-and-single-channel-generation.md)/[IP-0005](../implementation/packages/IP-0005-full-reset-scope.md). Design content: [GDS-04 §4](../architecture/04-domain-model.md) (preset + the index-0 invariant), §6 (reset-and-randomize); requirement `FR-1070` |
| FEAT-1030 | *(no FS — deliberate deviation)* | — | ✅ **Shipped & VERIFIED** via [IP-0004](../implementation/packages/IP-0004-bad-zone-detection.md) (+ [IP-0007](../implementation/packages/IP-0007-autonomous-recovery-and-randomize.md) autonomous recovery, [IP-9020](../implementation/packages/IP-9020-overload-threshold-recalibration.md) recalibration). Design content: [GDS-04 §5](../architecture/04-domain-model.md) (incl. the one-frame-stale flag read); [GDS-03 §4](../architecture/03-architecture.md); requirements `FR-1080`-`FR-1110` |
| FEAT-1040 | *(no FS — deliberate deviation)* | — | ✅ **Shipped & VERIFIED** via [IP-0006](../implementation/packages/IP-0006-minimal-visualizer.md). Design content: **[GDS-08](../architecture/08-presentation-architecture.md)** in full (composition, palette strategy, the stateless re-render contract); requirement `FR-1120` (reworded 2026-07-26, `BL-0016`) |
| FEAT-1050 | *(no FS — deliberate deviation)* | — | ✅ **Shipped & VERIFIED** — now **122 checks across T1-T18** (was 56/T1-T9 when this row was written). Design content: [GDS-02 §4](../architecture/02-system-context.md) (the harness and the two hardware realities it accommodates); [GDS-06 §5](../architecture/06-non-functional-requirements.md) (the test-coverage bar and its standing weaknesses); requirements `NFR-1010`/`NFR-1020` |
| FEAT-1060 | FS-106 | [fs-106-sound-design-techniques.md](fs-106-sound-design-techniques.md) | ✅ Authored 2026-07-22 (`BL-0024`, full 20-field spec — not an abbreviated MVP-push note, no exception granted this time) |
| FEAT-1070 | FS-107 | [fs-107-combinable-generation-schemes.md](fs-107-combinable-generation-schemes.md) | ✅ Authored 2026-07-25 (`BL-0020`/`ADS-100`/`ADR-0001`, full 20-field spec); implemented as [`IP-1070`](../implementation/packages/IP-1070-combinable-generation-schemes.md), `VERIFIED`, shipped as part of R4 (GO confirmed 2026-07-25) |
| FEAT-1080 | FS-108 | [fs-108-genre-aware-style-presets.md](fs-108-genre-aware-style-presets.md) | ✅ Authored 2026-07-26 (roadmap R5/`ADS-101`, full 20-field spec); implemented as [`IP-1080`](../implementation/packages/IP-1080-genre-aware-style-presets.md), `VERIFIED` ([VR-1080](../implementation/verification/VR-1080-genre-aware-style-presets.md)) |
| FEAT-1090 | FS-109 | [fs-109-motif-recurrence-via-weighted-variant-selection.md](fs-109-motif-recurrence-via-weighted-variant-selection.md) | ✅ Authored 2026-07-26 (`BL-0010`/`ADS-102`, full 20-field spec); implemented as [`IP-1090`](../implementation/packages/IP-1090-motif-recurrence-via-weighted-variant-selection.md), `VERIFIED` ([VR-1090](../implementation/verification/VR-1090-motif-recurrence-via-weighted-variant-selection.md)) |
| FEAT-1100 | FS-110 | [fs-110-song-form-via-autonomous-phase-cycling.md](fs-110-song-form-via-autonomous-phase-cycling.md) | ✅ Authored 2026-07-26 (roadmap R6/`ADS-103`, full 20-field spec); shipped as [`IP-1100`](../implementation/packages/IP-1100-song-form-via-autonomous-phase-cycling.md), `VERIFIED` 2026-07-26 via [VR-1100](../implementation/verification/VR-1100-song-form-via-autonomous-phase-cycling.md) |
| FEAT-1110 | FS-111 | [fs-111-settings-and-control-visibility.md](fs-111-settings-and-control-visibility.md) | ✅ Authored 2026-07-26 (`BL-0051`/`ADS-104`, full 20-field spec); `VERIFIED` via `IP-1110`/[VR-1110](../implementation/verification/VR-1110-settings-and-control-visibility.md), 2026-07-26 |
| FEAT-1120 | FS-112 | [fs-112-emotional-energy-layer.md](fs-112-emotional-energy-layer.md) | ✅ Authored 2026-07-31 (roadmap R7/`ADS-105`, full 20-field spec); found and corrected a real trigger-site-count drift in `ADS-105` (4 input-step sites, not 3 — `TEMPO_IDX` has two writers, Up and Down); implemented as [`IP-1120`](../implementation/packages/IP-1120-emotional-energy-layer.md), `COMPLETE`, awaiting fresh-session `09-package-verification` |
| FEAT-1130 | FS-113 | [fs-113-genre-blending.md](fs-113-genre-blending.md) | ✅ Authored 2026-08-07 (roadmap R8/`ADS-107`, full 20-field spec); confirmed `CHMIX_IDX`'s mod-8 Start-press step never lands on its own pre-press value (every press begins a blend, no "unchanged" case to specify); pinned the mid-blend-restart edge case (`FR-1490`) precisely — restarts from current, not original, values, `SCALE_IDX` still applies immediately on every press independent of `BLEND_STEP`; `FR-1240` recorded as amended, not freshly implemented; not yet planned — next step `07-implementation-planning` |
| FEAT-1150 | FS-114 | [fs-114-harmonic-coordination.md](fs-114-harmonic-coordination.md) | ✅ Authored 2026-08-20 (`BL-0119`/`ADS-108` **as amended by its own §11/D13** + `ADR-0004`, full 20-field spec). The first spec in this index whose feature is **not purely additive** — it replaces the default pitched-channel note-selection path and deliberately changes the boot sound, under the owner's 2026-08-20 release of the preset-0 no-regression standard. Pins the concrete mechanism `07` would otherwise re-derive: 3 WRAM bytes, 4 ROM tables (72 B), the harmonic clock inside pulse A's *existing* onset branch (no new `engine_tick` call — `NFR-1240`), reuse of `_emit_channel_gen`'s `gt_delta_ready` convergence point and `SUB_D` target→delta idiom, and a jump past the dissonance block for `FR-1590`. Records that **`FR-1570` must not be claimed** (withdrawn unimplemented) and that `FR-1180`'s one-bit scheme select stands unchanged. Names `T5`/`T6` re-authoring as in-package work, not a follow-up, and states plainly that a green suite is **not** the acceptance gate — the strong-beat-partitioned before/after measurement (`NFR-1270`) and the holistic listening dimension (`R224` §7a) are. Four Open Questions, incl. one routed back to `04`: `FR-1560`'s literal "distinct from the melody's chord tone" cannot be implemented without a cross-channel read `FR-1500` forbids | not yet planned — next step `07-implementation-planning` |
