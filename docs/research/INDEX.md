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
| R101 | SM83 instruction set & cycle costs | [encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md](encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md) | ✅ Authored 2026-07-22 (confirms no gap — `gbc_lib.py`'s opcode emitters stay simple; cycle-exact accounting not currently warranted, empirical stress-test evidence covers NFR-1010) |
| R102 | PPU modes, VBlank & VRAM/OAM access timing | [encyclopedia/R102-ppu-modes-and-vram-oam-access-timing.md](encyclopedia/R102-ppu-modes-and-vram-oam-access-timing.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired — grounds the shipped VBlank-gated `visuals.py` write pattern) |
| R103 | LCDC/STAT registers | [encyclopedia/R103-lcdc-and-stat-registers.md](encyclopedia/R103-lcdc-and-stat-registers.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired) |
| R104 | CGB palette system (BCPS/BCPD, RGB15) | [encyclopedia/R104-cgb-palette-system.md](encyclopedia/R104-cgb-palette-system.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired; grounds `visuals.py`'s `_emit_write_palette`/`rgb15`) |
| R105 | OAM, sprites & OAM DMA | [encyclopedia/R105-oam-sprites-and-dma.md](encyclopedia/R105-oam-sprites-and-dma.md) | ✅ Authored 2026-07-22 (confirms no gap — Driftune has no sprites; records the real DMA/HRAM contract for if that ever changes) |
| R106 | MBC/SRAM | [encyclopedia/R106-mbc-and-sram.md](encyclopedia/R106-mbc-and-sram.md) | ✅ Authored 2026-07-22 (confirms no gap — MSTR-001 C2's no-SRAM commitment stands; records what an MBC adoption would need) |
| R107 | Joypad register & dual-read settling | [encyclopedia/R107-joypad-input.md](encyclopedia/R107-joypad-input.md) | ✅ Authored 2026-07-21 |
| R108 | APU channels & register map | [encyclopedia/R108-apu-sound-channels.md](encyclopedia/R108-apu-sound-channels.md) | ✅ Authored 2026-07-21 (this project's single most load-bearing hardware topic; covers user-list Phase 1 items 6-8 — APU overview, audio registers, pulse channel behavior) |
| R109 | Cartridge header, checksums & boot requirements | [encyclopedia/R109-cartridge-header.md](encyclopedia/R109-cartridge-header.md) | ✅ Authored 2026-07-21 |
| R110 | Interrupt model & ISR conventions | [encyclopedia/R110-interrupts-and-timing.md](encyclopedia/R110-interrupts-and-timing.md) | ✅ Authored 2026-07-21 (covers user-list Phase 1 items 4-5 — interrupts/timers, VBlank timing) |
| R111 | APU hardware quirks & DMG vs. CGB audio differences | [encyclopedia/R111-apu-hardware-quirks.md](encyclopedia/R111-apu-hardware-quirks.md) | ✅ Authored 2026-07-21 (user-list Phase 1 items 14-15) |
| R112 | GBC hardware architecture overview / memory map & banking | [encyclopedia/R112-gbc-memory-map-overview.md](encyclopedia/R112-gbc-memory-map-overview.md) | ✅ Authored 2026-07-22 (user-list Phase 1 items 1, 3 — confirms no gap: single 32KB bank, no MBC in use; ties R101/R104-R110/R112 together as one whole-address-space orientation map) |
| R113 | Frame sequencer: envelope, length counter & sweep timing | [encyclopedia/R113-frame-sequencer-envelope-length-sweep.md](encyclopedia/R113-frame-sequencer-envelope-length-sweep.md) | ✅ Authored 2026-07-21 (user-list Phase 1 items 11-13) |
| R114 | Wave channel programming | [encyclopedia/R114-wave-channel-programming.md](encyclopedia/R114-wave-channel-programming.md) | ✅ Authored 2026-07-21 (user-list Phase 1 item 9; Phase 5 item 58) |
| R115 | Noise channel implementation | [encyclopedia/R115-noise-channel-implementation.md](encyclopedia/R115-noise-channel-implementation.md) | ✅ Authored 2026-07-21 (user-list Phase 1 item 10; Phase 5 item 59) |

Superseded: [R100-gbc-sound-hardware.md](R100-gbc-sound-hardware.md) (content split into R108,
with R107/R109/R110-R115 newly split out and R100's own "Confirmed during IP-0001" section folded
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
| R208 | Palette & color design under CGB constraints for a non-game display | [encyclopedia/R208-palette-and-color-design-under-cgb-constraints.md](encyclopedia/R208-palette-and-color-design-under-cgb-constraints.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired; confirms the shipped red/calm semantic and single-palette restraint match real convention, surfaces a new accessibility finding — see backlog `BL-0021`) |
| R209 | Game Boy music driver survey (hUGEDriver, GBT Player, LSDJ, Nanoloop) | [encyclopedia/R209-gb-music-driver-survey.md](encyclopedia/R209-gb-music-driver-survey.md) | ✅ Authored 2026-07-21 (user-list Phase 2 items 16-21) |
| R210 | Tracker music formats, sequencing techniques & real-time synthesis on GB | [encyclopedia/R210-tracker-formats-sequencing.md](encyclopedia/R210-tracker-formats-sequencing.md) | ✅ Authored 2026-07-21 (user-list Phase 2 items 22-24) |
| R211 | Melody/chord/bass/countermelody/percussion/phrase/motif generation techniques | [encyclopedia/R211-melodic-harmonic-generation-techniques.md](encyclopedia/R211-melodic-harmonic-generation-techniques.md) | ✅ Authored 2026-07-21 (user-list Phase 3 items 26-33 — surfaced a research-gap, see backlog `BL-0010`) |
| R212 | Musical form, tension/release & macro-level parameters (song structure, cadence, key modulation, time signature, tempo variation, dynamics) | [encyclopedia/R212-form-tension-and-macro-musical-parameters.md](encyclopedia/R212-form-tension-and-macro-musical-parameters.md) | ✅ Authored 2026-07-21 (user-list Phase 3 items 34-40 — same gap as R211, confirmed from the form angle) |
| R213 | PRNGs, seed management & deterministic generation | [encyclopedia/R213-prng-seed-management.md](encyclopedia/R213-prng-seed-management.md) | ✅ Authored 2026-07-21 (user-list Phase 4 items 41-43) |
| R214 | Rule-based/grammar/L-system/cellular-automata generation survey | [encyclopedia/R214-grammar-and-cellular-generation-survey.md](encyclopedia/R214-grammar-and-cellular-generation-survey.md) | ✅ Authored 2026-07-21 (user-list Phase 4 items 46-49, 51-52) |
| R215 | Genetic algorithms, constraint solving, state machines & event scheduling (survey) | [encyclopedia/R215-constraint-and-scheduling-survey.md](encyclopedia/R215-constraint-and-scheduling-survey.md) | ✅ Authored 2026-07-21 (user-list Phase 4 items 53-56) |
| R216 | Sound design techniques: timbre, arpeggio, vibrato, portamento & percussion synthesis | [encyclopedia/R216-sound-design-techniques.md](encyclopedia/R216-sound-design-techniques.md) | ✅ Authored 2026-07-21 (user-list Phase 5 items 57, 60-68) |
| R217 | UX conventions for generative instruments (seed entry, presets, playback controls) | [encyclopedia/R217-ux-conventions-for-generative-instruments.md](encyclopedia/R217-ux-conventions-for-generative-instruments.md) | ✅ Authored 2026-07-21 (user-list Phase 7 items 81-88 — most already answered by existing decisions, see topic SS3) |
| R218 | Inspiration & history survey (Eno/Koan, No Man's Sky, Spore, Rogue, live coding, bytebeat) | [encyclopedia/R218-inspiration-and-history-survey.md](encyclopedia/R218-inspiration-and-history-survey.md) | ✅ Authored 2026-07-21 (user-list Phase 10 items 105-110, 113-115; classic GB soundtracks/modern chiptune, items 111-112, covered by R207/R209) |

Superseded: [R200-generative-music-design.md](R200-generative-music-design.md) (content split
across R201-R204, R206-R207).

## R300 — Tooling, Emulation & Verification

| ID | Topic | File | Status |
|---|---|---|---|
| R301 | PyBoy headless API | [encyclopedia/R301-pyboy-headless-api.md](encyclopedia/R301-pyboy-headless-api.md) | ✅ Authored 2026-07-21 |
| R302 | Python-assembler codegen patterns | [encyclopedia/R302-python-assembler-codegen-patterns.md](encyclopedia/R302-python-assembler-codegen-patterns.md) | ✅ Authored 2026-07-22 (confirms no gap — the label/fixup mechanism has handled 9 packages cleanly; `IP-0007`'s `JR`-out-of-range incident is evidence it correctly catches the one error class it exists to catch) |
| R303 | 2bpp tile encoding & palette data formats | [encyclopedia/R303-2bpp-tile-encoding.md](encyclopedia/R303-2bpp-tile-encoding.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired; confirms `visuals.py`'s tile bytes are correctly encoded) |
| R304 | ROM validation | [encyclopedia/R304-rom-validation.md](encyclopedia/R304-rom-validation.md) | ✅ Authored 2026-07-22 (split out from R109 per its own "split out if it grows more complex" condition; surfaces a minor test-coverage note — see backlog `BL-0022`) |
| R305 | Emulator-based test design | [encyclopedia/R305-emulator-test-design.md](encyclopedia/R305-emulator-test-design.md) | ✅ Authored 2026-07-21 (extended to cover user-list Phase 9 items 101-104 — audio verification, fixed-seed regression, long-duration, hardware-compat testing) |
| R306 | Toolchain portability | [encyclopedia/R306-toolchain-portability.md](encyclopedia/R306-toolchain-portability.md) | ✅ Authored 2026-07-22 (path handling confirmed portable; dependency management is NOT — this session hit a real `pyboy`-not-preinstalled gap, see backlog `BL-0023`) |
| R307 | Real-time audio engine architecture patterns | [encyclopedia/R307-realtime-audio-engine-architecture.md](encyclopedia/R307-realtime-audio-engine-architecture.md) | ✅ Authored 2026-07-21 (user-list Phase 6 items 69-80) |
| R308 | CPU/RAM/ROM performance budgeting | [encyclopedia/R308-performance-budgeting.md](encyclopedia/R308-performance-budgeting.md) | ✅ Authored 2026-07-21 (user-list Phase 8 items 89-96) |
| R309 | Emulator comparison & debugging tools (SameBoy, BGB) | [encyclopedia/R309-emulator-debugging-tools.md](encyclopedia/R309-emulator-debugging-tools.md) | ✅ Authored 2026-07-21 (user-list Phase 9 items 97-100) |

Superseded: [R300-tooling-and-testing.md](R300-tooling-and-testing.md) (content split across
R301, R305).
