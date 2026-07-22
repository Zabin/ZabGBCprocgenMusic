# R306 — Toolchain Portability

- **Tier:** R300 · **Owned by:** `02-research-tooling-and-testing` · **Status:** ✅ Authored
  2026-07-22 (was "no portability need identified yet"; re-evaluated with concrete evidence from
  this session's own fresh-environment friction — see §4/§5)

## 1. Purpose
Re-confirm whether "no portability need" still holds, using real evidence from repeated
fresh-session `09-package-verification` runs (this project's actual portability test, run seven
times across `VR-0001`-`VR-0007`) rather than a theoretical judgment.

## 2. Scope
Build/test reproducibility across fresh environments — not cross-platform GUI/CI infrastructure,
which this project genuinely doesn't need (single build target, no CI pipeline, `Claude.md`).

## 3. Concepts
"Portability" for a project like this has a narrow, concrete meaning: can `python3 build_rom.py
<path>` and `python3 test_rom.py` be run successfully in a brand-new environment with nothing
but a Python interpreter and this repo checked out? The relevant risks are dependency
availability (is every import resolvable?) and path assumptions (does any script hardcode an
absolute path or assume a specific working directory?) — not the broader cross-OS/cross-CI
concerns "toolchain portability" evokes for larger projects. No external literature applies here;
this is evaluated against the project's own repeated real-world evidence (below), the same way
`R302` evaluated its own question against the shipped tree rather than external sourcing.

## 4. Operational Context
**Path handling is already portable**: `test_rom.py:30` uses `BASE = Path(__file__).resolve().parent`
(relative to the script's own location, not a hardcoded absolute path); `build_rom.py` takes its
output path as a command-line argument (`sys.argv[1]`), not a hardcoded destination. Grepped both
files plus `music_engine.py`/`gbc_lib.py`/`input_map.py`/`visuals.py` for `sys.platform`,
Windows-style path separators, or other OS-specific assumptions — none found.

**Dependency availability is not yet portable, and this session hit the gap directly**: `pyboy`
(and its own `pysdl2`/`numpy` dependencies) is required by `test_rom.py` but is **not
pre-installed** in a fresh environment — confirmed empirically this session (pipeline journal run
#7: `ModuleNotFoundError: No module named 'pyboy'` on the first `python3 test_rom.py` attempt of
a genuinely fresh session, requiring an unplanned `pip install pyboy` before verification could
proceed at all). No `requirements.txt`, `pyproject.toml`, or equivalent dependency manifest exists
anywhere in the repo (confirmed by directory listing) — the only place `pyboy` is even mentioned
as a dependency is inline in `R301`'s own grounding text and `memory.md`'s example code, neither
of which a fresh session would consult *before* attempting to run the test suite.

## 5. Implementation Guidance
**The "no portability need" judgment for path handling is reconfirmed** — no change needed there.
**The "no gap yet" judgment for dependency management does NOT fully hold anymore** — this
session's own experience is direct, repeated evidence (every independent-verification run in this
project's history has needed to discover, then install, `pyboy` fresh) that a minimal dependency
manifest would remove real, recurring friction from the one workflow (`09-package-verification`)
that structurally *requires* fresh environments. **Concrete recommendation**: add a
`requirements.txt` (or `pyproject.toml` `[project.dependencies]`) listing `pyboy` at the version
this project has verified against (`2.7.0`, per `R301`'s own citation) — a single-line, near-zero-
risk addition that every future fresh-session verification run would benefit from. This is a
doc/tooling improvement, not a code behavior change — appropriately scoped as a small
`08-refactoring`-adjacent or direct doc-tooling task, not something needing architecture-level
planning.

## 6. Feature Mapping
NFR (implicit — none of `NFR-1000`-`NFR-1030` currently state a fresh-environment-setup
requirement explicitly; this finding suggests one could be worth adding), the standing
independent-verification workflow (`09-package-verification`'s own rules) this friction repeatedly
affects.

## 7. Related Topics
R301 (PyBoy headless API — the dependency this topic's finding is about), R305 (emulator-based
test design — the workflow this friction affects every time it runs in a fresh session).
