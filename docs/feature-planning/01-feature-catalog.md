# Feature Catalog — v1 (Foundation release bucket)

- **Owned by:** `05-feature-decomposition` · **Status:** ✅ Authored, 2026-07-21
- **Release bucket:** "Foundation" — the first playable slice: engine + input + bad-zone + a
  minimal visualizer, all headlessly verified. Everything below is one release bucket; there is
  no epic/phase split yet at this project's size.
- **Release status: ✅ SHIPPED — GO confirmed 2026-07-25.** Every feature below (`FEAT-1000`
  through `FEAT-1060`) is `VERIFIED` and integration-reviewed as part of the consolidated
  R1 (Foundation) + R2 (Sound Design) + R3 (Integrity Remediation) release — see
  [`docs/reviews/release-assessment-r1-r2-r3.md`](../reviews/release-assessment-r1-r2-r3.md).

| ID | Feature | Summary | FR/NFR traced |
|---|---|---|---|
| FEAT-1000 | Core generation engine | Real-time per-channel note generation (scale-constrained walk for pulse A/B/wave, Euclidean-gated noise hits), preset tables, PSG register writes | FR-1000, FR-1010, NFR-1030 |
| FEAT-1010 | Input steering | Joypad edge detection + the 6-control parameter mapping (GDS-03 §3) | FR-1020...FR-1060 |
| FEAT-1020 | Reset-to-preset | Select-triggered full reinitialization | FR-1070 |
| FEAT-1030 | Bad-zone detection | Dissonance/stale/overload scoring + combined flag | FR-1080...FR-1110 |
| FEAT-1040 | Minimal visualizer | Tile/palette animation reacting to tempo + per-channel activity + bad-zone flag | FR-1120 |
| FEAT-1050 | Headless verification suite | PyBoy-driven button-sequence tests asserting on sound registers/WRAM state for every feature above | NFR-1010, NFR-1020 |
| FEAT-1060 | Sound design techniques | Arpeggio (chord-implying frequency cycling), vibrato (periodic pitch modulation), portamento (multi-frame pitch glide), duty-cycle variation — layered onto `FEAT-1000`'s existing per-channel generation, no new input control | FR-1130...FR-1170, NFR-1040, NFR-1050 |
| FEAT-1070 | Combinable generation schemes | A second per-channel note-selection strategy (Scheme E — Euclidean-gated onset timing + fixed-motif pitch selection) alongside the shipped Scheme W (LFSR walk), selectable per pitched channel via spare bits in the existing `CHMIX_IDX`/`CHMIX_MASKS` preset space — no new input control. `BL-0020`'s "solo or in combination" ask is satisfied at the ensemble level (different channels running different schemes), not by blending within one channel. First feature of `docs/roadmap/04-release-roadmap.md`'s **R4 — Multi-Scheme Foundation** | FR-1180...FR-1220, NFR-1060, NFR-1070 |

## Dependency graph (Foundation bucket, `FEAT-1000`...`FEAT-1050`)

`FEAT-1000` is the foundation every other feature reads from or writes into; `FEAT-1010` writes
its parameter indices; `FEAT-1020` resets its state and `FEAT-1010`'s indices together;
`FEAT-1030` reads its per-channel note events; `FEAT-1040` reads its state read-only; `FEAT-1050`
exercises all of the above. Build order: `FEAT-1000` -> (`FEAT-1010`, `FEAT-1030` can proceed in
parallel once `FEAT-1000`'s note-event hook exists) -> `FEAT-1020` (needs both) -> `FEAT-1040` ->
`FEAT-1050` alongside every feature (tests are written per-package, not only at the end).

`FEAT-1060` (added 2026-07-22, `BL-0024`) depends on `FEAT-1000` (extends `_emit_channel_gen`,
the existing per-channel generation routine) and must not regress `FEAT-1030` (bad-zone scoring
continues to read scale-degree state, not instantaneous modulated frequency — FR-1140 makes this
explicit) or `FEAT-1050` (every new behavior needs its own headless test coverage, same
convention as every prior feature).

`FEAT-1070` (added 2026-07-25, `BL-0020`/`ADS-100`) depends on `FEAT-1000` (extends
`_emit_channel_gen`'s note-selection step, same seam `FEAT-1060` already touches) and, critically,
on the shipped `IP-9010` (`CHMIX_MASKS`, delivered as part of `FEAT-1030`'s remediation tranche —
`BL-0019`), since it rides that table's spare bits per `ADR-0001`. Must not regress `FEAT-1030`
(`FR-1220` makes bad-zone scheme-agnosticism explicit) or `FEAT-1050` (new headless coverage
required, same convention). No dependency on `FEAT-1060` — the two features touch adjacent code
(the same `_emit_channel_gen`/`CHANNELS` seam) but are functionally independent; sequencing them
in either order is safe, per `07-implementation-planning`'s own eventual call.

## Feature Review

No structural conflicts found; every FR/NFR from `docs/requirements/01-functional-requirements.md`
maps to exactly one feature above. No feature is undersized/oversized enough to need further
splitting for a first implementation pass.

**2026-07-22 update:** `FEAT-1060` reviewed against the existing catalog — no conflict with
`FEAT-1000`/`FEAT-1030`/`FEAT-1040`'s existing FR coverage; right-sized for one-or-two
implementation packages (per `07-implementation-planning`'s own sizing call), not requiring
further splitting at this stage.

**2026-07-25 update:** `FEAT-1070` reviewed against the existing catalog — no conflict, no
requirement double-assigned (`FR-1180`-`FR-1220`/`NFR-1060`/`1070` traced to exactly this one
feature, confirmed against `docs/requirements/01-functional-requirements.md`'s full FR/NFR
inventory). Right-sized for a single implementation package (Scheme E's onset-timing and
pitch-selection halves are tightly coupled — both live in the same note-selection branch of
`_emit_channel_gen` — splitting them the way `FEAT-1060` split into `IP-1060`/`IP-1061` would be
artificial here, since neither half is independently useful or independently testable without the
other; a sizing call `07-implementation-planning` should confirm, not override, when it plans
this). No architectural inconsistency: the design (`ADS-100`) was already synthesized against the
shipped module boundaries (GDS-03), not invented at this stage.
