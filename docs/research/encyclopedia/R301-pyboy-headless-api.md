# R301 — PyBoy Headless API

- **Tier:** R300 (tooling & verification) · **Owned by:** `02-research-tooling-and-testing`
- **Status:** ✅ Authored 2026-07-21 · **Supersedes:** part of
  `docs/research/R300-tooling-and-testing.md` (retained as superseded pointer)
- **PyBoy version pinned by this project:** 2.7.0 (matches the reference project's own pin;
  `pip install pyboy` resolved to 2.7.0 during `IP-0001`, confirmed by direct install log).

## 1. Purpose

Ground `test_rom.py`'s use of PyBoy against the real, versioned API surface, not assumption.

## 2. Scope

Headless (`window='null'`) driving: memory access (including sound registers), button input,
frame/tick control.

## 3. Concepts

- **Memory access**: `pyboy.memory[addr]` reads/writes Game Boy memory directly, including
  memory-mapped I/O registers — confirmed empirically during `IP-0001` (`pb.memory[0xFF26]` for
  `NR52` behaves correctly) and consistent with the official API documentation's own description
  [PyBoy API documentation, docs.pyboy.dk](https://docs.pyboy.dk/).
- **Tick/frame control**: `pyboy.tick()` advances one frame; in current PyBoy it returns `True`
  until emulation stops, `set_emulation_speed(0)` removes the real-time throttle for headless
  batch-driving [docs.pyboy.dk](https://docs.pyboy.dk/); [PyBoy GitHub — pyboy.py source](https://github.com/Baekalfen/PyBoy/blob/master/pyboy/pyboy.py).
- **Button input**: `pyboy.button_press(name)`/`pyboy.button_release(name)` (used throughout
  `test_rom.py`) is the current-generation convenience API; older PyBoy versions used
  `send_input()` with `WindowEvent` constants — **do not use the `WindowEvent` API in new code**,
  it is the pre-2.0 convention [PyBoy Wiki — Migrating from v1.x.x to v2.0.0](https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0).
- **Window mode**: "dummy" and "headless" window types were merged into `'null'` in the 2.x line
  — `test_rom.py`'s `window='null'` is the current-correct headless mode, not a legacy alias
  [PyBoy Wiki — Migrating from v1.x.x to v2.0.0](https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0).
- **`sound_emulated`**: confirmed via direct `IP-0001` testing that `sound_emulated=True` is
  required (or at least sufficient) for `NR52`'s active-channel bits to reflect real state —
  the reference project ran with `sound_emulated=False` throughout (it never asserted on audio),
  so this project's own use is new-tested ground, not inherited.

### Sources
- [PyBoy API documentation (docs.pyboy.dk)](https://docs.pyboy.dk/)
- [PyBoy GitHub — Baekalfen/PyBoy](https://github.com/Baekalfen/PyBoy)
- [PyBoy Wiki — Migrating from v1.x.x to v2.0.0](https://github.com/Baekalfen/PyBoy/wiki/Migrating-from-v1.x.x-to-v2.0.0)
- Project's own empirical confirmation (`IP-0001` install + test run), for the version pin and
  the `sound_emulated` finding specifically.

## 4. Operational Context

`test_rom.py` already uses exactly this confirmed-current API set (`memory[]`, `tick()`,
`button_press`/`button_release`, `set_emulation_speed(0)`, `window='null'`,
`sound_emulated=True`) — no drift found between this topic and the shipped harness.

## 5. Implementation Guidance

- Keep using `button_press`/`button_release`/`memory[]` — do not "upgrade" to `send_input`/
  `WindowEvent`, which would be a regression to the pre-2.0 API per the migration guide above.
- Any future PyBoy version bump should be re-checked against the Migration wiki before assuming
  API stability — pin the version explicitly in project docs (this topic) whenever it changes.

## 6. Feature Mapping

All of `test_rom.py`, NFR-1020, `IP-0001`'s T1-T5 suites.

## 7. Related Topics

R108 (what the memory reads this API performs actually mean), R305 (test-design patterns built on
top of this API).
