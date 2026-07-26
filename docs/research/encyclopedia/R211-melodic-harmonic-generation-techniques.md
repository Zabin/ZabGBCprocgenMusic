# R211 — Melody, Bass, Chord & Percussion Generation Techniques

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 3, items 26-33 (rhythm generation [see R202],
  melody generation, chord progression generation, bass line generation, countermelody
  generation, percussion generation, phrase generation, motif development)

## 1. Purpose
Survey concrete generation techniques per musical role, beyond R201's already-adopted scale-
constrained-walk baseline, as named upgrade paths for `IP-0002`+ and post-v1 backlog candidates.

## 2. Scope
Melody (covered by R201, cross-referenced here), chord progressions, bass lines, countermelody,
percussion (cross-ref R115/R202), phrase-level structure, and motif development/variation.

## 3. Concepts
- **Melody generation**: R201 already covers this (scale-constrained random walk, Markov-chain
  upgrade path) — not re-derived here.
- **Chord progression generation**: functional-harmony-rule systems constrain transitions to
  "plausible functional relationships... transitions between tonic, dominant, and subdominant
  regions," and favor "smooth movement between individual voices" (voice-leading) over abrupt
  jumps [search synthesis of functional-harmony chord-generation literature — see Sources]. More
  sophisticated approaches (genetic algorithms trained on real song corpora, ML models) exist but
  need training data/floating-point inference wholly impractical on SM83 — the *rule-based*
  functional-harmony approach (small transition table: tonic→{dominant, subdominant}, dominant→
  {tonic}, etc.) is the SM83-tractable analogue, same "table lookup, not learned model" discipline
  as R201's Markov-chain note.
- **Bass line generation**: no distinct citation found beyond general chord-tone-following
  convention (a bass line commonly tracks the current chord's root/fifth) — treated as an
  engineering convention rather than an over-cited "finding." Directly actionable: once/if a
  chord-progression generator (above) exists, the wave channel's bass role (R207/R114) could
  derive its target note from the current chord's root rather than random-walking independently —
  a concrete v2+ upgrade, not v1 scope.
- **Countermelody generation**: no distinct citation found; conventionally, a countermelody is
  constrained to avoid parallel motion and unisons with the lead voice at each step (a real-time-
  tractable per-step constraint check, not a global optimization) — flagged as a v2+ idea for
  pulse B once/if pulse A and pulse B are made to interact rather than walk independently.
- **Percussion generation**: covered by R115 (noise channel) and R202 (Euclidean rhythm) —
  cross-referenced, not re-derived.
- **Phrase generation & motif development**: the R201-cited generative-music literature
  (Eno-lineage systems, Markov-chain composition) generally operates at the *note* level, not the
  *phrase* level — genuine phrase-level structure (a recognizable 4/8-bar motif that recurs,
  varies, and develops) is a materially harder generative-music problem than per-note generation,
  without a cheap SM83-tractable technique surfaced by this research pass. Named as a **known,
  real gap** rather than asserted solved — flagged to the backlog as a research-gap for a future,
  deeper pass if/when Driftune's roadmap wants recognizable musical "sections" rather than
  continuous ambient drift.

### Sources
- Functional harmony/chord-progression rule systems: search synthesis (multiple sources,
  including a genetic-algorithm chord-progression paper and general functional-harmony
  descriptions) — no single canonical citation; flagged as engineering-convention-grade, not a
  single authoritative source.
- R201's own sources (Eno/Koan, Markov chains) for the phrase-level-gap observation.

## 4. Operational Context
None of chord/bass/countermelody/phrase-generation is implemented — `IP-0001` is pulse-A melody
only (R201).

## 5. Implementation Guidance
- **v1/v2 scope (IP-0002/0003) should not attempt chord-progression-driven harmony** — it's a
  bigger structural addition (a shared harmonic-context WRAM field all channels read) than the
  independent-per-channel-walk model GDS-03 already committed to. Named as a real, larger v3+
  candidate, not silently adopted.
- **Recommend filing the phrase/motif-development gap as a research-gap backlog entry** now,
  rather than pretending R201's note-level techniques already solve it — honest scope statement
  per this skill's own "never overstate a finding" rule.

## 6. Feature Mapping
No current `IP-xxxx` depends on this topic directly; informs future backlog scope only.

## 7. Related Topics
R201 (melody, already adopted technique), R202 (rhythm/percussion), R115 (noise channel), R212
(song-structure/tension — the phrase-level gap this topic names is the same gap that section
covers from the "form" angle), R220 (2026-07-22 — found a cheap song-form-structure partial
answer via horizontal-resequencing/vertical-layering; this topic's motif-recurrence half remains
open, see `BL-0010`'s updated note).

## 8. Addendum — 2026-07-26: Weighted Random Selection (`BL-0037`)

A 115-topic wishlist audit found "weighted random selection" was never independently grounded,
even though Driftune already ships a working example of it — `music_engine.py`'s
`DELTA_TABLE = [0xFF, 0x00, 0x00, 0x01]` (-1, 0, 0, +1, indexed by 2 LFSR bits) makes "no pitch
change" twice as likely as either directional step, a genuine weighted (not uniform) random walk
shipped since `IP-0001`/`IP-0002` with no citation backing it until now. Same
"implementation-outpaced-its-own-documentation" pattern already named by `BL-0025`/`BL-0026`/
`BL-0029` — a retroactive grounding gap, not a missing capability.

**A lookup-table-driven weighting mechanism is a real, prior-art technique for exactly this
purpose.** A patented method for "generating random weighted musical choices" describes generating
a pseudo-random number, then applying "a weighting method associated with each pattern... to
modify the random number, with patterns potentially having a weighting curve lookup table" (US
patent 6121533, general prior-art description found via search). This is structurally identical
to `DELTA_TABLE`'s own design: an LFSR-derived index used to select from a small table whose entry
*distribution* (not just its values) encodes the desired bias — the table itself, not extra
arithmetic, is what makes the selection non-uniform.

**Biased/weighted random walks specifically for real-time pitch assignment are a named, precedented
melody-generation technique**, distinct from unweighted note-by-note walks: real-time pitch
generation can use "a note-by-note random walk sequence" (unweighted, 'drunk' mode) or a
weighted/contoured variant that "applies the random walk sequence to onsets and interpolates
between them" (general random-walk-melody-generation prior art found via search). Driftune's own
`DELTA_TABLE` sits in the same family as the simpler "drunk mode" but with an explicit bias toward
stasis (repeated 0 entries) rather than a uniform step distribution — a deliberate, if previously
uncited, design choice.

### Addendum sources
- General prior-art description of a lookup-table weighting mechanism for random musical choices
  (patent-literature search finding) and of "drunk"/biased random-walk melody generation (general
  procedural-melody-generation prior art) — no single primary source independently fetched this
  pass (WebFetch unavailable for every attempted primary source this session); flagged **needs
  fetch-verification** if a future pass wants primary-document depth.

### Addendum implementation guidance
- `DELTA_TABLE`'s existing 2-of-4-entries-are-zero bias is now retroactively grounded as a
  standard lookup-table-weighting technique, not an ungrounded implementation detail — no code
  change implied, this closes a documentation gap only.
- **Any future generation scheme wanting a different weighting shape** (e.g. `BL-0020`'s Scheme
  W/E precedent, or a Holiday-preset's stepwise-motion bias per `R219`'s addendum) should reuse
  this exact mechanism — a differently-weighted lookup table, not new arithmetic — consistent with
  this project's established "extend the table, not the mechanism" pattern (`CHMIX_MASKS`,
  `ARPEGGIO_OFFSETS`, `MOTIF_TABLE`).
