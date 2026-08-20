# Release Plan — origin to a releasable v1.0

- **Owned by:** `05-feature-decomposition` · **Status:** ✅ Authored 2026-08-07
- **Authored to close:** `BL-0095`'s substantive half. This file is named as an authoritative
  ledger by `00-pipeline-manager`'s own Step 1 reconciliation, but had **never existed** in this
  repository's history (confirmed across all 6 refs at tip, every commit ever made on any ref, and
  all reachable objects). That reconciliation input has been silently inert since the project
  began; authoring this file makes it real.
- **Derived from:** [`docs/roadmap/04-release-roadmap.md`](../roadmap/04-release-roadmap.md)
  (R0-R13 sequence) · [`01-feature-catalog.md`](01-feature-catalog.md) (FEAT-1000…1120) ·
  [`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
  (68 baselined rows) · [`docs/roadmap/09-release-exit-criteria.md`](../roadmap/09-release-exit-criteria.md)
  (the quality bar every release must clear) · [`docs/roadmap/05-milestone-definitions.md`](../roadmap/05-milestone-definitions.md)
  (Milestones A-F) · [`docs/pipeline/backlog.md`](../pipeline/backlog.md) (49 open items) ·
  [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md).

---

## §0 Which document owns what

Three documents describe "what ships when," and they are **not** redundant. Getting this wrong is
the main way this file could do harm, so it is stated first:

| Document | Owns | Does not own |
|---|---|---|
| [`docs/roadmap/04-release-roadmap.md`](../roadmap/04-release-roadmap.md) | The **release vocabulary and sequence** (R0-R13), each release's purpose, capabilities, testing goals and dependency. The whole tree cites these R-numbers. | Feature-level or backlog-level assignment. |
| **This file** | The **feature-planning-layer view**: which `FEAT-xxxx` and which `BL-xxxx` land in which release, entry/exit criteria per release, the critical path, and what "releasable v1.0" concretely means. | The R-numbering itself. It is consumed here, never redefined. |
| [`01-feature-catalog.md`](01-feature-catalog.md) | The `FEAT-xxxx` rows themselves — purpose, scope, included requirements, dependencies. | Scheduling. |

**This plan introduces no new release identifiers except one**, `R12.5`, proposed in §2 and
flagged in §9 for the roadmap owner's adoption. Everything else reuses R0-R13 verbatim.

---

## §0.5 Decisions on record (2026-08-07)

Four open questions were put to the user directly and answered. This plan is written to them; they
are not assumptions.

| Question | Decision | Effect on this plan |
|---|---|---|
| **v1.0 scope** | **R0-R8 + R12 + R12.5 + R13.** R9 and R10 move to **v1.1**. | Confirms §5's recommended scope. **De-escalates `BL-0086`** from release-blocking to v1.1 cleanup. |
| **Product name** (`BL-0007`) | **Keep "Driftune"** as final. | `BL-0007` `DONE`. No rename anywhere; header/build/docs already use it. |
| **Hardware validation** (`BL-0058`) | **Ship emulator-validated, stated plainly; add a SameBoy/BGB mode-accurate cross-check at R13.** Real silicon → v1.1 goal. | `BL-0058` off `NEEDS-USER`; R13 gains one concrete task. Not a v1.0 blocker. |
| **`08-content-authoring`'s broken scope** (`BL-0089`) | **Create the three modules** — extract data into real `tiles.py`/`patterns.py`/`music_data.py`, restoring the decomposition `GDS-03`/`GDS-09` always described. | **Adds a refactoring package to the critical path before R12.5** (see §2.5). Chosen over repointing or retiring the skill. |

**No `NEEDS-USER` backlog items remain open.** Every remaining open item is `SCHEDULED` to a named
release or a named ride.

---

## §1 The release ladder

State as of 2026-08-07. "Shipped" means a `11-release-readiness` GO is on record.

| Release | Milestone | State | Gate |
|---|---|---|---|
| R0 Skeleton | A | ✅ Shipped, `VERIFIED` | — |
| R1 Foundation | A | ✅ Shipped, GO 2026-07-25 | — |
| R2 Sound Design Layer | A | ✅ Shipped, GO 2026-07-25 | — |
| R3 Integrity Remediation | B | ✅ Shipped, GO 2026-07-25 | — |
| R4 Multi-Scheme Foundation | B | ✅ Shipped, GO 2026-07-25 | — |
| R4.5 Cart-Shape Checkpoint | B | ✅ **Decided** — `ADR-0002`, single-bank retained, MBC/SRAM declined | — |
| R5 Genre-Aware Style Presets | B | ✅ Shipped, GO 2026-07-26 | — |
| R6 Song-Form Engine | C | ✅ Shipped, GO 2026-07-31 (+ `IP-1090`, `IP-1110`) | — |
| **R7 Emotional/Energy Layer** | C | 🟡 **`IP-1120` `COMPLETE`, unverified** | Verification queue (§2.1) |
| **R8 Genre Blending** | D | ⬜ **Unstarted, fully unblocked** | none |
| **R9 Visual Evolution & A-V Sync** | E | 🟡 Designed (`ADS-106`, `FR-1430`-`1460`) — **v1.1** (scope decision 2026-08-07) | `BL-0086`, now v1.1 cleanup |
| R10 Interactive Control Expansion | E | ⬜ **v1.1** (scope decision 2026-08-07) | R8 |
| R11 Persistence Layer | F | ❌ **Struck** — R4.5 decided NO-GO | — (closed) |
| R12 Performance & ROM-Budget | F | ⬜ Not started | all prior |
| **R12.5 Content & Musical Quality** | F | ⬜ **Proposed here** (§2.5) | R12 |
| R13 Release Candidate | F | ⬜ Not started | R12.5 |

**R11 is struck, not deferred.** Its own entry states: *"R4.5's decision must have been GO… If
R4.5 was NO-GO, this release is struck from the roadmap entirely, not deferred indefinitely — an
explicit no is a valid outcome."* `ADR-0002` decided NO-GO. Recording it as struck here so no
future pass treats it as pending work.

---

## §2 Per-release detail (forward releases only)

### §2.1 R7 — Emotional/Energy Layer · *finish the verification queue*

**Entry:** met (`IP-1120` `COMPLETE`, 142/142, ROM byte-identical to a fresh build).

The only work left is **not a decision and not new code**: four packages are `COMPLETE` and await
`09-package-verification`, which structurally cannot verify a package built in its own session.

| Package | Awaiting | Closes |
|---|---|---|
| `IP-9030` VBlank budget assertion | fresh-session `09` | `BL-0069` |
| `IP-8010` remove vestigial patch-point dicts | fresh-session `09` | `BL-0064` |
| `IP-8020` shared WRAM constants module | fresh-session `09` | `BL-0065` |
| `IP-1120` emotional/energy layer | fresh-session `09` | — (R7 itself) |

**Exit:** all four `VERIFIED`; `10-integration-review` clean at 20-package scope; R7 GO.
R7's own roadmap entry notes it *"should ship bundled with R6 or R9 rather than standalone, since
it alone produces no audible/visible change."* R6 already shipped, so **bundle R7's GO with R8's**
rather than calling a GO for a release with nothing to hear.

**Rides along:** `BL-0088` (T20 dead code), `BL-0013` (IP-0004 doc deviation, `IN PIPELINE`).

### §2.2 R8 — Genre Blending · *the only unblocked forward release*

**Entry:** met. Dependencies R5 + R6 both shipped. **Needs nothing from the user.**

Interpolate between R5's `STYLE_TABLE` regions using R6's drift mechanism — a session audibly
drifts from one genre reference toward another instead of hard-cutting. Full pipeline needed:
`03` (ADS) → `04` (FR/NFR) → `05` (FEAT-1130) → `06` (FS-113) → `07` (IP-1130) → **G3** → `08` → `09`.

**Exit:** at least one blend pair `VERIFIED`; no regression to hard-cut style switching.
Its own roadmap entry flags the real risk: *"parameter interpolation producing an audibly
'in-between-and-bad' state… needs `09-content-review`, not just automated assertion."* That is a
**hard dependency on R12.5's machinery** (§2.5) — R8 is the first release whose success cannot be
established by assertion alone.

**Rides along:** `BL-0040`, `BL-0041`, `BL-0048`, `BL-0032`, `BL-0033`, `BL-0039`, `BL-0042`,
`BL-0043` — the whole style/scheme-coverage cluster is R8's natural home, since R8 is the release
that finally exercises style combinations rather than isolated presets.

### §2.3 R9 — Visual Evolution & A-V Sync · *blocked at a High finding*

**Entry: NOT met.** `BL-0086` (High): `ADS-106` §2 and the already-baselined `NFR-1190` describe
a palette mechanism `visuals.py` does not have — it emits 36 bytes of inline immediates, has no
ROM-resident palette table, and never reads `CHMIX_IDX` in the palette path. Planning or building
from that premise produces a package whose cost criterion is unmeetable as written.

**Unblocking sequence:** `03` corrects `ADS-106` §2/§6 + Decision Log (and re-decides the
selection rule with the branch-to-N-blocks option on the table) → `04` re-words `NFR-1190` → then
normal `05`→`06`→`07`→G3→`08`→`09`.

**Rides along:** `BL-0087`, `BL-0091`, `BL-0092`, `BL-0093` (all land in documents the correcting
`03` pass already has open), plus `BL-0084`, `BL-0085`, `BL-0021` (accessibility — the exit
criteria require an `R208` luminance check on *any* release touching `visuals.py`, not only when
`RM-9003` is scheduled), and `BL-0083` (the roadmap's own stale R9 prerequisite note).

### §2.4 R10 — Interactive Control Expansion

**Entry:** R8 shipped. Makes style/scheme directly steerable rather than only autonomously
drifting, reusing existing preset-index infrastructure (`R217`: all 6 controls are already
assigned, so no new input surface). **Rides along:** `BL-0011` (four cited generation-technique
upgrade candidates — a natural fit once steering is being revisited anyway).

### §2.5 R12.5 — Content & Musical Quality Pass · **proposed, and the most important gap in this plan**

**This release does not exist in the roadmap. It should.**

The finding that motivates it: **`09-content-review` has never run — no artifact has ever been
created on any branch, on any commit.** Meanwhile `music_engine.py` carries **15** constants
explicitly marked first-guess/not-tuned-by-ear (`BL-0005`'s standing convention). The project is
a *music generator* whose every musical constant — tempo steps, scale semitone sets, Euclidean
density patterns, dissonance/stale/overload thresholds, style rows, song-phase targets, motif
variants, valence table — has been chosen by reasoning and **never evaluated by ear**.

142/142 tests prove the engine does what it was specified to do. **They cannot and do not prove
it sounds good.** No stage in the pipeline has yet asked that question. A v1.0 that ships
unreviewed placeholder values would satisfy every requirement in the baseline and still risk
being a poor listening experience — which is the actual product.

`docs/roadmap/09-release-exit-criteria.md` already anticipates this, requiring *"for any release
touching musical character (R5, R6, R8, R9), a `09-content-review`-style listening pass, not
automated assertion alone."* **That criterion has never been satisfied for R5, R6, or R8.**

**Scope:** run `09-content-review` across the full shipped feature set; retune what the listening
pass rejects; re-review. Closes the content/tuning cluster: `BL-0005` (the root item, open since
the project's early days), `BL-0021`, `BL-0039`, `BL-0084`, `BL-0053`, plus whatever R8's own
blend-quality review surfaces.

**Placement:** after R12 (so tuning isn't invalidated by a later performance pass) and before R13.
Uses the `R4.5` half-numbered-checkpoint precedent the roadmap already established.

**Prerequisite — now a named work item, not an open gate.** `BL-0089` asked how to fix
`08-content-authoring`'s write scope, which pointed at three files that have never existed. **The
user decided 2026-08-07: create them** — extract the data out of `visuals.py` and `music_engine.py`
into real `tiles.py` / `patterns.py` / `music_data.py`, restoring the decomposition `GDS-03` and
`GDS-09` always described.

That is a genuine **`IP-8xx0` refactoring package** (executor `08-refactoring`) carrying the
standard equivalence contract — **byte-identical ROM** and an identical full-suite check-name set —
touching the two largest modules in the tree. It needs `07-implementation-planning` to author it
and its **own G3 authorization** (refactoring packages are never pre-authorized). It sits **on the
critical path immediately before R12.5**, because the tuning pass needs a working content surface
to write through. When it lands it supersedes `GDS-09` §2's honestly-recorded "three of those five
do not exist" note.

### §2.6 R12 — Performance & ROM-Budget · §2.7 R13 — Release Candidate

**R12** audits cumulative cost: cycle budget per `engine_tick`/`badzone_tick`, ROM byte budget,
long-duration stress at the full feature set. Directly owns `BL-0074` (no package owns the *fix*
verb for the per-frame budget — `IP-9030` is a guard, not a remediation) and `BL-0092` (the
`ADR-0002`/`R104` §8 re-measurement discipline that has not run for 8 packages; measured
**4293/32768, 13.1%, 28475 free** during the 2026-08-07 audit).

**R13** requires every item in `09-release-exit-criteria.md` satisfied, `10-integration-review`
clean at full scope, and `11-release-readiness` GO. Owns `BL-0007` (the working title) and the
final disposition of `BL-0058` (hardware validation).

---

## §3 Feature assignment — all 13

Every `FEAT-xxxx` in the catalog, assigned to exactly one release. No feature is scheduled before
a feature it depends on.

| Feature | Release | State |
|---|---|---|
| FEAT-1000 Core generation engine | R1 | ✅ Shipped |
| FEAT-1010 Input steering | R1 | ✅ Shipped |
| FEAT-1020 Reset-to-preset | R1 | ✅ Shipped |
| FEAT-1030 Bad-zone detection | R1 | ✅ Shipped |
| FEAT-1040 Minimal visualizer | R1 | ✅ Shipped |
| FEAT-1050 Headless verification suite | R1 | ✅ Shipped |
| FEAT-1060 Sound design techniques | R2 | ✅ Shipped |
| FEAT-1070 Combinable generation schemes | R4 | ✅ Shipped |
| FEAT-1080 Genre-aware style presets | R5 | ✅ Shipped |
| FEAT-1090 Motif recurrence | R6 (bundled) | ✅ Shipped |
| FEAT-1100 Song-form phase cycling | R6 | ✅ Shipped |
| FEAT-1110 Settings & control visibility | R6 (bundled) | ✅ Shipped |
| FEAT-1120 Emotional/energy layer | **R7** | 🟡 `COMPLETE`, unverified |
| *FEAT-1130 Genre blending* (not yet catalogued) | **R8** | ⬜ Needs a catalog row |
| *FEAT-1140 Visual evolution* (not yet catalogued) | **R9** | ⬜ Needs a catalog row; gated |
| **FEAT-1150 Harmonic coordination** | **MVP-critical remediation — jumps the R-queue** | 🟢 Catalogued 2026-08-20; spec/plan/build in flight |

The two italic rows are **forward placeholders, not catalog entries** — `05-feature-decomposition`
must add real `FEAT-1130`/`FEAT-1140` rows when R8/R9 reach decomposition. Named here so the
sequencing is visible, marked italic so they are not mistaken for existing rows.

**`FEAT-1150` is bucketed ahead of R8 and R9 deliberately, and the reasoning is recorded rather
than assumed.** It is not a roadmap release; it is remediation of `BL-0119` — the project's largest
measured quality gap and the direct, measured cause of the project owner's own verdict that the
music does not sound good. Three facts put it ahead of the queue:

1. **It is the only open item that can move the product's central quality question.** `BL-0119`'s
   own routing note is explicit that no amount of tuning work (`BL-0005`, `BL-0102`, `BL-0117`,
   `BL-0118`) reaches it: retuning changes how the engine *flees* bad harmony, not whether it
   *constructs* good harmony. R8's blending and R9's visuals are both real value on top of an
   engine whose vertical harmony is uncoordinated.
2. **The project owner directed it explicitly**, on 2026-08-20 — *"I'd like to get to a pleasant
   sounding music as soon as possible. Iterate pipeline until it is deemed pleasant and ready for
   human ears to review."* That is a sequencing instruction, and this skill's release-plan
   assignments are subordinate to it.
3. **Its dependencies are all satisfied.** `FEAT-1070`'s scheme mechanism is `VERIFIED` and shipped;
   `ADS-108` (amended) and `ADR-0004` are decided; `FR-1500`-`FR-1590`/`NFR-1240`-`NFR-1270` are
   baselined. Nothing in R8 or R9 blocks it, and it blocks neither of them — the graph edge does not
   exist in either direction, so re-ordering costs nothing structurally.

It does, uniquely in this plan, **change shipped behavior rather than adding to it** (the boot sound
changes; `T5`/`T6`-class assertions need re-authoring). That is authorized, not accidental — see
`FEAT-1150`'s own catalog row and `GDS-04` §4.1's dated amendment.

---

## §4 Backlog disposition — all 49 open items

Every open `BL-xxxx` has a home. Nothing is silently omitted.

### Former blocking gates (4) — **all answered 2026-08-07, none open**
| ID | Was blocking | Resolution |
|---|---|---|
| `BL-0086` | R9 | **De-escalated** — R9 is v1.1, so this is no longer release-blocking. Default: correct `ADS-106` + `NFR-1190` in the next doc-coherence pass, alongside `BL-0087`/`BL-0091`/`BL-0092`/`BL-0093`, which land in the same documents. |
| `BL-0089` | R12.5 | **Answered: create the three modules.** Becomes an `IP-8xx0` refactoring package on the critical path before R12.5 (§2.5), with its own G3. |
| `BL-0095` | — | Substantive half closed by this file. Residual: `05-feature-review.md`, §9. |
| `BL-0058` | R13 | **Answered: emulator-validated + SameBoy/BGB cross-check at R13.** Real silicon → v1.1. |

**Zero `NEEDS-USER` items remain in the backlog.** The only user input still owed is **G3
authorization per package**, at the point each one is ready to build.

### Assigned to a release (28)
- **R7 (verification queue):** `BL-0069`, `BL-0064`, `BL-0065`, `BL-0088`, `BL-0013`
- **R8 (style/scheme coverage + blending):** `BL-0040`, `BL-0041`, `BL-0048`, `BL-0032`, `BL-0033`, `BL-0039`, `BL-0042`, `BL-0043`, `BL-0030`
- **R9 (visual + the doc-coherence cluster its `03` pass already opens):** `BL-0087`, `BL-0091`, `BL-0092`, `BL-0093`, `BL-0084`, `BL-0085`, `BL-0021`, `BL-0083`
- **R10:** `BL-0011`
- **R12:** `BL-0074`
- **R12.5 (content/tuning):** `BL-0005`, `BL-0053`
- **R13:** `BL-0007`, `BL-0022`, `BL-0023`

### Ride the next pass that touches their file (9) — no release of their own
`BL-0082`, `BL-0090`, `BL-0094`, `BL-0096` (doc-coherence) · `BL-0025`, `BL-0026`, `BL-0028`
(package-doc drift) · `BL-0075`, `BL-0077` (docs/link hygiene).

### Test-rigor cluster (4) — one coordinated pass, recommended at R12
`BL-0044`, `BL-0045`, `BL-0027`, `BL-0062`. `BL-0062` is the parent observation (*"shipped tests
demonstrate a mechanism works once, where the claim is that it works generally"*); the other three
are instances. Fixing them individually repeats the pattern — fix the pattern once.

### Deferred with a live trigger (4) — explicitly out of scope for v1.0
`BL-0015` (rare self-healing transient; trigger: if it stops self-healing) · `BL-0073` (method-
independence in verification; trigger: next `09` run confirming a *finding*) · `BL-0079`
(`R221` dissonance-as-valence citation gap; trigger: if `DISSONANCE_SCORE` ever feeds `VALENCE`) ·
`BL-0011` is scheduled at R10 above, not deferred.

---

## §5 Definition of a releasable v1.0

**Required to ship** — positions taken, not hedged:

1. **All packages `VERIFIED`, not merely `COMPLETE`.** Four are queued today. Non-negotiable: the
   project's own G-rules reserve `VERIFIED` to independent verification, and a release built on
   self-attested completion abandons the discipline that produced its quality.
2. **Every `09-release-exit-criteria.md` item satisfied**, including the listening-pass criterion
   for R5/R6/R8/R9 that has **never yet been satisfied for any release**.
3. **A content review has actually run** (R12.5). Shipping 15 untuned-by-ear constants in a music
   generator is the single largest quality risk in the project, and it is invisible to the test
   suite.
4. **`10-integration-review` clean at full package scope**, and **`11-release-readiness` GO**.
5. ~~**A decided product name** (`BL-0007`).~~ ✅ **Settled 2026-08-07: "Driftune" is final.**
   `BL-0007` `DONE` — no rename needed; the ROM header, build output and docs tree already use it.

**Not required to ship** — deliberately:

6. **Hardware validation** (`BL-0058`). ✅ **Decided 2026-08-07:** ship v1.0 as *emulator-validated*,
   stated plainly in the release notes; add a mode-accurate-emulator cross-check (SameBoy/BGB,
   `R309`) at R13 to target the one divergence PyBoy structurally cannot model — it applies no
   PPU-mode gating to VRAM writes, while this ROM's `update_visuals` finishes on VBlank's last
   scanline. Real-silicon validation is a **v1.1 goal**, not a v1.0 blocker.
7. **R9, R10, and R11.** A legitimate, smaller RC is explicitly permitted:
   `05-milestone-definitions.md` states the RC *"requires whichever subset the project actually
   pursued to be fully `VERIFIED`."* **R0-R8 + R12 + R12.5 is a coherent, shippable v1.0** — a
   procedurally-generated chiptune engine with genre identity, song form, autonomous drift, mood
   derivation and blending, tuned by ear. R9's visual evolution is the strongest v1.1 candidate.

---

## §6 Critical path and parallel opportunities

**Critical path to v1.0 (recommended R0-R8 + R12 + R12.5 + R13 scope):**

```
[4-package verification queue] → R7 GO ─┐
                                        ├→ R8 (full 03→09 chain) → R12 → R12.5 → R13 → v1.0
                    (R8 needs no gate) ─┘
```

The queue is the true head of the path: it is the only item blocking R7, it needs no decision, and
**it is already actionable in a fresh session right now**.

**Genuinely parallel (no ordering constraint between them):**
- The verification queue (fresh session) ‖ R8's `03`-`07` planning chain — R8's planning does not
  depend on R7 being `VERIFIED`, only on R5+R6, both shipped.
- `BL-0086`'s correction pass (unblocking R9) ‖ everything above — R9 is off the recommended v1.0
  path, so this can proceed whenever, or be deferred to v1.1 wholesale.
- The doc-coherence cluster ‖ everything — each item rides a pass already scheduled.

**Longest pole:** R12.5. A content review that rejects values requires retuning *and* re-review,
and it is the one release whose duration is set by judgment rather than by work.

---

## §7 Next steps — sequential, for `00-pipeline-manager`

Revised 2026-08-07 against the scope decision and `BL-0089`'s answer.

1. **`09-package-verification`, fresh session, on `IP-9030`** (then `IP-8010`, `IP-8020`,
   `IP-1120` — one per session, oldest first). Needs no decision. Unblocks R7's GO and closes
   `BL-0069`/`BL-0064`/`BL-0065`.
2. **`03-architecture-design-synthesis` → new `ADS-107` for R8 (Genre Blending).** The only
   forward release in v1.0 scope that is fully unblocked. **Runs in parallel with step 1.**
3. **`07-implementation-planning` → an `IP-8xx0` module-extraction package** implementing
   `BL-0089`'s answer: move tile/palette data out of `visuals.py` and the musical tables out of
   `music_engine.py` into real `tiles.py` / `patterns.py` / `music_data.py`, under a byte-identical
   -ROM equivalence contract. **Needs its own G3 authorization.** Prerequisite to R12.5; can be
   planned any time, best executed while no feature package is in flight (`08-refactoring` requires
   a quiescent tree).
4. **`11-release-readiness` for a bundled R7+R8 GO** once both land — honoring R7's own
   "should ship bundled" note rather than calling a GO for a release with nothing to hear.
5. **R12 → R12.5 → R13.** R12.5 is the first time anyone listens to this thing; expect it to
   generate retuning work that is real, and budget for a second review pass after retuning.

Ahead of every `08-*` run, the standing G3 rule applies: **each package needs its own explicit
user go-ahead.** This plan schedules work; it authorizes none.

## §8 Deviation from this skill's own template

`05-feature-decomposition`'s workflow specifies four buckets — **MVP / Release 1 / Release 2 /
Future**. This plan **does not use them**, deliberately.

That vocabulary presumes a project with no established release scheme. This project has R0-R13,
authored 2026-07-22, cited by the roadmap, milestone definitions, exit criteria, traceability
matrix, every `ADS`, and most `IP` packages. Introducing a parallel bucket vocabulary would create
exactly the two-competing-schemes problem this document's §0 exists to prevent — and would be the
same class of defect as `BL-0095` itself, in the opposite direction.

**Mapping, for anyone reading the skill template alongside this file:** MVP ≈ R0-R2 (Milestone A)
· Release 1 ≈ R3-R6 (B+C) · Release 2 ≈ R7-R8 + R12/R12.5/R13 (D+F, the recommended v1.0 scope) ·
Future ≈ R9-R10 (E) and the struck R11.

---

## §9 Disposition of the three remaining `05` deliverables

`BL-0095` found four of five mandated deliverables absent. This file is one. The other three,
adjudicated the way `docs/requirements/INDEX.md`'s missing files were under `BL-0068`:

| Deliverable | Disposition |
|---|---|
| `02-epic-catalog.md` | **Deliberate deviation.** [`docs/roadmap/02-capability-map.md`](../roadmap/02-capability-map.md)'s `CAP-xx` rows are this project's working epic layer — every feature maps to a capability, capabilities carry purpose/modules/dependencies/status. A parallel `EP-xxxx` set would duplicate maintained facts. **Re-trigger:** if a feature ever fails to map cleanly onto a `CAP-xx`. |
| `04-feature-dependency-graph.md` | **Deliberate deviation.** [`docs/roadmap/03-capability-dependency-graph.md`](../roadmap/03-capability-dependency-graph.md) carries the Mermaid graph, critical path, blocking nodes and parallel streams at capability grain, and §6 of this file carries the release-grain path. **Re-trigger:** if feature-grain dependencies ever diverge from capability-grain ones. |
| `05-feature-review.md` | **Genuine gap — not a deviation.** No analogue exists anywhere; the catalog mentions "Feature Review" once, inline. Its job (features too large/small, duplicates, requirements unassigned or double-assigned, architectural inconsistency) is **not** performed by any other artifact. **Recommendation: author it**, scoped to the full FEAT-1000…1120 set, before R8 adds `FEAT-1130`. Filed as a finding in §10. |

---

## §10 Findings raised by this pass

Routed, not fixed here — this document changes nothing outside `docs/feature-planning/`.

| # | Finding | Owner |
|---|---|---|
| 1 | **`09-content-review` has never run**, on any branch, in the project's entire history, while 15 constants in `music_engine.py` are marked untuned-by-ear. The exit criteria's listening-pass requirement has never been satisfied for R5, R6 or R8. Motivates the proposed **R12.5**. | `00-pipeline-manager` to schedule; the roadmap owner to adopt R12.5 |
| 2 | **R12.5 needs roadmap adoption.** This plan proposes it; `04-release-roadmap.md` is read-only to this skill. | roadmap owner |
| 3 | **`05-feature-review.md` is a genuine gap** (§9) — recommend authoring before R8 adds a feature. | `05-feature-decomposition` |
| 4 | **R11 should be marked struck** in `04-release-roadmap.md`, per its own NO-GO clause. It currently reads as pending. | roadmap owner |
| 5 | **`FEAT-1130`/`FEAT-1140` are placeholders**, not catalog rows (§3). Real rows needed when R8/R9 reach decomposition. | `05-feature-decomposition` |
