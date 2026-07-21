---
name: 08-code-implementation
description: Implement exactly one approved, eligible Implementation Package end-to-end — write the engine-logic/build-machinery code and tests it describes (music_engine.py, visuals.py, input_map.py, gbc_lib.py, build_rom.py, test_rom.py), rebuild the ROM, run the full test suite, fix defects this package's own changes introduced, update the documentation and traceability the package names, and advance that package's status on the Master Build Plan. Use when asked to "implement IP-xxxx," "pick up the next ready package and build it," or "execute the next step of the Master Build Plan." This is the first skill in the pipeline authorized to modify production source. It implements exactly one package per invocation, never redesigns architecture, never edits requirements/specs/packages, and never chooses work outside the Master Build Plan. Content-only packages (pure visualizer tile/palette art, curated scale/rhythm data) belong to its peer 08-content-authoring; verification to VERIFIED belongs to 09-package-verification.
---

# Code Implementation

Turns **one approved, eligible Implementation Package** into **working, tested code**. Strictly
downstream of planning; strictly upstream of independent verification. One package per
invocation, never more.

## What this is for (and what it is not)

One question: *given one package and everything decided upstream, what is the smallest, most
faithful set of code and test changes that satisfies exactly what the package describes — no
more, no less — leaving the repository fully green and fully traceable?*

It SHALL NOT: redesign architecture (a design that doesn't fit once you're in the code is a
Blocking Report, not a license to redraw a boundary) · change requirements · modify the FS or the
package being executed (drift/staleness is a Blocking Report) · select work outside the Master
Build Plan (no "while I'm here" fixes — Outstanding Issues instead) · write `VERIFIED` (stage
09's exclusive transition).

Authoritative read-only inputs: the Master Build Plan · the package · its FS · the requirements
it covers (+ RTM) · GDS-03/07/09 + ADRs.

**Write scope (G1):** `music_engine.py`, `visuals.py`, `input_map.py`, `gbc_lib.py`,
`build_rom.py`, `test_rom.py`, and exactly the files the package names. The data halves of
`tiles.py`/`patterns.py`/`music_data.py` belong to `08-content-authoring` — a package that needs
both surfaces should have been split; if it wasn't, that's a planning finding, not a reason to
cross the seam silently (note it and implement only what the package names).

## Workflow

### Step 0–1 — Read the plan, select the package

Read the full Master Build Plan status table + dependency graph. If the user named a package,
that's the candidate — still gate-check it. Otherwise select deterministically: status exactly
`READY` → every dependency `VERIFIED` (**`COMPLETE` is not sufficient**) → prefer critical path →
lowest ID → if still tied, ask. Zero survivors: stop and report what's closest and what it waits
on.

**Eligibility ≠ authorization (G3).** Check the package's recorded authorization state (explicit
user go-ahead on record — this project has no bootstrap carve-out; every package needs its own
go-ahead). If it isn't there, stop and ask.

### Step 2–3 — Read the package and everything it cites

Every field, not just Implementation Tasks. Then verify the package's claims about the current
tree (files, function/label names, constants) still hold — material drift is a **Blocking
Report**, never routed around with a plausible substitute. Note the repo's test convention:
`test_rom.py` is a single self-running script with `check(name, cond, detail)` assertions grouped
in suites T1–T10 — new tests extend the pattern (add checks to the owning suite, or a new suite)
and must leave the script runnable end-to-end.

### Step 4 — Mark `IN PROGRESS` before the first edit

Update the Master Build Plan so a second session can't pick the same package.

### Step 5 — Implement only the work described

