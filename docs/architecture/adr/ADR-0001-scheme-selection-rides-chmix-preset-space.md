# ADR-0001 — Scheme Selection Rides the Existing `CHMIX_IDX` Preset Space

- **Date:** 2026-07-22 · **Status:** Accepted

## Context

`BL-0020` asks for multiple procedural generation schemes, usable solo or in combination. All 6
of Driftune's physical input controls are already assigned to a steerable parameter (GDS-03 §3:
D-pad Up/Down → tempo, D-pad Left/Right → octave, A → scale, B → density, Start → channel mix,
Select → reset). `R217` (UX conventions for generative instruments) found no unmet need for
additional controls. Adding a 7th steerable parameter would require either a new control
mechanism (button chords, long-press — both add real input-handling complexity and risk, neither
grounded by any research topic as a GBC-chiptune convention) or overloading an existing control.

## Decision

Generation-scheme selection (`ADS-100`) is packed into the same preset index Start already steps
(`CHMIX_IDX`), reusing spare bits in the per-preset mask byte `IP-9010` (the `BL-0019` remediation
package, not yet shipped) is already planned to introduce for channel-activity masking. No new
WRAM control byte, no new input control.

## Consequences

- **Positive**: zero new control-surface cost; reuses a mask-byte concept the codebase is already
  about to build (`IP-9010`), rather than inventing a second, parallel preset mechanism.
- **Negative**: couples two independent concerns (which channels are active, which scheme each
  runs) into one preset index's bit layout — a future third per-preset concern would need to
  renegotiate the packing, or a new control would need to be found after all. Documented as a
  known risk in `ADS-100` §8, not silently accepted.
- **Contingent**: this decision assumes `IP-9010` ships with the bit layout its own package doc
  currently specifies (bits 0-3 = channel-active mask, per `IP-9010-channel-mix-gating.md`). If
  that layout changes during `08-code-implementation`, this ADR's bit-packing assumption (bits
  4-6 for scheme-select) needs re-verification before `ADS-100`'s own eventual implementation
  package is authored.

## Superseded by

Not superseded — **amended 2026-08-19 by [`ADR-0003`](ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md)**.
This ADR's principle (scheme selection is keyed by the `CHMIX_IDX` preset index Start already
steps; no new control) stands unchanged. Its *bit-packing mechanism* is replaced: the third
scheme (`ADS-108`'s Scheme H) needs two bits per channel, which the mask byte cannot carry — the
exact "future third per-preset concern would need to renegotiate the packing" outcome this ADR's
own Consequences section predicted. Scheme bits move to a parallel `SCHEME_TABLE` keyed by the
same index.
