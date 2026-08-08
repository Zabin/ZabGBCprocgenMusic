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

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED**, and it is the tier's clearest example of research earning its keep by saying *no*. The original grammar/cellular-automata survey had no consumer. **§8 (2026-07-26) deep-evaluated L-systems for `BL-0010`'s motif-recurrence gap and concluded against a derivation engine**, on a load-bearing constraint from the literature (melody quality degrades at *longer* derivations — Worth & Stepney), recommending instead a small fixed-depth weighted-rule table. **That is exactly what shipped**: `ADS-102`/`FS-109`/`IP-1090`'s `MOTIF_TABLE` variant selection (`VERIFIED`). Also cited by `ADS-100`/`ADS-103`. So this topic both *prevented* an expensive wrong design and *shaped* the right one — a stronger outcome than a plain feature trace. Its CA-rhythm half remains an unscheduled candidate.

## 7. Related Topics
R201 (the Markov/random-walk baseline these are alternatives to), R202 (Euclidean rhythm, the CA
alternative's point of comparison), R211 (the phrase/motif gap the L-system idea addresses).

## 8. Addendum — 2026-07-26: L-Systems for Motif Recurrence, Deep Evaluation (`BL-0010`)

§3's original L-system note flagged it as "the most promising *specific* candidate, not yet
evaluated in depth" for R211/R212's phrase/motif-development gap. `BL-0010` tracked exactly this
follow-up. This addendum performs that deeper evaluation.

**Probabilistic L-systems, not deterministic ones, are the concretely cited approach for
melodic/motif generation on constrained systems.** Jon McCormack's foundational work "presented
probabilistic L-systems that include probabilities about several possible rules associated with a
symbol, mapping the resulting symbols to melodic notes" [McCormack — Grammar Based Music
Composition](https://users.monash.edu/~jonmc/research/Papers/L-systemsMusic.pdf) (title/author
confirmed via search, primary PDF not independently fetchable this pass, see Sources). This is
directly SM83-tractable in the same spirit as Driftune's own LFSR-driven walk: a small
production-rule table with weighted-choice-among-rules (the same weighted-lookup-table mechanism
`BL-0037`'s addendum to R211 §8 just grounded), not a general string-rewriting engine.

**L-systems demonstrably work for genuine musical *motif selection/recurrence* in real
compositional practice, not just as a graphical/algorithmic curiosity.** Composer Hanspeter
Kyburz's "Cells" (for saxophone and ensemble) "used results from 13 generations of L-system
rewrites to select pre-composed musical motifs" [search-synthesized description, primary source
not independently fetched — see Sources]. This confirms the specific application `BL-0010` asks
about — using L-system output to *select among a small set of recurring motifs* — is an
established, real-world compositional technique, not a speculative extension.

**A genuinely important limitation, confirmed by dedicated study, is that L-system-generated
melody quality degrades with derivation length — the opposite of what "more generations = richer
music" would suggest.** Worth & Stepney's study of musical L-system interpretations found that "a
typical L-system contains enough information to create only a short melody and still be
interesting, and at longer derivations the melodies begin to get dull with repeating sections"
[Worth & Stepney — Growing Music: Musical Interpretations of L-Systems, title/finding confirmed
via search, primary PDF not independently fetchable this pass — see Sources]. This is a **directly
actionable, load-bearing finding for Driftune specifically**: a naive "run the L-system longer for
more variety" design would be actively counterproductive. The correct design shape is a
**small, fixed-depth rule table re-applied per motif-recurrence event** (bounded derivation,
matching the "short melody, still interesting" finding), not an ever-growing derivation string —
structurally similar to Driftune's own `MOTIF_TABLE` (`IP-1070`, 8 fixed absolute-degree targets,
no growth over time), which is closer to this finding's own recommended shape than a
naive from-scratch L-system implementation would have been.

**Verdict: L-systems remain the recommended concrete technique for motif-recurrence**, now with a
specific, cited design constraint (bounded-depth rule application, weighted-probabilistic rule
choice, reusing the already-grounded weighted-lookup-table mechanism) rather than an open-ended
"L-systems are promising" note. This closes `BL-0010`'s motif-recurrence half at the research
layer — a concrete architecture/requirements pass is the correct next step, not further research,
per this topic's own §6 disposition.

### Addendum sources
- [McCormack — Grammar Based Music Composition](https://users.monash.edu/~jonmc/research/Papers/L-systemsMusic.pdf)
  (probabilistic L-systems for melody; primary PDF returned HTTP 403 on direct fetch this pass,
  title/author/core-finding confirmed via WebSearch's own synthesis of the paper's abstract/
  description — **flagged needs fetch-verification** for direct quotation-level citation)
- [Worth & Stepney — Growing Music: Musical Interpretations of L-Systems](https://ccrma.stanford.edu/~elisse/256A/final/growing%20music%20-%20musical%20interpretations%20of%20l-systems.pdf)
  (short-melody/dulls-at-length finding; primary PDF returned HTTP 403 on direct fetch this pass,
  finding confirmed via WebSearch's own synthesis — **flagged needs fetch-verification**)
- Kyburz "Cells" motif-selection-via-L-system-rewrites description — search-synthesized, no
  primary musicological source independently fetched this pass — **flagged needs
  fetch-verification**
- **Note on this addendum's citation confidence**: every primary source attempted for direct
  WebFetch in this research session returned HTTP 403 (a proxy/access constraint encountered this
  pass, not a claim about the sources' unavailability in general) — all three findings above rest
  on WebSearch's own synthesized summaries of real, named, findable sources rather than
  independently-verified full-text quotation. A future pass with working direct fetch access
  should upgrade these to primary-verified citations before this addendum is treated as
  fully closed-loop per this skill's own quality gate.

### Addendum implementation guidance
- **Design a motif-recurrence mechanism as a small, fixed-depth (not growing) rule table with
  weighted rule selection** — directly buildable on the same lookup-table-weighting mechanism this
  session's other addendum (R211 §8) just grounded, and structurally similar to `IP-1070`'s already
  -shipped `MOTIF_TABLE` (8 fixed targets, no derivation growth).
- **Do not implement an open-ended/growing L-system string** — Worth & Stepney's own finding is
  that longer derivations get *worse*, not richer; a bounded, re-triggered rule application per
  recurrence event is the correct shape.
- **`BL-0010`'s disposition should move from `DEFERRED` (research needed) to `SCHEDULED`
  (architecture-ready)** — the concrete design shape is now specified enough for
  `03-architecture-design-synthesis` to pick up directly, the same maturity level R220 reached for
  song-form before its own architecture pass.
