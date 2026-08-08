# R101 — SM83 Instruction Set & Cycle Costs

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22

## 1. Purpose
Ground `gbc_lib.py`'s opcode emitters (`ROM.LD_A_n`, `ROM.JR_Z`, `ROM.CALL`, etc.) against the
real SM83 instruction encoding and timing, and settle whether Driftune's per-frame CPU budget
needs cycle-exact accounting.

## 2. Scope
The SM83 (a modified Z80/8080 hybrid) instruction set: opcode byte encoding, addressing modes,
and per-instruction timing in M-cycles (1 M-cycle = 4 T-states = 4 clock ticks at ~4.19MHz DMG /
up to ~8.39MHz CGB double-speed).

## 3. Concepts
Instructions are variable-length (1-3 bytes) with timing expressed in M-cycles, not raw clock
ticks, since every instruction takes a whole multiple of 4 T-states; a `NOP` is 1 M-cycle, most
8-bit ALU ops on registers are 1 M-cycle, memory-indirect ops (`LD (HL),A`) are 2, 16-bit loads
and most jumps are 3-6, and conditional branches (`JR`/`JP`/`CALL`/`RET` with a condition) have
two different costs depending on whether the branch is taken — Pan Docs and the community opcode
tables give the taken/not-taken split explicitly. [Pan Docs — CPU Instruction
Set](https://gbdev.io/pandocs/CPU_Instruction_Set.html); [gbdev.io opcode
tables](https://gbdev.io/gb-opcodes/optables/).

### Sources
- [Pan Docs — CPU Instruction Set](https://gbdev.io/pandocs/CPU_Instruction_Set.html)
- [gbdev.io — Game Boy CPU (SM83) opcode tables](https://gbdev.io/gb-opcodes/optables/)
- [gekkio — Game Boy: Complete Technical Reference](https://gekkio.fi/files/gb-docs/gbctr.pdf) (cross-checked, cycle-accurate reference; single deep secondary source alongside the two primary tables above)

## 4. Operational Context
`gbc_lib.py`'s emitters map one Python method call to one SM83 opcode + operand bytes (e.g.
`LD_A_n` → `0x3E, n`), with no cycle bookkeeping anywhere in the assembler or the generated code —
`build_rom.py`/`music_engine.py` never reference an instruction's cycle count. The project's own
per-frame budget evidence is empirical, not derived from a cycle table: `R308`'s performance
budgeting topic and multiple `VR-000x` reports' 6000-8000+ frame stress runs (no hangs, no dropped
frames) are the actual verification mechanism NFR-1010 relies on.

## 5. Implementation Guidance
**No change needed anywhere in the tree.** `gbc_lib.py`'s opcode emitters are simple,
unambiguous 1:1 mappings and every routine in `music_engine.py`/`input_map.py`/`visuals.py` is
short (a few dozen instructions per per-frame call); the empirical stress-test evidence (`R308`,
`VR-0001`-`VR-0007`) already demonstrates the whole per-frame VBlank workload fits comfortably —
cycle-exact accounting would be genuine over-engineering for this ROM's actual size and workload.
**Do** revisit this topic with real per-instruction cycle tallying if a future package pushes
per-frame work close to the VBlank budget (a symptom would be `R308`-style stress testing starting
to show occasional frame drops) — at that point, add cycle counts to `gbc_lib.py`'s opcode table
so `build_rom.py` can assert a static per-routine cycle budget rather than relying on empirical
stress testing alone.

## 6. Feature Mapping
NFR-1010 (per-frame VBlank budget) — currently verified empirically (`R308`, stress-test evidence
across `VR-0001`-`VR-0007`), not via static cycle analysis grounded by this topic.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `gbc_lib.py`'s ~150 opcode emitters — every byte of shipped SM83 code is emitted through them. Formally specified as an interface in [GDS-09 §2](../../architecture/09-interface-specification.md), including the `JR` signed-8-bit range limit that actually fired during `IP-1090`. The *cycle-cost* half was originally a decision **not** to act (a C10 exception shape) but **§8 reopened it** — now an open recommendation tracked as `BL-0060`.
 **Updated 2026-07-31 (`BL-0069`):** §8.5's self-correction traces forward to `IP-9030`'s `BLOCKED` status and to the runtime `LY` budget assertion recommended for its re-scope — a research correction that stopped an unbuildable test from shipping. Architecture: `GDS-06` §2.2a.
## 7. Related Topics
R108 (APU register-write timing, the one place a misplaced write could matter more than raw
cycle count), R110 (interrupt/VBlank timing), R308 (performance budgeting — the topic that
actually carries this project's per-frame budget evidence).

---

## 8. Addendum — 2026-07-26: the revisit condition has been met (`BL-0060`)

**This addendum reverses §5's "no change needed anywhere in the tree" conclusion.** §5 named its
own revisit condition explicitly:

> *"**Do** revisit this topic with real per-instruction cycle tallying if a future package pushes
> per-frame work close to the VBlank budget (a symptom would be `R308`-style stress testing
> starting to show occasional frame drops) — at that point, add cycle counts to `gbc_lib.py`'s
> opcode table so `build_rom.py` can assert a static per-routine cycle budget."*

That condition is now met. The sibling topic [`R308` §8](R308-performance-budgeting.md) carries
the experiment in full; this addendum re-derives *this* topic's own conclusion against it.

> ⚠️ **§8.1-§8.3 were written against evidence that was falsified on 2026-07-31. Read
> [§8.5](#85-self-correction--2026-07-31-the-drop-evidence-was-wrong-the-conclusion-was-not-bl-0069)
> before citing anything in them.** The headline — **the revisit condition has been met and cycle
> accounting is warranted** — survives, and is now on materially stronger evidence. The
> dropped-VRAM-write causal story it was derived from does not. §8.1-§8.4 are retained verbatim as
> the methodological record; §8.5 states the correction and re-derives §8.2 and §8.3.

### 8.1 The symptom arrived, but not in the predicted form

§5 predicted the symptom would be "stress testing starting to show occasional frame drops." It was
not. What actually happened is that a specific, **reproducible frame class** silently drops VRAM
writes while the engine keeps perfect time — no dropped frames, no hang, no slowdown.

`R308` §8.2's experiment drove four frame classes and compared each visualizer cell against its
source WRAM on the press frame itself:

- plain index step (D-pad Up, B) — writes land;
- **Start** (index step + style application) — settings-row writes dropped;
- **Select** (index step + full `init_engine` reset) — settings-row writes dropped;
- **autonomous song-form phase transition** — settings-row writes **partially** dropped (the
  first of five cells landed, the fourth did not), and this one is not an input frame at all.

The partial drop is the decisive datum: the write sequence is cut off **mid-block**, which means
the frame's work is **overrunning the window**, not that any single operation is blocking a write.

### 8.2 What this says about the cycle budget specifically

The VBlank window is 10 scanlines of the 154-line frame (`R102`), i.e. 4560 dots ≈ **1140
M-cycles** of CPU time at CGB single speed before the PPU resumes rendering and Mode 3 begins
discarding VRAM writes (`R102` §3, already cited there).

Two measurements bound the problem:

- A static label-extent measurement (`R308` §8.3) puts `init_engine` at **176 bytes** — roughly
  **6% of the per-frame executed code region**. An addition that small tipping the write tail out
  of the window means the margin was already **approximately zero**, not merely "getting tight."
- The per-frame path (`read_joypad` → `apply_input` → `engine_tick` → `update_visuals`) spans a
  code region of ~3000 bytes. Not all of it executes on any given frame (branches), but at the
  SM83's typical ~2 bytes and ~2-3 M-cycles per instruction, even a third of that executing is
  already in the same order of magnitude as the whole 1140-M-cycle window.

**So §5's premise — "the generous per-frame budget a ~4MHz CPU gives a 4-channel generator" — does
not hold at the engine's current size.** That premise was correct when written (`IP-0001` era, one
channel, four short routines). Sixteen packages later it is not, and nothing in the intervening
work re-tested it, because the empirical proxy `NFR-1010` relies on is **structurally incapable**
of detecting this failure mode: a dropped VRAM write produces none of the three signals the stress
run watches for.

### 8.3 Is §5's proposed tooling design still the right one?

§5 proposed: add cycle counts to `gbc_lib.py`'s opcode table so `build_rom.py` can assert a static
per-routine cycle budget. **Assessed against what is now known: the design is still right, but it
is no longer the *first* thing to do, and its cost is higher than §5 implied.**

**Still right, because it answers the question that actually matters now.** The open question is
no longer "is there a problem" (there is, and it is characterised) but "**how far over the window
does the frame run, and which routine should shrink**." A static per-routine cycle sum answers
exactly that, at build time, for every routine, with no emulator in the loop — and it would let
`build_rom.py` fail the build when a package pushes a routine past a stated ceiling, turning a
silent runtime degradation into a loud build-time error. Nothing else on the table does that.

**Cost, honestly.** `gbc_lib.py` currently exposes roughly **150 opcode-emitter methods**. Each
needs its documented M-cycle cost attached — mechanical, well-documented per-opcode (the tables in
§3 above are the source), but 150 individual facts that must each be right, and wrong ones would
produce confidently-wrong budgets. Conditional-branch opcodes need **two** figures (taken and
not-taken differ), and the summing pass must decide how to treat them — worst-case is the honest
default for a budget assertion. Loops and `CALL` nesting mean a naive per-routine sum is a lower
bound unless call graphs are followed. This is a real package, not an afternoon.

**Which is why it should be second, not first.** `R308` §8.4's first-priority recommendation — a
**VRAM-write-integrity test** that drives each frame class and asserts every visualizer cell
matches its source on that frame — costs one `test_rom.py` suite, needs no new tooling, and would
have caught all four observed cases. It converts the blind spot into a covered one immediately.
Cycle tallying is the *diagnostic* that follows once the project decides to actually reduce the
overrun rather than merely detect it.

**A cheaper diagnostic worth considering first**, and not previously named: rather than static
tallying across all ~150 emitters, instrument a *single* measurement — read `LY`/`STAT` at the top
and bottom of `update_visuals` during a driven frame and record how far past VBlank the routine
finishes. That is a handful of lines, gives a direct empirical answer to "how far over are we,"
and would tell the project whether the overrun is marginal (shave one routine) or structural (the
architecture needs to change). It does not replace static budgeting as a *regression gate*, but it
is the right first measurement.

### 8.4 Revised guidance

- **Do not** treat the per-frame budget as generous. It is not, at current engine size.
- **Do** require any package adding per-frame work — especially to `apply_input` or
  `update_visuals` — to state its cost impact, per `NFR-1010`'s 2026-07-26 caveat.
- **Do** build the VRAM-write-integrity check first (`BL-0069`).
- **Do** measure the actual overrun with a targeted `LY`/`STAT` probe (§8.3) before committing to
  the full 150-emitter cycle-table package.
- **Do not** conclude the engine is broken: audio generation writes APU registers, not VRAM, and
  no APU write has ever been observed to drop. The demonstrated impact is confined to cosmetic,
  self-healing, one-frame display staleness (`GDS-08` §3's stateless re-render contract).

### Sources
- [`R308` §8](R308-performance-budgeting.md) — the local experiment, method and results
  (PyBoy 2.7.0, commit `e4db8ef`, 2026-07-26).
- [`R102` §3](R102-ppu-modes-and-vram-oam-access-timing.md) — Mode 3 VRAM inaccessibility and the
  10-scanline VBlank window, with its own Pan Docs citations.
- [Pan Docs — Rendering / PPU timing](https://gbdev.io/pandocs/Rendering.html) — the 154-line
  frame and 456-dot scanline figures underlying the ~1140 M-cycle VBlank window.

---

### 8.5 Self-correction — 2026-07-31: the drop evidence was wrong, the conclusion was not (`BL-0069`)

`IP-9030` was planned to detect and quantify §8.1's finding. Stage 08 built the diagnostic, took
the measurement, and the measurement falsified the finding; the package is `BLOCKED` and carries
the full data in its own
[Blocking Report](../../implementation/packages/IP-9030-vram-write-integrity-detection.md#blocking-report--2026-07-31-08-code-implementation-run-102).
`R308` §8.5 records the sibling tier's correction. This subsection corrects *this* topic.

**Withdrawn.** §8.1's four-frame-class list and the "partial drop is the decisive datum" reading,
and every step of §8.2 that reasons from the drop *pattern*. No VRAM write is dropped, on any
frame class. PyBoy 2.7.0 applies no PPU-mode gating to VRAM writes whatsoever (`R301` §3, citing
`mb.py:502-511`), so the experiment could not have observed a drop; and a WRAM mirror of each cell
write matches the VRAM byte on every frame of every class. The symptom was a `pb.tick()`
mid-frame sampling artifact producing a **uniform** one-frame display lag — identical on plain
index steps and on Select, and present on idle frames with no input at all. The asymmetry §8.1
built its argument on does not exist.

**§8.2 re-derived against real numbers.** The replacement evidence is the live `LY` register read
from *inside the ROM* at five points per frame — Tier-A, and (unlike VRAM write acceptance)
dependent on nothing beyond a plain memory-mapped counter that every emulator models:

| Probe point | Measured `LY` |
|---|---|
| main-loop top, immediately after `HALT` wakes | **144** — every frame, every class |
| entry to `update_visuals` (after `read_joypad`+`apply_input`+`engine_tick`) | **152-153** |
| end of `update_visuals`, **clean shipped build** | **153** — VBlank's last scanline |
| end of `update_visuals`, **instrumented build** (~7 extra stores/frame) | 0 idle · 1 Start · 9 Select |

The corrected §8.2 conclusion, stated plainly: **`read_joypad`+`apply_input`+`engine_tick` consume
roughly 9 of VBlank's 10 scanlines, and `update_visuals` finishes on the tenth.** The head-room is
a few dozen M-cycles — a handful of instructions — and it is spent on *every* frame, including
idle frames with no input and no phase transition.

This is duller than §8.1's story and considerably worse. Three differences matter for this topic:

1. **No frame class is special.** Select and Start are a few instructions further along an
   already-spent budget, not a distinct category. §8.2's "an addition as small as `init_engine`'s
   176 bytes tips the tail out" was directionally right about the *margin* and wrong about the
   *mechanism*: the margin really is ≈zero, but `init_engine` is not what spends it.
2. **It is therefore not fixable by shortening any single routine.** §8.2 implicitly framed the
   problem as one heavy path. It is not — the ordinary path is the heavy path. Shortening
   `init_engine` to nothing would not move `LY` at entry to `update_visuals`, because
   `init_engine` does not run on the idle frames that already reach 152-153.
3. **The falsified version was, ironically, the more reassuring one.** A single tight frame class
   is a local defect. A budget that is exhausted on every frame is a property of the engine's
   size, and it will get worse with every package that adds per-frame work — which is precisely
   what §5's revisit condition was written to catch.

**§8.3 re-answered: is §5's proposed tooling design still right?** Partly, and its *priority* has
changed for a second time.

- **`R308` §8.4's "VRAM-write-integrity test first" is withdrawn** — by the sibling topic itself.
  That test is not buildable honestly, because the harness cannot falsify it (`R305` §5's
  can/cannot-establish table). It has been replaced by a **runtime `LY` budget assertion**: have
  the ROM read `LY` at entry to `update_visuals`, store it to WRAM, and assert 144-153 in
  `test_rom.py`. A handful of instructions and one check.
- **This topic's position: build the runtime guard first, and agree with `GDS-06` §6 Open
  Question 1's sequencing.** It is cheap, it is falsifiable, and it guards the exact regression
  §8.2 fears — the next package quietly spending the last scanline.
- **But the static cycle table retains independent value the runtime guard cannot supply, and
  this topic does not want that lost.** A runtime assertion is a *detector*: it fires after a
  package has been written, built and run, and it says "you are over" without saying by how much
  or where. A static per-routine cycle sum is a *pricer*: it says what a routine costs **before**
  it ships, attributes the cost to a named routine, and can fail the build at authoring time. Now
  that the budget is known to be spent on the ordinary path, knowing *which* of `read_joypad`/
  `apply_input`/`engine_tick` owns the 9 scanlines is the question any remediation must answer
  first — and no runtime `LY` probe at a single point can answer it. **Revised recommendation:
  runtime guard now; static table when remediation is actually attempted, not before.**
- **§8.3's cost estimate stands unchanged** (~150 emitters, two figures per conditional branch,
  call-graph following for anything better than a lower bound). Nothing measured since makes it
  cheaper.

**A recommendation that was right, recorded because those deserve recording too.** §8.3 proposed,
as "a cheaper diagnostic worth considering first, and not previously named," reading `LY`/`STAT`
around `update_visuals` to measure how far past VBlank it finishes. **That probe was built, it
worked, and it is the entire evidentiary basis of this correction** — including the basis for
overturning the finding it was commissioned to confirm. It cost roughly a dozen instructions and
replaced a wrong conclusion with a measured one. §8.3's judgement that this should come before the
150-emitter package was correct and is hereby vindicated.

**Revised §8.4 guidance** (superseding the list above):

- **Do not** treat the per-frame budget as generous — unchanged, and now measured rather than
  inferred.
- **Do** require any package adding per-frame work **at all** to state its cost impact. The
  earlier wording singled out `apply_input`/`update_visuals`; that is too narrow, since idle
  frames already reach `LY` 152-153.
- **Do** build the runtime `LY` budget assertion first (`BL-0069`, via `IP-9030`'s re-scope).
- ~~**Do** build the VRAM-write-integrity check first.~~ **Withdrawn** — unbuildable in this
  harness; see `R305` §5.
- **Do not** infer a hardware mechanism from an emulator observation without checking the
  emulator's implementation of that mechanism. This addendum's original version did exactly that,
  and the check would have cost one `grep`. `R305` §3 carries it as a standing rule.
- **Do not** conclude the engine is broken — unchanged and still true. Audio writes APU registers,
  not VRAM. Nothing observable is wrong; what is thin is the margin, and the real exposure is on
  hardware, where mode 3 is enforced and nothing here can test it (`R102` §3c).

#### Sources
- [`IP-9030` Blocking Report](../../implementation/packages/IP-9030-vram-write-integrity-detection.md#blocking-report--2026-07-31-08-code-implementation-run-102) — both experiments and full data, 2026-07-31.
- [`R308` §8.5](R308-performance-budgeting.md) — the sibling tier's matching self-correction.
- [`R301` §3](R301-pyboy-headless-api.md) / [`R305` §5](R305-emulator-test-design.md) — PyBoy's
  unconditional VRAM writes (`mb.py:502-511`) and the resulting can/cannot-establish boundary.
- [`R102` §3c](R102-ppu-modes-and-vram-oam-access-timing.md) — the untested hardware exposure.
- Local experiments, 2026-07-31, PyBoy 2.7.0: ROM-side live-`LY` probes, WRAM-mirror comparison,
  ROM-side frame counter. Instrumented builds were throwaway and reverted.
