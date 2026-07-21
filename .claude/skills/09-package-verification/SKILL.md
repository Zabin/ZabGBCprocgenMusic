---
name: 09-package-verification
description: Independently verify exactly one COMPLETE Implementation Package against the shipped code — re-check every Definition of Done and Verification Checklist item against the actual source tree, rebuild the ROM and run the full test_rom.py suite (the permanent gates), audit the traceability updates the implementation claimed, produce a Verification Report (VR-xxxx) under docs/implementation/verification/, and advance the package COMPLETE→VERIFIED (or send it back with findings). This is the ONLY skill authorized to write VERIFIED on the Master Build Plan. Use when asked to "verify IP-xxxx," "check the last implemented package," or after any stage-08 run finishes. It verifies against what the package and its FS already say — it never fixes code (that goes back to stage 08), never edits the package or spec, and never verifies its own same-session implementation work. Do not use it to implement packages (08) or to review a whole release's packages together (10-integration-review).
---

# Package Verification

Independently confirms that **one Implementation Package marked `COMPLETE`** actually delivers
what it claims, then — and only then — advances it to `VERIFIED`. Sole authority for the
`COMPLETE → VERIFIED` transition. Its value is independence: it re-derives every claim from the
tree and the test run, taking nothing in the Implementation Summary on faith.

## What this is for (and what it is not)

One question: *does the shipped code, as it exists right now, satisfy every item of this
package's Definition of Done and Verification Checklist, every requirement in its Requirements
Covered, and the repository's permanent gates — yes or no, with evidence?*

It SHALL NOT:

- **Fix anything.** A failed check routes back to the owning stage-08 peer (or upstream if the
  defect is in the package/spec) — never a same-session patch, however small.
- **Edit the package, FS, requirements, or architecture.** All read-only. An unverifiable-as-
  written checklist is a finding for `07-implementation-planning`.
- **Verify work implemented in the same session.** State that independence is degraded and
  recommend a fresh session; proceed only if the user accepts the caveat explicitly.
- **Verify more than one package per invocation.**
- **Rubber-stamp.** `VERIFIED` with any item unchecked, any test failing, or any traceability
  cell stale corrupts the ledger the whole downstream pipeline trusts.

## Inputs (all read-only)

The target package (`docs/implementation/packages/IP-xxxx-*.md`), its FS, its Requirements
Covered FR/NFRs + the RTM, the Master Build Plan (read + status-write), the GDS/ADR sections it
cites, and the live source tree + `test_rom.py`.

## Outputs

1. **`docs/implementation/verification/VR-xxxx-<slug>.md`** — numbered to match the package
   (IP-1010 → VR-1010). Create the directory's `INDEX.md` (VR ID, package, date, result, headline
   findings) on first use. Sections: **Package** (ID, title, commit hash verified) · **Result**
   (`VERIFIED`/`RETURNED` + failed-check count) · **Definition of Done audit** (one row per item:
   evidence — file:line, check name, command output — pass/fail) · **Verification Checklist
   audit** (same) · **Requirements audit** (per Requirements Covered ID: where implemented ·
   where tested · RTM cell state · pass/fail) · **Test run** (full-suite counts + the exact
   commands: `python3 build_rom.py <path>` byte count + header validity, `python3 test_rom.py`
   pass/fail counts) · **Scope audit** (did the implementing diff stay inside the declared file
   set + the stage-08 peer seam — name any excursion) · **Findings** (one row each: description ·
   severity · recommended owner).
2. **Updated Master Build Plan + `packages/INDEX.md`**: on pass, `VERIFIED`, and downstream
   blocking notes updated (a dependent flips to `READY` only if *all* its dependencies are now
   `VERIFIED`). On fail, back to `IN PROGRESS` (or `BLOCKED` if the defect is upstream) with a
   pointer to the report.
3. **Updated RTM** — only to correct cells the audit proved wrong or confirm ones the
   implementation filled; never to paper over a gap.

