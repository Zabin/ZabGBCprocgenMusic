# VR-1110 — Verification Report: IP-1110 (Settings & Control Visibility)

## Package

- **Package:** [`IP-1110`](../packages/IP-1110-settings-and-control-visibility.md) — adds 5 new
  bar-height indicator tiles to the visualizer, one per base control (`TEMPO_IDX`, `OCTAVE_IDX`,
  `SCALE_IDX`, `DENSITY_IDX`, `CHMIX_IDX`), each showing that parameter's current index as a
  filled-bar glyph, updated every frame (`FS-111`/`ADS-104`, closes `BL-0051`'s base-control half).
- **Commit verified:** `b43f223` ("feat(visuals): IP-1110 -- settings & control visibility
  (BL-0051/ADS-104)") — tip of tree at verification time was `91ec1b8` (a journal-only entry
  recording `IP-1110` as `COMPLETE`, no functional changes on top).
- **Session independence:** genuinely fresh session, run in an isolated worktree. This session has
  no memory of authoring `IP-1110`; the implementing commit's own author/timestamp and the master
  build plan both attribute the work to a prior (main) session. No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. Both
disclosed findings (the reverted early-call-site regression, and the narrower Select-frame
display-lag) were independently reproduced exactly as described, not merely re-trusted. Three
findings recorded (all Low/doc-coherence or informational) — none blocks `VERIFIED`; see Findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| At boot, all 5 settings indicators already show the correct preset-value fill level | `build_visuals_init_asm` (`visuals.py:116-119`): pre-initializes `SETTINGS_CELLS` to `TILE_BAR_BASE + preset` for each of `SETTINGS_PRESETS = [4,1,0,0,0]`, before `update_visuals` ever runs. Shipped `T18.1` confirms (`cells=[6,3,2,2,2]` matches `expected`). This run's own `nondefault_scenario.py`/`select_frame_probe.py` boots independently confirm the same boot-time values `[6,3,2,2,2]` across 4 separate fresh-boot runs. | Pass |
| Each indicator updates to reflect its parameter's new value on the same frame a manual D-pad/A/B/Start press changes it | `_emit_update_settings_row` (`visuals.py:174-184`): reads each of `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` directly and writes `TILE_BAR_BASE + value` to the corresponding `SETTINGS_CELLS` entry, called every frame from `update_visuals` (`visuals.py:169`). Shipped `T18.2`-`T18.6` confirm one tap each. This run's own `nondefault_scenario.py` independently drove **10 consecutive** D-pad Up taps (full `TEMPO_IDX` wrap 4→5→6→7→0→1→...→6) and **6 consecutive** Start taps (`CHMIX_IDX` 0→1→2→3→4→5→6) — every single intermediate value, including the 7→0 wraparound, was correctly reflected on the same frame, not just the suite's own single-tap fixture. | Pass |
| The existing channel-activity tiles and calm/bad-zone palette swap are unaffected by this package's own writes | `_emit_update_settings_row` only ever writes `SETTINGS_CELLS` (read-only source registers, one `LD_nn_A` per control) — confirmed by reading the routine end to end (`visuals.py:174-184`): no reference to `CHANNEL_CELLS`, `TILE_OFF`/`TILE_ON`, or `_emit_write_palette` anywhere in it. Shipped `T18.7` confirms `CHANNEL_CELLS` still tracks `NR52` correctly with the settings row present. **This run's own independent stress test** (`stress_channel_cells.py`, not reusing any `test_rom.py` fixture): a clean fresh boot, **zero button input**, 3000 frames, comparing `CHANNEL_CELLS` against `NR52` every single frame — **0 mismatches out of 3000** — directly re-deriving that the regression the implementing session found and reverted (early call-site position) is genuinely absent from the shipped, reverted (last-position) code, not just absent from whichever single fixture `T9`/`T18` happen to run. | Pass |
| Select resets the underlying WRAM fields on the exact reset frame, and the settings-indicator display catches up within one further frame (disclosed exception) | `visuals.py:154-169`'s own comment plus `build_rom.py:80-83`'s call order (`apply_input` → `engine_tick` → `update_visuals`, all from one `HALT`-gated main-loop iteration) explain the mechanism: `init_engine`'s full reset (triggered by `apply_input` on a Select edge) costs enough extra CPU that this frame's `update_visuals` call silently drops its VRAM writes; the next frame's unconditional re-run repairs it. Shipped `T18.8`-`T18.10` confirm this exact shape from one pre-Select button sequence. **This run's own independent frame-by-frame probe** (`select_frame_probe.py`) reproduced the full sequence from **three distinct pre-Select button sequences** (not reusing `T18`'s own sequence), reading WRAM (`0xC000`-`0xC004`) and `SETTINGS_CELLS` (`0x9804`-`0x9808`) frame-by-frame: in all three, (a) WRAM reset to the exact preset values on the Select frame itself, (b) `SETTINGS_CELLS` was provably stale on that same frame (still showing the pre-Select drifted values), (c) `SETTINGS_CELLS` matched the restored preset exactly one frame later, and stayed correct a further frame after that. Reproduced reliably 3/3. | Pass |
| Every pre-existing test still passes | Full suite run this session: **122/122** (`T1`-`T18` all green — see Test run below). | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. `T1` (part of the 122/122 run) confirms header fields. | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 122/122, run this session, command `python3 test_rom.py`. | Pass |
| `09-package-verification` independently drives a non-default scenario live and confirms the DoD holds beyond whatever single fixture the new suite happens to use | Standalone script `nondefault_scenario.py` (not `test_rom.py`'s own fixtures): 6 consecutive Start taps stepping `CHMIX_IDX` through presets 1-6 in a row (T18 only checks one Start tap), and 10 consecutive D-pad Up taps exercising `TEMPO_IDX`'s full wraparound (7→0) — every intermediate value's indicator matched exactly. Plus the two disclosed-finding reproductions above, each independently re-derived rather than re-run. | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1350` (5 indicators, one per base control, bar-height glyph) | `_bar_tile_bytes(n)` (`visuals.py:70-78`, 8 fill-level glyphs), `SETTINGS_CELLS`/`SETTINGS_SOURCES` (`visuals.py:29-44`) | `T18.1`-`T18.6`; this run's boot/tap re-derivations | Pass |
| `FR-1360` (same-frame update) | `_emit_update_settings_row` called every frame from `update_visuals` (`visuals.py:169`) | `T18.2`-`T18.6`; this run's `select_frame_probe.py`/`nondefault_scenario.py` (all reads taken immediately post-tap, same frame) | Pass |
| `FR-1370` (purely additive) | `_emit_update_settings_row`'s full body (`visuals.py:174-184`) touches only `SETTINGS_CELLS`, confirmed by direct read | `T18.7`; this run's independent 3000-frame zero-input `CHANNEL_CELLS`/`NR52` stress test (0 mismatches) | Pass |
| `FR-1380` (at least one indicator live-reflects a manual change) | Same mechanism as `FR-1360`, any of the 5 controls | `T18.2`-`T18.6`; this run's own repeated-tap sequences for `TEMPO_IDX`/`CHMIX_IDX` | Pass |
| `NFR-1140` (ROM/VRAM budget) | 8 new tile patterns (128 bytes) + `_emit_update_settings_row`/init-time writes | This run independently re-measured via `rom.pos`-instrumentation (`ADR-0002`'s own method, script `measure_rom.py`): **4240 of 32768 bytes used, 28528 free** — a delta of exactly **-449 bytes** from `VR-1100`'s own measured 28977 free, matching the package's/Master Build Plan's own claimed "+449 bytes (28528 free)" figure exactly. | Pass |
| `NFR-1150` (VBlank-gated, comparable per-frame cost) | `build_rom.py:74-83`: main loop `HALT`s until the VBlank ISR sets `VBLANK_FLAG`, then runs `read_joypad`→`apply_input`→`engine_tick`→`update_visuals` once — `update_visuals` (and this package's addition inside it) only ever runs within that VBlank-gated window, the same as every pre-existing visualizer write. | Confirmed by direct code read of `build_rom.py`'s main loop | Pass |
| `NFR-1160` (no new input control) | `git show b43f223 --stat` confirms `input_map.py` is entirely untouched by this commit. | Confirmed by direct diff read | Pass |

No RTM file at FR-grain currently exists in this tree (same standing gap `VR-9010`-`VR-1100`
already noted — `docs/requirements/01-functional-requirements.md` is the traceability source of
record at FR grain). Traceability above is derived directly from that document's FR text
(confirmed present: `FR-1350`-`FR-1380`, `NFR-1140`-`NFR-1160`, added in the 2026-07-26 delta
review) against the shipped code and tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes; header valid (`T1` confirms all header
  fields; this run additionally independently re-measured `rom.pos` = 4240, free = 28528 bytes,
  matching the package's/Master Build Plan's own claimed ROM-budget figure exactly, and the
  claimed +449-byte delta from `VR-1100`'s own 28977-free baseline).
- `python3 test_rom.py` → **122 PASS, 0 FAIL** out of 122 (full suite, `T1`-`T18`).
- Independent non-default/adversarial live drive (three standalone scripts, not reusing any
  `test_rom.py` fixture, built to directly re-derive the two disclosed findings and exercise a
  non-default scenario per the standing convention):
  - **`stress_channel_cells.py`** (regression re-derivation, addresses the task's explicit ask):
    a clean fresh boot, zero button input, 3000 frames, sampling `CHANNEL_CELLS` against `NR52`
    every single frame. **0 mismatches out of 3000** — independently confirms the reverted
    early-call-site regression (channel-activity writes intermittently dropping on ordinary,
    no-input frames) is genuinely absent from the shipped, last-position code, not merely absent
    from whichever fixture `T9`/`T18` happen to run.
  - **`select_frame_probe.py`** (Select-frame timing re-derivation, addresses the task's explicit
    ask): three distinct pre-Select button sequences (`up,right,a,b,start`;
    `up,up,up,left,start,start`; `down,down,b,b,b,a`), each drifting the 5 base controls away from
    boot preset differently, then a Select press read frame-by-frame. All three sequences
    independently confirmed: (a) WRAM (`0xC000`-`0xC004`) resets to the exact preset values on the
    Select frame itself; (b) `SETTINGS_CELLS` (`0x9804`-`0x9808`) is provably stale on that exact
    frame (still showing pre-Select values); (c) `SETTINGS_CELLS` matches the restored preset
    exactly one frame later; confirmed reliable across all three distinct sequences, not a
    one-off.
  - **`nondefault_scenario.py`** (non-default-scenario drive, standing `VR-1070`/`VR-1080`/
    `VR-1090`/`VR-1100` convention): 6 consecutive Start taps (`CHMIX_IDX` stepped 0→1→2→3→4→5→6,
    every intermediate value's indicator correct) and 10 consecutive D-pad Up taps
    (`TEMPO_IDX` stepped through its full 0-7 range including the 7→0 wraparound, every
    intermediate value's indicator correct) — `T18` itself only ever taps each button once from
    boot; this scenario goes beyond that single-fixture coverage.
  - No hang, no crash; all three scripts completed cleanly. Scripts left at
    `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/`
    (`stress_channel_cells.py`, `select_frame_probe.py`, `nondefault_scenario.py`,
    `measure_rom.py`).

## Scope audit

Package declared `visuals.py` only for production code. Actual diff (`git show b43f223 --stat`):
`Claude.md`, `Driftune.gbc`, `ROADMAP.md`, `docs/architecture/07-data-model.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1110-settings-and-control-visibility.md`, `memory.md`,
`test_results.txt`, `test_rom.py`, `visuals.py`.

`visuals.py` is the only production-code file touched — confirmed no excursion into
`input_map.py`, `music_engine.py`, `gbc_lib.py`, or `build_rom.py`. `test_rom.py` gained the new
`T18` suite only (78 lines added, no modification to any pre-existing check). The package's own
doc (`IP-1110-...md`) was self-updated during implementation to record the two disclosed findings
(the reverted early-call-site regression and the narrower Select-frame display-lag) in its
Objective/Files-to-Modify/Tests-to-Add/Definition-of-Done/Risks fields — the same
disclose-in-place pattern this project's prior packages (e.g. `IP-1100`) have used, not an
undeclared excursion. All other touched files are documentation/ledger bookkeeping the package's
own `Documentation Updates` field named (`Claude.md`, `memory.md`, GDS-07/
`docs/architecture/07-data-model.md`) plus accurate status-row updates (`ROADMAP.md`, the Master
Build Plan, `packages/INDEX.md`, `test_results.txt`), and the committed ROM binary was refreshed
alongside the source (`Driftune.gbc | Bin 32768 -> 32768 bytes`).

One documentation-update item the package's own `Documentation Updates` field named was **not**
actually completed by the implementing commit: `docs/pipeline/backlog.md` was not touched at all
(absent from the `--stat` diff), so `BL-0051`'s own backlog row was not marked as having its
base-control half closed by this package — see Finding 1.

One additional doc-coherence gap found during this scope audit, outside the implementing commit
itself: `docs/features/INDEX.md`'s `FEAT-1110`/`FS-111` row still reads "not yet built," and
`docs/feature-planning/01-feature-catalog.md`'s bucket header (lines 16-17) still reads "`FEAT-1110`
... is not yet built" — both stale now that `IP-1110` is `COMPLETE` (122/122) and, as of this
report, `VERIFIED`. Per this project's established precedent (`VR-1090`/`VR-1100`'s own Scope
audits), a one-line, unambiguous status-string correction with no judgment call involved is
corrected in place as part of this VR's ledger updates rather than left as a pure finding.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| `IP-1110`'s own `Documentation Updates` field named `docs/pipeline/backlog.md` ("`BL-0051` closes its base-control half on this package's completion — mark accordingly at that time") as a required update. The implementing commit's diff does not touch `docs/pipeline/backlog.md` at all — `BL-0051`'s row still reads `IN PIPELINE` with no mention that its base-control half is now closed. Not a functional defect; a disclosed documentation commitment that was not fulfilled. | Low (doc-coherence only, no functional impact; the underlying feature is correctly built and tested) | `00-pipeline-manager` (update `BL-0051`'s row to note the base-control half closed on `IP-1110` reaching `VERIFIED`, consistent with how other multi-part `BL-xxxx` entries in this backlog are annotated) |
| `docs/features/INDEX.md`'s `FEAT-1110`/`FS-111` row and `docs/feature-planning/01-feature-catalog.md`'s bucket header both still read "not yet built" against the actual shipped/now-`VERIFIED` state — the same stale-row pattern `VR-1090`'s Finding 3 and `VR-1100`'s Finding 3 already caught for their own packages. Corrected as part of this VR's ledger updates (see Scope audit) rather than left purely as a finding, since it is this package's own direct feature row. | Low (doc-coherence, corrected in-place) | N/A — fixed by this VR |
| The shipped `T18.8`-`T18.10` Select-frame-lag sequence exercises only one pre-Select button combination (one tap of each control). This run's own `select_frame_probe.py` independently confirmed the same lag/self-heal shape holds across two additional, distinct pre-Select sequences, so the underlying mechanism is confirmed boundary-agnostic — but the shipped suite itself does not directly demonstrate this from more than one sequence. | Low (test-coverage gap, not a functional defect — the underlying `update_visuals`/`apply_input` timing interaction is a single code path, not sequence-dependent, and this run's independent drive confirms it holds across sequences) | `08-code-implementation` (optionally extend `T18.8`-`T18.10` to iterate over a second distinct pre-Select sequence, same rigor upgrade `VR-1100`'s own Finding 1 recommended for `T17.6`) |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1110` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1110` row status updated to `VERIFIED`.
- `ROADMAP.md`: stage-08/09 rows updated — `IP-1110` now `VERIFIED` via this report.
- `docs/features/INDEX.md`: `FEAT-1110`/`FS-111` row updated from "not yet built" to reflect
  `IP-1110` `VERIFIED`.
- `docs/feature-planning/01-feature-catalog.md`: bucket header's `FEAT-1110` clause updated from
  "not yet built" to reflect `VERIFIED` status (mirroring the existing `FEAT-1100` clause's own
  phrasing).
- This VR added to `docs/implementation/verification/INDEX.md`.

---

## Correction notice — 2026-07-31 (`BL-0069`/`BL-0073`)

**This report's independent reproduction of the "Select-frame dropped write" finding was itself
wrong, and the report is retained unaltered above as the record of what the verification run
concluded.** No finding in it is withdrawn as to `IP-1110`'s *behaviour* — the package's DoD was
correctly verified and `IP-1110` remains `VERIFIED`. What is withdrawn is the **mechanism** the
report attributed the observed one-frame display lag to.

**What was actually happening.** `pb.tick(1)` advances exactly one ROM frame but returns at a
point *inside* that frame's work — after `apply_input` has updated the WRAM indices and before
`update_visuals` has re-rendered `SETTINGS_CELLS` from them. A frame-by-frame probe that reads
WRAM and the derived tilemap cells after the same `tick()` is therefore comparing **two different
moments of the ROM's frame**, and will report a one-frame lag whether or not anything is wrong.
It does so uniformly — on plain index steps exactly as much as on Select, and on idle frames with
no input at all. Full evidence: `R308` §8.5, `R101` §8.5, and `IP-9030`'s Blocking Report.

**Why this matters beyond a correction.** This report did the right thing procedurally: it
declined to reuse `T18`'s own button sequence, built its own probe (`select_frame_probe.py`), and
reproduced the shape 3/3 across three distinct pre-Select sequences. That independence was real
and is exactly what the convention asks for. **It nevertheless confirmed a false finding, because
independence of *session and fixture* is not independence of *method* — the probe repeated the
same sampling error the original experiment made.** `BL-0073` carries the open question of whether
`09-package-verification`'s conventions should require method-independence when confirming a
*finding*, as opposed to verifying a package's Definition of Done. `R305` §3 now carries the
`tick()` sampling hazard as a standing test-design rule so the specific error is caught next time.

**Rows affected:** the "Select resets the underlying WRAM fields... (disclosed exception)" row's
*explanation* column. Its Pass verdict stands — the behaviour it verified (WRAM resets on the
Select frame; the display agrees within one further frame) is real and correctly observed. Only
the causal account is withdrawn.
