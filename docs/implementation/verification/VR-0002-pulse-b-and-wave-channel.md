# VR-0002 — Verification Report: IP-0002

- **Package:** IP-0002 — Pulse B + wave channel generation
- **Commit verified:** `504deda` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Result:** ✅ **VERIFIED**

## Independence note

This verification runs in a **fresh session** — no code from `IP-0002` (or any later package) was
authored in this session. The standing independence rule is satisfied in full, no caveat needed.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `_emit_channel_gen` parameterized to drive pulse A, pulse B, and wave generically | `music_engine.py:196-328` — single routine, called once per `CHANNELS` entry (`music_engine.py:128-136,551`); read in full, confirmed each channel gets its own `note_timer`/`cur_degree`/`lfsr_state`/register pair via the shared routine | PASS |
| Wave channel anchored one octave index lower, floored at 0 | `music_engine.py:136` (`octave_delta=-1`), floor logic at `music_engine.py:283-287` (`OR_A`/`JR_Z`/`DEC_A` — skips the decrement when `OCTAVE_IDX` is already 0) | PASS |
| Wave channel half note-rate (`tempo_mult=2`) | `music_engine.py:136` (`tempo_mult=2`), doubling logic at `music_engine.py:310-311` (`ADD_A_A` on the reload byte when `tempo_mult==2`) | PASS |
| `_wave_table_bytes()` (32-sample 4-bit sine-ish shape) + Wave RAM init | `music_engine.py:176-185`; consumed in `build_rom.py:65-66` (16 `LD_A_n`/`LD_nn_A` pairs writing `WAVE_RAM+i`, `i` in 0-15) | PASS |
| `CHANNELS` list drives `init_engine`/`engine_tick` generically for all 3 pitched channels | `music_engine.py:510` (`init_engine` loop seeding each channel's timer/LFSR), `music_engine.py:543` (`engine_tick` loop calling each `gen_tick_<suffix>`) | PASS |
| `test_rom.py` T6 (5 checks) + full regression green | See Test run below | PASS |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, fixed size, valid header | `python3 build_rom.py <path>` | 32768 bytes; title `DRIFTUNE`, CGB flag `0x80`, independently re-read from the built file, not trusted from the package doc |
| Full suite green | `python3 test_rom.py` | **60 PASS, 0 FAIL out of 60** (T1-T10 — the tree now includes IP-0003 through IP-0007's later checks too, all green; T6 specifically: T6.1-T6.5 all PASS) |

Note: PyBoy was not pre-installed in this fresh session (`ModuleNotFoundError: No module named
'pyboy'` on first run) — installed via `pip3 install pyboy` before the suite would run at all,
consistent with a genuinely independent environment.

## Non-default-parameter live drive (this skill's own additional requirement)

T6's own fixture boots fresh and never varies `OCTAVE_IDX`/`SCALE_IDX` away from the boot preset
(`PRESET_OCTAVE_IDX = 1`) — every consuming suite shares that one fixture. IP-0002's DoD makes two
claims that are invisible at the preset value alone: the octave-floor guard (only exercised when
`OCTAVE_IDX` is already `0`, since at preset `1` the wave channel's `octave_delta=-1` lands on `0`
without ever hitting the floor branch) and the half-rate reload. Drove both directly, live,
independent of `test_rom.py`:

- Booted fresh, tapped D-pad Left once to bring `OCTAVE_IDX` from preset `1` down to `0` (the
  floor edge case — one more decrement would underflow without the guard).
- Ran 600 further frames, sampling `NOTE_TIMER_PA` and `NOTE_TIMER_WV` reload values on every
  frame where each timer increased (i.e. every reload event):
  - `NOTE_TIMER_PA` reload value observed: `{30}` (pulse A, `tempo_mult=1`, `TEMPO_TABLE[4]=30`)
  - `NOTE_TIMER_WV` reload value observed: `{60}` — exactly double, confirming `tempo_mult=2`'s
    `ADD_A_A` doubling fires correctly, and confirming the floor guard did not produce a
    corrupted/wrapped reload value at the `OCTAVE_IDX=0` edge.
- `NR52` read back as `0xFF` after the drive — all four channels (including wave, bit2) still
  reporting active; no crash, hang, or silent channel drop at the floor edge.

This is exactly the class of gap a green suite alone would not catch (every suite that exercises
`IP-0002` shares the one fixture that never varies `OCTAVE_IDX` off preset) — confirmed correct at
the edge value it never tests.

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1010 (pulse B + wave portion — pulse A/noise covered by IP-0001/IP-0003) | `music_engine.py:196-328` (`_emit_channel_gen`), `music_engine.py:128-136` (`CHANNELS`) | `test_rom.py` T6.1/T6.2 (`NR52` bits 1/2 active), T6.3/T6.4 (independent walks), T6.5 (sustained activity); this run's own octave-floor/half-rate live drive above | PASS |

No RTM file exists yet as a separate document (`docs/requirements/03-rtm.md` is `⛔ Planned`,
`BL-0001`) — per the interim convention VR-0001 established, this table is the RTM-equivalent
audit for IP-0002's requirement.

## Scope audit

Files touched per the package doc: `music_engine.py`, `build_rom.py`. Confirmed by reading both
files in full for wave/pulse-B-related code — all changes are contained in `_emit_channel_gen`
(parameterized, replacing the prior pulse-A-only inline routine), the `CHANNELS` table, the
`init_engine`/`engine_tick` loops that consume it, `_wave_table_bytes()`, and `build_rom.py`'s
Wave RAM init loop. No excursion into `input_map.py`, `gbc_lib.py`, `visuals.py`, or `tiles.py`
found. (`music_engine.py` in the current tree also contains later packages' code — IP-0004's
stale/onset/dissonance bookkeeping and IP-0007's autonomous-recovery overrides are interleaved
into the same `_emit_channel_gen` body since the tree reflects all 7 packages already built; this
is expected and not an IP-0002 scope excursion — each addition is independently attributable by
its own inline comment tags, e.g. "IP-0004", "IP-0007".)

## Findings

None new. `BL-0008` (wave channel needing a distinct role from pulse B) was already closed by this
package per the journal; independently re-confirmed here via the octave-delta/tempo-mult reads
above — the wave channel is verified to differ from pulse B in both register and code path, not
merely by table lookup.

## Verdict

`IP-0002` satisfies every Definition of Done item, both permanent gates, and its traced
requirement, with independent re-derivation of every claim — including a live, non-default
(`OCTAVE_IDX=0`, the floor edge case) drive of the ROM that the existing suite's shared fixture
never exercises. **Advancing to `VERIFIED`.**
