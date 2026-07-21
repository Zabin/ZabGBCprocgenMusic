# R300 — Tooling & Verification Encyclopedia

- **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored, 2026-07-21 (grounds GDS-09, the verification harness)

## What's reused verbatim from the reference project

- **The Python-only assembler pipeline shape**: `gbc_lib.py`'s `ROM` class (opcode emitters,
  label/fixup resolution, `set_header`) is reused unmodified — confirmed by direct read of the
  file (225 lines, no game-specific content in it at all — it is already generic).
- **The headless-PyBoy harness shape**: `PyBoy(rom_path, window='null', sound_emulated=...)`,
  `pb.set_emulation_speed(0)`, drive with `pb.tick()` per frame, hold buttons via
  `pb.button_press`/`pb.button_release` (confirmed present in the reference `test_rom.py`'s
  button-driving helpers), read arbitrary memory via `pb.memory[addr]` (confirmed at
  `test_rom.py:316` reading `0xFF40` LCDC — i.e. this indexing already reads hardware I/O
  registers, not just WRAM, so no new PyBoy API surface is needed for sound-register assertions).
- **The pass/fail ledger convention** (`check(name, cond, detail)`, PASS/FAIL counters, a
  `test_results.txt` dump) — reused as-is, it's presentation, not domain logic.
- **Repo-relative paths** (`Path(__file__).resolve().parent`-derived `ROM_PATH`) — reused, avoids
  the exact staleness class the reference project fixed in its own `IP-9010`.

## What's new

- **Assertion vocabulary.** The reference suite's checks are almost entirely about WRAM game
  state, VRAM tile/tilemap content, and OAM sprite entries. Driftune's suite instead asserts
  primarily on: `NR52` (`0xFF26`, per-channel active status), `NR51`/`NR50` (panning/volume),
  each channel's frequency/duty/envelope registers, and a WRAM mirror of engine-internal state
  (current scale/tempo/dissonance-score/bad-zone-flag — exact addresses: GDS-07). This is a new
  *vocabulary* of what to check, not a new *mechanism* — same `pb.memory[addr]` reads, same
  `check()` ledger.
- **Button-sequence-driven behavioral assertions**, per MSTR-001 C9: a test drives a named
  sequence (e.g. hold RIGHT for N frames, then read the tempo register/WRAM mirror and assert it
  increased) rather than only checking static post-boot state. The reference suite already does
  this for movement/menu navigation (its T7/T14 button-driven suites) — the *pattern* transfers
  directly, only the buttons-to-behavior mapping is new (GDS-03's own deliverable).
- **A deliberate "drive into the bad zone, then Select, then assert recovery" test shape** — no
  equivalent test shape exists in the reference project (it has no analogous recoverable-bad-state
  mechanic). This is new test-design work for `09-package-verification` once GDS-03's bad-zone
  metric and reset behavior are concrete.
- **Determinism-for-testing.** MSTR-001 C6 requires determinism only where testing needs it (a
  fixed seed reproducing a fixed sequence). The reference project's own `worldgen.py` established
  the pattern of a Python-side "oracle" mirroring the on-ROM generation logic so tests can assert
  parity without re-implementing SM83 disassembly by hand — the same oracle-parity testing pattern
  is recommended for Driftune's generation routine wherever a test needs to predict "what note
  comes next" rather than just "did some plausible register change happen."

## Confirmed constraints / risks to carry into GDS-06 (NFRs)

- `sound_emulated=False` was used throughout the reference project's harness (it never checked
  audio). Whether Driftune's tests need `sound_emulated=True` for register state to update
  correctly (vs. register writes being readable regardless of the emulated-audio flag) is
  **unconfirmed** — flagged as a first-implementation-package smoke-test item, not assumed either
  way here (`sound_emulated` in PyBoy governs whether audio is actually mixed/output, not
  necessarily whether the underlying PSG register model updates; the safe assumption until tested
  is that register *state* updates regardless, since the DMG/CGB APU model is emulated for
  accuracy independent of whether samples are produced, but this must be verified against the
  actual PyBoy version pinned by this project, not assumed from the reference project's disuse of
  the flag).
- No change to the ROM-build gate (G5): `build_rom.py` (or this project's equivalent) must still
  produce a fixed-size, valid-header ROM every time, same as the reference project.
