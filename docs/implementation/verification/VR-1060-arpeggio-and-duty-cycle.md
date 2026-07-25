# VR-1060 — Verification Report: IP-1060 (Arpeggio + Duty-Cycle Variation)

## Package

- **Package:** [`IP-1060`](../packages/IP-1060-arpeggio-and-duty-cycle.md) — Arpeggio + duty-cycle
  variation
- **Commit verified:** `268458e` (tip of `music_engine.py` at verification time; `IP-1060`'s own
  code landed in `e967ff4`, subsequently touched only by `IP-1061`'s additive extension of the
  same `ARP_STATE_PA`/`PB` bytes)
- **Session independence:** genuinely fresh session — this session did not author `IP-1060`
  (built and self-tested in a prior session per journal run #22). No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. One
Low-Medium doc-coherence finding recorded (does not block `VERIFIED`, see Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Arpeggio audibly/measurably cycles frequency within a note's duration on pulse A | `_emit_arpeggio_tick` (`music_engine.py:397-458`) rewrites `NR13`/`NR14` every `ARP_SUBTICK_RELOAD`=6 frames with the trigger bit clear (no retrigger). `test_rom.py` T11.1: distinct arpeggio step values `[0,1,2,3]` seen over a sustained run at the **default** preset. Independently re-driven at a non-default preset (see Verification Checklist row below) — also cycles through all 4 steps. | Pass |
| Duty-cycle varies across onsets on pulse A | `DUTY_BY_DEGREE[CUR_DEGREE mod 4]` written to `NR11` in the onset block. T11.2: distinct duty values `[0x0, 0x40, 0x80, 0xC0]` seen at default preset; also confirmed at non-default preset (below). | Pass |
| Select-reset zeroes all new state | `init_engine` (`music_engine.py`) zeroes `ARP_STATE_PA`/`PB` on both boot and Select paths — confirmed by T11.3 (arpeggio step reads 0 on the exact reset frame). | Pass |
| Every pre-existing test still passes | Full suite run this session: **65/65** (T1-T11, all green — see Test run below). | Pass |
| ROM builds to 32768 bytes with valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`; T1.1-T1.5 all pass (size, title, GBC flag, cart type, header checksum). | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including T11 (G5) | 65/65, run this session, exact command `python3 test_rom.py`. | Pass |
| Independent non-default scale/octave drive confirms arpeggio/duty-cycle off the default preset | Drove the built ROM live via a standalone PyBoy script (not the suite's own fixtures): pressed `right` x2 (`OCTAVE_IDX`: 1→3) and `a` x2 (`SCALE_IDX`: 0→2), landing on **OCTAVE_IDX=3, SCALE_IDX=2** — a realistic non-default combination, neither extreme nor the shipped preset (`PRESET_OCTAVE_IDX=1`, `PRESET_SCALE_IDX=0`). Over the following 400 frames: arpeggio step bits (`ARP_STATE_PA & 0x30`) took all 4 values `[0x00,0x10,0x20,0x30]`; `NR11` duty bits took all 4 values `[0x0,0x40,0x80,0xc0]`. Confirms the DoD holds off the default preset, not just at it — satisfies this project's standing tunable-parameter verification standard (same discipline as `VR-0002`-`VR-0004`, `VR-0007`). | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1130` (arpeggio) | `music_engine.py` `_emit_arpeggio_tick`, `ARPEGGIO_OFFSETS=[0,2,4,2]` (3 distinct scale-degree offsets — root/+2/+4 — satisfying "among 2 or 3 notes") | T11.1 + this run's non-default live drive | Pass |
| `FR-1160` (duty-cycle variation) | `DUTY_BY_DEGREE` write in onset block | T11.2 + live drive | Pass |
| `NFR-1040` (ROM/WRAM budget) | 2 new ROM tables (`ARPEGGIO_OFFSETS` 4B, `DUTY_BY_DEGREE` 4B) + 3 new WRAM bytes (`ARP_STATE_PA`/`PB`/`ARP_DEGREE_SCRATCH`) — ROM still exactly 32768 bytes, single bank, no bank-switching change | T1.1 (ROM size) | Pass |
| `NFR-1050` (per-frame timing budget) | Sub-tick block runs every frame unconditionally, decrement + conditional branch only | 8200-frame stress run this session, no hang, `NR52` still reporting correctly (`0xFF`) at the end | Pass |

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, header valid (T1 confirms).
- `python3 test_rom.py` → **65 PASS, 0 FAIL** out of 65 (full suite, T1-T11).
- Independent non-default live drive (standalone script, `OCTAVE_IDX=3`/`SCALE_IDX=2`): arpeggio +
  duty-cycle both confirmed varying, as above.
- 8200-frame stress run (fresh boot, no input): no hang, `NR52` remained valid throughout.

## Scope audit

Package declared `music_engine.py` only. `IP-1061` (built in a later same-push session, not this
one) additively extended the same `ARP_STATE_PA`/`PB` bytes into bits6-7 for vibrato — a
documented, in-scope extension of `IP-1060`'s own packing scheme, not an excursion by `IP-1060`
itself. No file outside `music_engine.py` was touched by `IP-1060`'s own diff (confirmed via
`git show e967ff4 --stat`). No excursion.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| The `IP-1060` package doc's own text (Files to Create/Modify, Implementation Tasks rows) still describes a **3-entry** `ARPEGGIO_OFFSETS` table (`e.g. [0, 2, 4]`) cycled **mod 3**. The shipped implementation instead uses a 4-entry period-4 up/down table (`[0, 2, 4, 2]`), with the step index packed into 2 bits (`mod 4`, `AND 0x30`) — a real, deliberate, and correctly-documented-*elsewhere* design choice (GDS-07 §3 and the pipeline journal run #22 both accurately describe the shipped 4-step design), but the package doc itself was never updated to match, so a reader consulting `IP-1060`'s own doc in isolation would expect a 3-step cycle. No functional defect — FR-1130's "2 or 3 notes" requirement is still satisfied (3 *distinct pitches*: root/+2/+4; the 4th step revisits `+2`). | Low-Medium (doc-coherence only, same pattern as `BL-0013`/`BL-0016`/`BL-0018` — implementation-outpaced-package-text) | 07-implementation-planning (fold into the package doc the next time it's touched) or 08-code-implementation's own doc-update step, whichever next has reason to open this package's file |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1060` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1060` row status updated to `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
