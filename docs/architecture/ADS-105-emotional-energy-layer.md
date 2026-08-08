# ADS-105 — Emotional/Energy Layer (roadmap R7)

- **Status:** ✅ Authored 2026-07-31 · **Owned by:** `03-architecture-design-synthesis`
- **Dependencies:** [`R221`](../research/encyclopedia/R221-emotional-energy-parameter-mapping.md)
  (valence-arousal circumplex model, the axes' input signals); [`R101` §8.5](../research/encyclopedia/R101-sm83-instruction-set-and-cycle-costs.md)/
  [`GDS-06` §2.2a](06-non-functional-requirements.md) (the per-frame VBlank budget finding this
  design must not worsen); [`GDS-04`](04-domain-model.md) (the steering-index family this reads);
  [`GDS-07`](07-data-model.md) (WRAM headroom); `docs/roadmap/04-release-roadmap.md` R7,
  `docs/roadmap/03-capability-dependency-graph.md` Stream 2 (`CAP-12` → `CAP-13`).
- **Produces:** the future `FS-1xx` for `FEAT-1120` (roadmap R7), and grounds roadmap R9's
  eventual mood-reactive visual work once R9's own blocking research thread lands.

## 1. Executive Design Overview

R7 makes the engine's already-tracked internal state legible as **mood**, per `R221`'s
valence-arousal (circumplex) model: a two-axis summary — how *pleasant* (valence) and how
*energetic* (arousal) the current musical state reads — derived entirely from state the engine
already maintains (`TEMPO_IDX`, `DENSITY_IDX`, `SCALE_IDX`). Nothing audible or visible changes as
a direct result of this release in isolation, matching the roadmap's own framing: this is a
read/interpret layer, not a new generation mechanism, laying groundwork for R9's future
visualizer work rather than shipping a player-facing feature itself.

**The central design decision this ADS makes, and the reason it needed a dedicated pass rather
than folding straight into a spec:** `R221` recommended storing a derived `(valence, arousal)`
pair so a future consumer has something stable and cheap to read, but stopped short of saying
*when* that derivation should run. The naive answer — recompute every frame, like `_emit_badzone_tick`
already does for bad-zone state — is no longer free to assume. `IP-9030` (shipped this session)
measured that `read_joypad`→`apply_input`→`engine_tick` already consume roughly 9 of VBlank's 10
scanlines before the visualizer even starts, on *every* frame, with a margin of a handful of
instructions. Any per-frame addition to `engine_tick` spends directly against that already-thin
budget. **This ADS decides the derivation runs only when a relevant input actually changes** —
piggybacked onto the same write sites that already touch `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` —
rather than unconditionally every frame, keeping this release's own steady-state per-frame cost at
**zero**.

## 2. System Architecture

Two new WRAM bytes, `AROUSAL` and `VALENCE`, live in the same address family as the other
steering-derived state (`GDS-07`'s WRAM map, next free address `0xC068`). No new module: the
derivation logic is a new small routine in `music_engine.py` (`_emit_mood_update` or similar, named
at implementation time), called from exactly the sites that can change its inputs — never from the
per-frame main loop. `visuals.py` is **not** touched by this release; R9, not R7, is the eventual
consumer, and R9 remains separately blocked on its own unrun research thread (`04-release-roadmap.md`
R9's "prerequisite not yet satisfied" note). This release is architecturally inert with respect to
the visualizer, exactly as its roadmap entry frames it.

**Recompute trigger sites** (every write path that touches an axis input, confirmed against the
current tree):

- `input_map.py`'s `_step_on_bit` calls for `TEMPO_IDX` (D-pad Up/Down), `DENSITY_IDX` (B), and
  `SCALE_IDX` (A) — the three per-frame-input-driven writes to axis-feeding fields.
- `music_engine.py`'s `_emit_song_tick` — song-form phase transitions overwrite `TEMPO_IDX`/
  `DENSITY_IDX` autonomously (`IP-1100`), which must also trigger a recompute or the mood signal
  goes stale exactly when the engine's own arc changes it, the case R9 will care about most.
- `input_map.py`'s Select-reset path (`init_engine`) — resets `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/
  `DENSITY_IDX`/`CHMIX_IDX` to their boot presets; `AROUSAL`/`VALENCE` must be recomputed here too,
  or a post-reset read would show a stale pre-reset mood.
- `music_engine.py`'s `build_engine_asm`'s `init_engine` label (boot path) — the very first
  `AROUSAL`/`VALENCE` values must be computed once at boot, not left at `0x00` until the first
  input edge; the same "first frame already correct" discipline `IP-1110`'s boot-preset
  pre-initialization established.

**Not a recompute trigger, deliberately:** `IP-1080`'s style-application path (`_emit_apply_style`)
writes `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` too, on a Start press — this already funnels through
the *same* WRAM addresses the trigger sites above cover, so no separate hook is needed; the
existing recompute call at whichever site's write actually lands last in the per-frame call order
picks it up. (Verified against `GDS-09` §5's call-order contract: `apply_input` runs before
`engine_tick`, and `_emit_apply_style` is called from within `apply_input`'s Start-edge handling —
recorded here so a future reader doesn't add a redundant hook.)

## 3. Domain Model

Extends `GDS-04`'s domain model with one new concept: **the mood pair**, a derived
(not directly steerable) summary of the steering-index family's current state.

```
AROUSAL  (0-15, byte) ← derived from TEMPO_IDX, DENSITY_IDX
VALENCE  (0-15, byte) ← derived from SCALE_IDX, secondarily DISSONANCE_SCORE (deferred, see §9 OQ2)
```

Unlike every other entity `GDS-04` documents, the mood pair has **no writer of its own** in the
input-mapping sense — nothing steers it directly (matching `R221`'s "read/interpret layer, not new
generation logic" framing, and the roadmap's "nothing new to *hear* by itself"). It is a pure
function of existing state, recomputed at the trigger sites in §2. This makes it architecturally
closer to `visuals.py`'s tile indicators (a derived read of engine state) than to any of `GDS-04`'s
existing engine-state entities — but it lives in `music_engine.py`, not `visuals.py`, because its
consumer is not yet the visualizer (R9 is blocked) and because `music_engine.py` already owns
every other derived-from-steering-state computation (`_emit_badzone_tick` is the precedent: also a
derived summary of channel state, also WRAM-resident, also computed by `music_engine.py`).

## 4. User Stories

None — this release has no player-facing behavior. The "user" of this release is roadmap R9's
future implementation, and (secondarily) `test_rom.py`'s own assertions. Recorded explicitly
rather than fabricating a listener-facing story: `R221` and the roadmap both frame this as
infrastructure, and forcing a user story here would misrepresent the release's actual shape.

## 5. Functional Requirements (candidates for `04-requirements-engineering`)

- **FR-candidate 1**: The engine maintains a derived `AROUSAL` value (0-15) as a function of
  `TEMPO_IDX` and `DENSITY_IDX`, recomputed whenever either changes (button edge, song-form
  transition, style application, or reset), never left stale by more than the single frame in
  which the change occurred.
- **FR-candidate 2**: The engine maintains a derived `VALENCE` value (0-15) as a function of
  `SCALE_IDX`, recomputed on the same triggers as `AROUSAL` (`SCALE_IDX` and `TEMPO_IDX`/
  `DENSITY_IDX` are written at overlapping sites — see §2 — so one shared recompute routine
  handles both axes together, not two independent ones).
- **FR-candidate 3**: `AROUSAL`/`VALENCE` are initialized at boot to the values implied by the
  boot-preset steering indices, before the first frame renders or is tested against — no
  "correct after the first input" grace period.
- **FR-candidate 4**: Select-reset recomputes `AROUSAL`/`VALENCE` from the restored preset values
  on the same frame the reset itself lands, matching every other reset-to-preset field's own
  same-frame guarantee (`GDS-03` §5).

## 6. Non-functional Requirements (candidates)

- **NFR-candidate 1 (the load-bearing one)**: This release adds **zero unconditional per-frame
  CPU cost** to `engine_tick`. The recompute routine runs only from the trigger sites in §2, each
  of which is itself edge-triggered or transition-triggered, not a per-frame unconditional call.
  Verification must confirm this by inspection of the call graph, not merely by a passing stress
  test — a per-frame call that happens to be cheap enough not to trip `NFR-1010`'s stress-run
  proxy would still violate this NFR's intent, for exactly the reason `GDS-06` §2.2a documents
  (the stress-run method cannot detect a narrowed VBlank margin; it can only detect a frame drop).
- **NFR-candidate 2**: `AROUSAL`/`VALENCE`'s derivation cost, at whichever trigger site incurs it,
  must be small relative to that site's existing cost — `_step_on_bit`/`_emit_song_tick`/
  `init_engine` are not part of the exhausted VBlank-window path `IP-9030` measured (that path is
  `read_joypad`→`apply_input`→`engine_tick`, i.e. these routines already run inside it every
  frame regardless) — so this NFR is about not making an already-executing routine meaningfully
  heavier, not about a new addition to an unvisited code path. State the actual cycle cost in the
  implementing package's own Risks field once real opcodes are chosen.
- **NFR-candidate 3**: `AROUSAL`/`VALENCE` are addressed at `0xC068`-`0xC069` (`GDS-07`'s next-free
  8-aligned pair), 2 bytes against the WRAM block's ample remaining headroom — negligible.

## 7. Constraints

- **No new WRAM writer for the visualizer.** `visuals.py` must not be touched by this release —
  R9 owns consuming `AROUSAL`/`VALENCE` visually, and R9 is separately gated on its own research.
  A future FS/IP for this ADS's scope that touches `visuals.py` has exceeded R7's own boundary.
- **No new player control.** Nothing in `input_map.py`'s button-to-parameter mapping changes;
  `AROUSAL`/`VALENCE` are derived, never directly steered (§3).
- **Must not add an unconditional per-frame call.** The zero-added-per-frame-cost constraint
  (§6 NFR-candidate 1) is binding, not aspirational, given `IP-9030`'s measured margin.

## 8. Risks

- **The recompute-on-write design is more moving parts than a single per-frame call would be** —
  four trigger sites (three input steps, one song-tick, one reset, one boot-init — effectively
  five) instead of one. The risk is a missed site: if a future package adds a sixth way to change
  `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX` without also calling the recompute routine, `AROUSAL`/
  `VALENCE` silently go stale with no test failure, since nothing currently consumes them to
  notice. Mitigation: the implementing package's own supersession-sweep-equivalent should grep for
  every write to the three source addresses and confirm each triggers a recompute; `test_rom.py`
  should assert the derived values match a from-scratch recomputation after driving *each* trigger
  site independently, not just one.
- **`DISSONANCE_SCORE`'s valence-proxy role is deliberately excluded from v1** (see Open Question 2)
  — a future package that wants to add it needs the citation gap `R221` flagged closed first, or
  needs to accept the citation gap explicitly as a scoped risk, not silently assume it was settled
  here.
- **No consumer exists yet.** This release is, by its own design, unverifiable by observation —
  `test_rom.py` can only assert the derived values against the same formula the implementation
  uses, which is a weaker check than an independent behavioral assertion. This is inherent to a
  read-layer-with-no-consumer-yet release, named honestly rather than glossed; the same shape
  `R7`'s roadmap entry itself already flags ("should ship bundled with R6 or R9... alone produces
  no audible/visible change").

## 9. Open Questions

1. **Exact derivation formulas.** `R221` names the inputs per axis but not concrete formulas.
   Recommend (not decided here — this is `04-requirements-engineering`'s or the eventual FS
   author's call, since it crosses into testable acceptance-criterion territory): `AROUSAL` as a
   weighted sum of `TEMPO_IDX` (0-7 range) and `DENSITY_IDX` (0-7 range) each scaled/shifted into
   a combined 0-15 output (e.g. `(TEMPO_IDX + DENSITY_IDX) >> 0` clamped, or a lookup table if a
   non-linear mapping is wanted — a lookup table is cheap in ROM and trivially matches whatever
   curve a future content-review pass prefers, and avoids on-device division, which the SM83
   opcode set this project uses has no direct support for). `VALENCE` as a direct lookup from
   `SCALE_IDX` (only 4 values currently, `R204`-style small lookup table) rather than a formula —
   scale/mode-to-valence is a categorical mapping in the literature, not a continuous function.
2. **Is `DISSONANCE_SCORE` included as a secondary valence signal?** **Decided here: no, not in
   v1.** `R221` itself flags the dissonance-as-valence-proxy claim as "not yet confirmed by a
   direct citation... needs fetch-verification if this mapping becomes a real requirement." Since
   `VALENCE` is already fully derivable from `SCALE_IDX` alone (a well-established, independently-
   cited mapping), there is no need to accept an unconfirmed citation to ship v1. **Routed to
   `02-research-game-design`**: if a future pass wants `DISSONANCE_SCORE` folded into `VALENCE`
   (e.g. to distinguish "major scale, currently dissonant" from "major scale, currently
   consonant" as different valence states), that citation gap should close first, as its own
   research addendum, before any requirement bakes in the unconfirmed claim.
3. **Should `CHMIX_IDX`/active-channel-count factor into `AROUSAL`?** `R221` notes active-channel
   count is "a direct arousal-axis lever" in the literature (more simultaneous layers = higher
   arousal) and that `CHMIX_IDX` already selects the active-channel set. **Deferred, not decided
   here** — including it would mean deriving an active-channel *count* from `CHMIX_MASKS` (an
   extra lookup, still cheap) at every `CHMIX_IDX`-changing trigger site (Start press, style
   application, reset — already covered by §2's trigger list, so no *new* trigger site would be
   needed, only an additional input to the same formula). Left open for `04-requirements-
   engineering` to decide whether v1's arousal formula includes it or defers it — the
   architectural cost of adding it later is low either way, since the trigger-site plumbing is
   already in place.
4. **Naming**: `AROUSAL`/`VALENCE` versus more domain-flavored names (e.g. `ENERGY_LEVEL`/
   `MOOD_TONE`) — a naming-only question, left to the implementing package; `R221`'s own
   vocabulary (Russell's circumplex terms) is used here for precision against the research, not
   as a mandated final name.

## 10. Decision Log

| Decision | Rationale |
|---|---|
| Store `AROUSAL`/`VALENCE` as 2 stationary WRAM bytes (not computed on demand) | `R221`'s own recommendation — a future consumer (R9, or a test) needs something stable and cheap to read, not a formula to re-derive at every read site. |
| Recompute **only at the write sites that can change the inputs**, not every frame | The load-bearing decision this ADS exists to make. `IP-9030` measured the per-frame VBlank window as ~exhausted on every frame already; adding an unconditional per-frame computation here would spend directly against that margin for a release whose own roadmap entry says it produces no audible/visible change by itself — an especially bad trade. Recompute-on-write keeps this release's steady-state per-frame cost at exactly zero. |
| Five trigger sites identified and enumerated (3 input steps, 1 song-tick, 1 reset+boot-init) | Verified against the current tree (`input_map.py`'s `_step_on_bit` calls, `music_engine.py`'s `_emit_song_tick`, `init_engine`) rather than assumed — `IP-1080`'s style-application path confirmed to route through the same addresses, needing no separate hook. |
| `DISSONANCE_SCORE` excluded from `VALENCE` in v1 | `R221`'s own citation-confirmed signal (`SCALE_IDX`) is sufficient to ship; the dissonance-proxy claim is explicitly flagged unconfirmed and accepting it would mean baking an uncited claim into a shipped formula. Routed to `02-research-game-design` as a named future addendum, not silently dropped. |
| `visuals.py` untouched; no new player control | Matches R7's own roadmap scope exactly — a read-layer, not a feature. Keeps this release's equivalence-with-its-own-framing honest: "nothing new to hear or see" should mean literally no code outside `music_engine.py` (plus `GDS-07`'s WRAM map) changes. |
| Exact derivation formulas left as a recommendation, not a final decision | Crosses into testable-acceptance-criterion territory that belongs to `04-requirements-engineering`/the eventual FS author, per this skill's own scope boundary (design tension resolved here; exact numeric formulas are downstream). |

## Merge gate

- [x] All ten sections present, none a placeholder.
- [x] Every FR/NFR candidate traces to a cited source (`R221`, `IP-9030`'s measurement,
      `GDS-04`/`GDS-07`).
- [x] No production code, no literal byte-level opcode sequences — WRAM *addresses* are cited
      (per `GDS-07`'s own convention for ADS documents that reserve address space) but derivation
      is left at the formula-recommendation level, not opcodes.
- [x] `docs/architecture/INDEX.md` §2 and `ROADMAP.md`'s stage-03 row updated together, this pass.
- [x] No new research claims originated here — the `DISSONANCE_SCORE` citation gap is routed to
      `02-research-game-design`, not resolved by assertion.

**Merge decision.** This ADS's Decision Log is the load-bearing artifact for whoever drafts R7's
eventual `FS-1xx` — in particular the recompute-on-write decision and its five trigger sites, which
a downstream FS should cite rather than re-derive. No existing document needs to change to
accommodate this ADS: `GDS-04`/`GDS-07`/`GDS-06` are all consistent with the mood pair as
described (a new derived entity, 2 new WRAM bytes, no per-frame budget impact) and none asserted
anything this ADS contradicts.
