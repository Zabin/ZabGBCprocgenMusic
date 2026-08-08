---
name: 07-implementation-planning
description: Transform approved Feature Specifications (FS-xxx) — or backlog bugs routed here as remediation work — into an executable implementation plan under docs/implementation/ — a Technical Work Breakdown, build-ready Implementation Packages (IP-xxxx, the 14-field template), and the Master Build Plan (sequencing, dependency graph, critical path, status ledger). Use when asked to "plan the implementation of FS-xxx," "write the implementation package for this feature," "package the fix for BL-xxxx," "break this spec into work packages," or "update the Master Build Plan." This skill writes no production code (packages describe work in prose/pseudocode only), performs no research, no architecture redesign, no requirements authoring, and never modifies the Feature Specification it plans — and authoring a package is never itself an authorization to code it (G3): a package that implements work already scheduled by the current, user-approved release plan inherits that plan's authorization automatically; a package outside the release plan (not on it, or a materially different shape than what it describes) still needs the user's explicit per-package go-ahead. Do not use it to write Feature Specifications (06) or to implement packages (08).
---

# Implementation Planning

Turns **approved Feature Specifications** (and backlog-routed bug remediations) into an
**executable implementation plan**: a Technical Work Breakdown, Implementation Packages
(`IP-xxxx`), and an up-to-date Master Build Plan. It decides *how the work is cut and sequenced*
— never *what the engine/visualizer does* (upstream) and never *the code itself* (downstream).

## What this is for (and what it is not)

It SHALL NOT:

- **Write production code.** No package contains literal committed code — tasks and tests are
  described in prose/pseudocode sufficient for a coding agent, never as compilable source.
- **Modify specs, requirements, or architecture.** An unimplementable spec or a conflict found
  while planning routes upstream — never planned around quietly.
