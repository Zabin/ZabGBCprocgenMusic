# R210 — Tracker Music Formats, Sequencing Techniques & Real-Time Synthesis on GB

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 2, items 22-24 (tracker music formats, music
  sequencing techniques, real-time synthesis on Game Boy)

## 1. Purpose
Ground the vocabulary/technique of "sequencing" against tracker convention, and confirm real-time
(as opposed to only pre-baked) synthesis is an established, not novel, thing to attempt on this
hardware.

## 2. Scope
Tracker format concepts (patterns/orders/effects) and the tracker-effect vocabulary (arpeggio,
vibrato, portamento — detailed further in R216).

## 3. Concepts
- **Tracker format structure**: a *pattern* is a fixed-length grid of rows × channels, each cell
  holding a note/instrument/effect; a *song* is an ordered sequence of pattern references (an
  "order list"), allowing pattern reuse. This structure is what GBT Player's MOD/S3M conversion
  pipeline (R209) operates on directly.
- **Tracker effects** (arpeggio, vibrato, portamento, and others) are per-cell modifiers applied
  on top of a base note — "tracker chiptunes are based on very short looped waveforms which are
  modulated by tracker effects such as arpeggio, vibrato and portamento," dating to 1989-1990
  demoscene musicians [Wikipedia-mirrored Chiptune article](http://www.thefullwiki.org/Chiptune).
- **Real-time synthesis on GB is well-precedented**, not experimental: Nanoloop (R209) is a true
  real-time step-sequenced synthesizer running entirely on GB hardware, not a playback-only
  system — direct existence proof that GB-class hardware can do live sound-parameter computation
  per step/frame, which is exactly Driftune's own premise (MSTR-001 C6).

### Sources
- [thefullwiki.org — Chiptune](http://www.thefullwiki.org/Chiptune)
- [Nanoloop 2.7.9 manual](https://www.nanoloop.com/two/nanoloop27.html) (cross-ref R209)

## 4. Operational Context
Driftune has no pattern/order-list data structure at all — its "sequencing" is entirely emergent
from live generation (R201), not authored-pattern playback. This topic is precedent/vocabulary
grounding, not a structure to adopt.

## 5. Implementation Guidance
- **Do not introduce a pattern-grid data structure** — it would be authoring infrastructure for
  content Driftune deliberately doesn't have (MSTR-001 C6: real-time generation, not pre-baked
  tracks). If a future increment wants a hybrid ("some phrases are semi-authored, generation fills
  the rest"), that is new scope entering via `00-intake`, not an default extension of this
  research.
- **Tracker effects (arpeggio/vibrato/portamento) remain relevant as sound-design techniques**
  (R216) even without a tracker data format — they're describable as small per-tick register
  modulations Driftune's own `engine_tick` could apply, independent of any pattern-grid concept.

## 6. Feature Mapping
Background/vocabulary grounding only.

## 7. Related Topics
R209 (the driver survey this vocabulary describes), R216 (concrete arpeggio/vibrato/portamento
implementation guidance for Driftune's own engine).
