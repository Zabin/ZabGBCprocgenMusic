# GDS-03 — Architecture

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored, 2026-07-21
- **Grounds:** GDS-04 (domain model), GDS-05/06 (FR/NFR), GDS-07 (data model), GDS-09 (interface spec)
- **Resolves MSTR-001 C4 and C5** — the input→parameter mapping and the bad-zone metric are
  decided concretely here, per that document's explicit delegation. Both are v1 proposals: stated
  precisely enough to build and test against, revisable by a future architecture delta if
  `09-content-review`/real listening finds them musically unsatisfying (a content/tuning finding,
  not necessarily a re-architecture).

## §1 Module layout (G1 write-scope)

One file, one job, same discipline as the reference project:

```
gbc_lib.py       — reused verbatim: SM83 assembler (ROM class), color math, header writing
music_engine.py  — generation state + logic for all 4 channels, bad-zone scoring, reset-to-preset
input_map.py     — joypad edge-detection + the mapping table below; writes engine parameters
visuals.py       — tile data + palette animation driven by engine state (GDS-08 owns the detail)
build_rom.py     — master build: imports all modules, lays out ROM sections, patches pointers
test_rom.py      — headless PyBoy verification harness (R300)
```

`music_engine.py` owns all PSG register writes; `input_map.py` never writes registers directly,
only the engine's own parameter fields, so there is exactly one writer per hardware surface (a
direct carry-over of the reference project's "each file has one job" rule, restated for this
project's own file set — this replaces that project's `asm_game.py`-centric G1 table, which
doesn't apply here since there is no single game-logic file playing that role).

## §2 Main loop structure

Same interrupt-driven shape as the reference project (VBlank ISR drives per-frame work; the main
loop otherwise idles/`HALT`s), restated for this project:

```
VBlank ISR (every ~59.7Hz):
  read_joypad_edges()          -> input_map.apply_edges(engine_state)
  music_engine.tick()          -> advance per-channel note timers; on expiry, generate next note,
                                   write PSG registers, update bad-zone score
  visuals.update()             -> read engine_state (NR52 + WRAM mirror), update tile/palette anim
main loop:
  HALT until next VBlank
```

`music_engine.tick()` is the one place doing the "cheap every-frame check, expensive only on
note-expiry" split R100 requires: a per-channel countdown decrements every tick; the actual
next-note computation (scale lookup, dissonance scoring) runs only when a countdown hits zero.

## §3 Input → parameter mapping (resolves MSTR-001 C4)

