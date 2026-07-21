# Integration Review — Foundation Release Bucket

- **Scope:** All 7 Foundation-bucket Implementation Packages — `IP-0001` through `IP-0007`
  (`FEAT-1000`, `FEAT-1010`, `FEAT-1020`, `FEAT-1030`, `FEAT-1040`, `FEAT-1050`)
- **Commit reviewed:** `2f085b6` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Pre-condition check:** every package in scope confirmed `VERIFIED` on the Master Build Plan
  before this review began (`IP-0001`→`VR-0001`, `IP-0002`→`VR-0002`, ..., `IP-0007`→`VR-0007`,
  all cross-checked against `docs/implementation/00-master-build-plan.md` immediately prior).
- **Result:** ⚠️ **2 findings** — 1 High, 1 Medium (carried forward from `VR-0007`/`BL-0017`); no
  Critical.

## Full-suite gate (run against the reviewed commit)

- `python3 build_rom.py <path>` → 32768 bytes, valid header (title `DRIFTUNE`, CGB flag `0x80`,
  cart type `0x00`)
- `python3 test_rom.py` → **60 PASS, 0 FAIL out of 60** (T1-T10)

## Dimension 1 — Interface consistency

Exercised: read `build_rom.py`'s full call sequence end to end. Boot order: sound-hardware init
(`NR50`/`NR51`/`NR52` + per-channel base registers, Wave RAM) → `init_engine` → `init_visuals`.
Per-frame order (after `HALT` wakes on the VBlank ISR): `read_joypad` → `apply_input` →
`engine_tick` → `update_visuals`. This is the correct seam order for `visuals.py`'s FR-1120
read-only-consumer contract (it reads state `engine_tick` just wrote, not stale prior-frame
state). `CHANNELS` (a shared Python-level list in `music_engine.py`) is the actual cross-routine
interface between `init_engine`, `engine_tick`, and each channel's `_emit_channel_gen` call — read
in full, every entry (`pa`/`pb`/`wv`) carries a consistent 9-tuple shape consumed identically by
both routines. No patch-point dict is actually used (`build_engine_asm`'s returned `patches` dict
is empty/unused, per its own docstring — a parity stub, not a live interface) — no drift risk
there since nothing reads it. **Clean.**

## Dimension 2 — Invariant sweep

- **ROM budget:** exactly 32768 bytes every build (confirmed above); no manual `rom.seek()` calls
  outside the fixed low-memory vector table (`0x0000`-`0x0040`) and the two fixed entry points
  (`0x0100`, `0x0150`) — all other emission is strictly sequential, so section overlap is
  structurally impossible, not merely untested.
- **VBlank-gated visualizer writes:** the main loop `HALT`s until the VBlank ISR sets
  `VBLANK_FLAG`, then runs `engine_tick`/`update_visuals` synchronously in the same wake — so
  every VRAM/tilemap/palette write `update_visuals` makes happens at the start of the VBlank
  window, not mid-scanout. Correct GBC-safe pattern. **Clean.**
