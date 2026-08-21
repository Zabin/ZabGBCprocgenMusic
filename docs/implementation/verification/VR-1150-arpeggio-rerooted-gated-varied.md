# VR-1150 — The Arpeggio Re-rooted, Gated and Varied

| Field | Content |
|---|---|
| **Package** | [`IP-1150`](../packages/IP-1150-arpeggio-rerooted-gated-varied.md) — the arpeggio re-rooted, gated and varied (`FS-115`/`FEAT-1160`, `BL-0127`, riding `BL-0125`/`BL-0128`/`BL-0130`) |
| **Commit verified** | `850e64e` (branch `claude/controls-explanation-28fpbh`). Comparison build: `3e635ed` (`IP-1140` as shipped, the `NFR-1270`/`NFR-1280` baseline this package names). |
| **Date** | 2026-08-21 |
| **Independence** | **Genuinely fresh session.** This session has implemented nothing. It verified `IP-1140` earlier the same run — a different package, which does not compromise independence for this one (the rule bars verifying *one's own implementation work*, and no implementation work was done). |
| **Result** | ✅ **VERIFIED** — 0 failed checks. 3 findings, all Low/Low-Medium, none blocking. |

---

## 0. Measurement basis (`NFR-1270` as amended, and the output-boundary rule)

Same instrument as [`VR-1140`](VR-1140-harmonic-coordination.md) §0: a PyBoy PC hook on **every**
`LDH (n),A` site in the ROM image whose operand is `NR13`/`NR14`, `NR23`/`NR24` or `NR33`/`NR34`,
recording register `A` at the write — after `arp_tick`'s cache playback and after the vibrato ±1.
0 of 10,800 captured periods were unresolvable against the engine's own note-table generator.

Where a claim is about *what the engine resolved* rather than *what sounded* (the articulation
shapes, the cache contents), this run hand-derives the expected bytes in Python from
`ARP_PATTERN_PICK` → `ARP_PATTERNS` → `CHORD_TABLE` → the note table and compares **byte for
byte** — a stronger instrument than any statistic, and immune to the pitch-class aliasing that
tripped this run's own first statistical pass (§6, `N1`).

---

## 1. Definition of Done audit

| # | DoD item | Evidence | Result |
|---|---|---|---|
| 1 | Every `FS-115` acceptance criterion A1-A10 satisfied | Re-derived from the tree (§3) and independently driven (§2); `T23`'s 13 checks all pass | ✅ |
| 2 | `T23` exists and passes, **including (e)** — the `BL-0130` vibrato/portamento assertion | `test_rom.py:1856` `t23_chord_aware_arpeggio`; **13/13 `T23` checks PASS**. `T23.5` is a real assertion, not a comment: it collects sustained (non-arpeggiating) frames and asserts vibrato phases are observed on them. **Independently re-confirmed at the register level** — see §2 item 3 | ✅ |
| 3 | `T19`'s new frame class passes | `T19.7` (double-onset frame — both pulse channels resolving a fresh figure inside one `engine_tick`, the package's own most expensive class) and `T19.8` (idle frames ≤ 152, the class that actually measures `NFR-1280`) both PASS. Independently re-measured: §2 item 4 | ✅ |
| 4 | `T11` re-authored against the new contract and **genuinely re-derived** | `test_rom.py:541` — `T11.1` now asserts the *step index* cycles and says so explicitly ("says nothing about whether the pitch moves; that is `T23`'s job under `IP-1150`'s gated/varied contract"). That is a **narrowing** of scope to what the check can honestly prove, with the stronger claim moved to a suite that actually tests it — the opposite of loosening | ✅ |
| 5 | Full suite green; ROM exactly 32768 bytes, valid header (G5) | `python3 build_rom.py` → **32768 bytes**; `python3 test_rom.py` → **187 PASS, 0 FAIL out of 187** (T1-T23) | ✅ |
| 6 | `visuals.py`/`input_map.py`/`gbc_lib.py`/`build_rom.py`/`patterns.py`/`tiles.py`/`wram_constants.py` untouched, diff-confirmed | `git diff --stat 3e635ed 850e64e -- '*.py'` → **exactly three files**: `music_data.py` (+63), `music_engine.py` (+293/-…), `test_rom.py` (+430). Every named file is absent from the diff | ✅ |
| 7 | `engine_tick`'s call list **and call order** unchanged, confirmed by reading it | Read `build_engine_asm`'s tick body in the tree: the per-channel loop still emits `CALL arp_tick_{suffix}` **before** `_emit_channel_gen`'s `gen_tick`, and the routine keeps its `arp_tick_{suffix}` label and call site. **This is load-bearing** — that ordering *is* portamento — and it is intact | ✅ |
| 8 | **`NFR-1280` demonstrated, not assumed**: `arp_tick`'s common-path cost strictly lower, and the number recorded | **Independently re-counted from the assembler's own label table** on both builds: `arp_tick_pa` **156 bytes → 110 bytes**, `arp_tick_pb` **156 → 110**. A **29.5 % reduction in the routine that runs unconditionally, twice, every frame.** Corroborated behaviourally: `VIS_ENTRY_LY` on idle frames **152/153 → 151/152** (`VR-1140` §4 and §2 item 4 below) — a full scanline, ~456 cycles, returned every frame | ✅ |
| 9 | `VIS_ENTRY_LY` within `144`-`153` on every `T19` frame class including the new one — a regression is blocking | Independently measured over 3000 frames on this run's own drive: **`{151, 152}`**, and on the 20 observed frames where pulse A and pulse B onset together, **`{151}`**. Risk R2 (the onset frame becoming the new bottleneck because the two pulse channels are phase-locked) **did not materialize** — the double-onset frame is not merely inside budget, it is at the *cheaper* end of the observed range | ✅ |
| 10 | The sounding-pitch before/after `NFR-1270` measurement is **captured and reported, whatever it says** | Present in the package and on the Master Build Plan. Independently re-measured this run at the PSG-write boundary (see §4) | ✅ |
| 11 | `FR-1140`/`FR-1150` are **not claimed** in traceability — preserved and tested | `grep`: neither ID appears in `IP-1150`'s Requirements Covered except in the explicit negative ("must NOT be claimed — they must be *preserved*"), and neither appears against `IP-1150` on the Master Build Plan. Both are **independently proven still alive** in §2 item 3 | ✅ |

