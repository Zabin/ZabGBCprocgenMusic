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
| IP-9010 | Channel-mix gating — wire `CHMIX_IDX` to an actual channel-activity-mask table | `BL-0019` (High) | **VERIFIED** — [package](packages/IP-9010-channel-mix-gating.md), [VR-9010](verification/VR-9010-channel-mix-gating.md), `CHMIX_MASKS` table + gating in `_emit_channel_gen`/`_emit_noise_gen`, T12 suite (5 checks), 77/77 full-suite tests, independent non-default live drive (preset 5, wave+noise only) confirmed exclusion + re-inclusion, 8200-frame stress run clean. Two Low/Low-Medium findings (undeclared doc-scope addition; a code-comment's backlog-filing claim not actually filed — see VR-9010) |
| IP-9020 | Overload threshold recalibration — `OVERLOAD_THRESHOLD`/`ONSET_WINDOW_FRAMES` | `BL-0017` (Medium-High) | **VERIFIED** — [package](packages/IP-9020-overload-threshold-recalibration.md), [VR-9020](verification/VR-9020-overload-threshold-recalibration.md), `OVERLOAD_THRESHOLD` 20→7 (empirically recalibrated, not just the analytical VR-0007 formula — see package note), T13 suite (2 checks), 77/77 full-suite tests, independent non-default live drive (`TEMPO_IDX=5`/`DENSITY_IDX=6`, distinct from T13's own fixture) confirmed OVERLOAD reachable and default preset non-spurious, 8200-frame default-preset stress run clean. One Low finding (undeclared `Claude.md` doc-scope addition — see VR-9020) |

Both depend only on already-`VERIFIED` code (no dependency on each other — see the TWBS's
sequencing note for the session-hygiene recommendation to build `IP-9010` first, not a technical
requirement). Both are `VERIFIED` (see the Status column above) — G3 authorization, granted in
an earlier run, was the only blocker; no longer outstanding.

## Technical Work Breakdown (TWBS) — Sound Design Techniques (`FS-106`, `BL-0024`)

See [`01-technical-work-breakdown.md`](01-technical-work-breakdown.md) for the full verb-inventory,
supersession-sweep, and split rationale.

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1060 | Arpeggio + duty-cycle variation | FR-1130, FR-1160 | **VERIFIED** — [package](packages/IP-1060-arpeggio-and-duty-cycle.md), [VR-1060](verification/VR-1060-arpeggio-and-duty-cycle.md): 65/65 tests, non-default `OCTAVE_IDX=3`/`SCALE_IDX=2` independently re-driven, 8200-frame stress run clean |
| IP-1061 | Vibrato + portamento | FR-1140, FR-1150 | **VERIFIED** — [package](packages/IP-1061-vibrato-and-portamento.md), [VR-1061](verification/VR-1061-vibrato-and-portamento.md): 65/65 tests, non-default `TEMPO_IDX=7`/`OCTAVE_IDX=3` independently re-driven, 8200-frame stress run clean |

## Technical Work Breakdown (TWBS) — Combinable Generation Schemes (`FS-107`, `BL-0020`)

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1070 | Combinable generation schemes — Scheme E (Euclidean onset timing + fixed-motif pitch selection) | FR-1180...FR-1220, NFR-1060, NFR-1070 | **VERIFIED** — [package](packages/IP-1070-combinable-generation-schemes.md), [VR-1070](verification/VR-1070-combinable-generation-schemes.md), 85/85 full-suite tests, independent non-default live drive (density=5/tempo=6/preset 6 + a mid-note scheme-switch scenario) confirms the DoD. One Medium finding (pulse A/B Scheme E is code-complete but unreachable via any shipped preset). |

**G3 authorization for `IP-1070`**: **granted explicitly by the user, 2026-07-25** (asked directly
via `AskUserQuestion`, confirmed "Yes, authorize and build it" — not assumed from ambiguous
phrasing). Recorded here as the basis.

**G3 authorization for `IP-1060`/`IP-1061`**: the user's request that filed `BL-0024` — "Iterating
the pipeline skill run through to implantation the concepts in R216... Iterate until they are all
in a committed and pushed ROM" — is explicit, direct authorization to build and verify this
specific, scoped feature. Recorded here as the basis, distinct from and not extending to
`IP-9010`/`IP-9020`, which remain separately unauthorized (see below).

## Technical Work Breakdown (TWBS) — Genre-Aware Style Presets (`FS-108`, roadmap R5)

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1080 | Genre-aware style presets — parallel `STYLE_TABLE` keyed by `CHMIX_IDX`, applied immediately on Start press | FR-1230...FR-1260, NFR-1080, NFR-1090 | **VERIFIED** — [package](packages/IP-1080-genre-aware-style-presets.md), [VR-1080](verification/VR-1080-genre-aware-style-presets.md). 93/93 full-suite tests (T1-T15), ROM budget +78 bytes (29271 free, independently re-measured). Independently live-driven at non-default/exact-frame/adversarial-random combinations the suite's own fixtures don't use — one Medium finding (acceptance-criterion precision on bad-zone independence under general play, not a code defect) and one Low (informational ROM-budget re-confirmation). |

**G3 authorization for `IP-1080`**: **granted explicitly by the user, 2026-07-26** — asked
directly (chat) whether `IP-1080` was authorized; the user replied "All work is pre authorized
(generate new sessions for verification work and continue)." Recorded here as the basis, and as a
standing forward authorization for this pipeline's future packages in this same increment (not a
retroactive waiver of the independent-verification rule — `09-package-verification` still runs in
a genuinely fresh session/dispatched agent for every package, per the user's own explicit
instruction).

## Technical Work Breakdown (TWBS) — Motif Recurrence via Weighted Variant Selection (`FS-109`, `BL-0010`)

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1090 | Motif recurrence via weighted variant selection — extends `IP-1070`'s `MOTIF_TABLE` to 4 pre-composed variants, autonomously selected at motif-cycle boundaries via a weighted lookup table | FR-1270...FR-1300, NFR-1100, NFR-1110 | **VERIFIED** — [package](packages/IP-1090-motif-recurrence-via-weighted-variant-selection.md), [VR-1090](verification/VR-1090-motif-recurrence-via-weighted-variant-selection.md). 102/102 full-suite tests (T1-T16), ROM budget -182 bytes (29089 free, independently re-measured, exact match). Independently live-driven with a *guaranteed* exact-frame collision between a motif-cycle-boundary variant draw and an `IP-1080` style change (constructed from an empirically-recorded boundary-frame list, since the shipped `T16.8`'s own 47-frame interval was found to never actually produce a same-frame collision within its own test window), plus a tight 2-12-frame periodic Start-press sweep and an extended 60,000-frame retention/switch statistical sample — no corruption found. Two Medium findings (statistical weakness of `T16.6`'s own small sample; `T16.8`'s claimed same-frame-collision coverage doesn't actually occur in its own fixture) and one Low (a stale `docs/features/INDEX.md` status row, unrelated to this package's own diff) — none block `VERIFIED`. A test-methodology defect was caught and fixed within the implementing run: an initial exact-match assertion between observed onset degrees and `MOTIF_TABLE` values failed under bad-zone conditions (`IP-0007`'s autonomous dissonant-pull/stuck-escape overrides the motif-picked delta, same interaction `T14.3`'s own looser invariant already accounts for) — fixed by excluding bad-zone-active frames from that specific comparison, documented inline in the test. |

