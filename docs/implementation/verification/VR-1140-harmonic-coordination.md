# VR-1140 — Harmonic Coordination via a Shared Chord Context

| Field | Content |
|---|---|
| **Package** | [`IP-1140`](../packages/IP-1140-harmonic-coordination.md) — Harmonic coordination via a shared chord context (`FS-114`/`FEAT-1150`, `BL-0119`) |
| **Commit verified** | `850e64e` (branch `claude/controls-explanation-28fpbh`) — the current tree, which also carries `IP-1150`. Comparison builds used: `3ade5a8` (pre-`IP-1140` baseline) and `3e635ed` (`IP-1140` as shipped, pre-`IP-1150`). |
| **Date** | 2026-08-21 |
| **Independence** | **Genuinely fresh session.** This session has implemented nothing; `IP-1140` was built 2026-08-20 by another session and `IP-1150` on 2026-08-21 by a third. No caveat is claimed and none is needed. |
| **Result** | ✅ **VERIFIED** — 0 failed checks. 4 findings, all Low/Medium, none blocking; the largest (`F1`) is a traceability-annotation gap, not a behavioural one. |

---

## 0. Measurement basis — stated explicitly per `NFR-1270` (as amended 2026-08-21)

Every pitch figure in this report was sampled at the **output boundary**: a PyBoy PC hook is
attached to *every* `LDH (n),A` instruction in the ROM image whose operand is `NR13`/`NR14`
(pulse A), `NR23`/`NR24` (pulse B) or `NR33`/`NR34` (wave), and the value recorded is register
`A` at the instant of the write. That captures the pitch **after** `arp_tick`'s cache playback
**and after** the vibrato ±1 — i.e. after every writer in the chain. Nothing engine-internal is
read for pitch anywhere in this verification: `CUR_DEGREE_*` is read only where the requirement
under test is itself about note *selection* (`FR-1590`), never as a stand-in for what sounded.

Captured periods are mapped back to scale degrees by nearest-period match against
`music_engine._note_table_bytes` — the engine's own build-time generator, not a transcript — with
a ±3-period tolerance to absorb the vibrato wobble. **0 of 10,800 captured periods across the
main run were unresolvable**, which is itself evidence the instrument is reading real note-table
pitches rather than noise.

