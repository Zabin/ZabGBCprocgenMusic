# Product Roadmap — Index

- **Authored:** 2026-07-22, as a Lead-Systems-Architect/TPM synthesis pass across the existing
  Vision (`docs/master/MSTR-001-program-vision.md` v1.4) and the full Research Encyclopedia
  (`docs/research/`, 42 topics) — **no new research performed**, per the request that produced
  this package.
- **Authority:** MSTR-001 remains the authoritative Vision document. This package operationalizes
  it into a sequenced, traceable plan — it does not supersede, amend, or restate it as a competing
  source of truth. Where this package and MSTR-001 ever appear to disagree, MSTR-001 wins and this
  package is the one that needs correcting.
- **Relationship to the existing pipeline**: this package sits above `03-architecture-design-
  synthesis`/`05-feature-decomposition`/`06-feature-specification` in grain (it plans *what
  sequence of releases*, not *what a given package's files/tasks/tests are*) and is meant to feed
  those stages, in order, as each release is actually picked up — it is not itself an
  implementation plan and authorizes no code (G3 still applies per-package, unchanged).

[↑ Docs index](../INDEX.md) · [↑ Pipeline journal](../pipeline/pipeline-journal.md)

| # | Document | Answers |
|---|---|---|
| 01 | [Product Goals](01-product-goals.md) | What does success look like, in experience terms? |
| 02 | [Capability Map](02-capability-map.md) | What are all the capabilities, and what's their real current status? |
| 03 | [Capability Dependency Graph](03-capability-dependency-graph.md) | What order can/must capabilities be built in? |
| 04 | [Release Roadmap](04-release-roadmap.md) | What is the actual sequence of releases, R0-R13 (+R4.5)? |
| 05 | [Milestone Definitions](05-milestone-definitions.md) | How do releases group into demonstrable checkpoints? |
| 06 | [Feature Specifications](06-feature-specifications.md) | What are the individual features per release, catalog-grain? |
| 07 | [Traceability Matrix](07-traceability-matrix.md) | Does everything trace back to the Vision? What doesn't? |
| 08 | [Development Strategy](08-development-strategy.md) | How is this actually built, iteration to iteration? |
| 09 | [Release Exit Criteria](09-release-exit-criteria.md) | What must be true before any release is "done"? |
| 10 | [Final Roadmap Review](10-final-roadmap-review.md) | What's wrong with this roadmap, honestly? |

## Current state at authoring time (2026-07-22)

Milestone A (Foundation) is substantially complete — `R0`-`R1` shipped and `VERIFIED`, `R2`
shipped and `COMPLETE` pending `09-package-verification`. Milestone B is next but blocked on the
standing G3 authorization gate for `IP-9010`/`IP-9020` (`docs/pipeline/backlog.md` `BL-0019`/
`BL-0017`) — this package does not change that gate's status; it only sequences what happens once
it clears. Milestone C is independently startable in parallel, per `03-capability-dependency-
graph.md`.

## Integration with `00-pipeline-manager` (added 2026-07-22)

This package is now a standing input to the manager's loop, not a one-off artifact sitting outside
it:

- **Step 1 (reconcile)**: `00-pipeline-manager` reads `04-release-roadmap.md` (+ this index)
  alongside its other cross-stage ledgers (`ROADMAP.md`, the Master Build Plan, etc.) every run,
  and notes drift the same way it does for any other ledger (a release this file still marks "not
  started" that the tree shows in progress, etc.).
- **Step 3 (choose the next step)**: the roadmap's release sequence and dependency graph act as a
  **tie-breaker among options tier-precedence and the backlog already leave unblocked** — it never
  overrides a gate, a tier-precedence rule, or the pipeline's own upstream-before-downstream order.
  If the roadmap and the backlog-driven recommendation conflict, the backlog/tier-precedence
  recommendation wins and the conflict is journaled so this package can be corrected.
- **Write ownership**: `00-pipeline-manager` **reads but never writes** this directory (same
  "never edit a ledger the stages own" guardrail that already governs `ROADMAP.md`,
  `docs/implementation/00-master-build-plan.md`, etc.). Whichever skill's run actually completes or
  starts work on a named release (`R3`, `R4.5`, `R6`, …) is responsible for updating that release's
  status line in `04-release-roadmap.md` as part of its own normal doc-update discipline — the
  same convention every skill already follows for keeping `ROADMAP.md`'s per-stage row current.
- **Full mechanics**: see `.claude/skills/README.md`'s "Product Roadmap" section and
  `00-pipeline-manager/SKILL.md`'s Step 1/Step 3.

## How to use this package going forward

When a release from `04-release-roadmap.md` is picked up: **(1)** confirm its named precondition
(if any) is satisfied, **(2)** hand its capability/feature entries to `03-architecture-design-
synthesis` for any named-open design question, **(3)** hand the resulting design to
`04-requirements-engineering`/`05-feature-decomposition`/`06-feature-specification` to produce the
real `FR-xxxx`/`FEAT-xxxx`/`FS-xxx` artifacts (this package's `RM-xxxx` catalog entries are inputs
to that work, not replacements for it), **(4)** `07-implementation-planning` cuts the actual
`IP-xxxx` packages, **(5)** the normal `08`→`09`→`10`→`11` cycle proceeds as it always has. This
package is planning input at every one of those steps, never a shortcut around any of them.
