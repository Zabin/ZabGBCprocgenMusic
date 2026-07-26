# ADS-103 — Song-Form & Style-Drift State Machine

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored 2026-07-26
- **Dependencies:** R220 (style evolution/song-form structure — the cheap parameter-envelope
  state-machine finding this design implements), R212 (form/tension, the original gap), R204
  (bad-zone state machine — the closest existing precedent, and the mechanism this design must
  coexist with), `IP-0007` (autonomous bad-zone recovery, the shipped precedent for a fully
  autonomous no-input-required state machine), `ADS-101`/`IP-1080` (the existing coordinated-
  parameter-overwrite idiom this design reuses), `ADS-102`/`IP-1090` (the existing cycle-boundary
  weighted-selection idiom, a sibling autonomous mechanism already proven safe alongside bad-zone
  recovery)
- **Produces:** a future `FS-xxx` (once `04-requirements-engineering` derives FRs from this
  document) and an eventual Implementation Package
- **Trigger:** `docs/roadmap/04-release-roadmap.md`'s **R6 — Song-Form & Style-Drift Engine**,
  whose own entry names the architecture need ("a new state-machine mechanism sharing its shape
  with `IP-0007`'s bad-zone loop") and its own risk (interaction with bad-zone recovery needs an
  explicit precedence rule) — this document answers both, and closes `BL-0010`'s song-form half
  per R6's completion criteria

## 1. Executive Design Overview

R220's central finding is that song-form structure (a recognizable intro→build→peak→breakdown
arc) and style-drift (a session's musical character slowly migrating) are **the same mechanism at
two timescales** — both reduce to a state machine driving Driftune's already-tracked parameters
(`TEMPO_IDX`/`DENSITY_IDX`) through envelopes, using the exact "coordinated overwrite" idiom
`ADS-101`/`IP-1080` already shipped for style presets, just autonomously and on a schedule rather
than on a Start press. This design implements the cheaper, well-grounded half R220 recommends
(song-form structure via 4 cycling states) and treats style-drift as the same mechanism at a
longer cadence (interpolating toward a target style over minutes) — explicitly **not** pursuing
R214/R220's harder, still-unsolved L-system phrase-recurrence problem (that remains `BL-0010`'s
already-closed-separately motif-recurrence half, `ADS-102`/`IP-1090`).

R220 flagged one concrete open question for this stage to resolve: should the new state machine
share one "meta-state" WRAM byte with `IP-0007`'s bad-zone loop, or stay independent? This design
decides **independent** — the two mechanisms drive genuinely different WRAM fields (bad-zone
recovery biases `CUR_DEGREE_*` deltas only; song-form biases `TEMPO_IDX`/`DENSITY_IDX` only), so
forcing them into one shared state byte would conflate two orthogonal concerns for no benefit.
The real interaction R6's own risk names is not a WRAM collision (there is none) but a *behavioral*
one — a BUILD state pushing `DENSITY_IDX` high could itself trigger `OVERLOAD`, fighting the arc
it's trying to create — named here as an Open Question for empirical verification, not resolved
by architectural fiat.

## 2. System Architecture

