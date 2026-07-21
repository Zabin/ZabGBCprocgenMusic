---
name: 02-research-tooling-and-testing
description: Produce or refresh citation-grounded research on the build/verify toolchain for the Driftune GBC music engine — PyBoy emulator APIs and headless-driving patterns (including sound-register reads), Python-assembler codegen practices (label resolution, patch points), 2bpp tile encoding, ROM/header validation, sound-register- and memory-assertion-based test design, save-file handling across emulators — as docs/research/encyclopedia/R3xx-* topics. Use when asked to research emulation/testing/build-pipeline questions, to add/extend R3xx topics, or to ground an FS-xxx/IP-xxxx that touches gbc_lib.py, build_rom.py, or test_rom.py. Not for hardware register facts (02-research-gbc-hardware) or design conventions (02-research-game-design).
---

# Research: Tooling, Emulation & Verification

Produces the **R300-tier encyclopedia** (`docs/research/encyclopedia/R301`–…) — the grounding for
how this engine is *built and proven*, so packages that touch the toolchain cite real API behavior
rather than guesses. Tracked in [`docs/research/INDEX.md`](../../../docs/research/INDEX.md);
authored index-first.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| `docs/research/encyclopedia/R3xx-*.md` + the R300 section of `docs/research/INDEX.md` | Suggested initial set (adjust to real gaps): R301 PyBoy headless API (memory access incl. sound registers NR1x-NR5x, button input, tick/frame control, screenshots, `.ram` save files) · R302 Python-assembler codegen patterns (label resolution, patch-point dicts, section layout) · R303 2bpp tile encoding & palette data formats (for the visualizer) · R304 ROM validation (header checksum, size, cart-type fields) · R305 Emulator-based test design (sound-register assertions vs. memory-state assertions vs. pixel assertions, frame-count determinism, driving button sequences and asserting on engine-state transitions, save/reload harnesses) · R306 Toolchain portability (path conventions, CI-friendly builds, alternative emulators for cross-checking). |
| Grounding targets | `gbc_lib.py`, `build_rom.py`, `test_rom.py`, the `run-driftune` utility skill — every topic must trace to the real module(s) it constrains. |

**Author index-before-content**, same rule as the sibling tiers.

## Methodology (binding for every topic)

Same seven-section shape and citation rules as `02-research-gbc-hardware` (Purpose · Scope ·
Concepts · Operational Context · Implementation Guidance · Feature Mapping · Related Topics;
inline citations at the claim site; `### Sources` per `##` section; single-source claims flagged;
3–8 page band; unfetchable citations marked "needs fetch-verification" and reported). PyBoy's own
documentation/source and this repo's working `test_rom.py` are the primary sources for R301/R305
— verify API claims against the installed PyBoy version where possible and record the version.

## Workflow

1. **Read the trigger context** — which toolchain question needs grounding, which R3xx topic(s)
   own it.
2. **Check existing coverage first** in the R300 index section and topic files.
3. **If a gap exists:** index row first (`⛔ Planned`), then research (prefer primary docs/source
   + local experiment over blog posts — a 10-line PyBoy probe script run locally is Tier-A
   evidence; note the command and output in the topic), then write/update per the methodology.
4. **Cross-link both directions**; flip the index status; update `ROADMAP.md`'s research theme
   row.
5. **Verify against the quality gate and commit** as `docs(research): R3xx — <what changed>`.

## Quality gate (before calling a topic/edit done)

- [ ] Every claim has an inline citation (or a recorded local-experiment command + output).
- [ ] §5 gives concrete do/don't statements tied to `gbc_lib.py`/`build_rom.py`/`test_rom.py`.
- [ ] PyBoy version recorded for any API-behavior claim.
- [ ] Frontmatter cross-references bidirectionally consistent; 3–8 page band held.

## Gotchas

- Local experiments are allowed **read-only with throwaway scripts in the scratchpad** — this
  skill never edits the repo's production files (G1); a toolchain defect it finds (e.g. a
  hardcoded path in `build_rom.py`/`test_rom.py` that breaks portability) is a finding for
  intake/the manager, not a fix to make here — R306's §5 should inform whatever remediation
  package eventually ships, but the fix itself ships through 07→08.
- This skill does not touch Tier R100 (hardware) or Tier R200 (game design).

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
