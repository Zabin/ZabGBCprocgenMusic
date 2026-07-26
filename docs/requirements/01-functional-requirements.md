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
| FR-1120 | The visualizer reads `NR52`/`NR51` and the WRAM engine-state mirror and updates BG tile/palette content to represent tempo, per-channel activity, and bad-zone status, without writing to any engine-state or PSG register itself (read-only consumer). | GDS-03 §1, GDS-08 (pending) |
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

## Non-Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| NFR-1000 | The ROM builds to a fixed size with a valid header (correct logo, checksum, GBC compatibility flag) via `build_rom.py`, with no external assembler. | MSTR-001 C1/C3 |
| NFR-1010 | The per-frame VBlank ISR work (joypad edges + engine tick + visualizer update) completes within the VBlank-to-next-frame budget with no dropped frames, verified by driving the headless suite for an extended run (thousands of frames) with no hang/slowdown. | R100 cycle-budget note |
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

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-07-22 | Added FR-1130 (arpeggio), FR-1140 (vibrato), FR-1150 (portamento), FR-1160 (duty-cycle variation), FR-1170 (percussion-synthesis trace, no new behavior), NFR-1040 (ROM/WRAM budget), NFR-1050 (per-frame timing budget). Delta update per `BL-0024` (user-directed R216 sound-design-techniques implementation). No existing FR/NFR changed. | `BL-0024`, grounded in `R216`. |
| 2026-07-25 | Added FR-1180 (scheme-select determines note-selection strategy), FR-1190 (scheme switch takes effect at next onset, mirroring `IP-9010`'s activity-mask behavior), FR-1200 (Scheme E onset timing reuses the Euclidean-pattern mechanism), FR-1210 (Scheme E pitch selection via a fixed motif), FR-1220 (bad-zone detection/recovery is scheme-agnostic), NFR-1060 (ROM/WRAM budget), NFR-1070 (no new WRAM control byte/input control). Delta update formalizing `ADS-100` §5's candidate FRs per `BL-0020`, now that `IP-9010` has shipped with the bit layout `ADR-0001`'s contingency assumed (bits 0-3 channel-active, confirmed against the actual shipped `CHMIX_MASKS` — no re-check needed). No existing FR/NFR changed. | `BL-0020`, grounded in `ADS-100`/`ADR-0001`. |
| 2026-07-26 | Added FR-1230 (`CHMIX_IDX` preset maps to a style data row), FR-1240 (style values applied immediately, not gated to next onset — the one behavioral contrast with `FR-1190`'s scheme-select timing), FR-1250 (at least 3 audibly-distinct styles), FR-1260 (preset-0 style matches shipped default, no regression), NFR-1080 (ROM/WRAM budget), NFR-1090 (no new input control). Delta update formalizing `ADS-101` §5/§6's candidate FRs/NFRs for R5 (Genre-Aware Style Presets). No existing FR/NFR changed. | Roadmap R5, grounded in `ADS-101`. |
| 2026-07-26 | Added FR-1270 (motif data is a small fixed set of variants, variant 0 matches the shipped sequence), FR-1280 (weighted variant selection at motif-cycle boundaries, no input required), FR-1290 (weighting favors retaining the current variant), FR-1300 (variant 0 held throughout a run reproduces pre-change behavior exactly, no regression), NFR-1100 (ROM/WRAM budget), NFR-1110 (no new input control/WRAM control byte beyond the variant-index field). Delta update formalizing `ADS-102` §5/§6's candidate FRs/NFRs for `BL-0010`'s motif-recurrence half. No existing FR/NFR changed. | `BL-0010`, grounded in `ADS-102`. |

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
