# VR-1130 — Genre Blending

## Package

`IP-1130` — Genre Blending (roadmap R8, `FS-113`/`ADS-107`). Commit verified: `f6fd243` on
`claude/controls-explanation-28fpbh` ("IP-1130 remediation: fix VR-1130 F1 (real VBlank overrun,
not a harness artifact)"). This is a **re-verification pass**, superseding this VR's own prior
`RETURNED` result (against commit `7c9ccb2`, dated 2026-08-09, preserved below in full). Fresh
session relative to the remediating session — no independence caveat needed.

## Result

**`VERIFIED`** — every Definition of Done item, Verification Checklist item, and covered
Requirement holds under independent re-derivation; the full `test_rom.py` suite is green
(154/154) and the ROM builds correctly. **Three non-blocking findings** are logged: one Medium
(the remediation's own causal narrative for its disclosed residual timing effect is narrower than
what independent instrumentation actually shows — a real, pre-existing, engine-wide phenomenon,
not a defect this package needs to fix, but the *disclosure* is inaccurate) and two Low/Low-Medium
(a factually incorrect justification attached to the `T17.6` test-change; a stale WRAM-byte-count
figure in `NFR-1220`'s own body text). None of the three findings identify a functional defect,
a violated requirement, or a test change that masks a real bug.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `_emit_begin_blend`/`_emit_blend_tick` implement the contract exactly as `FS-113` specifies, including the mid-blend-restart edge case | `music_engine.py:416-478` (`_emit_begin_blend`), `:492-559` (`_emit_blend_tick`); independently hand-derived at `BLEND_STEP=3` for a pair `T21.3b` doesn't test (see Verification Checklist audit) | **Pass** |
| `T21` exists and passes, with (a)-(e) exercised independently, plus the new `T21.3b` | `test_rom.py:1369-1520`; all `T21.*` checks pass in the live run below | Pass |
| `T15.1`-`T15.4` / `T4.7` / `T16.8` updated and passing against the blend contract | `test_rom.py`; all pass, unchanged from the already-`VERIFIED`-adjacent prior pass's shape | Pass |
| Full suite passes (`T1`-`T21`) | `python3 test_rom.py` → `154 PASS, 0 FAIL out of 154` (this run) | Pass |
| `visuals.py` untouched | `git show --stat f6fd243` — no `visuals.py` entry | Pass |
| ROM builds to exactly 32768 bytes with a valid header | Rebuilt independently this run: 32768 bytes; logo present; title `DRIFTUNE`; CGB flag `0x80`; header checksum stored `0x72` = independently recomputed `0x72` | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Independently rebuilt and header-verified this run (see above) | Pass |
| Full `test_rom.py` suite passes including `T21`/`T21.3b` and updated `T15`/`T17.6`/`T8.7b` (G5) | `154 PASS, 0 FAIL out of 154` | Pass |
| Independently hand-derive a genuine interpolated midpoint (`BLEND_STEP` other than 0/4), for at least one non-default style pair, without importing `test_rom.py`'s own values | Standalone script (no `test_rom.py`/`music_engine.py` import of logic — only raw WRAM addresses cross-checked against `wram_constants.py`). Used **`BLEND_STEP=3`** (not `T21.3b`'s `2`) on the **preset 1→2 (Techno→Ambient) pair** (not `T21.3b`'s preset 0→1). Settled at preset 1 first (`src=(6,6,1)`, matches `STYLE_TABLE[1]`), then pressed Start toward preset 2 (`target=(1,0,-1)` from `STYLE_TABLE[2]`, duty `0xFF`→`-1` decoded independently). Hand-derived via `src + ((target-src)*step)>>2`, magnitude-negate-shift-renegate for negatives: `(3, 2, 0)`. Shipped ROM at the exact frame `BLEND_STEP` first read `3`: `(3, 2, 0)`. **Exact match.** | **Pass** |
| Independently re-confirm the mid-blend-restart forced-collision scenario using a second, independently-constructed pre-Start-press sequence | Constructed a fourth-generation independent sequence (distinct from this VR's own prior two and `T21`'s own): settled fully at preset 2 first, single-tick-hold press to preset 3, frame-by-frame poll (not a fixed hold length) for the first genuine `1≤BLEND_STEP≤3` frame, captured `(TEMPO_IDX,DENSITY_IDX,DUTY_BIAS)` at that instant, then a second press restarting toward preset 4. Result: `CHMIX_IDX` changed again (real second press), `SCALE_IDX` applied the second press's own target immediately, `BLEND_STEP` reset. **Note**: an earlier attempt at this same check, using a naive "read mid-blend value, then immediately press-and-tick" construction, produced an apparent mismatch — traced (see Findings, informational) to this independent run's own discovery of a pre-existing, non-blend-specific engine timing characteristic (below), not to a defect in `_emit_begin_blend`'s capture logic, which reads WRAM at instruction-execution time and is unaffected by any harness-side tick-boundary artifact. Re-run with a poll-based (not assumed-linear) construction, matching `T21`'s own robust methodology: **Pass**. | Pass |
| Boot/Select `BLEND_STEP` initialization (`VR-1130`'s prior F1 remediation claim 2) — independently confirmed, not merely re-run | Standalone script: `BLEND_STEP` reads `4` immediately after boot, before any input (`init_engine`'s new explicit `LD_A_n(4); LD_nn_A(BLEND_STEP)`, `music_engine.py:1339`). Cross-checked against the **pre-remediation** ROM (rebuilt from commit `7c9ccb2` in an isolated tree): `BLEND_STEP` also read `4` by frame 100 in that build too — **but only because a genuine boot-time spurious mini-blend (starting from WRAM's zero-fill default, `BLEND_STEP=0`) ran and self-corrected within the first few frames**, confirmed by tracing frames 1-10 post-boot on the old build directly (values move from a fresh `TEMPO_IDX=0`-adjacent state toward the default preset's `4` over ~4 frames, landing exactly). This directly confirms the remediation's own characterization of the pre-existing defect (a real, previously-undiagnosed boot-time spurious blend that happened to self-correct by the time any existing test's boot-settle window elapsed) rather than merely accepting the commit's prose. | Pass |
| Scrutinize the VBlank-overrun claim (`VIS_ENTRY_LY`) with own instrumentation, not the commit's own claim | Own script, `VIS_ENTRY_LY` (`0xC061`) read every frame of an 8-frame active-blend window from a fresh boot: `[152,153,153,153,152,153,153,152]` — no violation of the claimed `144-153` VBlank range, matching the disclosed fix. **However**, broader independent instrumentation (below, Findings F1) shows the underlying claim's *scope* is narrower than what the remediation's own commit message and code comments assert. | Pass (narrow claim); see Finding F1 for the scope caveat |

