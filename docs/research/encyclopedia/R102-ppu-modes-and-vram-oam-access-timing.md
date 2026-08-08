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

## 3b. ~~Addendum — 2026-07-26: this project has now actually hit the Mode-3 hazard~~ — WITHDRAWN 2026-07-31

> ⚠️ **This section's central claim was false and is withdrawn.** This project has **not** observed
> the Mode-3 hazard, and — as §3c explains — it structurally *cannot* observe it with its current
> harness. The superseded text is kept below rather than deleted, because how a well-grounded,
> independently-reproduced claim turned out to be unobservable is worth a future reader's time.
> **The design lesson at the end of this section survives intact and is, if anything, more sharply
> supported by the corrected measurement — it is restated in §3c.**

~~Until 2026-07-26 the Mode-3 ignored-write behaviour §3 documents was a hazard this project had
grounded but never observed. It has now been observed, repeatedly and reproducibly, and this is
the first real instance — worth recording here because §3's abstract statement and a concrete
shipped symptom are very different things for a future reader.~~

~~**Observed:** the visualizer's settings-indicator writes are silently discarded on any frame where
`apply_input` or `engine_tick` does more than minimum work — a Start press (style application), a
Select press (full `init_engine` reset), or an autonomous song-form phase transition. In the
song-form case the loss is **partial**: the first of five cells lands and the fourth does not.~~

~~**Why §3 explains it exactly:** the main loop `HALT`s until VBlank (Mode 1), then runs all
per-frame work before its visualizer writes. When that work outlasts the 10-scanline VBlank
window, the PPU has already resumed and later writes land in whatever mode they hit — surviving in
Mode 0/2, **discarded in Mode 3**, precisely as §3 states. The partial loss is the signature: a
write sequence straddling the Mode 1 → Mode 2/3 boundary loses only its tail.~~