## Workflow

1. **Select and gate.** The package must be exactly `COMPLETE`; anything else is ineligible —
   report the actual status and stop. Check the same-session independence rule.
2. **Read the package in full**, plus FS/requirements/cited GDS/ADRs. Build the checklist
   inventory: every DoD item, checklist item, Requirements Covered ID, named file.
3. **Audit the tree.** Every claimed file/change: confirm it exists and does what the package
   says by reading the code — not the Implementation Summary. Diff-scope check against the
   declared file set and the code/content peer seam.
4. **Run the gates.** Rebuild the ROM (byte count + header), run the full `test_rom.py`, record
   exact counts. For content packages, also re-drive the affected patterns/presets via
   `run-driftune` and compare against the spec's acceptance criteria/screenshots/register
   readouts. Any failure — even one that looks pre-existing — is investigated far enough to assign
   ownership: this package's defect (fail the verification) or pre-existing (finding with
   evidence). **If the package's Definition of Done references a tunable or generated parameter**
   (a seed, a scale/mode, a tempo, a density, an active-channel count — anything a listener or the
   generator sets at runtime that the suite's own shared fixtures default to one fixed value for),
   **drive the built ROM via `run-driftune` at a non-default value of that parameter yourself**,
   live, and check the claimed behavior directly — a full green suite is not sufficient evidence on
   its own if every suite that exercises the package shares a fixture that never varies the
   parameter. (Illustrative risk: a package's DoD is about density scaling from sparse to dense,
   every consuming suite's fixture defaults density to one fixed mid-range value, and the suite
   passes 100% green while density=0 or density=max both silently produce broken channel writes —
   no VR would catch that unless it drove the ROM at a non-default density itself rather than
   trusting the suite's existing fixture coverage.)
5. **Audit traceability.** Every Requirements Covered ID traces in the RTM to real files and
   real checks this package shipped.
6. **Write the report**, update the ledgers, commit as `docs(verification): VR-xxxx — <result>`.

## Quality gate (before writing `VERIFIED`)

- [ ] Every DoD and checklist item has recorded evidence — none waved through.
- [ ] ROM builds (32768 bytes, valid header); full suite green — run by name, counts recorded.
- [ ] Every covered requirement traces to real code and a real check in the RTM.
- [ ] The implementing change stayed in scope, or every excursion is explained and accepted.
- [ ] The report's Result matches the ledger status written.
- [ ] No code, package, spec, or requirement was edited by this run.
- [ ] For any tunable/generated parameter the DoD references, this run itself drove the ROM at a
      non-default value — not just re-run the suite and trusted its existing fixture coverage.

## Gotchas

- Every package on this project is a forward-design package (there is no as-built baseline to
  verify against) — verification is always against the current tree, not any historical claim;
  drift from what the package/FS says is a finding regardless.
- A `RETURNED` result is a *normal* outcome — cheap detection is the point. Route the finding,
  don't soften the result.
- Severity honesty: a cosmetic doc typo can pass with a Low note; an unchecked DoD item is a hard
  fail. Don't let smallness tempt you into fixing it — even one line belongs to stage 08.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 09 — Package Verification** of the pipeline (see
[`.claude/skills/README.md`](../README.md)). Peer: `09-content-review` (qualitative content
review). Upstream: the stage-08 peers. Downstream: `10-integration-review` (once a tranche's
packages are all `VERIFIED`), or back to stage 08 for the next package.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the VR written (path + Result), status transitions applied, RTM cells
   corrected.
2. **Recommendations** — every finding with severity and owner; independence caveats if any.
3. **Next step** — on `RETURNED`: re-run the owning stage-08 peer on this package against the
   findings; on `VERIFIED` with more `READY` packages in the tranche: stage 08 on the next one
   (critical-path first); on `VERIFIED` with the tranche done: `10-integration-review`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
