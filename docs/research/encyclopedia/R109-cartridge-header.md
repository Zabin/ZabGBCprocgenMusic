# R109 — Cartridge Header, Checksums & Boot Requirements

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose
Ground `gbc_lib.py`'s `set_header` (reused verbatim from the reference project) and the G5
build gate (fixed-size ROM, valid header).

## 2. Scope
The header block at `0x0100`-`0x014F`: entry point, Nintendo logo, title, CGB flag, cartridge
type, ROM/RAM size codes, header checksum, global checksum.

## 3. Concepts
- `0x0100`-`0x0103`: entry point (`NOP; JP main`).
- `0x0104`-`0x0133`: the fixed 48-byte Nintendo logo bitmap — the boot ROM halts if this doesn't
  match exactly.
- `0x0134`-`0x0142`: title (ASCII, padded).
- `0x0143`: CGB flag (`0x80` = CGB-enhanced, works on DMG too — the value `set_header` writes).
- `0x0147`: cartridge type (`0x00` = ROM ONLY, used for Driftune per MSTR-001 C2's no-SRAM
  decision; `0x03` = MBC1+RAM+BATTERY, used by the reference project for its save data).
- `0x0148`/`0x0149`: ROM size / RAM size codes.
- `0x014D`: header checksum — `x=0; for each byte 0x134..0x14C: x = x - byte - 1`, low byte kept.
- `0x014E`-`0x014F`: global checksum — sum of all bytes except these two, big-endian.

## 4. Operational Context
`gbc_lib.py:set_header` implements exactly this (confirmed by direct code read — it is the
reused-verbatim file, unchanged from the reference project). `test_rom.py` T1 independently
recomputes the header checksum and compares, rather than trusting the build script's own
arithmetic — this is the correct independence pattern (the test must not share a bug with the
code it's checking).

## 5. Implementation Guidance
No change needed — `IP-0001`'s T1 suite already re-derives and checks the checksum rather than
asserting a hardcoded expected byte, which is the right defense against a shared-bug false pass.
Any future header field change (e.g. adding a battery-backed cart type, should Driftune ever want
SRAM — currently a non-goal, MSTR-001 SS4) must update both `set_header`'s call site *and*
`test_rom.py`'s T1.4-equivalent check together.

## 6. Feature Mapping
NFR-1000 (valid header, fixed ROM size), `IP-0001` T1 suite.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `gbc_lib.py`'s `set_header` — title bytes, CGB compatibility flag `0x80`, cart type, and the header checksum the boot ROM verifies. Asserted by `test_rom.py` `T1.1`-`T1.5` as a permanent G5 gate.

## 7. Related Topics
R108 (the cart type's interaction with which hardware features are available — ROM ONLY means no
SRAM-backed persistence is possible even if a later increment wanted it). R304 (ROM validation —
the checksum *mechanism*, split out from this topic's field-*content* coverage). R106 (MBC/SRAM —
the cart-type/RAM-size bytes this topic covers, in more depth, for if that scope commitment is ever
revisited). R112 (whole-address-space memory map this ROM's header describes).
