# R305 — Emulator-Based Test Design

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored
  2026-07-21, extended 2026-08-17 (§5b, `BL-0103`/`BL-0105`)
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
- **⚠️ `pb.tick()` returns at a point *inside* the ROM's frame, not between frames — so state read
  after a `tick` is not internally consistent.** Measured 2026-07-31 (PyBoy 2.7.0): a ROM-side
  frame counter confirms exactly one ROM frame elapses per `tick(1)`, but the sampling point falls
  *after* `apply_input` has updated a steering index and *before* `update_visuals` has re-rendered
  the indicator from it. **Therefore: a check that reads a WRAM field and its derived VRAM cell
  after the same `tick()` and asserts they agree is comparing two different moments of the ROM's
  frame, and will report a spurious one-frame lag.** This is not an occasional race — it is
  deterministic, uniform across every frame class, and it occurs on idle frames with no input at
  all. It is the error that produced `R308` §8's false "dropped writes" finding, which then
  survived independent verification in `VR-1110` because the reproduction repeated the same
  sampling mistake. Correct shapes: assert WRAM against WRAM, assert VRAM against VRAM, or drive
  one extra `tick` and assert the derived cell has caught up (which is what `T18.10` already does,
  correctly, though its comment attributes the lag to the wrong cause).
- **⚠️ An emulator observation is only evidence about hardware for behaviour the emulator actually
  models — check the source before inferring a mechanism.** PyBoy applies no PPU-mode gating to
  VRAM writes (`R301` §3, `mb.py:502-511`), so no test here can observe a mode-3 discard. The
  standing rule this generalises to: **before concluding that a hardware mechanism explains an
  observed emulator behaviour, read the emulator's implementation of that mechanism.** If it isn't
  implemented, the observation is evidence about the harness, not the hardware. The check costs one
  `grep`; skipping it cost this project a finding that propagated into five documents and one
  planned package before being caught. Corollary for test design: **prefer assertions whose
  evidence chain runs through state the ROM itself computes and records** (a WRAM byte the ROM
  wrote, an `LY` value the ROM read) **over assertions that infer ROM behaviour from an emulated
  peripheral's side effects** — the former depends only on the CPU being correct, which is the one
  thing every emulator gets right.

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
  partial substitute for genuinely surprising findings, not a required step. **Updated 2026-07-31
  (`BL-0069`):** this is no longer purely an aspiration — §3's PyBoy VRAM-gating limitation means
  there is now a *named, specific* question (does Driftune's near-exhausted VBlank budget actually
  drop visualizer writes on silicon?) that this harness cannot answer even in principle. Where
  `R308` §8.5 measures the margin at a handful of instructions, cross-checking against a
  mode-accurate emulator (SameBoy/BGB, R309) is the cheapest available next step and is a genuine
  substitute for hardware on *this* question specifically.

### What the harness can and cannot establish

A blunt statement of the boundary, because it bounds every `test_rom.py` check and every `VR-xxxx`
independent drive:

| Claim class | Establishable here? | How |
|---|---|---|
| Engine state transitions, index arithmetic, reset/preset semantics | **Yes** | WRAM mirror reads (§3) |
| Which channels are sounding | **Yes** | `NR52` (§3) |
| Tile/tilemap/palette *content* the ROM intended to write | **Yes** | VRAM reads — but see the `tick()` sampling hazard |
| Where in the frame a routine runs; VBlank budget head-room | **Yes** | ROM-side `LY` probe stored to WRAM (`R301` §5) |
| Whether a VRAM write was *accepted* by the PPU | **No — by construction** | PyBoy accepts all writes (`R301` §3); needs silicon or a mode-accurate emulator |
| Sub-scanline (mode 2 vs. mode 3) write placement | **No** | same |
| Analog audio output quality | **No** | out of scope for register-level assertions (`MSTR-001` C9) |

**Do not write a check whose name implies a claim from the bottom half of that table.** A test
that cannot fail is worse than no test: it converts an open question into a false record of
coverage, which is precisely what happened between `R308` §8 and `VR-1110`.

