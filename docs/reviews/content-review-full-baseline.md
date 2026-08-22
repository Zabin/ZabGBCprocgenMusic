# Content Review — Full Baseline (First-Ever `09-content-review` Pass)

- **Owned by:** `09-content-review` · **Date:** 2026-08-14 · **Trigger:** `BL-0097`
- **Commit reviewed:** `9d58bf5429a1ba694b6d22a6c891aab6aa651fa3` (branch
  `claude/controls-explanation-28fpbh`) — ROM rebuilt fresh from this tree
  (`python3 build_rom.py Driftune.gbc` → 32768 bytes; SHA-256
  `81d689bdbf98dfde160337db0544a158ed77356b2d5cdee7a15541083563dacd`), full
  `python3 test_rom.py` suite run first: **154/154 PASS, 0 FAIL** (matches the Master Build Plan's
  recorded count exactly — no drift between what this review drove and what's on the ledger).

## Why this pass exists

Per `BL-0097`, `09-content-review` had never run once in this project's history despite
`docs/roadmap/09-release-exit-criteria.md` requiring a listening pass "for any release touching
musical character" — R5, R6, R8 all shipped without one. 15+ engine constants (tempo steps, scale
sets, density patterns, dissonance/stale/overload thresholds, `STYLE_TABLE` rows, `SONG_TABLE`
phase targets, motif variants, `VALENCE_TABLE`, blend duration) were chosen by reasoning alone and
never evaluated by ear or eye. This is that first pass.

## Scope

All `VERIFIED` packages per `docs/implementation/00-master-build-plan.md` at the time of this
review:

`IP-0001`-`IP-0007` (foundation) · `IP-9010` (channel-mix gating) · `IP-9020` (overload threshold
recalibration) · `IP-1060`/`IP-1061` (arpeggio+duty, vibrato+portamento) · `IP-1070` (combinable
generation schemes, Scheme E) · `IP-1080` (genre-aware style presets) · `IP-1090` (motif
recurrence via weighted variant selection) · `IP-1100` (song-form via autonomous phase cycling) ·
`IP-1110` (settings & control visibility indicators) · `IP-1130` (genre blending — reached
`VERIFIED` this session, per `VR-1130`'s re-verification pass at commit `f6fd243`, itself already
folded into the `9d58bf5` HEAD reviewed here).

**Explicitly out of scope, with reason** (per this skill's own instruction to state why rather
than silently skip):
- **`IP-1120`** (Emotional/Energy Layer) — `COMPLETE`, not yet `VERIFIED`, and its own package doc
  states zero audible/visible change: `AROUSAL`/`VALENCE` are derived WRAM bytes with no
  visualizer or input consumer yet (groundwork for roadmap R9). Confirmed by direct read of
  `visuals.py` and `input_map.py` — neither imports or reads `AROUSAL`/`VALENCE`. Nothing to
  review.
- **`IP-8010`/`IP-8020`/`IP-9030`** — `COMPLETE`, not `VERIFIED`, all refactoring/diagnostic
  packages with no player-visible content change (byte-identical ROM for the first two; `IP-9030`
  adds an internal `LY` diagnostic byte with no visualizer/audio surface).

## Evidence-gathering method

Rebuilt the ROM, ran the full suite (above), then drove `Driftune.gbc` headlessly via `pyboy`
(`pip install pyboy` — not preinstalled; `pip install Pillow` — needed for screenshots, also not
preinstalled) using throwaway driver scripts mirroring `test_rom.py`'s own idioms (`fresh_boot`,
`tap`, `settle_blend`). Per `run-driftune`'s own documented gotcha and this project's own
established finding (`test_rom.py`'s `t3_generation_live` docstring): **NR13/NR14 (pulse
frequency) are write-only on this hardware and on PyBoy's emulation of it — reading them back
returns fixed/uninformative values, not the true frequency.** All frequency/pitch-level evidence
below therefore uses the WRAM mirror (`CUR_DEGREE_*`, `NOTE_TIMER_*`) exactly as `test_rom.py`
does, not raw NR13/NR14 reads; NR11 (duty, upper 2 bits) and NR52 (channel-active bits) **are**
reliably readable and used directly. Screenshots (`pb.screen.image`) and WRAM-level tilemap reads
(`pb.memory[0x9800+n]`) were both used for the visualizer — tilemap reads are the more precise
signal for confirming which glyph is selected; screenshots confirm what a viewer would actually
see. All driver scripts and their full JSON outputs are in this session's scratchpad
(`/tmp/claude-0/.../scratchpad/review_driver*.py`, not part of this repo). Screenshots saved to
the same scratchpad's `shots/` subdirectory (not committed — paths cited below are this session's
local paths; regenerate with the cited driver scripts if the images themselves are needed later).

