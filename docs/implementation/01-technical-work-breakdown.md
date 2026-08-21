# Technical Work Breakdown

- **Owned by:** `07-implementation-planning` · **Status:** ✅ Authored, 2026-07-21 (v1 — two
  remediation tranches, `IP-9010`/`IP-9020`); extended 2026-07-22 (`IP-1060`/`IP-1061`, `FS-106`)

This project's first six packages (`IP-0001`-`IP-0007`, `07-implementation-planning`'s original
Master Build Plan pass) were authored directly against approved abbreviated FS notes during the
user-authorized MVP push (`BL-0012`) rather than through a separate TWBS document — see the
Master Build Plan's own history. This document begins with the pipeline's first *remediation*
tranche: two bug-scoped `BL-xxxx` entries routed here by `10-integration-review`
(`BL-0019`) and `09-package-verification`/`VR-0007` (`BL-0017`), neither backed by a formal FS
(bug remediations use the `IP-9xx0` series per this skill's own ID convention, citing their
`BL-xxxx` directly).

## Tranche: Foundation-bucket remediation (`BL-0019`, `BL-0017`)

### `BL-0019` — Channel-mix has no consumer

**Source:** `docs/reviews/integration-review-foundation-bucket.md`, Finding row 1 (High).

**Verb inventory.** The capability GDS-03/FR-1000/FR-1010 describe is "channel-mix selection":
*generate* (produce notes/PSG writes per channel — already built, `IP-0001`-`IP-0003`), *steer*
(step `CHMIX_IDX` via Start — already built, `IP-0001`), *apply* (gate which channels' generation
and register output actually reach the PSG based on the current mix — **never built, this is the
entire gap**), *persist* (reset `CHMIX_IDX` to preset on Select/boot — already built, `IP-0001`/
`IP-0005`), *review* (confirm the mix audibly/via `NR52` — out of scope for a code package,
belongs to `09-package-verification`'s own live drive once this ships). One package, `IP-9010`,
owns the missing *apply* verb — the only one without an owner. No split needed: gating is a single
cohesive change across `_emit_channel_gen`/`_emit_noise_gen` plus one new preset table, sized for
one stage-08 pass.

**Supersession sweep.** `IP-9010` doesn't retire an existing model (there was never a working
channel-mix gate to retire) — the sweep here is instead: confirm no code anywhere *already*
partially implements a mix gate that a naive fix might duplicate or conflict with. Grepped
`CHMIX` across `music_engine.py`/`build_rom.py`/`input_map.py`/`visuals.py`: the only hits are
`CHMIX_IDX`'s definition, `PRESET_CHMIX_IDX`'s reset-write, and `input_map.py`'s Start-button
step — confirmed clean, nothing else to reconcile.

**Package:** [`IP-9010`](packages/IP-9010-channel-mix-gating.md) → `08-code-implementation`.

### `BL-0017` — `OVERLOAD_THRESHOLD` mathematically unreachable

**Source:** `docs/implementation/verification/VR-0007-autonomous-recovery-and-randomize.md`,
Findings (Medium-High), re-surfaced by the integration review.

**Verb inventory.** Narrower capability — "overload detection/recovery" already has every verb
covered end to end (*generate* onsets, *detect* via the rolling window, *apply* the reload-doubling
recovery, *persist* via reset) — the gap isn't a missing verb, it's a **miscalibrated constant**
that makes the *detect* verb's own condition unreachable. No verb inventory gap; this is a pure
tuning fix, not a design gap — one package, one constant (plus a test that proves it's now
reachable).

**Supersession sweep:** not applicable — no model is being retired or generalized, only a
threshold value changed.

**Package:** [`IP-9020`](packages/IP-9020-overload-threshold-recalibration.md) →
`08-code-implementation`.

## Sequencing

`IP-9010` and `IP-9020` touch overlapping files (`music_engine.py`'s `_emit_channel_gen`/
`_emit_noise_gen`) but **disjoint code regions** within them (`IP-9010` adds a gating check before
each channel's register-write section; `IP-9020` only changes the `OVERLOAD_THRESHOLD` constant
and, if needed, `ONSET_WINDOW_FRAMES`) — no ordering dependency between them, but building both in
the same stage-08 session risks conflating their two independent test additions. Recommend
building sequentially (`IP-9010` first, since it's the higher-severity finding and the
Foundation-bucket integration review's headline blocker), each independently verified
(`09-package-verification`) before the next starts, same discipline as the original 7-package
tranche.

## Master Build Plan (remediation tranche)

Both packages added as new rows; see [`00-master-build-plan.md`](00-master-build-plan.md).
Neither is `READY` for `08-code-implementation` yet — **both require explicit G3 user
authorization**, not yet on record (this project carries no bootstrap carve-out).

## Tranche: Sound Design Techniques (`FS-106`, `FEAT-1060`, `BL-0024`)

**Source:** `docs/features/fs-106-sound-design-techniques.md`, a full 20-field spec (no
abbreviated-notes exception this time).

**Verb inventory.** The capability is "richer per-note timbral behavior," covering four
independent research-grounded techniques (`R216`): *generate* (arpeggio cycles pitch within a
note — owned below), *modulate-pitch* (vibrato's periodic offset, portamento's glide — owned
below), *modulate-timbre* (duty-cycle variation — owned below), *persist/reset* (Select-reset
must zero the new counters — owned below, riding the existing `init_engine` pattern rather than a
separate package). No verb is left unowned.

**Supersession sweep.** Neither package retires an existing model — arpeggio/vibrato/portamento/
duty-cycle are additive modulations layered onto the existing note-onset write, not a replacement
of it. Grepped `NR11`/`NR21`/`NR13`/`NR14`/`NR23`/`NR24`/`NR33`/`NR34` across `music_engine.py` to
confirm the only existing writers are `_emit_channel_gen`'s onset write and `build_rom.py`'s
boot-time init — confirmed clean, no other call site encodes the old fixed-duty/instant-onset
pattern that would need reconciling.

**Split rationale** (per `FS-106`'s own Risks section, "build one effect at a time"): two
packages rather than one four-effect package or four single-effect packages. `IP-1060` (arpeggio
+ duty-cycle) groups the two effects that don't touch the *same* per-frame frequency-write
timing — arpeggio's sub-tick cycling and duty-cycle's per-onset lookup are independent additions.
`IP-1061` (vibrato + portamento) groups the two effects that both modulate the *held* frequency
value every frame and interact with each other's output (portamento's glide target is the value
vibrato then perturbs) — building and testing them together is more honest than pretending they're
independent, per `FS-106`'s own "order of operations" note. Four single-effect packages would
over-fragment a already-small feature; one four-effect package would combine `IP-1060`'s simpler,
independent effects with `IP-1061`'s genuinely-interacting ones, diluting the verification signal
if something breaks.

**Packages:** [`IP-1060`](packages/IP-1060-arpeggio-and-duty-cycle.md) (arpeggio + duty-cycle) →
[`IP-1061`](packages/IP-1061-vibrato-and-portamento.md) (vibrato + portamento, depends on
`IP-1060` only for sequencing hygiene — same file, not a functional dependency) →
`08-code-implementation` for both.

**Authorization basis:** the user's own request that filed `BL-0024` — "Iterating the pipeline
skill run through to implantation the concepts in R216... Iterate until they are all in a
committed and pushed ROM" — is explicit, direct authorization to build and verify this specific,
scoped feature, distinct from and not extending to the separately-gated `IP-9010`/`IP-9020`. Both
packages below are recorded **G3-authorized** on this basis.

## Technical Work Breakdown — Combinable Generation Schemes (`FS-107`, `BL-0020`)

**Verb inventory.** This feature's runtime concerns: *generate* (Scheme E's onset-timing +
pitch-selection note-selection branch) and *apply* (the register write itself — already owned by
the existing, unmodified onset-write block every scheme shares). No *render* verb (no visualizer
change — `FS-107`'s own Open Question 3 confirms this is deliberate, not an oversight, and not
this package's job to add). No *persist* verb (no save data anywhere in this project). No
*review* verb applicable at planning time (that's `09-content-review`'s eventual job once built,
per `FS-107`'s own Risks section naming the audible-contrast judgment call). Every verb this
capability actually needs has an owner in the single package below; nothing is silently deferred.

**Supersession sweep.** This feature does **not** retire or generalize an existing model — Scheme
W (the shipped LFSR walk) is untouched, additive. Grepped `_emit_channel_gen`'s note-selection
step and every call site of `CUR_DEGREE_PA`/`PB`/`WV` across `music_engine.py` to confirm no other
code assumes "exactly one note-selection strategy exists" in a way that would break once a second
branch is added (e.g. a hardcoded assumption that `cur_degree` is always LFSR-delta-derived) —
confirmed clean: `_emit_badzone_tick`/`_emit_pairwise_dissonance`/`IP-0007`'s dissonant-pull
override all read/write `CUR_DEGREE_*` generically, with no assumption about *how* the value got
there, exactly as `FS-107`'s own FR-1220 requires.

**Split rationale:** one package, not split. `FS-107`'s own Feature Review already found Scheme
E's onset-timing and pitch-selection halves too tightly coupled to usefully separate — both live
in the same note-selection branch of `_emit_channel_gen`, and neither half is independently
testable or independently useful without the other (an onset-timing change with no new pitch
behavior isn't "Scheme E," and a motif table nothing ever advances through isn't either).

**Package:** [`IP-1070`](packages/IP-1070-combinable-generation-schemes.md) (Scheme E: Euclidean
onset timing + fixed-motif pitch selection) → `08-code-implementation`.

**Authorization basis:** none yet. `BL-0020` was filed as a feature request via `00-intake` (not
accompanied by the kind of explicit "build and ship this" language `BL-0024`'s filing request
carried) — `03`/`04`/`05`/`06`'s design/requirements/planning work has proceeded on the basis that
authoring a package is not itself authorization to code it (per this skill's own standing rule,
no bootstrap carve-out). `IP-1070` is recorded **NOT authorized** below; the user's explicit
per-package go-ahead is needed before `08-code-implementation` may build it.

## Technical Work Breakdown — Genre-Aware Style Presets (`FS-108`, roadmap R5)

**Verb inventory.** This feature's runtime concerns: *apply* (writing a style row's 4 target
values into `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` on a `CHMIX_IDX` change — the one
piece of new logic) — no *generate* verb of its own (this feature invents no new note-selection
strategy; `_emit_channel_gen`/`_emit_noise_gen` are consumers of the values it writes, unmodified).
No *render* verb (no visualizer change — `FS-108`'s own Open Question 3 confirms this is
deliberate). No *persist* verb (no save data anywhere in this project). *Review* is
`09-content-review`'s eventual job (`FS-108`'s own Risks section names the audible-distinctness
and genre-fidelity judgment calls) — not this package's job to resolve, only to make reviewable.
Every verb this capability needs has an owner; nothing silently deferred.

