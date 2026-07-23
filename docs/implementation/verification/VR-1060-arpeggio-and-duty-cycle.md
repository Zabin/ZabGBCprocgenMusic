# VR-1060 — Verification Report: IP-1060

- **Package:** IP-1060 — Arpeggio + duty-cycle variation
- **Commit verified:** `268458e` (branch `claude/iterate-pipeline-skill-houug0`, tip at verification
  time — `music_engine.py`'s shared `_emit_arpeggio_tick`/`_emit_channel_gen` routines were later
  extended in place by `IP-1061`'s vibrato/portamento work; this report verifies IP-1060's own
  arpeggio/duty-cycle claims against the current tree, per this skill's standing rule that
  verification is always against the live tree, not a historical snapshot)
- **Date:** 2026-07-23
- **Result:** ✅ **VERIFIED**

## Independence note

Fresh session — this session has implemented no part of `IP-1060`/`IP-1061`. Independence intact.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Arpeggio audibly/measurably cycles frequency within a note's duration on at least pulse A | `music_engine.py:381-460` (`_emit_arpeggio_tick`, `ARPEGGIO_OFFSETS` period-4 table at `music_engine.py:154`); live drive below confirms the step index (bits4-5 of `ARP_STATE_PA`) visits all 4 values over a sustained run | PASS |
| Duty-cycle varies across onsets on at least pulse A | `music_engine.py:341-352` (onset-block write to `NR11` from `DUTY_BY_DEGREE[CUR_DEGREE mod 4]`), table at `music_engine.py:159` | PASS |
| Select-reset zeroes all new state | `music_engine.py:689-693` (`init_engine`: `arp_state` reloaded to `ARP_SUBTICK_RELOAD`, step/vibrato bits cleared by the same write since the whole byte is overwritten) | PASS (T11.3/T11.5) |
| Every pre-existing test still passes | `python3 test_rom.py` | PASS — 65/65 (T1-T11) |
| ROM still builds to 32768 bytes with a valid header | `python3 build_rom.py driftune.gbc` | PASS — 32768 bytes, header valid (T1.1-T1.5) |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header | `python3 build_rom.py driftune.gbc` | 32768 bytes; title `DRIFTUNE`, GBC flag set, header checksum valid |
| Full `test_rom.py` suite passes, including the new suite (T11) | `python3 test_rom.py` | **65 PASS, 0 FAIL out of 65** |
| Independently drives a non-default scale/octave and confirms arpeggio/duty-cycle behavior holds off the default preset | Live PyBoy drive, see below | PASS |

## Non-default-parameter live drive (this skill's own additional requirement)

The shared `test_rom.py` T11 fixture boots at the default preset (`SCALE_IDX=0`, `OCTAVE_IDX=1`
per `PRESET_SCALE_IDX`/`PRESET_OCTAVE_IDX`). Per this skill's standing rule (a green suite alone
isn't sufficient when every consuming fixture shares one fixed parameter value), drove the built
ROM independently: pressed `A` ×3 (steps `SCALE_IDX` to `1`) and `Right` ×2 (steps `OCTAVE_IDX` to
`3`), confirmed via direct WRAM read (`SCALE_IDX=1`, `OCTAVE_IDX=3` — both off their boot
defaults), then ran 4000 frames sampling `ARP_STATE_PA`'s step bits and `NR11`'s duty bits every
frame:

- Arpeggio step index (bits4-5 of `0xC01D`) visited **all 4 values `[0, 1, 2, 3]`** at
  `SCALE_IDX=1`/`OCTAVE_IDX=3` — chord-tone cycling is live off the default scale/octave, not an
  artifact of the specific note-table the default preset happens to select.
- `NR11` duty bits visited **all 4 values `[0x0, 0x40, 0x80, 0xc0]`** over the same run — duty
  variation likewise holds at the non-default preset.

This directly satisfies IP-1060's own Verification Checklist item, which names exactly this test.

## Interaction-risk audit (package's own named risk)

The package doc's Risks section requires that arpeggio's sub-tick frequency rewrites must not
touch `CUR_DEGREE_*`/`STALE_COUNT_*`/dissonance scoring — those must stay driven by the
note-onset degree only. Read `_emit_arpeggio_tick` (`music_engine.py:381-490`) in full: the only
reference to `cur_degree` is a single read at `music_engine.py:433` (`rom.LD_A_nn(cur_degree)`,
used to compute the effective arpeggiated pitch) — no write. No reference to any `stale_count`
address or `DISSONANCE_SCORE`/`BAD_ZONE_FLAGS` anywhere in the routine. Confirmed: arpeggio is
isolated from bad-zone/stale bookkeeping exactly as the package requires. PASS.

## Test run

```
python3 build_rom.py driftune.gbc   # 32768 bytes
python3 test_rom.py                 # 65 PASS, 0 FAIL out of 65
```

