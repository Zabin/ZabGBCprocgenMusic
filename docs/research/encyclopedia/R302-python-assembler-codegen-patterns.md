# R302 — Python-Assembler Codegen Patterns

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored
  2026-07-22 (was "no gap yet — simple label/fixup mechanism"; re-evaluated against the now
  7-package-shipped tree — judgment confirmed, authored as a real grounding topic rather than a
  bare row)

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

## 7. Related Topics
R301 (PyBoy headless API — the other half of the build-then-verify toolchain), R304 (ROM
validation — the header/checksum pass that runs after `resolve()`), R109 (cartridge header, the
data `set_header` writes).
