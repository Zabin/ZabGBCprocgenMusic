# R307 — Real-Time Audio Engine Architecture Patterns

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 6, items 69-80 (engine architecture, data-
  oriented design, music state machine, scheduler design, tick processing, event queue, instrument
  manager, voice allocator, pattern generator, song generator, playback controller, save/load seed
  architecture)

## 1. Purpose
Ground `music_engine.py`'s existing structure against general real-time-audio-engine architecture
convention, and name which of the 12 listed sub-concerns are already answered vs. genuinely new
scope for a channel-starved, no-OS, single-threaded SM83 target (a very different environment
from the desktop/embedded-with-RTOS engines most of this literature describes).

## 2. Scope
Real-time audio engine design conventions (thread separation, tick-based processing, voice
allocation, priority scheduling) and which parts transfer to a single-threaded, interrupt-driven,
no-dynamic-allocation SM83 target.

## 3. Concepts
- **Thread/determinism separation**: real-time audio engines conventionally keep the audio
  processing thread free of non-deterministic operations — "the audio thread does not allocate
  memory, does not call into system libraries that might block, and does not perform any operation
  that is not deterministic in duration; all non-deterministic work happens on the control thread"
  [search synthesis — Audiality architecture notes, linuxdj.com](https://www.linuxdj.com/maia/audiality/).
  **Directly applicable even without real threads**: Driftune's single-threaded VBlank-ISR-driven
  loop (R110) already satisfies this by construction — `engine_tick` never allocates (SM83 has no
  heap at all), never blocks, and its per-frame cost is already bounded (R108/R110's cycle-budget
  discipline). The "two-thread" pattern's *goal* (determinism) is met by a *different* mechanism
  (a single fixed-budget ISR-driven tick) appropriate to hardware with no OS/threads at all.
- **Tick-based processing / voice scheduling**: "audio signals are produced in groups of multiple
  samples per... tick," and multi-voice engines use "a priority stream scheduler... cells
  dynamically assigned priority levels" [same source]. Driftune's per-channel `NOTE_TIMER_*`
  countdown (R110/R215) is the tick-based half of this pattern; the priority-scheduling half is
  unnecessary at only 4 fixed-role channels (R203) — a general priority queue would be pure
  overhead for a fixed, small, statically-assigned voice count.
- **Data-oriented design**: for 4 channels' worth of state, GDS-07's flat WRAM byte-array layout
  (parallel `NOTE_TIMER_*`/`CUR_DEGREE_*`/history-buffer arrays, one slot per channel) already *is*
  data-oriented — there's no object/instrument abstraction layer to "flatten," the design never
  had one.

### Sources
- [linuxdj.com — Audiality Audio Engine: Synthesis Architecture and Design Notes](https://www.linuxdj.com/maia/audiality/)
- [Analog Devices — Planning for Success in Real-Time Acoustic Processing](https://www.analog.com/en/resources/technical-articles/planning-for-success-in-real-time-audio-processing.html)

## 4. Operational Context
`music_engine.py`/`build_rom.py`'s existing ISR-driven, per-channel-array structure already
matches the transferable parts of this literature; the non-transferable parts (thread separation,
priority scheduling, dynamic voice allocation) are correctly absent because they solve problems
this hardware/design doesn't have.

## 5. Implementation Guidance
- **No architectural change needed** — this topic confirms the existing shape rather than
  recommending a different one. Useful primarily as citable justification (in a future FS/ADR) for
  *why* Driftune's engine doesn't have an instrument-manager/voice-allocator abstraction layer:
  those solve a variable-voice-count problem Driftune's fixed-4-channel design doesn't have.
- **"Instrument manager" and "voice allocator"** (as named concepts) map to R216's per-channel
  timbre/duty/envelope parameters and R203's fixed channel-role assignment respectively — already
  answered, not a missing layer.
- **"Pattern generator" / "song generator"** map to R201/R211/R212's note/phrase/form generation
  — already surveyed there, not re-derived here.
- **"Save/load seed architecture"**: not built (MSTR-001 C2, no SRAM at v1) — cross-ref R213's
  seed-management options if this scope is ever revisited.

## 6. Feature Mapping
Confirms existing `IP-0001` architecture; no new `IP-xxxx` implication.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED (confirmation shape).** This topic confirmed the already-shipped `IP-0001` architecture rather than prescribing a change — a legitimate `MSTR-001` C10 exception shape ("grounds implementation *quality* rather than producing a standalone feature"), recorded explicitly here rather than left implicit. It is also the named grounding for the `08-refactoring` skill's own discipline.

## 7. Related Topics
R110 (the tick/ISR mechanism), R203 (fixed channel-role assignment, the "voice allocation"
answer), R213 (seed architecture), R308 (the performance-budgeting half of this same concern).
