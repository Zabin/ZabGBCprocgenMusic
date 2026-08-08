# ADS-101 — Genre-Aware Style Presets

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored 2026-07-26
- **Dependencies:** R219 (genre feasibility on 4-channel GBC PSG, including the 2026-07-26
  Celtic/Seasonal/Holiday addendum), R220 (style evolution/song-form structure), R207 (GB-era
  chiptune channel-usage idioms), R216 (sound design techniques — duty-cycle/timbre), ADR-0001
  (scheme-selection rides the `CHMIX_IDX` preset space — the precedent this design extends),
  GDS-03 §3 (input mapping, all 6 controls already assigned)
- **Produces:** a future `FS-xxx` (once `04-requirements-engineering` derives FRs from this
  document) and an eventual Implementation Package
- **Trigger:** `docs/roadmap/04-release-roadmap.md`'s **R5 — Genre-Aware Style Presets**, whose
  own entry names the control mapping "TBD at architecture time" — this document is that decision

## 1. Executive Design Overview

R219 tiered ~29 genre references by feasibility on 4 monophonic PSG channels; R220 found a cheap
state-machine shape for driving Driftune's already-tracked parameters through envelopes over
time. Neither decided **how a listener (or a future autonomous drift mechanism) actually selects
a style**, or **which concrete parameter combination** each named style maps to. This document
answers both: style selection **reuses the existing `CHMIX_IDX` preset index** (Start button,
already stepped 0-7 by `input_map.py`'s `_step_on_bit`) as the trigger, but — unlike `ADS-100`'s
scheme-selection, which packed 3 extra bits into `CHMIX_MASKS`'s single mask byte — style data
needs more than a few bits per preset (a full tempo/density/scale/duty combination), so this
design adds a **second, parallel ROM table** (`STYLE_TABLE`) indexed by the same `CHMIX_IDX`,
rather than further bit-packing an already-tight byte (`CHMIX_MASKS` has exactly 1 spare bit
left, bits 0-6 already spoken for by channel-activity + scheme-select). Selecting a style
**actively overwrites** `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/a new duty-cycle-bias field to that
style's target values — the same "big, honest jump" precedent Select already establishes for a
full reset, just triggered by Start instead and scoped to musical-identity parameters rather than
every piece of state. Three concrete v1 styles are named (§3), each drawn from R219's
high-confidence tier and chosen to be maximally, audibly distinct from one another and from the
shipped baseline.

## 2. System Architecture

`build_engine_asm`'s init sequence (`music_engine.py:922-926`) already writes 5 preset constants
(`PRESET_TEMPO_IDX`/`PRESET_OCTAVE_IDX`/`PRESET_SCALE_IDX`/`PRESET_DENSITY_IDX`/
`PRESET_CHMIX_IDX`) into their WRAM indices once, at boot. This design adds a new routine,
`_emit_apply_style`, called from the same site `input_map.py`'s `_step_on_bit` already calls when
`CHMIX_IDX` changes (Start press) — **not** a new call site, an extra step folded into the
existing Start-press handler:

```
Start pressed → CHMIX_IDX steps (existing, unchanged, input_map.py:61)
                        │
                        ▼
        _emit_apply_style(rom)   ← NEW
                        │
        STYLE_TABLE[CHMIX_IDX] read (NEW ROM table, one row per preset)
                        │
        ┌───────────────┼────────────────┬─────────────────┐
        ▼               ▼                ▼                 ▼
   TEMPO_IDX  ←—   DENSITY_IDX  ←—   SCALE_IDX  ←—   DUTY_BIAS (NEW WRAM byte)
   (existing)      (existing)       (existing)       (new — read by
                                                       _emit_channel_gen's
                                                       existing duty-write
                                                       site, IP-1060)
```

`CHMIX_MASKS[CHMIX_IDX]` (channel-activity + scheme-select, `ADS-100`/`IP-9010`/`IP-1070`) is
**read exactly as it already is today** — this design adds a sibling table keyed by the same
index, not a replacement or an extension of the existing one. The two tables stay independent:
a future preset-data package (`BL-0032`'s follow-up) can freely vary `CHMIX_MASKS` without
touching `STYLE_TABLE` and vice versa.

## 3. Domain Model

- **Style**: a named, coordinated bundle of existing tracked-parameter *target values*
  (`TEMPO_IDX`, `DENSITY_IDX`, `SCALE_IDX`, a new `DUTY_BIAS`) that, applied together, makes the
  engine's output read as a recognizable genre reference — distinct from a **Scheme**
  (`ADS-100`'s per-channel *note-selection strategy*, which a style leaves untouched) and distinct
  from a **channel-mix preset** (`IP-9010`'s per-channel *active/muted* set, also left untouched
  by style selection — the two tables are read independently, per §2).
- **`STYLE_TABLE`**: 8 rows (one per `CHMIX_IDX` value, matching `CHMIX_MASKS`'s own preset
  count so both tables share one index — no new WRAM control byte), each row 4 bytes
  (`tempo_idx`, `density_idx`, `scale_idx`, `duty_bias`).
- **`DUTY_BIAS`** (new, 1 WRAM byte): a per-style offset added to `IP-1060`'s existing
  `DUTY_BY_DEGREE`-indexed duty-cycle selection, giving a style-level "brighter/darker" timbre
  lean without touching `IP-1060`'s own per-note degree-driven variation logic.
- **Concrete v1 styles** (3, satisfying R5's "at least 3 high-confidence styles" completion
  criteria, each chosen to be maximally distinct from the others and from the shipped baseline,
  per R219's tiers):
  1. **Techno/Chiptune-Driving** (R219: high-confidence, "the scene's own first-experiment
     genre") — fast tempo (`TEMPO_IDX` high), dense Euclidean-gated percussion (`DENSITY_IDX`
     high), minor/dorian mode (darker, driving harmonic character), bright duty bias (crisp
     pulse-wave lead, matching R219's own "pulse-wave leads... exactly this genre's own defining
     timbre" finding for the adjacent Synthwave entry).
  2. **Ambient/Lo-Fi** (R219: high-confidence, "closer to what Driftune already ships than any
     other reference in the list") — slow tempo, sparse density, major or pentatonic mode (calm,
     consonant-leaning), soft duty bias. Intentionally the style **closest to the current default
     preset** — the "no drastic change" anchor point the other two styles contrast against.
  3. **Holiday** (R219 §8 addendum: "the single cheapest genre-style addition... arguably")
     — major key (`SCALE_IDX` = major), moderate tempo, moderate-steady density (the addendum's
     own "90% are in 4/4 time... jubilant swing" finding), bright duty bias (bell-like timbre per
     the addendum's glockenspiel/celeste citation). The addendum's own further finding — a
     stepwise-motion-biased `DELTA_TABLE`/motif shape — is **not** included in this v1 (it would
     require either a per-style `DELTA_TABLE` variant or `ADS-100`'s Scheme-E motif mechanism,
     both real but separable follow-on work, named in §9) — v1 Holiday is realized purely through
     the four `STYLE_TABLE` fields already defined, a deliberate scope cut to stay inside this
     release's own "presets, not new generation logic" framing.
- **Celtic** (R219 §8: joins the Folk/World tier via a scale-table extension) is **not** a v1
  style — it requires a new mode entry in `SCALE_SEMITONES`/`SCALES` (Mixolydian/Dorian/Aeolian,
  R219 §8), which is real but separable content work, not a `STYLE_TABLE`-only addition like the
  three v1 styles. Named as the natural first post-v1 style once that scale-table extension
  lands (see §9).

## 4. User Stories

- As a listener, pressing Start now cycles through presets that change not just channel-mix/
  scheme (as today, `IP-9010`/`IP-1070`) but the *whole musical character* — tempo, density,
  scale, and timbre brightness all shift together, reading as a recognizable style change rather
  than an incremental parameter nudge.
- As a listener who has been manually steering tempo/scale/density with the D-pad/A/B, pressing
  Start to change style **overwrites** those manually-drifted values to the new style's target —
  the same kind of honest, visible "big jump" Select already performs for a full reset, just
  narrower in scope (musical-identity parameters only, not bad-zone state/seeds) and triggered by
  a different control. Nothing is hidden: the same WRAM indices the D-pad/A/B already read and
  write are the ones a style overwrites, so the listener can immediately resume independently
  steering from the new starting point.
- As a developer adding a 4th+ style later, `STYLE_TABLE` has 8 rows total (matching
  `CHMIX_MASKS`'s own preset count) — up to 5 more styles fit with zero mechanism change, only
  more preset data.

## 5. Functional Requirements (candidate — for `04-requirements-engineering` to formalize)

- FR-candidate: Each `CHMIX_IDX` preset value maps to a `STYLE_TABLE` row specifying target
  `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` values.
- FR-candidate: Changing `CHMIX_IDX` (Start) applies that row's values to the corresponding WRAM
  indices immediately (not gated to the next onset — unlike `ADS-100`'s scheme-select or
  `IP-9010`'s channel-mix, which both take effect at next onset; style parameters are read
  per-tick by the existing generation routines exactly like a manual D-pad/A/B change already is,
  so there is no new "mid-note" edge case to define).
- FR-candidate: At least 3 styles (Techno/Chiptune-Driving, Ambient/Lo-Fi, Holiday) are
  implemented, each independently verified as producing its documented parameter combination and
  judged audibly distinct via `09-content-review`.
- FR-candidate: Style preset 0 (`PRESET_CHMIX_IDX`'s existing boot/Select-reset value) maps to a
  `STYLE_TABLE` row matching the current shipped default preset exactly — no regression to boot
  behavior (same non-regression discipline `IP-9010`'s own preset-0 requirement already
  established for `CHMIX_MASKS`).

## 6. Non-functional Requirements (candidate)

- ROM budget: `STYLE_TABLE` is 8 rows × 4 bytes = 32 bytes; negligible against the measured 29349
  free ROM bytes (`ADR-0002`'s own instrumentation).
- WRAM budget: 1 new byte (`DUTY_BIAS`); `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` are already-existing
  addresses, overwritten in place, not duplicated.
- No new input control (§7) — reuses `CHMIX_IDX`'s existing Start-press trigger exactly.

## 7. Constraints

- **No new input control** — same constraint `ADS-100` operated under (GDS-03 §3, R217); this
  design satisfies it by keying `STYLE_TABLE` off the same `CHMIX_IDX` index `ADS-100`/`IP-9010`
  already use, rather than requesting a distinct "style" button.
- **`CHMIX_MASKS`'s mask byte is not further bit-packed** — with only 1 spare bit left (bit7)
  after `IP-9010`'s channel-activity nibble and `ADS-100`'s scheme-select 3 bits, a style concept
  needing 4 real parameter values genuinely cannot fit in remaining bits — a parallel table keyed
  by the same index is the correct mechanism, not a forced continuation of `ADS-100`'s
  bit-packing pattern past where it still fits.
- **Single 32KB bank, no MBC** (`ADR-0002`) — 32 bytes of new ROM data is far inside this
  ceiling; no bank-switching question is raised by this design.
- **Style selection is a coordinated overwrite of existing parameters, not a new generation
  mechanism** — `_emit_channel_gen`/`_emit_noise_gen`/`_emit_badzone_tick` are all unmodified;
  this design only changes *which values* `TEMPO_IDX` etc. hold, never *how* those values are
  consumed.

## 8. Risks

- **Overwriting manually-steered parameters on every Start press could read as the engine
  "fighting" the listener's own tuning**, if styles are stepped through quickly/idly rather than
  deliberately selected. Mitigation: this is the same class of judgment `09-content-review`
  already exists to make for Select's existing full-reset behavior — named here so review
  specifically listens for whether Start's narrower (musical-identity-only) overwrite reads as
  intentional/legible or as unwanted interference; not resolved at the architecture stage.
- **Three styles chosen for maximal audible contrast may not read as *recognizably* the named
  genre** (e.g. "Techno" vs. simply "fast and dense") without a listener already primed by the
  genre reference — a real, R219-acknowledged limit of parameter-preset-only genre signaling (no
  new timbral/percussive mechanism is added by this design). Mitigation: named for
  `09-content-review` to judge against R219's own genre-fidelity framing, not asserted as solved
  here.
- **`DUTY_BIAS` interacting with `IP-1060`'s existing per-degree `DUTY_BY_DEGREE` indexing** needs
  a concrete combination rule (add-and-clamp vs. override) decided during
  `07-implementation-planning`/`08-code-implementation` — flagged as an implementation detail this
  document deliberately leaves open (§9), not silently assumed.

## 9. Open Questions

- **Should `DUTY_BIAS` add to or override `IP-1060`'s per-degree duty selection?** Not decided
  here — a `07-implementation-planning`-level detail once the exact combination is prototyped and
  listened to.
- **Should Celtic be added as a 4th style once its `SCALE_SEMITONES` extension lands** (R219 §8),
  and should Holiday's own stepwise-motion-bias finding be folded in via a per-style `DELTA_TABLE`
  variant or via `ADS-100`'s Scheme-E motif mechanism instead? Both genuinely open, deliberately
  deferred past this v1's three-style scope (§3) — natural `00-intake`/backlog candidates once v1
  styles are built and their actual listening character is known.
- **Should style selection eventually be driven autonomously** (R220's own state-machine finding,
  cycling styles over session length rather than only on a Start press) **rather than only
  user-triggered?** This document deliberately scopes to user-triggered only (matching R5's own
  "a style control" wording) — autonomous style-drift is R220/R6's own separate, already-named
  territory (`docs/roadmap/04-release-roadmap.md`'s **R6 — Song-Form & Style-Drift Engine**), not
  duplicated here.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-26 | Style selection reuses the existing `CHMIX_IDX` preset index (Start) as its trigger, rather than a new input control. | Same constraint and precedent `ADS-100` already established (GDS-03 §3, R217: no unmet need for more controls); reusing an existing, already-stepped index costs zero new control surface. |
| 2026-07-26 | Style data lives in a new, parallel `STYLE_TABLE` keyed by the same `CHMIX_IDX` index, rather than further bit-packing `CHMIX_MASKS`. | `CHMIX_MASKS` has only 1 spare bit left after `IP-9010`'s channel-activity nibble and `ADS-100`'s scheme-select 3 bits — genuinely insufficient for a 4-parameter style bundle. A parallel table sharing the same index avoids a new WRAM control byte while giving each style full room (tempo/density/scale/duty). |
| 2026-07-26 | Style selection actively overwrites `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS`, applied immediately (not gated to next onset). | Matches R5's own "audibly shifts the whole mix" completion criteria — a style that only biased future generation subtly would be a weaker, less legible change than a direct value overwrite; the overwrite-on-existing-control precedent is already established by Select's own full-reset behavior. |
| 2026-07-26 | Three concrete v1 styles named: Techno/Chiptune-Driving, Ambient/Lo-Fi, Holiday — Celtic deferred, deliberately not a v1 style. | Maximizes audible contrast between the three (fast/dense/dark vs. slow/sparse/calm vs. bright/major/festive) using only R219's high-confidence tier; Celtic requires a separable scale-table content addition (R219 §8) not yet built, so including it in v1 would conflate a `STYLE_TABLE`-only change with new content work. |
