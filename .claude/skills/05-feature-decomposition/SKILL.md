---
name: 05-feature-decomposition
description: Transform an approved requirements baseline (docs/requirements/) into an implementable Release Plan, Epic Catalog, Feature Catalog (FEAT-xxxx planning rows), Feature Dependency Graph, and Feature Review under docs/feature-planning/. Use when asked to "decompose the requirements into features," "build a feature catalog," "group requirements into epics," "plan releases/MVP scope," "build a feature dependency graph," or as the stage-05 step of the project's first, from-scratch increment. This skill performs no new research, no architecture redesign, no requirements authoring/editing, no implementation packages, and no code — it is a pure organization-and-planning step between an approved requirements baseline and downstream Feature Specifications (FS-xxx). Catalog rows (FEAT-xxxx) are planning-grain summaries, deliberately distinct from the full FS-xxx specification documents stage 06 writes.
---

# Feature Decomposition

Turns an **approved requirements baseline** into a **Release Plan, Epic Catalog, Feature Catalog,
Feature Dependency Graph, and Feature Review**. The bridge between "what must the music engine and
visualizer do" and "what do we build first, in what order." Strictly downstream of 04; strictly
upstream of 06.

## What this is for (and what it is not)

One question: *given the approved requirements, what is the smallest set of cohesive,
independently-implementable units covering all of them, how do they group into epics, how do they
depend on each other, and in what order should they ship?*

It SHALL NOT: perform research · redesign architecture (module boundaries are inputs) · create or
modify requirements (a gap found here is a Review finding, never a new FR) · generate
implementation packages or estimates (Complexity/Risk are qualitative signals only) · write code.

Authoritative inputs (read-only): `docs/requirements/` (primary material) · `docs/architecture/`
(GDS ladder + ADRs — module boundaries are the structural seams) · `docs/research/` (context
only). **Confirm the requirements baseline is approved** (Review findings adjudicated) before
grouping; if not, stop and surface that.

## Outputs

