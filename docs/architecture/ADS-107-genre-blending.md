# ADS-107 — Genre Blending (roadmap R8)

- **Status:** ✅ Authored 2026-08-07 · **Owned by:** `03-architecture-design-synthesis`
- **Dependencies:** [`ADS-101`](ADS-101-genre-aware-style-presets.md) (`STYLE_TABLE`, the
  4-field tempo/density/scale/duty-bias row this design interpolates between, keyed by
  `CHMIX_IDX`); [`ADS-103`](ADS-103-song-form-and-style-drift-state-machine.md) (the
  `SONG_STATE_TIMER` countdown-then-overwrite idiom this design reuses, and its own §9 Open
  Question — *"should style-drift reuse this exact state machine… or a separate mechanism?"* —
  which this ADS exists to answer); [`R220`](../research/encyclopedia/R220-style-evolution-and-song-form-structure.md)
  (the "song-form and style-drift are the same mechanism at two timescales" finding); `R217`
  (UX conventions — the no-free-input-surface finding, cited by roadmap R10); [`GDS-07`](07-data-model.md)
  (WRAM headroom — next free address `0xC070` as of this ADS); [`GDS-06`](06-non-functional-requirements.md)
  §2.2a (the per-frame VBlank budget finding every new-per-frame-cost design must respect);
  `docs/roadmap/04-release-roadmap.md` R8.
- **Produces:** the future `FS-1xx` for `FEAT-1130` (roadmap R8).

## 1. Executive Design Overview

R8 lets a session drift audibly from one shipped genre style toward another over time, rather than
only hard-cutting between `STYLE_TABLE` presets on a Start press. `R220`'s own finding — *"song-form
structure and style-drift are the same mechanism at two timescales"* — was already used once, by
`ADS-103`, which shipped the fast-timescale half (4-phase song-form) and explicitly deferred the
slow-timescale half (style-drift) to a future pass, naming the open question this ADS now answers:
*does blending reuse `ADS-103`'s exact state-machine shape, or does it need its own?*

**Central decision: a new, independent timer-driven mechanism that reuses the shape, not the
state.** Blending gets its own WRAM fields (§2), for the same reason `ADS-103` kept song-form
independent of bad-zone recovery: the two concerns are orthogonal (style identity vs. song
energy-arc) and forcing them to share state would conflate them for no benefit. What *is* reused
is the pattern itself — a countdown timer that, on reaching zero, performs one coordinated,
already-proven-safe WRAM overwrite — the same idiom `ADS-101` (style apply) and `ADS-103` (phase
transition) both already ship.

**Second central decision: `SCALE_IDX` does not interpolate — it hard-switches at blend start.**
`STYLE_TABLE`'s four fields split cleanly into two categories: `tempo_idx`/`density_idx`/`duty_bias`
are ordinal quantities a fractional step can genuinely land between; `scale_idx` selects a
scale/mode by index — "3.5 steps between Dorian and Pentatonic" names nothing real. Interpolating
it would produce an out-of-range or meaningless index. It switches once, at the moment a blend
begins, exactly like the existing instant `_emit_apply_style` already does today — the one field a
blend genuinely cannot gradient keeps the one behavior that already works.

**Third: blending is autonomous, driven by the same Start press that already exists — not a new
control.** `R217` found all 6 physical controls are already assigned (cited by roadmap R10's own
framing); Start already steps `CHMIX_IDX` and applies its style. This design does not add a
hold/double-tap gesture — it changes **what Start's existing edge does**: instead of writing the
new style instantly, it captures the current tempo/density/duty-bias as a *source* and begins a
drift toward the new preset's row over a small, fixed number of frames. The player-visible action
is identical (press Start, get a new style); what changes is that the transition is now heard as a
drift instead of a snap — precisely the roadmap's own framing, *"drift from one genre reference
toward another over time, rather than only hard-cutting."*

## 2. System Architecture

