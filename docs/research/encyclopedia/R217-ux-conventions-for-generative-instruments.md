# R217 — UX Conventions for Generative Instruments (Seed Entry, Presets, Playback Controls)

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
  (lighter pass — most of this is out of GDS-01's current flat-design scope; documented so a
  future scope change has grounding, not because it's needed now)
- **Maps to user-provided research list:** Phase 7, items 81-88 (seed entry methods, menu design,
  visualization ideas, live parameter editing, preset management, song regeneration, pause/resume
  behavior, playback controls)

## 1. Purpose
Survey UX conventions for generative-music instruments/toys, honestly checked against GDS-01's
deliberate no-menu, no-pause, single-running-state design (MSTR-001 §4 non-goals) rather than
assumed as needed features.

## 2. Scope
Which of these 8 items are already answered by existing decisions, and which are genuinely
unaddressed future scope.

## 3. Concepts
- **Live parameter editing**: already shipped — this is exactly what R206's input-mapping
  research grounds (GDS-03 SS3). Not a gap.
- **Visualization**: already the subject of R205 (generative visualizer conventions) — not
  re-covered here, cross-referenced.
- **Playback controls / pause-resume**: explicitly a **non-goal** per MSTR-001 §4 ("no pause
  state") and GDS-01 SS ("no pause, no save, no exit... turning the device off is the only
  'stop'"). Not a gap — a deliberate design decision, restated here so this UX-research pass
  doesn't quietly reopen it.
- **Seed entry methods, menu design, preset management**: genuinely **unaddressed** — GDS-01's
  flat design has no menu state at all, so there is currently no UI surface for entering a seed or
  saving/loading a preset. If R213's DIV-seeding idea (a different seed each boot) or a
  save-a-favorite-preset idea (MSTR-001 C2's named non-goal, "no SRAM/battery save... yet") were
  ever pursued, they would need real menu-design work this research pass does not attempt to
  originate (menu/UI design without an existing convention to cite would be this skill inventing a
  spec, which its own gotchas explicitly forbid).
- ~~**song regeneration**: genuinely unaddressed, grouped with the three items above~~ —
  **CLOSED 2026-08-21. The grouping was the error; see §3a.** Regeneration needs no UI surface,
  and it shipped as a button.

### Sources
- Cross-references only (R205, R206, MSTR-001, GDS-01) — no new external citation needed; this
  topic's job is honestly triaging the user's list against decisions already made, not
  originating new UX conventions from outside sources this pass didn't find strong material for.

### 3a. Addendum 2026-08-21 — "song regeneration" closes, and the grouping that hid it for thirteen months

**Status: closed.** Delivered by [`ADR-0006`](../../architecture/adr/ADR-0006-select-becomes-reroll-not-reset.md):
Select becomes a **reroll** — it reseeds each pitched channel's LFSR (genuinely new melodic
material), clears the bad-zone fields, and **leaves the listener's five steering indices
untouched**. `GDS-01`'s flat single-running-state model is unchanged and **no `01-vision` change
was made or required**.

#### The premise §3 filed this under, and why it was right about three items and wrong about this one

§3 grouped song regeneration with seed entry, menu design and preset management on one shared
premise: *"GDS-01's flat design has no menu state at all, so there is currently no UI surface
for… explicitly 'regenerating.'"* §5 then routed the whole group through `01-vision`, because a
menu state is a scope change to the flat interaction model.

That premise is correct for the other three. A seed you type, a preset you name and recall, and a
menu you navigate all genuinely require a surface this ROM does not have. **It is not correct for
regeneration**, and the survey conventions this topic set out to gather are what show why:
regeneration in shipped generative instruments is consistently a **single control with no
parameters, no confirmation and no navigation** — Liquid Music offers a button that generates a
new variation when the current direction is unwanted; Orb Producer Suite's "Infinity" control
mutates continuously from one toggle; Playbeat exposes randomization as per-aspect controls, so a
user can reroll one dimension while explicitly holding the others
([audioservices.studio, "The Best Generative Sequencers"](https://audioservices.studio/blog/the-best-generative-sequencers-tips-and-tricks);
corroborated for the general "generate-a-new-variation control" pattern by
[zZounds, "Beat Tools: Generative Music Software"](https://blog.zzounds.com/2019/06/20/beat-tools-generative-music-software-for-pcs/)).
None of those is a menu. **Playbeat's shape is the closest analogue to what `ADR-0006` decided**:
reroll the generated material, hold the parameters the user chose. Driftune already has six
edge-triggered controls (`R206`/GDS-03 SS3); regeneration needed one of them, not a new surface.

> **Citation caveat, per this tier's own methodology.** The three products above are cited from
> search-result summaries rather than fetched product documentation, and the pattern is
> corroborated across two independent write-ups rather than resting on one. What they support is
> the modest claim actually being made — *a parameterless "give me a different result" control is
> an established shape in this product category, and at least one shipped tool pairs it with
> deliberately-held parameters* — not any quantitative claim. Flagged as needing
> fetch-verification if a future pass wants to lean harder on it.

#### Two things worth recording as this closes

1. **The capability was two-thirds present the whole time, and this topic's own filing is part of
   why nobody noticed.** `IP-0007` added the `DIV` reseed on Select in 2026-07 — that *is*
   regeneration's mechanism, and it has been shipping and verified (`VR-0007`) ever since. What
   made Select unusable as a reroll was not a missing capability but an unrelated one bolted to the
   same button: the reload of all five steering indices, itself a vestige of the era when Select was
   the engine's only bad-zone escape. **The real gap was never "we cannot regenerate"; it was
   "regenerating costs you your settings."** No document framed it that way, because this topic had
   already filed regeneration as unbuilt and behind a vision gate.
2. **A research gap parked behind a scope change should name the interaction surface it actually
   needs, not the category it resembles.** Had §3 written *"regeneration needs a control, and all
   six are already mapped (`R206`)"*, it would have been re-examined the moment a control's purpose
   came into question — which is exactly what happened in 2026-08 and would have connected
   immediately. Writing *"needs a menu"* attached it to a `01-vision` gate it never required, and
   nothing revisits a question filed behind a gate that will not open. This is a note on **how this
   topic files things**, not a defect in its conclusions: every one of §3's judgements about the
   other seven items still holds.

**Forward trace for this item** (per §6b's convention):
`ADR-0006` → `FR-1070` (amended in place, 2026-08-21) → the shipped Select handler.

### Sources
- [audioservices.studio — "The Best Generative Sequencers For Electronic Music"](https://audioservices.studio/blog/the-best-generative-sequencers-tips-and-tricks)
  (Orb Producer Suite's "Infinity" mutation control; Playbeat's per-aspect randomization, i.e.
  reroll-one-dimension-hold-the-rest; Liquid Music's generate-a-new-variation button)
- [zZounds Music Blog — "Beat Tools: Generative Music Software for PCs"](https://blog.zzounds.com/2019/06/20/beat-tools-generative-music-software-for-pcs/)
  (corroborating the parameterless "new variation" control as a category-wide pattern)
- Cross-references: `R206` (six controls, all mapped), `R213` (`DIV` seeding), `GDS-01`,
  `ADR-0006`, `IP-0007`/`VR-0007`.

## 4. Operational Context
No code implication — confirms existing scope boundaries.

## 5. Implementation Guidance
- **No action needed** for live-editing, visualization, or playback-control items — already
  correctly scoped (shipped, researched elsewhere, or a deliberate non-goal respectively).
- **If seed-entry/preset-save scope is ever requested**, it re-enters via `01-vision` (a menu state
  is a scope change to GDS-01's flat interaction model, per that document's own change-control
  note) — not something this research topic should pre-design speculatively.
- ~~regeneration~~ **left that list on 2026-08-21** (see §3a): it shipped as a **button**
  (`ADR-0006` → `FR-1070`), which adds no menu state and therefore needed no vision change. The
  general rule the correction leaves behind, applicable to every future parked item in this topic:
  **route a request by the interaction surface it actually needs, not by the category it
  resembles.** Concretely, for this project: an item needing only an edge-triggered action is a
  `R206`/GDS-03 SS3 control-budget question (six controls, all currently mapped — so the real
  question is always "which control changes meaning, and what does that retire?"), not a
  `01-vision` scope question.

## 6. Feature Mapping
No current `IP-xxxx`. Confirms MSTR-001 §4 / GDS-01's existing non-goals.

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

🟡 **PARTIAL EXCEPTION (amended 2026-08-21) — seven of the eight surveyed items confirm existing non-goals; one produced a feature.** Song regeneration shipped via `ADR-0006` → `FR-1070` → the Select handler (see §3a). The seven-item half of the original exception is unchanged and reads on: UX conventions for generative instruments (presets, undo, save/recall, visible parameter state). Its conclusion was that Driftune's deliberate *absence* of most of them is consistent with the ambient-instrument posture `MSTR-001` §4 and `GDS-01` already committed to — i.e. it validated a boundary rather than moving it. Cited by `ADS-100`, `ADS-101` and the strategic assumptions register, always in that confirming role. **One partial caveat worth naming**: the "make current parameter state visible" convention it documents *did* eventually ship, as `IP-1110`'s settings-indicator row — but by way of the user's own direct request and `ADS-104`, which cite `R205`/`R222`/`R223` rather than this topic. An honest exception with one near-miss, not a clean trace.

## 7. Related Topics
R205 (visualizer), R206 (input mapping, the "live editing" this topic confirms is answered), R213
(seed management options this topic's "seed entry" item would need a menu for, if ever pursued).
