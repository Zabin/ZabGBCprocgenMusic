---
name: 08-content-authoring
description: Implement exactly one approved, eligible content-scoped Implementation Package — visualizer tile pixel art, visualizer scene/pattern layouts, palettes, and curated musical building blocks such as scale/mode tables and rhythm/preset templates (the data halves of tiles.py, patterns.py, music_data.py) plus the test_rom.py checks that verify them — rebuild the ROM, run the full suite, and advance the package on the Master Build Plan. Use when asked to implement a content package ("draw the new visualizer tile set," "add the new scale/preset table," "lay out the new visualizer pattern," "implement IP-xxxx" where the package names this skill). Peer of 08-code-implementation, which owns engine logic and build machinery; this skill never edits music_engine.py/visuals.py/input_map.py/gbc_lib.py/build_rom.py beyond the data-registration hook its package explicitly names (e.g. a put() call in build_tile_data() or a pattern registration in ALL_PATTERNS). Verification to VERIFIED belongs to 09-package-verification; qualitative review belongs to 09-content-review.
---

# Content Authoring

The stage-08 peer that owns Driftune's **content**: visualizer tile art, visualizer scene/pattern
layouts, palettes, and the curated musical building blocks (scale/mode tables, rhythm and preset
templates) that the generator draws from at runtime. Same discipline as `08-code-implementation`
— one approved, eligible package per invocation, faithful to the package, full suite green after —
with a content-shaped write surface and content-shaped verification.

Note the seam this peer sits on: the *generation algorithm itself* (how the engine chooses among
scales, how it varies tempo, how it decides density) is runtime logic and belongs to
`08-code-implementation`'s `music_engine.py`. This skill owns the *curated data tables* that
algorithm consumes and selects from — a scale definition, a rhythm template, a named preset — not
the selection logic. A package that blurs this line should have been split at stage 07; if it
wasn't, implement only this skill's half and file the seam problem as an Outstanding Issue.

## Write scope (G1)

- `tiles.py` — visualizer tile pixel arrays, `TL_*` constants, `put()` registrations in
  `build_tile_data()`.
- `patterns.py` — visualizer scene/animation-pattern generator functions, `ALL_PATTERNS` (the
  registered set of tile/palette layouts the visualizer can display, analogous to a screen table).
- `music_data.py` — scale/mode tables, rhythm and tempo-preset templates, named starting-state
  presets — the static musical building blocks `music_engine.py` selects from and varies at
  runtime, not the selection/variation logic itself.
- `test_rom.py` — checks verifying the new content (tile non-zero/bitplane checks, pattern-content
  checks, scale/rhythm-table checks), extending the existing suite pattern.
- Palette definitions in `build_rom.py` **only if** the package explicitly names them (colors
  live there today; a palette-only package is legitimate content work).

Everything else — generation logic, ISRs, register writes, ROM layout, WRAM — is
`08-code-implementation`'s surface. A package needing both surfaces should have been split at
stage 07; if it wasn't, implement only this skill's half and file the seam problem as an
Outstanding Issue.

## Workflow (mirrors the code peer; differences below)

1. **Select & gate** exactly as `08-code-implementation` Steps 0–1 (status `READY`, dependencies
   `VERIFIED`, explicit G3 authorization — no bootstrap carve-out applies to this project). The
   package must name this skill as its owner.
2. **Read the package + spec + the content quick-refs** — `memory.md`'s tile index map and
   palette tables, and GDS-07/GDS-08 once authored — before drawing or tabulating anything. Verify
   claimed tile slots are actually free and claimed patterns/constants exist.
3. **Mark `IN PROGRESS`**, then author the content per the package:
   - **Tiles:** 8×8 arrays in the established 2-bit color-index style; register via `put()` in an
     unused slot; keep the tile index map's conventions (see `memory.md`).
   - **Patterns:** generator functions returning the established (tiles, attrs) shape for a
     visualizer scene; respect the visible grid and any reserved status-indicator region (e.g. a
     bad-zone indicator) the spec names; keep any per-pattern parameter tables in the format the
     spec establishes.
   - **Music data:** scale/mode definitions, rhythm templates, and presets as the established
     tuple/table shape the engine consumes; keep frame/tempo-unit conventions consistent with
     `music_engine.py`'s expectations — this is curated static data, not generation logic.
   - **Budget:** every tile is 16 bytes, every pattern has its own byte cost, scale/rhythm tables
     are pointer-walked — state the byte cost against the GDS-07 section budget; overflow is a
     Blocking Report, not a squeeze.
4. **Verify (G5 + eyes/ears):** rebuild the ROM, run the full `test_rom.py`, **and** drive the
   affected patterns/presets in the emulator via `run-driftune` — capture visualizer screenshots
   and the sound-register values (NR1x-NR5x) the new content produces — content work is not done
   on green checks alone; the screenshots and register readouts go in the Implementation Summary
   for `09-content-review` to judge.
5. **Docs & traceability:** update `memory.md`'s tile/palette/scale quick-refs and any
   Documentation Updates the package names; fill the RTM cells for Requirements Covered.
6. **Ledger, summary, stop:** package → `COMPLETE`; Implementation Summary (same fields as the
   code peer, plus screenshot/register-readout paths); no second package.

## Blocking conditions & quality checklist

Identical in kind to `08-code-implementation` (drift, eligibility, authorization, budget
overflow → Blocking Report; full-suite green, scope discipline, traceability, honest summary) —
plus:

- [ ] New tiles registered in `build_tile_data()` and recorded in `memory.md`'s tile index map.
- [ ] Patterns/presets respect the grid and any reserved status-indicator conventions the spec
      names.
- [ ] Byte cost stated against the section budget.
- [ ] Screenshot(s) and sound-register readouts of the affected content captured and referenced in
      the summary.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 08 — Package Execution (content peer)** of the pipeline (see
[`.claude/skills/README.md`](../README.md)). Upstream: `07-implementation-planning`. Downstream:
`09-package-verification` (ledger verification) and `09-content-review` (qualitative review of
the rendered/sounded result).

End every run with the Implementation Summary plus:

1. **Recommendations** — Outstanding Issues with suggested owners.
2. **Next step** — after `COMPLETE`: `09-package-verification` on this package, then
   `09-content-review` for the rendered/sounded result (both before any dependent package builds
   on it); after a Blocking Report: whatever it names.

Never end a run without naming the next step.
