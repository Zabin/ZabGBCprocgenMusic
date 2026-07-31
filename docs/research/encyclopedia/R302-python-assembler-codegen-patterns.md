# R302 — Python-Assembler Codegen Patterns

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored
  2026-07-22 (was "no gap yet — simple label/fixup mechanism"; re-evaluated against the now
  7-package-shipped tree — judgment confirmed, authored as a real grounding topic rather than a
  bare row); **§8-9 addendum added 2026-07-22** (MSTR-001 §9 thread — what adopting R106's
  MBC5 recommendation would cost this design; a different question from §1-7's "is the current
  flat-32KB design clean," answered honestly as real assembler-architecture work, not a patch)

## 1. Purpose
Ground `gbc_lib.py`'s label/fixup assembler pattern against general two-pass-assembler design
practice, and re-confirm whether the mechanism still scales cleanly now that the tree has grown
across 7 shipped packages plus 2 remediation packages in planning.

## 2. Scope
The forward-reference resolution pattern `gbc_lib.py`'s `ROM` class implements: a two-pass
label/fixup assembler, not any general-purpose assembler theory.

## 3. Concepts
This is the standard **two-pass assembler** pattern: pass one emits bytes and records each
label's byte offset as it's defined (`ROM.label`, `gbc_lib.py:24-26`); forward references (a jump
target not yet defined) are recorded as **fixups** — a `(position, label-name, type)` tuple — with
a placeholder byte written in their place (`ROM._abs`/`ROM._rel`, `gbc_lib.py:30-41`); pass two
(`ROM.resolve`, `gbc_lib.py:194-204`) walks every fixup, looks up the now-fully-populated label
table, and patches the real address/offset in. This is a textbook technique (the same shape as
how real two-pass assemblers, including RGBDS, resolve forward `jr`/`call` targets) — the
project's own choice to hand-roll a minimal version rather than depend on an external assembler
(RGBDS) is a deliberate scope decision (MSTR-001's "no external assembler" commitment,
`Claude.md`'s own "no RGBDS" framing), not a gap in assembler-theory knowledge. This is a
project-internal design decision documented in the code itself rather than externally-sourced
literature — no external citation applies to "is a two-pass label/fixup assembler a sound
pattern," since it's a well-established, uncontroversial technique with no controversy or
alternative worth surveying at this project's scale.

## 4. Operational Context
Two fixup types exist: `'abs16'` (a full 16-bit address, used by `CALL`/`JP`/`LD_HL,label` — no
range limit) and `'rel8'` (an 8-bit signed relative offset, used by `JR`/`JR_Z`/`JR_NZ` — range
`-128..127`). `ROM.resolve()` raises `Exception(f"JR oor '{lbl}': {off}")` if a relative fixup
ends up out of range at resolve time — this is exactly the failure mode `IP-0007`'s own package
doc records hitting and fixing (`docs/implementation/packages/IP-0007-autonomous-recovery-and-randomize.md`:
"Fixed two `JR`-out-of-range assembler errors... converted to `JP_NZ`" once the recovery logic
lengthened `_emit_channel_gen`/`_emit_noise_gen`). This is the mechanism working exactly as
designed — a hard, unambiguous build-time failure rather than a silently-wrong relative offset —
not a defect. `ROM.label()` raises on a duplicate label name (`gbc_lib.py:25`), the other class of
error this pattern catches early. Across 7 shipped packages (`IP-0001`-`IP-0007`) plus the two
remediation packages now in planning (`IP-9010`/`IP-9020`), the label/fixup mechanism has needed
zero changes — every new routine just calls `rom.label(...)`/emits opcodes/calls `_abs`/`_rel`
through the existing higher-level opcode methods, the same pattern from `IP-0001` onward.

## 5. Implementation Guidance
**No change needed — the "no gap yet" judgment is reconfirmed**, now with the `IP-0007`
`JR`-out-of-range incident as concrete evidence the mechanism correctly surfaces the one error
class it exists to catch (rather than that error class going unnoticed and shipping a
subtly-broken jump). **Do** keep converting a routine to `JP`/`JP_NZ`/`JP_Z` (absolute, unlimited
range) rather than `JR`/`JR_NZ`/`JR_Z` (relative, ±127 bytes) whenever a `JR oor` exception fires
during a build — this is the established, already-proven fix pattern (`IP-0007`), not something
to solve a new way each time. **Do not** add automatic `JR`→`JP` promotion to `gbc_lib.py` itself
— the explicit build-time failure is more valuable than a silent code-size-increasing rewrite,
given how rare the failure has been (once, across 9 packages).

## 6. Feature Mapping
None directly (a toolchain-internal topic) — grounds every package's own `Files to
Create/Modify` claims about `music_engine.py`/`build_rom.py`/etc. being buildable as described.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `gbc_lib.py`'s shipped two-pass label/fixup resolution and the memory-mapped-in-place `ROM.data` model — now formally specified as an interface in [GDS-09 §2](../../architecture/09-interface-specification.md). Every `IP-xxxx` in the tree is built through it.

## 7. Related Topics
R301 (PyBoy headless API — the other half of the build-then-verify toolchain), R304 (ROM
validation — the header/checksum pass that runs after `resolve()`), R109 (cartridge header, the
data `set_header` writes), R106 (MBC/SRAM — the §8 addendum below grounds what adopting R106's
MBC5 recommendation would cost this topic's own assembler).

## §8 Addendum (2026-07-22) — what bank-switching would cost this design

**Added for MSTR-001 §9's third research thread** (v1.2 reopened the single-bank non-goal;
R106, this tier's sibling topic, names MBC5 as the concrete recommendation *if* bank-switching is
ever adopted). This addendum grounds the tooling cost honestly — it does **not** reconfirm "no
gap" the way §5 above does for the current flat-32KB design; those are two different questions
answered under two different assumptions, both true in their own scope.

**`gbc_lib.py`'s `ROM` class is architecturally single-bank today, not incidentally.**
`ROM.__init__` allocates one flat `bytearray(size=32768)` (`gbc_lib.py:11`); `self.pos`/`self.labels`/
`self.fixups` all address into that one flat space — a label is just a byte offset, with no bank
component (`gbc_lib.py:24-26`). This is the same design R302 §3-4 already confirmed is clean and
textbook *for a flat address space* — the two-pass label/fixup mechanism itself (record offsets,
patch forward references) is bank-agnostic in principle, but this project's specific
implementation has never needed to represent "which bank a label lives in," so it doesn't.

**Real GBC bank-switching splits the ROM window into a fixed half and a switchable half**: `$0000`-
`$3FFF` is always bank 0; `$4000`-`$7FFF` is whichever bank was last selected by writing the MBC's
bank-select register (R106 §3's MBC1/3/5 protocols) [Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html).
Concretely, adopting this would require, at minimum: (1) `ROM.label()`/`self.labels` gaining a
bank component — a label is no longer just an offset, it's `(bank, offset)`, and two different
banks can validly reuse the same `$4000`-`$7FFF` offset for unrelated code; (2) `_abs`/`_rel`
fixups need to know whether a call target is in the fixed bank-0 region (safe to `CALL` directly
from anywhere) or in a switched bank (only safely callable if the caller first confirms/sets the
right bank selected — calling into a *different*, not-currently-switched-in bank via a plain
`CALL` silently executes whatever code happens to be switched in, a real and dangerous silent-
failure class this project's `resolve()` currently has no way to detect); (3) `build_rom.py`'s
section-layout model (which currently just appends sections sequentially into the one flat
`bytearray`) would need real per-bank layout/budget tracking, not just a longer flat file.
**This is genuine assembler-architecture work — a new addressing model, not a config flag or a
small patch** — consistent with this addendum's own instruction to assess it honestly rather than
undersell the cost.

**PyBoy itself is not the blocker.** PyBoy's cartridge-loading module dispatches to dedicated
per-controller submodules — `cartridge.py` imports and dispatches to `.mbc1`/`.mbc3`/`.mbc5`
(among others) based on the header's cart-type byte [PyBoy source — `pyboy/core/cartridge/cartridge.py`](https://github.com/Baekalfen/PyBoy/blob/master/pyboy/core/cartridge/cartridge.py) —
confirming bank-switched ROMs are natively, properly emulated (unsurprising, since PyBoy plays
real commercial MBC1/3/5 cartridge dumps as its primary use case, not just Driftune's flat-ROM
case). `test_rom.py`'s existing memory-read/register-assertion pattern (R301) would keep working
unchanged for reads inside the fixed bank-0 window; **the only new test-design concern is that a
memory read at a switchable-window address (`$4000`-`$7FFF`) is now ambiguous without also
tracking which bank was selected at read time** — a genuinely new piece of state `test_rom.py`
would need to track and assert on (e.g. reading the MBC's bank-select shadow, or PyBoy exposing
the currently-mapped bank directly — not independently confirmed this pass, flagged "needs
fetch-verification" if bank-switching is actually adopted).

### §8 Sources
- [Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html) (fixed vs. switchable window)
- [PyBoy source — `pyboy/core/cartridge/cartridge.py`](https://github.com/Baekalfen/PyBoy/blob/master/pyboy/core/cartridge/cartridge.py)
  (confirms native MBC1/3/5 dispatch, Tier-A primary-source evidence)
- Whether PyBoy exposes "currently selected bank" as a directly-readable test-harness value:
  not confirmed this pass — flagged "needs fetch-verification" before `test_rom.py` design work
  starts, not asserted as available.

## §9 Implementation Guidance addendum (bank-switching specifically)
- **Do not treat bank-switching adoption as a `gbc_lib.py` patch** — budget it as a real
  assembler-architecture package in its own right (`07-implementation-planning` should size it
  honestly, likely its own `IP-8xx0`-scale refactoring effort or larger, not folded into whatever
  feature package motivated the ROM-budget pressure).
- **Do** keep the current flat-address design exactly as-is until bank-switching is genuinely
  needed (R106 §4/§5's own "no MBC/SRAM work is needed or planned" still holds for the *shipped*
  ROM) — this addendum grounds a future cost, it does not recommend incurring it now.
- **Do** treat "which bank is selected" as new first-class test state the moment bank-switching
  is adopted — R305 (emulator-based test design) should be revisited alongside any such adoption,
  not assumed to extend for free.
