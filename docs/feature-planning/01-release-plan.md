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
| **R9 Visual Evolution & A-V Sync** | E | 🟡 Designed (`ADS-106`, `FR-1430`-`1460`), **blocked** | `BL-0086` (High) |
| R10 Interactive Control Expansion | E | ⬜ Not started | R8 |
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

**Prerequisite:** `BL-0089` — `08-content-authoring`'s entire declared write scope is three files
that do not exist (`tiles.py`/`patterns.py`/`music_data.py`). Retuning constants is exactly the
work that skill exists to do, so this gate must be resolved before R12.5 can execute.

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

The last two rows are **forward placeholders, not catalog entries** — `05-feature-decomposition`
must add real `FEAT-1130`/`FEAT-1140` rows when R8/R9 reach decomposition. Named here so the
sequencing is visible, marked italic so they are not mistaken for existing rows.

---

## §4 Backlog disposition — all 49 open items

Every open `BL-xxxx` has a home. Nothing is silently omitted.

### Blocking gates (4) — require a user decision
| ID | Blocks | Decision needed |
|---|---|---|
| `BL-0086` | **R9** | Correct `ADS-106` + `NFR-1190` now, or at planning time |
| `BL-0089` | **R12.5** | Repoint `08-content-authoring`'s write scope, or retire the 3 never-built modules |
| `BL-0095` | — | This file closes the substantive half; the residual is §9's deliverable disposition |
| `BL-0058` | R13 | Is hardware/emulator-cross-check validation wanted, and at what priority |

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
5. **A decided product name** (`BL-0007`). "Driftune" is a working title the vision doc itself
   flags as open; a v1.0 ships under a name someone chose.

**Not required to ship** — deliberately:

6. **Hardware validation** (`BL-0058`). Every claim this project makes is a claim about PyBoy
   2.7.0. Real-silicon validation needs a flash cart and a physical device, which is outside every
   automated stage's reach. **Recommendation:** ship v1.0 as *emulator-validated*, stated plainly
   in the release notes, and treat hardware as a v1.1 goal. The cheaper partial substitute —
   cross-checking against a mode-accurate emulator (SameBoy/BGB, `R309`) — is worth doing at R13
   and does not block.
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

## §7 Next three steps — sequential, for `00-pipeline-manager`

1. **`09-package-verification`, fresh session, on `IP-9030`** (then `IP-8010`, `IP-8020`,
   `IP-1120` — one per session, oldest first). Needs no decision. Unblocks R7's GO and closes
   `BL-0069`/`BL-0064`/`BL-0065`.
2. **`03-architecture-design-synthesis` → new `ADS-107` for R8 (Genre Blending).** The only
   forward release that is fully unblocked. Runs in parallel with step 1.
3. **`11-release-readiness` for a bundled R7+R8 GO** once both land — honoring R7's own
   "should ship bundled" note rather than calling a GO for a release with nothing to hear.

Ahead of the next `08-*` run, the standing G3 rule applies: **every package needs its own explicit
user go-ahead.** This plan schedules work; it authorizes none.

---

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
