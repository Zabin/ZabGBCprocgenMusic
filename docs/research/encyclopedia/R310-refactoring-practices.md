# R310 — Refactoring Practices: Equivalence Proof, Baseline Capture, Doc-Tree Restructuring

- **Tier:** R300 (tooling & verification) · **Owned by:** `02-research-tooling-and-testing`
- **Status:** ✅ Authored 2026-07-31 (`BL-0076`)
- **Trigger:** `.claude/skills/08-refactoring/SKILL.md` and `07-implementation-planning`'s own
  conventions both cite "grounding: `R307`" for the equivalence-contract discipline refactoring
  packages must carry — but `R307` is `R307-realtime-audio-engine-architecture.md`, an unrelated
  topic; no `R307-refactoring-practices.md` was ever authored, and the citation was dangling.
  This topic supplies the missing grounding under a free ID and both citations are corrected to
  point here.

## 1. Purpose

Ground `08-refactoring`'s equivalence-proof discipline — the property that separates a legitimate
refactor from a silent behavior change — in both established software-engineering practice and
this project's own concrete toolchain, so a refactoring package's claims are checkable rather than
asserted.

## 2. Scope

What "equivalent" means for (a) a behavior-preserving change to a repo-root `.py` file and (b) a
meaning-preserving restructuring of a `docs/` file; how to capture a baseline before the first
edit; how to structure the refactor itself; how the proof is produced and checked afterward. Not
in scope: bug fixes, feature additions, or architecture changes made under cover of a refactor —
`08-refactoring`'s own rules already forbid these, and this topic does not relitigate that boundary.

## 3. Concepts

- **Behavior-preservation is the defining property, not an incidental one.** Martin Fowler's
  canonical definition: refactoring is "a change made to the internal structure of software to
  make it easier to understand and cheaper to modify without changing its observable behavior"
  [Fowler, *Refactoring: Improving the Design of Existing Code*, 2nd ed., Introduction]. The
  discipline that makes this safe in practice is running the test suite before and after every
  small step, never batching multiple structural changes without a green run between them — the
  same "small reversible steps" language `08-refactoring`'s own `SKILL.md` already uses,
  independently arrived at and confirmed here as standard practice rather than a house rule.
- **Golden-master / characterization testing** is the general technique for proving a black-box
  transformation preserves output: capture the system's real output against a fixed input set
  before changing anything, then diff the same inputs' output after [Feathers, *Working
  Effectively with Legacy Code*, ch. 13, "I Don't Understand the Code Well Enough to Change It" —
  the characterization-test pattern]. **This project's own equivalence proof is a golden-master
  test at the strongest possible grain**: the built ROM is a single deterministic byte sequence
  (`build_rom.py` takes no random input, per `R213`'s confirmation that `LFSR_SEED` is a fixed
  constant precisely so builds and test runs stay reproducible), so "byte-identical ROM" is not an
  approximation of behavioral equivalence — for this toolchain, it *is* behavioral equivalence,
  strictly stronger than the sampled-output-diffing golden-master technique usually requires,
  because there is no sampling: every possible input trace is covered by construction.
- **Baseline capture, concretely, in this toolchain.** `08-refactoring`'s own `SKILL.md` (Step 3)
  already specifies exactly what a baseline is here: the built ROM's SHA-256 hash, the full
  `test_rom.py` output (check count and every check name), and — for doc-scoped work — the
  inventory of every status token/ID/link the package's scope touches. This is the concrete,
  toolchain-specific instance of the golden-master principle above: hash the deterministic
  artifact, snapshot the test names (not just the pass count, since a suite that still passes
  N checks after silently dropping and adding a different N checks is not equivalent), snapshot
  the doc inventory (since doc equivalence has no single hash — meaning-preservation is checked
  field-by-field).
- **Equivalence contract, the two shapes.** Default: **byte-identical ROM**, verified by comparing
  the pre- and post-refactor SHA-256 hashes — the strongest, cheapest-to-check proof available,
  and the right default because any code restructuring that changes ROM bytes has changed *some*
  observable thing (a label address, an instruction encoding, a data byte) even if `test_rom.py`
  doesn't happen to assert on it. **Non-default**: an enumerated list of predicted byte deltas,
  each with its own justification (e.g. "this label moved 3 bytes because an intermediate NOP was
  removed, and nothing reads its absolute address, only via the assembler's own symbolic
  resolution" — `R302`'s label/fixup mechanism is what makes this kind of claim checkable rather
  than hand-waved). A package that cannot commit to one of these two shapes is not a refactor.