## Dimension 1 — Visual fidelity

Exercised: boot-state tile/palette render, the calm↔bad-zone palette swap, all 4 channel-activity
cells, all 5 settings-indicator bars at multiple fill levels, post-Select-reset state.

- **Tile/palette rendering confirmed correct at the byte level.** Direct tilemap reads
  (`pb.memory[0x9800+n]`) at several states: boot `settings_cells_tiles=[6,3,2,2,2]` (tempo=4→6,
  octave=1→3, scale=0→2, density=0→2, chmix=0→2 — `TILE_BAR_BASE(2)+value`, matches
  `visuals.py`'s `_emit_update_settings_row` formula exactly); after 7 Up-presses,
  `TEMPO_IDX` wraps to 3 (`4+7 mod 8`) and its cell reads tile `5` (`2+3`) — exact match; after 7
  B-presses, `DENSITY_IDX=7` (max) and its cell reads tile `9` (`2+7`, the max-fill glyph) — exact
  match. `CHANNEL_CELLS` (tiles 0/1 = off/on) tracked `NR52`'s live bits exactly in every sample
  taken (e.g. `NR52=0xf3` → `channel_cells=[1,1,0,0]`... consistent across all samples, see
  Dimension 3).
- **Calm vs. bad-zone palette swap confirmed both by code path and by screenshot.** Captured a
  genuine calm-state screenshot (`BAD_ZONE_FLAGS==0`, frame 56 of one fresh boot) showing the
  blue/teal `CALM_PALETTE` colors, and a bad-zone screenshot (`BAD_ZONE_FLAGS&0x08`, frame 0 of
  the same boot window) showing the red/orange `BAD_PALETTE` colors — visually and unambiguously
  distinct, not a subtle shift. `_emit_write_palette`'s `BCPS`/`BCPD` write sequence matches
  `visuals.py`'s documented palette tables exactly (`CALM_PALETTE = [rgb15(0,0,0), rgb15(0,8,16),
  rgb15(4,16,24), rgb15(10,28,20)]`, `BAD_PALETTE = [rgb15(0,0,0), rgb15(16,0,0), rgb15(24,4,4),
  rgb15(31,10,6)]`).
- **No washed-out or inverted art found.** `TILE_OFF`/`TILE_ON` (solid color-0/color-3 8x8 blocks)
  and the 8 bar-height glyphs (`_bar_tile_bytes`) render as designed in every screenshot taken —
  the bar fills grow from the bottom up as their source WRAM value increases, confirmed at fill
  levels 0 (boot default octave/scale), 3 (post-7-Up tempo), and 7 (post-7-B density).

## Dimension 2 — Readability & composition

- **Channel-activity vs. settings-indicator rows are visually distinct and both legible at a
  glance** — 4 cells (on/off binary) immediately followed by 5 bar-height cells (0-7 fill), same
  tilemap row, confirmed to update independently (channel-mix muting a channel cleared its
  `CHANNEL_CELLS` bit without disturbing any `SETTINGS_CELLS` value, and vice versa for every
  settings-control step tested).
- **Bad-zone state is visually distinguishable from calm at a glance** — see Dimension 1's
  screenshot pair; a red-dominant palette vs. a blue/teal one is a strong, non-subtle signal, well
  within R205's "2-3 restrained tones" guidance while still being unambiguous.
- **One real readability finding**, surfaced under Dimension 4 below and not repeated here: the
  calm palette is essentially never what a first-time player sees, because the default preset
  enters the bad-zone state almost immediately after boot in every trial run. See Finding F1.

## Dimension 3 — Musical correctness

Driven via the R224 question set below (full table). Headline register/WRAM-level findings that
support those answers:

- **Tempo** (`TEMPO_IDX`): one Up press cleanly steps `TEMPO_IDX` 4→5 (`TEMPO_BPM` 120→140), and
  the note-timer reload ceiling visibly shortens (max `NOTE_TIMER_PA` observed over 60 frames: 30
  → 26, consistent with `TEMPO_TABLE=[round(3600/bpm)...]`'s faster cadence) — a single, clear,
  audible-by-cadence step, not a jump or a no-op.
- **Register/octave** (`OCTAVE_IDX`): steps cleanly through all 4 values via Right/Left (confirmed
  via `SETTINGS_CELLS`); direct pitch confirmation is unavailable via PyBoy's write-only
  NR13/NR14 (see Method note above) — this dimension's audible-extremes question is therefore
  answered from code (`OCTAVE_ROOT_HZ`/`octave_delta` design, unchanged this pass) rather than a
  live register trace; flagged as a testing-capability gap, not a defect (see `R301` §3 precedent
  already cited by `IP-1110`'s own doc).
- **Mode/scale** (`SCALE_IDX`): cycling all 4 scales and sampling `CUR_DEGREE_PA` over 120 frames
  each shows visibly different degree sets reached per scale (e.g. dorian: `{2,3,4,5}` vs.
  pentatonic: `{1,2}` in the sampled window) — the walk is genuinely constrained differently per
  scale, not decorative.
- **Density** (`DENSITY_IDX`): **not monotonic as designed — see Finding F2.** Onset-event counts
  (rising edges of `NR52` bit3, the noise channel's active flag, over a fixed 600-frame window)
  across all 8 `DENSITY_IDX` values: `10, 14, 19, 38, 28, 35, 27, 13` against
  `DENSITY_K=[2,3,4,5,6,8,10,12]`. Indices 0-2 track `k` roughly linearly as designed
  (≈4.7 events per unit `k`, matching the Euclidean pattern's own arithmetic almost exactly), but
  index 3 (`k=5`) produces the *most* onsets of any setting (38, vs. an expected ≈23), and indices
  6-7 (`k=10,12`, nominally the two densest settings) produce noticeably *fewer* onset events (27,
  13) than several sparser settings — index 7 is the second-lowest of all 8. `DENSITY_IDX=6`
  showed 154 frames of `OVERLOAD` state in the same window (vs. 0 at every other index except a
  smaller 35 at index 5), a plausible partial cause (`IP-0007`'s autonomous overload response
  doubles note-timer reloads, throttling onset rate) — but does not explain index 7's low count
  (0 overload frames observed there). This directly touches R224's own density manipulation-check
  framing ("at the densest setting, can you still track the melody, or does it read as noise?") —
  the honest answer at `DENSITY_IDX=7` is that it does *not* read as busier than several lower
  settings, which is the opposite of the intended design.
- **Channel-mix/style** (`CHMIX_IDX`, `STYLE_TABLE`): a Start press was driven and sampled every
  frame through the blend. Preset 0→1 (Techno target `(6,6,2,1)`): `BLEND_STEP` reached 4 within 3
  frames, landing exactly on the target `(TEMPO_IDX,DENSITY_IDX,SCALE_IDX,DUTY_BIAS)=(6,6,2,1)` —
  `SCALE_IDX` jumped immediately (frame 0, per its documented hard-switch), the other 3 fields
  visibly interpolated across the 4 steps rather than snapping. Channel-mix muting: driving to
  preset 1 (`pulse A+B` only, mask `0b0011`) showed `NR52` still reporting the wave channel active
  for ~40 frames post-press (`0xf7`), then settling to the documented mask exactly (`0xf3` — pulse
  A+B only) by frame ~80 and remaining there through frame 360 — consistent with the documented
  "takes effect at the channel's own next onset, not instantly" gating contract, not a bug.
- **Bad-zone recovery**: see Dimension 4 and Finding F1/F3.
- **Motif variation** (`MOTIF_TABLE`/`N_VARIANTS`): confirmed reachable only via `CHMIX_IDX=6`
  (the only shipped preset with any Scheme-E bit set — a pre-existing, already-documented
  `VR-1070` Medium finding, re-confirmed here, not new). At preset 6, ran 40,000 frames and
  observed the weighted selector cycling variants `0→1→2→3→0` at cycle-boundary frames `1065,
  1577, 1833, 2009` — variety is genuinely reachable and does recur/cycle rather than getting
  stuck on one variant, consistent with `MOTIF_VARIANT_SELECTOR`'s "mostly retain, occasionally
  advance" design.
- **Song-form** (`SONG_TABLE`): ran 2200 frames from boot; observed the documented INTRO→BUILD
  transition at frame 1764 (`SONG_STATE` 0→1), landing `TEMPO_IDX`/`DENSITY_IDX` exactly on
  `SONG_TABLE[1]`'s row `(4,4)` — matches the table exactly, confirming the phase-transition
  mechanism fires and applies its target values correctly.
- **Sound design** (arpeggio/vibrato/duty, `IP-1060`/`IP-1061`): re-confirmed `test_rom.py`'s own
  `T11` result (400 frames, default tempo: all 4 arpeggio steps, all 4 vibrato phases, >1 duty
  value observed — passing in the 154/154 run) and independently re-drove at a **non-default**
  combination (`TEMPO_IDX=7`, max) over 600 frames: all 4 arpeggio steps, all 4 vibrato phases,
  and all 4 duty values (`0x0, 0x40, 0x80, 0xc0`) observed — the effect is live and audible-by-
  register-churn at both default and non-default tempo, not a fixed-tempo artifact.

## Dimension 4 — Bad-zone behavior

- **Entry and autonomous recovery both confirmed live**, not just state-machine transitions.
  A 4000-frame no-input run showed `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/`ONSET_WINDOW_COUNT`
  cycling in and out of the combined bad-zone state repeatedly and autonomously — dissonance score
  climbing into the 20s-30s, the combined flag setting, then clearing again without any input,
  over and over (observed transitions at, e.g., frames ~1466→1556 in, ~1736→ out). The longest
  unbroken bad-zone stretch observed in this run was **120 consecutive frames (~2 seconds)** —
  matching `IP-0007`'s documented "recovery acts within roughly one note duration per channel, not
  instantly" framing, not an indefinite stuck state.
