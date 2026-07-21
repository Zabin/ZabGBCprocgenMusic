# Feature Catalog — v1 (Foundation release bucket)

- **Owned by:** `05-feature-decomposition` · **Status:** ✅ Authored, 2026-07-21
- **Release bucket:** "Foundation" — the first playable slice: engine + input + bad-zone + a
  minimal visualizer, all headlessly verified. Everything below is one release bucket; there is
  no epic/phase split yet at this project's size.

| ID | Feature | Summary | FR/NFR traced |
|---|---|---|---|
| FEAT-1000 | Core generation engine | Real-time per-channel note generation (scale-constrained walk for pulse A/B/wave, Euclidean-gated noise hits), preset tables, PSG register writes | FR-1000, FR-1010, NFR-1030 |
| FEAT-1010 | Input steering | Joypad edge detection + the 6-control parameter mapping (GDS-03 §3) | FR-1020...FR-1060 |
| FEAT-1020 | Reset-to-preset | Select-triggered full reinitialization | FR-1070 |
| FEAT-1030 | Bad-zone detection | Dissonance/stale/overload scoring + combined flag | FR-1080...FR-1110 |
| FEAT-1040 | Minimal visualizer | Tile/palette animation reacting to tempo + per-channel activity + bad-zone flag | FR-1120 |
| FEAT-1050 | Headless verification suite | PyBoy-driven button-sequence tests asserting on sound registers/WRAM state for every feature above | NFR-1010, NFR-1020 |

## Dependency graph

`FEAT-1000` is the foundation every other feature reads from or writes into; `FEAT-1010` writes
its parameter indices; `FEAT-1020` resets its state and `FEAT-1010`'s indices together;
`FEAT-1030` reads its per-channel note events; `FEAT-1040` reads its state read-only; `FEAT-1050`
exercises all of the above. Build order: `FEAT-1000` -> (`FEAT-1010`, `FEAT-1030` can proceed in
parallel once `FEAT-1000`'s note-event hook exists) -> `FEAT-1020` (needs both) -> `FEAT-1040` ->
`FEAT-1050` alongside every feature (tests are written per-package, not only at the end).

## Feature Review

No structural conflicts found; every FR/NFR from `docs/requirements/01-functional-requirements.md`
maps to exactly one feature above. No feature is undersized/oversized enough to need further
splitting for a first implementation pass.
