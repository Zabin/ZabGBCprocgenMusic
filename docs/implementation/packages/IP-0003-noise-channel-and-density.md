# IP-0003 — Noise channel + density wiring

*Abbreviated package doc (`BL-0012`) — user-authorized MVP push, full FS-1xx backfill scheduled.*

| Field | Content |
|---|---|
| **ID / Feature(s)** | IP-0003 / FEAT-1000 (noise complete), FEAT-1010 (`DENSITY_IDX` now has a real consumer) |
| **Traces to** | FR-1010 (full — all 4 channels), GDS-03 SS3, R202 (Euclidean rhythm), R115 (noise implementation) |
| **Scope** | `music_engine.py`: `_emit_noise_gen` — a fixed 16-step grid, `DENSITY_IDX` selects `k` (onsets) from `DENSITY_K = [2,3,4,5,6,8,10,12]`, pattern precomputed per-`k` at build time via a simple bucket-boundary Euclidean approximation (`_euclidean_pattern`), stored as 16 unpacked 0/1 bytes per density level (128 bytes total — simplicity over ROM economy, deliberate for MVP). Percussive envelope (`NR42`=`0xF2`, fast decay), 15-bit ("hiss") width (`NR43`=`0x41`). `NOISE_STEP_TABLE` derives step duration from the existing tempo table (`/4`, 16th-note subdivision). |
| **Test evidence** | `test_rom.py` T7 — drives `DENSITY_IDX` to both extremes (0 and 7, non-default per the verification skill's own standard) and confirms onset rate scales monotonically (138 vs. 563 onset-frames/600 frames). Full regression: **44/44**. |
| **G5 gate** | ✅ 32768 bytes, valid header; ✅ 44/44 |
| **Findings** | None new. |
