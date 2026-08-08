# ADS-104 — Settings & Control Visibility

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored 2026-07-26
- **Dependencies:** R205 (visualizer conventions), R208 (palette/color design — luminance/hue
  findings already grounding `CALM_PALETTE`/`BAD_PALETTE`), R104 §7-8 (VRAM/ROM tile-budget cost
  analysis — 254/256 tile slots free, ~29k+ free ROM bytes at last measurement), GDS-03 §1 (module
  ownership — `visuals.py` is a read-only consumer of engine state, never writes it), GDS-07
  (existing WRAM map for every parameter this design must read)
- **Produces:** a future `FS-xxx` (once `04-requirements-engineering` derives FRs from this
  document) and an eventual Implementation Package
- **Trigger:** `BL-0051` (user-filed via `00-intake`: "visuals that indicate the different
  settings in place and what the buttons influence") — unifying four previously-scattered Open
  Questions (`FS-107`/`108`/`109`/`110`'s own "should the visualizer gain an X-reactive signal?")
  that each deferred exactly this class of request to "a future intake request," now arrived

## 1. Executive Design Overview

The shipped visualizer (`IP-0006`/`FEAT-1040`) does exactly two things: 4 per-channel-activity
tiles (`CHANNEL_CELLS`, one per pitched/noise channel, lit when that channel's `NR52` bit is
active) and a whole-screen calm/bad-zone palette swap (`CALM_PALETTE`/`BAD_PALETTE`). It has never
shown the *value* of any tracked parameter, nor which button edits which parameter — a listener
discovers what Up/Down/Left/Right/A/B/Start do only by pressing them and listening for a change.
The user's request asks for exactly this gap to close, using "octave and tempo" as its own
concrete example — the two most listener-legible base parameters.

This design's core decision: add a second row of small, at-a-glance **parameter-level indicator
tiles** — one per base control (`TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`), each
rendered as a simple filled-bar-height glyph proportional to that parameter's current index
(0-7 → 0-7 filled rows within an 8×8 tile, the same "a number becomes a shape" idiom `R205`'s own
game-visualizer conventions already recommend for at-a-glance meters) — reusing the existing BG
palette mechanism, no new palette needed for v1. `CHMIX_IDX` is represented too (a 5th indicator,
since it's the 5th of the 6 base controls with a directly-displayable single value; Select has no
persistent "value" to display, it's a momentary action). The three *newer* mechanisms (Scheme
selection, `STYLE_TABLE`, `MOTIF_VARIANT_IDX`, `SONG_STATE`) are explicitly **out of this v1's
scope** — named, grounded follow-on work (§9), not solved here, keeping this pass scoped to the
user's own stated example ("octave and tempo") and the base-control legend gap, which is the
larger and more foundational absence.

## 2. System Architecture

`visuals.py` gains a new routine, `_emit_update_settings_row` (or equivalent), called from the
same `update_visuals` per-frame site `IP-0006`'s existing channel-activity/bad-zone update already
runs from — a read-only consumer exactly like the existing code (GDS-03 §1's "visualizer never
writes engine state" invariant is unchanged: this reads `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/
`DENSITY_IDX`/`CHMIX_IDX`, writes only to VRAM tilemap/tile-pattern cells, VBlank-gated the same
way every existing visualizer write already is).

```
update_visuals (existing, unchanged call site)
        │
        ├─ existing: channel-activity tiles (CHANNEL_CELLS, NR52-driven)
        ├─ existing: calm/bad-zone palette swap (BAD_ZONE_FLAGS-driven)
        └─ NEW: _emit_update_settings_row
                   reads TEMPO_IDX/OCTAVE_IDX/SCALE_IDX/DENSITY_IDX/CHMIX_IDX
                   writes 5 new tilemap cells, each showing that parameter's
                   current index as a filled-bar-height glyph (0-7 rows)
```

No new tile-pattern *mechanism* is invented — 8 pre-rendered bar-height tiles (one per possible
0-7 fill level) are added to the tile pattern set (`build_tile_data()`), the same way
`CHANNEL_CELLS`'s own on/off tile pair already works, just with 8 fill levels instead of 2. The 5
new tilemap cells simply select which of those 8 pattern indices to display, recomputed once per
frame (cheap: 5 reads + 5 tilemap byte writes, comparable to the existing channel-activity
update's own per-frame cost).

## 3. Domain Model

- **Settings-row indicator**: one of 5 new BG tilemap cells, each bound to exactly one base
  control's tracked parameter (`TEMPO_IDX`→tempo bar, `OCTAVE_IDX`→octave bar, `SCALE_IDX`→scale
  bar, `DENSITY_IDX`→density bar, `CHMIX_IDX`→mix-preset bar). Distinct from `CHANNEL_CELLS`
  (per-channel activity, unchanged) and from the calm/bad-zone palette (unaffected).
- **Bar-height tile set**: 8 new tile patterns (one per fill level 0-7), each an 8×8 2bpp glyph
  with `N` filled rows from the bottom (a simple, unambiguous "how full is this" shape — no text
  rendering needed, avoiding a font/glyph-table investment this project has never made).
- **Control legend**: not a runtime mechanism — the *fixed, static* association between each
  indicator's on-screen position and its control (e.g. "the leftmost bar is tempo, D-pad Up/Down")
  is a content/documentation concern (the box art / manual / a static help-screen tilemap row),
  not something the ROM computes at runtime. Named explicitly so it isn't silently assumed to be
  a dynamic feature (§7).

## 4. User Stories

- As a listener, glancing at the screen shows 5 small bar-height indicators alongside the
  existing 4 channel-activity tiles — pressing D-pad Up visibly raises the tempo bar one notch,
  immediately and legibly, the same frame the parameter itself changes (no new latency beyond
  the existing per-frame visualizer update already has).
- As a listener who has never read documentation, the *existence* of 5 distinct bars invites
  experimentation ("what does this one do?") even before any external legend is consulted —
  though full comprehension of *which* bar maps to *which* button still requires the static
  legend (a manual/box-art concern, §3), not something the ROM alone can convey without a
  further text/iconography investment this design deliberately doesn't make in v1.
- As a developer extending this later (§9), the 8-level bar-tile mechanism is directly reusable
  for a future style/motif-variant/song-phase indicator — the same tile-budget-conscious
  approach, not a one-off.

## 5. Functional Requirements (candidate — for `04-requirements-engineering` to formalize)

- FR-candidate: The visualizer displays 5 indicators, each showing the current index (0-7) of
  `TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`, and `CHMIX_IDX` respectively, as a
  filled-bar-height glyph.
- FR-candidate: Each indicator updates within the same frame its underlying parameter changes
  (no perceptible lag beyond the existing per-frame visualizer update cadence).
- FR-candidate: The 5 new indicators do not alter the existing channel-activity tiles or
  calm/bad-zone palette behavior — purely additive.
- FR-candidate: At least one indicator (any) demonstrably reflects a manual D-pad/A/B/Start
  change live, confirmed by `09-content-review`/a headless test reading the relevant tilemap
  cell's pattern index after a button press.

## 6. Non-functional Requirements (candidate)

- ROM/VRAM budget: 8 new tile patterns × 16 bytes (2bpp, 8×8) = 128 bytes ROM; 5 new tilemap
  cells (already-existing tilemap space, no new VRAM region) — negligible against the measured
  ~254/256-free tile-slot headroom (`R104` §7-8) and free-ROM headroom (`ADR-0002`'s
  instrumentation).
- Performance: 5 reads + 5 tilemap writes per frame, VBlank-gated the same way every existing
  visualizer write already is (GDS-03's own timing-discipline invariant, unchanged) — comparable
  cost to the existing 4-cell channel-activity update.
- No new input control (this is a pure display feature).

## 7. Constraints

- **No new palette** — v1 reuses the existing BG palette mechanism; a bar-height glyph's shape
  (not color) conveys the value, sidestepping any new hue/luminance design question `R208` would
  otherwise raise.
- **No dynamic on-screen text/legend** — this project has no font/glyph-rendering investment;
  which indicator maps to which control is a static, off-ROM concern (box art/manual), named
  explicitly so a future spec doesn't silently assume the ROM itself explains the mapping.
- **Read-only visualizer invariant preserved** — `visuals.py` still never writes engine state
  (GDS-03 §1), consistent with every prior visualizer change.
- **Scheme/style/motif-variant/song-phase indicators are out of v1 scope** — named, grounded
  follow-on work (§9), not solved here; keeps this pass scoped to the user's own stated example.

## 8. Risks

- **5 additional tilemap cells may compete for on-screen space** with the existing 4
  channel-activity cells depending on the actual tilemap layout `IP-0006` chose — this design
  assumes free tilemap real estate exists (consistent with the tile-*pattern*-slot headroom
  `R104` already measured) but does not re-verify tilemap *layout* space directly; flagged for
  `07-implementation-planning`/`08-code-implementation` to confirm against the actual shipped
  tilemap arrangement, not assumed here.
- **A bar-height glyph alone may not be legible enough** without the external static legend —
  a real `09-content-review` judgment call (does "5 bars, no labels" actually read as useful, or
  does it need at least a 1-tile icon per bar to hint at its identity?), not resolved here.
- **`CHMIX_IDX`'s bar doesn't distinguish channel-mix from scheme-select from style** (it's one
  index driving three different mechanisms per `ADS-100`/`ADS-101`) — the bar shows *which
  preset* is active, not *what each preset means*; this is an accepted v1 limitation, not a defect,
  since decoding preset meaning already requires the same external legend the base controls do.

## 9. Open Questions

- **Should Scheme-select (`ADS-100`), style identity (`ADS-101`), motif-variant (`ADS-102`), and
  song-form phase (`ADS-103`) each eventually get their own indicator too**, using the same
  8-level bar-tile mechanism this design establishes? Deliberately deferred past v1 — this closes
  the four scattered per-feature Open Questions collectively by naming the *general mechanism*
  (reusable bar-tiles) rather than four bespoke ad hoc signals; a natural v1.1+ extension once v1
  ships and its own legibility is content-reviewed, not built here.
- **Should the static control legend (which bar = which button) be represented anywhere in-ROM**
  (e.g. a help/pause screen), or remain purely external (manual/box art)? Genuinely open — a
  scope decision for whoever picks up `04-requirements-engineering`/`06-feature-specification`,
  not resolved at the architecture stage; this design's v1 assumes external-only.
- **Exact bar-tile pixel design** (which fill pattern reads most clearly at Game Boy Color's
  actual screen size/viewing distance) is a content-authoring/tuning decision, not fixed here —
  same `BL-0005`-class deferral as every other visual/preset-value decision in this project.
- **Does the actual shipped tilemap layout have free cells for 5 more indicators** without
  crowding the existing 4 channel-activity cells? Flagged in Risks (§8) for the implementing
  package to confirm directly against `visuals.py`'s current tilemap arrangement, not assumed.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-26 | Settings visibility ships as 5 new bar-height indicator tiles (one per base control: tempo/octave/scale/density/channel-mix), reusing the existing BG palette mechanism — no new palette, no font/text rendering. | Directly answers the user's own stated example ("octave and tempo") and the base-control legend gap, which is the largest, most foundational absence — cheaper and more legible than text rendering (which this project has never built) and reuses `R205`'s own "a number becomes a shape" convention. |
| 2026-07-26 | Scheme/style/motif-variant/song-form-phase indicators (the four previously-scattered per-feature Open Questions) are unified into one named, deferred follow-on using the *same* bar-tile mechanism, rather than solved individually or all at once now. | Keeps this pass scoped to what the user actually asked for; the reusable mechanism this design establishes (8-level bar tiles) is the right foundation for those four follow-ons once picked up, avoiding four bespoke one-off signals. |
| 2026-07-26 | The control-to-indicator legend (which bar means which button) is a static, off-ROM concern (manual/box art), not an in-ROM dynamic feature, for v1. | This project has no font/glyph-rendering investment; building one solely for a legend would be a disproportionate new capability for what a static external legend already solves cheaply. |
