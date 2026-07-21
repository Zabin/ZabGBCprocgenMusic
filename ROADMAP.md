# ROADMAP — per-document status

Kept in sync with `docs/pipeline/pipeline-journal.md`'s Position block and each directory's own
`INDEX.md`. This is a flat summary for a quick glance; the indexes are authoritative on detail.

| Stage | Artifact(s) | Status |
|---|---|---|
| 00 Pipeline | Journal, backlog | ✅ Live (`docs/pipeline/`) |
| 01 Vision | MSTR-001 v1.0, GDS-00 | ✅ Authored 2026-07-21 |
| 02 Research | Per-topic encyclopedia (`docs/research/encyclopedia/`) covering 27 cited topics: R107-R115 (hardware), R201-R207/R209-R218 (procedural music/visualizer/engine design), R301/R305/R307-R309 (tooling) authored; remaining topics (R101-R106/R112/R208/R302-304/R306) explicitly `⛔ Planned` with named "no gap yet" reasoning — see `docs/research/INDEX.md` | ✅ Authored/restructured 2026-07-21 |
| 03 Architecture | GDS-00/01/03/07 authored; GDS-02/04/05/06/08/09/10 planned (`BL-0001`) | 🟡 Partial |
| 04 Requirements | FR-1000...FR-1120, NFR-1000...NFR-1030 | ✅ Authored 2026-07-21 |
| 05 Feature Decomposition | Feature Catalog v1 (FEAT-1000...FEAT-1050) | ✅ Authored 2026-07-21 |
| 06 Feature Specification | FS-100...FS-105 planned, none authored yet (`BL-0006`) | ⛔ Planned |
| 07 Implementation Planning | Master Build Plan, TWBS (IP-0001...IP-0006+) | ✅ Authored 2026-07-21 |
| 08 Implementation | IP-0001 `COMPLETE` (pulse A generation, full input mapping, scoped reset, headless harness bootstrap) | ✅ IP-0001 done; IP-0002+ not started |
| 09 Verification | IP-0001 self-tested (32/32); independent verification attempted run #2, blocked — user chose to wait for a fresh session (`BL-0004`) | 🔴 Blocked on a fresh session |
| 10 Integration Review | — | ⛔ Not reached |
| 11 Release Readiness | — | ⛔ Not reached |

See `docs/pipeline/backlog.md` for the live list of what each 🟡/🔴/⛔ actually needs next.
