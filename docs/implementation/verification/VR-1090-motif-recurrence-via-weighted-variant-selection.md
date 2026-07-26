# VR-1090 — Verification Report: IP-1090 (Motif Recurrence via Weighted Variant Selection, `BL-0010`)

## Package

- **Package:** [`IP-1090`](../packages/IP-1090-motif-recurrence-via-weighted-variant-selection.md)
  — extends Scheme E's `MOTIF_TABLE` from one fixed 8-entry row into `N_VARIANTS=4` rows of
  pre-composed motif variants, and adds the autonomous weighted-selection routine
  (`MOTIF_VARIANT_SELECTOR`) that draws which variant is active at each motif-cycle boundary
  (`FS-109`/`ADS-102`).
- **Commit verified:** `c67a105` ("feat(engine): IP-1090 -- motif recurrence via weighted
  variant selection (BL-0010)") — tip of tree at verification time was `0039748` (a
  journal-only entry recording `IP-1090` as `COMPLETE`, no functional changes on top).
- **Session independence:** genuinely fresh session — this session has no memory of authoring
  `IP-1090`; the implementing commit's own timestamp and the master build plan both attribute
  the work to a prior session. No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. Two
Medium, one Low-Medium, and one Low finding recorded (none blocks `VERIFIED`; see Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Motif data comprises 4 variants, row 0 identical to pre-`IP-1090` sequence | `MOTIF_TABLE` (`music_engine.py:284-289`): 4 rows of 8 bytes; row 0 = `[0,2,4,5,4,2,0,7]`, byte-identical to the pre-`IP-1090` shipped sequence. `N_VARIANTS = 4` (`:290`). `T16.1`/`T16.2` confirm pairwise distinctness and row-0 match. | Pass |
| At each motif-cycle-boundary frame, `MOTIF_VARIANT_IDX` is drawn via the weighted selector, no input required | `music_engine.py:493-523`: after the existing motif-step-advance arithmetic, `B` (new motif-step bits) is checked for zero (cycle wrap); only on that frame does the code step the channel's own `lfsr_state`, mask 2 bits, index `MOTIF_VARIANT_SELECTOR`, add the signed delta to `MOTIF_VARIANT_IDX`, and re-mask `AND 0x03`. No new joypad read anywhere in the diff (confirmed: `git show c67a105 --stat` shows `input_map.py` untouched). `T16.5` confirms `MOTIF_VARIANT_IDX` changes only on boundary frames, never mid-cycle. This run's own independent drive (S1, below) exercised a *guaranteed* boundary-frame collision scenario and found the same clean timing. | Pass |
| Draw measurably favors retention over switching across a long run | `MOTIF_VARIANT_SELECTOR = [0x00, 0x00, 0x00, 0x01]` (`:299`) — 3-of-4 retain, 1-of-4 advance, a designed 25% switch rate. `T16.6` (6000 frames, 11 boundary events) observed 0/11 switches — passes the suite's own `changes < boundaries` comparison, but see Finding 1 (statistical weakness of this specific comparison/sample size). This run's own independent 60,000-frame drive (see Test run, below) observed 117 boundaries / 23 switches ≈ 19.7% empirical switch rate — consistent with the designed 25% weighting and comfortably below 50%, a materially stronger confirmation of `FR-1290`. | Pass |
| With `MOTIF_VARIANT_IDX` held at 0, output is byte-identical to pre-`IP-1090` behavior | The variant-relative lookup (`music_engine.py:528-541`) computes `motif_table_base + MOTIF_VARIANT_IDX*8 + motif_step`; at `MOTIF_VARIANT_IDX=0` this reduces to `motif_table_base + motif_step`, the exact pre-`IP-1090` offset. `MOTIF_VARIANT_IDX` is zeroed in `init_engine` (`:1068`) on both boot and Select-reset, alongside `scheme_state`'s own zeroing (which resets the motif-step counter to 0 too) — so a fresh reset is at variant 0 until the first boundary. `T16.7` confirms every observed onset's degree matches `MOTIF_TABLE[variant*8+step]` exactly (excluding bad-zone-override frames, the same caveat `T14.3` already established). | Pass |
| A style change (`IP-1080`) landing on the same frame as a cycle boundary corrupts neither mechanism's state | `_emit_apply_style` (`music_engine.py:358-372`) touches only `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` — confirmed by reading its full body; no write to `scheme_state` or `MOTIF_VARIANT_IDX` exists anywhere in that routine. `T16.8` exercises repeated Start presses (every 47 frames) over 4000 frames and finds no corruption — **but this run independently determined that `T16.8`'s own chosen interval (47) never actually produces an exact-frame collision with a real motif-cycle boundary in this ROM's deterministic default-preset timing** (boundaries occur at frames 511, 1023, 1535, 2048, 2559, 3071, 3583 in this setup; no multiple of 47 lands on any of them, nearest miss is 6 frames off) — see Finding 2. This run's own independent drive (S1, below) constructed a *guaranteed* exact-frame collision (Start press scheduled on every recorded boundary frame) and confirmed no corruption of either mechanism under that stronger condition. | Pass |
| Every pre-existing test still passes | Full suite run this session: **102/102** (T1-T16 all green — see Test run below). | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. Verified size = 32768 via `wc -c`. `T1` (part of the 102/102 run) confirms header fields. | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 102/102, run this session, command `python3 test_rom.py`. | Pass |
| `09-package-verification` independently drives a non-default variant sequence (e.g. forcing several consecutive switch-draws) live and confirms the DoD holds beyond the new suite's own fixture | Standalone PyBoy script (not `test_rom.py`'s own fixtures): `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1090.py`. Rather than re-running the suite's own randomized draw and hoping to observe a switch, this run **forced the adversarial timing scenario the package/spec name explicitly as a real risk**: an exact-frame collision between a motif-cycle boundary and a `CHMIX_IDX` style change — see Test run (S0/S1/S2), below, for the three independent scenarios driven live, none of which the shipped suite's own fixtures exercise. | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1270` (fixed variant set, variant 0 matches shipped) | `MOTIF_TABLE` (`music_engine.py:284-290`) | `T16.1`, `T16.2` | Pass |
| `FR-1280` (weighted selection at cycle boundaries, no input) | `music_engine.py:493-523` (cycle-boundary detection + LFSR-driven draw) | `T16.4`, `T16.5`; this run's S1 (guaranteed boundary-collision drive) | Pass |
| `FR-1290` (weighting favors retention) | `MOTIF_VARIANT_SELECTOR = [0,0,0,1]` (`:299`) | `T16.6` (weak sample, 11 events — Finding 1); this run's independent 60,000-frame drive (117 events, 19.7% switch rate) | Pass |
| `FR-1300` (variant 0 held throughout reproduces pre-change behavior exactly) | Variant-relative offset reduces to original at idx=0 (`:528-541`); `init_engine` zeroes `MOTIF_VARIANT_IDX` (`:1068`) | `T16.2`, `T16.7` | Pass |
| `NFR-1100` (ROM/WRAM budget) | `MOTIF_TABLE` extended by 24 bytes, `MOTIF_VARIANT_SELECTOR` 4 bytes, `MOTIF_VARIANT_IDX` 1 WRAM byte | This run independently re-measured via `rom.pos`-instrumentation (`ADR-0002`'s own method): **3679 of 32768 bytes used, 29089 free** — a delta of exactly -182 bytes from `VR-1080`'s own measured 29271 free, matching the Master Build Plan's own claimed "-182 bytes (29089 free)" figure exactly. The ~150 bytes beyond the ~28 bytes of new data is the cycle-boundary/variant-selection SM83 code emitted once per pitched channel (3 channels) — a reasonable, non-negligible but still small fraction of the 29089-byte remaining budget. | Pass |
| `NFR-1110` (no new input control/WRAM control byte beyond the variant-index field) | `git show c67a105 --stat` confirms `input_map.py` is entirely untouched by this commit; only `music_engine.py` gained code, plus documentation files. | Confirmed by direct diff read | Pass |

No RTM file at FR-grain currently exists in this tree (same standing gap `VR-9010`/`VR-9020`/
`VR-1070`/`VR-1080` already noted — `docs/requirements/01-functional-requirements.md` is the
traceability source of record at FR grain). Traceability above is derived directly from that
document's FR text against the shipped code and tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes; header valid (`T1` confirms all header
  fields; this run additionally independently re-measured `rom.pos` = 3679, free = 29089 bytes,
  matching the package's/Master Build Plan's own claimed ROM-budget figure exactly).
- `python3 test_rom.py` → **102 PASS, 0 FAIL** out of 102 (full suite, T1-T16).
- Independent non-default/adversarial live drive (standalone script,
  `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1090.py`),
  built specifically to stress-test the exact interaction both `IP-1090`'s package doc and
  `FS-109` name as the real, flagged risk — a `CHMIX_IDX` style change landing on the exact same
  frame as a motif-cycle-boundary variant draw — more tightly than `T16.8`'s own fixture:
  - **S0** (empirical boundary recording): a clean pass with no Start presses, same setup `T16`
    uses (fresh boot, 6 Start-taps to `CHMIX_IDX` preset 6, Scheme E on the wave channel,
    default tempo/density), over 6000 frames, recorded the exact frames a motif cycle boundary
    occurs: `[511, 1023, 1535, 2048, 2559, 3071, 3583, 4095, ...]` (~512-frame period, matching
    the default preset's fixed Euclidean/tempo cadence — deterministic, not random). Cross-
    checking this list against `T16.8`'s own chosen interval (Start press every 47 frames, run
    for 4000 frames: presses at 0, 47, 94, ..., 3619) found **zero exact matches** — the nearest
    miss is 6 frames off (press at 517 vs. boundary at 511). This means `T16.8`, as shipped,
    never actually exercises the literal same-frame collision its own name/docstring claims to
    test, within its own 4000-frame window — recorded as Finding 2.
  - **S1** (guaranteed exact-frame collision): re-ran from a fresh boot with a real Start press
    scheduled on *every* frame recorded in S0's boundary list — forcing the exact collision
    `T16.8`'s interval choice happens to miss, on every single occurrence rather than
    probabilistically. Checked, on every frame: `MOTIF_VARIANT_IDX` stays in `range(N_VARIANTS)`,
    the motif-step counter stays in range 0-7, and on every collision frame the style fields
    (`TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS`) match `STYLE_TABLE[CHMIX_IDX]` exactly.
    **0 violations over 6000 frames with 11 guaranteed collisions** — neither mechanism's state
    was corrupted under the adversarial condition the package explicitly names as a risk.
  - **S2** (tight periodic sweep, intervals 2-12 frames — far tighter than `T16.8`'s 47):
    11 separate 3000-frame runs, one per interval, pressing Start every N frames for N in
    2..12 (multiple presses can land inside or adjacent to the same boundary window at these
    cadences). **0 violations across all 11 intervals** (`MOTIF_VARIANT_IDX` in-range at every
    frame, style fields matched `STYLE_TABLE[CHMIX_IDX]` on every press frame).
  - Additional independent confirmation (outside the standalone script, ad hoc REPL run): a
    60,000-frame drive of the same preset-6/Scheme-E setup with no Start presses, to get a
    larger statistical sample of the retention-vs-switch weighting than `T16.6`'s own 6000-frame/
    11-event sample: 117 boundary events, 23 switches (≈19.7%), consistent with the designed
    25% (`0x01`-of-4) weighting and comfortably below 50% — a materially stronger confirmation
    of `FR-1290` than the shipped suite's own thinly-sampled assertion (see Finding 1).
  - No hang, no crash, engine remained responsive throughout all of S0/S1/S2 and the 60,000-frame
    sample (well over 75,000 cumulative frames driven independently at non-default/adversarial
    combinations distinct from every shipped fixture).

## Scope audit

Package declared `music_engine.py` only for code. Actual diff (`git show c67a105 --stat`):
`Claude.md`, `ROADMAP.md`, `docs/architecture/07-data-model.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/pipeline/backlog.md`, `memory.md`, `music_engine.py`, `test_results.txt`, `test_rom.py`.

`music_engine.py` is the only production-code file touched — confirmed no excursion into
`input_map.py`, `visuals.py`, `gbc_lib.py`, or `build_rom.py`, exactly as declared. All other
touched files are documentation/ledger bookkeeping the package's own `Documentation Updates`
field named (`Claude.md`, `memory.md`, GDS-07, `docs/pipeline/backlog.md`) plus small,
accurate, in-the-spirit status-row updates (`ROADMAP.md`, the Master Build Plan, `packages/
INDEX.md`, `test_results.txt`) — same low-risk pattern `VR-1070`/`VR-1080` already found and
accepted for analogous undeclared-but-accurate edits. Not a functional excursion.

A build-hygiene gap found during this scope audit: the repo's *committed* `Driftune.gbc`
binary was **not** refreshed by `c67a105` (confirmed: `git show c67a105 --stat` lists no
`Driftune.gbc` entry) — it still reflects `IP-1080`'s own last-committed build (`20f5d2c`), not
the current `IP-1090` source. Rebuilding from source (`python3 build_rom.py Driftune.gbc`, as
this run and `test_rom.py` both do) produces the correct, current 32768-byte ROM — confirmed by
comparing a fresh build against the tracked file byte-for-byte (2999 of 32768 bytes differ,
concentrated where the extended `MOTIF_TABLE`/new `MOTIF_VARIANT_SELECTOR` data and the new
cycle-boundary code live). Every prior shipped package's own implementing commit (e.g. `IP-1080`'s
`20f5d2c`, confirmed via `VR-1080`'s own scope-audit stat listing `Driftune.gbc`) recommitted a
freshly built ROM alongside its source changes; `IP-1090`'s implementing commit is the first to
omit that step. Not a functional defect (the DoD's "ROM builds to 32768 bytes with valid header"
is satisfied by a fresh build, which this run performed and then reverted to avoid committing an
out-of-scope fix), but a real repo-hygiene gap — see Finding 4. This run intentionally did not
commit its own rebuilt `Driftune.gbc` over the stale one, since doing so would be fixing an
`IP-1090` omission rather than reporting it, outside this skill's own read-only-except-ledgers
scope.

One doc-coherence gap found during this scope audit, outside the implementing commit itself:
`docs/features/INDEX.md`'s `FEAT-1090`/`FS-109` row still reads "`READY`, G3-authorized... not
yet built," which is stale — the package is actually `COMPLETE` and shipped (102/102 tests).
This file is not part of `IP-1090`'s own declared `Documentation Updates` list and is outside
this skill's own authorized write scope (Master Build Plan + `packages/INDEX.md` + RTM only), so
it is filed as a finding rather than corrected here — see Finding 3.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| `T16.6`'s statistical confirmation of `FR-1290` ("weighting favors retention") uses only an 11-event sample (6000 frames at the default preset's own ~512-frame cycle period) and asserts `changes < boundaries` — a comparison that is nearly powerless: it only fails if literally every single boundary draw switches. A selector with a true 50% (non-retention-biased) switch rate would still pass this specific assertion the overwhelming majority of the time at n=11 (only failing on the ~1-in-2048 chance all 11 switch). This run's own independent 60,000-frame drive (117 events, 19.7% switch rate) does provide genuine confirmation the *actual* shipped weighting is retention-biased as designed — but that confirmation came from this VR's own extended sample, not from the shipped test's own methodology, which remains statistically weak as written. | Medium (a test-rigor gap, not a functional defect — the underlying selector value `[0,0,0,1]` is correct and the real behavior does favor retention at ~75/25, confirmed independently; but `T16.6` as shipped would not reliably catch a *wrong* weighting table if one were introduced by a future regression, since it would still very likely pass at that sample size) | `08-code-implementation` (extend `T16.6`'s run length and/or add a quantitative ratio-threshold assertion, e.g. "switch rate stays under 40%", not just "fewer than all", the same rigor upgrade this project applied to `VR-1080`'s own randomized-stress methodology) |
| `T16.8`'s docstring/intent is to confirm "repeated style changes... even landing on a motif-cycle boundary" never corrupt either mechanism, and it does exercise a real (if unintentional) adversarial timing pattern — but this run's own boundary-frame reconstruction (S0) proves the test's chosen interval (every 47 frames) never actually produces an exact-frame collision with a real motif-cycle-boundary frame within its own 4000-frame window (nearest miss: 6 frames). The test is exercising a related but weaker scenario (frequent, irregular, near-miss style changes) than the literal same-frame collision the package's own Definition of Done and this test's own name claim to cover. This VR's own S1 scenario (guaranteed collision, constructed from S0's own recorded boundary list) is what actually confirms the literal DoD claim — `T16.8` alone would not have caught a defect that only manifested on the exact collision frame. | Medium (a claim-precision gap in the shipped test, same class of finding `VR-1080`'s own Finding 1 recorded for `FS-108`'s bad-zone-independence wording — the underlying engine behavior is correct, confirmed independently by this run's S1/S2, but the shipped test's coverage claim overstates what its own fixture actually exercises) | `08-code-implementation` (either retime `T16.8`'s interval to a value verified in advance to land on a real boundary frame for the fixture's own preset/tempo/density combination, or — more robust against future tuning-value changes — reconstruct the boundary list live the way this VR's S0/S1 did and schedule the Start press directly against it) |
| `docs/features/INDEX.md`'s `FEAT-1090`/`FS-109` row still describes the package as "`READY`, G3-authorized... not yet built," which is stale against the actual `COMPLETE` status (102/102 tests, shipped in commit `c67a105`) that `packages/INDEX.md`, the Master Build Plan, and `ROADMAP.md` all correctly show. Not introduced by `IP-1090`'s own implementing commit's diff (which did not touch this file) and outside this skill's own authorized ledger-write scope, so filed rather than corrected here. | Low (doc-coherence only, no functional impact — a future reader of `docs/features/INDEX.md` alone would incorrectly believe `FS-109` is unbuilt) | `00-pipeline-manager` or a future `08` pass (a one-line status-row sync, same class of gap `VR-1070`/`VR-1080` found and filed rather than fixed in-place) |
| The committed `Driftune.gbc` binary in the repo was not refreshed by `IP-1090`'s own implementing commit (`c67a105` — confirmed via its own `--stat` output, no `Driftune.gbc` entry) and still reflects `IP-1080`'s last build. A fresh `python3 build_rom.py Driftune.gbc` from the current tree produces the correct, current ROM (verified byte-for-byte different from the tracked copy at 2999 bytes, concentrated at the new `MOTIF_TABLE`/`MOTIF_VARIANT_SELECTOR` data and cycle-boundary code) — so this is a repo-hygiene gap, not a functional defect, but it breaks the "clone and the shipped `.gbc` matches the shipped source" invariant every prior package's own implementing commit maintained (confirmed: `IP-1080`'s `20f5d2c` did commit a fresh `Driftune.gbc`, per `VR-1080`'s own scope-audit stat listing it). | Low-Medium (no functional/correctness impact once rebuilt, which every G5 gate in this project already requires before trusting the ROM; but a stale committed binary is a real trap for anyone who runs the tracked `.gbc` directly without rebuilding first) | `08-code-implementation` (recommit a freshly built `Driftune.gbc` alongside `IP-1090`'s source changes, restoring the "commit the build artifact with the source" convention every prior package followed) |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1090` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1090` row status updated to `VERIFIED`.
- `ROADMAP.md`: stage-08/09 rows updated — `IP-1090` now `VERIFIED` via this report; all 14
  shipped packages now `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
- `docs/pipeline/backlog.md`: `BL-0010` (the motif-recurrence half) and `BL-0042` (the concrete
  `N_VARIANTS`/weighting values) are left for `00-pipeline-manager`/a future triage pass to
  formally close now that `IP-1090` is `VERIFIED` — not edited directly by this report beyond
  what is named in Findings, per this skill's read-only-except-ledgers scope.
