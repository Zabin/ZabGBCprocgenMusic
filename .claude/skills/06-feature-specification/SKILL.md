---
name: 06-feature-specification
description: Transform an approved Feature (a FEAT-xxxx Feature Catalog entry) into a detailed technical design specification under docs/features/ — one FS-xxx-name.md per Feature using the fixed 20-field template, ready to hand to 07-implementation-planning. Use when asked to "write the feature spec for FEAT-xxxx/FS-xxx," "turn this approved feature into a design spec," "detail the behavior/interfaces/data impact for a feature," or as the stage-06 step of the project's first, from-scratch increment (forward-design specs for the initial feature set — there is no shipped ROM to describe as-built). This skill performs no new requirements, no architecture redesign, no code, and does not modify the approved Feature it specifies — it is a pure elaboration step. Do not use it to decompose requirements into features (05-feature-decomposition) or to make architecture decisions (03-architecture-design-synthesis).
---

# Feature Specification

Turns an **approved Feature** into a **detailed technical design specification**. Strictly
downstream of 04/05; strictly upstream of 07/08.

## What this is for (and what it is not)

One question: *given one approved Feature and everything decided upstream, what exactly must the
music engine and visualizer do — the listener/player workflows, behavior, module responsibilities,
interfaces, data, state, errors, and acceptance criteria — stated precisely enough that an
Implementation Package can be written without re-deciding anything design-level?*

It SHALL NOT: write code (no opcode listings, no byte layouts beyond what GDS-07 already commits
to) · redesign architecture (a Feature that doesn't fit is a finding for the architecture owner)
· create requirements (a gap is an Open Question, never an invented FR) · modify the Feature
Catalog entry it elaborates (mis-scoping is a finding for `05-feature-decomposition`).

Authoritative inputs (read-only): the Feature Catalog + Epic Catalog
(`docs/feature-planning/`) · the requirements baseline (`docs/requirements/`) · the GDS ladder +
ADRs (`docs/architecture/`) · GDS-09's module interface contracts. **If inputs conflict, or the
Feature's scope can't be satisfied within the existing architecture, record it in Open Questions
— never resolve unilaterally.**

## Outputs

One file per Feature: `docs/features/FS-xxx-<slug>.md` — number `FS-101` upward (a readable
3-digit series distinct from the catalog's `FEAT-xxxx` planning rows; record the FEAT↔FS mapping
in both documents' metadata). Update `docs/features/INDEX.md` (one row per spec: ID, title,
status, owning Epic, FEAT source, one-line summary) in the same pass.

## Workflow

### Step 0 — Confirm approval, build the reading inventory

Confirm the target Feature has an approved catalog entry (approval comes from
`05-feature-decomposition`'s Feature Review, not from any prior shipped behavior — this project
has no as-built baseline bucket). Read the entry plus
every requirement, module, and ADR it cites. Inventory: Included Requirements (every one must
appear in the spec) · Dependencies/Dependent Features · Affected Modules · bound ADRs · anything
the entry implies but doesn't state (candidate Open Questions).

### Step 1 — Draft the spec, field by field, in order

The fixed 20-field template (an explicit "None" is informative; a missing field is not):

| Field | Content |
|---|---|
| **Feature ID** | `FS-xxx`, plus the `FEAT-xxxx` catalog source |
| **Title** | matching the catalog entry |
| **Purpose** | from the entry's Purpose/User Value — not reinvented |
| **Scope** | positive boundary, consistent with the entry's Scope/Excluded Requirements |
| **Requirements Implemented** | every owned FR/NFR ID — none added, none dropped |
| **User Workflows** | step-by-step listener/player (or build-pipeline) sequences, end to end |
| **System Behaviour** | the observable contract per workflow step, normal path + edge cases the requirements imply |
| **Module Responsibilities** | which existing module (per GDS-03) owns which piece — never a new module invented here |
| **Interfaces Used** | existing GDS-09 contracts consumed/extended (patch-point dict keys, `ALL_PATTERNS`, `build_tile_data()`, …) — a needed-but-missing interface is an Open Question |
| **Data Model Changes** | ROM/WRAM/SRAM entities read or written, against GDS-07 — additions only where requirements demand, flagged if the existing model doesn't support the behavior |
| **State Changes** | engine-state/persistent state created, transitioned, retired, and the triggers |
| **Error Handling** | failure modes and the player/system-visible contract (e.g. invalid save magic → fresh boot, or a corrupted bad-zone detector → forced reset to good state) |
| **Performance Considerations** | NFR-driven constraints (VBlank budget, ROM budget), cited to NFR IDs |
| **Integrity Considerations** | save-data / checksum / determinism constraints, cited to their source |
| **Acceptance Criteria** | checkable by a reviewer cold |
| **Verification Plan** | Test/Demonstration/Analysis/Inspection per criterion, consistent with the requirements' own Verification Methods; name the `test_rom.py` suite(s) it lands in |
| **Dependencies** | other FS-xxx/modules required first, per the entry |
| **Risks** | ambiguity/dependency/architecture-fit risk |
| **Open Questions** | every genuine ambiguity, with why it matters and which upstream artifact resolves it |
| **Related ADRs** | binding decisions this design must stay consistent with |

**Writing discipline:** trace, don't assert (every non-trivial statement ties to a cited
requirement/GDS section/ADR/interface) · behavior, not implementation — unless GDS-07/GDS-09/an
ADR already commits to the detail · unknowns become Open Questions, every time · no scope creep
past the Feature's own boundary (name the neighboring Feature and move on).

