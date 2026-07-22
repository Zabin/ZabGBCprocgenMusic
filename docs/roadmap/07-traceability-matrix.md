# Product Roadmap 07 — Traceability Matrix

- **Grounded in:** all prior sections of this package + MSTR-001 v1.4
- **Status:** ✅ Authored 2026-07-22

One row per MSTR-001 commitment or §9 research thread, traced all the way to the feature grain.
`—` means "satisfied at this level already, nothing further downstream needed."

| Vision Ref | Product Goal (01) | Capability (02) | Milestone (05) | Release (04) | Feature(s) (06) |
|---|---|---|---|---|---|
| MSTR-001 C1/C2 (cart shape/persistence, reopened v1.2) | Success Criteria (persistence explicitly optional) | CAP-18 Persistence, CAP-21 Build Tooling | B (decision) / F (feature) | R4.5, R11 | RM-4501, RM-11002 |
| MSTR-001 C3 (Python-assembler build) | — (already satisfied) | CAP-21 Build Tooling | A | R0 | — (shipped) |
| MSTR-001 C4 (input steers live params) | Interaction Philosophy | CAP-15 UI/Input | A / E | R1 (shipped) / R10 | RM-10001 |
| MSTR-001 C5 (autonomous bad-zone recovery) | Emotional Goals | CAP-08 Bad-Zone Self-Correction | A / B | R1 (shipped) / R3 | RM-3002 |
| MSTR-001 C6 (real-time, on-device) | Procedural Generation Philosophy | CAP-02 Composition Core | A | R1 | — (shipped) |
| MSTR-001 C7 (all 4 channels used) | Overall Experience | CAP-01 Audio Engine, CAP-07 Instrument Roles | A | R1 | — (shipped) |
| MSTR-001 C8 (visualizer reacts to engine state) | Audiovisual Identity | CAP-14 Visual Engine | A / E | R1 (MVP, shipped) / R9 | RM-9001, RM-9002, RM-9003 |
| MSTR-001 C9 (emulator-verified, testable) | Success Criteria | CAP-20 Testing Harness | A (ongoing every milestone) | every release | every `RM-xxxx`'s own acceptance criteria |
| MSTR-001 C10 (research traceable to shipped code) | Success Criteria | CAP-20 (audit target), this roadmap package itself | cross-cutting | — | this document's own existence is the mechanism; a forward-trace audit remains separately owed (`docs/pipeline/backlog.md`, run #26) |
| §9 thread: musical identity & diversity | Artistic Goals, Replayability Goals | CAP-11 Style Engine | B / D | R5, R8 | RM-5001, RM-5002, RM-8001 |
| §9 thread: style evolution & song-form | Emotional Goals, Replayability Goals | CAP-12 Evolution Engine | C / D | R6, R8 | RM-6001, RM-6002, RM-8001 |
| §9 thread: emotional/energy model | Emotional Goals | CAP-13 Emotional/Energy Engine | C | R7 | RM-7001, RM-7002 |
| §9 thread: visual evolution & AV sync | Audiovisual Identity | CAP-14 (evolution) | E | R9 | RM-9000 (research prerequisite), RM-9001, RM-9002 |
| §9 thread: cart shape & persistence | Success Criteria (explicitly optional) | CAP-18, CAP-21 | B (decision) / F (feature) | R4.5, R11 | RM-4501, RM-11002 |
| `BL-0019` (channel-mix unwired, High) | Interaction Philosophy | CAP-10 | B | R3 | RM-3001 |
| `BL-0017` (overload unreachable, Medium-High) | Emotional Goals | CAP-08 | B | R3 | RM-3002 |
| `BL-0020` (combinable schemes, user-filed) | Procedural Generation Philosophy, Replayability | CAP-09, CAP-11, CAP-12 | B / D | R4, R8 | RM-4001, RM-4002, RM-8001 |
| `BL-0010` (song-form/motif gap) | Emotional Goals | CAP-12 | C | R6 | RM-6001 (song-form half closes here; motif-recurrence half stays open, see below) |
| `BL-0021` (accessibility luminance gap) | Audiovisual Identity | CAP-14 | E | R9 | RM-9003 |

## Vision objectives not addressed by this roadmap

- **Motif recurrence** (the L-system half of `BL-0010`, R214 SS5) — deliberately **not** scheduled
  anywhere in this roadmap. R220 itself named this the harder, still-unsolved remainder;
  including it here would violate the guiding principle against large unfinished systems (an
  L-system engine is a genuinely open research-to-architecture problem, not yet groundable at
  feature grain). Recorded as an explicit gap, not silently dropped.
- **MSTR-001 §2's "developers/coding agents" audience goal** (the repo as a worked example) has no
  dedicated capability or release — it is satisfied continuously by the documentation-driven
  pipeline's own discipline (this roadmap package included), not by a shippable ROM feature.
  Correctly has no roadmap row; named here so its absence reads as deliberate, not missed.
- **Hardware certification** (MSTR-001 §4 non-goal) — correctly absent; `08-development-
  strategy.md`'s hardware-testing cadence is a validation practice, not a release gate, per
  MSTR-001's own non-goals list.

## Unnecessary features check

Every `RM-xxxx` entry in `06-feature-specifications.md` traces to a row in the table above — none
were added because they were easy or omitted because they were hard. Two entries are flagged for
attention, not removal:

- **RM-7001/RM-7002** (emotional/energy read-layer) produce **no audible or visible change by
  themselves** — they satisfy `01-product-goals.md`'s success criterion #3 ("a listener can point
  to a specific audible/visible improvement") only when shipped bundled with R6 or R9, never as a
  standalone release. Flagged in `04-release-roadmap.md`'s R7 entry and repeated here so it isn't
  missed at scheduling time.
- **RM-9000** (visual-evolution research pass) is not a feature in the normal sense (no code, no
  test) — it is a hard prerequisite gate. Included in the feature list because omitting it risks
  R9 being scheduled without it, not because it's itself shippable.

No feature was found tracing to nothing — the matrix above is exhaustive against
`06-feature-specifications.md`'s full `RM-xxxx` list.
