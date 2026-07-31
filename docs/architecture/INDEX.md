# Architecture & Design Synthesis — Index

Owned by `03-architecture-design-synthesis` (GDS-01...10, ADS, ADRs) and `01-vision` (GDS-00 +
strategic assumptions register). See `.claude/skills/README.md` for the pipeline.

The ladder is authored level by level as the pipeline actually reaches it. **This was originally
a from-scratch increment with no shipped ROM**, and GDS-00/01/03/07 were synthesized forward on
that basis. That is no longer the situation: a ROM has shipped and 16 packages are `VERIFIED`, so
the levels authored from 2026-07-26 onward (GDS-02, GDS-04, and those still to come) are written
**against the real system as-built and measured**, not forward from intention. Each such level
says so in its own §0.

[↑ Docs index](../INDEX.md)

## §1 — The global ladder (GDS-00...GDS-10)

| Level | Title | File | Status |
|---|---|---|---|
| GDS-00 | Vision | [00-vision.md](00-vision.md) | ✅ Authored 2026-07-21; amended 2026-07-22 (v1.1 drift fix); amended 2026-07-22 (v1.2 — cart-shape/save reopened, not decided); amended 2026-07-22 (v1.3 — research-to-code traceability goal, C10); amended 2026-07-22 (v1.4 — §9 research findings cycled in) |
| GDS-01 | Concept of Interaction | [01-concept-of-play.md](01-concept-of-play.md) | ✅ Authored 2026-07-21 |
| GDS-02 | System Context | [02-system-context.md](02-system-context.md) | ✅ Authored 2026-07-26 — the first ladder level authored against a real, shipped system rather than synthesized forward (its §0 records that late-authoring deviation honestly). Describes the as-built artifact/build-chain/verification-harness context, the six external constraint ceilings, and — newly named here, nowhere else in the tree — the fact that Driftune has **never been run on physical GBC hardware**. Three Open Questions routed (hardware validation, `BL-0023`'s absent dependency manifest, `BL-0015`'s uncharacterized PyBoy timing semantics) |
| GDS-03 | Architecture (module layout, main loop, input->parameter mapping, bad-zone metric) | [03-architecture.md](03-architecture.md) | ✅ Authored 2026-07-21 (SS1-5; SS6 lists what's still open); reconciled 2026-07-22 against shipped `IP-0004`/`IP-0007` (`BL-0013`, `BL-0017` root-cause note) |
| GDS-04 | Domain Model | [04-domain-model.md](04-domain-model.md) | ✅ Authored 2026-07-26 — the engine's entity set as actually shipped (read out of `music_engine.py`, not inferred). Three statements exist here and nowhere else in the tree: the **steering-index family** and its writer analysis (`TEMPO_IDX`/`DENSITY_IDX` each have three independent writers under a verified last-write-wins contract), the **index-0 invariant** as one cross-cutting rule rather than four per-table requirements, and the **one-frame-stale bad-zone read**. Four Open Questions routed |
| GDS-05 | Functional Requirements | 05-functional-requirements.md | ⛔ **Deliberately not owed** — superseded by the direct `04-requirements-engineering` pass; `FR-1000`...`FR-1380` cover the shipped capability set at leaf grain, and reverse-engineering a capability summary out of a clean leaf baseline would produce a second thing to keep in sync. Rationale recorded in [GDS-06 §0](06-non-functional-requirements.md) |
| GDS-06 | Non-functional Requirements | [06-non-functional-requirements.md](06-non-functional-requirements.md) | ✅ Authored 2026-07-26 — §0 answers the question no document previously did (how a ladder-level NFR differs from an `NFR-xxxx`: discipline/rationale/breach-posture vs. testable leaf statement). Covers ROM budget, timing discipline, save integrity (**explicitly empty** — nothing is persisted), build determinism, test-coverage bar. **§2.2 records that `R101`'s own stated cycle-tallying revisit trigger appears to have fired**: `IP-1110`'s reproducible Select-frame VRAM-write drop is evidence the per-frame budget is tighter than the never-measured "generous budget" posture assumed. Four Open Questions routed |
| GDS-07 | Data Model (WRAM map) | [07-data-model.md](07-data-model.md) | ✅ Authored 2026-07-21; extended 2026-07-22 with 6 previously-undocumented WRAM addresses (`BL-0018`) and reconciled re: the unused ring buffer (`BL-0013`) and the `DIV`-reseed drift fix |
| GDS-08 | Presentation Architecture (visualizer) | 08-presentation-architecture.md | ⛔ Planned |
| GDS-09 | Interface Specification | 09-interface-specification.md | ⛔ Planned |
| GDS-10 | Requirements Traceability Matrix level | 10-requirements-traceability-matrix.md | ⛔ Planned |

## §2 — Per-cluster design syntheses (ADS-xxx)

| ADS | Title | File | Status |
|---|---|---|---|
| ADS-100 | Combinable Generation Schemes | [ADS-100-combinable-generation-schemes.md](ADS-100-combinable-generation-schemes.md) | ✅ Authored 2026-07-22 — routes `BL-0020`; real design tension (control-surface scarcity, ROM budget) warranted a dedicated ADS rather than folding into the GDS ladder directly |
| ADS-101 | Genre-Aware Style Presets | [ADS-101-genre-aware-style-presets.md](ADS-101-genre-aware-style-presets.md) | ✅ Authored 2026-07-26 — routes `docs/roadmap/04-release-roadmap.md`'s R5; real design tension (no spare `CHMIX_MASKS` bits left for a 4-parameter style bundle, control-surface scarcity) warranted a dedicated ADS; decides a parallel `STYLE_TABLE` keyed by the existing `CHMIX_IDX` index, 3 concrete v1 styles named (Techno/Chiptune-Driving, Ambient/Lo-Fi, Holiday) |
| ADS-102 | Motif Recurrence via Weighted Variant Selection | [ADS-102-motif-recurrence-via-weighted-variant-selection.md](ADS-102-motif-recurrence-via-weighted-variant-selection.md) | ✅ Authored 2026-07-26 — routes `BL-0010`'s motif-recurrence half (R214 §8); real design tension (bounded-depth L-system finding vs. `IP-1070`'s existing single fixed `MOTIF_TABLE`) warranted a dedicated ADS; decides `MOTIF_TABLE` extends to a small fixed set of variants selected at cycle-boundary events via a weighted lookup table, no derivation engine |
| ADS-103 | Song-Form & Style-Drift State Machine | [ADS-103-song-form-and-style-drift-state-machine.md](ADS-103-song-form-and-style-drift-state-machine.md) | ✅ Authored 2026-07-26 — routes `docs/roadmap/04-release-roadmap.md`'s R6 (`BL-0010`'s song-form half, R220); decides the new state machine stays independent of `IP-0007`'s bad-zone loop (disjoint WRAM fields), 4-phase song-form structure ships in v1, style-drift deferred |
| ADS-104 | Settings & Control Visibility | [ADS-104-settings-and-control-visibility.md](ADS-104-settings-and-control-visibility.md) | ✅ Authored 2026-07-26 — routes `BL-0051`; unifies four scattered visualizer-reactive-signal Open Questions (`FS-107`-`FS-110`) with the user's own base-control-legend request; decides 5 new bar-height indicator tiles (tempo/octave/scale/density/channel-mix), reusing the existing BG palette, no new font/text rendering; scheme/style/motif-variant/song-phase indicators deferred to the same reusable mechanism |

## §3 — Vision-layer artifacts owned by `01-vision`

| Artifact | File | Status |
|---|---|---|
| Strategic assumptions register | [strategic-assumptions-register.md](strategic-assumptions-register.md) | ✅ Authored 2026-07-22 (7 assumptions; A7's trigger already fired — see `BL-0023`) |

## §4 — Architecture Decision Records

See `adr/INDEX.md`. 2 recorded: `ADR-0001` (scheme selection rides the `CHMIX_IDX` preset space);
`ADR-0002` (defer MBC/bank-switching and SRAM/battery-save adoption — the R4.5 cart-shape
decision checkpoint, evidence-based, named re-triggers).
