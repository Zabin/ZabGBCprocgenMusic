# R201 — Algorithmic Composition Techniques for Chiptune

- **Tier:** R200 (procedural-music & visualizer design) · **Owned by:** `02-research-game-design`
- **Status:** ✅ Authored 2026-07-21 · **Supersedes:** part of
  `docs/research/R200-generative-music-design.md` SS1 (retained as a superseded pointer)

## 1. Purpose

Ground `music_engine.py`'s note-generation algorithm (currently: an 8-bit LFSR-driven,
scale-constrained random walk on pulse A) against real algorithmic-composition literature and
practice, both to validate the v1 choice and to name concrete, cited upgrade paths for `IP-0002`+.

## 2. Scope

Random-walk melody generation, Markov-chain note transitions, generative-music history (Eno/Koan)
as the genre this project sits in, and why a scale-constrained walk is the right v1 choice for an
SM83-cycle-budgeted engine.

## 3. Concepts

- **Generative music** (the term, coined in this context by Brian Eno around his 1996 Koan-based
  work) denotes music produced by an ever-running system rather than a fixed, pre-composed piece —
  exactly Driftune's own framing (MSTR-001 SS1: "not just picking from pre-baked tracks").
  Historically, Eno's own systems combined simple algorithms — Markov chains, random walks,
  bouncing-ball-style delay patterns — with a constrained note/scale palette so the *output*
  stays musical even though the *process* is simple and stochastic [Gorilla Sun — Brian Eno's
  Endless Music Machines](https://www.gorillasun.de/blog/brian-enos-endless-music-machines/);
  [Wikipedia — Generative music](https://en.wikipedia.org/wiki/Generative_music).
- **Markov-chain melody generation**: a transition-probability table (row = current scale degree,
  columns = probability of moving to each other degree) drives the walk; the algorithm "builds a
  Markov chain for the probabilities of a note being played according to previous ones, then uses
  it to build randomly a new... piece" [ResearchGate — The Analysis of Generative Music Programs](https://www.researchgate.net/publication/232000203_The_Analysis_of_Generative_Music_Programs).
  This is strictly more expressive than a uniform/near-uniform random walk (it can encode e.g. "a
  scale degree 5 usually resolves to 1, rarely leaps to 3") but needs a stored N×N table.
- **Constrained random walk**: the degenerate, cheaper case of a Markov chain where the transition
  weights are a small, fixed, position-independent distribution over a handful of step sizes
  (Driftune's `DELTA_TABLE = [-1, 0, 0, +1]`) rather than a full per-degree table. This is exactly
  what a resource-constrained (SM83, no floating point, tight cycle budget per R110) real-time
  generator should start with — it produces the same *qualitative* stepwise-melodic-motion
  behavior a Markov chain would, at a fraction of the ROM/RAM cost (4 bytes vs. an 8×8+ table).

### Sources
- [Gorilla Sun — Brian Eno's Endless Music Machines](https://www.gorillasun.de/blog/brian-enos-endless-music-machines/)
- [Wikipedia — Generative music](https://en.wikipedia.org/wiki/Generative_music)
- [ResearchGate — The Analysis of Generative Music Programs](https://www.researchgate.net/publication/232000203_The_Analysis_of_Generative_Music_Programs)
- [Tandfonline — Generative Music Editorial](https://www.tandfonline.com/doi/full/10.1080/07494460802663967)

## 4. Operational Context

`music_engine.py`'s `engine_tick` (`IP-0001`) implements the constrained-random-walk case exactly:
an 8-bit Galois LFSR (deterministic given a fixed seed, per MSTR-001 C6's testing-not-listening
determinism requirement) drives a 2-bit index into `DELTA_TABLE`, added to `CUR_DEGREE_PA` and
wrapped mod 8. This is a legitimate, literature-consistent v1 choice, not a simplification that
sacrifices "real" generative technique for expedience — it's the same family of algorithm scaled
to the platform's real constraints.

## 5. Implementation Guidance

- **Keep the constrained-random-walk approach for pulse B and the wave channel in `IP-0002`** —
  don't jump to a full Markov table until a concrete musical shortfall is observed (per
  `BL-0005`'s own deferral to a real listening pass once more channels exist). A Markov upgrade,
  if wanted later, should enter via `00-intake` as a `feature`, not be silently substituted.
  Concrete upgrade shape if pursued: a 4-8 row transition table per scale (favoring
  scale-degree-1/5 resolution, matching common-practice voice-leading conventions), replacing
  `DELTA_TABLE`'s flat 4-entry lookup with an N-entry-per-current-degree lookup — same LFSR driver,
  larger table.
  This is the concrete Markov-vs-random-walk trade-off named in GDS-03 SS3/SS6 as a "shape, not
  values" deferral; here it is properly grounded rather than asserted without comparison.
- **Independent, per-channel LFSR state (already the plan — GDS-07 reserves `CUR_DEGREE_PB`/`WV`
  and their own note-timers)** avoids all three melodic channels walking in lockstep, which R203
  (voice-leading/density) separately flags as a masking risk.

## 6. Feature Mapping

FR-1010, FR-1080 (dissonance scoring depends on what this topic's algorithm produces), `IP-0001`
(shipped), `IP-0002` (pulse B/wave — not yet authored).

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds the generation core itself — the scale/mode and motif machinery in `music_engine.py` that every later scheme builds on. Shipped via `IP-0001`-`IP-0003` (`FEAT-1000`, `VERIFIED`) and extended by `IP-1070`'s combinable schemes (`ADS-100`/`FS-107`). Requirements: `FR-1000`/`FR-1010`. Tests: `T3`-`T5` liveness and note-progression checks. Its Markov/L-system survey half is *not* what shipped — that thread was re-examined in `R214` §8 and resolved against a derivation engine; see `R214`'s own trace.

## 7. Related Topics

R202 (rhythm/tempo — the *timing* half of generation, this topic covers *pitch*), R203
(voice-leading across channels once more than one uses this algorithm), R204 (bad-zone scoring
consumes this algorithm's output).
