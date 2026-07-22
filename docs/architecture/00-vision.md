# GDS-00 — Vision (design-facing restatement)

- **Owned by:** `01-vision` · **Status:** ✅ Authored 2026-07-21; amended 2026-07-22 (v1.1
  drift fix); amended 2026-07-22 (v1.2 cart-shape/save reopening, see below) · **Source:**
  `docs/master/MSTR-001-program-vision.md` v1.2

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
3. **Detect and recover** *(step amended v1.1, matching MSTR-001 C5)* — the generator's own state
   is scored against a "bad zone" metric every tick (or on a coarser cadence if per-frame cost is
   prohibitive — a GDS-03/06 performance question); crossing into the bad zone is itself part of
   the visible/audible state, not a silent internal flag. **Detection alone is not sufficient**:
   the generator must also autonomously bias its own generation back toward a good state, every
   frame, with no input required — recovery is not gated behind the player pressing Select.
4. **Reset (manual override)** *(role reframed v1.1)* — Select unconditionally forces the
   generator back to a defined good starting state, regardless of current state (bad zone or
   not), **and randomizes each channel's melodic starting point** — "reset and randomize," a
   player-available override that exists alongside step 3's autonomous recovery, not the only way
   out of a bad zone (that was step 4's pre-v1.1 sole role — same idea as a reference-project
   "new game," but resetting a generative process instead of starting a playthrough).
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

**Added 2026-07-22, not a vision change**: `BL-0020` (a user-filed feature request for multiple
selectable/combinable generation *schemes*, grounded in the now-complete R2xx research) raises a
third item of the same shape — how multiple generation approaches would coexist or combine is an
architecture-level design question, not decided here, and not in tension with anything in
MSTR-001 (C6's "generation logic... every frame" already accommodates one scheme or several
without requiring either). Noted here only so `03-architecture-design-synthesis` picks it up with
the same "propose one concrete design, not an options menu" discipline the other two items
already carry, when it takes up `BL-0020`.

## Cart shape and persistence — reopened, not decided (v1.2)

Earlier drafts of this document (and MSTR-001 v1.0/v1.1) treated "single 32KB bank, no SRAM save"
as settled shape. MSTR-001 v1.2 reopened both — the project owner named this as an arbitrary
decision that had been mistaken for a firm one. **This document does not decide the replacement
either.** `03-architecture-design-synthesis` must not assume single-bank/no-save when it reaches
cart-shape or persistence design; it should wait for (or itself request) the research MSTR-001 §9
commissions — MBC/bank-switching hardware facts and build-chain impact, and what a real save
design would need to support a longer-arc listener relationship (favorites, returning to a
discovered piece). Until that research lands, this remains an open item of the same shape as the
input-mapping/bad-zone-metric/scheme-combination items already delegated to GDS-03 below — a
fourth thing not guessed here.

## Testability requirement carried down from MSTR-001 C9

Every shipped behavior must be expressible as: boot the ROM headlessly, drive a button sequence,
and assert on register/WRAM state (sound registers for audio behavior, a WRAM mirror of engine
state for the parameters/bad-zone flag the visualizer and future tests both need to read). This
requirement shapes GDS-07 (Data Model): the engine's live parameters and bad-zone status need a
WRAM home even though nothing saves them to SRAM (MSTR-001 C2), specifically so the test harness
and the visualizer have something authoritative to read without re-deriving it from register
state (which PyBoy can also read directly, but a WRAM mirror is cheaper to assert on and is also
what the visualizer routine itself will read).

## Amendment note (2026-07-22)

MSTR-001 C5 was amended to v1.1 on 2026-07-21 (autonomous bad-zone recovery required; Select
reframed as "reset and randomize") and GDS-01/GDS-03 were updated the same session — but this
document (GDS-00, also owned by `01-vision`) was missed from that amendment's recorded blast
radius and kept describing the pre-v1.1 model until this drift was caught during a
`01-vision` consistency check the following day. Fixed above (steps 3-4); no new decision made
here, only a lagging restatement brought back into agreement with MSTR-001 §8's already-recorded
v1.1 change.

**Gate:** closed 2026-07-21. Next: GDS-01 (Concept of Play) via `03-architecture-design-synthesis`.
