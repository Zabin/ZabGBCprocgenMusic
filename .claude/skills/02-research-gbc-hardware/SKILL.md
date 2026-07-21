---
name: 02-research-gbc-hardware
description: Produce or refresh expert-level, citation-grounded research on Game Boy Color hardware and the SM83 CPU — PPU/VRAM/OAM timing, LCDC/STAT, CGB palettes, the four APU sound channels and their register map (NR1x-NR5x), interrupts, OAM DMA, joypad reads, cartridge header/checksums — to ground specs/features for the Driftune ROM pipeline. Use when asked to research GBC/SM83 topics, to add/extend docs/research/encyclopedia/R1xx-* topics, or to gather implementation-grounding facts before drafting an FS-xxx/IP-xxxx that touches the hardware surface (gbc_lib.py opcodes, music_engine.py ISRs/channel writes, input_map.py joypad reads, visuals.py VRAM writes). Not for beginner tutorials — every topic is written for an agent about to emit SM83 bytes that must be correct.
---

# Research: GBC Hardware & SM83

Produces the **R100-tier encyclopedia** (`docs/research/encyclopedia/R101`–…) — the hardware
facts an agent needs to not get a ROM wrong. The tier is tracked in
[`docs/research/INDEX.md`](../../../docs/research/INDEX.md), which lists the planned topics; this
skill authors them index-first.

## What this is for (and what it is not)

This skill exists to answer: "if an agent is about to implement or spec something touching the
PPU, VRAM timing, palettes, interrupts, DMA, the joypad, or the APU's four sound channels, what
does it need to know to not get it wrong" — never "explain what a Game Boy is." Every document
should be dense enough that an emulator author would not roll their eyes, and every claim must
trace to a real, cited source (Pan Docs, gbdev wiki/community docs, official-adjacent references,
or the project's own verified code/test behavior) — never invented timings, never register bits
from memory. Because Driftune's core purpose is real-time on-device sound generation, the R108
APU topic (and its interaction with R110's interrupt-driven timing) is this project's single most
load-bearing hardware topic — give it the depth the game-focused topics would give collision or
scrolling.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| `docs/research/encyclopedia/R1xx-*.md` + the R100 section of `docs/research/INDEX.md` | Implementation-grounding topics. Suggested initial set (adjust to real gaps): R101 SM83 instruction set & cycle costs · R102 PPU modes, VBlank & VRAM/OAM access timing · R103 LCDC/STAT registers · R104 CGB palette system (BCPS/BCPD, OCPS/OCPD, RGB15) · R105 OAM, sprites & OAM DMA · R106 MBC/SRAM (only if the design wants battery-backed persistence of e.g. last-good-state or user preferences) · R107 Joypad register & dual-read settling · R108 APU channels & register map (NR10-NR52: pulse/wave/noise channel control, frequency/volume envelopes, the frame sequencer) · R109 Cartridge header, checksums & boot requirements · R110 Interrupt model & ISR conventions (timer-driven generation ticks, VBlank-gated visualizer writes). |
| Engine grounding | `gbc_lib.py` (opcode emitters, header writer), `music_engine.py` (ISRs, channel-register writes, generation-tick timing), `input_map.py` (joypad IO constants), `visuals.py` (VRAM/palette writes), `build_rom.py` (ROM layout) — every topic must trace to the real module(s) it constrains. |

**Author index-before-content:** add the topic's row to the R100 table in
`docs/research/INDEX.md` (`⛔ Planned`, ID, title, one-line scope) before writing the file; flip
to `✅` when the quality gate passes.

## Methodology (binding for every topic)

- **Seven-section shape:** Purpose · Scope · Concepts · Operational Context · Implementation
  Guidance · Feature Mapping · Related Topics. **A document missing §5 Implementation Guidance
  has not done the job** — every concept must resolve to a concrete "do/don't do this in
  `gbc_lib.py`/`music_engine.py`/…" statement tied to real file paths and function/label names.
- **Inline-cite every register bit, timing figure, and named behavior at the claim site.** Every
  `##` section ends with a `### Sources` subsection (live URL + accessed date; add a Wayback
  snapshot where fetchable). The project's own `test_rom.py` results are a valid Tier-A source
  for "what this ROM verifiably does."
- **Flag single-source claims inline** — don't present a one-source number as settled fact.
- **3–8 page band** per topic; split rather than sprawl.
- If `WebFetch`/`WebSearch` are unavailable in the session, still author from well-established
  hardware facts but mark every unverifiable citation "needs fetch-verification" and report the
  gap in the completion summary so the manager files it.

## Workflow

1. **Read the trigger context.** What spec/feature/code change needs grounding? Identify which
   R1xx topic(s) are implicated.
2. **Check existing coverage first** — read the R100 index section and relevant topic files
   before assuming a gap; re-reading beats re-researching.
3. **If a gap exists:** index row first, then research with tiered sources (prefer primary
   hardware documentation and the project's own verified code/tests over blog summaries), then
   write/update the topic per the methodology.
4. **Cross-link both directions** — update Related Topics in siblings, and Feature Mapping on the
   FS-xxx spec(s) it grounds (metadata only).
5. **Flip the index status**, update `ROADMAP.md`'s research theme row, verify against the quality
   gate, and commit as `docs(research): R1xx — <what changed>`.

## Quality gate (before calling a topic/edit done)

- [ ] Every claim has an inline citation at the claim site.
- [ ] Every `##` section has a `### Sources` subsection.
- [ ] §5 Implementation Guidance gives concrete do/don't statements tied to real file paths and
      function/label names — not generic advice.
- [ ] Frontmatter Dependencies/Referenced By/Feature Mapping bidirectionally consistent.
- [ ] Nothing reads like novice-tutorial prose; file stays in the 3–8 page band.

## Gotchas

- Don't re-derive what `Claude.md`/`memory.md` already document about *this ROM specifically*
  (WRAM map, tile/channel-state index) — cite them; the encyclopedia adds the *hardware* grounding
  those documents assume.
- Common defect classes this tier exists to prevent: joypad dual-read settling errors, VRAM writes
  issued outside VBlank corrupting the visualizer, and APU register writes that don't respect the
  frame-sequencer's timing (a frequency/volume write landing on the wrong internal tick silently
  gets dropped or misapplied) — work these into §5 as concrete do/don't guidance before they ever
  become a shipped bug, not after.
- This skill does not touch Tier R200 (procedural-music & generative-visual design —
  `02-research-game-design`) or Tier R300 (tooling & verification —
  `02-research-tooling-and-testing`).

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 02 — Research** of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md)). The three `02-research-*` skills are peers — run
whichever owns the tier the gap is in. Upstream: `01-vision`. Downstream:
`03-architecture-design-synthesis` (and whichever spec-authoring skill requested the grounding).

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — every topic produced or updated (paths), every index status flipped.
2. **Recommendations** — remaining coverage gaps, citation-verification gaps, single-source
   claims needing a second source, and who owns each follow-up.
3. **Next step** — if this run closed a grounding gap requested by a downstream skill, return to
   that skill and resume the blocked artifact; if another research tier still has a gap for the
   current increment, name the sibling `02-research-*` skill; otherwise advance to
   `03-architecture-design-synthesis`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
