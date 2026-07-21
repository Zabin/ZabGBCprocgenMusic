# R215 — Genetic Algorithms, Constraint Solving, State Machines & Event Scheduling (Survey)

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 4, items 53-56 (genetic algorithms survey,
  constraint solving, state machines, event scheduling)

## 1. Purpose
Briefly survey the remaining named algorithm families from the user's list, honestly assessing
SM83-tractability for each rather than treating every named technique as equally applicable.

## 2. Scope
Genetic algorithms, constraint solving, state machines, and event scheduling, as applied to music
generation.

## 3. Concepts
- **Genetic algorithms (GA)**: confirmed real prior art (e.g. "Muse: A Genetic Algorithm for
  Musical Chord Progression Generation," and GA approaches "learn rules and patterns from a
  dataset... and generate progressions via penalties based on conditional probabilities")
  [scholarworks.gvsu.edu — Muse thesis](https://scholarworks.gvsu.edu/gradprojects/232/); (also
  cited in R211 SS3 for chord progressions). **Not SM83-tractable for real-time on-device use**:
  GAs need a population of candidate solutions evaluated by a fitness function each generation —
  this is an offline-composition technique (run once, at design time, to produce content baked
  into ROM) or a build-time tool, never a per-tick runtime algorithm on this hardware. Correctly
  out of scope for Driftune's real-time generation (MSTR-001 C6), though it could plausibly be
  used **offline** to help *design* a good transition table for R211's rule-based chord idea —
  named as a design-tool possibility, not a runtime technique.
- **Constraint solving**: as used in the chord-progression literature (R211's functional-harmony
  citation), constraint checking ("does this transition violate voice-leading rule X") is cheap
  per-step *if* the constraint set is small and fixed (a handful of boolean checks) — this is
  exactly the tractable form R211 SS5's countermelody idea already assumes ("a per-step constraint
  check, not a global optimization"). General-purpose constraint *solving* (searching for a
  globally-optimal assignment) is not SM83-tractable; per-step constraint *checking* is.
- **State machines**: already the architecture Driftune's own main loop and (were there one)
  GDS-01's flat interaction model would use if it had multiple modes — currently moot (GDS-01
  deliberately has exactly one state, "running"). If R212's named song-structure/form gap is ever
  pursued, a small state machine (e.g. "building tension" → "climax" → "resolving") is the
  standard, cheap way to represent macro-level form — flagged as the concrete mechanism for that
  future work, not built now.
- **Event scheduling**: Driftune's `engine_tick` already *is* a (very simple) event scheduler —
  each channel's `NOTE_TIMER_*` is a countdown-to-next-event, exactly the "cells... assigned
  priority levels... highest levels processed first"-style tick/priority scheduling pattern real
  audio engines use [search synthesis — Audiality architecture notes, cross-ref R307], just
  simplified to fixed-priority-per-channel rather than a general priority queue (unnecessary at
  only 4 channels).

### Sources
- [scholarworks.gvsu.edu — Muse: A GA for Musical Chord Progression Generation](https://scholarworks.gvsu.edu/gradprojects/232/)
- Cross-references to R211 (constraint-checking already assumed there) and R307 (event-scheduling
  architecture, detailed further there).

## 4. Operational Context
State machines and event scheduling are *already* the shape of the shipped engine (informally);
GAs and general constraint solving are correctly unused and should stay that way for runtime code.

## 5. Implementation Guidance
- **Do not build a runtime GA** — if chord-progression design work (R211) ever wants GA-assisted
  authoring, that happens **offline** (a one-time Python script producing a static transition
  table checked into `music_engine.py`, analogous to how `generate_theme_variations` worked in the
  reference project) — never on-device.
- **A small explicit state machine is the right future mechanism for R212's song-structure gap**,
  if that gap is ever worked — named here so a future architecture pass doesn't have to
  re-discover it.

## 6. Feature Mapping
No current `IP-xxxx`; informs future backlog scope for R211/R212's named gaps.

## 7. Related Topics
R211 (chord-progression generation, the GA/constraint-checking application), R212 (song-structure
gap, the state-machine application), R307 (event-scheduling architecture, detailed there).
