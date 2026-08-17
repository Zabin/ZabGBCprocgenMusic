# IP-9040 — Wire `mood_update` into Genre Blending

**v2 (2026-08-17) — re-scoped after v1's Blocking Report** (see below): v1's straightforward
`CALL('mood_update')` at both sites regressed the VBlank budget on active-blend frames. v2 keeps
the same two call sites and the same files, but replaces each site's *full* `mood_update()`
call with an inline, half-sized recompute of only the one field that site's own writes actually
obligate (`_emit_begin_blend` only writes `SCALE_IDX` → only needs `VALENCE`; `_emit_blend_tick`
only writes `TEMPO_IDX`/`DENSITY_IDX` → only needs `AROUSAL`) — grounded in throwaway measurement
before re-authoring (see `01-technical-work-breakdown.md`'s own `IP-9040` v2 TWBS entry for the
full grounding). Fields below are updated to the v2 design; v1's own record is preserved in the
Blocking Report section at the bottom, unedited, per this project's own precedent of never erasing
a prior attempt's own history.

| Field | Content |
|---|---|
| **Package ID** | `IP-9040` · `IP-9xx0` bug-remediation series · **Executor: `08-code-implementation`** · cites `BL-0111` (`10-integration-review`'s R7 verification tranche review, finding F2) |
| **Objective** | `IP-1130`'s genre-blend write path (`_emit_begin_blend`/`_emit_blend_tick`, both `music_engine.py`) writes `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` — three of the exact inputs `IP-1120`'s `mood_update` routine derives `AROUSAL`/`VALENCE` from — without ever recomputing them. Result, empirically confirmed by the finding's own review: `AROUSAL`/`VALENCE` silently go stale on every Start-press-triggered blend, violating `FR-1410`'s "recomputed on every write... within one frame" contract. **v2**: recompute the one field each site actually obligates, inline, instead of calling the full `mood_update` routine at either site — `_emit_begin_blend` only writes `SCALE_IDX` (recomputes `VALENCE` only); `_emit_blend_tick` only writes `TEMPO_IDX`/`DENSITY_IDX` (recomputes `AROUSAL` only) — closing the same gap v1 targeted, at roughly half the per-site instruction cost and with no `CALL`/`RET` overhead, grounded in v1's own measured Blocking Report. |
| **Requirements Covered** | `FR-1410` (the violated contract — restores it for the genre-blending write path specifically; the 6 sites `IP-1120` itself wired remain correct and untouched). No new requirement. |
| **Architecture Components** | [`ADS-105` §2](../../architecture/ADS-105-emotional-energy-layer.md) (the original 6-trigger-site enumeration this package extends to a 7th/8th write path); [`FS-112`](../../features/fs-112-emotional-energy-layer.md) (the behavior contract `FR-1410` states); [`GDS-09` §5](../../architecture/09-interface-specification.md) (per-frame call-order — this package's recomputes must land after their triggering write, same convention as every existing `mood_update` call site); [`ADS-107`](../../architecture/ADS-107-genre-blending.md)/[`FS-113`](../../features/fs-113-genre-blending.md) (the blend mechanism this package adds recomputes into, without altering). |
| **Interfaces** | No new routine, no new WRAM, no new file. `mood_update`'s own label/body and its 6 existing `IP-1120` call sites are unchanged and untouched — **v2 does not call `mood_update` from either new site**; each site inlines the one-field half of `mood_update`'s own formula its own writes obligate, reusing registers already live at that point in the routine rather than a fresh `CALL`. |
| **Files to Create/Modify** | **`music_engine.py`** only, both sites unchanged in *location* from v1, changed in *body*: (1) `_emit_begin_blend` — immediately after the routine's existing `rom.XOR_A(); rom.LD_nn_A(BLEND_STEP)` (i.e. after every `HL`/`A`/`B`/`C`-using row-read/delta computation in the routine has already completed — v1's Blocking Report found the originally-specified earlier placement, immediately after the `SCALE_IDX` write, corrupts the duty-bias computation that follows it, since the recompute's own register use collides with the row traversal's), add the **inline `VALENCE`-only recompute**: `rom.LD_A_nn(SCALE_IDX); rom.LD_C_A(); rom.LD_B_n(0); _ld_hl_label(rom, 'valence_table'); rom.ADD_HL_BC(); rom.LD_A_HL(); rom.LD_nn_A(VALENCE)` — no `AROUSAL` write here at all (its own inputs, `TEMPO_IDX`/`DENSITY_IDX`, are not written by this routine, so `FR-1410` imposes no obligation on this frame). (2) `_emit_blend_tick` — inside the 3-field interpolation `for` loop over `_BLEND_FIELDS` (currently `music_engine.py:492-557`): stash the `tempo` field's own freshly-computed value (already in `A` right before its own `rom.LD_nn_A(dst_addr)`) into the otherwise-unused `D` register (`rom.LD_D_A()`, right after that `LD_nn_A`); once the `density` field's own iteration lands its value in `A` (right after *its* `LD_nn_A(dst_addr)`), add `D` (`rom.ADD_A_D()`) and write straight to `AROUSAL` (`rom.LD_nn_A(AROUSAL)`) — no fresh `LD_A_nn(TEMPO_IDX)`/`LD_A_nn(DENSITY_IDX)` WRAM re-reads, no `VALENCE` touch (`SCALE_IDX` is never written by this routine). Both additions still land strictly inside the active-blend branch, never on the `BLEND_STEP>=4` early-exit path, preserving `NFR-1170`. No other file touched — `input_map.py`'s Start-press handler calls `_emit_begin_blend` unchanged; `visuals.py` has no consumer of `AROUSAL`/`VALENCE` and is not touched. |
| **Implementation Tasks** | (1) Re-confirm both insertion points against the current tree before editing — line numbers may have shifted; verify by reading the routine bodies. (2) Re-run the write-site sweep (grep every write to `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` tree-wide) to confirm no third unwired site has appeared since this package was authored — if one has, stop and report. (3) Add the inline `VALENCE`-only recompute to `_emit_begin_blend`, at the routine's tail (after `BLEND_STEP<-0`), per Files to Create/Modify. (4) Restructure `_emit_blend_tick`'s `_BLEND_FIELDS` loop body to stash `tempo`'s value in `D` and write `AROUSAL` once `density`'s own value lands, per Files to Create/Modify — confirm `D` is genuinely free across the whole loop body before relying on it (re-read the loop; v1/this pass's own grounding used it without conflict, but re-verify against the tree at implementation time, not from this doc alone). (5) Rebuild; independently drive a Start-press blend live and confirm `AROUSAL`/`VALENCE` now track `TEMPO_IDX+DENSITY_IDX`/`VALENCE_TABLE[SCALE_IDX]` correctly on every frame of the blend, not just at the endpoints. (6) **Measure `VIS_ENTRY_LY` across all three frame classes named in Verification Checklist below — not just one generic "active-blend frame"** — most importantly the mid-blend-restart collision frame (`FR-1490`'s scenario), the one case v1's own grounding pass could not confirm clean within budget. If any leaves the 144-153 range, this is a real regression requiring a fresh Blocking Report (v3), not a silent absorb — the deferred-recompute redesign named in the v2 TWBS entry is the next candidate if this happens, not something to improvise inline. (7) Add `T22` per Tests to Add. (8) **Fold in the four already-`SCHEDULED` `VR-1130` doc-correction findings while this routine is open** (`BL-0106`-`0109`, unchanged from v1): (a) `BL-0108` — correct `NFR-1220`'s body text (`docs/requirements/01-functional-requirements.md:88`) from "The 4 new blend-state WRAM bytes" to "The 7 new blend-state WRAM bytes"; (b) `BL-0109` — correct `IP-1130`'s own package doc Risks field (`docs/implementation/packages/IP-1130-genre-blending.md:17`) to disclose the as-shipped `N=4` instead of the stale `N=16` placeholder; (c) `BL-0106` — narrow `_emit_begin_blend`'s own docstring (the "Disclosed timing finding" paragraph) from claiming the timing effect is specific to "the combined `begin_blend`+`blend_tick` cost on the Start-press frame itself" to the broader, independently-confirmed truth: a general, ~30-frame-periodic engine-wide characteristic present even during pure idle running — cite `VR-1130`'s own F1 finding directly; (d) `BL-0107` — **investigated in v1, found already resolved**: `test_rom.py`'s current `T17.6` comment already states the accurate account; re-confirm this is still true (no edit expected) rather than re-assuming it from this doc alone, in case the tree moved since v1's own check. |
| **Tests to Add** | New `test_rom.py` suite **`T22` — Genre blending recomputes AROUSAL/VALENCE**: (a) fresh boot, settle, record `AROUSAL`; press Start once, read `AROUSAL` on the press frame itself — assert unchanged (matches `TEMPO_IDX`/`DENSITY_IDX`'s own instant-vs-gradual semantics: they haven't moved yet); read `VALENCE` on the same frame — assert it already matches `VALENCE_TABLE[SCALE_IDX]`'s new value (`SCALE_IDX` applies immediately). (b) continue ticking through the blend (`BLEND_STEP` 1→4) and assert `AROUSAL == TEMPO_IDX+DENSITY_IDX` on **every** intermediate frame, not just the endpoint — this is the check `BL-0111` itself was found by, so it must genuinely exercise a mid-blend frame the way the review's own live drive did, not just settle-then-read. (c) once the blend settles (`BLEND_STEP==4`), assert `AROUSAL`/`VALENCE` match the fully-landed style's values exactly. (d) a second Start press mid-blend (reusing `T21`'s own mid-blend-restart construction) — assert `AROUSAL`/`VALENCE` track correctly through the restart too, not just a single uninterrupted blend — **this is the check that must pass cleanly for v2 to be Definition-of-Done-complete; v1's own attempt failed exactly here (`T22.7`)**. (e) full regression — `T1`-`T21` still green. |
| **Documentation Updates** | `docs/requirements/01-functional-requirements.md` — `NFR-1220`'s body text (task 8a). `docs/implementation/packages/IP-1130-genre-blending.md` — Risks field `N=16`→`N=4` (task 8b). `music_engine.py`'s `_emit_begin_blend` docstring — narrow the timing-effect claim (task 8c). `GDS-07` — no new address, no row needed, but the existing `AROUSAL`/`VALENCE`/`BLEND_STEP` rows' "no consumer yet"/"recomputed... at the 6 write sites" language should note the count is now **8** sites, not 6, the next time either row is touched (not itself a Definition-of-Done item for this package, named for completeness). `Claude.md` — test count (→ `T1`-`T22`), Known Good Behavior note that genre blending now correctly keeps mood state live. |
| **Definition of Done** | Both inline recomputes added at the exact points named above. `T22` exists and passes, with (a)-(e) exercised independently — **including `T22.7`'s restart-collision check, which v1 could not close**. The write-site sweep re-run and confirmed clean (no third unwired site). `VIS_ENTRY_LY` measured across all three frame classes named in the Verification Checklist and recorded — within 144-153 or a fresh Blocking Report filed, not silently absorbed. The four folded-in doc corrections (task 8a-c) landed; 8d re-confirmed already-resolved. Full suite passes (`T1`-`T22`). ROM builds to exactly 32768 bytes with a valid header. |
| **Verification Checklist** | ROM builds, exactly 32768 bytes, valid header (G5). Full `test_rom.py` suite passes including `T22` (G5). `09-package-verification` independently re-derives `AROUSAL`/`VALENCE` for at least one genuine mid-blend frame (`BLEND_STEP` neither 0 nor 4) from a fixture of its own construction, reproducing the exact live-drive method `BL-0111`'s own review used to find the defect. Verification must also independently re-drive `VIS_ENTRY_LY` measurement across all three frame classes v2's Implementation Task 6 names (plain single-blend intermediate steps, the initial press-frame collision, and **specifically the mid-blend-restart collision frame**) rather than trusting the Implementation Summary's own reported values — this last frame class is where v1 failed, and is the one this checklist item exists to guard against a v2 regression slipping through unverified. |
| **Dependencies** | `IP-1120` (`VERIFIED`) — the `mood_update` routine (its formula is reused inline; its own routine and 6 call sites are unmodified by this package). `IP-1130` (`VERIFIED`) — the two routines this package adds recomputes into. Both `VERIFIED`, so this package is `READY`. |
| **Risks** | **Timing risk, narrowed but not eliminated by v2's own design.** v1's Blocking Report + this v2 pass's own grounding measurement isolated the regression to `_emit_blend_tick`'s per-active-blend-frame cost specifically (`_emit_begin_blend`'s own site, in isolation, measured within budget); the inline half-sized recomputes bring every ordinary single-blend frame back within budget, matching `FR-1410` exactly. **The mid-blend-restart collision frame (`FR-1490`'s scenario) remained out-of-budget even with this minimized design** in this pass's own throwaway grounding experiment — plausibly the already-disclosed general ~30-frame-periodic engine-wide characteristic (`BL-0106`) landing unluckily on this specific timing, but not independently confirmed, and not something this planning pass can resolve without doing 08's own full, committed re-implementation and measurement. **Task 6 is scoped explicitly around this** — if the real build still regresses on this specific frame class, the correct response is another Blocking Report (v3) naming the deferred-recompute redesign (named in the v2 TWBS entry, not adopted here because it needs a settled/flushed sentinel that risks crossing the G3 pre-authorization's "same mechanism" condition) as the next candidate, not a workaround improvised mid-implementation. **Scope discipline**: task 8's four folded-in doc corrections must stay doc-only. **ROM budget**: net negative vs. v1 (no `CALL`/`RET` overhead at either site, `VALENCE`-only/`AROUSAL`-only bodies instead of both fields at both sites) — negligible either way against `R104`'s measured headroom. |
| **Rollback Considerations** | Fully additive at the instruction level: no field removed or renamed, no existing behavior changed for any frame that isn't an active-blend frame. Reverting is a straightforward commit revert. The four folded-in doc corrections (task 8) are independently valuable and should not be reverted alongside a code-only rollback, same convention `IP-9030`'s own Rollback Considerations established. |

### Authorization (G3) — v2 RE-VERIFIED and GRANTED, pre-authorized conformance-remediation path

**Recorded: authorization GRANTED 2026-08-17 (re-verified fresh for v2, not inherited from v1)**,
under the `00-pipeline-manager` skill's conformance-remediation pre-authorization path (user
policy set 2026-08-14, codified in `.claude/skills/00-pipeline-manager/SKILL.md`'s G3 gate-check,
commit `b41d32a`). Both bases cited per that rule: (1) original authorization — `IP-1130` (the
package this remediates) was release-plan-covered (`01-release-plan.md` §2.2, R8, v1.0 scope) and
additionally carried its own explicit G3 grant on record (commit `351c0cf`); (2) finding —
`BL-0111` (`10-integration-review`'s R7 verification tranche, finding F2), a conformance gap
against the already-baselined `FR-1410`. All four of the path's conditions re-checked against
v2's actual (changed) design, not assumed to carry over unchanged from v1: original package
release-plan covered (yes, unchanged); finding is a conformance gap against an already-baselined
FR, not new scope (yes, unchanged — v2 restores the same contract, more cheaply); fix stays inside
`IP-1130`'s own mechanism/file footprint, `music_engine.py` only, no new file/routine/WRAM (yes —
v2 is a leaner instantiation of the same mechanism, not a different one, per the v2 TWBS entry's
own reasoning); severity Medium-High, below Critical (yes, unchanged).

