# VR-1070 — Verification Report: IP-1070 (Combinable Generation Schemes, `BL-0020`)

## Package

- **Package:** [`IP-1070`](../packages/IP-1070-combinable-generation-schemes.md) — Combinable
  generation schemes (Scheme E)
- **Commit verified:** `ed00ba3` (IP-1070's own implementation commit; tip of tree at
  verification time was `5fecf48`, the journal-only run #49 entry, no functional changes on top)
- **Session independence:** genuinely fresh session — this session did not author `IP-1070`
  (built and self-tested in an earlier session today, per `docs/pipeline/pipeline-journal.md` run
  #49 / commit `ed00ba3`). No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. Two
findings recorded (Medium, Low — neither blocks `VERIFIED`; see Findings).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| A pitched channel assigned Scheme E audibly/measurably cycles through a fixed, repeating motif rather than free-drifting | `MOTIF_TABLE = [0, 2, 4, 5, 4, 2, 0, 7]` (`music_engine.py:236`), consumed in `_emit_channel_gen`'s Scheme-E branch (`:398-420`) — on a pattern-hit onset, the packed `scheme_state`'s motif-step nibble advances mod 8 and `MOTIF_TABLE[motif_step]` is looked up as the new absolute degree target. `test_rom.py` T14.2/T14.3 confirm all 8 motif-step positions are reached and the resulting degree sequence stays within the motif's value set; independently re-confirmed at a non-default density (this run's S1.2/S1.3, below). | Pass |
| Its onset timing is Euclidean-pattern-gated rather than fixed-interval | Scheme-E branch (`:370-396`) advances a per-channel Euclidean step (bits0-3 of `scheme_state`, independent of the noise channel's own `NOISE_STEP_IDX`) and looks up `noise_pattern_table[DENSITY_IDX*16 + step]` — the same table `_emit_noise_gen` already emits/consumes, keyed identically. T14.1 confirms all 16 step positions are reached at `DENSITY_IDX=0` (T14's only density); this run's S1.1/S1.4 (below) independently confirm both full step coverage AND that the actual onset rate at `DENSITY_IDX=5` (`k=8`) matches the predicted `k/n=0.500` (497/995 observed transitions ≈ 0.499) — a density T14 never exercises. | Pass |
| A channel switch (via `CHMIX_IDX`) takes effect at the next onset, not mid-note | `_emit_channel_gen` re-reads `CHMIX_MASKS[CHMIX_IDX]`'s scheme bit only at the top of the note-selection step (`:343-350`), which only runs once `NOTE_TIMER_*` has already counted down to 0 for that channel — an in-flight note (`NOTE_TIMER_WV > 0`) cannot re-enter this code until it naturally expires. T14 does not test this transition edge directly (its own fixture reaches preset 6 from a fresh boot, so no channel is ever mid-note under the old scheme when the switch happens). This run's S2 scenario (below) independently drove exactly this edge case and confirmed it holds. | Pass |
| Bad-zone detection/recovery applies identically regardless of scheme | The dissonant-pull/stuck-force override block (`:431-461`) sits strictly *after* the `gt_delta_ready_{suffix}` label both the Scheme-W (LFSR-delta) and Scheme-E (motif-target-delta) paths converge on — it operates on register `B` (the pending signed delta) before that delta is added to `cur_degree`, identically regardless of which path produced `B`. T14.5/T14.6 confirm bad-zone entry/recovery with Scheme E active at default tempo/density; this run's S1.9/S1.10 independently re-confirm the same at a different (tempo=6/density=5) combination. Additionally: this run's raw-state trace (frame-level debug) directly observed the override actually firing and overriding a Scheme-E-computed motif target (dissonant flag set, degree pulled to/held at tonic 0 instead of the motif's next value) — visible, working composition, not just passing assertions. | Pass |
| Select resets all new WRAM | `init_engine` (`:937-939`) zeroes each channel's `scheme_state` on both boot and Select-reset (confirmed `init_engine` is the Select-reset target via `input_map.py:68`'s `CALL('init_engine')`). T14.7 confirms `MOTIF_STEP_WV` resets to 0 on the exact reset frame. | Pass |
| Every pre-existing test still passes | Full suite run this session: **85/85** (T1-T14 all green — see Test run below). | Pass |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`. Verified size=32768, title=`DRIFTUNE`, CGB flag=`0x80`, checksum byte=`0x72`, cartridge-type byte (`0x147`)=`0x00` (ROM ONLY, no MBC/bank-switching — confirms `NFR-1060`'s "no bank-switching change" holds), ROM-size byte (`0x148`)=`0x00` (32KB, single bank). | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 85/85, run this session, command `python3 test_rom.py`. | Pass |
| `09-package-verification` independently drives a non-default, realistic scheme-assignment combination (e.g. Scheme E on wave only, Scheme W on pulse A/B) live and confirms the DoD holds off whatever single fixture the new suite happens to use | Read `CHMIX_MASKS` directly (`music_engine.py:206-215`): **preset 6 is the only preset in the shipped table with any scheme-select bit (4-6) set at all** — it is also T14's own fixture. Since no other preset offers a genuinely different scheme *assignment* to drive, this run instead independently drove preset 6 in combination with two OTHER non-default parameters T14 never varies (`DENSITY_IDX=5` instead of T14's `0`, `TEMPO_IDX=6` instead of T14's default `4`) via a standalone PyBoy script (not `test_rom.py`'s own fixtures), plus a second, structurally different scenario T14 doesn't test at all (a live mid-note `CHMIX_IDX` switch from preset 5, Scheme W, to preset 6, Scheme E, testing `FR-1190`'s "next onset, not mid-note" edge directly). All 18 independent checks passed (after fixing one self-inflicted test-script bug, see Findings). Script: `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1070.py` (full output recorded in this run's transcript). | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1180` (scheme-select bit determines strategy) | `CHANNELS`' `scheme_bit` field (pa=4, pb=5, wv=6, `music_engine.py:172-182`), tested via `BIT_b_A(scheme_bit)` in `_emit_channel_gen` (`:349`) | T14.1-T14.4 (wave on Scheme E, pulse A regression); this run's S1.5-S1.8 (pulse A/B unaffected at a different combination) | Pass |
| `FR-1190` (scheme switch takes effect at next onset) | Scheme bit re-read only at note-timer expiry (`:343-350`), same "next onset, not mid-note" contract `IP-9010` already established for channel-activity gating | Not directly tested by T14 (fixture never switches mid-note). **This run's S2 scenario independently drove and confirmed this edge case** (mid-note preset-5→6 switch; `CUR_DEGREE_WV`/`MOTIF_STEP_WV` provably unchanged for the remainder of the in-flight note, Scheme E state begins advancing only once the next onset actually fires) | Pass |
| `FR-1200` (Scheme E onset timing reuses the Euclidean-pattern mechanism) | `:370-396`, reuses `noise_pattern_table`/`DENSITY_IDX` exactly as `_emit_noise_gen` keys it | T14.1 (step coverage at `DENSITY_IDX=0`); this run's S1.1/S1.4 independently confirm both coverage and a rate match (`k/n`) at `DENSITY_IDX=5` (`k=8`), a density T14 never drives | Pass |
| `FR-1210` (Scheme E pitch selection via a fixed motif) | `MOTIF_TABLE` (`:236`) + `:398-420` | T14.2/T14.3; this run's S1.2/S1.3 at a different combination | Pass |
| `FR-1220` (bad-zone detection/recovery is scheme-agnostic) | Override block (`:431-461`) sits after the Scheme-W/Scheme-E branch join, operates on the shared `B` register regardless of origin | T14.5/T14.6 (default tempo/density); this run's S1.9/S1.10 (tempo=6/density=5) plus a direct frame-level observation of the override overriding a Scheme-E motif target | Pass |
| `NFR-1060` (ROM/WRAM budget) | `MOTIF_TABLE` (8 bytes, not the package doc's originally-estimated 32 — see Findings) + 3 WRAM bytes (`0xC038`-`0xC03A`) | ROM builds to exactly 32768 bytes (unchanged total, same single 32KB bank, cartridge-type `0x00`/ROM-size `0x00` confirmed — no bank-switching introduced) | Pass |
| `NFR-1070` (no new WRAM control byte/input control) | Scheme selection is derived from the already-resident `CHMIX_MASKS[CHMIX_IDX]` read each tick (`:344-349`), no new control byte written by `input_map.py` (confirmed: `input_map.py` diff in commit `ed00ba3` is empty — `git show ed00ba3 --stat` lists no `input_map.py` change) | Implicit in the scope audit (`input_map.py` untouched) | Pass |

No RTM file at FR-grain currently exists in this tree (same standing gap `VR-9010`/`VR-9020`/
`VR-1060`/`VR-1061` already noted — `docs/requirements/01-functional-requirements.md` is the
traceability source of record at FR grain). Traceability above is derived directly from that
document's FR text against the shipped code and tests.

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, header valid (T1 confirms all header
  fields; this run additionally spot-checked cartridge-type/ROM-size bytes directly).
- `python3 test_rom.py` → **85 PASS, 0 FAIL** out of 85 (full suite, T1-T14).
- Independent non-default live drive (standalone script,
  `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/ec7a8104-2c55-5583-ac56-4ccd7155cd3c/scratchpad/drive_ip1070.py`):
  - **Scenario 1** (`DENSITY_IDX=5`, `TEMPO_IDX=6`, `CHMIX_IDX=6` — wave on Scheme E, pulse A/B
    on Scheme W, a combination T14 never drives): over 6000 independently-driven frames, the wave
    channel's Euclidean step visited all 16 positions, its motif step visited all 8 positions,
    its degree sequence stayed within `{0,2,4,5,7}` (the motif's value set) or bad-zone-reachable
    values; the onset (motif-advance) rate was 497/995 ≈ 0.499, matching the Euclidean-pattern
    prediction for `k=8, n=16` (0.500) almost exactly — directly confirming `FR-1200`'s "reuses
    the same mechanism" claim at a density T14 never exercises (`k=2` only). Pulse A/B continued
    their independent LFSR walks unaffected and never advanced their own `MOTIF_STEP_*` bytes.
    Over a further 6000-frame drive at this same combination, the engine entered a bad-zone state
    and autonomously recovered from it, with Scheme E active throughout.
  - **Scenario 2** (`FR-1190` mid-note switch edge, not tested by T14 at all): started at preset
    5 (wave+noise active, wave on Scheme W), let a wave note begin, mid-note stepped `CHMIX_IDX`
    to preset 6 (Scheme E) — `CUR_DEGREE_WV` and `MOTIF_STEP_WV` were confirmed unchanged for the
    remaining 55 frames of the in-flight note, then `MOTIF_STEP_WV` began advancing (Scheme E
    took over) exactly once the next onset fired.
  - One self-inflicted test-script bug was found and fixed during this drive (see Findings) —
    the underlying engine behavior was correct throughout; only the independent script's initial
    frame-attribution logic was wrong.
- 8200-frame stress run: folded into Scenario 1's 6000+6000-frame drive above (12000+ frames
  total at a non-default, realistic-high combination) — no hang, engine remained responsive
  throughout.

## Scope audit

Package declared `music_engine.py` only for code, plus `Claude.md`/`memory.md`/
`docs/pipeline/backlog.md`/GDS-07 for documentation. Actual diff (`git show ed00ba3 --stat`):
`Claude.md`, `Driftune.gbc`, `ROADMAP.md`, `docs/architecture/07-data-model.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/pipeline/backlog.md`, `memory.md`, `music_engine.py`, `test_results.txt`, `test_rom.py`.
`input_map.py` and `build_rom.py` are untouched, matching the package's own claim that neither
needed changes (confirmed directly: no diff hunk against either file in `ed00ba3`).

One file outside the package's declared `Documentation Updates` list: `ROADMAP.md` (a one-line
status-row update, same low-risk pattern `VR-9010` already found and accepted for
`docs/architecture/07-data-model.md`'s own undeclared-but-accurate edit). Not a functional
excursion — flagged as a minor scope note only (see Findings).

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| The shipped `CHMIX_MASKS` table (`music_engine.py:206-215`) sets a scheme-select bit (bits 4-6) on exactly one preset (6 — wave only). Pulse A (bit4) and pulse B (bit5) scheme-select bits are fully wired in code (`CHANNELS` tuple, `_emit_channel_gen`'s scheme branch, `init_engine`'s reset path all correctly parameterize and reset `MOTIF_STEP_PA`/`PB` identically to `MOTIF_STEP_WV`) but are **unreachable via any shipped preset** — no `CHMIX_IDX` value ever sets bit4 or bit5. This run independently confirmed the pulse A/B code path itself is correct by other means (regression checks S1.7/S1.8, and by code-reading — the branch is byte-for-byte parameterized the same way as the wave channel's, differing only in which bit/address is threaded through), so this is not a functional defect in the *mechanism*, but it does mean `BL-0020`'s original "solo or in combination" ask is only partially realized in the shipped *data*: a listener can never actually hear pulse A or pulse B running Scheme E, nor hear more than one channel running Scheme E simultaneously, through any preset Start currently cycles to. The package's own Risks section flagged "audible-contrast risk" as a `09-content-review` concern but did not flag this specific reachability gap. | Medium (a requirements-adjacent capability — combining/soloing Scheme E across multiple channels — is code-complete but has zero data-level reachability; no crash/correctness risk, but a real gap between `BL-0020`'s stated intent and what the shipped preset table actually lets a listener reach) | 00-intake (file as a new backlog entry recommending either a `08-content-authoring` package to add 1-2 more `CHMIX_MASKS` presets exercising pulse A/B Scheme E and/or multi-channel Scheme E combinations, or an explicit accept-as-is disposition if a single wave-only example is judged sufficient for this increment) |
| This run's own first attempt at the independent non-default live drive (Scenario 1) contained a test-script bug: it attempted to attribute each onset to the Euclidean-pattern step observed *after* a step-nibble transition, which does not reliably align with the exact frame the resulting degree-write becomes visible in PyBoy's memory array (likely because a bad-zone override can leave a motif-selected onset's degree unchanged from the prior value, and/or genuine one-frame read-timing effects around interrupt-driven onset processing) — this produced a false-positive "mismatch" on every odd step before being replaced with a rate-based check (motif-advances / euclid-advances vs. `k/n`), which passed cleanly (0.499 vs. predicted 0.500). Root-caused via targeted frame-by-frame instrumentation before concluding it was a test-methodology issue, not an engine defect. Recorded here for the record since a future verifier attempting the same positional-correlation approach would hit the same false alarm. | Low (verification-methodology note only; no engine defect, self-corrected within this run, evidence attached) | 09-package-verification (informational — future verifiers driving Scheme E's onset timing at non-default densities should use a rate-based check, not per-step positional attribution, unless first confirming exact frame-level synchronization empirically) |
| `ROADMAP.md` was updated by this package's commit (`ed00ba3`) even though the package's own `Documentation Updates` field does not name it (same low-risk pattern `VR-9010` already accepted for an analogous undeclared-but-accurate `docs/architecture/07-data-model.md` edit). | Low (small, accurate, in-the-spirit doc-coherence addition — not a functional or scope-risk excursion) | 07-implementation-planning (note the pattern for future packages: `ROADMAP.md`'s stage-07/08 status rows are routinely touched alongside the Master Build Plan/packages INDEX and could be named explicitly in the template) |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1070` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1070` row status updated to `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
- `docs/pipeline/backlog.md`: `BL-0020` "Run" note appended with this verification's outcome
  (Status left as `IN PIPELINE`, per this skill's scope — status flip to `DONE` is the pipeline
  manager's job).
