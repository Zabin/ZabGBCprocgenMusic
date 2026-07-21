# Pipeline Journal

## Position

- **Updated:** 2026-07-21 (run #3)
- **Increment:** Foundation release bucket, first pass — from-scratch increment (no prior ROM).
- **Pipeline state:**
  - `01-vision`: ✅ MSTR-001 v1.0 + GDS-00 authored.
  - `02-research-*`: ✅ Restructured into a per-topic encyclopedia (`docs/research/encyclopedia/`)
    with real citations, per the user's direct request to ground open questions in outside
    research. R107-R110 (hardware), R201-R207 (procedural music/visualizer design), R301/R305
    (tooling) authored this run; R101-R106/R208/R302-304/R306 remain `⛔ Planned` (genuinely no gap
    yet — see `docs/research/INDEX.md` for why each is deferred). Surfaced one new finding
    (`BL-0008`: wave channel should get a distinct bass/timbre role, not pulse B's melodic
    treatment) and firmed up one placeholder (`BL-0005`'s dissonance weight table is now
    Helmholtz-roughness-grounded, though tempo/octave/scale/density values are still untuned).
  - `03-architecture-design-synthesis`: 🟡 GDS-00/01/03/07 authored (the levels needed to unblock
    requirements + a first implementation package); GDS-02/04/05/06/08/09/10 remain `⛔ Planned`
    (`BL-0001`).
  - `04-requirements-engineering`: ✅ FR-1000...FR-1120, NFR-1000...NFR-1030 authored (v1).
  - `05-feature-decomposition`: ✅ Feature Catalog v1 (FEAT-1000...FEAT-1050), single "Foundation" bucket.
  - `06-feature-specification`: ⛔ No FS-xxx authored yet (`BL-0006`) — `docs/features/INDEX.md`
    lists the planned FS-100...FS-105 slots.
  - `07-implementation-planning`: ✅ Master Build Plan + TWBS authored (IP-0001...IP-0006+).
  - `08-code-implementation`: ✅ IP-0001 `COMPLETE` — `gbc_lib.py` (reused verbatim),
    `music_engine.py`, `input_map.py`, `build_rom.py`, `test_rom.py` all written; G5 gate green
    (32768-byte ROM, valid header, 32/32 `test_rom.py` checks).
  - `09-package-verification`: 🔴 **Blocked on a fresh session** — attempted this run; the
    skill's own rules require explicit user acceptance of degraded (same-session) independence,
    and the user chose to wait for a fresh session instead (`BL-0004`).
  - `10-integration-review` / `11-release-readiness`: not reached — no release bucket has a
    verified package set yet.
- **Backlog:** 7 open entries (`BL-0001`, `BL-0004`...`BL-0008`; `BL-0002`/`BL-0003`/`BL-0009`
  are `DONE`, the latter two archived at the next triage sweep) — none `NEEDS-USER`; `BL-0004` is
  the one genuinely blocking the recorded next step, but its blocker (fresh session) is not
  something more pipeline work closes.
- **Next step:** `09-package-verification` on `IP-0001`, **in a genuinely fresh session** (the
  user explicitly declined to run it in this session with degraded independence) — this remains
  the pipeline's recorded next step and should be the first thing a future session's manager run
  attempts. (A future run may reasonably judge that authoring `FS-100`/`FS-101` (`BL-0006`) first
  is also legitimate, since it doesn't depend on `IP-0001`'s verification — but this run stops
  here rather than deciding that itself, since a gate stop ends the loop for this invocation.)
- **Open gates:** the fresh-session requirement for `09-package-verification` on `IP-0001`
  (user's explicit choice, run #2) is the standing blocker on that specific step; it is not a
  gate on the rest of the pipeline (feature specs, further research, etc. can still proceed in
  future runs without waiting on it). The next *package* (`IP-0002` onward) will each still need
  its own explicit G3 go-ahead before `08-code-implementation` builds it.

## Run log

| # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
|---|---|---|---|---|---|---|
| 1 | 2026-07-21 | run (compressed, single session) | `01-vision` → `02-research-gbc-hardware`/`02-research-game-design`/`02-research-tooling-and-testing` → `03-architecture-design-synthesis` (GDS-00/01/03/07) → `04-requirements-engineering` → `05-feature-decomposition` → `07-implementation-planning` → `08-code-implementation` (`IP-0001`) | Foundation release bucket, first pass | Vision, research (R100/R200/R300), architecture (GDS-00/01/03/07 — button mapping + bad-zone metric resolved), requirements (FR/NFR v1), feature catalog v1, master build plan, `IP-0001` built and self-tested (32/32). Pipeline skill hierarchy + toolchain (`gbc_lib.py`, test-harness pattern) harvested from the reference project (`zabin/rsgame`) and adapted in `.claude/skills/`. | `GATE: none — recorded here as a single compressed run through multiple stages rather than one-invocation-per-journal-row, since this is the project's first-ever session; subsequent runs should return to the normal one-step-per-journal-row discipline.` |
| 2 | 2026-07-21 | iterate | `09-package-verification` | `IP-0001` | Triaged backlog first (archived `BL-0002`/`BL-0003` to `backlog-archive.md` as `DONE`). Invoked `09-package-verification` on `IP-0001` per the recorded next step; the skill's own rules required explicit user acceptance of degraded (same-session) independence before proceeding — asked via `AskUserQuestion`. User chose **"wait for a fresh session"** rather than accept the caveat. No verification performed, no code/docs touched beyond this journal + the backlog (`BL-0004` disposition updated to `DEFERRED` with the user's answer as the revisit context). | `GATE: 09-package-verification on IP-0001 requires a genuinely fresh session — user declined to waive independence this run. Next invocation (any mode) should attempt this first, or, if judged more valuable, author FS-100/FS-101 (BL-0006) instead — but that choice is for the next run to make, not assumed here.` |
| 3 | 2026-07-21 | run (direct stage invocation, user-directed) | `02-research-game-design` (also covering `02-research-gbc-hardware`/`02-research-tooling-and-testing`'s own tiers, since the user's request spanned all three) | R107-R110, R201-R207 (except R208), R301, R305 | User asked directly to "satisfy as many questions as possible using research on... procgen music, music theory, and gbc." Ran real `WebSearch` research (Helmholtz/psychoacoustic dissonance sources, Toussaint's Euclidean-rhythm paper, GB chiptune/LSDJ channel-role convention, Eno/generative-music history, Pan Docs APU/joypad references, PyBoy's own API docs) and restructured the run #1 monolithic R100/R200/R300 files into the per-topic `docs/research/encyclopedia/` structure the adapted `02-research-*` skills actually expect (discovered as a doc-defect this run, `BL-0009`, fixed in place). Grounded GDS-03's dissonance-weight table in a real roughness ordering (`BL-0005` partially addressed) and surfaced one new finding (`BL-0008`: wave channel should get a distinct role from pulse B). Old files retained as superseded pointers, not deleted. | `Next: 09-package-verification on IP-0001 in a fresh session remains the standing gate (BL-0004, unchanged by this run's research-only work); alongside that, 06-feature-specification (BL-0006) can now also draw on R201-R207/R301/R305 for FS-100/FS-101/IP-0002's eventual FS.` |

**Note on this run's format:** the pipeline manager's own rules (`00-pipeline-manager/SKILL.md`)
require one journal row per internal step/skill invocation, never batched. Run #1 above is a
deliberate, one-time exception for this project's origin session — narrated as a single row
because the work was done directly (harvesting + authoring across stages in one continuous
session) rather than by invoking `00-pipeline-manager` in its normal iterate mode. **Every run
from here forward must follow the normal discipline**: one row per skill invocation, harvested
findings before the next step, gates stopped at and asked about. This note itself is the
tripwire — the next session's `00-pipeline-manager sync` should read it and resume normal
per-step journaling rather than treating run #1 as a precedent to repeat.