- **WRAM map completeness (GDS-07 vs. shipped code) — FINDING.** Grepped every `0xC0xx`-defined
  constant in `music_engine.py` against `docs/architecture/07-data-model.md`'s §1-§8 tables.
  `LFSR_STATE_PB` (`0xC017`), `LFSR_STATE_WV` (`0xC018`), `NOISE_STEP_IDX` (`0xC019`), `SEMI_PA`
  (`0xC01A`), `SEMI_PB` (`0xC01B`), `SEMI_WV` (`0xC01C`) — six addresses live in the shipped
  ROM, added incrementally by `IP-0002`/`IP-0003`/`IP-0004` — appear **nowhere** in GDS-07. This
  is distinct from the already-tracked `BL-0013` (which is about the *unused* `HIST_HEAD_*`/
  `HIST_*` fields GDS-07 *does* document but the code doesn't use) — this is the opposite
  direction: addresses the code *does* use that GDS-07 never documents at all. No functional
  defect (the addresses don't collide with anything — `0xC013`-`0xC015` and `0xC020`-`0xC037`,
  GDS-07's own reserved-but-unused ring-buffer range, are correctly avoided) — filed as `BL-0018`.
  See Findings.
- **No module took on a second job:** `music_engine.py` carries generation + bad-zone detection +
  autonomous recovery, all under one cohesive "the engine" responsibility per GDS-03's own design
  (not a violation); `visuals.py` stayed strictly read-only across all three packages that could
  have touched it. **Clean.**

## Dimension 3 — Behavioral coherence

Exercised: traced every `CHMIX_IDX` reference across the entire tree — `music_engine.py`
(definition, `PRESET_CHMIX_IDX` reset-write only), `input_map.py` (Start-button step only). **No
code anywhere reads `CHMIX_IDX` to gate, mute, or otherwise condition any channel's generation or
register writes** — confirmed by grep across `music_engine.py`, `build_rom.py`, `visuals.py`; no
`CHMIX`/channel-mix preset *table* (analogous to `TEMPO_TABLE`/`DENSITY_K`) exists anywhere
either. This is a genuine, cross-package dead-end:

- `IP-0001`'s own package doc explicitly scoped this as a promise: *"`DENSITY_IDX`/`CHMIX_IDX` are
  wired and tested for their own index behavior but have no consumer until `IP-0002`/`0003`."*
- `IP-0003`'s package doc confirms the `DENSITY_IDX` half of that promise was kept ("`DENSITY_IDX`
  now has a real consumer"). **The `CHMIX_IDX` half was never kept by any of `IP-0002`-`IP-0007`**
  — no package doc mentions wiring it, and none of the seven independent `VR-000x` verifications
  caught the gap, because each one audited its own package's scope only; this is exactly the class
  of finding single-package verification cannot see and integration review exists to catch.
- `FR-1000`/`FR-1010` (both traced by `FEAT-1000`, which the Master Build Plan and Feature Catalog
  both currently show as fully delivered via `IP-0001`-`IP-0003`) explicitly describe channels
  activating "its channel-mix preset includes/activates" — text that presumes a functioning gate
  that does not exist in the shipped ROM. All four channels always play regardless of `CHMIX_IDX`.
- `Claude.md`/`memory.md` **do** already informally flag this ("channel-mix wired but not yet
  consumed," "Next channel-mix preset (wired, not yet consumed)") — so it was never silently
  hidden — but it was never formally routed through the pipeline: zero backlog entries reference
  `CHMIX`/channel-mix, despite `Claude.md`'s own "Known Issues" section claiming
  `docs/pipeline/backlog.md` is the live, non-stale list of open items.

This is the review's headline finding, filed as `BL-0019` (High). See Findings.

## Dimension 4 — Traceability coherence

- Master Build Plan, `packages/INDEX.md`, and `verification/INDEX.md` all agree: all 7 packages
  `VERIFIED`, cross-references bidirectional (every `IP-xxxx` row links its `VR-xxxx`, every
  `VR-xxxx` names its `IP-xxxx`) and consistent with the actual files on disk (confirmed by
  listing `docs/implementation/verification/` and `docs/implementation/packages/`).
- **`ROADMAP.md` is stale** — its stage-09 row still says "1/7 independently verified" and its
  stage-10 row says "Not reached," both true as of run #6 but not since run #12. Not filed as a
  new backlog entry (routine drift this stage is explicitly instructed to correct, not report) —
  updated directly as part of this review's own output (see below), consistent with this skill's
  named "Update `ROADMAP.md`'s reviews row" responsibility.
- Feature Catalog's `FEAT-1000` row traces to `FR-1000`/`FR-1010`/`NFR-1030` and is implicitly
  treated as fully delivered by the Master Build Plan — but per Dimension 3's finding, `FR-1000`/
  `FR-1010`'s channel-mix clause is not actually satisfied. This is the traceability-layer
  reflection of the same `BL-0019` finding, not a separate one.

## Dimension 5 — Documentation coherence

- `Claude.md`'s architecture/data-layout/input-mapping/Known Good Behavior sections all read as
  accurate against the shipped tree (spot-checked every WRAM range, every input mapping, every
  "Known Good Behavior" bullet against the actual code) — including its two honest
  channel-mix-not-consumed notes, now properly backed by a filed backlog entry (`BL-0019`) instead
  of being the only place that fact was recorded.
- `memory.md`'s WRAM quick-reference table is more current than GDS-07 itself in one respect (it
  already lists `LFSR_STATE_PB`/`WV`, `SEMI_PA`/`PB`/`WV` — the exact fields `BL-0018` found
  missing from GDS-07) — meaning the gap is specifically in the formal architecture doc, not in
  the project's own working memory. No inconsistency between `Claude.md`/`memory.md` themselves.

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| `BL-0019` | `IP-0001` (scoped the promise), `IP-0002`-`IP-0007` (never fulfilled it), `FR-1000`/`FR-1010`, `FEAT-1000` | `CHMIX_IDX` ("channel-mix," the Start-button-controlled parameter) is stepped and reset correctly but has **no consumer anywhere in the shipped code** — no channel is ever gated, muted, or otherwise conditioned on its value, and no channel-mix preset table exists. All four channels always play regardless. `FR-1000`/`FR-1010`'s text presumes this gate functions; it does not. Already informally noted in `Claude.md`/`memory.md` but never formally tracked. | **High** | `07-implementation-planning` — author a remediation package (wire `CHMIX_IDX` to a real channel-activity-mask table and gate each channel's register writes/generation on it, per `GDS-03`'s original design intent), then `08-code-implementation` → `09-package-verification` |
| `BL-0018` | `IP-0002` (`LFSR_STATE_PB`/`WV`), `IP-0003` (`NOISE_STEP_IDX`), `IP-0004` (`SEMI_PA`/`PB`/`WV`), `GDS-07` | Six WRAM addresses (`0xC017`-`0xC019`, `0xC01A`-`0xC01C`) are live in the shipped ROM but undocumented in `docs/architecture/07-data-model.md` — added incrementally across three packages, none of which updated GDS-07. No collision, no functional defect — `memory.md`'s own WRAM quick-reference already has these fields, so the gap is specific to the formal architecture document. | Low-Medium (doc-coherence only, no functional impact) | `03-architecture-design-synthesis` — append a §9 (or extend §8) to GDS-07 documenting these six addresses, alongside its already-scheduled `BL-0013` reconciliation pass |
| (carried forward, not re-filed) | `IP-0007`, `IP-0004`, `FR-1100` | `BL-0017` (`OVERLOAD_THRESHOLD` mathematically unreachable) was filed by `VR-0007` immediately prior to this review and is the natural companion to this review's own findings — re-surfaced here for visibility, not duplicated as a new ID. | Medium-High (see `BL-0017`) | Unchanged — `07-implementation-planning`/`08-code-implementation`, per `BL-0017`'s own disposition |

## Verdict

The seven-package Foundation tranche integrates cleanly at the mechanical level — no interface
mismatches, no ROM-budget or VRAM-timing violations, no duplicated behavior, and documentation
tracks the shipped tree accurately everywhere except one architecture doc gap (`BL-0018`, Low-
Medium). It does **not** integrate cleanly at the behavioral level: a fully-specified,
requirements-traced, player-facing control (channel mix, `FR-1000`/`FR-1010`/`FEAT-1000`) is
completely non-functional, dropped silently across five packages' worth of development and
undetected by seven independent package verifications because none of them had this review's
whole-tranche vantage point. **High-severity finding (`BL-0019`) — recommend against advancing to
`11-release-readiness` until it is remediated and re-verified**, alongside `BL-0017` (already
Medium-High, already scheduled).
