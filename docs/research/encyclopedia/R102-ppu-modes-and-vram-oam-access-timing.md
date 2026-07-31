# R102 — PPU Modes, VBlank & VRAM/OAM Access Timing

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-22
  (deferred pending `IP-0006`'s visualizer landing — now shipped and independently `VERIFIED`,
  `VR-0006` — this topic grounds its already-shipped VBlank-gating design)

## 1. Purpose
Ground `visuals.py`'s VRAM/tilemap/palette write timing against the real PPU access-timing
contract — confirming the already-shipped design (writes issued from the main loop right after
waking from `HALT` on the VBlank interrupt) is genuinely safe, not merely accidentally so.

## 2. Scope
The PPU's four per-scanline modes and when VRAM/OAM/CGB-palette registers are CPU-writable.

## 3. Concepts
The PPU cycles through four modes per scanline: **Mode 2 (OAM scan)**, **Mode 3 (pixel
transfer/"HDraw")**, **Mode 0 (HBlank)**, repeating for 144 visible lines, then **Mode 1
(VBlank)** for 10 scanlines' worth of time before the next frame starts. During Mode 2, OAM is
locked to the CPU; during Mode 3, both VRAM and OAM are locked (CPU writes are ignored, reads
return undefined data, typically `$FF`). VRAM becomes CPU-writable during Mode 0 (HBlank) and
Mode 1 (VBlank); OAM becomes writable during Mode 0 and Mode 1 as well. [Pan Docs — Accessing VRAM
and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html). CGB palette registers (`BCPS`/
`BCPD`, see `R104`) follow the same VRAM-class access restriction — they are part of the PPU's
color-RAM path, not directly CPU-RAM, so writing them outside HBlank/VBlank risks the same
ignored-write hazard.

### Sources
- [Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html)
- [Pan Docs — OAM](https://gbdev.io/pandocs/OAM.html)
- [mgba-emu gbdoc — Open Game Boy Documentation Project](https://mgba-emu.github.io/gbdoc/) (cross-reference for mode-timing figures)

## 3b. Addendum — 2026-07-26: this project has now actually hit the Mode-3 hazard

Until 2026-07-26 the Mode-3 ignored-write behaviour §3 documents was a hazard this project had
grounded but never observed. It has now been observed, repeatedly and reproducibly, and this is
the first real instance — worth recording here because §3's abstract statement and a concrete
shipped symptom are very different things for a future reader.

**Observed:** the visualizer's settings-indicator writes are silently discarded on any frame where
`apply_input` or `engine_tick` does more than minimum work — a Start press (style application), a
Select press (full `init_engine` reset), or an autonomous song-form phase transition. In the
song-form case the loss is **partial**: the first of five cells lands and the fourth does not.

**Why §3 explains it exactly:** the main loop `HALT`s until VBlank (Mode 1), then runs all
per-frame work before its visualizer writes. When that work outlasts the 10-scanline VBlank
window, the PPU has already resumed and later writes land in whatever mode they hit — surviving in
Mode 0/2, **discarded in Mode 3**, precisely as §3 states. The partial loss is the signature: a
write sequence straddling the Mode 1 → Mode 2/3 boundary loses only its tail.

**The design lesson this sharpens**, beyond what §5 already says: "issue VRAM writes during
VBlank" is not achieved by *starting* the frame's work in VBlank. It is only achieved if the
writes themselves are still inside the window when they execute. A long main-loop iteration that
begins in VBlank and ends outside it satisfies the letter of the rule and violates its substance.
Cross-referenced from [`R101` §8](R101-sm83-instruction-set-and-cycle-costs.md) and
[`R308` §8](R308-performance-budgeting.md), which carry the measurement and the remediation
priority respectively.

### Sources
- [`R308` §8.2](R308-performance-budgeting.md) — the local experiment (PyBoy 2.7.0, commit
  `e4db8ef`) producing the four-frame-class table and the partial-drop observation.
- [Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html)
  (already cited in §3) — the underlying ignored-write behaviour.

## 4. Operational Context
`build_rom.py`'s `main_loop` (`build_rom.py:75-85`) `HALT`s the CPU until the VBlank interrupt
sets `VBLANK_FLAG` (the ISR at `0x0040`, GDS-07 §8), then runs `engine_tick`/`update_visuals`
synchronously in the same wake — meaning every VRAM/tilemap write (`visuals.py:61-73`'s
`init_visuals` tile-data/tilemap setup at boot) and every per-frame write
(`visuals.py:76-103`'s `update_visuals` tilemap-cell and `BCPS`/`BCPD` palette writes) executes
at the very start of the VBlank window — the one period where both VRAM and the CGB palette
registers are guaranteed CPU-accessible for the whole ~10-scanline duration. `10-integration-review`'s
Foundation-bucket report already confirmed this pattern is correct by inspection (see
`docs/reviews/integration-review-foundation-bucket.md`, Dimension 2); this topic supplies the
hardware citation that inspection was implicitly relying on.

## 5. Implementation Guidance
**No change needed.** `visuals.py`'s `update_visuals` must continue to be called only from the
VBlank-gated `main_loop` path (never from an arbitrary point mid-frame) — if a future package
ever adds a second call site for VRAM/palette writes (e.g. a mid-frame effect), it must either
also be VBlank-gated or explicitly justify writing during Mode 0 HBlank (much narrower window,
~200 T-states per scanline, insufficient for `update_visuals`'s current ~40-byte palette write
budget spread across two 8-color writes). **Do not** move any VRAM/tilemap/palette write earlier
in the frame than the post-`HALT` wake point — that is the one invariant this topic exists to
protect.

## 6. Feature Mapping
FR-1120 (visualizer, read-only + correctly-timed writes), NFR-1010 (per-frame budget — the VBlank
window's actual duration is part of that budget), GDS-07 §8 (`VBLANK_FLAG` synchronization
mechanism).


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds the VBlank-gated visualizer write discipline in `build_rom.py`'s main loop and `visuals.py` (`IP-0006`, `IP-1110`). Requirement: `NFR-1010`. **§3b records the first real observed instance** of the Mode-3 ignored-write hazard this topic documents (`BL-0069`).

## 7. Related Topics
R103 (`LCDC`/`STAT`, the registers that report/configure PPU mode), R104 (CGB palette registers,
subject to the same access-timing rule), R110 (interrupt model — the VBlank ISR itself), R308
(performance budgeting).
