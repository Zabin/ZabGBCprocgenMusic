# R218 — Algorithmic/Generative Music & Procedural Generation: Inspiration Survey

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 10, items 105-115 (algorithmic composition
  history, Brian Eno's generative music, Koan, No Man's Sky procedural music, Spore procedural
  audio, Rogue procedural generation, classic GB soundtracks, modern chiptune, live coding, bytebeat,
  tiny procedural synths)

## 1. Purpose
A named-precedent survey across adjacent generative-art/procedural-generation history — not to
adopt any one system's specific technique wholesale, but to place Driftune in a lineage and mine
each for one concrete, cited, SM83-relevant idea.

## 2. Scope
Eno/Koan (expanding R201), two notable procedural-game-audio case studies (No Man's Sky, Spore),
one foundational non-audio procedural-generation case study (Rogue) for cross-domain technique
transfer, and three code-centric generative-audio traditions (live coding, bytebeat, and the
GB-specific tiny-synth tradition already covered in R209).

## 3. Concepts
- **Brian Eno / Koan** (expanded from R201): Eno's own framing evolved toward pure algorithm —
  "his interest moved towards algorithms and the way algorithmic music continuously changes and
  evolves over time without the need for direct human intervention," including "generative
  screensavers," i.e. treating the *visual* and *musical* generative processes as siblings, not
  separate concerns [Gorilla Sun — Brian Eno's Endless Music Machines](https://www.gorillasun.de/blog/brian-enos-endless-music-machines/).
  Directly relevant: this is the same visual+audio-from-one-process framing GDS-00/R205 already
  give Driftune's visualizer (reading the *same* engine state, not an independent artistic layer).
- **No Man's Sky** (65daysofstatic): a **curation-based** model, not pure real-time synthesis —
  a large corpus of pre-recorded, deliberately-decomposable material is "ripped apart" and
  algorithmically recombined at runtime, rather than synthesized from scratch [Game Informer —
  65daysofstatic on Creating No Man's Sky's Generative Soundtrack](https://gameinformer.com/b/features/archive/2016/05/30/65daysofstatic-on-creating-no-man-39-s-sky-generative-soundtrack.aspx).
  **Explicitly not Driftune's model** (MSTR-001 C6 requires on-device real-time generation, not
  curation of pre-recorded assets) — named here specifically to distinguish, since "procedural
  music in games" is often assumed to mean this curation style by default.
  Stated directly by the composers themselves; framing "generative" as: real-time algorithmic
  curation of pre-composed material.
- **Spore** (Eno's "The Shuffler"): closer to Driftune's spirit than No Man's Sky — "stochastically
  generated in real time... from many music samples through a set of rules," explicitly reactive
  to player behavior over session-length timescales (energetic early, "more relaxing... slowing
  down" later in a session) [Rolling Stone — Brian Eno's Mutating "Spore" Score](https://www.rollingstone.com/culture/culture-news/brian-enos-mutating-spore-score-reinventing-game-music-255336/).
  Directly actionable idea: **session-length adaptive drift** (music trends toward a different
  character the longer a session runs) is a real, cited precedent for a Driftune feature *not*
  currently in scope (the engine currently has no session-duration-aware state at all) — flagged
  as a `feature`-type backlog candidate, not built.
- **Rogue** (procedural dungeon generation, 1980) — cross-domain, not audio, but the founding
  case of "the creators didn't want to author the content themselves... they needed a generation
  algorithm" for the explicit reason of wanting to be surprised by their own system [PCG Wiki —
  Rogue](http://pcg.wikidot.com/pcg-games:rogue) — the same motivating spirit MSTR-001 §1
  articulates for Driftune's music ("continuously evolving," not hand-authored). No specific
  audio technique transfers; the *motivating philosophy* does.
- **Live coding (TidalCycles, Sonic Pi)**: pattern-transformation languages for real-time
  algorithmic music, performed live — architecturally these run on general-purpose computers with
  full floating-point/audio-synthesis backends (SuperCollider), **not remotely SM83-tractable as
  systems**, but their core idea — patterns as first-class, composable, transformable objects — is
  a conceptual frame, not a technique to port [Strange Loop — Live Coding Music with TidalCycles](https://thestrangeloop.com/2016/live-coding-music-with-tidalcycles.html).
- **Bytebeat**: the single most directly SM83-relevant item in this whole survey. A bytebeat
  program is "a single-line formula that defines a waveform as a function of time" using only
  integer/bitwise arithmetic (shifts, XOR, AND, modulo) run at a fixed sample rate — the
  best-known example, `t*(42&t>>10)`, independently discovered by at least three people
  [countercomplex — Viznut's deep analysis of one-line music programs](http://viznut.fi/texts-en/bytebeat_deep_analysis.html); [royvanrijn — Bytebeat: Algorithmic Symphonies](https://www.royvanrijn.com/blog/2011/12/bytebeat-algorithmic-symphonies/).
  This is a **materially different generation paradigm** from everything else in this encyclopedia
  (R201-R216): instead of generating discrete notes/frequencies, a bytebeat expression directly
  computes a raw waveform sample stream. Not directly applicable to the GBC's channel-based PSG
  (there's no "arbitrary raw sample" output channel at full sample rate — only Wave Channel's 32
  fixed samples per cycle, R114), **except** as a technique for *generating new Wave RAM tables*:
  a bytebeat-style integer expression could procedurally generate the 32-sample wave shape itself
  (a genuinely novel, cheap, SM83-tractable idea this survey surfaces that no other topic named) —
  flagged as a concrete, promising `feature`-type backlog candidate for wave-channel timbre
  generation (distinct from R114's current "pick from a few precomputed tables" plan).

### Sources
- [Gorilla Sun — Brian Eno's Endless Music Machines](https://www.gorillasun.de/blog/brian-enos-endless-music-machines/)
- [Game Informer — 65daysofstatic on No Man's Sky's Generative Soundtrack](https://gameinformer.com/b/features/archive/2016/05/30/65daysofstatic-on-creating-no-man-39-s-sky-generative-soundtrack.aspx)
- [Rolling Stone — Brian Eno's Mutating "Spore" Score](https://www.rollingstone.com/culture/culture-news/brian-enos-mutating-spore-score-reinventing-game-music-255336/)
- [PCG Wiki — Rogue](http://pcg.wikidot.com/pcg-games:rogue)
- [Strange Loop — Live Coding Music with TidalCycles](https://thestrangeloop.com/2016/live-coding-music-with-tidalcycles.html)
- [countercomplex (viznut) — deep analysis of one-line music programs](http://viznut.fi/texts-en/bytebeat_deep_analysis.html)
- [royvanrijn — Bytebeat: Algorithmic Symphonies](https://www.royvanrijn.com/blog/2011/12/bytebeat-algorithmic-symphonies/)
- Classic GB soundtracks / modern chiptune composition / GB-specific tiny synths: covered by R207
  (channel idioms) and R209 (driver survey) — not re-covered here to avoid duplication.

## 4. Operational Context
None of this survey's ideas are implemented. The bytebeat-for-wave-table idea is genuinely novel
relative to everything else already planned.

## 5. Implementation Guidance
- **Recommend filing two concrete `feature`-type backlog candidates from this survey**: (1)
  session-length-adaptive drift (Spore precedent) — the engine trends toward a different
  character the longer it's run; (2) bytebeat-generated Wave RAM tables (novel synthesis of this
  survey's bytebeat finding with R114's wave-channel plan) — procedurally computing wave shapes
  from a small integer expression instead of only picking among precomputed tables, potentially
  giving the wave channel its own steerable "shape" generation rather than a fixed small menu.
  Neither is built or scheduled — both are genuinely new scope for `00-intake` to triage.
- **No Man's Sky's curation model should NOT be adopted** — explicitly confirms MSTR-001 C6's
  real-time-generation requirement by contrast with the most famous "procedural game music"
  example, which actually works differently.

## 6. Feature Mapping
No current `IP-xxxx`; two new `feature`-type backlog candidates surfaced.

## 7. Related Topics
R201 (Eno/generative-music baseline, expanded here), R114 (wave-channel timbre, the bytebeat idea's
target), R205 (visualizer-as-sibling-process framing, echoed in Eno's own later work), R209/R207
(GB-specific music systems, not re-covered here).
