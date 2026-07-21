# R214 — Rule-Based, Grammar, L-System & Cellular-Automata Generation Survey

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 4, items 46-49, 51-52 (rule-based composition,
  grammar-based generation, L-systems for music, cellular automata for rhythm, fractal music,
  noise functions)

## 1. Purpose
Survey generation-algorithm families beyond R201's Markov/random-walk baseline, as named,
cited upgrade candidates rather than adopted techniques.

## 2. Scope
Grammar/L-system approaches, cellular automata for rhythm/composition, and fractal/noise-function
techniques, each evaluated for SM83-tractability the same way R201 evaluated Markov chains.

## 3. Concepts
- **Formal grammars / L-systems**: named among the standard families of algorithmic-composition
  technique ("genetic algorithms, neural networks, or formal grammars") [ResearchGate — The
  Analysis of Generative Music Programs](https://www.researchgate.net/publication/232000203_The_Analysis_of_Generative_Music_Programs)
  (already cited in R201). An L-system rewrites a symbol string by production rules each
  generation, which could represent a phrase/motif (R211's named gap) rather than a single note —
  potentially a real, cited answer to R211's phrase-generation gap, at the cost of needing a
  string-rewriting engine (more state/logic than the current per-note table lookups) — flagged as
  the most promising *specific* upgrade path for R211's gap, not decided here.
- **Cellular automata (CA) for rhythm/composition**: a real, actively-researched technique —
  "increased cell activity results in faster rhythms," and CA-driven systems have been used for
  "real-time creation of musical phrases" and even dedicated hardware ("cellular automata based
  hardware design") [ScienceDirect — Automatic generation of harmonious music using cellular
  automata based hardware design](https://www.sciencedirect.com/science/article/abs/pii/S0167926017303553);
  [ResearchGate — Cellular Automata Music: From Sound Synthesis to Musical Forms](https://www.researchgate.net/publication/289133468_Cellular_Automata_Music_From_Sound_Synthesis_to_Musical_Forms).
  A 1-D CA (e.g. Rule 30/90-style) is genuinely SM83-cheap: a small bit array, one rule application
  per tick — plausibly *cheaper* than the current LFSR-driven walk for rhythm generation
  specifically, and a real, cited alternative to R202's Euclidean-rhythm choice.
- **Fractal music / noise functions**: no strong, specific citation surfaced beyond general
  awareness that self-similar/fractal structure and coherent-noise functions (e.g. Perlin-style)
  are used in some generative-music contexts; treated as **lower-confidence, not further pursued
  this pass** — flagged as needing a dedicated deeper search if a future package specifically
  wants this family, rather than asserted from a weak result.

### Sources
- [ResearchGate — The Analysis of Generative Music Programs](https://www.researchgate.net/publication/232000203_The_Analysis_of_Generative_Music_Programs)
- [ScienceDirect — Automatic generation of harmonious music using cellular automata based hardware design](https://www.sciencedirect.com/science/article/abs/pii/S0167926017303553)
- [ResearchGate — Cellular Automata Music: From Sound Synthesis to Musical Forms](https://www.researchgate.net/publication/289133468_Cellular_Automata_Music_From_Sound_Synthesis_to_Musical_Forms)
- Fractal/noise-function music generation: not independently confirmed this pass — flagged
  "needs fetch-verification"/deeper search, not asserted as evidenced.

## 4. Operational Context
None of these are implemented — Driftune ships the R201 random-walk + R202 Euclidean-rhythm
baseline only.

## 5. Implementation Guidance
- **Recommend a CA-based rhythm generator as the concrete answer to `BL-0005`'s eventual
  "should density generation be more than a fixed Euclidean k/n" question**, if that question is
  ever raised post-listening-pass — cheaper and more cited than the fractal/noise-function
  alternative, and a genuinely different qualitative rhythmic feel from pure Euclidean spacing
  (CA rhythms can accelerate/decelerate based on prior state, Euclidean patterns are static once
  chosen).
- **Recommend an L-system as the concrete answer to R211's phrase/motif-generation gap**, if a
  future increment wants recognizable recurring phrases — this is a `feature`-type backlog
  candidate for after the v1 engine ships (per MSTR-001's own "start simple, extend later"
  posture), not decided/scheduled here.
- **Do not pursue fractal/noise-function generation without a dedicated follow-up research pass**
  — this pass's search results were too thin to ground a real recommendation either way.

## 6. Feature Mapping
No current `IP-xxxx`; both CA-rhythm and L-system-phrase ideas are unscheduled `feature`-type
backlog candidates for post-v1 consideration.

## 7. Related Topics
R201 (the Markov/random-walk baseline these are alternatives to), R202 (Euclidean rhythm, the CA
alternative's point of comparison), R211 (the phrase/motif gap the L-system idea addresses).
