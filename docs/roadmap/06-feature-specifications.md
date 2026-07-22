# Product Roadmap 06 — Feature Specifications

- **Grounded in:** `04-release-roadmap.md`, `02-capability-map.md`
- **Status:** ✅ Authored 2026-07-22
- **Note on grain:** these are **catalog-grain** feature entries (the `05-feature-decomposition`
  `FEAT-xxxx` level of detail) — planning input for future `06-feature-specification` full
  20-field `FS-xxx` documents, not a substitute for them. IDs use a new `RM-xxxx` prefix (Roadmap
  feature) to avoid colliding with the live `FEAT-xxxx` numbering until each is formally decomposed
  by `05-feature-decomposition` at build time.

## R3 — Integrity Remediation

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-3001 | Channel-mix gating | Wire `CHMIX_IDX` to a real per-channel activity mask | Start button finally does something audible | None (fix to shipped code) | Critical | Each preset visibly/audibly mutes the documented channel subset; full regression green | CAP-10 | MSTR-001 C4; FR-1000/1010 | Low (already fully specified, `IP-9010`) | S |
| RM-3002 | Overload threshold recalibration | Make `BAD_OVERLOAD` reachable under realistic play | Bad-zone recovery becomes complete, not 2/3 functional | None | High | Overload flag observably sets under a driven max-tempo/density scenario | CAP-08 | MSTR-001 C5 | Low (already fully specified, `IP-9020`) | S |

## R4 — Multi-Scheme Foundation

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-4001 | Scheme E (motif-cycling) generation | Second selectable generation approach per `ADS-100` | A channel can sound structurally different, not just parametrically different | R3 (CAP-10) | High | Scheme-select bits produce the documented motif-cycling behavior, independently verified | CAP-09 | `BL-0020`; `ADS-100` | Medium (new generation logic, ROM-budget question flagged) | M |
| RM-4002 | Per-channel scheme selection UI wiring | Let `CHMIX_IDX`'s spare bits carry scheme choice | (enabler, no direct player-facing UI yet — full control comes at R10) | RM-4001 | Medium | Scheme selection persists correctly across Select-reset | CAP-09, CAP-10 | `ADR-0001` | Low | S |

