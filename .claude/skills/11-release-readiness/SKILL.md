---
name: 11-release-readiness
description: Make the evidence-based go/no-go assessment for one release bucket and, on GO, update the engineering baseline — produce a Release Assessment under docs/reviews/ (scope delivered vs. planned, verification and integration evidence, known deviations, residual risks, explicit GO/NO-GO), and on GO flip the baseline records (ROADMAP.md statuses, release-plan bucket state, Claude.md status line, affected INDEX files) so the whole tree agrees the release shipped. Use when asked "are we ready to release," "run the release readiness review," "close out the baseline/MVP bucket," or after 10-integration-review comes back clean for a release's scope. The GO/NO-GO recommendation is advisory — the user makes the actual release decision (G4); this skill never writes code, never edits packages/specs/requirements, and performs no deployment. Do not use it to review package integration (10) or to verify packages (09).
---

# Release Readiness & Baseline Update

Closes the loop on **one release bucket** (MVP / Release 1 / Release 2, per
`docs/feature-planning/01-release-plan.md` — this project has no as-built baseline bucket, since
nothing has shipped yet): assembles the evidence that the bucket's promised
scope was delivered, verified, and integration-reviewed; states an explicit **GO / NO-GO**
recommendation with the reasoning; and — on the user's GO — updates the engineering baseline so
every tracker agrees the release shipped. The final stage; its output is the record the *next*
increment plans against.

## What this is for (and what it is not)

One question: *for this release bucket, does the evidence — not the intention — show that
everything promised is `VERIFIED`, integrated, documented, and honest about deviations, such that
declaring the release is defensible?*

It SHALL NOT: write or fix code · edit packages/specs/requirements/architecture · re-run
verification or integration review itself (a missing report is a NO-GO input, not a gap to fill
in-pass) · deploy anything · declare GO on the user's behalf (G4 — the recommendation is
advisory; the user makes the call before any baseline flip).

## Inputs (all read-only)

The release plan + feature catalog (`docs/feature-planning/`), the Master Build Plan + package
index (`docs/implementation/`), the VRs (`docs/implementation/verification/`), the Integration
and Content Review reports for this scope (`docs/reviews/`), the RTM, and `ROADMAP.md`.

## Workflow

1. **Reconstruct the promise.** From the release plan: every Feature in the bucket, and from the
   catalog/RTM every requirement those features own. Scope as *planned*, not as it conveniently
   ended up.
2. **Audit delivery.** Feature by feature: FS approved → package(s) planned → `VERIFIED` (with a
   real VR) → covered by a clean Integration Report (and Content Review where content shipped).
   Any feature deferred, descoped, or split since planning is a **deviation** to record with its
   authorizing decision (or flagged as unauthorized drift).
3. **Sweep residual risk.** Outstanding Issues from Implementation Summaries, Low/Medium findings
   accepted through 09/10, open Candidate Requirements touching this scope, known-stale docs.
   None necessarily blocks GO — unstated ones do.
4. **Write the Release Assessment** → `docs/reviews/release-assessment-<release>.md`: **Release**
   (bucket, date, commit hash) · **Scope audit** (one row per planned Feature: FS → IP(s) →
   VR(s) → integration coverage → delivered/deviated) · **Evidence** (ROM build + test-suite
   state, the VR/report inventory relied on) · **Deviations** (each with its authorization
   trail) · **Residual risks** · **Assessment** (**GO**/**NO-GO**, blocking items enumerated on
   NO-GO).
5. **On the user's explicit GO — update the baseline** (the only mutating step, trackers only):
   flip the bucket's state in `01-release-plan.md`; flip delivered rows in `ROADMAP.md`; update
   `Claude.md`'s status/version line (e.g. the "Known Good Behavior (vN)" heading); update
   affected `INDEX.md` files; date-stamp the baseline in the assessment. Commit as
   `docs(release): <release> — assessment + baseline update`. On NO-GO (or GO not yet given),
   write the assessment only and touch nothing.

## Quality gate

- [ ] Every Feature the release plan put in this bucket appears in the scope audit — none quietly
      dropped.
- [ ] Every "delivered" row is backed by a named VR and integration coverage, not memory.
- [ ] Every deviation has its authorization trail, or is flagged as unauthorized drift.
- [ ] The GO/NO-GO reasoning is stated, and no baseline record flipped without the user's
      explicit GO.
- [ ] After a GO flip: release plan, ROADMAP, Master Build Plan, and Claude.md agree — no tracker
      telling the old story.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 11 — Release Readiness & Baseline Update**, the final stage of the pipeline
(see [`.claude/skills/README.md`](../README.md)). Upstream: `10-integration-review`. Downstream:
the next increment's planning.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the Release Assessment written (path + GO/NO-GO), and any baseline records
   flipped (only after an explicit user GO).
2. **Recommendations** — on NO-GO, the blocking items each with its owning skill; on GO, the
   residual risks the user is accepting and any deferred scope now owed to a future bucket.
3. **Next step** — on NO-GO: the highest-leverage blocking item's owning skill (usually 07→08→09,
   then re-run 10); on GO with baseline updated: the next increment — `00-pipeline-manager` to
   survey the tree, then typically `05`/`06` for the next bucket, or `01`/`02-research-*` if the
   increment changes direction.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
