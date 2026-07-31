# R107 — Joypad Register & Dual-Read Settling

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose
Ground `input_map.py`'s `read_joypad` routine (reused near-verbatim from the reference project)
against the real hardware contract, since it's the entire steering mechanism (MSTR-001 C4).

## 2. Scope
`P1`/`JOYP` (`0xFF00`) — the 2×4 button/d-pad matrix and its read-settling convention.

## 3. Concepts
Buttons and d-pad share one 4-bit read port, selected by writing bit 4 (select d-pad, active
low) or bit 5 (select buttons, active low) of `P1`; the selected group's state then appears in
the low nibble, **active-low** (0 = pressed). If neither group is selected, the low nibble reads
all 1s. Most real programs read the port several times in a row after selecting a group — the
first reads settle the input lines, only the last read is trusted. [Pan Docs — Joypad Input](https://gbdev.io/pandocs/Joypad_Input.html)

### Sources
- [Pan Docs — Joypad Input](https://gbdev.io/pandocs/Joypad_Input.html)
- [gbdev.gg8.se — Joypad Input](https://gbdev.gg8.se/wiki/articles/Joypad_Input)

## 4. Operational Context
`input_map.py`'s `read_joypad` selects the button group, reads `P1` four times before masking
(matching the settling convention above), does the same for the d-pad group, `OR`s and `CPL`s the
two active-low nibbles into one active-HIGH byte at `JOY_CUR`, then derives `JOY_NEW` as the
rising-edge bits versus `JOY_PREV`. This is the reference project's own convention, reused
verbatim because it already matches the hardware-documented settling practice.

## 5. Implementation Guidance
No change needed to `input_map.py` — its four-read settle already matches documented practice.
Any *new* input-reading code (there is none planned) must keep the same four-read pattern rather
than a single read, to avoid intermittent false edges from unsettled lines.

## 6. Feature Mapping
FR-1020–FR-1070 (all edge-triggered input mapping), GDS-07 SS5 (`JOY_PREV`/`JOY_CUR`/`JOY_NEW`).


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `input_map.py`'s shipped `read_joypad` — the two-nibble read, the `CPL` active-high convention, and the settling reads this topic's dual-read guidance requires. Requirements: `FR-1020`-`FR-1070`. Tested by `test_rom.py` `T4`/`T5`.

## 7. Related Topics
R110 (the VBlank-driven frame cadence `read_joypad` runs on).
