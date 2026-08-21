# ADR-0005 — The Arpeggio Becomes Chord-Aware, Gated and Varied; It Is Not Retired

- **Date:** 2026-08-21 · **Status:** Accepted ·
  **Amends the behavior established by:** `IP-1060`/`IP-1061` (`R216`) ·
  **Builds on:** [`ADR-0004`](ADR-0004-harmonic-coordination-replaces-the-default-walk-in-place.md)
  (unchanged and unaffected — this decision is downstream of it, not a revision of it) ·
  **Absorbs:** `CR-0006` (arpeggio re-rooting), `BL-0125` (`arp_tick`'s hardcoded octave and its
  cached-table-index idea)
- **Source:** [`ADS-108` §12](../ADS-108-harmonic-coordination.md) (D14), from
  [`BL-0127`](../../pipeline/backlog.md) — the project owner's listening report, measured.

## Context

`IP-1060` added an arpeggio to both pulse channels in 2026-07, when the engine had no harmony. Its
stated purpose (`R216`) was *"implying a chord on a single channel"* — it was **faking harmony in
the absence of harmony**, and at the time that was the right call.

`ADR-0004`/`IP-1140` then gave the engine real harmony: three pitched voices deriving their notes
from one shared `CHORD_IDX`. The arpeggio was not revisited. It still computes

```
effective_degree = (CUR_DEGREE + ARPEGGIO_OFFSETS[step]) AND 0x07
```

every frame, for both pulse channels, where `ARPEGGIO_OFFSETS = [0, 2, 4, 2]` is a triad in
*scale-degree offsets*. Since `IP-1140`, `CUR_DEGREE` is the chord tone the harmony just chose — so
the routine stacks a second, differently-rooted triad on top of the engine's own chord.

The project owner heard the result and reported **"constant repeated arpeggios"** before any
document had noticed the conflict.

