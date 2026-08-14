# Integration Review — R7 Verification Tranche

## Scope

An explicit package list — the four packages independently `VERIFIED` this session
(`docs/pipeline/pipeline-journal.md` runs #128-#131), reviewed together because they closed out
in the same verification pass, not because all four are the same roadmap release: `IP-9030`
(VBlank budget assertion — general infrastructure, `BL-0069`), `IP-8010` (remove vestigial
patch-point dicts — refactoring, `BL-0064`), `IP-8020` (shared WRAM constants module —
refactoring, `BL-0065`), `IP-1120` (Emotional/Energy Layer — roadmap R7's actual capability,
`FEAT-1120`/`FS-112`). Named "R7 tranche" by the session that requested this review; only
`IP-1120` is itself an R7 deliverable — noted here so the scope label isn't read as a release-
bucket claim the other three don't carry.

Commit reviewed: `9d7276d` (tip at the time this review began; `755e5bb` after the pipeline
manager's own journal commit, no code delta between them).

All four confirmed `VERIFIED` on the Master Build Plan before this review began (checked directly,
not from the invoking session's own summary):
[VR-9030](../implementation/verification/VR-9030-vblank-budget-assertion.md),
[VR-8010](../implementation/verification/VR-8010-remove-vestigial-patch-point-dicts.md),
[VR-8020](../implementation/verification/VR-8020-shared-wram-constants-module.md),
[VR-1120](../implementation/verification/VR-1120-emotional-energy-layer.md).

## Gates

`python3 build_rom.py` → 32768 bytes, valid header, matches the committed `Driftune.gbc`
byte-for-byte. `python3 test_rom.py` → **154 PASS, 0 FAIL out of 154** (`T1`-`T21`).

## Dimension 1 — Interface consistency

Checked every WRAM address the four packages touch or reference against the full tree's address
map (`wram_constants.py`, `music_engine.py`, `visuals.py`, `input_map.py`, parsed
programmatically): **zero collisions**. `IP-9030`'s `VIS_ENTRY_LY` (`0xC061`) and `IP-1120`'s
`AROUSAL`/`VALENCE` (`0xC068`/`0xC069`) both land in previously-free headroom with no overlap on
each other or on `IP-1130`'s later `BLEND_*` fields (`0xC070`-`0xC076`, shipped after this
tranche). `IP-8020`'s relocation touches no address values, only which Python module declares
them — independently confirmed identical values pre/post in `VR-8020`.

Checked the acyclic-import invariant `IP-8020` exists to preserve: `wram_constants.py` imports
nothing; `music_engine.py` and `visuals.py` both import *from* `wram_constants.py`, never the
reverse — no cycle introduced across the set.

## Dimension 2 — Invariant sweep

- **ROM budget**: within the measured headroom (`VR-1130`'s own re-measurement, 4477 used/28291
  free, is the most recent and includes this tranche's additions — not re-derived here since
  nothing in this tranche changes ROM-emitted bytes materially: `IP-8010`/`IP-8020` are byte-
  identical refactors, `IP-9030` adds ~7 bytes, `IP-1120` adds ~57 bytes per its own package doc).
- **VBlank gating**: `IP-9030`'s own `VIS_ENTRY_LY` diagnostic is itself the tranche's
  contribution to this invariant's ongoing enforcement — confirmed still passing (`T19`, live
  run above).
- **WRAM/GDS-07 map integrity**: every WRAM address any of the four packages added
  (`VIS_ENTRY_LY`, `AROUSAL`, `VALENCE`) is documented in `GDS-07` §6 (checked directly, all
  three rows present and accurate).
- **One-job-per-file**: `wram_constants.py`'s single job (constant definitions, no logic) doesn't
  violate the rule. **However**: `GDS-03` §1's own module-layout table — the architecture
  document's canonical "one file, one job" inventory — still lists only the original six modules
  (`gbc_lib.py`, `music_engine.py`, `input_map.py`, `visuals.py`, `build_rom.py`, `test_rom.py`)
  and has not been updated to include `wram_constants.py`, which has existed in the tree since
  `IP-8020` shipped 2026-07-31 — over two weeks stale at review time. `Claude.md`'s own module
  overview (line 19) already lists it correctly, so this is specific to `GDS-03`, not a
  tree-wide gap. **Finding F1** (below).

## Dimension 3 — Behavioral coherence

Traced every place `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` — `IP-1120`'s own three recompute-trigger
inputs — are written anywhere in the current tree, not just within this tranche's four packages,
since `IP-1120`'s own Risks field explicitly names this as the failure mode to watch for ("a
future package adding a 7th way to write these fields without also calling `_emit_mood_update`
silently produces stale `AROUSAL`/`VALENCE`, with no test failure, since nothing currently
consumes them to notice"). Found exactly that risk materialized, by `IP-1130` (Genre Blending,
shipped and `VERIFIED` *after* `IP-1120`, entirely outside this tranche's own scope but touching
the same three fields):

