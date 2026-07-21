# GDS-00 — Vision (design-facing restatement)

- **Owned by:** `01-vision` · **Status:** ✅ Authored, 2026-07-21 · **Source:** `docs/master/MSTR-001-program-vision.md` v1.0

This is the design-facing restatement of MSTR-001, in the vocabulary the GDS ladder builds on.
MSTR-001 is authoritative for purpose-level statements; this document translates its commitments
into terms `03-architecture-design-synthesis` can build GDS-01…10 from.

## What Driftune is, in system terms

A GBC ROM running one continuous process, every frame:

1. **Generate** — a music-generation routine advances internal state and decides what each of the
   four sound channels (pulse A, pulse B, wave, noise) plays for the next tick, writing to the
   PSG registers (`NR1x`/`NR2x`/`NR3x`/`NR4x`, plus the mixing/volume registers `NR50`/`NR51`/
   `NR52`) accordingly.
2. **Steer** — the joypad is polled every frame; D-pad/face-button state maps to live adjustments
   of the generator's own parameters (concrete mapping: GDS-03, §"Input → parameter mapping").
3. **Detect** — the generator's own state is scored against a "bad zone" metric every tick (or on
   a coarser cadence if per-frame cost is prohibitive — a GDS-03/06 performance question);
   crossing into the bad zone is itself part of the visible/audible state, not a silent internal
   flag.
4. **Reset** — Select forces the generator back to a defined good starting state, regardless of
   current state (bad zone or not) — same idea as a reference-project "new game," but resetting a
   generative process instead of starting a playthrough.
5. **Render** — a visualizer routine reads the same tracked generator state (tempo, per-channel
   activity, bad-zone-ness, whatever else GDS-03 defines) and updates BG tile/palette content to
   represent it, on its own cadence (need not be every frame — VBlank-budget dependent).

There is no game state machine in the reference-project sense (title → intro → playing → save →
map → victory) — GDS-01 (Concept of Play, next in the ladder) defines this project's own, much
flatter interaction model instead of inheriting that shape.

## What must be decided at GDS-03 (not guessed here)

Per MSTR-001 C4/C5, this vision deliberately leaves two things undecided, to be answered
concretely (not as an options menu) by `03-architecture-design-synthesis`:

- The **input → parameter mapping** (which button/direction controls which generation parameter).
- The **bad-zone detection metric** (what concretely is measured, thresholded, and how it's
  computed cheaply enough to run continuously on SM83 hardware).

## Testability requirement carried down from MSTR-001 C9

Every shipped behavior must be expressible as: boot the ROM headlessly, drive a button sequence,
and assert on register/WRAM state (sound registers for audio behavior, a WRAM mirror of engine
state for the parameters/bad-zone flag the visualizer and future tests both need to read). This
requirement shapes GDS-07 (Data Model): the engine's live parameters and bad-zone status need a
WRAM home even though nothing saves them to SRAM (MSTR-001 C2), specifically so the test harness
and the visualizer have something authoritative to read without re-deriving it from register
state (which PyBoy can also read directly, but a WRAM mirror is cheaper to assert on and is also
what the visualizer routine itself will read).

**Gate:** closed 2026-07-21. Next: GDS-01 (Concept of Play) via `03-architecture-design-synthesis`.
