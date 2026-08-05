# Functional & Non-Functional Requirements — v1 baseline

- **Owned by:** `04-requirements-engineering` · **Status:** ✅ Authored, 2026-07-21
- **Derived from:** GDS-00/01/03/07. This is a from-scratch increment's first requirements pass —
  every FR/NFR below traces to a GDS-03/07 decision, not to existing code (there is none yet).

## Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| FR-1000 | On power-on, the engine initializes to the known-good preset (GDS-03 §5) and begins generating audio on all channels its channel-mix preset activates, with no button input required. | GDS-01, GDS-03 §5 |
| FR-1010 | The generation routine writes valid PSG register values for pulse A, pulse B, wave, and noise channels such that `NR52` reports each active channel as currently playing when its channel-mix preset includes it. | GDS-03 §1-2, R100 |
| FR-1020 | D-pad Up/Down each step `TEMPO_IDX` by exactly one (wrapping), on the frame of a rising edge only — holding the direction does not repeat the step. | GDS-03 §3, GDS-07 §1 |
| FR-1030 | D-pad Left/Right each step `OCTAVE_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1040 | The A button steps `SCALE_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1050 | The B button steps `DENSITY_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1060 | The Start button steps `CHMIX_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1070 | The Select button, on a rising edge, unconditionally reloads all of `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` to the known-good preset and clears `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/all `STALE_COUNT_*`/`ONSET_WINDOW_COUNT`, regardless of the current bad-zone state. | GDS-03 §5 |
| FR-1080 | On every note-onset event, the engine recomputes `DISSONANCE_SCORE` from the currently-sounding pitched channels' scale degrees and sets `BAD_ZONE_FLAGS` bit0 (`DISSONANT`) when the score exceeds the dissonance threshold. | GDS-03 §4a |
| FR-1090 | On every note-onset event, each pitched channel's history ring buffer (`HIST_PA`/`PB`/`WV`) records the new scale degree; `STALE_COUNT_*` increments while a period-1-or-2 repeat continues and resets otherwise; `BAD_ZONE_FLAGS` bit1 (`STUCK`) is set when any `STALE_COUNT_*` exceeds the stale threshold. | GDS-03 §4b |
| FR-1100 | The engine counts note-onset events across all channels in a rolling window and sets `BAD_ZONE_FLAGS` bit2 (`OVERLOAD`) when the count exceeds the overload threshold within the window. | GDS-03 §4c |
| FR-1110 | `BAD_ZONE_FLAGS` bit3 (`COMBINED`) is the logical OR of bits0-2, recomputed whenever any of them changes. | GDS-03 §4d |
| FR-1120 | The visualizer reads `NR52`/`NR51` and the WRAM engine-state mirror and updates BG tile/palette content to represent per-channel activity and bad-zone status, without writing to any engine-state or PSG register itself (read-only consumer). **Reworded 2026-07-26** (`BL-0016`, per [GDS-08 §7](../architecture/08-presentation-architecture.md)): the original text also claimed tempo representation. Displaying the tempo *setting* is real but is owned by `FR-1350` (`IP-1110`'s indicator row), not here; tempo-*synced motion* — a visual element whose timing follows the beat, which is how the original wording read naturally in `R205`/`R223`'s audio-visual-sync context — was never built and is now `CR-0001` below, explicitly not baselined. | GDS-03 §1, GDS-08 §2/§3 |
| FR-1130 | Each pitched channel's note-onset behavior rapidly cycles the channel's frequency register among 2 or 3 notes of a chord implied by the channel's current scale degree (root + at least one harmonic interval above it, e.g. a third and/or fifth within the active scale), for the duration of that note, before the next scheduled note-onset event. | R216 §3/§5 (arpeggio-as-polyphony), GDS-03 §1 (channel ownership) |
| FR-1140 | Each pitched channel's currently-sounding frequency is periodically modulated by a small, bounded oscillation (vibrato) around the note's base frequency, audible as a pitch wobble rather than a step change, without altering which scale degree the channel is considered to be playing for dissonance/stale-repetition scoring purposes (FR-1080/FR-1090 read the base note, not the modulated instantaneous frequency). | R216 §3/§5 (vibrato) |
| FR-1150 | On a note-onset event where the channel's previous and new scale degrees differ, the channel's frequency register transitions from the previous note's frequency to the new note's frequency over more than one frame (a glide/portamento), rather than jumping directly to the new frequency on the onset frame. | R216 §3/§5 (portamento) |
| FR-1160 | At least one pulse channel's duty-cycle register bits (`NR11`/`NR21`) vary across note-onset events rather than remaining fixed at a single duty-cycle value for the entire session. | R216 §3/§5/§6 (duty-cycle variation) |
| FR-1170 | The noise channel's percussion synthesis (fast-decay envelope on `NR42`, `FR-1010`'s existing noise-channel scope) already satisfies R216 §3's chiptune-percussion-synthesis convention ("basic percussion... generated from white noise going through an ADSR envelope") as shipped by `IP-0003` — this requirement records the trace explicitly; it introduces no new behavior. | R216 §3 (percussion synthesis, already shipped), FR-1010 |
| FR-1180 | Each pitched channel's note-selection strategy (Scheme W — the shipped LFSR-driven walk — or Scheme E — Euclidean-gated onset timing with fixed-motif pitch selection) is determined by that channel's scheme-select bit in the currently-active `CHMIX_IDX` preset's mask data, independently of the other two pitched channels' scheme assignment (a "combination" is expressed at the ensemble level, never blended within one channel's own output). | ADS-100 §2/§3 (Domain Model: "Generation Scheme," "Scheme assignment"), ADR-0001 |
| FR-1190 | Switching `CHMIX_IDX` (Start) to a preset with a different scheme assignment for a pitched channel takes effect from that channel's next note-onset event, not instantaneously mid-note — consistent with how `CHMIX_IDX`'s channel-activity half (`FR-1000`/`FR-1010`, `IP-9010`) already behaves. | ADS-100 §5 (FR-candidate 2) |
| FR-1200 | A pitched channel running Scheme E gates its note onsets through the same Euclidean-pattern mechanism the noise channel already uses for density-driven hits (reusing `DENSITY_IDX`'s existing k-value selection), rather than a fixed per-tempo timer reload — producing a patterned, not continuously-regular, onset rhythm. | ADS-100 §3 (Domain Model: "Scheme E," onset timing), R202 |
| FR-1210 | A pitched channel running Scheme E selects its next scale-degree by stepping through a fixed, precomputed cyclic motif (a short sequence of scale-degree deltas), rather than an LFSR-picked random delta. | ADS-100 §3 (Domain Model: "Scheme E," pitch selection), R211, R216 |
| FR-1220 | Bad-zone detection (`FR-1080`/`FR-1090`/`FR-1100`) and autonomous recovery (`IP-0007`'s dissonant/stuck/overload-driven overrides) apply identically to a pitched channel regardless of which generation scheme (Scheme W or Scheme E) it is currently running — no scheme-specific bad-zone logic exists. | ADS-100 §2 ("both schemes still write through the same `BAD_ZONE_FLAGS`-driven... overrides"), §5 (FR-candidate 4) |
| FR-1230 | Each `CHMIX_IDX` preset value maps to a style data row specifying that style's target tempo index, density index, scale/mode index, and duty-cycle bias. | ADS-101 §2/§3/§5 (FR-candidate 1) |
| FR-1240 | Changing `CHMIX_IDX` (Start) applies its mapped style row's target values to `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/the duty-cycle-bias state immediately on the press that changes the preset — not gated to the next note-onset event, unlike `CHMIX_IDX`'s channel-activity/scheme-select half (`FR-1190`). | ADS-101 §2/§4/§5 (FR-candidate 2) |
| FR-1250 | The style data defines at least 3 named styles, each producing a tempo/density/scale/duty-cycle-bias combination that is audibly distinguishable, by content review, from every other defined style and from the default (preset-0) combination. | ADS-101 §3/§5 (FR-candidate 3) |
| FR-1260 | The style row mapped to `CHMIX_IDX` preset 0 (the boot/Select-reset preset) specifies exactly the tempo/density/scale/duty-cycle-bias combination already shipped as the default preset — selecting preset 0 introduces no change to current boot/reset behavior. | ADS-101 §5 (FR-candidate 4) |
| FR-1270 | A Scheme-E channel's motif data is one of a small, fixed set of motif variants, each a complete sequence of absolute scale-degree targets for one full motif-step cycle; variant index 0 specifies exactly the motif sequence already shipped. | ADS-102 §3/§5 (FR-candidate 1) |
| FR-1280 | On the frame a Scheme-E channel's motif-step counter completes a full cycle (wraps back to its first step), the engine selects the motif variant that will be used for the following cycle via a weighted, non-uniform selection among the defined variants — with no button input required. | ADS-102 §2/§5 (FR-candidate 2) |
| FR-1290 | The motif-variant selection weighting favors the channel's currently-active variant over switching to a different one on most cycle-boundary selections, rather than choosing uniformly among all defined variants each time. | ADS-102 §3/§5 (FR-candidate 3) |
| FR-1300 | With motif-variant selection held at variant index 0 for an entire run, a Scheme-E channel's onset-by-onset pitch sequence is identical to the sequence produced before motif variants were introduced — no regression to the previously shipped single-motif behavior. | ADS-102 §5 (FR-candidate 4) |
| FR-1310 | The engine cycles autonomously through 4 named song-form phases (intro, build, peak, breakdown), looping back to the first after the last, with no button input required. | ADS-103 §5 (FR-candidate 1) |
| FR-1320 | On each song-form phase transition, the engine overwrites `TEMPO_IDX`/`DENSITY_IDX` to that phase's documented target values on the same tick as the transition, not gated to any future event. | ADS-103 §5 (FR-candidate 2) |
| FR-1330 | Bad-zone detection/recovery (`FR-1080`-`FR-1110`) and Scheme-E motif-variant selection (`FR-1270`-`FR-1300`) both operate identically regardless of the current song-form phase — no phase-specific logic exists in either mechanism. | ADS-103 §5 (FR-candidate 3) |
| FR-1340 | Over a sufficiently long run, all 4 song-form phases occur in their defined cyclic order with no hang or stall. | ADS-103 §5 (FR-candidate 4) |
| FR-1350 | The visualizer displays 5 indicators, one each for `TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`, and `CHMIX_IDX`, each rendered as a filled-bar-height glyph proportional to that parameter's current index. | ADS-104 §5 (FR-candidate 1) |
| FR-1360 | Each of the 5 settings indicators updates within the same frame its underlying parameter changes, with no perceptible lag beyond the existing per-frame visualizer update cadence. | ADS-104 §5 (FR-candidate 2) |
| FR-1370 | The 5 settings indicators do not alter the existing channel-activity tiles' or calm/bad-zone palette's behavior — their addition is purely additive to the visualizer's existing output. | ADS-104 §5 (FR-candidate 3) |
| FR-1380 | At least one settings indicator demonstrably reflects a manual D-pad/A/B/Start-driven parameter change, confirmed by reading the relevant tilemap cell's pattern index after the corresponding button press. | ADS-104 §5 (FR-candidate 4) |
| FR-1390 | The engine maintains a derived `AROUSAL` value (range 0-15) that is a deterministic, monotonically non-decreasing function of `TEMPO_IDX` and `DENSITY_IDX` — increasing either input never decreases `AROUSAL`, holding the other constant. | ADS-105 §5 (FR-candidate 1) |
| FR-1400 | The engine maintains a derived `VALENCE` value (range 0-15) via a fixed, deterministic one-to-one mapping keyed by `SCALE_IDX` — each of the 4 scale/mode values maps to exactly one `VALENCE` output. | ADS-105 §5 (FR-candidate 2) |
| FR-1410 | `AROUSAL`/`VALENCE` are recomputed on every write to any of `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`, such that no more than one frame after any such write, both values reflect the post-write inputs. | ADS-105 §5 (FR-candidate 1/2, §2 trigger-site enumeration) |
| FR-1420 | `AROUSAL`/`VALENCE` hold correct values (matching the boot-preset steering indices) on the very first rendered/tested frame after boot, and hold correct values (matching the restored preset indices) on the same frame a Select-reset completes — neither is left stale pending a subsequent input edge. | ADS-105 §5 (FR-candidate 3/4) |
| FR-1430 | The visualizer's non-bad-zone palette is selected by a table lookup keyed by `CHMIX_IDX`, applied every frame `BAD_ZONE_FLAGS` is clear — not only at the moment `CHMIX_IDX` changes. | ADS-106 §5 (FR-candidate 1) |
| FR-1440 | The `CHMIX_IDX`=0 row of that lookup table produces a palette identical to the calm palette already shipped — selecting preset 0 introduces no visual change from current shipped behavior. | ADS-106 §5 (FR-candidate 2) |
| FR-1450 | Whenever `BAD_ZONE_FLAGS` is non-zero, the visualizer's palette is the existing bad-zone warning palette unconditionally, regardless of the current style-theme selection — the bad-zone override is absolute, not a blend or a priority tie-break. | ADS-106 §5 (FR-candidate 3) |
| FR-1460 | At least 3 non-default style-theme palettes each produce a color combination distinguishable, by content review, from the default theme and from each other. | ADS-106 §5 (FR-candidate 4) |

