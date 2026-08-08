# R217 — UX Conventions for Generative Instruments (Seed Entry, Presets, Playback Controls)

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
  (lighter pass — most of this is out of GDS-01's current flat-design scope; documented so a
  future scope change has grounding, not because it's needed now)
- **Maps to user-provided research list:** Phase 7, items 81-88 (seed entry methods, menu design,
  visualization ideas, live parameter editing, preset management, song regeneration, pause/resume
  behavior, playback controls)

## 1. Purpose
Survey UX conventions for generative-music instruments/toys, honestly checked against GDS-01's
deliberate no-menu, no-pause, single-running-state design (MSTR-001 §4 non-goals) rather than
assumed as needed features.

## 2. Scope
Which of these 8 items are already answered by existing decisions, and which are genuinely
unaddressed future scope.

## 3. Concepts
- **Live parameter editing**: already shipped — this is exactly what R206's input-mapping
  research grounds (GDS-03 SS3). Not a gap.
- **Visualization**: already the subject of R205 (generative visualizer conventions) — not
  re-covered here, cross-referenced.
- **Playback controls / pause-resume**: explicitly a **non-goal** per MSTR-001 §4 ("no pause
  state") and GDS-01 SS ("no pause, no save, no exit... turning the device off is the only
  'stop'"). Not a gap — a deliberate design decision, restated here so this UX-research pass
  doesn't quietly reopen it.
- **Seed entry methods, menu design, preset management, song regeneration**: genuinely
  **unaddressed** — GDS-01's flat design has no menu state at all, so there is currently no UI
  surface for entering a seed, saving/loading a preset, or explicitly "regenerating." If R213's
  DIV-seeding idea (a different seed each boot) or a save-a-favorite-preset idea (MSTR-001 C2's
  named non-goal, "no SRAM/battery save... yet") were ever pursued, they would need real menu-
  design work this research pass does not attempt to originate (menu/UI design without an
  existing convention to cite would be this skill inventing a spec, which its own gotchas
  explicitly forbid).

### Sources
- Cross-references only (R205, R206, MSTR-001, GDS-01) — no new external citation needed; this
  topic's job is honestly triaging the user's list against decisions already made, not
  originating new UX conventions from outside sources this pass didn't find strong material for.

## 4. Operational Context
No code implication — confirms existing scope boundaries.

## 5. Implementation Guidance
- **No action needed** for live-editing, visualization, or playback-control items — already
  correctly scoped (shipped, researched elsewhere, or a deliberate non-goal respectively).
- **If seed-entry/preset-save/regeneration scope is ever requested**, it re-enters via `01-vision`
  (a menu state is a scope change to GDS-01's flat interaction model, per that document's own
  change-control note) — not something this research topic should pre-design speculatively.

## 6. Feature Mapping
No current `IP-xxxx`. Confirms MSTR-001 §4 / GDS-01's existing non-goals.

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⛔ **EXCEPTION — confirms existing non-goals, produces no feature.** UX conventions for generative instruments (presets, undo, save/recall, visible parameter state). Its conclusion was that Driftune's deliberate *absence* of most of them is consistent with the ambient-instrument posture `MSTR-001` §4 and `GDS-01` already committed to — i.e. it validated a boundary rather than moving it. Cited by `ADS-100`, `ADS-101` and the strategic assumptions register, always in that confirming role. **One partial caveat worth naming**: the "make current parameter state visible" convention it documents *did* eventually ship, as `IP-1110`'s settings-indicator row — but by way of the user's own direct request and `ADS-104`, which cite `R205`/`R222`/`R223` rather than this topic. An honest exception with one near-miss, not a clean trace.

## 7. Related Topics
R205 (visualizer), R206 (input mapping, the "live editing" this topic confirms is answered), R213
(seed management options this topic's "seed entry" item would need a menu for, if ever pursued).
