# GDS-02 — System Context

- **Level:** GDS-02 of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26
- **Upstream:** [GDS-00 Vision](00-vision.md), [GDS-01 Concept of Interaction](01-concept-of-play.md),
  `MSTR-001` (C1/C2/C3/C9/C10), research `R101`/`R104`/`R106`/`R108`/`R109`/`R110`/`R112`
  (hardware), `R301`/`R302`/`R304`/`R305`/`R306`/`R308`/`R309` (tooling & verification)
- **Downstream:** GDS-03 (already authored — see the ordering note below), GDS-06
  (non-functional requirements draw their budget/timing/reproducibility ceilings from §6 here)

## §0 A note on this level's late authoring

This level was authored **after** GDS-03 (Architecture) and GDS-07 (Data Model), not before them.
That is a real deviation from the ladder's own "strictly sequential" rule, and it happened for a
real reason rather than by oversight: this project's first increment went straight from GDS-01 to
the levels implementation actually blocked on (module layout, then the WRAM map), because a
working ROM was the session's goal and those were the two levels standing between the vision and
code. The consequence is worth stating plainly, since it changes what this document *is*:

Every earlier ladder level on this project was **synthesized forward** — written before the thing
it described existed. GDS-02 is the first level authored **against a real, shipped system**. It
therefore describes the system context as-built and measured, not as-intended, and where the
as-built state falls short of an aspiration (notably §7's hardware gap) it says so rather than
describing the aspiration as though it were the context. Nothing here is a forward commitment;
GDS-06 is where the ceilings this level *observes* become requirements the project must *hold*.

## §1 System boundary

**Driftune is one artifact: a 32768-byte Game Boy Color ROM image that generates music in real
time.** Everything the listener experiences is produced by that ROM running on a GBC (or an
emulator of one). There is no server, no companion app, no asset streaming, no external data.

Inside the boundary:

- the ROM image itself (`Driftune.gbc`), including its own generation engine, input handling,
  visualizer, and all ROM-resident data tables;
- the Python build chain that produces it from source, deterministically;
- the headless verification harness that drives and asserts on it.

Outside the boundary, and depended upon rather than owned:

- **The GBC hardware itself** (or PyBoy's emulation of it) — the SM83 CPU, the 4-channel PSG
  (`R108`), the PPU/VRAM (`R102`/`R103`), the joypad (`R107`), the interrupt controller
  (`R110`), and the boot ROM's own power-on sequence.
- **The CPython interpreter** the build/test chain runs under, and **PyBoy 2.7.0** (`R301`) plus
  its own `pysdl2`/`numpy` dependencies.
- **The listener**, who supplies the only input the system takes: eight button edges.

## §2 The artifact — the shipped ROM

Measured against the tree at the time of authoring:

| Property | Value | Grounding |
|---|---|---|
| Size | exactly 32768 bytes (a single 32KB bank, no MBC) | `ADR-0002`; asserted by `test_rom.py` `T1.1` |
| Title | `DRIFTUNE` (bytes `0x134`-`0x13B`) | `R109`; asserted by `T1.2` |
| CGB flag | `0x80` at `0x143` (CGB-compatible) | `MSTR-001` C1, `R109`; asserted by `T1.3` |
| Cart type | `0x00` — ROM ONLY, no MBC, no SRAM, no battery | `ADR-0002`; asserted by `T1.4` |
| Header checksum | valid over `0x134`-`0x14C` (`x = x - b - 1`) | `R304`; asserted by `T1.5` |
| ROM used / free | 4240 bytes used, **28528 free** | `ADR-0002`'s own `rom.pos` instrumentation |

The ROM's internal layout is fixed by `build_rom.py` and is a hardware-imposed shape rather than
a design choice: RST vectors at `0x0000`-`0x003F` (stubbed `RETI`, so a stray interrupt cannot
execute garbage), the VBlank ISR at `0x0040` (which does nothing but set `VBLANK_FLAG` — the
main-loop synchronization convention, per `R110`), the remaining interrupt vectors at `0x0048`-
`0x0060` (also stubbed), the entry point at `0x0100`, the cartridge header at `0x0134`-`0x014F`,
and all engine/visualizer code and data from `0x0150` upward. GDS-07 owns the detail of what sits
where above `0x0150`; this level records only that the layout is single-bank, statically laid out
at build time, and currently occupies 13% of its ceiling.

## §3 The build pipeline

**`python3 build_rom.py <output.gbc>` is the entire build.** There is no external assembler, no
linker, no makefile, and no build-system dependency beyond CPython itself — a direct commitment
from `MSTR-001` C3, and the reason `R302` exists as a topic at all.

The chain is: `gbc_lib.py` provides a generic `ROM` class whose methods emit SM83 opcodes directly
into a byte array and resolve labels in a second pass (`R302`'s two-pass label-resolution
pattern); `music_engine.py`, `input_map.py`, and `visuals.py` each contribute their own routines
and data tables through that class; `build_rom.py` orchestrates the section layout, writes the
header, and computes the checksums (`R304`). The output is a byte-for-byte deterministic function
of the source — the same tree always produces the same ROM, which is what makes
`09-package-verification`'s independent-rebuild check meaningful rather than ceremonial.

One consequence worth naming at system-context altitude: because the "assembler" is ordinary
Python, **build-time computation is free and runtime computation is expensive**. Every frequency
table, Euclidean rhythm pattern, semitone table, and style/motif/song table in this project is
computed in Python at build time and emitted as ROM-resident data, never derived on the SM83 at
runtime. That asymmetry is a property of this system's context, not of any one module's design,
and it shapes every downstream level.

## §4 The verification harness

**`python3 test_rom.py` is the entire test suite** — a single self-running script, 122 checks
across suites `T1`-`T18`, driving the built ROM under PyBoy in headless mode (`window='null'`,
`set_emulation_speed(0)` to remove the real-time throttle, per `R301`).

What makes this harness unusual, and what `MSTR-001` C9 specifically required: **it asserts on
sound-hardware registers and the WRAM engine-state mirror, not on the screen.** A conventional
Game Boy test harness screenshots the framebuffer; this one reads `NR52`'s per-channel active
bits, drives button sequences via `button_press`/`button_release`, and compares WRAM engine state
(`0xC000`-`0xC060`) against expectations. That choice is forced by the domain — the deliverable is
sound, and sound is what must be asserted — and it is the reason GDS-07's WRAM map exists as a
first-class design artifact rather than an implementation detail: the mirror is the test surface.

Two hardware realities the harness must accommodate, both discovered empirically rather than
assumed:

- **The PSG's frequency registers (`NR13`/`NR14` and peers) are write-only** on real hardware and
  in PyBoy's emulation of it (`R108`/`R111`). Reading them back is not a usable signal. "Is the
  engine actually generating" is therefore asserted through the WRAM mirror, not through the
  registers the engine writes — a limitation that directly motivated the mirror's existence.
- **The GBC boot ROM runs its own logo animation for ~90 frames** before cartridge code at
  `0x0100` executes (`R110`, confirmed empirically against this ROM). Every boot-time assertion
  must tick past it first; `test_rom.py`'s `BOOT_FRAMES = 100` constant encodes this.

Alongside the suite, the `run-driftune` utility skill drives the same ROM interactively for
exploratory work — building, running, pressing buttons, reading sound registers, and screenshotting
— which is what stage-09/10 passes use for their independent live drives beyond the shipped
fixtures.

## §5 External actors and interfaces

There is exactly one human actor and one interface.

**The listener** interacts through eight joypad inputs and nothing else (`R107`, GDS-01, GDS-03
§3): D-pad Up/Down (tempo), Left/Right (octave), A (scale), B (density), Start (channel-mix
preset, which since `IP-1080` also applies a coordinated style row), Select (reset-and-randomize).
Every input is edge-triggered — holding a direction does not repeat — and the system has no other
input surface: no menus, no text entry, no configuration, no link cable, no save file to carry
state between sessions (`ADR-0002`).

The system's outputs are likewise two: **audio** on the four PSG channels, and a **minimal
visualizer** (4 channel-activity tiles, a calm/bad-zone palette swap, and since `IP-1110` five
bar-height parameter indicators). GDS-08 owns the visualizer's composition; this level records
only that it exists as an output channel and is strictly a read-only consumer of engine state —
never a second writer.

## §6 External constraints

These are the ceilings the system operates inside. They are observations at this level; GDS-06
turns the ones that need enforcing into requirements.

| Constraint | Current state | Source |
|---|---|---|
| **ROM budget** — single 32KB bank, no bank switching | 4240 / 32768 bytes used; 28528 free | `ADR-0002`, `MSTR-001` §4 |
| **Per-frame CPU budget** — all generation, input, and visualizer work must complete inside one frame | No frame-drop or hang observed across repeated 8000-20000+ frame stress runs | `R101` (cycle costs), `R308` (budgeting), `NFR-1010` |
| **VRAM access window** — visualizer writes must land in VBlank | All visualizer writes run from the VBlank-gated main loop | `R102`, GDS-03 §1 |
| **APU frame-sequencer timing** — envelope/length/sweep tick at fixed sub-frame rates | Respected by the per-note write discipline | `R113` |
| **No persisted state** — no SRAM, no battery, no save file | Every session starts from the same boot preset | `ADR-0002`, `MSTR-001` C2 (reopened as a question, not yet re-decided) |
| **Toolchain** — CPython + PyBoy 2.7.0 (+ `pysdl2`, `numpy`) | Path handling confirmed portable; **dependency manifest absent** | `R306`, `R301` |

The last row is a real, recurring, measured cost rather than a theoretical one: `R306` §4 records
that **every** independent fresh-session verification run in this project's history has had to
discover and install PyBoy manually, because no `requirements.txt` or equivalent exists anywhere
in the repo. It is tracked as `BL-0023` and remains open.

## §7 Real-hardware aspiration — an honest gap

**Driftune has never been run on physical Game Boy Color hardware.** Every assertion this project
makes about its behavior — all 122 checks, every stress run, every verification report, every
integration review — is an assertion about how the ROM behaves *under PyBoy 2.7.0*.

`MSTR-001` §5 names running on real hardware as a goal, and nothing in the design knowingly
depends on emulator-specific behavior: the ROM is a valid CGB cartridge by `R109`/`R304`'s own
criteria, uses no undocumented opcodes, and respects the documented PPU/APU timing windows
(`R102`/`R113`). But "nothing knowingly depends on it" is a reasoned expectation, not evidence.
Named honestly rather than glossed:

- The one APU erratum this project has researched in depth — `R111`'s Channel 3 wave-RAM
  corruption on retrigger — is **confirmed DMG-only and absent on CGB**, so it is explicitly
  *not* an exposure for this target. That is a genuine reassurance and is recorded as one, not
  inflated into a risk. What remains unquantified is the broader question `R111` does not answer:
  whether PyBoy's APU emulation diverges from CGB silicon anywhere this engine's per-frame
  register writes would notice. No research topic currently addresses that, and no evidence
  either way exists.
- `BL-0015` separately records that PyBoy's `tick()`/interrupt timing semantics are not fully
  characterized by this project — a prior verification run flagged it, and it remains unclosed.

This gap does not block any current pipeline stage, and no requirement currently claims hardware
validation. It is recorded here because a System Context level that described a hardware target
this system has never actually met would be describing an intention, not a context.

## §8 What this level deliberately does not decide

- **Module decomposition and the one-job-per-file rule** — GDS-03, already authored.
- **The WRAM map, ROM section layout, and tile index map** — GDS-07, already authored.
- **The visualizer's composition and palette strategy** — GDS-08, still `⛔ Planned`.
- **The module interface contracts** (`build_engine_asm(rom) → patches`, `build_tile_data()`,
  the `ROM` class surface) — GDS-09, still `⛔ Planned`, and flagged as absent by every `FS-1xx`
  authored so far.
- **Whether the cart shape should change** (MBC/SRAM adoption) — `ADR-0002` deferred this with
  named re-triggers; this level records the current shape, it does not reopen the decision.

## §9 Open Questions

1. **Does Driftune actually run correctly on physical GBC hardware?** Genuinely unknown (§7). No
   pipeline stage can answer it — it needs a flash cart and a physical device, which is outside
   every automated stage's reach. Owner: the project owner, as an external validation activity.
   The pipeline's useful contribution would be a **new** `02-research-gbc-hardware` topic
   characterizing where PyBoy's APU emulation is known to diverge from CGB silicon — `R111`
   covers a DMG-only erratum and does not answer this, so the gap is real rather than already
   researched — so that a hardware test would know what to look for instead of being a general
   smoke test.
2. **Should a dependency manifest be added?** `R306` §5 makes a concrete, evidence-backed
   recommendation (`requirements.txt` pinning `pyboy==2.7.0`), and `BL-0023` has tracked it since
   2026-07-22 without being scheduled. Not a design question — a small tooling task whose only
   open part is *when*. Owner: `07-implementation-planning`, whenever a package next touches the
   build/test toolchain.
3. **What are PyBoy's exact `tick()`/interrupt-timing semantics?** `BL-0015` records that a prior
   verification run could not fully characterize them, and this level's §4 relies on frame-tick
   semantics for every timing-sensitive assertion the suite makes (notably `IP-1110`'s own
   disclosed one-frame Select-reset display lag, which is a *timing* observation interpreted
   through PyBoy's model). Owner: `02-research-tooling-and-testing`, if a future run makes the
   ambiguity actually costly; currently `DEFERRED` with no fired trigger.

## Merge gate

- [x] The previous level's gate (GDS-01) was verified closed before this level started — its own
      prose records "Gate: closed 2026-07-21. Next: GDS-03 (Architecture)."
- [x] Primary sources pulled in, not cited from a distance — `MSTR-001` C1/C2/C3/C9's actual
      commitments, `R301`/`R304`/`R306`'s actual measured findings, and the real shipped header
      values/ROM measurements appear as content here, not as pointers.
- [x] No production code, no byte layouts beyond what this level's own scope (§2's header table
      and section boundaries) requires — the WRAM map and tile layout stay GDS-07's.
- [x] No new research claims originated — §6's dependency-manifest finding and §7's hardware-quirk
      risk are both `R306`/`R111`'s own conclusions, restated with attribution; §9's three Open
      Questions are routed to owners rather than answered here.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md`'s stage-03 row updated together.

**Merge decision.** `Claude.md` and `memory.md` both carry system-context-adjacent statements
today (the build/test commands, the boot-frame constant, the ROM-size invariant, the PyBoy
version). Those **stay authoritative in `Claude.md`/`memory.md` as the working developer
quick-reference** — they are what a coding agent reads before touching the tree, and relocating
them into a ladder level would make the quick-reference worse without making this level better.
GDS-02 does not supersede them; it is the level that explains *why* those constants are what they
are and records the constraints and gaps around them (§6, §7) that a quick-reference has no place
for. No text was moved out of either file by this level. The one genuinely new statement this
level adds to the tree — §7's explicit "never run on hardware" gap — belongs here and nowhere
else, since it is a property of the system's context rather than a fact a developer needs at
edit time.

**Gate:** closed 2026-07-26. Next unauthored level: GDS-04 (Domain Model).
