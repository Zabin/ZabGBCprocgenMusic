# Product Roadmap 08 — Development Strategy

- **Grounded in:** the existing pipeline's own governance (`.claude/skills/README.md` G1-G5),
  `docs/pipeline/pipeline-journal.md`'s established practice, `04-release-roadmap.md`
- **Status:** ✅ Authored 2026-07-22

This roadmap does not introduce a new development philosophy — it operationalizes the pipeline's
existing, already-proven discipline (7 Foundation packages + 2 sound-design packages shipped this
way) at the scale this longer roadmap now demands.

## Iterative development

One release = one or a small handful of implementation packages against one coherent Definition of
Done (`07-implementation-planning`'s own right-sizing rule). No release in `04-release-roadmap.md`
exceeds a "size M" feature grouping (`06-feature-specifications.md`'s own sizing column) —
consistent with the guiding principle that complex capabilities mature over multiple releases
rather than appearing all at once (e.g. Style Engine: R5 ships 3 presets, not a full genre
taxonomy; Evolution Engine: R6 ships one song-form arc mechanism, R8 extends it to blending later).

## Risk reduction

- **Sequence the known-broken fix first** (R3, `BL-0019`/`BL-0017`) before building anything new on
  top of it — a broken control or dead detection path compounds if new capability is layered over
  it instead of under a fix.
- **Parallelize independent streams** (Milestone B vs. C, per `03-capability-dependency-graph.md`)
  so a blocker in one (e.g. B's standing G3 gate) does not stall the other.
- **Gate genuinely undecided architecture questions explicitly** (R11's cart-shape decision, R9's
  visual-evolution research prerequisite) rather than letting a release quietly assume an answer.
- **New arithmetic/algorithmic risk gets flagged and pre-mitigated at planning time**, matching the
  pattern that already worked for `IP-1061` (vibrato's carry-safe-arithmetic risk was named in the
  package doc *before* implementation, not discovered during it) — `07-implementation-planning`
  should apply the same discipline to R6's state-machine/bad-zone interaction and R8's
  interpolation-coherence risk.

## Continuous integration

Every package rebuilds the full ROM and runs the full `test_rom.py` suite before being called
`COMPLETE` — the existing, unbroken practice (65/65 at last count, growing every release). This
roadmap adds no new CI mechanism; it extends the existing one's scope as new capabilities land.

## Continuous testing

- **Automated**: every `RM-xxxx` feature's acceptance criteria names a specific, headlessly
  assertable behavior — no feature in `06-feature-specifications.md` lacks one.
- **Content review** (musical/visual judgment, not just register assertions): explicitly named
  wherever automation alone can't judge quality — R5's style presets, R8's blend coherence, R9's
  visual response — matching the existing `09-content-review` skill's own scope, not a new
  process.
- **Stress testing**: every release that touches per-frame timing (R3's threshold fix, R6's state
  machine, R9's visual updates) repeats the existing multi-thousand-frame headless stress-run
  practice already established since `IP-0007`.

## Architecture evolution

`03-architecture-design-synthesis` remains the sole owner of every genuinely new mechanism this
roadmap names (Scheme E's design, the song-form state machine's precedence rule against bad-zone
recovery, cart-shape adoption) — this roadmap sequences *when* those decisions get made, never
*what* they resolve to. No release in this roadmap should be read as having pre-decided an
architecture question its own entry names as open.

## Refactoring strategy

Two known refactoring-scale needs are already on record and should ride whichever release first
needs them, rather than being scheduled standalone: `BL-0023` (a `requirements.txt` for the
`pyboy` dependency — near-zero risk, should land before Milestone B's fresh-session verification
work multiplies the friction it already causes) and the bank-switching assembler work R302 §8-9
sized honestly as "real assembler-architecture work" — **only incurred if R11's cart-shape decision
is GO**, never spec'd speculatively ahead of that decision.

## Regression prevention

Every release's completion criteria includes "full-suite regression" (see `04-release-roadmap.md`)
— no release is considered done if it silently breaks an earlier one's assertions. The
`test_rom.py` suite's own growth (32 → 60 → 65 checks across the shipped history) is the project's
own evidence this discipline holds in practice, not just in principle.

## Hardware testing cadence

MSTR-001 §4 names real-hardware certification a non-goal — emulator verification (PyBoy) is the
release gate, not hardware. That said, this roadmap recommends a **non-blocking hardware validation
checkpoint at the end of each milestone** (not each release) — flash the current ROM to real GBC
hardware or a cycle-accurate second emulator (R309: SameBoy/BGB, already researched) and confirm
no PyBoy-specific timing divergence has crept in (the one open, low-severity finding on record,
`BL-0015`, is exactly the kind of thing this cadence would catch earlier). This is a validation
practice, never a release-blocking gate — consistent with MSTR-001's own non-goal.

## Performance validation

CAP-19 (Performance & Budget Management) is cross-cutting, not a single release — but R12
formalizes it into a dedicated audit pass before RC. Between milestones, every release that adds
per-frame logic (R4's scheme dispatch, R6's state machine, R9's visual updates) should self-report
its cycle-cost delta in its own package doc's Risks section, the same discipline `IP-1061`'s
package doc already modeled for vibrato's arithmetic.
