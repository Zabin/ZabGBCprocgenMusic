---
name: 09-content-review
description: Qualitatively review shipped content against its spec — drive the built ROM in the emulator, screenshot every affected visualizer pattern/state, capture the sound-register (NR1x-NR5x) sequences produced, and judge visualizer tile-art readability, palette use, scene composition, generation musicality (scale/rhythm/tempo fidelity to the spec, bad-zone recoverability) — producing a Content Review report under docs/reviews/. The stage-09 peer of 09-package-verification: verification audits the ledger claims mechanically; this skill judges whether the rendered/sounded result actually satisfies the design intent the FS and R2xx research describe. Use after ANY stage-08 package (08-content-authoring or 08-code-implementation) changes what's rendered on the visualizer or what the engine sounds like — not only content-authoring packages; a bad-zone indicator or status overlay authored inside a code package still needs this review — or when asked to "review the new visualizer pattern/scale set/preset," "check the visualizer art," or "does the generated music actually sound right." Read-only with respect to code and content — findings route back to whichever stage-08 peer owns the reviewed content (or upstream); it never fixes anything.
---

# Content Review

Judges **rendered/sounded content against design intent**. `09-package-verification` proves the
package did what its checklist says; this peer proves the result *reads and sounds* the way the
spec and the R200-tier design research say it should. It observes and reports; it changes nothing
but its own report.

## Scope selection

**Trigger on the change, not on which stage-08 peer made it.** One package's rendered-visualizer
or sounded-music change (after its `08-content-authoring` *or* `08-code-implementation` run — a
bad-zone status indicator or a new sound authored inside a code package is exactly as much this
skill's business as new tile art or a new scale table), one feature's content surface, or an
explicitly named set of patterns/scales/presets. The reviewed content should already be
`COMPLETE` (and ideally `VERIFIED`) — if the mechanical verification hasn't run, say so; this
review doesn't substitute for it. Before skipping a package because it "isn't a content package,"
check whether it changed what's on the visualizer or what the engine produces at all —
`09-package-verification`'s own checklist confirms a mechanism (does a button press transition
engine state correctly); it does not confirm what the visualizer actually *shows* or the engine
actually *sounds like* to a listener, so a code package that adds/changes visualizer content or
generated output is not "covered" just because its VR passed.

## What to check (the review dimensions)

1. **Visual fidelity** — build the ROM and drive every affected visualizer pattern/state via
   `run-driftune`, capturing screenshots (each generation mode, the bad-zone indicator state, the
   post-reset state as applicable). Do the tiles render as the spec describes? Bitplanes correct
   (no washed-out or inverted art)? Palette assignments per `memory.md`'s tables?
2. **Readability & composition** — against R205/R208 (once authored) and the FS: does the
   visualizer read at a glance as responding to the music — tempo, voice activity, register state
   legibly distinct from each other? Is the bad-zone state visually distinguishable from a good
   state?
3. **Musical correctness** — drive the ROM and capture the sound-register (NR1x-NR5x) sequences
   produced for each reviewed generation mode/preset; compare against the spec's notation (scale/
   mode, tempo, rhythm template, channel assignment). Audible check via emulator where practical,
   register-level check via `music_data.py`/`music_engine.py` otherwise.
4. **Bad-zone behavior** — if the reviewed content touches bad-zone detection or the Select reset:
   drive the engine into the bad zone (per the spec's trigger conditions), confirm the indicator
   and the audible degradation actually appear, then confirm Select produces the documented good
   starting state — not just that a state-machine transition fired, but that the resulting
   register writes are actually the good-state values the spec names.
5. **Documentation coherence** — `memory.md`'s tile/palette/scale quick-refs and `Claude.md`'s
   relevant sections reflect the shipped content; the FS's acceptance criteria all have evidence.

## Output

**`docs/reviews/content-review-<scope>.md`**: scope + package list (with the commit hash
reviewed), the screenshots and sound-register captures taken (paths), evidence per dimension, and
findings as one row each — `Finding | Artifacts involved | Description | Severity | Recommended
owner` — using the project's Critical/High/Medium/Low scale. A clean review states what was
actually exercised to earn the "clean." Update `ROADMAP.md`'s reviews row if it tracks review
documents.

## Quality gate

- [ ] The ROM reviewed was rebuilt from the current tree (commit hash recorded).
- [ ] Every affected pattern/state was actually driven and screenshotted/register-captured — not
      judged from source.
- [ ] All five dimensions exercised; a dimension with nothing to report says what was checked.
- [ ] Every finding has a severity and a concrete recommended owner; none fixed in-pass.
- [ ] Nothing but the report (and tracker rows) was written.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 09 — Content Review**, peer of `09-package-verification` (see
[`.claude/skills/README.md`](../README.md)). Upstream: whichever stage-08 peer authored the
reviewed visualizer/audio content — `08-content-authoring` or `08-code-implementation`.
Downstream: `10-integration-review`, or back to that same stage-08 peer with findings.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the report written (path), scope, headline result (clean / N findings by
   severity), screenshots/register captures taken.
2. **Recommendations** — each finding with its owner: content defects → whichever stage-08 peer
   authored the reviewed content (`08-content-authoring` or `08-code-implementation` — via a `07`
   remediation package if the fix isn't covered by an open package); spec-intent ambiguity →
   `06-feature-specification`; design-convention gaps → `02-research-game-design`.
3. **Next step** — clean: continue the tranche (next stage-08 package, or
   `10-integration-review` if the tranche is done); findings: route them per above and name the
   first step.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
