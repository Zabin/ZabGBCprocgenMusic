# GDS-04 — Domain Model

- **Level:** GDS-04 of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26
- **Upstream:** [GDS-01 Concept of Interaction](01-concept-of-play.md),
  [GDS-02 System Context](02-system-context.md), [GDS-03 Architecture](03-architecture.md),
  research `R201`/`R202`/`R203`/`R204`/`R207`/`R211`/`R213`/`R214`/`R216`/`R220`
- **Downstream:** GDS-05 (capability FRs elaborate these entities' behaviors),
  [GDS-07 Data Model](07-data-model.md) (already authored — owns *where* each entity lives)

## §0 What this level is, and the line it holds against GDS-07

This level describes **what the engine's entities are**: their meaning, attributes, lifecycle,
relationships, and the invariants binding them. GDS-07 already describes **where they live** —
WRAM addresses, byte packings, table layouts. That split is load-bearing here because GDS-07 was
authored first (see GDS-02 §0 on this project's out-of-order ladder history), so the temptation to
restate its address map is real. This document names no WRAM address and no byte layout. Where an
entity's storage matters, it points at GDS-07 and moves on.

Like GDS-02, this level is authored against a **real, shipped engine** — the entity set below was
read out of `music_engine.py` as it actually stands, not synthesized forward. The domain has grown
well past GDS-01's original sketch: six packages since (`IP-1060`/`IP-1061`/`IP-1070`/`IP-1080`/
`IP-1090`/`IP-1100`) each introduced entities the ladder never named, plus `IP-1110`'s display
entities. Naming them here is the point of authoring this level now rather than earlier.

## §1 The steering-index family

The five values the listener steers are **one coherent entity family**, not five unrelated
variables. No existing document says this, and it matters: every member shares the same semantics,
and treating them as a family is what makes the writer analysis in §1.2 legible.

| Index | Domain meaning | Cardinality |
|---|---|---|
| `TEMPO_IDX` | which of 8 tempo steps (60→180 BPM) sets the note-step period | 8 |
| `OCTAVE_IDX` | which of 4 octave roots (C3…C6) is the walk's home register | 4 |
| `SCALE_IDX` | which of 4 scales/modes (major, minor, dorian, pentatonic) constrains pitch | 4 |
| `DENSITY_IDX` | which of 8 onset densities (k = 2…12 hits per 16-step grid) drives rhythm | 8 |
| `CHMIX_IDX` | which of 8 ensemble presets is active — see §1.3, it means three things | 8 |

**Shared semantics (all five):**

- **Bounded and wrapping.** Each is an index into a fixed table, never a free value; stepping past
  the end wraps to 0. Cardinalities are powers of two precisely so the wrap is a bitmask rather
  than a comparison — a domain shape chosen for the SM83's instruction set (`R302`), recorded here
  because it explains why "add a 5th scale" is not a free change.
- **Edge-triggered when steered.** A held button steps the index exactly once (GDS-01, GDS-03 §3).
- **Reset to a known-good preset.** Select restores all five to the boot preset (§4).
- **Displayable.** Since `IP-1110`, each has a bar-height indicator on the visualizer. This is a
  genuinely new domain property — before it, these were internal state with no representation.

### §1.1 Effective vs. nominal values

`OCTAVE_IDX` is nominal, not effective: each channel applies its own **octave delta** to it (the
wave channel sits one index lower, floored at 0, per `R207`'s bass-role finding), and the wave
channel's register formula is itself an octave lower for identical register values (`R108`/`R114`)
— so the wave voice lands two octaves below the pulse voices from one shared index. Similarly
`TEMPO_IDX` is modulated per channel by a **tempo multiplier** (the wave channel moves at half
rate). The domain entity is the shared nominal index; the per-channel derivation is a channel
attribute (§2), not a separate index.

### §1.2 Writers — and the one contract that governs them

Three of the five indices have exactly one writer. Two have three, and that is the single most
important relationship in this domain model:

| Index | Writers |
|---|---|
| `OCTAVE_IDX` | D-pad Left/Right; Select-reset |
| `SCALE_IDX` | A button; Select-reset; **style application** (`IP-1080`) |
| `CHMIX_IDX` | Start; Select-reset |
| **`TEMPO_IDX`** | D-pad Up/Down; Select-reset; **style application** (`IP-1080`); **song-form phase transition** (`IP-1100`) |
| **`DENSITY_IDX`** | B button; Select-reset; **style application** (`IP-1080`); **song-form phase transition** (`IP-1100`) |

**The governing contract: last write wins, no special-casing.** When two mechanisms write the same
index on the same frame, whichever runs later in the frame's fixed call order simply wins; neither
mechanism inspects, defers to, or coordinates with the other. This was established as a deliberate
contract by `FR-1240` (for the D-pad-vs-style case) and extended verbatim by `FR-1320` (for the
song-form case), and it is **adversarially confirmed, not merely reasoned**: `VR-1100` forced
guaranteed same-frame collisions between a Start-press style application and a song-form phase
transition at all three cycle-internal phase boundaries, and found song-form's write wins cleanly
every time with neither mechanism's own bookkeeping corrupted.

Recording this at domain altitude matters because the alternative designs (priority ordering,
write locks, "manual input suppresses autonomous writes for N frames") are all things a future
increment might reach for, and this project has deliberately not done any of them. The domain
treats these indices as **shared mutable state with an ordering discipline**, not as owned state.

### §1.3 `CHMIX_IDX` means three things

`CHMIX_IDX` is the most overloaded entity in the domain. One index simultaneously selects:

1. **The active-channel set** — which of the four channels sound at all (`IP-9010`; a 4-bit mask).
2. **The per-channel generation scheme** — Scheme W or Scheme E, per pitched channel (`IP-1070`,
   riding spare bits of the same mask per `ADR-0001`).
3. **The style row** — a coordinated tempo/density/scale/duty-bias bundle applied on change
   (`IP-1080`, a parallel table keyed by the same index).

These are three genuinely independent lookups sharing one key, which `ADS-101` §2 explicitly
designed as independent tables rather than one merged structure. The domain consequence, worth
naming plainly: **`CHMIX_IDX` is not "the channel mix" — it is the ensemble-preset identity**, and
its three consumers are free to disagree about what any given preset means. The known cost is
recorded as `BL-0032`/`BL-0033`/`BL-0041`/`BL-0048`: several combinations the mechanisms support
are unreachable because no shipped preset row exercises them.

A second, subtler consequence: the three lookups **do not share timing**. Channel-activity and
scheme-select take effect at the channel's next note onset (`FR-1190`); the style row applies
immediately on the press (`FR-1240`). One index, two different latencies — deliberate, but a real
domain asymmetry a reader would not guess.

## §2 Channel

A **channel** is a sound-producing voice with its own independent generation state. There are
four, and they are not interchangeable — three are *pitched*, one is *percussive*, and the domain
treats them differently.

**Pitched channels** (pulse A, pulse B, wave) each carry:

- a **current scale degree** (0–7, the position within the active scale's 8-degree table — never
  an absolute pitch; pitch is derived from degree + scale + effective octave);
- a **note timer** counting down to the next onset;
- an **LFSR state**, its own private pseudo-random stream (§6);
- a **repetition counter** feeding stale-detection (§5);
- an **arpeggio state** and, for the pulse channels, a **duty register** (`IP-1060`);
- a **scheme state**, packing this channel's Euclidean-pattern step and motif step (`IP-1070`);
- fixed structural attributes: its **octave delta** and **tempo multiplier** (§1.1), and its
  **role** — pulse A/B carry melody, wave carries bass/timbre (`R207`).

**The noise channel** has no pitch, no scale degree, and no LFSR walk. It carries only a step
index into a Euclidean rhythm pattern and its own note timer. It participates in density and
overload (§5) but not in dissonance or motif.

**Why three pitched channels, not one polyphonic voice:** the PSG has no polyphony per channel
(`R108`). Chords are approximated by arpeggiation within a channel (`R216`, `IP-1060`) and by
ensemble across channels. That constraint is why "voice" and "channel" are the same entity here,
where in most music software they would not be.

## §3 Generation scheme

A **generation scheme** is a channel's strategy for deciding *when* its next note fires and *which*
degree it moves to. Two exist, and a channel runs exactly one at a time — never a blend
(`FR-1180`; `ADS-100` was explicit that "combination" means different channels running different
schemes, at ensemble level).

| | **Scheme W** (walk) | **Scheme E** (Euclidean + motif) |
|---|---|---|
| Onset timing | fixed per-tempo timer reload | gated by a Euclidean pattern sized by `DENSITY_IDX` (`R202`) |
| Degree selection | LFSR-picked small signed delta, weighted toward staying/stepping (`R201`) | steps through a **motif** — a fixed sequence of absolute degree targets |
| Character | continuously drifting, never repeating | patterned, recognizable, recurring |

Scheme assignment is an attribute of the (channel, `CHMIX_IDX` preset) pair, not of the channel
alone — it is re-derived from the preset's mask every tick rather than stored (`NFR-1070`).

### §3.1 Motif and motif variant

A **motif** is an 8-step sequence of absolute scale degrees (not deltas — an implementation-shaped
choice recorded in `IP-1070`, but domain-visible because it means a motif is a *destination
sequence*, so it sounds the same regardless of where the channel was before it started).

A **motif variant** is one of four alternative motifs sharing the same start and end degree with
differing middle contour, so switching between them reads as *development of one phrase* rather
than an unrelated new phrase (`IP-1090`, grounded in `R214` §8's "recurrence dominates, switches
are occasional" finding). The active variant is engine-wide, not per-channel (a v1 scoping
decision, `ADS-102` §9).

**Variant lifecycle:** the variant may change *only* at a motif-cycle boundary — the frame a
channel's motif step wraps 7→0 — never mid-phrase. At each boundary a weighted draw retains the
current variant with probability 3-in-4 and advances to the next otherwise. This is a genuine
domain rule, not an implementation detail: mid-phrase variant switching would break the "same
phrase, developing" character the entity exists to produce.

## §4 Preset, style row, and the index-0 invariant

A **preset** is a complete known-good assignment of all five steering indices, plus clean
derived state. It is the engine's fixed point: boot lands on it, and Select returns to it (§7).

A **style row** is a coordinated bundle — target tempo, density, scale, and duty-cycle bias —
applied atomically when `CHMIX_IDX` changes (`IP-1080`). Where the preset is *the* baseline, style
rows are *alternative* coordinated destinations, one per ensemble preset.

### §4.1 The index-0 invariant — load-bearing, and proven so

**Every table keyed by a steering index must have, at index 0, a row exactly equal to the shipped
boot preset's corresponding values.**

This binds `STYLE_TABLE` row 0 (`FR-1260`), `MOTIF_TABLE` variant 0 (`FR-1300`), `SONG_TABLE`
phase 0, and `CHMIX_MASKS` preset 0 (all four channels active, all Scheme W). It exists so that
boot and Select-reset land on identical, deterministic, known-good state no matter how many
index-keyed mechanisms the engine accumulates — each new mechanism inherits a neutral element
rather than perturbing the baseline.

**It is not a stylistic guideline.** `IP-1100`'s own implementation initially gave phase 0 a
deliberately distinct "INTRO identity" that diverged from the boot preset; that broke **ten
pre-existing tests** across four unrelated suites (`T2`, `T5`, `T7`, `T13`, `T15`) in one change,
and was reverted. The invariant is recorded here at domain altitude precisely because it is the
kind of rule each new mechanism's author is tempted to treat as optional, and the tree has already
demonstrated once what that costs.

#### Amendment 2026-08-20 — the invariant was two rules under one name; one of them is released

`ADS-108` §11.5 (`ADR-0004`) found that the paragraphs above conflate two distinct claims, and that
downstream design work had been binding itself to the weaker one on the strength of the stronger
one's evidence. They are separated here:

- **(a) The fixed-point rule — STANDS, unchanged and load-bearing.** *Index 0 of every
  steering-index-keyed table equals the boot preset's corresponding values, so that boot and
  Select-reset land on identical, deterministic, known-good state no matter how many index-keyed
  mechanisms the engine accumulates.* This is what the statement in bold above actually says, and it
  is what the `IP-1100` regression actually proved: phase 0 diverging from the boot preset broke
  boot and Select-reset's agreement **with each other**, not their agreement with any historical
  recording. Every new index-keyed table still inherits this without exception.
- **(b) The historical-no-regression rule — RELEASED.** *The boot preset's audible result must never
  differ from what previously shipped.* This is a different claim, never independently justified at
  this altitude, which had accumulated (a)'s authority by proximity — and which by 2026-08 had
  become the binding constraint on the project's largest tracked quality defect (`BL-0119`), forcing
  harmonic coordination to be designed as a parallel scheme beside the default rather than as the
  default. The project owner released it explicitly on 2026-08-20: *"Don't hold the preset 0 to an
  arbitrary standard, it was developed by you at a previous iteration… I'd like to get to a pleasant
  sounding music as soon as possible."*

**Practical effect.** A mechanism may now change what the ROM *sounds like* at boot, deliberately
and on the record. It still may not give index 0 a row that disagrees with the boot preset — a table
whose index 0 diverges from `PRESET_*` remains a defect, exactly as before. Where the boot preset's
own values change, every index-0 row changes with them, in the same package, or (a) is violated.

## §5 Bad-zone state

The **bad zone** is a derived judgement about whether the music has drifted somewhere unpleasant.
It is not a mode the engine enters — generation never stops or changes shape — it is a set of
flags that bias generation and swap the visualizer palette.

Three independent detectors, each with its own threshold, plus a combined flag:

| Flag | Detects | Domain basis |
|---|---|---|
| `DISSONANT` | simultaneously-sounding degrees form harsh intervals | interval-class roughness weights, `R204`/Helmholtz |
| `STUCK` | a channel repeats the same degree too long | repetition as a listener-perceptible failure, `R204` |
| `OVERLOAD` | too many onsets across all channels in a rolling window | density-as-fatigue, `R204` |
| `COMBINED` | logical OR of the three | the single signal the visualizer consumes |

**Two domain properties worth stating explicitly, because both have caused real confusion:**

1. **Recovery is autonomous, not input-gated.** When a flag is set, each channel biases its own
   next-degree choice away from the offending behavior *by itself* — the listener need not press
   anything (`IP-0007`, an explicit correction to GDS-01's original Select-only framing). Select
   remains available as an immediate escape, but it is not the recovery mechanism.
2. **Flags are read one frame stale by the channels that act on them.** Bad-zone scoring runs
   after all channels have generated within a frame, so a channel's override decision uses the
   *previous* frame's flags. This is a real domain-visible timing property, not a bug — but it is
   subtle enough that a test in `IP-1090`'s suite sampled the flags on the wrong side of the tick
   and produced a false failure that only surfaced months later when `IP-1100`'s density changes
   shifted the onset trajectory. Recorded here so the next reader does not rediscover it the same
   way.

## §6 Randomness

Each pitched channel owns a private **8-bit Galois LFSR**. Three properties are domain-relevant:

- **Per-channel, independently seeded** — so the three melodic walks decorrelate rather than
  moving in lockstep (`R203`'s voice-leading/masking finding). One shared stream would make the
  ensemble sound like one instrument.
- **Reseeded from the free-running divider on every boot and every Select** (`R213`), so reset
  gives a genuinely different melodic starting point rather than replaying an identical sequence
  — "reset and randomize," not merely "reset."
- **Deterministic given a seed**, which is what makes headless testing tractable at all
  (`MSTR-001` C6: determinism as a testing tool, not a listening promise).

The LFSR is reused, not duplicated, by every mechanism needing a weighted draw — notably
`IP-1090`'s motif-variant selection, which draws from the channel's own otherwise-idle stream
while running Scheme E rather than introducing a second randomness source (`NFR-1110`).

## §7 Song-form phase

A **song-form phase** is a named macro-section of a listening session: intro, build, peak,
breakdown, cycling indefinitely (`IP-1100`, grounded in `R220`'s parameter-envelope finding).
Each phase carries target values for `TEMPO_IDX` and `DENSITY_IDX` and a duration in frames.

**Lifecycle:** a frame counter counts down; on reaching zero the phase advances (wrapping) and the
new phase's targets are written to the two indices immediately, on that same frame. Fully
autonomous — no input required, and no input can steer it (a listener who has manually drifted
tempo will see the next transition overwrite that drift, per §1.2's contract).

**The phase entity is deliberately disjoint from bad-zone state and from motif-variant state** —
it neither reads nor writes any field either mechanism owns (`ADS-103` §2), which is what makes
"song-form is unaffected by bad zones, and vice versa" true by construction rather than by
careful coordination.

## §8 Settings indicator

An **indicator** is a display-only entity: one visualizer cell bound to one steering index,
rendering that index's current value as a proportional bar height (`IP-1110`). Five exist, one per
index family member (§1).

Domain-relevant properties: indicators are **strictly derived** — pure functions of state they
never write (the read-only-visualizer invariant, GDS-03 §1); they are **recomputed every frame**
rather than event-driven, so they need no invalidation logic; and they carry **no state of their
own**. GDS-08 owns their composition and layout. They are named here because "the engine's state
is now observable to the listener" is a genuine change in the domain, not merely a rendering
detail — before `IP-1110`, a listener could not tell what any index was set to.

## §9 Entity relationships (summary)

```
CHMIX_IDX ──selects──> active-channel set ──gates──> Channel (sounds or silent)
     │
     ├──selects──> per-channel Generation Scheme ──drives──> onset timing + degree choice
     │                                    │
     │                                    └─(Scheme E)──> Motif ──varies via──> Motif Variant
     │                                                       ▲ (weighted draw at cycle boundary)
     └──selects──> Style Row ──writes──> TEMPO_IDX, DENSITY_IDX, SCALE_IDX, duty bias

Song-Form Phase ──(on transition, autonomously)──writes──> TEMPO_IDX, DENSITY_IDX

TEMPO_IDX/OCTAVE_IDX/SCALE_IDX/DENSITY_IDX ──parameterize──> every Channel's generation
Channel onsets ──feed──> Bad-Zone detectors ──bias──> subsequent degree choices
                                            └──drive──> visualizer palette
All five indices ──render as──> Settings Indicators (read-only)
Preset ──restores──> all of the above (Select / boot)
```

## §10 Open Questions

1. **Should the motif variant be per-channel rather than engine-wide?** `ADS-102` §9 scoped it
   engine-wide for v1 on the grounds that only one channel runs Scheme E under any shipped preset
   — a premise that stops holding the moment `BL-0032`'s preset-data work lands a multi-Scheme-E
   preset. Genuinely open; owner `03-architecture-design-synthesis` (a future ADS), triggered by
   that preset work rather than by a date.
2. **Should `SCALE_IDX` and duty bias join the song-form phase envelope?** Phases currently move
   only tempo and density. `ADS-103` §9 named this as a natural v1.1 extension; nothing requires
   it. Owner: `03`/`04` when a future increment picks up style-drift.
3. **Is "last write wins" (§1.2) the right long-term contract for the shared indices?** It is
   simple, verified, and has caused no observed defect — but it means a listener's manual tempo
   change can be silently overwritten seconds later by an autonomous phase transition, which is a
   *listener-experience* question this level cannot settle from evidence. It has never been
   content-reviewed as such. Owner: `09-content-review`, or `01-vision` if it turns out to bear on
   the steering promise GDS-01 makes.
4. **Does the domain need a "good-state snapshot" entity at all?** GDS-01/the original ladder
   sketch named one, on the assumption that recovery would restore a previously-captured good
   state. The shipped design took a different route — recovery biases generation in place, and
   Select restores the *fixed* preset rather than a captured snapshot — so no snapshot entity was
   ever built. Recorded here as a deliberate non-entity rather than an omission; reopening it
   would be a `01-vision`-level change to what "recover" means.

## Merge gate

- [x] The previous level's gate (GDS-02) was verified closed before this level started — its own
      prose records "Gate: closed 2026-07-26. Next unauthored level: GDS-04 (Domain Model)."
- [x] Entities read out of the shipped `music_engine.py` directly, not inferred from downstream
      docs — the steering-index cardinalities, channel attribute tuple, scheme split, motif
      variant shape, bad-zone thresholds, and song-form phase structure all come from source.
- [x] No production code, and **no WRAM address or byte layout anywhere** — GDS-07's line held
      deliberately (§0).
- [x] No new research claims originated — `R201`/`R202`/`R203`/`R204`/`R207`/`R211`/`R213`/`R214`/
      `R216`/`R220` are cited for grounding already established; §10's four Open Questions are
      routed to owners rather than answered.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md`'s stage-03 row updated together.

**Merge decision.** No text moves out of `Claude.md`/`memory.md` — neither carries domain-model
content today (they carry *layout* and *how-to-change-it* content, which is GDS-07's and their own
respectively). This level is additive: it is the first place the entity set is described as a set,
and three statements exist here and nowhere else in the tree — the steering-index **family** and
its writer analysis (§1.2), the **index-0 invariant** stated as a cross-cutting rule rather than
four separate per-table requirements (§4.1), and the **one-frame-stale bad-zone read** (§5.2).
Those three are this level's genuine contribution; the rest synthesizes what was scattered across
`ADS-100`-`ADS-104` and the `FS-1xx` specs into one coherent picture. GDS-07 gains a pointer to
this level for entity *meaning*, and keeps sole authority over entity *location*.

**Gate:** closed 2026-07-26. Next unauthored level: GDS-05 (Functional Requirements) — though see
GDS-03's own note that GDS-05/06 were superseded in ordering by a direct `04-requirements-
engineering` pass on this from-scratch increment; the next level authored may therefore be GDS-06
or GDS-08 depending on what the pipeline actually needs.
