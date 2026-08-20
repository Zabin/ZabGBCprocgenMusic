# ADS-108 — Harmonic Coordination via a Shared Chord Context

- **Status:** ✅ Authored 2026-08-19 · **Owned by:** `03-architecture-design-synthesis`
- **Dependencies:** [`R225`](../research/encyclopedia/R225-harmonic-coordination-shared-chord-context.md)
  (the grounding this ADS synthesizes — shared-context architecture, sparse functional transition
  tables, harmonic rhythm, root/fifth bass, chord-tone-on-strong-beat melody, cadence-as-chord-
  constraint, and the measured onset-schedule cost model);
  [`R211`](../research/encyclopedia/R211-melodic-harmonic-generation-techniques.md) §3 and its
  **§9 withdrawal** (the prior "do not attempt chord-progression harmony" position this work
  supersedes); [`R212`](../research/encyclopedia/R212-form-tension-and-macro-musical-parameters.md)
  §3 (cadence gap, partially reversed by `R225` §3f); `R203`/`R207` (channel roles); `R204`
  (the bad-zone detector this must be reconciled with); `R216` (`ARPEGGIO_OFFSETS`);
  [`ADS-100`](ADS-100-combinable-generation-schemes.md) + [`ADR-0001`](adr/ADR-0001-scheme-selection-rides-chmix-preset-space.md)
  (the per-channel scheme mechanism this extends, and the bit-space it has run out of);
  [`ADS-101`](ADS-101-genre-aware-style-presets.md) (the "parallel table keyed by the existing
  index" precedent this design reuses); [`ADS-102`](ADS-102-motif-recurrence-via-weighted-variant-selection.md)
  (Scheme E's motif variants, an interaction named honestly in §8);
  [`ADS-103`](ADS-103-song-form-and-style-drift-state-machine.md) (the per-frame state-machine
  shape this design deliberately does **not** copy); [`GDS-04`](04-domain-model.md) (the
  steering-index family and the index-0 invariant); [`GDS-06`](06-non-functional-requirements.md)
  §2.2a and [`GDS-07`](07-data-model.md) (the exhausted per-frame budget and the WRAM map);
  `BL-0119` (the measured defect), `BL-0113`/`IP-9040` (the abandonment that sets the cost bar).
- **Produces:** the future `FS-1xx`/`FEAT-1xxx` for harmonic coordination. **Authoring this ADS is
  not authorization to build it (G3).**

## 1. Executive Design Overview

Driftune's three pitched channels each own a private `CUR_DEGREE_*`, `LFSR_STATE_*` and
`NOTE_TIMER_*` and read **no field in common**. Every note is in key; nothing coordinates what the
notes are in key *together*. `BL-0119` measured the consequence on the shipped ROM: a near-uniform
vertical interval distribution — the signature of independent random processes — and **36.1 % harsh
pairs** (m2, M2, tritone, m7, M7). That is the direct, measured cause of the user's own verdict,
and it is an architecture gap. No amount of retuning `DISSONANCE_THRESHOLD`, `DELTA_TABLE` or the
scale tables changes it, because those constants govern how the engine *flees* bad harmony, not
whether it *constructs* good harmony.

**Central decision: introduce one shared harmonic context — a current-chord index in WRAM — that
every pitched voice reads at its own onset, and derive each voice's note from it by role.** The
bass takes the chord's root or fifth; the melody takes a chord tone on strong onsets and steps
between them on weak ones; the harmony voice takes a different chord tone an octave away. Nothing
listens to anything else; coordination flows through the single shared field. This is `R225` §3a's
structural finding, and it is what makes the cost linear in voices and the code local.

**Second central decision: all of it runs at onsets, none of it per frame.** `R101` §8.5 measured
`read_joypad`+`apply_input`+`engine_tick` consuming ~9 of VBlank's 10 scanlines on every frame, and
`IP-9040` was abandoned (`BL-0113`) for being unable to add a handful of instructions to that path.
`R225` §3h measured the escape route: **95.1 % of frames execute no pitched-onset branch at all**,
pulse A and pulse B are phase-locked (worst case 2 coincident onsets, not 3), and a chord change at
the chosen harmonic rhythm lands on ~0.8 % of frames. Every rule below therefore lives inside an
onset branch that already exists. `ADS-103`'s `song_tick` — an unconditional per-frame call — is
explicitly **not** the shape to copy; it was affordable in 2026-07 because it predates the budget
being measured as exhausted.

**Third: the mechanism is already half-shipped.** `music_data.py`'s `ARPEGGIO_OFFSETS = [0, 2, 4, 2]`
(`IP-1060`, `R216`) already stacks scale-degree thirds to imply a triad on one channel, inside
budget, under test. The delta this ADS designs is that those chord tones must be rooted on a
**shared** chord rather than on each channel's own wandering degree (`R225` §3g). This is a small
architectural change with a large audible consequence — not a new subsystem.

**Honest scope statement up front.** Increment 1 (this design) delivers the mechanism and makes it
reachable on a dedicated preset; it does **not** change what the ROM sounds like at boot, because
doing so breaks `GDS-04`'s index-0 invariant and a body of shipped tests. Flipping the default is a
separate, deliberate step (§2.7, D11) gated on a content review. The user's complaint is answered
at that step, not at this one — stated plainly so nobody reads increment 1 as the fix landing.

## 2. System Architecture

### 2.1 The shared context — three WRAM bytes

| Field | Addr | Role |
|---|---|---|
| `CHORD_IDX` | `0xC077` | Which row of `CHORD_TABLE` is currently sounding (0-3). The single field every pitched voice reads. |
| `CHORD_ONSET_CTR` | `0xC078` | Onsets remaining before the next chord transition. Counts **onsets, not frames** (§2.4). |
| `CHORD_TOGGLE` | `0xC079` | 1 bit of bass alternation state (root ↔ fifth) plus 1 bit of strong/weak onset parity for the melody voice. Packed, not two bytes. |

`GDS-07` records `0xC077` as the next free address. **`0xC020`-`0xC037` is not available** — it is
reserved for the `HIST_*` repetition buffers, unused in the shipped ROM but deliberately not
reclaimed (`BL-0013`); this ADS does not reclaim it either.

The context is **stored, not derived**. A derived form ("chord = `SONG_STATE_TIMER_HI` mod 4")
would cost arithmetic at every read site — i.e. on exactly the per-onset paths that run twice on a
busy frame — to save one byte of a resource that is not scarce (`R225` §5a).

### 2.2 Chord representation — a table of degrees, not degree arithmetic

`CHORD_TABLE[SCALE_IDX][chord][tone]` — 4 scales × 4 chords × 3 tones = **48 bytes of ROM**, every
entry a scale degree already in 0-7.

The obvious alternative — "chord tones are root, root+2, root+4 in scale degrees" — is **wrong on
this project's actual data**, and the ADS records why so no downstream FS re-invents it.
`SCALE_SEMITONES` rows are 8 entries whose 8th duplicates the 1st (`major` = `[0,2,4,5,7,9,11,12]`),
and `_emit_channel_gen` masks every degree `AND 0x07`. Third-stacking that crosses the octave seam
therefore lands one scale step wrong: the V chord's fifth is degree 4+4 = 8, which masks to 0 (C)
where the correct pitch is D (`R225` §5b, observed in that topic's own simulation before
correction). Widening the degree space to 12+ entries fixes it too, but costs +128 bytes of note
tables and touches every masking site in shipped, tested code. A hand-authored table takes the
octave decision at authoring time for free — and is exactly the LSDJ representation (`R225` §3g)
and this project's established "extend the table, not the mechanism" pattern (`R211` §8).

`pentatonic` gets an explicit call-out rather than a silent hole: its row is a 5-note scale packed
into 8 slots, so stacked thirds do not yield triads there at all. Its four rows must be authored as
pentatonic-idiomatic sonorities, not derived. The alternative — excluding pentatonic from
chord targeting — was rejected: it would make one of four user-selectable scales silently lose the
feature, which is a worse listener experience than an imperfect chord set (§9 OQ3).

### 2.3 Progression — a sparse, tonic-biased, asymmetric weighted table

`CHORD_TRANSITION[chord]` — 4 rows × 4 entries = **16 bytes**, indexed by 2 bits of the driving
channel's own LFSR, shaped exactly like `DELTA_TABLE` and `MOTIF_VARIANT_SELECTOR`: the
*distribution of entries*, not arithmetic, encodes the bias (`R211` §8).

Four chords (I, IV, V, vi), not more. `R225` §3a records that corpus clustering converges on
**three** functional categories; §3b records that the transition matrix is sparse, asymmetric, and
that IV and V hold a privileged position among non-tonic harmonies, with harmony spending long
periods on tonic-function chords and brief forays away. A 4-chord vocabulary with a tonic-return
bias is literature-shaped, not a concession to the hardware. Concrete weights are first-guess
placeholders (`BL-0005` class) — the *shape* is the architectural commitment.

### 2.4 Harmonic rhythm and where the clock lives

**One chord per 4 pulse-A onsets.** `R225` §3c grounds one-chord-per-bar as the popular-music
baseline; §3h measured pulse A's onset interval at 30 frames at boot defaults, making this ≈120
frames ≈ 2 s — and, critically, making it **tempo-tracking for free**, because the counter is in
onsets rather than frames and pulse A's onset interval is already derived from `TEMPO_IDX` and
`SONG_TABLE`.

The clock is decremented **inside `gen_tick_pa`'s existing onset branch**. Two properties make
pulse A the right driver, and both are load-bearing:

1. It is the fastest pitched onset (30 frames vs. the wave channel's 60), so the chord clock never
   starves.
2. Its onset bookkeeping **runs regardless of channel-mix gating** — `IP-9010` gates only the
   register writes, not the timer/degree/stale bookkeeping (`Claude.md`, `_emit_channel_gen`'s own
   docstring). A preset that mutes pulse A therefore still advances the harmony. Had gating skipped
   the branch, this design would silently stop working on preset rows that exclude pulse A.

The chord counter is deliberately **not** coupled to `SONG_STATE`'s timer. They are different
cadences (seconds vs. `R220`'s minutes-scale envelopes), and `IP-1100` documents disjointness from
every other mechanism as a property worth preserving — the same reasoning `ADS-103` and `ADS-107`
each applied to their own state.

### 2.5 Scheme H — a third note-selection scheme, and the bit-space problem it exposes

Harmonic note selection is a **third per-channel scheme, "Scheme H,"** alongside Scheme W (the LFSR
walk) and Scheme E (Euclidean-gated motif). This follows `ADR-0001`'s established extension point —
but `ADR-0001`'s carrier has run out of room. `CHMIX_MASKS` gives each preset one byte: bits 0-3
are the channel mask, bits 4-6 are **one** scheme bit per pitched channel, bit 7 is spare. Three
schemes need two bits per channel; six bits are not there.

**Decision: a parallel `SCHEME_TABLE` keyed by `CHMIX_IDX`** — 8 bytes, one per preset, 2 bits per
pitched channel (pa 0-1, pb 2-3, wv 4-5), values 0=W, 1=E, 2=H. This is precisely the move
`ADS-101` already made when `CHMIX_MASKS` ran out of bits for a 4-field style bundle: a parallel
table keyed by the *same* index, not a wider mask. `CHMIX_MASKS` bits 4-6 are then **retired**, not
left as a shadow source of truth — with a hard non-regression obligation on the migration:
`SCHEME_TABLE` must reproduce today's bits 4-6 exactly for all 8 presets, and preset 6's Scheme-E
wave assignment (`ADS-100`'s own worked example, covered by shipped tests) must be byte-for-byte
preserved. Two rejected alternatives are recorded in §10 (widen `CHMIX_MASKS` to 16 bits; make
harmony a global on/off flag).

### 2.6 Per-voice rules

Ordered as `R225` §5d orders them — ascending cost, descending impact — because each is
independently shippable and independently audible. A downstream `07` should not package them as one
indivisible unit.

| Voice | Rule under Scheme H | Cost shape |
|---|---|---|
| **Wave (bass)** | On onset: degree = `CHORD_TABLE[scale][CHORD_IDX][0]` (root) or `[2]` (fifth), alternating via `CHORD_TOGGLE`'s bass bit | **Replaces** the LFSR walk — one table read instead of an LFSR step plus a `DELTA_TABLE` read. Plausibly *cheaper* than what it displaces |
| **Pulse A (melody)** | Strong onset (parity bit set): degree = a chord tone, which of the three drawn from 2 LFSR bits. Weak onset: the existing `DELTA_TABLE` walk, constrained to ±1 (a passing/neighbour tone) | One extra branch; both limbs already exist in `_emit_channel_gen` |
| **Pulse B (harmony)** | On onset: a chord tone offset within the triad from pulse A's, placed **an octave apart** via the existing `octave_delta` parameter | Same table read; the octave placement is a build-time parameter, not runtime work |

The octave placement is a real instruction, not a preference. `R225` §5f measured that separating
pulse B by **+2 scale degrees** from a chord tone manufactures sevenths against the bass, while
separating it by a whole octave does not — same cost, materially different result. It is also a
deliberate change to pulse B's shipped register placement, and is flagged as such in §8.

Predicted effect, from `R225` §5f's simulation (a model, not an audio claim; it reproduces the
shipped ROM's measured distribution to within ~3 points, which is why it is quoted at all): harsh
intervals **32.6 % → 14.9 % on strong-beat sonorities**, with m2 6.1 %→1.3 % and tritone
2.8 %→0.7 %.

### 2.7 What is deliberately out of increment 1

- **Phrase structure, rests and cadence.** `R225` §3f establishes these become cheap once a chord
  context exists — a half cadence is "end the phrase on V," a perfect authentic cadence is "end on
  I," i.e. two forced values of `CHORD_IDX` at two known counter positions, and a rest is an onset
  whose trigger write is skipped. The design is *reserved*, not re-litigated later: a `PHRASE_POS`
  byte at `0xC07A` and the two cadence constraints above are increment 2's shape. Deferred because
  it multiplies the verification surface, and because the three voice rules above are audible
  without it.
- **Flipping the default preset to Scheme H** (§1, D11).
- **Harmonizing Scheme E** (§8).
- **Re-rooting the `IP-1060` arpeggio** (§8).

## 3. Domain Model

Three new entities join `GDS-04`'s set:

- **Chord** — a set of three scale degrees, identified by an index into a per-scale table. Not a
  pitch set: it is scale-relative, so `SCALE_IDX` and `OCTAVE_IDX` changes flow through it
  unchanged, exactly as `CUR_DEGREE_*` already does.
- **Harmonic clock** — an onset-counted countdown owned by pulse A's onset branch, whose expiry is
  the only event that writes `CHORD_IDX`. Single-writer, unlike `GDS-04`'s steering-index family
  (`TEMPO_IDX`/`DENSITY_IDX` each have three writers under a last-write-wins contract). Keeping it
  single-writer is deliberate: a second writer would reintroduce exactly the coordination ambiguity
  this design exists to remove.
- **Scheme assignment** — promoted from a bit inside `CHMIX_MASKS` to a field of its own
  (`SCHEME_TABLE`), because it now has three values rather than two.

`CHORD_IDX` is a **read-mostly broadcast field**: one writer, three readers, all reads at onsets.
That shape — not the chord vocabulary — is the architectural content of this ADS.

## 4. User Stories

- *As a listener*, when several channels sound together I hear them as playing the same music,
  rather than three things happening at once. (`BL-0119`'s measured defect, stated from the ear.)
- *As a listener*, the low voice sounds like a bass line supporting what is above it, rather than a
  third melody wandering by step. (`BL-0119` (c).)
- *As a listener*, I can tell when the harmony moves and when it stays — the music has somewhere to
  return to.
- *As a reviewer running `09-content-review`*, I have a holistic question that can surface "the
  voices don't sound like they're playing together" (`R224` §7a, added for exactly this defect).
- *As the engine*, I remain able to detect and recover from a genuine bad zone, without the recovery
  mechanism fighting the harmony generator (§2 / D8).

## 5. Functional Requirements (candidates, for `04-requirements-engineering`)

| ID | Statement | Traces to |
|---|---|---|
| FR-1500 | The engine maintains a current-chord index in WRAM that every pitched channel reads at its own onset. | `R225` §3a; `BL-0119` |
| FR-1510 | Chord membership is a ROM table of scale degrees per (scale, chord), all entries within the shipped 0-7 degree space; no runtime third-stacking arithmetic. | `R225` §3g/§5b |
| FR-1520 | The current chord advances via a weighted transition table indexed by LFSR bits, over a 4-chord vocabulary with a tonic-return bias. | `R225` §3a/§3b; `R211` §8 |
| FR-1530 | The chord advances once per N pulse-A onsets (N=4 as shipped), counted in onsets so the harmonic rhythm tracks tempo automatically. | `R225` §3c/§5c |
| FR-1540 | A Scheme-H wave channel sounds the current chord's root or fifth, alternating, instead of an LFSR walk. | `R225` §3d; `R203`/`R207` |
| FR-1550 | A Scheme-H pulse A sounds a chord tone on strong onsets and a ±1 step on weak onsets. | `R225` §3e |
| FR-1560 | A Scheme-H pulse B sounds a chord tone an octave apart from pulse A's. | `R225` §5d/§5f |
| FR-1570 | Per-channel scheme selection moves to a parallel `SCHEME_TABLE` keyed by `CHMIX_IDX`, with 2 bits per pitched channel; the migration reproduces every current `CHMIX_MASKS` bits-4-6 assignment exactly. | `ADR-0001`; `ADS-101` precedent |
| FR-1580 | Preset 0 remains all-Scheme-W; increment 1 changes nothing about boot behavior. | `GDS-04` index-0 invariant |
| FR-1590 | Bad-zone dissonance recovery does not override a Scheme-H channel's strong-onset chord tone; stuck and overload recovery are unchanged. | §2 / D8; `R225` §5e; `R204` |

## 6. Non-functional Requirements (candidates)

| ID | Statement | Traces to |
|---|---|---|
| NFR-1240 | No mechanism in this design adds unconditional per-frame work; every added instruction executes only inside an already-taken onset branch. | `GDS-06` §2.2a; `R101` §8.5; `BL-0113` |
| NFR-1250 | Added ROM cost stays within ~100 bytes of tables (`CHORD_TABLE` 48 + `CHORD_TRANSITION` 16 + `SCHEME_TABLE` 8) plus the emitted code, against the recorded free-ROM headroom. | `GDS-06` ROM budget |
| NFR-1260 | `VIS_ENTRY_LY` (`T19`) stays within `144`-`153` on every frame class including a chord-transition frame — a chord-transition frame class is added to `T19`'s existing five. | `IP-9030`; `GDS-06` §2.2a |
| NFR-1270 | Harmonic quality is verified on **strong-beat sonorities**, partitioned by metric strength, not on an aggregate interval histogram over all onsets. | `R225` §5f; `R224` §7b |

`NFR-1270` is not bookkeeping. A chord-tone/passing-tone design deliberately sounds non-chord tones
on weak beats; measured in aggregate it improves only modestly (32.6 %→28.5 % modelled) while the
strong-beat figure it is actually designed to move goes 32.6 %→14.9 %. Verifying against the
aggregate would report a working design as a failing one.

## 7. Constraints

1. **The per-frame budget is exhausted and measured.** `R101` §8.5; `IP-9040` was abandoned over a
   handful of instructions. This is the hardest constraint in the project and it is what shapes
   §2.4's entire design.
2. **The degree space is 8 entries with a duplicated octave and an `AND 0x07` mask** everywhere
   (§2.2). Any design that needs degrees above 7 pays for widening it.
3. **`CHMIX_MASKS` has no bits left** for a third scheme (§2.5).
4. **The index-0 invariant** (`GDS-04`): preset 0 must not regress. This is what forces the staged
   default flip (D11).
5. **SM83 has no division and this project's opcode subset has no ADC/SBC** (`R216`'s vibrato note)
   — every constant here must be a power of two or a table entry. N=4 onsets per chord and a
   4-entry transition row are both chosen to wrap with a plain `AND`.
6. **No sprite/OAM budget is involved** — this design is audio-only; `visuals.py` is untouched.

## 8. Risks

| # | Risk | Assessment |
|---|---|---|
| R1 | **The `CHMIX_MASKS`→`SCHEME_TABLE` migration touches shipped, tested behavior.** Preset 6's Scheme-E wave assignment is covered by existing tests. | Real but bounded: the migration is mechanical and has an exact non-regression oracle (reproduce all 8 presets' current bits 4-6). Should be its own package, sequenced first. |
| R2 | **Pulse B's octave move changes the shipped mix.** Increment 1 puts pulse B an octave from pulse A on Scheme-H presets only, so preset 0 is unaffected — but it is a deliberate timbral change wherever Scheme H is active. | Accepted, scoped to Scheme-H presets, and named here rather than discovered in review. |
| R3 | **Scheme E stays harmonically uncoordinated.** `MOTIF_TABLE` holds absolute degrees with no chord awareness, so a preset mixing an E channel with H channels will have one voice ignoring the harmony. | Disclosed, not solved. Increment 1's preset set should pair H channels together. Increment 2's path is named: transpose the motif's degrees by the chord root — a single `ADD` at the motif lookup, not a redesign (`ADS-102` untouched). |
| R4 | **The `IP-1060` arpeggio is not re-rooted.** Under Scheme H, `CUR_DEGREE` is a chord tone, and `ARPEGGIO_OFFSETS = [0,2,4,2]` stacks diatonic thirds *from it* — so an arpeggio starting on the third implies the chord's upper extensions rather than the chord. | Analyzed and accepted for increment 1: stacked diatonic thirds from any tone of a diatonic triad land on tones of the same or a closely-related triad, so the result is benign rather than wrong. Re-rooting would put a table read on the arp sub-tick — nearer the per-frame path — which `NFR-1240` will not fund without measurement. Content review measures it. |
| R5 | **The bad-zone detector may fight the generator.** A deliberate weak-beat passing tone is, by construction, dissonance the detector exists to flee; `DISSONANCE_THRESHOLD` was never tuned by ear (`BL-0005`) and `BL-0102` already reports a bad-zone-at-boot condition. | Addressed structurally by `FR-1590` (recovery never overrides a strong-onset chord tone) and left open numerically (§9 OQ1). Deleting the bad-zone system was considered and rejected — D8. |
| R6 | **The design could be judged by the wrong metric** and reported as a failure. | Mitigated by `NFR-1270` and `R224` §7b, which exist because this risk was identified during the research pass, not after a review went wrong. |
| R7 | **Increment 1 does not answer the user's complaint.** The default preset still sounds exactly as it does today. | Deliberate (D11) and stated in §1. The risk is that it reads as the work being done; this document says twice that it is not. |

## 9. Open Questions

1. **What should `DISSONANCE_THRESHOLD` be, once the interval distribution is deliberately
   non-uniform?** Cannot be answered from a design document — needs a measured/heard comparison.
   → `09-content-review` (with `BL-0102`'s bad-zone-at-boot finding, which is the same question
   from the other end).
2. **When does preset 0 flip to Scheme H?** The gate is evidence that the harmonized presets
   actually sound better, not a schedule. → `09-content-review` produces the evidence; the flip
   itself needs `04`'s amendment of the index-0 invariant and the user's call.
3. **What are pentatonic's four chord rows?** Stacked thirds do not apply (§2.2); the right answer
   is idiomatic rather than derivable. → `02-research-game-design` if a citation is wanted,
   otherwise `08-content-authoring` judgement recorded as a first-guess table.
4. **Is N=4 onsets per chord right?** First-guess, `BL-0005` class. → `09-content-review`.
5. **Should the chord clock survive a change of driving channel?** Today pulse A is always the
   fastest pitched onset; a future per-channel `tempo_mult` change could break that assumption
   silently. → flagged for whichever `06`/`07` pass touches `tempo_mult`; not worth defending
   against now.
6. **Does increment 2 harmonize Scheme E** (R3's named path), or do the two schemes stay separate
   voices by design? → `03` again, when increment 2 is scoped.

## 10. Decision Log

| # | Decision | Rationale | Alternatives rejected |
|---|---|---|---|
| D1 | **One shared current-chord field in WRAM; all voices read it, none listen to each other.** | `R225` §3a: what makes multi-voice systems cohere is that a shared field exists, not the sophistication of its contents. Keeps cost linear in voices and every rule local. | Pairwise voice negotiation (needs inter-channel reads and ordering guarantees); constraint solving (`R215` already found it unaffordable). |
| D2 | **Store the chord index; do not derive it.** | Derivation costs arithmetic at every read site — the per-onset paths that run twice on a busy frame — to save a byte that is not scarce (`GDS-07`: 0xC077 free). | Deriving from `SONG_STATE_TIMER_HI`. |
| D3 | **Chord membership is a hand-authored per-scale degree table, not runtime third-stacking.** | Third-stacking is *incorrect* on this data: the `AND 0x07` mask over an 8-entry table whose 8th duplicates the 1st puts the V chord's fifth a step wrong (`R225` §5b). A table takes the octave decision at authoring time, matches LSDJ's own representation, and follows "extend the table, not the mechanism." | Widening the degree space to 12+ entries (+128 B of note tables, touches every mask site in tested code); excluding pentatonic (silently loses the feature on one of four scales). |
| D4 | **Four chords (I, IV, V, vi), sparse tonic-biased weighted transition table.** | `R225` §3a (corpus clustering converges on three functional categories), §3b (matrix sparse and asymmetric; IV and V privileged; long dwells on tonic). Reuses `DELTA_TABLE`'s exact weighted-lookup mechanism (`R211` §8). | A larger diatonic set (more table, no evidence it helps); a uniform transition table (contradicts every corpus cited). |
| D5 | **Harmonic rhythm counted in pulse-A onsets (N=4), not frames.** | `R225` §3c's one-chord-per-bar baseline; counting onsets makes it track `TEMPO_IDX`/`SONG_TABLE` for free instead of drifting out of phase with them. | Frame counter (drifts with tempo); coupling to `SONG_STATE`'s timer (wrong cadence, and breaks `IP-1100`'s deliberate disjointness). |
| D6 | **The chord clock lives inside `gen_tick_pa`'s existing onset branch — no new per-frame tick.** | The load-bearing cost decision. 95.1 % of frames take no pitched-onset branch (`R225` §3h); a per-frame `chord_tick` would add work to 100 % of them, which `BL-0113`/`IP-9040` proved unaffordable. Pulse A is the fastest pitched onset and its bookkeeping runs even when mix-excluded (`IP-9010`), so the clock never starves or stalls. | Copying `ADS-103`'s `song_tick` shape (per-frame; affordable in 2026-07 only because it predates the measurement). |
| D7 | **Scheme H is a third per-channel scheme, carried by a new parallel `SCHEME_TABLE` keyed by `CHMIX_IDX`; `CHMIX_MASKS` bits 4-6 are retired into it.** | `ADR-0001`'s bit space is full (1 bit/channel, 3 values needed). `ADS-101` already solved this exact problem the same way — a parallel table keyed by the same index. Retiring rather than shadowing avoids two sources of truth. | Widening `CHMIX_MASKS` to 16-bit entries (a 2-byte fetch on a hot path, and it breaks every existing single-byte read); a global harmony on/off flag (throws away per-channel role assignment, which is the whole point). |
| D8 | **Keep the bad-zone system; make it scope-aware rather than deleting or overriding it.** Dissonance recovery must not override a Scheme-H channel's strong-onset chord tone; stuck and overload recovery are untouched. | The two are not redundant: chord targeting removes *unintended* dissonance, bad-zone recovery is the safety net for states it cannot prevent (stuck notes, overload, density/mix corners) — `R225` §5e. A tonic-pull that overrides a chord tone silently un-harmonizes the very mechanism being added. Stuck/overload are orthogonal to harmony and need no change. | Deleting the bad-zone system (loses real, shipped, tested recovery — `IP-0007`, `T10`); letting it override unchanged (fights the generator by construction). |
| D9 | **Voice roles: wave = root/fifth, pulse A = chord tone on strong / step on weak, pulse B = chord tone an octave apart.** | `R225` §3d (root/fifth is the supportive bass figure *and* is mode-independent, so it needs no per-chord quality table), §3e (the strong/weak rule is the entire mechanism that converts "in key" into "in harmony"), §5f (octave separation, not degree separation, is what avoids manufactured sevenths). Wave first because it is the cheapest and fixes `BL-0119` (c) outright. | Separating pulse B by +2 scale degrees (measured to manufacture sevenths against the bass, same cost); leaving the wave channel on its walk (it is the measured worst offender). |
| D10 | **Phrase structure, rests and cadence are increment 2, with their shape reserved here.** | `R225` §3f makes them cheap (two forced `CHORD_IDX` values at known counter positions; a rest is a skipped trigger write) — but they multiply the verification surface, and the three voice rules are audible without them. Reserving the shape (a `PHRASE_POS` byte, the HC/PAC constraints) stops increment 2 re-litigating the design. | Shipping everything at once (a large, hard-to-verify increment against an unforgiving budget); deferring without recording the shape (loses `R225` §3f's reversal of `R212`'s negative result). |
| D11 | **Increment 1 does not change boot behavior; preset 0 stays all-Scheme-W and the default flip is a separate, evidence-gated step.** | `GDS-04`'s index-0 invariant and a body of shipped tests both assume today's boot sound. Changing what the ROM sounds like at boot should be an explicit, separately-authorized decision with heard evidence behind it, not a side effect of landing a mechanism. | Flipping preset 0 in the same increment (breaks the invariant and a test body in the same change that introduces the mechanism, so a regression could not be attributed); never flipping it (leaves the user's actual complaint unanswered — which is why the flip is *scheduled*, not merely allowed). |
| D12 | **Verification is on strong-beat sonorities, partitioned by metric strength.** | `R225` §5f/`R224` §7b: the aggregate histogram is the right instrument for detecting the *absence* of coordination and the wrong one for verifying its *presence*, because weak-beat non-chord tones are deliberate. | Reusing `BL-0119`'s aggregate metric as the acceptance criterion (would report the design as a near-failure at 28.5 % when the figure it moves is 14.9 %). |

---

## 11. Amendment — 2026-08-20: the released invariant, and the parallel scheme it deletes

**Status:** ✅ Amended 2026-08-20 · **Owned by:** `03-architecture-design-synthesis` ·
**Produces:** [`ADR-0004`](adr/ADR-0004-harmonic-coordination-replaces-the-default-walk-in-place.md),
which supersedes [`ADR-0003`](adr/ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md).

### 11.1 Why this document is being reopened

`ADS-108` as authored above rests, in six separate places (§1's "Honest scope statement," §2.5,
§2.7, §7 constraint 4, D11, §8 R7), on one premise: **preset 0's audible behavior may not change.**
That premise came from `GDS-04` §4.1's index-0 invariant. It is the reason harmonic coordination
was designed as a *parallel* Scheme H sitting beside the default rather than *as* the default, and
it is therefore the reason `CHMIX_MASKS` ran out of bits — which is the entire reason `ADR-0003`'s
`SCHEME_TABLE` migration exists.

**The user has released that premise**, in these words:

> "Don't hold the preset 0 to an arbitrary standard, it was developed by you at a previous
> iteration.
> Use your judgement on when it is best to start each, I'd like to get to a pleasant sounding music
> as soon as possible.
> Iterate pipeline until it is deemed pleasant and ready for human ears to review."

This is not a tuning preference; it removes a stated architectural constraint. Reopening the design
on the record — rather than letting a downstream stage quietly build something `ADS-108` argues
against — is what §10's own "an unrecorded decision effectively didn't happen" discipline requires.
`GDS-04` §4.1 is amended in step (see §11.5); this section does not release an invariant that its
owning level still asserts.

### 11.2 The question, stated precisely

Does harmonic coordination need to be a *third* per-channel scheme (Scheme H) selected by a new
`SCHEME_TABLE`, or can it replace the note-selection step of the *existing default* scheme
(Scheme W) in place?

The two are not different musical designs. They are the same mechanism — `CHORD_IDX`,
`CHORD_TABLE`, `CHORD_TRANSITION`, the three per-voice rules of §2.6 — carried by two different
selection structures. Everything in §2.1-§2.4, §3, §5's `FR-1500`-`FR-1560` and §6 is unaffected by
the answer. What the answer decides is §2.5, `FR-1570`, `FR-1580`, `ADR-0003`, and `BL-0123`'s
entire refactoring package.

### 11.3 Decision — D13: harmonic coordination replaces the default scheme's note selection in place

**The chord-derived note selection becomes what the default scheme does. No third scheme, no
`SCHEME_TABLE`, no `CHMIX_MASKS` migration.** `ADR-0001`'s one-bit-per-channel packing (bits 4-6,
`0` = default, `1` = Scheme E) is retained unchanged; the meaning of the `0` value changes from
"unharmonized LFSR walk" to "chord-derived selection." Scheme E is untouched — still selected by
bit value `1`, still unharmonized, exactly the deferral §8 R3 already recorded.

**Reasoning, in the order the reasons actually bind:**

1. **The parallel structure existed only to protect preset 0.** §2.5 does not argue that three
   schemes are musically desirable; it argues that a third scheme is *needed* because Scheme H must
   coexist with an untouchable default. With the premise gone, the requirement to coexist goes with
   it. Reread as a standalone argument, §2.5 says "we need two bits per channel because we need
   three values" — and the third value existed only to keep the first one reachable.
2. **Three values are not needed, because the third value is now unwanted.** An unharmonized
   independent random walk is `BL-0119`'s measured defect, not a mode worth spending a bit to
   preserve. Retaining it as selectable would keep, as shipped behavior, the exact thing this
   increment exists to remove. Before/after comparison — the one legitimate reason to want both —
   is available from git at zero ROM cost by rebuilding the prior commit.
3. **Scheme E already occupies the "other" slot and is explicitly staying unharmonized.** §8 R3
   defers harmonizing Scheme E to increment 2. The reachable scheme *set* in increment 1 is
   therefore {harmonized default, Scheme E} — two values, one bit, which is precisely what
   `ADR-0001` already provides. `ADR-0003` would migrate a table to make room for a value
   increment 1 does not create.
4. **It answers the user's actual complaint in increment 1 rather than increment 2.** §1's own
   scope statement concedes that increment 1 "does not change what the ROM sounds like at boot,"
   and §8 R7 records the risk that this "reads as the work being done." Under D13 that risk is
   deleted rather than mitigated: the mechanism and the audible improvement land together, in one
   package, measurable by one before/after comparison. The user's directive names speed to audible
   improvement as the optimization target.
5. **It removes a whole package of non-regression risk instead of managing it.** `BL-0123` and §8
   R1 both treat the `CHMIX_MASKS`→`SCHEME_TABLE` migration as real structural surgery on shipped,
   tested code needing its own `IP-8xx0` package, its own equivalence oracle, and its own
   verification pass — all of it delivering, by construction, **zero** audible change. Under D13
   that work is not sequenced earlier or made cheaper; it does not exist. The safest structural
   surgery is the kind that is not performed.
6. **The code shape is strictly smaller.** `_emit_channel_gen` already converges both existing
   schemes on a single `gt_delta_ready_{suffix}` label carrying a signed delta in `B`. Chord-derived
   selection produces a *target degree*, and the `SUB_D` idiom Scheme E's own motif lookup already
   uses converts a target into exactly that delta. The change is therefore a **replacement of the
   LFSR-delta block on the existing fall-through path**, not a new branch: no added scheme test, no
   widened table read, and §2.6's cost analysis holds a fortiori. `NFR-1240` (nothing unconditional
   per frame) is satisfied more easily under D13 than under §2.5, not less.

**What is given up, recorded honestly.** The unharmonized walk stops being reachable in the shipped
ROM. Three shipped-behavior assumptions break with it: the boot sound changes; `T5`/`T6`-class tests
that assert the specific ±1 stepwise degree walk stop describing the engine and must be re-authored
against the new contract; and any future "turn harmony off" ask needs a bit rather than reusing an
existing one. The first two are exactly what the user's release authorizes and expects. The third is
a genuine, accepted cost — mitigated by the fact that `CHMIX_MASKS` bit 7 is still spare, so the
door `ADR-0001` left open remains open, and `ADR-0003` stays on file as the recorded design should a
*fourth* per-preset concern ever need it.

### 11.4 Consequences for this document

| Clause | Disposition under D13 |
|---|---|
| §2.5 (Scheme H + `SCHEME_TABLE`) | **Withdrawn.** Retained above as superseded reasoning, not as the design. Its bit-space analysis remains correct *given* three schemes; D13 removes the third. |
| §2.6 (per-voice rules) | **Unchanged**, now applied to the default scheme. "Scheme H" in that table reads "the default scheme." |
| §2.7 (default-preset flip deferred) | **Withdrawn.** There is nothing to flip: the default *is* the harmonized path. `CR-0005` is absorbed into increment 1. |
| §7 constraint 4 (index-0 invariant) | **Amended** — see §11.5. The determinism half stands; the historical-no-regression half is released. |
| §8 R1 (migration risk) | **Deleted with its cause.** No migration is performed. |
| §8 R2 (pulse B octave move) | **Widened, not narrowed** — it now applies at boot rather than only on Scheme-H presets. A deliberate change to the shipped mix, disclosed here rather than discovered in review. |
| §8 R3 (Scheme E unharmonized) | **Unchanged and now sharper**: preset 6 mixes an unharmonized Scheme-E wave against harmonized pulses. Disclosed; increment 2's named path (transpose the motif by the chord root) is unaffected. |
| §8 R5 (bad-zone fights the generator) | **Unchanged and now increment-1-critical**, because the harmonized path is the boot path. `FR-1590`'s structural answer is not optional polish here. |
| §8 R7 (increment 1 doesn't answer the complaint) | **Deleted.** Increment 1 now answers it. |
| D7, D11 | **Superseded by D13** (D7's `ADR-0003` superseded by `ADR-0004`). |
| D1-D6, D8-D10, D12 | **Unchanged.** D8 (bad-zone stays, scope-aware) and D12 (strong-beat-partitioned verification) are load-bearing under D13 exactly as written. |
| §5 `FR-1570`/`FR-1580` | Routed to `04-requirements-engineering` for amendment; see §11.6. |

### 11.5 The index-0 invariant, narrowed rather than deleted

`GDS-04` §4.1 conflates two rules under one name, and only one of them is released:

- **(a) The fixed-point rule** — *index 0 of every steering-index-keyed table equals the boot
  preset's values, so boot and Select-reset land on identical, deterministic, known-good state.*
  **This stands, unchanged and load-bearing.** It is what `IP-1100`'s ten-test regression actually
  proved: phase 0 diverging from the boot preset broke boot/Select agreement *with each other*, not
  agreement with any historical recording. Every new index-keyed table this increment adds still
  inherits it.
- **(b) The historical-no-regression rule** — *the boot preset's audible result must never differ
  from what previously shipped.* **Released**, by the user's own words quoted in §11.1, as
  self-imposed. It never had an independent architectural justification; it was (a)'s reputation
  borrowed by a different claim.

The distinction matters beyond this increment: a future mechanism may now change the boot *sound*
deliberately, but still may not give index 0 a row that disagrees with the boot preset.

### 11.6 Routing

- `04-requirements-engineering` — amend `FR-1570` (withdraw: no `SCHEME_TABLE` migration) and
  `FR-1580` (withdraw: boot behavior *is* what changes); reconcile `FR-1260`'s index-0 guarantee
  with §11.5's (a)/(b) split; move `CR-0005` into scope. Follow that document's own append-only
  dated Delta Review convention.
- `07-implementation-planning` — `BL-0123`'s `IP-8xx0` refactoring package is **not owed**; close it
  as obviated rather than scheduling it.
- `09-package-verification` — D12/`NFR-1270`'s strong-beat partition is now the acceptance
  instrument for a change audible at boot, so the before/after comparison is against the prior
  commit's ROM rather than against a non-default preset.