**Supersession sweep.** This feature does **not** retire or generalize an existing model —
`TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` are written by this feature exactly the way `input_map.py`'s
D-pad/A/B handlers already write them (a plain `LD_nn_A` to the same WRAM address), so there is no
old fixed-shape assumption to break. Grepped every read site of these three addresses across
`music_engine.py`/`input_map.py` to confirm none assumes they only ever change via a D-pad/A/B
press (e.g. a stale cached copy taken once at boot) — confirmed clean: every generation routine
(`_emit_channel_gen`, `_emit_noise_gen`, the tempo/density/scale table lookups) re-reads these
WRAM addresses fresh every tick, so a style-driven write is indistinguishable, from the reading
code's own perspective, from a manual D-pad/A/B write.

**Concrete data decisions** (`FS-108` Open Questions 1/2, resolved here per this stage's own
"shape, not values — but implementation planning fixes the values" convention):

- **`CHMIX_IDX`-to-style assignment**: index 0 → Default (must equal the shipped preset exactly,
  `FR-1260` — not itself styled as a named genre); index 1 → Techno/Chiptune-Driving; index 2 →
  Ambient/Lo-Fi; index 3 → Holiday; indices 4-7 → same row as index 0 (default) until a future
  content-authoring pass assigns them a 4th+ style (`BL-0039`) — every index has a defined,
  non-arbitrary row, satisfying `FR-1230`'s "each preset maps to a row" without inventing
  unreviewed character for indices nothing has designed yet.
- **`DUTY_BIAS` combination rule**: `DUTY_BIAS` is a small signed value added to the existing
  `(cur_degree & 0x03)` duty-table index (`music_engine.py:541-542`) **before** the table lookup,
  then re-masked with `AND 0x03` (wrap, not clamp) — reusing the exact same masking idiom the
  duty-selection code already uses for its own per-note cycling, rather than introducing new
  comparison/clamp logic. Resolves `BL-0038`.

**Split rationale:** one package, not split. The `STYLE_TABLE` data table, its read-and-apply
routine, and the 3 v1 style rows are one cohesive unit with no natural split point — `FS-108`'s
own Feature Review already confirmed this (unlike `FS-106`'s two-package arpeggio/vibrato split,
nothing here is independently useful or independently testable on its own).

**Package:** [`IP-1080`](packages/IP-1080-genre-aware-style-presets.md) (parallel `STYLE_TABLE`
+ apply-on-Start routine) → `08-code-implementation`.

