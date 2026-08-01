# R216 — Sound Design Techniques: Timbre, Arpeggio, Vibrato, Portamento & Percussion Synthesis

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 5, items 57 (pulse waveform design — cross-ref
  R108/R113), 60 (envelope design — cross-ref R113), 61-68 (instrument abstraction, timbre
  variation, arpeggio, vibrato, portamento, duty cycle usage, chiptune drum synthesis,
  hardware-friendly effects)

## 1. Purpose
Concrete, cited sound-design technique guidance for `IP-0002`/`IP-0003`'s channel behavior, one
level more specific than R201's algorithm-level treatment.

## 2. Scope
The classic tracker-effect vocabulary (arpeggio/vibrato/portamento), duty-cycle usage, and
chiptune percussion synthesis — each evaluated for direct SM83 applicability.

## 3. Concepts
- **Arpeggio-as-polyphony**: the single most load-bearing chiptune technique for a channel-
  starved chip — "heavy use of ultra-fast arpeggios to emulate chords of three or four notes on a
  single channel" [thefullwiki.org — Chiptune](http://www.thefullwiki.org/Chiptune). Mechanically:
  cycle a channel's frequency register rapidly (every few frames) among 2-3 notes of an implied
  chord — cheap (a 2-3-entry table, a fast sub-tick counter), and directly actionable for
  Driftune's pulse channels without any new hardware capability.
- **Vibrato**: periodic small pitch modulation — a low-frequency oscillator (e.g. a small
  triangle-wave table) added to/subtracted from the current note's frequency register each frame
  or few-frame interval. Cheap (one small table, one running phase counter per channel).
- **Portamento**: a glide between two pitches rather than a discrete jump — implemented as a
  per-frame frequency-register step from the old note's value toward the new note's value over N
  frames, rather than writing the new value immediately on note-onset. Slightly more state (a
  "glide target" and "glide remaining" per channel) than Driftune's current instant-onset model.
- **Duty cycle** (pulse channels' `NR11`/`NR21` high bits, 12.5/25/50/75%): a genuinely audible
  timbre switch with zero additional data cost (it's already a register Driftune writes) —
  "square wave (a symmetrical pulse pattern producing only odd overtones)" is one of several
  available configurations [thefullwiki.org — Chiptune](http://www.thefullwiki.org/Chiptune) (also
  cross-ref R108). Currently fixed at 50% (`0x80`) for pulse A — trivially could become a steerable
  or per-note-varying parameter.
- **Chiptune percussion synthesis**: "basic percussion, often generated from white noise going
  through an ADSR envelope" [thefullwiki.org — Chiptune](http://www.thefullwiki.org/Chiptune) —
  directly confirms R115's noise-channel-with-fast-decay-envelope recommendation from independent
  chiptune-genre convention, not just hardware-capability reasoning.

### Sources
- [thefullwiki.org — Chiptune](http://www.thefullwiki.org/Chiptune)
- Cross-references: R108 (duty cycle register), R113 (envelope mechanics), R115 (noise-channel
  percussion recommendation, now doubly confirmed).

## 4. Operational Context
`IP-0001` uses a fixed 50% duty, no arpeggio/vibrato/portamento — none of these techniques are
implemented yet.

## 5. Implementation Guidance
- **Arpeggio is the single highest-value technique to add for `IP-0002`+**: it directly extends
  R211's "no chord-progression support" gap into something achievable *without* the bigger
  shared-harmonic-context architecture R211 SS5 flagged as out of v1 scope — a single channel can
  *imply* harmony via fast arpeggiation without any cross-channel coordination at all. Recommend
  filing this as a concrete, scoped `feature`-type backlog entry for post-`IP-0002` consideration.
- **Vibrato/portamento are lower-priority polish** — real, cheap, and correctly chiptune-idiomatic,
  but add per-channel state for a subtler effect than arpeggio's chord-implying power. Reasonable
  `IP-0004`+/backlog candidates, not urgent.
- **Making duty cycle a steerable or degree-linked parameter** (e.g. duty cycle varies with scale
  degree, or becomes an 8th input-mapped parameter if a spare control is ever found — R206 already
  flagged GBC has none spare) is a cheap, no-new-register-cost texture variation for a future
  content-tuning pass.

## 6. Feature Mapping
`IP-0002`+ (arpeggio, duty-cycle variation — unscheduled `feature`-type backlog candidates),
R115 (percussion envelope, already recommended there, now double-confirmed).

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** The tier's most direct research→feature chain. Sound-design techniques (arpeggio, duty-cycle variation, vibrato, portamento) became `FEAT-1060`/`FS-106` and shipped as **two** packages — `IP-1060` (arpeggio + duty cycle) and `IP-1061` (vibrato + portamento), both `VERIFIED`. Also cited by `ADS-100`, `ADS-101` and `GDS-04`. Requirements: `FR-1130`-`FR-1170`, `NFR-1040`/`NFR-1050`. Tests: `T10`-`T12`.

## 7. Related Topics
R108 (duty-cycle/envelope registers), R113 (envelope timing), R115 (noise percussion), R211
(the chord-progression gap arpeggio partially answers without new architecture).
