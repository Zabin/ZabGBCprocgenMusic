# The documentation-driven-development skill pipeline (Driftune)

The numbered skills in this directory form one pipeline. **The number is the run order**: a
skill's inputs are produced by lower-numbered stages, and its output feeds the next higher stage.
Skills sharing a number (the three `02-research-*` skills; the three `08-*` peers; the two `09-*`
peers) are peers at the same stage — run whichever owns the gap; they have no ordering among
themselves. Unnumbered skills (`run-driftune`) are utilities outside the pipeline.

Every pipeline skill ends **every** run with a mandatory chat summary: what changed,
recommendations (findings routed to their owning skill), and an explicit **Next step** naming the
skill to run next. The default way to drive the pipeline is `00-pipeline-manager`: it keeps a
persistent journal at `docs/pipeline/pipeline-journal.md` (position + append-only run log,
reconciled against the tree's real ledgers every run — the tree always wins), executes the next
step by invoking the owning skill, and stops at every human gate. Running a stage skill directly
is always legitimate too — the manager's next `sync` picks up the change.

**Nothing surfaced is forgotten:** every finding/recommendation an invoked skill reports is
harvested by the manager into `docs/pipeline/backlog.md` at the end of the run, and every open
backlog entry is triaged (given an explicit disposition — scheduled / deferred-with-trigger /
needs-user / rejected) at the start of the next run, before the next step is chosen. New work
enters the same backlog through `00-intake` (features, bugs, observations — classified, deduped,
and routed to the pipeline stage where they belong), never by side-channel implementation.

**First increment (bootstrap):** Driftune has no shipped ROM yet — there is nothing to baseline.
The pipeline's first pass through stages 01–07 is therefore a genuine **from-scratch increment**:
`01-vision` is authored from the user's actual stated intent for the project (a standalone GBC
ROM whose purpose is real-time procedurally-generated chiptune, with a generative visualizer and
D-pad/button-driven music parameters), not derived from any existing code or shipped artifact —
because none exists. Every stage after it works forward from that vision the normal way: research
grounds it, architecture synthesizes it, requirements make it traceable, and so on down to code.
There is no as-built carve-out and no `docs/pipeline/BOOTSTRAP.md` special run order for this
project — G3's package-authorization rule applies from the very first package with no bootstrap
exception (see `00-pipeline-manager`). New scope beyond the initial vision enters afterward via
`00-intake`, exactly as it would for any later increment.

## Stages

| # | Skill | Produces | Where |
|---|---|---|---|
| 00 | `00-pipeline-manager` · `00-intake` | Manager: pipeline journal (position + run log), backlog harvest + triage, one-step-per-run execution of the next stage (`status`/`triage`/`log`/`sync`/`run` modes). Intake: files new features/bugs/observations into the backlog with a recommended entry stage. | `docs/pipeline/`, chat |
| 01 | `01-vision` | Program vision (MSTR-001), GDS-00 Vision, strategic assumptions register | `docs/master/`, `docs/architecture/` |
| 02 | `02-research-gbc-hardware` · `02-research-game-design` · `02-research-tooling-and-testing` | Research encyclopedia tiers R100 (GBC hardware/SM83, esp. the APU) / R200 (procedural-music & generative-visual design, filed under the `02-research-game-design` skill name) / R300 (tooling, emulation & verification) | `docs/research/` |
| 03 | `03-architecture-design-synthesis` | GDS-01…10 ladder (Concept of Operation, System Context, Architecture, Domain Model, FR/NFR levels, Data Model, Presentation Architecture, Interface Spec, RTM level), ADS-xxx, ADRs | `docs/architecture/` |
| 04 | `04-requirements-engineering` | FR-xxxx, NFR-xxxx, Requirements Review, Requirements Traceability Matrix | `docs/requirements/` |
| 05 | `05-feature-decomposition` | Release Plan, Epic Catalog, Feature Catalog (FEAT-xxxx rows), Feature Dependency Graph, Feature Review | `docs/feature-planning/` |
| 06 | `06-feature-specification` | Feature Specifications (FS-xxx, 20-field template) | `docs/features/` |
| 07 | `07-implementation-planning` | Technical Work Breakdown, Implementation Packages (IP-xxxx, 14-field template), Master Build Plan | `docs/implementation/` |
| 08 | `08-code-implementation` · `08-content-authoring` · `08-refactoring` | Code: source + tests + docs + traceability for exactly one package (status → `COMPLETE`). Content peer: visualizer tile/palette art and curated musical building blocks (the data halves of `tiles.py`/`patterns.py`/`music_data.py`) + their verification tests. Refactoring peer: behavior-preserving code restructuring / meaning-preserving doc restructuring with equivalence evidence (byte-identical ROM by default), via `IP-8xx0` packages only. | repo-root `*.py`, `docs/`, ledgers |
| 09 | `09-package-verification` · `09-content-review` | Verification Report (VR-xxxx); the **only** skill that writes `VERIFIED`. Content peer: Content Review report (visual/audio/layout correctness vs. spec) under `docs/reviews/`. | `docs/implementation/verification/`, `docs/reviews/` |
| 10 | `10-integration-review` | Integration Report for an epic/release's verified package set | `docs/reviews/` |
| 11 | `11-release-readiness` | Release Assessment (GO/NO-GO) + baseline update on GO | `docs/reviews/`, trackers |

