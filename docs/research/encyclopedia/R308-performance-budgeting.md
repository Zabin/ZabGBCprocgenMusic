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

## 7. Related Topics
R110 (the cycle-budget discipline this topic's "no compression needed yet" call depends on),
R307 (architecture patterns this topic's memory-mapped-data confirmation supports).