T11.1 (arpeggio step index cycles, default preset), T11.2 (duty-cycle varies, default preset),
T11.3 (Select resets arpeggio step to 0), T11.4/T11.5 (vibrato, `IP-1061`'s own scope — passing
incidentally since both packages share the tree, not re-audited here) all pass. No regression in
T1-T10.

## Scope audit

Per `git show --stat e967ff4` (the `IP-1060` commit): `music_engine.py`, `test_rom.py`,
`Claude.md`, `memory.md`, `docs/architecture/07-data-model.md`, `Driftune.gbc`, `test_results.txt`
— exactly the files the package doc's own "Files to Create/Modify" and "Documentation Updates"
name. No excursion into `build_rom.py`, `input_map.py`, `gbc_lib.py`, or `visuals.py`.

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1130 (arpeggio) | `music_engine.py:381-460` (`_emit_arpeggio_tick`), `music_engine.py:154-155` (`ARPEGGIO_OFFSETS`/`ARP_SUBTICK_RELOAD`) | T11.1 (default preset), this run's live drive (non-default scale/octave) | PASS |
| FR-1160 (duty-cycle variation) | `music_engine.py:341-352` (onset-block write), `music_engine.py:159` (`DUTY_BY_DEGREE`) | T11.2 (default preset), this run's live drive (non-default scale/octave) | PASS |
| NFR-1040 (ROM/WRAM budget) | 2 new ROM tables (8 bytes total: `ARPEGGIO_OFFSETS`×4 + `DUTY_BY_DEGREE`×4), 3 new WRAM bytes (`ARP_STATE_PA`/`PB`/`ARP_DEGREE_SCRATCH`, `music_engine.py:55-57`) | ROM still builds to exactly 32768 bytes (G5) | PASS — negligible, well within budget |
| NFR-1050 (per-frame timing budget) | Bounded per-frame work in `_emit_arpeggio_tick` (fixed instruction count, no loops) | 4000+ frame live drive this run plus the package's own 6000+ frame stress run, no hangs/timing anomalies observed either time | PASS (stress-run evidence, per `R101`'s "no gap yet" static-analysis conclusion — same standard `IP-0007`/`VR-0007` used) |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention prior VRs established, this table is the RTM-equivalent audit.

## Findings

| Finding | Severity | Owner |
|---|---|---|
| `IP-1060`'s package doc describes `ARPEGGIO_OFFSETS` as "3 entries" (e.g. `[0, 2, 4]`); the shipped table is 4 entries (`[0, 2, 4, 2]`), a deliberate period-4 up/down shape chosen (per the code's own comment, `music_engine.py:150-153`) to avoid needing a mod-3 counter on hardware with no division instruction. Musically and functionally sound, tested, and working — but the package doc's own prose text was never updated to match the as-shipped table shape. Same character as `BL-0013`/`BL-0016` (doc says something slightly different from what shipped, no functional defect). | Low (doc-coherence only, no functional impact — the 4-entry table is arguably a *better* fit for the SM83 opcode subset than the doc's own 3-entry suggestion, and R216 never mandated an exact count) | 07-implementation-planning (reword the package doc's "Files to Create/Modify" field's parenthetical example next time this package is touched) or fold into a general doc-coherence sweep alongside `BL-0013`/`BL-0016` |
| `FS-106`'s own Purpose/Title field frames this feature as giving "the three pitched channels (pulse A, pulse B, wave)" the new timbral behavior; `IP-1060`'s package doc explicitly scoped arpeggio+duty-cycle to pulse A/B only (wave keeps its plain bass role, a judgment call the package doc names and defends). This is a documented, deliberate scope narrowing, not an oversight — but `FS-106`'s top-level framing text was never updated to reflect it the way its own `System Behaviour` field's per-effect detail already implicitly allows (it doesn't force wave inclusion either). | Low (doc-coherence only; the narrower scope is sound — wave's bass role reads better without fast pitch cycling per `IP-1060`'s own stated rationale, and no requirement mandates wave-channel arpeggio) | 06-feature-specification (reword `FS-106`'s Title/Purpose next time the spec is touched, or accept as a standing footnote) |

## Verdict

`IP-1060` satisfies every item of its Definition of Done and Verification Checklist, as coded and
as independently driven at both the default preset (via the existing T11 suite) and a non-default
scale/octave (this run's own live drive, per this skill's standing requirement for
tunable-parameter packages). The package's own named interaction risk (arpeggio must not leak
into stale/dissonance bookkeeping) was independently audited and confirmed absent. Both G5 gates
pass (32768 bytes, valid header; 65/65 `test_rom.py`). Scope stayed within the declared file set.
Two Low-severity doc-coherence findings recorded (package-doc table-size wording,
FS-106 title/scope wording) — neither blocks `VERIFIED`, both fold into this project's existing
doc-coherence-finding pattern (`BL-0013`/`BL-0016`). **Advancing to `VERIFIED`.**
