# VR-9020 — Verification Report: IP-9020 (Overload threshold recalibration, remediation for `BL-0017`)

## Package

- **Package:** [`IP-9020`](../packages/IP-9020-overload-threshold-recalibration.md) — Overload
  threshold recalibration
- **Commit verified:** `075642f` (tip of tree at verification time, immediately after this
  session's own `VR-9010` commit; `IP-9020`'s own code landed in `0a1a423`)
- **Session independence:** genuinely fresh session — this session did not author `IP-9020`
  (built and self-tested in an earlier session today, per `docs/pipeline/pipeline-journal.md`
  run #33 / commit `0a1a423`). No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. One Low
finding recorded (does not block `VERIFIED`, see Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `BAD_ZONE_FLAGS` bit2 is empirically observed set within the new test's bounded frame budget at a realistic (not necessarily maximal) tempo/density combination | `test_rom.py` T13.1 (`tempo_idx=6`/`density_idx=5`, both realistic-high not maximal): observed within 2000 frames. Independently re-driven this session at a **different** combination (`TEMPO_IDX=5`/`DENSITY_IDX=6`, one Up + six B presses — neither index maximal): OVERLOAD observed within 2000 frames, peak `ONSET_WINDOW_COUNT`=9. | Pass |
| The default/sparse preset does not spuriously trigger it over an equivalently long run | `test_rom.py` T13.2: no spurious trigger over 2000 frames. Independently re-confirmed this session over an independent 2000-frame run: `spurious_overload=False`, peak `ONSET_WINDOW_COUNT`=6 — matches the package's own documented empirical measurement ("default peaks at 6") exactly. | Pass |
| Every pre-existing test still passes | Full suite run this session: **77/77** (T1-T13, all green — see Test run below). | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. T1 suite confirms full header-field validity. | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new check (G5) | 77/77, run this session, command `python3 test_rom.py`. | Pass |
| `09-package-verification` independently re-drives a realistic-but-non-maximal tempo/density combination live and confirms OVERLOAD triggers within a reasonable frame budget — not just trusting the new test's own fixture | Wrote and ran a standalone PyBoy script (not `test_rom.py`'s own T13 fixture) driving the built ROM to `TEMPO_IDX=5` (1 Up press from default 4) / `DENSITY_IDX=6` (6 B presses from default 0) — a different, realistic-high, non-maximal combination than T13's own fixture (`TEMPO_IDX=6`/`DENSITY_IDX=5`); neither index is at its maximum (7). Over 2000 frames: `overload_seen=True`, peak `ONSET_WINDOW_COUNT`=9 (above the `OVERLOAD_THRESHOLD=7`, i.e. `count>7` fires, consistent with the package's own empirically-measured peak-of-8 finding for its own combination). Also independently re-ran the default-preset non-spurious check over a second, independent 2000-frame run: no spurious trigger, peak count 6. Script: `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip9020.py` (full output recorded in this run's transcript). | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1100` ("...counts note-onset events across all channels in a rolling window and sets `BAD_ZONE_FLAGS` bit2 (OVERLOAD) when the count exceeds the overload threshold within the window") | `_emit_badzone_tick` (`music_engine.py:733-751`) — unchanged logic from `IP-0004`/`IP-0007`; only the `OVERLOAD_THRESHOLD` constant (`music_engine.py:78`, `20`→`7`) changed, with `ONSET_WINDOW_FRAMES` (`:79`, `32`) left unchanged. Inline comment (`:64-77`) records the recalibration's empirical justification (measured peaks: default=6, realistic-high=8, max=11), matching the package's own task-3 requirement to document the new value's justification the way `DISSONANCE_WEIGHT_BY_IC` cites its R204 grounding. | T13.1/T13.2, plus this run's independent live drive at a third, distinct combination (`TEMPO_IDX=5`/`DENSITY_IDX=6`) | Pass |

No RTM file at FR-grain currently exists in this tree (see `VR-9010`'s identical note on this
point — `docs/roadmap/07-traceability-matrix.md` operates at capability/milestone grain, not FR
grain, and editing it is out of this skill's scope). Traceability above is derived directly from
`docs/requirements/01-functional-requirements.md`'s `FR-1100` text against the shipped code and
tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, header valid (T1 confirms all header fields).
- `python3 test_rom.py` → **77 PASS, 0 FAIL** out of 77 (full suite, T1-T13).
- Independent live drive (standalone script, `TEMPO_IDX=5`/`DENSITY_IDX=6` — distinct from T13's
  own `TEMPO_IDX=6`/`DENSITY_IDX=5` fixture): OVERLOAD confirmed reachable, peak
  `ONSET_WINDOW_COUNT`=9, within 2000 frames.
- Independent live re-drive of the default/sparse preset over an independent 2000-frame run: no
  spurious OVERLOAD trigger, peak `ONSET_WINDOW_COUNT`=6 (matches the package's own documented
  empirical measurement exactly).
- 8200-frame stress run (fresh boot, no input, default preset): no hang, `BAD_ZONE_FLAGS`=`0b0`
  (clean, no spurious bad-zone state) at the end.

## Scope audit

Package declared `music_engine.py` only for code (a pure constant-value change plus its
justifying comment), and `docs/pipeline/backlog.md` only for documentation ("no
architecture/requirements doc changes needed"). Actual diff (`git show 0a1a423 --stat`):
`Claude.md`, `Driftune.gbc`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/pipeline/backlog.md`, `music_engine.py`,
`test_results.txt`, `test_rom.py`. `music_engine.py`'s actual diff confirmed constant-only
(`OVERLOAD_THRESHOLD` `20`→`7`, `ONSET_WINDOW_FRAMES` left at `32`) plus the justifying comment
block — matches the package's own "pure constant change" framing exactly, zero ROM-budget impact.

`Claude.md` was updated (test-count line `73`→`77`/`T1-T12`→`T1-T13`, plus a new bullet
summarizing the recalibration) but was not named in the package's own `Documentation Updates`
field — a small, accurate, in-the-spirit bookkeeping update (test-count lines need updating
regardless of which package added tests), not a functional excursion. Flagged as a minor scope
note (see Findings), same low-severity pattern as `VR-9010`'s equivalent finding for
`docs/architecture/07-data-model.md`.

No excursion into `input_map.py`, `build_rom.py`, or any other file — the change is exactly as
narrow as the package doc promised.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| `Claude.md`'s test-count line and Known-Issues bullet were updated by this package's commit even though the package's own `Documentation Updates` field only names `docs/pipeline/backlog.md`. The edit itself is accurate and necessary bookkeeping (the shipped test count genuinely changed), so no functional or coherence defect — but it is an undeclared scope addition, the same pattern flagged in `VR-9010` for `IP-9010`'s equivalent `docs/architecture/07-data-model.md` touch. | Low (beneficial, undeclared scope addition — doc-only, necessary bookkeeping) | 07-implementation-planning (note the recurring pattern across both `IP-9010` and `IP-9020`: a package's `Documentation Updates` field should routinely name `Claude.md`'s test-count line whenever `Tests to Add` adds a new suite, since every package that adds tests will need this same one-line touch) |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-9020` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-9020` row status updated to `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
- `docs/pipeline/backlog.md`: `BL-0017` "Run" note appended with this verification's outcome
  (Status left as-is, per this skill's scope — status flip to `DONE` is the pipeline manager's
  job).
