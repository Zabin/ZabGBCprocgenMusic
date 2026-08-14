# VR-9030 — VBlank Budget Assertion

## Package

`IP-9030` (v2) — VBlank Budget Assertion (re-scoped from *VRAM Write-Integrity Detection*),
`IP-9xx0` bug-remediation series, no owning FS. Commit verified: `808a9a2` on
`claude/controls-explanation-28fpbh` (tree tip at verification time). Fresh session — no prior
work on this package in this session; independence unimpaired.

## Result

**`VERIFIED`** — every Definition of Done item and Verification Checklist item holds under
independent re-derivation; the full `test_rom.py` suite is green (154/154) and the ROM builds
correctly. No new findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `VIS_ENTRY_LY` written every frame | `visuals.py:139` — `LDH_A_n(LY & 0xFF); LD_nn_A(VIS_ENTRY_LY)`, the first two instructions of `build_visuals_update_asm` | Pass |
| `T19` exists and passes, asserting 144-153 across all five frame classes | `test_rom.py:1126-1230` (`T19.1`-`T19.6`); live run below | Pass |
| Measured values recorded in Implementation Summary and `T19`'s own comments | `test_rom.py:1129-1132`, `Claude.md:330` | Pass |
| `T17.6` covers all three phase-transition boundaries | `test_rom.py:970-1015` — loops `transition_frames[:3]`, one iteration per boundary | Pass |
| `T18.8`-`T18.10` cover ≥2 pre-Select sequences | `test_rom.py:1083-1086` — `pre_select_sequences` has 2 distinct sequences, looped | Pass |
| Both falsified-wording locations corrected (`T18.10` name, `visuals.py` comment block) | `test_rom.py:1119-1121` (no drop claim, names the self-healing render-vs-reset lag); `visuals.py:150-165` (corrected comment, explicitly states no write is ever dropped, cites `BL-0069`/`R308` §8.5) | Pass |
| `IP-1080`'s DoD reworded to mechanism-level claim | `docs/implementation/packages/IP-1080-genre-aware-style-presets.md:14` — reworded text present, matches `FS-108`'s acceptance criterion (4) phrasing | Pass |
| `Claude.md`/`IP-1110`'s doc read correctly, not re-edited by this package | Confirmed both already carry the corrected account (pre-existing from the 2026-07-31 documentation review) | Pass |
| Full suite passes; ROM builds to 32768 bytes, valid header | See Test run below | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Independently rebuilt this run: 32768 bytes, valid header | Pass |
| Full `test_rom.py` suite passes including `T19` (G5) | `154 PASS, 0 FAIL out of 154` | Pass |
| Independently re-derive the `VIS_ENTRY_LY` measurement from a fixture of the verifier's own construction | Standalone script (own `fresh_boot`, 100 boot frames matching `test_rom.py`'s own `BOOT_FRAMES`, no import of `test_rom.py` logic): read `VIS_ENTRY_LY` across a **50-frame idle stretch** (T19.1 only samples 5) — min/max **152/153**, matching the package's own measured range exactly; also drove **A and Down presses** (T19.2 only exercises Up/B) — both read **153**. All within 144-153, no exceptions across 52 independent samples. | **Pass** |
| Confirm no `T19` check can pass vacuously — deliberately perturb the ROM and confirm `T19` actually fails | Built a throwaway copy of the tree with 400 `NOP` instructions injected at the top of `update_visuals` (before the `VIS_ENTRY_LY` store), pushing the probe well past its normal position. Rebuilt (32768 bytes) and independently drove it: `VIS_ENTRY_LY` read **2** on every idle frame sampled (20/20), far outside 144-153 — `T19` would fail decisively against this build. Confirms the checks are genuinely falsifiable, not tautological. | **Pass** |
| Confirm the package's own diagnostic did not itself consume the head-room it measures (compare against the pre-package baseline of `LY` 152-153) | The Blocking Report's own Measurement 1 (taken before this package existed) recorded `LY` 152-153 at the equivalent point (entry to `update_visuals`, pre-instrumentation). This run's independent re-measurement (above) also reads 152-153 — no drift. Consistent with the probe's placement as the routine's very first two instructions, which by construction measures state *before* its own 7-cycle cost is incurred. | Pass |
| Read `R305` §5's can/cannot table; confirm no `T19` check claims a property from its lower half | Read `R301` §3 and `R305` §5 in full. `T19`'s own docstring (`test_rom.py:1126-1135`) explicitly disclaims asserting VRAM-write acceptance/discard; grepped `T19`'s six checks — all assert only `VIS_ENTRY_LY`'s numeric range, never a VRAM-write-observability claim. Compliant. | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `NFR-1010` (per-frame timing budget) | `visuals.py:139`, `VIS_ENTRY_LY` diagnostic | `T19.1`-`T19.6` | `01-functional-requirements.md:67` — already states "Implemented 2026-07-31... `IP-9030`'s `VIS_ENTRY_LY`... now supply exactly this check," correct and unchanged | Pass |
| `NFR-1020` (headless test asserting real state) | `T19` itself is an instance of this NFR | `T19.1`-`T19.6` | Traces correctly | Pass |
| `FR-1350`-`FR-1380` (settings-indicator behaviors, widened test coverage via `BL-0052`/`BL-0057`) | `test_rom.py`'s `T17.6`/`T18.8`-`T18.10` widened per Implementation Tasks 4-5 | `T17.6` (3 boundaries), `T18.8`-`T18.10` (2 sequences) | Traces correctly, no cell changed (these FRs' own implementation is unchanged by this package — only their test coverage widened) | Pass |

## Test run

- `python3 build_rom.py <path>` → `32768 bytes`. Header independently re-parsed: valid.
- `python3 test_rom.py` → **`154 PASS, 0 FAIL out of 154`** (`T1`-`T21`).
- Own 50-frame idle + A/Down-press independent re-measurement of `VIS_ENTRY_LY`: min/max 152/153,
  matching the shipped suite's own measured range.
- Own perturbation build (400 `NOP` injected before the probe): `VIS_ENTRY_LY` reads 2 on every
  sampled frame — confirms `T19` is genuinely falsifiable.

## Scope audit

`git show --stat 808a9a2`'s ancestry for this package's own commits (`26dd167` and earlier `IP-9030`
work) touches `visuals.py`, `test_rom.py`, `Claude.md`, `memory.md`,
`docs/architecture/07-data-model.md`, `docs/implementation/packages/IP-1080-genre-aware-style-presets.md`,
plus the Master Build Plan / `packages/INDEX.md` — matching the package's declared file set
exactly. `music_engine.py`, `input_map.py`, `gbc_lib.py`, `build_rom.py` untouched. No excursion
found.

## Findings

None.

## Ledger updates

- Master Build Plan `IP-9030` row: `COMPLETE` → **`VERIFIED`**, this VR linked.
- `docs/implementation/packages/INDEX.md` `IP-9030` row: updated to `VERIFIED`.
- `docs/implementation/verification/INDEX.md`: new row added (✅ `VERIFIED`).
- No code, package, spec, or requirement text was edited by this run.
