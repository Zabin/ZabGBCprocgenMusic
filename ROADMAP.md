# ROADMAP — per-document status

Kept in sync with `docs/pipeline/pipeline-journal.md`'s Position block and each directory's own
`INDEX.md`. This is a flat summary for a quick glance; the indexes are authoritative on detail.

| Stage | Artifact(s) | Status |
|---|---|---|
| 00 Pipeline | Journal, backlog | ✅ Live (`docs/pipeline/`) |
| 01 Vision | MSTR-001 v1.3 (v1.1: autonomous bad-zone recovery, Select reframed as reset-and-randomize; v1.2: single-bank/no-save non-goals reopened as research questions, §9 future-direction topic list added; v1.3: C10 — every research topic must trace forward to shipped code or a named exception), GDS-00 (updated to match v1.3), strategic assumptions register (7 assumptions; A5 reopened, A7's trigger already fired) | ✅ Amended 2026-07-22, new research threads + forward-traceability audit owed |
| 02 Research | Per-topic encyclopedia (`docs/research/encyclopedia/`) — **all 39 topics across R100/R200/R300 now authored, every `⛔ Planned` row closed out** 2026-07-22: R101-R115 (hardware, incl. R101-R106/R112 closed this run), R201-R218 (design, incl. R208 closed this run), R301-R309 (tooling, incl. R302-R304/R306 closed this run) — see `docs/research/INDEX.md` | ✅ Fully authored 2026-07-22 |
| 03 Architecture | GDS-00/01/03/07 authored (GDS-01/03 amended for autonomous recovery, `IP-0007`; GDS-03/07 reconciled 2026-07-22 against shipped code, `BL-0013`/`BL-0018`); GDS-02/04/05/06/08/09/10 planned (`BL-0001`). New: `ADS-100` (combinable generation schemes, `BL-0020`) + `ADR-0001`. | 🟡 Partial |
| 04 Requirements | FR-1000...FR-1120, NFR-1000...NFR-1030 | ✅ Authored 2026-07-21 |
| 05 Feature Decomposition | Feature Catalog v1 (FEAT-1000...FEAT-1050) | ✅ Authored 2026-07-21 |
| 06 Feature Specification | FS-100...FS-105 planned, none formally authored — abbreviated per-package notes used instead for the MVP push (`BL-0006`/`BL-0012`) | ⛔ Planned (backfill scheduled) |
| 07 Implementation Planning | Master Build Plan, TWBS (IP-0001...IP-0007 + remediation tranche IP-9010/IP-9020 for `BL-0019`/`BL-0017`) | ✅ Authored 2026-07-21; 🟡 IP-9010/IP-9020 await G3 authorization |
| 08 Implementation | **MVP complete + extended** — IP-0001 `VERIFIED`; IP-0002-IP-0007 `COMPLETE` (4-channel generation, full input mapping, bad-zone detection with autonomous avoidance/recovery, Select reset-and-randomize, minimal visualizer). 60/60 tests, 8000+ frame stress run clean (bad-zone entry + self-recovery both observed). | ✅ All 7 Foundation-bucket packages COMPLETE |
| 09 Verification | All 7 packages independently `VERIFIED` ([VR-0001](docs/implementation/verification/VR-0001-skeleton-and-single-channel-generation.md)-[VR-0007](docs/implementation/verification/VR-0007-autonomous-recovery-and-randomize.md)), each in a genuinely fresh session (`IP-0001` under a one-time user-accepted same-session exception, `BL-0004`, `IP-0002`-`IP-0007` fully independent). | ✅ 7/7 independently verified |
| 10 Integration Review | [Foundation bucket review](docs/reviews/integration-review-foundation-bucket.md) — 2 findings (`BL-0019` High, `BL-0018` Low-Medium; `BL-0017` Medium-High carried forward from `VR-0007`). No Critical. | ⚠️ Reviewed — High finding open |
| 11 Release Readiness | Not reached — recommend against advancing until `BL-0019` (channel-mix non-functional) is remediated and re-verified | ⛔ Not reached |

See `docs/pipeline/backlog.md` for the live list of what each 🟡/🔴/⛔ actually needs next.