## R5 — Genre-Aware Style Presets

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-5001 | High-confidence style preset table | Encode R219's tier-1 genres as parameter-region presets | Recognizable genre character on demand | R4 | High | ≥3 styles independently verified as producing their documented parameter combination | CAP-11 | R219; MSTR-001 §9 | Medium (content-tuning risk — needs `09-content-review`, not just automated pass) | M |
| RM-5002 | Style preset selection mechanism | Expose style presets to a control path | (enabler for R10's full UI; may ship test-only first) | RM-5001 | Medium | Style index steps correctly, wraps correctly, survives reset | CAP-11, CAP-15 | GDS-03 §3 | Low | S |

## R6 — Song-Form & Style-Drift Engine

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-6001 | Song-form state machine | Drive tempo/density/scale through an intro/build/peak/breakdown envelope | A session has audible shape, not flat texture | R1 only | High | State transitions occur on the documented schedule; a full arc is independently verified across a long run | CAP-12 | R220; `BL-0010` | Medium (interaction with bad-zone recovery loop — needs an explicit precedence rule) | M |
| RM-6002 | Bad-zone / song-form precedence rule | Resolve which mechanism wins when both want to bias the same parameter simultaneously | Consistent, non-jarring behavior even in edge cases | RM-6001 | High | No observed conflict/oscillation between the two mechanisms across an 8000+ frame stress run | CAP-08, CAP-12 | GDS-03 §4/§5 | Medium (genuinely new design question, not yet answered anywhere) | S |

## R7 — Emotional / Energy Layer

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-7001 | Valence-arousal read-layer | Derive a mood signal from existing tracked state | No direct audible change alone — the enabler for R9 | R6 | Medium | Derived values match expected valence/arousal across a documented test matrix | CAP-13 | R221 | Low (read-only layer, no new generation logic) | S |
| RM-7002 | Emotion-region naming | Map named emotions (calm/tense/etc.) to valence-arousal quadrants | Future UI/visual work has a real vocabulary to consume | RM-7001 | Low | Every named emotion in MSTR-001 §9's list maps to exactly one quadrant region, documented | CAP-13 | MSTR-001 §9, §12 | Low | XS |

## R8 — Genre Blending

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-8001 | Style interpolation | Blend between two style presets' parameter values over a drift window | A session can musically migrate between genre references | R5 + R6 | Medium | At least one blend pair verified both by assertion (interpolated values correct) and by content review (musically coherent, not "in-between-and-bad") | CAP-11, CAP-12 | `BL-0020`; MSTR-001 §5 | Medium (musical-coherence risk is real and not fully automatable) | M |

## R9 — Visual Evolution & Audio-Visual Synchronization

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-9000 | Visual-evolution research pass | **Hard prerequisite** — ground ROM/VRAM budget and sync technique before any design | Indirect — prevents a mis-scoped design | None (research, not implementation) | Critical (blocks the rest of this release) | New R2xx/R1xx topic(s) authored, citation-backed | CAP-14 | MSTR-001 §9 | N/A (research task) | S |
| RM-9001 | Style-reactive palette/animation | Visualizer responds to the active style/blend state | Screen visibly matches genre character | RM-9000, R5/R8 | Medium | Palette/animation state independently verified against style signal | CAP-14 | MSTR-001 C8; R205/R208 | Medium (ROM/VRAM budget, per RM-9000) | M |
| RM-9002 | Mood-reactive palette/animation | Visualizer responds to the valence-arousal signal | Screen visibly matches mood | RM-9000, R7 | Medium | Palette/animation state independently verified against mood signal | CAP-14 | MSTR-001 C8 | Medium | M |
| RM-9003 | Accessibility luminance pass | Close `BL-0021`'s narrow calm/bad-zone luminance gap while palette work is already in flight | Bad-zone state reads clearly under color-vision deficiency, not just by hue | RM-9001 or RM-9002 (ride either) | Low | Luminance gap widened or a shape-based secondary signal added, per `BL-0021`'s own recommendation | CAP-14 | R208 | Low | XS |

## R10 — Interactive Control Expansion

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-10001 | Style/scheme steering control | Let an existing control directly steer style/scheme, not only autonomous drift | Direct player agency over genre character | R5, R8 | Medium | New steering path verified; existing 6-control behavior unregressed | CAP-11, CAP-15 | MSTR-001 C4; R217 | Medium (control-mapping conflicts must be avoided — R217 confirms no spare physical control exists) | S |

## R4.5 — Cart-Shape Decision Checkpoint

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-4501 | Cart-shape adoption decision | Explicit architecture GO/NO-GO on MBC5(+SRAM), moved early per `10-final-roadmap-review.md` finding #1 | Determines whether R11 exists and de-risks R5-R8's ROM-budget trajectory | R4 (real budget trajectory visible); R106/R302 facts already gathered | Critical | A recorded, dated architecture decision — either outcome is valid | CAP-18, CAP-21 | MSTR-001 C1/C2 | N/A (decision, not build) | N/A |

## R11 — Persistence Layer (conditional on R4.5 = GO)

| ID | Name | Purpose | Player Value | Dependencies | Priority | Acceptance Criteria | Capabilities | Vision Refs | Risk | Size |
|---|---|---|---|---|---|---|---|---|---|---|
| RM-11002 | Favorite-seed/style save | Persist one favorite seed+style across power-off | "My favorite piece is still here" | RM-4501 = GO | Low | Save/reload verified across a simulated power-cycle via PyBoy's native battery-RAM handling | CAP-18, CAP-21 | MSTR-001 §9 | Medium (genuine new build-tooling surface, per R106 §5) | M |

**Sizes:** XS = under a day-equivalent of focused implementation, S = one implementation package,
M = two-to-three packages or one materially complex package, L = a multi-package tranche (none
sized L in this pass — per the guiding principle against large unfinished systems, anything
sizing L should be split further at `07-implementation-planning` time, not accepted here).
