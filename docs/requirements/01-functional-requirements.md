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

## Non-Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| NFR-1000 | The ROM builds to a fixed size with a valid header (correct logo, checksum, GBC compatibility flag) via `build_rom.py`, with no external assembler. | MSTR-001 C1/C3 |
| NFR-1010 | The per-frame VBlank ISR work (joypad edges + engine tick + visualizer update) completes within the VBlank-to-next-frame budget with no dropped frames, verified by driving the headless suite for an extended run (thousands of frames) with no hang/slowdown. | R100 cycle-budget note |
| NFR-1020 | Every shipped behavior (FR-1000 through FR-1120) has at least one headless PyBoy test that drives a button sequence and asserts on sound-register and/or WRAM engine-state changes. | MSTR-001 C9 |
| NFR-1030 | Threshold/preset constants (tempo table, octave table, scale table, density table, channel-mix table, dissonance/stale/overload thresholds) live in one clearly-labeled data block in `music_engine.py`, tunable without touching generation logic. | GDS-03 §6 |

## Open items carried to feature decomposition

- Exact preset table **values** (tempo BPMs, octave ranges, scale note-sets, Euclidean k/n pairs,
  channel-mix masks) and threshold **constants** are authored as data at `05-feature-
  decomposition`/`06-feature-specification`/first implementation package — this requirements pass
  fixes behavior shape, not tuning values (consistent with GDS-03 §6's own deferral).