### v1 record (superseded by v2 above, preserved verbatim for history)

### Blocking Report — 2026-08-17

**Reason:** Implementation Task 6 (this package's own explicit contingency) requires measuring
`VIS_ENTRY_LY` on an active-blend frame with the `mood_update` calls in place, and filing a
Blocking Report rather than a workaround if the budget is exceeded. Both `CALL('mood_update')`
insertions were implemented exactly as specified (after a mid-routine clobbering bug was caught
and corrected in `_emit_begin_blend` — see below), the ROM built, and `T22`'s own new suite passed
6 of 7 checks — but `T22.7` failed on a restarted-blend scenario, and independent measurement
confirms a genuine `VIS_ENTRY_LY` regression: on an active-blend frame with this package's calls
in place, `VIS_ENTRY_LY` read `1` and `0` (outside the required 144-153 VBlank range) on a plain
single blend, and `1`/`0` again on the restarted-blend scenario `T22.7` exercises — exactly the
central risk this package's own Risks field named in advance (`mood_update` adds roughly a dozen
instructions to `_emit_blend_tick`'s already-budget-sensitive per-active-blend-frame path,
previously brought back within margin only by `VR-1130` F1's `BLEND_DELTA_*` precompute fix).

**Implementation-time correction, not itself the blocking issue (recorded for the eventual
retry):** the package doc's own Files to Create/Modify field specified the `_emit_begin_blend`
call landing "immediately after the `SCALE_IDX` write specifically," mid-routine. `mood_update`
clobbers `A`/`B`/`C`/`HL` (it is not register-preserving, same convention every one of its 6
existing call sites already relies on — each calls it only once it no longer needs its own working
registers) — but `_emit_begin_blend`'s row traversal keeps `HL` parked at each field's own row
offset between reads, and the duty-bias read/delta computation immediately following the
originally-specified insertion point still needed `HL`/`A`/`B`/`C` intact. Placing the call there
verbatim corrupted the duty-bias delta computation, breaking `T21.3`/`T21.3b`/`T21.8` (all
duty-bias-specific mismatches). Moving the call to the end of `_emit_begin_blend` (after every
`HL`/`A`/`B`/`C`-using computation completes, still before the routine returns) fixed this without
changing the frame-level semantics the original placement reasoning cared about — `SCALE_IDX` has
already landed and `TEMPO_IDX`/`DENSITY_IDX` are still untouched regardless of where within this
routine the call lands, so `AROUSAL`/`VALENCE`'s pre-press-vs-instant behavior is unaffected. This
correction is independent of the blocking issue below and should carry forward into the retry.

**Missing dependency:** none — both dependencies (`IP-1120`, `IP-1130`) are `VERIFIED` and
unaffected. The gap is a timing/budget one, not a missing artifact.

**Required action:** re-derive a cheaper way to satisfy `FR-1410` for the genre-blending write
path that doesn't add `mood_update`'s full ~dozen-instruction cost to every active-blend frame.
Candidates for the next planning pass to evaluate (not prescribed — `07`'s own judgment call):
(a) call `mood_update` only on the frame `BLEND_STEP` reaches 4 (blend settles) plus the press
frame, rather than every active-blend frame — trades exact per-frame `FR-1410` conformance during
the blend for conformance at press-time and landing-time only, a scope question for `04`/`06` to
weigh against the requirement's literal "within one frame" wording; (b) a cheaper, purpose-built
recompute inline in `_emit_blend_tick` that reuses values already in registers from the
interpolation loop instead of a full `CALL`/`RET` plus `mood_update`'s own independent WRAM
re-reads; (c) re-measure whether `_emit_begin_blend`'s own single per-press call (not
per-active-blend-frame) is within budget on its own — the failing measurement above bundles both
call sites' cost together and was not isolated per-site before this report was filed, so isolating
them is real remaining diagnostic work for whoever picks this back up.

**Recommended owner:** `07-implementation-planning`, re-scoping `IP-9040` (v2) with one of the
above approaches or an isolated per-site budget measurement first; needs its own fresh G3 pass
through the pre-authorization path once re-scoped, re-checking the "stays inside the original
package's own mechanism/file footprint" condition against whatever approach is chosen.

**Working-tree state:** all code/test/doc changes from this attempt were reverted before ending
the run — no partial implementation is committed. `IP-9040` is set `BLOCKED` on the Master Build
Plan and `packages/INDEX.md`, pointing here.

### v2 record (superseded by v3 below, preserved verbatim for history)

v2's own design (inline `VALENCE`-only recompute in `_emit_begin_blend`, inline `AROUSAL`-only
recompute in `_emit_blend_tick`) is documented above in the main field table. Its own TWBS entry
(`01-technical-work-breakdown.md`) records the grounding measurement that produced it.

