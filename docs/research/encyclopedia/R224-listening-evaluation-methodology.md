# R224 — Listening-Evaluation Methodology: Structured, Per-Parameter Critique Elicitation

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-08-08
- **Trigger:** `BL-0097` — `09-content-review` has never run in this project's history, and 15
  constants in `music_engine.py` are first-guess/not-tuned-by-ear (tempo steps, scale semitone
  sets, Euclidean density patterns, `DISSONANCE_THRESHOLD`/`STALE_THRESHOLD`/`OVERLOAD_THRESHOLD`,
  `STYLE_TABLE` rows, `SONG_TABLE` phase targets, motif variants (`N_VARIANTS`), `VALENCE_TABLE`).
  This topic grounds *how to ask a listener about those constants* so a future `09-content-review`
  pass produces actionable, per-parameter findings instead of an undifferentiated "sounds fine"/
  "sounds off" reaction.

## 1. Purpose

Determine a citation-grounded method for turning a listening session into a **structured set of
targeted questions, one per tunable engine parameter**, so a reviewer's feedback can be routed
directly back to a specific constant or table row — the same way `09-content-review`'s own charter
already separates "judge whether the rendered/sounded result satisfies design intent" from fixing
anything itself. Undirected listening ("does this sound good?") cannot localize a defect to
`DISSONANCE_THRESHOLD=20` vs. `STYLE_TABLE` row 2's duty bias vs. `N_VARIANTS=4`'s weighting curve;
a structured elicitation method can.

## 2. Concepts

**Standardized listening-test protocols exist specifically to make subjective audio judgments
comparable and repeatable, not just plausible.** MUSHRA (ITU-R BS.1534) is "a controlled perceptual
evaluation protocol... for quantifying perceived audio quality across multiple systems or
conditions," using "a hidden reference, standard anchors, and the systems under test," with items
"randomized" and raters scoring "on a 0-100 scale" with "seamless switching among stimuli...
permitted prior to score submission" [TestDevLab — MUSHRA methodology](https://www.testdevlab.com/blog/how-we-conduct-listening-tests-mushra-methodology-from-itu-r-recommendations).
The core transferable idea for Driftune is **not the 0-100 scale** (built for codec-quality
discrimination, a different question) but the **structural discipline**: compare specific,
bounded stimuli against a known-good reference/anchor, with the comparison isolated per axis rather
than one global "quality" judgment.

