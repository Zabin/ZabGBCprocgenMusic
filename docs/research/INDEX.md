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
| R101 | SM83 instruction set & cycle costs | [encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md](encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md) | ✅ Authored 2026-07-22; **§8 addendum 2026-07-26 reverses the "cycle accounting not warranted" conclusion**; **§8.5 self-correction 2026-07-31 (`BL-0069`) — §8's dropped-write evidence FALSIFIED, the conclusion survives on direct `LY` measurement (budget ~exhausted on every frame, not one heavy frame class); re-answers the tooling question as "cheap runtime `LY` guard first, static cycle table only at remediation time"** |
| R102 | PPU modes, VBlank & VRAM/OAM access timing | [encyclopedia/R102-ppu-modes-and-vram-oam-access-timing.md](encyclopedia/R102-ppu-modes-and-vram-oam-access-timing.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired — grounds the shipped VBlank-gated `visuals.py` write pattern); **§3b WITHDRAWN 2026-07-31 (`BL-0069`) — the project never observed the Mode-3 hazard and cannot with this harness; new §3c records the exposure as live, measured (`update_visuals` finishes at `LY` 153) and untested, plus §4's "writes execute at the very start of VBlank" corrected to the end** |
| R103 | LCDC/STAT registers | [encyclopedia/R103-lcdc-and-stat-registers.md](encyclopedia/R103-lcdc-and-stat-registers.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired) |
| R104 | CGB palette system (BCPS/BCPD, RGB15) | [encyclopedia/R104-cgb-palette-system.md](encyclopedia/R104-cgb-palette-system.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired; grounds `visuals.py`'s `_emit_write_palette`/`rgb15`); **§7-8 addendum 2026-07-26** (`BL-0034` hardware half — palette-only theming costs ~8 bytes/theme against 29349 free ROM bytes, no new mechanism needed; simultaneous multi-palette tile variety would need real, ungrounded-until-then `VBK`/tilemap-attribute work) |
| R105 | OAM, sprites & OAM DMA | [encyclopedia/R105-oam-sprites-and-dma.md](encyclopedia/R105-oam-sprites-and-dma.md) | ✅ Authored 2026-07-22 (confirms no gap — Driftune has no sprites; records the real DMA/HRAM contract for if that ever changes) |
| R106 | MBC/SRAM | [encyclopedia/R106-mbc-and-sram.md](encyclopedia/R106-mbc-and-sram.md) | ✅ Authored 2026-07-22; **substantially extended 2026-07-22** (MSTR-001 §9 thread — the "no gap, C2 stands" framing is superseded now that v1.2 reopened C1/C2; real MBC1/3/5 + PyBoy save-mechanics facts recorded, MBC5(+RAM+BATTERY) named as the concrete recommendation if either is ever adopted, decision itself still not made here) |
| R107 | Joypad register & dual-read settling | [encyclopedia/R107-joypad-input.md](encyclopedia/R107-joypad-input.md) | ✅ Authored 2026-07-21 |
| R108 | APU channels & register map | [encyclopedia/R108-apu-sound-channels.md](encyclopedia/R108-apu-sound-channels.md) | ✅ Authored 2026-07-21 (this project's single most load-bearing hardware topic; covers user-list Phase 1 items 6-8 — APU overview, audio registers, pulse channel behavior) |
| R109 | Cartridge header, checksums & boot requirements | [encyclopedia/R109-cartridge-header.md](encyclopedia/R109-cartridge-header.md) | ✅ Authored 2026-07-21 |
| R110 | Interrupt model & ISR conventions | [encyclopedia/R110-interrupts-and-timing.md](encyclopedia/R110-interrupts-and-timing.md) | ✅ Authored 2026-07-21 (covers user-list Phase 1 items 4-5 — interrupts/timers, VBlank timing); **§3/§5 extended 2026-07-31 (`BL-0069`): first measured wake latency — `HALT` wakes at `LY` 144 on every frame, and per-frame work consumes ~9 of VBlank's 10 scanlines** |
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
| R217 | UX conventions for generative instruments (seed entry, presets, playback controls) | [encyclopedia/R217-ux-conventions-for-generative-instruments.md](encyclopedia/R217-ux-conventions-for-generative-instruments.md) | ✅ Authored 2026-07-21 (user-list Phase 7 items 81-88 — most already answered by existing decisions, see topic SS3). **SS3a addendum 2026-08-21 (`BL-0143`) — the "song regeneration" gap closes.** It was filed as unaddressed and routed through `01-vision` because it was grouped with seed entry, menu design and preset management under one premise ("no menu state exists"). That premise holds for those three and **not** for regeneration, which in shipped generative instruments is consistently a **parameterless single control**, not a surface — Playbeat's reroll-one-dimension-hold-the-rest being the closest analogue to what `ADR-0006` decided. Also records that the capability was **two-thirds present since `IP-0007`** (2026-07's `DIV` reseed on Select), so the real gap was never "we cannot regenerate" but "regenerating costs you your settings"; and the general lesson — **route a parked item by the interaction surface it actually needs, not the category it resembles**, since nothing revisits a question filed behind a gate that will not open. SS6b's blanket "produces no feature" exception becomes **partial** |
| R218 | Inspiration & history survey (Eno/Koan, No Man's Sky, Spore, Rogue, live coding, bytebeat) | [encyclopedia/R218-inspiration-and-history-survey.md](encyclopedia/R218-inspiration-and-history-survey.md) | ✅ Authored 2026-07-21 (user-list Phase 10 items 105-110, 113-115; classic GB soundtracks/modern chiptune, items 111-112, covered by R207/R209) |
| R219 | Genre feasibility on 4-channel GBC PSG | [encyclopedia/R219-genre-feasibility-on-4-channel-gbc-psg.md](encyclopedia/R219-genre-feasibility-on-4-channel-gbc-psg.md) | ✅ Authored 2026-07-22 (MSTR-001 §9 thread — grounds which of the user's ~25 genre references are realistically expressible on this hardware) |
| R220 | Style evolution, blending & song-form structure | [encyclopedia/R220-style-evolution-and-song-form-structure.md](encyclopedia/R220-style-evolution-and-song-form-structure.md) | ✅ Authored 2026-07-22 (MSTR-001 §9 thread — extends `BL-0010`/R211/R212's phrase/form gap; horizontal-resequencing/vertical-layering technique identified as a cheap, existing-parameter-driven answer for song-form + style-drift) |
| R221 | Emotional/energy parameter mapping | [encyclopedia/R221-emotional-energy-parameter-mapping.md](encyclopedia/R221-emotional-energy-parameter-mapping.md) | ✅ Authored 2026-07-22 (MSTR-001 §9 thread — valence-arousal model mapped onto Driftune's existing tempo/density/scale/dissonance-score state) |
| R222 | Visual evolution conventions | [encyclopedia/R222-visual-evolution-conventions.md](encyclopedia/R222-visual-evolution-conventions.md) | ✅ Authored 2026-07-26 (`BL-0034` — palette-swap-only day/night/seasonal theming is the established, hardware-precedented technique, Pokemon Gold/Silver cited; grounds `CAP-14`/R9's design half, VRAM-budget half still owed to `02-research-gbc-hardware`) |
| R223 | Audio-visual synchronization conventions | [encyclopedia/R223-audio-visual-synchronization.md](encyclopedia/R223-audio-visual-synchronization.md) | ✅ Authored 2026-07-26 (`BL-0035` — pitch is the highest-confidence mapping dimension, green-channel-preferential intensity mapping, one-frame sync lag confirmed perceptually acceptable, corroborating `VR-0006`'s own prior finding) |
| R224 | Listening-evaluation methodology: structured, per-parameter critique elicitation | [encyclopedia/R224-listening-evaluation-methodology.md](encyclopedia/R224-listening-evaluation-methodology.md) | ✅ Authored 2026-08-08 (`BL-0097` — grounds `09-content-review`'s first-ever question-set design: one manipulation-check + one semantic-differential rating per tunable parameter); **§7 addendum 2026-08-19 (`BL-0120`) — adds the holistic (non-parameter-scoped) dimension the original question set structurally excluded, plus the strong-beat-sonority measurement correction** |
| R225 | Harmonic coordination: shared chord context across independent voices | [encyclopedia/R225-harmonic-coordination-shared-chord-context.md](encyclopedia/R225-harmonic-coordination-shared-chord-context.md) | ✅ Authored 2026-08-19 (`BL-0119` — re-grounds `R211` §5's now-overtaken "don't attempt chord-progression harmony" deferral, **which §9 of that topic now formally withdraws**, into a concrete SM83-tractable mechanism: a 1-3 byte shared chord-root context, a sparse tonic-biased transition table, root/fifth bass, chord-tone-on-strong-beat melody, cadence-as-chord-constraint; costed against newly-measured onset schedules — 95.1 % of frames execute no pitched-onset branch) |

Superseded: [R200-generative-music-design.md](R200-generative-music-design.md) (content split
across R201-R204, R206-R207).

**Addenda landed 2026-07-26** (all closing previously-filed backlog research-gaps, none a new
topic): **R211 §8** (`BL-0037` — weighted random selection, grounding `DELTA_TABLE`'s existing
shipped bias); **R214 §8** (`BL-0010` — L-systems for motif recurrence, deep-evaluated with a
concrete bounded-depth/weighted-rule design constraint); **R219 §8** (`BL-0036` — Celtic/Seasonal/
Holiday genre-coverage gap, Celtic joins the Folk/World tier, Holiday found high-confidence and
uniquely cheap, Seasonal reclassified as a preset-rotation concern not a genre).

**Addenda landed 2026-08-19** (`BL-0119`/`BL-0120`, the harmonic-coordination pass): **R211 §9** —
the first *withdrawal* addendum in the R200 tier (§5's "do not attempt chord-progression harmony"
bullet struck, replacement position pointed at R225), following R101 §8.5/R102 §3b's
supersede-don't-erase discipline; **R212 §7** cross-link recording R225 §3f as a partial reversal of
its cadence negative result; **R224 §7** — the holistic, non-parameter-scoped review dimension plus
the strong-beat-sonority metric correction (research half of `BL-0120`; the `09-content-review`
skill-definition half is explicitly **not** closed and is out of every pipeline stage's write
scope).

> **Forward-trace convention (`MSTR-001` C10) — established 2026-07-26 (`BL-0067`).** Every topic
> carries a `## 6b. Forward trace` section naming the shipped code it fed, or an explicitly-named
> exception (a topic whose real job is grounding implementation *quality* or a decision *not* to
> act). Rationale and the decision to keep this per-topic rather than in a central matrix:
> [GDS-10 §4](../architecture/10-requirements-traceability-matrix.md).
> **Status: COMPLETE 2026-07-31 — all 47 topics carry a forward-trace section.** R300
> (R301-R309) done 2026-07-26; R100 (R101-R115) done 2026-07-26; **R200 (R201-R223, 23 topics)
> done 2026-07-31**, closing `BL-0067`/`BL-0071` and the audit `MSTR-001` v1.3's own changelog
> predicted would be owed.
>
> **Whole-encyclopedia tally: 47 topics — 33 traced, 14 carrying honest exceptions or recorded
> partials.** The exceptions, by category:
>
> - **No forward trace at all, correctly** — `R105` (no sprites/OAM used by design), `R209` (the
>   GB music-driver survey; Driftune adopted none of them and wrote its own engine), `R210`
>   (tracker formats; there is no tracker, no pattern data, no sequencer).
> - **Grounded a decision *not* to act** — `R106` (`ADR-0002`'s decision not to adopt MBC/SRAM),
>   `R111` (confirmed a non-risk: the erratum is DMG-only), `R215` (constraint/scheduling
>   approaches considered and set aside), `R306`, `R308`.
> - **Orientation/history topics** — `R112` and `R218`, exactly the category `MSTR-001` v1.3
>   predicted would turn up.
> - **Confirms an existing non-goal** — ~~`R217`~~ **`R217` moved to *Partial* 2026-08-21**: seven of its eight surveyed
>   items still confirm existing non-goals, but **song regeneration produced a feature** — `ADR-0006` → `FR-1070` → the
>   Select handler. See that topic's SS3a.
> - **Recommendation deliberately rejected, for a recorded reason** — `R213` (`DIV` boot seeding
>   not adopted; the fixed `LFSR_SEED` is what makes every test run a fixed-seed regression run,
>   `R305` §5).
> - **Partial — design-level trace, feature half still owed** — `R208` (`BL-0021`'s accessibility
>   finding accepted at design altitude, unbuilt), `R222` (palette-swap strategy adopted by
>   `GDS-08`, no theme shipped), `R223` (sync contract in `GDS-08`, tempo-synced motion unbuilt,
>   `CR-0001`), `R309`.
>
> **That ratio is the audit's value: none of it was visible before the convention existed**, and
> two entries are findings in their own right — `R209` is the encyclopedia's weakest-traced topic
> (cited by nothing anywhere in the tree), while `R214` is the strongest argument *for* the
> discipline: its §8 talked the project out of an L-system derivation engine and into the fixed
> weighted-variant table that actually shipped as `IP-1090`.

## R300 — Tooling, Emulation & Verification

| ID | Topic | File | Status |
|---|---|---|---|
| R301 | PyBoy headless API | [encyclopedia/R301-pyboy-headless-api.md](encyclopedia/R301-pyboy-headless-api.md) | ✅ Authored 2026-07-21 · **§3/§5 extended 2026-07-31 (`BL-0069`): PyBoy models no PPU-mode gating on VRAM writes (`mb.py:502-511`) — a hard bound on what any headless test here can prove** |
| R302 | Python-assembler codegen patterns | [encyclopedia/R302-python-assembler-codegen-patterns.md](encyclopedia/R302-python-assembler-codegen-patterns.md) | ✅ Authored 2026-07-22 (confirms no gap for the current flat-32KB design — the label/fixup mechanism has handled 9 packages cleanly; `IP-0007`'s `JR`-out-of-range incident is evidence it correctly catches the one error class it exists to catch); **§8-9 addendum 2026-07-22** (MSTR-001 §9 thread — bank-switching would need real per-bank label addressing + cross-bank-call safety, genuine assembler-architecture work, not a patch; PyBoy itself natively supports MBC1/3/5 per its own source) |
| R303 | 2bpp tile encoding & palette data formats | [encyclopedia/R303-2bpp-tile-encoding.md](encyclopedia/R303-2bpp-tile-encoding.md) | ✅ Authored 2026-07-22 (`IP-0006`'s trigger fired; confirms `visuals.py`'s tile bytes are correctly encoded) |
| R304 | ROM validation | [encyclopedia/R304-rom-validation.md](encyclopedia/R304-rom-validation.md) | ✅ Authored 2026-07-22 (split out from R109 per its own "split out if it grows more complex" condition; surfaces a minor test-coverage note — see backlog `BL-0022`) |
| R305 | Emulator-based test design | [encyclopedia/R305-emulator-test-design.md](encyclopedia/R305-emulator-test-design.md) | ✅ Authored 2026-07-21 (extended to cover user-list Phase 9 items 101-104 — audio verification, fixed-seed regression, long-duration, hardware-compat testing) · **§3/§5 extended 2026-07-31 (`BL-0069`): the `pb.tick()` mid-frame sampling hazard, the check-the-emulator-source rule, and a can/cannot-establish table** |
| R306 | Toolchain portability | [encyclopedia/R306-toolchain-portability.md](encyclopedia/R306-toolchain-portability.md) | ✅ Authored 2026-07-22 (path handling confirmed portable; dependency management is NOT — this session hit a real `pyboy`-not-preinstalled gap, see backlog `BL-0023`) |
| R307 | Real-time audio engine architecture patterns | [encyclopedia/R307-realtime-audio-engine-architecture.md](encyclopedia/R307-realtime-audio-engine-architecture.md) | ✅ Authored 2026-07-21 (user-list Phase 6 items 69-80) |
| R308 | CPU/RAM/ROM performance budgeting | [encyclopedia/R308-performance-budgeting.md](encyclopedia/R308-performance-budgeting.md) | ✅ Authored 2026-07-21 (user-list Phase 8 items 89-96) · **§8.5 self-correction 2026-07-31 (`BL-0069`): §8's dropped-write mechanism FALSIFIED and withdrawn; the budget-exceeded conclusion survives on stronger `LY`-probe evidence** |
| R309 | Emulator comparison & debugging tools (SameBoy, BGB) | [encyclopedia/R309-emulator-debugging-tools.md](encyclopedia/R309-emulator-debugging-tools.md) | ✅ Authored 2026-07-21 (user-list Phase 9 items 97-100) |
| R310 | Refactoring practices — equivalence proof, baseline capture, doc-tree restructuring | [encyclopedia/R310-refactoring-practices.md](encyclopedia/R310-refactoring-practices.md) | ✅ Authored 2026-07-31 (`BL-0076`) — grounds `08-refactoring`'s and `07-implementation-planning`'s equivalence-contract convention, previously citing a non-existent `R307-refactoring-practices.md` (`R307`'s real ID is taken by an unrelated topic); both skill files' citations corrected to `R310` |

Superseded: [R300-tooling-and-testing.md](R300-tooling-and-testing.md) (content split across
R301, R305).
