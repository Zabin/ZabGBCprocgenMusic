# Product Roadmap 04 — Release Roadmap

- **Grounded in:** `02-capability-map.md`, `03-capability-dependency-graph.md`, the existing
  Master Build Plan (`docs/implementation/00-master-build-plan.md`) and backlog
- **Status:** ✅ Authored 2026-07-22

Fourteen releases, `R0` through `R13`, tracing the full arc from empty ROM to release candidate.
**`R0`-`R2` are already shipped** — included for traceability and continuity (per the guiding
principle against throw-away work: nothing here re-does or discards what already exists), not as
new work. `R3` onward is genuinely new roadmap content. Every release satisfies the guiding
principles: compiles, runs, produces a real audible/visible improvement, is testable on emulator
(hardware cadence per `08-development-strategy.md`), introduces no large unfinished system, and
traces to Vision/research.

## R0 — Skeleton (shipped, historical)

- **Purpose:** Prove the build/verify toolchain works at all before any music exists.
- **Capabilities introduced:** CAP-01 (partial, pulse A only), CAP-17, CAP-20, CAP-21.
- **User-visible improvement:** A GBC boots and produces one audible pulse-channel tone.
- **Completion criteria:** `IP-0001`'s narrower single-channel slice, `VERIFIED` (`VR-0001`).
- **Status:** ✅ Shipped, `VERIFIED`.

## R1 — Foundation (shipped)

- **Purpose:** The first genuinely playable slice — full 4-channel generative engine, input
  steering, autonomous bad-zone recovery, minimal visualizer.
- **Capabilities introduced:** CAP-01 (complete), CAP-02, CAP-03, CAP-04, CAP-07, CAP-08, CAP-15,
  CAP-16, CAP-14 (MVP).
- **User-visible improvement:** Continuous 4-channel generative chiptune, steerable by all 6
  controls, self-recovering from bad-sounding states, with a reactive tile/palette display.
- **Architecture changes:** GDS-00/01/03/07 authored; `music_engine.py`/`input_map.py`/
  `visuals.py`/`build_rom.py` established.
- **Testing goals:** Headless button-drive + register/WRAM assertions for every behavior (T1-T10).
- **Completion criteria:** All 7 packages (`IP-0001`-`IP-0007`) `VERIFIED`; `10-integration-review`
  run.
- **Known risks realized:** `BL-0019` (channel-mix unwired, High), `BL-0017` (overload threshold
  unreachable, Medium-High) — both open, both block this roadmap's critical path (see R3).
- **Status:** ✅ Shipped, `VERIFIED`, integration-reviewed. **`11-release-readiness` GO withheld**
  per the integration review's own recommendation until `BL-0019` is remediated.

## R2 — Sound Design Layer (shipped)

- **Purpose:** Layer expressive articulation (arpeggio, vibrato, portamento, duty-cycle) onto R1's
  held notes, per R216's concrete guidance.
- **Capabilities introduced:** CAP-06.
- **User-visible improvement:** Notes glide, wobble, and imply chords instead of sounding static;
  duty-cycle varies per onset.
- **Testing goals:** Suite grew to 65/65 (new suite T11); two clean multi-thousand-frame stress
  runs.