### 5b. `NR52`-active-bit onset counting undercounts at high onset density (2026-08-17, `BL-0103`/`BL-0105`)

`09-content-review`'s F2 finding measured `DENSITY_IDX`'s onset-event count (via `NR52` bit3
rising-edge sampling, once per `tick()`, the same technique `test_rom.py`'s own `T7` uses) as
non-monotonic at the top of the range — `27` at `DENSITY_IDX=6` and `13` at `DENSITY_IDX=7`,
against an expected near-linear scaling with `DENSITY_K=[2,3,4,5,6,8,10,12]`. Two competing
explanations were named, unresolved: (a) `IP-0007`'s overload throttle genuinely suppressing
onsets, or (b) `NR52`-bit-continuity undercounting — two onsets landing close enough together
never letting the channel's envelope/DAC drop back to inactive between them, merging two real
onsets into one observed rising-edge event.

**Register-write-level instrumentation conclusively resolves this in favor of (b).** A local
experiment hooked the exact ROM instruction that writes the noise channel's `NR44` trigger bit
(`pyboy.hook_register`, PyBoy 2.7.0 — located unambiguously via a byte-pattern search for the
2-instruction sequence `LD A,0xC0 ; LDH (NR44),A` in the built ROM, found exactly once) and
counted **real trigger-write executions**, independent of `NR52` sampling, across a 600-frame
window at each `DENSITY_IDX`:

| `DENSITY_IDX` | `DENSITY_K` | Raw trigger writes (ground truth) | `NR52`-sampled onsets (existing method) | Undercounted |
|---|---|---|---|---|
| 0 | 2 | 10 | 10 | 0 |
| 1 | 3 | 15 | 15 | 0 |
| 2 | 4 | 19 | 19 | 0 |
| 3 | 5 | 24 | 24 | 0 |
| 4 | 6 | 28 | 28 | 0 |
| 5 | 8 | 38 | 38 | 0 |
| 6 | 10 | 46 | 28 | **18** |
| 7 | 12 | 55 | 37 | **18** |

The raw trigger-write counts scale **monotonically and near-proportionally with `DENSITY_K`**
(ratio ≈4.6-5.0 across every index, no anomaly) — the Euclidean-pattern generation and the
engine's own onset-triggering logic work exactly as designed at every density level, including
the two highest. The divergence appears *only* in the `NR52`-sampled count, and only at the two
densest settings, exactly where onset spacing gets tight enough for two real triggers to land
within the same continuously-active `NR52` window. **Explanation (a) — the overload throttle
genuinely suppressing onsets — is not what's happening**; `IP-0007`'s throttle does still engage
at high density (as `BL-0103`'s own original filing noted, "index 6 showed 154/600 overload
frames"), but its effect is on note *duration*/*timing*, not on whether a trigger write happens at
all — the raw write count proves every scheduled onset still fires.

**Implication for `test_rom.py`/future onset-counting checks and `BL-0103`'s retuning question**:
this is a genuine, standing limitation of `NR52`-active-bit sampling as an onset-counting
technique at high onset density, not a defect in `DENSITY_K`/`OVERLOAD_THRESHOLD`/the Euclidean
generation itself. Any future check needing an accurate onset count at `DENSITY_IDX` 6-7 should
use register-write-level instrumentation (the `hook_register` technique demonstrated above) rather
than `NR52` rising-edge sampling — the latter is fine at low-to-moderate density (0 undercounted
through index 5) but not reliable at the top of the range. `BL-0103`'s original "does
`DENSITY_IDX` reliably read as busier" question is **answered "yes" at the engine level** — the
apparent non-monotonicity was a measurement artifact of the review's own methodology, not a
listener-perceivable defect in what the engine actually schedules; whether the *perceived*
busyness still reads correctly to a listener at those two densest settings (a separate, genuinely
acoustic question `NR52`/trigger-write instrumentation cannot answer either) remains open per
`BL-0105` below.

**`BL-0105`'s acoustic-verification gap, addressed narrowly, not closed generally**: the register-
write-level technique above only narrows the class of *mechanism*-level questions the harness's
own onset-counting can miss — it is still not acoustic verification (no pitch/timbre information
is recovered, only *how many times* and *when* a trigger register was written).

`BL-0105`'s own concrete ask — whether PyBoy's `sound_emulated=True` APU state can yield raw audio
samples at all — **was attempted this pass, with a positive result**: `pb.sound` (PyBoy 2.7.0)
exposes `.ndarray` (a per-`tick()` stereo buffer, confirmed shape `(801, 2)`, `int8`, at
`.sample_rate=48000`) with genuine nonzero waveform content reflecting the actual PSG mix — not a
stub. A local experiment ticked the shipped ROM to a frame with active channels and read
`pb.sound.ndarray` directly: 1512 of 1602 samples nonzero, values varying frame-to-frame in a way
consistent with real audio output (not silence or a constant). **This means the standing "no
acoustic-verification capability" gap is a real capability that has simply never been exercised**,
not an actual PyBoy limitation — a future pass could FFT a captured buffer against the expected
note frequency (`freq(hz)` in `music_engine.py`, `R108`/`R114`'s formula) to confirm actual pitch,
closing the octave/scale acoustic-correctness question `BL-0105` names. **Not built here** — this
pass confirms feasibility only; designing and adding a frequency-detection assertion helper to
`run-driftune`'s toolkit (sample-buffer capture + FFT peak-frequency extraction + tolerance-banded
comparison against `freq()`'s own expected value) is real implementation work for a future
`02-research-tooling-and-testing`/`08-code-implementation` pass, not a research-topic-only task.

### Sources
- PyBoy 2.7.0's own `hook_register(bank, addr, callback, context)` API (docstring, installed
  package) — confirmed working exactly as documented: a hook on a specific ROM address fires the
  callback whenever the Game Boy executes that instruction, independent of `tick()`'s once-per-
  frame `pyboy.memory` sampling granularity.
- PyBoy 2.7.0's own `PyBoy.sound` → `pyboy.api.sound.Sound` object (installed package, `dir()`
  inspected directly — no public docstring found on the class or its properties, so this claim
  rests on direct local-experiment observation rather than documentation): exposes `.ndarray`,
  `.raw_ndarray`, `.raw_buffer`/`.raw_buffer_dims`/`.raw_buffer_format`/`.raw_buffer_head`/
  `.raw_buffer_length`, `.sample_rate`. Confirmed via direct instantiation with
  `sound_emulated=True` and reading `.ndarray` after ticking to an active-channel frame: real,
  non-constant stereo `int8` sample data at 48kHz, not a stub or all-zero buffer.
- Local experiment (this topic, 2026-08-17): byte-pattern search + `hook_register`-based trigger
  counting across all 8 `DENSITY_IDX` values, 600-frame windows, described above; not committed to
  production (throwaway, per this skill's own read-only-experiment convention).

## 6. Feature Mapping

`test_rom.py` (all suites), NFR-1020, `IP-0004`'s future bad-zone test design.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds the shipped harness's central design choice — assert on sound registers and the WRAM engine-state mirror rather than the framebuffer (`MSTR-001` C9) — realised across all 18 `test_rom.py` suites. Design: [GDS-02 §4](../../architecture/02-system-context.md). **Extended 2026-07-31 (`BL-0069`):** §3's two new hazards (the `tick()` mid-frame sampling point, and inferring hardware mechanisms from unmodelled emulator behaviour) trace forward to `IP-9030`'s `BLOCKED` status and to the re-scoped `LY`-budget assertion that replaces its planned `T19`. The §5 can/cannot table is the standing constraint every future suite is written against.

## 7. Related Topics

R301 (the API these test patterns are built on), R108/R110 (the hardware facts that motivate each
pattern).
