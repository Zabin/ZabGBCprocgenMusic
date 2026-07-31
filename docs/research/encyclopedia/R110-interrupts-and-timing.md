# R110 — Interrupt Model & ISR Conventions

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose
Ground the VBlank-driven main loop that every frame of generation, input, and (eventually)
visualizer work runs inside — this is the timing backbone R108's cycle-budget note depends on.

## 2. Scope
The VBlank interrupt, the reference project's flag-and-HALT main-loop convention (reused
verbatim), and the ~59.7Hz frame cadence it provides.

## 3. Concepts
The Game Boy's PPU raises a VBlank interrupt once per frame (~59.7Hz, the ~70224-cycle frame at
~4.19MHz). A minimal ISR at the VBlank vector (`0x0040`) sets a WRAM flag and returns (`RETI`);
the main loop `HALT`s (stopping CPU execution until any enabled interrupt fires), then on wake
checks the flag, clears it, and does the frame's real work — this defers all per-frame logic to
a predictable, low-power-between-frames point rather than doing it inside the ISR itself (keeping
the ISR itself trivially short, a standard embedded convention). Empirically, PyBoy's boot ROM
(logo animation) runs for approximately 90 frames before jumping to cartridge code at `0x0100` —
confirmed directly against this project's own built ROM during `IP-0001` (see `Claude.md`
"Emulator Test Command" / `test_rom.py`'s `BOOT_FRAMES` constant), not assumed from documentation.

**Measured wake latency and per-frame window consumption (added 2026-07-31, `BL-0069`).** The
flag-and-`HALT` pattern above had never been measured against the actual scanline counter on this
project — only reasoned about. It has now been, by reading the live `LY` register (`0xFF44`) from
inside the ROM at five points per frame and storing each to WRAM for the harness to read back
(method and full table: [`R101` §8.5](R101-sm83-instruction-set-and-cycle-costs.md)). Two results
belong to this topic:

- **`HALT` wakes at `LY` = 144, on every frame, of every input class, without exception** — the
  first scanline of VBlank. The interrupt path (PPU raises VBlank → ISR at `0x0040` sets the flag
  and `RETI`s → main loop wakes, re-checks and clears the flag) costs no measurable scanline. The
  pattern §3 describes as "a predictable point" is confirmed predictable to better than one
  scanline, which is the first hard evidence for a claim this topic has made since `IP-0001`.
- **The per-frame work then consumes ~9 of VBlank's 10 scanlines before the visualizer runs.**
  `read_joypad`+`apply_input`+`engine_tick` bring `LY` to 152-153; `update_visuals` finishes on
  153, the window's last line. That is a fact about the *frame cadence* this topic owns, not just
  about the visualizer: the "fixed, known tick rate" §4 relies on is intact — the engine keeps
  perfect time and no frame is dropped — but the VBlank window inside that cadence is
  substantially spent, and nothing in the build guards what remains. `GDS-06` §2.2a records the
  architecture-level consequence; `R101` §8.5 the cycle-budget one.

Note what this does *not* say: the frame rate is fine, the tick is regular, and `HALT` is doing
its job. What is nearly exhausted is the sub-frame window in which VRAM is writable — a different
budget from the one `NFR-1010`'s stress runs measure.

### Sources
- Project's own empirical measurement (`IP-0001`, `test_rom.py` `BOOT_FRAMES` derivation) —
  primary source; no external citation needed for an emulator-specific timing constant.

## 4. Operational Context
`build_rom.py`'s VBlank ISR and `main_loop` (flag-check/HALT/clear/dispatch) are exactly this
pattern, reused verbatim from the reference project's `asm_game.py`. `music_engine.py`'s
`engine_tick` and `input_map.py`'s `read_joypad`/`apply_input` are called once per this frame
cadence from `main_loop`, giving the whole engine a fixed, known tick rate to derive tempo-in-
frames from (`music_engine.py`'s `TEMPO_TABLE`, computed from BPM at ~60fps).

## 5. Implementation Guidance
- Any future ISR (none planned beyond VBlank for v1) must stay minimal (flag-set-and-return) —
  do not move generation logic into the ISR itself; the existing flag-and-HALT pattern is correct
  and should not be changed without a concrete reason.
- **Do not assume that "the frame's work starts in VBlank" means "the frame's work fits in
  VBlank."** Measured (§3): the wake is at `LY` 144 but `update_visuals` finishes at `LY` 153, the
  window's last line. Any package adding work to `read_joypad`/`apply_input`/`engine_tick` in
  `input_map.py`/`music_engine.py` spends head-room the visualizer needs, even though none of
  those routines touch VRAM themselves. State the per-frame cost impact of such a change
  explicitly (`GDS-06` §2.2a's widened posture) — a stress run will not catch it, because
  exhausting the VBlank window produces no hang, no slowdown and no dropped frame.
- **Do measure with a ROM-side `LY` probe rather than inferring from emulator-visible effects.**
  Reading `LY` and storing it to WRAM costs ~4 instructions and depends on nothing the emulator
  might not model; inferring frame timing from whether a VRAM write appeared to land does depend
  on that, and got this project a wrong answer (`R102` §3b/§3c, `R305` §3).
- Tests that check boot-time state must wait at least `BOOT_FRAMES` (~90) frames first — this is
  now documented in three places (`memory.md`, `test_rom.py`, this topic) precisely because it
  was a real, easy-to-hit mistake during `IP-0001` (a test read WRAM before the boot ROM had even
  handed control to cartridge code).

## 6. Feature Mapping
NFR-1010 (per-frame budget), GDS-03 SS2 (main loop structure), `IP-0001`'s T2/T3 suites; the
2026-07-31 wake-latency/window-consumption measurement grounds `GDS-06` §2.1/§2.2a and the
`LY`-budget assertion recommended for `IP-9030`'s re-scope.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `build_rom.py`'s shipped interrupt model: the VBlank ISR at `0x0040` setting `VBLANK_FLAG`, the `RETI`-stubbed unused vectors, `IE` configured for VBlank only, and the `HALT`-until-VBlank main loop. Formally specified as the per-frame call-order contract in [GDS-09 §5](../../architecture/09-interface-specification.md). Requirement: `NFR-1010`.
 **Updated 2026-07-31 (`BL-0069`):** §3's measured wake latency (`LY` 144) and window consumption (~9 of 10 scanlines) traces forward to `GDS-06` §2.1's corrected standing and to `IP-9030`'s re-scoped `LY` guard.
## 7. Related Topics
R108 (what happens inside a tick — the register writes this cadence gates), R305 (test-design
implications of the boot-frame-count discovery). R102 (the PPU-mode timing the VBlank interrupt
is keyed to), R105 (OAM DMA — a case where the CPU is HRAM-restricted, relevant if this project
ever combines DMA with the existing VBlank ISR).
