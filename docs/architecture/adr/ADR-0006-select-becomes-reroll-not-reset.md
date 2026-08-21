# ADR-0006 — Select Becomes "Reroll", Not "Reset": New Material, Kept Settings

- **Date:** 2026-08-21 · **Status:** Accepted ·
  **Amends the behavior established by:** `IP-0001`/`IP-0005` (the full-reset scope) and
  `IP-0007` (the `DIV` reseed half) ·
  **Narrows:** [`GDS-04` §4.1](../04-domain-model.md)'s fixed-point invariant — see §4.1's own
  second dated amendment, authored alongside this record ·
  **Closes on the record:** `R217` §3's "song regeneration" research gap ·
  **Source:** the project owner's own direct instruction, 2026-08-21.

## Context

### What Select does today, and where each part of it came from

`FR-1070` mandates that a Select rising edge do three unrelated things at once:

1. **Reload** all five steering indices (`TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`,
   `CHMIX_IDX`) to the boot preset.
2. **Clear** every bad-zone field (`BAD_ZONE_FLAGS`, `DISSONANCE_SCORE`, all `STALE_COUNT_*`,
   `ONSET_WINDOW_COUNT`).
3. **Reseed** each pitched channel's LFSR from the free-running `DIV` register (`IP-0007`, `R213`).

Only the third was ever designed as its own idea. Parts 1 and 2 date from `IP-0001`/`IP-0005`,
when Select was the engine's **only** escape from a bad zone: nothing detected a bad zone
autonomously, nothing recovered from one, so "put everything back to the state we know sounds
acceptable" was the entire recovery strategy and reloading the indices was a necessary part of it.

### The premise that supported it stopped holding in 2026-07, and nothing acted on that

`IP-0007` made bad-zone recovery **autonomous** (`MSTR-001` C5 amended v1.1, `GDS-01` step 4): the
engine biases its own generation out of dissonant, stuck and overloaded states every frame, with no
input required. From that moment, Select stopped being the only way out — and the project *noticed*.
`Claude.md` has said so in prose since that day: *"Select remains available as a manual 'reset and
randomize' override, but is no longer the only way out."* `GDS-04` §5 says it too: *"Select remains
available as an immediate escape, but it is not the recovery mechanism."*

**Both documents recorded the supersession and neither re-examined the mechanism it superseded.**
The index reload survived thirteen months of increments as a vestige of a design constraint that had
already been lifted. This is the exact shape `07-implementation-planning`'s amended collision &
obsolescence sweep question 3 exists to catch, and it is one of the two real cases that amendment
cites by name.

### What the reload actively costs, which is the part that makes this urgent rather than tidy

Since `IP-0001` the engine has grown five steerable parameters, a settings-indicator row that makes
their values visible (`IP-1110`), style presets, and — this month — a harmonic layer whose character
depends heavily on `SCALE_IDX`. A listener who has spent a minute dialling in a tempo, an octave, a
mode and a density now has, as the **only** control for "give me different music," a button that
throws all four away. The one action a listener is most likely to want mid-session is welded to the
one action that destroys their session.

### The user's instruction

Verbatim, 2026-08-21:

> "The select-reset does not need to bring it back to the boot default either, just course correct
> from a bad zone."

Asked whether there was a better use for the button, he approved folding in **reroll**.

## Decision

**Select becomes a reroll: new material, kept settings.** On a rising edge it shall:

- **Reseed** each pitched channel's LFSR from `DIV` — unchanged from today (`IP-0007`, `R213`).
  This is what makes the material genuinely new rather than a restart of the same walk.
- **Clear** `BAD_ZONE_FLAGS`, `DISSONANCE_SCORE`, every `STALE_COUNT_*`, and
  `ONSET_WINDOW_COUNT` — unchanged from today. This is the "course correct from a bad zone" half
  the user named, and it remains unconditional (not gated on the bad zone being flagged).
- **Not reload** `TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX` or `CHMIX_IDX`. **The
  listener's settings survive the press.**

Every other field `init_engine` currently initializes on the Select path — note timers, current
degrees, the chord context, the arpeggio caches, blend state, song-form state — is **derived
generation state, not listener intent**, and continues to be re-established exactly as it is today.
The line this decision draws is precisely: *state the listener chose* survives; *state the engine
wandered into* does not.

### Why the button, and why this is not a scope change

`R217` §3 parked "song regeneration" as **genuinely unaddressed**, on the reasoning that
*"GDS-01's flat design has no menu state at all, so there is currently no UI surface for… explicitly
'regenerating'"*, and routed any such scope back through `01-vision` because *"a menu state is a
scope change to GDS-01's flat interaction model."*

**That reasoning is correct and does not apply here.** It rules out a *menu*; it says nothing about
a *button*. A button press adds no state, no mode, no screen and no navigation — the engine remains
in exactly one state, **running**, before and after. `GDS-01`'s flat single-running-state model is
untouched, `MSTR-001` §4's "no pause, no menu, no save" non-goals are untouched, and no
`01-vision` change is required or requested. `NFR-1090`'s established principle (*reuse an existing
control rather than requesting a distinct one*) is satisfied in its strongest form: this reuses a
control that already exists **and** retires a behaviour, rather than adding one.

Recorded explicitly, with `R217` receiving a matching addendum, so the gap closes **on the record**
rather than remaining listed as unaddressed while the capability quietly ships.

## Consequences

### The fixed-point invariant must be re-stated, and is — it must not break by omission

`GDS-04` §4.1(a) currently reads: *"Index 0 of every steering-index-keyed table equals the boot
preset's corresponding values, so that boot and Select-reset land on identical, deterministic,
known-good state."* **Under this decision, boot and Select genuinely diverge**, so that sentence
stops being true as written.

