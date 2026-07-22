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

## Non-Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| NFR-1000 | The ROM builds to a fixed size with a valid header (correct logo, checksum, GBC compatibility flag) via `build_rom.py`, with no external assembler. | MSTR-001 C1/C3 |
| NFR-1010 | The per-frame VBlank ISR work (joypad edges + engine tick + visualizer update) completes within the VBlank-to-next-frame budget with no dropped frames, verified by driving the headless suite for an extended run (thousands of frames) with no hang/slowdown. | R100 cycle-budget note |
| NFR-1020 | Every shipped behavior (FR-1000 through FR-1120) has at least one headless PyBoy test that drives a button sequence and asserts on sound-register and/or WRAM engine-state changes. | MSTR-001 C9 |
| NFR-1030 | Threshold/preset constants (tempo table, octave table, scale table, density table, channel-mix table, dissonance/stale/overload thresholds) live in one clearly-labeled data block in `music_engine.py`, tunable without touching generation logic. | GDS-03 §6 |
| NFR-1040 | Arpeggio/vibrato/portamento (FR-1130/FR-1140/FR-1150) each add bounded per-channel WRAM scratch state (a sub-tick/phase/glide counter per pitched channel) and bounded ROM-resident tables (an arpeggio-interval table, a vibrato depth/rate table) — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal). | MSTR-001 C2/§4, GDS-07 §6, strategic assumptions register A5 |
| NFR-1050 | Arpeggio/vibrato/portamento's added per-frame work (sub-tick cycling, phase-counter advance, glide-step computation) fits within the existing VBlank-tick budget (NFR-1010) — verified by the same extended-run headless stress-test method already used for the shipped engine, not by static cycle analysis (R101's own "no gap yet" conclusion still applies; see NFR-1010). | R101, R308, NFR-1010 |

## Open items carried to feature decomposition

- Exact preset table **values** (tempo BPMs, octave ranges, scale note-sets, Euclidean k/n pairs,
  channel-mix masks) and threshold **constants** are authored as data at `05-feature-
  decomposition`/`06-feature-specification`/first implementation package — this requirements pass
  fixes behavior shape, not tuning values (consistent with GDS-03 §6's own deferral).
- FR-1130-FR-1160's exact parameters (which 2-3 harmonic intervals the arpeggio uses, vibrato
  depth/rate, portamento glide-frame count, which duty-cycle values and how they're selected) are
  likewise data decisions deferred to feature decomposition/spec/implementation, same convention.

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-07-22 | Added FR-1130 (arpeggio), FR-1140 (vibrato), FR-1150 (portamento), FR-1160 (duty-cycle variation), FR-1170 (percussion-synthesis trace, no new behavior), NFR-1040 (ROM/WRAM budget), NFR-1050 (per-frame timing budget). Delta update per `BL-0024` (user-directed R216 sound-design-techniques implementation). No existing FR/NFR changed. | `BL-0024`, grounded in `R216`. |

**Known pre-existing gap (not introduced by this update):** this project's first requirements
pass (run #1) authored FR/NFR content directly into this single file rather than the four
separate deliverables `04-requirements-engineering`'s own workflow specifies (a dedicated
`02-non-functional-requirements.md`, `03-requirements-review.md`, and
`04-requirements-traceability-matrix.md` were never authored). This delta update follows the
established single-file convention rather than unilaterally restructuring — the split is a
`refactor`-type backlog candidate for a future pass, not addressed here.