## Additional independent instrumentation (task-directed, beyond the checklist's literal text)

Using `pyboy.hook_register` at `blend_tick`'s own entry address (obtained by building the ROM
in-process via `gbc_lib.ROM`/`build_rom.build` and reading `rom.labels['blend_tick']` — the same
class of instruction-level tracing the remediation's own commit message claims to have used, not
guessed), instrumented how many times `blend_tick` actually executes within each `pyboy.tick()`
call:

- **During active blends** (60 randomized-interval Start presses, seed 42): 8 of 60 presses
  (~13%) showed a `BLEND_STEP` value repeated across two consecutive `tick()` reads (an apparent
  "stall"). Hook-tracing the exact same frames shows this is **not a stall in the shipped SM83
  code** — `blend_tick` is called **zero times** in the harness's `tick()` call that reads the
  repeated value, and **twice** in a later `tick()` call, i.e. two real engine frames' worth of
  `blend_tick` execution become visible within one harness `tick()` sample and zero within the
  previous one. `BLEND_STEP` itself is still incremented by exactly 1 per real call — no field
  value is ever computed incorrectly at the moment `blend_tick` actually runs.
- **Critically, this same `{0-then-2}` call-count pattern is present during pure idle running
  (zero button presses, `BLEND_STEP` pinned at `4` the whole time, no blend active at all)** —
  600 idle frames post-boot showed the identical pattern with a clean, exact **30-frame period**
  (`two`-call frames at `66, 96, 126, ..., 576`, every diff exactly `30`; matching `zero`-call
  frames at `125, 155, ..., 575`).

