# GDS-10 — Requirements Traceability Matrix Level

- **Level:** GDS-10, the final level of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26
- **Upstream:** `docs/requirements/`, `MSTR-001` C10, all preceding ladder levels
- **Scope note:** this level is deliberately **thin and structural**. It records *how traceability
  is carried on this project* and defers all detail to `docs/requirements/`. It is not itself a
  matrix and does not contain one.

## §1 The two traceability directions

This project carries traceability in two directions, and they are in genuinely different health.

| Direction | Question | Mechanism | State |
|---|---|---|---|
| **Backward** | where did this requirement come from? | each FR/NFR's *Traces to* column | ✅ complete and maintained |
| **Forward (requirement → code)** | did this requirement get built and tested? | the FEAT → FS → IP → VR chain | ✅ works, distributed across artifacts |
| **Forward (research → code)** | did this research topic land in anything? | *nothing* | ❌ **no artifact of any kind exists** |

The third row is `MSTR-001` C10's obligation, added in v1.3, and §4 is about it.

## §2 Backward traceability — how it works

Every numbered requirement in `docs/requirements/01-functional-requirements.md` carries a *Traces
to* column naming its source: a GDS level and section, an `ADS-1xx` section, an `ADR`, or an
`R-xxx` research topic. `FR-1310`, for instance, traces to `ADS-103` §5; `NFR-1140` to `ADS-104`
§6 plus `R104` §7-8.

