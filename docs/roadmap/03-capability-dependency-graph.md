# Product Roadmap 03 — Capability Dependency Graph

- **Grounded in:** `02-capability-map.md`'s Dependencies column
- **Status:** ✅ Authored 2026-07-22

## Tiers

**Foundational** (bedrock — nothing above builds without these; all already shipped and
`VERIFIED`): CAP-01 Audio Engine, CAP-02 Composition Core, CAP-03 Rhythm Engine, CAP-04 Melody
Engine, CAP-07 Instrument/Voice-Role System, CAP-15 UI/Input System, CAP-16 Seed Management,
CAP-17 Playback/Runtime System, CAP-20 Testing Harness, CAP-21 Build Tooling.

**Intermediate** (build directly on Foundational; mostly shipped, two carry open defects that
block downstream work): CAP-05 Harmony/Voice-Interaction (partial), CAP-06 Sound Design/Timbre
(shipped, unverified), CAP-08 Bad-Zone Self-Correction (shipped, `BL-0017` open), CAP-10
Channel-Mix Control (**broken**, `BL-0019` open), CAP-14 Visual Engine (MVP shipped, evolution
pending).

**Advanced** (planned, not started; each depends on specific Intermediate capabilities being both
shipped *and* structurally sound — not just "exists"): CAP-09 Multi-Scheme Generation, CAP-11
Style Engine, CAP-12 Evolution Engine, CAP-13 Emotional/Energy Engine, CAP-18 Persistence.

**Cross-cutting** (not a tier — a constraint every release at every tier must satisfy): CAP-19
Performance & Budget Management.

## Dependency graph

```
Foundational (all VERIFIED, shipped)
  CAP-01 Audio Engine
  CAP-02 Composition Core ──┬── CAP-03 Rhythm Engine
                             ├── CAP-04 Melody Engine
  CAP-07 Instrument Roles    │
  CAP-15 UI/Input            │
  CAP-16 Seed Management     │
  CAP-17 Playback/Runtime    │
  CAP-20 Testing Harness     │
  CAP-21 Build Tooling       │
                             │
Intermediate                 │
  CAP-05 Harmony/Voice ◄─────┤ (partial: dissonance scoring shipped, real harmony not pursued)
  CAP-06 Sound Design ◄──────┤ (shipped, verification owed)
  CAP-08 Bad-Zone Recovery ◄─┴──── depends on CAP-05 too         [BL-0017 open defect]
  CAP-10 Channel-Mix Control ◄──── depends on CAP-01 only        [BL-0019 BROKEN — critical-path blocker]
  CAP-14 Visual Engine (MVP) ◄──── depends on CAP-01, CAP-08

Advanced (not started — two independent streams + one independent branch)
  STREAM 1 (Integrity & Diversity):
    CAP-10 fix (BL-0019 remediation) ──► CAP-09 Multi-Scheme ──► CAP-11 Style Engine
  STREAM 2 (Musical Maturity, parallel to Stream 1 — no dependency on CAP-09/10):
    CAP-08 + CAP-03 + CAP-04 ──► CAP-12 Evolution Engine ──► CAP-13 Emotional/Energy Engine
  CONVERGENCE (needs BOTH streams):
    CAP-11 (style-reactive) + CAP-13 (mood-reactive) ──► CAP-14 Visual Engine evolution
  INDEPENDENT BRANCH (no dependency on either stream):
    CAP-21 (bank-switching extension, if adopted) ──► CAP-18 Persistence

Cross-cutting (continuous, not sequenced):
  CAP-19 Performance & Budget Management — gates every release above, at every tier
```

## Critical path

**`CAP-10` (fix `BL-0019`'s unwired channel-mix control) is the single hardest blocker in the
entire graph.** It is a Medium-effort fix (a remediation package, `IP-9010`, already fully
specified) sitting in front of the entire Multi-Scheme → Style Engine chain (`CAP-09` → `CAP-11`),
which is itself a prerequisite for genre-aware presets and genre blending — two of the roadmap's
named later-stage goals. **This fix is also already G3-authorization-blocked** (`docs/pipeline/
backlog.md` `BL-0019`, `IP-9010` — "not authorized" on the Master Build Plan) — the critical path's
true bottleneck today is not technical, it is the standing authorization gate.

Secondary critical-path item: `BL-0017` (overload threshold unreachable) is lower severity and
does not block any Advanced capability directly, but should be fixed in the same authorization
pass as `BL-0019` since `IP-9020` is already specified and touches the same bad-zone-adjacent code
region as `CAP-08`.

## Parallel work streams

Once `CAP-10` is fixed, **two genuinely independent streams** can proceed in parallel with no
cross-blocking:

- **Stream 1 — Integrity & Diversity**: `CAP-09` Multi-Scheme → `CAP-11` Style Engine → genre
  presets/blending (Releases R4-R5, R8 in `04-release-roadmap.md`).
- **Stream 2 — Musical Maturity**: `CAP-12` Evolution Engine → `CAP-13` Emotional/Energy Engine
  (Releases R6-R7). **This stream does not depend on `CAP-10` at all** and could start
  immediately, in parallel with the `CAP-10` fix itself, if development capacity allows — R220/
  R221 both found their mechanisms depend only on already-shipped Foundational state.

A third, fully independent branch — **Persistence** (`CAP-18`, gated on an explicit architecture
adoption decision, not a technical blocker) — can be picked up at any point after that decision is
made, with zero interaction with either stream.

## Bottlenecks

1. **`CAP-10` / `BL-0019`** — technical fix is small, the authorization gate is the real
   bottleneck (see Critical Path above).
2. **`CAP-14` Visual Engine evolution** — the one true convergence point in the graph. It cannot
   meaningfully proceed until *both* Stream 1 (`CAP-11`, for style-reactive visuals) and Stream 2
   (`CAP-13`, for mood-reactive visuals) have shipped something to react to — starting it earlier
   would mean building against a moving target. It also has an **un-run research prerequisite**
   (MSTR-001 §9's "visual evolution & audio-visual synchronization" thread — the one §9 thread
   this session's research pass did not reach) that should be scheduled before design work starts,
   not discovered as a mid-release gap.
3. **`CAP-08`'s open defect (`BL-0017`)** is not a hard blocker for any Advanced capability, but
   leaving it open means `CAP-08`'s bad-zone signal (which `CAP-12`/`CAP-13` both build on) is
   known-incomplete — fixing it before Stream 2 starts is cheap insurance, not a hard requirement.

## Opportunities for incremental delivery

- Stream 1 and Stream 2 each produce an independently demonstrable, audible improvement at every
  release (a new selectable scheme; a recognizable song-form arc) — neither needs to wait for the
  other to ship something a listener can hear.
- `CAP-06` (Sound Design/Timbre) is already shipped and only needs `09-package-verification` — the
  cheapest possible "next release," not gated on anything in this graph at all.
- `CAP-18` Persistence can be sliced arbitrarily thin (e.g. "save just the last-used style index"
  before "save a whole collection of favorites") without touching either stream — a good candidate
  for a small release whenever development capacity has a gap between Stream 1/2 milestones.
