# ADS-100 — Combinable Generation Schemes

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored 2026-07-22
- **Dependencies:** R202 (Euclidean rhythms), R211 (melodic/harmonic generation techniques),
  R212 (form/tension/macro parameters), R213 (PRNG/seed management), R214 (grammar/L-system/
  cellular-automata survey), R215 (constraint/scheduling survey), R216 (sound design techniques),
  R218 (inspiration/history survey); GDS-03 §1-3 (module layout, main loop, input mapping); GDS-07
  §1/§3 (`CHMIX_IDX`, per-channel generation state)
- **Produces:** a future `FS-xxx` (once `04-requirements-engineering` derives FRs from this
  document) and an eventual `IP-9xx0`-or-later Implementation Package
- **Trigger:** `BL-0020` (user-filed feature request), routed here by `01-vision`'s GDS-00
  amendment naming this a third "decide at GDS-03" item

## 1. Executive Design Overview

Today, all three pitched channels (pulse A, pulse B, wave) use exactly one generation approach:
an LFSR-driven, scale-constrained random walk (`_emit_channel_gen`, shared across all three via
the `CHANNELS` list). `BL-0020` asks for **multiple generation schemes, usable solo or in
combination**. This document proposes one concrete design: a second, contrasting generation
scheme (**Scheme E — Euclidean Phrase**, alongside the existing **Scheme W — Walk**), selectable
**per pitched channel**, with the combination expressed at the **ensemble level** — different
channels running different schemes simultaneously, not by blending two schemes' output into one
channel. Scheme selection is carried by the **existing, already-planned `CHMIX_IDX` preset space**
(GDS-07 §1, GDS-03 §3's "Active-channel mix" control, Start button) rather than a new input
control or a new WRAM parameter — the mask byte `IP-9010` is already about to wire up for
channel-activity has spare bits this design packs scheme-selection into, at zero additional
control-surface cost.

## 2. System Architecture

`_emit_channel_gen` (`music_engine.py:196-328`) currently hardcodes one note-selection strategy
(LFSR delta → table lookup) inside its shared, parameterized routine. This design adds a second
strategy without duplicating the whole routine: the **existing per-frame structure is unchanged**
(countdown → note-selection → table lookup → register write → timer reload → stale/onset
bookkeeping, IP-0004/IP-0007's bad-zone hooks all still apply identically to both schemes) — only
the **note-selection step** branches on the channel's current scheme bit, reading either the
existing LFSR-delta path (Scheme W) or a new motif-table-index path (Scheme E). Both schemes
still write through the same `BAD_ZONE_FLAGS`-driven dissonant/stuck/overload overrides
(`IP-0007`) — a scheme change does not create a second, parallel bad-zone-recovery mechanism.

```
                    ┌─ CHMIX_IDX (Start-stepped preset index) ─┐
                    │                                          │
        CHMIX_MASKS[CHMIX_IDX]  (IP-9010's existing byte, 8 presets)
        bits 0-3: channel-active mask (pa/pb/wv/nz) — IP-9010's scope
        bits 4-6: per-pitched-channel scheme-select (pa/pb/wv)  — NEW, this design
                    │                                          │
      ┌─────────────┴──────────┐              ┌────────────────┴───────────┐
      │ bit clear: Scheme W     │              │ bit set: Scheme E          │
      │ (existing LFSR walk,    │              │ (new: Euclidean-gated      │
      │  music_engine.py        │              │  onset timing + a short    │
      │  :213-259, unchanged)   │              │  cycling motif table)      │
      └─────────────────────────┘              └─────────────────────────────┘
```

## 3. Domain Model

- **Generation Scheme**: a note-selection *strategy* a pitched channel can run — distinct from a
  *preset* (a tempo/octave/scale/density/mix *value*, which any scheme still consumes identically:
  a scheme decides *which degree plays next*, not *how fast* or *in which scale*, so `TEMPO_IDX`/
  `OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX` remain scheme-agnostic, shared engine state exactly as
  today).
- **Scheme W (Walk)** — the shipped LFSR-driven random walk. No new concept; this design names
  the existing behavior for the first time as one of (now) two schemes.
- **Scheme E (Euclidean Phrase)** — new. Two parts, both grounded in already-authored research
  and both cheap to build on top of shipped machinery:
  1. **Onset timing**: instead of a fixed per-tempo note-timer reload, gate onsets through the
     *same* Euclidean-pattern mechanism the noise channel already uses (`_euclidean_pattern`,
     `music_engine.py:149-158`, R202) — reusing `DENSITY_IDX`'s existing k-value selection rather
     than adding a new density axis, so a Scheme-E channel's onset *rhythm* is patterned rather
     than every-N-frames-regular.
  2. **Pitch selection**: instead of an LFSR-picked signed delta, step through a short, fixed
     **motif** — a small precomputed cyclic array of scale-degree deltas (e.g. 4 motifs × 8 steps,
     grounded in R211's "phrase/motif" techniques and R216's arpeggio-pattern framing) — giving a
     repetitive, recognizable melodic fragment rather than Scheme W's continuous drift. This is
     deliberately **not** R214's L-system/grammar approach (the more powerful but also more
     ROM/complexity-expensive option that research survey named) — a fixed small motif table is
     the right-sized first contrasting scheme for this increment; L-systems remain a named,
     grounded, **not-yet-warranted** upgrade path (see §9).
- **Scheme assignment (the "combination")**: which of the 2 schemes each of the 3 pitched channels
  runs, for the currently-selected `CHMIX_IDX` preset. A preset where all 3 pitched channels run
  Scheme W is "solo Scheme W" (today's shipped behavior, preset 0 stays this way — no regression);
  a preset mixing schemes across channels (e.g. pulse A+B on Scheme W, wave on Scheme E) is a
  "combination," satisfying `BL-0020`'s literal ask without needing any new blending/mixing
  mechanism inside a single channel's own output.

## 4. User Stories

- As a listener, pressing Start cycles through mix presets that now also audibly change *how* the
  music is generated, not just *which* channels are active — a wave channel on Scheme E reads as a
  recognizable repeating bass motif against pulse A/B's freer Scheme-W drift, a concrete new
  listening texture `BL-0020` asked for.
- As a developer/coding agent adding a third scheme later, the per-channel scheme-select bit
  pattern (§2) has room for up to 8 schemes per channel if widened past 1 bit — this design uses 1
  bit (2 schemes) as the right-sized first step, not a permanent ceiling.

## 5. Functional Requirements (candidate — for `04-requirements-engineering` to formalize)

- FR-candidate: Each pitched channel's note-selection strategy (Scheme W or Scheme E) is
  determined by its scheme-select bit in the current `CHMIX_IDX` preset's mask byte.
- FR-candidate: Switching `CHMIX_IDX` (Start) changes scheme assignment take effect from that
  channel's next note onset (not instantaneously mid-note) — consistent with how `CHMIX_IDX`'s
  activity-mask half (`IP-9010`) is already specified to behave.
- FR-candidate: Scheme E's onset timing reuses the existing `_euclidean_pattern`/`DENSITY_K`
  mechanism; Scheme E's pitch selection reuses a new, small motif table — not a new PRNG source
  (keeping `R213`'s existing seed-management model unchanged).
- FR-candidate: Bad-zone detection/recovery (`IP-0004`/`IP-0007`) applies identically regardless
  of which scheme a channel is running — no scheme-specific bad-zone logic.

## 6. Non-functional Requirements (candidate)

- ROM budget: the motif table (≈32 bytes for 4×8 one-byte deltas) plus the extra scheme-select
  bits packed into `IP-9010`'s already-planned mask byte (zero additional WRAM/ROM table for the
  selection mechanism itself, only for the motif data) — negligible against the current build's
  headroom (GDS-07 §6).
- No new WRAM address is needed for scheme *selection* (it's derived from `CHMIX_IDX` each tick,
  the same way `CHANNELS`' `octave_delta`/`tempo_mult` are already per-channel Python-level
  constants, not stored state) — only a small per-channel "which step of the current motif" scratch
  byte is new WRAM, analogous to `NOISE_STEP_IDX`.

## 7. Constraints

- **No new input control** — all 6 physical controls (D-pad×2 axes, A, B, Start, Select) are
  already assigned (GDS-03 §3); this design is constrained to ride an existing control's preset
  space rather than requesting a 7th, per `R217`'s finding that most seed/preset UX questions are
  already answered by existing decisions.
- **Single 32KB bank, no MBC** (MSTR-001 C2/§4, A5 in the strategic assumptions register) — the
  motif-table approach was chosen specifically because it's the cheapest research-grounded
  contrasting scheme, not the most powerful one, to respect this ceiling without triggering a
  bank-switching conversation.
- **Combination is ensemble-level, not per-channel-blended** — a single channel's PSG output is
  never a mix of two schemes; this sidesteps a real, harder voice-leading/DSP problem R203 doesn't
  claim to solve on this hardware.

## 8. Risks

- **Audible contrast may be subtler than intended** — a 4-motif, 8-step table is a small
  vocabulary; if Scheme E doesn't read as clearly distinct from Scheme W in practice, the "solo vs
  combination" value proposition weakens. Mitigation: this is exactly the kind of judgment call
  `09-content-review` exists to make once built — not resolvable at the architecture stage, named
  here so that review knows to specifically listen for this.
- **`CHMIX_IDX` mask-byte bit-packing couples two independent concerns** (channel activity,
  scheme selection) into one preset index — a future third concern wanting its own `CHMIX_IDX`-
  preset-space bit would need to renegotiate this packing. Accepted for now given the "no new
  control" constraint (§7); flagged so a future ADS revisiting this doesn't rediscover the
  coupling from scratch.
- **Depends on `IP-9010` (`BL-0019`) shipping first** — this design's mask-byte reuse assumes
  `IP-9010`'s `CHMIX_MASKS` table exists with the bit layout `IP-9010`'s own package doc specifies
  (bits 0-3 channel-active). If `IP-9010` ships with a different bit layout than currently
  planned, this design's bits 4-6 assignment needs re-checking against the as-shipped layout, not
  assumed unchanged.

## 9. Open Questions

- **Should Scheme E's motif table be fixed at build time (ROM-resident, as designed here) or
  randomized per-session** (analogous to `IP-0007`'s `DIV`-seeded LFSR)? This design defaults to
  fixed (simpler, cheaper, and motifs are meant to be *recognizable*, which a randomized-per-boot
  motif would undercut) — genuinely open if a future content-review pass finds fixed motifs
  become stale after repeated listening.
- **Is a third scheme (R214's L-system/grammar approach, R215's constraint-solving approach)
  worth building once Scheme E ships?** Not decided here — this design deliberately scopes to
  exactly two schemes as the minimum viable "solo vs. combination" proof, per `BL-0020`'s own
  wording ("multiple... schemes," satisfied at two). A third scheme is a natural, well-grounded
  future `00-intake` item once Scheme E's actual listening character is known.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-22 | Combination is expressed at the ensemble level (different channels, different schemes) rather than blended within one channel. | Matches the project's existing 4-fixed-channel architecture with zero new DSP/mixing machinery; R203's voice-leading topic doesn't claim per-channel scheme-blending is SM83-tractable, and nothing in the research survey (R211-R218) proposed it either. |
| 2026-07-22 | Scheme selection rides the existing (not-yet-shipped) `CHMIX_IDX` preset space rather than a new input control or a new steerable parameter. | All 6 physical controls are already assigned (GDS-03 §3); `R217` found no unmet UX need for more controls; reusing `IP-9010`'s already-planned mask byte's spare bits costs zero new control surface. |
| 2026-07-22 | Scheme E is a Euclidean-onset + fixed-motif design, not R214's L-system/grammar approach. | Right-sized for one increment's ROM/complexity budget (MSTR-001 §4 non-goal against bank-switched growth); reuses already-shipped `_euclidean_pattern` machinery; L-systems remain a named, grounded future option (§9), not discarded. |
| 2026-07-22 | This design is contingent on `IP-9010`'s bit layout; not implemented until `IP-9010` ships and its actual mask-byte layout is confirmed. | Avoids designing against a package that hasn't shipped and could still change during `08-code-implementation`. |
