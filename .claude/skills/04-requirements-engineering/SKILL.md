---
name: 04-requirements-engineering
description: Transform an approved architecture baseline (research encyclopedia, GDS ladder, ADRs) into a traceable requirements baseline under docs/requirements/ — hierarchical Functional Requirements (FR-xxxx), Non-Functional Requirements (NFR-xxxx), a Requirements Review report, and a Requirements Traceability Matrix. Use when asked to "derive requirements from the architecture," "write functional/non-functional requirements," "build a traceability matrix," "review the requirements for conflicts/gaps/duplicates," or as the stage-04 step of the project's first, from-scratch increment (derive the requirements from the GDS-05/06 architecture levels — there is no shipped ROM's verified behaviors to derive from yet). This skill performs no new research, no architecture redesign, and no implementation — it is a pure derivation-and-bookkeeping step. Do not use it to originate domain knowledge (02-research-*) or to make architecture decisions (03-architecture-design-synthesis).
---

# Requirements Engineering

Turns an **approved architecture baseline** into a **traceable requirements baseline**. Strictly
downstream of research and architecture; strictly upstream of feature planning and
implementation. It does not do either neighbor's job.

## What this is for (and what it is not)

One question: *given what has already been researched and architected, what must the music engine
and visualizer do, how well must they do it, and can every one of those statements be traced back
to a source and forward to a test?*

It SHALL NOT:

- **Perform new research.** A requirement needing a fact not in the inputs is a gap to report,
  not a fact to invent or look up.
- **Redesign the architecture.** A wrong/ambiguous/self-contradictory architecture statement is a
  Review finding, never patched by writing around it.
- **Implement code.** Requirements describe observable behavior, not implementation.
- **Invent requirements not supported by the inputs.** Anything untraceable goes to **Candidate
  Requirements**, explicitly excluded from the baseline, never silently promoted.

Authoritative inputs (read-only): `docs/research/` · the GDS ladder (`docs/architecture/`,
especially GDS-01…GDS-09) · `docs/architecture/adr/` · and, once they exist, `test_rom.py` (each
of its checks is evidence of a required, already-verified behavior) and `Claude.md`'s Known Good
Behavior list. On the project's first, from-scratch increment neither exists yet — the GDS ladder
is the sole source. **If inputs conflict, report the conflict in the Review — never resolve
it unilaterally.**

## Outputs

Always exactly these four files, in this order, under `docs/requirements/` (plus the directory's
`INDEX.md`):

1. `docs/requirements/01-functional-requirements.md`
2. `docs/requirements/02-non-functional-requirements.md`
3. `docs/requirements/03-requirements-review.md`
4. `docs/requirements/04-requirements-traceability-matrix.md`

## Workflow

Work the four steps in order; each step's output is the next step's input.

### Step 0 — Read the inputs and build a source map

Read every input document. Keep a working inventory (notes, not a deliverable) of: every distinct
**capability** GDS-01/GDS-05 implies; every **entity/relationship** in GDS-04; every **binding
ADR**; anything that reads as a requirement but has **no traceable source** (→ Candidate
Requirements later).

### Step 1 — Functional Requirements (`01-functional-requirements.md`)

Hierarchical, 4-digit gapped numbering (`FR-1000` capability → `FR-1100` major function →
`FR-1110` sub-function → `FR-1111` atomic leaf). Suggested capability groupings for this project
(adapt to what GDS-05 actually says): FR-1xxx engine states & transitions (init, generating,
bad-zone, reset) · FR-2xxx music-generation algorithm (scale/mode, tempo, rhythm, voice-leading,
density) · FR-3xxx channel management (NR1x-NR5x writes, active-channel set) · FR-4xxx bad-zone
detection & Select-reset · FR-5xxx button-to-parameter input mapping · FR-6xxx save/load (SRAM,
if the design persists last-good-state or user preferences) · FR-7xxx presentation/visualizer
(tile/palette animation synced to tempo, voice activity, register state).

**Every leaf requirement carries this fixed field set** (an explicit "None" is informative; a
missing field is not): ID · Title · Description · Rationale (cite the source statement) ·
Priority (state the scale once) · Inputs · Outputs · Preconditions · Postconditions · Acceptance
Criteria (checkable by a tester with no design context) · Dependencies · Verification Method
(Test/Demonstration/Analysis/Inspection — justify anything but Test) · Source Documents (exact
file + section) · Related ADRs · Notes.

