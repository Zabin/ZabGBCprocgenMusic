# ADR-0004 — Harmonic Coordination Replaces the Default Walk In Place; Scheme Selection Stays on `ADR-0001`'s Packing

- **Date:** 2026-08-20 · **Status:** Accepted ·
  **Supersedes:** [`ADR-0003`](ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md) ·
  **Reaffirms:** [`ADR-0001`](ADR-0001-scheme-selection-rides-chmix-preset-space.md)
- **Source:** [`ADS-108` §11](../ADS-108-harmonic-coordination.md) (D13)

## Context

`ADR-0003` moved per-channel scheme selection out of `CHMIX_MASKS`'s bits 4-6 into a parallel
8-byte `SCHEME_TABLE`, because [`ADS-108`](../ADS-108-harmonic-coordination.md) §2.5 introduced a
**third** generation scheme ("Scheme H," chord-derived note selection) alongside Scheme W (the LFSR
walk) and Scheme E (Euclidean-gated motif). Three values per channel need two bits; `ADR-0001`'s
packing provides one.

That third scheme existed for one reason, stated plainly in `ADS-108` §1, §2.7 and D11: **preset 0's
audible behavior could not change**, because [`GDS-04` §4.1](../04-domain-model.md)'s index-0
invariant was read as forbidding it. Harmony therefore had to live *beside* the default rather than
*become* it.

On 2026-08-20 the project owner released that constraint explicitly — *"Don't hold the preset 0 to
an arbitrary standard, it was developed by you at a previous iteration… I'd like to get to a
pleasant sounding music as soon as possible"* — and `GDS-04` §4.1 has been amended in step
(`ADS-108` §11.5) to separate the invariant's genuine fixed-point content, which stands, from its
historical-no-regression reading, which is released.

## Decision

**Chord-derived note selection becomes the behavior of the existing default scheme.** The
`CHMIX_MASKS` bits-4-6 packing `ADR-0001` established is retained byte-for-byte: one bit per pitched
channel, value `0` = default, value `1` = Scheme E. Only the *meaning* of value `0` changes, from
"unharmonized LFSR walk" to "chord-derived selection." Scheme E is untouched and remains
unharmonized (`ADS-108` §8 R3, deferred to increment 2).

Consequently:

- **No `SCHEME_TABLE` is created.** `ADR-0003` is superseded before implementation; nothing was
  built against it.
- **No `CHMIX_MASKS` migration is performed.** `BL-0123`'s `IP-8xx0` refactoring package is obviated
  rather than sequenced.
- **The unharmonized independent walk stops being reachable in the shipped ROM.** It is not retained
  behind a bit.
- **The boot sound changes.** That is the point, not a side effect.

The musical mechanism itself — `CHORD_IDX`/`CHORD_ONSET_CTR`/`CHORD_TOGGLE`, `CHORD_TABLE`,
`CHORD_TRANSITION`, the onset-counted harmonic clock in pulse A's onset branch, and the three
per-voice rules — is unchanged from `ADS-108` §2.1-§2.4/§2.6. This ADR decides the *carrier*, not
the music.

## Consequences

- **Positive — an entire package of pure-risk work disappears.** The migration `ADR-0003` mandated
  was mechanical, non-regression-critical, separately verifiable, and by construction inaudible.
  Not performing it removes that risk outright rather than managing it.
- **Positive — the audible improvement lands in increment 1.** `ADS-108` §8 R7 (the risk that
  increment 1 reads as the work being done while changing nothing anyone can hear) is deleted rather
  than mitigated.
- **Positive — the emitted code shrinks rather than grows.** `_emit_channel_gen`'s existing
  fall-through path is *replaced*, not branched around: no extra scheme test on the onset path, and
  the existing `gt_delta_ready_{suffix}` convergence point and its `SUB_D` target→delta idiom are
  reused verbatim. `NFR-1240` (nothing unconditional per frame) is easier to satisfy under this ADR
  than under `ADR-0003`, not harder — which matters against the budget `R101` §8.5 measured and
  `BL-0113`/`IP-9040` proved unforgiving.
- **Negative — a body of shipped tests stops describing the engine.** `T5`/`T6`-class assertions on
  the ±1 stepwise degree walk must be re-authored against the chord-derived contract. This is
  expected and authorized; it is also the loudest possible signal that behavior genuinely changed,
  which is a property worth having.
- **Negative — "harmony off" is no longer a free bit.** A future ask for an unharmonized mode needs
  `CHMIX_MASKS` bit 7 (still spare) or a new carrier. `ADR-0003` remains on file, unbuilt, as the
  recorded design should a fourth per-preset concern ever exhaust the packing for real.
- **Neutral — `ADR-0001`'s actual principle is reaffirmed**: scheme selection is keyed by the preset
  index Start already steps; no new control, no new steerable parameter, no new table.
- **Neutral — `ADS-101`'s `STYLE_TABLE`, `ADS-102`'s `MOTIF_TABLE` and `ADS-103`'s `SONG_TABLE` are
  untouched**, and each still satisfies the fixed-point half of the index-0 invariant.

## Superseded by

Nothing — accepted.