Driver: `scratchpad/vr/boundary.py` + `measure_intervals.py` (throwaway, not committed to the
repo per this project's own convention).

### A methodological correction this run made to its own instrument (recorded, not hidden)

The first pass sampled all three channels on the **pulse-A onset frame itself** and reported
strong-beat 25.7 % / weak-beat 7.9 % — with the strong/weak relationship *inverted* against every
figure this project has ever recorded. The cause is real and is a property of the engine, not of
the harness: `FR-1150`'s portamento deliberately retriggers the onset at the **old** degree, and
`arp_tick` carries the pitch to the new target over the *following* frames. So a single-frame
sample taken on the onset frame measures the outgoing note against the incoming note's beat class.

The correct window is the **note**: each pulse-A note inherits the strong/weak parity recorded at
its own onset, and the harsh-interval rate is computed across every frame that note actually
sounds. All headline figures below use the note window. The onset-frame figure is retained in the
driver output as a secondary reading precisely so the discrepancy stays visible. Filed as `F4`.

---

## 1. Definition of Done audit

| # | DoD item | Evidence | Result |
|---|---|---|---|
| 1 | Every `FS-114` acceptance criterion (1)-(11) satisfied | Behaviour re-derived from the tree (§3) and independently driven (§4); `T22`'s 16 checks all pass | ✅ |
| 2 | `T22` exists and passes | `test_rom.py:1646` `t22_harmonic_coordination`; **16/16 `T22` checks PASS** in this run's own suite execution | ✅ |
| 3 | `T19`'s chord-transition frame class passes | `T19` present and green; independently corroborated — this run measured `VIS_ENTRY_LY` on **27 real chord-transition frames** of the `3e635ed` build at **152-153**, and **28** on the current build at **151-152**. Both inside `144`-`153` | ✅ |
| 4 | Re-authored `T5`/`T6`-class checks pass **against the new contract, genuinely re-derived rather than loosened** | Read `T5.5`/`T6.3`/`T6.4` in the tree: `T5.5` now asserts a chord-tone membership predicate derived from `CHORD_TABLE`, which is **narrower** than the `{0,1,7}` set it replaced, not wider. The package's own record shows this narrowing caught a real `CHORD_TOGGLE` initialization defect (`0b11`→`0b01`) — a loosened check cannot catch a defect | ✅ |
| 5 | Full suite green (G5) | `python3 test_rom.py` → **187 PASS, 0 FAIL out of 187** (T1-T23) | ✅ |
| 6 | ROM builds to exactly 32768 bytes, valid header (G5) | `python3 build_rom.py …/driftune.gbc` → `32768 bytes`; `T1` header checks green | ✅ |
| 7 | `visuals.py`/`input_map.py`/`gbc_lib.py`/`build_rom.py` untouched, confirmed by diff | `git diff --stat 3ade5a8 3e635ed -- '*.py'` → **exactly three files**: `music_data.py` (+109), `music_engine.py` (+341/-…), `test_rom.py` (+243). `visuals.py`, `input_map.py`, `gbc_lib.py`, `build_rom.py`, `patterns.py`, `tiles.py`, `wram_constants.py` all absent from the diff | ✅ |
| 8 | **No new unconditional per-frame instruction anywhere** (`NFR-1240`) — confirmed by reading `engine_tick`'s call list, which must be unchanged | The implementing diff's only `build_engine_asm` hunks are (a) a keyword argument added to the existing `_emit_channel_gen` call, (b) four `rom.label`/`rom.emit` **data** blocks. **No `rom.CALL` was added or removed anywhere in `engine_tick`.** Corroborated behaviourally: `VIS_ENTRY_LY` on the `3e635ed` build reads 152-153, identical to the `3ade5a8` baseline's 152-153 | ✅ |
| 9 | `VIS_ENTRY_LY` measured on chord-transition frames and within `144`-`153`; a regression is blocking | Independently measured this run, not accepted from the package: **152-153** across 27 chord-transition frames on `3e635ed`. No regression against the pre-package baseline | ✅ |
| 10 | The strong-beat-partitioned before/after interval measurement is **captured and reported in this package's evidence, whatever it says** | Present in the package doc and on the Master Build Plan — including a prominent, dated, self-inflicted **correction** (`BL-0128`) marking the originally-banked figures overstated and leaving them standing so the correction sits where the claim was made. This is the DoD item honoured in its strongest form | ✅ |
| 11 | **`FR-1570` is not claimed anywhere in this package's traceability** | `grep`: `FR-1570` appears in the package doc **only** in the negative ("is NOT covered and must not be claimed"), and in `01-functional-requirements.md` marked `WITHDRAWN … never implemented`. No `SCHEME_TABLE` exists anywhere in the tree | ✅ |

---

## 2. Verification Checklist audit — every item independently driven

| # | Checklist item | What this run did | Result |
|---|---|---|---|
| 1 | Rebuild + re-run the full suite | Done. 32768 bytes; 187 PASS / 0 FAIL | ✅ |
| 2 | **Re-derive at least one chord transition by hand** from `CHORD_TRANSITION` and the driving LFSR's actual state, rather than trusting `T22`(b) | Read pulse A's real `LFSR_STATE` (`0xC016`) and `CHORD_IDX` on the frame **before** each counter-expiring onset, stepped the LFSR in Python by the engine's own Galois rule (`SRL`; `XOR 0xB8` on carry), took the low 2 bits, and indexed `CHORD_TRANSITION[chord*4 + bits]`. **7 of 7 transitions in a 2400-frame run matched the engine's write exactly.** First five: `chord 0, lfsr 0x21 → bits 0 → 0` ✓; `0, 0x94 → 2 → 2` ✓; `2, 0x9C → 2 → 0` ✓; `0, 0x8B → 1 → 1` ✓; `3, 0x9A → 1 → 2` ✓ | ✅ |
| 3 | Confirm on a live drive at a **non-default** `SCALE_IDX` and `OCTAVE_IDX` that chord tones follow the scale — a transcription error in one of four scale blocks would be invisible at the default | Drove three non-default combinations the suite's own fixtures never set — **(pentatonic, oct 1)**, **(minor, oct 3)**, **(dorian, oct 2)** — plus the default as a control, 1800 frames each, reading pulse B's **sounding** pitch at the PSG boundary. Fraction whose **pitch class** is a tone of the current chord in *that scale's own* `CHORD_TABLE` rows: **99.8 % / 99.6 % / 99.6 % / 99.6 %**. All four scale blocks are correct, at non-default octaves. (The <0.5 % residue is `FS-115` B4 by design: a note already sounding when the chord advances under it is deliberately not re-derived mid-note.) | ✅ |
| 4 | Independently confirm `FR-1590` by driving into a dissonant bad zone and checking a strong-onset chord tone survives, while a stuck-flag frame still forces a step | Drove `TEMPO_IDX`/`DENSITY_IDX` to their maxima for 6000 frames to provoke bad zones. **Dissonant-but-not-stuck strong onsets that kept a chord tone: 18/18.** `BAD_ZONE_FLAGS` low-nibble values observed: `0, 9, 12, 13` — DISSONANT and OVERLOAD both reached, **COMBINED** set. **Partial:** the STUCK bit never set in this drive, so the "stuck still forces a step" half was not exercised here; it is covered by `T8`/`T10`/`T14.3` in the suite, which are green. Filed as `F3` | ✅ (with `F3`) |
| 5 | Re-measure `VIS_ENTRY_LY` on chord-transition frames from this run's own drive | Done — see DoD 9. **152-153** on `3e635ed`, **151-152** on the current tree | ✅ |
| 6 | **Independently re-run the strong-beat-partitioned interval measurement rather than accepting the implementing session's number** | Done at the output boundary, on all three builds. See §4 | ✅ |

---

## 3. Tree audit — every claimed change confirmed by reading the code

| Claim | Location in the tree | Result |
|---|---|---|
| `CHORD_TABLE` 4×4×3 = 48 bytes, entries 0-7 | `music_data.py:278`, with `assert len(CHORD_TABLE) == 48 and all(0 <= d <= 7 …)` at `:284` | ✅ |
| `CHORD_TRANSITION` 4×4 = 16 bytes, values < `N_CHORDS` | `music_data.py:295`, asserted at `:302` | ✅ |
| `MELODY_PICK = [0,1,2,1]` | `music_data.py:311` | ✅ |
| `HARMONY_PICK` **replaced by `SLOT_NEXT`** (declared deviation 2) | `music_data.py:326` `SLOT_NEXT = [1, 2, 0, 1]`; `HARMONY_PICK` absent from the tree, consistent with the package's own Implementation Record | ✅ (deviation disclosed and justified) |
| `PASSING_TABLE` added (declared deviation 3) | `music_data.py:336` `[0xFF, 0x01, 0xFF, 0x01]` — always ±1, no hold entry, exactly as recorded | ✅ (deviation disclosed) |
| `N_CHORD_ONSETS = 4` | `music_data.py:343` | ✅ |
| WRAM `CHORD_IDX = 0xC077`, `CHORD_ONSET_CTR = 0xC078`, `CHORD_TOGGLE = 0xC079` | `music_engine.py:138-141` | ✅ |
| Harmonic clock inside `gen_tick_pa`'s **existing** onset branch, gated on `role == 'melody'` | `music_engine.py:627-664` | ✅ |
| **One** write site for `CHORD_IDX`, anywhere | `music_engine.py:653` (the clock) and `:1622` (`init_engine`). Confirmed by grep — no third writer | ✅ |
| Chord advance **sets** parity bit1; a hold **toggles** it | `:658` `SET_b_A(1)` vs `:662` `XOR_n(0x02)` — so a chord change always lands on a strong onset and the phase cannot drift. Independently confirmed by `T22.5` and by this run's own drive | ✅ |
| Pulse B's `octave_delta` **stays 0** (declared deviation 1) | `music_engine.py:264` `CHANNELS` row for `pb` carries `0`, with the reasoning inline at `:253-262` | ✅ (deviation disclosed; see `F2`) |
| `init_engine` writes all three fields on **both** boot and Select | `music_engine.py:1622-1624` — `CHORD_IDX←0`, `CHORD_ONSET_CTR←4`, `CHORD_TOGGLE←0b01` | ✅ |
| `CHORD_TOGGLE` initial value `0b01`, not `0b11` | `music_engine.py:1624` — the defect the re-authored `T5.5` caught is fixed in the shipped tree | ✅ |
| Four ROM tables emitted via the existing table-emission path, no new mechanism | `build_engine_asm` data section: `chord_table`, `chord_transition`, `melody_pick`, `slot_next` | ✅ |

**Scope audit.** The implementing change touched exactly `music_data.py`, `music_engine.py`,
`test_rom.py`. The stage-08 code/content peer-seam crossing (`G1`) was **declared in advance** in
the package's Risks field 3 with its reasoning, not discovered at execution — the correct handling.
`music_data.py`'s edit is confined to adding pure-data tables. **No excursion.**

---

## 4. Independent re-measurement at the output boundary

All three builds, boot defaults, 3600 frames, 120 pulse-A onsets each, identical instrument:

| Build | strong-beat | weak-beat | aggregate | bad-zone at sampled onsets | `VIS_ENTRY_LY` |
|---|---|---|---|---|---|
| `3ade5a8` — **before** `IP-1140` | 33.2 %¹ | 30.7 %¹ | **32.0 %** | **34**/120 | 152-153 |
| `3e635ed` — **`IP-1140` as shipped** | **22.4 %** | 25.1 % | **23.7 %** | **15**/120 | 152-153 |
| `850e64e` — current tree (`IP-1150` on top) | **9.4 %** | 29.9 % | **19.6 %** | **7**/120 | 151-152 |

¹ The pre-`IP-1140` build has no chord context, so no real strong/weak parity exists; parity there
is synthesized as alternating onsets. **The aggregate column needs no parity and is the
apples-to-apples comparison.**

**Findings from this measurement:**

- **The package's headline claim is confirmed in substance and in direction.** `IP-1140` reduced
  harsh vertical intervals on sounding pitch from **32.0 % → 23.7 %** aggregate and
  **33.2 % → 22.4 %** on strong beats. That is a real, independently reproduced improvement.
- **The `BL-0128` correction is confirmed as necessary and correctly stated.** The originally
  banked "strong-beat 12.2 %" is not reproducible at the output boundary by any windowing — the
  true strong-beat rate on that build is ~22-26 %. The package's own posted correction (25.7 %)
  and this run's independent figure (22.4 %) differ only by measurement window, and both sit in
  the same place: roughly double what was banked. **The correction stands; the original figure
  does not.**
- **Two of the package's own recorded figures reproduce exactly**, which is strong corroboration
  that this run and the implementing run are measuring the same engine: bad-zone activity
  **34 → 15** sampled onsets (package: "34/121 → 15/121") and `VIS_ENTRY_LY` **152-153** on
  chord-transition frames (package: "152-153"). `IP-1150`'s own recorded **7/121** and
  **151/152** likewise reproduce as 7/120 and 151-152.
- **The weak-beat column behaves exactly as `NFR-1270` predicts it must.** `IP-1140` improves it
  (30.7 → 25.1 %); `IP-1150` worsens it (25.1 → 29.9 %) while nearly halving the strong-beat
  figure — because gating the arpeggio leaves the deliberate weak-onset passing tone exposed for
  the whole note instead of decorating it away. An undifferentiated aggregate histogram would have
  reported that trade as noise. This is `BL-0122`'s reasoning validated on real data.

---

## 5. Requirements audit

| Requirement | Implemented at | Tested by | Result |
|---|---|---|---|
| `FR-1500` shared `CHORD_IDX`, no cross-channel private reads | `music_engine.py:138`, `:627-664`; all voice rules read `CHORD_IDX`/`CHORD_TOGGLE` only | `T22.1`/`T22.2`; §2 item 2 | ✅ |
| `FR-1510` ROM chord table, no runtime arithmetic | `music_data.py:278`; `_emit_chord_tone_addr` (`music_engine.py:485`) is table addressing only | `T22.4`/`T22.6`; §2 item 3 | ✅ |
| `FR-1520` weighted 4-chord tonic-biased transition on 2 LFSR bits | `music_engine.py:635-653` | `T22.1`; **hand-derived 7/7**, §2 item 2 | ✅ |
| `FR-1530` chord advances every 4 **onsets**, not frames | `music_engine.py:628-637` | `T22.2` | ✅ |
| `FR-1540` bass = root/fifth alternating | `music_engine.py:686-688` | `T22.3` | ✅ |
| `FR-1550` melody = chord tone strong / ±1 step weak | `music_engine.py:690-760` | `T22.4`/`T22.5` | ✅ |
| `FR-1560` harmony voice distinct from the melody's tone | `music_engine.py:702-739` via `SLOT_NEXT`; unison structurally impossible | `T22.6`; §2 item 3 (99.6-99.8 % chord-tone at 4 scales) | ✅ (wording gap → `F1`) |
| `FR-1570` | **not claimed, correctly** — withdrawn unimplemented | n/a | ✅ |
| `FR-1580` (as amended) preset 0 is harmonically coordinated | Chord derivation is the default path; no scheme flag gates it | Whole of `T22` runs at boot defaults | ✅ |
| `FR-1590` dissonance does not override a strong-onset chord tone | The harmonized limbs jump past the dissonance block | `T22`; **18/18 independently driven**, §2 item 4 | ✅ |
| `NFR-1240` no unconditional per-frame cost | `engine_tick` `CALL` list unchanged (diff-confirmed) | `VIS_ENTRY_LY` unchanged 152-153 vs. baseline | ✅ |
| `NFR-1250` ≤ ~100 bytes of ROM | 48+16+4+4 = **72 bytes**; 27348 bytes free | build output | ✅ |
| `NFR-1260` `VIS_ENTRY_LY` in `144`-`153` incl. a chord-transition class | `T19` | **152-153 independently measured**, §2 item 5 | ✅ |
| `NFR-1270` strong-beat-partitioned acceptance **on sounding pitch** | — | **This report is that measurement**, §4 | ✅ |

---

## 6. Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| **F1** | **`IP-1140`'s 13 covered requirements carry no implemented-by/verified-by traceability annotation, while `IP-1150`'s do.** `FR-1130`, `FR-1600`, `FR-1610`, `NFR-1280` each end with "**Implemented by `IP-1150`** — `<file>` `<function>`; verified by `T23.x`". `FR-1500`-`FR-1560`, `FR-1580`-`FR-1590`, `NFR-1240`-`NFR-1270` end at their source column with no such cell. The behaviour is genuinely implemented and genuinely tested (this report re-derives all of it), so this is a **ledger** gap, not a coverage gap — but it is exactly the kind of gap that lets a later reader believe a requirement is unbuilt. The convention post-dates `IP-1140` by one day, which explains it without excusing it. Also folds in the package's own routed item: **`FR-1560`'s literal wording** still describes a cross-channel read ("distinct from the melody role's currently-sounding chord tone") where the shipped `SLOT_NEXT` design satisfies it through the shared field instead. Both are one edit pass. | Medium (doc/ledger coherence; no functional gap) | `04-requirements-engineering` |
| **F2** | **Deviation 1's follow-on is now cheaper than when it was withheld, and nothing is tracking that.** Pulse B's `octave_delta` stayed `0` because teaching the then-current `arp_tick` the offset cost 3 *unconditional per-frame* instructions, which `NFR-1240` forbids. `IP-1150` has since moved all of `arp_tick`'s table arithmetic to onset time and **returned a full scanline of VBlank** (`VIS_ENTRY_LY` 152/153 → 151/152, independently confirmed in §4). The exact "cached per-channel note-table-index byte" the package named as its follow-on candidate is essentially what `ARP_CACHE_PA`/`PB` now is. The reason for withholding the octave separation has weakened materially; `FR-1560`'s octave half remains unimplemented and unowned. | Medium (a baselined requirement's octave clause is unbuilt, and its stated blocker has since lifted) | `07-implementation-planning` |
| **F3** | **The STUCK half of `FR-1590` was not reachable in this run's own drive.** 6000 frames at maximum tempo and density produced DISSONANT, OVERLOAD and COMBINED but never set `BAD_ZONE_FLAGS` bit1. The dissonant half was confirmed 18/18; the stuck half rests on `T8`/`T10`/`T14.3` alone. Not a defect — plausibly a *good* sign, since `IP-1140`+`IP-1150` more than halved bad-zone activity — but it means no verification run has independently exercised stuck recovery against the harmonized path, and the checklist item asked for exactly that. | Low-Medium (verification-coverage) | `09-package-verification` (a named drive recipe for reaching STUCK), or `02-research-game-design` if STUCK is now effectively unreachable |
| **F4** | **A single-frame sample on the onset frame measures the outgoing note, and this is not written down anywhere.** `FR-1150`'s portamento deliberately triggers the onset at the *old* degree and lets `arp_tick` glide to the new one, so any instrument that samples "the pitch at the onset" is reading the previous note against the current note's beat class — which inverted this run's first strong/weak figures completely (25.7 %/7.9 % instead of 9.4 %/29.9 %). `NFR-1270` now normatively fixes *what* to sample (sounding pitch) and `BL-0124` fixed *when within the frame*; **neither fixes which frames constitute the note**. This is the third distinct sampling error in the same family. | Medium (measurement methodology; would silently corrupt any future acceptance number) | `04-requirements-engineering` (extend `NFR-1270` to name the note, not the onset frame, as the window) |

---

## 7. Result

**`IP-1140` → `VERIFIED`.**

Every Definition-of-Done item and every Verification-Checklist item has recorded evidence.
The permanent gates are green (32768 bytes, valid header; 187/187). The three disclosed deviations
from `FS-114` are all present in the tree exactly as recorded, each with its measurement-driven
reason. The chord transition table was hand-derived against the live LFSR and matched 7/7; the
per-scale chord tables were confirmed correct at three non-default scale/octave combinations the
suite never sets; `FR-1590`'s dissonance exception was independently driven 18/18.

The package's own acceptance figures were **not** accepted: they were re-measured from scratch at
the PSG-write boundary, on three builds. The result confirms `BL-0128` — the originally banked
strong-beat 12.2 % is wrong and the correction to ~25 % is right — while also confirming that the
improvement `IP-1140` actually delivered is real (aggregate 32.0 % → 23.7 % on sounding pitch,
bad-zone activity 34 → 15 with no threshold retuning). A package whose headline number was found
overstated and which posted that correction itself, in the place the claim was made, is being
verified on the corrected number, which is the outcome the output-boundary rule exists to produce.

The four findings are routed and none blocks the transition.