### Blocking Report — v3 — 2026-08-17

**Reason:** v2's own Implementation Task 6 named the mid-blend-restart collision frame (`FR-1490`)
as the one case its planning-time grounding experiment could not confirm clean, and required
re-measuring it in the real, committed build before calling the package done. That re-measurement
was done: the v2 design (inline recomputes) was implemented exactly as specified, the ROM built,
and `T22`'s new suite passed 6 of 7 checks — but **`T22.7` failed again, on the exact same
scenario v1 also failed on**, and independent `VIS_ENTRY_LY` measurement confirms the same
regression class: on the mid-blend-restart collision frame specifically, `VIS_ENTRY_LY` read `0`
(outside the required 144-153 VBlank range) at the exact frame `BLEND_STEP` reaches 4, self-
healing to `153` one tick later — every other frame class (plain single-blend intermediate steps,
the initial press-frame collision) measured clean, exactly matching the v2 planning pass's own
grounding experiment's result. **v2's inline half-sized design did narrow the problem** (from
regressing on *every* active-blend frame of *any* blend, v1's own finding, to regressing only on
the specific frame both `_emit_begin_blend` and `_emit_blend_tick` fire fully-loaded on the same
frame, which only happens on a Start press landing mid-blend) — but did not eliminate it. Per this
package's own explicit contingency (both v1's and v2's Risks fields), this is a Blocking Report,
not a further improvised trim.

