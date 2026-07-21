# R212 — Musical Form, Tension/Release & Macro-Level Parameters

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 3, items 34-40 (musical tension and release, song
  structure, cadence generation, key modulation, time signatures, tempo variation, dynamics
  without velocity)

## 1. Purpose
Survey macro-level (above-the-note) musical structure concepts, honestly separating what
Driftune's current flat, continuously-drifting design already provides from what would be new
scope.

## 2. Scope
Tension/release, song structure/cadence, key modulation, time signatures, tempo variation, and
"dynamics" on hardware with no velocity-sensitive input.

## 3. Concepts
- **Tension and release** in Driftune's own design is *already* structurally present, just not
  through composed musical form: the bad-zone mechanic (GDS-03 SS4, grounded in R204) **is**
  Driftune's tension/release cycle — dissonance/repetition/overload accumulating is tension,
  Select's reset is release. This is a real, if unconventional, mapping worth naming explicitly:
  Driftune substitutes a *player-recoverable systemic* tension/release mechanic for a *composed*
  one.
- **Song structure/cadence** (a piece having a beginning/middle/end, or recognizable sections)
  does **not** currently exist in Driftune's design — GDS-01 explicitly frames the whole ROM
  as one continuously-running process with no "song" boundary. This is the same real gap R211 SS3
  names from the phrase-level angle; here it's confirmed at the macro/form level too. Both
  observations point to the same underlying honest limitation: **Driftune generates texture and
  variation, not composed musical form**, and no citation search this pass surfaced an SM83-
  tractable way to generate real cadential/formal structure cheaply — a research-gap, not a
  solved problem.
- **Key modulation**: not currently a parameter — `SCALE_IDX` (GDS-03 SS3) changes *mode/scale*
  live (player-steered), which is closer to "modal mixture" than a composed modulation (a directed
  move from one key center to another with a prepared cadential approach). Player-steered scale
  switching is simpler and already shipped; composed modulation is a materially different, harder
  problem, same category as the phrase-generation gap above.
- **Time signature**: Driftune has no meter concept at all — `TEMPO_TABLE` sets a uniform
  frame-per-note-step rate, not a beat/measure hierarchy. Adding real time-signature variation
  (e.g. alternating groupings) is additive scope, not currently planned.
- **Tempo variation**: already shipped (`TEMPO_IDX`, player-steered, discrete steps, R202 SS3) —
  the "variation" here is player-driven, not autonomous/composed (the engine doesn't currently
  drift its own tempo without input) — worth naming as a real design choice (deliberate: R206's
  "one control one parameter" convention wants tempo changes attributable to the player, not an
  invisible autonomous drift the player can't account for).
- **"Dynamics without velocity"**: the GBC has no velocity-sensitive input at all (buttons are
  binary), so "dynamics" can only come from the engine's own volume-envelope/channel-mix choices
  (R113), not from player touch — already the only avenue available, not a gap, just a hardware
  ceiling worth stating explicitly so no future spec assumes an unavailable input dimension.

### Sources
- Cross-references to this project's own GDS-01/GDS-03/R201/R202/R204/R211 — this topic is
  primarily a synthesis/honesty-check across those, not new external citation; no literature
  search surfaced a canonical, SM83-tractable "generate real musical form" technique to cite as a
  solution (see R211 SS3 for the same negative-result framing).

## 4. Operational Context
Confirms rather than changes shipped scope — no code implication.

## 5. Implementation Guidance
- **File the "no composed song-structure/cadence/key-modulation" gap as one combined research-gap
  backlog entry** (alongside R211's phrase/motif gap — same underlying limitation, different
  angles) rather than two separate vague entries, so future scoping work sees the full shape of
  the gap in one place.
- **No action needed for tempo/dynamics** — both are already correctly scoped to what the
  hardware/design supports (R202, R113).

## 6. Feature Mapping
No current `IP-xxxx`; feeds a combined research-gap backlog entry for future scoping.

## 7. Related Topics
R201/R211 (note/phrase-level generation — the same gap from a lower altitude), R204 (bad-zone
mechanic as Driftune's actual tension/release substitute), R206 (player-attributable-change
convention, why tempo variation is player-steered rather than autonomous).