Four new WRAM bytes (next free address `0xC070`, per `GDS-07` §6, re-confirmed against the tree at
authoring time — no address collision):

| Field | Size | Role |
|---|---|---|
| `BLEND_SRC_TEMPO` | 1 | `TEMPO_IDX`'s value at the instant the current blend began |
| `BLEND_SRC_DENSITY` | 1 | `DENSITY_IDX`'s value at the instant the current blend began |
| `BLEND_SRC_DUTY` | 1 | `DUTY_BIAS`'s value at the instant the current blend began |
| `BLEND_STEP` | 1 | Current blend step, `0`-`4` (0 = just begun, 4 = complete/terminal — 4 discrete steps of movement, see §6 rationale) |

No new timer byte: `BLEND_STEP` doubles as both progress index and countdown driver (see §3) — one
fewer field than `ADS-103`'s `SONG_STATE`+`SONG_STATE_TIMER` pair needed, since a blend's total
duration is short enough (target: a few seconds, tuned at content-review time) to count in whole
steps rather than needing a 16-bit frame countdown.

**Trigger — Start's existing handler gains one branch, no new call site**, mirroring exactly how
`ADS-101`'s `_emit_apply_style` was folded into the same edge `input_map.py`'s Start handling
already owns:

```
Start pressed → CHMIX_IDX steps (existing, unchanged, input_map.py:64-68)
                        │
                        ▼
        _emit_begin_blend(rom)   ← NEW, replaces the direct _emit_apply_style call
                        │
        BLEND_SRC_TEMPO/DENSITY/DUTY ← current TEMPO_IDX/DENSITY_IDX/DUTY_BIAS  (snapshot)
        SCALE_IDX ← STYLE_TABLE[CHMIX_IDX].scale_idx                            (hard switch, now)
        BLEND_STEP ← 0
```

**Per-frame tick — new `_emit_blend_tick`, called from `engine_tick`** alongside `song_tick`:

```
_emit_blend_tick (every frame):
    if BLEND_STEP >= 4: RET                      ← blend already complete, cheapest possible exit
    BLEND_STEP++
    TEMPO_IDX   ← BLEND_SRC_TEMPO   + (STYLE_TABLE[CHMIX_IDX].tempo   - BLEND_SRC_TEMPO)   * BLEND_STEP / 4
    DENSITY_IDX ← BLEND_SRC_DENSITY + (STYLE_TABLE[CHMIX_IDX].density - BLEND_SRC_DENSITY) * BLEND_STEP / 4
    DUTY_BIAS   ← BLEND_SRC_DUTY    + (STYLE_TABLE[CHMIX_IDX].duty    - BLEND_SRC_DUTY)    * BLEND_STEP / 4
```

`BLEND_STEP` walks `1→2→3→4`; at `BLEND_STEP=4` each fraction is exactly `4/4`, landing precisely
on the target with no rounding-short defect. The division by 4 is a **compile-time-known
power-of-two shift** (`>> 2`), not runtime division — SM83 has no division opcode, and this design
does not need one. The multiply-then-shift is exact at the terminal step and only approximate
(intentionally, by design) at the 3 intermediate steps, which is the point of a coarse blend.

**Steady state is free.** Once `BLEND_STEP` reaches its terminal value, every subsequent frame's
`_emit_blend_tick` call is one comparison and a `RET` — the same "cheap guard, expensive work only
at boundaries" shape `song_tick` already established and `IP-9030` already proved affordable.

## 3. Domain Model

No new domain entity beyond a **Blend**, a transient, self-terminating process: a `(source, target,
progress)` triple over the same three continuous `STYLE_TABLE` fields the domain model already
tracks. It has no independent identity once complete — `BLEND_STEP` reaching its terminal value
*is* "not blending," there is no separate flag. `SCALE_IDX` is explicitly outside the Blend's
scope (§1) — it is owned entirely by the existing instant-style-apply concept `ADS-101` defined.

## 4. User Stories

