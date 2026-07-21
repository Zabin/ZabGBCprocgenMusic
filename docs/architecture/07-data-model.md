# GDS-07 — Data Model (WRAM map)

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored, 2026-07-21
- **Grounds:** `music_engine.py`/`input_map.py`/`visuals.py` implementation, `test_rom.py` assertions.
- No SRAM section exists (MSTR-001 C2 — no save/battery commitment at v1).

All addresses below are proposals fixed at this architecture level so implementation and tests
can be written against the same addresses without renegotiating them mid-package — same
discipline as the reference project's GDS-07, restated for this project's own fields. A byte is
reserved even where a smaller range would fit, for headroom and alignment, matching that
project's own convention.

## §1 Engine parameter state (GDS-03 §3's indices)

| Addr | Name | Range | Meaning |
|---|---|---|---|
| `0xC000` | `TEMPO_IDX` | 0–7 | Index into the tempo preset table (D-pad Up/Down) |
| `0xC001` | `OCTAVE_IDX` | 0–7 | Index into the octave-range preset table (D-pad Left/Right) |
| `0xC002` | `SCALE_IDX` | 0–3 | Index into the scale/mode table (A) |
| `0xC003` | `DENSITY_IDX` | 0–7 | Index into the Euclidean-density preset table (B) |
| `0xC004` | `CHMIX_IDX` | 0–7 | Index into the channel-activity-mask preset table (Start) |

## §2 Bad-zone state (GDS-03 §4)

| Addr | Name | Meaning |
|---|---|---|
| `0xC005` | `BAD_ZONE_FLAGS` | bit0 `DISSONANT`, bit1 `STUCK`, bit2 `OVERLOAD`, bit3 `COMBINED` (the OR of the first three — GDS-03 §4d); bits 4-7 reserved |
| `0xC006` | `DISSONANCE_SCORE` | Current summed interval-class dissonance (0–45 theoretical max, §4a) |
| `0xC007` | `STALE_COUNT_PA` | Pulse-A repetition streak counter (§4b) |
| `0xC008` | `STALE_COUNT_PB` | Pulse-B repetition streak counter |
| `0xC009` | `STALE_COUNT_WV` | Wave-channel repetition streak counter |
| `0xC00A` | `ONSET_WINDOW_COUNT` | Note-onset events counted in the current overload window (§4c) |
| `0xC00B` | `ONSET_WINDOW_TICK_CTR` | Countdown of ticks remaining in the current overload window |

## §3 Per-channel generation state

| Addr | Name | Meaning |
|---|---|---|
| `0xC00C` | `NOTE_TIMER_PA` | Frames remaining on pulse A's current note |
| `0xC00D` | `NOTE_TIMER_PB` | Frames remaining on pulse B's current note |
| `0xC00E` | `NOTE_TIMER_WV` | Frames remaining on the wave channel's current note |
| `0xC00F` | `NOTE_TIMER_NZ` | Frames remaining on the noise channel's current hit |
| `0xC010` | `CUR_DEGREE_PA` | Pulse A's current scale-degree index (signed-offset encoding, engine-internal) |
| `0xC011` | `CUR_DEGREE_PB` | Pulse B's current scale-degree index |
| `0xC012` | `CUR_DEGREE_WV` | Wave channel's current scale-degree index |
| `0xC013` | `HIST_HEAD_PA` | Ring-buffer write head (0–7) into `HIST_PA` (§4) |
| `0xC014` | `HIST_HEAD_PB` | Ring-buffer write head into `HIST_PB` |
| `0xC015` | `HIST_HEAD_WV` | Ring-buffer write head into `HIST_WV` |

## §4 Repetition-detection history buffers (§4b's "last 8 notes")

| Range | Name | Size |
|---|---|---|
| `0xC020`-`0xC027` | `HIST_PA` | 8 bytes — pulse A's last 8 scale-degree values |
| `0xC028`-`0xC02F` | `HIST_PB` | 8 bytes — pulse B's |
| `0xC030`-`0xC037` | `HIST_WV` | 8 bytes — wave channel's |

## §5 Input state

| Addr | Name | Meaning |
|---|---|---|
| `0xC050` | `JOY_PREV` | Previous-frame joypad bitmap, active-HIGH — same bit layout the reference project's `memory.md` documents (`bit0=A bit1=B bit2=SELECT bit3=START bit4=RIGHT bit5=LEFT bit6=UP bit7=DOWN`), reused for consistency since it's a generic convention, not game-specific |
| `0xC051` | `JOY_CUR` | Current-frame joypad bitmap, same bit layout (added during `IP-0001` implementation — this is the reference project's own `read_joypad` output register, reused verbatim) |
| `0xC052` | `JOY_NEW` | `JOY_CUR AND NOT JOY_PREV` — rising-edge bits only, computed once per frame (added during `IP-0001`) |

Edge detection: `JOY_NEW = JOY_CUR AND NOT JOY_PREV`, computed once per frame in `input_map.py`'s
`read_joypad`; `JOY_PREV` is then updated to `JOY_CUR` for the next frame. This is the reused
mechanism the reference project already uses for its own menu-navigation edge-triggering
(`asm_game.py`'s `read_joypad` label).

## §8 Generation PRNG state (added during `IP-0001` implementation)

| Addr | Name | Meaning |
|---|---|---|
| `0xC016` | `LFSR_STATE` | 8-bit Galois LFSR state driving pseudo-random note-walk deltas (§4a below references its consumer). Seeded to a fixed non-zero value at boot/reset, so a fresh run is deterministic (MSTR-001 C6) — same seed each boot is a deliberate v1 simplification; a future package may expose seed variation (e.g. from `DIV` at power-on) as a backlog item, not decided here. |
| `0xC060` | `VBLANK_FLAG` | Set to 1 by the VBlank ISR, cleared by the main loop after processing one frame — the reference project's own main-loop-synchronization convention, reused verbatim. |

This section is appended rather than renumbered so `IP-0001`'s own commit diff against this file
stays a clean addition — a live doc, corrected in place per the pipeline's own discipline (`GDS-07`
must match the shipped bytes, not drift the way the reference project's `Claude.md` once did).

## §6 Headroom

Fields span `0xC000`-`0xC050` (81 bytes used of the block) with the next free 8-aligned address
at `0xC060` — ample headroom before any bank-switching question (a non-goal per MSTR-001 §4)
becomes relevant.

## §7 Reset-to-preset constants (GDS-03 §5)

The known-good preset values (which `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`
Select and power-on both load) are ROM-resident constants in `music_engine.py`, not WRAM —
exact values are a `04-requirements-engineering`/`06-feature-specification` data decision (GDS-03
§6), not fixed here; this section only reserves that they exist as a named constant block the
reset routine copies from.

**Gate:** closed 2026-07-21.