- **Select-triggered manual recovery confirmed exact.** Drove the engine into a bad zone, then
  pressed Select: `BAD_ZONE_FLAGS` 9→0, `DISSONANCE_SCORE` 30→0 on the reset frame, and
  `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` all landed exactly on
  `PRESET_*` values (`4,1,0,0,0`) — the documented "known-good state," confirmed by direct
  WRAM read, not inferred.
- **Finding F1 (see table below): the shipped default preset enters the dissonant bad-zone state
  almost immediately at boot, reproducibly across every trial.** 5 independent fresh boots each
  showed `BAD_ZONE_FLAGS&0x08` already set at the very first sampled frame after the standard
  100-frame boot settle (frame 0 of the post-boot sampling window, every single trial). This means
  the blue/teal calm palette (Dimension 1) is not reliably what a first-time listener actually
  sees first — the red bad-zone palette is. Recovery does happen (per the point above), but the
  *entry* timing is surprisingly eager for a preset intended as "known-good."

R224's bad-zone-recovery rating question (never-recovers—over-corrects) is answered in the
question table below with this evidence as its basis.

## Dimension 5 — Documentation coherence

- **`memory.md`'s Visualizer quick reference (lines 80-93) matches shipped `visuals.py` exactly**
  — `CHANNEL_CELLS` at `0x9800`-`0x9803`, `SETTINGS_CELLS` at `0x9804`-`0x9808`, tile indices 2-9
  for the bar glyphs, calm/bad palette swap via `BCPS`/`BCPD` on `BAD_ZONE_FLAGS` bit3 — all
  confirmed against the actual `visuals.py` source and this review's own live captures. Clean.
