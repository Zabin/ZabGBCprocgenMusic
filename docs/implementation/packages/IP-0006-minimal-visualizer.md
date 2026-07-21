# IP-0006 — Minimal visualizer

*Abbreviated package doc (`BL-0012`) — user-authorized MVP push, full FS-1xx backfill scheduled.*

| Field | Content |
|---|---|
| **ID / Feature(s)** | IP-0006 / FEAT-1040 (minimal scope) |
| **Traces to** | FR-1120, GDS-03 SS1/SS6 (visualizer deferred to this package), R205 (visualizer conventions) |
| **Scope** | New `visuals.py` (read-only consumer of engine state, per FR-1120's own write-scope rule — never writes a PSG register or engine-state field). `init_visuals`: 2 tiles (off/on, solid color 0 / solid color 3), 4 tilemap cells cleared, BG palette 0 set to a calm (blue/green) theme, LCD on (`LCDC=0x91`, BG tile data at `0x8000`, BG display on). `update_visuals`, called once per frame after `engine_tick`: each of the 4 tilemap cells shows tile 1 (on) or 0 (off) matching `NR52`'s corresponding channel-active bit; BG palette 0 is rewritten each frame to the calm or bad-zone (red) color set based on `BAD_ZONE_FLAGS` bit3. Template-based design per R205 SS5 (fixed tiles, cheap per-frame writes) rather than per-pixel procedural rendering. |
| **Explicit non-scope** | No GDS-08 (Presentation Architecture) has been formally authored — this package proceeds directly from R205's research grounding, per the user-authorized MVP pace exception (`BL-0012`). More elaborate visual states (distinct animation beyond a palette swap, tempo-synced motion) are unscheduled `feature`-type candidates. |
| **Test evidence** | `test_rom.py` T9 (3 checks): `LCDC` set correctly at boot; each indicator tile matches its own `NR52` bit at a point in time and continuously across a 300-frame sustained run. Full regression: **56/56**. |
| **G5 gate** | ✅ 32768 bytes, valid header; ✅ 56/56 |
| **Findings** | GDS-08 remains unauthored (`BL-0001`) — this package is evidence that R205's grounding was sufficient to implement against without it, but a proper GDS-08 pass would still be valuable before further visualizer work, per `BL-0001`'s existing disposition. |
