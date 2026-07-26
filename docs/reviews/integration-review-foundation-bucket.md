# Integration Review — Foundation Release Bucket

**This document now covers five reviews: the original 7-package review (2026-07-21, preserved
below in full), a 2026-07-25 re-review at 9-package scope, an 11-package scope, a 12-package
scope, and a 2026-07-26 re-review at full 13-package scope. See "Re-review — 2026-07-26
(13-package scope, +IP-1080)" for the current state — earlier sections are kept verbatim as the
historical record, not rewritten.**

## Original review — 2026-07-21

- **Scope:** All 7 Foundation-bucket Implementation Packages — `IP-0001` through `IP-0007`
  (`FEAT-1000`, `FEAT-1010`, `FEAT-1020`, `FEAT-1030`, `FEAT-1040`, `FEAT-1050`)
- **Commit reviewed:** `2f085b6` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Pre-condition check:** every package in scope confirmed `VERIFIED` on the Master Build Plan
  before this review began (`IP-0001`→`VR-0001`, `IP-0002`→`VR-0002`, ..., `IP-0007`→`VR-0007`,
  all cross-checked against `docs/implementation/00-master-build-plan.md` immediately prior).
- **Result:** ⚠️ **2 findings** — 1 High, 1 Medium (carried forward from `VR-0007`/`BL-0017`); no
  Critical.

## Full-suite gate (run against the reviewed commit)

- `python3 build_rom.py <path>` → 32768 bytes, valid header (title `DRIFTUNE`, CGB flag `0x80`,
  cart type `0x00`)
- `python3 test_rom.py` → **60 PASS, 0 FAIL out of 60** (T1-T10)

## Dimension 1 — Interface consistency

Exercised: read `build_rom.py`'s full call sequence end to end. Boot order: sound-hardware init
(`NR50`/`NR51`/`NR52` + per-channel base registers, Wave RAM) → `init_engine` → `init_visuals`.
Per-frame order (after `HALT` wakes on the VBlank ISR): `read_joypad` → `apply_input` →
`engine_tick` → `update_visuals`. This is the correct seam order for `visuals.py`'s FR-1120
read-only-consumer contract (it reads state `engine_tick` just wrote, not stale prior-frame
state). `CHANNELS` (a shared Python-level list in `music_engine.py`) is the actual cross-routine
interface between `init_engine`, `engine_tick`, and each channel's `_emit_channel_gen` call — read
in full, every entry (`pa`/`pb`/`wv`) carries a consistent 9-tuple shape consumed identically by
both routines. No patch-point dict is actually used (`build_engine_asm`'s returned `patches` dict
is empty/unused, per its own docstring — a parity stub, not a live interface) — no drift risk
there since nothing reads it. **Clean.**

## Dimension 2 — Invariant sweep

- **ROM budget:** exactly 32768 bytes every build (confirmed above); no manual `rom.seek()` calls
  outside the fixed low-memory vector table (`0x0000`-`0x0040`) and the two fixed entry points
  (`0x0100`, `0x0150`) — all other emission is strictly sequential, so section overlap is
  structurally impossible, not merely untested.
- **VBlank-gated visualizer writes:** the main loop `HALT`s until the VBlank ISR sets
  `VBLANK_FLAG`, then runs `engine_tick`/`update_visuals` synchronously in the same wake — so
  every VRAM/tilemap/palette write `update_visuals` makes happens at the start of the VBlank
  window, not mid-scanout. Correct GBC-safe pattern. **Clean.**
