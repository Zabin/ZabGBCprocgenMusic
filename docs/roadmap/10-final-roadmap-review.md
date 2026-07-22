# Product Roadmap 10 — Final Roadmap Review

- **Grounded in:** all prior sections of this package
- **Status:** ✅ Authored 2026-07-22

A genuine self-review, not a rubber stamp — findings below are real, not decorative.

## Missing capabilities

- **Content-tuning/preset-authoring** (`BL-0005`'s already-open item: tempo/octave/scale/density
  preset values and bad-zone thresholds are untuned placeholders) has no dedicated `CAP-xxx` row
  in `02-capability-map.md` — it's referenced throughout as a testing/review *practice*
  (`08-development-strategy.md`), not named as a capability in its own right. **Recommendation**:
  this is defensible as-is (it's a cross-cutting quality practice, not a player-facing capability,
  matching CAP-19's own cross-cutting treatment) but should be named explicitly if this roadmap is
  ever formalized into `05-feature-decomposition`'s real Feature Catalog, so it isn't lost.

## Missing milestones

None found. The six milestones (A-F) cover every capability in the map; no capability is orphaned
without a milestone that completes it.

## Poor sequencing

- **R7 (Emotional/Energy Layer) produces no standalone audible/visible change** — already flagged
  in `06`/`07`, but worth restating here as a sequencing finding, not just a feature note:
  **R7 should never be scheduled as an isolated release** in practice; `04-release-roadmap.md`
  lists it separately from R6 for capability-mapping clarity, but the *actual* recommended
  execution groups R6+R7 as one release-equivalent unit, or ships R7 immediately before R9 so its
  output has a consumer within the same milestone. This is a documentation-granularity choice, not
  a real blocking dependency — noted so a future scheduler doesn't literally ship R7 alone.
- **R11's cart-shape decision (`RM-11001`) is bundled with the Persistence release, but the
  decision's *consequences* could matter much earlier.** If R4 (Multi-Scheme), R5 (Style Presets),
  R6 (Evolution), and R7 (Emotional layer) collectively add enough new data tables to approach the
  32KB ceiling before R11 is ever reached, the project would be forced into an unplanned,
  unsequenced bank-switching decision mid-Milestone-D, exactly the kind of scope surprise this
  roadmap is meant to prevent. **Recommendation**: split `RM-11001` (the cart-shape decision
  itself) out of R11 and move it earlier — ideally right after R4, once Stream 1's first new data
  tables exist and a real ROM-budget trajectory can be measured — while leaving `RM-11002` (the
  actual save feature) at R11. The decision costs nothing to make early; deferring it risks an
  unplanned mid-roadmap architecture emergency.

## Circular dependencies

None found. The dependency graph in `03-capability-dependency-graph.md` is a DAG — Stream 1
(CAP-10→09→11) and Stream 2 (CAP-08→12→13) each flow one direction, converge only at CAP-14, and
the Persistence branch (CAP-21→18) never re-enters either stream.

## Excessive risk

- **R8 (Genre Blending)'s musical-coherence risk is real and only partially mitigable by
  automation** — interpolating parameter values doesn't guarantee the *result* sounds musically
  coherent rather than confused. Already flagged with a content-review requirement; no further
  mitigation identified beyond "budget real listening-pass time, don't treat this as a pure
  engineering task."
- **R4's ROM-budget risk compounds with R5/R6/R7's own new data tables** — individually each is
  flagged Medium risk; cumulatively, four consecutive releases each adding new tables without an
  interleaved budget audit is a real compounding risk `04-release-roadmap.md`'s per-release framing
  doesn't surface on its own. **Recommendation**: pull R12's budget-audit discipline forward into
  a lightweight check after every release in Milestones B/C/D, not only once at R12 — cheap
  insurance against discovering an overflow four releases too late.

## Architecture concerns

- **R6's song-form/bad-zone precedence rule (`RM-6002`) is a genuinely new, unanswered design
  question** — this roadmap correctly flags it rather than guessing, but it means R6 cannot be
  fully scoped by `07-implementation-planning` until `03-architecture-design-synthesis` resolves
  it. Not a defect in this roadmap, but worth surfacing here as the review's own explicit
  reminder: **do not let R6 start implementation before that architecture question is answered.**
- **R9's dependency on a not-yet-run research pass** (`RM-9000`) is correctly named as a hard
  prerequisite rather than silently assumed — the review confirms this is handled correctly, not a
  gap.

## Feature overlap

`RM-5002` (style preset selection mechanism, R5) and `RM-10001` (style/scheme steering control,
R10) both touch "how a style gets selected." This is **intentional staged delivery, not true
overlap** — R5 ships an internal/test-only selection path (or a minimal one), R10 later exposes it
through a real control mapping — but the review flags it explicitly so a future implementer
doesn't build the full control-mapping work twice, once at R5 and again at R10.

## Overly large releases

None found. Every `RM-xxxx` entry sizes XS/S/M (`06-feature-specifications.md`); nothing sizes L.
The three releases with the most feature rows (R3, R5, R9) each stay at 2-4 features, consistent
with "approximately one manageable implementation cycle."

## Insufficient testing

- **R7's acceptance criteria (a derivation-matrix assertion) is thin relative to its role as an
  enabler for R9** — recommend R9's own test plan re-verify the emotional-layer output at the
  point it's actually consumed (mood-reactive visuals), not only trust R7's own isolated
  assertion, since a read-layer bug might only become observable once something renders from it.
- Every other release's testing goals are adequately specified against `09-release-exit-criteria.md`.

## Vision misalignment

None found. `07-traceability-matrix.md` traces every roadmap element back to MSTR-001 or a
research-grounded backlog finding; the one deliberately-excluded item (motif recurrence,
L-systems) is excluded for a stated, defensible reason, not a misalignment.

## Summary recommendations, ranked

1. **Split the cart-shape decision out of R11 and move it earlier** (right after R4) — the single
   highest-value sequencing fix this review found. **Applied**: `04-release-roadmap.md` now has a
   new `R4.5` checkpoint release carrying `RM-4501` (the decision), `06-feature-specifications.md`
   and `07-traceability-matrix.md` updated to match; `R11` retains only the actual save feature
   (`RM-11002`), gated on `R4.5 = GO`.
2. **Treat R6+R7 as one execution unit**, or explicitly schedule R7 immediately before its first
   consumer (R9), never as a standalone shipped release.
3. **Interleave lightweight ROM-budget checks through Milestones B/C/D**, not only at R12.
4. **Resolve R6's bad-zone/song-form precedence question at `03-architecture-design-synthesis`
   before `07-implementation-planning` scopes R6** — already correctly flagged, restated as a
   hard sequencing dependency.
5. **Re-verify R7's output at its point of consumption in R9's own test plan**, not only in
   isolation.

None of these findings invalidate the roadmap's overall shape — they are refinements to
sequencing and risk-surfacing, not structural defects. The roadmap satisfies every guiding
principle it was asked to satisfy: every release compiles/runs/produces a real improvement, no
release introduces a large unfinished system, complex capabilities mature over multiple releases,
and every element traces back to the Vision.
