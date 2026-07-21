# Research — Index

Owned by the three `02-research-*` skills (peers, no ordering among themselves). Authored as a
per-topic encyclopedia under `docs/research/encyclopedia/` (index-first: a row is added `⛔
Planned` before the topic file is written, flipped `✅` when the quality gate passes).

[↑ Docs index](../INDEX.md)

**Restructuring note (2026-07-21):** the first research pass (run #1) authored three monolithic
per-tier files (`R100-gbc-sound-hardware.md`, `R200-generative-music-design.md`,
`R300-tooling-and-testing.md`, directly under `docs/research/`) before the adapted `02-research-*`
skills' own expected structure (`docs/research/encyclopedia/R1xx`/`R2xx`/`R3xx`, one topic per
file, 7-section shape, inline citations) was reconciled against. This run split and re-grounded
the load-bearing content into the expected structure with real citations; the three original
files are **retained, superseded** (not deleted — nothing here is thrown away, only superseded
per the pipeline's own "relocate, don't delete" discipline) and each carries a pointer to its
replacement topic(s) at the top.

## R100 — GBC Hardware & SM83

| ID | Topic | File | Status |
|---|---|---|---|
| R101 | SM83 instruction set & cycle costs | R101-*.md | ⛔ Planned (no gap yet — `gbc_lib.py`'s opcode emitters are simple and unambiguous; author if a future package needs cycle-exact timing) |
| R102 | PPU modes, VBlank & VRAM/OAM access timing | R102-*.md | ⛔ Planned (no visuals yet — `IP-0006`) |
| R103 | LCDC/STAT registers | R103-*.md | ⛔ Planned (`IP-0006`) |
| R104 | CGB palette system (BCPS/BCPD, OCPS/OCPD, RGB15) | R104-*.md | ⛔ Planned (`IP-0006`) |
| R105 | OAM, sprites & OAM DMA | R105-*.md | ⛔ Planned (Driftune has no sprites — author only if that changes) |
| R106 | MBC/SRAM | R106-*.md | ⛔ Planned (MSTR-001 C2: no SRAM commitment at v1 — author only if that non-goal is revisited) |
| R107 | Joypad register & dual-read settling | [encyclopedia/R107-joypad-input.md](encyclopedia/R107-joypad-input.md) | ✅ Authored 2026-07-21 |
| R108 | APU channels & register map | [encyclopedia/R108-apu-sound-channels.md](encyclopedia/R108-apu-sound-channels.md) | ✅ Authored 2026-07-21 (this project's single most load-bearing hardware topic) |
| R109 | Cartridge header, checksums & boot requirements | [encyclopedia/R109-cartridge-header.md](encyclopedia/R109-cartridge-header.md) | ✅ Authored 2026-07-21 |
| R110 | Interrupt model & ISR conventions | [encyclopedia/R110-interrupts-and-timing.md](encyclopedia/R110-interrupts-and-timing.md) | ✅ Authored 2026-07-21 |

Superseded: [R100-gbc-sound-hardware.md](R100-gbc-sound-hardware.md) (content split into R108,
with R107/R109/R110 newly split out and R100's own "Confirmed during IP-0001" section folded
into R108 SS4).

## R200 — Procedural Music & Visualizer Design

| ID | Topic | File | Status |
|---|---|---|---|
| R201 | Algorithmic composition techniques for chiptune | [encyclopedia/R201-algorithmic-composition-techniques.md](encyclopedia/R201-algorithmic-composition-techniques.md) | ✅ Authored 2026-07-21 |
| R202 | Rhythm & tempo generation | [encyclopedia/R202-rhythm-tempo-generation.md](encyclopedia/R202-rhythm-tempo-generation.md) | ✅ Authored 2026-07-21 |
| R203 | Voice-leading & density control across a fixed small channel count | [encyclopedia/R203-voice-leading-density-control.md](encyclopedia/R203-voice-leading-density-control.md) | ✅ Authored 2026-07-21 |
| R204 | "Bad zone" detection heuristics | [encyclopedia/R204-bad-zone-detection-heuristics.md](encyclopedia/R204-bad-zone-detection-heuristics.md) | ✅ Authored 2026-07-21 |
| R205 | Generative visualizer conventions | [encyclopedia/R205-generative-visualizer-conventions.md](encyclopedia/R205-generative-visualizer-conventions.md) | ✅ Authored 2026-07-21 (lighter pass — deepen when `IP-0006`/GDS-08 start) |
| R206 | Button-to-musical-parameter mapping conventions | [encyclopedia/R206-button-parameter-mapping-conventions.md](encyclopedia/R206-button-parameter-mapping-conventions.md) | ✅ Authored 2026-07-21 |
| R207 | GB-era chiptune composition & channel-usage idioms | [encyclopedia/R207-gb-chiptune-channel-idioms.md](encyclopedia/R207-gb-chiptune-channel-idioms.md) | ✅ Authored 2026-07-21 (surfaced a finding — see backlog) |
| R208 | Palette & color design under CGB constraints for a non-game display | R208-*.md | ⛔ Planned (`IP-0006`/GDS-08 — R205 SS5 already sketches the restraint principle; deepen when the visualizer's real palette count is decided) |

Superseded: [R200-generative-music-design.md](R200-generative-music-design.md) (content split
across R201-R204, R206-R207).

## R300 — Tooling, Emulation & Verification

| ID | Topic | File | Status |
|---|---|---|---|
| R301 | PyBoy headless API | [encyclopedia/R301-pyboy-headless-api.md](encyclopedia/R301-pyboy-headless-api.md) | ✅ Authored 2026-07-21 |
| R302 | Python-assembler codegen patterns | R302-*.md | ⛔ Planned (no gap yet — `gbc_lib.py`'s label/fixup mechanism is simple; author if a future package needs it formalized) |
| R303 | 2bpp tile encoding & palette data formats | R303-*.md | ⛔ Planned (`IP-0006` — no tile data exists yet) |
| R304 | ROM validation | R304-*.md | ⛔ Planned (folded into R109 for now — split out if header validation grows more complex than the current checksum recompute) |
| R305 | Emulator-based test design | [encyclopedia/R305-emulator-test-design.md](encyclopedia/R305-emulator-test-design.md) | ✅ Authored 2026-07-21 |
| R306 | Toolchain portability | R306-*.md | ⛔ Planned (no portability need identified yet — single build target, single CI-less environment) |

Superseded: [R300-tooling-and-testing.md](R300-tooling-and-testing.md) (content split across
R301, R305).