---

## 2. Verification Checklist audit — every item independently driven

| # | Checklist item | What this run did | Result |
|---|---|---|---|
| 1 | Rebuild + re-run the full suite | Done. 32768 bytes; 187 PASS / 0 FAIL | ✅ |
| 2 | **Re-derive at least one note's full articulation by hand** from the drawn pattern row and `CHORD_TABLE`, rather than trusting `T23`(a) — **and** confirm at a non-default `SCALE_IDX` *and* `OCTAVE_IDX` that arpeggiated pitches follow the scale | Reconstructed each pulse-B note's **whole four-step figure** in Python: read the channel's own post-onset LFSR, drew the row through `ARP_PATTERN_PICK`, expanded it through `ARP_PATTERNS`, resolved `SUSTAIN` → the note's own degree and each slot → `CHORD_TABLE[scale*12 + chord*3 + slot]`, converted every degree to its `(lo, hi)` note-table pair, and compared **byte for byte** against `ARP_CACHE_PB`. Run at **five (scale, octave) combinations**: `(major,1)`, `(pentatonic,1)`, `(minor,3)`, `(dorian,2)`, `(minor,0)` — covering **all four scale blocks and the octave-0 floor**. **400/400 articulations matched exactly, at every combination.** A transcription error in any one of the four per-scale `CHORD_TABLE` blocks, or in any octave's note table, cannot survive this. Worked example (note 1, boot defaults): `chord 0, deg 2, lfsr 0x4D → row 2 = [3,2,3,0]` → hand-derived `[(114,6),(178,6),(114,6),(11,6)]` = engine cache | ✅ |
| 3 | **Independently confirm that vibrato and portamento survive on a sustained note** — the `BL-0130` check, "the one most likely to have been satisfied by a comment rather than an assertion" | Proven **at the register-write boundary**, not from `ARP_STATE`. (a) **Vibrato:** identified every pulse-A note whose resolved cache is all-identical (i.e. the all-sustain row — this note does not arpeggiate), then checked whether the *captured `NR13`/`NR14` values* still changed frame to frame across that note. **64 of 64 sustained notes showed a varying sounding period.** The per-frame write demonstrably still executes, with this note's own pitch, exactly as `FR-1600` requires. (b) **Portamento:** on every degree-changing pulse-A onset, checked whether the boundary pitch on the onset frame is still the **outgoing** degree's pitch. **79/79.** The retrigger fires at the old pitch and `arp_tick` carries the glide — intact. **`BL-0130`'s High risk is independently disproven, on the register the APU reads** | ✅ |
| 4 | Re-measure `VIS_ENTRY_LY` on this run's own drive, **including an onset frame where pulse A and pulse B fire together** | 3000-frame drive: overall `{151, 152}`; **20 double-onset frames observed, all at `LY` 151** | ✅ |
| 5 | **Independently re-count `arp_tick`'s emitted instructions before/after** | Built both trees in-process and read the assembler's own `rom.labels`. `arp_tick_pa`: `0x04EC..0x0588` = **156 bytes** before; `0x0663..0x06D1` = **110 bytes** after. Identical for `pb`. The new `arp_resolve_{pa,pb}` labels (and 16 unrolled per-step labels) appear in the *onset* path, not the per-frame one — which is precisely the design claim | ✅ |
| 6 | **Independently re-run the strong-beat-partitioned interval measurement on sounding pitch** rather than accepting the implementing session's number | Done at the PSG-write boundary on both builds. See §4 | ✅ |

