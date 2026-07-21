# IP-0002 — Pulse B + wave channel generation

*Abbreviated package doc (`BL-0012`) — user-authorized MVP push, full FS-1xx backfill scheduled.*

| Field | Content |
|---|---|
| **ID / Feature(s)** | IP-0002 / FEAT-1000 (pulse B + wave complete) |
| **Traces to** | FR-1010 (full), GDS-03 SS1-SS3, `BL-0008` (wave bass-role finding, now implemented), R207/R114 |
| **Scope** | `music_engine.py`: parameterized `_emit_channel_gen` (was pulse-A-only inline code) now drives pulse B (independent LFSR/timer/degree) and the wave channel (own LFSR/timer/degree, octave anchored one index lower + floored at 0, half note-rate via `tempo_mult=2`, reusing the pulse note tables — the wave frequency formula's own one-octave-lower quirk gives a further free bass drop, R108/R114). `_wave_table_bytes()` (sine-ish 32-sample shape) + Wave RAM init in `build_rom.py`. `CHANNELS` list now drives `init_engine`/`engine_tick` for all 3 pitched channels generically. |
| **Test evidence** | `test_rom.py` T6 (5 checks) + full regression (T1-T5 unchanged, 32/32); **37/37 total**. Independently drove `TEMPO_IDX` to both extremes during `IP-0001`'s own verification — not re-done here since the tempo mechanism itself didn't change, only which channels consume it. |
| **G5 gate** | ✅ 32768 bytes, valid header; ✅ 37/37 |
| **Findings** | None new — `BL-0008` closed by this implementation. |
