# Product Roadmap 05 — Milestone Definitions

- **Grounded in:** `04-release-roadmap.md`
- **Status:** ✅ Authored 2026-07-22

Six milestones group the fourteen releases into demonstrable, decision-relevant checkpoints.

## Milestone A — Foundation (R0-R2)

- **Objective:** Prove the full pipeline (research → architecture → requirements → features →
  packages → verification) can produce a genuinely playable generative instrument.
- **Capabilities completed:** CAP-01 through CAP-04, CAP-06, CAP-07, CAP-08, CAP-14 (MVP),
  CAP-15, CAP-16, CAP-17, CAP-20, CAP-21.
- **Major demonstration:** Power on the ROM; hear continuous, steerable, self-recovering 4-channel
  generative chiptune with expressive articulation (arpeggio/vibrato/portamento/duty-cycle); see a
  reactive tile/palette display.
- **Acceptance criteria:** 65/65 `test_rom.py` checks; ROM builds to a valid 32768-byte header;
  all Foundation-bucket packages `VERIFIED` (R2's two packages still owe verification).
- **Remaining work:** `09-package-verification` on `IP-1060`/`IP-1061` (fresh session).
- **Status:** ✅ **Substantially complete** — one verification step short of fully closed.

## Milestone B — Integrity & Diversity Groundwork (R3-R5, +R4.5)

- **Objective:** Close the Foundation bucket's known defects, then build the first real
  structural/stylistic variety on top of a now-sound base.
- **Capabilities completed:** CAP-10 (repaired), CAP-09, CAP-11.
- **Major demonstration:** Start button visibly gates channels; a pitched channel switches between
  two structurally different generation schemes; at least 3 genre-adjacent styles are audibly
  distinct and selectable.
- **Acceptance criteria:** `BL-0019`/`BL-0017` both `DONE`; `10-integration-review` clean;
  `11-release-readiness` GO achievable for the Foundation bucket; scheme/style capabilities
  independently verified.
- **Remaining work:** **G3 authorization for `IP-9010`/`IP-9020`** (the standing gate blocking
  this milestone's very first release). Also includes **R4.5**, the cart-shape decision checkpoint
  (moved into this milestone per `10-final-roadmap-review.md` finding #1, applied) — a decision,
  not a build, sequenced after R4 so a real ROM-budget trajectory is visible first.
- **Status:** Not started — blocked on authorization, not technical readiness.

## Milestone C — Musical Maturity (R6-R7)

- **Objective:** Give a session real temporal shape (structure and mood), independent of Milestone
  B's stylistic-diversity work.
- **Capabilities completed:** CAP-12, CAP-13.
- **Major demonstration:** An uninterrupted multi-minute session that a listener can narrate as
  having a beginning, a build, a peak, and a resolution — and that a bystander can describe in
  emotional-spectrum terms (calmer, tenser, etc.) without being told to listen for it.
- **Acceptance criteria:** Song-form state machine and emotional/energy read-layer both
  `VERIFIED`; `BL-0010`'s song-form half formally closed.
- **Remaining work:** An explicit precedence rule for how the song-form state machine and the
  bad-zone recovery loop interact when both want to bias the same parameter simultaneously
  (flagged as an open design question, not yet resolved).
- **Status:** Not started — **parallelizable with Milestone B**, no blocking dependency on it.

## Milestone D — Genre Identity (R8, drawing on B+C)

- **Objective:** Combine Milestone B's style regions with Milestone C's drift mechanism into
  genuine genre blending — directly answering the user's original "solo or in combination" request
  (`BL-0020`).
- **Capabilities completed:** CAP-11 + CAP-12 combined usage (no new capability, a combination
  milestone).
- **Major demonstration:** A session audibly drifts from one genre reference toward another over
  several minutes, landing somewhere musically coherent in between.
- **Acceptance criteria:** At least one blend pair independently verified and content-reviewed (not
  just automated-tested — musical coherence needs a listening pass).
- **Remaining work:** None beyond R8 itself.
- **Status:** Not started — depends on both B and C.

## Milestone E — Audiovisual & Interaction Polish (R9-R10)

- **Objective:** Extend the visualizer to react to the new style/mood dimensions; re-examine
  control mapping now that style/scheme are steerable.
- **Capabilities completed:** CAP-14 (evolution), interactive control expansion.
- **Major demonstration:** The screen visibly changes character with style and mood; a listener
  can directly steer style/scheme via existing controls.
- **Acceptance criteria:** Visual response to at least one style and one mood dimension,
  independently verified; existing 6-control behavior unregressed.
- **Remaining work:** **The visual-evolution research thread (MSTR-001 §9) must run first** — this
  is a hard prerequisite, not a nice-to-have, named explicitly so it isn't skipped.
- **Status:** Not started — this is the roadmap's one true convergence bottleneck (needs D and C).

## Milestone F — Persistence & Release Hardening (R11-R13)

- **Objective:** Resolve the open persistence question, formalize performance/budget discipline,
  and reach an actual, evidence-based release-candidate decision.
- **Capabilities completed:** CAP-18 (if adopted), CAP-19 (formalized), full `11-release-
  readiness` cycle.
- **Major demonstration:** A complete regression pass across every shipped capability; (if
  persistence adopted) a favorite piece surviving power-off.
- **Acceptance criteria:** All of `09-release-exit-criteria.md` satisfied; `10-integration-review`
  clean across the whole package; `11-release-readiness` GO recorded.
- **Remaining work:** The persistence adopt-or-decline decision itself (R11's explicit
  precondition) — genuinely open, not a technical gap.
- **Status:** Not started — final milestone, depends on whichever of B/C/D/E subset was pursued.

## Milestone sequencing summary

```
A (done, ~verified) ─┬─► B (blocked on G3) ──┐
                      │                       ├─► D ──► E ──► F (RC)
                      └─► C (parallelizable) ─┘
                                                    ▲
                      R11 Persistence (independent, gated on architecture decision) ──┘
```

A milestone-F release candidate does **not** require every one of B/C/D/E to have shipped — it
requires whichever subset the project actually pursued to be fully `VERIFIED` and integration-
reviewed. This roadmap names the full ambition; it does not mandate exhausting it before a
legitimate, smaller RC is possible (see `10-final-roadmap-review.md`'s note on right-sizing scope).
