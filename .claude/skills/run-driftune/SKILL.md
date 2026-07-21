---
name: run-driftune
description: Build, launch, drive, and screenshot/probe Driftune — the Game Boy Color ROM built by this repo's Python assembler pipeline whose primary purpose is real-time procedurally-generated chiptune music — using PyBoy headless. Use when asked to build the ROM, run the engine, smoke-test it, take screenshots, read sound registers, press buttons/drive the generator's parameters, or run the ROM test suite. Utility skill outside the numbered pipeline; the pipeline's stage-08/09/10 skills call it for their G5 permanent gates and emulator evidence.
---

# Run Driftune

Driftune is a GBC ROM assembled entirely by Python: `build_rom.py` imports the content and logic
modules (`tiles.py`, `patterns.py`, `music_data.py`, `music_engine.py`, `visuals.py`,
`input_map.py`, via the `ROM` class in `gbc_lib.py`) and writes `Driftune.gbc`. Verification is
**PyBoy** headless — sound-register assertions, memory-state assertions, and screenshots; no real
hardware needed. Unlike a typical game ROM, the primary thing under test here is *what the engine
is doing to the four sound channels* (NR10-NR52) at any given moment, not just what's on screen.

All paths are repo-relative (no absolute/hardcoded paths anywhere in the pipeline). Python 3 with
`pyboy` installed (`pip install pyboy numpy`); `pillow` is optional (screenshots degrade to
diagnostics-only without it — no check depends on it).

## Build

```bash
python3 build_rom.py Driftune.gbc
# expected: "Wrote <N> bytes → Driftune.gbc"
```

`build_rom.py` takes the output path as `argv[1]` (defaults to `Driftune.gbc` if omitted). A
successful build matches the committed ROM-size/header contract GDS-07 records. The checked-in
`Driftune.gbc` at the repo root (once one exists) is the shipped artifact — don't overwrite it
except as a deliberate, committed release step.

## Test (the G5 permanent gate)

```bash
python3 test_rom.py
# expected: "RESULTS: N/N passed   0 failed" (N grows as packages add checks)
```

`test_rom.py` is a single self-running script (not pytest), run from the repo root — it derives
`ROM_PATH`/`RAM_PATH` from its own location (`BASE = Path(__file__).resolve().parent`), no
absolute paths or manual directory setup needed. Suites are organized by engine concern, e.g.:
T1 (header) · T2 (VRAM tiles/visualizer patterns) · T3 (LCDC) · T4 (engine state machine) · T5
(APU/channel register writes) · T6 (generation algorithm — scale/tempo/density) · T7 (joypad/
button-to-parameter mapping) · T8 (bad-zone detection) · T9 (Select reset-to-good-state) · T10
(SRAM save/load, if persisted state exists) — adjust the actual suite list to what the project
really ships; the numbering convention, not the content, is what's fixed. It writes
`test_results.txt`. It boots PyBoy repeatedly; a minute or more is normal. **The suite handles its
own `.ram`/`.sav` cleanup** — no manual `rm` needed before a fresh run.

## Drive the engine / screenshot / read sound registers (agent path)

```python
from pyboy import PyBoy
pb = PyBoy('Driftune.gbc', window='null', sound_emulated=False)   # repo-relative
pb.set_emulation_speed(0)
for _ in range(180): pb.tick()            # boot to the generating state (or straight there if the engine has no title screen)

pb.button('start'); [pb.tick() for _ in range(30)]   # e.g. title/init -> generating
pb.button('right', delay=60); [pb.tick() for _ in range(60)]  # hold right ~1s — steer a music parameter (mapping is TBD at architecture stage)
pb.button('select'); [pb.tick() for _ in range(30)]  # bad-zone reset to good starting state

pb.screen.image.save('shot.png')          # 160x144 PIL image (needs Pillow; use pb.screen.ndarray otherwise)

# Sound registers — the primary assertion surface for this project:
nr10 = pb.memory[0xFF10]   # channel 1 sweep
nr11 = pb.memory[0xFF11]   # channel 1 length/duty
nr13, nr14 = pb.memory[0xFF13], pb.memory[0xFF14]  # channel 1 frequency lo/hi
nr50 = pb.memory[0xFF24]   # master volume/VIN panning
nr51 = pb.memory[0xFF25]   # channel-to-terminal panning (which channels are audible where)
nr52 = pb.memory[0xFF26]   # sound on/off + channel-active flags (bit 0-3)

# Engine state — WRAM addresses per GDS-07's Data Model once authored:
engine_state = pb.memory[0xC000]   # e.g. 0=INIT 1=GENERATING 2=BAD_ZONE 3=RESETTING
pb.stop()
```

Write throwaway driver scripts in the scratchpad, not the repo. `docs/architecture/07-data-model.md`
(GDS-07) is the authoritative WRAM/SRAM map and assertion surface — prefer sound-register and
memory assertions for engine-logic checks, screenshots for visualizer content review.
`test_rom.py`'s own helpers (`fresh_boot`, button patterns) are the reference idiom; mirror them.

## Gotchas

- **Sound registers are the ground truth, not the screen.** A visualizer screenshot shows what the
  engine is *displaying*, not necessarily what it's *sounding like* — assert on NR1x-NR5x directly
  for anything about correctness of the generated music; use screenshots for visualizer-content
  review (`09-content-review`), not as a proxy for audio correctness.
- **PyBoy uses `<rom>.ram`** as the battery-save file next to the ROM path, if the project persists
  any state (e.g. a last-good-state snapshot or user preferences) via SRAM.
- **Frame counts matter.** The engine reads input and advances generation state on specific
  frames; use settle loops after button presses as `test_rom.py` does, and confirm the actual
  frame cadence against GDS-02/03 rather than assuming a convention carried over from an unrelated
  project.
- **Screenshots need Pillow.** If absent, `pb.screen.image` isn't available — use
  `pb.screen.ndarray` instead; no test should depend on Pillow being installed.
- **Bad-zone drift and reset are stateful across many frames.** Driving the engine into a bad zone
  (per whatever the shipped detector's trigger conditions are) may take a sustained run, not a
  single button press — budget enough ticks in driver scripts and tests to actually observe the
  drift and the Select-triggered recovery, not just the immediate next frame.
- **The ROM is deterministic** given the same input script and a clean save state (assuming the
  generator seeds deterministically from a fixed or logged seed) — identical runs should produce
  identical register/memory traces; use that for regression evidence.
