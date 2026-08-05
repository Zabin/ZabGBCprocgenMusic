# ADS-106 — Visual Evolution & Audio-Visual Synchronization (roadmap R9)

- **Status:** ✅ Authored 2026-07-31 · **Owned by:** `03-architecture-design-synthesis`
- **Dependencies:** [`R222`](../research/encyclopedia/R222-visual-evolution-conventions.md)
  (palette-swap-only convention, day/night/seasonal precedent, color-cycling as a named follow-up
  technique); [`R223`](../research/encyclopedia/R223-audio-visual-synchronization.md) (pitch as
  the highest-confidence sync signal, green-channel intensity mapping, no real-time audio
  analysis needed); [`R104` §7-8](../research/encyclopedia/R104-cgb-palette-system.md) (VRAM/ROM
  budget — palette-only theming costs ~8 bytes/theme, negligible against measured 29349-byte
  headroom, `ADR-0002`); [`GDS-08`](08-presentation-architecture.md) §4.2 (palette-swap already
  adopted as the standing extension strategy), §4.3 (the "never carry a state distinction by
  color alone" principle), §6 (the four deferred reactive-signal placements — style is already
  named "the natural first palette theme," song-form "wants both mechanisms"); `ADS-105`/`IP-1120`
  (roadmap R7, shipped this session — `AROUSAL`/`VALENCE`, currently no consumer); `MSTR-001` v1.5
  §9 (this thread's promotion to "concretely groundable," closing the prerequisite this release
  previously named as unsatisfied); `docs/roadmap/04-release-roadmap.md` R9,
  `docs/roadmap/06-feature-specifications.md` RM-9000/RM-9001/RM-9002/RM-9003.
- **Produces:** the future `FS-1xx` for R9's feature work (`FEAT-11xx`-equivalent catalog entries
  for RM-9001/RM-9002/RM-9003).

## 1. Executive Design Overview

R9 extends the shipped visualizer (2 channel-activity tiles' worth of logic plus `IP-1110`'s 5
settings-indicator cells, all reading a flat calm/bad-zone palette swap) so the screen's overall
color character changes with **style** (`CHMIX_IDX`/`STYLE_TABLE`, roadmap R5) and, later,
**mood** (`AROUSAL`/`VALENCE`, roadmap R7) — without inventing a second rendering path. Both `R222`
and `R223` deliberately stopped short of the actual selection-rule design, naming it as this ADS's
job; `R104` §7-8 already proved the budget is not a constraint by any measure.