**Why it was wrong** (full evidence: `R308` §8.5, `R101` §8.5, and `IP-9030`'s Blocking Report):
PyBoy 2.7.0 accepts every VRAM write regardless of PPU mode — `pyboy/core/mb.py`'s `setitem()`
writes `lcd.VRAM0`/`VRAM1` unconditionally at lines 502-511, with no `STAT`/mode check anywhere
(`R301` §3). **A Mode-3 discard is not an observable event in this harness**, so the 2026-07-26
"observation" was not one. What was actually seen was a `pb.tick()` mid-frame sampling artifact
producing a uniform one-frame display lag across *all* frame classes, idle frames included; a WRAM
mirror taken at the instant of each write confirms every write lands. The "partial loss" that read
as a Mode-1→Mode-3 boundary signature was a partial *observation* — the cells written before the
sampling point versus after it.

### Sources
- [`R308` §8.5](R308-performance-budgeting.md) / [`R101` §8.5](R101-sm83-instruction-set-and-cycle-costs.md)
  — the sibling tiers' matching self-corrections, 2026-07-31.
- [`IP-9030` Blocking Report](../../implementation/packages/IP-9030-vram-write-integrity-detection.md#blocking-report--2026-07-31-08-code-implementation-run-102)
  — both falsifying experiments and the full data, 2026-07-31.
- [`R301` §3](R301-pyboy-headless-api.md) — PyBoy 2.7.0's unconditional VRAM writes, `mb.py:502-511`.
- ~~[`R308` §8.2] — the 2026-07-26 experiment producing the four-frame-class table.~~ Withdrawn.

## 3c. The Mode-3 exposure is live, measured, and untested (2026-07-31)

§3b's *claim* was wrong. The *concern* underneath it was right, and the corrected measurement
supports it better than the original evidence did. This section states what the project actually
knows, because it is the useful thing for a future reader and nothing else in the tree carries it.

**Three facts, in the order that matters:**

1. **Mode-3 enforcement is real on hardware.** §3's citation stands unchanged: on a real CGB, VRAM
   is inaccessible to the CPU during Mode 3 and writes issued then are silently ignored
   ([Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html)).
   Nothing about the falsification touches this.
2. **PyBoy does not model it.** Every VRAM write is accepted regardless of mode (`R301` §3,
   `mb.py:502-511`). So the project's entire test suite — 122 checks, every stress run, every
   `VR-xxxx` — is silent on this property by construction, and always was.
3. **This project's margin against it is now measured, and it is thin.** ROM-side live-`LY` probes
   (`R101` §8.5 carries the table) show `HALT` waking at `LY` 144 on every frame, per-frame work
   before the visualizer consuming through `LY` 152-153, and the shipped `update_visuals`
   finishing at **`LY` 153 — VBlank's final scanline**. Adding ~7 stores per frame pushed the
   visualizer's writes to `LY` 0-9, i.e. into rendering, where Modes 2 and 3 alternate. The
   head-room is a handful of instructions, on every frame including idle ones.

**Therefore: the hazard §3 documents is a live exposure for this ROM, and it is untested and
untestable here.** The shipped build appears to clear it — by one scanline. Whether it *actually*
clears it on silicon, where the enforcement exists, is a question this project cannot answer with
PyBoy. `GDS-06` §2.3 and `GDS-02` §7 record it as the first concrete, named question that requires
either physical hardware or a mode-accurate emulator (SameBoy/BGB, `R309`) — the latter being the
cheap partial substitute worth trying first.

**Severity, stated honestly so this is not over-read:** the failure mode, if it exists on
hardware, is a cosmetic tilemap cell showing a stale value for one frame, self-healing via the
stateless re-render contract (`GDS-08` §3). No audio is affected — APU register writes are not
VRAM writes and are unaffected by PPU mode. This is a fidelity gap worth closing, not a defect
worth alarm.

**The design lesson §3b drew, restated — it survives the falsification unchanged and is the most
transferable thing on this page.** Beyond what §5 already says: *"issue VRAM writes during VBlank"
is not achieved by starting the frame's work in VBlank.* It is only achieved if the writes
themselves are still inside the window when they execute. A long main-loop iteration that begins
in VBlank and ends outside it satisfies the letter of the rule and violates its substance. The
2026-07-26 evidence for this was wrong; the 2026-07-31 measurement establishes it directly, and
`GDS-06` §2.1 has been corrected to draw exactly this distinction (entering the window versus
fitting inside it).

**A second lesson, methodological, which this section exists to make unmissable:** §3b inferred a
*hardware* mechanism from an *emulator* observation without checking whether the emulator
implements that mechanism. The check costs one `grep` of the emulator's memory-write path. Skipping
it produced a claim that propagated into five documents and one planned implementation package,
and survived independent verification, before being caught. `R305` §3 now carries this as a
standing rule for anyone writing tests or drawing conclusions from this harness.

### Sources
- [Pan Docs — Accessing VRAM and OAM](https://gbdev.io/pandocs/Accessing_VRAM_and_OAM.html) —
  Mode-3 inaccessibility on real hardware (same citation as §3).
- [`R101` §8.5](R101-sm83-instruction-set-and-cycle-costs.md) — the live-`LY` measurement table.
- [`R301` §3](R301-pyboy-headless-api.md), [`R305` §3/§5](R305-emulator-test-design.md) — the
  harness limitation and the standing rules derived from it.
- [`GDS-06` §2.1/§2.3](../../architecture/06-non-functional-requirements.md),
  [`GDS-02` §7](../../architecture/02-system-context.md) — the architecture-level record.

## 4. Operational Context
`build_rom.py`'s `main_loop` (`build_rom.py:75-85`) `HALT`s the CPU until the VBlank interrupt
sets `VBLANK_FLAG` (the ISR at `0x0040`, GDS-07 §8), then runs `engine_tick`/`update_visuals`
synchronously in the same wake. ~~meaning every VRAM/tilemap write ... executes at the very start
of the VBlank window~~ — **corrected 2026-07-31 (§3c): that was an assumption, and measurement
refutes it.** The *wake* is at the very start of the window (`LY` 144, confirmed on every frame),
but `update_visuals`'s writes are not: `read_joypad`+`apply_input`+`engine_tick` run first and
consume through `LY` 152-153, so the visualizer's tilemap-cell and `BCPS`/`BCPD` writes
(`visuals.py`'s `update_visuals`) execute at the **end** of the window, finishing on `LY` 153.
Boot-time `init_visuals` writes are unaffected — they run before the LCD is enabled. `10-integration-review`'s
Foundation-bucket report confirmed this pattern is correct by inspection (see
`docs/reviews/integration-review-foundation-bucket.md`, Dimension 2); this topic supplies the
hardware citation that inspection was implicitly relying on. **Note (2026-07-31):** that
inspection was correct about the *structure* — there is exactly one place visualizer code runs and
it is inside the gated region — but inspection alone could not have caught how little of the
window remains by the time it runs. That took measurement (§3c).

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
 **Updated 2026-07-31 (`BL-0069`):** §3b withdrawn; §3c's untested-hardware-exposure finding traces forward to `GDS-06` §2.3 and `GDS-02` §7 (`BL-0058`), and to the `R309` mode-accurate-emulator cross-check recommended as the cheap next step.
## 7. Related Topics
R103 (`LCDC`/`STAT`, the registers that report/configure PPU mode), R104 (CGB palette registers,
subject to the same access-timing rule), R110 (interrupt model — the VBlank ISR itself), R308
(performance budgeting).
