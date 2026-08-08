# ADR-0002 — Defer MBC/Bank-Switching and SRAM/Battery-Save Adoption; Single 32KB Bank Retained

- **Date:** 2026-07-25 · **Status:** Accepted

## Context

MSTR-001 v1.0/v1.1 treated "single 32KB bank, no SRAM save" as settled cart shape. The project
owner corrected this (v1.2 amendment, §8): both were arbitrary decisions mistaken for firm ones,
reopened as genuine research questions rather than foreclosed non-goals. §9 commissioned research
to ground the actual adoption call. That research has since landed:

- [R106](../../research/encyclopedia/R106-mbc-and-sram.md) (extended): MBC5 (or MBC5+RAM+BATTERY
  for save) is the concrete hardware recommendation *if* bank-switching or save is ever adopted;
  PyBoy natively emulates MBC1/3/5 (not a verification blocker).
- [R302](../../research/encyclopedia/R302-python-assembler-codegen-patterns.md) (§8-9 addendum): adopting
  bank-switching is real assembler-architecture work, not a config flag — `gbc_lib.py`'s
  label/fixup system would need a bank component (labels aren't just a byte offset once code can
  live in more than one bank), fixups would need to distinguish safely-callable bank-0 targets
  from switched-bank targets (a new silent-failure class today's `resolve()` cannot detect), and
  `build_rom.py`'s flat sequential-append layout would need genuine per-bank budget tracking.

GDS-00 §"Cart shape and persistence" (v1.2/v1.4) explicitly delegates the actual adopt/not-adopt
decision to this skill, stating the facts now exist but "the decision itself... is still not made
here or by that research." `docs/roadmap/04-release-roadmap.md` named **R4.5 — Cart-Shape
Decision Checkpoint** specifically to make this call before Milestones B-D's cumulative new data
tables (style-region presets, song-form/emotional-state tables) create real ROM-budget pressure —
sequenced right after R4 (just shipped) so a real budget trajectory would be visible first.

**Measured budget trajectory, as of this decision (commit `51e7a5d`, R1+R2+R3+R4 shipped):**
instrumented `build_rom.py`'s own `ROM` object post-build and read `rom.pos` (the highest emitted
address) directly — **3419 of 32768 bytes used (10.4%), 29349 bytes free** — after all 12 shipped
packages, including R4's two new data tables (`CHMIX_MASKS`, `MOTIF_TABLE`). This is the actual
evidence R4.5 was named to wait for, not a projection.

Persistence: no shipped or roadmapped feature through Milestone D commits to persisting any state
across power-off. MSTR-001 C2 names only aspirational examples ("a favorite seed, a style
preference, a collection of discovered pieces") — none has entered the requirements baseline via
`04-requirements-engineering`, and none is named as in-scope for any release through R7.

## Decision

**Do not adopt MBC5 (or any MBC), and do not add SRAM/battery-save capability, at this time.**
Driftune remains a single 32KB bank, no MBC, no SRAM — the cart-type byte and `build_rom.py`'s
flat layout are unchanged. This is a **deferral with a named re-trigger**, not a re-closing of the
question MSTR-001 v1.2 reopened:

- **Re-trigger 1 (ROM budget):** revisit adoption when measured ROM usage (via the same
  `rom.pos`-instrumentation method used here) crosses **75% of the single bank (~24,576 bytes)**,
  or when a specific planned feature's own data-table estimate would cross that threshold on
  arrival — whichever comes first. At 10.4% used after 4 releases' worth of tables, this is not
  close; Milestone C/D's style-region and song-form/emotional-state tables (R219-R221) are
  estimated at low hundreds of bytes each based on their research topics' own described shape
  (parameter-envelope state machines and tiered preset tables, not new code paths), nowhere near
  budget-threatening on current evidence.
- **Re-trigger 2 (save):** revisit adoption the moment any concrete feature requiring persisted
  state is formally proposed and reaches `04-requirements-engineering` with an approved FR — not
  before, since building save infrastructure with no consumer would be speculative complexity
  this project's own "no more, no less" discipline (Claude.md, `08-code-implementation`'s scope
  rules) exists to prevent.

## Consequences

- **Positive:** avoids real, non-trivial assembler-architecture rework (`gbc_lib.py` label/fixup
  bank-awareness, `build_rom.py` per-bank budget tracking, new `test_rom.py` bank-selection state)
  with zero current consumer — no feature today needs more than one bank's worth of ROM or any
  persisted byte. Keeps the toolchain at its proven, fully-tested single-bank shape through
  Milestone B's completion.
- **Negative:** if a save-requiring feature or a large content push (e.g. a much bigger style/
  song-form table set than R219-R221 project) arrives without warning, this decision will need
  revisiting on short notice rather than having pre-built headroom. Judged an acceptable,
  evidence-based risk given the 29KB of measured headroom and the absence of any pending save
  feature — not a silent assumption.
- **Neutral:** MSTR-001 C1/C2 remain correctly framed as "open, not decided" at the vision layer —
  this ADR is the concrete architecture-layer decision GDS-00 delegated to this skill, not a
  reversal of the vision's own reopening. A future adoption remains fully available; nothing here
  forecloses it, per C2's own explicit wording.
- **Traceability:** `strategic-assumptions-register.md` A5 (single-32KB-bank assumption) is
  updated to record this decision as its current disposition — confirmed-with-evidence-and-a-
  named-re-trigger, not merely "not yet re-examined."

## Superseded by

Nothing yet — accepted, not superseded.