- **`Claude.md`'s "Change the visualizer" and WRAM-map sections match shipped code** — spot-checked
  against `visuals.py`/`music_engine.py`'s actual tables and addresses; no drift found for the
  packages in this review's scope.
- **`docs/architecture/07-data-model.md` (GDS-07)'s WRAM table matches every address this review
  read directly** (`BLEND_STEP` at `0xC073`, `SONG_STATE` at `0xC03D`, `MOTIF_VARIANT_IDX` at
  `0xC03C`, etc.) — no stale rows found among those exercised.
- **No FS acceptance-criteria gaps found** among `FS-108`/`FS-109`/`FS-110`/`FS-111`/`FS-113`'s
  content-relevant criteria — each criterion this review could evidence (immediate style landing,
  motif-variant recurrence, phase-transition landing values, settings-bar tile mapping, blend
  interpolation) was independently reproduced above.
- This review did **not** re-audit every prose paragraph of every doc in scope (out of budget for
  a first pass across 16 packages) — the check above is a sampled, targeted cross-reference against
  what was actually driven, not an exhaustive documentation sweep. Flagged as a scope limitation,
  not a clean bill of health for documents this pass didn't open.

## R224 Question Set — Full Table

| Parameter | Manipulation-check question | Answer | Rating question | Answer |
|---|---|---|---|---|
| Tempo (`TEMPO_IDX`) | "After one press, did the tempo change land as a single clear step, or did it feel like nothing happened / like it jumped too far?" | Clear single step: `TEMPO_IDX` 4→5, `TEMPO_BPM` 120→140, note-timer ceiling shortened 30→26 frames — one press, one step, no overshoot. | sluggish—driving | Register evidence supports "driving" at the top end (max tempo, `TEMPO_IDX=7`) — cadence visibly tightens; no audio was directly heard (write-only PSG limitation, see Method), so this is a register-cadence judgment, not a verified acoustic one. |
| Register (`OCTAVE_IDX`) | "Does the octave shift stay musically usable at both extremes, or does it leave the mix (e.g. bass channel) sounding wrong at the top/bottom of its 4-step range?" | Not directly answerable from this pass's evidence — `OCTAVE_IDX` steps cleanly through all 4 values (confirmed via the settings-bar tilemap), but PyBoy's write-only NR13/NR14 means the actual resulting pitch was never read back; the wave channel's own `-1` `octave_delta` (floored at 0) was checked at the code level only, not driven live. | muddy—thin | **Not answered** — flagged as a genuine evidence gap (Finding F4), not guessed. |
| Mode (`SCALE_IDX`) | "Is each of the 4 scale choices clearly a different mood, or do two of them sound interchangeable?" | Each scale constrains the walk to visibly different degree sets over the same 120-frame window (e.g. dorian `{2,3,4,5}` vs. pentatonic `{1,2}`) — mechanically distinct, not interchangeable at the data level. | dark—bright | Ties to `VALENCE_TABLE=[10,6,12,4]` (major/minor/dorian/pentatonic) — dorian carries the highest valence value, pentatonic the lowest, in the shipped (untuned, `BL-0005`) table; whether that ordering matches an actual listener's dark/bright perception is unverified by ear this pass — the same write-only-register limitation applies. |
| Density (`DENSITY_IDX`) | "At the densest setting, can you still track the melody, or does it read as noise?" | **Answered negatively, and unexpectedly**: `DENSITY_IDX=7` (nominally densest) produced *fewer* measured onset events (13) than `DENSITY_IDX=1` (14) over an identical window — the densest setting does not read as busier than a sparse one. See Finding F2. | sparse—cluttered | Onset-event counts across all 8 steps: `10, 14, 19, 38, 28, 35, 27, 13` — the actual sparse↔cluttered progression is non-monotonic, peaking at index 3, not at the nominal maximum. |
| Channel-mix/style (`CHMIX_IDX`) | "Does the 4-step blend into the new style feel like a transition, or an abrupt cut?" | Transition, not a cut: preset 0→1 interpolated `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` visibly across 3 intermediate frames before landing exactly on the target row at `BLEND_STEP=4`; `SCALE_IDX` alone jumps immediately (by design). | abrupt—smooth | Register-level evidence supports "smooth" for the 3 blended fields; `SCALE_IDX`'s deliberate hard-switch is a one-field exception to that smoothness, by design (`FS-113`), not a defect. |
| Bad-zone recovery (Select / autonomous) | "When the music sounds like it's stuck or clashing, does it recognizably pull itself back toward something coherent, and does that take a noticeable-but-not-jarring amount of time?" | Yes — autonomous recovery cycles the engine in and out of the bad-zone state repeatedly and un-stuck within a bounded window (max 120 consecutive frames, ~2s, in this run); Select recovery is exact and immediate (`BAD_ZONE_FLAGS`/`DISSONANCE_SCORE` both hit 0 on the reset frame, preset values land exactly). | never-recovers—over-corrects | Lands closer to "recovers reliably" on this two-sided scale — no run showed an unrecovered stuck state. The *entry* side is the surprising finding (F1), not the recovery side — the engine recovers fine, but re-enters bad-zone very readily from the default preset. |
| Motif variation (`N_VARIANTS`, `MOTIF_TABLE`) — not in R224 §4, composed per its methodology | "Across several repeats of the same phrase, do the variants feel like variations on a theme, or like unrelated fragments / exact repetition?" | Variations on a theme, mechanically: all 4 variants share the same start/end degree (`0...7`) with differing middle contour (per `MOTIF_TABLE`'s own inline documentation), and the weighted selector was observed cycling through all 4 (0→1→2→3→0) over 40,000 frames at the one preset (`CHMIX_IDX=6`) that reaches Scheme E at all. | repetitive—incoherent | Register evidence favors "coherent, occasional variation" over either extreme — retention dominates (3-in-4 weight), switches are occasional, consistent with the intended design; **but reachability is a real, pre-existing (`VR-1070`) gap** — a listener who never presses Start 6 times never hears this mechanism at all. |
| Song-form phases (`SONG_TABLE`) — not in R224 §4, composed per its methodology | "Does the piece's overall arc (build/peak/etc.) feel like it goes somewhere, or does it feel flat regardless of phase?" | The mechanism demonstrably goes somewhere: the INTRO→BUILD transition at frame 1764 landed `TEMPO_IDX`/`DENSITY_IDX` exactly on `SONG_TABLE[1]`'s `(4,4)` row (tempo unchanged 120 BPM, density k=3→6, audibly-relevant per the earlier Density finding's own onset-count sensitivity) — a real, verified state change tied to elapsed time, not a no-op. | static—dynamic | Register evidence favors "dynamic" for the transition mechanism itself; whether the *magnitude* of each phase's tempo/density delta reads as a satisfying arc to an actual listener is unverified by ear (same write-only-audio limitation). |
| Sound design (arpeggio/vibrato/duty) — not in R224 §4, composed per its methodology | "Do the pulse channels sound like they're playing a chord/texture on top of the base note, or does the base note sound plain/unchanged?" | Arpeggio step index, vibrato phase, and duty-cycle bits were all confirmed cycling through their full value ranges live, at both default and maximally-fast tempo (`TEMPO_IDX=7`) — the mechanism is genuinely active on every frame sampled, not a static/frozen fallback. | plain—textured | Register churn strongly favors "textured" (constant per-frame state change across 3 independent mechanisms); actual audible chord-like perception is unverified by ear (same limitation). |

