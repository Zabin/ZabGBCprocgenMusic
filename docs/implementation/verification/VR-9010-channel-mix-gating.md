# VR-9010 — Verification Report: IP-9010 (Channel-mix gating, remediation for `BL-0019`)

## Package

- **Package:** [`IP-9010`](../packages/IP-9010-channel-mix-gating.md) — Channel-mix gating
- **Commit verified:** `0821b4f` (tip of tree at verification time; `IP-9010`'s own code landed
  in `3995231`)
- **Session independence:** genuinely fresh session — this session did not author `IP-9010`
  (built and self-tested in an earlier session today, per `docs/pipeline/pipeline-journal.md`
  run #33 / commit `3995231`). No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. Two
Low-Medium findings recorded (do not block `VERIFIED`, see Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `CHMIX_MASKS` (or equivalent) exists and is consumed by all 4 channels' generation routines | `CHMIX_MASKS` (`music_engine.py:182-191`), an 8-entry table, bit0=pa/bit1=pb/bit2=wv/bit3=nz. Consumed by `_emit_channel_gen` (`music_engine.py:376-391`, gates `dac_reg`/`dac_on`/`bit_index` before the frequency/duty write block) for pulse A/B/wave, and by `_emit_noise_gen` (`music_engine.py:611-634`) for noise. `CHANNELS` table (`:158-168`) carries each channel's `dac_reg`/`dac_on`/`bit_index` (NR12/0xF3/0 for pa, NR22/0xF3/1 for pb, NR30/0x80/2 for wv) — confirmed identical to `build_rom.py:58,61,63`'s own boot-time writes to the same registers, so re-enabling reproduces the exact boot tone. | Pass |
| An excluded channel silences (inactive in `NR52`) and a re-included channel resumes, both confirmed by the new test suite | `test_rom.py` T12 (5 checks, `t12_channel_mix_gating`, lines 441-487): T12.3/T12.4 confirm pulse B/wave inactive in `NR52` after stepping to preset 3 (`0b1001`); T12.7/T12.8 confirm both resume after wrapping back to preset 0. Muting mechanism forces the DAC/envelope off explicitly (`XOR_A`/`LDH_n_A(dac_reg)` for pitched channels at `:387-389`, `XOR_A`/`LDH_n_A(NR42)` for noise at `:634`) — guarantees `NR52` inactivity within the same onset, not merely "stopped retriggering," per the package doc's own non-negotiable point. | Pass |
| Every pre-existing test still passes (regression) | Full suite run this session: **77/77** (T1-T13, all green — see Test run below). T12.1 itself is the explicit regression guard for preset-0-all-active. | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. Verified size=32768, title=`DRIFTUNE`, CGB flag=0x80, checksum byte=0x72 (non-zero/plausible; T1 suite covers full header-field assertions). | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 77/77, run this session, command `python3 test_rom.py`. | Pass |
| `NR52` correctly reflects `CHMIX_IDX`'s current mask for at least one non-default, non-trivial combination, independently re-driven live by `09-package-verification` (not just trusting the new suite's own fixture) | Wrote and ran a standalone PyBoy script (not `test_rom.py`'s own fixtures) driving the built ROM to **preset 5** (`0b1100` = wave + noise active, pulse A + pulse B excluded) — a different, non-default, non-trivial combination than `test_rom.py`'s own T12 fixture (which drives preset 3, `0b1001`). After a 60-frame settle (allowing the in-flight note started under the prior mask to finish, matching the package doc's own "run enough frames for that channel's current note to finish" allowance) and a 400-frame sampling window: `pulse_a_ever_on=False`, `pulse_b_ever_on=False`, `wave_ever_on=True`, `noise_ever_on=True` — exactly matching mask `0b1100`. Then stepped Start 3 more times (wrap 5+3=8→0) and confirmed all 4 channels resumed reporting active in `NR52` within 300 frames. Script: `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip9010.py` (full output recorded in this run's transcript). | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1000` ("...begins generating audio on all channels its channel-mix preset activates...") | `CHMIX_MASKS[0] = 0b1111` (all 4 active at boot preset), `init_engine` writes `PRESET_CHMIX_IDX` to `CHMIX_IDX` (`music_engine.py:776`) | T2 (boot), T12.1 (regression guard: all 4 active at boot preset over a sustained run) | Pass |
| `FR-1010` ("...`NR52` reports each active channel as currently playing when its channel-mix preset includes it") | Gating logic in `_emit_channel_gen`/`_emit_noise_gen` as above | T12.3-T12.5 (exclusion), T12.7-T12.8 (re-inclusion), plus this run's independent live drive at preset 5 | Pass |
| `FR-1060` (Start steps `CHMIX_IDX` by exactly one, wrapping, edge-triggered — already satisfied, unaffected by this package) | `input_map.py`'s existing Start handler, unchanged by this package (confirmed via scope audit below) | T4.7 (pre-existing, unaffected), T12.2/T12.6 (this package's own tests re-confirm stepping as a side effect) | Pass |

No RTM file at FR-grain currently exists in this tree (`docs/requirements/` has no dedicated
traceability-matrix document; `docs/roadmap/07-traceability-matrix.md` operates at
capability/milestone grain, not FR grain, and is out of this skill's scope to edit). Traceability
above is derived directly from `docs/requirements/01-functional-requirements.md`'s FR text against
the shipped code and tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, header valid (T1 confirms all header fields).
- `python3 test_rom.py` → **77 PASS, 0 FAIL** out of 77 (full suite, T1-T13 — T13 belongs to
  `IP-9020`, verified separately, but is part of the same full-suite run recorded here for the
  record).
- Independent non-default live drive (standalone script, preset 5 = `0b1100`, wave+noise only):
  pulse A/B confirmed silenced, wave+noise confirmed active, over 400 independently-driven frames;
  re-inclusion after wrapping back to preset 0 confirmed within 300 frames.
- 8200-frame stress run (fresh boot, no input, default preset): no hang, `NR52` = `0b11110111`
  (valid, all pitched channels + wave/noise gated as expected) at the end.

## Scope audit

Package declared `music_engine.py` only for code, plus `Claude.md`/`memory.md`/
`docs/pipeline/backlog.md` for documentation. Actual diff (`git show 3995231 --stat`): `Claude.md`,
`Driftune.gbc`, `docs/architecture/07-data-model.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/pipeline/backlog.md`, `memory.md`,
`music_engine.py`, `test_results.txt`, `test_rom.py`. The one file outside the package's declared
`Documentation Updates` list is `docs/architecture/07-data-model.md` (one line changed: the
`CHMIX_IDX` WRAM-map row updated to describe the real mask table instead of the stale
"index into the channel-activity-mask preset table" placeholder text) — a small, accurate,
in-the-spirit doc-coherence fix, not a functional excursion. Flagged as a minor scope note, not a
blocking finding (see Findings).

No excursion into `input_map.py` or `build_rom.py`, matching the package's own claim that neither
needed changes.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| `docs/architecture/07-data-model.md`'s `CHMIX_IDX` row was updated by this package's commit even though the package's own `Documentation Updates` field only names `Claude.md`/`memory.md`/`docs/pipeline/backlog.md`. The edit itself is accurate and beneficial (removes stale text), so no functional or coherence defect — but it is an undeclared scope addition. | Low (beneficial, undeclared scope addition — doc-only) | 07-implementation-planning (note the pattern for future packages: name every doc file actually likely to need a one-line update, or accept small beneficial doc-scope drift as standard practice) |
| The implementation's own code comment (`music_engine.py:274-281`, in `_emit_channel_gen`'s docstring) states the dissonance-scoring-includes-muted-channels design decision was "Flagged to the backlog, not silently decided" — but no corresponding entry exists in `docs/pipeline/backlog.md` for this specific decision (searched for "dissonance"/"chmix"/"muted channel" combinations — no match). The design decision itself is sound and clearly documented in code, and does not block `FR-1010`/`FR-1000` (dissonance scoring is `FR-1080`'s concern, not this package's Requirements Covered), but the traceability claim in the comment is currently false — nothing was actually filed. | Low-Medium (a documentation/traceability claim in shipped code doesn't match the actual backlog state — same "implementation-outpaced-doc" pattern as `BL-0025`/`BL-0026`) | 00-intake (file the actual backlog entry the code comment claims already exists — record the dissonance-scoring-vs-channel-mix interaction as a named, disclosed design decision) |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-9010` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-9010` row status updated to `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
- `docs/pipeline/backlog.md`: `BL-0019` "Run" note appended with this verification's outcome
  (Status left as-is, per this skill's scope — status flip to `DONE` is the pipeline manager's
  job).
