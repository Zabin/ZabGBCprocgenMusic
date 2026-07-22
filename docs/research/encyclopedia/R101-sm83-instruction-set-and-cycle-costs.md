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

## 7. Related Topics
R108 (APU register-write timing, the one place a misplaced write could matter more than raw
cycle count), R110 (interrupt/VBlank timing), R308 (performance budgeting — the topic that
actually carries this project's per-frame budget evidence).
