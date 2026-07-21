# Verification Reports — Index

Owned by `09-package-verification` — the only skill that writes `VERIFIED`.

[↑ Implementation index](../00-master-build-plan.md)

| VR | Package | Date | Result | Headline |
|---|---|---|---|---|
| [VR-0001](VR-0001-skeleton-and-single-channel-generation.md) | IP-0001 | 2026-07-21 | ✅ VERIFIED | Skeleton build chain + pulse-A generation + full input mapping + scoped reset; 32/32 tests, non-default tempo extremes independently re-driven. Same-session verification, user-accepted exception (not a standing waiver). |
| [VR-0002](VR-0002-pulse-b-and-wave-channel.md) | IP-0002 | 2026-07-21 | ✅ VERIFIED | Pulse B + wave channel generation (parameterized `_emit_channel_gen`, `CHANNELS` table); 60/60 tests, octave-floor edge case (`OCTAVE_IDX=0`) + half-rate reload independently re-driven live. Genuinely fresh session. |
| [VR-0003](VR-0003-noise-channel-and-density.md) | IP-0003 | 2026-07-21 | ✅ VERIFIED | Noise channel + Euclidean density wiring; 60/60 tests, mid-range density (`DENSITY_IDX=3`, k=5) independently driven live confirming monotonic scaling between (not just at) the suite's tested extremes. Genuinely fresh session. |
| [VR-0004](VR-0004-bad-zone-detection.md) | IP-0004 | 2026-07-21 | ✅ VERIFIED | Bad-zone detection (dissonance/stuck/overload/combined); 60/60 tests, non-default scale (`SCALE_IDX=3`, pentatonic) independently driven live. One new doc-coherence finding: `FR-1090` still names an unbuilt `HIST_PA/PB/WV` ring buffer — extends `BL-0013`'s existing scope up to the requirements layer. |
| [VR-0005](VR-0005-full-reset-scope.md) | IP-0005 | 2026-07-21 | ✅ VERIFIED | Full reset-to-preset (audit-only package, no new code); 60/60 tests, pulse B/wave/noise Select-reset coverage independently driven live, closing the `BL-0014` gap the package doc itself flagged. |