This is maintained by construction rather than by audit: `04-requirements-engineering`'s own
quality gate refuses a requirement without a real citation ("implied by the architecture is not a
citation"), and every delta pass since has held that line across seven extensions. Spot-checking
the current baseline, no requirement is missing its source.

**Backward traceability on this project is in good shape and needs nothing.**

## §3 Forward traceability — a chain, not a matrix

`04-requirements-engineering`'s own workflow specifies a dedicated
`04-requirements-traceability-matrix.md` with columns `Req ID | Title | Research Source |
Architecture Section | ADR | Module | Feature Spec | Implementation Package | Test`. **That file
was never authored.** `docs/requirements/INDEX.md` records it as `⛔ Planned (tracked inline via
each FR/NFR's "Traces to" column for now)`, and seven Verification Reports each note the same
thing in their own Requirements-audit sections ("No RTM file at FR-grain currently exists in this
tree — `docs/requirements/01-functional-requirements.md` is the traceability source of record at
FR grain").

What exists instead is a **chain of artifacts, each carrying one hop**:

```
FR/NFR  ──(Traces to column)──>        its GDS/ADS/R-xxx source        [backward]
FR/NFR  ──(FEAT catalog row's
           "FR/NFR traced" column)──>  FEAT-xxxx
FEAT    ──(FS metadata)──>             FS-xxx
FS      ──(IP's "Requirements Covered"
           + "Files to Modify")──>     IP-xxxx  ──>  real source files
IP      ──(VR's Requirements audit
           table)──>                   VR-xxxx  ──>  named test checks (T1.1 … T18.10)
```

Every hop is explicit and bidirectional in practice: an FR names its feature, a feature names its
spec, a spec names its package, a package names its files and tests, and a VR **re-derives the
whole mapping independently** and records it as a table (`ID | Where implemented | Where tested |
Result`). The VR audit is the strongest link in the chain, because it is performed by a session
with no memory of the implementation and it has caught real gaps.

### §3.1 Is the missing `03-rtm.md` a real gap? — a position

**No. It is a reasonable deviation, and building the matrix now would probably make traceability
worse, not better.**

The reasoning:

1. **The information is not missing — it is distributed.** Every hop above exists in a document
   that is *already* maintained for its own reasons. A matrix would be a second copy of facts that
   already have owners.
2. **A matrix's value is in finding gaps, and this project has a better gap-finder.** The purpose
   of an RTM is to surface requirements that never got built or never got tested. Independent
   verification does that job per-package, with a fresh session actually running the tests — a
   strictly stronger check than a table asserting a test exists.
3. **A matrix would be a synchronization liability.** With 38 FRs, 17 NFRs, 12 features, 6 specs,
   16 packages and 16 VRs, a single matrix has ~90 rows and would need updating on every pipeline
   step. Nothing in this project's history suggests it would stay accurate; the several
   doc-staleness findings this pipeline keeps catching (`BL-0047`, `BL-0049`, `BL-0050`,
   `BL-0054`, `BL-0056`, `BL-0059`) are all single-line status rows, and a 90-row matrix would
   drift far faster.
4. **The one thing a matrix would genuinely add is a whole-baseline view** — "show me every
   requirement with no test." That is real value, but it is a *query*, and the honest way to
   satisfy a query over distributed data that is already maintained is to run the query when it is
   needed, not to denormalize it permanently.

**The recommendation this level records:** leave `03-rtm.md` unauthored; keep the chain. If a
whole-baseline view is ever wanted, generate it on demand from the existing artifacts rather than
maintaining it by hand. `docs/requirements/INDEX.md`'s row should be re-labelled from `⛔ Planned`
to a deliberate deviation with this rationale, so it stops reading as owed work — that is
`04-requirements-engineering`'s edit to make, not this level's.

The same reasoning applies to `02-requirements-review.md`, also listed `⛔ Planned`: review
findings are carried inline as dated *Delta Review* sections in the single requirements file, one
per extension, and all seven exist. The single-file convention is a **documented, working standing
deviation** — that file's own "Known pre-existing gap" note already acknowledges it — not an
oversight.

## §4 The research → code direction: a real, unaddressed gap

`MSTR-001` C10 (added v1.3) requires that **every authored research topic be traceable forward to
a design feature actually implemented in code**, or carry an explicitly recorded exception. Its
own changelog entry predicted the consequence:

> *"a full forward-trace audit across all 39 authored `R1xx`/`R2xx`/`R3xx` topics is owed... Likely
> near-term finding: several orientation/history topics... may currently have no forward trace and
> will need either a real forward link or a recorded C10 exception."*

**That audit has never been run.** The topic count has since grown from 39 to 44. No forward-trace
artifact of any kind exists — not a matrix, not a column, not a per-topic field. C10 is a
commitment the tree currently has no mechanism to check itself against.

Two concrete instances are already known, both found incidentally rather than by audit:

- **`R105` (OAM/sprites/DMA)** — GDS-08 §1.1 established the visualizer uses no sprites at all,
  every pixel being background tilemap. `R105` therefore has no forward trace, and needs a
  recorded C10 exception on the topic itself (`BL-0063`).
- **`R308`/`R101`'s cycle-budgeting guidance** — grounded a *decision not to act* (cycle counting
  is over-engineering), which is a legitimate C10 exception shape ("grounds implementation quality
  rather than producing a feature") but is nowhere recorded as one. GDS-06 §2.2 has since
  partially overturned that decision, which makes the untracked status more consequential.

**This level's position:** unlike §3.1's matrix, this gap is **real and worth closing**, because
unlike requirement→code traceability there is *no* alternative mechanism doing the job. Nothing
anywhere would notice a research topic that never landed. The lightweight fix that matches this
project's existing conventions is a **per-topic forward-trace field** — one line in each topic's
own header naming the FR/FEAT/IP it fed, or the recorded exception — maintained where the topic
lives, rather than a central matrix (§3.1's reasoning applies equally here). Owner:
`02-research-*` skills for the per-topic field; the sweep across all 44 is a `10-integration-review`
traceability-dimension pass or a dedicated backlog item.

## §5 What this level does *not* do

- It does not contain a matrix, and does not require one to exist (§3.1).
- It does not audit anything — it describes the mechanism. The C10 audit §4 identifies is routed,
  not performed here.
- It does not edit `docs/requirements/`'s own index rows, though it recommends one re-labelling
  (§3.1). Those belong to `04-requirements-engineering`.

## Merge gate

- [x] The previous level's gate (GDS-09) was verified closed before this level started.
- [x] Traceability described as it actually works — the chain (§3), not the template's assumed
      matrix — with the current state of `docs/requirements/INDEX.md` verified directly rather
      than assumed.
- [x] A position taken with reasoning on the missing `03-rtm.md` (§3.1: a reasonable deviation,
      leave it) and on the C10 forward-trace gap (§4: a real gap, close it) — rather than merely
      noting both.
- [x] No matrix built, no requirements edited, no research claims originated.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md`'s stage-03 row updated together.

**Merge decision.** Nothing moves. This level is a pointer by design — `docs/requirements/` stays
the authoritative home of every requirement and its citations, and the FEAT/FS/IP/VR artifacts
stay the authoritative carriers of each forward hop.

### The ladder is complete

GDS-10 closes the ladder. Final state:

| Level | State |
|---|---|
| GDS-00 Vision | ✅ authored (`01-vision`'s, amended through v1.4) |
| GDS-01 Concept of Interaction | ✅ authored 2026-07-21 |
| GDS-02 System Context | ✅ authored 2026-07-26 |
| GDS-03 Architecture | ✅ authored 2026-07-21, reconciled 2026-07-22 |
| GDS-04 Domain Model | ✅ authored 2026-07-26 |
| **GDS-05 Functional Requirements** | **deliberately not owed** — superseded by the direct `04-requirements-engineering` pass; rationale in GDS-06 §0 |
| GDS-06 Non-functional Requirements | ✅ authored 2026-07-26 |
| GDS-07 Data Model | ✅ authored 2026-07-21, extended 2026-07-22 and 2026-07-26 |
| GDS-08 Presentation Architecture | ✅ authored 2026-07-26 |
| GDS-09 Interface Specification | ✅ authored 2026-07-26 |
| GDS-10 RTM level | ✅ authored 2026-07-26 (this document) |

Ten of eleven levels authored with closed gates; the eleventh recorded as deliberately not owed
rather than outstanding. **`BL-0001` — open since run #1, the pipeline's oldest backlog entry —
can now be closed.**

Worth recording honestly about how this happened: five of these levels (02, 04, 06, 08, 09) were
authored in a single run, years of ladder-time after the code they describe. That inversion was
not ideal, and each level's own §0 says so where relevant. But it produced documents that describe
a real system rather than an intended one, and it surfaced findings a forward synthesis could not
have — the never-tested-on-hardware gap (GDS-02 §7), the fired cycle-tallying trigger (GDS-06
§2.2), the vestigial patch-point contract (GDS-09 §3), and the 1→11 constant duplication (GDS-09
§6) are all things you can only find by reading shipped code against a written intention.

**Gate:** closed 2026-07-26. **The GDS ladder is complete.** Next: `docs/requirements/`'s own
index re-labelling (§3.1) and the C10 forward-trace audit (§4), both routed to their owners.
