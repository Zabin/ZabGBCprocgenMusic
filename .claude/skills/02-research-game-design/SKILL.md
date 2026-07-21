---
name: 02-research-game-design
description: Produce or refresh citation-grounded research on procedural-music and generative-visual design for the Driftune GBC music engine — algorithmic composition techniques for chiptune (scale/mode selection, tempo and rhythm generation, voice-leading and density control across four channels), "bad zone" / dissonance-and-repetition detection heuristics, generative visualizer conventions (tile/palette animation synced to tempo, voice activity, register state), button-to-musical-parameter mapping conventions, and GB-era chiptune composition & channel-usage idioms — as docs/research/encyclopedia/R2xx-* topics. Use when asked to research procedural-music/visualizer-design questions, to add/extend R2xx topics, or to ground an FS-xxx that adds/changes a generation mode, a bad-zone metric, a button mapping, or a visualizer effect before it is specified. Not for hardware facts (02-research-gbc-hardware) or tooling (02-research-tooling-and-testing).
---

# Research: Procedural Music & Visualizer Design

Produces the **R200-tier encyclopedia** (`docs/research/encyclopedia/R201`–…) — the design
grounding for decisions about how the generated music should *sound*, how the visualizer should
*read*, and how player input should *steer* both, so feature specs cite convention and evidence
rather than taste. Tracked in [`docs/research/INDEX.md`](../../../docs/research/INDEX.md);
authored index-first.

## What this is for (and what it is not)

This skill answers: "if an agent is about to spec or tune a generation algorithm, a bad-zone
detector, a button-to-parameter mapping, or a visualizer effect, what do successful procedural-
music systems and chiptune-era games do, and why?" — never "write the spec itself" (that's stage
06) and never "decide this project's vision" (stage 01). Claims cite real sources: published
algorithmic-composition literature and postmortems, documented conventions of GB-era chiptune
composition, generative-art/visualizer design writing, and the project's own verified behavior
(`Claude.md` Known Good Behavior, `test_rom.py`). Numbers presented as recommendations ("a
density parameter above N active notes/beat in a 4-channel system reads as cluttered") must carry
the comparison or source that grounds them.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| `docs/research/encyclopedia/R2xx-*.md` + the R200 section of `docs/research/INDEX.md` | Suggested initial set (adjust to real gaps): R201 Algorithmic composition techniques for chiptune (scale/mode generation, motif variation, Markov/L-system approaches) · R202 Rhythm & tempo generation, groove and swing on a frame-driven clock · R203 Voice-leading & density control across a fixed small channel count (avoiding clashes/masking when 2-4 voices compete) · R204 "Bad zone" detection heuristics: dissonance metrics, repetition/staleness detection, channel-overload signals, and recovery-to-good-state design · R205 Generative visualizer conventions: syncing tile/palette animation to tempo, voice activity, and register state · R206 Button-to-musical-parameter mapping conventions (what feels controllable vs. chaotic when a D-pad/face-button steers scale, tempo, octave, density, channel mix) · R207 GB-era chiptune composition & channel-usage idioms (pulse/wave/noise role conventions) · R208 Palette & color design under CGB constraints for a non-game, audio-reactive display. |
| Design grounding targets | `music_data.py` (scale/rhythm/preset tables), `music_engine.py` (generation-algorithm constants, bad-zone thresholds), `input_map.py` (button/parameter constants), `visuals.py` (visualizer timing/response constants), and any FS-xxx touching generation behavior, bad-zone detection, input mapping, or the visualizer. |

**Author index-before-content**, same rule as the sibling tiers.

## Methodology (binding for every topic)

Same seven-section shape and citation rules as `02-research-gbc-hardware` (Purpose · Scope ·
Concepts · Operational Context · Implementation Guidance · Feature Mapping · Related Topics;
inline citations at the claim site; `### Sources` per `##` section; single-source claims flagged;
3–8 page band; if WebSearch/WebFetch are unavailable, mark citations "needs fetch-verification"
and report the gap). §5 Implementation Guidance must land on concrete statements tied to this
project's real files and constants — e.g. "density above 3 concurrent onsets across 4 channels
(currently unconstrained in `music_engine.py`) tends to read as noise rather than texture in the
algorithmic-composition literature; a bad-zone density threshold should sit below that," not "make
the music feel good."

## Workflow

1. **Read the trigger context** — which generation mode/bad-zone metric/button mapping/visualizer
   effect needs grounding, and which R2xx topic(s) own it.
2. **Check existing coverage first** in the R200 index section and topic files.
3. **If a gap exists:** index row first (`⛔ Planned`), then research, then write/update the topic
   per the methodology.
4. **Cross-link both directions**; flip the index status; update `ROADMAP.md`'s research theme
   row.
5. **Verify against the quality gate and commit** as `docs(research): R2xx — <what changed>`.

## Quality gate (before calling a topic/edit done)

- [ ] Every claim has an inline citation at the claim site; every `##` section has `### Sources`.
- [ ] §5 gives concrete do/don't statements tied to this project's real files/constants.
- [ ] Recommendations are grounded in comparison/evidence, not taste presented as fact.
- [ ] Frontmatter cross-references bidirectionally consistent; 3–8 page band held.

## Gotchas

- Design research **grounds** specs; it never quietly *becomes* a spec. "The engine should add a
  call-and-response phrasing mode" is intake (stage 00) + requirements (stage 04), not a research
  conclusion.
- The shipped engine is evidence too, once one exists: `Claude.md`'s Known Good Behavior list
  documents what already works and why a listener/player can rely on it — treat changes to it as
  expensive.
- This skill does not touch Tier R100 (hardware) or Tier R300 (tooling & verification).

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 02 — Research** of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md)). The three `02-research-*` skills are peers — run
whichever owns the tier the gap is in. Upstream: `01-vision`. Downstream:
`03-architecture-design-synthesis` (and whichever spec-authoring skill requested the grounding).

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — every topic produced or updated (paths), every index status flipped.
2. **Recommendations** — remaining coverage gaps, citation-verification gaps, and who owns each
   follow-up.
3. **Next step** — if this run closed a grounding gap requested by a downstream skill, return to
   that skill; if another research tier still has a gap for the current increment, name the
   sibling `02-research-*` skill; otherwise advance to `03-architecture-design-synthesis`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
