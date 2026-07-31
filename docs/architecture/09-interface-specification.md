# GDS-09 — Interface Specification

- **Level:** GDS-09 of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26
- **Upstream:** [GDS-03 Architecture](03-architecture.md) (module decomposition),
  [GDS-07 Data Model](07-data-model.md), [GDS-08 Presentation Architecture](08-presentation-architecture.md),
  research `R302` (assembler codegen patterns), `R306`
- **Downstream:** every future `FS-xxx`'s *Interfaces Used* field — see §0

## §0 The gap this closes

Every Feature Specification this project has authored — `FS-106`, `FS-107`, `FS-108`, `FS-109`,
`FS-110`, `FS-111` — carries the same line in its *Interfaces Used* field:

> *"GDS-09 (Interface Specification) remains `⛔ Planned`, same standing gap every prior FS has
> flagged — not blocking."*

Six specs, one repeated apology. Each was right that it wasn't blocking (the interfaces are small
and readable in source), and right to flag it rather than pretend otherwise. This level exists so
the seventh spec doesn't have to write that line.

**It is authored against the shipped modules, read directly** — and doing so turned up one
contract that the ladder, GDS-03, and the FS specs have all been describing as real which is in
fact **vestigial** (§3). That finding alone justifies the level.

## §1 What this project's module surface actually is

The ladder table lists the expected GDS-09 contracts as *"`build_engine_asm(rom) → patches dict`,
`build_tile_data()`, `ALL_PATTERNS`, `music_data()`, the `ROM` class surface."*

**Three of those five do not exist here.** `build_tile_data()`, `ALL_PATTERNS`, and `music_data()`
are the *reference project's* interfaces, inherited into the ladder template. This project has no
`tiles.py`, no `patterns.py`, and no `music_data.py` at all — `visuals.py` owns its tile bytes
inline (`_tile_off_bytes()`, `_tile_on_bytes()`, `_bar_tile_bytes(n)`), and `music_engine.py` owns
its own data tables as module-level Python constants. Recorded plainly rather than documenting
interfaces that aren't there.

The real surface is five modules and four functions:

| Module | Public surface | Consumed by |
|---|---|---|
| `gbc_lib.py` | `ROM` class; `rgb15(r,g,b)` | all others |
| `music_engine.py` | `build_engine_asm(rom)`; ~40 WRAM/register constants; data tables; `_emit_apply_style(rom)`; `_wave_table_bytes()` | `input_map.py`, `build_rom.py`, `test_rom.py` |
| `input_map.py` | `build_input_asm(rom)` | `build_rom.py` |
| `visuals.py` | `build_visuals_init_asm(rom)`; `build_visuals_update_asm(rom)` | `build_rom.py` |
| `build_rom.py` | `build(rom)`; CLI entry | `test_rom.py`, `ADR-0002`'s budget instrumentation |

## §2 The `ROM` class — the one interface everything depends on

`gbc_lib.py`'s `ROM` is the assembler. Its surface divides into four groups:

**State:** `data` (a 32768-byte `bytearray` — the entire address space, memory-mapped in place per
`R308`), `pos` (the write cursor — also the ROM-budget measurement point `ADR-0002` standardized
on), `labels`, `fixups`.

**Layout control:** `seek(addr)` moves the cursor; `emit(*bytes)` writes and advances;
`label(name)` records the current position under a name; `addr(name)` looks one up.

**Opcode emitters:** ~150 methods, each a 1:1 mapping from an SM83 mnemonic to its bytes
(`LD_A_n`, `JR_NZ`, `ADD_HL_BC`, …). `R302` confirms this is the intended codegen pattern; the
emitters are deliberately dumb, with no optimization, reordering, or peephole pass — what a module
emits is exactly what ships, which is what makes the ROM byte-for-byte deterministic (GDS-06 §4).

**Resolution:** `resolve()` runs the second pass, patching every forward reference recorded in
`fixups`. `set_header(...)` writes the cartridge header and checksums.

### §2.1 The three build-time errors this interface can raise

These are the contract's real teeth, and worth naming because two of them have actually fired
during this project's development:

| Error | Raised when | Consequence |
|---|---|---|
| `Dup label '<n>'` | `label()` is called twice with the same name | **Label collisions are a hard build failure, never silent** (§4) |
| `Undef '<lbl>'` | `resolve()` finds a reference to a label nobody defined | typo or missing routine caught at build time |
| `JR oor '<lbl>': <off>` | a relative jump's target is outside signed-8-bit range | **has fired in practice** — `IP-1090`'s additions grew the Scheme-E branch past the limit, forcing a `JR`→`JP` change |

