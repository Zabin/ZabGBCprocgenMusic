# Product Roadmap 02 — Capability Map

- **Grounded in:** `01-product-goals.md`, MSTR-001 v1.4, GDS-00/01/03, the Feature Catalog
  (`docs/feature-planning/01-feature-catalog.md`), `docs/pipeline/backlog.md`, R2xx encyclopedia
- **Status:** ✅ Authored 2026-07-22

Every capability Driftune needs, present or future, with real current status (shipped/partial/
broken/planned) — not an aspirational list pretending nothing exists yet. `CAP-xxx` IDs are new
to this roadmap package; each row cites the existing artifact (`FEAT-xxxx`, `IP-xxxx`, `BL-xxxx`,
`Rxxx`) that already covers or grounds it, so this map adds sequencing value without duplicating
what those artifacts already own.

| ID | Name | Purpose | Description | User-Visible Outcome | Dependencies | Related Vision / Grounding | Status |
|---|---|---|---|---|---|---|---|
| CAP-01 | Audio Engine | Own all PSG register I/O | Writes `NR1x`-`NR5x` for all four channels; the single hardware-facing write surface | The ROM makes sound at all | None (bedrock) | MSTR-001 C7; R108/R111/R113-R115 | **Shipped** (`FEAT-1000`, `IP-0001`-`IP-0003`, `VERIFIED`) |
| CAP-02 | Composition/Generation Core | Decide what each channel plays next, every frame | Per-channel note-timer/degree state machine (`_emit_channel_gen`) | Continuous, non-repeating melodic motion | CAP-01 | MSTR-001 C6; R201 | **Shipped** (`FEAT-1000`, `VERIFIED`) |
| CAP-03 | Rhythm Engine | Tempo + onset timing | Tempo preset table; Euclidean-gated noise-channel density | Audible pulse/groove, steerable | CAP-01 | R202; GDS-03 §3 | **Shipped** (`FEAT-1000`/`FEAT-1010`, `VERIFIED`) |
| CAP-04 | Melody Engine | Constrain note choice to a musical scale/mode | Scale-degree table lookup + LFSR-driven step | Recognizably "in key" motion, not noise | CAP-02 | R201; GDS-03 §3 | **Shipped** (`FEAT-1000`, `VERIFIED`) |
| CAP-05 | Harmony / Voice-Interaction Engine | Manage how simultaneous voices relate | Pairwise interval-class dissonance scoring; arpeggio as a pseudo-polyphony substitute | Chords are implied, not clashing | CAP-02, CAP-04 | R203/R204/R216; GDS-03 §4a | **Partial** — dissonance scoring shipped (`FEAT-1030`, `VERIFIED`); real multi-voice harmony not pursued (R219 finding: not achievable on 4 monophonic channels without this substitution) |
| CAP-06 | Sound Design / Timbre Engine | Layer expressive articulation onto held notes | Arpeggio, vibrato, portamento, duty-cycle variation | Notes feel "played," not just triggered | CAP-02, CAP-04 | R216; FR-1130-FR-1170 | **Shipped, not yet independently verified** (`FEAT-1060`, `IP-1060`/`IP-1061` `COMPLETE`) |
| CAP-07 | Instrument / Voice-Role System | Give each channel a distinct musical job | Wave = bass/timbre anchor, pulse A/B = melody, noise = percussion | The mix sounds arranged, not four identical voices | CAP-01 | R207; `BL-0008` | **Shipped** (`FEAT-1000`, `VERIFIED`) |
| CAP-08 | Bad-Zone Self-Correction System | Keep the generator from staying unpleasant | Dissonance/stuck/overload detection + autonomous recovery bias | The music "fixes itself" without input | CAP-02, CAP-04, CAP-05 | MSTR-001 C5; R204 | **Shipped, one known defect** (`FEAT-1030`, `VERIFIED`; `BL-0017` — overload signal unreachable, remediation `IP-9020` authored, **not G3-authorized**) |
| CAP-09 | Multi-Scheme Generation | More than one selectable generation *approach*, combinable | A second scheme (e.g. motif-cycling) alongside the shipped LFSR walk, per-channel selectable | Real structural variety, not just parameter tuning of one algorithm | CAP-10 | `BL-0020`; `ADS-100`/`ADR-0001` | **Planned** — architecture design complete, **blocked on CAP-10** |
| CAP-10 | Channel-Mix / Active-Voice Control | Let Start steer which channels contribute | Channel-activity-mask table gating generation/register writes | The Start button actually does something | CAP-01 | GDS-03 §3; FR-1000/1010 | **Broken/unwired** (`BL-0019`, High — remediation `IP-9010` authored, **not G3-authorized**) — blocks CAP-09 |
| CAP-11 | Style Engine | Recognizable, steerable genre-adjacent character | Parameter-region presets (tempo/density/scale/duty/arpeggio-pattern combinations) mapped to genre references | "This sounds like techno now" vs. "this sounds ambient now" | CAP-03, CAP-06, CAP-09 | R219 (feasibility tiering) | **Planned** — research grounded, no design yet |
| CAP-12 | Evolution Engine (song-form + style-drift) | Give a session a shape over time | Parameter-envelope state machine reusing existing tracked parameters | Recognizable intro/build/peak/breakdown arc; slow style drift across a long session | CAP-02, CAP-03, CAP-04, CAP-08 (shares state-machine shape) | R220; `BL-0010` | **Planned** — concretely groundable, no design yet |
| CAP-13 | Emotional / Energy Engine | Make the engine's own state legible as mood | Valence-arousal derivation from tempo/density/scale/dissonance-score | The music (and eventually visuals) "feel like" a mood, not just a parameter set | CAP-03, CAP-04, CAP-08, CAP-12 (natural sequel) | R221 | **Planned** — concretely groundable, no design yet |
| CAP-14 | Visual Engine | Render the engine's state back to the screen | Tile/palette animation (currently: 4-channel-activity tiles, calm/bad-zone palette swap) | The screen tells you what's happening without needing to listen | CAP-01, CAP-08 (shipped); CAP-11, CAP-13 (evolution) | MSTR-001 C8; R205/R208 | **Shipped MVP** (`FEAT-1040`, `VERIFIED`); evolution (mood/style-reactive) **planned**, needs a not-yet-run research pass; accessibility finding open (`BL-0021`) |
| CAP-15 | UI / Input System | Let the listener steer live | Joypad edge-detection + one-control-one-parameter mapping | Every button visibly/audibly does exactly one thing | CAP-01 | MSTR-001 C4; GDS-03 §3 | **Shipped** (`FEAT-1010`, `VERIFIED`) |
| CAP-16 | Seed Management | Make every power-on/reset genuinely different | `DIV`-register-seeded, zero-guarded Galois LFSR reseed | No two sessions start identically | CAP-02 | R213; A6 (assumptions register) | **Shipped** (`FEAT-1020`, `VERIFIED`) |
| CAP-17 | Playback / Runtime System | The one continuous process everything else runs inside | VBlank-ISR-driven main loop, no states beyond "running" | Instant-on, never pauses, never exits | CAP-01 | MSTR-001 §1; GDS-01 | **Shipped** (`IP-0001`, `VERIFIED`) |
| CAP-18 | Persistence | Optionally remember something across power-off | MBC5+RAM+BATTERY save of a favorite seed/style/collection, *if adopted* | "My favorite piece is still here next time" | CAP-21 (build-tooling extension) | MSTR-001 C1/C2 (reopened, undecided), §9; R106 | **Not started** — facts gathered (R106), **adoption undecided** |
| CAP-19 | Performance & Budget Management | Keep the engine inside SM83/ROM/RAM/cycle limits | Per-frame cost discipline, ROM/WRAM budget tracking | No slowdown, no dropped frames, no build failures from overflow | All | NFR-1010/1030/1040/1050; R101/R308 | **Ongoing, cross-cutting** — not a phase, a continuous constraint every release respects |
| CAP-20 | Testing & Verification Harness | Prove every capability actually works | PyBoy headless button-drive + register/WRAM assertions | Every shipped behavior has a repeatable, objective proof | All | MSTR-001 C9; R301/R305 | **Shipped, ongoing** (`FEAT-1050`; 65/65 checks at last count, grows every release) |
| CAP-21 | Build Tooling | Turn source into a valid cartridge image | Hand-rolled two-pass label/fixup assembler + build/layout script | The ROM exists at all, reproducibly, with no external assembler | MSTR-001 C3 | R302 | **Shipped**; bank-switching extension **planned, real cost known** (R302 §8-9), not started |

## Capabilities explicitly named in the user's example list, mapped

Every category the user's request named as an example maps onto the table above: Audio Engine
(CAP-01), Composition Engine (CAP-02), Rhythm Engine (CAP-03), Harmony Engine (CAP-05), Melody
Engine (CAP-04), Style Engine (CAP-11), Evolution Engine (CAP-12), Instrument System (CAP-07),
Visual Engine (CAP-14), UI System (CAP-15), Seed Management (CAP-16), Playback System (CAP-17),
Persistence (CAP-18), Performance (CAP-19), Testing (CAP-20), Tooling (CAP-21). Two capabilities
were added beyond the example list because the shipped engine and its backlog already demand them:
CAP-06 (Sound Design/Timbre — already a distinct, shipped concern per R216/`FEAT-1060`) and CAP-08/
CAP-10 (Bad-Zone Self-Correction / Channel-Mix Control — both load-bearing, one with an open High-
severity defect that gates CAP-09's entire downstream chain).