**Missing dependency:** none — both dependencies (`IP-1120`, `IP-1130`) are `VERIFIED` and
unaffected. Still a timing/budget gap, not a missing artifact.

**Required action:** the two remaining, previously-named-but-not-yet-attempted candidates are the
deferred-recompute redesign (exploiting `FR-1410`'s own explicit "no more than one frame after"
tolerance to move the collision-frame recompute onto a later, non-colliding frame) and a
requirements-tier scope conversation (whether `FR-1410`'s literal "within one frame" wording
should carry an explicit, narrow exception for this one collision-frame class, which — if
adopted — would need routing through `04-requirements-engineering`, not absorbed silently here,
since it changes what's baselined rather than restoring it, and a package resting on a changed
requirement no longer automatically qualifies for the conformance-remediation pre-authorization
path's condition 2). Both were named as candidates in v1's own Blocking Report and v2's own TWBS
entry; neither has been attempted. The deferred-recompute redesign's own known difficulty (a
settled/flushed sentinel is needed to avoid violating `NFR-1170`'s zero-idle-cost contract, and
that sentinel risks changing `BLEND_STEP`'s own existing observable contract, which several
`test_rom.py` suites already assert exact values against) should be worked out concretely — with
its own throwaway grounding measurement, same convention this pass and v2's own planning pass
both used — before a v4 implementation attempt, not discovered again mid-build.