One control, one orthogonal parameter, no chords, no menu layer — directly following R200's
"each control owns exactly one knob" recommendation and GDS-01's flat interaction model. All
edge-triggered (a button/direction only acts on the frame it transitions from not-pressed to
pressed — holding it does not repeat the action), matching the reference project's own
edge-triggered menu-navigation convention (`memory.md`'s `JOY_CUR` bit map, reused bit layout).

| Input | Parameter | Effect |
|---|---|---|
| **D-pad Up** | Tempo | Step to the next-faster preset tempo (wraps at the fastest step) |
| **D-pad Down** | Tempo | Step to the next-slower preset tempo (wraps at the slowest step) |
| **D-pad Right** | Register/octave | Shift the melodic channels' octave range up one step (wraps at the top) |
| **D-pad Left** | Register/octave | Shift the melodic channels' octave range down one step (wraps at the bottom) |
| **A** | Scale/mode | Cycle to the next scale in a fixed list (wraps) |
| **B** | Density | Cycle to the next note-density preset (Euclidean `k` value at a fixed step count `n` — R200 §1.2) (wraps) |
| **Start** | Active-channel mix | Cycle to the next preset channel-activity mask (which of the 4 channels currently contribute) (wraps) |
| **Select** | Reset | Immediately reinitialize the generator to the known-good preset (§5) — not gated on the current bad-zone state |

**Why presets/steps rather than continuous ranges** for tempo/octave/density/channel-mix: each is
a small (4–8 entry) table the engine indexes into, matching MSTR-001 C9's testability requirement
(a test can assert "index incremented," a discrete, exact check) and R200's tempo open-question
(resolved here in favor of discrete steps, for the same testability reason — continuous/fine-
grained tempo is not ruled out forever, just not v1). Exact table contents (which BPM values,
which scales, which Euclidean k/n pairs, which channel-mix presets) are a `04-requirements-
engineering`/`06-feature-specification` data decision, not fixed at this architecture level —
this level fixes the *shape* (one wrapping index per parameter, one control per parameter), not
the *values*.

**Scale/mode candidate list** (content-authoring decision, not frozen here): major, natural minor,
dorian, and a pentatonic — a deliberately small v1 set (four), matching MSTR-001's "start simple,
extend later" posture; more modes are an easy, data-only backlog addition later since the
mapping's *shape* (A cycles through a list) doesn't change with list length.

## §4 Bad-zone detection metric (resolves MSTR-001 C5)

Combines the three R200-surveyed, SM83-tractable signals into one scalar, computed on the same
note-expiry cadence as generation itself (§2) — not every frame, keeping it inside the cycle
budget R100 names.

### 4a. Dissonance score (primary signal)

Only the three pitched channels (pulse A, pulse B, wave) participate — noise has no pitch. For
each of the (at most) 3 pairs of currently-sounding pitched channels, compute the interval between
their current scale-degree-mapped notes mod 12 semitones, and look up a fixed dissonance weight
table (consonant intervals — unison, major/minor 3rd, perfect 4th/5th, octave — score low;
dissonant ones — minor 2nd, tritone, major 7th — score high). Sum across all sounding pairs into
`DISSONANCE_SCORE` (a single byte is enough headroom: max 3 pairs × a weight table capped at
0–15 = 45, fits in a byte).

**Reconciled 2026-07-22 (`BL-0013`) against the shipped `IP-0004` implementation**: this level
originally proposed a literal 12-entry table (one weight per semitone interval, 0-11). The
shipped table (`music_engine.py:100`, `DISSONANCE_WEIGHT_BY_IC`) is instead a **7-entry
interval-class table** — intervals and their inversions folded together (e.g. a minor 2nd and a
major 7th, ic1, share one weight, per standard pitch-class-set-theory practice) — a deliberate
MVP simplification, not an oversight: it halves the table's ROM footprint and the per-pair lookup
cost, and R204 SS5's Helmholtz-roughness-cited ordering survives the fold unchanged (inversions
share the same consonance/dissonance character in the source literature). Both versions were
independently re-verified as producing musically-sound behavior (`VR-0004`). **The literal
12-entry table remains a valid v2 upgrade path** (e.g. if a future scheme wants to distinguish an
interval from its inversion, which the current 7-entry fold cannot) — not scheduled, no trigger
identified. `docs/requirements/01-functional-requirements.md`'s `FR-1080` text is unaffected
(it doesn't specify table size); `04-requirements-engineering` should still confirm no other FR
text implies the literal 12-entry version.

`BAD_DISSONANT = DISSONANCE_SCORE > DISSONANCE_THRESHOLD` (threshold a tunable content constant,
not fixed here — starting proposal: roughly 60% of the theoretical max, tuned by ear at
`08-content-authoring`/`09-content-review`).

### 4b. Repetition/staleness score (secondary signal)

Each pitched channel keeps a small circular buffer of its last 8 played scale degrees in WRAM. On
every new note, compare the buffer for a short repeating cycle (period 1 or 2 — i.e. "stuck on
one note" or "stuck oscillating between two notes"); increment a per-channel `STALE_COUNT` while
the cycle continues, reset it when the pattern breaks.

`BAD_STUCK = any channel's STALE_COUNT > STALE_THRESHOLD` (starting proposal: 8 consecutive
repeats of the same short cycle — long enough not to flag intentional short-term repetition that
sounds fine, short enough to catch a genuinely stuck generator within a few seconds at typical
tempos).

**Reconciled 2026-07-22 (`BL-0013`) against the shipped `IP-0004` implementation**: this level
proposed period-1-**or**-2 detection via an 8-entry ring buffer (`HIST_PA`/`PB`/`WV`, reserved at
GDS-07 §4/`0xC020`-`0xC037`, with write-head pointers at GDS-07 §3/`0xC013`-`0xC015`). The
shipped detection is **period-1 only** — comparing only the immediately-preceding scale degree
(`music_engine.py:260-271`) — and does not use the ring buffer or write-head fields at all; those
WRAM addresses remain reserved but genuinely unused in the shipped ROM (confirmed by grep,
`10-integration-review`'s Foundation-bucket report). This is a deliberate MVP simplification: a
period-2 "oscillating between two notes" pattern is real, subtler repetition, but period-1
"stuck on one note" already catches the more common, more audible degenerate case, and every
`STALE_COUNT_*` threshold/behavior was independently verified sound at the period-1 scope
(`VR-0004`, `VR-0005`). **The period-1-or-2 ring-buffer design remains a valid v2 upgrade path** —
the WRAM fields are already reserved and would need no data-model change to adopt, only new
comparison logic in `_emit_channel_gen`. Not scheduled; no trigger identified beyond "if
period-2 stuck states are observed often enough in practice to matter perceptually," which no
`VR-000x`/content review has reported. `FR-1090`'s text still names the `HIST_PA`/`PB`/`WV` ring
buffer explicitly — `04-requirements-engineering` should reword it to describe the shipped
period-1 comparison (or mark the ring buffer explicitly as the v2 path this paragraph names),
per this reconciliation.

### 4c. Channel-overload score (tertiary signal)

A rolling onset counter: count note-trigger events (any channel) within the last `W` ticks
(starting proposal: `W` = 32 ticks, roughly half a second at 60 Hz); `BAD_OVERLOAD =
onset_count_in_window > OVERLOAD_THRESHOLD` (starting proposal: more onsets than the densest
Euclidean preset (§3) would produce across all 4 channels simultaneously at the fastest tempo
preset — i.e. this should only trip from a generation-logic bug or an edge case the density/tempo
presets didn't anticipate, not from normal operation at any single preset combination; exact
number derived once §3's preset tables are authored, at `04-requirements-engineering`).

**Note 2026-07-22 (`BL-0017`, not part of the `BL-0013` reconciliation — a genuine calibration
miss, not a documented simplification)**: `VR-0007` computed the shipped preset tables' actual
onset-rate ceiling — `≈8.8` onsets/32-tick window even at the fastest tempo *and* densest preset
simultaneously — against the shipped `OVERLOAD_THRESHOLD=20`, more than double that ceiling.
`BAD_OVERLOAD` can therefore never fire under any reachable engine state, not even the
"generation-logic bug" edge case this section's own text anticipates (a bug would need to more
than double the theoretical maximum onset rate to ever trip it). This is exactly the
"derived once §3's preset tables are authored" step this section deferred to
`04-requirements-engineering` — evidence suggests that derivation either didn't happen or used a
different basis than the preset tables' actual values. A remediation package (`IP-9020`) is
already authored recalibrating the constant against this section's own stated intent; this note
records the architecture-level root cause `BL-0017`'s own finding didn't have space to fully
diagnose.

### 4d. Combined flag

```
BAD_ZONE = BAD_DISSONANT OR BAD_STUCK OR BAD_OVERLOAD
```

All four flags/scores (the three component signals plus the combined flag) are mirrored to WRAM
(GDS-07) — both for the visualizer (GDS-08 may represent "how close to bad" as well as the binary
flag) and for the test harness (MSTR-001 C9: a test must be able to assert entry into and recovery
from the bad zone, which requires reading these as WRAM state rather than re-deriving them from
raw register history).

## §5 Reset-to-preset behavior (Select)

A fixed "known-good" preset, the same state the engine also starts from on power-on (GDS-01):
a named-in-data scale (e.g. major), a mid-range tempo step, a mid-range octave, a low/sparse
density step, and a channel-mix preset using only the two pulse channels (the safest-sounding
combination — no wave/noise texture yet, nothing to be dissonant against). Reset clears
`DISSONANCE_SCORE`, all `STALE_COUNT`s, and the onset-window counter, and re-primes each channel's
next-note timer so playback resumes cleanly rather than picking up mid-note. This is a data
constant (GDS-07 gives it a WRAM/ROM home), not additional logic beyond "load these fixed values
into the same fields normal generation writes."

**Amended (`IP-0007`):** the project owner directed that Select be a *manual override*, not the
*only* way out of a bad zone — the engine must detect **and act on** a bad zone on its own. Two
changes follow from this:

1. **Autonomous avoidance/recovery, every frame, independent of Select.** Each pitched channel's
   note-generation routine (§1's `_emit_channel_gen`) checks `BAD_ZONE_FLAGS` before applying its
   normal LFSR-picked step: if `DISSONANT` (bit0), the step is overridden to pull the channel's
   scale degree toward the tonic (degree 0) — every channel gravitating toward the same pitch
   class directly lowers the pairwise interval-based dissonance score, clearing bit0 within a few
   note-onsets without any input. If `STUCK` (bit1) and the (possibly tonic-pulled) step is still
   zero, a step is forced anyway, so a repeated note can't persist even at the tonic. If
   `OVERLOAD` (bit2), every channel's (including noise's) next note-timer reload is doubled again
   on top of its normal value, spacing onsets out until the rolling window count naturally drops.
   This recovery is *reactive at the granularity of each channel's own note cadence* — it changes
   what happens next, not what's already sounding — so it takes effect within roughly one note
   duration per channel, not instantly.
2. **Select is now reset *and* randomize.** The tempo/octave/scale/density/channel-mix indices
   still reset to the fixed, deterministic known-good preset values (unchanged). Each channel's
   LFSR seed, previously a fixed constant, is now derived from the free-running `DIV` register
   (R213) XORed with a small fixed per-channel constant (to keep channels decorrelated from each
   other even if `DIV` is read at the same value) — so pressing Select gives a genuinely different
   melodic starting point each time, not the identical sequence every time, while still landing on
   the same safe parameters. A Galois LFSR must never be seeded to 0 (it would stay there
   forever); a zero result is forced to a fixed nonzero fallback. This same reseeding happens at
   power-on too (one code path for both), which incidentally also resolves the `DIV`-seeding idea
   named in `BL-0011`.

## §6 What this level deliberately does not decide

- The exact tempo/octave/density/channel-mix preset **values** (§3) and dissonance/stale/overload
  **thresholds** (§4) — data decisions for `04-requirements-engineering`/`06-feature-specification`
  and tunable-by-ear content decisions for `08-content-authoring`/`09-content-review`.
- The visualizer's concrete tile/palette design (GDS-08, not yet authored this pass).
- Bank-switching/ROM-size questions (deferred per MSTR-001 §4 non-goals, revisit only if actually
  needed).

**Gate:** closed 2026-07-21 for §1–§5 (module layout, main loop, input mapping, bad-zone metric,
reset behavior). GDS-02 (System Context), GDS-04 (Domain Model), GDS-05/06 (FR/NFR — superseded
here by a direct `04-requirements-engineering` pass since this is a from-scratch increment, not an
as-built one), GDS-07 (Data Model/WRAM map), GDS-08 (Presentation/visualizer), GDS-09 (Interface
spec), GDS-10 (RTM) remain `⛔ Planned` — see `docs/architecture/INDEX.md` and the pipeline
backlog for what's next.