- `_emit_begin_blend` (`music_engine.py:449`) writes `SCALE_IDX` directly on every Start press —
  no `mood_update` call anywhere in the routine.
- `_emit_blend_tick` (`music_engine.py:492`) writes `TEMPO_IDX`/`DENSITY_IDX` every active-blend
  frame as the interpolation lands — no `mood_update` call anywhere in the routine.
- `input_map.py`'s Start-press handler (`:64-77`) calls `_emit_begin_blend` directly, inlined
  rather than routed through `_step_on_bit`'s `extra_call` mechanism `IP-1120`'s other four
  trigger sites use — so there was no natural place for a `mood_update` call to land even if
  `IP-1130`'s own planning had thought to add one.

**Empirically confirmed, not just read from the source**: drove a fresh boot, pressed Start once
(beginning a blend toward preset 1's style), and sampled `AROUSAL`/`TEMPO_IDX`/`DENSITY_IDX`
every frame for 20 frames. `TEMPO_IDX`/`DENSITY_IDX` correctly interpolate from `(5,3)` to their
`STYLE_TABLE[1]` target `(6,6)` over the blend — but `AROUSAL` stays pinned at its pre-press value
(`4`) through all 20 frames, never once matching `TEMPO_IDX+DENSITY_IDX` after the press. A second
independent drive confirmed the same for `VALENCE`: after a Start press changes `SCALE_IDX` to
`2`, `VALENCE` reads `10` (the *pre-press* value) against an expected `VALENCE_TABLE[2]=12` —
stale immediately and permanently until some *other* trigger site (Up/Down/A/B, a song-form
transition, or Select) happens to fire.

This is not cosmetic: `FR-1410` states `AROUSAL`/`VALENCE` are "recomputed on every write to any
of `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`... within one frame" — an unconditional claim about
*every* write, and the genre-blending write path silently violates it. No functional/player-
visible consequence exists **today** (neither field has a real consumer yet — both are
groundwork for roadmap R9), which is exactly why neither `VR-1120` (which predates `IP-1130`
entirely) nor `VR-1130` (whose own scope never names `AROUSAL`/`VALENCE`, since `IP-1130`'s
package doc doesn't cite them as Requirements Covered) could have caught it — this is invisible to
any single-package verification and only visible from this review's cross-package vantage point.
**Finding F2** (below), the review's headline finding.

## Dimension 4 — Traceability coherence

Master Build Plan, `packages/INDEX.md`, and `docs/implementation/verification/INDEX.md` all agree:
all four packages `VERIFIED`, each with a linked VR, no orphan rows. RTM cells for
`FR-1390`-`1420`/`NFR-1170`/`1180` (`IP-1120`'s own requirements) trace correctly to real code and
real `T20` checks — re-confirmed directly, not merely trusted from `VR-1120`.

**`ROADMAP.md`'s stage-07 summary row (line 15) is confirmed further stale than `BL-0082`
(already `SCHEDULED`, filed 2026-07-31) recorded it**: that entry says "16/16 packages `VERIFIED`,
1 `READY` (`IP-9030`)" — the real current count, re-derived directly from the Master Build Plan,
is **21 `VERIFIED`** (the original 16, plus this tranche's 4, plus `IP-1130`). Not a new finding —
`BL-0082` already names this exact row and its exact cause (no stage owns writing `ROADMAP.md`);
this review simply re-confirms it from a fresh count and notes the drift has widened, which the
pipeline manager's existing `BL-0082`/`BL-0096`/`BL-0098` reconciliation-pass disposition already
covers.

## Dimension 5 — Documentation coherence

`Claude.md`'s architecture overview, WRAM quick-reference (via `memory.md`), and Known Good
Behavior header are all internally consistent with the tranche's shipped state — the "Known Good
Behavior" header correctly does **not** claim R7/the refactors as part of the GO-confirmed shipped
baseline (that's a distinct, `11-release-readiness`-owned claim from "`VERIFIED`", and R7 hasn't
had its own GO call yet) — no false claim found there. `GDS-03` §1's module table is the one
document out of step with the actual tree (Finding F1, Dimension 2 above — filed once, not
duplicated here).

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| **F1** — `GDS-03` §1's module-layout table omits `wram_constants.py` | `IP-8020`, `docs/architecture/03-architecture.md` §1 | The architecture document's canonical "one file, one job" module inventory still lists only the original six repo-root modules; `wram_constants.py` has existed in the tree since `IP-8020` shipped (2026-07-31) and is correctly listed in `Claude.md`'s own module overview, but never made it into `GDS-03`'s own table. No functional impact — purely a documentation-coherence gap, same pattern as prior findings like `BL-0018`. | Low-Medium | `03-architecture-design-synthesis` — add a one-line row for `wram_constants.py` (dependency-free, shared constants) the next time `GDS-03` is touched |
| **F2** — `AROUSAL`/`VALENCE` go silently stale on every genre-blend-triggered write to `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`, violating `FR-1410` | `IP-1120` (`mood_update`'s 6-site enumeration), `IP-1130` (`_emit_begin_blend`/`_emit_blend_tick`, shipped after `IP-1120`, outside this tranche) | `IP-1130`'s Start-press blend path writes all three of `mood_update`'s trigger inputs (`SCALE_IDX` immediately, `TEMPO_IDX`/`DENSITY_IDX` gradually over the blend) without ever calling `mood_update` — the exact "7th write path" risk `IP-1120`'s own Risks field named. Empirically confirmed: after a Start press, `AROUSAL` stays pinned at its pre-press value through the entire blend (never matching `TEMPO_IDX+DENSITY_IDX`); `VALENCE` goes stale the instant `SCALE_IDX` changes and stays stale until an unrelated trigger site fires. No player-visible consequence today (neither field has a real consumer yet, both are R9 groundwork), which is exactly why no single-package verification caught it — `VR-1120` predates `IP-1130`, and `IP-1130`'s own Requirements Covered never names `AROUSAL`/`VALENCE`, so `VR-1130`'s scope never looked. | **Medium-High** (a stated, baselined requirement — `FR-1410`'s "recomputed on every write" — is violated by a shipped, `VERIFIED` interaction the pipeline's own per-package process structurally could not see; no current player-visible harm, but it will silently corrupt roadmap R9's first real consumer of this data the moment R9 lands, unless caught first) | `07-implementation-planning` — author a small remediation package adding a `mood_update` call to `_emit_begin_blend` (covers the immediate `SCALE_IDX` case) and to `_emit_blend_tick`'s active-blend path (covers the gradual `TEMPO_IDX`/`DENSITY_IDX` case) — both straightforward, low-risk additions to already-`VERIFIED` code, needing its own `07`→`08`→`09` loop and G3 before it may build |

## Verdict

**Not clean — one Medium-High finding (F2), recommend it be remediated and re-verified before
this tranche's packages are counted toward any release-bucket GO.** Since none of the four
packages in this tranche is itself the bucket that needs a GO call soon (R7 has no completion
criteria beyond "read-layer `VERIFIED`", already met, and the roadmap's own R7 entry explicitly
says it should ship bundled with R6 or R9 rather than standalone) this finding does not block an
imminent release decision, but it should not be left open indefinitely either, since R9 — the
feature that will finally consume `AROUSAL`/`VALENCE` — is the next thing this exact defect would
silently corrupt. F1 is a low-stakes doc fix, not a gate on anything.

## Quality gate self-check

- [x] Every package in scope confirmed `VERIFIED` before the review began (checked directly
      against the Master Build Plan).
- [x] All five dimensions actually exercised — each states what was checked.
- [x] ROM rebuild + full suite run against the reviewed commit, results recorded (154/154).
- [x] Every finding has a severity and a concrete recommended owner; none fixed in-pass.
- [x] Nothing but this report was written by this review.
