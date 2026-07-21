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
| GDS-00 | Vision | [00-vision.md](00-vision.md) | ✅ Authored 2026-07-21 |
| GDS-01 | Concept of Interaction | [01-concept-of-play.md](01-concept-of-play.md) | ✅ Authored 2026-07-21 |
| GDS-02 | System Context | 02-system-context.md | ⛔ Planned |
| GDS-03 | Architecture (module layout, main loop, input->parameter mapping, bad-zone metric) | [03-architecture.md](03-architecture.md) | ✅ Authored 2026-07-21 (SS1-5; SS6 lists what's still open) |
| GDS-04 | Domain Model | 04-domain-model.md | ⛔ Planned |
| GDS-05 | Functional Requirements | 05-functional-requirements.md | ⛔ Planned (superseded in ordering by a direct `04-requirements-engineering` FR/NFR pass, see `docs/requirements/`) |
| GDS-06 | Non-functional Requirements | 06-non-functional-requirements.md | ⛔ Planned |
| GDS-07 | Data Model (WRAM map) | [07-data-model.md](07-data-model.md) | ✅ Authored 2026-07-21 |
| GDS-08 | Presentation Architecture (visualizer) | 08-presentation-architecture.md | ⛔ Planned |
| GDS-09 | Interface Specification | 09-interface-specification.md | ⛔ Planned |
| GDS-10 | Requirements Traceability Matrix level | 10-requirements-traceability-matrix.md | ⛔ Planned |

## §2 — Per-cluster design syntheses (ADS-xxx)

None yet — no capability cluster has surfaced tension beyond what GDS-03 already resolved.

## §3 — Vision-layer artifacts owned by `01-vision`

| Artifact | File | Status |
|---|---|---|
| Strategic assumptions register | strategic-assumptions-register.md | ⛔ Planned |

## §4 — Architecture Decision Records

See `adr/INDEX.md`. None recorded yet for this from-scratch increment.