### Step 2 — Self-check against the Quality gate

A spec failing any item is not done — fix the field. Open Questions are for genuine upstream
ambiguity, not unfinished fields.

### Step 3 — Update the index

Add/update the spec's row in `docs/features/INDEX.md` and the FEAT entry's forward-reference
metadata (metadata only — never the entry's content).

## Quality gate

- [ ] The Feature was confirmed approved before drafting.
- [ ] Every template field populated; every Included Requirement appears in Requirements
      Implemented — none added, none dropped.
- [ ] Every workflow has a behavior contract covering normal path + ≥1 edge case.
- [ ] Every module named exists in GDS-03; every interface cited exists in GDS-09 (or is an Open
      Question).
- [ ] No concrete byte layout/algorithm not already committed to by GDS-07/GDS-09/an ADR.
- [ ] Every Open Question states why it matters and what upstream artifact resolves it.
- [ ] The catalog entry was not edited; no FR/NFR was created.

## Gotchas

- Don't re-derive what the FEAT entry already decided (Purpose, Scope, Dependencies, Modules,
  ADRs) — carry them forward verbatim; divergence is a defect.
- Don't promote an Open Question to a settled answer because the spec "needs" one — honest Open
  Questions beat confident invented answers.
- Once a Feature has shipped code and passing tests, later specs for that Feature's evolution can
  cite `test_rom.py` check IDs in Acceptance Criteria as existing evidence — but on this project's
  first pass, before anything ships, Acceptance Criteria describe what will be checked, not what
  already is.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 06 — Feature Specification** of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream: `05-feature-decomposition`.
Downstream: `07-implementation-planning`.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the spec(s) produced or updated (paths), and the index entry added/updated.
2. **Recommendations** — every Open Question with its owning upstream skill (`03` for
   architecture/interface gaps, `04` for requirement gaps, `02-research-*` for domain gaps), plus
   any mis-scoping finding for `05`'s catalog owner.
3. **Next step** — if Open Questions block implementation-readiness, route them upstream first
   and re-invoke this skill to close them; otherwise advance to `07-implementation-planning` to
   convert this spec into package(s) — or, if more features in the current bucket still need
   specs, re-invoke this skill for the next one and name it.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
