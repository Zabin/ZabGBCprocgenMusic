# R213 — PRNGs, Seed Management & Deterministic Generation

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 4, items 41-43 (pseudorandom number generators,
  seed management, deterministic generation)

## 1. Purpose
Formalize and validate the LFSR-based PRNG already shipped in `IP-0001`, and name the concrete
seed-management options for a future "reproduce a specific run" feature (currently non-goal per
MSTR-001, but the `run-driftune` utility skill/tests already depend on determinism).

## 2. Scope
LFSR PRNG properties, and seed-management patterns (fixed vs. player-chosen vs.
hardware-entropy-derived).

## 3. Concepts
- **Galois LFSR** (already implemented, `music_engine.py`'s `lfsr_step`): an 8-bit shift register
  with XOR feedback on a fixed tap polynomial. Properties: fully deterministic given its seed and
  polynomial (same sequence every time, R201's cited requirement for testability); period bounded
  by register width (an 8-bit maximal-length LFSR has a 255-value period before repeating) — a
  real, known limitation worth naming: Driftune's pulse-A walk will eventually visit a repeating
  256-step LFSR cycle, which interacts with R204's stale-repetition detector (a period-256 LFSR
  cycle is far longer than the 8-note repetition window R204 checks, so this is not currently a
  practical concern, but is the honest reason a *longer* LFSR — 16-bit — would be a strictly
  larger-period upgrade if ever needed).
- **Seed management patterns**: (a) **fixed seed at boot** (Driftune's current choice, `LFSR_SEED
  = 0xA5` constant) — maximally simple, maximally deterministic, but every power-on plays the
  *identical* sequence until player input diverges it, which somewhat undercuts "ever-different"
  (MSTR-001 §1) on a fresh boot specifically; (b) **hardware-entropy-derived seed** (e.g. reading
  the free-running `DIV` timer register at boot, a per-power-on-varying value) — the standard
  cheap "make it look random each run" trick on GB-class hardware, at the cost of an un-reproducible
  boot sequence (bad for regression tests unless the seed is also readable/loggable); (c)
  **player-enterable seed** (out of current scope — no menu/entry UI exists, GDS-01's flat design
  has no such state).

### Sources
- No single external citation for Galois-LFSR-as-PRNG properties (standard, widely-documented
  digital-logic technique, already correctly implemented) — this topic's value is the analysis of
  Driftune's own existing choice and the named alternatives, not a novel external claim.

## 4. Operational Context
`IP-0001` ships option (a), fixed seed — confirmed correct and intentional (MSTR-001 C6:
determinism is for testing, not necessarily for listening-experience variety).

## 5. Implementation Guidance
- **Recommend `IP-0002`+ consider seeding `LFSR_STATE` from `DIV` (`0xFF04`) at boot** instead of
  the fixed `0xA5` constant, **while keeping a fixed-seed override path for `test_rom.py`** (e.g.
  a test can write a known value to `LFSR_STATE` directly after boot, before driving further
  frames, exactly as `test_rom.py` already does for other WRAM fields) — this would make every
  power-on genuinely different (closer to MSTR-001 §1's "ever-different" framing) without
  sacrificing test determinism, since tests control the WRAM value directly rather than relying on
  boot-time randomness. This is a `feature`-type backlog candidate, not decided/implemented here.
- **No action needed on LFSR period** — 255 steps is far longer than any practically-observable
  session length at typical tempos before Select naturally resets it anyway.

## 6. Feature Mapping
`IP-0001` (shipped, fixed-seed choice confirmed intentional); a `DIV`-seeding upgrade is an
unscheduled `feature`-type backlog candidate.

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⚠️ **TRACED — as a recommendation deliberately NOT taken, which is the interesting case.** This topic recommended `DIV`-based boot seeding so each power-on differs. **It was not adopted**: `LFSR_SEED` remains a fixed constant in `music_engine.py`, and `IP-0001` confirmed that choice as intentional. The reason is recorded elsewhere and is load-bearing — `R305` §5 notes that the fixed seed is what makes every `test_rom.py` run a fixed-seed regression run *by construction*, and that adopting `DIV` seeding would require tests to overwrite `LFSR_STATE` post-boot to keep that property. So the topic's forward trace is real but inverted: it grounds a **standing, reasoned rejection** plus a named migration cost, cited by `ADS-100`, `FS-106`, `FS-107`, `GDS-03` and `GDS-04`. The `DIV`-seeding upgrade remains an unscheduled candidate, not an oversight.

## 7. Related Topics
R201 (the algorithm this PRNG drives), R204 (repetition detection's interaction with LFSR period),
R305 (test-design implications of any future non-fixed seeding).
