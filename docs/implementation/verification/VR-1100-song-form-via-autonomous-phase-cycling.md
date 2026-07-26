# VR-1100 — Verification Report: IP-1100 (Song-Form via Autonomous Phase Cycling, roadmap R6)

## Package

- **Package:** [`IP-1100`](../packages/IP-1100-song-form-via-autonomous-phase-cycling.md)
  — adds a new, independent state machine (`SONG_STATE`/`SONG_STATE_TIMER_LO`/
  `SONG_STATE_TIMER_HI`) that autonomously cycles 4 named song-form phases
  (INTRO→BUILD→PEAK→BREAKDOWN→INTRO, looping), overwriting `TEMPO_IDX`/`DENSITY_IDX` to a new
  `SONG_TABLE`'s target values on each transition (`FS-110`/`ADS-103`).
- **Commit verified:** `6c0a7d0` ("feat(engine): IP-1100 -- song-form via autonomous phase
  cycling (roadmap R6)") — tip of tree at verification time was `d33b76b` (a journal-only entry
  recording `IP-1100` as `COMPLETE`, no functional changes on top).
- **Session independence:** genuinely fresh session — this session has no memory of authoring
  `IP-1100`; the implementing commit's own timestamp and the master build plan both attribute
  the work to a prior session. No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. Three
