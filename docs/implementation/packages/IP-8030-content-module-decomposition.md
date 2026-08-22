# IP-8030 — Content Module Decomposition (`tiles.py`/`patterns.py`/`music_data.py`)

| Field | Content |
|---|---|
| **Package ID** | `IP-8030` · `IP-8xx0` refactoring series · **Executor: `08-refactoring`** · cites `BL-0089` |
| **Objective** | `08-content-authoring`'s declared write scope names three files — `tiles.py`, `patterns.py`, `music_data.py` — that have never existed in this tree; `GDS-09` §1 records this honestly ("this project has no `tiles.py`, no `patterns.py`, and no `music_data.py` at all"). Content data instead lives inline: tile pixel bytes in `visuals.py`, every scale/tempo/style/song/motif/rhythm table in `music_engine.py`. The user decided 2026-08-07 (`BL-0089`) to create the three modules — extract the data out, restoring the module decomposition `GDS-03`/`GDS-09` always described — over the two cheaper alternatives (repoint the skill's scope, or narrow/retire it). This is a pure structural relocation: every extracted value is copied exactly, not recomputed or corrected. It is the release plan's own named critical-path prerequisite "immediately before R12.5" (`01-release-plan.md` §2.5) — the retuning pass needs a real `08-content-authoring` write surface to retune through. |
| **Requirements Covered** | None. Purely structural — no `FR`/`NFR` is implemented, changed, or affected; every moved value is byte-for-byte identical to its current declaration. |
| **Architecture Components** | [`GDS-09` §1](../../architecture/09-interface-specification.md) — the finding this package executes on ("three of those five do not exist here"; becomes stale once this lands, follow-up correction owed to `03-architecture-design-synthesis`, not this package). [`GDS-03` §1](../../architecture/03-architecture.md) — the one-job-per-file/acyclic-import rule this package must preserve: the three new modules must stay dependency-free (no import of `music_engine.py`/`visuals.py`/`input_map.py`/`build_rom.py`), the same shape `wram_constants.py` (`IP-8020`) already established, so existing files can import them without creating a cycle. [`GDS-07`](../../architecture/07-data-model.md) — the WRAM/ROM layout these tables feed; unaffected in value or ROM position, only in which Python module declares the source constants. |
| **Interfaces** | Three new dependency-free modules at repo root, each exporting plain module-level constants (no wrapper function/registry — see the TWBS entry's explicit naming-convention decision: this project's own `wram_constants.py` precedent is flat constants, not the reference project's `build_tile_data()`/`ALL_PATTERNS`/`music_data()` shape `GDS-09` §1 found never adopted here). **`tiles.py`**: `_tile_off_bytes()`, `_tile_on_bytes()`, `_bar_tile_bytes(n)`, `CALM_PALETTE`, `BAD_PALETTE`. **`patterns.py`**: `_euclidean_pattern(k, n=NOISE_STEPS)`, `NOISE_STEPS`, `DENSITY_K`, `NOISE_STEP_TABLE`. **`music_data.py`**: `TEMPO_BPM`, `TEMPO_TABLE`, `OCTAVE_ROOT_HZ`, `SCALE_SEMITONES`, `SCALES`, `SEMITONE_TABLE_DATA`, `DISSONANCE_WEIGHT_BY_IC`, `DELTA_TABLE`, `VALENCE_TABLE`, `STYLE_TABLE`, `SONG_TABLE`, `N_SONG_PHASES`, `ARPEGGIO_OFFSETS`, `DUTY_BY_DEGREE`, `MOTIF_TABLE`, `N_VARIANTS`, `MOTIF_VARIANT_SELECTOR`, `CHMIX_MASKS`. `visuals.py` imports from `tiles.py`; `music_engine.py` imports from `patterns.py` and `music_data.py`; both existing files keep every function/constant they don't export moved. |
| **Files to Create/Modify** | **Create** `tiles.py`, `patterns.py`, `music_data.py` (repo root, alongside every other single-purpose module). **Modify `visuals.py`**: delete `_tile_off_bytes()`/`_tile_on_bytes()`/`_bar_tile_bytes(n)` (currently lines 64-80) and `CALM_PALETTE`/`BAD_PALETTE` (currently lines 87-88); add `from tiles import (_tile_off_bytes, _tile_on_bytes, _bar_tile_bytes, CALM_PALETTE, BAD_PALETTE)`. **Modify `music_engine.py`**: delete `TEMPO_BPM`/`TEMPO_TABLE` (~155-160), `OCTAVE_ROOT_HZ` (~163), `SCALE_SEMITONES`/`SCALES` (~166-174), `SEMITONE_TABLE_DATA` (~176-183), `DISSONANCE_WEIGHT_BY_IC` (~189), `DELTA_TABLE` (~198), `VALENCE_TABLE` (~99), `CHMIX_MASKS` (~260-268), `STYLE_TABLE` (~288-298), `SONG_TABLE`/`N_SONG_PHASES` (~308-320), `ARPEGGIO_OFFSETS` (~320-324), `DUTY_BY_DEGREE` (~325), `MOTIF_TABLE`/`N_VARIANTS` (~342-350), `MOTIF_VARIANT_SELECTOR` (~357), `DENSITY_K`/`NOISE_STEP_TABLE` (~362-366), `_euclidean_pattern()`/`NOISE_STEPS` (~369-378, `NOISE_STEPS` itself defined earlier alongside `CHANNELS`' block — re-locate exactly at implementation time); add `from music_data import (...)` and `from patterns import (_euclidean_pattern, NOISE_STEPS, DENSITY_K, NOISE_STEP_TABLE)`. Line numbers are this planning pass's own reading of the tree (2026-08-17) — **re-verify every one against the current tree before editing**, per this project's standing discipline on guessed line numbers. **Deliberately NOT moved** (stays in `music_engine.py`, named explicitly so it isn't mistaken for an oversight): `CHANNELS` (ties WRAM/register constants to behavioral parameters, keyed to `music_engine.py`'s own local address names — engine wiring, not tunable content, and moving it risks a real import cycle); `LFSR_POLY`/`LFSR_SEED_PA`/`LFSR_SEED_PB`/`LFSR_SEED_WV` (algorithmic seeds, not musical content); `DIV` (hardware register); `freq()`/`_note_table_bytes()`/`_wave_table_bytes()` (generation functions that consume the moved tables via import, stay as engine-side ROM-emission logic, not data). **Modify `test_rom.py`**: lines 94-97 (`from music_engine import STYLE_TABLE, DUTY_BIAS` / `from music_engine import MOTIF_TABLE, N_VARIANTS` / `from music_engine import SONG_TABLE, N_SONG_PHASES` / `from music_engine import VALENCE_TABLE`) — split each into its correct new source (`STYLE_TABLE`/`MOTIF_TABLE`/`N_VARIANTS`/`SONG_TABLE`/`N_SONG_PHASES`/`VALENCE_TABLE` all from `music_data`; `DUTY_BIAS` stays a `music_engine` import, it's a WRAM address, not a moved table). Line 277's function-local `from music_engine import DENSITY_K` becomes `from patterns import DENSITY_K`. **No other file touched** — `build_rom.py`/`input_map.py`/`gbc_lib.py` import only functions and register/WRAM constants from `music_engine.py`/`visuals.py`, never the moved data tables (confirmed by this planning pass's own supersession sweep, see the TWBS entry). |
| **Implementation Tasks** | (1) Capture the baseline (ROM SHA-256 + full check-name list) **before any edit**, per `08-refactoring`'s own Step 3 convention. (2) Re-verify every line-number reference above against the current tree (they may have shifted since this pass) — read each region before cutting it, don't trust this doc's numbers blindly. (3) Create `tiles.py`, move the 3 functions + 2 palettes, values copied exactly (not re-derived); update `visuals.py`'s import. (4) Create `patterns.py`, move `_euclidean_pattern`/`NOISE_STEPS`/`DENSITY_K`/`NOISE_STEP_TABLE`; update `music_engine.py`'s import. (5) Create `music_data.py`, move the remaining 17 named tables/constants; update `music_engine.py`'s import. (6) Update `test_rom.py`'s 5 import lines (4 module-level, 1 function-local) per Files to Create/Modify. (7) Grep the whole tree for every moved name's old qualified form (`from music_engine import <name>`, `music_engine.<name>`) to confirm no stray reference survives beyond what task 6 already fixed — the supersession sweep this planning pass already ran found only `test_rom.py`, but re-run it at implementation time against the real, possibly-shifted tree rather than trusting this doc's own sweep result unchanged. (8) Rebuild; diff the ROM hash against the task-1 baseline — **must be byte-identical** (pure Python-level constant/function relocation, zero ROM-data-layout consequence). (9) Run the full suite; identical check-name set to the baseline. |
| **Tests to Add** | None — same reasoning as `IP-8010`/`IP-8020`: the equivalence proof (byte-identical ROM, identical check-name set) is the verification. Do not add a test asserting the new modules' existence or that their values match the old locations — that tests the refactor's own mechanics, not shipped behavior, and would need updating every time an unrelated table is added anywhere. |
| **Documentation Updates** | None owed by this package directly. Recorded, not executed here (out of a refactoring package's own write scope — `03-architecture-design-synthesis` owns the GDS ladder): `GDS-09` §1's "three of those five do not exist here" paragraph becomes stale once this lands and needs a follow-up correction pass; `01-release-plan.md` §2.5's own prose ("When it lands it supersedes `GDS-09` §2's... note") should be checked against the corrected section number. `Claude.md`'s module-overview table may want the three new files named, at `08-refactoring`'s discretion — optional, not a Definition-of-Done item. |
| **Definition of Done** | `tiles.py`/`patterns.py`/`music_data.py` exist, each dependency-free (imports nothing from `music_engine.py`/`visuals.py`/`input_map.py`/`build_rom.py`/`gbc_lib.py`/`wram_constants.py`/`test_rom.py`). `visuals.py` no longer locally declares any of the 4 tile-content items named above; `music_engine.py` no longer locally declares any of the 21 moved names (17 in `music_data.py` + 4 in `patterns.py`). `test_rom.py`'s imports repointed, no `ImportError`. ROM is **byte-identical** to the pre-refactor baseline. Full suite passes with the identical check-name set. |
| **Verification Checklist** | ROM builds, exactly 32768 bytes, valid header (G5). Full `test_rom.py` suite passes (G5). **Equivalence contract: byte-identical ROM** (SHA-256 match) — the default and only acceptable outcome; a hash mismatch is a defect in this package's own execution (a typo'd value, a wrong emission order), not a predicted delta to justify. `09-package-verification` independently confirms: (a) the hash match from a clean rebuild; (b) `visuals.py`/`music_engine.py` genuinely no longer locally declare any of the moved names (grep-checkable against the exact lists in Interfaces); (c) all three new modules are genuinely dependency-free (no import of any other project module); (d) `test_rom.py`'s 5 repointed import lines resolve correctly and the suite's check-name set is unchanged from the baseline. |
| **Dependencies** | None — `visuals.py`/`music_engine.py`/`input_map.py`/`test_rom.py` are all stable, `VERIFIED`-package-derived files. Quiescence check (per this project's standing refactoring-scheduling discipline): confirm no other package is `IN PROGRESS` or `COMPLETE`-but-unverified touching `visuals.py`/`music_engine.py`/`test_rom.py` before starting. As of this authoring, `IP-9040` (the only package that recently touched `music_engine.py`) is `DEFERRED` without having built — no uncommitted or unverified work sits on these files. |
| **Risks** | **Scope discipline, not technical difficulty, is the real risk** — `visuals.py` has other plain-int constants (`LCDC`/`BCPS`/`BCPD`/`NR52`/`LY`/`TILEMAP_BASE`/`VRAM_TILE_DATA`/`TILE_OFF`/`TILE_ON`/`TILE_BAR_BASE`/`VIS_ENTRY_LY`/`SETTINGS_CELLS`/`SETTINGS_SOURCES`/`SETTINGS_PRESETS`/`CHANNEL_CELLS`) that are **not** tile *content* (they're hardware registers, tilemap addressing, or engine-wiring cross-references) and must not be swept into `tiles.py` "while we're in here" — same discipline `IP-8020`'s own Risks field established for its own scope. `music_engine.py` similarly keeps `CHANNELS`/`LFSR_*`/`DIV` deliberately, named above. **Import-cycle risk**: each new module must be verified genuinely dependency-free at execution time — a single stray `from music_engine import ...` inside `music_data.py` (e.g. to reuse a WRAM address in a comment-adjacent computation) would reintroduce exactly the cycle `GDS-03` §1 forbids. **`test_rom.py` is the one real non-`visuals.py`/`music_engine.py` file this package touches** — its 5 import lines are load-bearing for the full suite; get them wrong and every test using `STYLE_TABLE`/`MOTIF_TABLE`/`SONG_TABLE`/`VALENCE_TABLE`/`DENSITY_K` fails loudly at collection time, not silently — a safe failure mode, but worth flagging so it isn't mistaken for a real regression. **ROM budget**: zero impact — no data is added, removed, or resized, only relocated between Python source files; `gbc_lib.ROM`'s emitted bytes are unaffected by which module the Python-level value that feeds `rom.emit()` was declared in. |
| **Rollback Considerations** | Straightforward commit revert restores `visuals.py`/`music_engine.py`/`test_rom.py`'s local declarations and imports; the three new modules can be deleted with no other file left referencing them (confirm via grep before considering rollback complete — a partial revert that deletes a new module but leaves an import in `visuals.py`/`music_engine.py`/`test_rom.py` would break the build loudly, a safe failure mode). No requirement, address, or shipped behavior is affected by rollback either way — this package changes nothing observable. |

### Authorization (G3) — refactoring go-ahead

**Status: `GRANTED` 2026-08-17.** The user was asked directly, via `00-pipeline-manager`'s Step 4
gate check, whether `IP-8030` may build now — a plain yes/no, per this field's own prior wording
("needs an explicit user go-ahead before `08-refactoring` may build it"). **The user said yes.**
This is distinct from — and in addition to — the user's earlier 2026-08-07 design decision on
*what* `BL-0089` should become (that decided the shape of the fix; this authorizes spending a
build cycle on it now). Scheduling conditions for authoring this package (per
`00-pipeline-manager`'s own refactoring-scheduling rules) were already met at authoring time: the
`refactor`-type backlog entry was `SCHEDULED` with the user aware of it, no Critical/High bug was
open at the same entry stage, and the debt is stated as an observable cost (blocks R12.5's own
critical path). `08-refactoring` may now build this package, subject to its own eligibility
re-check immediately before running (quiescence, tree-green-as-found, no release bucket mid-close
overlapping `visuals.py`/`music_engine.py`/`test_rom.py`).

### Refactoring Summary (`08-refactoring`, 2026-08-17)

**Eligibility re-checked and cleared** immediately before the first edit: package `READY` + G3
`GRANTED` (above); pipeline quiescent (Master Build Plan swept, no `IN PROGRESS`/`COMPLETE`-but-
unverified package touching `visuals.py`/`music_engine.py`/`test_rom.py`); tree green as-found
(rebuilt clean, 32768 bytes, valid header, full suite 154/154 before any edit); no release bucket
mid-close overlapping these files.

**Baseline** (captured before the first edit): ROM SHA-256 `81d689bdbf98dfde160337db0544a158ed77356b2d5cdee7a15541083563dacd`,
32768 bytes. Full `test_rom.py`: **154 PASS, 0 FAIL**, all 154 check names recorded.

**Files Created**: `tiles.py`, `patterns.py`, `music_data.py` (repo root). **Files Modified**:
`visuals.py` (4 tile/palette items removed, import added), `music_engine.py` (21 moved names
removed, 2 import statements added, `NOISE_STEPS`/`DENSITY_K`/`_euclidean_pattern` region and
the preset-tables region replaced with pointer comments), `test_rom.py` (5 import lines
repointed: 4 module-level, 1 function-local), `Claude.md` (module-overview table + 9 "How to
Change Things" quick-reference entries repointed to the file each moved table/function now
actually lives in — Step 6 traceability, not merely the package's own optional module-overview
suggestion). **Files Deleted**: none.

**Two unstated tensions between this package's own Definition-of-Done and Interfaces fields,
resolved rather than blocked on** (both are pure-arithmetic/compile-time-constant substitutions,
independently verified to produce byte-identical values, so equivalence is unaffected):
1. The DoD requires all three new modules import nothing from `gbc_lib.py`, but the Interfaces
   field's `CALM_PALETTE`/`BAD_PALETTE` were originally built via `gbc_lib.rgb15(r,g,b)`. Resolved
   by keeping a private 2-line duplicate of that same pure bit-packing formula (`_rgb15`) inside
   `tiles.py` rather than importing `gbc_lib.py` or hardcoding the packed integers as unexplained
   magic numbers. Verified: `tiles._rgb15`-derived values match `gbc_lib.rgb15`'s own output
   exactly (both palettes, all 8 colors).
2. The DoD also bars importing `wram_constants.py`, but `STYLE_TABLE`/`SONG_TABLE`'s rows were
   originally built from `PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX`/`PRESET_SCALE_IDX` (imported from
   `wram_constants.py` in the pre-refactor tree). Resolved by substituting the literal values
   directly (`4`, `0`, `0` respectively — verified identical to `wram_constants.py`'s own current
   values) with an explanatory comment at each site, since these are compile-time Python
   constants, not runtime-varying state.

`patterns.py` imports `TEMPO_TABLE` from `music_data.py` (for `NOISE_STEP_TABLE`'s derivation) —
not barred by the DoD's enumerated list (`music_engine.py`/`visuals.py`/`input_map.py`/
`build_rom.py`/`gbc_lib.py`/`wram_constants.py`/`test_rom.py`) and does not reintroduce the
`GDS-03` §1 import cycle (`music_data.py` does not import from `patterns.py`).

**Equivalence Evidence**: post-refactor ROM SHA-256 **`81d689bdbf98dfde160337db0544a158ed77356b2d5cdee7a15541083563dacd`
— byte-identical to baseline**, 32768 bytes, valid header. Full suite: **154 PASS, 0 FAIL**,
check-name set diffed line-for-line against the baseline list — **identical**. Supersession sweep
(Task 7, re-run against the real tree rather than trusting the planning-pass sweep unchanged):
grepped the whole tree for every one of the 21 moved names' old qualified forms
(`music_engine.<name>`, `from music_engine import <name>`) and the 5 moved `visuals.py` items —
zero stray references found beyond the 5 `test_rom.py` import lines already repointed. All three
new modules independently confirmed dependency-free (`tiles.py`: zero imports; `patterns.py`:
imports only `music_data.py`; `music_data.py`: zero imports, per the resolution above).

**Migration Map**: no ID or filename was renamed — this is a pure relocation of existing plain
Python names into new files, same names, same values. `music_engine.py`'s `TEMPO_BPM`,
`TEMPO_TABLE`, `OCTAVE_ROOT_HZ`, `SCALE_SEMITONES`, `SCALES`, `SEMITONE_TABLE_DATA`,
`DISSONANCE_WEIGHT_BY_IC`, `DELTA_TABLE`, `VALENCE_TABLE`, `STYLE_TABLE`, `SONG_TABLE`,
`N_SONG_PHASES`, `ARPEGGIO_OFFSETS`, `DUTY_BY_DEGREE`, `MOTIF_TABLE`, `N_VARIANTS`,
`MOTIF_VARIANT_SELECTOR`, `CHMIX_MASKS` → now declared in `music_data.py`, importable from there.
`music_engine.py`'s `_euclidean_pattern`, `NOISE_STEPS`, `DENSITY_K`, `NOISE_STEP_TABLE` → now in
`patterns.py`. `visuals.py`'s `_tile_off_bytes`, `_tile_on_bytes`, `_bar_tile_bytes`,
`CALM_PALETTE`, `BAD_PALETTE` → now in `tiles.py`.

**Outstanding Issues (found, not fixed — filed for `00-intake`)**: (1) `GDS-09` §1's "three of
those five do not exist here" paragraph is now stale (this package created exactly those three
files) — the package's own Documentation Updates field named this as owed to
`03-architecture-design-synthesis`, out of this refactoring package's own write scope, not
touched here. (2) `01-release-plan.md` §2.5's own prose referencing "`GDS-09` §2's... note" should
be checked against the corrected section number once (1) lands — same field, same deferral.
Neither blocks R12.5 or any other work; both are pure doc-coherence follow-ups.

**Master Build Plan**: `IP-8030` set `COMPLETE` (never `VERIFIED` — that transition belongs
exclusively to `09-package-verification`).
