# Feature Catalog — v1 (Foundation release bucket)

- **Owned by:** `05-feature-decomposition` · **Status:** ✅ Authored, 2026-07-21
- **Release bucket:** "Foundation" — the first playable slice: engine + input + bad-zone + a
  minimal visualizer, all headlessly verified. Everything below is one release bucket; there is
  no epic/phase split yet at this project's size.
- **Release status: ✅ SHIPPED — GO confirmed 2026-07-25 (R1-R4); GO confirmed 2026-07-26 (R5
  addition); GO confirmed 2026-07-26 (`IP-1090`/`BL-0010` addition).** Every feature `FEAT-1000`
  through **`FEAT-1110`** is `VERIFIED` and integration-reviewed as part of the consolidated
  R1 (Foundation) + R2 (Sound Design) + R3 (Integrity Remediation) + R4 (Multi-Scheme Foundation)
  + R5 (Genre-Aware Style Presets) + Motif Recurrence via Weighted Variant Selection release — see
  [`docs/reviews/release-assessment-r1-r2-r3.md`](../reviews/release-assessment-r1-r2-r3.md)
  (R4 addition confirmed via that document's second re-assessment section; R5 addition confirmed
  via its third; `IP-1090`/`BL-0010` addition confirmed via its fourth). **`FEAT-1100` (added
  2026-07-26, roadmap R6/`ADS-103`) is `VERIFIED` (`IP-1100`/`VR-1100`) but not yet part of the
  shipped baseline** — awaits its own `11-release-readiness` G4 GO. **`FEAT-1110` (added
  2026-07-26, `BL-0051`/`ADS-104`) is `VERIFIED` (`IP-1110`/`VR-1110`) but not yet part of the
  shipped baseline** — awaits its own `11-release-readiness` G4 GO.

