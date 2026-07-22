# Architecture & Design Synthesis — Index

Owned by `03-architecture-design-synthesis` (GDS-01...10, ADS, ADRs) and `01-vision` (GDS-00 +
strategic assumptions register). See `.claude/skills/README.md` for the pipeline.

This is a from-scratch increment (no shipped ROM), so the ladder is authored level by level as
the pipeline actually reaches it, not mined from existing code the way the reference project's
bootstrap was.

[↑ Docs index](../INDEX.md)

## §1 — The global ladder (GDS-00...GDS-10)

| Level | Title | File | Status |
|---|---|---|---|
| GDS-00 | Vision | [00-vision.md](00-vision.md) | ✅ Authored 2026-07-21; amended 2026-07-22 (v1.1 drift fix); amended 2026-07-22 (v1.2 — cart-shape/save reopened, not decided); amended 2026-07-22 (v1.3 — research-to-code traceability goal, C10); amended 2026-07-22 (v1.4 — §9 research findings cycled in) |
| GDS-01 | Concept of Interaction | [01-concept-of-play.md](01-concept-of-play.md) | ✅ Authored 2026-07-21 |
| GDS-02 | System Context | 02-system-context.md | ⛔ Planned |
| GDS-03 | Architecture (module layout, main loop, input->parameter mapping, bad-zone metric) | [03-architecture.md](03-architecture.md) | ✅ Authored 2026-07-21 (SS1-5; SS6 lists what's still open); reconciled 2026-07-22 against shipped `IP-0004`/`IP-0007` (`BL-0013`, `BL-0017` root-cause note) |
| GDS-04 | Domain Model | 04-domain-model.md | ⛔ Planned |
| GDS-05 | Functional Requirements | 05-functional-requirements.md | ⛔ Planned (superseded in ordering by a direct `04-requirements-engineering` FR/NFR pass, see `docs/requirements/`) |
| GDS-06 | Non-functional Requirements | 06-non-functional-requirements.md | ⛔ Planned |
| GDS-07 | Data Model (WRAM map) | [07-data-model.md](07-data-model.md) | ✅ Authored 2026-07-21; extended 2026-07-22 with 6 previously-undocumented WRAM addresses (`BL-0018`) and reconciled re: the unused ring buffer (`BL-0013`) and the `DIV`-reseed drift fix |
| GDS-08 | Presentation Architecture (visualizer) | 08-presentation-architecture.md | ⛔ Planned |
| GDS-09 | Interface Specification | 09-interface-specification.md | ⛔ Planned |
| GDS-10 | Requirements Traceability Matrix level | 10-requirements-traceability-matrix.md | ⛔ Planned |

## §2 — Per-cluster design syntheses (ADS-xxx)

| ADS | Title | File | Status |
|---|---|---|---|
| ADS-100 | Combinable Generation Schemes | [ADS-100-combinable-generation-schemes.md](ADS-100-combinable-generation-schemes.md) | ✅ Authored 2026-07-22 — routes `BL-0020`; real design tension (control-surface scarcity, ROM budget) warranted a dedicated ADS rather than folding into the GDS ladder directly |

## §3 — Vision-layer artifacts owned by `01-vision`

| Artifact | File | Status |
|---|---|---|
| Strategic assumptions register | [strategic-assumptions-register.md](strategic-assumptions-register.md) | ✅ Authored 2026-07-22 (7 assumptions; A7's trigger already fired — see `BL-0023`) |

## §4 — Architecture Decision Records

See `adr/INDEX.md`. 1 recorded: `ADR-0001` (scheme selection rides the `CHMIX_IDX` preset space).