## Non-Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| NFR-1000 | The ROM builds to a fixed size with a valid header (correct logo, checksum, GBC compatibility flag) via `build_rom.py`, with no external assembler. | MSTR-001 C1/C3 |
| NFR-1010 | The per-frame VBlank ISR work (joypad edges + engine tick + visualizer update) completes within the VBlank-to-next-frame budget with no dropped frames, verified by driving the headless suite for an extended run (thousands of frames) with no hang/slowdown. **Caveat added 2026-07-26, corrected and widened 2026-07-31** (`BL-0060`/`BL-0069`, per [GDS-06 §2.2a](../architecture/06-non-functional-requirements.md)): the extended-run method remains the primary check but is **no longer sufficient on its own for any package adding per-frame work at all**. ~~`IP-1110` shipped a reproducible case where that frame's VRAM writes are dropped~~ — that case was falsified by direct measurement; no write is dropped and the harness cannot observe one (`R301` §3). The real finding is broader: `read_joypad`+`apply_input`+`engine_tick` consume ~9 of VBlank's 10 scanlines on **every** frame, idle included, leaving `update_visuals` about one scanline (`R101` §8.5). The original caveat named only the Select-reset frame and `update_visuals`, which is too narrow — no frame class is special. A stress run cannot detect this in any case: exhausting the VBlank window produces no hang, no slowdown and no dropped frame, the only three things the run watches for. Such a package states its per-frame cost impact explicitly; `IP-9030` v2 adds the falsifiable `LY` budget check this caveat has stood in for. **Implemented 2026-07-31**: `IP-9030`'s `VIS_ENTRY_LY` diagnostic + `test_rom.py`'s `T19` suite now supply exactly this check. | R100 cycle-budget note, GDS-06 §2.2a; `IP-9030`; `test_rom.py` `T19` |
| NFR-1020 | Every shipped behavior (FR-1000 through FR-1120) has at least one headless PyBoy test that drives a button sequence and asserts on sound-register and/or WRAM engine-state changes. | MSTR-001 C9 |
| NFR-1030 | Threshold/preset constants (tempo table, octave table, scale table, density table, channel-mix table, dissonance/stale/overload thresholds) live in one clearly-labeled data block in `music_engine.py`, tunable without touching generation logic. | GDS-03 §6 |
| NFR-1040 | Arpeggio/vibrato/portamento (FR-1130/FR-1140/FR-1150) each add bounded per-channel WRAM scratch state (a sub-tick/phase/glide counter per pitched channel) and bounded ROM-resident tables (an arpeggio-interval table, a vibrato depth/rate table) — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal). | MSTR-001 C2/§4, GDS-07 §6, strategic assumptions register A5 |
| NFR-1050 | Arpeggio/vibrato/portamento's added per-frame work (sub-tick cycling, phase-counter advance, glide-step computation) fits within the existing VBlank-tick budget (NFR-1010) — verified by the same extended-run headless stress-test method already used for the shipped engine, not by static cycle analysis (R101's own "no gap yet" conclusion still applies; see NFR-1010). | R101, R308, NFR-1010 |
| NFR-1060 | Scheme E's motif table(s) (ROM-resident, fixed at build time) and any per-channel "current motif step" scratch state add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-100 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1070 | Generation-scheme selection introduces no new WRAM control byte and no new input control — the scheme assignment for each pitched channel is derived from the existing `CHMIX_IDX`/`CHMIX_MASKS` mechanism (`FR-1000`/`FR-1010`, `IP-9010`) each tick, the same way other per-channel constants are already Python-level, not stored, state. | ADS-100 §6/§7, ADR-0001 |
| NFR-1080 | The style data table (one row per `CHMIX_IDX` preset) and its one new WRAM byte (duty-cycle bias) add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-101 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1090 | Style selection introduces no new input control — it is triggered by the existing `CHMIX_IDX`/Start mechanism (`FR-1060`) already in use for channel-activity/scheme-select, reusing the same preset index rather than requesting a distinct control. | ADS-101 §6/§7 |
| NFR-1100 | The motif-variant table(s) and the motif-variant-selection weighting table (both ROM-resident, fixed at build time) and any per-channel "current motif variant" scratch state add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-102 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1110 | Motif-variant selection introduces no new input control and no new WRAM control byte beyond the single variant-index scratch field — selection happens autonomously at motif-cycle boundaries, the same class of no-input-required behavior already established for bad-zone detection/recovery (`FR-1080`-`FR-1110`). | ADS-102 §6/§7 |
| NFR-1120 | The song-form phase table and its scratch state add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-103 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1130 | The song-form state machine introduces no new input control — phase advancement happens autonomously on a per-frame timer, the same class of no-input-required behavior already established for bad-zone detection/recovery and motif-variant selection. | ADS-103 §6/§7 |
| NFR-1140 | The 8 new bar-height tile patterns and the 5 new settings-indicator tilemap cells add bounded ROM/VRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) and the measured tile-slot/tilemap headroom (`R104` §7-8), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-104 §6, MSTR-001 §4, GDS-07 §6, R104 §7-8 |
| NFR-1150 | The settings-indicator update (5 reads + 5 tilemap writes per frame) is VBlank-gated the same way every existing visualizer write already is, and its per-frame cost is comparable to the existing channel-activity update's own cost — verified against the existing VBlank-timing budget (NFR-1010), not by static cycle analysis alone. | ADS-104 §6, NFR-1010 |
| NFR-1160 | The settings-indicator feature introduces no new input control — it is a pure read-only display of existing tracked parameters, updated automatically as those parameters change under their own existing controls. | ADS-104 §6/§7 |
| NFR-1170 | The `AROUSAL`/`VALENCE` derivation adds **zero unconditional per-frame CPU cost** — it is invoked only from the write sites that can change its inputs (button-edge input steps, song-form phase transitions, style application, boot/Select-reset), never from an unconditional per-frame call in `engine_tick`'s own main body. Verified by call-graph inspection (which routines call the derivation, and whether that call is itself conditional/edge-triggered), not solely by the extended-run stress method (`NFR-1010`'s own caveat, `GDS-06` §2.2a, applies with full force here — a per-frame call cheap enough not to trip a stress-test would still violate this NFR's intent). | ADS-105 §6 (NFR-candidate 1), GDS-06 §2.2a, R101 §8.5 |
| NFR-1180 | `AROUSAL`/`VALENCE` (2 new WRAM bytes) add bounded WRAM — within the current 32KB single-bank budget's ample headroom (`GDS-07` §6), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5); the derivation's added cost at each trigger site is small relative to that site's own existing cost. | ADS-105 §6 (NFR-candidate 2/3), GDS-07 §6, MSTR-001 §4 |
| NFR-1190 | The style-theme palette lookup adds zero unconditional per-frame CPU cost beyond one indexed table read replacing one constant reference — the palette-write routine already runs every frame under the existing stateless re-render contract; this capability changes what it reads, not how often it runs or how much it does. | ADS-106 §6 (NFR-candidate 1), GDS-08 §5 |
| NFR-1200 | The new style-theme palette table adds bounded ROM — at most a handful of 8-byte palette rows, negligible against the measured free-ROM headroom (`R104` §7), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-106 §6 (NFR-candidate 2), R104 §7, MSTR-001 §4 |

