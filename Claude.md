# Driftune — Developer Guide

## Development pipeline (read this first for any non-trivial change)

This project is driven by a documentation-driven-development skill pipeline, harvested and
adapted from a separate reference project — see [`.claude/skills/README.md`](.claude/skills/README.md)
(stages, iteration loops, hard rules G1–G5) and
[`docs/pipeline/pipeline-journal.md`](docs/pipeline/pipeline-journal.md)/[`backlog.md`](docs/pipeline/backlog.md)
for where things stand. The default entry point is the `00-pipeline-manager` skill ("run the
pipeline skill"); new features/bugs enter via `00-intake`, never by side-channel edits.

## Architecture Overview

Each file has ONE job. Edit only what you need.

```
gbc_lib.py       — ROM class (assembler opcodes) + color math + header writing (reused verbatim
                    from the reference project — nothing game/music-specific lives here)
wram_constants.py — shared WRAM constants (5 param indices, 5 PRESET_* values, BAD_ZONE_FLAGS),
                    dependency-free by design (IP-8020, BL-0065) so music_engine.py and
                    visuals.py can both import it without an import cycle
tiles.py         — visualizer tile pixel art + BG palette data (IP-8030, BL-0089), dependency-free
patterns.py      — Euclidean rhythm-pattern generation + density/step-timing data (IP-8030,
                    BL-0089), imports only music_data.py's TEMPO_TABLE
music_data.py    — curated scale/tempo/style/song/motif/valence tables (IP-8030, BL-0089),
                    dependency-free
music_engine.py  — all sound-channel generation logic (4 channels), bad-zone detection,
                    PSG register writes (preset/table data now lives in music_data.py/patterns.py)
input_map.py     — joypad edge detection + the input->parameter mapping (never writes PSG regs)
visuals.py       — tile/palette visualizer, read-only consumer of engine state (never writes
                    engine state or PSG registers); tile/palette data now lives in tiles.py
build_rom.py     — master build: imports all modules, lays out ROM sections, patches pointers
test_rom.py      — headless PyBoy verification harness (drives button sequences, asserts on
                    sound registers + WRAM engine state) — 191 checks across T1-T23
```

### Data layout, WRAM map

Authoritative source: [`docs/architecture/07-data-model.md`](docs/architecture/07-data-model.md)
(GDS-07). Quick orientation: parameter indices at `0xC000`-`0xC004` (tempo/octave/scale/density/
channel-mix — channel-mix now gates each channel's own generation routine, `IP-9010`/`BL-0019`),
bad-zone state at
`0xC005`-`0xC00B` (dissonance score, per-channel stale counts, onset-window counter/timer),
per-channel generation state (note timers, scale degrees, LFSR states) at `0xC00C`+, joypad state
at `0xC050`-`0xC052`, noise step index at `0xC019`, **arpeggio state (`IP-1060`) at `0xC01D`-
`0xC01F`** (`ARP_STATE_PA`/`PB` — packed countdown+step byte — and a shared scratch byte),
`VBLANK_FLAG` at `0xC060`, and **`VIS_ENTRY_LY` at `0xC061` (`IP-9030`, `BL-0069`)** — the `LY`
register's value recorded at entry to `update_visuals`, a permanent diagnostic asserting the
per-frame VBlank budget stays within `144`-`153` (`T19`; see the Known Good Behavior note below).
**`AROUSAL`/`VALENCE` at `0xC068`-`0xC069` (`IP-1120`, roadmap R7)** — derived mood bytes
(`TEMPO_IDX+DENSITY_IDX`, `VALENCE_TABLE[SCALE_IDX]`), recomputed only at the 6 write sites that
can change their inputs, never per-frame; no visualizer/input consumer yet (groundwork for
roadmap R9, separately blocked); see `T20`.
**`BLEND_SRC_TEMPO`/`DENSITY`/`DUTY`/`BLEND_STEP` at `0xC070`-`0xC073` (`IP-1130`, roadmap R8)** —
genre-blending state: `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` now glide toward a newly-selected
`STYLE_TABLE` row over `BLEND_STEP`'s 0-4 progress instead of landing instantly; `SCALE_IDX` still
hard-switches the same frame as the Start press. See `T21` and the Known Good Behavior note below.
**`ARP_CACHE_PA`/`ARP_CACHE_PB` at `0xC07A`-`0xC089` (`IP-1150`, `BL-0127`)** — 4
(freq_lo, freq_hi) pairs per pulse channel, the whole of the note's arpeggio figure resolved at
that channel's own onset and merely played back by `arp_tick`. `0xC08A`-`0xC08C`
(`ARP_ROW_SCRATCH`/`ARP_BASE_LO`/`ARP_BASE_HI`) are working storage used only *within* one
`arp_resolve` call. This is what returned a scanline of VBlank head-room (see below).
**`CHORD_IDX`/`CHORD_ONSET_CTR`/`CHORD_TOGGLE` at `0xC077`-`0xC079` (`IP-1140`, `BL-0119`)** —
the **shared harmonic context**: which chord is sounding, how many pulse-A onsets until it
advances, and packed bass-alternation / strong-weak-parity / published-melody-slot bits. One
writer, three readers, all reads at onsets. This is what makes the three pitched channels play the
same music; see the Known Good Behavior entry below.
**No SRAM** — this project makes no save/battery commitment (MSTR-001 C2).

### Input mapping (GDS-03 SS3)

| Input | Parameter |
|---|---|
| D-pad Up/Down | Tempo step +/- |
| D-pad Right/Left | Octave step +/- |
| A | Next scale/mode |
| B | Next density preset (noise-channel Euclidean pattern) |
| Start | Next channel-mix preset (`CHMIX_MASKS`-gated — only the preset's included channels sound, `IP-9010`) |
| Select | **Reroll** — reseed every channel's melodic LFSR from `DIV` (genuinely new material) and clear all bad-zone state, **leaving every one of the listener's own settings untouched** (`IP-1160`/`ADR-0006`/amended `FR-1070`, 2026-08-21). Unconditional manual override — not the only recovery path, see below. **This control's meaning changed**: it used to also reset `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`/`DUTY_BIAS` to the boot preset, which discarded everything the listener had dialled in. There is deliberately no longer any single "return everything to default" control — every value is reachable in at most 7 presses of its own control (`ADR-0006`, an accepted cost) |

All edge-triggered (rising edge only — holding does not repeat).

### Autonomous bad-zone avoidance/recovery (IP-0007)

The engine detects **and acts on** a bad zone every frame, without requiring Select (MSTR-001 C5
amended v1.1). Select remains available as a manual **reroll** override — new melodic material
plus a cleared bad-zone slate, with the listener's settings preserved (`IP-1160`) — but it has not
been the only way out since `IP-0007` (2026-07), and that is exactly why it no longer needs to
reset anything the listener chose:

- **Dissonant** → each pitched channel's next scale-degree step is overridden to pull toward the
  tonic (degree 0) instead of the normal LFSR-picked delta, converging the channels toward the
  same pitch class until the interval-based dissonance score drops back under threshold.
- **Stuck** → if the (possibly tonic-pulled) step would still be zero, a step is forced anyway, so
  a repeated note can't persist even at the tonic.
- **Overloaded** → every channel's next note-timer reload is doubled again, spacing onsets out
  until the rolling onset-window count naturally drops.

Recovery acts at the granularity of each channel's own note cadence (it changes what plays next,
not what's already sounding), so it takes effect within roughly one note duration per channel, not
instantly — see `docs/architecture/03-architecture.md` §5's amendment for the full rationale.

### Channel-mix gating (`IP-9010`, `BL-0019`)

`CHMIX_IDX` (stepped by Start) indexes an 8-entry `CHMIX_MASKS` table (one 4-bit mask per preset,
bit0=pulse A/bit1=pulse B/bit2=wave/bit3=noise, matching `NR52`'s own channel-bit order). Each
channel's generation routine checks its own bit before writing its onset/hit registers: included
→ normal write (plus restoring the channel's DAC/envelope in case it was previously silenced);
excluded → the channel's DAC is explicitly turned off (`NR12`/`NR22`/`NR30`/`NR42` written `0x00`),
which hardware-clears the channel's `NR52` bit immediately rather than merely skipping the next
trigger. Note-timer/degree/stale/onset-window bookkeeping still runs every frame regardless of
inclusion, so an excluded channel's internal walk stays live and it resumes cleanly the instant
its mask bit is re-enabled. Preset 0 (`PRESET_CHMIX_IDX`) is always "all 4 active." Dissonance
scoring deliberately still reads all 3 pitched channels' semitones regardless of exclusion — an
explicit, documented design decision (see `_emit_badzone_tick`'s own docstring), not an oversight.

### Sound design techniques (`IP-1060`/`IP-1061`, R216)

Pulse A/B (not wave — it keeps its plain sustained bass role) get four layered timbral effects,
all always-on, no new input control:

- **Arpeggio** → every few frames (`ARP_SUBTICK_RELOAD`), the channel's frequency register is
  rewritten (no retrigger — envelope keeps decaying naturally) to cycle through four cached
  pitches. **Rewritten by `IP-1150` (2026-08-21) — see the Known Good Behavior entry; the old
  description said "`ARPEGGIO_OFFSETS`, a period-4 pattern of scale-degree deltas from the
  currently-held root note, implying a chord on a single channel," and every part of that is
  now wrong.** The pitches are tones of the **currently-sounding shared chord** (`CHORD_TABLE`),
  the figure is **drawn per onset** from `ARP_PATTERNS`, and a note whose pitch is not a chord
  tone (notably the melody's weak-onset passing tone) **does not arpeggiate at all**. The
  per-frame routine no longer computes anything — `arp_resolve`, called from each channel's own
  onset branch, resolves the whole figure into `ARP_CACHE_PA`/`PB` and `arp_tick` just indexes it.
  **Sustaining never means skipping the frame's frequency write** — see the portamento bullet
  below for why that would silently delete two other shipped effects.
- **Duty cycle** → `NR11`/`NR21`'s duty bits vary per onset (`DUTY_BY_DEGREE`, indexed by
  `CUR_DEGREE mod 4`) instead of staying fixed at 50%.
- **Vibrato** → every frame, a tiny +-1 low-byte wobble is added to the held frequency
  (`ARP_STATE_PA`/`PB` bits6-7, a 4-phase cycle: +1, none, -1, none) — a deliberate scope
  reduction from a true frequency-domain LFO (the SM83 opcode set this project uses has no
  ADC/SBC for safe multi-byte carry-chain arithmetic), kept to the smallest safe unit with
  exact carry/borrow handling via `JP_C`/`JP_NC`.
- **Portamento** → on a degree-changing onset, the trigger write uses the *old* degree's
  frequency (retriggering envelope/duty at the outgoing pitch) rather than the new one;
  `arp_tick`, which runs every frame and — critically — runs *before* `gen_tick` in
  `engine_tick`'s call order, carries the pitch the rest of the way to the new target over the
  following frame(s). This 2-call reordering is what actually produces the glide — see
  `engine_tick`'s own comment before changing that order.

## How to Change Things

### Tune a preset table or threshold
Edit the relevant table: `TEMPO_BPM`, `OCTAVE_ROOT_HZ`, `SCALE_SEMITONES`, `DELTA_TABLE`,
`DISSONANCE_WEIGHT_BY_IC` in `music_data.py`; `DENSITY_K` in `patterns.py`; the `*_THRESHOLD`
constants and the `PRESET_*` constants stay in `music_engine.py`/`wram_constants.py` respectively
(IP-8030, BL-0089) — no other file needs to change; `build_rom.py` regenerates everything from
these tables at build time. **These are still first-guess placeholders** (`BL-0005`), not tuned
by ear.

### Add a new scale/mode
Add an entry to `SCALE_SEMITONES` and `SCALES` in `music_data.py` (exactly 8 semitone-offset
entries, extending into the next octave past each scale's own unique pitch count) —
`SCALE_IDX`'s wrap mask (`0x03` today, 4 scales) must be widened if the list grows past a
power-of-two boundary; check `input_map.py`'s `_step_on_bit` call for `SCALE_IDX`.

### Add a new pitched channel's generation
See `music_engine.py`'s `_emit_channel_gen` (parameterized: countdown → LFSR delta → table lookup
→ register write → timer reload → stale/onset-window bookkeeping) — add an entry to the
`CHANNELS` list with the new channel's WRAM fields and registers.

### Change bad-zone detection
`_emit_badzone_tick` in `music_engine.py` (dissonance via `_emit_pairwise_dissonance`, stuck via
per-channel `STALE_COUNT_*`, overload via the rolling onset window) — see
`docs/research/encyclopedia/R204-bad-zone-detection-heuristics.md` for the grounding.

### Change the visualizer
`tiles.py` — tile data (`_tile_off_bytes`/`_tile_on_bytes`) or the calm/bad-zone palettes
(`CALM_PALETTE`/`BAD_PALETTE`); `visuals.py` — the 4 channel-indicator cells (`CHANNEL_CELLS`)
and every routine that reads engine state to render (IP-8030, BL-0089: tile/palette *data* moved
to `tiles.py`, `visuals.py` keeps the rendering logic and imports from it).

### Change channel-mix presets
`CHMIX_MASKS` in `music_data.py` (8 entries, bit0=pulse A/bit1=pulse B/bit2=wave/bit3=noise,
matching `NR52`'s own bit order) — preset 0 must stay `0b1111` (every pre-existing test assumes
all channels active at boot/reset) and every entry must stay nonzero (an all-silent preset has no
recovery path short of Select). Gating itself lives in `_emit_channel_gen`'s and
`_emit_noise_gen`'s onset blocks (`IP-9010`/`BL-0019`) — extending it to a new channel means
adding that channel's `dac_reg`/`dac_on`/`bit_index` to its `CHANNELS` entry (or, for a
non-`CHANNELS` channel like noise, following `_emit_noise_gen`'s own inline pattern).

### Change Scheme E's motif table or scheme assignment
`MOTIF_TABLE` in `music_data.py` (8 absolute scale-degree targets, 0-7, shared by every
Scheme-E channel) — a first-guess placeholder shape, not tuned by ear (`BL-0005`). Which
`CHMIX_IDX` presets assign Scheme E to which channel is `CHMIX_MASKS`'s bits4-6 (pa=4, pb=5,
wv=6, 0=Scheme W/1=Scheme E) — preset 0 must stay all-Scheme-W (no regression to the shipped
default). Scheme E's onset-timing/pitch-selection logic itself lives in `_emit_channel_gen`'s
note-selection step (`IP-1070`/`BL-0020`) — extending it to a new scheme means adding another
branch there, keyed off a new bit in the same spare-bit range (`ADR-0001`).

### Change the arpeggio's figures
`ARP_PATTERNS` in `music_data.py` — 4 rows x 4 steps; entries are **chord-tone slots (0-2)** into
the current chord's own `CHORD_TABLE` row, plus the reserved `ARP_SUSTAIN` (=3) meaning "hold this
note's own pitch for that step." Two structural constraints, both `FR-1610` and both load-bearing
rather than stylistic: **row 0 must stay all-sustain** (it is how the chord-tone gate is
expressed — `_emit_channel_gen` forces index 0 on a weak melody onset or a stuck bad-zone frame),
and **step 0 of every row must stay `ARP_SUSTAIN`** (so a note begins on the pitch its own onset
triggered, which is what leaves `IP-1061`'s portamento glide intact). The rows must also differ in
*how many* steps move, not merely in the order of slots — four permutations of one sweep would
still present a single figure to a listener, which is the complaint this replaced.
`ARP_PATTERN_PICK` (4 entries, LFSR-indexed, shaped like `DELTA_TABLE`) is the weighting; making
every entry `0` retires the arpeggio outright, which is `ADR-0005`'s named fallback and is
deliberately a one-line data edit. First-guess values throughout (`BL-0005` class).
**Do not** reintroduce degree offsets here: that was the defect (`BL-0127`), and the `AND 0x07`
it needed is the octave-seam arithmetic `ADS-108` D3 already ruled incorrect for chord math.

### Change the harmony (chords, progression, voice roles)
`CHORD_TABLE` in `music_data.py` — 4 scales x 4 chords x 3 tones, flattened, entries are scale
degrees 0-7, addressed `scale*12 + chord*3 + slot`. **Hand-authored on purpose, and re-deriving it
at runtime by stacking thirds would be a bug, not an optimization**: `SCALE_SEMITONES` rows are 8
entries whose 8th duplicates the 1st and every degree is masked `AND 0x07`, so third-stacking
across the octave seam puts the V chord's fifth a scale step wrong (degree 4+4=8 masks to 0/C where
the correct pitch is D). Pentatonic has its own rows — stacked thirds yield no triads in a 5-note
scale, so those four are idiomatic sonorities rather than derived.
`CHORD_TRANSITION` (4 rows x 4 entries, indexed by 2 LFSR bits — the weighting lives in the
*distribution of entries*, exactly like `DELTA_TABLE`); `MELODY_PICK`/`SLOT_NEXT` (which chord tone
each pulse voice takes); `PASSING_TABLE` (the melody's weak-onset step — **not** `DELTA_TABLE`,
which is 50% "hold" and produced a leap-then-hold melody when it was tried here);
`N_CHORD_ONSETS` (chord length, must stay a power of two — the counter wraps with a plain `AND`).
Per-voice roles are `CHANNEL_ROLES` in `music_engine.py`; the rules themselves are the three limbs
in `_emit_channel_gen`'s note-selection block. First-guess values throughout (`BL-0005` class).
**Anything added here must stay inside an existing onset branch** — see `NFR-1240` and the VBlank
note below.

### Change style-preset values
`STYLE_TABLE` in `music_data.py` (8 rows, one per `CHMIX_IDX` preset — independent of
`CHMIX_MASKS`, `ADS-101` SS2 — each `(tempo_idx, density_idx, scale_idx, duty_bias)`) — first-guess
placeholder values, not tuned by ear (`BL-0005`). Index 0 must stay identical to
`PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX`/`PRESET_SCALE_IDX`/`duty_bias=0` (no regression to the
shipped default, `FR-1260`). Applying a style is `_emit_apply_style` (`music_engine.py`), called
from `input_map.py`'s Start-press handler immediately after `CHMIX_IDX` steps — unlike
`CHMIX_MASKS`'s channel-mix/scheme half, style values apply the same frame, not at next onset.

### Change motif variants
`MOTIF_TABLE` in `music_data.py` (now `N_VARIANTS=4` rows of 8 bytes each — variant 0 must stay
byte-identical to the original shipped sequence, `FR-1300`) and `MOTIF_VARIANT_SELECTOR` (4
signed-delta entries, LFSR-indexed, shaped like `DELTA_TABLE`, first-guess retention-biased
weighting, not tuned by ear — `BL-0042`). Variant selection happens only at a motif-cycle
boundary (motif step wraps 7→0) inside `_emit_channel_gen`'s Scheme-E branch (`IP-1090`/`BL-0010`)
— never mid-cycle, and never for a channel running Scheme W. The selection draw reuses that
channel's own LFSR (otherwise idle while running Scheme E), introducing no new randomness source.

### Change song-form phases
`SONG_TABLE` in `music_data.py` (4 rows of 4 bytes — `tempo_idx`, `density_idx`, `duration_lo`,
`duration_hi`, duration in frames — first-guess placeholder values/durations, not tuned by ear,
`BL-0005`). Phase 0 (INTRO) must stay identical to `PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX` (no
regression to boot/Select-reset behavior — this was a real regression caught and fixed during
`IP-1100`'s own implementation, not merely a design guideline). The state machine
(`SONG_STATE`/`SONG_STATE_TIMER_LO`/`SONG_STATE_TIMER_HI`) autonomously cycles all 4 phases via
`_emit_song_tick` (`IP-1100`/roadmap R6), called once per frame from `engine_tick` alongside
`_emit_badzone_tick` — entirely independent of bad-zone recovery and Scheme-E motif-variant
selection (disjoint WRAM fields). No new input control.

### Change settings-indicator tile patterns
`_bar_tile_bytes(n)` in `tiles.py` (8 fill levels, 0-7, one bar-height glyph each — first-guess
pixel design, not tuned by eye, same `BL-0005`-class deferral as every other visual/preset-value
decision). `SETTINGS_CELLS` (5 tilemap cells, immediately after `CHANNEL_CELLS`) each display one
base control's current index (`TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`) as a
fill level via `_emit_update_settings_row`, called once per frame from `update_visuals`
(`IP-1110`/`BL-0051`/`ADS-104`), positioned last in that routine.

> **Corrected 2026-07-31 (`BL-0069`).** This paragraph previously stated that on the exact frame
> Select is pressed, `apply_input`'s `init_engine` reset costs enough extra CPU that the
> settings-row VRAM writes for that frame are **silently dropped**. **That finding is false and is
> withdrawn.** No VRAM write is dropped, on any frame. PyBoy 2.7.0 applies no PPU-mode gating to
> VRAM writes at all (`R301` §3, `mb.py:502-511`), so the harness could never have observed a
> drop; and a WRAM mirror taken at the instant of each write matches the VRAM byte on every frame
> of every class. What was actually seen is a **`pb.tick()` mid-frame sampling artifact**: `tick`
> returns after `apply_input` has updated the index but before `update_visuals` has re-rendered
> from it, so any test reading a WRAM field and its derived tilemap cell after the same `tick`
> reports a one-frame lag — **uniformly, on every frame class including idle frames with no
> input**. The Select-vs-`Up` asymmetry that made it look like a real drop does not exist.
>
> **The real finding, which is broader and worse:** `HALT` wakes at `LY` 144, but
> `read_joypad`+`apply_input`+`engine_tick` consume roughly **9 of VBlank's 10 scanlines**, so
> `update_visuals` finishes at `LY` 153 — the window's last line — on *every* frame. Head-room is
> a handful of instructions and nothing in the build or the suite guards it. Full account:
> `R308` §8.5, `R101` §8.5, `R102` §3c, `GDS-06` §2.2a. On real hardware, which does enforce
> mode 3, that margin is a live and untested exposure (`GDS-02` §7, `BL-0058`) — the display
> would still self-heal the next frame, since `update_visuals` reruns unconditionally
> (`GDS-08` §3). **`IP-9030` (`VIS_ENTRY_LY`, `T19`) now makes this margin measurable every
> frame rather than merely believed** — see the Known Good Behavior entry below.

`OCTAVE_IDX`/
`SCALE_IDX` (4 possible values) share the same 8-level tile set as `TEMPO_IDX`/`DENSITY_IDX`/
`CHMIX_IDX` (8 possible values) rather than a separate narrower set — those two bars simply never
exceed half-full, a first-guess placeholder decision (`FS-111` Open Question 1).

## Known Good Behavior (v1.5 — Foundation + Sound Design + Integrity Remediation + Multi-Scheme Foundation + Genre-Aware Style Presets + Motif Recurrence via Weighted Variant Selection + Song-Form via Autonomous Phase Cycling + Settings & Control Visibility, **SHIPPED BASELINE — full R1-R6 + `IP-1090` + `IP-1110` GO confirmed by the user 2026-07-31**)

- ROM builds to exactly 32768 bytes, valid GBC header, cart type ROM-only (no battery)
- Boots within ~90 frames (GBC boot-ROM logo animation time) to: all 3 pitched channels (pulse
  A/B, wave) generating independent scale-constrained melodic walks, wave channel anchored as a
  bass/timbre voice (lower octave, half note-rate); noise channel gating percussive hits via an
  Euclidean rhythm pattern sized by `DENSITY_IDX`
- All 6 input controls edit exactly their own parameter index, edge-triggered, wrapping correctly;
  driving `DENSITY_IDX` to its extremes measurably changes noise-onset rate (138 vs. 563
  onset-frames per 600-frame run at min vs. max density)
- Bad-zone detection: `DISSONANCE_SCORE` (Helmholtz-roughness-grounded interval-class weights)
  recomputed every frame from the three pitched channels' current notes; per-channel `STALE_COUNT`
  tracks repeated notes; a rolling onset-window counter tracks overall channel activity rate; all
  three combine into `BAD_ZONE_FLAGS` bit3
- The engine autonomously biases its own generation out of dissonant/stuck/overloaded states,
  every frame, with no input required (confirmed: a long headless run enters a bad zone and
  recovers from it on its own — `test_rom.py` T10)
- **Select is a reroll, not a reset (`IP-1160`, 2026-08-21 — the control's meaning changed).** It
  resets every channel's generation state and all bad-zone counters and **randomizes each
  channel's melodic seed from the `DIV` register**, so the engine resumes immediately on the same
  frame from a genuinely different starting point. What it no longer does is touch the listener's
  own settings: `TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`, `CHMIX_IDX` and `DUTY_BIAS`
  are **bit-identical across the press**. Confirmed at the output boundary on captured audio: at
  non-default settings the sounded pitch track changes across 28/40 250 ms windows while all six
  values read unchanged on the press frame itself. Mechanically, `init_engine` is now a boot-only
  prologue holding all eight steering writes (the five `PRESET_*`, `DUTY_BIAS`, and phase 0's own
  `SONG_TABLE[0]` tempo/density pair) that falls through into `engine_reroll`, the shared body the
  Select handler calls directly. **Boot is unchanged**, verified byte-for-byte: WRAM `0xC000`-
  `0xC09F` and the 10 s sounded pitch track are identical to the pre-change build
- Visualizer: LCD on, 4 tile indicators reflect `NR52`'s per-channel active bits every frame; BG
  palette swaps from calm (blue/green) to bad-zone (red) tones based on `BAD_ZONE_FLAGS` bit3
- Pulse A/B arpeggiate (frequency cycles through a 4-step chord-tone pattern every few frames,
  no envelope retrigger), vibrato-wobble every frame, glide (portamento) from the old pitch to
  the new one across a degree-changing onset, and vary duty cycle per onset (`IP-1060`/`IP-1061`,
  `R216`)
- Start-stepped channel-mix presets (`CHMIX_MASKS`, `IP-9010`/`BL-0019`) actually gate which
  channels sound: an excluded channel's frequency/duty writes are skipped and its DAC/envelope is
  explicitly forced off, clearing its `NR52` bit within one note-cycle; a re-included channel
  resumes generating and reporting active on its own next onset. Internal bookkeeping
  (stale/onset-window counters, the melodic walk itself) keeps running for an excluded channel so
  it resumes musically-current, not frozen, when re-enabled.
- Overload detection (`IP-9020`/`BL-0017`) is now empirically reachable: `OVERLOAD_THRESHOLD`
  recalibrated from `20` (mathematically unreachable) to `7`, based on measured peak onset counts
  (not just the analytical average-rate formula, which understated real bursts) — reachable at a
  realistic-high tempo/density combination, not spuriously reachable at the sparse default.
- Combinable generation schemes (`IP-1070`/`BL-0020`): each pitched channel can independently run
  Scheme W (the original LFSR walk) or Scheme E (a Euclidean-pattern-gated onset schedule + a
  fixed 8-step motif), selected per `CHMIX_IDX` preset (preset 6 assigns Scheme E to the wave
  channel, per `ADS-100`'s own worked example — a recognizable repeating bass motif against pulse
  A/B's freer drift). Bad-zone detection/recovery applies identically regardless of scheme.
- Genre-aware style presets (`IP-1080`, roadmap R5/`ADS-101`): pressing Start now applies a
  coordinated tempo/density/scale/duty-bias combination immediately (same frame), not just a
  channel-mix/scheme change — 3 named v1 styles (Techno/Chiptune-Driving, Ambient/Lo-Fi, Holiday)
  plus the shipped default at preset 0. Bad-zone state (`DISSONANCE_SCORE`/`BAD_ZONE_FLAGS`/
  `STALE_COUNT_*`/`ONSET_WINDOW_COUNT`) is untouched by a style change.
- Motif recurrence via weighted variant selection (`IP-1090`, `BL-0010`/`ADS-102`): a Scheme-E channel's motif data is now 4 pre-composed
  variants (variant 0 identical to the original shipped sequence); at each motif-cycle boundary
  the engine autonomously draws which variant plays next via a retention-biased weighted lookup,
  no input required. Bad-zone detection/recovery and every other mechanism are unaffected.
- Song-form via autonomous phase cycling (`IP-1100`, roadmap R6/`ADS-103`, **`VERIFIED` via
  `VR-1100`, **in the shipped baseline as of the 2026-07-31 GO**): the engine autonomously cycles 4 named
  phases (INTRO/BUILD/PEAK/BREAKDOWN, looping), overwriting `TEMPO_IDX`/`DENSITY_IDX` to that
  phase's target values on each transition, no input required, over a ~110-second full cycle.
  Entirely independent of bad-zone detection/recovery and Scheme-E motif-variant selection.
- Settings & control visibility (`IP-1110`, `BL-0051`/`ADS-104`, **`VERIFIED` via `VR-1110`, in
  the shipped baseline as of the 2026-07-31 GO**): the visualizer displays 5 bar-height indicator
  tiles, one per base control (tempo/octave/scale/density/channel-mix), each reflecting that
  parameter's current index, updated every frame — purely additive to the existing
  channel-activity tiles/palette, no new palette, no font/text rendering. A one-frame display lag
  exists on **every** frame class, not specifically on a Select reset — it is a `pb.tick()`
  harness sampling artifact, not a dropped write or a Select-specific behavior (corrected
  2026-07-31, `BL-0069`; see "VBlank budget assertion" below).
- VBlank budget assertion (`IP-9030`, `BL-0069`): a permanent diagnostic (`VIS_ENTRY_LY`) records
  `LY` at entry to `update_visuals` every frame; `T19` asserts it stays within VBlank (`144`-`153`)
  across five frame classes (idle, plain index step, Start, Select, song-form transition).
  Measured: `HALT` wakes at `LY` 144 on every frame; `read_joypad`+`apply_input`+`engine_tick`
  alone consume through `LY` 152-153, so `update_visuals` runs against roughly one remaining
  scanline — on every frame, idle included, not only on heavy-input frames. Guards against a
  regression silently spending that head-room; does not itself widen the budget. This superseded
  an earlier, incorrect finding that VRAM writes were being dropped on specific frame classes —
  see `R308` §8.5 for the full self-correction.
- Emotional/Energy Layer (`IP-1120`, roadmap R7/`ADS-105`/`FS-112`): two derived WRAM bytes,
  `AROUSAL` (`TEMPO_IDX+DENSITY_IDX`) and `VALENCE` (`VALENCE_TABLE[SCALE_IDX]`), recomputed only
  at the 6 write sites that can change those inputs — never per-frame (`NFR-1170`, a direct
  response to `IP-9030`'s VBlank-budget finding). Infrastructure-only: zero audible/visible
  change, `visuals.py` untouched; groundwork for roadmap R9's future mood-reactive visualizer
  work, which remains separately blocked. `VALENCE_TABLE`'s 4 entries are illustrative
  first-guess values, not tuned by ear (`BL-0005`-class deferral).
- Genre Blending (`IP-1130`, roadmap R8/`ADS-107`/`FS-113`, amends `FR-1240`): a Start press's
  style change is no longer instant for 3 of its 4 fields — `SCALE_IDX` still hard-switches the
  same frame, but `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` now glide toward the newly-selected
  `STYLE_TABLE` row over `BLEND_STEP`'s 0-4 progress (as-shipped: **N=4 frames** to land exactly,
  a first-guess placeholder like every other untuned constant here, not the package's
  originally-proposed N=16 — `FS-113` Open Question 1, deferred to `09-content-review` tuning). A
  second Start press mid-blend restarts the blend from the engine's then-current,
  partially-interpolated values, not the original pre-first-press values. Disclosed finding: this
  package's own unconditional per-frame `blend_tick` call (cheap steady-state check-and-return)
  shifted `engine_tick`'s cycle timing enough to newly expose a **pre-existing, latent** one-frame
  self-healing read-order race between the visualizer's `NR52` sample and the wave channel's own
  periodic DAC retrigger (not introduced by, or fixable within, this package — `visuals.py` is
  untouched) — same self-healing-lag class as the settings-indicator display's own note above, now
  also disclosed for the channel-activity indicator tiles (`T9.3`, tolerating exactly a single-
  frame skew, never two consecutive).
  **`VR-1130` F1 remediation (2026-08-08):** the original active-blend design re-derived each
  field's delta from `STYLE_TABLE` every single active-blend frame; independent verification found
  this genuinely exceeded the VBlank budget on those frames (measured via `VIS_ENTRY_LY` reading
  `0` — mid active-display, nowhere near VBlank — not a display artifact). Fixed by precomputing
  each field's delta once, in `_emit_begin_blend` (`BLEND_DELTA_TEMPO`/`DENSITY`/`DUTY`,
  `0xC074`-`0xC076`), removing the per-frame `STYLE_TABLE` lookup from `_emit_blend_tick` entirely.
  Fixing this also surfaced and closed a second, independent latent defect: `BLEND_STEP` was never
  explicitly initialized, so a boot or Select-reset could leave `blend_tick` free to keep
  "blending" using stale source/delta values and corrupt the freshly-reset
  `TEMPO_IDX`/`DENSITY_IDX`/`DUTY_BIAS` on the following frames — `init_engine` now explicitly
  resets `BLEND_STEP` to `4` (settled/no-active-blend) on both boot and Select. One further
  disclosed, understood, bounded timing effect remains: the *combined* `begin_blend`+`blend_tick`
  cost on the Start-press frame itself can still exceed one harness `tick()` call's cycle budget,
  confirmed via `pyboy` instruction-level hook tracing — the blend's first interpolation write can
  become externally observable one `tick()` call later than the press, though `_emit_begin_blend`'s
  own direct writes (`BLEND_SRC_*`/`BLEND_DELTA_*`/`SCALE_IDX`) always land same-frame, and the
  final landing-exactly-on-target guarantee (`FR-1480`) is unaffected regardless. `T21.3b` now
  independently hand-derives a genuine mid-blend value against the shipped ROM, closing the
  coverage gap that let the original defect ship undetected.

- **Harmonic coordination via a shared chord context (`IP-1140`, `BL-0119`/`FS-114`/`FEAT-1150`,
  `ADS-108` as amended by its §11/D13 + `ADR-0004`) — THE BOOT SOUND CHANGED, DELIBERATELY.** This
  is the first change in this project's history that is not additive to the shipped baseline, and
  it is the answer to the project owner's own "the music doesn't sound good yet." `BL-0119` measured
  the cause: three pitched channels random-walking with no shared harmonic state, so every note was
  in key and nothing coordinated what the notes were in key *together*. All three pitched channels
  now derive their notes from one shared `CHORD_IDX` that advances every 4 pulse-A onsets through a
  sparse, tonic-biased transition table (V returns to I three times in four; V never retrogresses
  to IV). The wave channel alternates the chord's root and fifth instead of wandering by step;
  pulse A takes a chord tone on strong onsets and a passing step on weak ones; pulse B takes the
  chord tone one slot above whichever pulse A published, so the two can never double into unison.
  **The unharmonized independent walk is no longer reachable on any preset** — the project owner
  explicitly released the preset-0 no-regression standard as arbitrary and self-imposed
  (`GDS-04` §4.1 carries the dated amendment: the invariant's *fixed-point* half stands, its
  *historical-no-regression* half is released), which is what let harmony *become* the default
  instead of sitting beside it as a third scheme. Scheme E is untouched and remains unharmonized.
  **Cost discipline** — the whole mechanism lives inside onset branches that already existed;
  `engine_tick`'s call list is unchanged and **nothing unconditional was added to the per-frame
  path** (`NFR-1240`; `IP-9040` was abandoned over exactly that, `BL-0113`). Measured on
  chord-transition frames, `VIS_ENTRY_LY` stays at 152-153, inside VBlank.
  **Measured result** (boot defaults, 3600 frames, pitch classes derived from degrees rather than
  from the engine's own one-frame-lagged `SEMI_*` bytes): harsh vertical intervals on
  **strong-beat sonorities 23.3% → 12.2%**, weak-beat 36.6% → 30.6%, aggregate 30.0% → 21.5%.
  **⚠️ Those four figures are OVERSTATED and are corrected below (`BL-0128`, 2026-08-21).** They
  were computed from `CUR_DEGREE` — what the harmony layer *intends* — while `arp_tick` rewrote
  the frequency register afterwards on every frame, so the pitch that actually sounded was never
  measured. On **sounding pitch**, the same build and the same run read strong-beat **25.7%**,
  weak-beat **36.1%**, aggregate **30.9%**. The improvement was real but roughly half of it was
  being overwritten by the arpeggio; `IP-1150` fixes the cause, and `NFR-1270` now makes sounding
  pitch the normative measurement basis.
  The strong-beat figure is the acceptance instrument (`NFR-1270`/`BL-0122`) — a chord-tone/
  passing-tone melody sounds non-chord tones on weak beats *on purpose*, so the aggregate would
  report a working design as a near-failure. `R225` §5f's simulation predicted exactly this shape.
  Bad-zone activity dropped from 34/121 to 15/121 sampled onsets with no threshold retuning.
  **Still not built, and still audible as missing**: there are no rests anywhere and no formal
  phrase boundaries (`CR-0003`); the melody alternates leap and step rather than sustaining long
  phrases. A human listening pass is what decides whether this is now pleasant — a green suite has
  never once predicted that, which is the whole point of `BL-0097`/`BL-0120`.

- **The arpeggio re-rooted, gated and varied (`IP-1150`, `BL-0127`/`FS-115`/`FEAT-1160`,
  `ADS-108` §12/D14 + `ADR-0005`) — THE BOOT SOUND CHANGED AGAIN, DELIBERATELY.** The project
  owner listened to `IP-1140`'s result and reported **"constant repeated arpeggios."** He was
  right, and the cause was a mechanism nobody had revisited: `IP-1060` added the arpeggio in
  2026-07 to *imply a chord on a single channel* (`R216`) — i.e. to **fake harmony in its
  absence** — and when `IP-1140` supplied real harmony, the arpeggio kept adding
  `[0, 2, 4, 2]` scale-degree offsets **to the chord tone the harmony had just chosen**, stacking
  a second, differently-rooted triad on the engine's own chord, every frame, on both pulse
  channels, forever.
  **Measured before/after on sounding pitch** (boot defaults, 3600 frames, `3e635ed` → this
  build): harsh vertical intervals on **strong beats 25.7% → 10.9%**, weak-beat 36.1% → 27.8%,
  aggregate 30.9% → 19.3%. Sounding pulse-channel frames that are tones of the current chord:
  **46.4% → 74.9%** (not 100%, and correctly so — a sustained passing tone is a non-chord tone on
  purpose). Bad-zone activity 15/121 → **7/121** sampled onsets, again with no threshold retuning.
  **On the complaint itself**, measured at the source rather than by ear-proxy: the shipped build
  produced **3** distinct articulation shapes across a run and **0%** of notes went un-arpeggiated
  — and those 3 were one compiled-in shape plus two octave-seam wrap variants, one of which
  (13.2% of notes) inverted the figure into a downward leap of a sixth, the `R225` §3g defect
  audibly present. This build produces **21** distinct shapes and **47.1%** of notes do not
  arpeggiate at all.
  **It also gave VBlank head-room back.** `arp_tick` no longer computes anything: `arp_resolve`,
  called from each channel's existing onset branch, resolves the figure into `ARP_CACHE_PA`/`PB`
  and the per-frame routine just indexes it — deleting the `SCALE_IDX`/`OCTAVE_IDX` → `ptr_table`
  → note-table address resolution that ran twice per frame forever. Measured over 600 idle frames:
  `VIS_ENTRY_LY` **152/153 → 151/152**, a clean one-scanline (~456-cycle) recovery on *every*
  frame. This is the first per-frame head-room recovered since `R101` §8.5 measured the budget
  exhausted, and `IP-9040` was abandoned over three instructions (`BL-0113`).
  **The trap this package existed to not fall into** (`BL-0130`): `FR-1150`'s portamento and
  `FR-1140`'s vibrato are not routines of their own — they are produced **by** `arp_tick`'s
  per-frame frequency rewrite, which is why `engine_tick` calls it *before* `gen_tick`. So
  implementing the gate as "skip the write" would have deleted both on every weak melody onset,
  where portamento matters most, **with the whole suite still green** because nothing asserted a
  glide had occurred. Sustaining means *write this note's own pitch*, never *stop writing*, and
  `T23.5` now asserts it.
  **Two behaviours that changed on purpose and are requirements, not side effects**: a
  scale/octave change during an already-sounding note now lands at that channel's **next onset**
  rather than mid-note (`FR-1620` — the onset write itself still uses current values, so nothing
  is less responsive than one note); and `init_engine` repopulates both caches on boot **and**
  Select (`FR-1630`), the `BLEND_STEP` defect class `VR-1130` already found once.
  **Retirement was weighed as the strongest rival and rejected on evidence** (`ADS-108` §12.5):
  with no rests and no phrase structure yet (`CR-0003`), sub-note motion is currently the only
  thing happening between onsets, so removing it trades "mechanically busy" for "static and
  plodding." It survives as a one-line fallback — an all-sustain `ARP_PATTERN_PICK` *is*
  retirement.
  **Still not built, and still audible as missing**: rests and phrase boundaries (`CR-0003`) —
  unchanged by this package, and now the largest remaining structural gap.

**191/191 `test_rom.py` checks pass** (T1-T23). An 8000+ frame stress run with continuous input
churn completed with no hangs, entering and autonomously recovering from a bad zone along the way.
See `docs/implementation/packages/` for each package's exact scope.

**Explicitly not built**: ~~chord-progression~~ (**built 2026-08-20, `IP-1140`** — see the
harmonic-coordination entry above) /
song-form composition, phrase structure/rests/cadence (`CR-0003`), session-length-adaptive drift, non-default preset tuning by ear, a proper
`visuals.py` beyond the 4-tile/2-palette MVP — see `docs/pipeline/backlog.md` (`BL-0005`,
`BL-0011`) for named, deferred candidates.

## Known Issues

None currently reproducing. See [`docs/pipeline/backlog.md`](docs/pipeline/backlog.md) for the
live list of open items (nothing here is a stale snapshot).
