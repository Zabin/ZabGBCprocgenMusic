# MSTR-001 — Program Vision: Driftune

- **Document ID:** MSTR-001 · **Version:** 1.2 · **Status:** ✅ Authored (from-scratch increment
  — no shipped ROM exists yet; this vision is the origin of the project, not a restatement of
  existing code)
- **Date:** 2026-07-21 (v1.0); 2026-07-21 (v1.1 — see §8); 2026-07-22 (v1.2 — see §8) · **Owned
  by:** `01-vision` skill
- **Derived from:** the project owner's initial instruction (2026-07-21): build a standalone GBC
  ROM whose primary purpose is real-time procedurally-generated chiptune music, with
  music-reactive visuals, player-steerable generation parameters, and a "bad zone" detection +
  reset mechanic; verified headlessly via PyBoy in the same spirit as the harvested reference
  project's `test_rom.py`.
- **Design-facing restatement:** [`docs/architecture/00-vision.md`](../architecture/00-vision.md)
  (GDS-00)

## §0 Provenance — what is harvested vs. what is new

This project's **documentation-driven-development pipeline** (this skill hierarchy, the
journal/backlog mechanism, the G1–G5 governance rules) and its **assembler toolchain foundation**
are harvested from a separate, unrelated finished project (a GBC platformer, referred to below as
"the reference project") that proved the same Python-only build+verify approach end to end
(404/404 headless-PyBoy checks passing at last release). Nothing about that project's *content*
(its world, characters, or story) carries over — only the *process* and a narrow slice of
*general-purpose code*:

| Harvested near-verbatim | Harvested as a starting pattern, substantially rebuilt | Built new for this project |
|---|---|---|
| `gbc_lib.py` — the generic SM83 assembler/`ROM` class and header writer. Nothing game- or music-specific lives in it; it is reused unchanged. | The **headless PyBoy verification harness pattern** from `test_rom.py` — same repo-relative-paths, same `PyBoy(rom, window='null')`-driven-by-button-sequence structure, same pass/fail ledger convention — but this project's suite asserts on **sound-register and music-engine-state changes**, not sprite/tilemap/save-game state, so the assertion vocabulary is new even though the harness shape is reused. | The **procedural music engine**: real-time, on-device, continuously-evolving generation logic driving all four GBC sound channels, steerable by live input, with bad-zone detection and reset. The reference project's `music.py` generated fixed background melodies at build time (a monophonic tune plus build-time transposed variants, baked into the ROM); this project's generation happens at runtime, every frame, is the primary product rather than background dressing, and is a from-scratch design, not an extension of that module. |
| The **documentation-driven pipeline itself** (`.claude/skills/`, staged 00→11, the journal + backlog persistence model, G1–G5). Adapted in file names and domain examples only — the mechanics are unchanged. | | The **input→parameter mapping layer** (D-pad/face buttons steering generation parameters live) — no equivalent exists in the reference project, whose input drove sprite movement. |
| | | The **reactive visualizer** (tile/palette animation synced to the music engine's own tracked state) — no equivalent exists in the reference project, whose visuals were a static handcrafted world. |

## §1 What this project is

**Driftune** (working title — open to revision at a future vision pass, not a locked brand) is a
standalone **Game Boy Color** ROM whose entire purpose is generative music: it is a self-playing,
player-steerable chiptune instrument, not a game with a win condition. On boot, the ROM starts
generating an evolving piece of music in real time, on-device, using all **four** of the GBC's
native sound channels (two pulse, one wave, one noise) — not by selecting among a small set of
pre-baked tracks, but by running generation logic every frame that decides what each channel plays
next. A simple generative visualizer (tile and palette animation) renders the music's current
state back to the screen — tempo, per-channel activity/register content, and whatever other
parameters the engine tracks — so the screen is a second, visual expression of the same live
state, not a separate game world layered on top.

The player does not "play" this in the traditional sense of controlling a character or chasing a
goal. Instead, the D-pad and face buttons **steer the generator's parameters live** — scale/mode,
tempo, register/octave range, note density, which channels are active, and other parameters this
project's architecture stage will define concretely (§3, C4). The generator is expected to be
able to **drift into a "bad zone"**: a state that is dissonant, stuck/repetitive, or overloads its
channels in a way that stops sounding good by whatever concrete metric the architecture/
requirements stages define (§3, C5). When it does, **Select** resets the generator back to a known
good starting state. Steering is exploration, not fine-tuned control — part of the intended
experience is that the player can push the system somewhere unpleasant and then recover from it.

Like the reference project, this ROM is built **entirely by a modular Python assembler pipeline**
— no RGBDS or other external toolchain. Python modules emit SM83 machine code and data directly;
a build script assembles them into a valid ROM; a headless-emulator test suite proves the result,
including asserting on the sound hardware's own register state, not just "does it boot." The
project is therefore also a second proof point (alongside the reference project) that this
Python-pipeline approach generalizes beyond one game to a structurally different kind of ROM.

## §2 Who it is for

1. **Players/listeners:** anyone who wants to carry a small, always-different, hands-on generative
   chiptune instrument — GBC homebrew/chiptune-scene enthusiasts first, but the experience itself
   requires no gaming skill or prior context: pick it up, press buttons, hear the music change.
   No fail state in the game sense exists; the "bad zone" is a musical failure state (it can sound
   bad), not a player failure state (nothing is lost — the generator recovers on its own, and
   Select is always available as a manual override too).
2. **Developers and coding agents:** exactly as with the reference project, this repository is a
   worked example of a fully-tested, documentation-driven GBC project, with every behavior
   traceable from vision to a named emulator test — including, newly, tests that assert on audio
   hardware state rather than only visual/gameplay state.

## §3 Scope commitments (what must always be true)

| # | Commitment | Notes |
|---|---|---|
| C1 *(amended v1.2)* | The ROM is **CGB-color**, with a **valid header** (correct logo, checksum, GBC compatibility flag). Cart shape (single-bank vs. MBC/bank-switched) is **not fixed by this vision** — it is an open question for dedicated research (hardware feasibility, build-chain impact) before `03-architecture-design-synthesis` commits to one, not a ceiling assumed for convenience. | Mirrors the reference project's `gbc_lib.py:set_header` convention; same header-writing code is reused for whatever cart type is eventually chosen. |
| C2 *(amended v1.2)* | **Cart type and save behavior are not decided by this vision.** Whether Driftune persists any state across power-off (a favorite seed, a style preference, a collection of discovered pieces) is an open question for dedicated hardware/UX research, not a foreclosed non-goal. A concrete save design still enters through the normal pipeline (research grounding → architecture → requirements) before it's built — this clause only removes the prior blanket "no save" commitment, it does not commit to a save design either. | Superseded framing: v1.0/v1.1 read "no SRAM/battery-save commitment is made yet," which the project owner has since named as an arbitrary decision mistaken for a firm one — corrected here, not silently. |
| C3 | The build is the **modular Python assembler chain** — `gbc_lib.py` (reused verbatim) plus this project's own modules — reproducible from source with no external assembler, exactly as `build_rom.py` does in the reference project. | See §0 provenance table. |
| C4 | **Input steers live generation parameters**, not song selection or menu navigation. The concrete D-pad/face-button → parameter mapping is **not decided here** — it is this vision's explicit delegation to `03-architecture-design-synthesis`, which must propose one concrete mapping (not a menu of options) before requirements are written against it. | Directly requested by the project owner as an architecture-stage deliverable, not a vision-stage guess. |
| C5 *(amended v1.1)* | **A "bad zone" exists and is recoverable — autonomously, by the generator itself, not only by the player.** The generator must be able to reach a state that is musically bad by some concrete, measurable definition, and it must detect that state **and act on it**, biasing its own generation back toward a good state without requiring input. **Select remains available as a manual override** — it deterministically returns the generator to a known-good starting state (and, as of v1.1, randomizes each channel's melodic starting point too — "reset and randomize," not "the only way out"). The exact detection metric and recovery mechanism are **not decided here** — delegated to `03-architecture-design-synthesis`/`04-requirements-engineering`, same pattern as C4. | Directly requested by the project owner (v1.0: the mechanic must exist and be testable; v1.1: "if you are already able to detect bad zones, avoid them or navigate naturally out of them... Select is only for the user to reset/randomize if they want to"). |
| C6 | **Generation is real-time and on-device**, every frame, not a fixed set of pre-baked tracks chosen between. Determinism is required only where testability needs it (e.g. a fixed seed reproduces a fixed sequence for a regression test) — determinism is a testing tool, not a listening-experience requirement; the engine is expected to feel different across un-seeded runs. | Directly distinguishes this project from the reference project's `music.py`, which generated fixed content at build time. |
| C7 | **All four GBC sound channels are used** by the generation logic — not necessarily simultaneously at all times (channel activity is itself a steerable/visualizable parameter per C4), but the engine's design must have a real part for each of pulse A, pulse B, wave, and noise, not treat some as decorative afterthoughts. | Directly requested ("using the GBC's four sound channels"). |
| C8 | **The visualizer reacts to the music engine's own tracked state** (tempo, per-channel activity, or other parameters the engine defines) — it is generative dressing driven by the same state the audio uses, not an independently authored game world or narrative. | Directly requested ("Doesn't need to be a game world; think generative visualizer"). |
| C9 | Every release is **emulator-verified**: the ROM builds to a valid header and the full test suite passes headlessly — and, newly relative to the reference project's gate, the suite must be able to **drive button input sequences and assert on resulting sound-register/engine-state changes**, not only "does it boot" or "does the screen look right." | Directly requested; generalizes the reference project's G5 gate to audio-hardware assertions. |

## §4 Non-goals (at this vision's date)

Not commitments against forever — just explicitly *not* promised **yet**, same convention as the
reference project's own non-goals list: real-hardware certification (emulator verification is the
gate, same as the reference project) · a traditional win condition, score, or fail state in the
player-facing sense (the "bad zone" is a musical state, not a game-over) · localization/text
content of any kind (the ROM has no narrative text) · multiplayer/link-cable features ·
MIDI/external-hardware sync or export · reuse of any of the reference project's game-specific
content (tiles, tilemaps, world layout, melody) — only its generic assembler code and its process
are reused, per §0.

**Removed at v1.2** (were listed here in v1.0/v1.1, now explicitly reopened, not decided either
way — see §8's amendment rationale and §9 below): *SRAM/battery save of any kind* and *bank-switched
ROM growth beyond one bank*. Neither is now a non-goal — both are open questions this vision
defers to dedicated research before any architecture commitment is made.

## §9 Future direction — under active research (added v1.2)

The project owner has supplied a substantially larger ambition for what Driftune's musical and
presentational identity could become than §1-§4 currently commit to: a recognizable but evolving
musical character spanning many genre references (ambient, chiptune, electronic/dance families,
jazz/blues, classical/orchestral/folk, synthwave, experimental, and hybrids of these), style
evolution/drift/blending over a session or across sessions, a fuller harmonic/melodic/rhythmic
vocabulary (motif development, harmonic progression, song-form structure — intro/build/peak/
breakdown/ending — rather than only continuous undifferentiated texture), an explicit emotional/
energy model, a visual identity that evolves alongside the music (theme/palette changes, mood- and
style-reactive visuals, not only tempo/activity-reactive), and a longer-arc listener relationship
(favorites, a sense of returning/discovered pieces, a personal collection) — see the project
owner's full 22-section topic list, preserved verbatim in the pipeline journal's run log for this
amendment.

**This is recorded here as direction, not as new binding commitments.** Per the project owner's
own correction (2026-07-22): *"This is exactly why this type of research is needed, arbitrary
decisions have been mistaken for firm decisions... It should educate the vision through research
in these areas."* Nothing in this §9 is architecture, requirements, or code — each topic cluster
is a standing instruction to the owning `02-research-*` skill(s) to investigate feasibility on
real GBC hardware within whatever cart/save shape §3 C1/C2 eventually settle on, and to report
back findings this vision (or `03-architecture-design-synthesis`, for design-level questions) can
then decide against — never to be silently designed around without that research pass. Named
research threads this section opens (not exhaustive, refined as research actually runs):

- **Musical identity & diversity** (§§3-4 of the topic list): is a recognizable, evolving
  "signature sound" achievable across multiple genre references on 4 GBC PSG channels, and which
  referenced genres are realistically expressible at all (a house/techno four-on-the-floor pulse
  is plausible with the existing noise-channel Euclidean machinery; full jazz voice-leading or
  orchestral texture may not be, on this hardware, without real research to say so either way) —
  routes to `02-research-game-design`.
- **Style evolution, structure, and the emotional/energy model** (§§5, 8-13 of the topic list):
  what SM83-tractable techniques exist for phrase/motif development, song-form structure, and a
  drifting-over-time style/energy state — this overlaps and extends the already-open `BL-0010`
  research gap (no cheap technique yet found for composed musical form) — routes to
  `02-research-game-design`.
- **Visual evolution & audio-visual synchronization** (§§15-17 of the topic list): what a
  richer, evolving visual identity (beyond the current 4-tile/2-palette MVP) costs in ROM/VRAM
  budget and VBlank time, and what synchronization techniques (beat/structural/mood-mapped) are
  practical — routes to `02-research-game-design` (convention/technique) and
  `02-research-gbc-hardware` (VRAM/OAM/palette budget reality).
- **Cart shape & persistence** (the C1/C2 reopening above, and §§14, 18-19 of the topic list —
  procedural identity, favorites, collection, sharing): what MBC options exist for a GBC cart,
  what bank-switching costs the build/test chain, and what a real SRAM/battery-save design would
  need to support "returning to a favorite piece" — routes to `02-research-gbc-hardware`
  (MBC/SRAM hardware facts) and `02-research-tooling-and-testing` (multi-bank build/verify
  chain impact).

No timeline or increment commitment is made for any of this — §9 is a durable record of ambition
and its open research threads, revisited whenever `01-vision` runs a consistency check, not a
promise about the next package built.

## §5 Quality bar

"Done" for any change means: the ROM builds with a valid header at a fixed size; the full headless
test suite is green, including at least one test per shipped feature that drives a button sequence
and asserts on the resulting sound-register or engine-state change (C9); the behavior is
traceable through the pipeline's artifacts (requirement → feature spec → package → verification
report); and the developer quick-reference docs (this project's equivalent of the reference
project's `Claude.md`/`memory.md`) match the shipped bytes.

## §6 Authority & document precedence

1. This document (MSTR-001) is the top of the tree for *purpose-level* statements; the GDS ladder
   (`docs/architecture/`) is authoritative for design as each level's merge gate closes.
2. Until this project authors its own `docs/master/MSTR-00x` governance document, the rules
   **G1–G5** in [`.claude/skills/README.md`](../../.claude/skills/README.md) are binding (adapted
   for this project's own file set — see that document's write-scope table).
3. This project's developer quick-reference file(s) are the live source of convenience lookups;
   the GDS ladder and this vision remain authoritative over them.
4. Conflicts between documents are findings for the owning skill — never resolved by silently
   editing the downstream copy.

## §7 Change control

A change to §1–§4 is the most expensive kind of change in the tree: it is made only by the
`01-vision` skill, dated, with rationale recorded in §8's amendment log, and the downstream blast
radius enumerated (artifact → owning skill).

## §8 Vision Amendment Log

| Date | Version | What changed | Why | Downstream blast radius |
|---|---|---|---|---|
| 2026-07-21 | 1.0 | Initial authoring — project origin. | Project owner's initial instruction to harvest the reference project's pipeline/toolchain and build a new procgen-music-first GBC ROM. | Grounds `docs/architecture/00-vision.md` (GDS-00) and everything downstream. |
| 2026-07-21 | 1.1 | Amended C5: the bad-zone mechanic must be autonomously self-correcting, not only Select-recoverable; Select's role reframed as "reset and randomize," a manual override rather than the sole recovery path. | Project owner: "If you are already able to detect bad zones, avoid them or navigate naturally out of them. The Select button is only for the user to reset/randomize if they want to." | GDS-01 §"the loop" (item 4, new), GDS-03 §5 (amended — the autonomous-recovery mechanism and Select's randomize behavior), `IP-0007` (implementation, already shipped and tested at the time this amendment was recorded — the code preceded this doc update in the same session, corrected here per the pipeline's own discipline that vision changes are recorded even when implementation moved first under direct user instruction). |
| 2026-07-22 | 1.2 | Amended C1/C2: removed the "single-bank at present"/"no SRAM save" framing as fixed non-goals, reopened both as explicit research questions (§9 added). Recorded a large (22-section) future-direction topic list the project owner supplied, spanning musical identity/diversity, style evolution, song structure, emotional/energy model, visual evolution, and longer-arc listener relationship (favorites/collection) — not adopted as binding commitments, but named as standing research threads for the owning `02-research-*` skills. | Project owner, verbatim: "This is exactly why this type of research is needed, arbitrary decisions have been mistaken for firm decisions... It should educate the vision through research in these areas. Do not limit to a single bank ceiling. Do not discount saves." Direct correction of the v1.0/v1.1 framing, which had closed off cart-shape and save-behavior questions without a research basis for doing so. | GDS-00 (matching update to its own non-goal framing, this run), `strategic-assumptions-register.md` A5 (single-32KB-bank assumption reopened, no longer treated as comfortably confirmed), new research topics owed to `02-research-game-design`/`02-research-gbc-hardware`/`02-research-tooling-and-testing` per §9's own routing (none authored yet — this amendment only opens the threads), `03-architecture-design-synthesis` (must not assume single-bank/no-save when it eventually reaches cart-shape/persistence design — wait for the research this amendment commissions). |