**Recommended owner:** `07-implementation-planning`, re-scoping `IP-9040` (v3→v4) with the
deferred-recompute redesign fully worked out and grounded before authoring, or — if that redesign
turns out not to be practically achievable within `NFR-1170`'s own constraint — escalating the
"one frame after" wording question to `04-requirements-engineering`/the user as a genuine
Requirements-tier open question (at which point this remediation would need its own fresh,
explicit go-ahead rather than continuing to qualify for the pre-authorized path, since it would
no longer be restoring an unchanged baseline).

**Working-tree state:** all code/test/doc changes from this attempt were reverted before ending
the run — no partial implementation is committed. `IP-9040` remains `BLOCKED` on the Master Build
Plan and `packages/INDEX.md`, pointing here (v3).

### Addendum — deferred-recompute redesign tried (throwaway experiment, 2026-08-17), made it worse

Before escalating, the deferred-recompute redesign named above as the first candidate was
actually built and measured (uncommitted, thrown away after — same convention as every other
grounding experiment this package's history uses): one new WRAM byte (`AROUSAL_DEFERRED`,
`0xC077`), a cheap flag-check-and-flush at the top of `_emit_blend_tick` (before its `BLEND_STEP
>= 4` early exit, so the flush still fires on the frame immediately after settling), and the
interpolation loop's own AROUSAL write replaced with setting the flag instead of writing
immediately — deferring every AROUSAL recompute by exactly one `blend_tick` call, uniformly,
which is within `FR-1410`'s own explicit "no more than one frame after" tolerance.