## Findings

| Finding | Artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| **F1** — Default preset enters the dissonant bad-zone almost immediately at boot, reproducibly | `music_engine.py` (`PRESET_*` values, `DISSONANCE_THRESHOLD=20`, `DISSONANCE_WEIGHT_BY_IC`, `LFSR_SEED_*`), bad-zone-recovery question in the R224 table above | 5/5 independent fresh boots showed `BAD_ZONE_FLAGS` combined bit already set at the first sampled post-boot-settle frame (`DISSONANCE_SCORE` in the high-20s/low-30s). The shipped "known-good preset" is, in practice, rarely what a first-time listener actually hears calm — the red bad-zone palette (Dimension 1) is what they see first almost every time, before autonomous recovery (which does work, per Dimension 4) pulls it back. This is plausibly a consequence of PyBoy's deterministic `DIV`-seeded LFSRs producing the same early trajectory on every headless boot (real hardware boot timing would vary the seed more) — worth confirming whether this reproduces on varied seeds/hardware before concluding the threshold itself is miscalibrated, but the headless-harness behavior every future verifier/reviewer will see is exactly this. | **Medium-High** — no crash/correctness defect, and autonomous recovery does work, but it directly undercuts the "calm default" design intent and is the single most listener-visible finding in this pass | `02-research-game-design` or `07-implementation-planning`/`08-code-implementation` to evaluate whether `DISSONANCE_THRESHOLD`/`LFSR_SEED_*`/`PRESET_*`'s starting interval relationships should be retuned so the default preset's first several seconds reliably stay calm (ties directly into the roadmap's proposed R12.5 Content & Musical Quality Pass, `BL-0097`) |
| **F2** — `DENSITY_IDX` does not monotonically increase onset rate; the nominal densest setting (7) produces fewer measured onset events than several sparser settings | `music_engine.py` (`DENSITY_K`, `_euclidean_pattern`, `OVERLOAD_THRESHOLD`/`ONSET_WINDOW_FRAMES`, `_emit_noise_gen`), density question in the R224 table above | Onset-event counts (NR52 bit3 rising edges, 600-frame window, all other state at boot default) across `DENSITY_IDX=0..7`: `10, 14, 19, 38, 28, 35, 27, 13`, against `DENSITY_K=[2,3,4,5,6,8,10,12]`. Indices 0-2 track `k` closely; index 3 overshoots (38 vs. an expected ≈23); indices 6-7 undershoot substantially (27 vs. ≈47, 13 vs. ≈56). Index 6 showed heavy `OVERLOAD` activity in the same window (154/600 frames) — a plausible partial cause via `IP-0007`'s autonomous note-timer-doubling throttle — but index 7 showed **zero** overload frames, so that alone doesn't explain its low count. A second plausible contributor this review did not fully isolate: `NR52`-bit-continuity undercounting when two onsets land close enough together that the channel's own envelope/DAC decay never drops it back to "inactive" between them (the edge-counting method would then merge two real onsets into one observed event) — more likely at high `k`, exactly where the undercount is largest. Root cause not conclusively isolated in this pass; both explanations point at the same symptom (musically, `DENSITY_IDX`'s higher settings do not reliably read as "busier"). | **Medium** — this is exactly the kind of routing-actionable finding this review exists to produce: it lands on a specific mechanism (the Euclidean-density table interacting with autonomous overload throttling and/or the noise channel's envelope timing), not a vague "sounds off" | `08-code-implementation`/`02-research-tooling-and-testing`: add register-write-level (not `NR52`-active-level) onset instrumentation to conclusively separate "throttled by `IP-0007`" from "undercounted by envelope overlap" before deciding whether `DENSITY_K`'s upper values, `OVERLOAD_THRESHOLD`, or the noise channel's envelope/length settings need retuning |
| **F3** — Bad-zone entry/recovery cycles quickly and repeatedly under the default preset (max 120 consecutive combined-bad-zone frames observed in a 4000-frame no-input run) | `music_engine.py` (`_emit_badzone_tick`, `DISSONANCE_THRESHOLD`), same evidence underlying F1 | Distinct from F1 (which is about the *first* entry) — this is about steady-state behavior: even after the initial recovery, the engine re-enters and re-exits the bad zone repeatedly during ordinary no-input play, at a period on the order of a few hundred frames. Not necessarily wrong (autonomous, self-correcting oscillation may be an acceptable or even desirable "living" quality) but was never characterized or decided on before now. | **Low-Medium** — informational; ties into F1's same retuning conversation rather than standing alone | `02-research-game-design`: decide (and document, e.g. in R204 or `ADS`) whether this oscillation frequency is an intended texture or an unintended consequence of `DISSONANCE_THRESHOLD`'s calibration, before any retuning pass changes it incidentally |
| **F4** — Register/octave and mode/scale audible correctness could not be independently confirmed by ear or by raw PSG register in this pass | `music_engine.py` (`OCTAVE_ROOT_HZ`, `SCALE_SEMITONES`), register and mode questions in the R224 table above | PyBoy's NR13/NR14 (pulse frequency) are write-only and unreadable, a pre-existing, already-documented limitation (`test_rom.py`'s own `t3_generation_live` docstring, `R108`/`VR-0001`). This review, like every prior verification pass, could only confirm octave/scale *mechanism* correctness (the right WRAM values land, the right degree sets are reached) via the WRAM mirror — not the actual resulting pitch or perceived mood. No register-level audio synthesis capture was attempted this pass (PyBoy's `sound_emulated=True` produces internal APU state but this review did not extract/analyze raw audio samples). | **Low** — a standing, disclosed testing-capability gap, not a new defect; named here because R224's own register/mode manipulation-check questions cannot be fully answered without it | `02-research-tooling-and-testing`: evaluate whether PyBoy's raw audio-sample extraction (if the emulator core exposes it) is worth adding to `run-driftune`'s toolkit for a future listening pass, so R224's octave/mode questions can eventually get a real acoustic answer rather than a WRAM-mirror proxy |
| **F5** — Motif variation (`N_VARIANTS`/`MOTIF_TABLE`) is reachable via only one shipped preset | `music_engine.py` (`CHMIX_MASKS`), motif question in the R224 table above | **Not a new finding** — re-confirmed here, already documented as a Medium finding in `VR-1070` ("pulse A/B Scheme E is code-complete but unreachable via any shipped preset"). Repeating it in this review's own table only because R224's motif question directly surfaces it again and the skill's own convention is to cite the specific question that surfaced each finding — no new severity assessment, no duplicate backlog entry needed. | **Medium** (unchanged from `VR-1070`'s original assessment) | Already routed in `VR-1070`; no new owner action from this pass — flagged here for traceability only |

