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
