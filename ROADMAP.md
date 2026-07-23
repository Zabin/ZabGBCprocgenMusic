# ROADMAP — per-document status

Kept in sync with `docs/pipeline/pipeline-journal.md`'s Position block and each directory's own
`INDEX.md`. This is a flat summary for a quick glance; the indexes are authoritative on detail.

| Stage | Artifact(s) | Status |
|---|---|---|
| 00 Pipeline | Journal, backlog | ✅ Live (`docs/pipeline/`) |
| 01 Vision | MSTR-001 v1.4 (v1.1: autonomous bad-zone recovery; v1.2: single-bank/no-save reopened, §9 added; v1.3: C10 research-to-code traceability; v1.4: §9's three research threads cycled in — genre feasibility tiered, style-evolution/song-form + emotional/energy promoted to groundable architecture candidates, cart-shape facts recorded not decided), GDS-00 (updated to match v1.4), strategic assumptions register (7 assumptions; A5 research landed, adoption decision still open; A7's trigger already fired) | ✅ Amended 2026-07-22; visual-evolution thread + forward-traceability audit + cart-shape adoption decision remain owed |
| 02 Research | Per-topic encyclopedia (`docs/research/encyclopedia/`) — 42 topics: R101-R115 (hardware, **R106 substantially extended 2026-07-22** — MBC1/3/5 + PyBoy save-mechanics facts), R201-R221 (design, **R219-R221 added 2026-07-22**), R301-R309 (tooling, **R302 §8-9 addendum added 2026-07-22** — bank-switching's cost to `gbc_lib.py`/`build_rom.py`/`test_rom.py`) — see `docs/research/INDEX.md` | ✅ **All three MSTR-001 §9 research threads now closed** (musical identity/style-evolution/emotional-energy, MBC/save hardware facts, multi-bank tooling cost) — ready for `03-architecture-design-synthesis`/`04-requirements-engineering` if picked up; no decisions made, facts only |
| 03 Architecture | GDS-00/01/03/07 authored (GDS-01/03 amended for autonomous recovery, `IP-0007`; GDS-03/07 reconciled 2026-07-22 against shipped code, `BL-0013`/`BL-0018`); GDS-02/04/05/06/08/09/10 planned (`BL-0001`). New: `ADS-100` (combinable generation schemes, `BL-0020`) + `ADR-0001`. | 🟡 Partial |
| 04 Requirements | FR-1000...FR-1120, NFR-1000...NFR-1030 | ✅ Authored 2026-07-21 |
| 05 Feature Decomposition | Feature Catalog v1 (FEAT-1000...FEAT-1050) | ✅ Authored 2026-07-21 |
| 06 Feature Specification | FS-100...FS-105 planned, none formally authored — abbreviated per-package notes used instead for the MVP push (`BL-0006`/`BL-0012`) | ⛔ Planned (backfill scheduled) |
| 07 Implementation Planning | Master Build Plan, TWBS (IP-0001...IP-0007 + remediation tranche IP-9010/IP-9020 for `BL-0019`/`BL-0017`) | ✅ Authored 2026-07-21; 🟡 IP-9010/IP-9020 await G3 authorization |
| 08 Implementation | **MVP complete + extended** — IP-0001 `VERIFIED`; IP-0002-IP-0007 `COMPLETE` (4-channel generation, full input mapping, bad-zone detection with autonomous avoidance/recovery, Select reset-and-randomize, minimal visualizer). 60/60 tests, 8000+ frame stress run clean (bad-zone entry + self-recovery both observed). | ✅ All 7 Foundation-bucket packages COMPLETE |
| 09 Verification | All 7 packages independently `VERIFIED` ([VR-0001](docs/implementation/verification/VR-0001-skeleton-and-single-channel-generation.md)-[VR-0007](docs/implementation/verification/VR-0007-autonomous-recovery-and-randomize.md)), each in a genuinely fresh session (`IP-0001` under a one-time user-accepted same-session exception, `BL-0004`, `IP-0002`-`IP-0007` fully independent). | ✅ 7/7 independently verified |
| 10 Integration Review | [Foundation bucket review](docs/reviews/integration-review-foundation-bucket.md) — 2 findings (`BL-0019` High, `BL-0018` Low-Medium; `BL-0017` Medium-High carried forward from `VR-0007`). No Critical. | ⚠️ Reviewed — High finding open |
| 11 Release Readiness | Not reached — recommend against advancing until `BL-0019` (channel-mix non-functional) is remediated and re-verified | ⛔ Not reached |
| **Product Roadmap** | [`docs/roadmap/`](docs/roadmap/INDEX.md) — full planning package (product goals, capability map/dependency graph, 14-release sequence R0-R13+R4.5, milestones A-F, traceability matrix, dev strategy, exit criteria, self-review) synthesized 2026-07-22 from the existing Vision + 42-topic Research Encyclopedia, no new research | ✅ Authored 2026-07-22 — planning input for `03`/`04`/`05`/`06` as each release is picked up, not itself an implementation authorization |

See `docs/pipeline/backlog.md` for the live list of what each 🟡/🔴/⛔ actually needs next.
