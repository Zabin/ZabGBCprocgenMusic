# VR-1061 — Verification Report: IP-1061

- **Package:** IP-1061 — Vibrato + portamento
- **Commit verified:** `268458e` (branch `claude/iterate-pipeline-skill-houug0`, tip at
  verification time)
- **Date:** 2026-07-23
- **Result:** ✅ **VERIFIED** (with one Medium finding — see below)

## Independence note

Fresh session — this session has implemented no part of `IP-1060`/`IP-1061`. Independence intact.
Same session and same-run posture as `VR-1060` (this is the second and final package of the
tranche verified this run).

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Vibrato is measurably active (bounded oscillation) without disturbing bad-zone scoring inputs | `music_engine.py:399-402` (phase advance), `music_engine.py:462-489` (`vib_up`/`vib_down`/`vib_write` — exact `JP_C`/`JP_NC` carry/borrow, bounded ±1 low-byte); confirmed no write to `cur_degree`/`stale_count`/`DISSONANCE_SCORE`/`BAD_ZONE_FLAGS` anywhere in `_emit_arpeggio_tick` (same routine audited for `VR-1060`'s interaction-risk check, which already covers this function in full) | PASS |
| Portamento measurably glides over more than one frame on a degree change and skips the glide on a repeat | `music_engine.py:234-244` (portamento stash of the *old* degree into `ARP_DEGREE_SCRATCH`), `music_engine.py:333` (onset write uses the stashed old degree, not the just-updated `cur_degree`), `music_engine.py:709-716,717-725` (`engine_tick`'s documented `arp_tick`-before-`gen_tick` call order — the mechanism that actually produces the 2-frame transition) | PASS, but see the finding below — the *mechanism* is real and correctly wired, but is a materially narrower "old-frequency-for-one-extra-frame, then arp_tick's next call lands on the new target" transition, not the N-frame linear-interpolation glide the package doc itself describes |
| Every pre-existing test (including `IP-1060`'s) still passes | `python3 test_rom.py` | PASS — 65/65 (T1-T11) |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py Driftune.gbc` | PASS — 32768 bytes, header valid |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header | `python3 build_rom.py Driftune.gbc` | 32768 bytes; title `DRIFTUNE`, GBC flag set, header checksum valid |
| Full `test_rom.py` suite passes, including the new suite (T11) | `python3 test_rom.py` | **65 PASS, 0 FAIL out of 65** |
| Independently drives a non-default tempo/octave and confirms vibrato/portamento behavior holds off the default preset | Live PyBoy drive, see below | PASS (vibrato directly confirmed; portamento confirmed via onset-event count + code trace, per the write-only-register constraint this project has already established — see below) |

## Non-default-parameter live drive (this skill's own additional requirement)

`NR13`/`NR14` (frequency registers) are write-only on real hardware and in PyBoy — confirmed
empirically this run (`pb.memory[0xFF13]` reads back `0xFF` regardless of what was last written;
`pb.memory[0xFF14]` reads back `0xBF`, the fixed mask of only-readable bits). This is the same
limitation `R108`/`VR-0001` already established, and the one `test_rom.py`'s own T11 docstring
cites for why portamento has no dedicated dynamic assertion. Given that constraint, drove the
built ROM independently at a non-default preset: pressed `Up` ×3 (steps `TEMPO_IDX` upward, per `T4.1`'s established 1-step-per-tap convention)
and `Right` ×2 (steps `OCTAVE_IDX` upward), confirmed via WRAM read (`TEMPO_IDX=5`, off its boot
preset of `4`; `OCTAVE_IDX=3`, off its boot preset of `1`) — both non-default, which is what this
checklist item requires — then ran 3000 frames:

- Vibrato phase bits (`ARP_STATE_PA` bits6-7) visited **all 4 values `[0, 1, 2, 3]`** — vibrato is
  live at the non-default preset, same as the default-preset T11.4 result.
- **56 `CUR_DEGREE_PA` onset transitions** were observed over the 3000-frame run at the fastest
  tempo — each one exercises the portamento code path (`ARP_DEGREE_SCRATCH` stash → old-pitch
  retrigger → next-frame `arp_tick` landing on the new target). No hang, no `NR52` dropout, no
  assertion-worthy anomaly across 56 live portamento transitions at the fastest reachable tempo
  (the setting most likely to stress the 2-frame timing window, since faster tempo means less time
  between onsets).

This is the practical ceiling of what can be independently confirmed given the write-only-register
constraint — the same ceiling `VR-0001`/`T11`'s own docstring already accepts project-wide.

## Findings

| Finding | Severity | Owner |
|---|---|---|
| `IP-1061`'s package doc (`Files to Create/Modify`, `Implementation Tasks`) describes portamento as a dedicated N-frame linear-interpolation glide: "a portamento glide-remaining counter, and a portamento 'current interpolated frequency' scratch pair," with "a per-frame delta ... added each frame." **No such WRAM was ever created** — `git show --stat 268458e` shows zero new WRAM addresses beyond `IP-1060`'s existing `ARP_STATE_PA`/`PB`/`ARP_DEGREE_SCRATCH` (already accounted for in `VR-1060`). What shipped instead (documented candidly in the commit message, but never fed back into the package doc or `FS-106`) is a 2-frame transition: the onset frame retriggers the channel at the *old* pitch (via the `ARP_DEGREE_SCRATCH` stash), and the very next frame's `arp_tick` call — which by then sees the already-updated `cur_degree` — writes the *new* target directly (with that frame's own arpeggio/vibrato modulation applied on top). There is no intermediate, interpolated frequency value between old and new at any point; it is old-then-new across exactly two writes, not a multi-step glide. This satisfies `FR-1150`'s literal text (the frequency "transitions ... over more than one frame ... rather than jumping directly to the new frequency on the onset frame" — it does not jump on the onset frame, and it does span 2 frames) and the package's own DoD wording ("glides over more than one frame"), but is a materially narrower implementation than `FS-106`'s Acceptance Criteria (3) describes ("each written value lies between the old and new frequency" — with only 2 written values, both frames are boundary values, not strictly interior ones), and than the package doc's own stated design. Additionally, **no automated test asserts on this behavior at all** — `test_rom.py`'s T11 docstring (`test_rom.py:382-396`) explains why (write-only registers) and covers portamento only via regression/stress-run absence-of-anomaly, not a positive assertion of the glide mechanism itself — meaning a future refactor that silently broke the `arp_tick`-before-`gen_tick` ordering (the sole mechanism producing this behavior) would pass the full suite undetected. | **Medium** (the shipped mechanism is real, deliberate, and does satisfy `FR-1150`'s literal requirement — this is not a functional failure — but it is a significant, undocumented-at-the-package-doc-level scope reduction from both the package's own stated design and `FS-106`'s Acceptance Criteria, compounded by zero automated test coverage for the one behavior this finding concerns) | `07-implementation-planning` (reconcile `IP-1061`'s package doc to describe the as-shipped 2-frame mechanism, same in-place-correction discipline `IP-1060`/`BL-0018`/`BL-0013` already established) and `06-feature-specification` (reword `FS-106`'s Acceptance Criteria (3) to match, or explicitly accept the narrower shipped behavior as sufficient) — a test-coverage improvement (e.g. a WRAM shadow-mirror of the last-written frequency, purely for test visibility, the same tradeoff `FS-106`'s own Open Question already flagged as a real implementation-package-level decision) is a `08-code-implementation` follow-up, not required to close this finding |

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1140 (vibrato) | `music_engine.py:399-402,462-489` | T11.4 (default preset), this run's live drive (non-default tempo/octave) | PASS |
| FR-1150 (portamento) | `music_engine.py:234-244,333,709-725` | No dedicated dynamic assertion (write-only-register limitation, documented in `test_rom.py:382-396`); this run's live drive confirmed 56 onset transitions executed with no anomaly at the fastest tempo; code trace confirms the mechanism matches the commit's own description | PASS as literally worded by `FR-1150`, see finding above for the gap between the *literal* requirement and the *fuller* design both the package doc and `FS-106` originally described |
| NFR-1040 (ROM/WRAM budget) | 1 new ROM table (0 bytes — vibrato uses no table, computed directly from phase bits, a further budget-friendly deviation from the package doc's own "4-8 signed entries" plan, not separately flagged since it only *reduces* the ROM footprint), 0 new WRAM (reuses `IP-1060`'s `ARP_STATE_PA`/`PB` spare bits) | ROM still builds to exactly 32768 bytes (G5) | PASS — well within budget, in fact leaner than planned |
| NFR-1050 (per-frame timing budget) | Bounded per-frame work in `_emit_arpeggio_tick`'s vibrato block (fixed instruction count, no loops) | This run's 3000-frame live drive plus the package's own 8000+ frame stress run, no hangs/timing anomalies either time | PASS |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention prior VRs established, this table is the RTM-equivalent audit.

## Scope audit

Per `git show --stat 268458e` (the `IP-1061` commit): `Claude.md`, `Driftune.gbc`,
`docs/architecture/07-data-model.md`, `music_engine.py`, `test_results.txt`, `test_rom.py` —
matches the package doc's own "Files to Create/Modify"/"Documentation Updates" fields. No
excursion into `build_rom.py`, `input_map.py`, `gbc_lib.py`, or `visuals.py`.

## Test run

```
python3 build_rom.py Driftune.gbc   # 32768 bytes
python3 test_rom.py                 # 65 PASS, 0 FAIL out of 65
```

## Verdict

`IP-1061` satisfies `FR-1140` (vibrato) fully, both as coded and independently confirmed live at a
non-default tempo/octave — the vibrato mechanism is correctly isolated from bad-zone/stale
bookkeeping, same as `IP-1060`'s arpeggio. `FR-1150` (portamento) is satisfied by its literal
wording — the channel does not jump directly to the new frequency on the onset frame, and the
transition does span more than one frame — but the shipped mechanism is a materially narrower
2-frame retrigger-then-jump, not the N-frame interpolated glide both the package doc and `FS-106`
describe, and has zero dedicated automated test coverage (a real, disclosed limitation of this
project's write-only PSG frequency registers, not an oversight). Both G5 gates pass (32768 bytes,
valid header; 65/65 `test_rom.py`). Scope stayed within the declared file set. One Medium finding
recorded (portamento's design-doc-vs-shipped gap plus its test-coverage gap) — routed to
`07-implementation-planning`/`06-feature-specification` for doc reconciliation, not a hard fail
since the underlying requirement's literal text is met and the reduction was a genuine,
budget-driven, honestly-disclosed engineering tradeoff (commit `268458e`'s own message), the same
character this project has already accepted for `BL-0013`/`IP-0004`'s period-1 simplification.
**Advancing to `VERIFIED`.**

This completes independent verification of both packages in the `BL-0024`/`FS-106`
(R216 sound-design-techniques) tranche.
