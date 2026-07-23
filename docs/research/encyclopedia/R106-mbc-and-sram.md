# R106 — MBC / SRAM

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22;
  **substantially extended 2026-07-22** (MSTR-001 §9 thread — the v1.0/v1.1 "no save/battery
  commitment" framing this topic originally recorded was reopened by MSTR-001 v1.2, not kept)

## 1. Purpose

Ground the real MBC (Memory Bank Controller) and battery-backed-SRAM facts needed *before*
`03-architecture-design-synthesis` decides whether Driftune adopts bank-switching or persistent
save — this topic grounds facts only, it does not decide either question (MSTR-001 C1/C2, v1.2:
both explicitly reopened, not committed either way).

## 2. Scope

Memory Bank Controllers (bank-switched ROM/RAM beyond the base 32KB address space), battery-backed
cartridge SRAM for persistent saves, and PyBoy's own save-file mechanics (this project's sole
verification target, `strategic-assumptions-register.md` A2) — since a save design that PyBoy
can't verify headlessly would violate MSTR-001 C9's testability requirement.

## 3. Concepts

**The base addressing ceiling and how MBCs lift it.** The Game Boy's 16-bit address bus gives a
fixed 32KB ROM window; cartridges larger than 32KB (or that want persistent RAM) use an MBC chip
on the cartridge itself to bank-switch additional ROM/RAM into that window, controlled by writing
to specific ROM-mapped address ranges the MBC intercepts rather than the ROM itself
[Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html); [Pan Docs — MBCs](https://gbdev.io/pandocs/MBCs.html).
Cartridge RAM (`0xA000`-`0xBFFF` when banked in) is often battery-buffered — a coin cell keeps the
SRAM powered while the console is off, preserving saves.

**Three real MBC options, in increasing capability order:**
- **MBC1** — the most common controller historically. Bank-switching is split: writing
  `$2000`-`$3FFF` selects the lower 5 bits of the ROM bank number (writing `$00` is silently
  converted to bank `$01` — a real hardware quirk, not a bug to reproduce carelessly); writing
  `$6000`-`$7FFF` selects between two modes, "16Mbit ROM/8KB RAM" or "4Mbit ROM/32KB RAM" — MBC1
  cannot address both maximum ROM and maximum RAM simultaneously. Effectively **125 usable ROM
  banks** (banks `$20`/`$40`/`$60` are unavailable due to the same high-bit-reuse quirk that
  remaps bank 0) [GbdevWiki — Memory Bank Controllers](https://gbdev.gg8.se/wiki/articles/Memory_Bank_Controllers).
- **MBC3** — adds a real-time-clock option (irrelevant to Driftune) and RAM enable via writing
  `$0A` to `$0000`-`$1FFF` (`$00` disables); supports up to 128 ROM banks (2MB) [GbdevWiki —
  Memory Bank Controllers](https://gbdev.gg8.se/wiki/articles/Memory_Bank_Controllers).
- **MBC5** — the most modern/flexible of the three, explicitly designed to fix MBC1's bank-0
  quirk: writing `$00` to the ROM-bank-select range genuinely selects bank 0 (unlike MBC1/MBC3).
  ROM bank number is split across two write ranges (low 8 bits at `$2000`-`$2FFF`, 9th bit at
  `$3000`-`$3FFF`), addressing up to **512 banks** (8MB) — far beyond anything this project's
  scale would need. RAM banking uses the same `$0A`-to-enable convention as MBC3, writing the bank
  number (`$00`-`$0F`) to `$4000`-`$5FFF` [GbdevWiki — Memory Bank Controllers](https://gbdev.gg8.se/wiki/articles/Memory_Bank_Controllers).

**PyBoy's save mechanics — the project's actual testability constraint.** PyBoy supports
battery-backed cartridge RAM automatically: "battery-backed RAM is handled automatically, with the
battery flag implying saving of RAM" — the header's cart-type byte must be one of the
RAM+BATTERY variants (e.g. MBC1+RAM+BATTERY, MBC3+RAM+BATTERY, MBC5+RAM+BATTERY) for PyBoy to
persist SRAM at all [PyBoy API docs](https://docs.pyboy.dk/); community reports confirm PyBoy
writes/reads a `.ram`-suffixed file alongside the ROM path, distinct from the `.sav` extension
some other emulators use [PyBoy community reports, single-source — flagged
"needs fetch-verification" against PyBoy's own current-version source if a save design is actually
adopted]. **This means a save design is independently testable headless** — `test_rom.py` could
assert on SRAM content across a simulated power-cycle (stop/restart PyBoy, or write-then-read the
`.ram` file directly) — satisfying MSTR-001 C9 without new tooling.

### Sources
- [Pan Docs — Memory Map](https://gbdev.io/pandocs/Memory_Map.html)
- [Pan Docs — MBCs](https://gbdev.io/pandocs/MBCs.html)
- [GbdevWiki — Memory Bank Controllers](https://gbdev.gg8.se/wiki/articles/Memory_Bank_Controllers)
- [PyBoy API documentation](https://docs.pyboy.dk/)
- PyBoy `.ram`-file-naming/save-trigger specifics: community forum/Discord-mirror reports only,
  single-source — flagged "needs fetch-verification" against PyBoy's own source before any save
  design is built against it.

## 4. Operational Context

`build_rom.py` currently writes cart type `0x00` (ROM ONLY — confirmed by `test_rom.py` T1.4 and
every `VR-000x`'s header audit) — no MBC, no cartridge RAM, no battery. **This is no longer framed
as a permanent commitment** (MSTR-001 v1.2 removed both the single-bank and no-save non-goals) —
it remains the *current shipped shape*, which is a different, weaker claim. The entire 32KB
address space is still sufficient for the currently-shipped feature set (`test_rom.py` T1.1
confirms exactly 32768 bytes used); nothing shipped today needs bank-switching or SRAM.

## 5. Implementation Guidance

- **If a future architecture pass adopts bank-switching for code/data growth** (e.g. `BL-0020`'s
  multi-scheme question, or R219/R220's genre-diversity/style-evolution tables outgrowing 32KB):
  **MBC5 is the concrete recommendation**, not MBC1 — MBC1's bank-0 quirk and split-mode ROM/RAM
  ceiling are real footguns for no benefit at this project's scale, while MBC5's simpler, more
  uniform bank-select protocol costs nothing extra to implement and leaves far more headroom.
  `gbc_lib.py`'s `set_header` call would need the corresponding cart-type byte (MBC5, or
  MBC5+RAM+BATTERY if persistence is also adopted) and ROM/RAM-size bytes; `build_rom.py`'s
  fixed-address-emission model would need genuine bank-switch-aware code emission (a materially
  bigger `gbc_lib.py`/`build_rom.py` change than a header-byte edit alone — not a small addition).
- **If a future architecture pass adopts persistent save** (a favorite seed/style preference/
  collection of discovered pieces, per MSTR-001 §9): **MBC5+RAM+BATTERY is the concrete
  recommendation** for the same reasons, and the design is genuinely testable headless via PyBoy
  per §3 above — this satisfies MSTR-001 C9 without needing new verification tooling, a real point
  in favor of the idea being buildable within this project's existing toolchain, not just
  hardware-plausible.
- **Do not adopt bank-switching or SRAM as a side effect of some other package** — either is a
  real architecture-level decision (MSTR-001 C1/C2, `03-architecture-design-synthesis`'s to make)
  with header/build-chain/test-chain consequences, not a drive-by header-byte change.
- **This topic still does not decide the question** — it only removes the prior "no gap, closed"
  framing and replaces it with real, actionable facts for whenever the decision is made.

## 6. Feature Mapping

MSTR-001 C1/C2 (the reopened, not-yet-decided scope commitments this topic grounds), MSTR-001 §9
(the vision-tier thread that triggered this update), `test_rom.py` T1.4 (current cart-type=
ROM-ONLY assertion, still accurate for the *shipped* ROM, not a forward commitment).

## 7. Related Topics

R109 (cartridge header — the cart-type/RAM-size bytes this topic's recommendations would touch),
R112 (memory map overview), R220 (style evolution/song structure — a plausible source of future
ROM-budget pressure motivating bank-switching), R221 (emotional/energy model — no direct
persistence need, listed for completeness since it's a §9 sibling thread).
