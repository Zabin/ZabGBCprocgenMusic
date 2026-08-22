# Content Review — Human Listening Pass (`R224` guided session)

- **Scope:** the first genuinely human-in-the-loop listening pass this project has run.
  `content-review-full-baseline.md` (2026-08-14) built the R224 question set but answered every
  question itself from register/WRAM instrumentation — an explicitly named limitation of that
  pass (its own F4/`BL-0105`). This pass closes that specific gap for the six parameters where a
  real ear, not a proxy, is the right instrument: raw APU audio was captured live from `pyboy`
  (not synthesized), sent to the user as WAV clips, and the user answered R224's own
  manipulation-check-plus-rating question for each one directly.
- **Commit reviewed:** `d959a06` (branch `claude/controls-explanation-28fpbh`) — post-`IP-8030`
  refactor. `IP-8030`'s own equivalence proof (byte-identical ROM, pre/post) means the audio
  content is unaffected by which commit the ROM was built from; the clips themselves were
  captured from the pre-`IP-8030` build, functionally identical.
- **Method:** `pb.sound.ndarray` (raw stereo APU samples, `int8`, 48kHz) accumulated per-tick
  across a scripted button sequence, DC-centered, peak-normalized, and written as 16-bit PCM WAV —
  see `capture.py` in this session's scratchpad (not committed; throwaway driver per this
  project's own convention, `run-driftune`'s "write throwaway driver scripts in the scratchpad"
  guidance). Six clips, one per parameter, each stepping or exercising that parameter's full
  range live.

## R224 Question Set — Human Answers

| Parameter | Clip | R224 question (combined manipulation-check + rating) | Answer |
|---|---|---|---|
| Tempo | `clip_tempo.wav` (9.5s, 7× Up) | Does each press land as a clear step, and does the escalation feel controllable (sluggish—driving)? | **Clear steps, driving** |
| Register/octave | `clip_octave.wav` (6.6s, 4× Right) | Does the octave shift stay musically usable across its full range (muddy—thin)? | **Useful across range** |
| Scale/mode | `clip_scale.wav` (6.6s, 4× A) | Is each of the 4 scale choices clearly a different mood (dark—bright), or do some read as interchangeable? | **Some sound similar** |
| Density | `clip_density.wav` (9.5s, 7× B) | At the densest setting, is the melody still trackable, or does it read as noise (sparse—cluttered)? | **Busiest, reads as noise** |
| Bad-zone recovery | `clip_badzone.wav` (18s, no input) | Does the engine recognizably pull back to something coherent in a reasonable time (never-recovers—over-corrects)? | **Recovers too slowly** |
| Channel-mix/style blend | `clip_style_blend.wav` (9.1s, 2× Start) | Does the transition into a new style read as a blend, or an abrupt cut (abrupt—smooth)? | **Feels like a real blend** |

Two of six parameters passed clean (tempo, register). Style blending passed clean, directly
corroborating `IP-1130`'s own design intent from a real ear rather than only WRAM-value
assertions. Three surfaced findings, detailed below.

## Findings

| Finding | Artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| **G1** — Scale/mode choices are not all perceptually distinct | `music_data.py` (`SCALE_SEMITONES`, moved from `music_engine.py` by `IP-8030`), scale question above | The user's own ear, on a clean 4-step cycle through every scale with no other variable changing, found at least two of the four scales read as similar rather than clearly distinct moods — the entire point of `SCALE_IDX` as a control. This is a genuine human-perceptual finding no register-level check could have produced (R224's own reason for existing): `T4.5`/`T6.x`'s own mechanism checks (`SCALE_IDX` changes, the right semitone set is read) all pass and say nothing about whether the four sets are *musically differentiated*. Not previously flagged by any prior review. | **Medium** — no mechanism defect, direct contradiction of the control's design intent (4 meaningfully different modes) | `02-research-game-design` — review `R201`/`R211`'s own scale-selection grounding against the actual shipped `SCALE_SEMITONES` sets and recommend either different intervals or accept fewer perceptually-distinct scale slots than 4 |
| **G2** — Densest setting reads as noise/clutter, not "busy but trackable" | `patterns.py` (`DENSITY_K`, `_euclidean_pattern`, moved from `music_engine.py` by `IP-8030`), density question above | Distinct from `BL-0103` (now `DONE` — that finding was a measurement artifact in onset-*counting*, not a perceptual claim; register-level instrumentation proved raw onset triggers *do* scale monotonically with `DENSITY_K`). This finding is the opposite kind of evidence: the counts are correct, but a real ear at the top of the range hears clutter, not "busier." Both can be true simultaneously — a correctly-scaling mechanism can still cross a musicality threshold at its upper end. | **Medium** — corroborates the *spirit* of the earlier density concern from an angle the counting fix couldn't address; a genuine "does it sound good" gap, not a mechanism defect | `02-research-game-design` — evaluate whether `DENSITY_K`'s top 1-2 values should be pulled in, or whether the noise-channel envelope/decay needs to leave more space between onsets at high `k`, feeding the same R12.5 pass `BL-0102` targets |
| **G3** — Autonomous bad-zone recovery reads as too slow | `music_engine.py` (`_emit_badzone_tick`, `DISSONANCE_THRESHOLD`), bad-zone question above | Corroborates and sharpens `BL-0104` (which characterized the oscillation but explicitly left open whether it's a defect or a desirable "living" quality, pending a decision). This is the first direct human judgment on that open question: a real listener, given an 18-second unprompted sample of the shipped default preset, judged the recovery timing as too slow, not as an intentional or pleasant texture. Not dispositive on its own (one listener, one sample), but it is real evidence the `BL-0104` decision was waiting on. | **Low-Medium** — same class as `BL-0104` itself; this finding narrows that open question rather than opening a new one | `02-research-game-design` — fold directly into `BL-0104`'s own decision, now with a first real data point favoring "unintended, should be tightened" over "acceptable living texture" |

## Related backlog

`BL-0117`-`BL-0119` file these three findings (see `docs/pipeline/backlog.md`). All three route to
the same `02-research-game-design` owner and the same R12.5 (Content & Musical Quality Pass)
destination as `BL-0102`/`BL-0104`, which this pass's G2/G3 directly reinforce with independent,
human-sourced evidence — not duplicates, but corroboration from a different evidence class than
either finding had before.

## Quality gate self-check

- [x] Real audio was captured from the emulator's own APU output, not synthesized or guessed.
- [x] Every question was answered by an actual human listening, not proxied by register/WRAM state.
- [x] Every finding cites the specific clip and question that surfaced it.
- [x] Findings checked against the existing backlog for duplicates before filing (`BL-0103`
      explicitly distinguished from G2; `BL-0104` explicitly linked, not duplicated, for G3).
- [x] Nothing fixed in-pass — this review only observes and reports.