## Iteration loops

The pipeline is iterative, not a one-way waterfall — but every loop re-enters at a numbered stage
and flows forward from there:

- **Per feature:** 06 → 07 → (08 → 09 per package) — repeated for each feature in a release bucket.
- **Per package:** 08 → 09; a `RETURNED` verification loops back to 08 on the same package.
- **Per content artifact:** `08-content-authoring` → `09-content-review`; findings loop back to 08.
- **Per refactor:** `refactor`-type backlog entry (via `00-intake` or manager harvest) → 07 authors
  an `IP-8xx0` with an equivalence contract → `08-refactoring` → `09-package-verification`.
  Refactoring runs only under the explicit conditions in `00-pipeline-manager` (quiescent tree,
  green G5 gates, per-package G3 authorization with no carve-out) and never mixes with feature or
  fix work.
- **Per release:** 10 → 11; integration findings loop back through 07 → 08 → 09 before 10 re-runs.
- **Upstream findings never get fixed downstream.** A requirements conflict found at stage 05 goes
  back to 04; an architecture gap found at 06 goes back to 03; a domain-knowledge gap anywhere
  goes to the owning 02 skill. Each skill's summary routes its findings to the owning stage.

## Question ordering (tier precedence)

Open questions and human gates form an altitude order, not a flat queue: a decision at a higher
stage can reshape or moot a question at every stage below it, but never the reverse. When more
than one stage has a ripe open question (a `NEEDS-USER` backlog entry, an unresolved Open
Question, a pending gate), `00-pipeline-manager` surfaces the **highest tier first, one tier per
run**, rather than batching everything the tree happens to have open:

`01 Vision` > `03 Architecture` > `04 Requirements` > `05 Feature Decomposition` >
`06 Feature Specification` > `07 Implementation Planning` > `08 Implementation` >
`09 Verification` / `10 Integration` / `11 Release` (peers, ordered by what they review, not by
further precedence among themselves). `02 Research` grounds `01`/`03` and is only pulled in when
the specific higher-tier question needs a domain fact — it has no precedence slot of its own.

A lower-tier question that genuinely depends on a still-open higher-tier one is held back (not
asked) until the higher-tier answer lands, then re-derived rather than replayed verbatim — the
higher answer may have already resolved it. Questions from unrelated parts of the tree at
different tiers don't wait on each other and can still be asked in the same round-trip. See
`00-pipeline-manager`'s own workflow for the full mechanics (how entries get held, annotated, and
re-checked).

## Hard rules the stages share (interim governance — formalized later as MSTR-006)

Until `01-vision`/`03-architecture-design-synthesis` author the `docs/master/` MSTR corpus, the
rules below are the binding governance text. Skills cite them as **G1–G5**.

- **G1 — Write scope.** Each skill writes **only** its own output scope and reads everything
  upstream as authoritative. No skill before 08 writes production code; no skill after 08 fixes
  code (findings route back). Within stage 08, the peers split the write surface: only
  `08-code-implementation` writes engine logic and build machinery (`music_engine.py`,
  `visuals.py`, `input_map.py`, `gbc_lib.py`, `build_rom.py`, `test_rom.py`); `08-content-authoring`
  writes only the data halves of `tiles.py`/`patterns.py`/`music_data.py` and their verification
  tests; `08-refactoring` writes exactly the files its `IP-8xx0` package names (crossing the
  code/content seam is permitted there only because its equivalence proof — byte-identical ROM or
  enumerated predicted deltas — is stronger than the seam), plus meaning-preserving doc
  restructuring.
- **G2 — Status honesty.** Statuses are honest ledgers. The vocabulary is exactly
  `NOT STARTED / READY / IN PROGRESS / BLOCKED / COMPLETE / VERIFIED`. Stage 08 may write
  `IN PROGRESS`/`COMPLETE`/`BLOCKED`; only stage 09 writes `VERIFIED`; only the user's explicit GO
  lets 11 flip the baseline.
- **G3 — Package authorization.** A fully-specified package is **not** authorization to build it —
  the user grants that explicitly, per package. There is no bootstrap carve-out for this project
  (nothing is as-built yet): every package, from the very first, waits for the user's explicit
  go-ahead before `08-code-implementation`/`08-content-authoring`/`08-refactoring` may build it.
- **G4 — Release GO.** The GO/NO-GO recommendation at stage 11 is advisory; the user makes the
  release call before any baseline record flips.
- **G5 — Permanent gates.** After every stage-08 run, the ROM must build
  (`python3 build_rom.py <path>` → 32768 bytes, valid header) and the full ROM test suite
  (`python3 test_rom.py`) must pass. A package that breaks either is not `COMPLETE`, regardless of
  what its own new tests show. See `run-driftune` for the exact commands.
