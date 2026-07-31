# IP-9030 — VBlank Budget Assertion (re-scoped)

> **Re-scoped 2026-07-31 (v2).** This package was originally *VRAM Write-Integrity Detection*.
> Stage 08 built its diagnostic, took its measurement, and the measurement **falsified the finding
> the package existed to detect** — see the [Blocking Report](#blocking-report--2026-07-31-08-code-implementation-run-102)
> below, which is the record of why this re-scope exists and must not be removed. The original
> 14 fields are retained verbatim in the [Appendix](#appendix--superseded-original-scope-v1).
> The **filename is deliberately unchanged** so existing links (`R101` §8.5, `R102` §3c, `R308`
> §8.5, `GDS-06` §2.2a/§2.3, `R301`/`R305`, the Master Build Plan, `packages/INDEX.md`) keep
> resolving; only the title and scope changed.
>
> **What changed in one line:** from *"prove writes are dropped"* (unprovable — the harness
> accepts every VRAM write regardless of PPU mode) to *"assert the VBlank budget the writes
> depend on"* (measurable, falsifiable, and guarding the thing that is actually at risk).

| Field | Content |
|---|---|
| **Package ID** | `IP-9030` (v2) · `IP-9xx0` bug-remediation series, no owning FS · **Executor: `08-code-implementation`** · cites `BL-0069`, with `BL-0052`/`BL-0057` folded in and `BL-0040`'s doc half handled as a doc fix |
| **Objective** | **Guard the per-frame VBlank budget with a falsifiable, permanent assertion.** Measurement (`R101` §8.5) established that `HALT` wakes at `LY` 144 on every frame, that `read_joypad`+`apply_input`+`engine_tick` consume through `LY` 152-153, and that `update_visuals` therefore runs against ~1 remaining scanline — on *every* frame, idle included. Nothing in the build or the suite guards that head-room, so the next package to add per-frame work spends it silently. Three deliverables: (1) a single permanent ROM diagnostic recording `LY` at **entry** to `update_visuals`; (2) a `T19` suite asserting that value stays within VBlank (144-153) across every frame class; (3) the two folded-in test-hardening items. **This package does not fix the tight budget** and does not attempt to widen it — `R101` §8.5 is explicit that remediation (static cycle tallying, or an architecture change) should follow only once a regression guard exists, and this is that guard. |
| **Requirements Covered** | `NFR-1010` (per-frame timing budget — this package supplies the falsifiable check its stress-run method structurally cannot provide, per the caveat added 2026-07-26 and widened by `GDS-06` §2.2a), `NFR-1020` (every shipped behavior has a headless test asserting on real state), `FR-1350`-`FR-1380` (the settings-indicator behaviors whose test coverage `BL-0052`/`BL-0057` widen). No new requirement is created. |
| **Architecture Components** | [`GDS-06` §2.1](../../architecture/06-non-functional-requirements.md) (the corrected "sound in mechanism, marginal in budget" standing this package guards), **§2.2a** (the re-derived finding), **§2.3** (what the harness structurally cannot verify — the boundary this package's scope respects), **§6 OQ1** (the "cheap runtime guard first, static cycle table only at remediation time" sequencing this package implements); [`R101` §8.5](../../research/encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md) (the measurement and the same recommendation from the cycle-cost topic's own owner); [`R102` §3c](../../research/encyclopedia/R102-ppu-modes-and-vram-oam-access-timing.md) (why the margin matters on hardware, and why it is untestable here); [`R110` §3](../../research/encyclopedia/R110-interrupts-and-timing.md) (the measured wake latency); [`R301` §5](../../research/encyclopedia/R301-pyboy-headless-api.md) / [`R305` §5](../../research/encyclopedia/R305-emulator-test-design.md) (the do/don't rules and the can/cannot-establish table this package is written against); [`GDS-09` §5](../../architecture/09-interface-specification.md) (the per-frame call-order contract being measured); [`GDS-08` §3](../../architecture/08-presentation-architecture.md) (stateless re-render). |
| **Interfaces** | Extends `build_visuals_update_asm` (`visuals.py`) with one diagnostic store at its **head** — same routine and call site `IP-0006`/`IP-1110` already own, no new dispatch, no change to the per-frame call order. Adds one WRAM byte, read by `test_rom.py` exactly as it already reads every other engine-state address. No change to `music_engine.py`, `input_map.py`, `gbc_lib.py`, or `build_rom.py`. |
| **Files to Create/Modify** | **`visuals.py`** — (1) add WRAM constant `VIS_ENTRY_LY` at `0xC061`; (2) emit the `LY`→`VIS_ENTRY_LY` store as the **first** thing `build_visuals_update_asm` does, before the `NR52` read. **`test_rom.py`** — add the `T19` suite; extend `T17.6` (currently one phase-transition boundary, `test_rom.py:911`) and `T18.8`-`T18.10` (currently one pre-Select sequence, `test_rom.py:988-1002`); correct `T18.10`'s check name. **`Claude.md`** — the drop-finding paragraph was **already corrected 2026-07-31 during the documentation review**; this package only adds `VIS_ENTRY_LY` to the data-layout notes and a Known Good Behavior entry. **`docs/implementation/packages/IP-1080-genre-aware-style-presets.md`** — doc-only, `BL-0040`'s remaining half. ~~`IP-1110`'s package doc~~ — **already corrected 2026-07-31 during the documentation review**; not this package's to touch. *(Address verified: `0xC061` is referenced nowhere in the tree — `GDS-07` §6 records fields spanning `0xC000`-`0xC050` with `VBLANK_FLAG` at `0xC060` and the block free above it. `memory.md` was checked and carries no drop-finding text, so it is **not** in this list.)* |
| **Implementation Tasks** | (1) Re-confirm `0xC061` unclaimed by grep, then add `VIS_ENTRY_LY` to `visuals.py` alongside its existing plain-int WRAM declarations — one more constant on the duplication debt `BL-0065` already tracks; deliberate, do not fix `BL-0065` here. (2) Emit `LDH A,(LY)` / `LD (VIS_ENTRY_LY),A` as the **first two instructions** of `build_visuals_update_asm`. Entry, not tail — see Risks for why the tail probe is not being rebuilt. (3) Add the `T19` suite per Tests to Add, recording the **currently measured** values in comments so a future reader can distinguish a regression from a deliberate re-baseline. (4) Extend `T17.6` to loop over all three phase-transition boundaries rather than only the first (`BL-0052`), reusing its existing empirically-derived-frame method. (5) Extend `T18.8`-`T18.10` to iterate at least two distinct pre-Select button sequences (`BL-0057`) — `VR-1110` demonstrated three; reuse its sequences. (6) **Correct the falsified wording in the two places that still state the drop finding as fact** — `T18.10`'s check name and the long comment block in `visuals.py`. (`Claude.md` and `IP-1110`'s package doc were corrected during the 2026-07-31 documentation review and are no longer this package's responsibility — verify they read correctly, do not re-edit.) The long comment block in `visuals.py`'s `build_visuals_update_asm` (lines ~163-177) states the drop finding as an established property and must be rewritten to the corrected account. (7) **Doc-only** (`BL-0040`): reword `IP-1080`'s Definition of Done from the absolute bad-zone-independence claim to the mechanism-level claim, exactly as `FS-108`'s acceptance criterion (4) was reworded in run #99. (8) Record the measured `VIS_ENTRY_LY` values per frame class in the Implementation Summary. |
| **Tests to Add** | New `test_rom.py` suite **`T19` — VBlank budget**. Every check reads `VIS_ENTRY_LY` and asserts `144 <= LY <= 153`, driving: (a) **idle** — no input, several frames, asserting on each rather than once (the budget is spent on idle frames too, so this is the baseline case, not a trivial one); (b) **plain index step** — D-pad Up and B; (c) **Start** — style application; (d) **Select** — full `init_engine` reset; (e) **song-form phase transition** — an empirically-derived transition frame, reusing `T17`'s existing frame-derivation method. (f) **Head-room reporting**: at least one check should report the observed value in its `detail` string, not merely pass/fail, so the margin is visible in test output and a *narrowing* margin is noticeable before it becomes a failure. (g) Full regression — `T1`-`T18` still green, with `T17.6`/`T18.8`-`T18.10` at their widened coverage. **Explicitly out of scope** (`R301` §5, `R305` §5): any check asserting that a VRAM write was or was not accepted by the PPU. That property is unobservable in this harness and a check claiming it would be unfalsifiable. |
| **Documentation Updates** | `Claude.md` — test count (→ ~135 across `T1`-`T19`); **correct the settings-row paragraph**, which currently states the Select-frame drop as established fact, to the corrected account (a uniform harness-sampling artifact, plus the real finding: the budget is ~exhausted on every frame); add `VIS_ENTRY_LY` to the data-layout notes and a Known Good Behavior entry for the budget assertion. `memory.md` — add `VIS_ENTRY_LY` to the quick-reference WRAM table (checked: it carries no drop-finding text needing correction). `GDS-07` — add the `VIS_ENTRY_LY` row; it is a real new WRAM address. `IP-1110`'s package doc — correct its disclosed-finding text. `IP-1080`'s DoD — task 7. `docs/pipeline/backlog.md` is **not** this skill's to write (the manager harvests). |
| **Definition of Done** | `VIS_ENTRY_LY` is written every frame and `T19` exists and passes, asserting 144-153 across all five frame classes. The measured values are recorded in the Implementation Summary **and** in `T19`'s own comments. `T17.6` covers all three phase-transition boundaries; `T18.8`-`T18.10` cover ≥2 pre-Select sequences. Both remaining falsified-wording locations are corrected (`T18.10`'s name and `visuals.py`'s comment block); `Claude.md` and `IP-1110`'s doc were already corrected 2026-07-31 and are only to be re-read, not re-edited. `IP-1080`'s DoD wording is corrected. Full suite passes; ROM builds to exactly 32768 bytes with a valid header. |
| **Verification Checklist** | ROM builds, exactly 32768 bytes, valid header (G5). Full `test_rom.py` suite passes including `T19` (G5). `09-package-verification` **independently re-derives the `VIS_ENTRY_LY` measurement** from a fixture of its own construction rather than trusting the Implementation Summary — the standing non-default-scenario convention (`VR-1070` through `VR-1110`). **Additionally, and specifically because of this package's history**: verification must confirm that no `T19` check can pass vacuously (deliberately perturb the ROM — e.g. add filler work before `update_visuals` in a throwaway build — and confirm `T19` actually fails), and must confirm the package's own diagnostic did not itself consume the head-room it measures (compare `VIS_ENTRY_LY` against the pre-package baseline of `LY` 152-153 at that point). Verification should also read `R305` §5's can/cannot table and confirm no check in `T19` claims a property from its lower half. |
| **Dependencies** | `IP-0006` (`VERIFIED`), `IP-1110` (`VERIFIED`) — the visualizer routine being instrumented. `IP-1100` (`VERIFIED`) — the phase-transition frame class. `IP-1080` (`VERIFIED`) — the Start/style-apply frame class. All `VERIFIED`, so this package is `READY`. |
| **Risks** | **The diagnostic adds per-frame work to a budget this package's own premise says is nearly spent.** This is the honest central risk and it replaces the v1 risk (that the diagnostic write might itself be dropped), which is moot — nothing is dropped. Two instructions (`LDH A,(n)` = 3 M-cycles, `LD (nn),A` = 4) ≈ 7 M-cycles ≈ 1.6% of one scanline. That is small but **not zero against a margin of roughly one scanline**, and it is spent on every frame. Mitigation: the probe is at routine **entry**, so it measures the state *before* its own cost is incurred, and its 7 cycles push only the *visualizer's* writes later, not the measurement. Stage 08 must record the before/after comparison. **Probing entry rather than the tail is a deliberate narrowing.** A tail probe was built in v1 and read a uniform, uninformative `LY` 153 in the clean build; entry is the falsifiable boundary because it measures what the three preceding routines actually spent. A second tail byte would double the per-frame cost to buy a number that was already shown to be flat — judged not worth it. Consequence to accept honestly: **this package does not measure how far past VBlank the visualizer's own writes extend.** That question belongs to remediation, which will want static cycle attribution anyway (`R101` §8.5). **A passing `T19` is a weaker guarantee than it looks** — it asserts the *entry* boundary, not that every write lands inside the window, and per `GDS-06` §2.3 the latter is unverifiable here. The suite must not be described as proving VBlank-safe writes. **ROM budget**: ~5 bytes of code plus 1 WRAM byte against 28528 free (`ADR-0002`'s `rom.pos` method; confirm by measurement). **`BL-0065` interaction**: one more duplicated constant in `visuals.py`; deliberate and acknowledged, not to be fixed here. **Doc-correction scope**: tasks 6-7 touch two code files and one package doc to unwind a falsified claim. This is deliberate — leaving a known-false finding in `Claude.md` while shipping the package that disproved it would be the worse outcome — but stage 08 should treat these as wording corrections only and not re-litigate the findings themselves. |
| **Rollback Considerations** | Fully additive in code: one WRAM byte, ~5 bytes at a routine head, one new test suite, two widened suites. Reverting the code is a straightforward commit revert; no existing behaviour is modified and no existing address is reused. The documentation corrections (tasks 6-7) are **independently valuable and should not be reverted with the code** — they correct a claim now known to be false regardless of whether the diagnostic ships. If the per-frame cost is ever judged not worth it, `VIS_ENTRY_LY` and `T19` are removable together, leaving the corrections in place. |

### Authorization (G3) — a judgement call, flagged for the user

**Position: the existing grant does not cleanly cover this, and I recommend re-confirming.**

`IP-9030`'s G3 was granted on the user's standing basis 2026-07-26 and is recorded on the Master
Build Plan. That grant was given for a package whose Objective was *"make the dropped-VRAM-write
behaviour detectable and quantified"* — a test-and-diagnose package addressing a finding that has
since been shown not to exist. Three things have changed materially:

1. **The premise is gone.** The user authorized work against a problem that turned out not to be
   the problem. Authorization for X is not obviously authorization for Y merely because both
   carry the same ID.
2. **The deliverable changed shape.** v1's diagnostic was framed as instrumentation to be removed
   once it had produced its number. v2 ships a **permanent per-frame ROM diagnostic** and a
   permanent suite — a small but ongoing cost in the exact budget the package documents as nearly
   exhausted. That is a different thing to consent to.
3. **The scope now includes correcting four documents**, including `Claude.md`'s Known Good
   Behavior, to unwind a published finding.

Against that: the *intent* the user expressed — close the blind spot around per-frame timing —
is better served by v2 than by v1, the cost is smaller, and none of it is irreversible. So this
is not a case where proceeding would be unsafe; it is a case where the honest thing is to say the
grant was given for something else and let the user decide. **Status: `READY`, authorization
`NEEDS RE-CONFIRMATION` — not authorized to build.** Recorded on the Master Build Plan.

---

## Blocking Report — 2026-07-31 (`08-code-implementation`, run #102)

**Status: `BLOCKED`.** Stage 08 built the package's own diagnostic, took the measurement the
package exists to produce, and the measurement **falsified the premise the package was scoped
against**. Per this skill's blocking conditions ("its cited files/signatures/labels have
materially drifted" / executing as written would require changing an upstream claim), the correct
outcome is to stop and report rather than to force-fit `T19` to a finding that does not exist.

### What was built (and has since been reverted)

`VIS_END_LY` (`0xC061`) was added to `visuals.py` and the `LY`→`VIS_END_LY` store emitted at the
tail of `build_visuals_update_asm`, exactly as Implementation Tasks 1-2 specify. ROM built to
32768 bytes. The measurement was then taken across all frame classes. Because the result
invalidates the package's scope, the code change was **reverted** — the working tree is back at
`IP-1110`'s state, full suite 122/122 green. Nothing is half-applied.

### Measurement 1 — where the frame's work actually sits (ROM-side `LY` probes)

A throwaway instrumented build stored the live `LY` register at five points per frame:

| Probe point | Observed `LY` |
|---|---|
| main-loop top, just after `HALT` wakes | **144** — every frame, every class |
| after `read_joypad`+`apply_input`+`engine_tick`, entering `update_visuals` | **152-153** |
| after the channel-activity cells | 152-153 |
| entering the settings-row block | **153** |
| after `update_visuals` returns | **0** (idle/`Up`), **1** (`Start`), **9** (`Select`) |

Per-cell, in the instrumented build: settings cells 0-2 are written at `LY` 153; **cells 3-4 are
written at `LY` ≥ 0 on *every* frame, including idle frames with no input at all.**

This is the package's real analytical deliverable, and it is a **stronger** finding than the one
it was scoped around: `HALT` wakes correctly at VBlank start (the gating is structurally sound),
but `read_joypad`+`apply_input`+`engine_tick` alone consume roughly **9 of VBlank's 10
scanlines**, leaving `update_visuals` running against an essentially exhausted window. In the
*clean* build `VIS_END_LY` reads **153 on every frame class** — just inside VBlank. Adding ~7
diagnostic stores per frame was enough to push the visualizer's writes past the boundary. The
margin is not merely thin; it is on the order of a handful of instructions.

### Measurement 2 — the drop hypothesis is false

`R308` §8, `R101` §8, `R102` §3b, `GDS-06` §2.1/§2.2 and `BL-0069`/`BL-0070`/`BL-0061` all record
that visualizer VRAM writes are **silently dropped** on Start-press, Select-press and song-form
phase-transition frames, discarded by PPU mode 3, with plain index steps (`Up`/`B`) unaffected —
the "partial drop" (cell 0 landed, cell 3 did not) having been called decisive evidence of a
write sequence cut off mid-block. **Two independent lines of evidence falsify this.**

1. **PyBoy does not model mode-3 VRAM inaccessibility at all.** `pyboy/core/mb.py` `setitem()`,
   lines 502-511 (PyBoy 2.7.0): the `0x8000 <= i < 0xA000` branch writes `lcd.VRAM0`/`VRAM1`
   unconditionally, with no LCD-mode check anywhere. **No PyBoy-based experiment can observe a
   dropped VRAM write**, so no PyBoy-based experiment ever confirmed one.

2. **Direct measurement: nothing is dropped.** An instrumented build mirrored each settings-cell
   value into WRAM at the same instant it was written to VRAM. The WRAM mirror and the VRAM byte
   are **identical on every frame of every class** — the write always lands.

The observed symptom is real but is a **harness observation-window artifact**: `pb.tick(1)`
returns at a point inside the ROM's frame work — after `apply_input` has updated the steering
index, but before `update_visuals` has re-rendered from it (a ROM-side frame counter confirms
exactly one ROM frame per `tick`, so this is not a dropped or doubled frame). Every observation
therefore shows the indicator exactly one frame behind its source. Measured across classes:

| Frame class | `TEMPO_IDX` after tick | value ROM wrote | VRAM cell | lag |
|---|---|---|---|---|
| `Up` (plain index step) | 5 | 6 (the *old* index) | 6 | **one frame** |
| `Start` (style apply) | 6 | 6 | 6 | **one frame** |
| `Select` (`init_engine` reset) | 4 (= preset) | 6 | 6 | n/a — no value change |

**The asymmetry that made the original finding look decisive does not exist.** Plain index steps
lag identically to Start/Select; the earlier "`Up`/`B` are unaffected" reading was a measurement
error. Likewise the "partial drop" is a partial *observation* — cells 0-2 complete before the
`tick` boundary and cells 3-4 after it — and it occurs on idle frames too, which no drop
hypothesis predicts.

### What this means for the package

`T19` as specified cannot be written honestly. Items (b), (c) and (d) instruct stage 08 to assert
"currently observed" dropped-write behaviour on the Start, Select and phase-transition frame
classes; that behaviour is not observable, and asserting it would encode a falsified claim into
the permanent suite. Item (e)'s `VIS_END_LY` quantification is sound and was executed, but its
result (a uniform 153) is uninformative in the clean build and only becomes informative under
instrumentation — so the constant does not earn its permanent per-frame cost as scoped.

**Required action** (owners named for the manager to route):

1. `02-research-gbc-hardware` / `02-research-tooling-and-testing` — correct `R101` §8, `R308` §8
   and `R102` §3b. The cycle-budget *reversal* those addenda made still stands and is now better
   evidenced (measurement 1); the *mechanism* they attribute it to (mode-3 discard) must be
   withdrawn, and `R301`/`R305` must record PyBoy's unconditional VRAM writes as a first-class
   harness limitation — it bounds what any headless test on this project can ever prove.
2. `03-architecture-design-synthesis` — correct `GDS-06` §2.1/§2.2. §2.1's "VBlank gating is
   solid/structural" claim is *partly* vindicated (`HALT` wakes at `LY` 144) and partly refuted
   (the window is ~exhausted before `update_visuals` starts); §2.2's judgement that `R101`'s
   revisit trigger had fired **still holds**, on the new evidence rather than the old.
3. `07-implementation-planning` — re-scope this package. A write-integrity suite asserting
   mode-3 drops is not buildable under PyBoy. What *is* buildable and valuable: a **budget**
   assertion (`LY` at entry to `update_visuals` stays within VBlank) plus the `BL-0052`/`BL-0057`
   test-hardening items, which are unaffected by any of this and remain worth doing.
4. `00-pipeline-manager` — `BL-0069`, `BL-0070` and `BL-0061` all rest on the falsified mechanism
   and need re-derivation; `IP-1110`'s disclosed "dropped writes on a Select frame" finding, and
   the `T18.10` check wording that encodes it, are also affected.

**No requirement is violated by any of this** — the display is correct on every frame from the
ROM's own point of view, and `FR-1120`/`FR-1350`-`FR-1380` hold. The real, unresolved risk is
narrower and was never tested: on **physical hardware**, which does enforce mode-3, a window this
tight is a genuine hazard — and `GDS-02` §7 already records that Driftune has never run on real
hardware (`BL-0058`).


---

## Appendix — superseded original scope (v1)

Retained verbatim for the record. **Do not implement from this table** — its premise was falsified;
see the Blocking Report above and the v2 fields at the top of this document.


| Field | Content |
|---|---|
| **Package ID** | `IP-9030` (`IP-9xx0` bug-remediation series — no owning FS; cites `BL-0069`, with `BL-0052`/`BL-0057` folded in and `BL-0040`'s remaining half handled as a doc fix) |
| **Objective** | Make the visualizer's dropped-VRAM-write behaviour **detectable and quantified**, converting a blind spot into a covered one. Two deliverables: (1) a `test_rom.py` suite that drives every known-affected frame class and asserts each visualizer cell matches its source state on that frame; (2) a minimal permanent ROM diagnostic (`VIS_END_LY`) that records how far past VBlank `update_visuals` actually finishes, so the *magnitude* of the overrun is measurable rather than merely its existence. **This package does not fix the overrun** — `R308` §8.4 and `R101` §8.4 both state detection and quantification must precede remediation, and this package produces the number that decides which remediation is appropriate. |
| **Requirements Covered** | `NFR-1010` (per-frame timing budget — this package addresses the caveat added 2026-07-26 recording that its stress-run method is insufficient alone), `NFR-1020` (every shipped behavior has a headless test asserting on real state), `FR-1120`/`FR-1350`-`FR-1380` (the visualizer behaviors whose write integrity is being asserted). No new requirement is created; this package tests claims the baseline already makes. |
| **Architecture Components** | [`R308` §8](../../research/encyclopedia/R308-performance-budgeting.md) and [`R101` §8](../../research/encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md) (the finding and its analysis); [`R102` §3/§3b](../../research/encyclopedia/R102-ppu-modes-and-vram-oam-access-timing.md) (Mode-3 ignored-write mechanism); [GDS-08 §3](../../architecture/08-presentation-architecture.md) (the stateless re-render contract that makes the symptom self-healing); [GDS-09 §5](../../architecture/09-interface-specification.md) (the per-frame call-order contract the overrun runs against); [GDS-06 §2.2](../../architecture/06-non-functional-requirements.md) |
| **Interfaces** | Extends `build_visuals_update_asm` (`visuals.py`) with a single diagnostic write at its tail — the same routine and call site `IP-0006`/`IP-1110` already own, no new dispatch. Adds one WRAM byte, read by `test_rom.py` exactly as it already reads every other engine-state address. No change to `music_engine.py`, `input_map.py`, `gbc_lib.py`, or `build_rom.py`. |
| **Files to Create/Modify** | `visuals.py` — (1) add one WRAM constant `VIS_END_LY` at `0xC061` (confirmed free: GDS-07 §6 records fields spanning `0xC000`-`0xC050` with `VBLANK_FLAG` at `0xC060` and the block otherwise unused above it; `0xC061` is the next byte and is referenced nowhere in the tree — verify by grep before writing); (2) at the very end of `build_visuals_update_asm`, immediately before its `RET`, read the `LY` register (`0xFF44`) and store it to `VIS_END_LY` — roughly 4 instructions, no branching, no dependency on any other state. **`test_rom.py`** — add the new `T19` suite (below) and extend `T17.6`/`T18.8`-`T18.10` per the folded-in items. **`docs/implementation/packages/IP-1080-genre-aware-style-presets.md`** — doc-only fix, see Implementation Task 6. |
| **Implementation Tasks** | (1) Grep the tree for `0xC061` to confirm it is unclaimed, then add the `VIS_END_LY` constant to `visuals.py` alongside its existing plain-int WRAM declarations (note: this deliberately extends the duplication `BL-0065` tracks — it is one more constant on an existing acknowledged debt, not a new pattern; do not attempt to fix `BL-0065` here, that is its own refactoring package). (2) Emit the `LY`→`VIS_END_LY` store at the tail of `build_visuals_update_asm`, after the settings-row block, so it records the state *after* all visualizer writes have been attempted. (3) Add the `T19` suite per Tests to Add. (4) Extend `T17.6` to loop over all three phase-transition boundaries rather than only the first (`BL-0052`), reusing the same empirically-derived-frame methodology it already uses. (5) Extend `T18.8`-`T18.10` to iterate over at least two distinct pre-Select button sequences rather than one (`BL-0057`) — `VR-1110` already demonstrated three work; reuse its sequences. (6) **Doc-only** (`BL-0040` remaining half): `IP-1080`'s Definition of Done states in absolute terms that "a style change does not alter `DISSONANCE_SCORE`/`BAD_ZONE_FLAGS`/`STALE_COUNT_*`/`ONSET_WINDOW_COUNT`". Reword to the mechanism-level claim exactly as `FS-108`'s acceptance criterion (4) was reworded in run #99 — the style-application path itself never touches those fields; `engine_tick` runs every frame regardless, so an unrelated channel's coincidental onset can. (7) **Record the measurement**: after building, drive each frame class and report the observed `VIS_END_LY` values in the Implementation Summary. This is the package's real analytical output — see Definition of Done. |
| **Tests to Add** | New `test_rom.py` suite **`T19` — VRAM write integrity**: (a) **normal frame** — drive plain index steps (D-pad Up, B) and assert every settings cell and every channel-activity cell matches its source state on the press frame (expected: all land, per `R308` §8.2); (b) **Start frame** — drive a Start press and assert on all nine cells on that frame (expected per current evidence: settings writes dropped — the test should assert the *currently observed* behavior and be written so that a future fix flips it to a clean pass, with the expectation clearly named as "documents current known-bad behavior", not as desired behavior); (c) **Select frame** — same, for a Select press; (d) **song-form transition frame** — same, on an empirically-derived transition frame, specifically asserting the *partial* pattern (an early cell lands, a later one does not) since that is the signature that distinguishes an overrun from a wholesale block; (e) **`VIS_END_LY` quantification** — for each of the four frame classes, read `VIS_END_LY` and assert it is within the VBlank range (`LY` 144-153) on normal frames, and record (not merely assert) its value on the heavy frames so the overrun magnitude is visible in test output; (f) full regression — `T1`-`T18` still green. |
| **Documentation Updates** | `Claude.md` (test count → 132-ish across `T1`-`T19`; a Known Good Behavior note that write integrity is now asserted, and an honest note that `T19` currently documents known-bad behavior on three frame classes), `memory.md` (visualizer quick-reference gains `VIS_END_LY` and what it means), GDS-07 (`VIS_END_LY` is a real new WRAM address — add the row), `docs/pipeline/backlog.md` is **not** this skill's to write (the manager harvests). |
| **Definition of Done** | `T19` exists and passes, asserting the write-integrity property on all four frame classes. `T17.6` covers all three phase-transition boundaries; `T18.8`-`T18.10` cover at least two pre-Select sequences. `VIS_END_LY` is written every frame and its values across the four frame classes are **recorded in the Implementation Summary** — this is the package's key analytical deliverable, since `R101` §8.3 names it as the measurement that decides whether the overrun is marginal (shave a routine) or structural (change the architecture). `IP-1080`'s DoD wording is corrected. Full suite passes; ROM builds to 32768 bytes with a valid header. |
| **Verification Checklist** | ROM builds, exactly 32768 bytes, valid header (G5). Full `test_rom.py` suite passes including `T19` (G5). `09-package-verification` independently re-derives the `VIS_END_LY` measurement rather than trusting the Implementation Summary's numbers, and independently confirms at least one frame class's drop behaviour from a fixture of its own construction — the standing non-default-scenario convention (`VR-1070`/`VR-1080`/`VR-1090`/`VR-1100`/`VR-1110`). Verification should also sanity-check that `VIS_END_LY`'s own write did not itself change which cells land (it is 4 instructions at the very tail, after every other write — but it is not free, and the package's own change could in principle shift the boundary). |
| **Dependencies** | `IP-0006` (`VERIFIED`) and `IP-1110` (`VERIFIED`) — the visualizer routines being instrumented and asserted on. `IP-1100` (`VERIFIED`) — the song-form transition frame class. `IP-1080` (`VERIFIED`) — the Start/style-apply frame class. All `VERIFIED`, so this package is `READY`. |
| **Risks** | **The diagnostic write is itself per-frame work** — 4 instructions at the tail of the very routine whose tail is already the exposed one. It cannot drop *earlier* writes (it runs last), but it could in principle be the write that gets dropped, making `VIS_END_LY` stale on exactly the frames it is meant to measure. Mitigation: the test should treat a stale `VIS_END_LY` as itself a positive finding (it would confirm the overrun reaches the very end of the routine) rather than as a broken test. Flagged explicitly so stage 08 does not mistake it for a defect. **ROM budget**: ~6 bytes of code plus 1 WRAM byte — negligible against 28528 free (`ADR-0002`'s method; confirm by measurement, not assumption). **Test-authoring risk**: `T19` asserts *currently known-bad* behavior on three frame classes. Written carelessly this creates a test that will fail when someone fixes the bug — the exact opposite of useful. It must be written so the known-bad expectations are named as such and are trivially flippable, and the Implementation Summary must say so. **`BL-0065` interaction**: this adds an eleventh-plus duplicated constant to `visuals.py`; deliberate and acknowledged, not to be fixed here. |
| **Rollback Considerations** | Fully additive: one WRAM byte, ~6 bytes of code at a routine tail, one new test suite, two extended test suites, one doc wording fix. Reverting is a straightforward commit revert; no existing behaviour is modified and no existing address is reused. The `VIS_END_LY` diagnostic is independently removable if it is ever judged not worth its per-frame cost. |