---

## 3. Tree audit — claimed changes confirmed by reading the code

| Claim | Location | Result |
|---|---|---|
| `ARPEGGIO_OFFSETS` replaced by a pattern table + LFSR-indexed selector | `music_data.py:180` `ARP_PATTERNS` (4 rows × 4), `:196` `ARP_PATTERN_PICK = [1,2,3,0]`, `:167` `ARP_SUSTAIN = 3` | ✅ |
| `FR-1610`'s two **structural** constraints are enforced in code, not merely described | `music_data.py:187-191` — three `assert`s: row 0 is all-sustain; **every** row starts on `ARP_SUSTAIN`; entries bounded by `ARP_SUSTAIN`. The rows sound a non-onset pitch on **0, 3, 2 and 1** of four steps — genuinely different rhythmic surfaces, not four permutations of one sweep | ✅ |
| The gate is a **forced row index**, never a skipped write | `music_engine.py:955-980` — a weak melody onset or a STUCK frame `XOR_A` (row 0) and still `CALL arp_resolve`. There is no branch that bypasses the per-frame write | ✅ (this is what makes item 3 above true) |
| Row drawn from the channel's **own** LFSR, no new randomness source | `music_engine.py:965-974` — the same `SRL`/`XOR LFSR_POLY` idiom, stored back | ✅ |
| `arp_resolve` resolves to **frequency pairs** (Task 5's primary shape, not Plan B) | `music_engine.py:1113-1195` — resolves the `(SCALE_IDX, OCTAVE_IDX)` → `ptr_table` address **once** for all four steps, then stores `(lo, hi&7)` pairs. `arp_tick` is index-and-write | ✅ |
| `arp_tick`'s `ARPEGGIO_OFFSETS` lookup, `CUR_DEGREE`+offset arithmetic, `AND 0x07` mask **and** `ptr_table` resolution all deleted | `grep`: no `arpeggio_offsets_table` label or emission anywhere in the tree; `ARPEGGIO_OFFSETS` survives **only in explanatory comments** | ✅ (see `F1`) |
| `ARP_DEGREE_SCRATCH` retained, correctly | `music_engine.py:63`, still used at `:590`/`:1029` for the portamento stash — Task 6 said grep before removing, and it is genuinely still needed | ✅ |
| `init_engine` populates both caches on **both** boot and Select (`FR-1630`) | `music_engine.py:1680` — `CALL arp_resolve_{suffix}` on the shared init path | ✅ |
| WRAM `ARP_CACHE_PA`=`0xC07A`, `ARP_CACHE_PB`=`0xC082`, scratch `0xC08A`-`0xC08C` | `music_engine.py`; `GDS-07` §3 rows and next-free updated; `Claude.md` quick-reference updated | ✅ |

**Scope audit.** Exactly `music_data.py`, `music_engine.py`, `test_rom.py`. The stage-08
code/content peer-seam crossing (`G1`) was **declared in advance** in Risk 5 with the same
justification `IP-1140` used and `music_data.py`'s edit is confined to the arpeggio tables.
**No excursion.**

---

## 4. Independent re-measurement at the output boundary

`3e635ed` → `850e64e`, boot defaults, 3600 frames, 120 pulse-A onsets, note-window attribution:

| | strong-beat | weak-beat | aggregate | bad-zone / 120 onsets | `VIS_ENTRY_LY` |
|---|---|---|---|---|---|
| `3e635ed` (`IP-1140`) | 22.4 % | 25.1 % | 23.7 % | 15 | 152-153 |
| `850e64e` (this package) | **9.4 %** | 29.9 % | **19.6 %** | **7** | **151-152** |

Complaint-directed measures, this run's own drive over 3600 frames / 474 notes across both pulse
channels:

| Measure | Package's recorded figure | This run | Verdict |
|---|---|---|---|
| distinct articulation shapes | 21 | **38** (pa 23, pb 33) | ✅ confirmed and exceeded |
| notes that do not arpeggiate at all | 47.1 % | **37.8 %** | ✅ confirmed in substance (see `F2`) |
| bad-zone activity | 15/121 → 7/121 | 15/120 → **7/120** | ✅ reproduces exactly |
| `VIS_ENTRY_LY`, idle frames | 152/153 → 151/152 | 152-153 → **151-152** | ✅ reproduces exactly |
| strong-beat harsh intervals | 25.7 % → 10.9 % | 22.4 % → **9.4 %** | ✅ confirmed (window differs, conclusion identical) |

**On the project owner's actual complaint — "constant repeated arpeggios" — the evidence is
unambiguous.** The pre-`IP-1150` design could only ever emit one compiled-in figure (plus its
`AND 0x07` wrap variants) and *every* note arpeggiated. This build emits **38 distinct shapes**
and **37.8 % of notes do not arpeggiate at all**. Independently corroborated by
`09-content-review`'s own finding on the same build (pulse-A pitch held for only ever 2, 4 or 6
frames before; 2-60 frames after, mean 5.0 → 13.7).

