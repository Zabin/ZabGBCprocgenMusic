# Implementation Packages — Index

Owned by `07-implementation-planning` (authoring), `08-*` peers (execution), `09-package-verification` (VERIFIED status).

[↑ Implementation index](../00-master-build-plan.md)

| ID | Package | Status |
|---|---|---|
| IP-0001 | [Skeleton build chain + single-channel generation + headless harness bootstrap](IP-0001-skeleton-and-single-channel-generation.md) | VERIFIED ([VR-0001](../verification/VR-0001-skeleton-and-single-channel-generation.md)) |
| IP-0002 | [Pulse B + wave channel generation](IP-0002-pulse-b-and-wave-channel.md) | VERIFIED ([VR-0002](../verification/VR-0002-pulse-b-and-wave-channel.md), fresh-session independent verification) |
| IP-0003 | [Noise channel + density wiring](IP-0003-noise-channel-and-density.md) | VERIFIED ([VR-0003](../verification/VR-0003-noise-channel-and-density.md), fresh-session independent verification) |
| IP-0004 | [Bad-zone detection](IP-0004-bad-zone-detection.md) | VERIFIED ([VR-0004](../verification/VR-0004-bad-zone-detection.md), fresh-session independent verification) |
| IP-0005 | [Full reset-to-preset across all channels/bad-zone state](IP-0005-full-reset-scope.md) | VERIFIED ([VR-0005](../verification/VR-0005-full-reset-scope.md), fresh-session independent verification, closed `BL-0014`) |
| IP-0006 | [Minimal visualizer](IP-0006-minimal-visualizer.md) | VERIFIED ([VR-0006](../verification/VR-0006-minimal-visualizer.md), fresh-session independent verification — `BL-0016` filed) |
| IP-0007 | [Autonomous bad-zone avoidance/recovery + Select randomization](IP-0007-autonomous-recovery-and-randomize.md) | VERIFIED ([VR-0007](../verification/VR-0007-autonomous-recovery-and-randomize.md), fresh-session independent verification — `BL-0017` filed, Medium-High) |
| IP-9010 | [Channel-mix gating (remediation for `BL-0019`)](IP-9010-channel-mix-gating.md) | VERIFIED — [VR-9010](../verification/VR-9010-channel-mix-gating.md), 77/77 full-suite tests, independent non-default live drive (preset 5) confirmed |
| IP-9020 | [Overload threshold recalibration (remediation for `BL-0017`)](IP-9020-overload-threshold-recalibration.md) | VERIFIED — [VR-9020](../verification/VR-9020-overload-threshold-recalibration.md), 77/77 full-suite tests, independent non-default live drive (`TEMPO_IDX=5`/`DENSITY_IDX=6`) confirmed |
| IP-1060 | [Arpeggio + duty-cycle variation](IP-1060-arpeggio-and-duty-cycle.md) | VERIFIED ([VR-1060](../verification/VR-1060-arpeggio-and-duty-cycle.md), fresh-session independent verification — Low-Medium doc-coherence finding) |
| IP-1061 | [Vibrato + portamento](IP-1061-vibrato-and-portamento.md) | VERIFIED ([VR-1061](../verification/VR-1061-vibrato-and-portamento.md), fresh-session independent verification — two Low-Medium findings) |
| IP-1070 | [Combinable generation schemes (Scheme E)](IP-1070-combinable-generation-schemes.md) | VERIFIED — [VR-1070](../verification/VR-1070-combinable-generation-schemes.md), 85/85 tests, independent non-default live drive confirms the DoD; one Medium finding (pulse A/B Scheme E unreachable via any shipped preset) |
| IP-1080 | [Genre-aware style presets](IP-1080-genre-aware-style-presets.md) | VERIFIED — [VR-1080](../verification/VR-1080-genre-aware-style-presets.md), 93/93 full-suite tests, independent non-default/exact-frame/adversarial-random live drive confirms the DoD; one Medium finding (bad-zone-independence acceptance criterion states an absolute invariant the code only guarantees narrowly) |
| IP-1090 | [Motif recurrence via weighted variant selection](IP-1090-motif-recurrence-via-weighted-variant-selection.md) | VERIFIED — 102/102 full-suite tests (T1-T16); see [VR-1090](../verification/VR-1090-motif-recurrence-via-weighted-variant-selection.md) |
| IP-1100 | [Song-form via autonomous phase cycling](IP-1100-song-form-via-autonomous-phase-cycling.md) | VERIFIED 2026-07-26 — 112/112 full-suite tests (T1-T17); independently verified via [VR-1100](../verification/VR-1100-song-form-via-autonomous-phase-cycling.md) |
| IP-1110 | [Settings & control visibility](IP-1110-settings-and-control-visibility.md) | VERIFIED 2026-07-26 — 122/122 full-suite tests (T1-T18); independently verified via [VR-1110](../verification/VR-1110-settings-and-control-visibility.md); one disclosed, independently-reproduced finding (a self-healing one-frame display lag specifically on a Select-reset frame, see IP-1110's own package doc) |
| IP-9030 | [VBlank budget assertion (`BL-0069`) — re-scoped v2 2026-07-31, was *VRAM write-integrity detection*](IP-9030-vram-write-integrity-detection.md) | **READY**, authorization **NEEDS RE-CONFIRMATION**. v1 was `BLOCKED` when its own measurement falsified its premise (no VRAM write is dropped; PyBoy models no PPU-mode gating, so the planned `T19` could never fail). v2 asserts the real, measurable thing instead: `LY` at entry to `update_visuals` stays within 144-153. Blocking Report and superseded v1 scope both retained in the package doc. |