- **Completion criteria:** `IP-1060`/`IP-1061` `COMPLETE`.
- **Status:** ✅ Shipped and **independently verified** ([VR-1060](../implementation/verification/VR-1060-arpeggio-and-duty-cycle.md),
  [VR-1061](../implementation/verification/VR-1061-vibrato-and-portamento.md), 2026-07-25 —
  fresh-session `09-package-verification`, both non-default tunable-parameter combinations
  re-driven live per this project's own verification standard). Two Low-Medium doc-coherence
  findings filed (`BL-0025`/`BL-0026`, package-doc text vs. shipped design) and one Low-Medium
  test-coverage finding (`BL-0027`, portamento has no dynamic register-level test) — none block
  this release; none are functional defects.

---

**Everything below this line is new roadmap content — not yet built.**

## R3 — Integrity Remediation

- **Purpose:** Close the two open defects blocking this roadmap's entire critical path before any
  new capability is layered on top of a known-broken control and a known-dead detection path.
- **Capabilities introduced:** none new — repairs CAP-10 (channel-mix), hardens CAP-08 (overload
  threshold).
- **Capabilities expanded:** CAP-10 goes from broken to functional; CAP-08's overload signal
  becomes reachable.
- **User-visible improvement:** The Start button visibly/audibly changes which channels play; the
  visualizer's bad-zone palette can now actually be triggered by overload, not just dissonance/
  stuck states.
- **Architecture changes:** None — both remediation packages (`IP-9010`, `IP-9020`) are already
  fully specified against the existing architecture.
- **Testing goals:** New assertions for channel-mix gating and a driven-overload scenario;
  full-suite regression.
- **Completion criteria:** `IP-9010`/`IP-9020` `VERIFIED`; `10-integration-review` re-run clean;
  `11-release-readiness` GO becomes possible for the Foundation bucket.
- **Potential risks:** `IP-9010`'s own package doc flags a real open design question (should an
  excluded channel's dissonance still count toward bad-zone scoring) needing an explicit answer
  during implementation, not a guess. **Resolved 2026-07-25:** left dissonance scoring reading
  every pitched channel's degree unconditionally (documented choice, not silently defaulted — see
  `_emit_channel_gen`'s own docstring and `IP-9010`'s implementation commit).
- **Expected demonstration:** Press Start repeatedly, hear channels drop in/out; drive max tempo +
  density, watch the visualizer's palette actually flip to bad-zone red from overload.
- **Status (2026-07-25):** **G3 authorized and both packages built** this session — `IP-9010`
  (`CHMIX_MASKS` channel-mix gating) and `IP-9020` (`OVERLOAD_THRESHOLD` 20→7, empirically
  recalibrated) both `COMPLETE`, 77/77 full suite, 8200-frame stress runs clean. **Not yet
  independently verified** — built in the same session that authorized them, so
  `09-package-verification`'s standing fresh-session-independence rule applies; owed to a future
  session, same as `IP-1060`/`IP-1061` were before this run. Once verified: `10-integration-review`
  re-run, then this release's completion criteria (below) are met.

## R4 — Multi-Scheme Foundation

- **Purpose:** Introduce the first real structural alternative to the shipped LFSR-walk
  generation, per `BL-0020`/`ADS-100`.
- **Capabilities introduced:** CAP-09.
- **Capabilities expanded:** CAP-10 (consumed by scheme selection, riding its mask-byte space per
  `ADR-0001`).
- **User-visible improvement:** A pitched channel can audibly switch between "wandering melody"
  and "cycling motif" character, selectable per-channel.
- **Architecture changes:** `ADS-100`'s "Scheme E" design implemented; `CHMIX_IDX`'s preset space
  gains scheme-selection bits.
- **Testing goals:** Assert scheme-selection bits produce the correct generation behavior per
  channel; regression on R1-R3.
- **Completion criteria:** New implementation package(s) `VERIFIED`.
- **Potential risks:** WRAM/ROM budget for a second scheme's data tables (flagged by `ADS-100`
  itself as needing a budget check).
- **Expected demonstration:** Toggle a channel between Scheme W and Scheme E live, hear a clearly
  different melodic character.
- **Dependency:** R3 (CAP-10 must be functional first).

## R4.5 — Cart-Shape Decision Checkpoint

- **Purpose:** Added by this package's own `10-final-roadmap-review.md` (finding #1) — make the
  MBC5/bank-switching adoption call *before* Milestones B-D's cumulative new data tables (Scheme
  E, style presets, song-form/emotional state) create ROM-budget pressure, rather than bundling
  the decision late at R11 where it originally sat and risking an unplanned mid-roadmap
  architecture emergency.
- **Capabilities introduced:** none — a decision checkpoint, not a build.
- **User-visible improvement:** none directly; this release exists purely to de-risk everything
  after it.
- **Completion criteria:** A recorded, dated `03-architecture-design-synthesis` decision on
  MBC5+SRAM adoption (GO or NO-GO — both are valid, complete outcomes) using the facts R106/R302
  already gathered; no new research needed.