**The weak-beat regression is real, understood and correct.** 25.1 % → 29.9 % is the direct,
intended consequence of `FR-1600`: the melody's weak-onset passing tone is now *exposed for the
whole note* instead of being decorated away by an arpeggio that had no business being there. A
package that improved the strong beat by 13 points while worsening the weak beat by 5 is doing
exactly what `NFR-1270`'s partition exists to make visible — and an undifferentiated aggregate
would have reported it as a modest 4-point win, hiding both halves.

---

## 5. Requirements audit

| Requirement | Implemented at | Tested by | RTM cell | Result |
|---|---|---|---|---|
| `FR-1130` (as amended) — arpeggio spells the **shared** chord | `_emit_arp_resolve` slot path; `ARP_PATTERNS` | `T23.1`/`T23.2`/`T23.2b`; **400/400 hand-derived**, §2 item 2 | annotated "Implemented by `IP-1150`" | ✅ |
| `FR-1600` — only a chord tone arpeggiates; sustaining still writes | forced row 0 at `music_engine.py:955-979` | `T23.3`/`T23.4`, non-regression half `T23.5`; **64/64 + 79/79 independently**, §2 item 3 | annotated | ✅ |
| `FR-1610` — figure drawn per onset, alternatives differ in rhythmic surface | `ARP_PATTERNS`/`ARP_PATTERN_PICK` + the three `assert`s | `T23.6`/`T23.7`/`T23.8`/`T23.9`; **38 shapes / 37.8 % sustained** | annotated | ✅ |
| `FR-1620` — scale/octave change lands at the next onset | onset-resolved cache | `T23.10`/`T23.11` | annotated | ✅ |
| `FR-1630` — boot **and** Select re-establish arpeggio state | `init_engine` `CALL arp_resolve_{pa,pb}` | `T23.12`; `T23.1` proves the cache holds real note-table pitches | annotated | ✅ |
| `NFR-1280` — unconditional per-frame cost **strictly lower** | the whole design | `T19.8`; **156 → 110 bytes independently re-counted**, §2 item 5 | annotated | ✅ |
| `NFR-1260` (satisfied, not implemented) | — | `T19.7`; **151 on double-onset frames independently** | — | ✅ |
| `NFR-1270` (satisfied, not implemented, sounding-pitch basis) | — | **§4 is that measurement** | — | ✅ |
| `FR-1140`/`FR-1150` — **not claimed; preserved** | `arp_tick`'s vibrato block + unconditional final `LDH` writes, untouched | **64/64 vibrato, 79/79 portamento at the register boundary** | correctly unclaimed | ✅ |

---

