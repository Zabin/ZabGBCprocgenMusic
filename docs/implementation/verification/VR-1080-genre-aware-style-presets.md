# VR-1080 — Verification Report: IP-1080 (Genre-Aware Style Presets, roadmap R5)

## Package

- **Package:** [`IP-1080`](../packages/IP-1080-genre-aware-style-presets.md) — Genre-aware style
  presets (`STYLE_TABLE` keyed by `CHMIX_IDX`, applied immediately on Start press)
- **Commit verified:** `20f5d2c` (IP-1080's own implementation commit; tip of tree at
  verification time was `65eb7a0`, the journal-only run #60 entry, no functional changes on top)
- **Session independence:** genuinely fresh session — this session did not author `IP-1080`
  (built and self-tested in an earlier session today per `docs/implementation/00-master-build-
  plan.md`'s own note and commit `20f5d2c`'s timestamp). No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. One
Medium and one Low finding recorded (neither blocks `VERIFIED`; see Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Selecting any of the 3 named-style `CHMIX_IDX` presets immediately (same frame) sets `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` to that style's documented values | `STYLE_TABLE` (`music_engine.py:240-249`): row 1 = `(6,6,2,0x01)` Techno, row 2 = `(1,0,3,0xFF)` Ambient/Lo-Fi, row 3 = `(3,3,0,0x01)` Holiday. `_emit_apply_style` (`:329-343`) reads `STYLE_TABLE[CHMIX_IDX]`'s 4 bytes and writes them into `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` in turn, called from `input_map.py:73` immediately after `CHMIX_IDX` is stepped (`input_map.py:66-73`), same frame, same call chain — no intervening logic (confirmed by reading `input_map.py:62-74` directly). `test_rom.py` T15.1-T15.3 confirm all 3 styles via `tap()` (a 2-frame-settled read). **This run independently re-verified all 3 styles on the literal exact press frame** (single tick, no settle, no release) at non-sequential preset order (3, 1, 2) — see Test run S1, below. | Pass |
| Preset 0 remains identical to the pre-`IP-1080` shipped default | `STYLE_TABLE[0] = (PRESET_TEMPO_IDX, PRESET_DENSITY_IDX, PRESET_SCALE_IDX, 0x00)` (`:241`) — matches `PRESET_TEMPO_IDX=4`/`PRESET_DENSITY_IDX=0`/`PRESET_SCALE_IDX=0` (`:142-146`) exactly. `init_engine` (`:980-989`) sets `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` to these same constants and separately zeroes `DUTY_BIAS`, so boot/Select-reset never even needs to call `_emit_apply_style` — the two code paths are independently constructed to agree, not merely coincidentally equal. T15.4 confirms cycling all 8 presets (wrap) lands back at the fresh-boot default combination. | Pass |
| A style change leaves all bad-zone WRAM state untouched | `_emit_apply_style` (`:329-343`) touches only `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` — confirmed by reading its full body, no write to `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/`STALE_COUNT_*`/`ONSET_WINDOW_COUNT` exists in the routine. T15.5 confirms this from a single from-boot-default scenario. **This run's broader randomized-stress sweep (S5, below) found that `STALE_COUNT_PA`/`ONSET_WINDOW_COUNT`/`BAD_ZONE_FLAGS` CAN still change on the exact frame a style is applied — not because the style-change write touches them (confirmed false by code and by instrumentation: the collision correlates with a *different* channel's onset timer expiring that same frame, not `_emit_apply_style`'s own writes), but because `engine_tick` (which processes every channel's onset/bad-zone bookkeeping) runs unconditionally every frame, including a Start-press frame, exactly as it already does on every other frame.** This is the same "recomputes every frame regardless of any button press" background dynamic `test_rom.py`'s own T15.5 comment already documents for `DISSONANCE_SCORE` — this run's finding is that the *same* caveat also applies to the 3 other fields under general/adversarial play, at a non-negligible rate (114/712 ≈ 16% of style-change frames in a 6000-frame randomized-input run), not just the rare case T15.5's narrow comment implies. Recorded as a finding (Medium) — see Findings — because the DoD/AC(4) wording states the invariant in absolute terms without this caveat. | Pass (as literally, narrowly stated: the style-change *write* never touches bad-zone state) — see Finding 1 for the broader-claim precision gap |
| Select resets `DUTY_BIAS` to 0 | `init_engine` (`:989`): `rom.XOR_A(); rom.LD_nn_A(DUTY_BIAS)` on both boot and Select-reset paths (confirmed `init_engine` is the Select-reset target via `input_map.py:81`'s `CALL('init_engine')`). T15.6 confirms `DUTY_BIAS` drifts to a nonzero value after selecting preset 1, then resets to 0 on the exact Select frame. | Pass |
| Every pre-existing test still passes | Full suite run this session: **93/93** (T1-T15 all green — see Test run below). | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. Verified size=32768 via `wc -c`; T1 (part of the 93/93 run) confirms header fields (title=`DRIFTUNE`, CGB flag, checksum, cartridge-type=ROM-only/no MBC, ROM-size=32KB single bank). | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 93/93, run this session, command `python3 test_rom.py`. | Pass |
| `09-package-verification` independently drives a non-default style selection (e.g. index 3, Holiday) live and confirms the DoD holds off whatever single fixture the new suite happens to use | Standalone PyBoy script (not `test_rom.py`'s own fixtures): `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1080.py`. Independently drove: (S1) presets 3, 1, 2 (non-ascending order, distinct from T15's own 1→2→3 walk) with a true single-tick exact-frame read (T15.1-3 use `tap()`'s 2-frame-settled read); (S2) `DUTY_BIAS`'s add-then-wrap composition with the real `NR11` duty register (not just the WRAM byte) at preset 2 (Ambient/Lo-Fi, `duty_bias=0xFF=-1`) vs. default; (S3) a rapid double-Start press (FS-108's own named edge case); (S4) a listener manually steering `TEMPO_IDX` via D-pad after a style is applied, then confirming the next Start press overwrites it back to the new style's own value (FS-108 workflow #2); (S5) a 6000-frame randomized-input stress run. **13/14 independent checks passed outright; the 1 "failing" check (bad-zone fields never changing on a style-change frame, checked strictly) surfaced Finding 1 above** — investigated to root cause (a genuine, pre-existing, unrelated background dynamic, not a defect this package introduced) rather than waved through. | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1230` (`CHMIX_IDX` preset maps to a style row) | `STYLE_TABLE` (`music_engine.py:240-249`), read via `_ld_hl_label('style_table')` + `ADD_HL_BC` in `_emit_apply_style` (`:335-339`), same indexed-table idiom `chmix_masks_table`/`motif_table` already use | T15.1-T15.3; this run's S1 (non-sequential order, exact-frame read) | Pass |
| `FR-1240` (style applied immediately, not next-onset) | `_emit_apply_style` called from `input_map.py:73`, directly after `CHMIX_IDX`'s step (`:66-72`), inside `apply_input` which runs before `engine_tick` each frame (`build_rom.py:80-83`) — no onset gate of any kind | T4.7, T15.1-T15.3 (2-frame-settled read); **this run's S1 independently confirms the literal same-frame timing** (single-tick read, no settle) for presets 3/1/2 specifically | Pass |
| `FR-1250` (≥3 audibly-distinct styles) | 3 named rows (`:242-244`) with materially different tempo/density/scale/duty values per style. Audible-distinctness judgment is explicitly a `09-content-review` task (not asserted here, per FS-108's own Verification Plan) | T15.1-T15.3 confirm each style's parameter *combination* is distinct at the WRAM level; this run's S2 additionally confirmed `DUTY_BIAS`'s effect is independently visible in the real `NR11` register (not just sitting unread in WRAM) — see Test run | Pass (parameter-level; audible judgment deferred to `09-content-review` as designed) |
| `FR-1260` (preset-0 matches shipped default) | `STYLE_TABLE[0]` (`:241`) built directly from `PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX`/`PRESET_SCALE_IDX` constants, `duty_bias=0`; `init_engine` (`:980-989`) independently sets the same 3 constants + zeroes `DUTY_BIAS` | T15.4 (wraps all 8 presets, confirms match); this run's S1's preset-2→preset-3 transitions passed through preset boundaries without incident | Pass |
| `NFR-1080` (ROM/WRAM budget) | `STYLE_TABLE` = 32 bytes (`rom.label('style_table')` + 8×4-byte rows, `:1097-1099`) + 1 new WRAM byte (`DUTY_BIAS`, `0xC03B`) | This run independently re-measured via `rom.pos`-instrumentation (`ADR-0002`'s own method): **3497 of 32768 bytes used, 29271 free** — exactly matching the Master Build Plan's own claimed "+78 bytes, 29271 free" (delta from `VR-1070`'s measured 29349 free = 78 bytes, matching `STYLE_TABLE`'s 32 bytes + assorted `_emit_apply_style`/call-site instruction bytes). ROM still builds to exactly 32768 bytes (single bank, no MBC — cartridge-type/ROM-size bytes unchanged from prior verified packages). | Pass |
| `NFR-1090` (no new input control) | `input_map.py` diff (`git show 20f5d2c -- input_map.py`): `_emit_apply_style` is called from the *existing* Start-press branch (`ai_start`'s predecessor code, `:66-74`); no new joypad bit, no new `JOY_*` constant, no new control read anywhere in the diff | Confirmed by direct diff read; no test needed beyond code inspection (same standing pattern `VR-1070`'s `NFR-1070` audit used) | Pass |

No RTM file at FR-grain currently exists in this tree (same standing gap `VR-9010`/`VR-9020`/
`VR-1060`/`VR-1061`/`VR-1070` already noted — `docs/requirements/01-functional-requirements.md`
is the traceability source of record at FR grain). Traceability above is derived directly from
that document's FR text against the shipped code and tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes; header valid (T1 confirms all header
  fields; this run additionally independently re-measured `rom.pos` = 3497, free = 29271 bytes,
  matching the package's own claimed ROM-budget figure exactly).
- `python3 test_rom.py` → **93 PASS, 0 FAIL** out of 93 (full suite, T1-T15).
- Independent non-default live drive (standalone script,
  `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1080.py`):
  - **S1** (exact-frame timing, non-sequential preset order 3→1→2, distinct from T15's own
    sequential 1→2→3 walk and 2-frame-settled reads): all 3 transitions matched their documented
    `STYLE_TABLE` row on the literal single-tick press frame — `(3,3,0,1)`, `(6,6,2,1)`,
    `(1,0,3,255)` respectively, all exact.
  - **S2** (`DUTY_BIAS` composition with the real duty-cycle register): reached preset 2
    (Ambient/Lo-Fi, `duty_bias=0xFF`), confirmed `NR11`'s duty bits (bits 6-7) visited a
    different set of values ({0,128,192}) than the default preset's own set ({0,64}) over a
    400-frame sample window each — direct register-level confirmation that `DUTY_BIAS` actually
    composes with `_emit_channel_gen`'s existing duty-write site (`music_engine.py:595-606`), not
    just an unread WRAM byte.
  - **S3** (rapid double-Start, FS-108's own named edge case): two Start presses one frame apart
    landed cleanly on preset 2 with preset 2's full style applied — no coalescing, no skipped
    intermediate style, no stuck/partial state.
  - **S4** (FS-108 workflow #2 — manual steering then overwrite): selected preset 1
    (`TEMPO_IDX=6`), manually drove `TEMPO_IDX` down to 2 via 4 D-pad-Down taps, confirmed the
    drift took effect, then pressed Start again (→ preset 2) and confirmed `TEMPO_IDX` was
    overwritten to preset 2's own value (1) rather than continuing from the manually-drifted
    value — the "listener resumes steering from an honest new baseline" claim, independently
    exercised.
  - **S5** (extended randomized-input stress, several thousand frames): 6000 frames of uniformly
    random button presses (all 8 controls), no hang, engine remained responsive throughout;
    reached a bad-zone state at least once; `CHMIX_IDX` (style) changed 712 times over the run,
    genuinely exercising style transitions throughout, not just at the start. Of those 712
    style-change frames, 114 (≈16%) showed a coincidental change in `BAD_ZONE_FLAGS`/
    `STALE_COUNT_PA`/`ONSET_WINDOW_COUNT` on the same frame — root-caused via targeted
    instrumentation (a second diagnostic script cross-checking `NOTE_TIMER_PA` against each
    "violating" frame) to a *different* channel's onset timer independently expiring that same
    frame, not `_emit_apply_style`'s own writes (which the code confirms never touch those
    addresses). This is a genuine finding about claim precision, not a functional defect — see
    Finding 1.
  - 6000+6000 frames total (S5's stress run plus the cumulative frame count across S1-S4's
    scenarios) at non-default, adversarial-random combinations — no hang, no crash, engine
    remained responsive throughout.

## Scope audit

Package declared `music_engine.py` only for code (plus the one named call-site addition in
`input_map.py`, explicitly flagged in the package's own Interfaces field as "an added step in
that existing call chain, not a new call site or a change to `_step_on_bit`'s own code"), plus
`Claude.md`/`memory.md`/GDS-07/`docs/pipeline/backlog.md` for documentation.

Actual diff (`git show 20f5d2c --stat`): `Claude.md`, `Driftune.gbc`, `ROADMAP.md`,
`docs/architecture/07-data-model.md`, `docs/features/INDEX.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`input_map.py`, `memory.md`, `music_engine.py`, `test_results.txt`, `test_rom.py`.

`input_map.py` IS touched (17 lines), but exactly as the package's own Interfaces field
predicted and scoped — one new `import` (`_emit_apply_style`), one new call inserted into the
existing Start-press branch, and no change to `_step_on_bit` or any other control's handling
(confirmed: `git show 20f5d2c -- input_map.py` shows only the Start-branch addition and its
import). Not an excursion.

Files outside the package's declared `Documentation Updates` list: `ROADMAP.md`,
`docs/features/INDEX.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `test_results.txt` — all small, accurate, in-the-spirit
status-row updates (ledger bookkeeping this package's own commit correctly kept in sync), same
low-risk pattern `VR-9010`/`VR-1070` already found and accepted for analogous undeclared-but-
accurate edits. Not functional excursions.

`test_rom.py`'s existing T4.7 assertion was *changed* (not just extended) — the "no other
parameter changed" invariant every other control in T4's table still holds was correctly
special-cased for Start, since Start now legitimately changes 4 addresses by design. Read the
full diff context (`test_rom.py:183-194`): this is a deliberate, correctly-reasoned test update
matching the feature's own intended behavior change, not a masked regression — confirmed by
independently re-deriving what the pre-`IP-1080` invariant should now correctly assert for Start
specifically (exactly what the diff shows).

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| FS-108's acceptance criterion (4) and `IP-1080`'s DoD both state, in absolute terms, that "a style change does not alter `DISSONANCE_SCORE`/`BAD_ZONE_FLAGS`/`STALE_COUNT_*`/`ONSET_WINDOW_COUNT`." This is true in the narrow, code-verified sense that `_emit_apply_style`'s own writes never touch those addresses (confirmed by full-body code read). It is **not** true in the broader sense a literal reading implies — that a Start press changing style is guaranteed to leave those bytes reading identical to the previous frame in all circumstances. `engine_tick` (which processes every channel's onset/bad-zone bookkeeping) runs unconditionally every frame, including the exact frame a style is applied, exactly as it does on every other frame — so a coincidental onset from an *unrelated* channel can still update `STALE_COUNT_PA`/`ONSET_WINDOW_COUNT`/`BAD_ZONE_FLAGS` on that same frame. `test_rom.py`'s own T15.5 comment already documents this exact caveat for `DISSONANCE_SCORE` ("recomputes every single frame regardless of any button press... a background dynamic unrelated to this feature") but does not extend the same caveat to the other 3 fields, and its own single from-boot-default test scenario happens not to hit the collision. This run's broader randomized-stress sweep (6000 frames, 712 real style-change frames) measured a ≈16% same-frame-collision rate under adversarial/randomized play — root-caused via instrumentation to independent, unrelated channel-onset timing, not a code defect this package introduced, but a real gap between the DoD/AC(4)'s literal wording and what is actually guaranteed. | Medium (a requirements/acceptance-criterion precision gap — the underlying engine behavior is correct and intentional per `ADS-101`'s "bad-zone bookkeeping stays scheme/style-agnostic and keeps ticking every frame" design, but the claim as written could mislead a future reader — e.g. `09-content-review` or a future package depending on this invariant — into assuming a stronger same-frame guarantee than the code actually provides; no crash/correctness risk) | `04-requirements-engineering` (reword `FR-1240`'s companion acceptance criterion / a future FS-108 revision to state the invariant precisely: "the style-change write itself never touches bad-zone state; bad-zone fields may still coincidentally change on the same frame due to other channels' independent onset activity, exactly as `DISSONANCE_SCORE` already does every frame") — same pattern as `VR-1070`'s own recorded test-methodology-precision finding, not a code fix |
| The Master Build Plan's / `IP-1080`'s own claimed ROM-budget figures ("+78 bytes, 29271 free") were independently re-derived by this run via direct `rom.pos`-instrumentation (`ADR-0002`'s own method, not merely re-quoted) and matched exactly (3497 used / 29271 free). No discrepancy found — recorded here only because the Verification Checklist gate requires this to be independently re-confirmed, not assumed, per this package's own Risks field ("this package should confirm against the actual printed `build_rom.py` layout / `rom.pos`-instrumentation measurement... not merely assumed negligible"). | Low (confirmation note, not a defect — the package's own claim was accurate) | None — informational, closes out the package's own Risks-field self-check requirement |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1080` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1080` row status updated to `VERIFIED`.
- `docs/features/INDEX.md`: `FEAT-1080`/`FS-108` row updated to reflect `IP-1080` `VERIFIED`.
- `ROADMAP.md`: stage-08/09 rows updated — `IP-1080` now `VERIFIED` via this report; all 13
  shipped packages now `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