## Open items carried to feature decomposition

- Exact preset table **values** (tempo BPMs, octave ranges, scale note-sets, Euclidean k/n pairs,
  channel-mix masks) and threshold **constants** are authored as data at `05-feature-
  decomposition`/`06-feature-specification`/first implementation package — this requirements pass
  fixes behavior shape, not tuning values (consistent with GDS-03 §6's own deferral).
- FR-1130-FR-1160's exact parameters (which 2-3 harmonic intervals the arpeggio uses, vibrato
  depth/rate, portamento glide-frame count, which duty-cycle values and how they're selected) are
  likewise data decisions deferred to feature decomposition/spec/implementation, same convention.
- FR-1180-FR-1220's exact parameters (the scheme-select bit position within `CHMIX_MASKS`'s spare
  bits 4-6, Scheme E's motif table contents/count, which `CHMIX_IDX` presets assign which scheme
  to which channel) are likewise data/preset decisions deferred to feature decomposition/spec/
  implementation — this pass fixes behavior shape (ADS-100's own "shape, not values" framing),
  same convention as every prior preset-table deferral.
- FR-1230-FR-1260's exact parameters (which 3+ styles map to which `CHMIX_IDX` presets, the exact
  tempo/density/scale/duty-bias values each style targets, the `DUTY_BIAS`-combination rule
  `BL-0038` flagged) are likewise data/implementation decisions deferred to feature decomposition/
  spec/implementation — `ADS-101` §3 already names 3 concrete candidate styles (Techno/Chiptune-
  Driving, Ambient/Lo-Fi, Holiday) as the recommended starting data, not yet baselined as
  requirement text since specific preset-table values are this project's established deferral
  point, same convention as every prior preset-table addition.