## 6. Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| **F1** | **A stale comment still lists `ARPEGGIO_OFFSETS` as a live `music_data.py` table.** `music_engine.py:294` reads "`IP-8030` (`BL-0089`): `CHMIX_MASKS`, `STYLE_TABLE`, `SONG_TABLE`, `N_SONG_PHASES`, `ARPEGGIO_OFFSETS`, …" — an inventory of what moved to `music_data.py`, one entry of which no longer exists anywhere. The three `music_data.py` mentions are deliberate, well-written explanations of what changed and why (and should stay); this one is an index that has gone wrong. Trivially fixable, but exactly the sort of thing that sends a future reader looking for a table that was deleted. Also folds in a second stale line: the `2026-08-21` Delta Review in `01-functional-requirements.md` (line 748) still says "Forward traceability (`FS`/`IP`/`T`) is `UNASSIGNED` for `FR-1600`-`FR-1630`", which `IP-1150` has since filled in on every one of those rows. | Low (doc-accuracy) | `08-code-implementation` (the code comment) / `04-requirements-engineering` (the Delta Review line — folds into `BL-0135`) |
| **F2** | **"Notes that do not arpeggiate at all" is reported without saying which channel it counts, and the two channels differ materially.** The package records **47.1 %**; this run measures **37.8 %** across both pulse channels together. The gap is not a discrepancy in the engine — it is that pulse A carries `FR-1600`'s weak-onset forced hold *in addition to* the 1-in-4 all-sustain draw, while pulse B only ever gets the draw, so pulse A sustains far more often than pulse B. Both figures are true of something; neither states what. Any figure of this shape should name its channel scope, the same discipline `NFR-1270` now imposes on the measurement *basis*. | Low-Medium (measurement reporting; same family as `BL-0128`/`BL-0138`) | `04-requirements-engineering` (fold into `NFR-1270`'s reporting discipline alongside `BL-0138`) |
| **F3** | **Pentatonic's arpeggio behaves measurably differently from the other three scales, and nothing in the tree says whether that is intended.** This run's first (statistical) pass at non-default scales reported moving-arpeggio chord-tone rates of 97.1 % for major/minor/dorian but **81.3 % for pentatonic**. The hand-derivation then proved the *resolution path is exactly correct at pentatonic too* (80/80 byte-identical), so this is **not** a defect — it is a property of the data: pentatonic's `CHORD_TABLE` rows are hand-authored "idiomatic sonorities" rather than triads (stacked thirds yield no triads in a 5-note scale, as `music_data.py` explains), and its `SCALE_SEMITONES` row spans 16 semitones rather than 12, so its degrees alias across octaves differently. Worth recording because it means **pentatonic's arpeggio is a musically different object from the other three scales' and no listening pass has ever evaluated it as such**. | Low-Medium (design-question surfaced by verification; no functional defect) | `09-content-review` (listen to pentatonic specifically) |

### `N1` — a note on this run's own instrument, not a finding against the package

The statistical pass behind `F3` initially reported apparent off-chord "strays" at **every**
scale, including boot defaults, where `T23.2` asserts zero. Investigated to the end rather than
reported: the residue is **two artifacts of the verifier's own instrument**, not of the engine.
(1) Frames of `FR-1150`'s portamento glide legitimately sound the *outgoing* pitch, which is
usually not a tone of the incoming note's chord — the same trap `BL-0138` names. (2) Mapping a
captured period to a degree by nearest match *across all four octave tables* aliases in
pentatonic, whose row spans more than an octave. The hand-derivation (§2 item 2) is immune to
both, which is why it, and not the statistic, is this report's evidence. Recorded here so the
next verifier does not rediscover it.

---

## 7. Result

**`IP-1150` → `VERIFIED`.**

Every Definition-of-Done item and every Verification-Checklist item has recorded evidence. The
permanent gates are green (32768 bytes, valid header; 187/187). Scope is exactly as declared.

The two items this package's own author identified as most likely to be waved through were both
independently proven at the register boundary rather than accepted:

- **`BL-0130` (High risk — the gate silently deleting portamento and vibrato):** 64/64 sustained
  notes still show a varying sounding period, and 79/79 degree-changing onsets still retrigger at
  the outgoing pitch. The write never stops.
- **`NFR-1280` (cheaper, not merely within budget):** `arp_tick` re-counted from the assembler's
  own label table at **156 → 110 bytes**, a 29.5 % reduction in the only routine that runs
  unconditionally every frame, twice — corroborated by a full scanline of `VIS_ENTRY_LY`
  recovered on every idle frame. Risk R2 (the double-onset frame becoming the new bottleneck)
  did not materialize: those frames measure at `LY` 151, the *cheap* end of the range.

The articulation chain was hand-derived end to end — `ARP_PATTERN_PICK` → `ARP_PATTERNS` →
`CHORD_TABLE` → note table — **400/400 byte-identical across all four scales and the octave-0
floor**, which is a stronger result than the checklist asked for and closes the "a transcription
error in one of four blocks is invisible at the default" concern completely.

On the complaint that caused this package, the answer is measurable and it is yes: 3 shapes → 38,
0 % un-arpeggiated → 37.8 %. Whether it now *sounds* pleasant remains a human question, which is
`BL-0097`/`BL-0120`'s standing point and not something this report claims to answer.

With `IP-1140` verified earlier this run, **the whole `BL-0119` → `BL-0127` harmonic chain is now
`VERIFIED` end to end.**
