# R221 — Emotional/Energy Parameter Mapping

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-22
- **Trigger:** MSTR-001 §9 (v1.2) — the user's §12 "Emotional Landscape" and §13 "Energy Model"
  ask whether Driftune's engine parameters can map to a recognizable emotional/energy spectrum.

## 1. Purpose

Determine whether a small set of Driftune's *existing* tracked engine parameters (tempo, density,
`DISSONANCE_SCORE`, active-channel count) can be mapped to a real, evidence-grounded
emotional/energy model, cheaply enough to run continuously on SM83 — rather than inventing a
bespoke emotion taxonomy with no grounding.

## 2. Concepts

**Russell's circumplex (valence-arousal) model is the standard, well-cited framework for exactly
this mapping.** It "represents emotions through a relationship between valence (pleasant-
unpleasant) and arousal (activation-deactivation)," and this is formalized in music-emotion
research as the "Energy-Valence Model," where "energy (sometimes called arousal) is a measure of
how alert or stimulated someone feels, and valence is a measure of how pleasant an emotion is"
[ResearchGate — Music Emotion Maps in Arousal-Valence Space](https://www.researchgate.net/publication/307909024_Music_Emotion_Maps_in_Arousal-Valence_Space).
This gives Driftune a **two-axis**, not one-dimensional, target — matching the user's own split
between §12 (Emotional Landscape, valence-shaped: calm/happy/melancholy/dark/peaceful/etc.) and
§13 (Energy Model, arousal-shaped: dormant/gentle/building/peak/release).

**Tempo and density are directly, empirically tied to the arousal axis** — "tempo and velocity
would correlate positively with perceived arousal" [same source, general game-audio parameter
mapping]. Driftune already tracks both (`TEMPO_IDX`, `DENSITY_IDX`/onset-window activity) as
first-class engine parameters, so **arousal is close to a free mapping**: no new engine state is
needed, only a derived read of state that already exists.

**A rule-based generative system explicitly controlled by target valence/arousal is a real,
published, adjacent design** — "A Rule-Based Generative Music System Controlled by Desired Valence
and Arousal" [ResearchGate](https://www.researchgate.net/publication/263964165_A_Rule-Based_Generative_Music_System_Controlled_by_Desired_Valence_and_Arousal)
confirms rule-based (not ML-based) valence/arousal-steered generation is an established category,
not a novel or ML-dependent-only approach — directly relevant since Driftune's engine is entirely
rule-based (LFSR-walk + table lookups), not a trained model.

**Layered adaptive-music systems use exactly this axis split for real-time mixing**: "the strength
(arousal) corresponds to the number of active layers, while the quality (valence) corresponds to
the choice of emotional modes of the generated musical components" [arXiv — An adaptive music
generation architecture for games](https://arxiv.org/pdf/2207.01698). This maps cleanly onto
Driftune's own vocabulary: active-channel count (already a steerable parameter, `CHMIX_IDX`, not
yet consumed per `BL-0019`) is a direct arousal-axis lever; scale/mode selection (`SCALE_IDX`,
already steerable) is a direct valence-axis lever, since major/minor/mode selection is one of the
most-established valence cues in music-emotion literature generally (not independently
re-researched this pass — treated as common-knowledge background, flagged if a future deeper pass
wants a dedicated citation).

**`DISSONANCE_SCORE` is a plausible valence-axis signal, not yet confirmed by a direct citation**:
dissonance/consonance is intuitively adjacent to (un)pleasantness, and Driftune's own
`DISSONANCE_SCORE` (R204, Helmholtz-roughness-grounded) already exists as a continuous 0-45 value —
but no source in this pass directly validated dissonance-score-as-valence-proxy specifically (as
opposed to major/minor-as-valence-proxy, which is well-established). **Flagged as needing
fetch-verification** if this mapping becomes a real requirement, not asserted as fully evidenced
here.

### Sources
- [ResearchGate — Music Emotion Maps in Arousal-Valence Space](https://www.researchgate.net/publication/307909024_Music_Emotion_Maps_in_Arousal-Valence_Space)
- [ResearchGate — A Rule-Based Generative Music System Controlled by Desired Valence and Arousal](https://www.researchgate.net/publication/263964165_A_Rule-Based_Generative_Music_System_Controlled_by_Desired_Valence_and_Arousal)
- [arXiv 2207.01698 — An adaptive music generation architecture for games](https://arxiv.org/pdf/2207.01698)
- Dissonance-as-valence-proxy: not independently confirmed this pass — flagged
  "needs fetch-verification."

## 3. Operational Context

Driftune already tracks every parameter this mapping would need (`TEMPO_IDX`, density/onset-
window activity, `SCALE_IDX`, `DISSONANCE_SCORE`, `CHMIX_IDX` even though unconsumed per
`BL-0019`) — this is a **read/interpret layer over existing state**, not new generation logic, the
cheapest of the three §9 research threads to eventually implement.

## 4. Implementation Guidance

- **A concrete, cheap valence-arousal derivation is achievable without new WRAM state**: arousal
  from `TEMPO_IDX`/density directly; valence from `SCALE_IDX` (mode) primarily, `DISSONANCE_SCORE`
  as a secondary, less-confirmed signal pending the fetch-verification flag above.
- **This is the most natural bridge between engine state and the visualizer's own future
  evolution** (R220's own §9-thread neighbor, "visual evolution") — a valence-arousal pair is
  exactly the kind of two-value summary a palette/animation-mood mapping would want to consume,
  more tractable than trying to visualize `BAD_ZONE_FLAGS` or raw `DISSONANCE_SCORE` directly.
- **Recommend against inventing a bespoke emotion taxonomy** (the user's §12 lists 13 named
  emotions — calm/happy/energetic/melancholy/tense/hopeful/mysterious/epic/dark/peaceful/
  triumphant/dreamlike/reflective) as 13 independent engine states; the arousal-valence
  literature's own convention is that named emotions are *regions* of the same continuous 2D
  space, not a taxonomy needing 13 separate detectors — a future requirements pass should map
  named emotions to (valence, arousal) quadrant regions, not build 13 parallel mechanisms.

## 5. Feature Mapping

No current `IP-xxxx`. Grounds a future `03-architecture-design-synthesis`/
`04-requirements-engineering` pass on an emotional/energy read-layer, per MSTR-001 §9's routing.

## 6. Related Topics

R204 (bad-zone detection — `DISSONANCE_SCORE`'s existing source), R205/R208 (visualizer
conventions — the natural consumer of a valence-arousal summary), R220 (style evolution/song
structure — the state machine this mapping's output would most usefully drive), MSTR-001 §9 (the
vision-tier thread this topic answers).
