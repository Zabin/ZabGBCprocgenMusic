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
| `0xC004` | `CHMIX_IDX` | 0–7 | Index into `CHMIX_MASKS` (`music_engine.py`) — bits0-3 a real per-preset channel-activity mask consumed by `_emit_channel_gen`/`_emit_noise_gen` (**Added `IP-9010` 2026-07-25**, closing `BL-0019`); bits4-6 a per-channel generation-scheme select (pa/pb/wv, 0=Scheme W/1=Scheme E), consumed by `_emit_channel_gen`'s note-selection step (**Added `IP-1070` 2026-07-25**, closing `BL-0020`, per `ADR-0001`'s spare-bit reuse) |

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
| `0xC013` | `HIST_HEAD_PA` | Ring-buffer write head (0–7) into `HIST_PA` (§4) — **reserved, unused in the shipped ROM, see §4's own note (`BL-0013`)** |
| `0xC014` | `HIST_HEAD_PB` | Ring-buffer write head into `HIST_PB` — reserved, unused |
| `0xC015` | `HIST_HEAD_WV` | Ring-buffer write head into `HIST_WV` — reserved, unused |
| `0xC016` | `LFSR_STATE` | Pulse A's 8-bit Galois LFSR (full detail at §8 below — kept there for historical reasons, added during `IP-0001` before this §3 table existed in its current form; listed here too only so this table's address range reads contiguously) |
| `0xC017` | `LFSR_STATE_PB` | **Added `IP-0002`, documented here `BL-0018` (2026-07-22)** — pulse B's own independent LFSR, same mechanism as `0xC016`/§8 |
| `0xC018` | `LFSR_STATE_WV` | **Added `IP-0002`, documented here `BL-0018`** — the wave channel's own independent LFSR |
| `0xC019` | `NOISE_STEP_IDX` | **Added `IP-0003`, documented here `BL-0018`** — 0-15, the noise channel's current position in its 16-step Euclidean-gated pattern (§3's density mechanism, R202) |
| `0xC01A` | `SEMI_PA` | **Added `IP-0004`, documented here `BL-0018`** — pulse A's current note's semitone class (mod 12), scratch state recomputed every `badzone_tick` call (§4a) — not meaningful across frames, a working register more than persistent state |
| `0xC01B` | `SEMI_PB` | **Added `IP-0004`, documented here `BL-0018`** — pulse B's semitone-class scratch, same role as `SEMI_PA` |
| `0xC01C` | `SEMI_WV` | **Added `IP-0004`, documented here `BL-0018`** — wave channel's semitone-class scratch, same role |
| `0xC01D` | `ARP_STATE_PA` | **Added `IP-1060` (2026-07-22)**, **extended `IP-1061` (2026-07-22)** — pulse A's arpeggio + vibrato state, packed: bits0-3 sub-tick countdown, bits4-5 arpeggio step index (0-3, wraps via `AND 0x30`), bits6-7 vibrato phase (0-3, advances every frame via `ADD 0x40`, wraps out of the byte harmlessly) |
| `0xC01E` | `ARP_STATE_PB` | **Added `IP-1060`, extended `IP-1061`** — pulse B's arpeggio + vibrato state, same packing |
| `0xC01F` | `ARP_DEGREE_SCRATCH` | **Added `IP-1060`** — shared working storage for the arpeggio tick's effective-degree computation (pa/pb ticks run sequentially within a frame, never concurrently, so sharing one byte is safe — same convention as `SEMI_PA`/`PB`/`WV`'s own "not persisted across frames" scratch role) |
| `0xC038` | `MOTIF_STEP_PA` | **Added `IP-1070` (2026-07-25, `BL-0020`)** — pulse A's packed Scheme-E state: bits0-3 this channel's own Euclidean-pattern step (0-15, independent of the noise channel's `NOISE_STEP_IDX`), bits4-6 its current motif step (0-7); bit7 unused. Only advances when this channel's `CHMIX_MASKS` scheme-select bit (bit4) is set; stays at 0 while running Scheme W. |
| `0xC039` | `MOTIF_STEP_PB` | **Added `IP-1070`** — same packing/role as `MOTIF_STEP_PA`, pulse B's scheme-select bit is bit5 |
| `0xC03A` | `MOTIF_STEP_WV` | **Added `IP-1070`** — same packing/role, wave channel's scheme-select bit is bit6 |
| `0xC03B` | `DUTY_BIAS` | **Added `IP-1080` (2026-07-26, roadmap R5)** — a per-style duty-cycle timbre offset (`ADS-101`), added to the existing degree-derived duty-table index (`cur_degree & 0x03`) at `_emit_channel_gen`'s duty-write site, then re-masked (`AND 0x03`, wrap not clamp) — reuses the same masking idiom the index already used. Independent of `STYLE_TABLE`'s other 3 fields, which write directly to the already-existing `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` addresses rather than a new one. 0 for the default style/preset 0 (`FR-1260`'s non-regression). |

## §4 Repetition-detection history buffers (§4b's "last 8 notes")

| Range | Name | Size |
|---|---|---|
| `0xC020`-`0xC027` | `HIST_PA` | 8 bytes — pulse A's last 8 scale-degree values |
| `0xC028`-`0xC02F` | `HIST_PB` | 8 bytes — pulse B's |
| `0xC030`-`0xC037` | `HIST_WV` | 8 bytes — wave channel's |

**Reconciled 2026-07-22 (`BL-0013`), matching GDS-03 §4b's own reconciliation note**: these three
ring buffers (and their `HIST_HEAD_*` write-head pointers, §3) are reserved but **genuinely unused
in the shipped ROM** — `IP-0004`'s stale/repetition detection is period-1 only (compares only the
immediately-preceding degree, no buffer needed) rather than the period-1-or-2 design this range
was reserved for. Confirmed unused by grep across `music_engine.py`/`build_rom.py`/`input_map.py`/
`visuals.py` (`10-integration-review`'s Foundation-bucket report). The range stays reserved as a
valid v2 upgrade path (GDS-03 §4b) — not reclaimed for other use, since reclaiming it would create
a real conflict if the period-1-or-2 design is ever adopted later.

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
| `0xC016` | `LFSR_STATE` | 8-bit Galois LFSR state driving pseudo-random note-walk deltas (§4a below references its consumer). **Updated 2026-07-22, drift fix**: originally seeded to a fixed non-zero value at boot/reset (this row's own text used to say so, framing `DIV`-based seed variation as an undecided future backlog item) — `IP-0007` has since implemented exactly that: each channel's LFSR (this one and its `0xC017`/`0xC018` siblings) is reseeded from the `DIV` register XORed with a fixed per-channel constant on both boot and Select, zero-guarded (`music_engine.py:514-523`), independently verified `VR-0007`. The "same seed each boot" simplification this row described is **no longer true** — this was a stale statement this consistency pass caught, not a new decision. |
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
