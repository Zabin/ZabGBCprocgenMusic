# Product Roadmap 09 — Release Exit Criteria

- **Grounded in:** MSTR-001 §5 (Quality Bar), `01-product-goals.md`'s Success Criteria
- **Status:** ✅ Authored 2026-07-22

Every release in `04-release-roadmap.md` — not only R13 — must satisfy all of the following before
being called done. This is the same bar MSTR-001 §5/C9 already sets, itemized against the
categories the user's request named explicitly.

## Functional Requirements

- Every capability the release claims to introduce/expand has a traced `FR-xxxx`/`NFR-xxxx` (or a
  named `04-requirements-engineering` gap ticket if the requirement doesn't exist yet) — no release
  ships behavior with no requirement behind it.
- Every acceptance criterion named in `06-feature-specifications.md` for that release's features is
  independently, headlessly verifiable — not "should sound right," but a specific register/WRAM
  assertion or a named content-review checklist item.

## Audio Quality

- No release regresses the four-channel commitment (MSTR-001 C7) or introduces audible artifacts
  (clicks, stuck notes, silent channels) not present before it — checked by the existing stress-
  test practice (multi-thousand-frame runs) plus, for any release touching musical character (R5,
  R6, R8, R9), a `09-content-review`-style listening pass, not automated assertion alone.
- Any new tunable constant (a threshold, a preset value) is explicitly flagged as "first-guess,
  not tuned by ear" if it hasn't been through content review yet — matching `BL-0005`'s own
  existing, honest convention rather than presenting placeholders as finished.

## Visual Quality

- Any release touching `visuals.py` (R9 primarily) is checked against R208's accessibility finding
  (`BL-0021`) as a matter of course, not only when RM-9003 is explicitly scheduled — a new palette
  should not introduce a *new* low-luminance-gap problem while fixing the old one.
- Visual state changes are confirmed via rendered-pixel assertion (the `VR-0006` discipline), not
  only WRAM-state assertion — a WRAM flag being correct doesn't guarantee the palette write landed.

## Performance

- No release may cause a dropped frame or a `HALT`-loop timing violation — checked via the existing
  cycle-budget discipline (R101/R308) and, for any release adding per-frame logic, a self-reported
  cycle-cost delta in that release's own package doc.
- ROM size stays within budget at every release: 32768 bytes if R11 declines bank-switching, or
  within whatever new ceiling R11 establishes if it adopts it — never silently exceeded.

## Stability

- Every release passes the existing multi-thousand-frame continuous-input-churn stress test with
  zero hangs, zero crashes.
- Any release introducing a new state machine (R6, R4's scheme dispatch) additionally stress-tests
  the specific new interaction surface (e.g. rapid scheme-switching, rapid style-switching mid-arc)
  beyond the generic churn test.

## Memory Usage

- WRAM budget is checked against `docs/architecture/07-data-model.md` (GDS-07) at every release
  that adds tracked state — GDS-07 must be updated in the same release, never left to drift (the
  exact discipline gap `BL-0018` found and closed once already; this criterion exists so it
  doesn't recur).
- SRAM budget (only relevant from R11 onward, if adopted) is checked against whatever size the
  architecture decision settles on.

## Hardware Compatibility

- PyBoy-headless verification is the hard gate (MSTR-001 C9) — required for every release, no
  exceptions.
- The milestone-level hardware validation checkpoint (`08-development-strategy.md`) is a
  recommended, non-blocking practice — its absence does not fail a release's exit criteria, but its
  presence should be recorded when it happens (a dated note, not a formal gate).

## Regression Status

- Full `test_rom.py` suite green, including every check from every prior release — no release ships
  with a known, unaddressed regression. A regression discovered mid-release routes back through
  `00-intake` like any other bug, not patched silently outside the pipeline.

## Documentation Completeness

- Every release updates, in the same commit/package as the code: the relevant `GDS-07` (data
  model) if WRAM changed, `Claude.md`'s Known Good Behavior list, the Master Build Plan / packages
  `INDEX.md`, and `docs/pipeline/pipeline-journal.md` (per the pipeline's own standing discipline).
- Every release's package doc(s) carry a Risks section naming what wasn't fully resolved — a clean
  release with silent unresolved risk is not exit-criteria-complete.

## Release-specific note

`R3`, `R4`, `R6`, `R9`, `R11` each name an **explicit precondition** in `04-release-roadmap.md`
(G3 authorization, an architecture decision, a research pass, a precedence-rule design) that is
**part of that release's exit criteria**, not a separate gate outside this document — a release
cannot be called exit-criteria-complete while its own named precondition is still open.