**Verb inventory** (one verb, single package — no split needed): this capability needs only
*apply* (autonomously selecting and applying which motif-variant row is active) — no *generate*
(variants are pre-composed data, not derived at runtime), no *render* (no visualizer signal
requested by any FR), no *persist* (no save data), no *review* (deferred to `09-content-review`
per the standing convention, not a package verb). One package, `08-code-implementation`.

**Supersession sweep**: `FS-109`'s framing is "extends" `MOTIF_TABLE`, not "supersedes" it — the
existing single-row shape is retained as variant 0, not retired. Swept `music_engine.py`/
`input_map.py`/`build_rom.py` for every literal reference to `motif_table`/`MOTIF_TABLE` to confirm
no other call site assumes the old single-row (non-indexed) shape: the only reads are the single
per-onset lookup inside `_emit_channel_gen`'s `gt_e_*` branch (line ~465, the site this package
extends to be variant-relative) and the single emission site in `build_engine_asm` (line ~1095,
which this package also extends). No other call site found — clean.

**G3 authorization for `IP-1090`**: **covered by the same standing forward authorization recorded
above for `IP-1080`** — the user's 2026-07-26 "All work is pre authorized (generate new sessions
for verification work and continue)" was recorded as a standing authorization for this pipeline's
future packages *in this same increment*, and the user's subsequent "Iterate pipeline skill"
instruction (after `IP-1080`'s own G4 GO confirmation) continued that same increment with no
narrowing of scope. `IP-1090` is therefore treated as G3-authorized on that same basis — not a
new, independently-solicited go-ahead, and named here explicitly so the trail is auditable rather
than assumed silently.

## Technical Work Breakdown (TWBS) — Song-Form via Autonomous Phase Cycling (`FS-110`, roadmap R6)

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1100 | Song-form via autonomous phase cycling — a new, independent state machine (`SONG_STATE`/`SONG_STATE_TIMER_LO`/`SONG_STATE_TIMER_HI`) cycling 4 phases, overwriting `TEMPO_IDX`/`DENSITY_IDX` per phase transition | FR-1310...FR-1340, NFR-1120, NFR-1130 | **COMPLETE** — 112/112 full-suite tests (T1-T17), ROM budget -112 bytes (28977 free, measured via `ADR-0002`'s own `rom.pos` method). **Caught and fixed a real regression during implementation**: the package's own initial draft made phase 0 (INTRO) intentionally differ from the shipped default preset, breaking 10 pre-existing tests — reverted to match `PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX` exactly, the same no-regression discipline `STYLE_TABLE`/`MOTIF_TABLE` already established. **Caught and fixed a flawed test-timing methodology within this same run**: an initial `T16.7` exact-match assertion (from `IP-1090`) began failing once song-form's own density changes altered the Euclidean-onset trajectory — root-caused to sampling `BAD_ZONE_FLAGS` one frame too late relative to when the bad-zone override actually reads it; fixed by sampling the flags value in effect *before* the tick, not after. |

**Verb inventory** (one verb, single package — no split needed): this capability needs only
*apply* (autonomously cycling phases and overwriting `TEMPO_IDX`/`DENSITY_IDX`) — no *generate*
(phase data is authored, not derived at runtime), no *render* (no visualizer signal requested by
any FR), no *persist* (no save data), no *review* (deferred to `09-content-review` per the
standing convention). One package, `08-code-implementation`.

**Supersession sweep**: `FS-110` neither retires nor generalizes an existing model — it adds a
new, independent tick alongside `_emit_badzone_tick`/each channel's `gen_tick`, none of which are
modified. No sweep applicable (nothing being superseded); confirmed by re-reading `ADS-103` §2's
own "entirely unmodified" claim against the current `engine_tick` call sequence — clean.

**Concrete data resolved this pass** (`FS-110` Open Question 1): `SONG_TABLE` — 4 rows × 4 bytes
(`tempo_idx`, `density_idx`, `duration_lo`, `duration_hi`, duration in frames, 16-bit to support a
genuinely multi-minute cycle per R6's own framing, first-guess placeholders per the standing
`BL-0005`-class deferral):

| Phase | `TEMPO_IDX` (BPM) | `DENSITY_IDX` (k) | Duration (frames, ~60fps) |
|---|---|---|---|
| 0 INTRO | 2 (90 BPM) | 1 (k=3) | 1800 (~30s) |
| 1 BUILD | 4 (120 BPM) | 4 (k=6) | 1800 (~30s) |
| 2 PEAK | 6 (160 BPM) | 6 (k=10) | 1200 (~20s) |
| 3 BREAKDOWN | 3 (105 BPM) | 2 (k=4) | 1800 (~30s) |

Full cycle ≈ 6600 frames (~110s, ~1.8 minutes) — satisfies R6's "audible over a multi-minute
session" framing. **WRAM addresses resolved**: `SONG_STATE` = `0xC03D`, `SONG_STATE_TIMER_LO` =
`0xC03E`, `SONG_STATE_TIMER_HI` = `0xC03F` (confirmed free against `docs/architecture/
07-data-model.md`: `0xC03C` is `IP-1090`'s `MOTIF_VARIANT_IDX`, `0xC03D`-`0xC04F` remains genuine
unused headroom before `JOY_PREV` at `0xC050`) — **3 new WRAM bytes, not `ADS-103`/`FS-110`'s
originally-estimated 2**, a small, disclosed deviation: a 16-bit timer (not 1 byte) is needed to
reach multi-minute phase durations without an awkward sub-frame-counting workaround; `SONG_TABLE`
is correspondingly 16 bytes (4×4), not `ADS-103`'s originally-estimated 12 (4×3) — both deviations
are negligible in absolute ROM/WRAM terms (`NFR-1120`'s own budget framing is unaffected in
substance) and are recorded here rather than silently absorbed.

**G3 authorization for `IP-1100`**: **granted explicitly by the user, 2026-07-26** — the user's own
words, "Use your judgement according to the release plan to iterate," is a direct, fresh
delegation of judgment to continue building per `docs/roadmap/04-release-roadmap.md`'s own
sequence (R6 is that sequence's next release) — a stronger and more explicit basis than the
"standing forward authorization" reasoning used for `IP-1090`, and recorded here as such rather
than conflated with it.

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
silently). **`IP-1060`/`IP-1061` ARE authorized** — the user's own `BL-0024`-filing request
explicitly directed the pipeline to carry the R216 sound-design-techniques feature through
implementation and verification ("iterate until... committed and pushed"), recorded as the
per-package go-ahead for these two packages specifically. **`IP-9010`/`IP-9020` ARE authorized as
of 2026-07-25 (pipeline journal run #33)** — after this run's own reconciliation surfaced that
neither package had actually been built despite an earlier session's directing premise assuming
otherwise, the user was asked explicitly via `AskUserQuestion` and chose to grant G3 for both now,
accepting that their independent verification moves to a future fresh session (this session
cannot verify its own same-session implementation work).