| ID | Feature | Summary | FR/NFR traced |
|---|---|---|---|
| FEAT-1000 | Core generation engine | Real-time per-channel note generation (scale-constrained walk for pulse A/B/wave, Euclidean-gated noise hits), preset tables, PSG register writes | FR-1000, FR-1010, NFR-1030 |
| FEAT-1010 | Input steering | Joypad edge detection + the 6-control parameter mapping (GDS-03 §3) | FR-1020...FR-1060 |
| FEAT-1020 | Reset-to-preset | Select-triggered full reinitialization | FR-1070 |
| FEAT-1030 | Bad-zone detection | Dissonance/stale/overload scoring + combined flag | FR-1080...FR-1110 |
| FEAT-1040 | Minimal visualizer | Tile/palette animation reacting to tempo + per-channel activity + bad-zone flag | FR-1120 |
| FEAT-1050 | Headless verification suite | PyBoy-driven button-sequence tests asserting on sound registers/WRAM state for every feature above | NFR-1010, NFR-1020 |
| FEAT-1060 | Sound design techniques | Arpeggio (chord-implying frequency cycling), vibrato (periodic pitch modulation), portamento (multi-frame pitch glide), duty-cycle variation — layered onto `FEAT-1000`'s existing per-channel generation, no new input control | FR-1130...FR-1170, NFR-1040, NFR-1050 |
| FEAT-1070 | Combinable generation schemes | A second per-channel note-selection strategy (Scheme E — Euclidean-gated onset timing + fixed-motif pitch selection) alongside the shipped Scheme W (LFSR walk), selectable per pitched channel via spare bits in the existing `CHMIX_IDX`/`CHMIX_MASKS` preset space — no new input control. `BL-0020`'s "solo or in combination" ask is satisfied at the ensemble level (different channels running different schemes), not by blending within one channel. First feature of `docs/roadmap/04-release-roadmap.md`'s **R4 — Multi-Scheme Foundation** | FR-1180...FR-1220, NFR-1060, NFR-1070 |
| FEAT-1080 | Genre-aware style presets | A new, parallel `STYLE_TABLE` keyed by the existing `CHMIX_IDX` preset index (Start), each row a coordinated target combination (tempo/density/scale/duty-cycle bias) applied immediately on preset change — 3 concrete v1 styles (Techno/Chiptune-Driving, Ambient/Lo-Fi, Holiday). No new input control; no new generation mechanism (`_emit_channel_gen`/`_emit_noise_gen`/`_emit_badzone_tick` all unmodified — only which values `TEMPO_IDX` etc. hold changes). First feature of `docs/roadmap/04-release-roadmap.md`'s **R5 — Genre-Aware Style Presets** | FR-1230...FR-1260, NFR-1080, NFR-1090 |
| FEAT-1090 | Motif recurrence via weighted variant selection | Extends `FEAT-1070`'s Scheme-E `MOTIF_TABLE` from a single fixed 8-step sequence to a small fixed set of pre-composed motif variants; at each motif-cycle boundary (step wraps 7→0), a weighted lookup table (retention-biased, reusing the `DELTA_TABLE`-style weighting idiom) autonomously selects the variant for the next cycle. No new input control, no L-system derivation engine — closes `BL-0010`'s motif-recurrence half. Spec: [`FS-109`](../features/fs-109-motif-recurrence-via-weighted-variant-selection.md) (authored 2026-07-26). | FR-1270...FR-1300, NFR-1100, NFR-1110 |
| FEAT-1100 | Song-form via autonomous phase cycling | A new, independent state machine (`SONG_STATE`/`SONG_STATE_TIMER`) autonomously cycling 4 named phases (intro/build/peak/breakdown, looping); each phase transition overwrites `TEMPO_IDX`/`DENSITY_IDX` to that phase's target values, same tick. No new input control; bad-zone detection/recovery and Scheme-E motif-variant selection are unaffected (disjoint WRAM fields, `ADS-103` §2). Closes roadmap R6/`BL-0010`'s song-form half. Spec: [`FS-110`](../features/fs-110-song-form-via-autonomous-phase-cycling.md) (authored 2026-07-26). | FR-1310...FR-1340, NFR-1120, NFR-1130 |
| FEAT-1110 | Settings & control visibility | Extends `FEAT-1040`'s minimal visualizer with 5 new bar-height indicator tiles, one per base control (`TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`), each a filled-bar-height glyph (0-7 rows) proportional to that parameter's current index, updated the same frame the parameter changes. Reuses the existing BG palette — no new palette, no font/text rendering. Purely additive: existing channel-activity tiles and calm/bad-zone palette swap are unchanged. Read-only (`visuals.py` still never writes engine state, GDS-03 §1). Closes the base-control half of `BL-0051`'s visualizer request; the newer per-feature reactive signals (scheme/style/motif-variant/song-form-phase) are explicitly out of scope, deferred to a v1.1+ using the same reusable bar-tile mechanism (`ADS-104` §9). Spec: [`FS-111`](../features/fs-111-settings-and-control-visibility.md) (authored 2026-07-26). | FR-1350...FR-1380, NFR-1140...NFR-1160 |

## Dependency graph (Foundation bucket, `FEAT-1000`...`FEAT-1050`)