**Authorization basis:** none yet. R5 originates from the roadmap's own release sequence
(`docs/roadmap/04-release-roadmap.md`, authored under the user's earlier "build a comprehensive
product roadmap" directive) — the same kind of authorization basis `BL-0020`/`IP-1070` had
(a roadmap/backlog entry naming the feature, with no explicit "build and ship this" language
attached), not the `BL-0024`-style explicit build-and-ship filing. `IP-1080` is recorded **NOT
authorized** below; the user's explicit per-package go-ahead is needed before
`08-code-implementation` may build it.

---

## TWBS — `IP-9030` re-scope (2026-07-31, `BL-0069`)

**Trigger.** `IP-9030` v1 (*VRAM write-integrity detection*) was returned `BLOCKED` by
`08-code-implementation` on 2026-07-31. Unusually, it did not block on drift or a missing
dependency: stage 08 built the diagnostic the package specified, took the measurement the package
existed to produce, and **the measurement falsified the package's own premise**. This section
records the re-cut and why it is shaped as it is.

**What was retired.** The v1 objective — assert that visualizer VRAM writes are dropped on three
heavy frame classes — is not merely wrong, it is **unbuildable**. PyBoy 2.7.0 accepts every VRAM
write regardless of PPU mode (`R301` §3, `mb.py:502-511`), so a check asserting a drop cannot
fail, and a check asserting no-drop cannot fail either. `R305` §5's can/cannot-establish table now
codifies the boundary. v1's `T19` items (b), (c) and (d) all sat on the wrong side of it.

**Supersession sweep.** Required whenever a package retires an existing model — here, the model
being retired is a *claim* rather than a code pattern, so the sweep was for every place the
falsified finding is stated as fact. Found, and each assigned an owner:

| Location | Disposition |
|---|---|
| `R308` §8, `R101` §8, `R102` §3b | corrected by the `02-research-*` owners, 2026-07-31 — **done** |
| `GDS-06` §2.1/§2.2, `GDS-02` §7 | corrected by `03`, 2026-07-31 — **done** |
| `visuals.py` `build_visuals_update_asm` comment block (~lines 163-177) | **folded into `IP-9030` v2**, task 6 |
| `Claude.md` settings-row paragraph + Known Good Behavior | **folded into `IP-9030` v2**, task 6 |
| `test_rom.py` `T18.10` check name | **folded into `IP-9030` v2**, task 6 |
| `IP-1110` package doc's disclosed-finding text | **folded into `IP-9030` v2**, task 6 |
| `memory.md` | **checked — clean**, carries no drop-finding text. Recorded as a positive result, not silence. |
| `BL-0069`/`BL-0070`/`BL-0061` | `00-pipeline-manager`'s to re-derive — **not this skill's** |

**Split decision: fold the doc corrections in, do not cut a separate doc-fix package.** Arguments
both ways were real. *For splitting:* the corrections are pure documentation and touch four files
this package otherwise has no reason to open, which is the usual signal for a separate cut.
*For folding, which won:* the corrections and the code change are the **same finding** — v2 exists
because the claim was false, and shipping the package that disproved a claim while leaving that
claim standing in `Claude.md`'s Known Good Behavior would be incoherent. A separate package would
also have to re-derive the entire evidentiary context to be reviewable, duplicating the Blocking
Report. The corrections are wording-only and mechanically small; the risk folding creates is that
stage 08 re-litigates the findings rather than transcribing the corrected account, which the
package's Risks field names explicitly as a thing not to do.

**No-split decision: `BL-0052`/`BL-0057` stay folded in, as in v1.** Both are `test_rom.py`
coverage-widening items (`T17.6` across all three phase-transition boundaries; `T18.8`-`T18.10`
across ≥2 pre-Select sequences), both entirely unaffected by the falsification, and both land in
the same file and the same stage-08 run as `T19`. Cutting them out now would be churn.
`BL-0040`'s doc half likewise stays.

**Verb inventory.** The capability is *review* only — assert a property of existing behaviour. No
*generate*, no *apply*, no *persist*. **Deliberate deferral recorded:** the *fix* verb (widening
the per-frame budget — static cycle tallying per `R101` §8.5, or moving visualizer writes to a
dedicated VBlank ISR per `GDS-06` §6 OQ1) is **explicitly not owned by any package yet**, and
that is intentional: both `R101` §8.5 and `GDS-06` §6 OQ1 hold that a regression guard should
exist before remediation is attempted, and this package is that guard. When remediation is
scheduled it needs its own package and its own G3.

**Right-sizing.** One focused stage-08 run: two instructions of ROM, one WRAM byte, one new test
suite, two widened suites, four wording corrections. Coherent against a single Definition of Done.

**Authorization.** Recorded as **`NEEDS RE-CONFIRMATION`**, superseding the 2026-07-26 standing-
basis grant. Reasoning in the package's own *Authorization (G3)* section and mirrored on the
Master Build Plan; in short, the grant was given for a materially different package and v2 ships a
permanent per-frame cost the original did not. This skill takes the position that the user's
underlying intent favours v2, and that the decision is nonetheless theirs.

---

## TWBS — `IP-8010`/`IP-8020` (2026-07-31, `BL-0064`/`BL-0065`)

Both `refactor`-type backlog entries from `GDS-09` (run #96), both `SCHEDULED`, neither previously
planned. Planned together in one pass since they surfaced from the same review, but cut as **two
separate packages**, not combined, despite the backlog's own "natural companion" framing.

**Split decision.** The backlog suggested combining these since both are `visuals.py`/interface-
hygiene items. Examined concretely: `BL-0064`'s scope is `music_engine.py` + `input_map.py` (two
dead local variables and a docstring, `build_rom.py` untouched); `BL-0065`'s scope is `visuals.py`
+ `music_engine.py` + a new shared module. The file overlap is real but partial (`music_engine.py`
only), and — decisively — **each needs its own equivalence contract for a different reason**:
`IP-8010`'s is trivial (two Python-level local variables never reaching `rom.data`); `IP-8020`'s
is a genuine claim about Python-level-only relocation having zero ROM consequence, which is a
different kind of assertion needing its own verification story. A single package with one
Definition of Done covering two independently-justified equivalence claims would make it harder
for `09-package-verification` to tell which claim failed if the hash ever *didn't* match. Splitting
costs nothing here — both are small enough that combining would save no real overhead — and keeps
each package's proof legible on its own. **No-split** would have been the wrong economy.

**`BL-0064` → `IP-8010` (code-only, doc corrections routed elsewhere).** The backlog entry itself
flagged three documents describing the vestigial patch-point contract as live: `GDS-03`'s
"patch-point contract" language, `GDS-09`'s ladder-table row, and six `FS-1xx` *Interfaces Used*
fields. Checked each: **`GDS-09` §3 already documents this accurately as a finding** (authored
against the real discovery, not stale) and its own Merge decision already records the `GDS-03`
correction as "this skill's [`03`'s] own to amend on a future pass" — not a doc-scoped refactoring
task, since `08-refactoring`'s write scope is structure/meaning-preservation, not design-content
correction, and `GDS-03`'s patch-point language is a content claim only its own owner should
revise. **The six `FS-1xx` fields were checked and are already clean** — a grep for "patch-point"
across `docs/features/fs-*.md` returns nothing, confirming `BL-0066`'s earlier corrective pass
already closed that half. So `IP-8010`'s scope is genuinely code-only: delete two dead `patches =
{}`/`return patches` pairs and their `-> dict` annotations, nothing else.

**`BL-0065` → `IP-8020` (code restructuring, byte-identical-ROM contract).** Scoped to exactly the
11 constants the backlog entry names (5 index addresses, 5 `PRESET_*` values, `BAD_ZONE_FLAGS`) —
**not** `LY` or `VIS_ENTRY_LY`, which `IP-9030` added to `visuals.py` this session. Checked both
against the `BL-0065` pattern and found neither fits: `LY` is a hardware-register constant with no
`music_engine.py` counterpart (the same un-remediated pattern as `NR52`/`LCDC` in the same file —
fixing one hardware register while leaving the others would be incoherent), and `VIS_ENTRY_LY` is
`visuals.py`'s own address, not a duplicate of anything `music_engine.py` owns. Recorded explicitly
in the package so a future reader doesn't wonder why two more recent, on-their-face-similar
constants were left out.

**Verb inventory.** Both are pure `refactor` capabilities (restructure existing code) — no
generate/render/apply/persist/review verb applies; not a multi-verb capability requiring the
inventory check.

**Supersession sweep.** Run for both: (1) confirmed no file besides `music_engine.py`/`input_map.py`
constructs or reads a `patches` dict (`build_rom.py`'s two call sites already discard the return
value — verified by reading the call sites, not assumed); (2) confirmed `input_map.py` already
imports the 5 index constants directly from `music_engine.py` (no duplication there to fix) and
should switch to the new shared module if `IP-8020`'s task 1 relocates canonical ownership;
(3) confirmed `test_rom.py`'s independent declaration of every WRAM address it reads (including
`VIS_ENTRY_LY`) is a separate, much larger, pre-existing test-harness convention, not an instance
of either `BL-0064`/`BL-0065` pattern — out of scope for both packages, named so it isn't mistaken
for an oversight.

**Authorization — the judgement call the manager's own rule requires be made explicitly, not
dodged.** This project's standing rule states refactoring packages are **never pre-authorized**,
with no bootstrap carve-out, "regardless" of other authorization context. The user's session-wide
grant this turn ("assuming pre authorization for everything this session") is broad, but the
standing rule's own wording ("never," "no bootstrap carve-out... regardless") reads as a
categorical exception carved out specifically *because* structural change is judged to warrant a
distinct decision from ordinary code/test work — not a rule that yields to a general grant unless
the word "refactor" is used, but a rule written to require the user's attention land specifically
on *this class* of change. **Position taken: the general grant does not satisfy that, and both
packages are recorded as authorization `NOT GRANTED` pending an explicit refactoring go-ahead.**
This is a conservative reading and could be wrong — the user may well have meant to include
refactoring — but the cost of asking is one round-trip, and the cost of proceeding on a
mis-read of a rule this project has stated in unusually emphatic, repeated language ("never,"
restated on both backlog entries, restated in `08-refactoring`'s own `SKILL.md` frontmatter) is
higher. Recorded on the Master Build Plan; both packages are `READY` and blocked only on this.

---

## TWBS — `IP-1120` (2026-07-31, `FS-112`/`FEAT-1120`, roadmap R7)

**No-split decision.** `FS-112`'s own Module Responsibilities already establish `music_engine.py`
as sole owner of the new derivation routine and both new WRAM bytes; `input_map.py` and
`music_engine.py` itself are callers at 6 total trigger sites (corrected from `ADS-105`'s original
5 — `FS-112` found `TEMPO_IDX` has two writers, Up and Down, not one). One routine, six call
additions, two WRAM bytes, one test suite: a single tightly-coupled unit with no natural split
point, matching `05-feature-decomposition`'s own Feature Review reasoning verbatim (splitting the
trigger sites across packages would risk exactly the "missed site, silent staleness" failure
`FS-112`'s Risks field names).

**Verb inventory.** This capability needs only *generate* (compute the derived values) — no
*render* (confirmed: `visuals.py` untouched, no consumer exists yet), no *apply* (nothing is
steered by this feature), no *persist* (WRAM only, no save), no *review* (no content to review —
two numeric bytes, not art/music data). Three of four verbs are deliberately, explicitly absent
because this feature's own scope is a pure backend read/interpret layer; recorded so the
capability isn't mistaken for incompletely decomposed.

**Supersession sweep.** Not applicable — this package introduces new state, it does not retire or
generalize an existing model. Confirmed no existing code computes anything resembling
"arousal"/"valence"/mood from steering state (grepped `music_engine.py`/`visuals.py` for
`AROUSAL`/`VALENCE` and found nothing, as expected for a wholly new capability).

**Formula decision — the concrete thing `FS-112` left for this pass.** Both formulas must avoid
on-device division (SM83 has none) and stay cheap against the razor-thin per-frame budget
`IP-9030` measured, even though none of the 6 trigger sites runs inside the exhausted VBlank
window itself (they're all outside `update_visuals`'s own call, per `FS-112`'s Performance
Considerations).

- **`AROUSAL`**: `TEMPO_IDX` (0-7) + `DENSITY_IDX` (0-7) = 0-14, fits directly in the required
  0-15 range with no scaling needed. Two `LD`+`ADD` instructions, no lookup table, no shift.
  Satisfies `FR-1390`'s monotonicity requirement trivially (sum of two non-decreasing inputs is
  non-decreasing in each, holding the other fixed).
- **`VALENCE`**: a 4-entry lookup table indexed directly by `SCALE_IDX` (0-3), each entry a fixed
  0-15 value — e.g. `VALENCE_TABLE = [10, 6, 12, 4]` (illustrative placement, not tuned by ear,
  same `BL-0005`-class first-guess deferral as every other untuned preset value this project has
  shipped; a future `09-content-review` pass can retune without touching the mechanism). Satisfies
  `FR-1400`'s fixed-one-to-one-mapping requirement by construction — a lookup table is definitionally
  a fixed mapping.

Both are `07-implementation-planning`'s own proposal, per `FS-112`'s explicit hand-off — stage 08
should implement exactly these unless it finds a concrete reason not to (Blocking Report, not a
silent substitution).

**Authorization — explicit judgment call, made and recorded, not assumed.** This package has not
been through any go-ahead conversation with the user. The session's earlier "assuming pre
authorization for everything this session" grant was given in a specific, narrower context — it
was the user's direct answer to a flagged re-confirmation question about `IP-9030`, and separately
extended to cover `IP-8010`/`IP-8020` when the user said "Continue include refactoring" in
response to those two packages being flagged `NOT GRANTED`. Both grants were reactive: the user
was answering a specific question this pipeline had just put to them about specific, already-named
packages. `IP-1120` is new-feature work, authored fresh this session under a separate "iterate
toward the next release" instruction that said nothing about authorizing implementation — it asked
for iteration through planning stages, and this project's own standing rule is that authoring a
package, however thoroughly, is never itself authorization to build it. **Recorded: authorization
`NOT GRANTED`.** `IP-1120` is `READY` (fully specified, its two dependency Features both
`VERIFIED`) but not authorized — the pipeline's next step is the G3 gate itself, not a build.

## TWBS — `IP-9040` (2026-08-14, `BL-0111`, `10-integration-review`'s R7 tranche finding F2)

**No-split decision.** The fix is two `CALL('mood_update')` additions inside two already-existing,
already-`VERIFIED` routines (`_emit_begin_blend`, `_emit_blend_tick`, both `music_engine.py`) —
no new WRAM, no new routine, no new file. A single tightly-scoped package matches the size of the
defect; splitting a two-line fix into more than one package would be pure overhead.

**Verb inventory.** Only *generate* applies (both call sites recompute `AROUSAL`/`VALENCE` from
already-current state) — no *render* (`visuals.py` still has no consumer, unaffected by this
package, per `IP-1120`'s own still-standing non-scope), no *apply* (nothing new is steered), no
*persist*, no *review* (two derived numeric bytes, not art/music data). Same shape as `IP-1120`'s
own verb inventory, since this package is closing a gap in that same capability's write coverage,
not introducing a new one.

**Supersession sweep — the actual finding this package exists to fix.** `BL-0111` *is* the result
of a supersession sweep `IP-1130`'s own planning never ran: `10-integration-review` grepped every
current write site touching `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` tree-wide (not just within
`IP-1120`'s own 6 named sites) and found `IP-1130`'s `_emit_begin_blend`/`_emit_blend_tick` write
all three without ever calling `mood_update` — exactly `IP-1120`'s own Risks field's named "7th
write path" hazard, materialized by a package that shipped after it. Re-ran the same sweep this
pass, tree-wide, once more before authoring: confirmed these are the **only** two write sites to
any of the three fields that don't already call `mood_update` (the 6 `IP-1120`-named sites still
do; `init_engine`'s own writes still do) — closing both closes the gap completely, no third site
missed.

**Placement, not just presence.** `_emit_begin_blend`'s call lands immediately after its own
`SCALE_IDX` write (mirroring `IP-1120`'s own convention of calling `mood_update` right after the
triggering write lands) — at that point `TEMPO_IDX`/`DENSITY_IDX` are still their pre-press
values (only `BLEND_SRC_*` has been captured, not yet applied — `SCALE_IDX` is the one field that
changes immediately on a Start press), so `AROUSAL` correctly stays at its pre-press value on the
press frame itself while `VALENCE` correctly updates immediately, matching each field's own
already-established instant-vs-gradual semantics exactly. `_emit_blend_tick`'s call lands inside
the active-blend branch, after the 3-field interpolation loop writes `TEMPO_IDX`/`DENSITY_IDX`/
`DUTY_BIAS` for that step, **before** falling through to `bt_done`'s early-exit label — this
means the call only executes on the frames `BLEND_STEP` is actually incrementing (1-4), never on
the overwhelming steady-state majority of frames (`BLEND_STEP` already `4`), preserving
`NFR-1170`'s zero-added-per-frame-cost contract exactly as `IP-1120`'s original 6 sites do.

**Timing risk, named explicitly.** `VR-1130`'s own F1 finding measured that `_emit_blend_tick`'s
per-frame cost was tight enough on active-blend frames to matter (the original per-frame
`STYLE_TABLE` re-derivation blew the budget; the `BLEND_DELTA_*` precompute fix brought it back
within budget). `mood_update` adds roughly a dozen more instructions to that same per-active-blend-
frame path. This is real added cost on a path already shown to be budget-sensitive — Risks field
below names it explicitly and requires `08`/`09` to re-measure `VIS_ENTRY_LY` on an active-blend
frame with this addition in place, not merely assume the earlier margin still holds.

**Authorization — explicit judgment call.** No standing grant covers this. The session's earlier
grants (`IP-9030`'s re-confirmed basis; `IP-8010`/`IP-8020`'s "Continue include refactoring";
`IP-1120`'s "Yes proceed"; `IP-1130`'s "Yes, build it.") were each reactive answers to a specific
flagged question about a specific, already-named package — none extends to fresh remediation work
authored today. This defect was found by review, not by the user, and nothing in the current,
user-approved release plan (`01-release-plan.md`) named it, since it didn't exist to name until
this session's `10-integration-review` surfaced it. **Recorded: authorization `NOT GRANTED`.**

## TWBS — `IP-9040` v2 re-scope (2026-08-17, re-scoping after v1's Blocking Report)

**No-split decision, unchanged.** Still one package, same two call sites, same files — v1's fix
shape (two `mood_update`-derived recomputes inside `_emit_begin_blend`/`_emit_blend_tick`) was
correct in principle; only the *implementation cost* of getting `AROUSAL`/`VALENCE` correct at
each site needed to shrink. No new file, no new routine, no new WRAM byte.

**Grounding, not guessing — three claims independently measured before re-authoring** (throwaway,
uncommitted experimental builds, same convention `VR-9030`/`VR-1130` used for their own live
`pyboy` measurements; nothing from these experiments was left in the tree):

1. **Isolated each v1 call site's own cost.** `_emit_begin_blend`'s full `CALL('mood_update')`
   alone (press-frame only, not per-active-blend-frame) measured **within budget** on both a
   plain single blend and a mid-blend-restart (`VIS_ENTRY_LY` 152-153 throughout). `_emit_blend_
   tick`'s full `CALL('mood_update')` alone (every active-blend frame) measured **the actual
   regression** — `VIS_ENTRY_LY` 0-1 on both scenarios, isolating v1's Blocking Report finding to
   one of its two sites, not both.
2. **A full `mood_update()` call recomputes both `AROUSAL` and `VALENCE` at every site, but each
   site only ever writes inputs to one of the two.** `_emit_begin_blend` only writes `SCALE_IDX`
   (`TEMPO_IDX`/`DENSITY_IDX` are read but not written there) — it only needs `VALENCE`'s
   recompute, not `AROUSAL`'s (no write, no `FR-1410` obligation to touch it). `_emit_blend_tick`
   only writes `TEMPO_IDX`/`DENSITY_IDX` — it only needs `AROUSAL`'s recompute, not `VALENCE`'s
   (`SCALE_IDX` is never touched there). Replacing each site's full `mood_update()` `CALL`/`RET`
   with an **inline, half-sized recompute** (the one field each site's own writes actually
   obligate) — reusing registers already live in `_emit_blend_tick`'s own interpolation loop
   (`tempo`'s just-written value stashed in the otherwise-free `D` register, added to `density`'s
   own value the moment it lands in `A`, written to `AROUSAL` immediately — before `duty`'s own
   iteration even begins, since duty is irrelevant to `AROUSAL`) instead of two fresh WRAM re-
   reads — measured **within budget on every ordinary single-blend frame, all 4 interpolation
   steps, matching `FR-1410` exactly with no CPU overhead beyond the ~6-7 lean instructions each
   site now adds.**
3. **The mid-blend-restart collision frame remains a genuine, specific, narrower residual risk,
   honestly disclosed rather than declared solved.** Even with the minimized inline design above,
   the exact frame a second Start press lands mid-blend (`_emit_begin_blend` and `_emit_blend_
   tick` both firing fully, same frame, `FR-1490`'s own scenario) still measured `VIS_ENTRY_LY`
   dropping to `0` — out of range — while the *first* press's own begin_blend+blend_tick(step
   0→1) collision frame (functionally the same shape) measured in-budget (152). The size of the
   swing (153→0, not a marginal few cycles) plus the asymmetry between two structurally similar
   collision frames is consistent with the already-disclosed, general ~30-frame-periodic engine-
   wide characteristic (`BL-0106`) landing unluckily on this specific restart timing, not a defect
   in the minimized design's own logic — but this is a hypothesis, not independently confirmed
   this pass, and doesn't change what Task 6 below must still do.

**Why the deferred-recompute idea (compute `AROUSAL` for last frame's write, one frame late,
exploiting `FR-1410`'s own explicit "no more than one frame after" tolerance) is named but NOT
adopted as this package's design:** cleanly flushing the *final* settle-frame's own deferred value
without ever running the recompute on a genuinely idle steady-state frame (which would violate
`NFR-1170`'s zero-unconditional-per-frame-cost contract) requires a sentinel/flag distinguishing
"settled, recompute pending" from "settled, already flushed" — realistically a new `BLEND_STEP`
value (5) or a new WRAM byte, either of which risks crossing condition 3 of the G3 pre-
authorization path ("no different approach than the original design already committed to") and
changes `BLEND_STEP`'s own existing observable contract that `test_rom.py`'s `T21`/`T22` suites
already assert exact values against. Named here as a candidate for `08` to revisit only if the
minimized design's own residual restart-collision risk (point 3 above) turns out not to clear
budget in the real build — not prescribed, since it wasn't required to prove out the general case.

**Files to Create/Modify, updated from v1**: same two routines, same two files
(`music_engine.py` only) — only the *body* of each `CALL('mood_update')` site changes, from a full
`CALL`/`RET` into `mood_update` to an inline, half-sized, single-field recompute reusing already-
live registers. `AROUSAL`/`VALENCE` WRAM addresses, `mood_update`'s own label/body, and its 6
existing `IP-1120` call sites are all unchanged and untouched.

**Task 6, re-scoped and widened**: v1's Task 6 asked for "an active-blend frame" (singular,
generic). v2's Task 6 must independently re-measure `VIS_ENTRY_LY` across, at minimum: (a) every
intermediate step of a plain single blend (the case now measured clean); (b) the initial press
frame itself (`BLEND_STEP` 0→1, begin_blend+blend_tick collision — measured clean, but with the
final shipped instruction sequence, not this pass's exact throwaway experiment); (c) **the mid-
blend-restart collision frame specifically** (`FR-1490`'s own scenario) — the one case this pass
could not close within budget with the minimized design alone. If (c) still regresses in the real
08 build, the correct response is another Blocking Report (or the deferred-recompute redesign
above, evaluated fresh against condition 3), not a silent absorb — same standing convention this
package's own v1 already established.

**Authorization (G3), re-verified fresh against v2's actual design, not inherited from v1.** All 4
conditions of the `00-pipeline-manager` conformance-remediation pre-authorization path re-checked:
(1) `IP-1130` (the package this remediates) is release-plan-covered (`01-release-plan.md` §2.2,
R8, v1.0 scope) and separately carries its own explicit G3 grant (commit `351c0cf`) — unchanged
from v1's own basis, still holds. (2) The finding (`BL-0111`) is still a conformance gap against
the already-baselined `FR-1410` — v2 doesn't change what's being restored, only how cheaply.
(3) v2's fix still lands inside `IP-1130`'s own `music_engine.py` mechanism/file footprint — no
new file, no new routine, no new WRAM byte, same two call sites, only their bodies changed from a
shared-routine `CALL` to an inline recompute of the same underlying formula `mood_update` itself
already uses — this is a leaner instantiation of the *same* mechanism, not a different one.
(4) Severity unchanged, Medium-High, below Critical. **Qualifies — G3 granted on that basis, both
bases (original `IP-1130` authorization + `BL-0111`) cited again below**, same as v1.

## TWBS — `IP-8030` (2026-08-17, `BL-0089`, module-decomposition refactor)

**Origin.** `BL-0089` (filed 2026-08-07, full-repo audit): `08-content-authoring`'s declared write
scope names `tiles.py`/`patterns.py`/`music_data.py`; none exists — content data lives inline in
`visuals.py` (tile pixel bytes) and `music_engine.py` (every scale/tempo/style/song/motif/rhythm
table). `GDS-09` §1 records this honestly at the interface level ("three of those five do not
exist here... `visuals.py` owns its tile bytes inline... `music_engine.py` owns its own data
tables as module-level Python constants"). **The user decided 2026-08-07: create the three
modules** — extract the data out, restoring the decomposition `GDS-03`/`GDS-09` always described,
over the two cheaper alternatives (repoint the skill scope at where content actually lives, or
retire/narrow the skill). This is the release plan's own named critical-path prerequisite
"immediately before R12.5" (`01-release-plan.md` §2.5) — R12.5's retuning pass needs a working
`08-content-authoring` write surface to retune *through*, which does not exist today.

**No design work owed here — this is execution of an already-made decision, not a fresh one.**
The split below is this planning pass's own judgment call (the user specified *that* the modules
should exist, not their exact per-table membership); recorded explicitly rather than left
implicit, since a guessed split is exactly the kind of drift stage 08 would otherwise discover
mid-implementation.

**Split, by content category, not by size:**

- **`tiles.py`** — visualizer tile pixel art + palette color data: `_tile_off_bytes()`,
  `_tile_on_bytes()`, `_bar_tile_bytes(n)` (currently `visuals.py:64-80`), `CALM_PALETTE`/
  `BAD_PALETTE` (currently `visuals.py:87-88`). All four are pure, `rom`-independent — no ROM
  object dependency, straightforward move.
- **`patterns.py`** — rhythm-pattern generation: `_euclidean_pattern(k, n)` (currently
  `music_engine.py:369-377`, pure function, no `rom` dependency), `DENSITY_K`, `NOISE_STEP_TABLE`
  (currently `music_engine.py:362-366`). `NOISE_STEPS` (the `n=16` default) moves alongside since
  `_euclidean_pattern`'s own default argument needs it.
- **`music_data.py`** — scale/mode/pitch/style/song/motif tables, the "curated musical building
  blocks" the content-authoring skill's scope names: `TEMPO_BPM`/`TEMPO_TABLE`, `OCTAVE_ROOT_HZ`,
  `SCALE_SEMITONES`/`SCALES`, `SEMITONE_TABLE_DATA`, `DISSONANCE_WEIGHT_BY_IC`, `DELTA_TABLE`,
  `VALENCE_TABLE`, `STYLE_TABLE`, `SONG_TABLE`/`N_SONG_PHASES`, `ARPEGGIO_OFFSETS`,
  `DUTY_BY_DEGREE`, `MOTIF_TABLE`/`N_VARIANTS`, `MOTIF_VARIANT_SELECTOR`, `CHMIX_MASKS`
  (currently scattered `music_engine.py:99-360`, per-table line numbers in the package's own
  Files to Create/Modify field — re-verify against the tree at implementation time, this planning
  pass's own line numbers may have shifted).

**Deliberately staying in `music_engine.py` (not content, engine wiring):** `CHANNELS` (ties
WRAM/register constants together with behavioral parameters, keyed to `music_engine.py`'s own
local WRAM address names — moving it would need those addresses re-exported and risks a real
import cycle, for a table that is wiring, not tunable musical content); `LFSR_POLY`/
`LFSR_SEED_PA`/`PB`/`WV` (algorithmic seeds, not musical content); `DIV`, `PRESET_*` (already
live in `wram_constants.py`, `IP-8020`). Named explicitly so a future pass doesn't assume these
were simply missed.

**Naming convention decision.** `GDS-09` §1 records the *reference project's* expected interface
names (`build_tile_data()`, `ALL_PATTERNS`, `music_data()`) as never having existed in this
project. This package does **not** adopt those wrapper-function/registry names — it uses plain
module-level constants in each new file, the same convention this project's own `wram_constants.py`
(`IP-8020`, `BL-0065`) already established for its own content-adjacent split. Inventing a
function/registry wrapper solely to match the reference project's naming, when this project's own
shipped convention is flat constants, would add ceremony without changing behavior — `GDS-09`
itself favors "record plainly rather than documenting interfaces that aren't there." Once this
package lands, `GDS-09` §1's "three of those five do not exist" note becomes stale and needs a
follow-up correction pass (owned by `03-architecture-design-synthesis`, not this package — refactor
packages don't edit the GDS ladder).

**Verb inventory:** N/A — a structural relocation of existing data, not a new capability spanning
runtime verbs.

**Supersession sweep:** every other module's imports of the moved names were checked
(`build_rom.py`, `test_rom.py`, `input_map.py`, `gbc_lib.py`). `build_rom.py`/`input_map.py`/
`gbc_lib.py` import only functions/register constants from `music_engine.py`/`visuals.py`, never
the moved data tables — clean, nothing to update there. `test_rom.py` imports `STYLE_TABLE`,
`MOTIF_TABLE`/`N_VARIANTS`, `SONG_TABLE`/`N_SONG_PHASES`, `VALENCE_TABLE` (module-level, lines
94-97) and `DENSITY_K` (function-local, line 277) directly `from music_engine import ...` — these
5 import lines must be repointed to `music_data`/`patterns` respectively; this is the one real
call-site update the sweep found, named in Files to Create/Modify below. No other tree-wide
reference to the old locations survives (a leftover `from music_engine import STYLE_TABLE` would
`ImportError` immediately, not silently pass — the equivalence contract's own full-suite run is
sufficient to catch a missed site).

**No split within this package** — the three new modules are one coherent Definition of Done (one
equivalence contract covering all three, one full-suite pass); splitting by target file would
triple the review overhead for no independent value, since none of the three can be verified in
isolation without the others.

---

## Tranche — `FS-115` / `FEAT-1160`: the arpeggio re-rooted, gated and varied (`BL-0127`) — 2026-08-21

**One package: [`IP-1150`](packages/IP-1150-arpeggio-rerooted-gated-varied.md)**, executor
`08-code-implementation`.

### Why one package and not three

`ADR-0005` states four rules (chord-aware, gated, varied, cheaper) and the obvious cut is one
package per rule. It is the wrong cut, for a reason that is structural rather than a matter of
convenience:

- **Gated and varied are the same table lookup, by design.** `FR-1610` requires the figure set to
  contain a member under which the note does not arpeggiate. That member *is* the gate — `FR-1600`
  is expressed by forcing the pattern index, not by a separate branch. There is no intermediate
  state in which one exists and the other does not, so a "gate" package and a "vary" package would
  share one mechanism and neither could be verified without the other.
- **Chord-aware alone is a shippable state that we have decided not to ship.** It would fix the
  measurable defect (46.4 % → 100 % chord tones) while leaving the *reported* one untouched — a
  perfectly in-chord figure still repeating identically 2.5×/second forever. `ADS-108` §12.5
  rejects that as answering the measurement instead of the listener. Cutting it as its own package
  would make shipping it an available outcome, and this tranche exists because the listener's
  complaint is the acceptance criterion.
- **Cheaper is not separable work at all.** The per-frame saving comes from *deleting* the address
  arithmetic that only exists to support degree-offset resolution. Remove the offsets (chord-aware)
  and the saving falls out; keep them and there is nothing to optimize that `BL-0125` has not
  already found blocked. `NFR-1280` is a constraint on the same edit, not a follow-on to it.

One package, one Definition of Done, one before/after measurement whose delta is attributable to
one change. The cost of the choice is a package that touches two files across the stage-08 peer
seam (declared in its Risk 5, same as `IP-1140`) and a larger single review surface.

### Verb inventory

The capability spans *generate* and *apply*; *render*, *persist* and *review* have named owners or
explicit deferrals:

| Verb | Owner |
|---|---|
| **generate** — decide which figure this note gets | `IP-1150`, per-onset draw inside `_emit_channel_gen`'s existing onset branch |
| **apply** — sound it, frame by frame | `IP-1150`, `_emit_arpeggio_tick` rewritten as cache playback |
| **render** — show it on the visualizer | **Deliberately deferred, not silent.** `visuals.py` is untouched; nothing in `ADS-108` §12, `FS-115` or `FR-1600`-`FR-1630` asks for a visual signal, and the existing channel-activity tiles already reflect `NR52` unchanged. Revisit only if roadmap R9 wants articulation as a visual axis. |
| **persist** | N/A — this project persists nothing (`MSTR-001` C2, `ADR-0002`). |
| **review** | `09-content-review`, named in `FS-115`'s Verification Plan and in `IP-1150`'s Verification Checklist, with its question stated concretely (*"does the arpeggio still read as a constant looping figure?"*) rather than left as "review the sound." |

### Collision & obsolescence sweep

All four questions asked; all four answered. This sweep is worth reading rather than skimming,
because **this tranche exists because the sweep's own question 3 was not asked when `IP-1140` was
planned** — the sweep was widened to four questions on 2026-08-20 for exactly this class of defect,
and this is its first real exercise.

**1 — Who else writes the state I write?**
`IP-1150` writes `NR13`/`NR14` and `NR23`/`NR24` (pulse A/B frequency) every frame, plus new
per-channel WRAM cache bytes. Grepped, not assumed:

- `_emit_channel_gen`'s onset branch writes the same four frequency registers, once per onset, with
  the trigger bit set. **This is the collision `IP-1140` shipped into**, and it is now explicit and
  intended: the onset write triggers the envelope at the note's pitch, `arp_tick` articulates it
  afterwards, and the cache the onset builds is what `arp_tick` reads — one producer, one consumer,
  a defined hand-off instead of two mechanisms overwriting each other.
- `input_map.py` writes **none** of these registers (confirmed by grep — it is `GDS-03`-forbidden
  from touching PSG registers and honours it).
- The new cache bytes have exactly **one writer** (the owning channel's own onset branch) and one
  reader (`arp_tick`, same channel). Not a shared broadcast field, unlike `CHORD_IDX`.
- `CHORD_IDX`/`CHORD_TOGGLE` are **read only** by this package. Its one write to `CHORD_TOGGLE`
  bits 2-3 stays where `IP-1140` put it; no new writer is introduced.

**2 — Does anything still encode a model I am retiring?**
The retired model is *"the arpeggio is a fixed degree-offset pattern applied to `CUR_DEGREE`."*
Grepped `ARPEGGIO_OFFSETS`, `arpeggio_offsets_table`, `ARP_SUBTICK_RELOAD`, `ARP_DEGREE_SCRATCH`
across the tree. Live encodings found and named in Files to Create/Modify: `music_data.py` L145
(the table), `music_engine.py` L24 (import), ~L1074 (the lookup), ~L1590 (the emission), and
`test_rom.py`'s `T11.1`, which asserts the step index cycles — a statement about the *retired*
design that will keep passing while meaning nothing, which is precisely why it is re-authored
rather than left. `Claude.md`'s "Sound design techniques" **Arpeggio** bullet describes the retired
design in prose and is named in Documentation Updates. `ARP_DEGREE_SCRATCH` is shared, so it is
grepped again before removal rather than assumed dead.

**3 — Does what I am ADDING make something existing redundant, vestigial, or contradictory?**
Asked in both directions:

- *Does the new mechanism obsolete something?* The arpeggio itself was the workaround (`R216`:
  "implying a chord on a single channel" — a harmony substitute) and this tranche is the belated
  answer to it. Nothing further is obsoleted: bad-zone recovery acts on note *selection* and stays
  orthogonal (`FR-1590`); vibrato and portamento are **not** made redundant and must survive
  (Risk 1); the mute gate is untouched.
- *Does it revive something previously blocked?* Yes, and it is recorded rather than quietly taken:
  `BL-0125`/`FR-1560`'s pulse-B octave placement was withheld by `IP-1140` **because `arp_tick`
  hardcoded `octave_delta = 0`** — a constraint this package removes. `FS-115` OQ3 records it as
  *unblocked, not owed*, and this package deliberately does not exercise it, so the before/after
  measurement stays attributable to one change.

**4 — Does my change alter what any existing metric actually measures?**
Yes, and this is the question that produced `BL-0128`. `NFR-1270`'s harsh-interval acceptance metric
was sampled at `CUR_DEGREE` — the harmony layer's *intent* — while `arp_tick` rewrote the frequency
register afterwards, so every figure recorded under it describes a pitch that was never heard.
`NFR-1270` has been amended (2026-08-21) to make **sounding pitch** the normative basis, and the one
package that claimed the NFR (`IP-1140`) has its recorded figures corrected as part of this tranche:
**strong 25.7 %, weak 36.1 %, aggregate 30.9 %**, not 12.2 %/30.6 %/21.5 %. `IP-1150`'s own
before/after is measured on the corrected basis from the start. No other metric in the tree samples
an intermediate this package inserts itself in front of (`VIS_ENTRY_LY` samples a frame boundary;
`DISSONANCE_SCORE` is computed from `SEMI_*` and is engine-internal, already caveated by `BL-0124`).

### Sequencing note

`IP-1150`'s only real dependency, `IP-1140`, is `COMPLETE` but **not `VERIFIED`** — so by the letter
of this plan's `READY` rule the package is `BLOCKED`. That is recorded honestly on the Master Build
Plan rather than smoothed over, together with the reason it does not stop the work: the project
owner's standing instruction is to iterate toward a pleasant result, `IP-1140`'s missing
verification is a *fresh-session* obligation rather than a defect finding, and `IP-1150` would be
re-planned anyway if that verification returned findings. The two packages verify as a pair.

---

## Tranche — Select becomes a reroll (`ADR-0006` / amended `FR-1070`) → `IP-1160`

**Source:** [`ADR-0006`](../architecture/adr/ADR-0006-select-becomes-reroll-not-reset.md) and the
amended `FR-1070`/`FR-1420`/`FR-1630` (`docs/requirements/01-functional-requirements.md`, Delta
Review 2026-08-21 second pass). Trigger: the project owner's own instruction — *"The select-reset
does not need to bring it back to the boot default either, just course correct from a bad zone"* —
plus his approval of folding reroll into the same button.

### Why one package, and why stages 05/06 were skipped

**One package.** The change has a single seam (`init_engine`'s entry structure), a single
Definition of Done ("a Select press changes the material and changes nothing the listener set"),
and its test work is inseparable from its code work — seven shipped checks assert the behaviour
being removed, so a package that changed the code without re-authoring them would leave a red tree
by construction. Splitting produces two halves neither of which is independently verifiable.

**05 skipped.** `05-feature-decomposition` exists to group requirements into features and features
into releases. This tranche adds no capability: it redefines the contract of a control that has
existed since `IP-0001`, under a requirement that already exists (`FR-1070`) and was amended rather
than added. There is no new `FEAT-xxxx` row to catalog and no release-bucket question to answer.

**06 skipped.** `06-feature-specification` exists to turn a catalog row into a behavior contract.
That contract already exists in full and in two places: `ADR-0006` decides the design and records
the alternatives weighed, and the amended `FR-1070` states the observable behaviour — including the
clause a spec would otherwise have had to discover, *"by every write path."* An `FS-116` would have
restated both without adding a decision. **Recorded as a deliberate skip with a reason, not as a
shortcut**: if a reader later finds the design underdetermined, the defect is in `ADR-0006` or
`FR-1070` and routes there, not to a missing FS.

### Verb inventory

The capability is *reroll*. Its verbs and their owners:

| Verb | Owner | Note |
|---|---|---|
| **generate** (produce genuinely new material) | `IP-1160` — reuses the existing `DIV` reseed | Already shipped since `IP-0007`; this package does not touch it, and that is worth stating: two-thirds of the capability was already present (`R217` §3a). |
| **apply** (course-correct out of a bad zone) | `IP-1160` — reuses the existing bad-zone clear | Unchanged behaviour, unchanged code. |
| **preserve** (leave the listener's settings alone) | `IP-1160` — **the only new work in the tranche** | This is the whole package. |
| **render** (show the listener what changed) | **Deliberately deferred, and the deferral is the point.** | The settings-indicator row (`IP-1110`) already shows the five indices, and after this change they *do not move* on a Select — so there is nothing new for the display to render. A listener sees the reroll by hearing it. Naming this rather than leaving it silent, per the verb-inventory rule: no visualizer feedback for the press itself is planned, and if listening says the press feels unacknowledged, that is a `09-content-review` finding routing to `03`, not a gap in this package. |
| **persist** | **N/A — no persisted state exists** (MSTR-001 C2, no SRAM). | |
| **review** | `09-package-verification` (mechanical) + `09-content-review` (does the reroll actually feel like new music with the same settings?) | The content review additionally owns `BL-0144`, escalated by the requirements pass. |

### Collision & obsolescence sweep

Run in full. This is the amended sweep's **first real customer**, and its performance is assessed
honestly at the end of this section rather than assumed.

**1 — Who else writes the state I write?**

The state whose write behaviour changes is the six values `FR-1070` clause (c) protects. Consulted
[`GDS-04` §1.2](../architecture/04-domain-model.md) (steering indices) and
[`GDS-04` §1.4](../architecture/04-domain-model.md) (pitch/output layer, authored 2026-08-21), then
`grep`ped the tree to confirm the registries are current. Both were.

| Value | Writers, per §1.2/§1.4 and confirmed by grep | Effect of this package |
|---|---|---|
| `OCTAVE_IDX` | D-pad L/R; `init_engine` | one writer removed from the Select path |
| `SCALE_IDX` | A; `init_engine`; style application | one writer removed from the Select path |
| `CHMIX_IDX` | Start; `init_engine` | one writer removed from the Select path |
| **`TEMPO_IDX`** | D-pad U/D; `init_engine`; style application; **song-form phase transition** | **two** writers removed from the Select path — see below |
| **`DENSITY_IDX`** | B; `init_engine`; style application; **song-form phase transition** | **two** writers removed from the Select path |
| `DUTY_BIAS` (§1.4) | style application; `blend_tick` interpolation; `init_engine` | one writer removed from the Select path |

**This question is what produced `D1`, and it produced it directly.** §1.2 has recorded *song-form
phase transition* as an independent writer of `TEMPO_IDX`/`DENSITY_IDX` since 2026-07-26. Following
that entry into `init_engine` finds a **second** write of both from `SONG_TABLE[0]`
(`music_engine.py:1637-1638`), 50 lines below the five obvious `PRESET_*` writes and under a
comment explaining why it is harmless — *"`SONG_TABLE[0]`'s tempo_idx/density_idx match
`PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX` exactly, so the writes just above are not disturbed."* That
reasoning is correct today and stops being correct the moment the writes above are removed. **Eight
writes, not five.** An implementation working from the obvious five would ship a Select that
preserves octave, scale and channel-mix while silently resetting tempo and density.

`GDS-04` §1.4 contributed a second, independent consequence: its `ARP_CACHE_PA`/`_PB` row records
that the caches are written *"only at onset, and by `init_engine` (boot and Select — `FR-1630`)"*
and resolve pitches through `SCALE_IDX`/`OCTAVE_IDX`. Since the reroll path no longer sets those
first, the caches now resolve against **the listener's** scale and octave. That is correct and
required (`FR-1630` as strengthened), and it is only obviously correct once the registry has said
who reads what. The same reasoning applies to `AROUSAL`/`VALENCE` (`FR-1420`) and to `BLEND_STEP`.

**Collisions:** none introduced. Every removal is a removal; the `last-write-wins` contract §1.2
governs is untouched, and no new writer of anything is added.

**2 — Does anything still encode a model I am retiring?**

The retired model is *"Select restores the boot preset."* `grep`ped its literal signature across
the tree, not only the files `Files to Modify` names:

| Location | What it encodes | Disposition |
|---|---|---|
| `input_map.py:80-85` | comment *"Select: unconditional reset to the known-good preset (FR-1070)"* + `CALL init_engine` | **In scope** — the call target changes and the comment is rewritten. |
| `music_engine.py`'s `init_engine` header comment (*"boot init AND Select-reset target, GDS-03 §5"*) | the conflated single entry point | **In scope.** |
| `test_rom.py` — `T5.2`/`T5.3`/`T5.4`/`T5.5`, `T15.6`, `T17.8`, `T18.9`/`T18.10` | assert the removed behaviour | **In scope**, re-authored per `D4`. |
| `test_rom.py` — `t7_noise_density:312` | `tap(pb, 'select')` with the comment *"Reset back to preset (density 0) before the next iteration's relative B-taps"* | **In scope**, and see question 4 — this is a fixture that *uses* Select as a reset primitive, which is a different failure from asserting Select's behaviour. |
| `Claude.md` — the input-mapping table row, the autonomous-recovery section, the Known Good Behavior bullet | the old prose | **In scope.** |
| **`GDS-03` §3's control table and §5 (*"Reset-to-preset behavior (Select)"*, incl. §5's `IP-0007` amendment)** | the architecture-level statement of the old model | **OUT OF SCOPE — routed upstream, not planned around.** `GDS-03` belongs to `03-architecture-design-synthesis`. `ADR-0006` supersedes it and `GDS-01`/`GDS-04` were amended in the same run, but `GDS-03` was not, and this skill does not edit architecture. Filed for `03`. |
| `PRESET_TEMPO_IDX` … `PRESET_CHMIX_IDX` constants | the preset itself | **Retained, and still used** — by boot, and by the tests' own expected values. Not vestigial. |

**3 — Does what I am ADDING make something existing redundant, vestigial, or contradictory?**

This package is almost entirely *removal*, which is the unusual case for this question. What it
adds is a boot-only prologue and a second entry label. Asked anyway, three answers:

- **`DUTY_BIAS ← 0` on the reroll path becomes contradictory** — not redundant, actively wrong.
  `DUTY_BIAS` is derived from the style row `CHMIX_IDX` selects; `CHMIX_IDX` now survives a Select,
  so clearing the bias would leave the engine's timbre disagreeing with the preset that chose it.
  Moved to the boot prologue (`D3` settled this at requirements altitude; recorded here because the
  implementation must not treat it as an afterthought).
- **`BLEND_STEP ← 4` on the reroll path is *not* obsoleted — it is strengthened, and this is worth
  recording because the opposite conclusion is the easy one.** `VR-1130`'s F1 defect was that a
  Select during an active blend left `blend_tick` running with stale source/delta values that
  overwrote *the freshly-reset* `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` on the following frames. A
  reader could reason: "Select no longer resets those, so there is nothing to protect." Exactly
  wrong — a stale blend would now overwrite **the listener's** values, which is precisely the
  promise this package exists to make. **Kept deliberately, with the reason recorded.**
- **`init_engine`'s name becomes misleading**, since it will no longer be the Select target. A
  naming issue, not a mechanism one; handled by the entry-label split rather than left implicit.

**4 — Does my change alter what any existing metric actually measures?**

**Yes — one real hit, and it is not the hit the question's own example predicts.**

`t7_noise_density` (`test_rom.py:312`) presses Select **as a reset primitive**, not to test Select:
*"Reset back to preset (density 0) before the next iteration's relative B-taps."* Its loop drives
`DENSITY_IDX` to each target by pressing B a *relative* number of times from an assumed zero. After
this package that assumption is false, and each iteration's taps accumulate from wherever the
previous one ended — so `T7` would be measuring densities other than the ones it labels.

**It would not have failed loudly.** The shipped loop iterates over exactly `(0, len(DENSITY_K)-1)`;
the first iteration taps B zero times, so it happens to leave `DENSITY_IDX` at 0 and the second
still lands on 7. `T7.setup` passes, `T7.3`'s max-versus-min comparison passes, and the suite stays
green — **while the fixture's stated invariant is false and the next person to add a middle density
gets wrong numbers with no warning.** That is the exact shape of defect this question exists to
catch: a measurement quietly re-pointed, not a test that breaks.

Two metrics checked and cleared: **`VIS_ENTRY_LY` on the Select frame** (`T19.4`) still measures
what it claims — the reroll path does strictly *less* work, so the frame gets cheaper, and the
assertion is a range check that does not encode the old cost. **`NFR-1270`'s harsh-interval
figures** are unaffected in basis, but any future measurement driver that presses Select to reach a
known baseline inherits `T7`'s problem; the requirement's newly-normative *scope* clause
(`BL-0140`) already forces such a driver to state what it measured over.

### How the amended sweep actually performed — an honest assessment

Recorded because the pipeline's own audit is the reason the sweep was amended, and a quiet success
would be worth less than a real reading.

- **Question 1 earned its place unambiguously, and the registries are why.** `D1` — eight writes,
  not five — came directly from following §1.2's *song-form phase transition* row into
  `init_engine`. Without the registry the natural move is to grep `TEMPO_IDX` in `init_engine`,
  find the `PRESET_*` write, and stop; the second write sits 50 lines later behind a comment
  arguing it is harmless, and that argument is *true* until this package makes it false. This is
  the strongest evidence in the run that the registries pay for themselves — and note the registry
  entry that mattered has existed since 2026-07-26. What changed is that a stage was told to
  consult it.
- **Question 4 earned its place, and did so on merit rather than by example.** Its own illustrative
  case is about an acceptance metric sampled at an internal intermediate. The hit here is
  structurally different — a *test fixture* using the changed behaviour as a primitive — and the
  question still caught it, because "what does this change cause to be measured differently"
  generalises past its example. It also caught something that would not have gone red.
- **Question 3 is the one to be honest about: on this case it did not do independent work.** Its
  text names *this exact Select scenario* as one of its two worked examples, so surfacing it here
  proves nothing about the question — the answer was written into the prompt. Asked on the merits
  (*what does adding a boot-only prologue make redundant?*), question 3 returned mostly naming
  observations; its one genuinely useful output was the **inverse** result — that `BLEND_STEP`'s
  guard is *strengthened*, not obsoleted, and must be kept for a reason opposite to the intuitive
  one. That is worth having, but it is a smaller yield than the question's framing implies.
  **Recommendation:** the amendment should not draw confidence from this case. Question 3's real
  test is a package that *adds* a mechanism — the next one that does should be watched, and the
  Select example arguably ought to be retired from the question's text now that it has been acted
  on, so a future reader does not mistake a worked example for evidence.
- **Question 2 performed as it always has** — it is the original supersession sweep, and it did its
  ordinary job of enumerating call sites, including catching that `GDS-03` §5 still encodes the old
  model and belongs upstream rather than in this package.
- **One structural observation about the sweep as a whole:** three of its four questions found
  something here, and *two of the three findings would have shipped green*. The sweep's value is
  concentrated in exactly the cases where the test suite cannot help, which is an argument for
  running it on removal-shaped packages too — the wording ("EVERY package that writes shared
  state or adds a mechanism") arguably does not obviously cover a package whose whole content is
  *stopping* writes. Suggested clarification, routed to whoever maintains the skill: say **"writes,
  stops writing, or adds a mechanism."**

### Findings routed upstream from this planning pass

| Finding | Owner |
|---|---|
| `GDS-03` §3's control table and §5 (*Reset-to-preset behavior (Select)*) still state the retired model. `ADR-0006` supersedes them; `GDS-01`/`GDS-04` were amended in the same run and `GDS-03` was not. | `03-architecture-design-synthesis` |
| The collision & obsolescence sweep's own scope wording covers packages that *write* shared state; a package that *stops* writing it is equally in need of the sweep and is arguably not obviously covered. Suggest "writes, stops writing, or adds a mechanism." Also: question 3's Select example has now been acted on and should probably be retired from the text. | the `.claude/skills/07-implementation-planning` maintainer |