**Generative-music evaluation has no single standard, but converges on decomposing "does it sound
good" into named sub-dimensions rather than asking it directly.** A survey of AI-music evaluation
found researchers "combining objective musical metrics (polyphony, scale consistency...) analysis
and subjective query metrics (harmonious, rhythmic, musically structured, and coherent)" as
*separate* rated dimensions, and that listeners are typically asked to "rate each excerpt in terms
of acoustic quality and musical quality" as distinct axes, often on a five-point Likert scale
[arXiv 2308.13736 — Comprehensive Survey for Evaluation Methodologies of AI-Generated Music](https://ar5iv.labs.arxiv.org/html/2308.13736).
This is direct precedent for splitting Driftune's own review into one question-set per parameter
(tempo, register, mode, density, dissonance recovery, style, motif, form, mood) instead of one
overall verdict.

**Osgood's semantic differential method gives a concrete, validated question *format* for isolating
a single perceptual axis.** Osgood's cross-cultural research found three reliable dimensions of
affective meaning — "evaluation (good-bad), potency (high-low) and activity (fast-slow)" — and
that "a seven-point semantic differential scale produced consistent, reliable results across dozens
of descriptive attributes" [SimplyPsychology — Semantic Differential Scale](https://www.simplypsychology.org/semantic-differential.html).
Applied to Driftune, each parameter's question becomes a bipolar-adjective-pair rating
("cluttered—sparse," "tense—resolved," "predictable—surprising") rather than a free-text or
single-verdict prompt, which keeps the reviewer's attention on one axis at a time and produces a
comparable score across review passes (e.g. before/after retuning `DENSITY_TABLE`).

**Isolating one attribute at a time via direct A/B comparison is the established technical
ear-training method, not a novel proposal.** Corey's technical-ear-training curriculum trains
listeners using "pink noise with single EQ bands boosted or cut, allowing you to toggle between the
flat signal and the processed signal to select which frequency band was changed"
[Critical Listening Lab](https://www.criticallisteninglab.com/en/demo); the underlying discipline —
change exactly one variable, hold everything else fixed, ask the listener to identify/rate only
that change — is exactly what Driftune's own control surface (`input_map.py`'s one-button-one-
parameter mapping) already makes cheap to construct: press Up/Down in isolation and only tempo
changed, so the question that follows can safely be scoped to tempo alone.

**Player-facing game-music evaluation literature separates "does the listener perceive the
intended effect" from "does the listener enjoy it," and recommends asking both.** A review of game
music evaluation methods frames the two questions as: whether the music "affects the player in the
intended way" (a *manipulation-check* question — did this parameter read as designed?) versus
whether it "leads to a more enjoyable experience" (a *quality* question) — treated as separate,
both-necessary axes, not a single collapsed rating [ResearchGate — Methodological approaches to the
evaluation of game music systems](https://www.researchgate.net/publication/266661267_Methodological_approaches_to_the_evaluation_of_game_music_systems).
This maps directly onto Driftune's constants: a manipulation-check question ("did pressing B
audibly increase note density, and did it still feel controllable?") is answerable even by a
reviewer who dislikes the result, and is the more diagnostic of the two for routing a fix to a
specific constant.

### Sources
- [TestDevLab — How We Conduct Listening Tests Based on MUSHRA Methodology](https://www.testdevlab.com/blog/how-we-conduct-listening-tests-mushra-methodology-from-itu-r-recommendations)
- [arXiv 2308.13736 — A Comprehensive Survey for Evaluation Methodologies of AI-Generated Music](https://ar5iv.labs.arxiv.org/html/2308.13736)
- [SimplyPsychology — Semantic Differential Scale: Definition, Questions, Examples](https://www.simplypsychology.org/semantic-differential.html)
- [Critical Listening Lab — ear-training exercises isolating single audio attributes](https://www.criticallisteninglab.com/en/demo)
  (Corey's *Audio Production and Critical Listening: Technical Ear Training* is the underlying
  textbook source for this method; the web resource is the accessible corroborating citation
  fetched this pass — flagged "needs fetch-verification" against the book itself if a future pass
  wants the primary text.)
- [ResearchGate — Methodological approaches to the evaluation of game music systems](https://www.researchgate.net/publication/266661267_Methodological_approaches_to_the_evaluation_of_game_music_systems)

## 3. Operational Context

Driftune's own control surface already isolates parameters mechanically — `input_map.py`'s
one-button-one-parameter mapping (R206) means a reviewer can trigger *exactly one* parameter change
per button press with everything else held constant, which is precisely the A/B isolation
discipline §2 describes, already free to exercise without any new tooling. `run-driftune`'s
scriptable PyBoy driving (R301/R305) can additionally hold a seed fixed while stepping a single
WRAM constant (e.g. `DISSONANCE_THRESHOLD`) across two builds, giving a true hidden-reference-style
A/B without needing the reviewer to press buttons at all — useful for the table-constant class of
tuning debt (`STYLE_TABLE`, `SONG_TABLE`, `VALENCE_TABLE`, `N_VARIANTS`'s weighting curve) that
isn't reachable by any single button.

## 4. Implementation Guidance

**Recommended structure for a `09-content-review` question set: one manipulation-check question +
one semantic-differential rating per tunable parameter, grouped by how the reviewer reaches it.**

- **Button-reachable parameters (direct A/B via `input_map.py`, no rebuild needed):**
  - *Tempo* (`TEMPO_IDX`, Up/Down): manipulation-check — "after one press, did the tempo change
    land as a single clear step, or did it feel like nothing happened / like it jumped too far?";
    rating — sluggish—driving.
  - *Register* (`OCTAVE_IDX`, Right/Left): manipulation-check — "does the octave shift stay
    musically usable at both extremes, or does it leave the mix (e.g. bass channel) sounding wrong
    at the top/bottom of its 4-step range?"; rating — muddy—thin.
  - *Mode* (`SCALE_IDX`, A): manipulation-check — "is each of the 4 scale choices clearly a
    different mood, or do two of them sound interchangeable?"; rating — dark—bright (ties to
    `VALENCE_TABLE`, R221).
  - *Density* (`DENSITY_IDX`, B): manipulation-check — "at the densest setting, can you still track
    the melody, or does it read as noise?" (directly operationalizes R203's clutter-threshold
    concern); rating — sparse—cluttered.
  - *Channel-mix/style* (`CHMIX_IDX`, Start): manipulation-check — "does the 4-step blend into the
    new style feel like a transition, or an abrupt cut?" (tests `IP-1130`'s glide, not just the
    destination); rating — abrupt—smooth.
  - *Bad-zone recovery* (Select, or letting `DISSONANCE_THRESHOLD`/`STALE_THRESHOLD`/
    `OVERLOAD_THRESHOLD` trigger during free play): manipulation-check — "when the music sounds
    like it's stuck or clashing, does it recognizably pull itself back toward something coherent,
    and does that take a noticeable-but-not-jarring amount of time?"; rating — never-recovers—
    over-corrects (a two-sided scale, since either extreme is a defect per R204).
- **Table/constant parameters not reachable by any single button (needs a fixed-seed A/B build
  pair via `run-driftune`, per §3):**
  - *Motif variation* (`N_VARIANTS=4`, weighting curve): "across several repeats of the same
    phrase, do the variants feel like *variations on a theme*, or like unrelated fragments /
    exact repetition?"; rating — repetitive—incoherent.
  - *Song-form phases* (`SONG_TABLE`): "does the piece's overall arc (build/peak/etc.) feel like it
    goes somewhere, or does it feel flat regardless of phase?"; rating — static—dynamic.
  - *Style presets* (`STYLE_TABLE` rows): one manipulation-check per shipped style ("does this
    preset read as the genre it's named for, at all, to an untrained ear?").
- **Always pair the manipulation-check with the rating, in that order.** The manipulation-check
  question is answerable independent of taste and is what routes a finding to a *specific* constant
  ("density's manipulation-check failed at max" → look at the Euclidean density pattern table, not
  guess broadly); the rating question is what tells `07-implementation-planning`/`08-content-
  authoring` *which direction* to move the constant. Per §2's game-music-evaluation citation,
  collapsing the two into one "did you like it" question loses exactly this routing information.
- **Do not invent a 0-100 MUSHRA-style score for Driftune.** MUSHRA's numeric scale is built for
  fine-grained *codec*-quality discrimination against a hidden reference the listener has heard
  before; Driftune has no reference recording to hide, and a 7-point semantic-differential pair per
  axis (Osgood's validated format) is the better-fitted, already-cited alternative for a small,
  informal review panel.

## 5. Feature Mapping

No current `IP-xxxx`. Grounds `09-content-review`'s first-ever invocation (per `BL-0097`'s
recommendation and the roadmap's R12.5 Content & Musical Quality Pass) — the question-set structure
above is intended to be lifted directly into that review's own listening-session design, not
re-derived from scratch when the review finally runs.

## 5b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⚠️ **EXCEPTION — grounds a not-yet-run pipeline stage, no code descends from it.** `09-content-review`
has never executed on any branch (`BL-0097`); this topic exists to be consumed by that stage's first
run, not by any `IP-xxxx`. Not stale — a live, named dependency of a scheduled pipeline step
(`BL-0097`, `SCHEDULED`).

## 6. Related Topics

R204 (bad-zone detection — the dissonance/stale/overload thresholds this topic's question set
targets directly), R206 (button-parameter mapping — the mechanical isolation this method leans on),
R220 (style evolution/song-form — `STYLE_TABLE`/`SONG_TABLE`, both named above), R221
(emotional/energy mapping — `VALENCE_TABLE`, the mode rating question), `09-content-review`
(the downstream consumer), `BL-0097`/`BL-0005` (the tuning-debt findings this topic answers).
