# VR-1061 — Verification Report: IP-1061 (Vibrato + Portamento)

## Package

- **Package:** [`IP-1061`](../packages/IP-1061-vibrato-and-portamento.md) — Vibrato + portamento
- **Commit verified:** `268458e` (`IP-1061`'s own commit; tip of `music_engine.py` unchanged
  since)
- **Session independence:** genuinely fresh session — this session did not author `IP-1061`
  (built and self-tested in a prior session per journal run #23). No waiver needed.

## Result

**VERIFIED** — 0 failed checks against the Definition of Done or Verification Checklist. Two
findings recorded (neither blocks `VERIFIED`; see Findings) — both disclosed testability/scope
deviations from the package's original design, not defects.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Vibrato is measurably active (bounded oscillation) without disturbing bad-zone scoring inputs | `_emit_arpeggio_tick` (`music_engine.py:397-488`) applies a ±1 low-byte wobble to the frequency register every frame via carry-safe `JP_C`/`JP_NC` branching, phase-cycled through 4 states (`+1, none, -1, none`) — bounded, never accumulating. `CUR_DEGREE_*`/dissonance/stale scoring (`FR-1080`/`FR-1090`) read only the onset-time degree, never the vibrato-perturbed instantaneous register value — confirmed by reading `_emit_channel_gen`'s dissonance-scoring call sites, which use `cur_degree`/`D` (the pre-onset value), not the vibrato output. T11.4: vibrato phase cycles through all 4 values at default preset; independently re-driven at non-default preset (below) — same result. | Pass |
| Portamento measurably glides over more than one frame on a degree change and skips the glide on a repeat | **Not measurable via register readback** — `NR13`/`NR14` are write-only (established project-wide limitation, first documented at `IP-0001`/`VR-0001`). Verified by code review instead, per this suite's own disclosed convention (see `t11_arpeggio_vibrato_duty`'s docstring): on a degree-changing onset, `_emit_channel_gen`'s onset write (`music_engine.py:333`) uses `ARP_DEGREE_SCRATCH` (the *old*, pre-onset degree) when `portamento=True`, retriggering at the outgoing pitch; `engine_tick`'s call order (`arp_tick` before `gen_tick`, confirmed at `music_engine.py:710-723`) means the *next* frame's `arp_tick` call reads the by-then-updated `CUR_DEGREE` and writes the new target — a genuine, if minimal (exactly 2 frames: old-frequency-retrigger, then new-frequency), non-instant transition. On a same-degree onset, `ARP_DEGREE_SCRATCH == cur_degree`, so the "old" and "target" write are identical — the repeat case correctly produces no audible glide (not literally "skipped," but equivalent in effect, since old==new). Traced and confirmed correct by static reading of the actual emitted instruction sequence, not assumed from the Implementation Summary. | Pass (by code review, with the write-only-register caveat noted as a finding, not a defect) |
| Every pre-existing test (including `IP-1060`'s) still passes | Full suite run this session: **65/65** (T1-T11, all green). | Pass |
| ROM builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` → `Wrote Driftune.gbc: 32768 bytes`; T1.1-T1.5 pass. | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Confirmed above. | Pass |
| Full `test_rom.py` suite passes, including the new suite (G5) | 65/65, `python3 test_rom.py`. | Pass |
| Independent non-default tempo/octave drive confirms vibrato/portamento behavior off the default preset | Drove the built ROM live via a standalone PyBoy script: pressed `up`x3 (`TEMPO_IDX`: 4→7, the **maximum**, a realistic-high setting) and `right`x2 (`OCTAVE_IDX`: 1→3). Over the following 400 frames at this combination: vibrato phase (`ARP_STATE_PA` bits6-7) cycled through all 4 values `[0,1,2,3]`; arpeggio step also confirmed still live `[0,1,2,3]`. Portamento's onset-write logic (old-degree retrigger, arp_tick carry-forward) is tempo/octave-independent by construction — traced in the code, not tempo-gated — so this drive confirms the tempo/octave-sensitive half (vibrato) directly and confirms no interaction regression at the extreme tempo setting. Satisfies this project's standing tunable-parameter verification standard. | Pass |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| `FR-1140` (vibrato, must not affect dissonance/stale scoring) | `_emit_arpeggio_tick`'s ±1 wobble, applied after the base-note write, `cur_degree`-based scoring untouched | T11.4 + non-default live drive; scoring independence confirmed by code reading (no test directly asserts DISSONANCE_SCORE is unaffected by vibrato specifically, but T8's existing dissonance suite already passes unchanged with vibrato active, which is consistent) | Pass |
| `FR-1150` (portamento) | Old-degree onset retrigger + `arp_tick`-before-`gen_tick` carry-forward (`engine_tick`) | Code review only — no dynamic register-level test exists or can exist given write-only PSG registers (see Findings) | Pass, with disclosed testability caveat |
| `NFR-1040` (ROM/WRAM budget) | No new ROM table for vibrato (deliberately scoped down, inline ±1 rather than a lookup table — see Findings); zero new WRAM for portamento (reuses `ARP_DEGREE_SCRATCH`); ROM still exactly 32768 bytes | T1.1 | Pass |
| `NFR-1050` (per-frame timing budget) | Vibrato/portamento logic adds only a few unconditional instructions to the existing per-frame `arp_tick` path | 8200-frame stress run this session, no hang | Pass |

## Test run

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, header valid.
- `python3 test_rom.py` → **65 PASS, 0 FAIL** out of 65.
- Independent non-default live drive (`TEMPO_IDX=7` max, `OCTAVE_IDX=3`): vibrato phase and
  arpeggio step both confirmed cycling through all values off the default preset.
- 8200-frame stress run: no hang, `NR52` valid throughout.

## Scope audit

Package declared `music_engine.py` only; confirmed via `git show 268458e --stat` — no file
outside `music_engine.py` touched. No excursion.

## Findings

| Finding | Severity | Recommended owner |
|---|---|---|
| The package doc's own "Files to Create/Modify" (item 1) specifies a new `VIBRATO_OFFSETS` ROM table; the shipped implementation instead computes the ±1 wobble inline via phase-conditional branching (no table at all) — a deliberate, code-comment-documented scope reduction forced by the SM83 subset's lack of ADC/SBC for safe multi-byte arithmetic (explained in `_emit_arpeggio_tick`'s own docstring). Similarly, item 2's "portamento glide-remaining counter" and "current interpolated frequency scratch pair" were never built — portamento instead reuses the existing `arp_tick`/`gen_tick` ordering `IP-1060` already established, at zero extra WRAM cost. Both deviations are functionally sound and already documented in GDS-07 §3 and the pipeline journal (run #23), but the package doc itself was never updated to match — same drift pattern as `BL-0025` (`IP-1060`). No functional defect. | Low-Medium (doc-coherence only) | 07-implementation-planning (fold into the package doc the next time it's opened) |
| Portamento (`FR-1150`) has **no dynamic, automated test** confirming its glide behavior — the write-only nature of `NR13`/`NR14` makes this a hardware-level testability ceiling, not a shipped-code defect, and the project has an established, disclosed precedent for accepting this (`R108`/`VR-0001`'s frequency-register-readback limitation). However, `NFR-1020` ("every shipped behavior... has at least one headless PyBoy test") was scoped to `FR-1000` through `FR-1120` and was never extended to cover `FR-1130`-`FR-1170` when those were added — so `FR-1150` sits in a real gap: not covered by `NFR-1020`'s letter, and not actually testable by any assertion this suite could add without a new WRAM mirror. Recommend either (a) accepting and recording this explicitly as a named exception to `NFR-1020`'s coverage goal (parallel to `MSTR-001` C10's own "carry an honestly-named exception" pattern for research-to-code traceability), or (b) a future package adding a lightweight WRAM mirror of the currently-held frequency purely for testability, if portamento is ever revisited for its "one-guess placeholder" glide-length tuning anyway. | Low-Medium (test-coverage/requirements-scoping gap, not a functional risk — the underlying logic was independently traced and confirmed correct by this verification) | 04-requirements-engineering (clarify `NFR-1020`'s scope or record the exception) |

## Ledger updates

- `docs/implementation/00-master-build-plan.md`: `IP-1061` row status `COMPLETE` → `VERIFIED`.
- `docs/implementation/packages/INDEX.md`: `IP-1061` row status updated to `VERIFIED`.
- This VR added to `docs/implementation/verification/INDEX.md`.