A new routine, `_emit_song_tick`, called once per frame from `engine_tick` (the same call site
`_emit_badzone_tick`/each channel's `gen_tick` already run from), following the exact
"count down, act at zero, reload" shape `IP-0007`'s own bad-zone loop and `IP-1070`'s Euclidean-
pattern timer already use:

```
engine_tick (existing, unchanged call site)
        │
        ▼
  _emit_song_tick   ← NEW
        │
   SONG_STATE_TIMER-- (existing-shape countdown)
        │
   timer == 0?
        │yes
        ▼
   SONG_STATE advances (INTRO→BUILD→PEAK→BREAKDOWN→INTRO, wrap mod 4)
        │
   SONG_STATE_TIMER reloads to that state's own bar-count
        │
   TEMPO_IDX/DENSITY_IDX overwritten to that state's target values
   (same coordinated-overwrite idiom ADS-101/IP-1080's _emit_apply_style already uses)
```

`_emit_badzone_tick` and each channel's `gen_tick` (including `IP-0007`'s dissonant/stuck
overrides and `IP-1090`'s motif-variant draws) are **entirely unmodified** — `_emit_song_tick`
only ever writes `TEMPO_IDX`/`DENSITY_IDX`, addresses no other mechanism reads or writes for its
own bookkeeping (`BAD_ZONE_FLAGS`/`CUR_DEGREE_*`/`MOTIF_VARIANT_IDX`/`scheme_state` are all
untouched), so no ordering dependency between `_emit_song_tick` and any existing tick routine is
introduced.

## 3. Domain Model

- **Song state**: one of 4 named phases (`INTRO`, `BUILD`, `PEAK`, `BREAKDOWN`), each holding a
  target `(tempo_idx, density_idx)` pair and a duration (in ticks, sized to read as a musically
  reasonable bar-count at default tempo — a content-authoring/tuning decision, not fixed here,
  same deferral convention as every prior preset-table addition).
- **`SONG_STATE`** (new, 1 WRAM byte): 0-3, indexing which of the 4 phases is active. Distinct
  from `CHMIX_IDX` (`IP-1080`'s style trigger — user-driven, instant) and from `BAD_ZONE_FLAGS`
  (reactive, metric-driven) — `SONG_STATE` is the first fully autonomous, schedule-driven (not
  metric- or input-driven) state this engine has.
- **`SONG_STATE_TIMER`** (new, 1 WRAM byte): ticks remaining in the current phase; reloaded to the
  new phase's own duration on every transition.
- **`SONG_TABLE`** (new ROM data): 4 rows, `(tempo_idx, density_idx, duration)` — one per phase,
  shape modeled directly on `STYLE_TABLE`'s own `(tempo_idx, density_idx, ...)` row convention.
- **Style-drift** (R220's slower-cadence half of the same mechanism): explicitly **deferred past
  this v1** — v1 ships song-form structure only (a fixed 4-phase loop over `TEMPO_IDX`/
  `DENSITY_IDX`); interpolating toward a drifting *style* target (reading `STYLE_TABLE`'s own rows
  as long-timescale envelope targets, per R220's own "same mechanism, slower cadence" framing) is
  named as a natural v2 extension of this same state machine (§9), not built here — keeps v1
  scoped to R6's own stated completion criteria ("song-form" specifically) rather than absorbing
  R220's second half unbounded.

## 4. User Stories

- As a listener who lets a session run uninterrupted, tempo and density visibly/audibly rise and
  fall in a recognizable arc (INTRO calm → BUILD rising → PEAK dense/fast → BREAKDOWN settling,
  looping) over several minutes, without touching any control — the same class of fully
  autonomous behavior bad-zone recovery already established, now driving musical *structure*
  rather than *correctness*.
- As a listener who has been manually steering tempo/density with the D-pad/B, the next
  song-state transition **overwrites** those manually-drifted values to the phase's target — the
  same "honest big jump" precedent Select's full-reset and `IP-1080`'s style application already
  establish, just autonomously triggered rather than button-triggered.
- As a listener in an active bad-zone recovery, a song-state transition landing on the same frame
  still overwrites `TEMPO_IDX`/`DENSITY_IDX` exactly as it would otherwise (bad-zone recovery
  never reads/writes those fields, confirmed in §2) — no special-casing needed, no interaction to
  design around, only to verify empirically (§9).

## 5. Functional Requirements (candidate — for `04-requirements-engineering` to formalize)

- FR-candidate: The engine cycles autonomously through 4 named song-form phases (`INTRO`,
  `BUILD`, `PEAK`, `BREAKDOWN`), looping, with no input required.
- FR-candidate: Each phase transition overwrites `TEMPO_IDX`/`DENSITY_IDX` to that phase's
  documented target values, immediately (same tick), the same "coordinated overwrite" contract
  `ADS-101`'s style application already establishes for those fields.
- FR-candidate: Bad-zone detection/recovery (`FR-1080`-`FR-1110`, `IP-0007`'s overrides) and
  Scheme-E motif-variant selection (`FR-1270`-`FR-1300`, `IP-1090`) both continue to operate
  identically regardless of the current song state — no song-state-specific logic exists in
  either mechanism.
- FR-candidate: A long (8000+ frame) headless run demonstrates all 4 phases occurring in the
  correct cyclic order with no hang/stall, satisfying R6's own "long-run regression for
  stability" testing goal.

## 6. Non-functional Requirements (candidate)

- ROM budget: `SONG_TABLE` (4 rows × 3 bytes = 12 bytes) — negligible against measured free ROM
  (`ADR-0002`'s instrumentation; comparable in scale to `IP-1080`'s own 32-byte `STYLE_TABLE`).
- WRAM budget: 2 new bytes (`SONG_STATE`, `SONG_STATE_TIMER`).
- No new input control — fully autonomous, same class as `IP-0007`'s bad-zone recovery and
  `IP-1090`'s motif-variant selection.
- Per-frame cost: one countdown-and-compare, comparable to `_emit_badzone_tick`'s own existing
  per-frame cost (R220's own "no new arithmetic complexity class" finding) — no new NFR-1010
  timing-budget risk expected, to be confirmed the same way every prior addition confirmed it
  (extended headless stress run).

## 7. Constraints

- **No shared meta-state with `IP-0007`'s bad-zone loop** — the two mechanisms drive disjoint
  WRAM fields (confirmed in §2); a shared state byte would conflate two orthogonal concerns for
  no benefit. This is the binding decision R220 asked this stage to make (§10).
- **No new input control** — matches every prior autonomous-mechanism precedent (`IP-0007`,
  `IP-1090`).
- **Style-drift (R220's slower-cadence half) is out of this v1's scope** — named as a natural
  extension (§9), not built here, keeping this pass scoped to R6's own "song-form" completion
  criteria.
- **Single 32KB bank, no MBC** (`ADR-0002`) — 12 bytes of new ROM data is far inside this ceiling.

## 8. Risks

- **A BUILD phase pushing `DENSITY_IDX` toward its high end could itself trigger `OVERLOAD`
  (`BAD_ZONE_FLAGS` bit2)**, fighting the arc it's trying to create with a bad-zone-driven pitch
  pull the listener would hear as working against the intended build — a real behavioral
  interaction, distinct from any WRAM collision (there is none). Not resolved here: named for
  `07-implementation-planning`/`09-package-verification` to empirically check once phase target
  values are chosen (a live drive through a full BUILD phase, checking whether `OVERLOAD` fires
  more often than at a comparable manually-set `DENSITY_IDX`) — if it does, the phase's own
  target density is the tuning lever, not a new precedence mechanism.
- **4 fixed phase durations may not read as a natural, non-mechanical arc** — a real
  `09-content-review` judgment call, not resolved here, same class of risk `ADS-101`'s own styles
  and `ADS-102`'s own motif variants were both content-reviewed for.
- **Interaction with `IP-1080`'s style presets**: a Start press mid-song-state changes
  `TEMPO_IDX`/`DENSITY_IDX` to a style's values immediately; the next song-state transition will
  then overwrite them again on its own schedule — the same "two independent autonomous/triggered
  writers to the same field, last-write-wins" pattern already established and already verified
  safe for `IP-1080`↔`IP-1090`'s adjacent-field interaction (`VR-1090`'s own adversarial testing);
  named here for the same class of verification once built, not assumed safe by analogy alone.

## 9. Open Questions

- **Should `DENSITY_IDX`'s BUILD-phase target be tuned to deliberately stay below
  `OVERLOAD_THRESHOLD`'s reachable range** (per §8's own risk), or is an occasional overload
  during BUILD actually a *desirable* dramatic moment (the engine "straining" as the arc peaks)?
  Genuinely open — a musical judgment call for `09-content-review` once phase values are chosen,
  not decided at the architecture stage.
- **Should style-drift (R220's slower-cadence half) reuse this exact state machine** (a 5th+
  "phase" that interpolates toward a `STYLE_TABLE` row over minutes) **or a separate mechanism**?
  R220 itself frames these as "the same mechanism, different cadence" — the natural default is
  reuse, but this is deliberately left to a future `03-architecture-design-synthesis` pass once
  v1's song-form structure has shipped and its own timing/tuning is known, not decided here.
- **Exact phase durations and `TEMPO_IDX`/`DENSITY_IDX` target values** — first-guess placeholders
  at implementation time, same `BL-0005`-class deferral as every prior preset/table addition.
- **Should `SCALE_IDX`/`DUTY_BIAS` also be part of the phase envelope** (a fuller "style" move,
  not just tempo/density), matching `IP-1080`'s own 4-field `STYLE_TABLE` shape? Deliberately
  scoped out of v1 (R6's own completion criteria names only the "recognizable arc," which
  tempo/density alone can produce) — a natural v1.1 extension once v1's 2-field version is
  content-reviewed, not decided here.

## 10. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-26 | The song-form/style-drift state machine does **not** share meta-state with `IP-0007`'s bad-zone loop — it stays fully independent (`SONG_STATE`/`SONG_STATE_TIMER`, new bytes). | The two mechanisms drive disjoint WRAM fields (bad-zone recovery: `CUR_DEGREE_*` deltas only; song-form: `TEMPO_IDX`/`DENSITY_IDX` only) — a shared state byte would conflate two orthogonal concerns for no benefit. Resolves R220's own explicitly flagged open question. |
| 2026-07-26 | Song-form phase transitions overwrite `TEMPO_IDX`/`DENSITY_IDX` immediately (same tick), reusing the exact coordinated-overwrite idiom `ADS-101`/`IP-1080` already shipped. | Consistency with every prior "big, honest jump" precedent (Select's full reset, style application) rather than inventing a new envelope-interpolation mechanism for v1 — R220 itself frames song-form as achievable via direct parameter-index writes, no interpolation required. |
| 2026-07-26 | Style-drift (R220's slower-cadence half of the same finding) is explicitly deferred past this v1 — only the 4-phase song-form structure ships now. | Keeps this pass scoped to R6's own stated completion criteria ("song-form" specifically); style-drift's own timing/tuning is better decided once song-form's real cadence is known from a shipped v1, not guessed now. |
| 2026-07-26 | The BUILD-phase/`OVERLOAD` interaction risk is named as an Open Question for empirical verification, not resolved by a new precedence mechanism. | No actual WRAM collision exists between the two mechanisms (confirmed by design) — the only real risk is a *musical* one (density push triggering overload), which is a tuning question phase-value selection can address, not an architectural one requiring new machinery. |
