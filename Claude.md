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
music_engine.py  — all sound-channel generation logic (4 channels), bad-zone detection,
                    preset/table data, PSG register writes
input_map.py     — joypad edge detection + the input->parameter mapping (never writes PSG regs)
visuals.py       — tile/palette visualizer, read-only consumer of engine state (never writes
                    engine state or PSG registers)
build_rom.py     — master build: imports all modules, lays out ROM sections, patches pointers
test_rom.py      — headless PyBoy verification harness (drives button sequences, asserts on
                    sound registers + WRAM engine state) — 122 checks across T1-T18
```

### Data layout, WRAM map

Authoritative source: [`docs/architecture/07-data-model.md`](docs/architecture/07-data-model.md)
(GDS-07). Quick orientation: parameter indices at `0xC000`-`0xC004` (tempo/octave/scale/density/
channel-mix — channel-mix now gates each channel's own generation routine, `IP-9010`/`BL-0019`),
bad-zone state at
`0xC005`-`0xC00B` (dissonance score, per-channel stale counts, onset-window counter/timer),
per-channel generation state (note timers, scale degrees, LFSR states) at `0xC00C`+, joypad state
at `0xC050`-`0xC052`, noise step index at `0xC019`, **arpeggio state (`IP-1060`) at `0xC01D`-
`0xC01F`** (`ARP_STATE_PA`/`PB` — packed countdown+step byte — and a shared scratch byte). **No
SRAM** — this project makes no save/battery commitment (MSTR-001 C2).

### Input mapping (GDS-03 SS3)

| Input | Parameter |
|---|---|
| D-pad Up/Down | Tempo step +/- |
| D-pad Right/Left | Octave step +/- |
| A | Next scale/mode |
| B | Next density preset (noise-channel Euclidean pattern) |
| Start | Next channel-mix preset (`CHMIX_MASKS`-gated — only the preset's included channels sound, `IP-9010`) |
| Select | Reset all channels + bad-zone state to the known-good preset **and randomize each channel's melodic seed** (unconditional, manual override — not the only recovery path, see below) |

All edge-triggered (rising edge only — holding does not repeat).

### Autonomous bad-zone avoidance/recovery (IP-0007)

The engine detects **and acts on** a bad zone every frame, without requiring Select (MSTR-001 C5
amended v1.1). Select remains available as a manual "reset and randomize" override, but is no
longer the only way out:

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
  rewritten (no retrigger — envelope keeps decaying naturally) to cycle through
  `ARPEGGIO_OFFSETS`, a period-4 up/down pattern of scale-degree deltas from the currently-held
  root note, implying a chord on a single channel.
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
Edit the relevant table in `music_engine.py` (`TEMPO_BPM`, `OCTAVE_ROOT_HZ`, `SCALE_SEMITONES`,
`DELTA_TABLE`, `DENSITY_K`, `DISSONANCE_WEIGHT_BY_IC`, the `*_THRESHOLD` constants, the `PRESET_*`
constants) — no other file needs to change; `build_rom.py` regenerates everything from these
tables at build time. **These are still first-guess placeholders** (`BL-0005`), not tuned by ear.

### Add a new scale/mode
Add an entry to `SCALE_SEMITONES` and `SCALES` in `music_engine.py` (exactly 8 semitone-offset
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
`visuals.py` — tile data (`_tile_off_bytes`/`_tile_on_bytes`), the 4 channel-indicator cells
(`CHANNEL_CELLS`), or the calm/bad-zone palettes (`CALM_PALETTE`/`BAD_PALETTE`).

### Change channel-mix presets
`CHMIX_MASKS` in `music_engine.py` (8 entries, bit0=pulse A/bit1=pulse B/bit2=wave/bit3=noise,
matching `NR52`'s own bit order) — preset 0 must stay `0b1111` (every pre-existing test assumes
all channels active at boot/reset) and every entry must stay nonzero (an all-silent preset has no
recovery path short of Select). Gating itself lives in `_emit_channel_gen`'s and
`_emit_noise_gen`'s onset blocks (`IP-9010`/`BL-0019`) — extending it to a new channel means
adding that channel's `dac_reg`/`dac_on`/`bit_index` to its `CHANNELS` entry (or, for a
non-`CHANNELS` channel like noise, following `_emit_noise_gen`'s own inline pattern).

### Change Scheme E's motif table or scheme assignment
`MOTIF_TABLE` in `music_engine.py` (8 absolute scale-degree targets, 0-7, shared by every
Scheme-E channel) — a first-guess placeholder shape, not tuned by ear (`BL-0005`). Which
`CHMIX_IDX` presets assign Scheme E to which channel is `CHMIX_MASKS`'s bits4-6 (pa=4, pb=5,
wv=6, 0=Scheme W/1=Scheme E) — preset 0 must stay all-Scheme-W (no regression to the shipped
default). Scheme E's onset-timing/pitch-selection logic itself lives in `_emit_channel_gen`'s
note-selection step (`IP-1070`/`BL-0020`) — extending it to a new scheme means adding another
branch there, keyed off a new bit in the same spare-bit range (`ADR-0001`).

### Change style-preset values
`STYLE_TABLE` in `music_engine.py` (8 rows, one per `CHMIX_IDX` preset — independent of
`CHMIX_MASKS`, `ADS-101` SS2 — each `(tempo_idx, density_idx, scale_idx, duty_bias)`) — first-guess
placeholder values, not tuned by ear (`BL-0005`). Index 0 must stay identical to
`PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX`/`PRESET_SCALE_IDX`/`duty_bias=0` (no regression to the
shipped default, `FR-1260`). Applying a style is `_emit_apply_style` (`music_engine.py`), called
from `input_map.py`'s Start-press handler immediately after `CHMIX_IDX` steps — unlike
`CHMIX_MASKS`'s channel-mix/scheme half, style values apply the same frame, not at next onset.

### Change motif variants
`MOTIF_TABLE` in `music_engine.py` (now `N_VARIANTS=4` rows of 8 bytes each — variant 0 must stay
byte-identical to the original shipped sequence, `FR-1300`) and `MOTIF_VARIANT_SELECTOR` (4
signed-delta entries, LFSR-indexed, shaped like `DELTA_TABLE`, first-guess retention-biased
weighting, not tuned by ear — `BL-0042`). Variant selection happens only at a motif-cycle
boundary (motif step wraps 7→0) inside `_emit_channel_gen`'s Scheme-E branch (`IP-1090`/`BL-0010`)
— never mid-cycle, and never for a channel running Scheme W. The selection draw reuses that
channel's own LFSR (otherwise idle while running Scheme E), introducing no new randomness source.

### Change song-form phases
`SONG_TABLE` in `music_engine.py` (4 rows of 4 bytes — `tempo_idx`, `density_idx`, `duration_lo`,
`duration_hi`, duration in frames — first-guess placeholder values/durations, not tuned by ear,
`BL-0005`). Phase 0 (INTRO) must stay identical to `PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX` (no
regression to boot/Select-reset behavior — this was a real regression caught and fixed during
`IP-1100`'s own implementation, not merely a design guideline). The state machine
(`SONG_STATE`/`SONG_STATE_TIMER_LO`/`SONG_STATE_TIMER_HI`) autonomously cycles all 4 phases via
`_emit_song_tick` (`IP-1100`/roadmap R6), called once per frame from `engine_tick` alongside
`_emit_badzone_tick` — entirely independent of bad-zone recovery and Scheme-E motif-variant
selection (disjoint WRAM fields). No new input control.

### Change settings-indicator tile patterns
`_bar_tile_bytes(n)` in `visuals.py` (8 fill levels, 0-7, one bar-height glyph each — first-guess
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
> (`GDS-08` §3). `OCTAVE_IDX`/
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
- Select unconditionally resets every channel's generation state and all bad-zone counters to the
  known-good preset (major scale, mid tempo/octave, sparse density) **and randomizes each
  channel's melodic seed from the `DIV` register** — engine resumes playing immediately on the
  same frame, with a genuinely different starting point each press
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
- Settings & control visibility (`IP-1110`, `BL-0051`/`ADS-104`, **`VERIFIED` via `VR-1110`, not
  yet part of the shipped baseline**): the visualizer displays 5 bar-height indicator tiles, one
  per base control (tempo/octave/scale/density/channel-mix), each reflecting that parameter's
  current index, updated every frame — purely additive to the existing channel-activity
  tiles/palette, no new palette, no font/text rendering. A disclosed, self-healing one-frame
  display lag exists specifically on the frame a Select reset is pressed (independently
  reproduced by `VR-1110` across 3 distinct pre-Select sequences; see "Change settings-indicator
  tile patterns" above).

**122/122 `test_rom.py` checks pass** (T1-T18). An 8000+ frame stress run with continuous input
churn completed with no hangs, entering and autonomously recovering from a bad zone along the way.
See `docs/implementation/packages/` for each package's exact scope.

**Explicitly not built**: chord-progression/
song-form composition, session-length-adaptive drift, non-default preset tuning by ear, a proper
`visuals.py` beyond the 4-tile/2-palette MVP — see `docs/pipeline/backlog.md` (`BL-0005`,
`BL-0011`) for named, deferred candidates.

## Known Issues

None currently reproducing. See [`docs/pipeline/backlog.md`](docs/pipeline/backlog.md) for the
live list of open items (nothing here is a stale snapshot).
