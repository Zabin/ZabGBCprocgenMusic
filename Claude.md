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
                    sound registers + WRAM engine state) — 60 checks across T1-T10
```

### Data layout, WRAM map

Authoritative source: [`docs/architecture/07-data-model.md`](docs/architecture/07-data-model.md)
(GDS-07). Quick orientation: parameter indices at `0xC000`-`0xC004` (tempo/octave/scale/density/
channel-mix — channel-mix wired but not yet consumed by any channel), bad-zone state at
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
| Start | Next channel-mix preset (wired, not yet consumed) |
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

### Sound design techniques (`IP-1060`/`IP-1061`, R216)

Pulse A/B (not wave — it keeps its plain sustained bass role) get four layered timbral effects,
all always-on, no new input control:

- **Arpeggio** → every few frames (`ARP_SUBTICK_RELOAD`), the channel's frequency register is
  rewritten (no retrigger — envelope keeps decaying naturally) to cycle through
  `ARPEGGIO_OFFSETS`, a period-4 up/down pattern of scale-degree deltas from the currently-held
  root note, implying a chord on a single channel.
- **Duty cycle** → `NR11`/`NR21`'s duty bits vary per onset (`DUTY_BY_DEGREE`, indexed by
  `CUR_DEGREE mod 4`) instead of staying fixed at 50%.
- *(Vibrato/portamento land in `IP-1061` — update this section once built.)*

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

## Known Good Behavior (MVP — Foundation release bucket, self-tested this session)

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
  no envelope retrigger) and vary duty cycle per onset (`IP-1060`, `R216`)

**63/63 `test_rom.py` checks pass** (T1-T11). A 6000+ frame stress run with continuous input
churn completed with no hangs, entering and autonomously recovering from a bad zone along the way.
See `docs/implementation/packages/` for each package's exact scope.

**Explicitly not built yet**: vibrato/portamento (`IP-1061`, planned next), chord-progression/
song-form composition, session-length-adaptive drift, non-default preset tuning by ear, a proper
`visuals.py` beyond the 4-tile/2-palette MVP — see `docs/pipeline/backlog.md` (`BL-0005`,
`BL-0011`) for named, deferred candidates.

## Known Issues

None currently reproducing. See [`docs/pipeline/backlog.md`](docs/pipeline/backlog.md) for the
live list of open items (nothing here is a stale snapshot).
