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
| IP-1100 | Song-form via autonomous phase cycling — a new, independent state machine (`SONG_STATE`/`SONG_STATE_TIMER_LO`/`SONG_STATE_TIMER_HI`) cycling 4 phases, overwriting `TEMPO_IDX`/`DENSITY_IDX` per phase transition | FR-1310...FR-1340, NFR-1120, NFR-1130 | **VERIFIED** 2026-07-26 — 112/112 full-suite tests (T1-T17), independent live-drive (guaranteed same-frame Start-press/phase-transition collisions forced at all three cycle-internal boundaries, not just the first; an empirical `OVERLOAD`-frequency comparison across all 4 phases) confirms the DoD, via [VR-1100](verification/VR-1100-song-form-via-autonomous-phase-cycling.md). ROM budget -112 bytes (28977 free, independently re-measured via `ADR-0002`'s own `rom.pos` method, matching exactly). **Caught and fixed a real regression during implementation**: the package's own initial draft made phase 0 (INTRO) intentionally differ from the shipped default preset, breaking 10 pre-existing tests — reverted to match `PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX` exactly, the same no-regression discipline `STYLE_TABLE`/`MOTIF_TABLE` already established. **Caught and fixed a flawed test-timing methodology within this same run**: an initial `T16.7` exact-match assertion (from `IP-1090`) began failing once song-form's own density changes altered the Euclidean-onset trajectory — root-caused to sampling `BAD_ZONE_FLAGS` one frame too late relative to when the bad-zone override actually reads it; fixed by sampling the flags value in effect *before* the tick, not after. |

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

## Technical Work Breakdown (TWBS) — Settings & Control Visibility (`FS-111`, `BL-0051`)

| IP | Package | Requirements | Status |
|---|---|---|---|
| IP-1110 | Settings & control visibility — 5 new bar-height indicator tiles (tempo/octave/scale/density/channel-mix), extending `visuals.py`'s existing `update_visuals`/`CHANNEL_CELLS` mechanism | FR-1350...FR-1380, NFR-1140, NFR-1150, NFR-1160 | **VERIFIED** 2026-07-26 — 122/122 full-suite tests (T1-T18); independently verified via [VR-1110](verification/VR-1110-settings-and-control-visibility.md). ROM budget: +449 bytes (28528 free, measured via `ADR-0002`'s own `rom.pos` method, independently re-measured by `VR-1110` — larger than the package's original 128-byte tile-data-only estimate, since the per-frame update/init routines' own instruction overhead wasn't counted in that estimate; disclosed here rather than silently absorbed). **Caught and fixed a real regression during implementation**: the package's initial placement of `_emit_update_settings_row` at the very start of `update_visuals` caused the *existing* channel-activity writes to intermittently drop on ordinary frames with no button input (T9.3 failed); reverted to the original tail position, which does not exhibit this regression — `VR-1110` independently re-confirmed via a fresh 3000-frame zero-input stress run (0 mismatches). ~~**Found (not fixed) a disclosed, narrower, self-healing timing finding**: on the exact frame Select is pressed, `apply_input`'s full `init_engine` reset costs enough extra CPU that this package's own settings-row VRAM writes for that one frame are silently dropped~~ — **WITHDRAWN 2026-07-31 (`BL-0069`)**: falsified by direct measurement. No VRAM write is dropped on any frame; PyBoy models no PPU-mode gating (`R301` §3), and a WRAM mirror of each write matches VRAM on every frame of every class. The one-frame lag is a `pb.tick()` harness sampling artifact, uniform across every frame class including idle ones — not Select-specific, not a dropped write. `test_rom.py`'s `T18.9`/`T18.10` (widened by `IP-9030` v2 to 2 pre-Select sequences) verify the WRAM reset lands on the exact frame and the display catches up within one further frame; `VR-1110`'s independent reproduction confirmed the same lag/self-heal shape but, per its own correction notice, attributed it to the wrong cause. |

**Verb inventory** (one verb, single package — no split needed): this capability needs only
*render* (a new read-and-display routine reacting to already-existing WRAM values) — no *generate*
(the tile-pattern data is authored, not derived at runtime), no *apply* (this feature writes no
engine state), no *persist* (no save data), no *review* (deferred to `09-content-review` per the
standing convention). One package, `08-code-implementation` (a visualizer logic change, not pure
art/content authoring — the tile-pattern *data* is simple enough, and coupled tightly enough to
the new per-frame routine reading it, that splitting a `08-content-authoring` half off would be
artificial, unlike `FEAT-1060`'s own arpeggio/vibrato-portamento split).

**Supersession sweep**: `FS-111` neither retires nor generalizes an existing model — it adds new
tile patterns and new tilemap cells alongside the existing `TILE_OFF`/`TILE_ON`/`CHANNEL_CELLS`
mechanism, none of which are modified. Grepped `build_rom.py`/`music_engine.py`/`gbc_lib.py` for
any other `0x98xx` (tilemap) reference — found nothing else touches the tilemap besides
`visuals.py`'s own `CHANNEL_CELLS` writes; confirmed clean.

**Concrete decisions resolved this pass** (`FS-111` Open Questions 1-2): (1) `OCTAVE_IDX`/
`SCALE_IDX` (4 possible values each) share the same 8-level tile-pattern set as `TEMPO_IDX`/
`DENSITY_IDX`/`CHMIX_IDX` (8 possible values each) rather than a separate narrower set — simpler
and cheaper, at the cost of those two bars never exceeding half-full; a first-guess placeholder
per the standing `BL-0005`-class visual-tuning deferral, not a final content decision. (2) The 5
new tilemap cells are `TILEMAP_BASE+4` through `TILEMAP_BASE+8` — confirmed against the current
`visuals.py` source that `CHANNEL_CELLS` occupies exactly `TILEMAP_BASE+0`..`+3` and no other
module writes or reads any other tilemap address, so these 5 cells are genuinely free, same
tilemap row, immediately following the channel-activity cells.

**G3 authorization for `IP-1110`**: **granted on the user's standing basis, 2026-07-26** — the
user's own words this session, "Iterate pipeline skill with pre authorization as per before,"
explicitly reaffirm that the prior authorization to iterate the pipeline (the same standing basis
already recorded for `IP-1090`) continues to apply across this run's internal steps, including
this package. Recorded here as its own explicit citation, per this project's standing rule that no
package's G3 basis is ever assumed silently, even when it rides a standing instruction rather than
a fresh one.

## Technical Work Breakdown (TWBS) — VRAM Write-Integrity Detection (`BL-0069`, remediation tranche)

| IP | Package | BL cited | Status |
|---|---|---|---|
| IP-9030 | **VBlank budget assertion** (re-scoped v2, 2026-07-31 — was *VRAM write-integrity detection*): a `VIS_ENTRY_LY` diagnostic recording `LY` at **entry** to `update_visuals`, plus a `T19` suite asserting it stays within VBlank (144-153) across five frame classes. Replaces the v1 write-integrity scope, which was unbuildable — the harness accepts every VRAM write regardless of PPU mode, so such a check could never fail | `BL-0069` (Medium); folds in `BL-0052`, `BL-0057`; doc half of `BL-0040` | **VERIFIED** 2026-08-14 — see [VR-9030](verification/VR-9030-vblank-budget-assertion.md). 154/154 full-suite tests (`T1`-`T21`). Independently re-derived `VIS_ENTRY_LY` from a fixture of the verifier's own construction (50-frame idle stretch + A/Down presses, min/max 152/153, matching); independently perturbed a throwaway build (400 `NOP`s before the probe) and confirmed `T19` would genuinely fail (`VIS_ENTRY_LY` read 2, outside 144-153) — the checks are not vacuous. No findings. v1 was `BLOCKED` 2026-07-31 when its own measurement falsified its premise; the Blocking Report is retained in the package doc. |
| IP-8010 | Remove the vestigial patch-point dicts — `build_engine_asm`/`build_input_asm` construct a `patches = {}` never assigned into, discarded by every caller; delete the dead scaffolding, no behavior change | `BL-0064` (Low); doc-only halves (`GDS-03` language, six `FS-1xx` fields) explicitly routed elsewhere — GDS-03's to `03`, FS fields already clean | **VERIFIED** 2026-08-14 — see [VR-8010](verification/VR-8010-remove-vestigial-patch-point-dicts.md). Independently rebuilt both the pre- and post-refactor commits from git history (not the reported hash): byte-identical, SHA-256 `a646a651af...` confirmed. `test_rom.py` itself byte-identical pre/post; current-tip suite 154/154. No findings. |
| IP-8020 | Shared WRAM constants module — extract the 11 constants `visuals.py` duplicates from `music_engine.py` (5 index addresses, 5 `PRESET_*` values, `BAD_ZONE_FLAGS`) into a new dependency-free shared module, preserving the acyclic-import rule; byte-identical-ROM equivalence contract (Python-level relocation only) | `BL-0065` (Low-Medium); explicitly excludes `LY`/`VIS_ENTRY_LY` (not instances of the pattern — see package's own reasoning) | **VERIFIED** 2026-08-14 — see [VR-8020](verification/VR-8020-shared-wram-constants-module.md). Independently rebuilt both pre/post-refactor commits from git history: byte-identical, SHA-256 `a646a651af...` confirmed. `wram_constants.py` independently confirmed dependency-free; `visuals.py` confirmed to no longer locally declare any of the 11; `LY`/`VIS_ENTRY_LY` confirmed still out of scope. `test_rom.py` byte-identical pre/post; current-tip suite 154/154. No findings. |
| IP-1120 | Emotional/Energy Layer — 2 new derived WRAM bytes (`AROUSAL`/`VALENCE`), recomputed only at the 6 write sites that can change their inputs (never per-frame); zero player-visible change, groundwork for roadmap R9's future mood-reactive visualizer work | `FS-112`/`FEAT-1120`, roadmap R7; `FR-1390`...`FR-1420`, `NFR-1170`, `NFR-1180` | **VERIFIED** 2026-08-14 — see [VR-1120](verification/VR-1120-emotional-energy-layer.md). 154/154 full-suite tests. Independently hand-derived `AROUSAL`/`VALENCE` for a non-trivial combination (`TEMPO_IDX=7`/`DENSITY_IDX=5`/`SCALE_IDX=2` via 3 Up+5 B+2 A taps, none of `T20`'s own fixtures) — exact match. `visuals.py` independently confirmed untouched. No findings. **R7 tranche fully VERIFIED — all 4 packages (`IP-9030`/`IP-8010`/`IP-8020`/`IP-1120`) closed.** |

**Verb inventory.** This capability needs only *review* (detect and quantify an existing
behaviour) — no *generate*, no *apply*, no *persist*. The *render* verb is explicitly **not**
covered and that is the point: `R308` §8.4 and `R101` §8.4 both state that remediation (changing
how or when the visualizer writes) must follow quantification, not accompany it. **Deferral
recorded explicitly**: the fix — whether shaving per-frame work, adding cycle-cost budgeting
(`R101` §8.3's ~150-emitter package), or moving visualizer writes into a dedicated VBlank ISR — is
deliberately **not** in scope, and which of those is even appropriate depends on the number this
package produces.

**Supersession sweep.** Nothing is retired or generalized — the package adds a diagnostic and
tests alongside unmodified routines. Sweep not applicable; recorded as a positive result rather
than silence.

**Right-sizing decisions, with rationale:**

- **`BL-0052` and `BL-0057` folded in, not split out.** Both are `DEFERRED` test-hardening items
  in `test_rom.py`, both small, and both are instances of the *same* pattern GDS-06 §5 named as a
  discipline-level observation — a shipped test demonstrating a mechanism once where the claim is
  general. This package's own Definition of Done is "the test suite actually covers the claims it
  makes," which is exactly what those two items are. One stage-08 run, one file, one coherent DoD.
  Splitting them into their own package would produce two near-empty packages and a third
  invocation for no traceability gain.
- **The `VIS_END_LY` diagnostic is folded in, and this is a real judgement call.** It is a
  production ROM change inside what is otherwise a test package, which normally argues for a
  split. It is included because **without it the package's central question is unanswerable**:
  PyBoy's tick granularity is per-frame, so the harness cannot observe mid-routine PPU state, and
  "how far past VBlank does `update_visuals` finish" — the number `R101` §8.3 says decides the
  remediation — simply cannot be measured from the test side alone. Six bytes of ROM is the
  minimum change that makes the problem measurable at all. Splitting it would mean shipping a
  detection package that detects the symptom but cannot size it, then a second package to size it.
- **The fix is not folded in**, per the verb inventory above.

**`BL-0040`'s remaining half rides along as a doc-only task** (Implementation Task 6): `IP-1080`'s
Definition of Done carries the same over-absolute bad-zone-independence claim that `FS-108`'s
acceptance criterion (4) carried before run #99 corrected it. Same fix, same mechanism-level
phrasing. It is in this package rather than its own because it is a one-sentence wording change in
a document this skill was already opening.

**G3 authorization for `IP-9030` v2**: **RE-CONFIRMED 2026-07-31** — the user's explicit words
this turn, *"Continue to iterate on assuming pre authorization for everything this session,"*
following the earlier turn's *"Same pre authorization as before."* Cited as the basis rather than
assumed silently: this is a fresh, contemporaneous grant covering the re-scoped v2 package
specifically (a permanent per-frame `LY` diagnostic + `T19`), not a reuse of the superseded
2026-07-26 grant. ~~Previously: **SUPERSEDED 2026-07-31 by the v2 re-scope; `NEEDS RE-CONFIRMATION`.**~~ The 2026-07-26 grant rested on the user's *"Same pre authorization as before"*, and it
was correctly cited — but it was given for a package whose objective was to detect and quantify a
dropped-VRAM-write behaviour that has since been shown not to exist. The v2 package addresses a
different (real) problem, ships a **permanent per-frame ROM diagnostic** rather than removable
instrumentation, and additionally corrects four documents that carry the falsified claim. Full
reasoning in the package's own *Authorization (G3)* section. The planning judgement is that the
user's underlying intent is better served by v2 than by v1 and nothing here is irreversible — but
that a grant given for X is not a grant for Y, and the user should decide. Cited explicitly rather
than assumed, in both directions. **Note this is a normal code/test package owned by `08-code-implementation`, not a
refactoring package** — the "refactoring packages are never pre-authorized" rule (`IP-8xx0`,
`08-refactoring`) does not apply here. It *does* apply to `BL-0064`/`BL-0065`, which remain
unplanned and would each need their own fresh go-ahead.

## Technical Work Breakdown (TWBS) — Genre Blending (`FS-113`, roadmap R8)

| IP | Package | FR/NFR cited | Status |
|---|---|---|---|
| IP-1130 | Genre Blending — interpolates `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` between `STYLE_TABLE` rows over 4 discrete steps on a Start press (`SCALE_IDX` hard-switches immediately, unchanged); 7 new independent WRAM bytes (`BLEND_SRC_TEMPO`/`DENSITY`/`DUTY`, `BLEND_STEP`, `BLEND_DELTA_TEMPO`/`DENSITY`/`DUTY`); no new input control | `FS-113`/`FEAT-1130`, roadmap R8; `FR-1470`...`FR-1490`, `NFR-1210`...`NFR-1230`; amends `FR-1240` | **VERIFIED** 2026-08-09 — see [VR-1130](verification/VR-1130-genre-blending.md) (re-verification pass, commit `f6fd243`). 154/154 full-suite tests (`T1`-`T21`), ROM budget independently re-measured (4477 used/28291 free). The F1 remediation's core claims independently re-derived and confirmed: the `BLEND_DELTA_*` precompute fix is correct (hand-derived at `BLEND_STEP=3`/preset 1→2, a value+pair the shipped `T21.3b` doesn't itself cover, exact match), `BLEND_STEP`'s explicit boot/Select initialization is correct (confirmed against a side-by-side rebuild of the pre-remediation commit, which shows the previously-undiagnosed boot-time spurious mini-blend genuinely existed and self-corrected by coincidence), and the mid-blend-restart contract (`FR-1490`) holds under a 4th independently-constructed sequence. **Three non-blocking findings, none a functional defect**: (1) Medium — the remediation's own disclosed timing-effect narrative ("the combined `begin_blend`+`blend_tick` cost on the Start-press frame itself") is scoped too narrowly; independent `hook_register` tracing shows the same `{0-then-2 calls per harness tick()}` pattern is a general, ~30-frame-periodic engine-wide characteristic present even with zero blend activity, not something confined to or caused by the press frame — `FR-1480`'s exact-landing guarantee is unaffected in every case tested, but the causal attribution in the commit message/code comments/this row is inaccurate and should be corrected; the underlying ~30-frame periodicity itself is pre-existing and outside this package's scope. (2) Low-Medium — the `T17.6` test-change's own stated justification ("blend_tick... runs after song_tick" as if newly true) is factually wrong: that call order was already present in the original `7c9ccb2` implementation, independently confirmed by rebuilding it; the test change's *result* is correct, only its reasoning is misattributed. (3) Low — `NFR-1220`'s body text still says "4" new WRAM bytes where the RTM's own note three lines below correctly says "7". **Carried forward, still open**: the package doc's own Risks field (`IP-1130-genre-blending.md:17`) still reads stale `N=16` text, untouched by this remediation (original `VR-1130` F2/current F4). The disclosed `T9.3` `NR52`/visuals self-healing race is unchanged (unrelated root cause, `visuals.py` still untouched). |
| IP-9040 | Wire `mood_update` into genre blending — **v2 re-scope**: inline, half-sized `VALENCE`-only recompute in `_emit_begin_blend` and `AROUSAL`-only recompute in `_emit_blend_tick` (`music_engine.py`), replacing v1's full `CALL('mood_update')` at both sites, closing the same gap `10-integration-review`'s R7 tranche review found (`IP-1130`'s blend write path never recomputed `AROUSAL`/`VALENCE`, violating `FR-1410`) at roughly half the per-site instruction cost. No new WRAM, no new routine. Folds in 4 already-`SCHEDULED` `VR-1130` doc corrections (`BL-0106`-`0109`) | `BL-0111` (Medium-High); folds in `BL-0106`/`BL-0107`/`BL-0108`/`BL-0109` (doc-only); v1/v2's regression tracked as `BL-0112` | **BLOCKED** 2026-08-17 (v3) — see the package doc's own v3 Blocking Report. v2's inline design was implemented exactly as specified and measured clean on every frame class except the mid-blend-restart collision frame (`FR-1490`), which regressed again (`T22.7` failed, `VIS_ENTRY_LY` read 0), the exact residual risk v2's own planning pass had named and flagged for re-verification. All code/test changes reverted, nothing partial committed. Needs a v4 re-scope — the deferred-recompute redesign fully worked out and grounded, or escalation of `FR-1410`'s "within one frame" wording to `04-requirements-engineering`/the user if that redesign proves impractical. Dependencies (`IP-1120`, `IP-1130`) both `VERIFIED`, unaffected. |

**Verb inventory.** *Generate* (the interpolation arithmetic itself) and *apply* (writing the
result to `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS`/`SCALE_IDX`) are both covered by this one package
— they are the same tight loop `FS-113`'s own no-split reasoning already established. *Persist*
does not apply (no SRAM). *Review* is explicitly deferred to `09-content-review` per `NFR-1230`
— named, not silently dropped: this package's own Acceptance Criteria are all WRAM-value
assertions, and the roadmap's own stated risk (an audibly "in-between-and-bad" blend) is not
something this package can or claims to resolve.

**Supersession sweep.** `FR-1240`'s original instant-apply guarantee is genuinely superseded for
3 of its 4 fields (§ above, `FS-113`'s own Requirements Implemented field). Swept the tree for
every call site that still assumes the old shape: `input_map.py:64-74` is the **only** call site
that invokes `_emit_apply_style`/steps `CHMIX_IDX` on a Start press — confirmed via `grep -n
_emit_apply_style *.py`, one match, the definition itself plus the one call site this package
already plans to change. No other `.py` file references `_emit_apply_style` or assumes
same-frame landing of `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` after a Start press. **In
`test_rom.py`**, the sweep is not clean and is not silent about it: `T15.1`-`T15.4` (the
per-preset immediate-landing checks and the cycle-to-default check) assert exactly the behavior
this package changes — both must be updated in this same package, per `BL-0099`/`FS-113`'s own
Verification Plan, not discovered later. `T15.5`/`T15.6` were checked and do **not** need
changes (`T15.5` only asserts bad-zone-flag non-interference; `T15.6` asserts Select's own direct
write, unaffected by this package).

**Right-sizing decision:** one package, matching `05-feature-decomposition`'s own no-split
reasoning for `FEAT-1130` (one trigger, one per-frame tick, four bytes, no independently
verifiable sub-piece) and `FS-113`'s own Module Responsibilities field, which already assigns
both new routines to `music_engine.py` and the one call-site change to `input_map.py`.

**G3 authorization for `IP-1130`: GRANTED 2026-08-07.** The user was asked directly via
`AskUserQuestion` once R8's full planning chain (`03`→`07`) was complete, and chose "Yes, build
it." Recorded as the basis rather than assumed — a fresh, specific grant for `IP-1130`, not a
reuse of any earlier grant in this session.

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
