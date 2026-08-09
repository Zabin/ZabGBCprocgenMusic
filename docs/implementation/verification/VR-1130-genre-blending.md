# VR-1130 — Genre Blending

## Package

`IP-1130` — Genre Blending (roadmap R8, `FS-113`/`ADS-107`). Commit verified: `7c9ccb2` on
`claude/controls-explanation-28fpbh` ("IP-1130 (Genre Blending) COMPLETE — T21 suite, T15/T4.7/
T16.8 blend-contract updates"). Fresh session relative to the implementing session — no
independence caveat needed.

## Result

**`RETURNED`** — 1 hard-fail finding (Critical) against the package's own Verification Checklist,
plus 1 documentation-consistency finding (Low-Medium). The full `test_rom.py` suite is green
(153/153) and the ROM builds correctly, but green-suite status does not establish correctness
here: every shipped check (`T21`, updated `T15.1`-`T15.4`, `T4.7`, `T16.8`) reads blend state only
at the two endpoints (the press frame's immediate `SCALE_IDX`/`BLEND_SRC_*` capture, and the
settled state after `settle_blend()`'s margin absorbs several frames) — never at a genuine
mid-blend `BLEND_STEP`. The package's own Verification Checklist explicitly requires this
verification pass to hand-derive and check a genuine midpoint, independent of the implementation's
own code. Doing so surfaces a real, reproducible mismatch between the documented interpolation
formula and the actual shipped WRAM state for 2 of the blend's 3 fields.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `_emit_begin_blend`/`_emit_blend_tick` implement the contract exactly as `FS-113` specifies, including the mid-blend-restart edge case | `music_engine.py:404-425` (`_emit_begin_blend`), `:439-506` (`_emit_blend_tick`); mid-blend-restart independently re-confirmed (see Verification Checklist audit, item 2) | **FAIL** — restart mechanism itself is correct, but "exactly as specified" fails on intermediate-step exactness (see Findings F1) |
| `T21` exists and passes, with (a)-(e) exercised independently | `test_rom.py:1337-1447`; all 8 `T21.*` checks pass in the live run below | Pass (as literally written) — but (b)'s "full-blend landing" and (c)'s mid-blend probe both only ever read `BLEND_STEP∈{0,4}`-adjacent state, never a genuine unmasked midpoint; see F1 |
| `T15.1`-`T15.4` updated and passing against the new contract, not merely left unbroken by coincidence | `test_rom.py:692-725`; all use `settle_blend()` (a margin-2-frame settle helper) before reading | Pass as written; same masking caveat as above |
| Full suite passes (`T1`-`T21`) | `python3 test_rom.py` → `153 PASS, 0 FAIL out of 153` (this run, see Test run below) | Pass |
| `visuals.py` untouched — confirmed by diff | `git show --stat 7c9ccb2` shows no `visuals.py` entry | Pass |
| ROM builds to exactly 32768 bytes with a valid header | `python3 build_rom.py` → 32768 bytes; header logo/title/CGB-flag/checksum independently recomputed and matched (`0x72` stored = `0x72` computed) | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Rebuilt independently this run: 32768 bytes, header checksum verified by hand (`0x72`) | Pass |
| Full `test_rom.py` suite passes including `T21` and updated `T15` (G5) | `153 PASS, 0 FAIL out of 153` | Pass |
| Independently re-derive an interpolated midpoint value (`BLEND_STEP` other than 0/4) for a non-default style pair, hand-computed independently of reading the implementation's own code | Own PyBoy script (not importing `test_rom.py`), transition preset 1 (Techno, settled `tempo=6,density=6,duty=+1`) → preset 2 (Ambient, target `tempo=1,density=0,duty=-1`). Hand-derived at `BLEND_STEP=2` using the package's own documented formula (`src + ((target−src)×step)>>2`, multiply-before-divide, magnitude-negate-shift-renegate for negatives): `tempo=4, density=3, duty=0`. Shipped ROM read at the exact frame `BLEND_STEP` first equals 2: `tempo=4, density=3, duty=1`. **`duty` does not match.** A second, deeper frame-by-frame trace (both this pair and the `T21.3`-adjacent 0→1 pair, run twice each for determinism) shows: `TEMPO_IDX` (processed first in `_BLEND_FIELDS`) always matches the formula exactly, every frame; `DENSITY_IDX` (processed second) matches except on the blend's very first frame (`BLEND_STEP=1`), where it shows the unchanged pre-blend value instead of the formula's tiny first-step delta; `DUTY_BIAS` (processed third/last) is wrong on **every** intermediate frame — it consistently displays what should have been the *previous* step's value, and only reaches the true target one full frame *after* `BLEND_STEP` has already read 4. | **FAIL** |
| Independently re-confirm the mid-blend-restart forced-collision scenario (`T21`(c)) using a second, independently-constructed pre-Start-press sequence | Built a distinct sequence: settle to preset 2 first (not preset 0), first test press uses a 2-frame hold (not `T21`'s 1-frame tap), forces the collision at `BLEND_STEP=3` (not empirically re-derived per-run like `T21`, arrived at differently), restarts to preset 4 (the "default (unassigned)" row, not one of `T21`'s 0-3 range). Result: `BLEND_SRC_*` correctly re-captured the exact mid-blend values in effect at collision (`(2,2,0)`, matching by hand read), `SCALE_IDX` applied the second press's own target (`0`) immediately, `CHMIX_IDX` changed to a genuinely new preset. **Core `FR-1490` contract holds** under this independently-constructed sequence. (One script-level artifact noted, not a defect: this sequence's own extra `tick()` call after the restart press produced `BLEND_STEP=2` instead of `T21.7`'s `1` — a self-inflicted difference in tick cadence between this script and `T21`'s own, not a new finding.) | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `FR-1470` (blend begins, capture + immediate `SCALE_IDX`) | `_emit_begin_blend`, `music_engine.py:404-425` | `T21.1`/`T21.2` | Traces to `IP-1130` correctly (`01-functional-requirements.md:58`) | Pass |
| `FR-1480` (4-discrete-step interpolation, landing exactly on target) | `_emit_blend_tick`, `music_engine.py:439-506` | `T21.3`, `T15.1`-`T15.4` (endpoint only) | Traces correctly | **Landing-exactly claim holds at the endpoint** (confirmed independently — all 3 fields land exactly once fully settled); **the "4 discrete steps" claim does not hold as an observable per-step guarantee for `density_idx`/`duty_bias`** — see F1 |
| `FR-1490` (mid-blend restart uses current values, no queueing) | `_emit_begin_blend`'s unconditional capture | `T21.4`-`T21.7`, independently re-confirmed this run | Traces correctly | Pass |
| `NFR-1210` (negligible steady-state cost) | `_emit_blend_tick`'s `BLEND_STEP>=4` early-`RET` | Not independently cycle-counted this run (code-review only: 1 `CP`+1 conditional jump on the steady-state path, consistent with the claim) | Traces correctly | Pass (code-review basis) |
| `NFR-1220` (bounded WRAM, 4 new bytes) | `music_engine.py:109-112` | ROM budget independently re-measured this run: 4483 bytes used / 28285 free — matches the Master Build Plan's own claimed figure exactly | Traces correctly | Pass |
| `NFR-1230` (WRAM-value-assertion testable; audible quality deferred to `09-content-review`) | — | This VR's own F1 finding is exactly the WRAM-assertion testability this NFR promises — it is testable, and testing it (rather than trusting the endpoint-only suite) is what surfaced the defect | Traces correctly | **NFR text itself holds; the shipped test suite does not yet exercise it** (F1) |
| `FR-1240` (amended) | `SCALE_IDX` half unchanged, confirmed by `_emit_begin_blend`'s immediate write; `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` half correctly superseded in the requirements text | `T21.1`, `T15.*` | `01-functional-requirements.md:35` amendment note present and accurate | Pass |

## Test run

- `python3 build_rom.py /tmp/.../verify_ip1130.gbc` → `Wrote ...: 32768 bytes`. Header independently re-parsed: Nintendo logo present, title `DRIFTUNE`, CGB flag `0x80`, header checksum stored `0x72` = computed `0x72`.
- `python3 test_rom.py` → **`153 PASS, 0 FAIL out of 153`** (`T1`-`T21`, including the 8 `T21.*` checks and the updated `T15.1`-`T15.4`/`T4.7`/`T16.8`).
- ROM budget independently re-measured (trailing-zero-run method): 4483 bytes used, **28285 bytes free** — matches the Master Build Plan's claimed figure exactly.

## Scope audit

`git show --stat 7c9ccb2` confirms the diff touches `music_engine.py`, `input_map.py`,
`test_rom.py`, `Claude.md`, `docs/architecture/07-data-model.md`, `docs/requirements/
01-functional-requirements.md`, and `docs/implementation/00-master-build-plan.md` — matching the
package's declared file set. `visuals.py` is untouched, confirmed. No excursion found.

## N=4-vs-N=16 disclosure audit (task-directed check)

Confirmed the as-shipped `N=4` frames (not the package's originally-proposed `N=16`) is
consistently and accurately disclosed in three of the four required locations:

- **Master Build Plan** (`00-master-build-plan.md:282`): "As-shipped blend duration **N=4
  frames** ... not the package's originally-proposed N=16 — disclosed." Accurate.
- **`Claude.md`** (`:316-318`): "as-shipped: **N=4 frames** to land exactly ... originally-proposed
  N=16." Accurate.
- **`GDS-07`** (`docs/architecture/07-data-model.md:109`): "As-shipped blend duration is **N=4
  frames** ... not the package's originally-proposed N=16." Accurate.
- **Package doc Risks field** (`docs/implementation/packages/IP-1130-genre-blending.md:17`):
  **still reads "`N=16` frames is a first-guess placeholder"** with no amendment noting the
  as-shipped deviation to `N=4`. This is stale relative to the other three locations and to the
  code itself. Low-Medium finding (F2) — not blocking on its own, but the disclosure is not
  "consistent everywhere it's claimed" as the task required checking.

## T9.3 self-healing NR52/visuals race — independent re-confirmation

Drove a fresh, independently-constructed 1200-frame run (4x the shipped `T9.3`'s own 300-frame
window) comparing `CHANNEL_CELLS` against `NR52` bit-for-bit every frame. Result: 17 mismatched
frames out of 1200, **longest consecutive-mismatch run = 1** (never 2+ consecutive), mismatches
recurring at a roughly periodic ~64-frame interval consistent with the wave channel's own
disclosed DAC-retrigger cadence. **The disclosed characterization (single-frame, always
self-healing, never sustained) holds** under this independent, longer-window drive. No finding.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `_emit_blend_tick`'s per-step interpolated values do not match the package's own documented formula for 2 of the 3 blended fields. `TEMPO_IDX` (first field processed in `_BLEND_FIELDS`) is exact on every single intermediate frame. `DENSITY_IDX` (second field) is exact except on the blend's very first frame. `DUTY_BIAS` (third/last field) is wrong on every intermediate frame — it consistently shows the *previous* step's value and only reaches the true target one full frame after `BLEND_STEP` has already read 4. This is deterministic and reproduced identically across two independent script runs and two different style-pair transitions (preset 0→1 and preset 1→2). Because the lag correlates with a field's *position in the processing loop* rather than being uniform across all WRAM reads on a given frame (`BLEND_STEP` and `TEMPO_IDX`, read on the very same `tick()` call as the stale `DENSITY_IDX`/`DUTY_BIAS` values, are always current), this does not fit the "generic `pb.tick()` harness-sampling artifact, uniform across every frame class" pattern this project's own history requires before accepting that framing (see `IP-1110`'s Master Build Plan entry: an earlier "harness artifact, self-healing, not a dropped write" claim for `visuals.py`'s settings-row lag was later **withdrawn** as `BL-0069` after direct measurement proved the lag was genuinely harness-uniform — that falsification test is exactly what this run just failed to reproduce for IP-1130's blend fields). The implementing session's commit message and `settle_blend()`'s docstring characterize this identically ("the same self-healing one-frame harness-sampling artifact ... not a dropped write or a real engine defect") without having run the equivalent falsification check, and every consuming test (`T21`, `T15.1`-`T15.4`, `T4.7`, `T16.8`) reads state only via `settle_blend()`'s margin-2 settle or the exact press frame — never a genuine intermediate `BLEND_STEP`, so this defect is invisible to the entire shipped suite. This directly fails the package's own Verification Checklist requirement to independently hand-derive and match a genuine midpoint. | **Critical** | `08-code-implementation` (re-open `IP-1130`) — first determine whether this is a genuine `_emit_blend_tick` ordering/codegen bug (most likely, given the position-correlated, non-uniform pattern) or a true harness artifact (falsify per the `BL-0069` precedent's method before re-asserting that framing); either fix the routine or, if genuinely harness-only, add the falsification evidence and extend `T21`/the package's claims to explicitly disclose per-field intermediate-step behavior rather than only endpoint exactness. |
| F2 | The package doc's own Risks field (`docs/implementation/packages/IP-1130-genre-blending.md:17`) still states "`N=16` frames is a first-guess placeholder" with no note of the as-shipped `N=4` deviation, unlike the Master Build Plan, `Claude.md`, and `GDS-07`, all three of which disclose `N=4` accurately and explicitly contrast it with the originally-proposed `N=16`. | Low-Medium | `07-implementation-planning` (package docs are that stage's to amend; a returned package is the natural point to fold this in alongside F1's fix) |

## Ledger updates

- Master Build Plan `IP-1130` row: reverted to **`IN PROGRESS`**, pointing at this VR, pending F1's resolution.
- RTM: no cell corrected — all traced entries for `FR-1470`/`1480`/`1490`/`NFR-1210`/`1220`/`1230`/`FR-1240` point to real files and real checks; the defect is in the *checks' coverage depth*, not in traceability accuracy, so no RTM edit was warranted.
- No code, package, spec, or requirement text was edited by this run.
