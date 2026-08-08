# R206 — Button-to-Musical-Parameter Mapping Conventions

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose

Ground GDS-03 SS3's concrete input mapping (one control, one parameter, no menu layer) against
real generative-instrument interface-design convention.

## 2. Scope

"One control, one parameter" hardware-interface philosophy from modular-synthesizer design, as
the closest real-world analogue to a GBC controller steering a live generative engine.

## 3. Concepts

- **Eurorack modular synthesis's core interface philosophy**: "limiting the parameters available
  and providing physical knobs... for each of them... allows for hands-on control without
  menu-heavy interfaces" — an explicit, stated reaction against menu-diving interfaces (the
  article's own example: "lessons learned from earlier FM synths like the DX7," notorious for
  deeply nested menus hiding simple parameters) [Perfect Circuit / factmag-adjacent search
  synthesis — see Sources]. This is the same principle GDS-03 SS3 already applied ("no chords, no
  menu layer... each control owns exactly one knob") — this topic confirms it against a real,
  named interface-design tradition rather than leaving it an unsourced design instinct.
- Modern performance-oriented modular interfaces sometimes generalize to *assignable* controls
  ("freely assigned to any parameter"), but the base convention — and the one directly applicable
  to a **fixed, small, unlabeled control set** like a GBC pad (no display to show a current
  assignment) — is the fixed, one-to-one mapping: every control has one, discoverable-by-trial-
  and-error meaning, memorizable without a manual. A reassignable-control model would need some
  form of on-screen labeling to stay usable, which the visualizer (GDS-08, not yet designed) does
  not currently plan to provide.

### Sources
- Search synthesis of Eurorack interface-design discussion (multiple sources on modular synth
  control philosophy, "one knob one parameter" vs. menu-heavy competitors); no single canonical
  paper exists for this convention (it is design-community consensus, not published research) —
  flagged as such rather than over-citing a single source as definitive.

## 4. Operational Context

GDS-03 SS3's mapping table (D-pad Up/Down→tempo, Right/Left→octave, A→scale, B→density,
Start→channel-mix, Select→reset) already follows this convention exactly, and `IP-0001` shipped it
in full (all 6 controls, edge-triggered, wrapping indices). No implementation gap — this topic is
confirmatory grounding for a decision already made and shipped.

## 5. Implementation Guidance

- **Do not add an assignable/rebindable control layer** — it would need on-screen labeling
  (visualizer scope creep) to stay usable per the "no display" constraint above, and nothing in
  the current backlog asks for it.
- **If a future control is ever added** (e.g. a 7th/8th parameter needing a control this project
  doesn't have spare — GBC has no more discrete inputs left: 4 d-pad + A/B/Start/Select = 8, all
  already assigned), the fixed-mapping convention argues for **combining wraps rather than adding
  chorded input** (e.g. widen an existing control's own preset list) over inventing a hold/combo
  gesture, which breaks the "discoverable by trial and error" property this convention protects.

## 6. Feature Mapping

FR-1020–FR-1070 (shipped), GDS-03 SS3.

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `input_map.py`'s entire button→parameter mapping — which control steps which index, and the one-step-per-edge discipline that makes steering feel controllable rather than chaotic. Shipped via `IP-0001` (`VERIFIED`). Architecture: `GDS-03` §3, `GDS-09` §5. Requirements: `FR-1020`-`FR-1070`. Tests: `T4`, `T5`, `T18`.

## 7. Related Topics

R205 (visualizer — the "no display to label controls" constraint this topic leans on), R107
(the joypad hardware this mapping reads).
