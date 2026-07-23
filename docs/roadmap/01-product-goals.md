# Product Roadmap 01 — Product Goals

- **Owned by:** this planning package (authored as a Lead-Systems-Architect/TPM synthesis pass,
  2026-07-22) · **Grounded in:** `docs/master/MSTR-001-program-vision.md` v1.4 (authoritative —
  this document explains what success looks like, MSTR-001 remains the source of truth if the two
  ever appear to disagree) and the full `docs/research/encyclopedia/` (42 topics, no new research
  performed for this package)
- **Status:** ✅ Authored 2026-07-22 · **Scope:** experience/outcome only — no implementation

This document answers "what does success look like" without naming a single file, register, or
algorithm. It restates and organizes MSTR-001 §1-§2 and the research encyclopedia's design-tier
findings (R2xx) into the player-experience vocabulary the rest of this roadmap package builds on.

## Overall Experience

Driftune is a small, always-different, hands-on generative chiptune instrument, not a game. On
power-on it immediately begins generating and playing an evolving piece of music, in real time,
on the real GBC sound hardware, indefinitely, with no goal, no win state, and no end. A listener
picks it up, presses buttons, and hears the music visibly and audibly respond — steering, not
programming. The visualizer is a second, synchronized expression of the same live state, not a
separate game layered on top (MSTR-001 §1, C8).

## Emotional Goals

The listener should move through a genuine, recognizable emotional range across a session — calm,
energetic, melancholy, tense, hopeful, mysterious — rather than one static mood stretched
indefinitely (MSTR-001 §9, grounded by R221's valence-arousal finding). The "bad zone" is part of
this goal, not a bug to eliminate: a piece that can genuinely go somewhere unpleasant and then
visibly claw its way back out (autonomously or via Select) is more emotionally alive than one that
can never go wrong at all (MSTR-001 C5).

## Artistic Goals

Authentic chiptune identity first — the GBC's real 4-channel PSG sound, not an imitation of it
(MSTR-001 §1, R207/R216). Within that constraint: elegance over density (a small number of
well-used mechanisms — scale-constrained walk, Euclidean rhythm, bad-zone recovery, arpeggio/
vibrato/portamento — compounding into something that reads as more than the sum of its parts,
rather than many shallow features). Musicality is judged by ear (`08-content-authoring`/
`09-content-review`'s eventual job), not only by test-suite green.

## Replayability Goals

No two power-ons (and no two Select presses) should sound identical — every channel's melodic
starting point is randomized from a live hardware source (`DIV`), not a fixed seed, so the
generator's *starting point* is always fresh even though its *rules* are consistent (MSTR-001 C6,
A6 in the strategic assumptions register). Longer-arc replayability (a session evolving
differently across genres/styles/energy states) is the ambition this roadmap's later releases
build toward (R219-R221).

## Procedural Generation Philosophy

Generation is real-time and on-device, every frame — never a fixed set of pre-baked tracks chosen
between (MSTR-001 C6). Rules over randomness-for-its-own-sake: every generation mechanism should
be a *constrained* random or rule-based process (scale-constrained walk, Euclidean-gated rhythm,
dissonance-weighted recovery), not free noise — R201/R204's own grounding. Determinism is a
testing tool only, never a listening-experience requirement (A6).

## Audiovisual Identity

Sound is primary; the visualizer is a synchronized reflection of the same tracked state (tempo,
per-channel activity, bad-zone-ness, and — per this roadmap's later releases — style/energy),
never an independently authored world (MSTR-001 C8). Visual restraint matches the GBC's own era-
appropriate palette economy (R208) — legible at a glance, not a spectacle competing with the
music for attention.

## Interaction Philosophy

One control, one knob, no menus, no chords (GDS-03 §3, R206). Steering is exploration: the
listener nudges a live process and hears/sees the result immediately, including the ability to
push it somewhere unpleasant and either watch it recover on its own or reset-and-randomize via
Select (MSTR-001 C5). Complexity grows in what a control steers over the roadmap's life (e.g. a
future style/genre control), never in how many controls exist or how they're combined.

## Success Criteria

A release succeeds when, and only when, all of the following are true (operationalized further in
`09-release-exit-criteria.md`):

1. The ROM builds to a valid, header-correct cartridge image and boots to continuous generation
   within the fixed init window.
2. The full headless test suite passes, including at least one assertion per shipped behavior
   that drives real input and reads real sound-register/WRAM state (MSTR-001 C9).
3. A listener can point to a **specific, audible or visible** improvement over the prior release —
   never a release that only refactors or "sets up for later" with nothing new to hear or see.
4. Every capability shipped traces to a Vision statement or a research-grounded finding — nothing
   is added because it's easy, cut because it's hard, or invented without a source (MSTR-001 C10,
   this package's own §7 Traceability Matrix).
5. The bad-zone/recovery guarantee (MSTR-001 C5) and the four-channel commitment (C7) hold at
   every release — no release regresses either, even while adding new capability on top.

## What success does *not* require

Per MSTR-001 §4's non-goals: a win condition, score, or fail state; localization; multiplayer;
MIDI/external sync; real-hardware certification as a release gate (emulator verification is the
gate, hardware testing is a *validation cadence* per `08-development-strategy.md`, not a blocking
requirement per release). Cart shape (single-bank vs. bank-switched) and persistence (save/no
save) are explicitly **not** success criteria either way — both remain open architecture decisions
this roadmap sequences around, not commitments this document makes (MSTR-001 C1/C2, v1.2).
