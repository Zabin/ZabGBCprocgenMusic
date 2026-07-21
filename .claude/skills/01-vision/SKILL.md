---
name: 01-vision
description: Author or refresh the project's Vision layer — the program vision (docs/master/MSTR-001-program-vision.md), the GDS-00 Vision level of the architecture ladder (docs/architecture/00-vision.md), and the strategic assumptions register (docs/architecture/strategic-assumptions-register.md) — keeping the three consistent with each other and with what the project has actually become. Use when asked "what is this project for," "update the vision," "does the vision still hold," "record a strategic assumption/pivot," at the start of a new major increment, or as the very first stage of the project (author the vision from the user's actual stated intent — there is no shipped ROM yet to derive it from). This is the top of the pipeline: it makes purpose-level statements only — no architecture decisions (03-architecture-design-synthesis), no requirements (04-requirements-engineering), no research claims (02-research-*), no code. A vision change is the most expensive kind of change in the tree; this skill makes them deliberately, records why, and names everything downstream the change invalidates.
---

# Vision

Owns the **Vision layer** — the answer to "what is this project, for whom, and what must always be
true about it." Everything downstream (research scope, architecture, requirements, features,
packages) traces back to statements made here, which is exactly why this skill is small, slow, and
deliberate: it changes rarely, and every change it makes ripples.

## What this skill owns

| Artifact | Role |
|---|---|
| `docs/master/MSTR-001-program-vision.md` | The program vision — what Driftune is (a standalone Game Boy Color ROM whose primary purpose is real-time procedurally-generated chiptune music, built entirely by a Python assembler pipeline), who it's for, scope commitments (e.g. ROM size/bank budget, MBC/battery-save posture if any, emulator-verified via PyBoy), the authority rules other documents cite. |
| `docs/architecture/00-vision.md` (GDS-00) | The architecture ladder's Vision level — the design-facing restatement the rest of the GDS ladder builds on. Owned here, not by `03-architecture-design-synthesis` (which owns GDS-01 onward). |
| `docs/architecture/strategic-assumptions-register.md` | The explicit assumptions the vision rests on — each with its trigger ("if this stops being true, revisit X"). Likely first entries: the four GBC sound channels (NR1x-NR5x) are sufficient for the intended musical range without external chips; PyBoy headless remains the verification target for both audio-register and visual state; the Python-assembler approach (no RGBDS toolchain) remains the build strategy; the generator runs entirely on-device in real time rather than selecting among pre-baked tracks. |

It SHALL NOT make architecture decisions, originate requirements or research claims, or edit any
downstream artifact — when a vision change invalidates downstream content, it *names* the affected
artifacts and their owning skills; the fixes run through the pipeline in order.

## First-run mode (no shipped artifact to baseline)

Driftune has no prior ROM, no `Claude.md`, no `memory.md` — there is nothing "as-built" to mine.
On the very first run, author all three artifacts **from the user's actual stated intent**,
gathered through direct questions where the intent isn't already on record, not derived from any
existing code or shipped game. Ground statements in what the user has said the project is for:
a music engine that continuously generates evolving chiptune on-device using the GBC's four sound
channels, driven by real-time generation logic rather than pre-baked track selection; a generative
visualizer (tile/palette animation) synced to tempo, voice activity, and register state rather
than a game world; D-pad and face buttons that steer music-generation parameters (the exact
mapping — scale/mode, tempo, register/octave, density, active channels — is deliberately left to
`03-architecture-design-synthesis` to settle, not decided here); and a "bad zone" concept where the
generator can drift into a bad-sounding state (dissonance, repetition, channel overload — the
precise detection metric is also an architecture-stage decision) that Select resets to a good
starting state. Genuine open questions about direction become register assumptions with triggers,
or — if they're truly load-bearing for what the project even is — a blocking question to the user;
they are never silently invented.

## Workflow

1. **Read the current Vision layer** (all three artifacts, if they exist) plus whatever the user
   has already told the project about intent (this conversation, any prior notes) and `ROADMAP.md`
   if one exists.
2. **Determine the mode:**
   - **First run** (no artifacts yet, nothing shipped): author all three per First-run mode above,
     asking the user directly for anything load-bearing that hasn't been stated.
   - **Consistency check** (default once they exist, cheap): do the three artifacts agree with
     each other and with reality? An engine that shipped a fifth sound-generation mode while the
     vision still describes four has vision drift — fix the record or flag the divergence,
     whichever direction is true.
   - **Deliberate change**: the user is pivoting scope or a commitment. Draft the change, record
     the rationale and date in the changed artifact, update the assumptions register (retire/add
     assumptions with triggers), and enumerate the downstream blast radius — which GDS levels,
     requirements, features, and packages now cite a superseded statement.
3. **Keep the three artifacts in lock-step.** MSTR-001 and GDS-00 must never disagree; where they
   share a statement, one carries it and the other points to it (record the merge decision in
   GDS-00's gate).
4. **Update trackers** — flip the artifacts' rows in `ROADMAP.md` and `docs/master/INDEX.md` /
   `docs/architecture/INDEX.md`.
5. **Commit** as `docs(vision): <what changed>`.

## Quality gate

- [ ] MSTR-001, GDS-00, and the assumptions register agree — no statement contradicted between them.
- [ ] Every changed statement carries a dated rationale, not a silent rewrite.
- [ ] Every retired/added strategic assumption has a trigger condition.
- [ ] The downstream blast radius of any change is enumerated by artifact and owning skill — none
      of it edited here.
- [ ] No architecture, requirement, research claim, or code was authored.
- [ ] First-run mode did not invent a load-bearing answer the user hadn't actually given — genuine
      ambiguity became a register assumption with a trigger, or a direct question, never a guess.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 01 — Vision**, the top of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md); stages run in numeric order, and `00-pipeline-manager`
reports where the project currently stands). Upstream: only the user. Downstream: the
`02-research-*` skills and `03-architecture-design-synthesis`.

End **every** invocation — first run, consistency check, deliberate change, or blocked stop —
with a chat summary containing exactly these three parts:

1. **What changed** — artifacts touched (or "consistency confirmed, nothing changed"), assumptions
   added/retired.
2. **Recommendations** — vision drift found, assumptions whose triggers have fired, and the full
   downstream blast radius of any change (artifact → owning skill).
3. **Next step** — say explicitly what to run next and why: after the first run or a vision
   change, the first invalidated downstream stage in numeric order (usually a `02-research-*`
   skill for new grounding needs, else `03-architecture-design-synthesis`); after a clean
   consistency check, whatever stage the current increment is actually at — run
   `00-pipeline-manager` if that isn't already known.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
