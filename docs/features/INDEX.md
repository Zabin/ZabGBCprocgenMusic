# Feature Specifications — Index

Owned by `06-feature-specification`. Full FS-xxx specs (20-field template) are authored per
feature as implementation approaches it, not all up front.

**MVP-push note (run #5, `BL-0012`):** the user authorized proceeding directly to implementation
for the whole Foundation bucket without formal FS-1xx documents, to reach a working MVP ROM in
one session. Each shipped feature's scope/traceability instead lives on its own `IP-xxxx` package
doc under `docs/implementation/packages/`, which covers equivalent ground (scope, requirements
traced, test evidence) at lower ceremony. Proper `FS-100`...`FS-105` documents are still owed as
a retroactive backfill (`BL-0012`) — this index stays `⛔ Planned` until that happens, not because
the features are unimplemented.

[↑ Docs index](../INDEX.md)

| FEAT | FS | File | Status |
|---|---|---|---|
| FEAT-1000 | FS-100 | fs-100-core-generation-engine.md | ⛔ Planned (implemented — see IP-0001/IP-0002/IP-0003) |
| FEAT-1010 | FS-101 | fs-101-input-steering.md | ⛔ Planned (implemented — see IP-0001) |
| FEAT-1020 | FS-102 | fs-102-reset-to-preset.md | ⛔ Planned (implemented — see IP-0001/IP-0005) |
| FEAT-1030 | FS-103 | fs-103-bad-zone-detection.md | ⛔ Planned (implemented — see IP-0004) |
| FEAT-1040 | FS-104 | fs-104-minimal-visualizer.md | ⛔ Planned (implemented — see IP-0006) |
| FEAT-1050 | FS-105 | fs-105-headless-verification-suite.md | ⛔ Planned (implemented — 56/56 checks across T1-T9, `test_rom.py`) |
| FEAT-1060 | FS-106 | [fs-106-sound-design-techniques.md](fs-106-sound-design-techniques.md) | ✅ Authored 2026-07-22 (`BL-0024`, full 20-field spec — not an abbreviated MVP-push note, no exception granted this time) |
| FEAT-1070 | FS-107 | [fs-107-combinable-generation-schemes.md](fs-107-combinable-generation-schemes.md) | ✅ Authored 2026-07-25 (`BL-0020`/`ADS-100`/`ADR-0001`, full 20-field spec); implemented as [`IP-1070`](../implementation/packages/IP-1070-combinable-generation-schemes.md), `VERIFIED`, shipped as part of R4 (GO confirmed 2026-07-25) |
| FEAT-1080 | FS-108 | [fs-108-genre-aware-style-presets.md](fs-108-genre-aware-style-presets.md) | ✅ Authored 2026-07-26 (roadmap R5/`ADS-101`, full 20-field spec); implemented as [`IP-1080`](../implementation/packages/IP-1080-genre-aware-style-presets.md), `VERIFIED` ([VR-1080](../implementation/verification/VR-1080-genre-aware-style-presets.md)) |
| FEAT-1090 | FS-109 | [fs-109-motif-recurrence-via-weighted-variant-selection.md](fs-109-motif-recurrence-via-weighted-variant-selection.md) | ✅ Authored 2026-07-26 (`BL-0010`/`ADS-102`, full 20-field spec); implemented as [`IP-1090`](../implementation/packages/IP-1090-motif-recurrence-via-weighted-variant-selection.md), `VERIFIED` ([VR-1090](../implementation/verification/VR-1090-motif-recurrence-via-weighted-variant-selection.md)) |
| FEAT-1100 | FS-110 | [fs-110-song-form-via-autonomous-phase-cycling.md](fs-110-song-form-via-autonomous-phase-cycling.md) | ✅ Authored 2026-07-26 (roadmap R6/`ADS-103`, full 20-field spec); planned as [`IP-1100`](../implementation/packages/IP-1100-song-form-via-autonomous-phase-cycling.md), `READY`, G3-authorized — not yet built |
