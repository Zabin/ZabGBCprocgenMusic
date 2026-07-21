# R305 — Emulator-Based Test Design

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored 2026-07-21
- **Supersedes:** part of `docs/research/R300-tooling-and-testing.md`

## 1. Purpose

Ground `test_rom.py`'s assertion-design choices (sound-register vs. WRAM-state assertions,
boot-frame determinism, button-sequence-driven checks) as a named, reusable test-design pattern
for `IP-0002`+.

## 2. Scope

What to assert on (register vs. WRAM mirror, per R108's write-only-register finding), and how to
structure a button-driven behavioral test.

## 3. Concepts

- **Assert on the WRAM mirror for anything write-only in hardware** (R108) — this is not merely a
  PyBoy quirk, it reflects genuine real-hardware read-only/write-only register asymmetry, so the
  pattern holds regardless of emulator/version.
- **`NR52` is the one PSG register that is both genuinely stateful and genuinely readable** — the
  correct assertion point for "is this channel making sound," distinct from "what note/parameter"
  (WRAM mirror's job).
- **Boot-frame determinism**: any assertion about power-on state must wait past the boot ROM's own
  logo-animation frames (R110, ~90 frames, empirically measured) — a test written before this was
  understood produces false failures (`IP-0001`'s own T2 initially failed for exactly this reason,
  corrected in the same package — see its VR/package doc once verified).
- **Button-sequence-driven assertions** (press → release → settle a few frames → read state) is
  the correct shape for edge-triggered input (R107) — reading state *during* the press (before
  release) risks catching a transient mid-transition value rather than the settled post-edge
  state.

### Sources
- Primary source is this project's own `IP-0001` implementation and its build-time debugging
  (the boot-frame-count discovery, the NR13/14 write-only discovery) — an emulator-specific test-
  design pattern is properly grounded in the project's own verified behavior per this skill's own
  methodology (`Claude.md` Known Good Behavior is an accepted citation class), not external
  literature, since this is toolchain-specific engineering knowledge rather than published theory.

## 4. Operational Context

`test_rom.py`'s existing structure (T1 no-emulator header checks, T2 boot-state checks using
`BOOT_FRAMES`, T3 sustained-play WRAM-mirror-based liveness checks, T4/T5 button-sequence-driven
parameter/reset checks) already implements every pattern above.

## 5. Implementation Guidance

- **`IP-0002`+ test suites should follow the same T-numbering/shape convention**: header (no
  emulator) → boot-state → sustained-behavior → button-driven-parameter → button-driven-reset,
  extended per new channel/feature rather than restructured.
- **Any test asserting a `RESULT` — dissonance score crossing a threshold, a stale-count
  incrementing, an overload flag tripping (`IP-0004`)** should drive the ROM at the specific
  preset/parameter combination expected to trigger that condition (per `09-package-verification`'s
  own rule about non-default-parameter driving), not rely on the default boot preset, which
  GDS-03 SS5 deliberately designs to be the *safest*, least-likely-to-trip-bad-zone combination.
- **Long-duration playback testing**: `IP-0001`'s T3 already drives 400 consecutive frames as a
  liveness check (NFR-1010's "thousands of frames, no hang" requirement is broader — T3 is a
  minimal instance of the same idea, not yet the full thousands-of-frames run NFR-1010 describes).
  Recommend a dedicated long-run suite (e.g. a T99-style final suite driving 10,000+ frames across
  varied parameter combinations, checking only for hangs/crashes, not specific state) once more
  channels exist to make a "does it survive a long varied run" check meaningful — not needed for
  a single-channel engine where the state space is small enough that 400 frames already exercises
  it.
- **Regression testing with fixed seeds**: already the default mode (`LFSR_SEED` is a fixed
  constant, R213) — every `test_rom.py` run is already a fixed-seed regression run by construction.
  If `IP-0002`+ adopts R213's recommended `DIV`-based boot seeding, tests must explicitly
  overwrite `LFSR_STATE` post-boot (as several already do for other WRAM fields) to keep this
  property — a concrete implication flagged here so it isn't lost when that change lands.
- **Hardware compatibility testing** (real GBC hardware, or cross-checking against SameBoy/BGB —
  R309): not currently performed; MSTR-001 §4 names real-hardware certification a deliberate
  non-goal at this vision's date. Cross-emulator checking (R309) remains available as a cheaper
  partial substitute for genuinely surprising findings, not a required step.

## 6. Feature Mapping

`test_rom.py` (all suites), NFR-1020, `IP-0004`'s future bad-zone test design.

## 7. Related Topics

R301 (the API these test patterns are built on), R108/R110 (the hardware facts that motivate each
pattern).