findings recorded (two Low/Low-Medium test-coverage/doc-coherence notes, one informational Low
finding on the empirical BUILD/`OVERLOAD` question the package itself named as open) — none
blocks `VERIFIED`; see Findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| With no input, the engine autonomously cycles all 4 named phases in order, each transition overwriting `TEMPO_IDX`/`DENSITY_IDX` on the transition frame itself | `_emit_song_tick` (`music_engine.py:1074-1120`): 16-bit decrement-with-borrow countdown; on reaching 0, `SONG_STATE` advances (`INC_A`/`AND_n(N_SONG_PHASES-1)`, wrap mod 4) and `TEMPO_IDX`/`DENSITY_IDX` are overwritten from `SONG_TABLE[SONG_STATE]`'s row, same frame. `SONG_TABLE` (`:276-282`): 4 rows, `(tempo_idx, density_idx, duration_lo, duration_hi)` — INTRO `(4,0,1800)`, BUILD `(4,4,1800)`, PEAK `(6,6,1200)`, BREAKDOWN `(3,2,1800)`. `T17.1`-`T17.4` (shipped) and this run's own independent S0/S1 live drive (re-derived transition frames from a fresh boot with zero button input: `1764→1, 3564→2, 4764→3, 6564→0`, matching cyclic order `[1,2,3,0]`, `TEMPO_IDX`/`DENSITY_IDX` exactly matching `SONG_TABLE` on every transition frame) both confirm. | Pass |
| Bad-zone/motif-variant state is unaffected by any phase transition | `_emit_song_tick`'s full body (`:1074-1120`) reads/writes only `SONG_STATE`/`SONG_STATE_TIMER_LO`/`HI`/`TEMPO_IDX`/`DENSITY_IDX` — confirmed by reading the routine end to end, no write to `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/`STALE_COUNT_*`/`ONSET_WINDOW_COUNT`/`CUR_DEGREE_*`/`MOTIF_VARIANT_IDX`/`scheme_state` anywhere in the diff (`git show 6c0a7d0` confirms `music_engine.py`'s only other changes are `SONG_TABLE`/WRAM-constant additions and the `engine_tick` call site). `T17.5` (shipped) samples `BAD_ZONE_FLAGS`/`STALE_COUNT_PA`/`ONSET_WINDOW_COUNT`/`MOTIF_VARIANT_IDX` immediately before and after a transition frame and finds no change. | Pass |
| A Start press landing on the same frame as a phase transition corrupts neither mechanism | `engine_tick`'s call order (`music_engine.py:1203-1227`): `apply_input` (which calls `_emit_apply_style` on a Start edge) runs from the main loop *before* `engine_tick`, and within `engine_tick`, `_emit_song_tick` is the last call (`:1227`, after `_emit_badzone_tick`) — so on a same-frame collision, `_emit_apply_style`'s `TEMPO_IDX`/`DENSITY_IDX` write always happens first in real time, then `_emit_song_tick`'s write (if a transition lands that frame) overwrites it last — confirmed directly from `build_rom.py:80-85`'s `apply_input`→`engine_tick` ordering and `music_engine.py:1208-1227`'s internal call order, not merely asserted. `T17.6` (shipped) forces this collision at the empirically-derived INTRO→BUILD boundary and confirms `SONG_STATE` advances, `CHMIX_IDX` steps, and song-form's value wins. This run's own independent S0/S1 (below) re-derived the transition frame independently and additionally forced the identical collision at the BUILD→PEAK and PEAK→BREAKDOWN boundaries — the shipped suite's own `T17.6` exercises only the first (INTRO→BUILD) boundary; see Finding 1. | Pass |
| Select resets to phase 0 | `init_engine` (`music_engine.py:1144-1154`): `SONG_STATE` zeroed, `TEMPO_IDX`/`DENSITY_IDX`/`SONG_STATE_TIMER_LO`/`HI` reloaded from `SONG_TABLE[0]`. `T17.7`/`T17.8` (shipped) confirm on the exact reset frame. | Pass |
| Every pre-existing test still passes | Full suite run this session: **112/112** (T1-T17 all green — see Test run below). | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. Verified via `wc -c` = 32768. `T1` (part of the 112/112 run) confirms header fields. | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 112/112, run this session, command `python3 test_rom.py`. | Pass |
| `09-package-verification` independently drives a non-default scenario (mid-cycle entry, or the guaranteed Start-press/transition collision) live and confirms the DoD holds beyond whatever single fixture the new suite happens to use | Standalone PyBoy script (not `test_rom.py`'s own fixtures): `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1100.py`. Re-derived transition frames from scratch (S0), forced the guaranteed collision at **three** distinct phase boundaries rather than only the one `T17.6` exercises (S1), and drove a separate empirical `OVERLOAD`-frequency comparison (S2) plus a 20,000-frame stability run — see Test run, below. | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1310` (autonomous 4-phase cycle, no input required) | `_emit_song_tick` (`music_engine.py:1074-1120`), called from `engine_tick` (`:1227`) with no joypad read anywhere in the routine | `T17.1`-`T17.3`; this run's S0 (independent re-derivation over a fresh, untapped 8000-frame boot) | Pass |
| `FR-1320` (phase transition overwrites tempo/density immediately, same tick) | `_emit_song_tick`'s transition branch writes `TEMPO_IDX`/`DENSITY_IDX` before `RET` (`:1114-1115`), same frame the countdown reaches 0 | `T17.4`; this run's S0/S1 (values checked exactly on the transition frame itself at every observed boundary) | Pass |
| `FR-1330` (bad-zone/motif-variant mechanisms phase-agnostic) | Confirmed by full-body read of `_emit_song_tick` (no write to either mechanism's fields) and of `_emit_badzone_tick`/the motif-variant-draw code (neither reads `SONG_STATE`/`SONG_STATE_TIMER_*`) | `T17.5` | Pass |
| `FR-1340` (all 4 phases occur in cyclic order over a long run) | `SONG_STATE`'s wrap-mod-4 advance (`:1106`) | `T17.2`/`T17.3` (7000-frame run); this run's own 20,000-frame stability run (S3) — `SONG_STATE` stayed within `{0,1,2,3}` throughout, multiple full cycles, no hang | Pass |
| `NFR-1120` (ROM/WRAM budget) | `SONG_TABLE` (16 bytes) + 3 new WRAM bytes (`SONG_STATE`/`SONG_STATE_TIMER_LO`/`HI`) | This run independently re-measured via `rom.pos`-instrumentation (`ADR-0002`'s own method, script `/tmp/.../scratchpad/measure_rom.py`): **3791 of 32768 bytes used, 28977 free** — a delta of exactly -112 bytes from `VR-1090`'s own measured 29089 free, matching the Master Build Plan's own claimed "-112 bytes (28977 free)" figure exactly. | Pass |
| `NFR-1130` (no new input control) | `git show 6c0a7d0 --stat` confirms `input_map.py` is entirely untouched by this commit; only `music_engine.py` and `test_rom.py` gained code, plus documentation files. | Confirmed by direct diff read | Pass |

No RTM file at FR-grain currently exists in this tree (same standing gap `VR-9010`/`VR-9020`/
`VR-1070`/`VR-1080`/`VR-1090` already noted — `docs/requirements/01-functional-requirements.md`
is the traceability source of record at FR grain). Traceability above is derived directly from
that document's FR text (confirmed present: `FR-1310`-`FR-1340`, `NFR-1120`/`NFR-1130`, added in
the 2026-07-26 delta review) against the shipped code and tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes; header valid (`T1` confirms all header
  fields; this run additionally independently re-measured `rom.pos` = 3791, free = 28977 bytes,
  matching the package's/Master Build Plan's own claimed ROM-budget figure exactly).
- `python3 test_rom.py` → **112 PASS, 0 FAIL** out of 112 (full suite, T1-T17).
- Independent non-default/adversarial live drive (standalone script,
  `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1100.py`),
  built specifically to stress-test the two risks both `IP-1100`'s package doc and `FS-110` name
  as real, previously-unresolved:
  - **S0** (independent boundary re-derivation): a clean fresh boot, zero button input, 8000
    frames, recording every `SONG_STATE` transition directly (not trusting `T17.6`'s own frame
    number): `[(1764, 1), (3564, 2), (4764, 3), (6564, 0)]` — cyclic order `[1,2,3,0]` confirmed,
    matching `T17.3`'s own assertion shape but derived from scratch by this run.
  - **S1** (guaranteed exact-frame collision at three distinct boundaries, not just the first):
    using S0's own independently-recorded frames, forced a real Start press on the exact frame of
    each of the INTRO→BUILD (1764), BUILD→PEAK (3564), and PEAK→BREAKDOWN (4764) transitions —
    `T17.6`, as shipped, only exercises the first of these. All three collisions: `SONG_STATE`
    advanced correctly, `CHMIX_IDX` stepped correctly (0→1 each time, confirming the style
    mechanism's own bookkeeping was untouched by the song-form write), and `TEMPO_IDX`/
    `DENSITY_IDX` matched `SONG_TABLE`'s (not `STYLE_TABLE`'s) target values at every collision —
    confirming "song-form's write wins" holds at every tested boundary, not only the first. (One
    incidental observation: at the BUILD→PEAK collision, `STYLE_TABLE[1]` — the CHMIX_IDX preset
    landed on — happens to hold the identical `(6,6)` tempo/density pair as `SONG_TABLE[2]`
    (PEAK), a data coincidence, not a code interaction; the other two boundaries have distinct
    style/song values and still show song-form's write landing last and winning.)
  - **S2** (empirical `OVERLOAD` frequency: BUILD-phase density vs. default): compared
    `BAD_ZONE_FLAGS` bit2 (`OVERLOAD`) activity across four full song-form-cycle repetitions
    (40,000 frames total, ~7000-11000 frames per phase) at each phase's own `SONG_TABLE` tempo/
    density pair: **INTRO** (tempo=4, density=0, identical to the shipped default preset):
    0/11200 frames (0.000%). **BUILD** (tempo=4, density=4): 0/10800 frames (0.000%) — BUILD's
    own density target does **not** measurably raise `OVERLOAD` frequency versus the default in
    this measurement; both are 0%. **PEAK** (tempo=6, density=6): 1512/7200 frames (21.0%) — a
    materially higher `OVERLOAD` rate. **BREAKDOWN** (tempo=3, density=2): 56/10800 frames
    (0.519%). See Finding 2 for the implication (the package's own named risk was about BUILD;
    the empirically-significant `OVERLOAD` phase turns out to be PEAK, one step later in the
    cycle, which the package doc/spec do not separately flag).
  - **S3** (stability): a 20,000-frame run (roughly 3 full song-form cycles) confirmed `SONG_STATE`
    stayed within `{0,1,2,3}` throughout, `SONG_STATE_TIMER_LO`/`HI` stayed within a valid 16-bit
    range at every sampled frame, and no hang/crash occurred.
  - No hang, no crash, engine remained responsive throughout all of S0/S1/S2/S3 (over 68,000
    cumulative frames driven independently at non-default/adversarial combinations distinct from
    every shipped fixture).

## Scope audit

Package declared `music_engine.py` only for code. Actual diff (`git show 6c0a7d0 --stat`):
`Claude.md`, `Driftune.gbc`, `ROADMAP.md`, `docs/architecture/07-data-model.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`memory.md`, `music_engine.py`, `test_results.txt`, `test_rom.py`.

`music_engine.py` is the only production-code file touched for the feature itself; `test_rom.py`
also gained code (the new `T17` suite plus a legitimate, disclosed fix to a pre-existing `T16.7`
assertion whose sampling was one frame stale relative to when the bad-zone override mechanism
actually reads `BAD_ZONE_FLAGS` — this only surfaced once song-form's own density changes altered
the Euclidean-onset trajectory, and is an in-scope test-methodology correction, not a functional
change to `IP-1090`'s own shipped behavior). No excursion into `input_map.py`, `visuals.py`,
`gbc_lib.py`, or `build_rom.py`. All other touched files are documentation/ledger bookkeeping the
package's own `Documentation Updates` field named (`Claude.md`, `memory.md`, GDS-07/
`docs/architecture/07-data-model.md`) plus accurate status-row updates (`ROADMAP.md`, the Master
Build Plan, `packages/INDEX.md`, `test_results.txt`) — same low-risk pattern prior VRs already
found and accepted for analogous undeclared-but-accurate edits.

Unlike `VR-1090`'s own Finding 4 (a stale committed `Driftune.gbc` binary), this commit **did**
refresh the committed ROM binary alongside the source changes (`Driftune.gbc | Bin 32768 ->
32768 bytes` in the `--stat` output) — restoring the "commit the build artifact with the source"
convention `IP-1090`'s implementing commit had been the first to skip. Not a finding; noted as a
positive scope-audit observation.

One doc-coherence gap found during this scope audit, outside the implementing commit itself:
`docs/features/INDEX.md`'s `FEAT-1100`/`FS-110` row still reads "`READY`, G3-authorized... not
yet built," which is stale — the package is actually `COMPLETE` and shipped (112/112 tests, all
subsequently independently re-confirmed by this run). This file is not part of `IP-1100`'s own
declared `Documentation Updates` list; per this run's ledger-write scope (Master Build Plan +
`packages/INDEX.md` + `ROADMAP.md`, mirroring `VR-1090`'s own precedent for touching
`docs/features/INDEX.md` when it is directly the row this package's own verification concerns),
this row is corrected as part of this VR's ledger updates rather than left as a pure finding,
since it is the direct `FEAT-1100` row this verification concerns and the correction is a
one-line, unambiguous status-string fix with no judgment call involved.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| The shipped `T17.6` forces the Start-press/phase-transition collision only at the first (INTRO→BUILD) boundary, using the plain-boot transition frame recorded during the (a)/(b) run earlier in the same test function. The package's own Definition of Done and `FS-110`'s Acceptance Criterion 4 state the "no corruption" guarantee generally (any phase transition, not only the first), and `_emit_song_tick`'s logic is identical at every boundary (a single routine, not four separate code paths), so this is not evidence of a functional gap — but the shipped suite itself does not directly demonstrate the guarantee at the BUILD→PEAK or PEAK→BREAKDOWN boundaries. This run's own S1 scenario independently forced and confirmed clean collisions at both of those additional boundaries. | Low-Medium (a test-coverage gap, not a functional defect — the underlying routine is boundary-agnostic by construction and this run's own independent drive confirms the behavior holds at every boundary tested; but `T17.6` alone would not catch a defect that only manifested at a later-boundary collision, e.g. an off-by-one in a hypothetical future refactor that special-cased the first transition) | `08-code-implementation` (extend `T17.6`, or add a `T17.6b`, to force the collision at a second, later-cycle boundary using the same live-reconstruction methodology, the same rigor upgrade `VR-1090`'s own Finding 2 recommended for `T16.8`) |
| The package/spec (`IP-1100`'s own "Risks" field, `FS-110`'s "Open Questions" #2) name BUILD's `DENSITY_IDX` target as the specific, unresolved `OVERLOAD`-frequency risk worth checking empirically. This run's own measurement (S2, above) found BUILD (tempo=4, density=4) produces **0% `OVERLOAD`** over a 10,800-frame sample — statistically indistinguishable from the default preset's own 0%, i.e. the named risk does not materialize for BUILD as tuned. However, the *next* phase, PEAK (tempo=6, density=6), produces a materially non-trivial **21.0% `OVERLOAD`** rate over 7,200 frames — a real, measurable effect that neither the package doc nor `FS-110` separately flags (both only name BUILD). This is descriptive data, not a functional defect (bad-zone recovery handles `OVERLOAD` identically regardless of song-form phase, per `FR-1330`, confirmed above) — but it is exactly the kind of finding `09-content-review`'s musical judgment call (`FS-110`'s own Open Question 2: "is an occasional overload during [a high-energy phase] a *desirable* dramatic moment?") should weigh, now with real numbers rather than a hypothetical. | Low (informational/tuning — no functional or test-correctness impact; the mechanism behaves exactly as designed at every phase, this is a data point about which named phase actually reaches the threshold) | `09-content-review` (judge whether PEAK's 21% `OVERLOAD` rate reads as a desirable dramatic climax or an unwanted glitchy patch, per `FS-110`'s own Open Question 2 — this data was not previously available) |
| `docs/features/INDEX.md`'s `FEAT-1100`/`FS-110` row was stale ("not yet built") against the actual shipped/`VERIFIED` state. Corrected as part of this VR's ledger updates (see Scope audit) rather than left purely as a finding, since it is this package's own direct feature row. | Low (doc-coherence, corrected in-place) | N/A — fixed by this VR |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1100` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1100` row status updated to `VERIFIED`.
- `ROADMAP.md`: stage-08/09 rows updated — `IP-1100` now `VERIFIED` via this report; all 15
  shipped packages now `VERIFIED`.
- `docs/features/INDEX.md`: `FEAT-1100`/`FS-110` row updated from "not yet built" to reflect
  `IP-1100` `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