- **Potential risks:** None beyond the decision itself being deferred past this checkpoint, which
  would defeat its purpose — flagged as the one failure mode to watch for.
- **Dependency:** R4 (best measured once Stream 1's first new data tables exist and a real
  ROM-budget trajectory is visible).

## R5 — Genre-Aware Style Presets

- **Purpose:** Turn R219's genre-feasibility research into real, selectable parameter regions.
- **Capabilities introduced:** CAP-11.
- **Capabilities expanded:** CAP-03/CAP-06/CAP-09 (all read by style presets).
- **User-visible improvement:** A style control (mapping TBD at architecture time — likely riding
  existing preset-index infrastructure) audibly shifts the whole mix toward a recognizable genre
  reference (e.g. "techno" vs. "ambient") using only R219's high-confidence tier.
- **Testing goals:** Assert each style preset produces its documented parameter combination;
  A/B-listenable regression (content-review, not just automated).
- **Completion criteria:** At least 3 high-confidence styles (R219 tier 1) implemented and
  independently verified.
- **Potential risks:** Scope creep toward R219's low-confidence tier (jazz/orchestral) — explicitly
  out of scope for this release, named so it isn't quietly attempted.
- **Expected demonstration:** Cycle through 3+ styles, each clearly distinct by ear.
- **Dependency:** R4.

## R6 — Song-Form & Style-Drift Engine

- **Purpose:** Give a session a shape over time, per R220's parameter-envelope finding.
- **Capabilities introduced:** CAP-12.
- **Capabilities expanded:** CAP-03/CAP-04/CAP-08 (all driven by the new state machine).
- **User-visible improvement:** A recognizable intro→build→peak→breakdown arc audible over a
  multi-minute session, not flat continuous texture.
