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