Measured on the shipped ROM (`3e635ed`, boot defaults, 3600 frames, sounding pitch reconstructed
from `CUR_DEGREE` + the live `ARP_STATE` step, with a driver that reproduces `IP-1140`'s own
recorded figures on `IP-1140`'s own basis):

- pulse B is placed on a current-chord tone at **100 %** of its onsets, yet only **46.4 %** of
  sounding pulse-channel frames are chord tones at all;
- pulse A arpeggiates *from* the chord root at **14.0 %** of onsets, pulse B at 29.8 % — so the great
  majority of the figures are triads built on a non-root of the sounding chord;
- harsh vertical intervals on strong beats are **12.0 % on intent and 25.7 % on sounding pitch** —
  the arpeggio more than doubles the number `IP-1140`'s entire increment existed to halve;
- the figure is a **24-frame shape repeating ~2.5×/second on every note of both channels forever**,
  with no gate, no draw, and no mechanism by which it could vary;
- the `AND 0x07` mask is the octave-seam arithmetic `ADR-0004`'s own `ADS-108` D3 already ruled
  *incorrect* for chord math (`R225` §3g);
- the routine costs ~120 **unconditional** instructions per frame, ~32 of them re-deriving a
  `(SCALE_IDX, OCTAVE_IDX) → ptr_table` address from inputs that change only at onsets — in a VBlank
  budget `R101` §8.5 measured as exhausted and over which `IP-9040` was abandoned for three
  instructions (`BL-0113`).

## Decision

**The arpeggio is kept, and re-decided, under four binding rules.** Full reasoning, evidence table
and rejected alternatives: [`ADS-108` §12](../ADS-108-harmonic-coordination.md) (D14).

1. **Chord-aware (R-A).** An arpeggio traverses **tones of the currently-sounding chord, read from
   `CHORD_TABLE`** — never scale-degree offsets from the sounding note. `CHORD_TABLE` is
   hand-authored, per-scale, already in ROM, and already took the octave-seam decision at authoring
   time, so the `AND 0x07` defect closes as a side effect rather than as separate work.
2. **Gated (R-B).** A voice arpeggiates only while the note it holds *is* a chord tone. Pulse A's
   weak onsets are deliberate passing tones (`FR-1550`); a passing tone must sustain, because
   arpeggiating a triad from it re-asserts it as a root and destroys the strong/weak distinction
   `ADS-108` D9 calls the entire mechanism converting "in key" into "in harmony." The parity bit
   required already exists (`CHORD_TOGGLE` bit1) and is already read at that onset.
3. **Varied (R-C).** The traversal is **drawn per onset** from a small table of patterns indexed by
   the channel's own LFSR — this project's standard weighted-table idiom (`R211` §8), where the bias
   lives in the distribution of entries and never in arithmetic. Rows are chord-tone slot indices,
   with **one reserved value meaning "sustain"**, so that a row may hold and an all-sustain row means
   "this note does not arpeggiate." Rules 2 and 3 are therefore **one mechanism**: the gate is a
   forced pattern index, not a second branch. At least one row must differ in *rhythmic surface*, not
   merely in pitch order.
4. **Cheaper, not dearer (R-D).** Per-frame cost must **strictly decrease**. R-A and R-C are
   onset-time work inside branches that already exist (`NFR-1240` unchanged); what `arp_tick` does
   per frame gets cheaper by caching, per channel at its onset, what it currently re-derives every
   frame. `VIS_ENTRY_LY` across every frame class is the acceptance instrument and a regression is
   **blocking**.

**Explicitly not retired.** Retirement was the strongest rival — certain, cheapest, and the largest
head-room recovery available in this engine — and was rejected on evidence about what would remain:
with no arpeggio, both pulse channels hold a static pitch for a whole note (~0.5 s) with only ±1
vibrato, and this engine has no rests and no phrase structure (`CR-0003`), so sub-note motion is
currently the *only* thing happening between onsets. That trades "mechanically busy" for "static and
plodding" — a different complaint, not fewer. Retirement is **kept as the named fallback** and R-C's
table shape is what makes it cheap: an all-sustain pattern table *is* retirement, a data edit rather
than a redesign.

## Consequences

- **The default boot sound changes again, deliberately** — the second such change in this project's
  history, on the same basis `ADR-0004` established (`GDS-04` §4.1's historical-no-regression reading
  released 2026-08-20; its fixed-point half still stands and is not touched here).
- **`IP-1140`'s recorded acceptance figures are overstated and must be corrected** wherever written
  down. They were measured on `CUR_DEGREE` (**intent**) rather than sounding pitch. Same build, same
  run, correct instrument: strong **25.7 %**, weak **36.1 %**, aggregate **30.9 %** — not
  12.2 %/30.6 %/21.5 %. `NFR-1270` must state the sounding-pitch basis normatively (`BL-0128`).
- **A cached per-channel resolution changes when a `SCALE_IDX`/`OCTAVE_IDX` change becomes audible on
  an already-sounding note** — next onset (≤ ~0.5 s) instead of next frame. No control becomes
  unresponsive; a mid-note pitch jump disappears. Judged an improvement, but it is a real behavioral
  change and is recorded, not left to an implementer. `init_engine` must refresh the cache on **both**
  boot and Select, or a reset leaves stale pitch material — the `BLEND_STEP` defect class `VR-1130`
  already found once.
- **`BL-0125`'s blocked octave placement becomes unblocked** (pulse B's `octave_delta`, `FR-1560`'s
  withheld half) at zero additional per-frame cost. Recorded as *unblocked*, not as owed — nothing
  currently demands it.
- **`ADR-0001`/`ADR-0004` are untouched.** No scheme bit changes, no new scheme, no `CHMIX_MASKS`
  change. This decision governs what sounds *between* onsets; note selection *at* onsets is exactly
  as `ADR-0004` left it.
- **`ADS-108` §2.6 is scoped, not rewritten** — it describes onset selection only; D14 governs the
  rest of the note.
- Downstream: `04-requirements-engineering` amends `FR-1130`/`FR-1160` in place and `NFR-1270`'s
  basis; `05`→`06`→`07`→`08` carry it to code; `09-content-review` asks the ear the one question no
  measurement answers — **does the arpeggio still read as a constant looping figure?**
