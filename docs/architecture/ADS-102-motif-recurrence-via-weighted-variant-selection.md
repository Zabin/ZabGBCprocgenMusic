# ADS-102 — Motif Recurrence via Weighted Variant Selection

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored 2026-07-26
- **Dependencies:** R214 §8 (2026-07-26 deep-evaluation of L-systems for motif recurrence —
  bounded-depth/weighted-rule-selection finding), R211 §8 (weighted-lookup-table mechanism,
  grounds `DELTA_TABLE`), R212 (form/tension — the original motif-development gap), ADS-100/
  ADR-0001 (Scheme E's already-shipped `MOTIF_TABLE` mechanism, `IP-1070` — the structural
  precedent this design extends rather than replaces)
- **Produces:** a future `FS-xxx` (once `04-requirements-engineering` derives FRs from this
  document) and an eventual Implementation Package
- **Trigger:** `BL-0010`'s `SCHEDULED` disposition — R214 §8 closed the research layer and
  recommended "a concrete architecture/requirements pass is the correct next step," naming the
  design shape (small, fixed-depth, weighted-rule table) but not the concrete mechanism; this
  document is that mechanism decision

## 1. Executive Design Overview

`IP-1070` already shipped a literal motif-recurrence mechanism for Scheme E channels:
`MOTIF_TABLE = [0, 2, 4, 5, 4, 2, 0, 7]`, an 8-entry fixed sequence of absolute target degrees,
stepped through in order (wrapping mod 8) on every Euclidean-gated onset. This is recurrence, but
of exactly one motif, played back identically every 8 onsets forever — it has no *development*,
the gap R211/R212 originally flagged and R214 §8 deep-evaluated. R214 §8's verdict is specific and
load-bearing: probabilistic L-systems are the right *family* of technique (real compositional
precedent — Kyburz's "Cells" selects among pre-composed motifs via L-system-rewrite output — not
generation-from-scratch), but a naive "run the derivation longer for more variety" design is
actively wrong (Worth & Stepney: melody quality *degrades* at longer derivations). The correct
shape R214 §8 names is "a small, fixed-depth rule table re-applied per motif-recurrence event" —
structurally close to `MOTIF_TABLE` itself, not a growing string.