- **Architecture changes:** New state-machine mechanism sharing its shape with `IP-0007`'s
  bad-zone loop (per R220's own finding) — a real, small architecture addition.
- **Testing goals:** Assert state transitions occur on schedule and drive the correct parameter
  envelopes; long-run (8000+ frame) regression for stability.
- **Completion criteria:** State machine `VERIFIED`; closes the song-form half of `BL-0010`.
- **Potential risks:** Interaction with the bad-zone recovery loop (both may want to bias the same
  parameters simultaneously) — needs an explicit precedence rule, flagged for architecture design.
- **Expected demonstration:** Let a session run uninterrupted for several minutes; a listener can
  narrate the arc without prompting.
- **Dependency:** R1 only (parallelizable with R3-R5, per the dependency graph).

## R7 — Emotional / Energy Layer

- **Purpose:** Make the engine's internal state legible as mood, per R221's valence-arousal
  finding.
- **Capabilities introduced:** CAP-13.
- **Capabilities expanded:** CAP-12 (natural sequel, same state-machine shape).
- **User-visible improvement:** Nothing new to *hear* by itself (this is a read-layer over
  existing sound) — the improvement is a new, tested WRAM signal ready for R9's visual work and
  future style/energy steering.
- **Testing goals:** Assert the valence/arousal derivation matches expected values across a matrix
  of tempo/density/scale/dissonance-score combinations.
- **Completion criteria:** Read-layer `VERIFIED`; this release is legitimately test-only-visible
  if taken alone — **should ship bundled with R6 or R9** rather than standalone, since it alone
  produces no audible/visible change (flagged explicitly in `10-final-roadmap-review.md`).
- **Dependency:** R6.

## R8 — Genre Blending

- **Purpose:** Interpolate between R5's style regions using R6's drift mechanism, per the user's
  original "solo or in combination" framing (`BL-0020`) and the "hybrid genres" vision item.
- **Capabilities introduced:** none new — combines CAP-11 + CAP-12.
- **User-visible improvement:** A session can audibly drift from one genre reference toward
  another over time, rather than only hard-cutting between presets.
- **Testing goals:** Assert interpolated parameter values land between the two endpoint styles'
  values at expected drift progress points.
- **Completion criteria:** At least one demonstrable blend pair `VERIFIED`.
- **Potential risks:** Parameter interpolation producing an audibly "in-between-and-bad" state
  rather than a musically coherent blend — needs `09-content-review`, not just automated assertion.
- **Dependency:** R5 + R6.

## R9 — Visual Evolution & Audio-Visual Synchronization

- **Purpose:** Extend R1's visualizer MVP to react to style (R5/R8) and mood (R7), per MSTR-001
  §9's still-open visual-evolution thread.
- **Capabilities expanded:** CAP-14.
- **User-visible improvement:** The screen visibly changes character (palette/animation) with
  style and mood, not only tempo/activity/bad-zone.
- **Prerequisite not yet satisfied:** the visual-evolution research thread (MSTR-001 §9) has not
  been run — **this release cannot be architected until that research lands**; named explicitly
  so it isn't skipped under roadmap pressure.
- **Testing goals:** Assert palette/animation state matches the current style/mood signal; pixel-
  level content review (same discipline `VR-0006` already established).
- **Completion criteria:** Visual response to at least one style dimension and one mood dimension,
  `VERIFIED`.
- **Potential risks:** ROM/VRAM budget for a richer palette/tile set (R9's own research should
  quantify this before design starts).
- **Dependency:** R5, R7 (bottleneck convergence point, per the dependency graph).

## R10 — Interactive Control Expansion

- **Purpose:** Re-examine the 6-control mapping now that style/scheme selection exist as new
  steerable dimensions.
- **User-visible improvement:** Style/scheme become directly steerable, not only autonomously
  drifting.
- **Architecture changes:** Likely reuses existing preset-index infrastructure (no new physical
  control — R217's own finding that all 6 controls are already assigned) rather than adding input
  surface.
- **Testing goals:** Same edge-triggered-mapping test discipline as the existing 6 controls.
- **Completion criteria:** New steering path `VERIFIED`, existing 6-control behavior unregressed.
- **Dependency:** R5, R8.

## R11 — Persistence Layer (conditional)

- **Purpose:** Optionally remember a favorite seed/style/collection across power-off, per MSTR-001
  §9 and R106's now-gathered facts.
- **Capabilities introduced:** CAP-18.
- **Explicit precondition:** **R4.5's decision must have been GO.** (Moved earlier per
  `10-final-roadmap-review.md` finding #1 — this release now only builds the save *feature*, the
  adoption *decision* itself already happened at R4.5.) If R4.5 was NO-GO, this release is struck
  from the roadmap entirely, not deferred indefinitely — an explicit no is a valid outcome.
- **User-visible improvement (if adopted):** A favorite piece/style survives power-off.
- **Testing goals:** Headless save/reload assertion via PyBoy's native battery-RAM handling (R106
  §3 already confirms this is testable without new tooling).
- **Completion criteria:** Save/load `VERIFIED` across a simulated power-cycle.
- **Dependency:** R4.5 = GO.

## R12 — Performance & ROM-Budget Optimization

- **Purpose:** Formalize the CAP-19 discipline into a dedicated hardening pass before RC — audit
  every release's cumulative cost against SM83 cycle/ROM/RAM budgets.
- **User-visible improvement:** None new by design — the improvement is confidence that R0-R11's
  cumulative addition hasn't silently degraded frame timing or approached the ROM ceiling.
- **Testing goals:** Cycle-cost audit per `badzone_tick`/`engine_tick`/state-machine additions;
  ROM byte-budget audit; long-duration stress run repeated at the full, final feature set.
- **Completion criteria:** No frame-budget or ROM-budget violation found, or every violation found
  has a named remediation package.
- **Dependency:** All prior releases in the target scope.

## R13 — Release Candidate

- **Purpose:** Final hardening — full regression, documentation completeness, hardware-compat
  validation cadence (per `08-development-strategy.md`), `11-release-readiness`'s actual GO/NO-GO
  call.
- **Completion criteria:** Every item in `09-release-exit-criteria.md` satisfied; `10-integration-
  review` clean across the full package; `11-release-readiness` GO recorded.
- **Dependency:** R3-R12 (whichever subset was actually pursued — this roadmap does not mandate
  every release above ships before an RC is considered; see `05-milestone-definitions.md` for
  which subsets constitute a legitimate RC candidate).