- FR-1270-FR-1300's exact parameters (the concrete `N_VARIANTS` count, the motif-variant table
  contents, and the weighting table's precise retention-vs-switch ratio, `BL-0042`) are likewise
  data/implementation decisions deferred to feature decomposition/spec/implementation — `ADS-102`
  §3 proposes 4 variants (variant 0 the existing shipped sequence) as a starting point, not yet
  baselined as requirement text, same convention as every prior preset/table-value deferral.
- FR-1310-FR-1340's exact parameters (each phase's target `TEMPO_IDX`/`DENSITY_IDX` values and
  duration) are likewise data/implementation decisions deferred to feature decomposition/spec/
  implementation — `ADS-103` explicitly leaves these as first-guess placeholders, same
  `BL-0005`-class deferral as every prior preset/table-value addition.
- FR-1350-FR-1380's exact parameters (the precise bar-tile pixel design, on-screen tilemap
  placement of the 5 new cells, and whether a static in-ROM control legend is ever added — `ADS-
  104`'s own §9 Open Questions) are likewise implementation/content decisions deferred to feature
  decomposition/spec/implementation, same `BL-0005`-class deferral as every prior visual/preset-
  value addition. `ADS-104`'s explicitly out-of-v1-scope follow-on (scheme/style/motif-variant/
  song-form-phase indicators reusing the same bar-tile mechanism) is not baselined here — it is a
  named future extension, not a requirement of this delta.

## Candidate Requirements

Untraceable-to-a-source or explicitly-unbuilt statements, **excluded from the numbered baseline**.

