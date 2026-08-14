# VR-8020 — Shared WRAM Constants Module

## Package

`IP-8020` — Shared WRAM Constants Module (`IP-8xx0` refactoring series, `BL-0065`, executed by
`08-refactoring`). Implementing commit: `ad1d2e2` ("IP-8020 COMPLETE — extracted visuals.py's
duplicated WRAM constants"), parent commit `c50f0f5` (`IP-8010`'s own implementing commit —
correct sequencing per this package's own Dependencies field). Fresh session — no prior work on
this package in this session; independence unimpaired.

## Result

**`VERIFIED`** — every Definition of Done item and Verification Checklist item holds under
independent re-derivation. The ROM is byte-identical across the implementing commit (independently
rebuilt both endpoints from git history), `test_rom.py` is byte-identical pre/post, and the new
`wram_constants.py` module is genuinely dependency-free with `visuals.py`'s 11 local
re-declarations fully removed. No findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| The 11 `BL-0065`-named constants have exactly one canonical Python-level definition | `wram_constants.py` (new, `ad1d2e2`) defines exactly `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`, `PRESET_TEMPO_IDX`/`PRESET_OCTAVE_IDX`/`PRESET_SCALE_IDX`/`PRESET_DENSITY_IDX`/`PRESET_CHMIX_IDX`, `BAD_ZONE_FLAGS` — 11 constants, no more, no fewer. Values independently diffed against the pre-refactor `visuals.py`'s own local declarations at `c50f0f5` — identical (a move, not a re-derivation). | Pass |
| Imported (not re-declared) by every file that uses them | `music_engine.py:18` imports all 11 from `wram_constants` (task 1's judgement call: the new module became the canonical source, `music_engine.py` imports back — the "genuine single source of truth" option the package recommended). `visuals.py:14` imports the same set. `input_map.py:12` switched from its prior `from music_engine import TEMPO_IDX, ...` to `from wram_constants import ...` — confirmed this follow-on edit (not explicitly required unless task 1 moved canonical ownership, which it did) was correctly made. | **Pass** |
| `visuals.py` no longer contains local re-declarations of any of the 11 | `grep` for `^TEMPO_IDX\|^OCTAVE_IDX\|^SCALE_IDX\|^DENSITY_IDX\|^CHMIX_IDX\|^PRESET_\|^BAD_ZONE_FLAGS` against post-refactor `visuals.py` (as a plain top-level assignment): zero matches — confirmed independently, not merely trusted from the Implementation Summary. Current-tip tree confirmed the same. | Pass |
| ROM byte-identical to the pre-refactor baseline | Independently reconstructed both `c50f0f5` (pre) and `ad1d2e2` (post, this package's implementing commit) into isolated directories and rebuilt each from scratch: both produce **`a646a651afb1fe755bc01b4c10c0b08c9b1f99ab36ae5f96c906353e20cf3e29`**, `cmp` confirms byte-for-byte identity — the identical hash `IP-8010`'s own `VR-8010` independently confirmed one commit earlier, exactly as expected since a pure Python-level constant relocation changes no ROM-emitted byte. | **Pass** |
| Full suite passes with the identical check-name set | `test_rom.py` byte-identical between `c50f0f5` and `ad1d2e2` (`diff`, zero output) — no tests added/removed/renamed. Current-tip suite: `154 PASS, 0 FAIL out of 154`. | Pass |
| `LY`/`VIS_ENTRY_LY` explicitly confirmed untouched and out of scope | Both still locally declared in post-refactor `visuals.py` (`LY = 0xFF44` at line 52, `VIS_ENTRY_LY = 0xC061` at line 61) — neither moved into `wram_constants.py`, matching the package's own explicit scope boundary. Current-tip tree confirmed the same (no drift since). | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Both independent rebuilds: 32768 bytes each; current-tip rebuild also 32768 bytes, valid header | Pass |
| Full `test_rom.py` suite passes (G5) | Current-tip: `154 PASS, 0 FAIL out of 154` | Pass |
| Equivalence contract: byte-identical ROM (SHA-256 match), independently confirmed from a clean rebuild | Done — see Definition of Done row above; both endpoints reconstructed from git history, not from the reported hash | **Pass** |
| `visuals.py` genuinely no longer locally declares any of the 11 constants (grep-checkable) | Confirmed by direct grep against the reconstructed post-refactor file and the current tip, both zero matches | **Pass** |
| The acyclic-import rule still holds — the new module imports nothing from either `music_engine.py` or `visuals.py` | Read `wram_constants.py` in full (both the reconstructed post-refactor version and the current tip): zero `import`/`from` statements of any kind — genuinely dependency-free, not merely undeclared-but-implicitly-coupled. Confirmed `music_engine.py` and `visuals.py` both import *from* `wram_constants`, never the reverse — no cycle. | **Pass** |

## Requirements audit

None — the package's own Requirements Covered field states "None. Purely structural." Confirmed
accurate: no `FR`/`NFR` cites `IP-8020` anywhere in `docs/requirements/01-functional-requirements.md`
(grepped, zero matches).

## Test run

- Independent rebuild of `c50f0f5` (pre-refactor, = `IP-8010`'s own implementing commit): `32768
  bytes`, SHA-256 `a646a651afb1fe755bc01b4c10c0b08c9b1f99ab36ae5f96c906353e20cf3e29`.
- Independent rebuild of `ad1d2e2` (post-refactor, this package's implementing commit): `32768
  bytes`, identical SHA-256. `cmp` confirms byte-for-byte identity.
- `test_rom.py` diff between the two commits: zero output (file unchanged).
- Current-tip: `python3 test_rom.py` → **`154 PASS, 0 FAIL out of 154`**; `python3 build_rom.py`
  → `32768 bytes`, valid header.

## Scope audit

`git show --stat ad1d2e2` confirms the diff touches `wram_constants.py` (new),
`music_engine.py`, `visuals.py`, `input_map.py`, plus the expected doc/ledger surface
(`docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`) — matching the package's
declared file set exactly. No scope creep found: `visuals.py`'s other plain-int constants
(`LCDC`/`BCPS`/`BCPD`/`NR52`/`LY`, `TILEMAP_BASE`/`VRAM_TILE_DATA`/`TILE_OFF`/`TILE_ON`/
`TILE_BAR_BASE`) confirmed still locally declared, untouched — the package's own named risk
("scope discipline is the real risk") did not materialize. `gbc_lib.py`, `build_rom.py`
untouched.

## Findings

None.

## Ledger updates

- Master Build Plan `IP-8020` row: `COMPLETE` → **`VERIFIED`**, this VR linked.
- `docs/implementation/packages/INDEX.md` `IP-8020` row: updated to `VERIFIED`.
- `docs/implementation/verification/INDEX.md`: new row added (✅ `VERIFIED`).
- No code, package, spec, or requirement text was edited by this run.
