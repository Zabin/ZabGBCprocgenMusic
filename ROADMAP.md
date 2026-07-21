# ROADMAP — per-document status

Kept in sync with `docs/pipeline/pipeline-journal.md`'s Position block and each directory's own
`INDEX.md`. This is a flat summary for a quick glance; the indexes are authoritative on detail.

| Stage | Artifact(s) | Status |
|---|---|---|
| 00 Pipeline | Journal, backlog | ✅ Live (`docs/pipeline/`) |
| 01 Vision | MSTR-001 v1.1 (amended: autonomous bad-zone recovery, Select reframed as reset-and-randomize), GDS-00 | ✅ Authored 2026-07-21 |
| 02 Research | Per-topic encyclopedia (`docs/research/encyclopedia/`) covering 27 cited topics: R107-R115 (hardware), R201-R207/R209-R218 (procedural music/visualizer/engine design), R301/R305/R307-R309 (tooling) authored; remaining topics (R101-R106/R112/R208/R302-304/R306) explicitly `⛔ Planned` with named "no gap yet" reasoning — see `docs/research/INDEX.md` | ✅ Authored/restructured 2026-07-21 |
| 03 Architecture | GDS-00/01/03/07 authored (GDS-01/03 amended for autonomous recovery, `IP-0007`); GDS-02/04/05/06/08/09/10 planned (`BL-0001`) | 🟡 Partial |
| 04 Requirements | FR-1000...FR-1120, NFR-1000...NFR-1030 | ✅ Authored 2026-07-21 |
| 05 Feature Decomposition | Feature Catalog v1 (FEAT-1000...FEAT-1050) | ✅ Authored 2026-07-21 |
| 06 Feature Specification | FS-100...FS-105 planned, none formally authored — abbreviated per-package notes used instead for the MVP push (`BL-0006`/`BL-0012`) | ⛔ Planned (backfill scheduled) |
| 07 Implementation Planning | Master Build Plan, TWBS (IP-0001...IP-0007) | ✅ Authored 2026-07-21 |
| 08 Implementation | **MVP complete + extended** — IP-0001 `VERIFIED`; IP-0002-IP-0007 `COMPLETE` (4-channel generation, full input mapping, bad-zone detection with autonomous avoidance/recovery, Select reset-and-randomize, minimal visualizer). 60/60 tests, 8000+ frame stress run clean (bad-zone entry + self-recovery both observed). | ✅ All 7 Foundation-bucket packages COMPLETE |
| 09 Verification | IP-0001 `VERIFIED` ([VR-0001](docs/implementation/verification/VR-0001-skeleton-and-single-channel-generation.md)). IP-0002-0007 self-tested, same-session per user-authorized exception (`BL-0012`) — independent verification still owed for each. | 🟡 1/7 independently verified |
| 10 Integration Review | Not reached — needs all 7 packages independently `VERIFIED` first | ⛔ Not reached |
| 11 Release Readiness | — | ⛔ Not reached |

See `docs/pipeline/backlog.md` for the live list of what each 🟡/🔴/⛔ actually needs next.