This design's decision: **extend the single `MOTIF_TABLE` into a small fixed set of motif
*variants*** (e.g. 4 rows, same 8-entry shape as today's table) and, at each natural recurrence
boundary — when the existing motif-step counter completes a full cycle (step wraps 7→0) — use a
**weighted lookup-table selection** (the same mechanism `R211 §8` already grounds for
`DELTA_TABLE`) to pick which variant plays for the *next* cycle. No L-system derivation engine is
built; the "L-system" contribution is fully absorbed into pre-composed variant rows plus a
weighted selector table, matching R214 §8's own observation that `MOTIF_TABLE`'s existing shape
is "closer to this finding's own recommended shape than a naive from-scratch L-system
implementation would have been." This is architecture-only: which module owns the mechanism,
how it interacts with the existing step counter, and the concrete v1 data shape. No code, no
byte layout beyond what's needed to state the decision.

## 2. System Architecture

Owned entirely by `music_engine.py`, the same module `IP-1070`'s Scheme E logic already lives in
(`_emit_channel_gen`, the `gt_e_*` label family, lines ~449-472 as of `IP-1080`'s tree state). No
new module — this is an extension of existing Scheme-E-only logic, not a new generation scheme
or a change to Scheme W (the shipped LFSR walk, unaffected).

```
Scheme-E onset (existing, unchanged — Euclidean pattern hit, gt_e_* path)
        │
        ▼
  motif_step advances (existing, bits4-6 of scheme_state, wrap mod 8)
        │
        ├─ step != 0 (mid-cycle) ──────────────────────────────┐
        │                                                       ▼
        └─ step == 0 (cycle just completed) ──► NEW: select   MOTIF_TABLE[variant_idx]
                     weighted variant_idx via                  [motif_step] read
                     MOTIF_VARIANT_SELECTOR                    (existing lookup,
                     (new table, LFSR-indexed,                  now variant-relative)
                     R211-§8-style weighting)
                     │
                     ▼
              MOTIF_VARIANT_IDX (new 1-byte WRAM field,
              persists across the next full 8-step cycle)
```

The existing motif-step counter (packed into `scheme_state` bits4-6, per `IP-1070`) is **read and
advanced exactly as it already is today** — this design does not touch that packing. The only new
runtime event is: on the frame the step counter wraps from 7 back to 0 (detected the same way the
existing wrap-and-mask arithmetic already produces — `AND 0x70` after the `+0x10` step naturally
yields 0 on the 8th advance), read `MOTIF_VARIANT_SELECTOR[lfsr_bits]` to pick a new
`MOTIF_VARIANT_IDX`, then use that index to select *which row* of a now-multi-row `MOTIF_TABLE`
the existing per-step lookup reads from for the next 8 onsets. Per-onset motif-value lookup logic
is otherwise unchanged — only the table's base address becomes `variant_idx`-relative
(`motif_table_base + variant_idx * 8`) instead of a single fixed table.

## 3. Domain Model

- **Motif variant**: one of a small, fixed set of complete 8-step absolute-degree sequences (the
  same shape as today's single `MOTIF_TABLE` row) — a pre-composed "cell" in Kyburz's sense, not a
  derivation output. Distinct from a **Scheme** (`ADS-100`'s per-channel note-selection
  *strategy*, of which Scheme E is one) and from a **Style** (`ADS-101`'s coordinated
  tempo/density/scale/duty bundle) — a motif variant only changes *which specific 8-note sequence*
  Scheme E plays, nothing else.
- **`MOTIF_TABLE`** (extended): becomes a 2D table, `N_VARIANTS` rows × 8 bytes each, replacing
  today's single 8-byte row. Row 0 is the existing shipped sequence
  (`[0, 2, 4, 5, 4, 2, 0, 7]`), preserved unchanged as variant 0 — the default/no-regression case.
- **`MOTIF_VARIANT_SELECTOR`** (new): a small LFSR-indexed lookup table, sized and populated per
  the R211-§8-grounded weighting mechanism — entries repeated in proportion to desired bias (e.g.
  weighted toward *staying* on the current/previous variant most of the time, occasionally
  switching), not a uniform draw across all variants every cycle. This directly encodes R214 §8's
  "short but interesting" constraint: recurrence dominates, variation is occasional, never a
  derivation that runs away from the original motif's character.
- **`MOTIF_VARIANT_IDX`** (new, 1 WRAM byte per Scheme-E-capable channel or one shared byte if v1
  scopes to a single Scheme-E channel at a time — see Open Questions): persists the currently
  active variant across a full 8-step cycle; read by the existing per-onset lookup, written only
  at cycle-boundary events.
- **v1 concrete shape** (proposed, for `07-implementation-planning` to confirm against real ROM
  budget and listening feel): `N_VARIANTS = 4` — variant 0 the existing shipped sequence
  (unchanged, satisfies no-regression), variants 1-3 new hand-composed 8-step sequences chosen for
  family resemblance to variant 0 (shared start/end degree, differing middle contour) rather than
  unrelated new melodic material — matching R214 §8's "selection among pre-composed motifs," not
  independent composition per variant.

## 4. User Stories

- As a listener with a Scheme-E channel active, the melodic material still clearly recurs (the
  same core motif shape is recognizable cycle to cycle, per R214 §8's "short melody, still
  interesting" finding) but occasionally shifts to a related variant, rather than looping one
  fixed 8-note sequence forever — audible development without losing recurrence.
- As a listener who has not touched any control, this happens autonomously (matching bad-zone
  recovery's and R220's own precedent of autonomous, no-input-required behavior) — no new button
  is spent on it.
- As a developer verifying no regression, `CHMIX_IDX` preset 6 (`IP-1070`'s existing sole
  Scheme-E-assigning preset) with variant selection forced/seeded to variant 0 for the entire run
  reproduces today's exact shipped sequence, byte for byte.

## 5. Functional Requirements (candidate — for `04-requirements-engineering` to formalize)

- FR-candidate: `MOTIF_TABLE` is extended to `N_VARIANTS` rows (proposed 4); row 0 is byte-
  identical to the currently shipped 8-entry sequence.
- FR-candidate: On the frame a Scheme-E channel's motif-step counter completes a full 8-step
  cycle (wraps to 0), the engine draws a new `MOTIF_VARIANT_IDX` via `MOTIF_VARIANT_SELECTOR`'s
  weighted lookup, autonomously, with no input required.
- FR-candidate: `MOTIF_VARIANT_SELECTOR`'s weighting is biased toward retaining the current
  variant across most cycle boundaries (occasional switch, not per-cycle reshuffling) — the
  concrete weighting ratio is an implementation-time tuning decision (§9), not fixed here.
- FR-candidate: With `MOTIF_VARIANT_IDX` held at 0 for an entire run (e.g. via a
  test-only/debug seed), Scheme E's output is byte-identical to the pre-`ADS-102` shipped
  behavior — the existing `IP-1070` regression tests must continue to pass unmodified.

## 6. Non-functional Requirements (candidate)

- ROM budget: `N_VARIANTS = 4` rows × 8 bytes = 32 bytes for `MOTIF_TABLE` (up from today's 8
  bytes, net +24), plus a small `MOTIF_VARIANT_SELECTOR` table (comparable in size to
  `DELTA_TABLE`'s 4 bytes, likely 8-16 bytes to encode a real weighting curve) — well inside the
  measured free-ROM headroom (`ADR-0002`'s instrumentation; `IP-1080` alone used only 78 bytes of
  a 29349-byte-free budget, so a comparably-sized addition here is negligible).
- WRAM budget: 1 new byte (`MOTIF_VARIANT_IDX`) if v1 scopes to a single Scheme-E channel at a
  time (today's only shipped Scheme-E preset, `CHMIX_IDX=6`, assigns it to exactly one channel,
  wave) — see Open Questions for the multi-channel-Scheme-E case.
- No new input control — fully autonomous, same class of behavior as bad-zone recovery
  (`IP-0007`) and distinct from `ADS-100`/`ADS-101`'s user-triggered selections.

## 7. Constraints

- **No open-ended derivation string** — the single hardest constraint R214 §8 establishes.
  Whatever is built must be bounded: a fixed small row count, no recursive rewriting, no growth
  over session length. This design satisfies it by construction (variant rows are pre-composed
  and static; only the *selector* runs at runtime, and it selects among existing rows, never
  derives new ones).
- **Reuses, does not replace, `IP-1070`'s existing motif-step mechanism** — the step counter's
  packing into `scheme_state` bits4-6 and its per-onset advance logic are unchanged; this design
  only adds a variant dimension orthogonal to the step dimension already there.
- **Reuses the already-grounded weighted-lookup-table idiom** (R211 §8) rather than inventing a
  new randomization primitive — `MOTIF_VARIANT_SELECTOR` is built the same way `DELTA_TABLE`
  already is: an LFSR-indexed table whose entry *repetition* encodes the desired bias.
- **Scheme-W (LFSR walk) channels are entirely unaffected** — this design is scoped to Scheme E's
  existing motif mechanism only; Scheme W has no motif concept to extend.

## 8. Risks

- **Variant transitions could read as a discontinuity/jump rather than "development"** if a new
  variant's degree sequence doesn't share enough contour with the outgoing one — mitigated by the
  v1 constraint (§3) that variants 1-3 are composed for family resemblance to variant 0, not
  independently; final judgment belongs to `09-content-review`, not asserted as solved here.
- **Interaction with `IP-1080`'s style presets**: a style change (Start press, `ADS-101`) is
  immediate and could land mid-cycle relative to a motif-variant boundary; this design does not
  special-case that interaction (the motif mechanism keeps ticking exactly as `ADS-101`'s own
  "bad-zone bookkeeping stays scheme/style-agnostic" precedent already established for other
  per-frame state) — named here so a future verification pass explicitly checks it rather than
  assuming it, same caution `BL-0040` already surfaced for a different combination.
- **Choosing `N_VARIANTS` and the selector's weighting curve are real tuning decisions** with no
  single objectively-correct answer from the research alone — R214 §8 grounds the *shape*
  (bounded, weighted, biased-toward-retention) but not exact numbers; flagged for
  `07-implementation-planning`/a content-authoring listening pass, not fixed here (§9).

## 9. Open Questions

- **Does `MOTIF_VARIANT_IDX` need to be per-channel or can v1 use a single shared byte?** Today's
  only shipped Scheme-E preset (`CHMIX_IDX=6`) assigns Scheme E to exactly one channel (wave), so
  a single shared byte suffices for v1 without loss of generality. If a future preset-data pass
  (per `BL-0032`'s follow-up) assigns Scheme E to multiple channels simultaneously, this needs
  revisiting — deliberately left open rather than over-built for a case not yet shipped.
- **What is the concrete `N_VARIANTS` count and `MOTIF_VARIANT_SELECTOR` weighting curve?** §3
  proposes 4 variants and a retention-biased selector as a starting point; the exact numbers are
  an implementation/content-authoring-time tuning decision, to be confirmed by ear (same class of
  decision `BL-0005`'s standing "presets are untuned placeholders" disposition already tracks) —
  not fixed by this architecture pass.
- **Should variant composition itself be assisted by an actual L-system rewrite step at
  content-authoring time** (offline, producing the static variant rows a human/script selects
  from), **or should the 3-4 variant rows simply be hand-composed** (matching `MOTIF_TABLE`
  row 0's own origin)? Either satisfies R214 §8's "pre-composed motifs, selected via
  L-system-derived choice" framing — the *selection* mechanism (runtime, weighted) is what R214 §8
  actually requires be L-system-flavored, not necessarily the variants' own authoring process.
  Left to `08-content-authoring` to decide pragmatically.
- **Should this eventually interact with R220's song-form state machine** (e.g. biasing variant
  selection toward "denser"/"sparser" variants during a build/breakdown phase, once R6 is built)?
  Real, natural future integration point — explicitly out of this design's v1 scope (R6 is its own
  separate, already-named roadmap release), named here so it isn't lost.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-26 | Motif recurrence is realized as a small, fixed set of pre-composed motif variants (extending `MOTIF_TABLE` from 1 row to `N_VARIANTS` rows), selected at cycle-boundary events via a weighted lookup table — not an L-system derivation engine. | Directly satisfies R214 §8's load-bearing constraint (melody quality degrades at longer derivations; the correct shape is bounded, pre-composed, weighted-selection, not growth) while reusing two already-shipped, already-grounded mechanisms (`IP-1070`'s motif-step counter, R211 §8's weighted-lookup-table idiom) rather than inventing a new one. |
| 2026-07-26 | Variant selection happens only at natural cycle-boundary events (motif-step wraps 7→0), not every onset. | Matches R214 §8's "short melody, still interesting" finding — variation should be occasional and structural (whole-cycle grain), not per-note, which would read as noise rather than development. |
| 2026-07-26 | Variant row 0 is byte-identical to today's shipped `MOTIF_TABLE`, preserved as the default. | No-regression discipline, same pattern every prior extension of shipped behavior in this project has followed (`ADS-100`/`ADS-101`'s own preset-0/style-0 non-regression requirements). |
| 2026-07-26 | Exact `N_VARIANTS` count and selector weighting curve left as an Open Question for implementation/content-authoring time, not fixed here. | R214 §8 grounds the *shape* of the solution, not specific tuning numbers — matching the existing, standing `BL-0005` disposition that preset/table values are tuned by ear at a later, more appropriate stage, not guessed at architecture time. |