## Screenshots / register captures taken

All under this session's scratchpad (`/tmp/claude-0/.../scratchpad/`, not part of the repo —
regenerate via the cited driver scripts if needed again):
- `shots/09_true_calm_palette.png` / `shots/10_true_bad_palette.png` — the calm/bad-zone palette
  pair (Dimension 1/4's primary visual evidence)
- `shots/01_boot_default.png`, `02_style_blend_settled.png`, `05_after_select_reset.png`,
  `06_settings_boot.png`, `07_settings_tempo_stepped.png`, `08_settings_density_stepped.png`
- `review_results.json` — the full structured capture from `review_driver.py` (boot state, tempo/
  octave/scale/density/style-blend/bad-zone/song-form/motif/sound-design traces)
- `review_driver2.py` through `review_driver12.py` — targeted follow-up drives (autonomous
  bad-zone cycling, preset-6 motif-variant cycling, tilemap-level settings-bar confirmation,
  channel-mix mute-timing confirmation, density onset-event counting, 5-trial boot-determinism
  check, non-default-tempo sound-design re-confirmation)

## Quality gate self-check

- [x] The ROM reviewed was rebuilt from the current tree (commit hash recorded above).
- [x] Every affected pattern/state named in scope was actually driven and screenshotted/register-
      captured — not judged from source alone (the two exceptions, F4's octave/mode pitch and
      F5's already-known reachability gap, are explicitly disclosed as evidence limits, not
      silently assumed clean).
- [x] All five dimensions exercised; each states what was actually checked, including the
      documentation-coherence dimension's explicit scope limitation (sampled, not exhaustive).
- [x] Every finding has a severity and a concrete recommended owner; none fixed in this pass.
- [x] Nothing but this report (and the `docs/reviews/INDEX.md`/`ROADMAP.md` tracker rows below)
      was written — no source, test, or package file touched.
