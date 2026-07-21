# IP-0005 — Full reset-to-preset across all channels/bad-zone state

*Abbreviated package doc (`BL-0012`) — user-authorized MVP push, full FS-1xx backfill scheduled.*

| Field | Content |
|---|---|
| **ID / Feature(s)** | IP-0005 / FEAT-1020 (complete) |
| **Traces to** | FR-1070, GDS-03 SS5 |
| **Scope** | Largely delivered as a side effect of `IP-0002`/`IP-0003`/`IP-0004` each extending `init_engine` to zero/preset-initialize their own new fields at the point they introduced them (the `CHANNELS`-list loop covers pulse B/wave's degree/timer/LFSR; noise's step index/timer; bad-zone's flags/score/stale-counts/onset-window are explicitly zeroed). This package's own contribution: confirming that coverage is actually complete (audited every WRAM field `IP-0002`-`IP-0004` introduced against `init_engine`'s body — no gaps found) rather than assuming it. |
| **Test evidence** | `test_rom.py` T5 (pulse A + shared parameters, from `IP-0001`) and T8.6-T8.9 (bad-zone state) both exercise Select's reset coverage; no dedicated new test needed since no new behavior was added, only confirmed. |
| **G5 gate** | ✅ (unchanged — no code added this package) |
| **Findings** | None. Pulse B/wave/noise's own reset coverage is implicitly exercised by T6/T7's own drift-then-implicit-reset-on-next-boot pattern, not independently re-verified per-channel-post-Select in this pass — flagged as a light gap a future session could close with a dedicated per-channel Select-reset assertion (low priority, no evidence of an actual defect). |