- **Authorize coding (G3) beyond what the release plan already covers.** A package being fully
  specified — even `READY` — is not itself authorization to build. If the package implements work
  the current, user-approved release plan (`docs/feature-planning/01-release-plan.md`, or its
  successor) already schedules, in the shape the plan describes, that plan approval is the
  authorization — no separate per-package go-ahead is required. A package that is *not* on the
  release plan, or diverges materially from what the plan describes (different scope, different
  approach, a plan the user hasn't actually approved), still requires the user's explicit
  per-package go-ahead before any stage-08 peer may build it. State every new package's
  authorization status explicitly, and cite which basis applies — release-plan coverage (name the
  plan section/row) or an explicit user go-ahead.
- **Execute anything.** The moment work turns into editing the repo-root `.py` files, it belongs
  to stage 08.

Authoritative read-only inputs: `docs/features/FS-xxx` · `docs/feature-planning/` ·
`docs/requirements/` · `docs/architecture/` (+ ADRs, GDS-09 interfaces) · `docs/pipeline/backlog.md`
(for bug remediations) · **the live source tree** (verify every cited file/function/label exists).

## Outputs

All under `docs/implementation/` (this skill's sole write scope):

1. **`docs/implementation/01-technical-work-breakdown.md`** — per tranche: FS (or BL) → work
   units → owning package(s), with the rationale for every split/no-split decision. Even a
   single-package tranche gets a short TWBS section — the record of *why the cut is what it is*
   is the artifact.
2. **`docs/implementation/packages/IP-xxxx-<slug>.md`** — one per unit of work, the **14-field
   template**, every field populated: Package ID · Objective · Requirements Covered ·
   Architecture Components · Interfaces · Files to Create/Modify · Implementation Tasks · Tests
   to Add · Documentation Updates · Definition of Done · Verification Checklist · Dependencies ·
   Risks · Rollback Considerations. Assign to the owning stage-08 peer explicitly: a logic/build
   package names `08-code-implementation`; a pure art/screens/music package names
   `08-content-authoring`; a structure-only (behavior/meaning-preserving) package names
   `08-refactoring`.
3. **`docs/implementation/00-master-build-plan.md`** — updated, not regenerated: new package
   rows (status, blocking dependencies, authorization state), dependency-graph edges,
   critical-path recalculation, parallel notes. Update `packages/INDEX.md` in the same pass —
   the index and the plan must never disagree.

## Conventions

- **ID scheme:** `IP-<FS series>0` mirrors the FS series (FS-101 → `IP-1010`; lettered slices
  `IP-1011`); bug-remediation packages with no FS take the `IP-9xx0` series, citing their
  `BL-xxxx`; refactoring packages take the `IP-8xx0` series, citing their `refactor`-type
  `BL-xxxx`. Check `packages/INDEX.md` for claimed IDs; gapped numbering.
- **Refactoring packages** (`IP-8xx0`) name `08-refactoring` as executor and additionally carry
  an **equivalence contract** in their Verification Checklist: byte-identical ROM (the default) or
  an enumerated, per-delta-justified list of predicted byte deltas; for doc-scoped work, the
  meaning-preservation constraints and the migration-map location if IDs/files move (grounding:
  `R310`). A package that mixes refactoring with behavior change must be split — the equivalence
  proof doesn't survive mixing. Refactoring packages follow the same G3 rule as every other
  package: authorized automatically if the release plan already schedules the refactor in the
  shape described, otherwise requiring the user's explicit go-ahead.
- **Status vocabulary (verbatim):** `NOT STARTED / READY / IN PROGRESS / BLOCKED / COMPLETE /
  VERIFIED`. This skill only writes `NOT STARTED`, `READY`, or `BLOCKED` — `IN PROGRESS`/
  `COMPLETE` belong to stage 08, `VERIFIED` exclusively to `09-package-verification`.
- **`READY` means** fully specified **and** every dependency `VERIFIED` (`COMPLETE` is not
  sufficient — stays `BLOCKED` with a note).
- **Every package is forward-design.** This project has no shipped ROM to document as-built, so
  every package enters at `NOT STARTED`/`READY`/`BLOCKED` and earns `COMPLETE`/`VERIFIED` the
  normal way, through stage 08 then 09 — there is no as-built-record entry path.

## Workflow

### Step 0 — Confirm the inputs are approved and eligible

The target FS(s) must be approved with no blocking Open Questions (or the target `BL-xxxx` must
be `SCHEDULED` to this step by the manager). If not, stop and report which gate is open and who
owns it.

### Step 1 — Technical Work Breakdown

Decompose along real seams: module boundaries (`gbc_lib`/`tiles`/`patterns`/`music_data`/
`music_engine`/`visuals`/`input_map`/`build_rom`), interface boundaries (GDS-09 contracts), test
boundaries (`test_rom.py` suites), and the code/content peer split. Right-size: one package = one
focused stage-08 run against one coherent Definition of Done. Record every split decision.

**Verb inventory (mandatory for any capability spanning more than one runtime concern).** Before
cutting packages, list every verb the capability actually requires — typically some subset of
*generate, render, apply, persist, review*. For each verb, name the package that covers it, or
record an explicit, deliberate deferral (with the reason). A capability is not fully decomposed
until every verb has an owner or a named deferral — silence is not a deferral. (Illustrative risk:
a bad-zone increment that packages *detect* — computing the dissonance/repetition/overload metric
— and *display* — showing a bad-zone indicator on the visualizer — but never names a package whose
Files-to-Modify actually wires the Select button to the *reset* verb, so the engine could
correctly detect and show a bad zone yet never let the listener escape it. Nothing in the TWBS
would catch this without an explicit verb-by-verb check.)

**Supersession sweep (mandatory whenever a package retires or supersedes an existing model).**
When a package's own framing is "generalizes X past its old fixed shape" or "supersedes Y," search
the tree for *every* call site that still encodes the pattern being retired — not just the one
call site the package's own Files-to-Modify names. A `grep` for the old model's literal signature
(hardcoded index comparisons, magic constants tied to the old shape, fixed-count loops) across
`music_engine.py`/`input_map.py`/`build_rom.py` is cheap and must be run before the package is
considered complete-in-scope. Record what the sweep found — including "found nothing else,
confirmed clean" as a real, positive result, not silence. (Illustrative risk: a package that
generalizes the engine from a fixed 4-channel assumption to a configurable active-channel set, but
a bad-zone "channel overload" check elsewhere still hardcodes the old fixed channel count — a
sweep for the old literal channel-count constant across the tree would surface it before either
package is called done.)

### Step 2 — Author the package(s)

All 14 fields, grounded in the **current** source tree — verify every file, function, label, and
constant the package cites actually exists as described (or is honestly marked "to create"). A
guessed `Files to Modify` list is this skill's most expensive defect: stage 08 treats drift as a
hard Blocking condition. `Tests to Add` names the `test_rom.py` suite/check it lands in;
`Verification Checklist` always includes the two permanent gates by name (ROM builds at 32768
bytes with valid header; full `test_rom.py` suite passes — G5). ROM-budget impact (bytes added,
section it lands in per GDS-07) belongs in Risks for any package that grows data or code.

### Step 3 — Update the Master Build Plan and package index

New rows (status, blockers, authorization state), graph edges, critical path, parallel
opportunities; `packages/INDEX.md` in sync. Per new package, state explicitly whether G3
authorization exists and its basis: **release-plan coverage** (cite the release plan section/row
the package matches, in shape and scope) or an explicit **user go-ahead on record**. If neither
applies, the default is **not authorized**.

### Step 4 — Cross-link and commit

Update each planned FS's metadata to point at its package(s) (metadata only), flip `ROADMAP.md`'s
implementation rows, commit as `docs(implementation): IP-xxxx — <what was planned>`.

## Quality gate

- [ ] Every planned FS/BL was confirmed approved + eligible before drafting.
- [ ] Every package has all 14 fields populated — no literal code anywhere.
- [ ] Every Files to Create/Modify entry checked against the current tree.
- [ ] Every Requirements Covered ID exists in `docs/requirements/` and matches the FS.
- [ ] Dependency edges consistent across package fields, the plan's graph, and the index.
- [ ] No package `READY` whose dependencies aren't all `VERIFIED`; no package marked authorized
      without an explicit, cited basis (release-plan coverage naming the matching section/row, or
      a user go-ahead) — a package outside or diverging from the release plan defaults to not
      authorized.
- [ ] The TWBS records the rationale for every split/no-split decision.
- [ ] For a multi-verb capability (generate/render/apply/persist/review), every verb has a
      named package or a recorded, deliberate deferral — the TWBS states this explicitly.
- [ ] For a package that supersedes an existing model, the supersession sweep was run and its
      result (clean, or what else it found) is recorded in the TWBS or the package itself.

## Gotchas

- **Don't let a package become a second FS.** The FS owns behavior; the package owns
  files/tasks/tests/sequencing.
- **Plan for verification at authoring time.** Every Verification Checklist item must be
  objectively checkable against the tree and a test run — a vague checklist makes stage 09 guess.
- **Bug remediations get packages too** — that's what keeps a fix traceable. A remediation
  package cites its `BL-xxxx` and the failing behavior; if the bug reveals a spec/requirements
  gap, route that upstream instead of absorbing it.
- Watch the ROM budget: `build_rom.py` lays out fixed sections (see GDS-07 / `Claude.md`); a
  package adding tile art, visualizer patterns, or scale/rhythm data must say where the bytes go.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 07 — Implementation Planning** of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream: `06-feature-specification`
(or the backlog, for remediations). Downstream: `08-code-implementation` /
`08-content-authoring`.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — TWBS sections, packages authored (IDs + paths + owning 08 peer), Master
   Build Plan / index rows, each new package's status + authorization state.
2. **Recommendations** — spec defects or Open Questions routed upstream, right-sizing concerns,
   critical-path or ROM-budget risks the user should know before authorizing.
3. **Next step** — if the new package(s) are `READY` and authorized (release-plan coverage cited,
   or an explicit user go-ahead on record), advance to the owning stage-08 peer naming the first
   package (critical-path first); if authorization is missing (package not on, or diverging from,
   the release plan), ask the user for the explicit go-ahead; if planning was blocked upstream,
   name the owning skill and what it must resolve.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
