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

## 6. Feature Mapping

`test_rom.py` (all suites), NFR-1020, `IP-0004`'s future bad-zone test design.

## 7. Related Topics

R301 (the API these test patterns are built on), R108/R110 (the hardware facts that motivate each
pattern).
