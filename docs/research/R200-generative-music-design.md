# R200 — Generative/Procedural Music Design Encyclopedia

- **Owned by:** `02-research-game-design` (re-scoped for this project: generative-*experience*
  design plays the role game design played for the reference project) · **Status:** ✅ Authored,
  2026-07-21 (grounds GDS-01/03/04)

## Prior art patterns applicable to a real-time, resource-constrained generator

1. **Scale-constrained random walk.** Maintain a "current scale degree" per melodic channel; each
   step, move by a small signed random delta clamped to stay within a chosen scale/mode's note
   set and an octave range. Cheap (one table lookup per note), naturally produces stepwise melodic
   motion, and is exactly the kind of arithmetic that's tractable on SM83 in the "only recompute
   on note-expiry" budget from R100. This is Driftune's baseline melodic technique for the pulse
   channels.
2. **Euclidean rhythm generation.** Distributing `k` onsets as evenly as possible across `n` steps
   (Bjorklund's algorithm) is a standard cheap way to generate rhythmically interesting,
   non-repetitive-feeling patterns from two small integers — a natural fit for a steerable
   "density" parameter (k) at a fixed step count (n), and cheap to recompute (small integer loop)
   when density changes rather than needing to be precomputed/stored.
3. **Markov-chain note transition tables.** A small (e.g. 7×7, one row per scale degree) transition
   probability table read each step is a classic technique, more "directed" than a pure random
   walk. Considered as a v2 upgrade over the random walk (needs a transition table in ROM/WRAM,
   more data than the random-walk's few bytes of state) — noted as a backlog candidate, not
   adopted for v1 (keeps the first increment's data footprint small, per MSTR-001's real-time/
   on-device emphasis over sophistication).
4. **Cellular-automata / L-system rhythm generation.** Common in algorithmic-composition literature
   for evolving patterns over time (a pattern mutates generation-to-generation rather than being
   redrawn from scratch). Relevant to Driftune's "continuously evolving" requirement (MSTR-001
   §1) as a v2+ idea for how the *rhythm* pattern itself drifts over long timescales, distinct from
   per-note pitch selection. Not adopted for v1 — flagged for `00-intake` once the v1 engine ships
   and there's a real baseline to extend.
5. **Wavetable/timbre cycling** (R100's Channel 3 live-rewrite capability) as its own generative
   axis, independent of pitch/rhythm — e.g. slowly cycling or randomly selecting among a small set
   of precomputed 32-sample waveforms as a "texture" parameter.

## Dissonance / "bad zone" measurement approaches (grounds GDS-03's concrete metric)

Candidates surveyed, evaluated for SM83-tractability (must be computable in integer arithmetic,
cheaply, on every note-change event — not full-spectrum psychoacoustic analysis):

- **Interval-class dissonance scoring.** Assign a small dissonance weight per possible interval
  (in semitones, mod 12) between concurrently sounding notes — consonant intervals (unison, 3rd,
  4th, 5th, octave) score low, dissonant ones (minor 2nd, tritone, minor 7th) score high. Summing
  pairwise scores across the currently-sounding channels each tick gives a cheap, table-lookup-only
  running dissonance figure. This is the strongest v1 candidate: it's a 12-entry lookup table and
  an O(channels²) (at most 4×4/2=6 pairs) sum, well within the note-change-event budget.
- **Repetition/staleness detection.** Track a short rolling history (e.g. last N notes per
  channel, or a hash of the last N) and flag "stuck" when the same short pattern repeats beyond a
  threshold. Cheap with a small circular buffer in WRAM; directly addresses MSTR-001's
  "stuck/repetitive" bad-zone criterion.
- **Channel-overload detection.** Count how many channels are simultaneously triggering new notes
  at a rate above a sane ceiling (derived from R100's cycle-budget note: too many notes-per-second
  across too many channels both sounds bad and risks the per-frame budget). A simple rate counter
  per channel, reset each tick window.
- **Full psychoacoustic/spectral dissonance models** (e.g. Sethares' sensory-dissonance curves)
  were surveyed and rejected for v1: they need floating-point partial-frequency analysis, entirely
  impractical on SM83 in real time. Interval-class scoring is the tractable approximation of the
  same underlying idea.

**Recommendation carried to GDS-03:** a combined score — interval-class dissonance (primary),
repetition detection (secondary), channel-overload (tertiary) — each cheap, each already a v1
candidate above, combined into one threshold-checked "bad zone" scalar. GDS-03 must pick the exact
weights/thresholds and the WRAM layout; this research only establishes that all three are
individually SM83-tractable and jointly cover MSTR-001's three named bad-zone symptoms
(dissonance, stuck/repetitive, overloaded channels).

## Input-steering prior art (grounds GDS-03's mapping table)

Prior generative-music toys/instruments (e.g. Brian Eno-style generative systems, Euclidean-
rhythm-sequencer hardware, algorithmic techno tools) commonly expose a small number of orthogonal
knobs: scale/key, tempo, density, and a "which voices are active" mute/solo layer. This maps
naturally onto a GBC controller's small, fixed input surface (4 face buttons + 4 D-pad directions
+ Start/Select) — the reference project's own input model (used for movement/menus) doesn't
transfer, but the general principle that **each control should own exactly one orthogonal
parameter, with no modal "menu" layer required for the core loop** does, and is the recommended
constraint for GDS-03's concrete mapping (avoids needing a settings-menu state machine, keeping
GDS-01's interaction model flat, per GDS-00's note that this project has no game-state-machine
shape to inherit).

## Open items for later research passes

- Whether tempo should be continuous (a WRAM byte, finely steppable) or a small discrete set of
  named tempi (simpler to reason about and to test, per MSTR-001 C9's assert-on-state
  requirement) — flagged to GDS-03/04, not resolved here.
- Long-timescale "evolution" (item 4 above) — deferred to a post-v1 backlog entry once the v1
  engine ships.