- **Doc-tree equivalence has no single hash, so it is checked as an inventory.** Meaning-preserving
  restructuring (archive-splitting a growing log, compacting a router doc to current-state-plus-
  pointer, per `08-refactoring`'s own Step 4a patterns) must preserve every `BL-`/`FR-`/`IP-`/etc.
  status token, every ID, and every link, even as file boundaries move. The check is row-for-row
  or byte-for-byte diff against the pre-refactor inventory (see `08-refactoring`'s own SKILL.md),
  not a human read-through — a read-through is exactly the kind of check that misses a silently
  dropped row in a 200-row table.
- **Link integrity is a real, cheap, previously-unchecked class of defect on this project.** A
  2026-07-31 documentation review found 27 broken internal links across 6 documents, none from any
  refactor, all from ordinary authoring drift (missing path prefixes, a filename-case mismatch) —
  filed as `BL-0077`. This confirms link integrity belongs in every doc-refactor's own equivalence
  check, not only as a general documentation-hygiene aspiration: it is a defect class this project
  has already produced, cheaply detectable, and exactly the kind of thing a restructuring pass can
  introduce at scale if unchecked.
- **Quiescence and green-baseline preconditions are refactoring-specific, not generic testing
  advice.** `08-refactoring`'s Eligibility checks 3-4 (no other package mid-flight touching the
  same files; the suite is green *before* the first edit) exist because a refactor's proof is a
  *before/after diff* — if the "before" state is already red, or another package is concurrently
  changing the same files, there is no stable "before" to diff against, and the diff proves
  nothing. This is the golden-master principle's precondition made explicit: characterization
  testing requires a trustworthy baseline to characterize.

### Sources
- Fowler, Martin. *Refactoring: Improving the Design of Existing Code*, 2nd edition — the
  canonical definition of refactoring as behavior-preserving structural change, and the
  small-steps/tests-green discipline. [refactoring.com](https://refactoring.com/) (publisher site,
  book's own framing reproduced there — needs fetch-verification if a live citation is required
  beyond the well-established published definition).
- Feathers, Michael. *Working Effectively with Legacy Code* — the characterization/golden-master
  testing pattern for proving output-equivalence of an opaque transformation.
  [Referenced via standard software-engineering literature; needs fetch-verification for a live
  URL.]
- `.claude/skills/08-refactoring/SKILL.md` — this project's own concrete baseline-capture and
  equivalence-contract workflow, Tier-A source for "what this toolchain's refactoring discipline
  actually requires."
- `R213` — confirms `LFSR_SEED`'s fixed-constant choice, the fact that makes `build_rom.py`'s
  output fully deterministic and therefore makes byte-identical-ROM a strict equivalence proof,
  not an approximation.
- `R302` — the label/fixup resolution mechanism that makes an enumerated predicted-delta claim
  checkable rather than asserted.
- `BL-0077` (2026-07-31 documentation review) — the concrete 27-broken-link finding grounding the
  link-integrity concept above in this project's own real defect history, not a hypothetical.

## 4. Operational Context

`08-refactoring`'s `SKILL.md` already implements every practice this topic grounds: Step 3
(baseline capture: ROM SHA-256 + full `test_rom.py` output), the Eligibility checklist (quiescence,
green baseline, an explicit equivalence contract per package), and Step 4a's named patterns for
growing living documents (archive-split for logs, compact-to-current-plus-pointer for router
docs). No drift found between this topic and the shipped skill definition — this topic supplies
the grounding the skill's citation was pointing at but missing, not a new practice to adopt.

## 5. Implementation Guidance

- **Always default to "byte-identical ROM" as the equivalence contract** in a code-scoped
  `IP-8xx0` package; only switch to an enumerated predicted-delta list when the restructuring
  provably cannot avoid moving bytes (e.g. removing dead code shifts every subsequent label), and
  justify every delta against `R302`'s label/fixup mechanism, not by assertion.
- **Capture the baseline exactly as `08-refactoring`'s Step 3 specifies** — the ROM's SHA-256 (not
  just its size; two different ROMs can both be 32768 bytes), and the full set of `test_rom.py`
  check *names*, not merely the PASS count, before the first edit.
- **For a doc-scoped refactor, snapshot the inventory first**: every status token, ID, and link in
  the affected files, so the post-refactor diff is a real check rather than a read-through. Treat
  a broken link introduced by the refactor as a hard equivalence-proof failure, not a cosmetic
  note — `BL-0077` shows this project has already produced this defect class without a refactor
  even being involved.
- **Never let a refactoring package batch multiple structural changes without a green
  `test_rom.py` run between them** — Fowler's small-steps discipline is not a stylistic
  preference here; it is what keeps a failure attributable to a specific step rather than an
  undiagnosable accumulation.
- **If a refactor reveals a bug, file it via `00-intake` and do not fix it in the same package** —
  fixing it destroys the equivalence proof (the "before" and "after" would then differ by more
  than structure), exactly as `08-refactoring`'s own SKILL.md already states; this topic confirms
  that rule is standard practice, not an idiosyncratic restriction.

## 6. Feature Mapping

`08-refactoring`'s own workflow (Steps 1-3, Eligibility checks 3-5, the Step 4a archive/compact
patterns) — no `IP-8xx0` package has yet been authored or built against this grounding (`BL-0064`/
`BL-0065` are the current refactoring candidates, both still unplanned as of this writing).

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⚠️ **PARTIALLY TRACED.** This topic grounds a **skill definition** (`08-refactoring`'s and
`07-implementation-planning`'s own equivalence-contract conventions) rather than any shipped
`ADS`/`FS`/`IP` — it corrects a dangling citation those two skill files already carried, and both
now cite `R310` in place of the broken `R307` reference. No refactoring package has been built
against it yet: `BL-0064`/`BL-0065` are the two candidates on record, both still unplanned. This is
a legitimate, narrower instance of the "grounds tooling/process rather than a feature" exception
shape `R301`/`R305`/`R306` occupy elsewhere in this tier — recorded honestly as partial rather than
claimed complete on the strength of the citation fix alone.

## 7. Related Topics

R302 (the label/fixup mechanism that makes an enumerated-delta equivalence claim checkable), R213
(the fixed-seed determinism that makes byte-identical-ROM a strict proof), R306 (toolchain
portability — the sibling grounding for how this project's build/test pipeline actually runs).