**The central design decision this ADS makes:** a **single new style-keyed theme-palette table**
(`THEME_TABLE`, one row per `CHMIX_IDX` preset, in `visuals.py`) replaces the flat `CALM_PALETTE`
constant as the non-bad-zone color source — selected by reading `CHMIX_IDX` directly (already
WRAM-resident, already read every frame's palette-write path), no new engine state, no new
per-frame cost beyond the existing calm/bad-zone write `IP-0006` already performs every frame.
`BAD_ZONE_FLAGS` **always overrides** the theme, exactly as it already overrides the plain
calm palette today — the safety-relevant signal never loses to a style choice.

**What v1 explicitly ships and what it explicitly defers, matching the same staged-scope pattern
`ADS-103` used for song-form (ship the state machine, defer style-drift) and `ADS-105` used for
R7 (ship the derivation, defer the consumer):**

- **Ships (v1, `RM-9001`):** the `THEME_TABLE` mechanism, style-keyed, discrete (no color-cycling
  yet), `BAD_ZONE_FLAGS`-overridden.
- **Deferred (v1.1, `RM-9002`):** mood-modulation via `AROUSAL`/`VALENCE` — the first real
  consumer of `IP-1120`'s output — reusing the identical selection-rule shape, not a new
  mechanism.
- **Deferred (v1.1+, unscheduled):** song-form-phase-driven color-cycling (`GDS-08` §6 point 3 —
  "the phase transition should read as a drift rather than a snap"), and any new audio-visual
  sync *indicator* signal beyond the theme palette itself.

This is a genuine, load-bearing scope decision, not a punt: combining style × mood into one
theme-selection index today would require deciding a taxonomy for their cross-product before
either axis has a single shipped consumer to validate against — the same over-scoping risk `R222`
§5 itself warns against ("do not invent a bespoke visual mood taxonomy"). Shipping style alone
first, then mood as a proven second application of the identical mechanism, is the cheaper and
more honest path.

## 2. System Architecture

`visuals.py` gains one new ROM-resident data table, `THEME_TABLE`, in the same declaration
neighborhood as `CALM_PALETTE`/`BAD_PALETTE` (`visuals.py:87-88`):

```python
# ADS-106 (roadmap R9): one 4-color theme palette per CHMIX_IDX preset (8 entries, matching
# STYLE_TABLE's own row count) -- replaces the flat CALM_PALETTE as the non-bad-zone color
# source. Index 0 matches CALM_PALETTE exactly (no-regression contract, same discipline
# STYLE_TABLE/SONG_TABLE/MOTIF_TABLE's own index-0 rows already established).
THEME_TABLE = [
    CALM_PALETTE,        # 0: default -- byte-identical to the shipped calm palette
    [...],                # 1: Techno/Chiptune-Driving
    [...],                # 2: Ambient/Lo-Fi
    [...],                # 3: Holiday
    CALM_PALETTE, CALM_PALETTE, CALM_PALETTE, CALM_PALETTE,  # 4-7: unassigned, default row
]
```

**Deliberately independent of `STYLE_TABLE`, not derived from it.** `GDS-03` §1's acyclic-import
rule keeps `visuals.py` from ever importing `music_engine.py` — `visuals.py` already reads
`CHMIX_IDX` as a plain WRAM byte (via `wram_constants.py`, `IP-8020`) without needing the style
*content* `STYLE_TABLE` encodes. `THEME_TABLE` is a second, independent data table keyed by the
same index, exactly the same relationship `IP-1110`'s settings indicators already have with the
five steering indices — reading an index, never reading another module's table.

`_emit_write_palette`'s existing call site (the one per-frame palette write `IP-0006` already
performs) changes its **calm-branch source** from the flat `CALM_PALETTE` constant to
`THEME_TABLE[CHMIX_IDX]` — an indexed table read, same `_ld_hl_label`/`ADD_HL_BC`/`LD_A_HL`-family
idiom every other indexed lookup in this codebase already uses (`delta_table`, `chmix_masks_table`,
`IP-1120`'s own `valence_table`). The **bad-zone branch is entirely unchanged**: `BAD_ZONE_FLAGS`
set still selects `BAD_PALETTE` unconditionally, regardless of `CHMIX_IDX`.

**No new WRAM state, no new recompute-on-write routine.** Unlike `IP-1120` (which needed a stored,
recomputed-on-write pair because `AROUSAL`/`VALENCE` are *derived* from three other fields),
`CHMIX_IDX` is already the single source of truth and already read every frame by the existing
palette-write path — this is a pure data-table-swap, the cheapest possible shape `R222` §5
recommends, adding zero new per-frame reads beyond the one indexed lookup replacing one constant
reference.

## 3. Domain Model

No new domain entity. `THEME_TABLE` is data, not state — the same category as `STYLE_TABLE`,
`SONG_TABLE`, `MOTIF_TABLE`: a ROM-resident lookup keyed by an existing index, contributing no new
field to `GDS-04`'s engine-state model. The only "state" involved (`CHMIX_IDX`) already exists and
is already read by the visualizer's existing per-frame palette-write step.

## 4. User Stories

- As a listener, when I change the active style preset (Start button), the screen's overall color
  character changes to match — not only the audio.
- As a listener, when the engine enters a bad zone, the screen still turns to the warning-red
  palette regardless of which style theme was active — the safety signal is never suppressed by a
  style choice.
- As a listener, at the default preset, the screen looks exactly as it always has — no visual
  regression from this release in isolation.

## 5. Functional Requirements (candidates, for `04-requirements-engineering`)

1. The visualizer's non-bad-zone palette is a `CHMIX_IDX`-keyed table lookup (`THEME_TABLE`),
   applied every frame `BAD_ZONE_FLAGS` is clear — not only at the moment `CHMIX_IDX` changes.
2. `THEME_TABLE[0]` is byte-identical to the currently-shipped `CALM_PALETTE` — selecting preset 0
   introduces no visual change from the current shipped behavior (the same no-regression contract
   `STYLE_TABLE`/`SONG_TABLE`/`MOTIF_TABLE` index-0 rows already established for their own axes).
3. Whenever `BAD_ZONE_FLAGS` is non-zero, the palette is `BAD_PALETTE` unconditionally, regardless
   of `THEME_TABLE`'s current selection — the bad-zone override is absolute, not a blend.
4. At least 3 non-default `THEME_TABLE` rows produce a palette distinguishable, by content review,
   from `THEME_TABLE[0]` and from each other (mirroring `FR-1250`'s own style-distinguishability
   bar, applied to color instead of audio).

## 6. Non-functional Requirements (candidates)

1. This release adds **zero unconditional per-frame CPU cost beyond one indexed table lookup
   replacing one constant reference** — the palette-write routine already runs every frame
   (`GDS-08` §5's stateless re-render contract); this ADS changes *what it reads*, not *how often
   it runs* or *how much it does*. No `NFR-1170`-class budget concern arises, since no new
   recompute-on-write logic is introduced (contrast `IP-1120`, which did need one).
2. `THEME_TABLE`'s ROM cost is bounded: 8 entries × 8 bytes (`rgb15()` 4-color format) = 64 bytes,
   negligible against `R104` §7's measured 29349-byte free headroom (per `ADR-0002`'s own
   instrumentation method) — well under 0.3% of free space even at the full 8-row table this ADS
   specifies, before any content-authoring pass assigns rows 4-7 a real theme.

## 7. Constraints

- **No new rendering mechanism.** `R222`/`GDS-08` §4.2 both bind this release to the existing
  palette-swap-only extension strategy — no per-tile palette attributes, no `VBK` bank switching,
  no new tiles. `THEME_TABLE`'s rows are BG palette 0 replacements, exactly like the shipped
  calm/bad swap.
- **`visuals.py` stays acyclic** (`GDS-03` §1) — `THEME_TABLE` is authored directly in `visuals.py`
  as its own data, never imported from `music_engine.py`'s `STYLE_TABLE`.
- **Discrete, not continuous, for v1** — no color-cycling in this release. `R222`'s own staging
  recommendation ("the follow-up technique once a discrete-state version ships") is honored
  literally: ship discrete first, name continuous cycling as the explicit next increment, not a
  requirement of this one.

## 8. Risks

- **Combinatorial risk avoided, not encountered — by explicit scope decision.** Deferring mood
  (`RM-9002`) rather than combining it with style now avoids needing a style×mood cross-product
  taxonomy before either axis has shipped a single consumer. Flagged so a future reader
  understands this is a decision, not an oversight.
- **Content-authoring risk, not architecture risk.** `THEME_TABLE`'s actual color values are a
  `08-content-authoring` judgment call (which colors "feel like" Techno/Chiptune-Driving vs.
  Ambient/Lo-Fi vs. Holiday) — this ADS specifies the mechanism and the override rule, not the
  palette values themselves, the same division of labor `ADS-101` already established for
  `STYLE_TABLE`'s own tempo/density/scale/duty values.
- **`BL-0021` (accessibility) is untouched by this ADS** — `GDS-08` §4.3 already placed that
  finding's resolution (a shape-based secondary bad-zone signal, not a palette adjustment) outside
  this mechanism entirely; `RM-9003` rides whichever future package touches the palette next,
  per the roadmap's own framing ("ride either" RM-9001 or RM-9002), and this ADS does not change
  that placement.

## 9. Open Questions

1. **Exact `THEME_TABLE` color values for rows 1-3** — left to `08-content-authoring`/
   `09-content-review`, same convention `STYLE_TABLE`'s own untuned-by-ear values follow
   (`BL-0005`-class deferral). Not blocking: the mechanism is fully specified without them.
2. **`RM-9002`'s exact mood-modulation rule** (how `VALENCE`/`AROUSAL` combine with the now-shipped
   style theme — a second independent table, a per-theme tint offset, or something else) is
   explicitly left to a future `03`/`06` pass once `RM-9001` has shipped and this mechanism has a
   proven, tested first application. Not answered here by design (§1's scope decision).
3. **Whether `RM-9001` and `RM-9002` should be one feature/package or two** is a `05-feature-
   decomposition`/`07-implementation-planning` sizing call, not an architecture one — this ADS's
   own position is that they are two, since `RM-9002` depends on a WRAM signal (`AROUSAL`/
   `VALENCE`) this ADS's v1 mechanism doesn't yet consume, and the roadmap's own RM-9001/RM-9002
   rows are already split.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-31 | **Style (`CHMIX_IDX`/`STYLE_TABLE`) is the v1 palette-selection driver, not mood or song-form.** | `GDS-08` §6 point 4 already named style as "the natural first palette theme" (a coordinated whole-ensemble change already exists, per `GDS-04` §1.3) — this ADS adopts that placement rather than re-deriving it. Mood (`AROUSAL`/`VALENCE`) has no shipped consumer yet (`IP-1120` this session); song-form explicitly "wants both mechanisms" (`GDS-08` §6 point 3), a larger design than v1 needs. |
| 2026-07-31 | **`THEME_TABLE` lives in `visuals.py`, independent of `STYLE_TABLE`, keyed by the same `CHMIX_IDX` index.** | Preserves `GDS-03` §1's acyclic-import rule (`visuals.py` never imports `music_engine.py`); mirrors `IP-1110`'s own already-established pattern of reading an index without reading the other module's content table. |
| 2026-07-31 | **`BAD_ZONE_FLAGS` unconditionally overrides the theme palette — no blend, no exception.** | `GDS-08` §4.3's own principle ("a state distinction should never be carried by color alone") argues for the bad-zone signal staying maximally legible; a style theme competing with the warning-red palette would weaken exactly the signal `BL-0021` already flagged as under-strength. The override is absolute, matching the existing calm/bad relationship exactly. |
| 2026-07-31 | **Discrete palette swap only — no color-cycling in v1.** | `R222` itself frames color-cycling as the follow-up technique "once a discrete-state version ships," not a v1 requirement. Shipping the simpler mechanism first, proven, is the same staging discipline `ADS-103` used for song-form (ship the state machine, defer style-drift). |
| 2026-07-31 | **Mood-modulation (`RM-9002`) is explicitly deferred to a follow-on increment reusing this same mechanism, not combined into v1.** | Combining style × mood today would require a cross-product taxonomy decision before either axis has a single shipped consumer to validate against — the same over-scoping `R222` §5 itself warns against. `RM-9001` ships style alone; `RM-9002` becomes `IP-1120`'s first real consumer once it rides its own future package. |
| 2026-07-31 | **`docs/roadmap/04-release-roadmap.md`'s R9 entry's "prerequisite not yet satisfied" note is now stale and needs correcting** (`BL-0083`) — not fixed in this pass, since the roadmap file is a read-only cross-cutting input no architecture-stage document edits directly. | Flagged for the pipeline manager's own reconciliation step, per this skill's standing practice for cross-cutting drift it notices but does not own. |