- As a listener, when I press Start to change styles, the tempo/density/timbre character now
  audibly glides toward the new style over a couple of seconds, rather than snapping instantly —
  the scale/mode itself still changes immediately, since a scale has no "partway."
- As a listener, if I press Start again while a blend is still in progress, the engine begins a
  new blend from wherever it currently is (not from the original source), toward the newly
  selected style — presses never queue or get lost.
- As a listener, nothing about existing behavior regresses if I never press Start twice quickly —
  a single style change still lands at exactly the target style's values, just over a few frames
  instead of one.

## 5. Functional Requirements (candidates, for `04-requirements-engineering`)

1. On a Start press that changes `CHMIX_IDX`, the engine begins a blend: it snapshots the current
   `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` as the blend source, and sets `SCALE_IDX` to the newly
   selected style's value immediately (unchanged from the pre-blend instant-apply contract).
2. Over the following frames, `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` step through exactly 4 discrete
   levels from their snapshotted source values to the target style's values, landing exactly on
   the target at the final step — never overshooting, never stalling short.
3. A second Start press that occurs while a blend is still in progress begins a new blend using the
   engine's *current* (possibly still-blending) values as the new source — it does not wait for
   the prior blend to finish, and does not discard the new selection.
4. **Supersedes `FR-1240`'s instant-apply guarantee for `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS`**:
   those three fields no longer land on the target value the same frame Start is pressed — they
   land on it after the blend completes. `SCALE_IDX` keeps `FR-1240`'s original same-frame
   guarantee. **This is a requirements-level change, not merely an addition — `04-requirements-
   engineering` must explicitly amend `FR-1240`, not silently add beside it**, or the baseline
   will contain two requirements describing incompatible behavior for the same trigger.

## 6. Non-functional Requirements (candidates)

1. `_emit_blend_tick`'s steady-state cost (blend complete, most frames) is one comparison and a
   return — no measurable addition to `engine_tick`'s existing per-frame cost. Its active-blend
   cost (at most 4 frames per Start press, a rare event relative to 60fps) does real arithmetic,
   costed and confirmed at implementation time against `IP-9030`'s measured VBlank margin.
2. 4 new WRAM bytes, within `GDS-07`'s ample headroom (next free address unaffected by anything
   else shipped between R7 and this pass — re-confirm at implementation time per this project's
   standing discipline, not assumed from this ADS alone).
