# R304 — ROM Validation

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored
  2026-07-22 (was folded into `R109`; split out now that `test_rom.py`'s T1 suite and
  `gbc_lib.py`'s `set_header` have accumulated enough independent validation logic to warrant its
  own topic, per the original deferral's own "split out if it grows more complex" condition)

## 1. Purpose
Ground `gbc_lib.py`'s header-checksum computation and `test_rom.py`'s T1 validation suite against
the real checksum algorithms and required header fields, as a dedicated verification-methodology
topic distinct from `R109`'s header-*content* grounding.

## 2. Scope
The two Game Boy header checksums (header checksum, global checksum) and what a build/test
pipeline should assert about a produced ROM before trusting it boots correctly.

## 3. Concepts
Two independent checksums exist: the **header checksum** (byte `0x14D`) covers only bytes
`0x134`-`0x14C` (title through the header-version byte) via `x = 0; for each byte b: x = x - b - 1`
(mod 256) — the boot ROM verifies this one and **refuses to boot the cartridge if it's wrong**,
making it the higher-stakes check. The **global checksum** (bytes `0x14E`-`0x14F`, big-endian) is
a simple sum of every byte in the ROM except those two checksum bytes themselves — real hardware
and most emulators do **not** verify this one at boot (it exists for tooling/completeness, not a
boot gate). [Pan Docs — The Cartridge Header](https://gbdev.io/pandocs/The_Cartridge_Header.html)
(the source `R109` already cites for header field layout; this topic adds the verification-role
distinction between the two checksums, which `R109` doesn't dwell on).

### Sources
- [Pan Docs — The Cartridge Header](https://gbdev.io/pandocs/The_Cartridge_Header.html)

## 4. Operational Context
`gbc_lib.py:219-225` computes exactly this pair: the header checksum loop (`chk=(chk-data[a]-1)&0xFF`
over `0x134..0x14C`) matches the documented algorithm precisely, and the global checksum loop sums
every byte except `0x14E`/`0x14F` — both independently re-derivable from the source, not merely
copied from a reference implementation without understanding. `test_rom.py`'s T1 suite
(`test_rom.py:100-111`) validates: exact 32768-byte size (T1.1), title bytes (T1.2), CGB
compatibility flag (T1.3), cart type = ROM ONLY (T1.4, `R106`'s no-SRAM commitment), and **only
the header checksum** (T1.5) — matching the real boot-gating checksum, not the global one. This is
the correct prioritization (the header checksum is what actually gates booting; asserting the
global checksum too would be extra rigor with no corresponding hardware-behavior payoff), but it
means T1 currently has **no assertion on the global checksum at all** — a latent gap: if a future
change to `set_header` or the byte-emission order silently broke the global-checksum computation,
no test would catch it (though it also wouldn't affect whether the ROM boots on real
hardware/emulators, which is why this has never mattered in practice).

## 5. Implementation Guidance
**No change needed to the checksum computation itself** — both algorithms are correctly
implemented and independently re-verified against the documented formulas by this topic. **Minor,
optional test-coverage improvement**: `test_rom.py` could add a T1.6 asserting the global checksum
bytes match an independently-recomputed sum, purely as defense-in-depth against a future
regression in `set_header`'s emission logic — low priority given the global checksum has no
boot-time consequence, not worth a dedicated package on its own, but a natural one-line addition
the next time `test_rom.py`'s T1 suite is touched for another reason. **Do not** add any
additional header validation beyond what `R109`/`R106`/`R112` already ground (cart type, ROM/RAM
size bytes, CGB flag) — the current field set is complete for this project's single-32KB-bank,
no-MBC, no-SRAM design.

## 6. Feature Mapping
`test_rom.py` T1.1-T1.5 (every `VR-000x` report's own G5-gate audit re-confirms these), MSTR-001
C2 (no-SRAM, reflected in the cart-type assertion).


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `gbc_lib.py`'s `set_header` checksum computation and `test_rom.py`'s `T1.1`-`T1.5`, run as a permanent G5 gate on every stage-08 package and re-run by every `VR-xxxx`.

## 7. Related Topics
R109 (cartridge header field *content* — this topic's sibling, covering the checksum
*mechanism* specifically), R106 (MBC/SRAM — the cart-type byte's meaning), R112 (memory map).