File by file per Files to Create/Modify and Implementation Tasks. Test-first where practical:
encode the package's "done when" as a failing `test_rom.py` check, then implement until it
passes. Never touch a file the package doesn't name; never add an abstraction or refactor it
didn't ask for; respect its explicit out-of-scope statements. SM83 specifics: keep VRAM/visualizer
writes VBlank-gated per the established ISR pattern; keep APU register writes (NR1x-NR5x)
consistent with the frame-sequencer timing the hardware research documents; route new WRAM/SRAM
addresses through the GDS-07 map (a new address not in the map is a data-model change the package
must have named); mind the section budget — `build_rom.py` will assert or overlap silently if data
outgrows its slot, so check the printed layout.

### Step 6 — Run the permanent gates (G5) and the full suite

```
python3 build_rom.py <out.gbc>   # must write 32768 bytes, valid header
python3 test_rom.py              # full suite — every check, not just this package's
```

(If the scripts' hardcoded output paths block a local run, `mkdir -p` the expected directory or
apply the documented workaround in `run-driftune` — do not silently edit paths outside the
package's scope; a genuine toolchain defect is a finding for `00-intake`, not a fix to make here.)

### Step 7 — Fix only defects this package introduced

A failure caused by this package's changes is in scope — fix it. A pre-existing, unrelated
failure is an Outstanding Issue (named, with the failing check), never a rider fix.

### Step 8–9 — Documentation and traceability

Update exactly the locations the package's Documentation Updates names — for this repo that
routinely includes `Claude.md`'s architecture/data-layout/Known Good Behavior sections and
`memory.md`'s quick-reference tables when the change moves an address, adds a tile, or changes
observable behavior. Then update the RTM: every Requirements Covered ID now traces to the real
file(s)/check(s) this run produced, replacing `UNASSIGNED`.

### Step 10–11 — Ledger, summary, stop

Set the package `COMPLETE` (never `VERIFIED`); update downstream packages' blocking notes without
auto-promoting them past the `VERIFIED`-dependency rule. Present the **Implementation Summary**:
Package Implemented · Files Modified · Files Created · Tests Added · Tests Passed (full-suite
counts — never a partial run presented as the whole) · Requirements Implemented · Documentation
Updated · Traceability Updated · Outstanding Issues. **Stop** — no second package, even if one
just became eligible.

## Blocking conditions

Stop immediately — no partial workarounds — when: the package fails eligibility/authorization ·
its cited files/signatures/labels have materially drifted · executing it as written would require
redesigning architecture or changing a requirement · a dependency doesn't exist. Produce a
**Blocking Report** (Reason · Missing dependency · Required action · Recommended owner), set the
package `BLOCKED` with a pointer, and end the run — no consolation package.

## Quality checklist (before presenting `COMPLETE`)

- [ ] Status was `READY`, dependencies `VERIFIED`, authorization explicitly cleared.
- [ ] Every touched file appears in the package's file lists (or is an implied test), and the
      content-peer seam (`tiles.py`/`patterns.py`/`music_data.py` data) was not crossed.
- [ ] ROM builds (32768 bytes, valid header); full `test_rom.py` passes; every Tests to Add item
      exists and passes.
- [ ] Every Requirements Covered ID traces to real files/checks in the RTM.
- [ ] Documentation Updates locations updated (`Claude.md`/`memory.md` included where behavior or
      layout moved); nothing unrelated touched.
- [ ] Master Build Plan shows `COMPLETE`; no downstream package auto-promoted.
- [ ] The Implementation Summary matches the actual diff.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 08 — Package Execution** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md)). Peer: `08-content-authoring` (art/screens/music
data). Upstream: `07-implementation-planning`. Downstream: `09-package-verification` (the only
skill that may write `VERIFIED`).

The Implementation Summary carries the run's factual record; in the same closing message,
additionally state:

1. **Recommendations** — every Outstanding Issue with its suggested owner (a follow-up package
   via `07`, an upstream artifact owner, or the user).
2. **Next step** — after `COMPLETE`, always `09-package-verification` on this same package
   (ideally in a fresh session, for independence) — never another implementation run first;
   after a Blocking Report, whatever its Required action/Recommended owner names.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