- **WRAM map completeness (GDS-07 vs. shipped code) — FINDING.** Grepped every `0xC0xx`-defined
  constant in `music_engine.py` against `docs/architecture/07-data-model.md`'s §1-§8 tables.
  `LFSR_STATE_PB` (`0xC017`), `LFSR_STATE_WV` (`0xC018`), `NOISE_STEP_IDX` (`0xC019`), `SEMI_PA`
  (`0xC01A`), `SEMI_PB` (`0xC01B`), `SEMI_WV` (`0xC01C`) — six addresses live in the shipped
  ROM, added incrementally by `IP-0002`/`IP-0003`/`IP-0004` — appear **nowhere** in GDS-07. This
  is distinct from the already-tracked `BL-0013` (which is about the *unused* `HIST_HEAD_*`/
  `HIST_*` fields GDS-07 *does* document but the code doesn't use) — this is the opposite
  direction: addresses the code *does* use that GDS-07 never documents at all. No functional
  defect (the addresses don't collide with anything — `0xC013`-`0xC015` and `0xC020`-`0xC037`,
  GDS-07's own reserved-but-unused ring-buffer range, are correctly avoided) — filed as `BL-0018`.
  See Findings.
- **No module took on a second job:** `music_engine.py` carries generation + bad-zone detection +
  autonomous recovery, all under one cohesive "the engine" responsibility per GDS-03's own design
  (not a violation); `visuals.py` stayed strictly read-only across all three packages that could
  have touched it. **Clean.**

## Dimension 3 — Behavioral coherence

Exercised: traced every `CHMIX_IDX` reference across the entire tree — `music_engine.py`
(definition, `PRESET_CHMIX_IDX` reset-write only), `input_map.py` (Start-button step only). **No
code anywhere reads `CHMIX_IDX` to gate, mute, or otherwise condition any channel's generation or
register writes** — confirmed by grep across `music_engine.py`, `build_rom.py`, `visuals.py`; no
`CHMIX`/channel-mix preset *table* (analogous to `TEMPO_TABLE`/`DENSITY_K`) exists anywhere
either. This is a genuine, cross-package dead-end:

- `IP-0001`'s own package doc explicitly scoped this as a promise: *"`DENSITY_IDX`/`CHMIX_IDX` are
  wired and tested for their own index behavior but have no consumer until `IP-0002`/`0003`."*
- `IP-0003`'s package doc confirms the `DENSITY_IDX` half of that promise was kept ("`DENSITY_IDX`
  now has a real consumer"). **The `CHMIX_IDX` half was never kept by any of `IP-0002`-`IP-0007`**
  — no package doc mentions wiring it, and none of the seven independent `VR-000x` verifications
  caught the gap, because each one audited its own package's scope only; this is exactly the class
  of finding single-package verification cannot see and integration review exists to catch.
- `FR-1000`/`FR-1010` (both traced by `FEAT-1000`, which the Master Build Plan and Feature Catalog
  both currently show as fully delivered via `IP-0001`-`IP-0003`) explicitly describe channels
  activating "its channel-mix preset includes/activates" — text that presumes a functioning gate
  that does not exist in the shipped ROM. All four channels always play regardless of `CHMIX_IDX`.
- `Claude.md`/`memory.md` **do** already informally flag this ("channel-mix wired but not yet
  consumed," "Next channel-mix preset (wired, not yet consumed)") — so it was never silently
  hidden — but it was never formally routed through the pipeline: zero backlog entries reference
  `CHMIX`/channel-mix, despite `Claude.md`'s own "Known Issues" section claiming
  `docs/pipeline/backlog.md` is the live, non-stale list of open items.

This is the review's headline finding, filed as `BL-0019` (High). See Findings.

## Dimension 4 — Traceability coherence

- Master Build Plan, `packages/INDEX.md`, and `verification/INDEX.md` all agree: all 7 packages
  `VERIFIED`, cross-references bidirectional (every `IP-xxxx` row links its `VR-xxxx`, every
  `VR-xxxx` names its `IP-xxxx`) and consistent with the actual files on disk (confirmed by
  listing `docs/implementation/verification/` and `docs/implementation/packages/`).
- **`ROADMAP.md` is stale** — its stage-09 row still says "1/7 independently verified" and its
  stage-10 row says "Not reached," both true as of run #6 but not since run #12. Not filed as a
  new backlog entry (routine drift this stage is explicitly instructed to correct, not report) —
  updated directly as part of this review's own output (see below), consistent with this skill's
  named "Update `ROADMAP.md`'s reviews row" responsibility.
- Feature Catalog's `FEAT-1000` row traces to `FR-1000`/`FR-1010`/`NFR-1030` and is implicitly
  treated as fully delivered by the Master Build Plan — but per Dimension 3's finding, `FR-1000`/
  `FR-1010`'s channel-mix clause is not actually satisfied. This is the traceability-layer
  reflection of the same `BL-0019` finding, not a separate one.

## Dimension 5 — Documentation coherence

- `Claude.md`'s architecture/data-layout/input-mapping/Known Good Behavior sections all read as
  accurate against the shipped tree (spot-checked every WRAM range, every input mapping, every
  "Known Good Behavior" bullet against the actual code) — including its two honest
  channel-mix-not-consumed notes, now properly backed by a filed backlog entry (`BL-0019`) instead
  of being the only place that fact was recorded.
- `memory.md`'s WRAM quick-reference table is more current than GDS-07 itself in one respect (it
  already lists `LFSR_STATE_PB`/`WV`, `SEMI_PA`/`PB`/`WV` — the exact fields `BL-0018` found
  missing from GDS-07) — meaning the gap is specifically in the formal architecture doc, not in
  the project's own working memory. No inconsistency between `Claude.md`/`memory.md` themselves.

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| `BL-0019` | `IP-0001` (scoped the promise), `IP-0002`-`IP-0007` (never fulfilled it), `FR-1000`/`FR-1010`, `FEAT-1000` | `CHMIX_IDX` ("channel-mix," the Start-button-controlled parameter) is stepped and reset correctly but has **no consumer anywhere in the shipped code** — no channel is ever gated, muted, or otherwise conditioned on its value, and no channel-mix preset table exists. All four channels always play regardless. `FR-1000`/`FR-1010`'s text presumes this gate functions; it does not. Already informally noted in `Claude.md`/`memory.md` but never formally tracked. | **High** | `07-implementation-planning` — author a remediation package (wire `CHMIX_IDX` to a real channel-activity-mask table and gate each channel's register writes/generation on it, per `GDS-03`'s original design intent), then `08-code-implementation` → `09-package-verification` |
| `BL-0018` | `IP-0002` (`LFSR_STATE_PB`/`WV`), `IP-0003` (`NOISE_STEP_IDX`), `IP-0004` (`SEMI_PA`/`PB`/`WV`), `GDS-07` | Six WRAM addresses (`0xC017`-`0xC019`, `0xC01A`-`0xC01C`) are live in the shipped ROM but undocumented in `docs/architecture/07-data-model.md` — added incrementally across three packages, none of which updated GDS-07. No collision, no functional defect — `memory.md`'s own WRAM quick-reference already has these fields, so the gap is specific to the formal architecture document. | Low-Medium (doc-coherence only, no functional impact) | `03-architecture-design-synthesis` — append a §9 (or extend §8) to GDS-07 documenting these six addresses, alongside its already-scheduled `BL-0013` reconciliation pass |
| (carried forward, not re-filed) | `IP-0007`, `IP-0004`, `FR-1100` | `BL-0017` (`OVERLOAD_THRESHOLD` mathematically unreachable) was filed by `VR-0007` immediately prior to this review and is the natural companion to this review's own findings — re-surfaced here for visibility, not duplicated as a new ID. | Medium-High (see `BL-0017`) | Unchanged — `07-implementation-planning`/`08-code-implementation`, per `BL-0017`'s own disposition |

## Verdict

The seven-package Foundation tranche integrates cleanly at the mechanical level — no interface
mismatches, no ROM-budget or VRAM-timing violations, no duplicated behavior, and documentation
tracks the shipped tree accurately everywhere except one architecture doc gap (`BL-0018`, Low-
Medium). It does **not** integrate cleanly at the behavioral level: a fully-specified,
requirements-traced, player-facing control (channel mix, `FR-1000`/`FR-1010`/`FEAT-1000`) is
completely non-functional, dropped silently across five packages' worth of development and
undetected by seven independent package verifications because none of them had this review's
whole-tranche vantage point. **High-severity finding (`BL-0019`) — recommend against advancing to
`11-release-readiness` until it is remediated and re-verified**, alongside `BL-0017` (already
Medium-High, already scheduled).

---

## Re-review — 2026-07-25

- **Scope:** All 9 Foundation-bucket Implementation Packages — `IP-0001` through `IP-0007` plus
  the remediation tranche `IP-9010` (channel-mix gating, `BL-0019`) and `IP-9020` (overload
  threshold recalibration, `BL-0017`)
- **Commit reviewed:** `c4f12b5`
- **Date:** 2026-07-25
- **Pre-condition check:** every package in scope confirmed `VERIFIED` on the Master Build Plan
  immediately before this review began — `IP-0001`-`IP-0007` unchanged since the original review;
  `IP-9010`→[VR-9010](../implementation/verification/VR-9010-channel-mix-gating.md),
  `IP-9020`→[VR-9020](../implementation/verification/VR-9020-overload-threshold-recalibration.md),
  both flipped `COMPLETE`→`VERIFIED` this session in a genuinely independent fresh-session pass.
- **Result:** ⚠️ **1 new finding (Medium)** — a real cross-package behavioral inconsistency between
  `IP-9010`'s two gating code paths, discovered by exercising the channel-mix + overload seam
  together (neither single-package `VR-9010`/`VR-9020` pass could see this, by design). No
  Critical/High findings. Both `BL-0019` and `BL-0017` are confirmed genuinely closed at the
  integration level, not just the per-package level.

### Full-suite gate (run against the reviewed commit)

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, valid header (title `DRIFTUNE`, CGB flag
  `0x80`, cart type `0x00`)
- `python3 test_rom.py` → **77 PASS, 0 FAIL out of 77** (T1-T13)

### Dimension 1 — Interface consistency

Re-exercised the same boot/per-frame call sequence the original review confirmed clean; unchanged
by `IP-9010`/`IP-9020` (both are additive to `_emit_channel_gen`/`_emit_noise_gen`, no new
call-site wiring). New seam specific to this tranche: `CHMIX_MASKS` is an 8-entry table of
byte-sized 4-bit masks (bits 0-3 used, bits 4-7 spare) — read in full against
[`ADR-0001`](../architecture/adr/ADR-0001-scheme-selection-rides-chmix-preset-space.md), which
plans to reuse exactly those spare bits for future scheme-selection (contingent on `IP-9010`
shipping with this bit layout, which it now has). Confirmed no code anywhere tests or assumes
bits 4-7 are zero (`BIT_b_A(bit_index)` only ever tests bits 0-3) — the spare-bit space `ADR-0001`
is counting on is genuinely free, not silently occupied. **Clean**, and confirms `ADR-0001`'s own
contingency is now satisfied.

### Dimension 2 — Invariant sweep

- **ROM budget:** exactly 32768 bytes, confirmed above; `IP-9010` added one 8-byte table
  (`CHMIX_MASKS`), `IP-9020` added zero bytes (pure constant change) — both within GDS-07 §6's
  already-ample headroom. **Clean.**
- **VBlank-gated visualizer writes:** unchanged by this tranche (neither package touches
  `visuals.py`). **Clean.**
- **WRAM map completeness:** re-checked every `0xC0xx` constant against
  `docs/architecture/07-data-model.md` — `CHMIX_IDX`'s row was updated by `IP-9010`'s own commit
  (confirmed accurate: describes `CHMIX_MASKS` as the real consumer, not the stale
  "index into the channel-activity-mask preset table" placeholder). No new WRAM address was
  introduced by either package (both reuse existing `0xC004`/constants) — no new gap to find.
  **Clean.**
- **No module took on a second job:** both packages stayed inside `music_engine.py`'s existing
  "the engine" responsibility; `IP-9020` is a pure constant change, `IP-9010` extends the existing
  `CHANNELS`-table parameterization pattern rather than adding a new mechanism. **Clean.**

### Dimension 3 — Behavioral coherence — FINDING

The original review's headline finding (`BL-0019`, channel-mix has no consumer) is now
**genuinely fixed**: re-traced every `CHMIX_IDX` reference and confirmed `_emit_channel_gen`/
`_emit_noise_gen` both gate on `CHMIX_MASKS[CHMIX_IDX]`, independently re-confirmed live (see
`VR-9010`). `BL-0017` (`OVERLOAD_THRESHOLD` unreachable) is also genuinely fixed (see `VR-9020`).

Exercising **both fixes together** (the seam this review exists to check, since `VR-9010` and
`VR-9020` each verified their own package in isolation) surfaced a real inconsistency: read
`_emit_channel_gen`'s onset block in full (`music_engine.py:361-388`) and found the `ONSET_WINDOW_
COUNT` increment (feeding `IP-9020`'s `OVERLOAD_THRESHOLD` check) happens **before** the `IP-9010`
channel-mix gate — meaning a pitched channel (pulse A/B/wave) excluded by the current `CHMIX_IDX`
preset still increments the overload window every note cycle, identically to when it's included.
`_emit_noise_gen`'s equivalent code (`music_engine.py:625-630`) does the **opposite**: its own
code comment explicitly states the design intent ("no phantom onset counted for a channel that
made no sound") and the mask check runs *before* the onset-window increment, so a muted noise
channel does **not** contribute phantom onsets.

Confirmed empirically (not just by reading the asm) with a standalone PyBoy drive, same default
tempo/density (`TEMPO_IDX=4`/`DENSITY_IDX=0`) `IP-9020` itself used to establish its "peaks at 6"
baseline:

| `CHMIX_IDX` preset | Channels active | Peak `ONSET_WINDOW_COUNT` over 4000 frames |
|---|---|---|
| 0 | all 4 (pa/pb/wv/nz) | 6 |
| 3 (`0b1001`) | pa + noise only (pb/wv muted) | **6 — identical, muting pb/wv changed nothing** |
| 6 (`0b0111`) | pa/pb/wv only (noise muted) | 5 — noise's own phantom-onset exclusion visibly working |

This confirms the inconsistency is real and behaviorally meaningful, not just a code-reading
concern: **muting a pitched channel provides zero relief from overload pressure** (its silent
onsets count exactly as much as when it's audible), while muting the noise channel does reduce
the count, per its own explicit by-design exclusion. Neither `IP-9010`'s nor `IP-9020`'s package
doc considered this interaction (`IP-9010`'s own Risks section flagged the *dissonance*-scoring-
vs-mute interaction as a design question to resolve, and it was — see `BL-0029` — but never
considered the analogous overload-scoring-vs-mute interaction at all; `IP-9020`'s own empirical
threshold calibration was performed exclusively at `CHMIX_IDX=0`, so it never exercised the
partially-muted case either).

No functional defect in either package alone — each behaves exactly as its own package doc
describes — but the combination produces a real, undocumented, and internally inconsistent
behavior: the same "excluded from the mix" concept is treated as "produces no phantom activity"
for one channel type and "produces full phantom activity" for three others, with no stated reason
for the asymmetry. This is exactly the class of finding integration review exists to catch — filed
as `BL-0030`.

### Dimension 4 — Traceability coherence

- Master Build Plan, `packages/INDEX.md`, and `verification/INDEX.md` all agree: all 9 packages
  `VERIFIED`, cross-references bidirectional and consistent with the files on disk.
- `ROADMAP.md` and `docs/roadmap/` were reconciled in the previous session (commit `8ddf62c`) —
  spot-checked against the current tree and found current, not stale: rows 04/06/07/08/09 already
  reflect `IP-9010`/`IP-9020`'s (at-the-time) `COMPLETE` status. **Drift found:** those rows still
  say `COMPLETE`/"verification pending" rather than `VERIFIED` — stale as of this run's own
  `VR-9010`/`VR-9020` (written after that reconciliation). Corrected directly as part of this
  review's own output (see below), same as the original review's own "update `ROADMAP.md`'s
  reviews row" responsibility.
- `BL-0019`/`BL-0017` both show `DONE` in `docs/pipeline/backlog.md` (flipped by the pipeline
  manager in run #38/#39) — consistent with this review's own confirmation that both are
  genuinely fixed at the integration level.

### Dimension 5 — Documentation coherence

- `Claude.md`'s Known Good Behavior section already describes both fixes accurately (channel-mix
  gating, overload recalibration) — spot-checked against the shipped code, accurate.
- `memory.md`'s WRAM quick-reference already reflects `CHMIX_IDX`'s real consumer.
- No new documentation-coherence gap found beyond the `ROADMAP.md` staleness noted in Dimension 4
  (corrected, not filed as a separate backlog entry — routine drift this stage is instructed to
  fix directly).

## Findings (re-review)

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| `BL-0030` | `IP-9010` (`_emit_channel_gen` vs. `_emit_noise_gen`), `IP-9020` (`OVERLOAD_THRESHOLD`), `FR-1100`/`FR-1010` | A muted pitched channel (pulse A/B/wave, excluded via `CHMIX_MASKS`) still increments `ONSET_WINDOW_COUNT` every note cycle — identical to when included — because the count happens before `IP-9010`'s gate check in `_emit_channel_gen`. The noise channel's equivalent code deliberately excludes muted-channel phantom onsets (explicit code-comment intent), producing an internally inconsistent design within the same remediation tranche: muting pitched channels gives zero relief from overload pressure; muting noise does. `IP-9020`'s own empirical threshold calibration (default preset peaks at 6, recalibrated threshold 7) was performed exclusively at `CHMIX_IDX=0` (all channels active) and never exercised any partially-muted configuration, so the interaction was invisible to both single-package verifications. Empirically confirmed: peak onset count is identical (6) whether pulse B/wave are muted or not, at the same tempo/density. | Medium (a real, undocumented behavioral inconsistency — surprising, not a crash/data-corruption risk; both packages individually satisfy their own DoD) | `07-implementation-planning` — author a small remediation package deciding (and documenting) whether pitched-channel exclusion should also skip the onset-window increment (matching noise's behavior, and reducing overload pressure when channels are muted) or whether the current behavior is intentional and should instead be documented as a deliberate asymmetry (e.g. "the overload metric tracks total generation *work*, not audible output" — a defensible alternative reading) — either resolution is acceptable, but it must be a stated decision, not an undocumented accident, then `08-code-implementation` (if the behavior changes) → `09-package-verification` |

## Verdict (re-review)

The 9-package tranche integrates cleanly at the mechanical level (interface consistency, ROM
budget, WRAM map, module boundaries — all clean) and both of the original review's blocking
findings (`BL-0019` High, `BL-0017` Medium-High) are **confirmed genuinely remediated and
re-verified**, not merely claimed. Exercising the two remediation packages together — the exact
vantage point this review exists to provide — surfaced one new Medium finding (`BL-0030`): an
internally inconsistent, undocumented interaction between channel-mix muting and overload
counting. This is real but not release-blocking: no crash, no data corruption, no requirement
violated (neither `FR-1010` nor `FR-1100` speaks to muted-channel onset counting either way), and
both packages independently satisfy their own Definition of Done. **Recommend: this finding does
not need to block `11-release-readiness` for the current R1+R2+R3 scope** — it is a design-quality
gap suitable for a follow-up remediation package, not a defect in what either package promised to
deliver. `11-release-readiness` can proceed to make its GO/NO-GO call with this finding named as a
known, non-blocking issue.

---

## Re-review — 2026-07-25 (11-package superset, closing the `FEAT-1060` coverage gap)

- **Scope:** All 11 shipped Implementation Packages — the 9 already covered by the prior
  re-review (`IP-0001`-`IP-0007`, `IP-9010`, `IP-9020`) plus `IP-1060` (arpeggio + duty-cycle) and
  `IP-1061` (vibrato + portamento), which
  [`release-assessment-r1-r2-r3.md`](release-assessment-r1-r2-r3.md) found had never been covered
  by any integration review despite sharing code paths with `IP-9010`/`IP-9020`. This review
  supersedes both prior sections for the purposes of a consolidated release; neither prior section
  is invalidated, both are preserved above as the historical record.
- **Commit reviewed:** `36740e6`
- **Date:** 2026-07-25
- **Pre-condition check:** all 11 packages confirmed `VERIFIED` on the Master Build Plan before
  starting (`VR-0001`-`VR-0007`, `VR-1060`, `VR-1061`, `VR-9010`, `VR-9020`).
- **Result:** ✅ **Clean** — the one open finding (`BL-0030`) is unchanged/re-confirmed, not new;
  no additional Critical/High/Medium finding surfaced by exercising `IP-1060`/`IP-1061` alongside
  `IP-9010`/`IP-9020`.

### Full-suite gate

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, valid header.
- `python3 test_rom.py` → **77 PASS, 0 FAIL out of 77** (T1-T13).

### Dimension 1 — Interface consistency

The seam this review exists to check: `IP-1060`/`IP-1061` extended the same `CHANNELS`-tuple
parameterization (`duty_reg`, `arp_state`) that `IP-9010` later extended again (`dac_reg`,
`dac_on`, `bit_index`) — four packages' worth of per-channel parameters coexisting in one 15-field
tuple, unpacked at four separate call sites (`init_engine`, two loops in `engine_tick`, the final
`_emit_channel_gen`/`_emit_arpeggio_tick` emission loop). Re-read all four unpacking sites in full:
field order and count agree at every site, no positional drift (this is exactly the class of
defect that would silently swap e.g. `dac_on` for `bit_index` if any one site fell out of sync —
confirmed none did). **Clean.**

### Dimension 2 — Invariant sweep

No new WRAM addresses since the prior re-review (`IP-1060`/`IP-1061` landed before it and were
already reflected in GDS-07). ROM budget unchanged at exactly 32768 bytes. **Clean.**

### Dimension 3 — Behavioral coherence — the actual new seam, exercised live

Read `_emit_arpeggio_tick` (shared by `IP-1060`/`IP-1061`) against `_emit_channel_gen`'s `IP-9010`
gate: `arp_tick` runs **unconditionally every frame** for every arpeggiating channel (pulse A/B),
regardless of `CHMIX_MASKS`'s current mute state for that channel — it has no mask-awareness of
its own, by design (the package doc never asked for it, and `_emit_channel_gen`'s DAC-off write
already guarantees silence independent of what frequency/vibrato values `arp_tick` continues to
compute and write).

Verified this holds, not just read it, via a standalone PyBoy drive: stepped `CHMIX_IDX` to preset
4 (`0b0110` — pulse A excluded, pulse B/wave included), settled 60 frames (past pulse A's own
30-frame note cycle, satisfying the "within one note-cycle" allowance every mute/re-mute already
carries), then sampled 500 frames. Result: pulse A's `NR52` bit stayed `0` throughout (never
active) even though `ARP_STATE_PA`'s step/vibrato-phase bits kept cycling through all 4 values the
entire time (`arp_tick` never stopped computing) and `NR11`'s duty bits stayed frozen at their
last pre-mute value (the onset block's duty write is correctly skipped for a muted channel, same
gate as the frequency write). No audio leakage, no `NR52` flicker, no interaction defect — muting
a channel that also arpeggiates/vibratos behaves exactly as both packages' own documented designs
predict when read together, now actually confirmed together for the first time.

This closes `BL-0031` — the coverage gap the release assessment found — with a genuinely clean
result, not an assumed one.

### Dimension 4 — Traceability coherence

Master Build Plan, `packages/INDEX.md`, `verification/INDEX.md`: all 11 packages `VERIFIED`,
cross-references bidirectional. `FEAT-1060` (Feature Catalog) now traces to an integration review
for the first time — closing the exact gap `release-assessment-r1-r2-r3.md` named. `ROADMAP.md`
already reflects the current 11-package `VERIFIED` state (updated in the prior run). **Clean.**

### Dimension 5 — Documentation coherence

`Claude.md`/`memory.md` already describe arpeggio/vibrato/duty-cycle and channel-mix gating
accurately (both were updated by their own implementing packages); no new gap found by reviewing
them against this expanded scope. **Clean.**

## Findings (11-package re-review)

No new findings. `BL-0030` (filed by the prior 9-package re-review) remains open and unchanged —
it does not involve `IP-1060`/`IP-1061` and this review's own dedicated check of the
`IP-1060`/`IP-1061` × `IP-9010` seam found no analogous or additional issue.

## Verdict (11-package re-review)

The full 11-package tranche integrates cleanly, including the one seam
(`FEAT-1060` × channel-mix gating) that had never been exercised together before. `BL-0031` (the
coverage gap) is closed. The only standing finding across the entire tree remains `BL-0030`
(Medium, non-blocking, unrelated to this review's new scope). **Recommend: `11-release-readiness`
can now be re-run with a complete evidence chain — every dimension this consolidated release's own
assessment needs is now on file.**

---

## Re-review — 2026-07-25 (12-package scope, +`IP-1070`)

- **Scope:** All 12 shipped Implementation Packages — the 11 already covered by the prior
  re-review plus `IP-1070` (combinable generation schemes, `BL-0020`), `VERIFIED` this session
  ([VR-1070](../implementation/verification/VR-1070-combinable-generation-schemes.md)).
- **Commit reviewed:** `0fb7d0b`
- **Date:** 2026-07-25
- **Pre-condition check:** all 12 packages confirmed `VERIFIED` on the Master Build Plan before
  starting.
- **Result:** ⚠️ **1 new finding (Low)** — a real, plausible interaction (channel-mix muting +
  Scheme E on the same channel) that no shipped preset or test exercises, though the code was
  read and confirmed safe by construction. No Critical/High/Medium new finding. `BL-0030` and
  `BL-0032` (both filed by prior single-package/re-review passes) remain open, unchanged by this
  review's own new scope.

### Full-suite gate

- `python3 build_rom.py Driftune.gbc` → 32768 bytes, valid header.
- `python3 test_rom.py` → **85 PASS, 0 FAIL out of 85** (T1-T14).

### Dimension 1 — Interface consistency

`IP-1070` extended the same `CHANNELS` tuple `IP-9010`/`IP-1060`/`IP-1061` each already extended
in turn — now 17 fields, unpacked at 4 separate call sites. Re-read all four sites in full:
field order and count agree everywhere, no positional drift (confirmed the same way the prior
9-package re-review confirmed `IP-9010`'s own extension). **Clean.**

### Dimension 2 — Invariant sweep

ROM budget unchanged at exactly 32768 bytes (`MOTIF_TABLE`, 8 bytes, well within headroom). WRAM
map: `MOTIF_STEP_PA`/`PB`/`WV` (`0xC038`-`0xC03A`) confirmed documented in GDS-07 and genuinely
free against the reserved `0xC020`-`0xC037` ring-buffer range — no collision. No module took on a
second job (Scheme E lives entirely inside `_emit_channel_gen`'s existing note-selection step, no
new module). **Clean.**

### Dimension 3 — Behavioral coherence — one new finding

Traced `IP-1070`'s actual interaction with `IP-9010` (channel-mix muting) by reading the code:
both schemes converge at a shared `gt_delta_ready_{suffix}` label (`music_engine.py:429`) *before*
the dissonant/stuck override, the onset-window count, and `IP-9010`'s own mute-check
(`music_engine.py:477-500`) — the mute gate is scheme-agnostic by construction, applying
identically whichever scheme produced the degree change. This is provably safe by inspection.

However: attempted to independently *exercise* this combination live (a channel both muted via
`CHMIX_MASKS` and assigned Scheme E) and found **no shipped preset produces it** — preset 6 (the
only preset with any scheme-select bit set) keeps the wave channel active, not muted. Attempted to
poke the `CHMIX_MASKS` ROM data directly via PyBoy to construct the combination for a live test;
confirmed ROM writes are rejected by the emulator (matching real hardware — cart ROM is read-only
from the CPU's perspective), so this combination cannot be exercised without a code/data change,
which is outside this review's read-only scope. Filed as a Low finding (code-reasoned-safe, but
genuinely zero live/test coverage) — related to, but distinct from, `BL-0032` (which is about
Scheme E being reachable at all for pulse A/B, not about the mute+Scheme-E interaction
specifically).

Also re-confirmed (via `VR-1070`'s own live drive, re-read not re-run) that bad-zone detection/
recovery applies identically with a Scheme-E channel active, and that `IP-1060`/`IP-1061`'s
arpeggio/vibrato/duty-cycle continue computing harmlessly on a channel that switches between
Scheme W and Scheme E (neither arpeggio/vibrato nor Scheme E's own state has any dependency on
the other — both simply read/write `CUR_DEGREE_*`/frequency registers through the same shared
onset-write path).

### Dimension 4 — Traceability coherence

Master Build Plan, `packages/INDEX.md`, `verification/INDEX.md` all agree: all 12 packages
`VERIFIED`. **Drift found:** `ROADMAP.md`'s stage-08/09 rows still said "`IP-1070` `COMPLETE`,
verification pending" / "11/11 packages" — stale as of this run's own `VR-1070` (written after
those rows were last touched). Corrected directly as part of this review's own output (routine
drift this stage is instructed to fix, not report).

### Dimension 5 — Documentation coherence

`Claude.md`/`memory.md`/GDS-07 already describe `IP-1070` accurately (updated by its own
implementing commit) — spot-checked, accurate. No new gap.

## Findings (12-package re-review)

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| (new) | `IP-1070`, `IP-9010` | A pitched channel that is both `CHMIX`-muted and assigned Scheme E is provably safe by code inspection (the mute gate is scheme-agnostic, applied after both schemes converge) but is exercised by **no shipped preset and no test** — `CHMIX_MASKS`'s only scheme-assigning preset (6) keeps its Scheme-E channel active. Confirmed this combination cannot be constructed live without a data/code change (ROM writes are correctly rejected by the emulator, matching real hardware). | Low (reasoned-safe by construction, zero functional risk identified; a test-coverage gap, not a defect) | 04/07 (whenever `BL-0032`'s own follow-up preset-data package is picked up, include at least one preset that combines a mute with a Scheme-E assignment, closing both gaps in one pass) |

## Verdict (12-package re-review)

The full 12-package tranche integrates cleanly. `IP-1070`'s interaction with every other shipped
package (channel-mix gating, arpeggio/vibrato/duty-cycle, bad-zone detection/recovery) is correct
by construction and confirmed correct wherever a shipped preset actually exercises it. The one gap
found — mute+Scheme-E combination, untested because no preset currently constructs it — is a data
coverage gap, not a functional defect, and is naturally closed by the same follow-up `BL-0032`
already recommends. No Critical/High/Medium finding. **Recommend: this review does not block any
future `11-release-readiness` call touching R4 scope.**

---

## Re-review — 2026-07-26 (13-package scope, +`IP-1080`)

- **Scope:** All 13 Foundation/R1-R5 Implementation Packages — `IP-0001`-`IP-0007` + `IP-1060` +
  `IP-1061` + `IP-9010` + `IP-9020` + `IP-1070` + `IP-1080`.
- **Commit reviewed:** `e00be3f`
- **Pre-condition check:** every package in scope confirmed `VERIFIED` on the Master Build Plan
  before this review began (`IP-1080` → [`VR-1080`](../implementation/verification/VR-1080-genre-aware-style-presets.md), independently verified via a dispatched fresh-session `Agent`, merged as commit `dffdb0b`).

### Full-suite gate (run against the reviewed commit)

```
python3 build_rom.py Driftune.gbc   # 32768 bytes
python3 test_rom.py                 # 93 PASS, 0 FAIL out of 93 (T1-T15)
```

ROM budget independently re-measured (`rom.pos` instrumentation, `ADR-0002`'s own method):
3497/32768 bytes used, 29271 free.

### Dimension 1 — Interface consistency

`IP-1080` adds a genuinely new seam: a second, parallel data table (`STYLE_TABLE`) keyed by the
same `CHMIX_IDX` index `CHMIX_MASKS` (`IP-9010`/`IP-1070`) already uses. Traced both tables' own
read sites end to end: `CHMIX_MASKS[CHMIX_IDX]` is read by `_emit_channel_gen`/`_emit_noise_gen`
(channel-activity + scheme-select, unchanged by this package); `STYLE_TABLE[CHMIX_IDX]` is read
only by the new `_emit_apply_style`, called once from `input_map.py`'s Start-press handler. No
code path reads both tables in a way that assumes a shared layout or a coupled index meaning —
confirmed by grep, the two tables' emission labels (`chmix_masks_table`, `style_table`) and read
sites never appear in the same function. The `CHANNELS`-tuple's 4 unpacking call sites (unchanged
by `IP-1080` — it touches no `CHANNELS` field) were re-checked for positional drift: still
consistent, 17 fields at every site.

### Dimension 2 — Invariant sweep

- **ROM budget:** exactly 32768 bytes; `STYLE_TABLE` (32 bytes) fits the measured headroom with
  room to spare (29271 free).
- **WRAM map:** `DUTY_BIAS` (`0xC03B`) confirmed present in GDS-07 §3 and `memory.md`, correctly
  placed in the genuine unused headroom between `IP-1070`'s `MOTIF_STEP_WV` (`0xC03A`) and
  `JOY_PREV` (`0xC050`) — no collision with the `BL-0013` reserved-but-unused ring-buffer range.
- **No module took on a second job:** `input_map.py` still only ever writes the parameter indices
  its own docstring commits to (`TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`,
  now also `DUTY_BIAS` via the new call — still a parameter index, not a PSG register, consistent
  with the module's own charter); it still never writes a PSG register directly.
- **APU/VBlank timing:** unaffected — `IP-1080` adds no new per-frame generation-tick work beyond
  a bounded 4-byte table read on a Start press; no visualizer/VRAM change at all.

### Dimension 3 — Behavioral coherence

Exercised the two genuinely new cross-package combinations live, not just read from code:

- **Style + channel-mix mute (`IP-1080` × `IP-9010`):** drove `CHMIX_IDX` to preset 3 (Holiday
  style, `CHMIX_MASKS[3]` = pulse A + noise active, pulse B/wave muted). Confirmed
  `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/`DUTY_BIAS` = Holiday's exact row (3, 3, 0, 1) **and**
  `NR52` settled to `0b1001` in its low nibble (pulse A + noise active, pulse B/wave inactive) —
  both mechanisms apply correctly and independently at the same preset, as `ADS-101` §2's "two
  tables stay independent" design predicts.
- **Style + Scheme E (`IP-1080` × `IP-1070`):** drove `CHMIX_IDX` to preset 6 (`IP-1070`'s own
  Scheme-E preset, wave channel on Scheme E). Confirmed `STYLE_TABLE[6]` (an unassigned index,
  copies the default row: 4, 0, 0, 0) applies correctly **and** the wave channel's Euclidean-step
  field (`MOTIF_STEP_WV` bits0-3) still cycles through all 16 positions over a 1500-frame drive —
  Scheme E is unaffected by the style mechanism landing on the same preset.
- **Finding surfaced by this exercise:** no shipped preset currently combines a *named*
  (non-default) style with Scheme E — `STYLE_TABLE`'s 3 named rows (indices 1-3) all sit at
  `CHMIX_IDX` values whose `CHMIX_MASKS` entry has no scheme-select bit set, and `IP-1070`'s own
  scheme-assigning preset (6) carries `STYLE_TABLE`'s unassigned/default row. Both mechanisms are
  confirmed independently correct (above), but this specific combination is untested and
  unreachable via any shipped preset — the same "mechanism supports combination, data doesn't yet
  exercise it" pattern `BL-0032`/`BL-0033` already found for Scheme E + channel-mix.

### Dimension 4 — Traceability coherence

`ROADMAP.md`, `docs/features/INDEX.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/verification/INDEX.md`, and the Master Build Plan all agree: 13/13 packages
`VERIFIED`, `IP-1080` cross-linked to `FS-108`/`VR-1080` bidirectionally. No stale row found this
pass (the routine drift a prior re-review sometimes found had already been corrected in the same
run that shipped each package, per the pattern established since run #51).

### Dimension 5 — Documentation coherence

`Claude.md` (new dev-guide subsection, test count 93/T1-T15, Known Good Behavior bullet),
`memory.md` (`DUTY_BIAS` WRAM row), and GDS-07 (`DUTY_BIAS` row) all confirmed accurate — spot-
checked against the shipped code, no gap.

## Findings (13-package re-review)

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| (new) | `IP-1080`, `IP-1070` | No shipped `CHMIX_IDX` preset combines a named (non-default) style (`STYLE_TABLE` indices 1-3) with Scheme E (`CHMIX_MASKS`'s only scheme-assigning preset, 6) — both mechanisms independently confirmed correct by this review's own live drive, but the combination itself is untested and unreachable via shipped data. Same pattern as `BL-0032`/`BL-0033`. | Low (both mechanisms individually correct and verified; a data/test-coverage gap, not a functional defect) | 05/07 (fold into `BL-0032`'s eventual follow-up preset-data package — or a new, related entry — so one future pass assigns a preset that combines a named style, a channel mute, *and* a Scheme-E assignment, closing all three coverage gaps at once) |
| (carried forward, non-blocking) | `IP-1080` | `BL-0040` — `FS-108`'s acceptance criterion (4) states the bad-zone-independence invariant in absolute terms; `VR-1080`'s own broader stress sweep found a ≈16% same-frame-collision rate from unrelated channel activity (not a code defect). Already filed, routed to `04-requirements-engineering`. | Medium (requirements-wording precision only; no functional risk) | 04 (already `SCHEDULED` via `BL-0040`, listed here for this scope's own completeness, not a new finding) |

## Verdict (13-package re-review)

The full 13-package tranche integrates cleanly. `IP-1080`'s two genuinely new cross-package
combinations (style + channel-mix mute, style + Scheme E) were both exercised live and confirmed
correct — `ADS-101`'s "two tables stay independent" design holds exactly as specified. One new
Low finding (named style + Scheme E combination untested, same data-coverage pattern as
`BL-0032`/`BL-0033`) and one already-filed Medium requirements-wording finding (`BL-0040`,
non-blocking). No Critical/High finding anywhere. **Recommend: this review does not block any
future `11-release-readiness` call touching R5 scope.**