Always exactly these five files under `docs/feature-planning/` (plus the directory's `INDEX.md`):

1. `docs/feature-planning/01-release-plan.md`
2. `docs/feature-planning/02-epic-catalog.md`
3. `docs/feature-planning/03-feature-catalog.md`
4. `docs/feature-planning/04-feature-dependency-graph.md`
5. `docs/feature-planning/05-feature-review.md`

**Produce them in dependency order** (features → epics → graph → releases → review), then write
all five; the numbered read order stays release-plan-first.

**ID conventions:** catalog rows are `FEAT-xxxx` (4-digit, gapped) — deliberately **not**
`FS-xxx`, which stage 06's full specification documents own. Epics are `EP-xxxx`.

## Workflow

### Step 0 — Requirement inventory

Read every approved input. Inventory: every FR/NFR ID (with module affiliations), every module
and interface from GDS-03/GDS-09, every constraining ADR, and any requirement with no clean home
(flag now, don't force-fit later).

### Step 1 — Feature Catalog (draft) → `03-feature-catalog.md`

Group related requirements into Features — one coherent listener-visible capability or one
internally complete system capability each (e.g., on the first pass, natural candidates are:
engine state machine (init/generating/bad-zone/reset) · music-generation algorithm (scale/tempo/
rhythm/voice-leading/density) · channel management & register writes · bad-zone detection &
Select-reset · button-to-parameter input mapping · SRAM save/load (if persisted state exists) ·
visualizer (tile/palette animation synced to tempo/voice-activity/register-state) — let the FR
groupings lead, don't force this list). Maximize cohesion, minimize coupling; align Feature
boundaries with module boundaries wherever the requirements support it, and justify any straddle
explicitly.

Every Feature carries the fixed field set: Feature ID (`FEAT-xxxx`) · Title · Purpose ·
Description (behavior terms) · Scope · Included Requirements (each FR/NFR owned by exactly one
Feature project-wide) · Excluded Requirements (where the adjacent ones actually live) ·
Dependencies · Dependent Features (keep both directions in sync) · Affected Modules · Related
ADRs · User Value · Technical Value · Complexity (qualitative + reasoning) · Risk · Suggested
Verification Strategy · Open Questions.

### Step 2 — Epic Catalog → `02-epic-catalog.md`

Group Features into Epics (`EP-xxxx`): ID · Title · Purpose · Features Included (complete list) ·
Modules · Estimated Scope (qualitative) · Risks · Dependencies. Every Feature belongs to exactly
one Epic; a Feature that seems to belong to two is mis-scoped (split it) or the Epic boundaries
are wrong (report it). Prefer fewer, well-justified Epics.

### Step 3 — Dependency Graph → `04-feature-dependency-graph.md`

Analyze feature, interface, architectural, and data-ownership dependencies. Document explicitly:
the **critical path**, **blocking Features** (high fan-out), **parallel opportunities**, and any
**circular dependency** (a Critical Review finding with the exact cycle — never silently broken).
Primary artifact: Mermaid `graph TD`/`LR` diagram(s) plus a written summary; split per-Epic if a
single graph exceeds ~25–30 nodes.

### Step 4 — Release Plan → `01-release-plan.md`

Assign **every** Feature to exactly one bucket: **MVP** / **Release 1** / **Release 2** /
**Future** — this project has no as-built baseline bucket, since nothing has shipped yet; the MVP
bucket is the truthful floor instead, and it earns that status the normal way (approved
requirements, decomposed, planned) rather than by already existing in a shipped ROM. Document
*why* for each assignment (value, graph position, risk, or a stated constraint). No Feature
schedules before a Feature it depends on. Call out explicitly: Highest Value · Highest Risk ·
Foundational · Optional · Deferred.

### Step 5 — Feature Review → `05-feature-review.md`

Review 02–04 for: Features too large/too small · duplicates · missing Features · requirements
not assigned / assigned twice (check against Step 0's inventory) · architectural inconsistencies.
One finding per row: `Finding type | IDs involved | Description | Severity | Recommendation`.
**Recommend — do not modify the other documents in the same pass.** A zero-finding first pass is
a signal to re-check the review, not proof of quality.

## Quality gate

- [ ] Baseline confirmed approved before grouping began.
- [ ] Every Feature/Epic has all fields populated (or explicitly None with a reason).
- [ ] Every FR/NFR owned by exactly one Feature; every Feature in exactly one Epic and one
      release bucket; no Feature scheduled before its dependency.
- [ ] Mermaid diagram(s) render and match the prose edges; no unresolved cycle.
- [ ] The Review reviewed the final content and applied no fixes.
- [ ] Nothing originated a requirement, architecture decision, package, or code.

## Gotchas

- **Catalog rows are not Feature Specifications.** A `FEAT-xxxx` row is a planning-grain summary
  that stage 06 expands into a full `FS-xxx` document under `docs/features/` — don't let a
  catalog entry grow into a spec body, and don't reuse the `FS-` prefix here.
- Run Step 5 standalone (no Steps 1–4) as a cheap health check when the catalog may have drifted.
- Maintain incrementally: a single requirements change updates the affected Feature + its
  Epic/graph/release rows, not a regeneration.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 05 — Feature Decomposition** of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream:
`04-requirements-engineering`. Downstream: `06-feature-specification`.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — which of the five deliverables were produced or updated (paths), and the
   headline numbers (features, epics, buckets, critical-path length).
2. **Recommendations** — the Feature Review's key findings (unassigned/double-assigned
   requirements, oversized features, cycles) and who owns each; anything needing a requirements
   or architecture change goes upstream to `04`/`03`.
3. **Next step** — if the Review surfaced Critical findings, resolve them first; otherwise
   advance to `06-feature-specification`, naming the specific catalog entry to specify next (the
   highest-priority bucket's first unspecified, unblocked feature per the release plan and
   dependency graph).

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
