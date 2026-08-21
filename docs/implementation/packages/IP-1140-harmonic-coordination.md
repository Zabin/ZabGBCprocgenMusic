# IP-1140 — Harmonic Coordination via a Shared Chord Context

| Field | Content |
|---|---|
| **Package ID** | `IP-1140` · mirrors `FS-114` · **Executor: `08-code-implementation`** · `FEAT-1150`, `BL-0119` remediation |
| **Objective** | Give the three pitched channels one shared harmonic context and derive each voice's note from it by role, **on the default boot path** — replacing the independent LFSR-delta note selection that `BL-0119` measured as the direct cause of 36.1 % harsh vertical intervals and the project owner's own "doesn't sound good" verdict. Bass alternates the current chord's root and fifth; melody takes a chord tone on strong onsets and a ±1 step on weak ones; the harmony voice takes a chord tone an octave below. The chord advances every 4 pulse-A onsets via a weighted, tonic-biased transition table. **Nothing unconditional is added to the per-frame path.** |
| **Requirements Covered** | `FR-1500`, `FR-1510`, `FR-1520`, `FR-1530`, `FR-1540`, `FR-1550`, `FR-1560` (operative half — see `FS-114` OQ2), `FR-1580` **as amended 2026-08-20** (reversed in place; absorbs the former `CR-0005`), `FR-1590`, `NFR-1240`, `NFR-1250`, `NFR-1260`, `NFR-1270`. **`FR-1570` is NOT covered and must not be claimed** — withdrawn unimplemented by `ADR-0004`. **`FR-1180` is unchanged**: scheme selection stays one bit per channel in `CHMIX_MASKS` bits 4-6; only the meaning of the `0` value changes. |
| **Architecture Components** | [`ADS-108`](../../architecture/ADS-108-harmonic-coordination.md) — **read §11 first**; §2.5, §2.7, §8 R1, §8 R7, D7 and D11 are withdrawn or superseded, and building against them would build the wrong thing. [`ADR-0004`](../../architecture/adr/ADR-0004-harmonic-coordination-replaces-the-default-walk-in-place.md) (binding). [`ADR-0003`](../../architecture/adr/ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md) — **superseded, never implemented; build no part of it.** [`ADR-0001`](../../architecture/adr/ADR-0001-scheme-selection-rides-chmix-preset-space.md) (reaffirmed in full). [`FS-114`](../../features/fs-114-harmonic-coordination.md) (the behavior contract, authoritative for every concrete value below). [`R225`](../../research/encyclopedia/R225-harmonic-coordination-shared-chord-context.md) (grounding + the affordability measurements). [`GDS-04` §4.1](../../architecture/04-domain-model.md) as amended 2026-08-20. |
| **Interfaces** | **No new routine and no new `engine_tick` call.** All work lands inside `_emit_channel_gen`'s existing per-channel onset branch, at the point where the LFSR-delta block currently sits, converging on the existing `gt_delta_ready_{suffix}` label with a signed delta in `B` — the same contract Scheme E's motif lookup already satisfies via `SUB_D`. `init_engine` gains three field initializations. `music_data.py` gains four pure-data tables, registered into the ROM data section by `build_rom.py`'s existing table-emission path (no new mechanism). |
| **Files to Create/Modify** | **`music_data.py`** — add `CHORD_TABLE` (4 scales × 4 chords × 3 tones, flattened to 48 bytes, entries are scale degrees 0-7), `CHORD_TRANSITION` (4 rows × 4 entries = 16 bytes, values 0-3), `MELODY_PICK = [0,1,2,1]`, `HARMONY_PICK = [2,0,2,1]` (chord-tone slot indices 0-2). **`music_engine.py`** — (1) three WRAM constants `CHORD_IDX = 0xC077`, `CHORD_ONSET_CTR = 0xC078`, `CHORD_TOGGLE = 0xC079`, each re-confirmed unclaimed by grep before writing (standing discipline); (2) `N_CHORD_ONSETS = 4`; (3) the harmonic-clock block in `gen_tick_pa`'s onset branch; (4) the three per-voice note-selection blocks replacing the LFSR-delta block on the non-Scheme-E path; (5) the `FR-1590` dissonance-skip jump; (6) pulse B's `octave_delta` `0 → -1` in `CHANNELS`; (7) the four new tables emitted with labels `chord_table`/`chord_transition`/`melody_pick`/`harmony_pick`; (8) `init_engine` writes `CHORD_IDX←0`, `CHORD_ONSET_CTR←4`, `CHORD_TOGGLE←0b10` on **both** boot and Select. **`test_rom.py`** — new `T22` suite; `T19` gains a chord-transition frame class; `T5`/`T6`-class assertions re-authored. **Untouched, confirmed by diff at close: `visuals.py`, `input_map.py`, `patterns.py`, `tiles.py`, `gbc_lib.py`, `wram_constants.py`, `build_rom.py`.** |
| **Implementation Tasks** | (1) Re-confirm `0xC077`-`0xC079` unclaimed by grep. (2) Author the four data tables in `music_data.py`, with the pentatonic rows written as idiomatic sonorities rather than stacked thirds (pentatonic has no semitones among its first five degrees, so third-stacking yields no triads — `FS-114` OQ3). (3) Emit the tables and add the WRAM constants. (4) Implement the harmonic clock inside `gen_tick_pa`'s onset branch: decrement `CHORD_ONSET_CTR`; on zero, step pulse A's LFSR, look up `CHORD_TRANSITION[CHORD_IDX*4 + (lfsr & 3)]`, write `CHORD_IDX`, reload the counter to 4, and **set** `CHORD_TOGGLE` bit1; otherwise **toggle** bit1. (5) Implement the wave rule (root/fifth by `CHORD_TOGGLE` bit0, then toggle bit0). (6) Implement the pulse A rule (strong → LFSR-picked chord tone via `MELODY_PICK`; weak → the existing `DELTA_TABLE` path, unchanged). (7) Implement the pulse B rule (LFSR-picked chord tone via `HARMONY_PICK`). (8) Convert each rule's target degree to the signed delta the existing path expects via `SUB_D`, exactly as Scheme E does — **do not** rebuild the downstream path. (9) `FR-1590`: make the harmonized limbs jump past the dissonance-override block and land in the stuck block, leaving Scheme E's flow through the dissonance block untouched. (10) Change pulse B's `octave_delta`. (11) `init_engine` initialization on both paths. (12) **Re-author the existing tests the feature deliberately breaks** — this is package work, not a follow-up. (13) Write `T22`. (14) Add `T19`'s chord-transition frame class. (15) Build, run the full suite, and **measure**: `VIS_ENTRY_LY` on chord-transition frames, and the strong-beat-partitioned interval distribution before/after. (16) Documentation updates below. |
| **Tests to Add** | New `test_rom.py` suite **`T22` — Harmonic Coordination**: (a) `CHORD_IDX` varies over a run and only ever holds 0-3. (b) `CHORD_IDX` changes on exactly every 4th pulse-A onset and on no other frame. (c) on wave onsets, `CUR_DEGREE_WV` ∈ {chord root, chord fifth} and alternates. (d) on strong pulse-A onsets, `CUR_DEGREE_PA` is one of the current chord's three tones. (e) on weak pulse-A onsets, `CUR_DEGREE_PA` moves by at most 1 (mod 8). (f) on pulse-B onsets, `CUR_DEGREE_PB` is one of the current chord's tones. (g) all three new bytes hold their specified values after boot **and** after Select. (h) the chord context tracks `SCALE_IDX` (press A, confirm chord tones come from the new scale's rows). **(c)-(f) must exclude frames where `BAD_ZONE_FLAGS`'s stuck bit is set** — stuck recovery deliberately forces a step off the chord tone, the same exclusion `T14.3`/`T16` already apply. **`T19`** gains a sixth frame class: `VIS_ENTRY_LY` within `144`-`153` on a chord-transition frame (`NFR-1260`). **Re-authored, not added**: `T5`/`T6`-class per-channel walk assertions (pulse B and wave no longer walk by ±1; pulse A still does on weak onsets), and any assertion on pulse B's register placement now that its octave moves. |
| **Documentation Updates** | `GDS-07` — three new WRAM rows (`0xC077`-`0xC079`), updated §6 headroom and next-free address, plus the four ROM tables. `Claude.md` — the WRAM quick-reference; the test count; a new "How to Change Things" entry for the chord tables; a Known Good Behavior entry stating plainly that **the boot sound has changed** and why; and a correction to the "Explicitly not built" line, which currently names chord-progression composition as unbuilt. `docs/features/INDEX.md`, `docs/implementation/packages/INDEX.md`, `00-master-build-plan.md` status rows. `docs/roadmap/04-release-roadmap.md` — no release row is claimed by this package (it is remediation, not a roadmap release); flag rather than edit if a row drifts. Per `BL-0028`'s standing recommendation, `Claude.md`'s test-count line and the GDS-07 rows are named here explicitly rather than left to be discovered. |
| **Definition of Done** | Every `FS-114` acceptance criterion (1)-(11) satisfied. `T22` exists and passes; `T19`'s chord-transition class passes; the re-authored `T5`/`T6`-class checks pass **against the new contract, and were genuinely re-derived rather than loosened until they stopped failing** — a check weakened to a tautology is not a passing check. Full suite green (G5). ROM builds to exactly 32768 bytes, valid header (G5). `visuals.py`/`input_map.py`/`gbc_lib.py`/`build_rom.py` untouched, confirmed by diff. **No new unconditional per-frame instruction anywhere** (`NFR-1240`) — confirmed by reading `engine_tick`'s call list, which must be unchanged. `VIS_ENTRY_LY` measured on chord-transition frames and within `144`-`153`; **a regression here is blocking, not absorbable** (`IP-9040`/`BL-0113` is the precedent). The strong-beat-partitioned before/after interval measurement is **captured and reported in this package's evidence**, whatever it says. **`FR-1570` is not claimed anywhere in this package's traceability.** |
| **Verification Checklist** | `09-package-verification` independently: rebuilds and re-runs the full suite; re-derives at least one chord transition by hand from `CHORD_TRANSITION` and the driving LFSR's actual state, rather than trusting `T22`(b); confirms on a live drive at a **non-default** `SCALE_IDX` and `OCTAVE_IDX` that chord tones follow the scale (the tables are per-scale, and a transcription error in one of four scale blocks would be invisible at the default); independently confirms `FR-1590` by driving the engine into a dissonant bad zone and checking that a strong-onset chord tone survives while a stuck-flag frame still forces a step; re-measures `VIS_ENTRY_LY` on chord-transition frames from its own drive; and **independently re-runs the strong-beat-partitioned interval measurement rather than accepting the implementing session's number** — `NFR-1270`/`BL-0122` exist precisely because the wrong instrument would report a working design as a failure. `09-content-review` separately applies `R224` §7a's holistic dimension. |
| **Dependencies** | `FEAT-1000`/`IP-0001`-`IP-0003` (shipped). `FEAT-1070`/`IP-1070` (`VERIFIED` — its `gt_delta_ready` convergence point and `SUB_D` idiom are reused verbatim; its Scheme-E path is left untouched). `FEAT-1030`/`IP-0007` (`VERIFIED` — reconciled with per `FR-1590`, not modified). **No dependency on any `SCHEME_TABLE` migration**: that work was obviated by `ADR-0004`, not deferred — `BL-0123` should be closed as **obviated**, not scheduled. All dependencies `VERIFIED`; this package is `READY`. |
| **Risks** | (1) **The VBlank budget killed `IP-9040`.** Mitigated structurally (zero unconditional per-frame work; the wave rule is net *cheaper* than the LFSR step plus `DELTA_TABLE` read it replaces; the melody's weak limb is the existing code) and measured explicitly. Still the single most likely reason this package fails. (2) **The boot sound changes, so "did tests break" no longer distinguishes a regression from the intended change.** This is why the before/after measurement, not the suite, is the acceptance instrument — and why task (12) demands genuine re-derivation rather than loosening. (3) **This package writes both `music_engine.py` and `music_data.py`, crossing the stage-08 code/content peer seam (`G1`).** Declared here rather than discovered at execution: the tables are meaningless without the mechanism and the mechanism cannot be tested without the tables, so splitting produces two packages neither of which is independently verifiable — the opposite of what the seam exists for. `08-code-implementation` executes both, with `music_data.py`'s edit confined to adding four pure-data tables and touching nothing else in that file. (4) **`DISSONANCE_THRESHOLD` may now be wrong.** A deliberate weak-beat passing tone is by construction what the detector flees, and `BL-0102` already reports bad-zone-at-boot. `FR-1590` removes the structural conflict but not the numeric one; out of scope, and a finding to file rather than a bar to lower. (5) **`BL-0119`'s remaining symptoms.** No rests, nothing formally resolving, and reduced-but-not-eliminated static runs remain — `CR-0003` owns all three. If the measurement passes but the listening still says "wandering," that routes to `CR-0003`, not back here. |
| **Rollback Considerations** | **Not purely additive — a revert is not a no-op.** Reverting restores the unharmonized independent walk as the boot behavior, and would need `FR-1580`'s amendment, `FS-114`, `FEAT-1150` and the re-authored tests reverted alongside, or the baseline and the code disagree. Because the change is confined to note *selection* — every downstream consumer (`CUR_DEGREE_*`'s meaning, the mute gate, the note tables, timers, bad-zone bookkeeping) is untouched — a revert is mechanically clean, a single-commit `git revert`, with no data migration and no persisted state to unwind. The prior commit's ROM is also the measurement baseline `NFR-1270` requires, so it must be buildable throughout this package's life regardless. |

### Authorization (G3)

**Status: `READY`, authorization `GRANTED 2026-08-20` — a standing grant for this increment,
recorded with its exact wording and its exact limits.**

The project owner's own words, this session, verbatim:

> "Don't hold the preset 0 to an arbitrary standard, it was developed by you at a previous
> iteration.
> Use your judgement on when it is best to start each, I'd like to get to a pleasant sounding music
> as soon as possible.
> Iterate pipeline until it is deemed pleasant and ready for human ears to review."

This is recorded as a **standing G3 authorization covering the packages that implement harmonic
coordination** (`BL-0119`; `FR-1500`-`FR-1590`/`NFR-1240`-`NFR-1270`), including `IP-1140` and any
follow-on remediation package this increment's own measurement produces. It follows the same
"standing forward authorization" convention this plan already records for `IP-1080`/`IP-1090` (the
2026-07-26 *"All work is pre authorized"* grant) and `IP-1110` (*"Iterate pipeline skill with pre
authorization as per before"*) — cited as the basis rather than assumed, exactly as `IP-1090`'s own
entry insists no package's G3 basis is ever assumed silently even when it rides a standing
instruction.

**What the grant does not cover**, stated so the limits are as legible as the grant: it does not
authorize work outside this increment; it does not waive `09-package-verification`'s fresh-session
independence rule; it does not waive G5's permanent gates; and it does not pre-authorize a
refactoring package (`IP-8xx0`), which this plan's own standing rule holds is never pre-authorized —
moot here, since `BL-0123`'s refactoring package is **obviated** by `ADR-0004` rather than deferred.

Two further things this same directive settled, recorded here because they are authorization-shaped
and would otherwise look like the pipeline deciding them for itself:

- **The preset-0 / index-0 no-regression standard is released.** `GDS-04` §4.1 carries the dated
  amendment separating the invariant's fixed-point half (stands) from its historical-no-regression
  half (released); `FR-1580` was reversed in place on that basis. This package is expected to change
  the boot sound.
- **`CR-0005`** (the default-preset flip) **moves from deferred into scope**, absorbed into the
  amended `FR-1580` rather than remaining a separately-gated later step.


---

## Implementation record — 2026-08-20 (`COMPLETE`, not `VERIFIED`)

**171/171 full suite (`T1`-`T22`). ROM 32768 bytes, valid header. `visuals.py`, `input_map.py`,
`gbc_lib.py`, `build_rom.py`, `patterns.py`, `tiles.py`, `wram_constants.py` untouched (diff-
confirmed). `engine_tick`'s call list is unchanged — no new per-frame call was added anywhere.**

### Measured result (the acceptance instrument, not the suite)

Boot defaults, 3600 frames, vertical-interval distribution across sounding pitched-channel pairs,
sampled at pulse-A onsets, **partitioned by metric strength** per `NFR-1270`/`BL-0122`:

| | strong-beat | weak-beat | aggregate |
|---|---|---|---|
| before (`3ade5a8`) | 23.3 % | 36.6 % | 30.0 % |
| after | **12.2 %** | 30.6 % | 21.5 % |

> **⚠️ CORRECTED 2026-08-21 — the four "after" figures above are OVERSTATED, and the table is left
> standing only so the correction is visible in the place the claim was made (`BL-0128`).**
>
> They were computed from `CUR_DEGREE`, which records **what this package's harmony layer intends**.
> `_emit_arpeggio_tick` (`IP-1060`) rewrites both pulse channels' frequency registers **every
> frame, after `gen_tick`**, adding `ARPEGGIO_OFFSETS` to that very degree — so the pitch that
> actually reached the APU was never measured. Re-measured on this same build and the same run with
> a driver that reproduces the table above **exactly** on its own basis (strong 12.0 % against the
> 12.2 % recorded, aggregate 21.8 % against 21.5 %), so the difference below is attributable to the
> instrument rather than to the run:
>
> | | strong-beat | weak-beat | aggregate |
> |---|---|---|---|
> | **after, on SOUNDING pitch** | **25.7 %** | **36.1 %** | **30.9 %** |
>
> The improvement this package delivered is **real but materially smaller than banked**, and the
> reason is now understood and packaged: the arpeggio places this package's carefully-chosen chord
> tones and then moves them off the chord for more than half the frames they sound — pulse B is
> placed on a chord tone at **100 %** of its onsets, yet only **46.4 %** of sounding pulse-channel
> frames are chord tones. `IP-1150` fixes the cause; `NFR-1270` has been amended to make sounding
> pitch the **normative** measurement basis so this cannot recur.
>
> This is the same class of error as this package's own `BL-0124` — which corrected *when* to
> sample — applied to **what** to sample, and it survived that correction. Both were caught by
> asking whether an arithmetically-impossible-looking number could be right; neither was caught by
> the suite.

`R225` §5f's simulation predicted 14.9 % on strong-beat sonorities and a much smaller aggregate
move; both parts of that prediction hold. m2/M7 and tritone are the components that collapse.
Bad-zone activity fell from 34/121 to 15/121 sampled onsets **with no threshold retuning** — the
generator stopped producing the dissonance rather than the detector being told to tolerate it,
which is the distinction `BL-0119` drew between a negative constraint and a positive generator.
`VIS_ENTRY_LY` on chord-transition frames: 152-153, inside VBlank (`NFR-1260`).

### A measurement-instrument correction that changes the reported baseline

The first driver derived intervals from the engine's own `SEMI_PA`/`PB`/`WV` bytes. Those are
written by `badzone_tick`, which `engine_tick` calls **after** `gen_tick`, while `pb.tick()`
returns between the two — the documented `R305`/`BL-0069` mid-frame sampling artifact. It was
therefore comparing this onset's degrees against last onset's semitones and manufacturing intervals
that were never sounded. Pitch classes are now derived in Python from degrees read at the same
instant, through `SEMITONE_TABLE_DATA`. **Both baselines were re-measured with the corrected
instrument**; the figures above are the corrected ones. The uncorrected run reported 33.3 % → 15.0 %
— a similar-looking improvement built on a broken measurement, which is worth recording because it
would have been easy to bank.

### Deviations from `FS-114`, each driven by measurement rather than convenience

1. **Pulse B's `octave_delta` stays 0** (`FS-114` specified `0 → -1` for `FR-1560`'s octave half).
   `FS-114` justified it as a build-time parameter costing no runtime work. That is true of the
   onset write and false of the system: `_emit_arpeggio_tick` runs **every frame** for pulse A/B and
   rewrites the frequency register from its own note-table lookup, which hardcodes `octave_delta=0`
   — so the onset would write the low octave and `arp_tick` would overwrite it the next frame,
   making the change inaudible rather than merely imperfect. Teaching `arp_tick` the offset costs 3
   **unconditional per-frame** instructions, which `NFR-1240` forbids and which is the exact cost
   class `IP-9040` was abandoned over (`BL-0113`). Withheld rather than paid, because the interval
   benefit it was reaching for is obtained by construction anyway: both pulses draw from the same
   triad, so a manufactured seventh is unreachable. **Follow-on candidate**: a cached per-channel
   note-table-index byte would make `arp_tick`'s lookup *cheaper* than it is today and carry the
   offset — a redesign beyond this package, filed for `07`.
2. **`HARMONY_PICK` replaced by `SLOT_NEXT`.** As specified, pulse A and pulse B drew independently
   from differently-weighted pick tables. Measured: they landed on the same pitch class **28 % of
   pulse-A onsets**, up from 13 % before the feature — they share an octave, so a quarter of the
   texture was two voices sounding as one. Pulse B now takes the slot one above whichever pulse A
   published in `CHORD_TOGGLE` bits2-3. Unison is now structurally impossible (measured 0 %), and
   the result is parallel thirds/sixths. This reads the **shared context**, not pulse A's private
   state, so `FR-1500` holds — `ADS-108` D1 forbids pairwise negotiation over private state
   (which needs inter-channel ordering guarantees) and explicitly endorses coordination flowing
   through a shared field. The ordering it does rely on is already guaranteed and already relied
   upon: `engine_tick` calls `gen_tick` in `CHANNELS` order, pulse A before pulse B, and `BL-0121`
   measured the two as phase-locked onto the same frame.
3. **`PASSING_TABLE` added for the melody's weak limb.** As specified, weak onsets reused
   `DELTA_TABLE` (`[-1, 0, 0, +1]`, deliberately 50 % "hold"). Measured: the melody got *less*
   shaped even as the harmony improved — mean directional run length fell 1.86 (pre-feature) to
   1.26, and the repeated-note rate stayed at 30 %, i.e. leap-then-hold rather than a line.
   `DELTA_TABLE`'s hold bias is right for an unaccompanied drunk walk and wrong for a note whose
   only job is to connect two chord tones. With `PASSING_TABLE` (always ±1): repeated-note rate
   **30 % → 4 %**, longest static run 8 → 3, and real 4-note figures now recur (`5,4,5,0` five times
   in a 183-onset run) where the pre-feature recurring figures were `(7,7,7,7)` and `(0,0,0,0)`.
   `DELTA_TABLE` itself is untouched and still serves Scheme E and every bad-zone recovery path.

### A real defect the re-authored tests caught

`CHORD_TOGGLE` was initialized `0b11`. Both its bass and parity bits are **toggled before they are
tested**, so the initial value must be the complement of the wanted first behaviour — `0b11` made
the first post-reset onset a *weak* passing tone where `FS-114` specifies a chord tone. Fixed to
`0b01`. This is precisely the failure a loosened `T5.5` would have missed: the old `T5.5` asserted
"`CUR_DEGREE_PA` ∈ {0, 1, 7}" from `DELTA_TABLE` reasoning that no longer describes the engine, and
would have passed on the wrong value.

### Outstanding, routed rather than fixed here

- **No rests, no phrase boundaries** (`CR-0003`). Reduced but not removed as a listening complaint;
  the melody alternates leap and step rather than sustaining phrases. Out of scope by design.
- **Weak-beat sonorities are 30.6 % harsh.** By construction — passing tones are non-chord tones —
  but it is the largest remaining number and a candidate for `09-content-review`'s ear.
- **`DISSONANCE_THRESHOLD` untouched** (`ADS-108` §9 OQ1). Bad-zone activity more than halved
  without retuning; whether the threshold is now *too* permissive is a listening question.
- **`FR-1560`'s literal wording** still says "distinct from the melody role's currently-sounding
  chord tone." The shipped `SLOT_NEXT` design now genuinely satisfies that in substance, but by a
  mechanism `FS-114` OQ2 argued was impossible. `04-requirements-engineering` should reword it at
  its next natural touch to describe derivation-from-the-shared-slot rather than a cross-channel
  read.
- **Fresh-session `09-package-verification` is owed** and is not waived by the standing G3 grant.
- **`09-content-review`** with `R224` §7a's holistic dimension is the other half of acceptance;
  WAV clips were captured for a human listening pass.