It is being **narrowed, not released**, and the narrowing is the point of recording it here rather
than letting a downstream package discover the contradiction:

- **What the invariant was actually protecting** is that every index-keyed table has a coherent
  neutral element at index 0, so each new index-keyed mechanism inherits the baseline rather than
  perturbing it. `IP-1100`'s ten-test regression proved exactly that: giving `SONG_TABLE` phase 0 a
  distinct "INTRO identity" broke `T2`/`T5`/`T7`/`T13`/`T15` in one change. **That protection is
  untouched by this decision** — index 0 of every table still equals the boot preset's values, and
  a table whose index 0 diverges from `PRESET_*` remains a defect.
- **What changes is only which event lands on the fixed point.** It was *boot and Select*; it is
  now *boot alone*. Select no longer visits the fixed point because Select no longer sets the
  indices at all — it does not land somewhere *else*, it stops being an event about the indices.
- **The `IP-1100` regression is still binding evidence**, and this decision does not weaken it. Its
  ten failures were caused by a *table* disagreeing with the boot preset, which is still forbidden.

`GDS-04` §4.1 carries this as its own second dated amendment, in the same voice as the 2026-08-20
one, so a reader meets the current statement rather than a superseded one plus a correction.

### Boot remains deterministic and known-good

This decision changes **only** the Select path. Boot still runs the identical `init_engine`,
including the index writes, so it still lands on the known-good preset every time; the LFSR reseed
from `DIV` on boot is unchanged and is the same non-determinism the engine has deliberately carried
since `IP-0007` (`MSTR-001` C6: determinism is a testing tool, not a listening promise — and the
suite's fixtures already accommodate a `DIV`-seeded boot). **Nothing about the boot path is touched,
and any implementation that changes boot behaviour has misimplemented this decision.**

### Derived state that reads a steering index must be re-established from the *listener's* value

This is the one genuine implementation hazard, and it is the mirror of the defect class `VR-1130`
found in `BLEND_STEP` and `FR-1630` was written to prevent. Several fields are re-established on
the Select path *by deriving them from a steering index*:

- the **arpeggio caches** (`FR-1630`) resolve pitches through `SCALE_IDX`/`OCTAVE_IDX`;
- `AROUSAL`/`VALENCE` (`FR-1420`) derive from `TEMPO_IDX`+`DENSITY_IDX` and `SCALE_IDX`;
- `BLEND_SRC_*`/`BLEND_STEP` relate to `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS`.

Today those derivations happen *after* the indices have been reset to the preset, so they are
trivially consistent. After this change they must be re-established from **whatever the listener
currently has set** — which they will be, provided the index writes are removed and nothing else is
reordered. Stated here because "remove five writes" looks like a smaller change than it is, and the
consequence of getting it wrong is an engine reseeded into pitch material derived from a preset the
listener is not on.

### Requirements this invalidates or reshapes

`FR-1070` is amended in place (it is the requirement being changed). `FR-1420`'s Select clause
("matching the restored preset indices") becomes wrong and must be re-stated as "unchanged by
Select." Every requirement whose prose calls `CHMIX_IDX` preset 0 "the boot/**Select-reset**
preset" — `FR-1260`, `FR-1300`, `FR-1440`, `FR-1580` — is describing an event that will no longer
set `CHMIX_IDX`; the requirements themselves remain correct, only that parenthetical is stale.
`FR-1630` stands and gains force (see the hazard above). `T5`'s suite asserts precisely the
behaviour being removed and must be re-authored against the new contract, **genuinely re-derived
rather than loosened** — `IP-1140`'s record shows a loosened `T5.5` would have let a real
off-by-one ship. Routing all of this to `04-requirements-engineering` is this record's own
downstream obligation.

### What the listener loses, stated rather than glossed

There is no longer any single control that returns the five indices to the boot preset. A listener
who has dialled themselves somewhere they dislike must step back out with the same buttons they
stepped in with — five controls, each wrapping, so every value is reachable in at most seven
presses. This is judged an acceptable trade and is **the trade the user explicitly asked for**
("does not need to bring it back to the boot default either"), but it is a real loss and is recorded
as one rather than presented as pure gain. Should it prove wrong in listening, the cheap remedy is a
long-press or a two-button chord, neither of which needs this decision reversed.

### Alternatives considered

1. **Leave Select alone; add reroll elsewhere.** Rejected: there is no free control (`R217`/`R206`
   — all six are mapped), and it would leave the obsolete workaround in place, which is the actual
   defect.
2. **Make Select conditional — reset the indices only when a bad zone is flagged.** Rejected: a
   control whose effect depends on invisible state is worse than either behaviour on its own, and
   `FR-1070`'s "unconditional, regardless of current bad-zone state" clause was a deliberate
   `IP-0001` decision worth keeping in its unconditional shape.
3. **Reroll only, no bad-zone clear.** Rejected: the user named course-correcting from a bad zone
   explicitly, and the clear is what makes the press feel immediate — a reseed alone takes up to one
   note per channel to become audible.
4. **Retire the arpeggio-style "one-line fallback" framing and keep a hidden reset.** Rejected as
   hidden state; see alternative 2.

## Status

**Accepted 2026-08-21**, on the project owner's direct instruction, under his standing G3 grant for
this increment. Downstream: `04-requirements-engineering` amends `FR-1070` in place and re-states
`FR-1420`; `07-implementation-planning` packages it (and is its own first real customer for the
amended four-question sweep, which flagged this obsolescence by name); `08-code-implementation`
implements it. No `01-vision` change is required — see "Why the button" above.