| ID | Candidate requirement | Why it is not baselined |
|---|---|---|
| CR-0001 | The visualizer contains at least one element whose *motion or animation timing follows the generated beat* (tempo-synced motion), distinct from displaying the tempo setting as a static value. | **Never built, never scheduled.** Split out of `FR-1120` on 2026-07-26 (`BL-0016`) per [GDS-08 §7](../architecture/08-presentation-architecture.md)'s three-part resolution. `IP-0006`'s own package doc named "tempo-synced motion" as its explicit non-scope; nothing since has built it. Kept as a candidate rather than deleted because it is a real and reasonable future capability (`R223` treats pitch/rhythm-driven visual mapping as well-grounded) — it simply has never been required of the shipped system, and `FR-1120` should not have implied it was. |
| CR-0002 | `AROUSAL`'s derivation additionally incorporates `CHMIX_IDX`-derived active-channel count as a third input (alongside `TEMPO_IDX`/`DENSITY_IDX`), per `R221`'s observation that active-channel count is itself a direct arousal-axis lever in the literature. | **Deliberately excluded from v1's baseline** (`BL-0080`, per `ADS-105` §9 OQ3). `FR-1390` is fully satisfiable, and citation-clean, from `TEMPO_IDX`/`DENSITY_IDX` alone — the same minimal-baseline discipline `ADS-105` already applied to excluding `DISSONANCE_SCORE` from `VALENCE`. Adding a third input widens the surface a v1 acceptance test must cover for a marginal, not-yet-requested richness gain. Kept as a candidate rather than dropped because `ADS-105` §2 confirms the architectural cost of adding it later is low — the trigger-site plumbing for a `CHMIX_IDX` change is already shared with `AROUSAL`/`VALENCE`'s other recompute triggers, so promoting this candidate later would not require new call sites, only a wider formula. |

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-07-22 | Added FR-1130 (arpeggio), FR-1140 (vibrato), FR-1150 (portamento), FR-1160 (duty-cycle variation), FR-1170 (percussion-synthesis trace, no new behavior), NFR-1040 (ROM/WRAM budget), NFR-1050 (per-frame timing budget). Delta update per `BL-0024` (user-directed R216 sound-design-techniques implementation). No existing FR/NFR changed. | `BL-0024`, grounded in `R216`. |
| 2026-07-25 | Added FR-1180 (scheme-select determines note-selection strategy), FR-1190 (scheme switch takes effect at next onset, mirroring `IP-9010`'s activity-mask behavior), FR-1200 (Scheme E onset timing reuses the Euclidean-pattern mechanism), FR-1210 (Scheme E pitch selection via a fixed motif), FR-1220 (bad-zone detection/recovery is scheme-agnostic), NFR-1060 (ROM/WRAM budget), NFR-1070 (no new WRAM control byte/input control). Delta update formalizing `ADS-100` §5's candidate FRs per `BL-0020`, now that `IP-9010` has shipped with the bit layout `ADR-0001`'s contingency assumed (bits 0-3 channel-active, confirmed against the actual shipped `CHMIX_MASKS` — no re-check needed). No existing FR/NFR changed. | `BL-0020`, grounded in `ADS-100`/`ADR-0001`. |
| 2026-07-26 | Added FR-1230 (`CHMIX_IDX` preset maps to a style data row), FR-1240 (style values applied immediately, not gated to next onset — the one behavioral contrast with `FR-1190`'s scheme-select timing), FR-1250 (at least 3 audibly-distinct styles), FR-1260 (preset-0 style matches shipped default, no regression), NFR-1080 (ROM/WRAM budget), NFR-1090 (no new input control). Delta update formalizing `ADS-101` §5/§6's candidate FRs/NFRs for R5 (Genre-Aware Style Presets). No existing FR/NFR changed. | Roadmap R5, grounded in `ADS-101`. |
| 2026-07-26 | Added FR-1270 (motif data is a small fixed set of variants, variant 0 matches the shipped sequence), FR-1280 (weighted variant selection at motif-cycle boundaries, no input required), FR-1290 (weighting favors retaining the current variant), FR-1300 (variant 0 held throughout a run reproduces pre-change behavior exactly, no regression), NFR-1100 (ROM/WRAM budget), NFR-1110 (no new input control/WRAM control byte beyond the variant-index field). Delta update formalizing `ADS-102` §5/§6's candidate FRs/NFRs for `BL-0010`'s motif-recurrence half. No existing FR/NFR changed. | `BL-0010`, grounded in `ADS-102`. |
| 2026-07-26 | Added FR-1310 (autonomous 4-phase song-form cycle), FR-1320 (phase transition overwrites tempo/density immediately), FR-1330 (bad-zone/motif-variant mechanisms are phase-agnostic), FR-1340 (all 4 phases occur in cyclic order over a long run), NFR-1120 (ROM/WRAM budget), NFR-1130 (no new input control). Delta update formalizing `ADS-103` §5/§6's candidate FRs/NFRs for roadmap R6 (song-form half of `BL-0010`). No existing FR/NFR changed. | Roadmap R6, grounded in `ADS-103`. |
| 2026-07-26 | **Corrective/precision pass — no new baseline IDs.** Reworded `FR-1120` to drop its tempo claim (`BL-0016`): the tempo *setting* display is real but owned by `FR-1350`, and tempo-*synced motion* was never built — split out as new `CR-0001` in a new **Candidate Requirements** section. Added a caveat to `NFR-1010` recording that its extended-run method is no longer sufficient alone for packages touching the Select-reset frame or `update_visuals` (`BL-0060`, per GDS-06 §2.2). Updated `FR-1120`'s Traces-to from "GDS-08 (pending)" to the now-authored GDS-08 §2/§3. Re-labelled `docs/requirements/INDEX.md`'s two `⛔ Planned` rows as deliberate deviations (`BL-0068`, per GDS-10 §3.1). **`BL-0040` investigated and found NOT to be a requirements defect** — see this pass's Delta Review. | `BL-0016`/`BL-0040`/`BL-0060`/`BL-0068`, grounded in the newly-authored GDS-06/GDS-08/GDS-10. |
| 2026-07-26 | Added FR-1350 (5 settings indicators, bar-height glyph per parameter), FR-1360 (each indicator updates same-frame as its parameter), FR-1370 (purely additive, no change to existing channel-activity/palette behavior), FR-1380 (at least one indicator demonstrably live-reflects a manual button change), NFR-1140 (ROM/VRAM budget), NFR-1150 (VBlank-gated, comparable per-frame cost), NFR-1160 (no new input control). Delta update formalizing `ADS-104` §5/§6's candidate FRs/NFRs for `BL-0051` (settings & control visibility). No existing FR/NFR changed. | `BL-0051`, grounded in `ADS-104`. |
| 2026-07-31 | Added FR-1390 (`AROUSAL` is a monotonic function of `TEMPO_IDX`/`DENSITY_IDX`), FR-1400 (`VALENCE` is a fixed one-to-one mapping keyed by `SCALE_IDX`), FR-1410 (both recomputed within one frame of any input write), FR-1420 (both correct on the first frame after boot and on a Select-reset's own frame), NFR-1170 (zero unconditional per-frame CPU cost — the load-bearing NFR, a direct response to `IP-9030`'s VBlank-budget measurement), NFR-1180 (bounded WRAM budget, bounded per-trigger-site cost). Delta update formalizing `ADS-105` §5/§6's candidate FRs/NFRs for roadmap R7 (Emotional/Energy Layer). Resolved `BL-0081` (exact derivation formulas) by keeping the baseline at the behavioral level — monotonicity and a fixed mapping, not literal lookup-table values, per this skill's own "no byte-level detail in requirements" rule; exact table contents are `07-implementation-planning`'s to propose. Resolved `BL-0080` (whether `AROUSAL` includes `CHMIX_IDX`-derived active-channel count) by explicitly scoping it out as new **`CR-0002`**, not baselined. No existing FR/NFR changed. | Roadmap R7, grounded in `ADS-105`. |
| 2026-07-31 | Added FR-1430 (style-theme palette selected by a `CHMIX_IDX`-keyed lookup, applied every frame `BAD_ZONE_FLAGS` is clear), FR-1440 (preset-0 theme matches the shipped calm palette exactly, no regression), FR-1450 (bad-zone palette unconditionally overrides the style theme), FR-1460 (at least 3 distinguishable non-default themes), NFR-1190 (zero unconditional per-frame CPU cost beyond one indexed read replacing one constant), NFR-1200 (bounded ROM budget, cited to `R104` §7's actual measured headroom). Delta update formalizing `ADS-106` §5/§6's candidate FRs/NFRs for roadmap R9 (Visual Evolution & Audio-Visual Synchronization), **scoped to `RM-9001` (style-reactive palette) only** — `RM-9002` (mood-reactive, `IP-1120`'s `AROUSAL`/`VALENCE` as first consumer) and `RM-9003` (accessibility) are explicitly out of scope for this pass, per `ADS-106`'s own deferral decisions, and carry no FR/NFR here. No existing FR/NFR changed. | Roadmap R9, grounded in `ADS-106`. |

## Delta Review — 2026-07-25 (`FR-1180`-`FR-1220`, `NFR-1060`/`1070`)

Reviewed this delta only (per the skill's own "not a wholesale regeneration" convention) for
duplicates, conflicts, ambiguities, missing requirements, impossible requirements, architecture
violations, and missing traceability:

- **No duplicate or conflicting requirement.** `FR-1180`-`FR-1220` introduce a genuinely new
  concept (generation scheme) orthogonal to every existing FR — none of `FR-1000`-`FR-1170`
  presumes a single note-selection strategy in a way this delta contradicts; `FR-1220` explicitly
  confirms `FR-1080`/`FR-1090`/`FR-1100` (bad-zone detection) is unaffected, closing the one place
  a conflict could plausibly have existed.
- **No architecture violation.** Each FR traces directly to `ADS-100`/`ADR-0001`; the ADR's own
  contingency (`IP-9010`'s bit layout) is satisfied — `IP-9010` shipped with bits 0-3 as
  channel-active, exactly as `ADS-100`/`ADR-0001` assumed, confirmed by re-reading
  `IP-9010-channel-mix-gating.md` and the shipped `CHMIX_MASKS` table together.
- **No missing requirement.** `ADS-100` §5/§6's four FR-candidates and two NFR-candidates all
  became baseline requirements (`FR-1200`/`FR-1210` split from one candidate for atomicity, per
  the skill's own "split ands" rule) — none silently dropped.
- **Traceability:** every new ID's Source Documents column cites `ADS-100`'s specific section (and
  `ADR-0001` where the ADR itself is the direct source, e.g. `FR-1180`'s scheme-selection
  mechanism). No candidate needed — every statement in `ADS-100` §5/§6 was traceable to the
  document itself, not invented here.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — no `FS-xxx`, Implementation
  Package, or test exists yet for this feature; correctly left honest rather than guessed. This is
  the expected state for a requirements-only delta pass, matching every prior FR addition's own
  initial state before `05`/`06`/`07`/`08` picked it up.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1070`-equivalent catalog row once picked up.

**Known pre-existing gap (not introduced by this update):** this project's first requirements
pass (run #1) authored FR/NFR content directly into this single file rather than the four
separate deliverables `04-requirements-engineering`'s own workflow specifies (a dedicated
`02-non-functional-requirements.md`, `03-requirements-review.md`, and
`04-requirements-traceability-matrix.md` were never authored). This delta update follows the
established single-file convention rather than unilaterally restructuring — the split is a
`refactor`-type backlog candidate for a future pass, not addressed here.

## Delta Review — 2026-07-26 (`FR-1230`-`FR-1260`, `NFR-1080`/`1090`)

Reviewed this delta only, same "not a wholesale regeneration" convention as the prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1230`-`FR-1260` introduce a genuinely new
  concept (style-driven coordinated parameter overwrite) orthogonal to every existing FR. The one
  place a conflict could plausibly arise — `FR-1240`'s "applied immediately" vs. `FR-1190`'s
  "takes effect at next onset" for the *same* `CHMIX_IDX` press — is not actually a conflict: the
  two govern different state (`FR-1190` governs scheme/channel-activity, both read per-onset by
  the generation routines already; `FR-1240` governs `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/duty
  bias, all read per-tick by existing code exactly like a manual D-pad/A/B change already is) —
  the timing difference is a deliberate, cited design decision (`ADS-101`'s own Decision Log), not
  an oversight, and is called out explicitly in `FR-1240`'s own text so a future reader isn't left
  to infer it.
- **No architecture violation.** Each FR/NFR traces directly to `ADS-101`; no ADR is directly
  implicated (this feature didn't need a new ADR — `ADS-101`'s own Decision Log carries its
  binding decisions).
- **No missing requirement.** `ADS-101` §5/§6's four FR-candidates and (implicitly) two
  NFR-candidates all became baseline requirements — none silently dropped. `ADS-101`'s Open
  Questions (`DUTY_BIAS` combination rule, Celtic/Holiday-motion follow-ups) are correctly *not*
  baselined here — they're implementation-level/future-scope decisions, not requirements gaps,
  already tracked as `BL-0038`/`BL-0039`.
- **Traceability:** every new ID's Source Documents column cites `ADS-101`'s specific section. No
  candidate needed — every statement in `ADS-101` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for R5.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1080`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (`FR-1270`-`FR-1300`, `NFR-1100`/`1110`)

Reviewed this delta only, same "not a wholesale regeneration" convention as every prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1270`-`FR-1300` introduce a genuinely new
  concept (motif *variant* selection) layered on top of, not contradicting, `FR-1210` (Scheme E
  selects its next scale degree by stepping through a fixed cyclic motif) — `FR-1210` still
  correctly describes the per-step lookup behavior; `FR-1270`-`FR-1300` add that *which* motif
  sequence is being stepped through can now change at cycle boundaries. No existing FR is
  weakened or overridden; `FR-1210`'s text needed no edit since it never asserted there is only
  ever one possible motif sequence, only that stepping is cyclic and fixed-per-cycle.
- **No architecture violation.** Each FR/NFR traces directly to `ADS-102`; no ADR is directly
  implicated (this feature didn't need a new ADR — `ADS-102`'s own Decision Log carries its
  binding decisions, the same pattern `ADS-101` already established).
- **No missing requirement.** `ADS-102` §5/§6's four FR-candidates and two NFR-candidates all
  became baseline requirements — none silently dropped. `ADS-102`'s Open Questions (concrete
  `N_VARIANTS`/weighting-curve values, per-channel `MOTIF_VARIANT_IDX` scoping, variant-authoring
  method, future R6 integration) are correctly *not* baselined here — implementation-level/
  future-scope decisions, not requirements gaps, already tracked as `BL-0042`/`BL-0043`.
- **Traceability:** every new ID's Source Documents column cites `ADS-102`'s specific section. No
  candidate needed — every statement in `ADS-102` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for this motif-recurrence work.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1090`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (`FR-1310`-`FR-1340`, `NFR-1120`/`1130`)

Reviewed this delta only, same "not a wholesale regeneration" convention as every prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1310`-`FR-1340` introduce a genuinely new
  concept (an autonomous song-form phase cycle) that writes the same `TEMPO_IDX`/`DENSITY_IDX`
  fields `IP-1080`'s style application (`FR-1240`) and the D-pad/B handlers already write —
  checked explicitly for conflict: `FR-1320`'s "overwrites... on the same tick as the transition"
  is the same "last write wins, no special-casing" contract `FR-1240` itself already established
  for a different trigger (Start press vs. an autonomous timer), not a new or contradictory rule.
  `FR-1330` explicitly confirms no interaction with bad-zone detection/recovery or motif-variant
  selection, closing the one place a real conflict could have existed (both mechanisms are
  scheme/phase-agnostic by the same construction `FR-1220`/prior delta reviews already verified).
- **No architecture violation.** Each FR/NFR traces directly to `ADS-103`; no ADR is directly
  implicated (`ADS-103`'s own Decision Log carries its binding decisions, same pattern
  `ADS-101`/`ADS-102` already established).
- **No missing requirement.** `ADS-103` §5/§6's four FR-candidates and two NFR-candidates all
  became baseline requirements — none silently dropped. `ADS-103`'s Open Questions (BUILD-phase/
  `OVERLOAD` tuning interaction, style-drift's eventual mechanism, exact phase values/durations,
  whether `SCALE_IDX`/`DUTY_BIAS` join the envelope) are correctly *not* baselined here —
  tuning/future-scope decisions, not requirements gaps.
- **Traceability:** every new ID's Source Documents column cites `ADS-103`'s specific section. No
  candidate needed — every statement in `ADS-103` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for R6.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1100`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (`FR-1350`-`FR-1380`, `NFR-1140`-`1160`)

Reviewed this delta only, same "not a wholesale regeneration" convention as every prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1350`-`FR-1380` introduce a genuinely new
  concept (a read-only settings-value display) that does not touch any existing engine-state
  write path — checked explicitly against `FR-1120` (the existing visualizer requirement,
  channel-activity/bad-zone only): `FR-1350`-`FR-1380` are additive to what `FR-1120` already
  requires, not a restatement or a contradiction of it. `FR-1370` explicitly confirms no
  interaction with the existing channel-activity/palette behavior, closing the one place a real
  conflict could have existed (a new visualizer write path competing with or altering an
  existing one).
- **No architecture violation.** Each FR/NFR traces directly to `ADS-104`; no ADR is directly
  implicated (`ADS-104`'s own Decision Log carries its binding decisions, same pattern
  `ADS-101`/`ADS-102`/`ADS-103` already established). `ADS-104` §2 explicitly preserves GDS-03
  §1's "visualizer never writes engine state" invariant — `FR-1350`/`FR-1360`/`FR-1380` are all
  phrased as read/display behavior only, consistent with that constraint.
- **No missing requirement.** `ADS-104` §5/§6's four FR-candidates and (in this case) three
  NFR-candidates all became baseline requirements — none silently dropped; the NFR set is one
  larger than the two-per-delta pattern of the three prior deltas because `ADS-104` §6 itself
  states three genuinely distinct non-functional concerns (ROM/VRAM budget, per-frame timing, no
  new input control) rather than two, and splitting them keeps each NFR atomic per this skill's
  own writing rules. `ADS-104`'s Open Questions (whether the four deferred per-feature indicators
  are ever built, whether a static in-ROM control legend is ever added, exact bar-tile pixel
  design, actual tilemap-layout headroom) are correctly *not* baselined here — future-scope/
  content/implementation decisions, not requirements gaps.
- **Traceability:** every new ID's Source Documents column cites `ADS-104`'s specific section. No
  candidate needed — every statement in `ADS-104` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for this settings-visibility work.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1110`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (corrective pass: `FR-1120`, `NFR-1010`, `CR-0001`, `BL-0040` adjudication)

A **corrective/precision pass**, not a new-feature formalization — no new baseline IDs were added.
Reviewed per the same "not a wholesale regeneration" convention as every prior delta.

- **`FR-1120`'s tempo claim, split (`BL-0016`).** The original text required the visualizer to
  represent "tempo, per-channel activity, and bad-zone status." [GDS-08 §7](../architecture/08-presentation-architecture.md)
  resolved this honestly in three parts, and this pass implements that resolution: the tempo
  *setting* is genuinely displayed now (`IP-1110`'s indicator bar) but is `FR-1350`'s claim, not
  `FR-1120`'s; tempo-*synced motion* was never built; so the original wording was satisfied on a
  narrow reading and overstated on the natural one. `FR-1120` now covers only per-channel activity
  and bad-zone status — both true since `IP-0006` — and the synced-motion claim moved to
  **`CR-0001`** in a new Candidate Requirements section, explicitly excluded from the baseline.
  This is the first Candidate Requirement this project has recorded; the section exists now for
  future use. **No requirement lost coverage**: the split moved a claim to a more accurate owner
  and demoted an unbuilt one, rather than dropping anything shipped.
- **`NFR-1010` gained a caveat, not a rewrite (`BL-0060`).** [GDS-06 §2.2](../architecture/06-non-functional-requirements.md)
  found that `R101`'s own stated cycle-tallying revisit trigger appears to have fired, and its
  merge decision explicitly left to this skill whether `NFR-1010` should point at that. It should:
  the requirement's extended-run verification method remains correct and primary, but `IP-1110`
  demonstrated a reproducible case it structurally cannot catch (a stress run with no Select press
  cannot exercise the Select-reset frame). The caveat records that limit without weakening the
  requirement — the method is still required, it is just no longer sufficient alone for one named
  class of package.
- **`BL-0040` investigated and found NOT to be a requirements defect — re-routed, not fixed.**
  The finding is that an absolute-sounding bad-zone-independence claim ("a style change does not
  alter `DISSONANCE_SCORE`/`BAD_ZONE_FLAGS`/`STALE_COUNT_*`/`ONSET_WINDOW_COUNT`") is true only
  narrowly, since `engine_tick` runs every frame and an unrelated channel's coincidental onset can
  touch those fields on the same frame (`VR-1080` measured ≈16% under adversarial play). It was
  routed to this skill on the assumption the imprecision lived in the FR text. **It does not.**
  Checked directly: no FR in `FR-1230`-`FR-1260` (the style range) states bad-zone independence at
  all, and the two FRs that *do* state independence claims of this shape — `FR-1220` (scheme) and
  `FR-1330` (song-form) — are both phrased at **mechanism level** ("no scheme-specific bad-zone
  logic exists" / "no phase-specific logic exists in either mechanism") rather than as same-frame
  guarantees, which is exactly the phrasing that keeps them accurate. The absolute claim exists
  only in **`FS-108`'s acceptance criterion (4)** (owned by `06-feature-specification`) and
  **`IP-1080`'s Definition of Done** (owned by `07-implementation-planning`). Nothing here to fix;
  `BL-0040` should be re-routed to those two owners.
  **Worth recording as a positive finding**: the FR baseline stayed accurate here *because* of a
  phrasing convention — state what logic exists, not what can never coincide — and future FRs of
  this shape should follow it.
- **`docs/requirements/INDEX.md` re-labelled (`BL-0068`).** The `02-requirements-review.md` and
  `03-rtm.md` rows read `⛔ Planned`, implying owed work. [GDS-10 §3.1](../architecture/10-requirements-traceability-matrix.md)'s
  reasoning is agreed with and adopted: review findings live inline as Delta Review sections (all
  eight present), and the RTM's information is distributed across artifacts already maintained,
  with independent verification a stronger gap-finder than a table. Both rows now read as
  deliberate, reasoned deviations.
- **No conflict, no duplicate, no architecture violation introduced.** `FR-1120`'s narrowing does
  not orphan any shipped behavior (`FR-1350` covers the indicator display); `NFR-1010`'s caveat
  strengthens rather than relaxes it; `CR-0001` is explicitly non-baselined.

No Critical/High finding. One item re-routed rather than resolved (`BL-0040` → `06`/`07`).

## Delta Review — 2026-07-31 (`FR-1390`-`FR-1420`, `NFR-1170`/`1180`, `CR-0002`)

New-feature formalization for roadmap R7 (Emotional/Energy Layer), same shape as every prior
per-release delta. Reviewed the four new FRs, two new NFRs, and one new Candidate Requirement
against the full existing baseline before closing.

- **Every new ID traces to `ADS-105`'s own §5/§6 candidates**, restructured for atomicity where
  the ADS's own wording conflated two properties. `ADS-105`'s FR-candidate 1 ("`AROUSAL` is a
  function of X, Y, recomputed whenever either changes") was split into `FR-1390` (the functional
  relationship) and `FR-1410` (the recompute-timing guarantee, covering both axes together since
  `ADS-105` §2 establishes they share trigger sites — a single atomic requirement for a
  single-mechanism guarantee, not two requirements that would always pass or fail together).
  Same split for FR-candidate 2 into `FR-1400`/`FR-1410`. FR-candidates 3/4 (boot-init, reset)
  merged into one `FR-1420` since both are the same "no stale-value grace period" property applied
  to two trigger events already covered together in `ADS-105`'s own trigger-site enumeration.
- **`BL-0081` resolved: acceptance criteria stay at the behavioral level, not literal formulas.**
  `ADS-105` recommended concrete lookup-table-style formulas but explicitly left the decision to
  this pass. Decided **against** baking in specific table values: `FR-1390` requires monotonicity
  (a testable, implementation-independent property — many concrete tables satisfy it) and
  `FR-1400` requires a fixed one-to-one mapping (also testable without committing to which mapping)
  rather than "AROUSAL = (TEMPO_IDX + DENSITY_IDX) at these exact indices." This follows this
  skill's own standing rule (a requirement naming byte-level detail has crossed into
  implementation) and the same discipline `GDS-07`/`GDS-09` apply project-wide — exact table
  contents are `07-implementation-planning`'s to propose against these acceptance criteria, not
  this baseline's to fix in advance.
- **`BL-0080` resolved: `CHMIX_IDX`-derived active-channel count excluded from v1, recorded as
  `CR-0002`.** `FR-1390` is fully satisfiable and citation-clean from `TEMPO_IDX`/`DENSITY_IDX`
  alone; adding a third input for marginal richness, with no current requester, would widen the
  acceptance-test surface for no baselined benefit. Kept as a candidate rather than dropped
  outright because `ADS-105` §2 confirms promoting it later costs little (the trigger-site
  plumbing for `CHMIX_IDX` changes already exists for other reasons) — the same reversibility
  reasoning `CR-0001` already established as this baseline's convention for "real future capability,
  not currently required."
- **No conflict with `FR-1120`/`CR-0001`, checked directly.** `FR-1120`/`CR-0001` concern the
  *visualizer's* observable output (tile/palette content, including the deferred tempo-synced-
  motion candidate); `FR-1390`-`FR-1420` concern a WRAM-resident derived value with **no
  visualizer consumer in this release** (`ADS-105` §2 states `visuals.py` is explicitly untouched
  — roadmap R9, separately blocked, owns the eventual visual consumption). Both requirement sets
  reference `TEMPO_IDX`, but one is about how tempo is *displayed* and the other is about how
  tempo *feeds a derived backend value* — adjacent territory, genuinely distinct claims, no
  overlap or restatement.
- **`NFR-1170` is this delta's load-bearing NFR and is cited to a live, in-session finding**
  (`IP-9030`'s VBlank-budget measurement, `R101` §8.5, `GDS-06` §2.2a) rather than to `ADS-105`
  alone — checked that this doesn't duplicate `NFR-1010`'s own caveat (added 2026-07-26, widened
  2026-07-31 to cover any package adding per-frame work): it does not. `NFR-1010`'s caveat is
  about the *verification method's* limits (a stress run cannot detect a narrowed margin);
  `NFR-1170` is a *design constraint on this specific package* (add zero unconditional per-frame
  cost, full stop) that would satisfy `NFR-1010`'s concern by construction rather than merely
  being tested against it. Complementary, not duplicate.
- **Forward traceability (Module/FS/IP/Test), updated 2026-07-31 now that `IP-1120` is
  `COMPLETE`:** `FR-1390`/`FR-1400`/`FR-1410`/`FR-1420`/`NFR-1170`/`NFR-1180` → Module
  `music_engine.py` (`_emit_mood_update`, called from `_emit_song_tick` and `init_engine`) +
  `input_map.py` (4 `_step_on_bit` call sites) · FS `FS-112` · IP `IP-1120` · Test `test_rom.py`
  `T20` (`T20.1`-`T20.4` FR-1390, `T20.5` FR-1400, `T20.6`-`T20.11` FR-1410, `T20.11`-`T20.12`
  FR-1420; `NFR-1170`/`NFR-1180` verified by call-graph inspection per their own Verification
  Method, not solely `T20`). Awaiting `09-package-verification`.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1120`-equivalent catalog row for roadmap R7.

## Delta Review — 2026-07-31 (`FR-1430`-`FR-1460`, `NFR-1190`/`1200`)

- **No duplicate or conflicting requirement.** `FR-1430`-`FR-1460` introduce a new visualizer
  capability (style-keyed theme palette selection) that is genuinely additive: nothing in the
  existing baseline states or implies a `CHMIX_IDX`-keyed palette lookup exists today.
- **Checked against `FR-1120`'s own split (`BL-0016`) and `CR-0001`.** `FR-1120` (as reworded)
  covers per-channel activity/bad-zone representation; `CR-0001` (not baselined) covers
  tempo-*synced motion*. Neither overlaps this delta: `FR-1430`-`FR-1460` are about which
  **palette** is active, not per-channel activity, tempo representation, or beat-synced motion.
  A style theme changing color is a different claim from a tile pulsing on the beat.
- **Checked against `FR-1370`** (`IP-1110`'s settings indicators are "purely additive... no change
  to existing channel-activity tiles' or calm/bad-zone palette's behavior"). No conflict: `FR-1370`
  is about the *indicator cells* not disturbing the *existing* calm/bad-zone swap; this delta
  changes what "the calm palette" *is* (a lookup instead of a constant) without touching the
  indicator cells at all, and `FR-1450` explicitly preserves the bad-zone swap's own priority.
- **`FR-1440`'s no-regression contract is load-bearing and mirrors the project's own established
  pattern** (`STYLE_TABLE`/`SONG_TABLE`/`MOTIF_TABLE` index-0 rows all carry the identical
  guarantee) — checked that this delta follows the same discipline rather than inventing a new
  one.
- **Scope boundary confirmed**: this pass baselines `RM-9001` only. `RM-9002` (mood-reactive,
  depending on `IP-1120`'s `AROUSAL`/`VALENCE`) and `RM-9003` (accessibility, `BL-0021`) are
  named in `ADS-106` but deliberately carry no FR/NFR here — the same exclusion discipline the R7
  delta applied to `CR-0002`. Both remain candidates for a future delta pass once their own
  packages are scheduled.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for R9.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add an
R9-equivalent catalog row.