**Writing rules** (FR and NFR alike): atomic (split "and"s) · unambiguous (no "should generally")
· testable · implementation-independent ("the engine shall reset to a good starting state when
Select is pressed while in the bad zone," not "write STATE_GOOD to WRAM address $C010") ·
consistent (contradictions are Review findings) · traceable ("implied by
the architecture" is not a citation) · complete (every Step-0 capability has ≥1 FR, or the gap is
a Review finding).

End with a `## Candidate Requirements` section for anything untraceable — same fields, explicitly
excluded from the numbered baseline, marked `CANDIDATE — NOT BASELINED` in the matrix.

### Step 2 — Non-Functional Requirements (`02-non-functional-requirements.md`)

Same ID discipline (`NFR-xxxx`), same fields and rules, under these category headings in order —
writing "(none derivable from inputs — see Candidate Requirements)" rather than inventing:
Performance (generation-tick/VBlank timing discipline) · Reliability · Maintainability
(one-job-per-file) · ROM/RAM budget · Data Integrity (save format/checksums, if persisted state
exists) · Portability (emulator + hardware) · Usability (input responsiveness, bad-zone
recoverability) · Testability · Build Reproducibility · Extensibility.

Numbers in Acceptance Criteria must come from a source document (e.g. a specific ROM byte budget,
a header field value, a named test-suite pass count once `test_rom.py` exists) — never from
generic convention; missing targets are flagged in Notes.

### Step 3 — Requirements Review (`03-requirements-review.md`)

Review the full FR+NFR set (plus Candidates) for: duplicates · conflicts (incl. vs. ADRs) ·
ambiguities · missing requirements · impossible requirements · architecture violations · missing
verification · missing traceability. One finding per row: `Finding type | IDs involved |
Description | Severity | Recommendation`. **Report only — apply nothing**; fixes are an explicit,
separate follow-up.

### Step 4 — Traceability Matrix (`04-requirements-traceability-matrix.md`)

One row per FR/NFR (Candidates marked). Columns: `Req ID | Title | Research Source |
Architecture Section | ADR | Module | Feature Spec | Implementation Package | Test`. Fill the
trace-back columns from Steps 0–3; the forward columns (Module, FS, IP, Test) get `UNASSIGNED`
where nothing exists yet — **never invent a forward reference**. Once `test_rom.py` exists, the
Test column can often be filled honestly from its named checks (T1.1…T10.x).

## Quality gate

- [ ] Every FR/NFR has all fields populated (or explicitly None with a reason).
- [ ] Every leaf is atomic, unambiguous, testable, implementation-independent.
- [ ] Every numbered requirement has a real Source Documents citation with a section.
- [ ] No baseline requirement contradicts another or an ADR — violations pulled to Candidates or
      flagged in the Review, never silently kept.
- [ ] The Review reviewed the final 01/02 content and applied no fixes.
- [ ] The matrix uses `UNASSIGNED` honestly; nothing originated a new fact, decision, or code.

## Gotchas

- Don't let Step 1/2 become design: a requirement naming a WRAM address or opcode has crossed
  into implementation — push back to observable behavior (the Data Model level GDS-07 owns the
  addresses).
- Don't backfill a matrix cell with a plausible guess — `UNASSIGNED` is the honest state.
- Delta updates (an ADR/GDS change): re-run Step 0 on the delta only, fix only the affected
  FR/NFRs, add a dated changelog note, re-run Step 3 focused on the change, update affected
  matrix rows — not a wholesale regeneration.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 04 — Requirements Engineering** of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream:
`03-architecture-design-synthesis`. Downstream: `05-feature-decomposition`.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — which of the four deliverables were produced or updated (paths), plus any
   changelog entries.
2. **Recommendations** — the Review's key findings (conflicts, gaps, candidates) and who owns
   each: architecture conflicts → `03-architecture-design-synthesis`, missing domain facts → the
   owning `02-research-*` skill, adjudication calls → the user.
3. **Next step** — if the Review surfaced Critical/High findings, resolve those upstream first
   and re-run the affected steps; once the baseline is approved (findings adjudicated, candidates
   dispositioned), advance to `05-feature-decomposition`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
