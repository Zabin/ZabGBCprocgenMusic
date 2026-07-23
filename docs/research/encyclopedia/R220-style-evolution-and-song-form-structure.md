# R220 — Style Evolution, Blending & Song-Form Structure

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-22
- **Trigger:** MSTR-001 §9 (v1.2) — style evolution/drift/blending (user's §5) and musical
  structure (§10: beginning/build/peak/breakdown/ending, endless playback). Extends the
  already-open `BL-0010` research gap (no cheap technique previously found for phrase/motif/
  song-structure generation) and follows up R214 SS5's L-system flag, per this topic's own
  intake instruction.

## 1. Purpose

Identify SM83-tractable techniques for (a) a listening session's musical style drifting,
blending, or migrating over time rather than staying static, and (b) a recognizable song-form arc
(intro → build → peak → breakdown → ending, looped or endless) — both currently absent from
Driftune's shipped engine, which generates continuous undifferentiated texture with no structural
state.

## 2. Scope

Two related but distinct questions: style evolution (which *parameters* drift, and by what
mechanism) and song-form structure (whether a *state machine* over those parameters can produce a
recognizable arc cheaply). Does not re-litigate R214's genre-agnostic CA/L-system survey — builds
on it directly.

## 3. Concepts

**Song-form structure is a solved, cheap problem in adaptive game audio — as parameter
envelopes over existing state, not new composition.** The standard game-audio toolkit for
non-linear music is **horizontal re-sequencing** (slicing music into segments with defined
entry/exit points that branch or transition) and **vertical layering** (stacking
compatible layers, adding/removing them based on game state) [The Game Audio Co. — Vertical
Layering vs. Horizontal Resequencing](https://www.thegameaudioco.com/making-your-game-s-music-more-dynamic-vertical-layering-vs-horizontal-resequencing);
[Silen Audio — Vertical v Horizontal Musical Resequencing](https://www.silen.audio/2022/12/14/quick-game-audio-tutorial-vertical-v-horizontal-musical-resequencing/).
"The most compelling soundtracks often blend vertical layering and horizontal resequencing" —
horizontal switching between sections, vertical layering adjusting intensity *within* a section
[same source]. Critically for a from-scratch engine like Driftune's: **neither technique requires
authored music segments** — they are re-sequencing/layering *mechanisms* applied to whatever the
generator produces. A song-form arc can be built as a small state machine (e.g. `INTRO` →
`BUILD` → `PEAK` → `BREAKDOWN` → repeat) that drives the *existing* engine parameters (tempo,
density, active-channel count, dissonance tolerance) through an envelope per state, using the same
WRAM-parameter-index mechanism `music_engine.py` already has (`TEMPO_IDX`/`DENSITY_IDX`/etc.) —
vertical layering, in this project's own vocabulary, since it's channel-activity/intensity
layering over one continuous generative texture rather than switching between authored tracks.

**Style evolution/drift is the same mechanism at a slower cadence.** No new citation is needed
beyond the above: a "style" in Driftune's terms is a point in the same parameter space
(tempo/density/scale/channel-mix/dissonance-tolerance) song-form states already move through;
drifting between styles across a session is song-form structure's state machine running on a much
longer timescale (minutes, not bars), with interpolation between parameter envelopes instead of
hard cuts between states.

**L-systems remain the most promising specific answer to the harder problem — genuine phrase/
motif recurrence** (R214 SS5's flag, still not adopted). A concrete precedent exists: composer
Hanspeter Kyburz used 13 generations of L-system rewrites to *select among pre-composed musical
motifs* for his ensemble work "Cells" [general algorithmic-composition literature, cited via R214].
This is a meaningfully different, harder problem than song-form/style-drift (recognizable *motif
return*, not just parameter-envelope structure) and stays a named, unscheduled upgrade path, not
solved by this topic.

**Genetic/generative-parameter mapping precedent for "progressive"/long-form development**: patent
literature on automated composition systems (broad prior art survey, not a specific technique
recommendation) confirms parameter-mapping-driven composition is an active, real engineering
approach at scale [USPTO — Automated music composition and generation systems employing parameter
mapping configurations](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11037540) —
cited here only to confirm the *category* (parameter-mapped generation) is a real engineering
family, not to recommend adopting patent-specific techniques.

### Sources
- [The Game Audio Co. — Making Your Game's Music More Dynamic: Vertical Layering vs. Horizontal Resequencing](https://www.thegameaudioco.com/making-your-game-s-music-more-dynamic-vertical-layering-vs-horizontal-resequencing)
- [Silen Audio — Quick Game Audio Tutorial: Vertical v Horizontal Musical Resequencing](https://www.silen.audio/2022/12/14/quick-game-audio-tutorial-vertical-v-horizontal-musical-resequencing/)
- [Game Developer — Horizontal resequencing and dynamic transitions for game music composers](https://www.gamedeveloper.com/audio/horizontal-resequencing-and-dynamic-transitions-for-game-music-composers)
- R214 (L-system/Kyburz precedent, already cited there; restated here for this topic's own
  song-structure framing, not re-researched)
- [USPTO 11037540 — parameter mapping configurations for automated composition](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11037540)
  (category confirmation only — single-source, flagged, not a specific-technique citation)

## 4. Operational Context

Driftune ships no song-form or style-drift mechanism today — `music_engine.py`'s
`engine_tick`/`_emit_channel_gen` produce continuous, structurally-flat texture; the only existing
"state machine" of any kind is the bad-zone detect/recover loop (`IP-0007`), which is reactive
(triggered by a dissonance/repetition/overload metric), not a scheduled structural arc.

## 5. Implementation Guidance

- **Song-form structure and style evolution are the same mechanism at two timescales — do not
  architect them as two separate systems.** Both reduce to a state machine driving the existing
  parameter-index WRAM fields through envelopes; a future architecture pass should design one
  mechanism parameterized by cadence (bars for song-form, minutes for style-drift), not duplicate
  logic.
- **This is genuinely cheap on SM83**: a state-machine tick (which state, how many frames/bars
  remain, what parameter targets) is comparable in cost to the existing `badzone_tick` — no new
  arithmetic complexity class, unlike L-systems or true multi-voice harmony.
- **Recommend NOT pursuing L-system-based phrase/motif recurrence in the same pass as song-form/
  style-drift** — it is a materially harder, still-unsolved-for-this-hardware problem (needs a
  string-rewriting engine and a motif table, R214 SS5) and should stay a separate, later-scheduled
  backlog item, folding `BL-0010` forward rather than blocking song-form work on it.
- **A concrete architecture decision this unlocks**: whether the bad-zone recovery mechanism
  (`IP-0007`) and a future song-form/style state machine should share one "meta-state" WRAM byte
  or stay independent — flagged for `03-architecture-design-synthesis`, not decided here.

## 6. Feature Mapping

No current `IP-xxxx`. Grounds a future `BL-0010`-successor feature (song-form + style-drift as one
parameter-envelope state machine) if/when `03-architecture-design-synthesis`/
`04-requirements-engineering` pick it up, per MSTR-001 §9's routing.

## 7. Related Topics

R201 (baseline generation algorithm this drives), R204 (bad-zone state machine — the closest
existing precedent for a "meta-state" driving engine parameters), R211/R212/`BL-0010` (the
original phrase/motif/form gap this topic extends), R214 (L-system/CA survey, motif-recurrence
precedent), R219 (genre feasibility — style-drift is how Driftune would move *between* the
genre-adjacent parameter regions R219 identifies), R221 (emotional/energy model — the third
parameter-space dimension a style/song-form state machine would also drive).