This directly contradicts the specific scope the remediation's own commit message and code
comments assign to the residual timing effect ("the *combined* `begin_blend`+`blend_tick` cost on
the Start-press frame itself"; "every other active-blend frame... is comfortably within budget").
The same `hook_register` methodology the remediation says it used, applied more broadly than just
the press frame, shows this is a **pre-existing, general, ~30-frame-periodic engine-wide
characteristic — present with zero blend activity, unrelated to `_emit_begin_blend`/
`_emit_blend_tick`'s own cost**, not something confined to (or caused by) the Start-press frame's
extra work. It is consistent with, and very likely the same underlying phenomenon as, this
project's own already-disclosed "near-exhausted VBlank budget" characterization (`R101` §8.5,
cited in `_emit_blend_tick`'s own docstring) and the already-accepted `T9.3` self-healing
`NR52`/visuals race — but the remediation's specific press-frame-scoped attribution was not
falsified against a broader sample before being asserted as confirmed fact, the same class of gap
this VR's own prior `RETURNED` pass required falsifying (the `BL-0069` precedent) before accepting
a "harness/timing artifact, bounded and understood" framing.

**No functional requirement is violated by this**: `FR-1480`'s exact-landing guarantee held in
every transition independently tested (including all 60 randomized presses and a separate
2500-frame randomized-input stress run — `BLEND_STEP` never observed outside `0-4`); the
interpolation formula matched the hand-derived expectation at every `BLEND_STEP` value checked,
including ones the shipped suite doesn't test (`BLEND_STEP=3`, preset 1→2). This is a
**disclosure-accuracy finding, not a correctness finding** — logged as F1 below.

## `T17.6`/`T8.7b` test-change legitimacy audit (task-directed)

**`T8.7b`** (widened `==0` → `<=1`): reasoning given — adding `BLEND_STEP`'s reset write to
`init_engine` shifts the routine's total instruction/cycle count by a few instructions, which
shifts `DIV`'s value at the exact moment of Select-reset, which changes the LFSR draw used to seed
pulse A's first post-reset onset, occasionally landing a legitimate same-frame onset. This is
directly traceable to the actual code change made (`init_engine` did gain a new
`LD_A_n(4); LD_nn_A(BLEND_STEP)` pair, `music_engine.py:1339`, which does shift subsequent cycle
timing), and is the *same* precedent already established one field over by the pre-existing
`T8.7c` (`"up to one onset per channel... can land within this exact frame"`). **Legitimate — not
a masking loosening.**

**`T17.6`** (removed the "song-form value wins the collision" assertion, replaced with an
eventual-settle assertion): the reasoning given in the commit/test comment/Master Build Plan
attributes this to a call-order change — *"no longer true now that `blend_tick`... runs after
`song_tick`"* — as if `IP-1130`'s remediation changed which routine writes last. **This specific
justification is factually incorrect.** Independently confirmed by inspecting the pre-remediation
commit directly (`git show 7c9ccb2:music_engine.py`): `engine_tick`'s call order was already
`badzone_tick → song_tick → blend_tick` — identical to the post-remediation order
(`music_engine.py:1355-1357`/equivalent in the old file) — meaning `blend_tick` already ran after
`song_tick` in the *original*, `RETURNED` `IP-1130` implementation, not something the F1
remediation introduced. Building and tracing the pre-remediation ROM directly confirms
`blend_tick` did fire and overwrite `TEMPO_IDX`/`DENSITY_IDX` on the exact collision frame back
then too (old build: `TEMPO_IDX`/`DENSITY_IDX` visibly change under `blend_tick`'s own formula on
the press frame, not left as `song_tick`'s raw write). The much more likely actual explanation —
not what the remediation's own text says — is that `T17.6`'s old assertion only ever *appeared* to
pass because F1's own defect (the pre-fix per-frame `STYLE_TABLE` re-derivation, which the
original `VR-1130` proved made `DENSITY_IDX`/`DUTY_BIAS` land a real frame late and produced wrong
first-step values) caused `blend_tick`'s own overwrite to coincidentally read back a value close
to what `song_tick` had just written, for the specific phase/preset pairing `T17.6` happens to
land on — not because `song_tick` genuinely "won" by call order. **The test change itself is
legitimate and does reflect real, correct post-fix behavior** (independently re-confirmed: after
`settle_blend()`, `TEMPO_IDX`/`DENSITY_IDX` do land on `STYLE_TABLE[1]`'s target, matching the new
assertion) — **but its stated justification is inaccurate and should be corrected** (Finding F2,
Low-Medium, not blocking, since the resulting test assertion is itself correct and not masking
anything).

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `FR-1470` | `_emit_begin_blend`, `music_engine.py:416-478` | `T21.1`/`T21.2` | Traces correctly | Pass |
| `FR-1480` (exact landing) | `_emit_blend_tick`, `:492-559` | `T21.3`, `T21.3b`, own hand-derivation at `BLEND_STEP=3`/preset 1→2 | Traces correctly | **Pass** — confirmed at multiple `BLEND_STEP` values and pairs beyond the shipped suite's own coverage |
| `FR-1490` (mid-blend restart) | `_emit_begin_blend`'s unconditional capture | `T21.4`-`T21.7`, independently re-confirmed (4th independent construction, poll-based) | Traces correctly | Pass |
| `NFR-1210` (negligible steady-state cost) | `_emit_blend_tick`'s `BLEND_STEP>=4` early-`RET` | Code-review basis, unchanged from prior pass | Traces correctly | Pass |
| `NFR-1220` (bounded WRAM) | `music_engine.py:109-124` — now **7** bytes (`0xC070`-`0xC076`), not the original 4 | `GDS-07` §6 updated correctly (91 bytes used, next free `0xC077`); RTM's own forward-traceability note (`01-functional-requirements.md:484-485`) correctly says "now 7 bytes... grew from 4" | **`NFR-1220`'s own body text (line 88) still literally reads "The 4 new blend-state WRAM bytes"** — stale relative to the RTM note one section below it and to `GDS-07` | **Pass** (bound itself still holds — ample headroom; text is stale — Finding F3, Low) |
| `NFR-1230` (WRAM-testable) | — | `T21.3b` is exactly this NFR's promise fulfilled — a genuine mid-blend WRAM assertion, independently hand-derived, now shipped | Traces correctly | Pass |
| `FR-1240` (amended) | Unchanged from prior `VERIFIED`-adjacent state | `T21.1`, `T15.*` | Traces correctly | Pass |

## Test run

- `python3 build_rom.py <path>` → `32768 bytes`. Header independently re-parsed: logo present,
  title `DRIFTUNE`, CGB flag `0x80`, checksum stored `0x72` = computed `0x72`.
- `python3 test_rom.py` → **`154 PASS, 0 FAIL out of 154`** (`T1`-`T21`, including `T21.3b` and the
  updated `T17.6`/`T8.7b`).
- ROM budget independently re-measured (trailing-zero-run method): **4477 bytes used, 28291 bytes
  free** (down from the pre-remediation `4483`/`28285` — plausible, since the delta-precompute
  redesign nets out to slightly fewer instructions overall despite 3 new WRAM constants). This
  closes the pending "ROM budget: re-measure owed to the next verification pass" note left open on
  the Master Build Plan's `IP-1130` row.
- Own 2500-frame randomized-input stress run (`start`/`select`/`up`/`down`/`left`/`right`/`a`/`b`,
  seed 7, ~1-in-5 frames pressing a random button): `BLEND_STEP` never observed outside its valid
  `0`-`4` range, no crash, no hang.

## Scope audit

`git show --stat f6fd243` confirms the diff touches `Claude.md`, `Driftune.gbc`,
`docs/architecture/07-data-model.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/01-functional-requirements.md`,
`memory.md`, `music_engine.py`, `test_results.txt`, `test_rom.py` — matching the package's
declared file set plus the expected doc/ledger surface for a remediation pass. `visuals.py`,
`input_map.py`, `gbc_lib.py`, `build_rom.py` untouched. No excursion found.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | The remediation's disclosed residual timing effect ("the combined `begin_blend`+`blend_tick` cost on the Start-press frame itself... every other active-blend frame is comfortably within budget") is scoped too narrowly. Independent `hook_register` instruction-level tracing (same methodology the remediation's own commit message claims to have used) shows the underlying `{0-then-2 calls per harness tick()}` pattern is a **general, pre-existing, ~30-frame-periodic engine-wide characteristic present even with zero blend activity** (idle running, `BLEND_STEP` pinned at 4 throughout, still shows the identical pattern with clean 30-frame periodicity) — not something caused by or confined to `_emit_begin_blend`/`_emit_blend_tick`'s own added cost on the press frame. No functional requirement is violated by this (`FR-1480`'s exact-landing guarantee and the interpolation formula both hold in every case independently tested, including `BLEND_STEP`/pair combinations the shipped suite doesn't cover), and the underlying phenomenon plausibly is (or is closely related to) this project's own already-disclosed "near-exhausted VBlank budget" (`R101` §8.5) / `T9.3` self-healing race — i.e. likely pre-existing and out of `IP-1130`'s own scope to fix. But the specific causal attribution in the shipped commit message, `music_engine.py`'s own docstrings/comments, and the Master Build Plan's `IP-1130` row is inaccurate as written, and was not falsified against a broader (non-press-frame, non-blend) sample before being asserted as a confirmed, bounded, fully-understood effect — echoing the exact "claimed-and-not-fully-falsified" pattern this VR's own prior `RETURNED` pass required correcting (the `BL-0069` precedent). | Medium | `02-research-gbc-hardware` or `00-intake` (the phenomenon is engine-wide, not `IP-1130`-scoped — worth its own investigation/backlog item rather than a re-open of this package) for the underlying ~30-frame periodicity; `07-implementation-planning`/doc-correction for narrowing the inaccurate press-frame-specific claims in `music_engine.py`'s comments and the Master Build Plan's `IP-1130` row |
| F2 | The `T17.6` test-change's own stated justification ("no longer true now that `blend_tick`... runs after `song_tick`") is factually incorrect — that call order (`badzone_tick → song_tick → blend_tick`) was already present in the original, `RETURNED` `IP-1130` implementation (`7c9ccb2`), independently confirmed by inspecting and rebuilding that exact commit. The test change's *result* is legitimate and correct (independently re-confirmed: post-settle, `TEMPO_IDX`/`DENSITY_IDX` do land on the style target) — this is not a masked bug — but the reasoning attached to it, now propagated into the test comment, the commit message, and the Master Build Plan's `IP-1130` row, misattributes the cause. The more likely actual explanation is that the pre-fix F1 defect (per-frame `STYLE_TABLE` re-derivation) made `blend_tick`'s own overwrite on the collision frame coincidentally read back close to `song_tick`'s just-written value for the specific phase/preset pairing `T17.6` happens to exercise — not that `song_tick` "won" by call order, which was never true post-`IP-1130`. | Low-Medium | `07-implementation-planning`/doc-correction — amend the `T17.6` comment, commit-message-derived Master Build Plan prose |
| F3 | `NFR-1220`'s own requirement body text (`01-functional-requirements.md:88`) still reads "The 4 new blend-state WRAM bytes" — stale since the F1 remediation added 3 more (`BLEND_DELTA_TEMPO`/`DENSITY`/`DUTY`, `0xC074`-`0xC076`), now 7 total. The RTM's own forward-traceability note three lines below (`:484-485`) already correctly says "now 7 bytes... grew from 4," so this is an internal inconsistency within the same document, not a missed update entirely. The bound itself (bounded WRAM within ample headroom) still holds regardless of the exact count. | Low | `07-implementation-planning` — one-line correction to `NFR-1220`'s body text |
| F4 | Carried forward, still unresolved: the package doc's own Risks field (`docs/implementation/packages/IP-1130-genre-blending.md:17`) still reads "`N=16` frames is a first-guess placeholder" with no note of the as-shipped `N=4` deviation — independently re-confirmed still present verbatim in the remediation commit's diff (the remediation's file-change list does not include this package doc). The Master Build Plan, `Claude.md`, and `GDS-07` all three still disclose `N=4` accurately. Originally logged as F2 in this VR's prior (`RETURNED`) pass; the F1 remediation did not touch this file. | Low-Medium | `07-implementation-planning` |

## Ledger updates

- Master Build Plan `IP-1130` row: **`VERIFIED`**, this VR linked, ROM-budget re-measurement note
  closed out (4477 used/28291 free, independently confirmed).
- `docs/implementation/packages/INDEX.md` `IP-1130` row: updated to `VERIFIED`.
- `docs/implementation/verification/INDEX.md`: this row updated (✅ `VERIFIED`, superseding the
  prior ❌ `RETURNED` entry).
- RTM: no cell corrected beyond what F3 already names (`NFR-1220`'s body text) — deferred to
  `07-implementation-planning` per this skill's own no-editing-specs-or-requirements rule.
- No code, package, spec, or requirement text was edited by this run.

---

## Appendix — prior pass (superseded)

The following is this VR's own prior content, preserved verbatim for history. Its `RETURNED`
result and Critical finding (F1, "blend_tick's per-step interpolated values do not match the
package's own documented formula for 2 of the 3 blended fields") were resolved by the remediation
commit `f6fd243`, independently re-verified above.

### Package (prior pass)

`IP-1130` — Genre Blending (roadmap R8, `FS-113`/`ADS-107`). Commit verified: `7c9ccb2` on
`claude/controls-explanation-28fpbh` ("IP-1130 (Genre Blending) COMPLETE — T21 suite, T15/T4.7/
T16.8 blend-contract updates"). Fresh session relative to the implementing session — no
independence caveat needed.

### Result (prior pass)

**`RETURNED`** — 1 hard-fail finding (Critical) against the package's own Verification Checklist,
plus 1 documentation-consistency finding (Low-Medium). The full `test_rom.py` suite was green
(153/153) and the ROM built correctly, but green-suite status did not establish correctness there:
every shipped check read blend state only at the two endpoints — never a genuine mid-blend
`BLEND_STEP`. Hand-deriving a genuine midpoint surfaced a real, reproducible mismatch between the
documented interpolation formula and the actual shipped WRAM state for 2 of the blend's 3 fields.

### Findings (prior pass)

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 (prior) | `_emit_blend_tick`'s per-step interpolated values did not match the documented formula for `DENSITY_IDX` (wrong on the first frame) and `DUTY_BIAS` (wrong on every intermediate frame). Root-caused and fixed by the remediation (`f6fd243`) — see this VR's current-pass audit above. | Critical (resolved) | `08-code-implementation` (resolved) |
| F2 (prior) | Package doc's Risks field still read "`N=16`" without disclosing the shipped `N=4`. **Still open** — not touched by the F1 remediation (confirmed: `docs/implementation/packages/IP-1130-genre-blending.md:17` unchanged). | Low-Medium | `07-implementation-planning` |

(Full prior-pass Definition of Done / Verification Checklist / Requirements / Test run / Scope
audit tables omitted here for length — superseded in full by the current pass above; available in
version history for this file.)
