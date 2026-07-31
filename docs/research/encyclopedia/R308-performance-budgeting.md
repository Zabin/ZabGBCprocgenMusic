# R308 — CPU/RAM/ROM Performance Budgeting

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 8, items 89-96 (CPU budgeting, RAM budgeting,
  ROM budgeting, cycle counting, audio timing accuracy, optimization techniques, cache-friendly
  data layouts, compression methods)

## 1. Purpose
Ground future headroom decisions (bank-switching, table sizes, generation complexity ceilings)
against real embedded-budgeting practice, and record Driftune's actual current usage as a
baseline.

## 2. Scope
ROM/RAM/CPU budgeting practice in resource-constrained embedded targets, and what applies to a
single-bank 32KB SM83 ROM with no allocator.

## 3. Concepts
- **ROM vs. RAM/CPU trade-off via compression**: "compressed data can be stored in ROM and then
  decompressed into RAM at initialization, gaining ROM at the expense of RAM and CPU time," with
  up to ~50% space savings possible [Comarch — Memory Optimization in Embedded Systems, Part 3](https://www.comarch.com/sw-and-hw-services/blog/part-3-memory-optimization-in-embedded-systems-in-the-c-language-rom/).
  Lightweight embedded-specific schemes (e.g. "HS 8,4... a reasonable default for embedded
  systems") deliberately avoid "complex range coders or Huffman codes that introduce large RAM
  state and decoder complexity" [Atomic Object — heatshrink Compression Library](https://spin.atomicobject.com/heatshrink-embedded-data-compression/).
  **Not currently relevant to Driftune**: at `IP-0001`'s current size (well under 32KB, no bank-
  switching in scope per MSTR-001 §4), decompression overhead would be pure cost with no present
  benefit — flagged for reconsideration only if ROM headroom genuinely becomes tight (e.g. many
  more wave-table variants, R114/R218's bytebeat idea, or expanded scale/preset tables).
- **Cache-friendly / memory-mapped-in-place data**: "selected ROMs can be flashed directly...
  then accessed through memory-mapped pointers allowing code to read game data in place without
  runtime allocation" [search synthesis — embedded ROM/RAM budgeting sources]. **This is already
  Driftune's exact model** — `gbc_lib.py`'s `ROM.data` bytearray is the whole address space, tables
  (`TEMPO_TABLE`, note tables, etc.) are read directly by address, no runtime allocation or
  decompression step exists anywhere in the pipeline. No change needed; this topic confirms the
  existing approach rather than prescribing a new one.

### Sources
- [Comarch — Part 3: Memory Optimization in Embedded Systems (ROM)](https://www.comarch.com/sw-and-hw-services/blog/part-3-memory-optimization-in-embedded-systems-in-the-c-language-rom/)
- [Atomic Object — heatshrink Compression Library for Embedded Data](https://spin.atomicobject.com/heatshrink-embedded-data-compression/)
- [SEGGER Blog — SMASH: an efficient compression algorithm for microcontrollers](https://blog.segger.com/smash-an-efficient-compression-algorithm-for-microcontrollers/)

## 4. Operational Context
`gbc_lib.py`'s `ROM` class already implements the memory-mapped-in-place model. No cycle-counting
tooling exists yet beyond the "extended headless run, watch for hangs/slowdown" empirical check
NFR-1010 already specifies (R110).

## 5. Implementation Guidance
- **No compression needed at current scale** — revisit only if a concrete future package's data
  tables (e.g. many more wave shapes, or expanded scale tables) meaningfully threaten the 32KB
  single-bank ceiling MSTR-001 §4 currently treats as a non-goal to exceed.
- **Cycle counting**: no dedicated instruction-cycle-counting tool is currently used;
  NFR-1010's "drive thousands of frames, watch for hangs" empirical test is the current, adequate
  proxy given the generous per-frame budget a ~4MHz CPU gives a 4-channel generator (R108/R110).
  If a future package's generation logic grows complex enough that this proxy feels insufficient,
  a dedicated cycle-count assertion (summing each opcode's documented cycle cost across a code
  path) would be the more rigorous follow-up — not needed yet.
- **RAM budgeting**: GDS-07's WRAM map currently uses ~97 bytes of a ~8KB window with the next
  free 8-aligned address explicitly tracked (GDS-07 SS6) — ample headroom, no action needed.

## 6. Feature Mapping
No current `IP-xxxx` — informational baseline for future headroom decisions.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⚠️ **TRACE STATUS CHANGED 2026-07-26 — see §8; MECHANISM CORRECTED 2026-07-31 — see §8.5.** Originally an informational baseline whose §5 grounded a decision **not** to act (no compression, no cycle counting) — a legitimate `MSTR-001` C10 exception shape, though never recorded as one. **§8 reverses the cycle-counting half of that conclusion on new evidence**, so this topic now carries an *open, actionable* recommendation tracked as **`BL-0060`**/**`BL-0061`**/**`BL-0069`**. **§8.5 (2026-07-31) withdraws §8's dropped-write mechanism as falsified** and replaces the recommendation with a per-frame `LY` budget assertion; the budget-exceeded conclusion itself survives on stronger evidence. The ROM/RAM-budgeting half remains a correctly-traced confirmation (`ADR-0002`'s `rom.pos` convention descends from it).

## 7. Related Topics
R110 (the cycle-budget discipline this topic's "no compression needed yet" call depends on),
R307 (architecture patterns this topic's memory-mapped-data confirmation supports).

---

## 8. Addendum — 2026-07-26: the per-frame budget is being exceeded routinely (`BL-0060`/`BL-0061`)

**This addendum reverses §5's "no cycle-counting needed" conclusion.** That conclusion was
reasonable on the evidence available in 2026-07-21 (`IP-0001`-era, four short per-frame routines,
no observed frame drops). Sixteen packages later the evidence is different, and this topic's own
sibling `R101` §5 named the revisit condition explicitly: *"revisit... if a future package pushes
per-frame work close to the VBlank budget (a symptom would be `R308`-style stress testing starting
to show occasional frame drops)."*

### 8.1 The triggering evidence

`IP-1110` (settings & control visibility) shipped with a disclosed finding: on the frame Select is
pressed, that frame's settings-indicator VRAM writes are silently dropped, self-healing the next
frame. `VR-1110` independently reproduced it across three distinct pre-Select button sequences.
`GDS-06` §2.2 judged this to be `R101`'s predicted symptom arriving through a different door —
a specific reproducible frame class rather than random drops under load.

### 8.2 Local experiment — the effect is broader than `IP-1110` disclosed

Run 2026-07-26 against the shipped ROM at commit `e4db8ef`, PyBoy 2.7.0. Method: drive one button,
read the affected WRAM index and its corresponding settings-indicator tilemap cell on the press
frame itself, and compare. Also read `CHANNEL_CELLS` against `NR52` on the same frame.

> ⚠️ **THE TABLE BELOW AND §8.3'S MECHANISM WERE FALSIFIED ON 2026-07-31 — READ [§8.5](#85-self-correction--2026-07-31-the-dropped-write-mechanism-was-wrong-bl-0069) BEFORE CITING ANY OF IT.** No write is dropped; PyBoy cannot drop one. §8.1-§8.4 are retained verbatim as the methodological record of how the error was made and caught. **§8.4's headline conclusion — that the per-frame budget is being exceeded and cycle accounting is warranted — survives, and is now better evidenced**; only the mechanism and this table's interpretation are withdrawn.

| Frame class | Extra work in that frame | Settings-row writes | Channel-activity writes |
|---|---|---|---|
| D-pad Up / B press | plain index step | **land** | land |
| **Start** press | index step **+ style application** | **DROPPED** | land |
| **Select** press | index step **+ full `init_engine` reset** | **DROPPED** | land |
| **Song-form phase transition** | extra work inside `engine_tick`, not `apply_input` | **PARTIALLY dropped** — cell 0 landed, cell 3 did not | land |

Two results here matter more than the original `IP-1110` disclosure:

1. **Select is not the only affected frame class** (this closes `BL-0061`'s question). A Start
   press does it too, and so does an autonomous song-form phase transition — which is *not* an
   input frame at all, so no amount of button-driven testing would have found it by design.
2. **The song-form case shows a PARTIAL drop**: the first of the five settings cells was written
   correctly and the fourth was not. That is the decisive observation — the write sequence is
   being **cut off mid-block**, not blocked wholesale.

### 8.3 What that actually means — the writes are not reliably VBlank-gated

A partial, position-dependent drop can only mean the frame's work is **overrunning the window the
writes must land in**. The main loop `HALT`s until VBlank, then runs
`read_joypad`→`apply_input`→`engine_tick`→`update_visuals` (`GDS-09` §5). VBlank is 10 scanlines
≈ 1140 M-cycles. If the preceding work outlasts that, `update_visuals` executes while the PPU has
already resumed rendering, and each individual write then lands in whatever PPU mode it happens to
hit — harmless in mode 0/2, **discarded in mode 3** (`R102`).

That is consistent with every row of the table: writes early in `update_visuals` (the
channel-activity cells) survive; writes at the end (the settings row) are exposed; and the more
work the frame did beforehand, the further out the tail is pushed.

**Corroborating evidence from `IP-1110`'s own implementation history**: moving the settings block
to the *front* of `update_visuals` did not fix it — it instead caused the *channel-activity*
writes to start dropping on ordinary no-input frames. Whichever block runs last is the exposed
one. That is exactly what an overrun predicts and what a "one heavy operation blocks one write"
theory does not.

**A static measurement makes the margin concrete.** Instrumenting `build_rom.build()` and reading
label extents: `init_engine` is only **176 bytes** of code — about 6% of the per-frame executed
region. If an addition that small tips the tail out of the window, **the margin was already
approximately zero**, and the "generous per-frame budget" premise in §5 and in `R101` §5 does not
hold at current engine size.

### 8.4 Revised recommendation

**The `NFR-1010` empirical stress-run proxy is no longer sufficient**, and not merely for the
narrow reason recorded in run #98. It cannot detect this class of problem at all: a dropped VRAM
write causes **no hang, no slowdown, and no frame drop** — the three things the stress run watches
for. The engine keeps perfect time; only the display is briefly wrong, and the stateless
re-render contract (`GDS-08` §3) repairs it the next frame. The project's primary timing check is
structurally blind to its primary timing problem.

Concretely recommended, in priority order:

1. **A VRAM-write-integrity check (cheap, high value, do this first).** A test that drives each
   frame class in the §8.2 table and asserts every visualizer cell matches its source state on
   that same frame. This directly asserts the property that actually matters, needs no new
   tooling, and would have caught all four rows. Cost: one `test_rom.py` suite.
2. **Cycle-cost tallying (the `R101` §5 follow-up — now genuinely warranted, but second).** Add
   documented M-cycle costs to `gbc_lib.py`'s opcode emitters and have `build_rom.py` assert a
   static per-routine budget. This is the *diagnostic* — it would say how far over the window the
   frame runs and which routine to shorten. Cost: a cycle-cost table across ~150 emitters, plus a
   summing pass; substantial but mechanical, and `R101`'s own §5 already specifies the design.
   **Note this is `R101`'s topic (tier R100) — this addendum recommends it; `R101`'s own owner
   (`02-research-gbc-hardware`) should record the reversal there.**
3. **Consider whether the architecture should change** — e.g. deferring visualizer writes to a
   dedicated VBlank ISR rather than doing them at the tail of a long main-loop iteration. That is
   a `03-architecture-design-synthesis` question (`GDS-08`/`GDS-09` both describe the current
   arrangement), not a research one, and it should not be reached for before (1) quantifies how
   bad the overrun actually is.

**Honest scoping of severity:** nothing here is a correctness defect in the *engine*. Audio
generation is unaffected — it writes APU registers, not VRAM, and no APU write has ever been
observed to drop. The impact is confined to cosmetic, self-healing, one-frame display staleness.
What has changed is the *confidence* the project can have in statements like `GDS-06` §2.1's
"VBlank gating is well-founded... solid... structural by construction" — that claim describes the
*intent* of the main-loop design, and the evidence above shows the implementation does not
reliably achieve it.

### Sources
- Local experiment, 2026-07-26, PyBoy 2.7.0, ROM at commit `e4db8ef` (method and results in §8.2).
- Static label-extent measurement via `build_rom.build()` + `rom.labels` (`ADR-0002`'s own
  instrumentation convention), same commit.
- [`VR-1110`](../../implementation/verification/VR-1110-settings-and-control-visibility.md) —
  the original three-sequence reproduction of the Select-frame case.
- [Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html) —
  mode-3 VRAM inaccessibility, already cited in `R102`.

---

### 8.5 Self-correction — 2026-07-31: the dropped-write mechanism was wrong (`BL-0069`)

`IP-9030` was planned to *detect and quantify* the §8.2 finding. Stage 08 built the diagnostic the
package specified, took the measurement, and the measurement falsified the finding. The package is
`BLOCKED` and carries the full evidence in its own
[Blocking Report](../../implementation/packages/IP-9030-vram-write-integrity-detection.md#blocking-report--2026-07-31-08-code-implementation-run-102).
This subsection records the correction at the topic that made the claim.

**The claim withdrawn:** that visualizer VRAM writes are silently *dropped* on Start-press,
Select-press and song-form phase-transition frames, discarded by the PPU in mode 3, with plain
index steps unaffected — and that the "partial drop" (cell 0 landed, cell 3 did not) was decisive
evidence of a write sequence cut off mid-block.

**Why it is wrong — two independent lines of evidence.**

1. **PyBoy models no PPU-mode gating on VRAM access whatsoever.** In PyBoy 2.7.0
   (`pip show pyboy`, installed version confirmed 2026-07-31), `pyboy/core/mb.py`'s `setitem()`
   handles `0x8000 <= i < 0xA000` at lines 502-511 by writing `lcd.VRAM0`/`VRAM1` unconditionally
   — the only branch is the CGB VRAM-bank select (`lcd.vbk.active_bank`); there is no `STAT`/mode
   check anywhere in the path. The matching read path (`getitem`, lines 370-374) is likewise
   ungated. **A dropped VRAM write is therefore not an observable event in this harness.** The
   §8.2 experiment could not have confirmed one, and did not.

2. **Direct measurement shows nothing is dropped.** An instrumented build mirrored each
   settings-cell value into a WRAM byte at the same instant it wrote that value to VRAM. The
   WRAM mirror and the VRAM byte are **identical on every frame of every class** — the write
   always lands.

**What was actually being observed — a harness observation-window artifact.** `pb.tick(1)`
returns at a point *inside* the ROM's frame work: after `apply_input` has updated the steering
index, but before `update_visuals` has re-rendered the indicator from it. A ROM-side frame counter
incremented at the main-loop top confirms exactly one ROM frame elapses per `tick`, so this is not
a dropped or doubled frame — it is a **sampling point that falls mid-frame**. Every observation
therefore shows the indicator exactly one frame behind its source:

| Frame class | `TEMPO_IDX` after `tick` | value the ROM wrote that frame | VRAM cell | reading |
|---|---|---|---|---|
| `Up` (plain index step) | 5 | 6 (the *old* index) | 6 | **one-frame lag** |
| `Start` (style apply) | 6 | 6 | 6 | **one-frame lag** |
| `Select` (`init_engine` reset) | 4 (= preset) | 6 | 6 | no value change to lag |

**The asymmetry that made §8.2 look decisive does not exist.** Plain index steps lag identically
to Start and Select; the "`Up`/`B` land" row was a measurement error, not a contrast. And the
"partial drop" is a partial *observation* — settings cells 0-2 complete before the `tick`
sampling point and cells 3-4 after it — which occurs on **idle, no-input frames too**. No drop
hypothesis predicts that; a mid-frame sampling point predicts it exactly.

**What survives, and is now on far better evidence.** §8.4's headline — the per-frame budget is
being exceeded and `NFR-1010`'s stress-run proxy is insufficient — **stands**. The replacement
evidence is the live `LY` register (`0xFF44`) read *from inside the ROM* at five points per frame.
That is Tier-A and, critically, **depends on no emulator behaviour PyBoy may or may not model**:
`LY` is a plain memory-mapped counter the ROM reads for itself, unlike VRAM write acceptance,
which is precisely the thing PyBoy does not simulate.

| Probe point (live `LY`, read by the ROM) | Observed |
|---|---|
| main-loop top, just after `HALT` wakes | **144**, every frame, every class |
| entering `update_visuals` (after `read_joypad`+`apply_input`+`engine_tick`) | **152-153** |
| entering the settings-row block | **153** |
| after `update_visuals` returns *(instrumented build)* | **0** idle/`Up`, **1** `Start`, **9** `Select` |
| per settings cell *(instrumented build)* | cells 0-2 at `LY` 153; **cells 3-4 at `LY` ≥ 0 on every frame, idle included** |
| end of `update_visuals` *(clean build, `VIS_END_LY`)* | **153** on every frame class — just inside VBlank |

Read honestly, with the instrumented/clean distinction kept straight: **the clean ROM finishes
inside VBlank, but only just — at `LY` 153, the last line of the window.** `HALT` wakes exactly at
VBlank start, so the gating *mechanism* is sound; what is nearly exhausted is the *budget*.
`read_joypad`+`apply_input`+`engine_tick` alone consume roughly **9 of VBlank's 10 scanlines**,
leaving `update_visuals` to run against what is left. Adding ~7 diagnostic stores per frame — a
few dozen M-cycles — was enough to push the visualizer's writes past the boundary entirely. The
margin is on the order of a handful of instructions.

This is a **stronger** result than the one it replaces. §8.2 claimed three heavy frame classes
misbehave; the corrected measurement says the window is ~exhausted on *every* frame, including
idle ones, and that the difference between "inside VBlank" and "outside" is a handful of
instructions of head-room that nothing in the build guards.

**The real, still-untested risk is on physical hardware.** Real CGB silicon *does* enforce mode-3
VRAM inaccessibility (`R102` §3). A margin this thin is a genuine hazard there — and it is a
hazard **no headless test on this project can ever rule out**, for exactly the reason in point (1)
above. `GDS-02` §7 records that Driftune has never run on real hardware (`BL-0058`); this
elevates that from an aspiration to the only way this specific question gets answered.

**Revised recommendation, superseding §8.4's priority list:**

1. **A per-frame `LY` budget assertion, not a write-integrity assertion.** §8.4 item 1 recommended
   asserting that every visualizer cell matches its source on the press frame. That test is not
   buildable honestly — it would assert a property the harness cannot falsify, and the naive form
   of it (read WRAM and VRAM after `tick()` and compare) is *exactly the error that produced this
   false finding*. What is buildable and valuable: have the ROM record `LY` at entry to
   `update_visuals` and assert it stays within 144-153 — a real, falsifiable budget check against
   the measurement above. See `R305` §3 for the test-design rule this generalises to.
2. **Cycle-cost tallying (unchanged in substance, strengthened in justification).** Still `R101`'s
   topic; still the right diagnostic. §8.4's cost estimate (~150 opcode emitters) stands.
3. **Architecture change** — unchanged: a `03-architecture-design-synthesis` question, still not
   to be reached for before (1) and (2) quantify the head-room.

**Methodological lesson, recorded because it is the transferable part.** The §8.2 experiment was
carefully run, internally consistent, independently reproduced by `VR-1110`, and wrong. It failed
because it inferred a *hardware* mechanism from an *emulator* observation without first checking
whether the emulator models that mechanism at all. The check that would have caught it costs one
`grep` of the emulator's memory-write path. `R305` §3 now carries this as a standing rule.

#### Sources
- [`IP-9030` Blocking Report](../../implementation/packages/IP-9030-vram-write-integrity-detection.md#blocking-report--2026-07-31-08-code-implementation-run-102) — both experiments, full data, 2026-07-31.
- PyBoy 2.7.0 installed source, `pyboy/core/mb.py` `setitem()` lines 502-511 and `getitem()` lines
  370-374 (read directly from the installed package; version confirmed via `pip show pyboy`).
- Local experiments, 2026-07-31, PyBoy 2.7.0: ROM-side live-`LY` probes at five per-frame points;
  WRAM-mirror-vs-VRAM comparison; ROM-side frame counter. Instrumented builds were throwaway and
  reverted — the shipped tree is unchanged and 122/122 green.
- [Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html) —
  mode-3 inaccessibility on real hardware, which remains true and remains untested here.