3. **4 discrete blend levels, not continuous interpolation** — deliberately chosen (§ below) to
   keep every acceptance criterion a WRAM-value assertion (exact expected index at each of 4
   steps), while the actual audible-quality judgment ("does this sound like a coherent glide or a
   stumbling mess") is explicitly left to `09-content-review`, never claimed by automated test —
   the same testable/judgment split `ADS-101`/`ADS-103` both already established.

## 7. Constraints

- **No new physical input.** Reuses Start's existing edge; `R217`'s no-free-control finding is
  respected by construction, not worked around.
- **No SM83 division.** The interpolation is a compile-time shift-by-2, not a runtime divide.
- **`SCALE_IDX` is out of the blend entirely** — a categorical field never interpolates in this
  design; a future extension wanting a scale "in-between" state would need a fundamentally
  different mechanism (e.g. a hybrid-scale table), explicitly not proposed here.
- **Independent WRAM from `SONG_STATE`/`SONG_STATE_TIMER`** — `ADS-103`'s own precedent for
  keeping orthogonal state machines on disjoint fields is followed, not just cited.

## 8. Risks

- **The roadmap's own named risk stands and is explicitly not resolved here**: *"parameter
  interpolation producing an audibly 'in-between-and-bad' state rather than a musically coherent
  blend."* This design keeps the interpolation coarse (4 steps) and fast specifically to bound
  that risk's exposure window, but whether it actually sounds coherent is a `09-content-review`
  question this ADS cannot answer architecturally.
- **`FR-1240` amendment is a real, not cosmetic, requirements change** — any downstream artifact
  (tests, other specs) that assumed instant style-apply as a stable contract needs to be checked
  for reliance on that exact timing. A quick check this pass: `test_rom.py`'s existing style-apply
  checks (`T15`) assert same-frame landing — **those checks will need updating when `IP-1130`
  implements this**, named here so `07-implementation-planning` does not discover it mid-package.
- **Rapid repeated Start presses** (a player mashing Start) restart the blend source every press
  (FR-candidate 3) — this is a deliberate design choice (never lose or queue a press), but it
  means the *audible* result of rapid mashing is a std of small, choppy glides rather than one
  clean transition. Not a defect; named so `09-content-review` knows to check it rather than being
  surprised by it.

## 9. Open Questions

1. **Exact blend duration in frames** (how many frames between each of the 4 `BLEND_STEP`
   increments) is a first-guess/`BL-0005`-class placeholder at implementation time, tuned by
   `09-content-review` once R12.5 (the release plan's proposed content pass) runs — not decided
   here.
2. **Should blend duration itself be tunable per style-pair** (e.g. a bigger tempo/density gap
   blends over more frames than a small one) or fixed regardless of distance? This design assumes
   **fixed** for v1 (simpler, and the 4-step count already bounds worst-case audible jump size
   regardless of distance) — a genuine v1.1 refinement, not decided here.
3. **Interaction with `IP-1090`'s motif-variant selection and `IP-0007`'s bad-zone recovery during
   an active blend** — both read `TEMPO_IDX`/`DENSITY_IDX` but neither writes them from a
   different source than this design touches, so no WRAM collision is expected; confirm this
   empirically at implementation/verification time rather than assuming it from this document
   alone, the same discipline `ADS-103`'s own risk section already modeled.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-08-07 | **Blending gets its own independent WRAM state (`BLEND_SRC_*`/`BLEND_STEP`), not a shared/extended `SONG_STATE`/`SONG_STATE_TIMER`.** Resolves `ADS-103`'s own explicitly-deferred Open Question. | Style identity and song-form energy-arc are orthogonal concerns, the same relationship `ADS-103` already established between song-form and bad-zone recovery — sharing state would conflate them for no benefit, even though the *shape* of the mechanism (countdown → coordinated overwrite) is deliberately reused. |
| 2026-08-07 | **`SCALE_IDX` hard-switches at blend start; only `tempo_idx`/`density_idx`/`duty_bias` interpolate.** | `SCALE_IDX` is categorical — "partway between two scales" names nothing real, while the other three fields are genuine ordinal quantities a fractional step can land between. |
| 2026-08-07 | **Blending is autonomous-once-triggered by the existing Start press — no new control, no hold/double-tap gesture.** | `R217`'s no-free-input finding (all 6 controls already assigned, cited by roadmap R10) rules out a new gesture; reusing Start's existing edge and changing what it *does* rather than adding a new *way to trigger it* respects that constraint by construction. |
| 2026-08-07 | **4 discrete blend levels via a compile-time shift, not continuous/fine-grained interpolation.** | Keeps every acceptance criterion a WRAM-assertion (exact index at each of 4 steps) rather than a fuzzy "close enough" check, avoids any runtime division (SM83 has none), and bounds the roadmap's own named audible-quality risk to a short window — explicitly deferring the actual "does it sound good" judgment to `09-content-review`, never claiming it here. |
| 2026-08-07 | **A second Start press mid-blend restarts the blend from the engine's current (possibly still-blending) values, discarding the prior target rather than queuing it.** | Consistent with every other control in this project (edge-triggered, never queued) and avoids a class of stuck-mid-transition bugs a queue would risk. |
| 2026-08-07 | **`FR-1240` must be explicitly amended, not left standing beside a new contradicting requirement.** | The instant-apply guarantee `FR-1240` currently states for `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` is genuinely superseded by this design (only `SCALE_IDX` keeps it) — recording this as silent addition rather than amendment would leave the baseline internally contradictory, the exact defect class `03`'s own quality gate exists to prevent. |
