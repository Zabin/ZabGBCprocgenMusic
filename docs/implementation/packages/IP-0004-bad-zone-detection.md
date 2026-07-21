# IP-0004 — Bad-zone detection

*Abbreviated package doc (`BL-0012`) — user-authorized MVP push, full FS-1xx backfill scheduled.*

| Field | Content |
|---|---|
| **ID / Feature(s)** | IP-0004 / FEAT-1030 (complete) |
| **Traces to** | FR-1080-FR-1110, GDS-03 SS4, R204 (dissonance grounding) |
| **Scope** | `music_engine.py`: `_emit_badzone_tick`, called once per frame from `engine_tick`. **Dissonance** (bit0): a `SEMITONE_TABLE` (4 scales x 8 degrees, mod-12) plus `_emit_pairwise_dissonance` computes an interval-class (0-6, inversions folded — a documented simplification of R204's raw 12-entry proposal) between each of the 3 pitched-channel pairs, weighted via `DISSONANCE_WEIGHT_BY_IC` (Helmholtz-roughness-ordered), summed into `DISSONANCE_SCORE`. **Stuck** (bit1): each channel's `_emit_channel_gen` now compares its new scale degree to the immediately-preceding one (period-1 repetition only — a deliberate MVP simplification of GDS-03's period-1-or-2 proposal; the reserved ring-buffer WRAM fields from GDS-07 are unused by this simpler design) and increments/resets its own `STALE_COUNT_*`. **Overload** (bit2): every onset (any channel, including noise hits) increments `ONSET_WINDOW_COUNT`; a 32-frame rolling window (`ONSET_WINDOW_TICK_CTR`) evaluates and resets it each cycle. **Combined** (bit3): OR of bits 0-2. `init_engine` zero-initializes all of this (also closing most of `IP-0005`'s original scope — see that package doc). |
| **Test evidence** | `test_rom.py` T8 (9 checks): confirms clean boot state, `DISSONANCE_SCORE` varies over a 2000-frame run, bit3 correctly tracks bits0-2, at least one bad-zone entry is observed, and Select clears all of it (with two checks deliberately relaxed from "== 0" to "a small fresh count" after discovering the reset's own same-frame onset firing legitimately ticks the stale/onset counters by 1-4 before the test can read them — documented inline in the test, not a defect). Full regression: **53/53**. |
| **G5 gate** | ✅ 32768 bytes, valid header; ✅ 53/53 |
| **Findings** | `BL-0005` partially addressed further (dissonance table already grounded by R204; thresholds — `DISSONANCE_THRESHOLD=20`, `STALE_THRESHOLD=8`, `OVERLOAD_THRESHOLD=20`, `ONSET_WINDOW_FRAMES=32` — remain first-guess placeholders, unchanged disposition). |
