# Technical Work Breakdown

- **Owned by:** `07-implementation-planning` · **Status:** ✅ Authored, 2026-07-21 (v1 — two
  remediation tranches, `IP-9010`/`IP-9020`)

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

## Master Build Plan

Both packages added as new rows; see [`00-master-build-plan.md`](00-master-build-plan.md).
Neither is `READY` for `08-code-implementation` yet — **both require explicit G3 user
authorization**, not yet on record (this project carries no bootstrap carve-out).
