# Functional & Non-Functional Requirements — v1 baseline

- **Owned by:** `04-requirements-engineering` · **Status:** ✅ Authored, 2026-07-21
- **Derived from:** GDS-00/01/03/07. This is a from-scratch increment's first requirements pass —
  every FR/NFR below traces to a GDS-03/07 decision, not to existing code (there is none yet).

## Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| FR-1000 | On power-on, the engine initializes to the known-good preset (GDS-03 §5) and begins generating audio on all channels its channel-mix preset activates, with no button input required. | GDS-01, GDS-03 §5 |
| FR-1010 | The generation routine writes valid PSG register values for pulse A, pulse B, wave, and noise channels such that `NR52` reports each active channel as currently playing when its channel-mix preset includes it. | GDS-03 §1-2, R100 |
| FR-1020 | D-pad Up/Down each step `TEMPO_IDX` by exactly one (wrapping), on the frame of a rising edge only — holding the direction does not repeat the step. | GDS-03 §3, GDS-07 §1 |
| FR-1030 | D-pad Left/Right each step `OCTAVE_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1040 | The A button steps `SCALE_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1050 | The B button steps `DENSITY_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1060 | The Start button steps `CHMIX_IDX` by exactly one (wrapping), edge-triggered. | GDS-03 §3, GDS-07 §1 |
| FR-1070 | ~~The Select button, on a rising edge, unconditionally reloads all of `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` to the known-good preset and clears `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/all `STALE_COUNT_*`/`ONSET_WINDOW_COUNT`, regardless of the current bad-zone state.~~ **AMENDED IN PLACE 2026-08-21 — Select becomes a *reroll*, not a reset** ([`ADR-0006`](../architecture/adr/ADR-0006-select-becomes-reroll-not-reset.md), on the project owner's direct instruction: *"The select-reset does not need to bring it back to the boot default either, just course correct from a bad zone."*). It now reads: **The Select button, on a rising edge, unconditionally (a) reseeds every pitched channel's pseudo-random melodic stream so the material that follows is genuinely new, and (b) clears `BAD_ZONE_FLAGS`/`DISSONANCE_SCORE`/all `STALE_COUNT_*`/`ONSET_WINDOW_COUNT`, regardless of the current bad-zone state; and (c) leaves `TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`, `CHMIX_IDX` and `DUTY_BIAS` at whatever values the listener currently has set — by **every** write path, not merely by the direct one.** The "unconditional, regardless of bad-zone state" property is deliberately retained from the original (`IP-0001`): a control whose effect depends on invisible state is worse than either behaviour alone. **Clause (c)'s "every write path" wording is load-bearing and is not boilerplate** — see the Delta Review below (finding **D1**): the reset path writes `TEMPO_IDX`/`DENSITY_IDX` **twice**, once from the preset and once from the song-form phase-0 row, and an implementation that removes only the first would silently reset two of the five settings while preserving the other three. **Why the old requirement was wrong rather than merely superseded**: it conflated three unrelated things, and the index reload existed only because Select was once the engine's **only** bad-zone escape. `IP-0007` made recovery autonomous in 2026-07 and both `Claude.md` and `GDS-04` §5 recorded that supersession in prose, while nothing re-examined the mechanism it obsoleted — so a listener's only control for "give me different music" also discarded every parameter they had set. | GDS-03 §5; **amended:** `ADR-0006`, `GDS-01` step 6, `GDS-04` §4.1 (second amendment) and §1.2's steering-index writer registry; user directive 2026-08-21 |
| FR-1080 | On every note-onset event, the engine recomputes `DISSONANCE_SCORE` from the currently-sounding pitched channels' scale degrees and sets `BAD_ZONE_FLAGS` bit0 (`DISSONANT`) when the score exceeds the dissonance threshold. | GDS-03 §4a |
| FR-1090 | On every note-onset event, each pitched channel's history ring buffer (`HIST_PA`/`PB`/`WV`) records the new scale degree; `STALE_COUNT_*` increments while a period-1-or-2 repeat continues and resets otherwise; `BAD_ZONE_FLAGS` bit1 (`STUCK`) is set when any `STALE_COUNT_*` exceeds the stale threshold. | GDS-03 §4b |
| FR-1100 | The engine counts note-onset events across all channels in a rolling window and sets `BAD_ZONE_FLAGS` bit2 (`OVERLOAD`) when the count exceeds the overload threshold within the window. | GDS-03 §4c |
| FR-1110 | `BAD_ZONE_FLAGS` bit3 (`COMBINED`) is the logical OR of bits0-2, recomputed whenever any of them changes. | GDS-03 §4d |
| FR-1120 | The visualizer reads `NR52`/`NR51` and the WRAM engine-state mirror and updates BG tile/palette content to represent per-channel activity and bad-zone status, without writing to any engine-state or PSG register itself (read-only consumer). **Reworded 2026-07-26** (`BL-0016`, per [GDS-08 §7](../architecture/08-presentation-architecture.md)): the original text also claimed tempo representation. Displaying the tempo *setting* is real but is owned by `FR-1350` (`IP-1110`'s indicator row), not here; tempo-*synced motion* — a visual element whose timing follows the beat, which is how the original wording read naturally in `R205`/`R223`'s audio-visual-sync context — was never built and is now `CR-0001` below, explicitly not baselined. | GDS-03 §1, GDS-08 §2/§3 |
| FR-1130 | ~~Each pitched channel's note-onset behavior rapidly cycles the channel's frequency register among 2 or 3 notes of a chord **implied by the channel's current scale degree** (root + at least one harmonic interval above it, e.g. a third and/or fifth within the active scale)~~ **Amended in place 2026-08-21** (`ADS-108` §12/D14, `ADR-0005`; `BL-0127`): an arpeggiating channel rapidly cycles its frequency register among **tones of the currently-sounding shared chord** (`FR-1500`), for the duration of that note, before the next scheduled note-onset event. The chord the arpeggio spells is the ensemble's chord, **not** a second chord implied by the channel's own degree — the original wording dates from before `FR-1500` existed and, once it did, described the engine stacking a differently-rooted triad on top of its own harmony (measured: only 46.4 % of sounding pulse-channel frames were tones of the sounding chord, and strong-beat harsh intervals read 25.7 % on sounding pitch against 12.0 % on the selected notes). Which tones and in what order is a data decision (`FR-1610`); *whether* the channel arpeggiates at all on a given note is `FR-1600`. | R216 §3/§5 (arpeggio-as-polyphony), GDS-03 §1 (channel ownership); **amended:** ADS-108 §12/D14, ADR-0005, BL-0127, FR-1500. **Implemented by `IP-1150`** — `music_engine.py` `_emit_arp_resolve`/`_emit_arpeggio_tick`, `music_data.py` `ARP_PATTERNS`; verified by `T23.1`/`T23.2`/`T23.2b` |
| FR-1140 | Each pitched channel's currently-sounding frequency is periodically modulated by a small, bounded oscillation (vibrato) around the note's base frequency, audible as a pitch wobble rather than a step change, without altering which scale degree the channel is considered to be playing for dissonance/stale-repetition scoring purposes (FR-1080/FR-1090 read the base note, not the modulated instantaneous frequency). | R216 §3/§5 (vibrato) |
| FR-1150 | On a note-onset event where the channel's previous and new scale degrees differ, the channel's frequency register transitions from the previous note's frequency to the new note's frequency over more than one frame (a glide/portamento), rather than jumping directly to the new frequency on the onset frame. | R216 §3/§5 (portamento) |
| FR-1160 | At least one pulse channel's duty-cycle register bits (`NR11`/`NR21`) vary across note-onset events rather than remaining fixed at a single duty-cycle value for the entire session. | R216 §3/§5/§6 (duty-cycle variation) |
| FR-1170 | The noise channel's percussion synthesis (fast-decay envelope on `NR42`, `FR-1010`'s existing noise-channel scope) already satisfies R216 §3's chiptune-percussion-synthesis convention ("basic percussion... generated from white noise going through an ADSR envelope") as shipped by `IP-0003` — this requirement records the trace explicitly; it introduces no new behavior. | R216 §3 (percussion synthesis, already shipped), FR-1010 |
| FR-1180 | Each pitched channel's note-selection strategy (Scheme W — the shipped LFSR-driven walk — or Scheme E — Euclidean-gated onset timing with fixed-motif pitch selection) is determined by that channel's scheme-select bit in the currently-active `CHMIX_IDX` preset's mask data, independently of the other two pitched channels' scheme assignment (a "combination" is expressed at the ensemble level, never blended within one channel's own output). | ADS-100 §2/§3 (Domain Model: "Generation Scheme," "Scheme assignment"), ADR-0001 |
| FR-1190 | Switching `CHMIX_IDX` (Start) to a preset with a different scheme assignment for a pitched channel takes effect from that channel's next note-onset event, not instantaneously mid-note — consistent with how `CHMIX_IDX`'s channel-activity half (`FR-1000`/`FR-1010`, `IP-9010`) already behaves. | ADS-100 §5 (FR-candidate 2) |
| FR-1200 | A pitched channel running Scheme E gates its note onsets through the same Euclidean-pattern mechanism the noise channel already uses for density-driven hits (reusing `DENSITY_IDX`'s existing k-value selection), rather than a fixed per-tempo timer reload — producing a patterned, not continuously-regular, onset rhythm. | ADS-100 §3 (Domain Model: "Scheme E," onset timing), R202 |
| FR-1210 | A pitched channel running Scheme E selects its next scale-degree by stepping through a fixed, precomputed cyclic motif (a short sequence of scale-degree deltas), rather than an LFSR-picked random delta. | ADS-100 §3 (Domain Model: "Scheme E," pitch selection), R211, R216 |
| FR-1220 | Bad-zone detection (`FR-1080`/`FR-1090`/`FR-1100`) and autonomous recovery (`IP-0007`'s dissonant/stuck/overload-driven overrides) apply identically to a pitched channel regardless of which generation scheme (Scheme W or Scheme E) it is currently running — no scheme-specific bad-zone logic exists. | ADS-100 §2 ("both schemes still write through the same `BAD_ZONE_FLAGS`-driven... overrides"), §5 (FR-candidate 4) |
| FR-1230 | Each `CHMIX_IDX` preset value maps to a style data row specifying that style's target tempo index, density index, scale/mode index, and duty-cycle bias. | ADS-101 §2/§3/§5 (FR-candidate 1) |
| FR-1240 | Changing `CHMIX_IDX` (Start) applies its mapped style row's `SCALE_IDX` target value immediately on the press that changes the preset — not gated to the next note-onset event, unlike `CHMIX_IDX`'s channel-activity/scheme-select half (`FR-1190`). **`TEMPO_IDX`/`DENSITY_IDX`/the duty-cycle-bias state no longer apply immediately as of this amendment (2026-08-07, roadmap R8/`BL-0020`)** — those three fields now land on their target values via the blend mechanism `FR-1470`-`FR-1490` define, not on the Start press itself. Original text (2026-07-26, `ADS-101`) stated all four fields applied immediately; this requirement is amended in place rather than left standing beside a contradicting new FR, since both described the same trigger. | ADS-101 §2/§4/§5 (FR-candidate 2); amended per ADS-107 §5 (FR-candidate 4) |
| FR-1250 | The style data defines at least 3 named styles, each producing a tempo/density/scale/duty-cycle-bias combination that is audibly distinguishable, by content review, from every other defined style and from the default (preset-0) combination. | ADS-101 §3/§5 (FR-candidate 3) |
| FR-1260 | The style row mapped to `CHMIX_IDX` preset 0 (the boot/Select-reset preset) specifies exactly the tempo/density/scale/duty-cycle-bias combination ~~already shipped as~~ **held by** the default preset (`PRESET_TEMPO_IDX`/`PRESET_DENSITY_IDX`/`PRESET_SCALE_IDX`, duty bias 0) — selecting preset 0 introduces no change to the boot/reset **steering-index state**. **Clarified in place 2026-08-20** (`ADS-108` §11.5, `GDS-04` §4.1 amendment): this requirement is, and always was, the *fixed-point* rule — `STYLE_TABLE` row 0 must agree with the boot preset's own values, so that boot and Select-reset land identically. It is **not** a guarantee that preset 0 *sounds* the way it did on any particular prior build; that reading was released by the project owner on 2026-08-20 and is now actively contradicted by `FR-1580`. The two do not conflict: `FR-1580` changes how the engine derives notes from the steering indices, while `FR-1260` constrains the steering indices themselves, which are unchanged. `FR-1300`'s motif-variant-0 clause and `SONG_TABLE` phase 0 carry the same clarification by the same reasoning. **Parenthetical corrected 2026-08-21** (`ADR-0006`): this requirement's own subject is unchanged, but it calls `CHMIX_IDX` preset 0 "the boot/Select-reset preset." **Select no longer sets `CHMIX_IDX` at all** (`FR-1070` as amended), so preset 0 is now **the boot preset**. The requirement binds a table row to the boot preset's values and that binding is untouched — only the name of the event that reaches it has narrowed, exactly as `GDS-04` §4.1's second amendment records. | ADS-101 §5 (FR-candidate 4); GDS-04 §4.1 as amended 2026-08-20 **and 2026-08-21**; `ADR-0006` |
| FR-1270 | A Scheme-E channel's motif data is one of a small, fixed set of motif variants, each a complete sequence of absolute scale-degree targets for one full motif-step cycle; variant index 0 specifies exactly the motif sequence already shipped. | ADS-102 §3/§5 (FR-candidate 1) |
| FR-1280 | On the frame a Scheme-E channel's motif-step counter completes a full cycle (wraps back to its first step), the engine selects the motif variant that will be used for the following cycle via a weighted, non-uniform selection among the defined variants — with no button input required. | ADS-102 §2/§5 (FR-candidate 2) |
| FR-1290 | The motif-variant selection weighting favors the channel's currently-active variant over switching to a different one on most cycle-boundary selections, rather than choosing uniformly among all defined variants each time. | ADS-102 §3/§5 (FR-candidate 3) |
| FR-1300 | With motif-variant selection held at variant index 0 for an entire run, a Scheme-E channel's onset-by-onset pitch sequence is identical to the sequence produced before motif variants were introduced — no regression to the previously shipped single-motif behavior. **Unaffected by `ADR-0006` and confirmed so 2026-08-21**: this is a statement about `MOTIF_TABLE` row 0's *contents*, not about any event that selects it. `MOTIF_VARIANT_IDX` is derived generation state and continues to reset on Select exactly as before. Recorded because `FR-1260`'s own clarification names this requirement as carrying the same reasoning, and a reader should not have to re-derive that the naming change does not reach it. | ADS-102 §5 (FR-candidate 4); `ADR-0006` (checked, no change) |
| FR-1310 | The engine cycles autonomously through 4 named song-form phases (intro, build, peak, breakdown), looping back to the first after the last, with no button input required. | ADS-103 §5 (FR-candidate 1) |
| FR-1320 | On each song-form phase transition, the engine overwrites `TEMPO_IDX`/`DENSITY_IDX` to that phase's documented target values on the same tick as the transition, not gated to any future event. | ADS-103 §5 (FR-candidate 2) |
| FR-1330 | Bad-zone detection/recovery (`FR-1080`-`FR-1110`) and Scheme-E motif-variant selection (`FR-1270`-`FR-1300`) both operate identically regardless of the current song-form phase — no phase-specific logic exists in either mechanism. | ADS-103 §5 (FR-candidate 3) |
| FR-1340 | Over a sufficiently long run, all 4 song-form phases occur in their defined cyclic order with no hang or stall. | ADS-103 §5 (FR-candidate 4) |
| FR-1350 | The visualizer displays 5 indicators, one each for `TEMPO_IDX`, `OCTAVE_IDX`, `SCALE_IDX`, `DENSITY_IDX`, and `CHMIX_IDX`, each rendered as a filled-bar-height glyph proportional to that parameter's current index. | ADS-104 §5 (FR-candidate 1) |
| FR-1360 | Each of the 5 settings indicators updates within the same frame its underlying parameter changes, with no perceptible lag beyond the existing per-frame visualizer update cadence. | ADS-104 §5 (FR-candidate 2) |
| FR-1370 | The 5 settings indicators do not alter the existing channel-activity tiles' or calm/bad-zone palette's behavior — their addition is purely additive to the visualizer's existing output. | ADS-104 §5 (FR-candidate 3) |
| FR-1380 | At least one settings indicator demonstrably reflects a manual D-pad/A/B/Start-driven parameter change, confirmed by reading the relevant tilemap cell's pattern index after the corresponding button press. | ADS-104 §5 (FR-candidate 4) |
| FR-1390 | The engine maintains a derived `AROUSAL` value (range 0-15) that is a deterministic, monotonically non-decreasing function of `TEMPO_IDX` and `DENSITY_IDX` — increasing either input never decreases `AROUSAL`, holding the other constant. | ADS-105 §5 (FR-candidate 1) |
| FR-1400 | The engine maintains a derived `VALENCE` value (range 0-15) via a fixed, deterministic one-to-one mapping keyed by `SCALE_IDX` — each of the 4 scale/mode values maps to exactly one `VALENCE` output. | ADS-105 §5 (FR-candidate 2) |
| FR-1410 | `AROUSAL`/`VALENCE` are recomputed on every write to any of `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`, such that no more than one frame after any such write, both values reflect the post-write inputs. | ADS-105 §5 (FR-candidate 1/2, §2 trigger-site enumeration) |
| FR-1420 | `AROUSAL`/`VALENCE` hold correct values (matching the boot-preset steering indices) on the very first rendered/tested frame after boot, and hold correct values ~~(matching the restored preset indices)~~ **(matching the steering indices the listener currently has set, which a Select no longer changes — `FR-1070` as amended)** on the same frame a Select completes — neither is left stale pending a subsequent input edge. **Amended in place 2026-08-21** (`ADR-0006`): the requirement's *property* is unchanged — no stale-value grace period, ever — but its Select clause named the wrong reference values. Under the amended `FR-1070` the correct post-Select values are the listener's, and the recomputation on that frame therefore becomes a **no-op in the common case** rather than a restoration. It is retained rather than dropped precisely because it must stay a no-op: an implementation that recomputes from `PRESET_*` instead would reintroduce the defect this requirement exists to prevent, in the opposite direction. | ADS-105 §5 (FR-candidate 3/4); **amended:** `ADR-0006`, `FR-1070` |
| FR-1430 | The visualizer's non-bad-zone palette is selected by a table lookup keyed by `CHMIX_IDX`, applied every frame `BAD_ZONE_FLAGS` is clear — not only at the moment `CHMIX_IDX` changes. | ADS-106 §5 (FR-candidate 1) |
| FR-1440 | The `CHMIX_IDX`=0 row of that lookup table produces a palette identical to the calm palette already shipped — selecting preset 0 introduces no visual change from current shipped behavior. **Checked against `ADR-0006` 2026-08-21 and unchanged**: it constrains a table row keyed by `CHMIX_IDX`, and says nothing about which events set that index. One consequence worth naming rather than leaving implicit — since Select no longer returns `CHMIX_IDX` to 0, **a listener on a non-default preset now keeps that preset's theme across a Select**, which is the intended "settings survive" behaviour applied to the visualizer. | ADS-106 §5 (FR-candidate 2); `ADR-0006` (checked) |
| FR-1450 | Whenever `BAD_ZONE_FLAGS` is non-zero, the visualizer's palette is the existing bad-zone warning palette unconditionally, regardless of the current style-theme selection — the bad-zone override is absolute, not a blend or a priority tie-break. | ADS-106 §5 (FR-candidate 3) |
| FR-1460 | At least 3 non-default style-theme palettes each produce a color combination distinguishable, by content review, from the default theme and from each other. | ADS-106 §5 (FR-candidate 4) |
| FR-1470 | On a Start press that changes `CHMIX_IDX`, the engine begins a blend: it captures the current `TEMPO_IDX`/`DENSITY_IDX`/duty-cycle-bias values as the blend's starting point, and applies the newly selected style's `SCALE_IDX` value immediately (unchanged from `FR-1240`'s original guarantee for that one field). | ADS-107 §5 (FR-candidate 1) |
| FR-1480 | Following a blend's start, `TEMPO_IDX`/`DENSITY_IDX`/the duty-cycle-bias state step through exactly 4 discrete levels from their captured starting values to the newly selected style's target values, landing exactly on the target at the final step — never overshooting the target, never stalling short of it. | ADS-107 §5 (FR-candidate 2) |
| FR-1490 | A second Start press occurring while a blend is still in progress begins a new blend using the engine's current (possibly still-blending) `TEMPO_IDX`/`DENSITY_IDX`/duty-cycle-bias values as the new starting point — it does not wait for the prior blend to finish, and does not discard or queue the new selection. | ADS-107 §5 (FR-candidate 3) |
| FR-1500 | The engine maintains a single current-chord index (`CHORD_IDX`) in WRAM that every pitched channel (pulse A, pulse B, wave) reads at its own note-onset event; no pitched channel reads any other channel's own generation state. | ADS-108 §2.1/§3/D1/D2; R225 §3a/§5a **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — `_emit_chord_tone_addr`/the harmonic clock in `gen_tick_pa`'s onset branch (`music_engine.py`); every voice reads `CHORD_IDX`/`CHORD_TOGGLE`, none reads another channel's private state; verified by `T22.1`/`T22.2`; `VR-1140` §2 item 2 (7/7 transitions hand-derived) |
| FR-1510 | Chord membership is a ROM-resident table of scale degrees, one row per (scale, chord) combination, every entry already within the shipped 0-7 scale-degree range — no runtime arithmetic derives a chord tone from a root degree. | ADS-108 §2.2/D3; R225 §3g/§5b **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — `CHORD_TABLE` in `music_data.py` (48 B, asserted 0-7 at import); `_emit_chord_tone_addr` is table addressing only, no arithmetic derives a tone; verified by `T22.4`/`T22.6`; `VR-1150` §2 item 2 (400/400 hand-derived across all four scale blocks and the octave-0 floor) |
| FR-1520 | The current chord advances to a new chord selected via a weighted transition table indexed by 2 bits of the driving channel's own LFSR, over a vocabulary of exactly 4 chords (tonic, subdominant, dominant, submediant) whose transition weights bias toward returning to the tonic chord. | ADS-108 §2.3/D4; R225 §3a/§3b/§5c **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — `CHORD_TRANSITION` + the 2-LFSR-bit draw in the harmonic clock; verified by `T22.1`; `VR-1140` §2 item 2 |
| FR-1530 | The current chord advances once every 4 note-onset events of whichever pitched channel drives the harmonic clock, counted in onsets rather than in frames, so the harmonic rhythm tracks the currently-selected tempo automatically without a separate tempo-dependent recalculation. | ADS-108 §2.4/D5/D6; R225 §3c/§5c **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — `CHORD_ONSET_CTR`, decremented once per pulse-A onset, `N_CHORD_ONSETS = 4`; verified by `T22.2` |
| FR-1540 | A pitched channel running the harmonic-coordination scheme ("Scheme H") assigned the bass role sounds, on each note-onset event, the current chord's root degree or its fifth degree, alternating between the two on successive onsets, instead of an LFSR-selected scale-degree walk. | ADS-108 §2.6/D9 (Wave row); R225 §3d/§5d **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — the wave limb of `_emit_channel_gen`'s note-selection block (`CHORD_TOGGLE` bit0); verified by `T22.3` |
| FR-1550 | A pitched channel running Scheme H assigned the melody role sounds, on a strong note-onset event, one of the current chord's tones (selected by 2 bits of that channel's own LFSR); on a weak note-onset event, it instead steps by exactly one scale degree from its current degree, in the LFSR-selected direction. | ADS-108 §2.6/D9 (Pulse A row); R225 §3e/§5d **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — the melody limb (`MELODY_PICK` on strong onsets, `PASSING_TABLE` on weak); verified by `T22.4`/`T22.5` |
| FR-1560 | ~~A pitched channel running Scheme H assigned the harmony role sounds, on each note-onset event, a chord tone distinct from the melody role's currently-sounding chord tone, placed exactly one octave away from it rather than at a closer scale-degree separation.~~ **REWORDED IN PLACE 2026-08-21** (`BL-0126`, absorbed into `BL-0135`). It now reads: **the harmony voice sounds, on each note-onset event, the chord tone one slot above whichever chord tone the melody role most recently published to the shared context — so the two voices can never double into unison — and is placed one octave away from the melody voice.** The old wording described a **cross-channel read of another voice's private state**, which `ADS-108` D1 forbids outright (it needs inter-channel ordering guarantees) and which `FS-114` OQ2 therefore argued was impossible. `IP-1140` satisfied the requirement's *substance* by a mechanism the wording did not describe: the melody publishes its slot into the **shared** context (`CHORD_TOGGLE` bits2-3) and the harmony voice derives from that, so `FR-1500`'s no-private-reads rule holds. Unison is now structurally impossible (measured 0 %, against 28 % of pulse-A onsets before the fix). **The octave half remains unimplemented** — withheld by `IP-1140` deviation 1 for a per-frame cost reason that `IP-1150` has since removed; see `BL-0136`, which is the live entry for it. This reword makes the requirement describe the shipped mechanism and keeps the unbuilt half visible rather than quietly satisfied. | ADS-108 §2.6/D9 (Pulse B row); R225 §3g/§5d/§5f **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — the harmony limb via `SLOT_NEXT`, reading pulse A's published slot from `CHORD_TOGGLE` bits2-3; verified by `T22.6`; `VR-1140` §2 item 3 (99.6-99.8 % chord-tone on sounding pitch at four scale/octave combinations) |
| FR-1570 | ~~Per-pitched-channel generation-scheme selection (Scheme W, Scheme E, or Scheme H) is determined by a 2-bit field per channel in a parallel `SCHEME_TABLE`, keyed by the currently-active `CHMIX_IDX` preset, replacing the single scheme-select bit previously carried in spare bits of `CHMIX_MASKS` (`FR-1180`); for every one of the 8 existing `CHMIX_IDX` presets, the migrated table reproduces exactly the same per-channel Scheme W/Scheme E assignment the prior `CHMIX_MASKS` bits 4-6 encoding produced, including preset 6's wave-channel Scheme-E assignment.~~ **WITHDRAWN 2026-08-20 (`ADS-108` §11/D13, `ADR-0004` superseding `ADR-0003`) — never implemented.** This requirement existed only because harmonic coordination was a *third* scheme needing a second selection bit per channel, which it was only because preset 0's audible behavior was held immutable. That constraint is released (see `FR-1580`, and `GDS-04` §4.1's own dated amendment), and chord-derived note selection now replaces the default scheme's note selection in place. The reachable scheme set stays at two values — harmonized default, or Scheme E — so **`FR-1180`'s single scheme-select bit per channel remains in force, unamended**, and no `SCHEME_TABLE` and no `CHMIX_MASKS` migration exist to require. | ADS-108 §11/D13; ADR-0004 (supersedes ADR-0003); ADR-0001 (reaffirmed in full) |
| FR-1580 | ~~`CHMIX_IDX` preset 0 (the boot/Select-reset preset) assigns Scheme W to every pitched channel in `SCHEME_TABLE` — selecting preset 0 introduces no change to current boot/reset audible behavior.~~ **AMENDED IN PLACE 2026-08-20 — the requirement is reversed, not merely dropped** (`ADS-108` §11/D13, `ADR-0004`). It now reads: **`CHMIX_IDX` preset 0 (the boot/Select-reset preset) assigns the chord-derived (harmonically-coordinated) note-selection scheme to all three pitched channels, so that the ROM's default boot and Select-reset sound is harmonically coordinated.** The project owner released `GDS-04` §4.1's *historical-no-regression* reading of the index-0 invariant as self-imposed on 2026-08-20; the invariant's *fixed-point* half (index 0 equals the boot preset, so boot and Select-reset agree with each other) is untouched and is still satisfied here, because preset 0's scheme assignment and the boot preset's are the same thing. This absorbs **`CR-0005`** into the baseline. `FR-1590`'s bad-zone exception, previously scoped to "a Scheme-H channel," is correspondingly load-bearing at boot rather than only on a non-default preset. | ADS-108 §11/D13; ADR-0004; GDS-04 §4.1 (as amended 2026-08-20); user directive 2026-08-20 **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — chord-derived selection is the default path in `_emit_channel_gen`; no scheme flag gates it, so preset 0 is harmonized by construction; verified by the whole of `T22` running at boot defaults |
| FR-1590 | On a note-onset event where bad-zone dissonance recovery (`FR-1080`) would otherwise override a pitched channel's next scale-degree step, a Scheme-H channel's strong-onset chord-tone target (`FR-1550`) is not overridden; stuck-note recovery (`FR-1090`) and overload recovery (`FR-1100`) apply to a Scheme-H channel exactly as they do to any other channel, unaffected by this exception. | ADS-108 §2.6/§8 (D8); R225 §5e; R204 **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`, 2026-08-21) — the harmonized limbs jump past the dissonance-override block and land in the stuck block; verified by `T22`; `VR-1140` §2 item 4 (18/18 driven live) |
| FR-1600 | A pitched channel arpeggiates (`FR-1130`) **only while the note it is holding is itself a tone of the currently-sounding chord**. A note that is deliberately not a chord tone — notably the melody voice's weak-onset passing tone (`FR-1550`) — sustains at its own pitch for its whole duration instead. **Sustaining means the channel's frequency register continues to be written every frame with that note's own pitch**, so vibrato (`FR-1140`) and portamento (`FR-1150`) are unaffected; it never means the per-frame frequency write stops. | ADS-108 §12/D14 R-B, ADR-0005; FR-1550; BL-0127. **Implemented by `IP-1150`** — the forced row-0 gate in `_emit_channel_gen`'s onset branch; verified by `T23.3`/`T23.4`, and its non-regression half (the write still happens) by `T23.5` |
| FR-1610 | The arpeggio figure a channel plays is **selected per note-onset from a set of alternatives**, not fixed for the session. The set includes at least one alternative under which the note does not arpeggiate at all (i.e. `FR-1600`'s sustain is expressible as a member of the same set rather than as a separate mechanism), and the alternatives differ in **how many of the note's frames sound a pitch other than the onset pitch**, not only in the order of pitches — a set of permutations of one figure would still present a single figure. Each pitched channel's selection is drawn independently of the others'. | ADS-108 §12/D14 R-C, ADR-0005; R211 §8; BL-0127. **Implemented by `IP-1150`** — `ARP_PATTERNS`/`ARP_PATTERN_PICK` in `music_data.py`, drawn per onset from each channel's own LFSR; verified by `T23.6`/`T23.7`/`T23.8`/`T23.9` |
| FR-1620 | A change to the scale or octave parameter while a note is **already sounding** takes audible effect on that channel from its **next note-onset event**, not mid-note. The onset write itself always uses the parameter values current at that onset, so no control becomes less responsive than one note duration — the same next-onset granularity `FR-1190` already establishes for scheme changes. | ADS-108 §12.4 (cached-resolution consequence), ADR-0005; FR-1190. **Implemented by `IP-1150`** — `ARP_CACHE_PA`/`PB` resolved at onset; verified by `T23.10`/`T23.11` |
| FR-1630 | Boot and a Select each re-establish every pitched channel's arpeggio state, so no pitch material derived from before it can sound after it. **Strengthened in place 2026-08-21** (`ADR-0006`): the re-established state shall be resolved from the **steering-index values the listener currently has set**, never from the boot preset's. Until now the two were the same thing on the Select path, because Select reset the indices first; under the amended `FR-1070` they diverge, and an implementation that re-resolves against `PRESET_SCALE_IDX`/`PRESET_OCTAVE_IDX` would reseed the engine into pitch material from a scale the listener is not on — audibly wrong, and the exact defect class `VR-1130` found in `BLEND_STEP`, which is why this requirement exists at all. | ADS-108 §12.4, ADR-0005; VR-1130 (the `BLEND_STEP` uninitialized-state defect this requirement exists to prevent recurring). **Implemented by `IP-1150`** — `init_engine` calls `arp_resolve_{pa,pb}` with row 0 on both boot and Select; verified by `T23.12` |

**Deliberately out of scope for this delta** (`ADS-108` §2.7, recorded as Candidate Requirements below, not silently omitted): phrase structure/rests/cadence (`CR-0003`), harmonizing Scheme E's motif against the shared chord (`CR-0004`), ~~flipping `CHMIX_IDX` preset 0's default scheme assignment to Scheme H (`CR-0005`)~~, and re-rooting the `IP-1060` arpeggio on the shared chord under Scheme H (`CR-0006`).

> **Amended 2026-08-20** (`ADS-108` §11/D13, `ADR-0004`): **`CR-0005` is no longer out of scope — it is absorbed into the baseline as the amended `FR-1580`.** The default boot sound becoming harmonically coordinated *is* this increment's deliverable, not a later evidence-gated flip. `FR-1570` is withdrawn unimplemented in the same amendment. `CR-0003`/`CR-0004`/`CR-0006` are unchanged and remain out of scope.

## Non-Functional Requirements

| ID | Requirement | Traces to |
|---|---|---|
| NFR-1000 | The ROM builds to a fixed size with a valid header (correct logo, checksum, GBC compatibility flag) via `build_rom.py`, with no external assembler. | MSTR-001 C1/C3 |
| NFR-1010 | The per-frame VBlank ISR work (joypad edges + engine tick + visualizer update) completes within the VBlank-to-next-frame budget with no dropped frames, verified by driving the headless suite for an extended run (thousands of frames) with no hang/slowdown. **Caveat added 2026-07-26, corrected and widened 2026-07-31** (`BL-0060`/`BL-0069`, per [GDS-06 §2.2a](../architecture/06-non-functional-requirements.md)): the extended-run method remains the primary check but is **no longer sufficient on its own for any package adding per-frame work at all**. ~~`IP-1110` shipped a reproducible case where that frame's VRAM writes are dropped~~ — that case was falsified by direct measurement; no write is dropped and the harness cannot observe one (`R301` §3). The real finding is broader: `read_joypad`+`apply_input`+`engine_tick` consume ~9 of VBlank's 10 scanlines on **every** frame, idle included, leaving `update_visuals` about one scanline (`R101` §8.5). The original caveat named only the Select-reset frame and `update_visuals`, which is too narrow — no frame class is special. A stress run cannot detect this in any case: exhausting the VBlank window produces no hang, no slowdown and no dropped frame, the only three things the run watches for. Such a package states its per-frame cost impact explicitly; `IP-9030` v2 adds the falsifiable `LY` budget check this caveat has stood in for. **Implemented 2026-07-31**: `IP-9030`'s `VIS_ENTRY_LY` diagnostic + `test_rom.py`'s `T19` suite now supply exactly this check. | R100 cycle-budget note, GDS-06 §2.2a; `IP-9030`; `test_rom.py` `T19` |
| NFR-1020 | Every shipped behavior (FR-1000 through FR-1120) has at least one headless PyBoy test that drives a button sequence and asserts on sound-register and/or WRAM engine-state changes. | MSTR-001 C9 |
| NFR-1030 | Threshold/preset constants (tempo table, octave table, scale table, density table, channel-mix table, dissonance/stale/overload thresholds) live in one clearly-labeled data block in `music_engine.py`, tunable without touching generation logic. | GDS-03 §6 |
| NFR-1040 | Arpeggio/vibrato/portamento (FR-1130/FR-1140/FR-1150) each add bounded per-channel WRAM scratch state (a sub-tick/phase/glide counter per pitched channel) and bounded ROM-resident tables (an arpeggio-interval table, a vibrato depth/rate table) — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal). | MSTR-001 C2/§4, GDS-07 §6, strategic assumptions register A5 |
| NFR-1050 | Arpeggio/vibrato/portamento's added per-frame work (sub-tick cycling, phase-counter advance, glide-step computation) fits within the existing VBlank-tick budget (NFR-1010) — verified by the same extended-run headless stress-test method already used for the shipped engine, not by static cycle analysis (R101's own "no gap yet" conclusion still applies; see NFR-1010). | R101, R308, NFR-1010 |
| NFR-1060 | Scheme E's motif table(s) (ROM-resident, fixed at build time) and any per-channel "current motif step" scratch state add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-100 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1070 | Generation-scheme selection introduces no new WRAM control byte and no new input control — the scheme assignment for each pitched channel is derived from the existing `CHMIX_IDX`/`CHMIX_MASKS` mechanism (`FR-1000`/`FR-1010`, `IP-9010`) each tick, the same way other per-channel constants are already Python-level, not stored, state. | ADS-100 §6/§7, ADR-0001 |
| NFR-1080 | The style data table (one row per `CHMIX_IDX` preset) and its one new WRAM byte (duty-cycle bias) add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-101 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1090 | Style selection introduces no new input control — it is triggered by the existing `CHMIX_IDX`/Start mechanism (`FR-1060`) already in use for channel-activity/scheme-select, reusing the same preset index rather than requesting a distinct control. | ADS-101 §6/§7 |
| NFR-1100 | The motif-variant table(s) and the motif-variant-selection weighting table (both ROM-resident, fixed at build time) and any per-channel "current motif variant" scratch state add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-102 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1110 | Motif-variant selection introduces no new input control and no new WRAM control byte beyond the single variant-index scratch field — selection happens autonomously at motif-cycle boundaries, the same class of no-input-required behavior already established for bad-zone detection/recovery (`FR-1080`-`FR-1110`). | ADS-102 §6/§7 |
| NFR-1120 | The song-form phase table and its scratch state add bounded ROM/WRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-103 §6, MSTR-001 §4, GDS-07 §6 |
| NFR-1130 | The song-form state machine introduces no new input control — phase advancement happens autonomously on a per-frame timer, the same class of no-input-required behavior already established for bad-zone detection/recovery and motif-variant selection. | ADS-103 §6/§7 |
| NFR-1140 | The 8 new bar-height tile patterns and the 5 new settings-indicator tilemap cells add bounded ROM/VRAM — the total addition stays within the current 32KB single-bank budget (GDS-07 §6's headroom) and the measured tile-slot/tilemap headroom (`R104` §7-8), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-104 §6, MSTR-001 §4, GDS-07 §6, R104 §7-8 |
| NFR-1150 | The settings-indicator update (5 reads + 5 tilemap writes per frame) is VBlank-gated the same way every existing visualizer write already is, and its per-frame cost is comparable to the existing channel-activity update's own cost — verified against the existing VBlank-timing budget (NFR-1010), not by static cycle analysis alone. | ADS-104 §6, NFR-1010 |
| NFR-1160 | The settings-indicator feature introduces no new input control — it is a pure read-only display of existing tracked parameters, updated automatically as those parameters change under their own existing controls. | ADS-104 §6/§7 |
| NFR-1170 | The `AROUSAL`/`VALENCE` derivation adds **zero unconditional per-frame CPU cost** — it is invoked only from the write sites that can change its inputs (button-edge input steps, song-form phase transitions, style application, boot/Select-reset), never from an unconditional per-frame call in `engine_tick`'s own main body. Verified by call-graph inspection (which routines call the derivation, and whether that call is itself conditional/edge-triggered), not solely by the extended-run stress method (`NFR-1010`'s own caveat, `GDS-06` §2.2a, applies with full force here — a per-frame call cheap enough not to trip a stress-test would still violate this NFR's intent). | ADS-105 §6 (NFR-candidate 1), GDS-06 §2.2a, R101 §8.5 |
| NFR-1180 | `AROUSAL`/`VALENCE` (2 new WRAM bytes) add bounded WRAM — within the current 32KB single-bank budget's ample headroom (`GDS-07` §6), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5); the derivation's added cost at each trigger site is small relative to that site's own existing cost. | ADS-105 §6 (NFR-candidate 2/3), GDS-07 §6, MSTR-001 §4 |
| NFR-1190 | The style-theme palette lookup adds zero unconditional per-frame CPU cost beyond one indexed table read replacing one constant reference — the palette-write routine already runs every frame under the existing stateless re-render contract; this capability changes what it reads, not how often it runs or how much it does. | ADS-106 §6 (NFR-candidate 1), GDS-08 §5 |
| NFR-1200 | The new style-theme palette table adds bounded ROM — at most a handful of 8-byte palette rows, negligible against the measured free-ROM headroom (`R104` §7), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-106 §6 (NFR-candidate 2), R104 §7, MSTR-001 §4 |
| NFR-1210 | The blend mechanism's per-frame CPU cost is negligible once a blend is complete (one comparison and a return, no measurable addition to `engine_tick`'s existing per-frame cost); real interpolation arithmetic runs only during an active blend's brief window (at most 4 frames per Start press), a rare event relative to the per-frame budget `IP-9030` measured — costed and confirmed against that measured margin at implementation time, not assumed from this NFR alone. | ADS-107 §6 (NFR-candidate 1), GDS-06 §2.2a |
| NFR-1220 | The 7 new blend-state WRAM bytes (`BLEND_SRC_TEMPO`/`BLEND_SRC_DENSITY`/`BLEND_SRC_DUTY`/`BLEND_STEP`/`BLEND_DELTA_TEMPO`/`BLEND_DELTA_DENSITY`/`BLEND_DELTA_DUTY`) add bounded WRAM — within the current 32KB single-bank budget's ample headroom (`GDS-07` §6), with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-107 §6 (NFR-candidate 2), GDS-07 §6, MSTR-001 §4 |
| NFR-1230 | The blend's 4-discrete-step interpolation is independently, headlessly verifiable via WRAM-value assertion (the exact expected index at each of the 4 steps, computed by the same shift-based formula the implementation uses) — whether the resulting audible transition is musically coherent is explicitly a `09-content-review` judgment, never claimed by an automated check. | ADS-107 §6 (NFR-candidate 3) |
| NFR-1240 | Harmonic-coordination mechanisms (`FR-1500`-`FR-1590`) add no unconditional per-frame CPU cost — every instruction they add executes only inside a note-onset branch already taken by the existing generation routines, never from an unconditional call in `engine_tick`'s own main body. | ADS-108 §2.4/§7/D6; GDS-06 §2.2a; R101 §8.5; R225 §3h/§5c; NFR-1170 (same-class precedent) **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`) — every added instruction lives inside a note-onset branch that already existed; `engine_tick`'s `CALL` list is unchanged, confirmed by diff in `VR-1140` DoD 8, and corroborated behaviourally (`VIS_ENTRY_LY` 152-153 before and after) |
| NFR-1250 | The harmonic-coordination tables (chord table, chord transition table, ~~`SCHEME_TABLE`~~ — the last withdrawn 2026-08-20 with `FR-1570`) add bounded ROM — no more than approximately 100 bytes combined against the measured free-ROM headroom (`R104` §7) — with no bank-switching change (MSTR-001 §4 non-goal, strategic assumptions register A5). | ADS-108 §6 (NFR-candidate 2); R104 §7; MSTR-001 §4 **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`) — 48 + 16 + 4 + 4 = **72 bytes** against the ~100-byte allowance; no bank-switching change |
| NFR-1260 | `VIS_ENTRY_LY` (`IP-9030`'s per-frame VBlank budget diagnostic, `T19`) stays within its established `144`-`153` range on every frame class `T19` already covers, plus a chord-transition frame added as a new frame class to that same check. | ADS-108 §6 (NFR-candidate 3); IP-9030; GDS-06 §2.2a **Implemented by `IP-1140`** (`VERIFIED` via `VR-1140`) — verified by `T19`'s chord-transition frame class, and independently re-measured at **152-153 across 27 real chord-transition frames** in `VR-1140` §2 item 5 |
| NFR-1270 | Harmonic-coordination quality (`FR-1540`-`FR-1560`) is verified against vertical-interval statistics partitioned by onset metric strength (strong-beat sonorities measured separately from weak-beat sonorities) — an aggregate interval histogram across all onsets, undifferentiated by metric strength, is not an acceptable acceptance instrument for this capability, because a chord-tone/passing-tone melody deliberately sounds non-chord tones on weak beats. **Amended 2026-08-20** (`ADS-108` §11.6): because `FR-1580` now makes the harmonized path the *boot* path, the required comparison baseline is the immediately-preceding commit's ROM measured under identical conditions — not a non-default preset of the same build. **Amended again 2026-08-21** (`ADS-108` §12.6, `ADR-0005`; `BL-0128`): the statistics **shall be computed on SOUNDING pitch** — the pitch actually written to each channel's frequency register, after the arpeggio and after any other per-frame frequency rewrite — and **never on the scale degree the note-selection step chose**, which records *intent* and is overwritten before it sounds. This is a normative statement about the measurement basis, not advice. `IP-1140`'s recorded figures were taken on intent and are **overstated**: same build, same run, correct basis, strong-beat **25.7 %**, weak-beat **36.1 %**, aggregate **30.9 %** — not the recorded 12.2 %/30.6 %/21.5 %. Any package claiming this NFR states its measurement basis explicitly. **Amended a third time 2026-08-21** (`BL-0138`, `BL-0140`, both surfaced by `VR-1140`/`VR-1150`): a measurement basis is **three** choices, not one, and this requirement had normatively fixed only the first. Any figure claimed as acceptance evidence for `FR-1540`-`FR-1560` shall state all three, and shall use these values**Satisfied (not implemented) by `IP-1140` and `IP-1150`**, and independently re-measured at the PSG-write boundary by `VR-1140` §4 and `VR-1150` §4 across three builds |
  1. **Signal — the sounding pitch**, read at the channel's frequency register (or captured audio), never at `CUR_DEGREE_*` and never at `SEMI_*`. (Established 2026-08-21 above; `BL-0128`.)
  2. **Window — the note, not the onset frame.** A note runs from its own onset frame to the frame before that channel's next onset, and inherits the strong/weak parity recorded at its own onset. Sampling a single frame *at* the onset measures the **outgoing** note, because `FR-1150`'s portamento deliberately retriggers at the old degree and lets the per-frame frequency rewrite carry the glide — so an onset-frame sample compares the previous note against the current note's beat class. `VR-1140` measured the size of this error directly: **strong-beat 25.7 % / weak-beat 7.9 % on an onset-frame sample against 9.4 % / 29.9 % on the note window — same run, same build, the partition inverted.** (`BL-0138`.)
  3. **Scope — the channel set, named.** A figure computed over pulse A alone, over both pulse channels, or over all three pitched voices is a different figure, and the channels genuinely differ: pulse A carries `FR-1600`'s weak-onset forced hold *in addition to* the per-onset pattern draw, so it sustains materially more often than pulse B. `IP-1150` reported "47.1 % of notes do not arpeggiate" and `VR-1150` independently measured 37.8 %; **both are correct, of different channel sets**, and neither said which. (`BL-0140`.)

  These three are one requirement rather than three because they are one failure repeated: **`BL-0124`** sampled at the wrong moment within the frame, **`BL-0128`** sampled the wrong signal, **`BL-0138`** sampled the wrong frames, **`BL-0140`** sampled the wrong channels. Each was found only after a confident, plausible, wrong number had been banked. `GDS-04` §1.4's pitch/output-layer writer registry now makes the underlying question — *who writes this last?* — answerable from one table, which is the structural half of the same fix. | ADS-108 §6 (NFR-candidate 4)/D12/§11.6/§12.6; R225 §5f; R224 §7b; BL-0122; BL-0128 |
| NFR-1280 | The re-decided arpeggio's **unconditional per-frame CPU cost is strictly lower** than that of the mechanism it replaces — the work moves into note-onset branches that already exist (`NFR-1240`'s existing discipline), and what runs every frame does less than it does today. Verified by `VIS_ENTRY_LY` (`NFR-1260`/`T19`) across every frame class that check covers; **a regression is blocking, not absorbable** (`IP-9040`/`BL-0113` precedent). | ADS-108 §12/D14 R-D, ADR-0005; R101 §8.5; GDS-06 §2.2a; BL-0125. **Implemented by `IP-1150`** — all table arithmetic moved out of `_emit_arpeggio_tick` into the onset-time `_emit_arp_resolve`; verified by `T19.7`/`T19.8`, measured `VIS_ENTRY_LY` 152/153 → 151/152 on idle frames |

## Open items carried to feature decomposition

- Exact preset table **values** (tempo BPMs, octave ranges, scale note-sets, Euclidean k/n pairs,
  channel-mix masks) and threshold **constants** are authored as data at `05-feature-
  decomposition`/`06-feature-specification`/first implementation package — this requirements pass
  fixes behavior shape, not tuning values (consistent with GDS-03 §6's own deferral).
- FR-1130-FR-1160's exact parameters (vibrato depth/rate, portamento glide-frame count, which
  duty-cycle values and how they're selected) are likewise data decisions deferred to feature
  decomposition/spec/implementation, same convention. **Amended 2026-08-21:** the arpeggio's own
  parameter — "which 2-3 harmonic intervals" — is no longer a free data decision. `FR-1130` as
  amended fixes the *source* of those pitches (tones of the currently-sounding shared chord); what
  remains deferred as data is the contents of `FR-1610`'s alternative-figure set, subject to that
  requirement's two structural constraints.

- FR-1180-FR-1220's exact parameters (the scheme-select bit position within `CHMIX_MASKS`'s spare
  bits 4-6, Scheme E's motif table contents/count, which `CHMIX_IDX` presets assign which scheme
  to which channel) are likewise data/preset decisions deferred to feature decomposition/spec/
  implementation — this pass fixes behavior shape (ADS-100's own "shape, not values" framing),
  same convention as every prior preset-table deferral.
- FR-1230-FR-1260's exact parameters (which 3+ styles map to which `CHMIX_IDX` presets, the exact
  tempo/density/scale/duty-bias values each style targets, the `DUTY_BIAS`-combination rule
  `BL-0038` flagged) are likewise data/implementation decisions deferred to feature decomposition/
  spec/implementation — `ADS-101` §3 already names 3 concrete candidate styles (Techno/Chiptune-
  Driving, Ambient/Lo-Fi, Holiday) as the recommended starting data, not yet baselined as
  requirement text since specific preset-table values are this project's established deferral
  point, same convention as every prior preset-table addition.
- FR-1270-FR-1300's exact parameters (the concrete `N_VARIANTS` count, the motif-variant table
  contents, and the weighting table's precise retention-vs-switch ratio, `BL-0042`) are likewise
  data/implementation decisions deferred to feature decomposition/spec/implementation — `ADS-102`
  §3 proposes 4 variants (variant 0 the existing shipped sequence) as a starting point, not yet
  baselined as requirement text, same convention as every prior preset/table-value deferral.
- FR-1310-FR-1340's exact parameters (each phase's target `TEMPO_IDX`/`DENSITY_IDX` values and
  duration) are likewise data/implementation decisions deferred to feature decomposition/spec/
  implementation — `ADS-103` explicitly leaves these as first-guess placeholders, same
  `BL-0005`-class deferral as every prior preset/table-value addition.
- FR-1350-FR-1380's exact parameters (the precise bar-tile pixel design, on-screen tilemap
  placement of the 5 new cells, and whether a static in-ROM control legend is ever added — `ADS-
  104`'s own §9 Open Questions) are likewise implementation/content decisions deferred to feature
  decomposition/spec/implementation, same `BL-0005`-class deferral as every prior visual/preset-
  value addition. `ADS-104`'s explicitly out-of-v1-scope follow-on (scheme/style/motif-variant/
  song-form-phase indicators reusing the same bar-tile mechanism) is not baselined here — it is a
  named future extension, not a requirement of this delta.
- FR-1500-FR-1590's exact parameters (the concrete `CHORD_TABLE` degree contents per scale
  including pentatonic's idiomatic sonorities, the `CHORD_TRANSITION` weight values, N=4 onsets
  per chord, and which `CHMIX_IDX` presets 1-7 assign Scheme H to which channels) are likewise
  data/preset decisions deferred to feature decomposition/spec/implementation — `ADS-108` §2.2/
  §2.3/§9 OQ3/OQ4 names these as first-guess placeholders (`BL-0005` class) or content-authoring
  judgment calls, not yet baselined as requirement text, same convention as every prior
  preset/table-value deferral.

## Candidate Requirements

Untraceable-to-a-source or explicitly-unbuilt statements, **excluded from the numbered baseline**.

| ID | Candidate requirement | Why it is not baselined |
|---|---|---|
| CR-0001 | The visualizer contains at least one element whose *motion or animation timing follows the generated beat* (tempo-synced motion), distinct from displaying the tempo setting as a static value. | **Never built, never scheduled.** Split out of `FR-1120` on 2026-07-26 (`BL-0016`) per [GDS-08 §7](../architecture/08-presentation-architecture.md)'s three-part resolution. `IP-0006`'s own package doc named "tempo-synced motion" as its explicit non-scope; nothing since has built it. Kept as a candidate rather than deleted because it is a real and reasonable future capability (`R223` treats pitch/rhythm-driven visual mapping as well-grounded) — it simply has never been required of the shipped system, and `FR-1120` should not have implied it was. |
| CR-0002 | `AROUSAL`'s derivation additionally incorporates `CHMIX_IDX`-derived active-channel count as a third input (alongside `TEMPO_IDX`/`DENSITY_IDX`), per `R221`'s observation that active-channel count is itself a direct arousal-axis lever in the literature. | **Deliberately excluded from v1's baseline** (`BL-0080`, per `ADS-105` §9 OQ3). `FR-1390` is fully satisfiable, and citation-clean, from `TEMPO_IDX`/`DENSITY_IDX` alone — the same minimal-baseline discipline `ADS-105` already applied to excluding `DISSONANCE_SCORE` from `VALENCE`. Adding a third input widens the surface a v1 acceptance test must cover for a marginal, not-yet-requested richness gain. Kept as a candidate rather than dropped because `ADS-105` §2 confirms the architectural cost of adding it later is low — the trigger-site plumbing for a `CHMIX_IDX` change is already shared with `AROUSAL`/`VALENCE`'s other recompute triggers, so promoting this candidate later would not require new call sites, only a wider formula. |
| CR-0003 | Phrase structure, rests, and cadence over the shared chord context: a phrase-position counter (`PHRASE_POS`) forces `CHORD_IDX` to the dominant chord at a half-cadence boundary and to the tonic chord at a perfect-authentic-cadence boundary, and a note-onset event may skip its trigger write entirely (a rest) at a phrase-final position. | **Never built, explicitly reserved as increment 2's shape, not this increment's.** `ADS-108` §2.7/D10 names the mechanism precisely (a `PHRASE_POS` byte at `0xC07A`, two forced-`CHORD_IDX`-value cadence constraints) specifically so a future pass does not re-litigate the design, but defers it because it multiplies the verification surface and the three per-voice rules (`FR-1540`-`FR-1560`) are independently audible without it. Kept as a candidate rather than dropped for the same reversibility reasoning `CR-0001`/`CR-0002` already established. |
| CR-0004 | A Scheme-E channel's motif-derived scale degree (`FR-1210`) is transposed by the current chord's root degree, so a Scheme-E channel sounds harmonically coordinated with any concurrently-sounding Scheme-H channel rather than ignoring the shared chord context entirely. | **Never built, explicitly deferred to increment 2** (`ADS-108` §8 R3, §9 OQ6). Increment 1 leaves Scheme E harmonically uncoordinated by design — `ADS-108` names the eventual mechanism ("a single `ADD` at the motif lookup, not a redesign") but does not commit to building it this increment, and whether it is ever built depends on a `03-architecture-design-synthesis` scoping decision not yet made. Increment 1's own preset set is expected to pair Scheme-H channels together to sidestep the gap rather than build this candidate. |
| CR-0005 | ~~`CHMIX_IDX` preset 0 (the boot/Select-reset preset) assigns Scheme H, not Scheme W, to at least one pitched channel — i.e. the ROM's default boot sound becomes harmonically coordinated rather than the three-independent-walks behavior shipped today.~~ **PROMOTED TO THE BASELINE 2026-08-20 — this is no longer a candidate.** See the amended **`FR-1580`**. | **Promoted, not dropped.** This candidate's own stated gate was *"the user's own call amending the index-0 invariant."* That call was made on 2026-08-20 — the project owner explicitly rejected the preset-0 standard as arbitrary and self-imposed and directed the pipeline toward audible improvement soonest. `ADS-108` §11/D13 and `ADR-0004` record the architecture re-decision; `GDS-04` §4.1 records the invariant's narrowing (the fixed-point half stands, the historical-no-regression half is released). The second half of the gate — evidence that the harmonized result actually sounds better — is **not** waived: it moves from a precondition on scheduling to an acceptance obligation on the delivered package, carried by `NFR-1270`'s strong-beat-partitioned measurement and `09-content-review`'s holistic dimension (`R224` §7a). Row retained rather than deleted so the promotion is visible in the same place the exclusion was recorded. |
| CR-0006 | ~~Under Scheme H, the `IP-1060` arpeggio (`ARPEGGIO_OFFSETS`) is re-rooted so its stacked-thirds pattern starts from the shared chord's root rather than from whichever chord tone the channel's `CUR_DEGREE` currently holds.~~ **ABSORBED INTO THE BASELINE 2026-08-21 — no longer a candidate.** See the amended **`FR-1130`** plus the new `FR-1600`/`FR-1610`. | **Analyzed and deliberately not built this increment** (`ADS-108` §8 R4). `ADS-108` finds the un-re-rooted behavior benign for increment 1 (stacked diatonic thirds from any triad tone land on tones of the same or a closely related triad) and explicitly declines to fund a table read on the arpeggio sub-tick — a per-frame-adjacent cost `NFR-1240` will not fund without measurement. `09-content-review` is named as the mechanism that would surface whether this candidate is actually needed. |

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-07-22 | Added FR-1130 (arpeggio), FR-1140 (vibrato), FR-1150 (portamento), FR-1160 (duty-cycle variation), FR-1170 (percussion-synthesis trace, no new behavior), NFR-1040 (ROM/WRAM budget), NFR-1050 (per-frame timing budget). Delta update per `BL-0024` (user-directed R216 sound-design-techniques implementation). No existing FR/NFR changed. | `BL-0024`, grounded in `R216`. |
| 2026-07-25 | Added FR-1180 (scheme-select determines note-selection strategy), FR-1190 (scheme switch takes effect at next onset, mirroring `IP-9010`'s activity-mask behavior), FR-1200 (Scheme E onset timing reuses the Euclidean-pattern mechanism), FR-1210 (Scheme E pitch selection via a fixed motif), FR-1220 (bad-zone detection/recovery is scheme-agnostic), NFR-1060 (ROM/WRAM budget), NFR-1070 (no new WRAM control byte/input control). Delta update formalizing `ADS-100` §5's candidate FRs per `BL-0020`, now that `IP-9010` has shipped with the bit layout `ADR-0001`'s contingency assumed (bits 0-3 channel-active, confirmed against the actual shipped `CHMIX_MASKS` — no re-check needed). No existing FR/NFR changed. | `BL-0020`, grounded in `ADS-100`/`ADR-0001`. |
| 2026-07-26 | Added FR-1230 (`CHMIX_IDX` preset maps to a style data row), FR-1240 (style values applied immediately, not gated to next onset — the one behavioral contrast with `FR-1190`'s scheme-select timing), FR-1250 (at least 3 audibly-distinct styles), FR-1260 (preset-0 style matches shipped default, no regression), NFR-1080 (ROM/WRAM budget), NFR-1090 (no new input control). Delta update formalizing `ADS-101` §5/§6's candidate FRs/NFRs for R5 (Genre-Aware Style Presets). No existing FR/NFR changed. | Roadmap R5, grounded in `ADS-101`. |
| 2026-07-26 | Added FR-1270 (motif data is a small fixed set of variants, variant 0 matches the shipped sequence), FR-1280 (weighted variant selection at motif-cycle boundaries, no input required), FR-1290 (weighting favors retaining the current variant), FR-1300 (variant 0 held throughout a run reproduces pre-change behavior exactly, no regression), NFR-1100 (ROM/WRAM budget), NFR-1110 (no new input control/WRAM control byte beyond the variant-index field). Delta update formalizing `ADS-102` §5/§6's candidate FRs/NFRs for `BL-0010`'s motif-recurrence half. No existing FR/NFR changed. | `BL-0010`, grounded in `ADS-102`. |
| 2026-07-26 | Added FR-1310 (autonomous 4-phase song-form cycle), FR-1320 (phase transition overwrites tempo/density immediately), FR-1330 (bad-zone/motif-variant mechanisms are phase-agnostic), FR-1340 (all 4 phases occur in cyclic order over a long run), NFR-1120 (ROM/WRAM budget), NFR-1130 (no new input control). Delta update formalizing `ADS-103` §5/§6's candidate FRs/NFRs for roadmap R6 (song-form half of `BL-0010`). No existing FR/NFR changed. | Roadmap R6, grounded in `ADS-103`. |
| 2026-07-26 | **Corrective/precision pass — no new baseline IDs.** Reworded `FR-1120` to drop its tempo claim (`BL-0016`): the tempo *setting* display is real but owned by `FR-1350`, and tempo-*synced motion* was never built — split out as new `CR-0001` in a new **Candidate Requirements** section. Added a caveat to `NFR-1010` recording that its extended-run method is no longer sufficient alone for packages touching the Select-reset frame or `update_visuals` (`BL-0060`, per GDS-06 §2.2). Updated `FR-1120`'s Traces-to from "GDS-08 (pending)" to the now-authored GDS-08 §2/§3. Re-labelled `docs/requirements/INDEX.md`'s two `⛔ Planned` rows as deliberate deviations (`BL-0068`, per GDS-10 §3.1). **`BL-0040` investigated and found NOT to be a requirements defect** — see this pass's Delta Review. | `BL-0016`/`BL-0040`/`BL-0060`/`BL-0068`, grounded in the newly-authored GDS-06/GDS-08/GDS-10. |
| 2026-07-26 | Added FR-1350 (5 settings indicators, bar-height glyph per parameter), FR-1360 (each indicator updates same-frame as its parameter), FR-1370 (purely additive, no change to existing channel-activity/palette behavior), FR-1380 (at least one indicator demonstrably live-reflects a manual button change), NFR-1140 (ROM/VRAM budget), NFR-1150 (VBlank-gated, comparable per-frame cost), NFR-1160 (no new input control). Delta update formalizing `ADS-104` §5/§6's candidate FRs/NFRs for `BL-0051` (settings & control visibility). No existing FR/NFR changed. | `BL-0051`, grounded in `ADS-104`. |
| 2026-07-31 | Added FR-1390 (`AROUSAL` is a monotonic function of `TEMPO_IDX`/`DENSITY_IDX`), FR-1400 (`VALENCE` is a fixed one-to-one mapping keyed by `SCALE_IDX`), FR-1410 (both recomputed within one frame of any input write), FR-1420 (both correct on the first frame after boot and on a Select-reset's own frame), NFR-1170 (zero unconditional per-frame CPU cost — the load-bearing NFR, a direct response to `IP-9030`'s VBlank-budget measurement), NFR-1180 (bounded WRAM budget, bounded per-trigger-site cost). Delta update formalizing `ADS-105` §5/§6's candidate FRs/NFRs for roadmap R7 (Emotional/Energy Layer). Resolved `BL-0081` (exact derivation formulas) by keeping the baseline at the behavioral level — monotonicity and a fixed mapping, not literal lookup-table values, per this skill's own "no byte-level detail in requirements" rule; exact table contents are `07-implementation-planning`'s to propose. Resolved `BL-0080` (whether `AROUSAL` includes `CHMIX_IDX`-derived active-channel count) by explicitly scoping it out as new **`CR-0002`**, not baselined. No existing FR/NFR changed. | Roadmap R7, grounded in `ADS-105`. |
| 2026-07-31 | Added FR-1430 (style-theme palette selected by a `CHMIX_IDX`-keyed lookup, applied every frame `BAD_ZONE_FLAGS` is clear), FR-1440 (preset-0 theme matches the shipped calm palette exactly, no regression), FR-1450 (bad-zone palette unconditionally overrides the style theme), FR-1460 (at least 3 distinguishable non-default themes), NFR-1190 (zero unconditional per-frame CPU cost beyond one indexed read replacing one constant), NFR-1200 (bounded ROM budget, cited to `R104` §7's actual measured headroom). Delta update formalizing `ADS-106` §5/§6's candidate FRs/NFRs for roadmap R9 (Visual Evolution & Audio-Visual Synchronization), **scoped to `RM-9001` (style-reactive palette) only** — `RM-9002` (mood-reactive, `IP-1120`'s `AROUSAL`/`VALENCE` as first consumer) and `RM-9003` (accessibility) are explicitly out of scope for this pass, per `ADS-106`'s own deferral decisions, and carry no FR/NFR here. No existing FR/NFR changed. | Roadmap R9, grounded in `ADS-106`. |
| 2026-08-07 | Added FR-1470 (blend begins on Start press: capture start values, `SCALE_IDX` applies immediately), FR-1480 (4-discrete-step interpolation landing exactly on target), FR-1490 (a second Start press mid-blend restarts from current values, never queues), NFR-1210 (negligible steady-state per-frame cost), NFR-1220 (bounded WRAM budget, 4 new bytes), NFR-1230 (WRAM-assertion-testable; audible-quality judgment explicitly deferred to `09-content-review`). Delta update formalizing `ADS-107` §5/§6's candidate FRs/NFRs for roadmap R8 (Genre Blending). **`FR-1240` amended in place** (not left standing beside a contradicting new FR): its `TEMPO_IDX`/`DENSITY_IDX`/duty-cycle-bias instant-apply guarantee is superseded by `FR-1470`-`FR-1490`'s blend mechanism — only the `SCALE_IDX` half of the original guarantee survives unchanged. Checked for other requirements citing `FR-1240`'s original guarantee (see this pass's own Delta Review); none found beyond descriptive prose in prior passes' own historical Delta Reviews, which are left as accurate records of their own time rather than retroactively edited. | Roadmap R8/`BL-0020`, grounded in `ADS-107`. |
| 2026-08-20 | Added FR-1500 (shared `CHORD_IDX` context), FR-1510 (chord table, no runtime arithmetic), FR-1520 (weighted 4-chord tonic-biased transition), FR-1530 (onset-counted harmonic rhythm, N=4), FR-1540 (Scheme-H wave = root/fifth), FR-1550 (Scheme-H pulse A = chord tone strong / step weak), FR-1560 (Scheme-H pulse B = chord tone an octave apart), FR-1570 (`CHMIX_MASKS`→`SCHEME_TABLE` migration, exact non-regression), FR-1580 (preset 0 stays all-Scheme-W), FR-1590 (bad-zone recovery does not override a Scheme-H strong-onset chord tone), NFR-1240 (zero unconditional per-frame cost), NFR-1250 (bounded ROM budget, ~100 bytes), NFR-1260 (`VIS_ENTRY_LY`/`T19` covers a chord-transition frame class), NFR-1270 (acceptance verified on strong-beat-partitioned intervals, not the aggregate histogram). Added CR-0003 (phrase/rest/cadence), CR-0004 (Scheme-E harmonization), CR-0005 (default-preset flip to Scheme H), CR-0006 (re-rooting the `IP-1060` arpeggio) — all explicitly named as increment-2/deferred scope, not silently omitted. Delta update formalizing `ADS-108` §5/§6's candidate FRs/NFRs (D1-D12) for `BL-0119`'s harmonic-coordination mechanism, harvested per `00-intake`'s own filing this session (`BL-0121`/`BL-0122`/`BL-0123`). No existing FR/NFR changed. | `BL-0119`, grounded in `ADS-108`/`R225`/`ADR-0003`. |
| 2026-08-20 (second pass, same day) | **Amendment pass — no new baseline IDs; four existing statements changed in place rather than left contradicting new architecture.** `FR-1570` **withdrawn unimplemented** (no `SCHEME_TABLE`, no `CHMIX_MASKS` migration — `FR-1180`'s single scheme-select bit per channel stands unamended). `FR-1580` **reversed in place**: preset 0 now assigns the chord-derived scheme to all three pitched channels, i.e. the default boot sound becomes harmonically coordinated — this absorbs `CR-0005`, which is marked **promoted to the baseline** rather than deleted. `FR-1260` **clarified in place**: it is the *fixed-point* rule (row 0 agrees with the boot preset's steering-index values), never a guarantee about how any prior build sounded; `FR-1300`/`SONG_TABLE` phase 0 carry the same clarification. `NFR-1250` narrowed (`SCHEME_TABLE`'s 8 bytes removed from its budget); `NFR-1270` amended to name the prior commit's ROM as the comparison baseline, since the change is now audible at boot. Driven by `ADS-108` §11 (D13) and `ADR-0004` (superseding `ADR-0003` before implementation), which in turn follow the project owner's explicit 2026-08-20 release of `GDS-04` §4.1's historical-no-regression reading of the index-0 invariant. | User directive 2026-08-20; `ADS-108` §11/D13; `ADR-0004`; `GDS-04` §4.1 amendment; `BL-0119`/`BL-0123`. |
| 2026-08-21 | **Amendment + addition pass, driven by a listening report.** `FR-1130` **amended in place** — the arpeggio's pitches now come from the currently-sounding shared chord (`FR-1500`), not from a chord implied by the channel's own degree; the original wording became *wrong*, not merely stale, the moment `FR-1500` was added, and directed the engine to stack a second differently-rooted triad on its own harmony (measured: 46.4 % of sounding pulse frames were chord tones; strong-beat harsh intervals 25.7 % on sounding pitch vs 12.0 % on selected notes). Added `FR-1600` (arpeggiate only a chord tone — a passing tone sustains, and *sustaining still writes the frequency register every frame*, so vibrato/portamento survive), `FR-1610` (figure drawn per onset from a set of alternatives including a no-arpeggio member, alternatives differing in rhythmic surface not only pitch order), `FR-1620` (a scale/octave change during an already-sounding note lands at the next onset), `FR-1630` (boot and Select re-establish arpeggio state). `NFR-1270` **amended in place a second time**: the measurement basis is normatively **sounding pitch**, never the selected degree — `IP-1140`'s recorded figures were taken on intent and are overstated. Added `NFR-1280` (the arpeggio's unconditional per-frame cost must strictly *decrease*; `VIS_ENTRY_LY` verifies; a regression is blocking). `CR-0006` **absorbed into the baseline**, marked rather than deleted. | `BL-0127`/`BL-0128`/`BL-0125`, grounded in `ADS-108` §12/D14 and `ADR-0005`. |
| 2026-08-21 (second pass, same day) | **Amendment pass — no new baseline IDs; the Select control is redefined and four measurement/traceability defects are closed.** `FR-1070` **amended in place** (`ADR-0006`): Select becomes a **reroll** — reseed every pitched channel's melodic stream, clear the bad-zone fields, and leave `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX`/`DUTY_BIAS` at the listener's values, **by every write path** (the Delta Review's D1 records that the reset path writes `TEMPO_IDX`/`DENSITY_IDX` twice, so "remove five writes" is a wrong reading of this requirement). `FR-1420` **amended in place** — its Select clause named the restored preset indices, which no longer exist as an event; the no-stale-value property is unchanged and the Select-frame recomputation becomes a deliberate no-op. `FR-1630` **strengthened in place** — the arpeggio caches must re-resolve from the **listener's** current scale/octave, not the preset's, which were the same thing only while Select reset the indices first. `FR-1260`/`FR-1300`/`FR-1440`'s "boot/Select-reset preset" parentheticals corrected to "boot preset" (bindings unchanged; only the name of the event that reaches index 0 narrows). `FR-1560` **reworded in place** (`BL-0126`) to describe the shipped shared-context mechanism instead of the cross-channel read `ADS-108` D1 forbids — with its still-unbuilt octave half left visible via `BL-0136`. `NFR-1270` **amended a third time** (`BL-0138`/`BL-0140`): a measurement basis is **signal, window and scope**, all three stated, with the note (not the onset frame) as the window and the channel set named. Forward traceability filled in for `FR-1500`-`FR-1590`/`NFR-1240`-`NFR-1270` (`BL-0135`), and the 2026-08-21 Delta Review's own stale "`UNASSIGNED` for `FR-1600`-`FR-1630`" line corrected (`BL-0139`). | `ADR-0006`; user directive 2026-08-21; `BL-0126`/`BL-0135`/`BL-0138`/`BL-0139`/`BL-0140`; `VR-1140`/`VR-1150`. |

## Delta Review — 2026-07-25 (`FR-1180`-`FR-1220`, `NFR-1060`/`1070`)

Reviewed this delta only (per the skill's own "not a wholesale regeneration" convention) for
duplicates, conflicts, ambiguities, missing requirements, impossible requirements, architecture
violations, and missing traceability:

- **No duplicate or conflicting requirement.** `FR-1180`-`FR-1220` introduce a genuinely new
  concept (generation scheme) orthogonal to every existing FR — none of `FR-1000`-`FR-1170`
  presumes a single note-selection strategy in a way this delta contradicts; `FR-1220` explicitly
  confirms `FR-1080`/`FR-1090`/`FR-1100` (bad-zone detection) is unaffected, closing the one place
  a conflict could plausibly have existed.
- **No architecture violation.** Each FR traces directly to `ADS-100`/`ADR-0001`; the ADR's own
  contingency (`IP-9010`'s bit layout) is satisfied — `IP-9010` shipped with bits 0-3 as
  channel-active, exactly as `ADS-100`/`ADR-0001` assumed, confirmed by re-reading
  `IP-9010-channel-mix-gating.md` and the shipped `CHMIX_MASKS` table together.
- **No missing requirement.** `ADS-100` §5/§6's four FR-candidates and two NFR-candidates all
  became baseline requirements (`FR-1200`/`FR-1210` split from one candidate for atomicity, per
  the skill's own "split ands" rule) — none silently dropped.
- **Traceability:** every new ID's Source Documents column cites `ADS-100`'s specific section (and
  `ADR-0001` where the ADR itself is the direct source, e.g. `FR-1180`'s scheme-selection
  mechanism). No candidate needed — every statement in `ADS-100` §5/§6 was traceable to the
  document itself, not invented here.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — no `FS-xxx`, Implementation
  Package, or test exists yet for this feature; correctly left honest rather than guessed. This is
  the expected state for a requirements-only delta pass, matching every prior FR addition's own
  initial state before `05`/`06`/`07`/`08` picked it up.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1070`-equivalent catalog row once picked up.

**Known pre-existing gap (not introduced by this update):** this project's first requirements
pass (run #1) authored FR/NFR content directly into this single file rather than the four
separate deliverables `04-requirements-engineering`'s own workflow specifies (a dedicated
`02-non-functional-requirements.md`, `03-requirements-review.md`, and
`04-requirements-traceability-matrix.md` were never authored). This delta update follows the
established single-file convention rather than unilaterally restructuring — the split is a
`refactor`-type backlog candidate for a future pass, not addressed here.

## Delta Review — 2026-07-26 (`FR-1230`-`FR-1260`, `NFR-1080`/`1090`)

Reviewed this delta only, same "not a wholesale regeneration" convention as the prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1230`-`FR-1260` introduce a genuinely new
  concept (style-driven coordinated parameter overwrite) orthogonal to every existing FR. The one
  place a conflict could plausibly arise — `FR-1240`'s "applied immediately" vs. `FR-1190`'s
  "takes effect at next onset" for the *same* `CHMIX_IDX` press — is not actually a conflict: the
  two govern different state (`FR-1190` governs scheme/channel-activity, both read per-onset by
  the generation routines already; `FR-1240` governs `TEMPO_IDX`/`DENSITY_IDX`/`SCALE_IDX`/duty
  bias, all read per-tick by existing code exactly like a manual D-pad/A/B change already is) —
  the timing difference is a deliberate, cited design decision (`ADS-101`'s own Decision Log), not
  an oversight, and is called out explicitly in `FR-1240`'s own text so a future reader isn't left
  to infer it.
- **No architecture violation.** Each FR/NFR traces directly to `ADS-101`; no ADR is directly
  implicated (this feature didn't need a new ADR — `ADS-101`'s own Decision Log carries its
  binding decisions).
- **No missing requirement.** `ADS-101` §5/§6's four FR-candidates and (implicitly) two
  NFR-candidates all became baseline requirements — none silently dropped. `ADS-101`'s Open
  Questions (`DUTY_BIAS` combination rule, Celtic/Holiday-motion follow-ups) are correctly *not*
  baselined here — they're implementation-level/future-scope decisions, not requirements gaps,
  already tracked as `BL-0038`/`BL-0039`.
- **Traceability:** every new ID's Source Documents column cites `ADS-101`'s specific section. No
  candidate needed — every statement in `ADS-101` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for R5.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1080`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (`FR-1270`-`FR-1300`, `NFR-1100`/`1110`)

Reviewed this delta only, same "not a wholesale regeneration" convention as every prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1270`-`FR-1300` introduce a genuinely new
  concept (motif *variant* selection) layered on top of, not contradicting, `FR-1210` (Scheme E
  selects its next scale degree by stepping through a fixed cyclic motif) — `FR-1210` still
  correctly describes the per-step lookup behavior; `FR-1270`-`FR-1300` add that *which* motif
  sequence is being stepped through can now change at cycle boundaries. No existing FR is
  weakened or overridden; `FR-1210`'s text needed no edit since it never asserted there is only
  ever one possible motif sequence, only that stepping is cyclic and fixed-per-cycle.
- **No architecture violation.** Each FR/NFR traces directly to `ADS-102`; no ADR is directly
  implicated (this feature didn't need a new ADR — `ADS-102`'s own Decision Log carries its
  binding decisions, the same pattern `ADS-101` already established).
- **No missing requirement.** `ADS-102` §5/§6's four FR-candidates and two NFR-candidates all
  became baseline requirements — none silently dropped. `ADS-102`'s Open Questions (concrete
  `N_VARIANTS`/weighting-curve values, per-channel `MOTIF_VARIANT_IDX` scoping, variant-authoring
  method, future R6 integration) are correctly *not* baselined here — implementation-level/
  future-scope decisions, not requirements gaps, already tracked as `BL-0042`/`BL-0043`.
- **Traceability:** every new ID's Source Documents column cites `ADS-102`'s specific section. No
  candidate needed — every statement in `ADS-102` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for this motif-recurrence work.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1090`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (`FR-1310`-`FR-1340`, `NFR-1120`/`1130`)

Reviewed this delta only, same "not a wholesale regeneration" convention as every prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1310`-`FR-1340` introduce a genuinely new
  concept (an autonomous song-form phase cycle) that writes the same `TEMPO_IDX`/`DENSITY_IDX`
  fields `IP-1080`'s style application (`FR-1240`) and the D-pad/B handlers already write —
  checked explicitly for conflict: `FR-1320`'s "overwrites... on the same tick as the transition"
  is the same "last write wins, no special-casing" contract `FR-1240` itself already established
  for a different trigger (Start press vs. an autonomous timer), not a new or contradictory rule.
  `FR-1330` explicitly confirms no interaction with bad-zone detection/recovery or motif-variant
  selection, closing the one place a real conflict could have existed (both mechanisms are
  scheme/phase-agnostic by the same construction `FR-1220`/prior delta reviews already verified).
- **No architecture violation.** Each FR/NFR traces directly to `ADS-103`; no ADR is directly
  implicated (`ADS-103`'s own Decision Log carries its binding decisions, same pattern
  `ADS-101`/`ADS-102` already established).
- **No missing requirement.** `ADS-103` §5/§6's four FR-candidates and two NFR-candidates all
  became baseline requirements — none silently dropped. `ADS-103`'s Open Questions (BUILD-phase/
  `OVERLOAD` tuning interaction, style-drift's eventual mechanism, exact phase values/durations,
  whether `SCALE_IDX`/`DUTY_BIAS` join the envelope) are correctly *not* baselined here —
  tuning/future-scope decisions, not requirements gaps.
- **Traceability:** every new ID's Source Documents column cites `ADS-103`'s specific section. No
  candidate needed — every statement in `ADS-103` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for R6.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1100`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (`FR-1350`-`FR-1380`, `NFR-1140`-`1160`)

Reviewed this delta only, same "not a wholesale regeneration" convention as every prior delta pass:

- **No duplicate or conflicting requirement.** `FR-1350`-`FR-1380` introduce a genuinely new
  concept (a read-only settings-value display) that does not touch any existing engine-state
  write path — checked explicitly against `FR-1120` (the existing visualizer requirement,
  channel-activity/bad-zone only): `FR-1350`-`FR-1380` are additive to what `FR-1120` already
  requires, not a restatement or a contradiction of it. `FR-1370` explicitly confirms no
  interaction with the existing channel-activity/palette behavior, closing the one place a real
  conflict could have existed (a new visualizer write path competing with or altering an
  existing one).
- **No architecture violation.** Each FR/NFR traces directly to `ADS-104`; no ADR is directly
  implicated (`ADS-104`'s own Decision Log carries its binding decisions, same pattern
  `ADS-101`/`ADS-102`/`ADS-103` already established). `ADS-104` §2 explicitly preserves GDS-03
  §1's "visualizer never writes engine state" invariant — `FR-1350`/`FR-1360`/`FR-1380` are all
  phrased as read/display behavior only, consistent with that constraint.
- **No missing requirement.** `ADS-104` §5/§6's four FR-candidates and (in this case) three
  NFR-candidates all became baseline requirements — none silently dropped; the NFR set is one
  larger than the two-per-delta pattern of the three prior deltas because `ADS-104` §6 itself
  states three genuinely distinct non-functional concerns (ROM/VRAM budget, per-frame timing, no
  new input control) rather than two, and splitting them keeps each NFR atomic per this skill's
  own writing rules. `ADS-104`'s Open Questions (whether the four deferred per-feature indicators
  are ever built, whether a static in-ROM control legend is ever added, exact bar-tile pixel
  design, actual tilemap-layout headroom) are correctly *not* baselined here — future-scope/
  content/implementation decisions, not requirements gaps.
- **Traceability:** every new ID's Source Documents column cites `ADS-104`'s specific section. No
  candidate needed — every statement in `ADS-104` §5/§6 was traceable to the document itself.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for this settings-visibility work.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1110`-equivalent catalog row once picked up.

## Delta Review — 2026-07-26 (corrective pass: `FR-1120`, `NFR-1010`, `CR-0001`, `BL-0040` adjudication)

A **corrective/precision pass**, not a new-feature formalization — no new baseline IDs were added.
Reviewed per the same "not a wholesale regeneration" convention as every prior delta.

- **`FR-1120`'s tempo claim, split (`BL-0016`).** The original text required the visualizer to
  represent "tempo, per-channel activity, and bad-zone status." [GDS-08 §7](../architecture/08-presentation-architecture.md)
  resolved this honestly in three parts, and this pass implements that resolution: the tempo
  *setting* is genuinely displayed now (`IP-1110`'s indicator bar) but is `FR-1350`'s claim, not
  `FR-1120`'s; tempo-*synced motion* was never built; so the original wording was satisfied on a
  narrow reading and overstated on the natural one. `FR-1120` now covers only per-channel activity
  and bad-zone status — both true since `IP-0006` — and the synced-motion claim moved to
  **`CR-0001`** in a new Candidate Requirements section, explicitly excluded from the baseline.
  This is the first Candidate Requirement this project has recorded; the section exists now for
  future use. **No requirement lost coverage**: the split moved a claim to a more accurate owner
  and demoted an unbuilt one, rather than dropping anything shipped.
- **`NFR-1010` gained a caveat, not a rewrite (`BL-0060`).** [GDS-06 §2.2](../architecture/06-non-functional-requirements.md)
  found that `R101`'s own stated cycle-tallying revisit trigger appears to have fired, and its
  merge decision explicitly left to this skill whether `NFR-1010` should point at that. It should:
  the requirement's extended-run verification method remains correct and primary, but `IP-1110`
  demonstrated a reproducible case it structurally cannot catch (a stress run with no Select press
  cannot exercise the Select-reset frame). The caveat records that limit without weakening the
  requirement — the method is still required, it is just no longer sufficient alone for one named
  class of package.
- **`BL-0040` investigated and found NOT to be a requirements defect — re-routed, not fixed.**
  The finding is that an absolute-sounding bad-zone-independence claim ("a style change does not
  alter `DISSONANCE_SCORE`/`BAD_ZONE_FLAGS`/`STALE_COUNT_*`/`ONSET_WINDOW_COUNT`") is true only
  narrowly, since `engine_tick` runs every frame and an unrelated channel's coincidental onset can
  touch those fields on the same frame (`VR-1080` measured ≈16% under adversarial play). It was
  routed to this skill on the assumption the imprecision lived in the FR text. **It does not.**
  Checked directly: no FR in `FR-1230`-`FR-1260` (the style range) states bad-zone independence at
  all, and the two FRs that *do* state independence claims of this shape — `FR-1220` (scheme) and
  `FR-1330` (song-form) — are both phrased at **mechanism level** ("no scheme-specific bad-zone
  logic exists" / "no phase-specific logic exists in either mechanism") rather than as same-frame
  guarantees, which is exactly the phrasing that keeps them accurate. The absolute claim exists
  only in **`FS-108`'s acceptance criterion (4)** (owned by `06-feature-specification`) and
  **`IP-1080`'s Definition of Done** (owned by `07-implementation-planning`). Nothing here to fix;
  `BL-0040` should be re-routed to those two owners.
  **Worth recording as a positive finding**: the FR baseline stayed accurate here *because* of a
  phrasing convention — state what logic exists, not what can never coincide — and future FRs of
  this shape should follow it.
- **`docs/requirements/INDEX.md` re-labelled (`BL-0068`).** The `02-requirements-review.md` and
  `03-rtm.md` rows read `⛔ Planned`, implying owed work. [GDS-10 §3.1](../architecture/10-requirements-traceability-matrix.md)'s
  reasoning is agreed with and adopted: review findings live inline as Delta Review sections (all
  eight present), and the RTM's information is distributed across artifacts already maintained,
  with independent verification a stronger gap-finder than a table. Both rows now read as
  deliberate, reasoned deviations.
- **No conflict, no duplicate, no architecture violation introduced.** `FR-1120`'s narrowing does
  not orphan any shipped behavior (`FR-1350` covers the indicator display); `NFR-1010`'s caveat
  strengthens rather than relaxes it; `CR-0001` is explicitly non-baselined.

No Critical/High finding. One item re-routed rather than resolved (`BL-0040` → `06`/`07`).

## Delta Review — 2026-07-31 (`FR-1390`-`FR-1420`, `NFR-1170`/`1180`, `CR-0002`)

New-feature formalization for roadmap R7 (Emotional/Energy Layer), same shape as every prior
per-release delta. Reviewed the four new FRs, two new NFRs, and one new Candidate Requirement
against the full existing baseline before closing.

- **Every new ID traces to `ADS-105`'s own §5/§6 candidates**, restructured for atomicity where
  the ADS's own wording conflated two properties. `ADS-105`'s FR-candidate 1 ("`AROUSAL` is a
  function of X, Y, recomputed whenever either changes") was split into `FR-1390` (the functional
  relationship) and `FR-1410` (the recompute-timing guarantee, covering both axes together since
  `ADS-105` §2 establishes they share trigger sites — a single atomic requirement for a
  single-mechanism guarantee, not two requirements that would always pass or fail together).
  Same split for FR-candidate 2 into `FR-1400`/`FR-1410`. FR-candidates 3/4 (boot-init, reset)
  merged into one `FR-1420` since both are the same "no stale-value grace period" property applied
  to two trigger events already covered together in `ADS-105`'s own trigger-site enumeration.
- **`BL-0081` resolved: acceptance criteria stay at the behavioral level, not literal formulas.**
  `ADS-105` recommended concrete lookup-table-style formulas but explicitly left the decision to
  this pass. Decided **against** baking in specific table values: `FR-1390` requires monotonicity
  (a testable, implementation-independent property — many concrete tables satisfy it) and
  `FR-1400` requires a fixed one-to-one mapping (also testable without committing to which mapping)
  rather than "AROUSAL = (TEMPO_IDX + DENSITY_IDX) at these exact indices." This follows this
  skill's own standing rule (a requirement naming byte-level detail has crossed into
  implementation) and the same discipline `GDS-07`/`GDS-09` apply project-wide — exact table
  contents are `07-implementation-planning`'s to propose against these acceptance criteria, not
  this baseline's to fix in advance.
- **`BL-0080` resolved: `CHMIX_IDX`-derived active-channel count excluded from v1, recorded as
  `CR-0002`.** `FR-1390` is fully satisfiable and citation-clean from `TEMPO_IDX`/`DENSITY_IDX`
  alone; adding a third input for marginal richness, with no current requester, would widen the
  acceptance-test surface for no baselined benefit. Kept as a candidate rather than dropped
  outright because `ADS-105` §2 confirms promoting it later costs little (the trigger-site
  plumbing for `CHMIX_IDX` changes already exists for other reasons) — the same reversibility
  reasoning `CR-0001` already established as this baseline's convention for "real future capability,
  not currently required."
- **No conflict with `FR-1120`/`CR-0001`, checked directly.** `FR-1120`/`CR-0001` concern the
  *visualizer's* observable output (tile/palette content, including the deferred tempo-synced-
  motion candidate); `FR-1390`-`FR-1420` concern a WRAM-resident derived value with **no
  visualizer consumer in this release** (`ADS-105` §2 states `visuals.py` is explicitly untouched
  — roadmap R9, separately blocked, owns the eventual visual consumption). Both requirement sets
  reference `TEMPO_IDX`, but one is about how tempo is *displayed* and the other is about how
  tempo *feeds a derived backend value* — adjacent territory, genuinely distinct claims, no
  overlap or restatement.
- **`NFR-1170` is this delta's load-bearing NFR and is cited to a live, in-session finding**
  (`IP-9030`'s VBlank-budget measurement, `R101` §8.5, `GDS-06` §2.2a) rather than to `ADS-105`
  alone — checked that this doesn't duplicate `NFR-1010`'s own caveat (added 2026-07-26, widened
  2026-07-31 to cover any package adding per-frame work): it does not. `NFR-1010`'s caveat is
  about the *verification method's* limits (a stress run cannot detect a narrowed margin);
  `NFR-1170` is a *design constraint on this specific package* (add zero unconditional per-frame
  cost, full stop) that would satisfy `NFR-1010`'s concern by construction rather than merely
  being tested against it. Complementary, not duplicate.
- **Forward traceability (Module/FS/IP/Test), updated 2026-07-31 now that `IP-1120` is
  `COMPLETE`:** `FR-1390`/`FR-1400`/`FR-1410`/`FR-1420`/`NFR-1170`/`NFR-1180` → Module
  `music_engine.py` (`_emit_mood_update`, called from `_emit_song_tick` and `init_engine`) +
  `input_map.py` (4 `_step_on_bit` call sites) · FS `FS-112` · IP `IP-1120` · Test `test_rom.py`
  `T20` (`T20.1`-`T20.4` FR-1390, `T20.5` FR-1400, `T20.6`-`T20.11` FR-1410, `T20.11`-`T20.12`
  FR-1420; `NFR-1170`/`NFR-1180` verified by call-graph inspection per their own Verification
  Method, not solely `T20`). Awaiting `09-package-verification`.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
`FEAT-1120`-equivalent catalog row for roadmap R7.

## Delta Review — 2026-07-31 (`FR-1430`-`FR-1460`, `NFR-1190`/`1200`)

- **No duplicate or conflicting requirement.** `FR-1430`-`FR-1460` introduce a new visualizer
  capability (style-keyed theme palette selection) that is genuinely additive: nothing in the
  existing baseline states or implies a `CHMIX_IDX`-keyed palette lookup exists today.
- **Checked against `FR-1120`'s own split (`BL-0016`) and `CR-0001`.** `FR-1120` (as reworded)
  covers per-channel activity/bad-zone representation; `CR-0001` (not baselined) covers
  tempo-*synced motion*. Neither overlaps this delta: `FR-1430`-`FR-1460` are about which
  **palette** is active, not per-channel activity, tempo representation, or beat-synced motion.
  A style theme changing color is a different claim from a tile pulsing on the beat.
- **Checked against `FR-1370`** (`IP-1110`'s settings indicators are "purely additive... no change
  to existing channel-activity tiles' or calm/bad-zone palette's behavior"). No conflict: `FR-1370`
  is about the *indicator cells* not disturbing the *existing* calm/bad-zone swap; this delta
  changes what "the calm palette" *is* (a lookup instead of a constant) without touching the
  indicator cells at all, and `FR-1450` explicitly preserves the bad-zone swap's own priority.
- **`FR-1440`'s no-regression contract is load-bearing and mirrors the project's own established
  pattern** (`STYLE_TABLE`/`SONG_TABLE`/`MOTIF_TABLE` index-0 rows all carry the identical
  guarantee) — checked that this delta follows the same discipline rather than inventing a new
  one.
- **Scope boundary confirmed**: this pass baselines `RM-9001` only. `RM-9002` (mood-reactive,
  depending on `IP-1120`'s `AROUSAL`/`VALENCE`) and `RM-9003` (accessibility, `BL-0021`) are
  named in `ADS-106` but deliberately carry no FR/NFR here — the same exclusion discipline the R7
  delta applied to `CR-0002`. Both remain candidates for a future delta pass once their own
  packages are scheduled.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — correctly honest, no `FS-xxx`/
  package/test exists yet for R9.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add an
R9-equivalent catalog row.

## Delta Review — 2026-08-07 (`FR-1470`-`FR-1490`, `NFR-1210`-`1230`, `FR-1240` amended)

- **`FR-1240` amendment checked for isolation, as this pass's argument required.** Grepped the
  whole file for every citation of `FR-1240`: two occurrences are the requirement's own row and
  its 2026-07-26 changelog entry (both now consistent with the amendment); the remaining four
  are inside **two prior passes' own historical `## Delta Review` sections** (the 2026-07-26 R5
  review discussing `FR-1240` vs. `FR-1190`'s differing timing, and the 2026-07-26 R6 review
  discussing `FR-1240` vs. `FR-1320`'s shared "last write wins" contract). **Left unedited,
  deliberately**: those sections are dated records of what was true and reasoned about *at the
  time each pass ran* — `FR-1240` genuinely did guarantee instant application for all four fields
  when R5 and R6 were reviewed, and both reviews' conclusions (no conflict with `FR-1190`; the
  same last-write-wins contract `FR-1320` reuses) remain accurate as historical statements. Only
  `FR-1240`'s own current text needed to change; rewriting past reviews to match present tense
  would falsify the record this file's own append-only Delta Review convention exists to
  preserve.
- **No duplicate or conflicting requirement introduced.** `FR-1470`-`FR-1490` describe a genuinely
  new mechanism (the blend) that did not exist under any prior FR — they extend, not duplicate,
  the space `FR-1240` used to cover alone.
- **The amendment does not disturb `FR-1320`'s own "last write wins" contract** (song-form phase
  transitions still overwrite `TEMPO_IDX`/`DENSITY_IDX` directly, same tick, per `ADS-103`) —
  checked explicitly since both `FR-1320` and the new blend mechanism write the same two fields.
  `ADS-107` §9 OQ3 already names the interaction as needing empirical confirmation at
  implementation/verification time rather than an architectural rule; this pass adds no new
  requirement resolving that OQ, matching `ADS-107`'s own explicit deferral.
- **No architecture violation.** Every new FR/NFR traces directly to `ADS-107`; no ADR is directly
  implicated.
- **Forward traceability (Module/FS/IP/Test), updated 2026-08-08 now that `IP-1130` is
  `COMPLETE`:** `FR-1470`/`FR-1480`/`FR-1490`/`NFR-1210`/`NFR-1220`/`NFR-1230` (and `FR-1240`'s
  amendment) → Module `music_engine.py` (`_emit_begin_blend`, `_emit_blend_tick`, called from
  `input_map.py`'s Start handler and `engine_tick` respectively) · FS `FS-113` · IP `IP-1130` ·
  Test `test_rom.py` `T21` (`T21.1`/`T21.2` FR-1470, `T21.3` FR-1480, `T21.4`-`T21.7` FR-1490,
  `T21.8`/`T4.7`/`T15.1`-`T15.4` FR-1240's surviving `SCALE_IDX` guarantee; `NFR-1220` verified by
  inspection — now 7 bytes, `0xC070`-`0xC076`, per `GDS-07` §6 (grew from 4 after `VR-1130`'s F1
  remediation added `BLEND_DELTA_TEMPO`/`DENSITY`/`DUTY`); `NFR-1230`'s own audible-quality half
  remains explicitly deferred to `09-content-review`, never claimed by `T21`). **Updated
  2026-08-08**: `VR-1130` returned this package with a Critical finding (`F1` — the per-frame
  `STYLE_TABLE` re-derivation genuinely exceeded the VBlank budget on active-blend frames,
  confirmed by `VIS_ENTRY_LY` measurement, not merely a display artifact) and a Low-Medium finding
  (`F2` — a stale package-doc Risks field). `F1` remediated: deltas now precomputed once in
  `_emit_begin_blend`; a second, independent latent defect surfaced and fixed in the same pass
  (`BLEND_STEP` was never explicitly initialized, corrupting a boot/Select-reset if left stale);
  `test_rom.py`'s `T21.3b` added, independently hand-deriving a genuine mid-blend value against the
  shipped ROM — the coverage gap that let `F1` ship undetected. `NFR-1210`'s own Verification
  Method (WRAM-assertion-testable, audible judgment deferred) previewed what
  `06-feature-specification`'s Acceptance Criteria field looked like once R8 reached that stage —
  confirmed consistent, not re-decided here. Re-awaiting `09-package-verification` (fresh session).

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add an
R8-equivalent catalog row (`FEAT-1130`, per the release plan's own forward placeholder).

## Delta Review — 2026-08-20 (`FR-1500`-`FR-1590`, `NFR-1240`-`1270`, `CR-0003`-`CR-0006`)

New-feature formalization for `BL-0119`'s harmonic-coordination mechanism, same shape as every
prior per-release delta. Reviewed the ten new FRs, four new NFRs, and four new Candidate
Requirements against the full existing baseline before closing.

- **Every new ID traces to `ADS-108`'s own §5/§6 candidates**, which this pass adopted directly
  (same ID numbers `ADS-108` itself proposed — checked for collision against the live baseline
  first: `FR-1500`-`FR-1590` and `NFR-1240`-`1270` were unused anywhere in `docs/requirements/`,
  `docs/features/`, or `docs/implementation/` before this pass). No restructuring for atomicity was
  needed beyond what `ADS-108` §2.6 already did itself — its per-voice table (wave/pulse A/pulse B)
  is already split one requirement per voice (`FR-1540`/`FR-1550`/`FR-1560`), matching this
  baseline's own "split ands" convention without further work.
- **No duplicate or conflicting requirement.** `FR-1500`-`FR-1590` introduce a genuinely new
  concept (a shared harmonic context all three pitched channels read) orthogonal to every existing
  FR — checked the two places a conflict could plausibly exist:
  - **Against `FR-1180`/`FR-1210` (scheme selection, Scheme E's motif mechanism).** `FR-1570`
    explicitly supersedes `FR-1180`'s `CHMIX_MASKS`-bits-4-6 carrier with `SCHEME_TABLE`, but does
    not alter what a scheme *does* — `FR-1180` is reworded only in its own future edit if
    `07-implementation-planning` chooses to touch it; this delta leaves `FR-1180`'s text standing
    (it still correctly describes that scheme assignment gates note-selection strategy) and adds
    `FR-1570` as the carrier-mechanism replacement, the same "extend, don't silently orphan"
    pattern `FR-1270`-`FR-1300` used for `FR-1210` previously. `FR-1210` (Scheme E's fixed-motif
    pitch selection) is untouched and unaffected — Scheme H is a third, independent scheme, not a
    modification of Scheme E, and `CR-0004` records that Scheme E stays harmonically uncoordinated
    this increment rather than silently implying otherwise.
  - **Against `FR-1080`/`FR-1090`/`FR-1100`/`FR-1220` (bad-zone detection/recovery, and its
    scheme-agnosticism).** `FR-1220` states bad-zone detection/recovery "appl[ies] identically to a
    pitched channel regardless of which generation scheme... it is currently running." `FR-1590`
    narrows this for Scheme H specifically (a strong-onset chord-tone target is not overridden by
    dissonance recovery) — this is a genuine, disclosed exception to `FR-1220`'s "no scheme-specific
    bad-zone logic exists" claim, not an oversight left unreconciled. Checked directly: `FR-1590`'s
    own text names the exception precisely (dissonance recovery only; stuck/overload recovery are
    explicitly carved back out as unaffected, matching `ADS-108` §8 D8's own "stuck/overload are
    orthogonal to harmony and need no change" position) and cites `FR-1080`/`FR-1220`
    both. Recommend `07-implementation-planning`/a future `04` pass narrow `FR-1220`'s own wording
    ("no scheme-specific bad-zone logic exists" → "...except the disclosed exception `FR-1590`
    names") the next time either FR is opened, so a future reader isn't left to reconcile the two
    unaided — filed as a Low finding below rather than blocking this delta, since `FR-1590`'s own
    text already names the exception precisely and no reader relying on `FR-1590` alone is misled.
- **No architecture violation.** Every new FR/NFR traces directly to `ADS-108`; `FR-1570` also
  cites `ADR-0003` (the binding decision record for the `SCHEME_TABLE` migration) and names
  `ADR-0001` as the superseded mechanism, not silently dropped.
- **No missing requirement, and deferred scope is named, not omitted.** `ADS-108` §5/§6's ten
  FR-candidates and four NFR-candidates all became baseline requirements — none silently dropped.
  `ADS-108` §2.7's four explicitly-out-of-scope items (phrase/rest/cadence `D10`; Scheme-E
  harmonization; the default-preset flip `D11`'s second half; re-rooting the `IP-1060` arpeggio)
  are **not silently omitted** — each is recorded as its own Candidate Requirement (`CR-0003`-
  `CR-0006`) naming exactly why it is not baselined and what would need to change for it to be,
  the same discipline `CR-0001`/`CR-0002` already established. `ADS-108` §9's six Open Questions are
  correctly *not* baselined as requirements — OQ1 (`DISSONANCE_THRESHOLD` retuning),
  OQ3 (pentatonic's chord rows), and OQ4 (N=4 tuning) are `BL-0005`-class data/tuning decisions
  (recorded in this pass's "Open items" bullet below); OQ2 (the default-preset flip's timing) is
  `CR-0005`'s own gate, already named there; OQ5 (chord-clock driving-channel assumption) and OQ6
  (whether increment 2 harmonizes Scheme E) are future-scoping questions with no present
  requirement to state, consistent with how prior deltas have handled forward-looking OQs.
- **The index-0/no-regression discipline is checked explicitly, per this project's own established
  pattern** (`STYLE_TABLE`/`SONG_TABLE`/`MOTIF_TABLE`/palette-table index-0 rows all carry the
  identical guarantee — `FR-1260`/`FR-1320` boot-phase/`FR-1440`). `FR-1580` follows the same
  discipline for `SCHEME_TABLE`'s preset-0 row, and `FR-1570`'s migration clause additionally
  requires the *other* 7 presets' pre-existing `CHMIX_MASKS` bits-4-6 assignments to survive
  byte-for-byte — a stronger, package-level non-regression obligation than a single index-0 row,
  matching `ADS-108` §8 R1's own framing of the migration's risk. This obligation is also filed
  separately as a sequencing/planning concern, not just a requirements one — see `BL-0123`.
- **Traceability:** every new ID's Traces-to column cites `ADS-108`'s specific section/decision
  letter and, where the underlying grounding is research rather than architecture synthesis, the
  specific `R225` section as well (e.g. `FR-1560` cites both `ADS-108` §2.6/D9 and `R225` §3g/§5d/
  §5f for the octave-separation instruction specifically) — per this project's own GDS-10 §2
  backward-traceability discipline. No candidate needed beyond `CR-0003`-`CR-0006` — every
  baselined statement was traceable to `ADS-108`/`R225` directly, not invented here.
- **Forward traceability (Module/FS/IP/Test):** all `UNASSIGNED` — no `FEAT-xxx`, `FS-xxx`,
  Implementation Package, or test exists yet for harmonic coordination; correctly left honest
  rather than guessed, the expected state for a requirements-only delta pass. **Explicit note for
  whoever picks this up:** `ADS-108` itself states, and this pass agrees, authoring this delta is
  **not** a `G3` package authorization — no `IP-xxxx` may be built against `FR-1500`-`FR-1590`
  without its own explicit per-package user go-ahead, and `BL-0123`'s `SCHEME_TABLE`-migration
  refactoring should be sequenced and authorized as its own first package ahead of any Scheme-H
  feature package that depends on it, per `ADS-108` §8 R1's own recommendation.

**One Low finding** (does not block this delta, filed for whichever stage next opens `FR-1220`):
`FR-1220`'s "no scheme-specific bad-zone logic exists" wording is now narrowly imprecise given
`FR-1590`'s disclosed exception — recommend rewording at the next natural touch of either FR
rather than a dedicated pass.

No Critical/High finding. This delta is ready for `05-feature-decomposition` to add a
harmonic-coordination-equivalent catalog row — noting this is a substantially larger increment
than any prior delta (10 FRs across 3 voices plus a structural migration), which the user will
likely want to weigh in on before it is scheduled alongside or ahead of other open work.

## Delta Review — 2026-08-20, second pass (`ADS-108` §11 / `ADR-0004` amendment: `FR-1570` withdrawn, `FR-1580` reversed, `FR-1260` clarified, `CR-0005` promoted)

Scope of this review: **only** the statements this pass changed, plus every other requirement that
cites or depends on them. Per this file's own convention (established by the 2026-08-07 pass for
`FR-1240`), a superseded requirement is **amended in place**, not left standing beside a
contradicting new one; and prior passes' own Delta Review sections are left as accurate records of
their own time rather than retroactively edited.

### What upstream changed

`03-architecture-design-synthesis` reopened `ADS-108` after the project owner released the
constraint the document's §1/§2.5/§2.7/§7.4/D11/§8-R7 all rested on:

> "Don't hold the preset 0 to an arbitrary standard, it was developed by you at a previous
> iteration. […] I'd like to get to a pleasant sounding music as soon as possible."

`ADS-108` §11 (D13) and `ADR-0004` re-decided, on the record, that chord-derived note selection
**replaces the default scheme's note selection in place** rather than sitting beside it as a third
scheme. `GDS-04` §4.1 was amended in the same pass to separate the index-0 invariant's two conflated
rules. This pass carries those consequences into the FR/NFR baseline. **No new domain fact, no new
architecture decision, and no implementation detail is originated here.**

### Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| D1 | Conflict (resolved by amendment) | `FR-1570` vs. `ADR-0004` | `FR-1570` mandated a `SCHEME_TABLE` migration that `ADR-0004` decides will not be performed. Leaving it standing would have made the baseline require work the architecture forbids. | High | **Applied**: withdrawn in place, with its reason and superseding sources named. Not deleted — the strikethrough plus rationale is what makes the withdrawal auditable. |
| D2 | Conflict (resolved by amendment) | `FR-1580` vs. `ADR-0004`/`CR-0005` | `FR-1580` required preset 0 to stay all-Scheme-W; `ADR-0004` requires the opposite. This was a direct contradiction, not a scope narrowing. | High | **Applied**: reversed in place. `CR-0005`, which stated the reversal as a candidate, is marked **promoted to the baseline** in the Candidate Requirements table rather than deleted, so the promotion is visible where the exclusion was recorded. |
| D3 | Ambiguity (pre-existing, now load-bearing) | `FR-1260`, `FR-1300`, `SONG_TABLE` phase 0 | These three "index 0 introduces no change to current boot/reset behavior" clauses each admit two readings: (a) row 0 agrees with the boot preset's steering-index values (a fixed-point rule), and (b) preset 0 sounds like some prior build (a historical rule). Under the old regime the readings coincided, so the ambiguity was harmless. `FR-1580`'s reversal separates them, and reading (b) would now falsely report a conflict with `FR-1580`. | **Medium-High** | **Applied to `FR-1260`** (clarified in place, reading (a) only, citing `GDS-04` §4.1's dated amendment). `FR-1300` and `SONG_TABLE` phase 0 are covered by the same clarification, cited from `FR-1260`'s note rather than duplicated — flagged here so a future pass does not read the absence of an edit as an oversight. |
| D4 | No conflict found (checked, reported) | `FR-1180`, `FR-1190`, `FR-1200`-`FR-1220` | `FR-1570` would have superseded `FR-1180`'s single-scheme-select-bit mechanism. With `FR-1570` withdrawn, **`FR-1180` stands unamended and in force** — verified by re-reading all five Scheme-W/Scheme-E requirements against `ADR-0004`. Scheme E's own behavior (`FR-1200`-`FR-1220`) is untouched by this increment. | Informational | No action. Recorded because "did we forget to amend `FR-1180`?" is the obvious next question and the answer is a deliberate no. |
| D5 | Scope change (reported, not resolved here) | `FR-1540`-`FR-1560`, `FR-1590` | These four were written as conditional on "a channel running Scheme H." With `FR-1580` reversed, that condition is satisfied at boot for all three pitched channels, so all four become **boot-path requirements** rather than non-default-preset requirements. Their *statements* need no rewording — "a pitched channel running the harmonic-coordination scheme" is still exactly right — but their **verification priority and blast radius change materially**, and `FR-1590`'s bad-zone exception in particular moves from a corner case to a permanently-exercised path. | Medium | No text change. Flagged for `05`/`06`/`07` to reflect in test design and Definition of Done, and for `09-package-verification` to treat `FR-1590` as a first-class check rather than an edge case. |
| D6 | Verification-method change | `NFR-1270` | The strong-beat-partitioned acceptance instrument was written assuming a same-build comparison between a harmonized preset and preset 0. That comparison no longer exists — both are now harmonized. | Medium | **Applied**: `NFR-1270` amended to name the immediately-preceding commit's ROM, measured under identical conditions, as the comparison baseline. This also discharges `BL-0122`'s still-open half, which asked that the partition survive into an actual package's Verification Checklist. |
| D7 | Obviated work item (reported to its owner) | `BL-0123` | `BL-0123` is a `SCHEDULED` refactoring entry for the `CHMIX_MASKS`→`SCHEME_TABLE` migration, whose only requirements-baseline anchor was `FR-1570`. With `FR-1570` withdrawn, the entry has no requirement behind it. | Medium | Not this skill's ledger to write. Routed to `07-implementation-planning` / `00-pipeline-manager` to close as **obviated** (not "done", not "deferred") — the work is not owed at any future date, because the design that required it was superseded before implementation. |
| D8 | Residual candidate check | `CR-0003`, `CR-0004`, `CR-0006` | Re-checked whether the invariant's release promotes any of the other three candidates. It does not: `CR-0003` (phrase/rest/cadence) was deferred for verification-surface reasons, `CR-0004` (harmonizing Scheme E) for an unmade `03` scoping decision, `CR-0006` (arpeggio re-rooting) for a measured per-frame-adjacent cost — none of the three was gated on preset 0's immutability. | Informational | No action. Recorded so the release is not over-applied. |
| D9 | Traceability | `FR-1570`, `FR-1580`, `FR-1260`, `NFR-1250`, `NFR-1270`, `CR-0005` | All six cited `ADR-0003` and/or `ADS-108` §2.5/§2.7/D7/D11 — sources that are now superseded or withdrawn. This project carries no separate traceability matrix (a deliberate deviation, `BL-0068`/`GDS-10` §3.1): backward traceability lives in each requirement's own *Traces to* column. | Low-Medium | **Applied**: each amended row's *Traces to* column re-pointed at `ADS-108` §11/D13 and `ADR-0004` in the same edit that changed its statement — which is the whole reason the deviation is safe, since there is no second copy to drift. `FR-1570` keeps no forward trace at all: it is annotated **WITHDRAWN**, never implemented, and no `FEAT`/`FS`/`IP`/`VR` may claim it. |

**No Critical findings. No finding requires an upstream return.** D1/D2/D3/D6 were applied as
in-place amendments (which is what this pass exists to do); D4/D5/D8 are informational; D7 is routed
to a ledger this skill does not write.

### Adjudication note

This pass applies an amendment that **deliberately breaks shipped, tested behavior** — the boot
sound changes, and `T5`/`T6`-class assertions on the ±1 stepwise walk will stop describing the
engine. That is not this skill's call to make and it has not been made here: it is the project
owner's explicit directive, recorded verbatim in `ADS-108` §11.1 and in the Master Build Plan's own
G3 authorization record, and re-decided at architecture altitude in `ADR-0004`. This document
records the consequence; it does not originate the decision.

---

## Delta Review — 2026-08-21 (`FR-1130` amended; `FR-1600`-`FR-1630`, `NFR-1270` amended, `NFR-1280`; `CR-0006` absorbed)

**Scope of this delta:** [`ADS-108` §12](../architecture/ADS-108-harmonic-coordination.md) (D14) and
[`ADR-0005`](../architecture/adr/ADR-0005-the-arpeggio-becomes-chord-aware-gated-and-varied.md),
carrying `BL-0127` (the project owner's *"constant repeated arpeggios"*, measured), `BL-0128`
(measurement basis), `BL-0125` (absorbed as `NFR-1280`'s enabling constraint) and `CR-0006`
(absorbed into the baseline). Step 0 was re-run **on the delta only**, per this skill's own
delta-update convention; nothing outside the arpeggio contract and the measurement basis was
re-derived.

### What changed, and why each change is an amendment rather than an addition

| Requirement | Change | Why in place rather than beside |
|---|---|---|
| `FR-1130` | **Amended in place.** The arpeggio's pitch source changes from *"a chord implied by the channel's current scale degree"* to *"tones of the currently-sounding shared chord"* (`FR-1500`). | The original statement is not merely incomplete, it is now **wrong about the engine's intent**. It was written 2026-07-22, when no shared chord existed and each channel's own degree was the only chord reference available. Once `FR-1500` shipped, a requirement telling the arpeggio to imply a chord *from the channel's own degree* directs the engine to sound a second, differently-rooted triad against its own harmony. Leaving it standing and adding a new FR beside it would have left two baselined requirements ordering contradictory behavior — exactly what this document's own writing rules forbid. |
| `FR-1600` (new) | An arpeggio happens only while the held note is a chord tone; a non-chord tone (the melody's weak-onset passing tone, `FR-1550`) sustains. | Genuinely new behavior, not a clarification of `FR-1130` — it constrains *when* the mechanism runs, which nothing previously said. |
| `FR-1610` (new) | The figure is selected per onset from a set of alternatives, one of which is "does not arpeggiate"; alternatives must differ in rhythmic surface, not only pitch order. | Genuinely new. Also the mechanism by which `FR-1600`'s gate is expressed, which is why the two are separate requirements that reference each other rather than one compound requirement (atomicity rule). |
| `FR-1620` (new) | A scale/octave change during an already-sounding note takes effect at the next onset, not mid-note. | A behavioral consequence of `ADS-108` §12.4's onset-resolved cache. Recorded as a requirement precisely so it cannot be introduced silently by an implementer as an incidental side effect — it is observable, so it is baselined. |
| `FR-1630` (new) | Boot and Select re-establish arpeggio state. | `VR-1130` already found this exact defect class once (`BLEND_STEP` left uninitialized, letting stale source values corrupt a fresh reset). Making it a requirement is cheaper than finding it a second time. |
| `NFR-1270` | **Amended in place**, second amendment. Measurement basis is now normatively **sounding pitch**, never the selected degree. | `BL-0128`. The NFR previously said *what to partition by* and was silent on *what to measure*, and every measurement taken under it read intent. A silent NFR that produced a wrong number twice is amended, not annotated. |
| `NFR-1280` (new) | The arpeggio's unconditional per-frame cost must **strictly decrease**; `VIS_ENTRY_LY` verifies it; a regression is blocking. | New, and deliberately phrased as a *decrease* rather than a bound. `NFR-1240` says "add nothing per-frame"; this says "give some back." `BL-0125` is absorbed here. |
| `CR-0006` | **Absorbed into the baseline**, marked rather than deleted. | Same treatment §11 gave `CR-0005`: the promotion stays visible in the place the exclusion was recorded. |

### Placeholder-promotion guard (run 2026-08-21, per this skill's 2026-08-20 addition)

Two of this delta's requirements constrain something about a concrete value, so the guard applies
and was run rather than assumed. `BL-0005` is open and covers every table in `music_data.py` as
first-guess and untuned, and the arpeggio's new figure table is squarely inside it.

**`FR-1610` — stated relationally, which the guard names as almost always the right answer.** It
does not baseline the pattern table's contents, its row count, its weighting, or any individual
figure. It baselines two *invariants that stay true whatever the table is tuned to*: the set must
contain a member under which the note does not arpeggiate, and its members must differ in how many
steps sound a pitch other than the onset pitch. A tuning pass can rewrite every byte of
`ARP_PATTERNS` and `ARP_PATTERN_PICK` without touching this requirement — which is exactly the
property `FR-1260` lacked, and lacked expensively: an acknowledged-arbitrary preset acquired the
authority of a requirement purely by being written down first, and then blocked a genuine
improvement for an entire increment until the **user** pushed back. That failure is why this guard
exists, and this delta is its first application.

**`FR-1600`** constrains a *condition* (the held note being a chord tone), not a value, so the
guard does not bite. **`FR-1620`/`FR-1630`** constrain timing and initialization, likewise.
**`NFR-1280`** is relational by construction — it requires the per-frame cost to *decrease*
against the immediately preceding build, never to reach a named number, so no measured figure is
frozen into it either.

**Nothing in this delta freezes a value the project's own backlog calls arbitrary.**

### Findings (report only — nothing applied here)

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| E1 | **Latent conflict, caught before it could ship** | `FR-1600`, `FR-1150`, `FR-1140` | `FR-1150`'s portamento is not implemented by a glide routine — it is produced *by the arpeggio tick's own per-frame frequency rewrite* carrying the pitch from the outgoing note to the new one (`Claude.md`'s sound-design section states this explicitly, and `engine_tick`'s call order is load-bearing for it). `FR-1140`'s vibrato is the same. So a naive reading of `FR-1600`'s gate — *"a non-chord tone does not arpeggiate"* → *"skip the per-frame write"* — would **silently delete portamento and vibrato on every weak melody onset**, which is where portamento matters most. | **High** (would be a real, audible regression in two shipped, verified features, introduced by a requirement written to improve a third) | Already mitigated in the requirement text: `FR-1600` states that sustaining means the frequency register **continues to be written every frame with that note's own pitch**, and never that the write stops. Carried forward as a named risk for `06`/`07`/`08` and as an explicit verification item — the check is that vibrato/portamento remain observable on a sustained (non-arpeggiating) note. No upstream change needed. |
| E2 | Verification-method change | `NFR-1270`, and every package that has claimed it | The amended basis invalidates the recorded figures of the one package that has claimed this NFR (`IP-1140`). | Medium-High | The corrected figures are stated in the NFR's own amendment text so no reader has to go looking. The three documents carrying the stale numbers (`IP-1140`'s package doc, the Master Build Plan row, `Claude.md`'s Known Good Behavior entry) are corrected by the stages that own them — this document does not reach into them. |
| E3 | Requirement made obsolete by measurement, not by design | `FR-1130` original wording | The original `FR-1130` passed every review it was ever given, and was correct when written. It became wrong when `FR-1500` was added, and no stage noticed — including this one, during the 2026-08-20 delta that *added* `FR-1500`. | Medium (process, not product) | A delta that adds a requirement introducing a new *source of truth* for something (here: what chord is sounding) should re-check every existing requirement that names the old source. Routed to this skill's own convention rather than to another stage; recorded so the next delta of this shape does the sweep. |
| E4 | Scope note, not a defect | `FR-1620` | The next-onset latency is stated as a requirement, but the underlying mechanism (a cache) is an implementation choice `ADS-108` §12.4 recommends and `NFR-1280` constrains by outcome. A different implementation meeting `NFR-1280` without a cache would not need `FR-1620`. | Low | `FR-1620` is baselined because the behavior is observable *and intended*, not because the cache exists. If a future implementation removes the latency while still meeting `NFR-1280`, `FR-1620` is amended in place, not violated. |

### Traceability

Per this project's recorded deviation (`BL-0068`/`GDS-10` §3.1) there is no separate matrix file to
update: backward traceability lives in each requirement's own *Traces to* column, and every row
touched above had its citation re-pointed at `ADS-108` §12/D14 and `ADR-0005` in the same edit that
changed its statement. ~~Forward traceability (`FS`/`IP`/`T`) is `UNASSIGNED` for `FR-1600`-`FR-1630`~~ **Corrected 2026-08-21 (`BL-0139`)**: `IP-1150` filled forward traceability in on every one of `FR-1600`-`FR-1630` (and `FR-1130`/`NFR-1280`) at the time it shipped; this sentence was true when written and stopped being true within the same day. `FR-1500`-`FR-1590`/`NFR-1240`-`NFR-1270` carried the opposite defect — implemented and tested but never annotated — and are filled in by this 2026-08-21 pass (`BL-0135`).
and `NFR-1280` until `05`/`06`/`07` run — no forward reference is invented here.

---

## Delta Review — 2026-08-21 (second pass: `FR-1070` amended, `ADR-0006`)

Scope: the delta only, per this skill's own delta-update rule — `FR-1070`/`FR-1420`/`FR-1630`
amended, `FR-1260`/`FR-1300`/`FR-1440` corrected, `FR-1560` reworded, `NFR-1270` amended a third
time, and forward traceability filled in for `FR-1500`-`FR-1590`/`NFR-1240`-`NFR-1270`.

### The finding this review exists for

| ID | Type | Requirements involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| **D1** | **Incomplete requirement as first drafted — caught here, before implementation** | `FR-1070`, `FR-1310`-`FR-1330` (song form), `FR-1230`-`FR-1260` (style) | **"Select stops reloading the five steering indices" is not a five-write change, and a literal reading of the original amendment would have shipped a half-broken control.** Tracing every write on the reset path against `GDS-04` §1.2's steering-index writer registry — which lists *song-form phase transition (`IP-1100`)* as an independent writer of `TEMPO_IDX` and `DENSITY_IDX` — finds **eight** writes to the six values `FR-1070` now protects, not five: the five `PRESET_*` writes, a `DUTY_BIAS` clear, **and a second `TEMPO_IDX`/`DENSITY_IDX` write from the song-form phase-0 row**, further down the same routine. Removing only the first group would leave a Select that preserves octave, scale and channel-mix while silently resetting tempo and density — the worst possible outcome, because it looks like it works. `FR-1070`'s clause (c) is therefore worded as *"by **every** write path, not merely by the direct one."* | **High** if it had reached implementation; **closed at requirements altitude** | None outstanding — the requirement now states it. Recorded in full because it is direct evidence for the registry's value: §1.2 has listed song form as a `TEMPO_IDX` writer since 2026-07-26, and consulting it is what turned a five-line change into an eight-line one. |
| **D2** | Conflict — pre-existing, newly load-bearing | `FR-1070` (amended), `FR-1310`-`FR-1330`, `GDS-04` §10 OQ3 | **The amended `FR-1070` makes "your settings survive" a stated promise, and song form still breaks it on a roughly-27-second timescale.** Song-form phase transitions autonomously overwrite `TEMPO_IDX`/`DENSITY_IDX` under `GDS-04` §1.2's last-write-wins contract — by design, `FR-1320`, and unchanged by this delta. So a listener's tempo and density survive a *Select* and are then overwritten by the *next phase transition* regardless. This is not a new defect and not introduced here: it is exactly `GDS-04` §10's Open Question 3 (*"a listener's manual tempo change can be silently overwritten seconds later by an autonomous phase transition… a listener-experience question this level cannot settle from evidence"*), which has been open since 2026-07-26 and has **never been content-reviewed**. What changes is its weight: it was a curiosity while Select discarded the settings anyway; it is a direct partial contradiction of a promise now that Select preserves them. | **Medium** (no requirement is violated — two baselined requirements simply pull against each other, both deliberately) | **Do not resolve here.** It is a `GDS-04`-level question and a listening question, not a requirements one, and resolving it unilaterally is exactly what this skill must not do. Escalated: `09-content-review` should evaluate it directly on the shipped reroll (does a phase transition feel like the engine breathing, or like the engine ignoring you?), and `03-architecture-design-synthesis` owns `GDS-04` §10 OQ3 if the answer is that it should change. Filed to the backlog by this run. |
| **D3** | Ambiguity resolved in place | `FR-1070` (amended), `FR-1230`-`FR-1260` | **`DUTY_BIAS` had no obvious home under "settings survive," and leaving it unstated would have been a coin-flip at implementation time.** It is not one of the five steering indices, so a literal reading of `ADR-0006` leaves it reset to 0; but it is derived from the style row that `CHMIX_IDX` selects, and `CHMIX_IDX` now survives — so resetting it would leave the engine's timbre bias disagreeing with the surviving preset that chose it. Resolved toward consistency: `FR-1070` clause (c) names `DUTY_BIAS` explicitly alongside the five indices. **It is listener-chosen state one derivation removed, and the line `ADR-0006` draws is about provenance, not about which table a value lives in.** | Low (resolved) | None. `T15.6` ("Select resets `DUTY_BIAS` to 0") must be re-authored against the new contract, not deleted — see D4. |
| **D4** | Missing verification / test-suite impact | `FR-1070`, `FR-1420`, `FR-1630` | **Six shipped checks assert precisely the behaviour being removed, and a seventh asserts a value that must now change.** Enumerated so no stage-07 package can claim it did not know: **`T5.2`/`T5.3`/`T5.4`** ("Select restores `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX` to preset") **invert** — they must assert *preservation*, and the setup that drifts the parameters first is exactly right and should be kept. **`T5.5`** must resolve chord 0's tones in **the listener's current scale**, not `PRESET_SCALE_IDX`. **`T15.6`** (`DUTY_BIAS` → 0) inverts, per D3. **`T17.8`** ("Select re-applies phase 0's `TEMPO_IDX`/`DENSITY_IDX` target values") **inverts and is the D1 canary** — it is the check that would have caught the eight-versus-five error, and it is currently green *because* the defect is the shipped behaviour. **`T18.9`/`T18.10`** (settings indicators reset on the Select frame, display catches up) invert. **Unaffected and must stay green as-is**: `T8.6`/`T8.7`/`T8.7b`/`T8.7c` (bad-zone clear), `T11.3`/`T11.5` (arpeggio/vibrato state), `T14.7` (motif step), `T17.7` (`SONG_STATE` → 0, which is retained), `T19.4` (VBlank on the Select frame), `T20.11`/`T20.12` (mood recompute — now a no-op, and must remain correct), `T22.12` (chord context), `T23.12` (arpeggio caches — which now additionally proves `FR-1630`'s strengthened half). | **Medium** (planned work, not a defect) | `07-implementation-planning` carries this enumeration into the package's `Tests to Add` field verbatim. **Every one of the seven is re-authored against the new contract, never loosened until it stops failing** — `IP-1140`'s record shows a loosened `T5.5` would have let a real off-by-one ship, and `T17.8` in particular must end up asserting the *opposite* of what it asserts today, not asserting nothing. |
| **D5** | Traceability gap closed | `FR-1500`-`FR-1590`, `NFR-1240`-`NFR-1270` | All thirteen requirements `IP-1140` covered were implemented and tested but carried **no** implemented-by/verified-by annotation, while `IP-1150`'s four carried full ones — the annotation convention post-dates `IP-1140` by one day. Filled in this pass from `VR-1140`'s own audit rather than from the package's claims. (`BL-0135`.) | Low (ledger, no coverage gap) | Closed. |
| **D6** | Doc-accuracy | 2026-08-21 Delta Review | Its closing line still read *"Forward traceability… is `UNASSIGNED` for `FR-1600`-`FR-1630`"*, which `IP-1150` falsified the same day. Corrected in place rather than deleted. (`BL-0139`.) | Low | Closed. |

### Placeholder-promotion guard — run, and it changed an answer

Run against every requirement this delta touches that constrains a concrete value.

- **`FR-1070` (amended) — passes, and passes *because* of the guard.** The requirement names no
  value at all now: it says the six listener-set values are *unchanged*, not what they should be.
  That is the relational form the guard prefers, and it arrived there for the guard's own reason —
  **the requirement being replaced is the exact failure the guard was written after.** `FR-1070`
  froze "the known-good preset" as Select's destination in run #1, when `BL-0005` had already
  recorded those preset values as untuned first guesses; the arbitrary destination then acquired
  the authority of a requirement purely by being written down, and stayed there for thirteen months
  after `IP-0007` removed its reason to exist. The amended form cannot rot the same way, because it
  no longer has a destination to be wrong about.
- **`FR-1630` (strengthened) — passes.** Constrains a *provenance* ("resolved from the listener's
  current values"), not a value.
- **`FR-1260`/`FR-1300`/`FR-1440` — pass, unchanged.** All three were already corrected to the
  relational fixed-point form on 2026-08-20; this pass touches only the name of the event that
  reaches index 0.
- **`NFR-1270` (amended) — passes.** Constrains the *method*, and deliberately still sets no
  numeric target: the harsh-interval percentages remain evidence to be reported, not a threshold to
  be met. Naming a threshold here would freeze a number `BL-0005`-class tuning is expected to move.
- **`FR-1560` (reworded) — passes.** Describes a structural relation (one slot above the published
  slot), not a value. Its unbuilt octave half is tracked at `BL-0136`, not frozen here.

### Checked and found not to conflict

- **`ADR-0006` vs. `GDS-04` §4.1.** No conflict: §4.1's second amendment was authored alongside
  the ADR, in the same run, precisely so this delta would not be amending requirements against a
  statement that had silently stopped being true. `FR-1260`'s "fixed-point" clarification, which
  cites §4.1 directly, remains correct word for word.
- **`ADR-0006` vs. `FR-1000`** (boot initializes to the known-good preset). No conflict — boot is
  untouched, and `FR-1000` is now the *only* requirement that puts the engine on the preset.
- **`ADR-0006` vs. `MSTR-001` §4 / `GDS-01`'s flat model.** No conflict, and no vision change: a
  button adds no menu state. `R217` §3a records the reasoning and the research grounding
  (regeneration is a parameterless single control across the product category; Playbeat's
  reroll-one-dimension-hold-the-rest is the direct analogue).
- **`FR-1590`** (bad-zone recovery does not override a strong-onset chord tone). Unaffected —
  Select clears the bad-zone fields, it does not change how recovery behaves.

### What is deliberately **not** in this delta

No new FR/NFR IDs. The amended `FR-1070` covers the whole redesign, and inventing
`FR-16xx`-series requirements for "reseed," "clear" and "preserve" separately would fragment one
control's contract across three rows for no traceability gain — the same reasoning `FR-1420` used
in 2026-07-31 to merge two candidates into one requirement.

