# ADR-0003 — Scheme Selection Moves Out of `CHMIX_MASKS` Into a Parallel `SCHEME_TABLE`

- **Date:** 2026-08-19 · **Status:** Accepted · **Amends (does not reverse):** [`ADR-0001`](ADR-0001-scheme-selection-rides-chmix-preset-space.md)

## Context

`ADR-0001` decided that generation-scheme selection rides the `CHMIX_IDX` preset space, packed
into spare bits of `CHMIX_MASKS`'s per-preset mask byte (bits 0-3 channel mask, bits 4-6 one
scheme bit per pitched channel, bit 7 spare). That decision recorded its own failure mode in its
Consequences: *"a future third per-preset concern would need to renegotiate the packing."*

[`ADS-108`](../ADS-108-harmonic-coordination.md) is that third concern. Harmonic coordination
(`BL-0119`, grounded in [`R225`](../../research/encyclopedia/R225-harmonic-coordination-shared-chord-context.md))
introduces **Scheme H** alongside the existing Scheme W (LFSR walk) and Scheme E (Euclidean-gated
motif). Three schemes need two bits per pitched channel — six bits. `CHMIX_MASKS` has three bits
free for schemes, plus one spare. The packing cannot absorb it.

## Decision

Per-channel scheme selection moves to a **parallel `SCHEME_TABLE`, keyed by the same `CHMIX_IDX`**
— 8 entries, one byte each, 2 bits per pitched channel (pulse A bits 0-1, pulse B bits 2-3, wave
bits 4-5), values `0`=W, `1`=E, `2`=H. `CHMIX_MASKS` keeps bits 0-3 (the channel-activity mask) and
its bits 4-6 are **retired**, not left as a shadow copy.

`ADR-0001`'s actual principle — *scheme selection is keyed by the preset index Start already
steps; no new control, no new steerable parameter* — is **unchanged and reaffirmed**. What changes
is only the carrier: a parallel table rather than spare bits of a mask byte. This is the same move
[`ADS-101`](../ADS-101-genre-aware-style-presets.md) already made when `CHMIX_MASKS` ran out of
room for a 4-field style bundle (`STYLE_TABLE`), so the codebase gains no new pattern.

The migration carries a hard non-regression obligation: `SCHEME_TABLE` must reproduce every one of
the 8 presets' current bits-4-6 assignments exactly — in particular preset 6's Scheme-E wave
channel (`ADS-100`'s worked example, covered by shipped tests) and preset 0's all-Scheme-W default
(`GDS-04`'s index-0 invariant).

## Consequences

- **Positive**: unblocks a third (and fourth) scheme without renegotiating a bit layout again;
  decouples "which channels are active" from "which scheme each runs," which `ADR-0001` explicitly
  named as the cost of the original packing; reuses `ADS-101`'s established parallel-table pattern.
- **Positive**: each channel's scheme field is now byte-addressable rather than a masked bit test,
  which is marginally *cheaper* to read on the onset path than the current `BIT_b_A` against a
  computed mask row.
- **Negative**: it is a migration of shipped, tested behavior. Nothing about the ROM should sound
  different afterward, which is both the safety property and the risk — a silent transcription
  error in one of eight bytes would be audible only on a preset a test may not exercise. `ADS-108`
  §8 R1 records this and recommends sequencing it as its own package with the exact
  reproduce-all-eight-presets oracle.
- **Negative**: +8 bytes of ROM table. Immaterial against recorded headroom.
- **Neutral**: no WRAM change, no new control, no change to `CHMIX_IDX`'s meaning or to Start's
  behavior.

## Superseded by

Nothing — accepted. `ADR-0001` is **amended, not superseded**: its decision that scheme selection
rides `CHMIX_IDX` stands; only its bit-packing mechanism is replaced.
