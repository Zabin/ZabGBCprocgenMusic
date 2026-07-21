# R309 — Emulator Comparison & Debugging Tools

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 9, items 97-100 (emulator comparison, SameBoy
  debugging, BGB debugger, real hardware testing); items 101-104 (audio verification, regression
  testing with fixed seeds, long-duration playback testing, hardware compatibility testing) are
  covered by R305, cross-referenced rather than repeated here.

## 1. Purpose
Ground manual/interactive debugging options beyond PyBoy's headless harness (R301/R305) — useful
when a `test_rom.py` failure needs human-in-the-loop investigation.

## 2. Scope
SameBoy and BGB as cross-check/debugging emulators distinct from PyBoy's headless-automation role.

## 3. Concepts
- **SameBoy**: accuracy-focused (GB/GBC/SGB), "completely passes many test ROM suites, including
  all of mooneye-gb's test suite, Wilbert Pol's tests and blargg's test ROMs," with "sample-
  accurate sound emulation" and "T-cycle accurate... LCD timing" — plus "an advanced text-based
  debugger with an expression evaluator, disassembler, conditional breakpoints, conditional
  watchpoints, backtracing" [SameBoy — Core Emulation Features](https://sameboy.github.io/features/); [SameBoy GitHub](https://github.com/LIJI32/SameBoy).
- **BGB**: a Windows/Wine GB/GBC emulator+debugger with "accurate/high quality sound emulation
  with bandlimited synthesis," accurate video timing, and a debugger supporting cheat-code
  creation and ROM inspection [BGB homepage](https://bgb.bircd.org/).
- Both are **independent implementations from PyBoy** — genuinely useful as a cross-check: if
  `test_rom.py` (PyBoy-based) shows unexpected behavior, reproducing it in SameBoy or BGB
  distinguishes a real ROM bug from a PyBoy-specific emulation quirk (the same independence
  principle `09-package-verification` already applies at the process level, applied here at the
  tooling level).

### Sources
- [SameBoy — Core Emulation Features](https://sameboy.github.io/features/)
- [SameBoy — GitHub (LIJI32/SameBoy)](https://github.com/LIJI32/SameBoy)
- [BGB GameBoy Emulator homepage](https://bgb.bircd.org/)

## 4. Operational Context
Not currently used — this project's entire verification pipeline is PyBoy-based (R301/R305). No
cross-emulator check has been performed on any shipped package yet.

## 5. Implementation Guidance
- **Recommend a SameBoy (or BGB) manual cross-check as part of `09-package-verification`'s own
  workflow** whenever a `test_rom.py` result is surprising or a finding is hard to explain from
  PyBoy's behavior alone — not a mandatory step for every package (would slow down the normal
  headless-first workflow this project is built around), but a named, available escalation path.
  This is a process recommendation for `09-package-verification`'s own SKILL.md to consider
  citing, not a change to the automated gate.
- **Real hardware testing** (flashing an actual GBC cartridge) is explicitly out of scope per
  MSTR-001 §4 ("real-hardware certification... not promised yet, emulator verification is the
  gate") — this topic does not recommend changing that; it's listed in the user's original
  request but the project's own vision already answers it deliberately.

## 6. Feature Mapping
No current `IP-xxxx` — a process/tooling recommendation for `09-package-verification`.

## 7. Related Topics
R301 (PyBoy, the primary automated tool this topic's tools would cross-check against), R305 (test
design — the sibling topic covering audio verification/regression/long-duration/hardware-
compatibility testing directly).