**Result: this measured *worse*, not better.** Even the plain single-blend case — which v2's own
inline design had already brought cleanly within budget — regressed under the deferred design
(`VIS_ENTRY_LY` read `0` on an intermediate step), and the mid-blend-restart case remained
regressed too. The extra per-frame flush-check cost (cheap in isolation — one WRAM read, one
`OR_A`, one conditional branch) was still enough to tip an already-razor-thin per-frame budget
over on some frame, on top of not actually eliminating any of v2's own remaining cost (the flush,
when it does fire, still does the same read-add-write work v2's inline recompute already did —
deferring *when* it runs, not *whether* it costs anything).

**What this confirms:** the genre-blending write path's per-active-blend-frame instruction budget
is tight enough that this project's toolchain currently has **no further headroom to add ANY
per-frame cost to it at all** — not a design problem this package's own remaining candidates can
engineer around, a hard resource ceiling. `IP-9040`'s remaining options are no longer "try a
cheaper implementation" (three real attempts — v1's full call, v2's inline halved recompute, this
deferred redesign — have now converged on the same wall) but genuinely: (a) accept a documented,
narrow `FR-1410` exception for this one collision-frame class (a real Requirements-tier decision,
not something `07`/`08` should decide unilaterally — it changes what "done" means for a baselined,
shipped contract), or (b) a materially larger effort outside a conformance-remediation package's
own scope (e.g., reducing `_emit_begin_blend`'s or `_emit_blend_tick`'s own *existing*,
pre-`IP-9040` cost to free up headroom — real optimization work on `IP-1130`'s own shipped
mechanism, which is a different, larger package than this one). **Escalating to the user via
`00-pipeline-manager`'s own NEEDS-USER path rather than attempting a fourth implementation guess.**
