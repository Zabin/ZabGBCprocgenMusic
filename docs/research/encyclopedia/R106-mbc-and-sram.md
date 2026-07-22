# R106 — MBC / SRAM

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (kept brief — MSTR-001 C2 makes no save/battery commitment at v1; see §5)

## 1. Purpose
Record why this topic stays out of scope, with real citations, and what would need to change if
that scope commitment is ever revisited.

## 2. Scope
Memory Bank Controllers (bank-switched ROM/RAM beyond the base 32KB address space) and
battery-backed cartridge SRAM for persistent saves.

## 3. Concepts
The Game Boy's 16-bit address bus gives a fixed 32KB ROM window; cartridges larger than 32KB (or
that want persistent RAM) use an MBC chip on the cartridge itself to bank-switch additional ROM/
RAM into that window, controlled by writing to specific ROM-mapped address ranges (which the MBC
intercepts rather than the ROM itself). Cartridge RAM (`0xA000`-`0xBFFF` when banked in) is often
battery-buffered — a coin cell keeps the SRAM powered while the console is off, preserving saves.
[Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html); [Pan Docs —
MBCs](https://gbdev.io/pandocs/MBCs.html). MBC1 (up to 2MB ROM / 32KB RAM) is the most common
controller in the wild.

### Sources
- [Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html)
- [Pan Docs — MBCs](https://gbdev.io/pandocs/MBCs.html)

## 4. Operational Context
`build_rom.py` writes cart type `0x00` (ROM ONLY — confirmed by `test_rom.py` T1.4 and every
`VR-000x`'s header audit) — no MBC, no cartridge RAM, no battery. This is a deliberate MSTR-001 C2
commitment ("no save/battery commitment at v1"), not an oversight: the entire 32KB address space
is already sufficient for the current ROM (`test_rom.py` T1.1 confirms exactly 32768 bytes used),
and nothing in the shipped feature set (four-channel procedural generation, no persistent
save-state) needs RAM beyond WRAM's own `0xC000`-`0xDFFF` block.

## 5. Implementation Guidance
**No MBC/SRAM work is needed or planned.** If a future vision amendment revisits MSTR-001 C2 (e.g.
to persist a favorite seed/preset across power cycles, or the ROM outgrows 32KB once
`BL-0020`'s multi-scheme architecture question lands), the concrete next steps would be: (1) pick
an MBC (MBC1 or MBC5 are the simplest, best-documented choices for a project this size — MBC5 is
the more modern/flexible pick if bank count needs to grow past MBC1's ~2MB ceiling, unlikely
given Driftune's scale), (2) `build_rom.py`'s `set_header` call would need the corresponding
cart-type byte and RAM-size byte, and (3) this topic should be substantially expanded with the
chosen MBC's actual bank-switch register protocol before any code is written against it — this
entry is a scope-commitment record, not implementation grounding, until that vision decision is
made.

## 6. Feature Mapping
MSTR-001 C2 (the non-goal this topic grounds), `test_rom.py` T1.4 (cart-type=ROM-ONLY assertion).

## 7. Related Topics
R109 (cartridge header — the cart-type/RAM-size bytes this topic would touch if revisited), R112
(memory map overview).