`FEAT-1000` is the foundation every other feature reads from or writes into; `FEAT-1010` writes
its parameter indices; `FEAT-1020` resets its state and `FEAT-1010`'s indices together;
`FEAT-1030` reads its per-channel note events; `FEAT-1040` reads its state read-only; `FEAT-1050`
exercises all of the above. Build order: `FEAT-1000` -> (`FEAT-1010`, `FEAT-1030` can proceed in
parallel once `FEAT-1000`'s note-event hook exists) -> `FEAT-1020` (needs both) -> `FEAT-1040` ->
`FEAT-1050` alongside every feature (tests are written per-package, not only at the end).

`FEAT-1060` (added 2026-07-22, `BL-0024`) depends on `FEAT-1000` (extends `_emit_channel_gen`,
the existing per-channel generation routine) and must not regress `FEAT-1030` (bad-zone scoring
continues to read scale-degree state, not instantaneous modulated frequency — FR-1140 makes this
explicit) or `FEAT-1050` (every new behavior needs its own headless test coverage, same
convention as every prior feature).

`FEAT-1070` (added 2026-07-25, `BL-0020`/`ADS-100`) depends on `FEAT-1000` (extends
`_emit_channel_gen`'s note-selection step, same seam `FEAT-1060` already touches) and, critically,
on the shipped `IP-9010` (`CHMIX_MASKS`, delivered as part of `FEAT-1030`'s remediation tranche —
`BL-0019`), since it rides that table's spare bits per `ADR-0001`. Must not regress `FEAT-1030`
(`FR-1220` makes bad-zone scheme-agnosticism explicit) or `FEAT-1050` (new headless coverage
required, same convention). No dependency on `FEAT-1060` — the two features touch adjacent code
(the same `_emit_channel_gen`/`CHANNELS` seam) but are functionally independent; sequencing them
in either order is safe, per `07-implementation-planning`'s own eventual call.

`FEAT-1080` (added 2026-07-26, roadmap R5/`ADS-101`) depends on `FEAT-1000` (reads/overwrites
`TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`, all `FEAT-1000`-owned state) and `FEAT-1010` (reuses
`CHMIX_IDX`, the same Start-stepped index `FEAT-1010`'s input mapping already owns — `STYLE_TABLE`
is read alongside `CHMIX_MASKS`, not a modification to `FEAT-1010`'s own input-handling code).
Must not regress `FEAT-1030` (bad-zone thresholds are unaffected by style-driven parameter
overwrites — no FR claims otherwise, and none of `FEAT-1030`'s own FRs reference `STYLE_TABLE`) or
`FEAT-1050` (new headless coverage required for `FR-1250`'s audible-distinctness claim, same
convention). No dependency on `FEAT-1060`/`FEAT-1070` — `FEAT-1080` reads a sibling table keyed by
the same `CHMIX_IDX` index those features' `CHMIX_MASKS`/scheme-select machinery already uses, but
touches none of their own code paths (`ADS-101` §2 keeps the two tables independent); sequencing
relative to either is unconstrained.

`FEAT-1090` (added 2026-07-26, `BL-0010`/`ADS-102`) depends directly on `FEAT-1070` — it extends
`FEAT-1070`'s own shipped `MOTIF_TABLE`/motif-step mechanism (Scheme E's pitch-selection half),
rather than adding an independent one; `FEAT-1070` must be `VERIFIED` first (it already is).
Must not regress `FEAT-1030` (bad-zone detection/recovery is unaffected — `ADS-102` §8 explicitly
notes motif-variant selection keeps ticking every frame the same scheme/style-agnostic way other
per-frame state already does) or `FEAT-1050` (new headless coverage required for `FR-1300`'s
no-regression claim and `FR-1280`/`FR-1290`'s selection-behavior claims, same convention). No
dependency on `FEAT-1080` — `FEAT-1090` touches `_emit_channel_gen`'s Scheme-E motif-lookup code
directly, `FEAT-1080` touches the sibling `STYLE_TABLE`/`_emit_apply_style` path; `ADS-102` §8
flags the *interaction* (a style change landing mid-cycle relative to a motif-variant boundary) as
a risk to verify, not a code dependency — sequencing relative to `FEAT-1080` is unconstrained, but
`09-package-verification`/`10-integration-review` should exercise the combination once both are
implemented, per that flagged risk.

`FEAT-1110` (added 2026-07-26, `BL-0051`/`ADS-104`) depends on `FEAT-1040` (it extends the
existing minimal visualizer's `update_visuals` call site, adding a new tilemap-write routine
alongside its existing channel-activity/bad-zone-palette writes) and reads `FEAT-1000`/`FEAT-1010`
(`TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`)/`FEAT-1070` (`CHMIX_IDX`) state read-only —
the same "visualizer never writes engine state" pattern `FEAT-1040` itself already established
(GDS-03 §1, unchanged). **No dependency on `FEAT-1080`/`FEAT-1090`/`FEAT-1100`** despite `ADS-104`
naming their reactive signals (style identity, motif-variant, song-form phase) as deferred v1.1+
follow-on indicators using the same bar-tile mechanism — this feature's v1 scope covers only the
5 base-control parameters (`TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`), all
already owned by `FEAT-1000`/`FEAT-1010`/`FEAT-1070`; no code path this feature touches reads
`STYLE_TABLE`'s implicit style identity, `MOTIF_VARIANT_IDX`, or `SONG_STATE`. Must not regress
`FEAT-1050` (new headless coverage required for `FR-1380`'s live-reflects-a-button-press
acceptance criterion, same convention as every prior feature).

`FEAT-1100` (added 2026-07-26, roadmap R6/`ADS-103`) depends on `FEAT-1000` (reads/overwrites
`TEMPO_IDX`/`DENSITY_IDX`, the same `FEAT-1000`-owned state `FEAT-1080` also overwrites). Must not
regress `FEAT-1030` (bad-zone detection/recovery — `ADS-103` §2 confirms the two mechanisms drive
genuinely disjoint WRAM fields: bad-zone biases `CUR_DEGREE_*` deltas only, song-form biases
`TEMPO_IDX`/`DENSITY_IDX` only, so no code-level conflict exists) or `FEAT-1090` (Scheme-E
motif-variant selection — also confirmed disjoint, `ADS-103` §2). **No dependency on `FEAT-1080`**
— the two features write the same two WRAM fields via different, independent triggers (Start
press vs. an autonomous per-frame timer); this is the same "last write wins, no special-casing
needed" contract `FEAT-1080`'s own `FR-1240` already established for the D-pad/B handlers, not a
new interaction to design around — but `ADS-103` §8 flags it for `09-package-verification`/
`10-integration-review` to exercise once both are implemented (a Start press landing on the same
frame as a phase transition), the same "reasoned safe, verify anyway" discipline `FEAT-1090`'s own
`FEAT-1080` interaction already followed. Must not regress `FEAT-1050` (new headless coverage
required for the long-run cyclic-order demonstration, `FR-1340`).

## Feature Review

No structural conflicts found; every FR/NFR from `docs/requirements/01-functional-requirements.md`
maps to exactly one feature above. No feature is undersized/oversized enough to need further
splitting for a first implementation pass.

**2026-07-22 update:** `FEAT-1060` reviewed against the existing catalog — no conflict with
`FEAT-1000`/`FEAT-1030`/`FEAT-1040`'s existing FR coverage; right-sized for one-or-two
implementation packages (per `07-implementation-planning`'s own sizing call), not requiring
further splitting at this stage.

**2026-07-25 update:** `FEAT-1070` reviewed against the existing catalog — no conflict, no
requirement double-assigned (`FR-1180`-`FR-1220`/`NFR-1060`/`1070` traced to exactly this one
feature, confirmed against `docs/requirements/01-functional-requirements.md`'s full FR/NFR
inventory). Right-sized for a single implementation package (Scheme E's onset-timing and
pitch-selection halves are tightly coupled — both live in the same note-selection branch of
`_emit_channel_gen` — splitting them the way `FEAT-1060` split into `IP-1060`/`IP-1061` would be
artificial here, since neither half is independently useful or independently testable without the
other; a sizing call `07-implementation-planning` should confirm, not override, when it plans
this). No architectural inconsistency: the design (`ADS-100`) was already synthesized against the
shipped module boundaries (GDS-03), not invented at this stage.

**2026-07-26 update:** `FEAT-1080` reviewed against the existing catalog — no conflict, no
requirement double-assigned (`FR-1230`-`FR-1260`/`NFR-1080`/`1090` traced to exactly this one
feature, confirmed against the full FR/NFR inventory). Right-sized for a single implementation
package (the `STYLE_TABLE` data table, its read-and-apply routine, and the 3 v1 style rows are
one cohesive unit — no natural split point the way `FEAT-1060` split arpeggio/vibrato-portamento
into two packages; `07-implementation-planning`'s own sizing call should confirm, not override).
No architectural inconsistency: `ADS-101` was synthesized against the shipped module boundaries
and the already-shipped `CHMIX_IDX`/`CHMIX_MASKS` mechanism, not inventing a new one. No
dependency-graph conflict: `FEAT-1080`'s independence from `FEAT-1060`/`FEAT-1070` (both share the
`CHMIX_IDX` index but touch disjoint tables/code paths) was checked directly against
`ADS-101` §2's own "two tables stay independent" statement, not assumed.

**2026-07-26 update:** `FEAT-1090` reviewed against the existing catalog — no conflict, no
requirement double-assigned (`FR-1270`-`FR-1300`/`NFR-1100`/`1110` traced to exactly this one
feature, confirmed against the full FR/NFR inventory). Unlike every prior feature this session,
`FEAT-1090` genuinely **depends on** an existing feature's code (`FEAT-1070`'s `MOTIF_TABLE`
mechanism) rather than merely reading sibling state — checked explicitly and recorded as a real
dependency-graph edge, not the "independent, shared index only" pattern `FEAT-1080` established.
Right-sized for a single implementation package (variant-table extension, cycle-boundary
detection, and weighted selection are one tightly coupled unit inside `_emit_channel_gen`'s
existing Scheme-E branch — no natural split point). No architectural inconsistency: `ADS-102` was
synthesized directly against `IP-1070`'s shipped `MOTIF_TABLE`/motif-step mechanism, extending it
rather than inventing a parallel one. One item flagged for `07-implementation-planning`'s
attention, not a catalog defect: `ADS-102` §8's own noted risk (a style change, `FEAT-1080`,
landing mid-cycle relative to a motif-variant boundary) has no dedicated FR of its own — correctly
so, since both `FR-1240` (style applies immediately) and this feature's own FRs already fully
describe each mechanism's independent behavior; the interaction itself is a verification-time
concern (`09`/`10`), not a missing requirement.

**2026-07-26 update:** `FEAT-1100` reviewed against the existing catalog — no conflict, no
requirement double-assigned (`FR-1310`-`FR-1340`/`NFR-1120`/`1130` traced to exactly this one
feature, confirmed against the full FR/NFR inventory). Right-sized for a single implementation
package (the phase table, the countdown-and-transition tick, and the coordinated overwrite are
one tightly coupled unit — no natural split point). No architectural inconsistency: `ADS-103` was
synthesized directly against the shipped WRAM map and `_emit_badzone_tick`'s own existing
countdown-tick shape, extending neither, inventing a new sibling tick instead. Checked explicitly
for the same "two writers, one field" pattern `FEAT-1080`/`FEAT-1090`'s own reviews already
established a discipline for: `FEAT-1100` and `FEAT-1080` both write `TEMPO_IDX`/`DENSITY_IDX` via
independent triggers, correctly not treated as a conflict (same "last write wins" contract), but
flagged for `09`/`10` verification per `ADS-103` §8, mirroring exactly how `FEAT-1090`'s own
`FEAT-1080` interaction was handled — consistent precedent, not a new judgment call.

**2026-07-26 update:** `FEAT-1110` reviewed against the existing catalog — no conflict, no
requirement double-assigned (`FR-1350`-`FR-1380`/`NFR-1140`-`NFR-1160` traced to exactly this one
feature, confirmed against the full FR/NFR inventory). Right-sized for a single implementation
package (a new tile-pattern set + one new per-frame tilemap-update routine is one cohesive unit —
no natural split point). No architectural inconsistency: `ADS-104` was synthesized directly
against `FEAT-1040`'s shipped `update_visuals` call site and GDS-03 §1's read-only invariant,
extending neither by writing engine state. Checked explicitly for a dependency-graph conflict
against `FEAT-1080`/`FEAT-1090`/`FEAT-1100` (all three add state this feature's parent `ADS-104`
names as future reactive-signal candidates) — confirmed no dependency exists in v1's actual scope
(only the 5 pre-existing base-control fields are read), consistent with `ADS-104` §4/§7's own
explicit v1-scope boundary; the four-way unification is a documented future extension (`ADS-104`
§9), not a hidden dependency incurred now.
