# VR-8010 — Remove the Vestigial Patch-Point Dicts

## Package

`IP-8010` — Remove the Vestigial Patch-Point Dicts (`IP-8xx0` refactoring series, `BL-0064`,
executed by `08-refactoring`). Implementing commit: `c50f0f5` ("IP-8010 COMPLETE — removed the
vestigial patch-point dicts"), parent commit `fd498df`. Fresh session — no prior work on this
package in this session; independence unimpaired.

## Result

**`VERIFIED`** — every Definition of Done item and Verification Checklist item holds under
independent re-derivation. The ROM is byte-identical across the implementing commit (confirmed by
independently rebuilding both the pre- and post-refactor trees from git history, not by trusting
the reported hash), and the full `test_rom.py` suite passes with an identical check set (the test
file itself is byte-identical pre/post — no tests were touched, consistent with this package's
own "no test added" scope). No findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| `build_engine_asm`/`build_input_asm` no longer construct or return a `patches` dict | Independently checked out `c50f0f5` (`git show c50f0f5:music_engine.py`/`input_map.py`): `grep -n patches` on both files returns **zero matches**. Confirmed independently at the pre-refactor commit `fd498df` that both `patches = {}` and `return patches` were present (4 lines total, 2 per file) before removal. | Pass |
| Docstrings/signatures reflect the change | `music_engine.py`'s `build_engine_asm` docstring at `fd498df` reads "Returns a patch dict (unused for now, kept for parity with the reference project's `build_game_asm` return-shape convention)"; at `c50f0f5` that sentence is gone, confirmed by diff. `input_map.py` had no equivalent sentence at either commit — the package's own note that no symmetric edit was needed there is correct, independently confirmed rather than assumed. | Pass |
| ROM byte-identical to the pre-refactor baseline (SHA-256 match) | Independently reconstructed both trees from git history (`fd498df` = parent, `c50f0f5` = implementing commit) into isolated directories, rebuilt each with its own `build_rom.py`/`gbc_lib.py`/`music_engine.py`/`input_map.py`/`visuals.py`: both builds produce **`a646a651afb1fe755bc01b4c10c0b08c9b1f99ab36ae5f96c906353e20cf3e29`**, exactly matching the hash the Master Build Plan's `IP-8010` row cites, and `cmp` confirms the two 32768-byte files are byte-for-byte identical. | **Pass** |
| Full `test_rom.py` suite passes with the identical set of check names as the baseline | `test_rom.py` itself is byte-identical between `fd498df` and `c50f0f5` (`diff` — zero output) — no tests were added, removed, or renamed by this package, exactly as the package's own "no new observable behavior" claim requires. Current-tip suite (154/154, `T1`-`T21`) confirms nothing downstream regressed either. | Pass |
| No other file was touched | `git show --stat c50f0f5` (independently inspected): `music_engine.py`, `input_map.py`, plus the expected doc/ledger surface (`docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`) — no other source file appears. | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| ROM builds, exactly 32768 bytes, valid header (G5) | Both independent rebuilds produced exactly 32768 bytes; current-tip rebuild also confirmed 32768 bytes with a valid header | Pass |
| Full `test_rom.py` suite passes (G5) | Current-tip suite: `154 PASS, 0 FAIL out of 154` | Pass |
| Equivalence contract: byte-identical ROM (SHA-256 match), independently rebuilt from a clean checkout rather than trusting the reported hash | Done exactly this way — see Definition of Done row above. Not merely re-run against the Implementation Summary's claimed hash; both endpoints were independently reconstructed from git history and rebuilt from scratch. | **Pass** |

## Requirements audit

None — the package's own Requirements Covered field states "None. This package changes no
observable behavior." Confirmed accurate: no `FR`/`NFR` cites this package anywhere in
`docs/requirements/01-functional-requirements.md` (grepped, zero matches for `IP-8010`).

## Test run

- Independent rebuild of `fd498df` (pre-refactor): `32768 bytes`,
  SHA-256 `a646a651afb1fe755bc01b4c10c0b08c9b1f99ab36ae5f96c906353e20cf3e29`.
- Independent rebuild of `c50f0f5` (post-refactor, this package's implementing commit): `32768
  bytes`, identical SHA-256. `cmp` confirms byte-for-byte identity.
- `test_rom.py` diff between the two commits: zero output (file unchanged).
- Current-tip (`test_rom.py`, full tree): `python3 test_rom.py` → **`154 PASS, 0 FAIL out of
  154`**. `python3 build_rom.py` on the current tree → `32768 bytes`, valid header.

## Scope audit

`git show --stat c50f0f5` confirms the diff touches `music_engine.py`, `input_map.py`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md` — matching
the package's declared file set exactly (`Files to Create/Modify` names only these two source
files). No excursion found. `visuals.py`, `gbc_lib.py`, `build_rom.py`, `input_map.py`'s call
sites in `build_rom.py` all confirmed untouched.

## Findings

None.

## Ledger updates

- Master Build Plan `IP-8010` row: `COMPLETE` → **`VERIFIED`**, this VR linked.
- `docs/implementation/packages/INDEX.md` `IP-8010` row: updated to `VERIFIED`.
- `docs/implementation/verification/INDEX.md`: new row added (✅ `VERIFIED`).
- No code, package, spec, or requirement text was edited by this run.
