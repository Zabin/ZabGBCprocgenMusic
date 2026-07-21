# Verification Reports — Index

Owned by `09-package-verification` — the only skill that writes `VERIFIED`.

[↑ Implementation index](../00-master-build-plan.md)

| VR | Package | Date | Result | Headline |
|---|---|---|---|---|
| [VR-0001](VR-0001-skeleton-and-single-channel-generation.md) | IP-0001 | 2026-07-21 | ✅ VERIFIED | Skeleton build chain + pulse-A generation + full input mapping + scoped reset; 32/32 tests, non-default tempo extremes independently re-driven. Same-session verification, user-accepted exception (not a standing waiver). |
| [VR-0002](VR-0002-pulse-b-and-wave-channel.md) | IP-0002 | 2026-07-21 | ✅ VERIFIED | Pulse B + wave channel generation (parameterized `_emit_channel_gen`, `CHANNELS` table); 60/60 tests, octave-floor edge case (`OCTAVE_IDX=0`) + half-rate reload independently re-driven live. Genuinely fresh session. |