The third is the interface's one genuine sharp edge: `JR` and `JP` are semantically
interchangeable to a caller but differ in reach, so *adding unrelated code to a routine can break
a jump elsewhere in it*. The error is loud and immediate, which is the right behavior, but it
means routine size is a real interface constraint rather than a style preference.

## §3 The patch-point contract is vestigial — a finding

GDS-03 names a "patch-point contract." The ladder table specifies `build_engine_asm(rom) →
patches dict`. Both `build_engine_asm` and `build_input_asm` are typed `-> dict` and both
construct a `patches` dict.

**Neither ever puts anything in it, and `build_rom.py` discards both return values.**

`build_engine_asm` creates `patches = {}`, never assigns a key, and returns it 160 lines later.
`build_input_asm` does the same. `build_rom.py` calls both as bare statements — no assignment, no
use. The dicts are constructed, returned, and dropped, every build.

**This is inherited scaffolding from the reference project, where patch points were a real
mechanism, carried across into this project's first package and never actually needed** — because
this project resolves everything through `gbc_lib`'s own label/fixup pass instead. There is no
defect: the code is correct, the ROM is correct, and nothing is broken. But three documents
describe a contract that carries no information, and every FS that cited "patch-point dict keys"
as an interface it consumes was citing something empty.

**This level's position:** the contract should be either removed or made real, and removal is
almost certainly right — the label/fixup mechanism already does the job. That is a
behavior-preserving code change (`08-refactoring` territory, `IP-8xx0`), not something a ladder
level does. Filed rather than fixed. Until then, **no document should describe the patches dict as
a live interface**, and this level does not.

## §4 The label namespace — a genuine shared interface

Every module emits labels into **one flat, global namespace**. `music_engine.py`'s `engine_tick`,
`input_map.py`'s `apply_input`, `visuals.py`'s `update_visuals`, and `build_rom.py`'s `main` all
live in the same dictionary, and `build_rom.py`'s main loop `CALL`s across module boundaries by
bare name.

**This is the real inter-module interface** — more so than any Python function signature. A module
does not expose routines to another module by returning them; it exposes them by *emitting a label
another module knows to call*. `build_rom.py` depends on exactly four such names existing:
`init_engine`, `read_joypad`, `apply_input`, `engine_tick`, `update_visuals` (five, counting
`init_visuals`).

**There is no prefixing convention**, and no naming scheme enforced anywhere. What exists instead
is `label()`'s duplicate check, which turns any collision into an immediate `Dup label` build
failure (§2.1). That is a genuinely adequate safety net — collisions cannot ship — but it is
detection, not prevention: two modules choosing the same name is caught at build time rather than
being impossible by construction.

**In practice the codebase has evolved an informal convention** — per-routine prefixes on local
labels (`uv_` in `update_visuals`, `ai_` in `apply_input`, `st_` in `song_tick`, `ie_` in
`init_engine`, plus per-channel suffixes like `_pa`/`_pb`/`_wv`). It is consistent, it works, and
it is documented nowhere. Recording it here makes it a convention rather than an accident.

## §5 The per-frame call-order contract

`build_rom.py`'s main loop is where the whole system's behavior is sequenced:

```
HALT                          ; wait for VBlank interrupt
(check + clear VBLANK_FLAG)
CALL read_joypad              ; sample buttons, compute edges
CALL apply_input              ; edges → parameter indices (+ style apply, + Select reset)
CALL engine_tick              ; generate: arp ticks → gen ticks → noise → bad-zone → song-form
CALL update_visuals           ; render nine cells + palette from current state
(loop)
```

**This ordering is a contract, not an implementation detail.** At least four documented behaviors
depend on this exact sequence:

1. **Input is applied before generation**, so a button press affects the same frame's notes rather
   than the next one — the responsiveness GDS-01 promises.
2. **Visuals run last**, so they render post-generation state, never a half-updated frame. GDS-08
   §3's stateless re-render assumes this position.
3. **Within `engine_tick`, bad-zone scoring runs after all channels generate** — which is exactly
   why channels read one-frame-stale flags (GDS-04 §5.2), the subtlety that produced a false test
   failure in `T16.7`.
4. **`song_tick` runs last inside `engine_tick`**, after `apply_input` has already run — which is
   why a song-form phase transition wins over a same-frame Start-press style application. GDS-04
   §1.2's last-write-wins contract **bottoms out precisely here**, and `VR-1100` confirmed it by
   forcing collisions at all three phase boundaries.

GDS-06 §2.2's frame-budget finding also bottoms out here: the Select-frame VRAM-write drop happens
because `apply_input`'s `init_engine` call inflates step 2, pushing step 4's writes past the safe
window. **The call order is where timing, correctness, and the write-collision contract all
meet** — which is why it deserves to be stated as an interface rather than left implicit in
`build_rom.py`.

## §6 Import direction — and the duplication it buys

Imports are strictly acyclic:

```
gbc_lib.py  ←──  music_engine.py  ←──  input_map.py
     ↑                  ↑                    ↑
     └──  visuals.py    └────────────────────┴──  build_rom.py
```

`gbc_lib` imports nothing project-specific. `music_engine` imports only `gbc_lib`. `input_map`
imports `gbc_lib` plus `music_engine` (the five index constants and `_emit_apply_style`).
`build_rom` imports everything.

**`visuals.py` deliberately does not import `music_engine`.** It declares the WRAM addresses it
reads as plain integers instead, with an inline comment recording the reason: avoiding a circular
import, keeping the visualizer a genuinely read-only consumer (GDS-03 §1).

**The cost is duplication, and it has grown.** When `IP-0006` shipped, `visuals.py` duplicated one
constant (`BAD_ZONE_FLAGS`). After `IP-1110` it duplicates **eleven**: five WRAM index addresses
and five `PRESET_*` values, plus the original. Every one is stated in two files with no mechanism
linking them.

Nothing has drifted — but nothing *prevents* drift either. If someone moves `TEMPO_IDX` in
`music_engine.py`, the build still succeeds and the tests still largely pass; the visualizer just
silently reads the wrong byte. The `PRESET_*` duplicates are worse: they are *values*, not
addresses, so a preset change would leave the boot-time indicator initialization showing stale
values with nothing failing.

**This level's position:** the acyclic-import rule is correct and worth keeping; the eleven-way
duplication is the price, and it is now high enough to be worth revisiting. Options exist (a
shared constants module both import, which breaks no cycle since it would depend on nothing) but
choosing one is a refactoring decision, not a ladder decision. Filed (§7 Q2).

## §7 Open Questions

1. **Should the vestigial patches-dict contract be removed?** §3 establishes it carries no
   information and is described as live in three documents. Removal is a small behavior-preserving
   change; the alternative (making it real) has no motivating need. Owner:
   `07-implementation-planning` for an `IP-8xx0` refactoring package, then `08-refactoring`. The
   documents describing it (GDS-03, the ladder table, six FS *Interfaces Used* fields) need
   updating either way.
2. **Should `visuals.py`'s eleven duplicated constants be de-duplicated?** §6. A shared
   constants module would preserve the acyclic rule and remove the drift risk. Owner:
   `07-implementation-planning`/`08-refactoring`. Not urgent — nothing has drifted — but the
   count grew 1→11 in one package, so the trend matters more than the current state.
3. **Should the informal label-prefix convention (§4) be written into the stage-08 skill's own
   rules?** It is consistent across every module today, entirely by convention, and the only
   enforcement is a collision error after the fact. Owner: the `08-code-implementation` skill's
   conventions, or `07-implementation-planning`'s package template.
4. **Does routine size need a stated ceiling given the `JR` range limit (§2.1)?** The failure mode
   is loud, so this is a friction question rather than a correctness one — but it has already cost
   one debugging cycle, and a routine growing past the limit fails at build time in a way whose
   message doesn't obviously point at "your routine got too big." Owner: `03`/`07`, low priority.

## Merge gate

- [x] The previous level's gate (GDS-08) was verified closed before this level started — its own
      prose records "Gate: closed 2026-07-26."
- [x] Authored against the shipped modules read directly — which is how §3's vestigial-contract
      finding and §6's 1→11 duplication growth were found rather than assumed.
- [x] The ladder table's three non-existent interfaces (`build_tile_data()`, `ALL_PATTERNS`,
      `music_data()`) are named as reference-project inheritances rather than documented as real.
- [x] No production code; no byte layouts (GDS-07 keeps those); no opcode listings.
- [x] No new research claims originated — `R302`/`R306`/`R308` cited for conclusions already
      reached; §7's four Open Questions routed to owners rather than answered.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md`'s stage-03 row updated together.

**Merge decision.** `Claude.md` stays authoritative as the working developer quick-reference — it
tells an implementer *how to add a routine or change a table*, which is edit-time procedure. This
level describes *what the module contracts are and what they guarantee*, which `Claude.md` has no
place for. Nothing moved.

Two documents now carry statements this level contradicts, and neither is this level's to edit:
**GDS-03**'s "patch-point contract" and the **six FS *Interfaces Used* fields** that cite a
patches dict and flag GDS-09 as absent. The FS fields become stale simply by this level existing
(the gap they flag is closed); the patch-point description becomes stale on the finding in §3.
Both are recorded as follow-ups rather than silently corrected — GDS-03 is this skill's own to
amend on a future pass, and the FS fields belong to `06-feature-specification`.

**Gate:** closed 2026-07-26. Next unauthored level: GDS-10 (Requirements Traceability Matrix
level) — the last one, and largely a pointer to `docs/requirements/`.
