# R223 — Audio-Visual Synchronization Conventions

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-26
- **Trigger:** `BL-0035` — MSTR-001 §9 (v1.2)'s still-open "audio-visual sync" thread (user's §17
  Audio-Visual Relationship: beat/melody/rhythm/harmonic/motion/color synchronization, intensity/
  emotional/structural mapping), bundled with `BL-0034` into `docs/roadmap/04-release-roadmap.md`'s
  R9 ("Visual Evolution & Audio-Visual Synchronization").

## 1. Purpose

Ground which of the engine's own generative state signals are the most reliable, well-precedented
targets for driving the visualizer, and what mapping conventions (discrete vs. continuous, which
audio dimension maps to which visual dimension) real music-visualization practice uses — so a
future sync feature maps *engine state Driftune already tracks* onto visuals, rather than
requiring new audio-analysis machinery (FFT, real-time beat detection) this project has never
needed and SM83 cannot cheaply afford.

## 2. Scope

Audio-to-visual parameter mapping conventions (pitch/timbre/intensity → color/motion), perceptual
tolerance for audio-visual lag, and which of Driftune's existing signals (onset events, tempo,
scale/mode, `DISSONANCE_SCORE`, `BAD_ZONE_FLAGS`) are the natural inputs. Excludes what visual
*states* exist to be driven (R222) and excludes real-time spectral audio analysis (out of scope —
Driftune generates its own audio deterministically from known state, it never needs to *listen to
its own output* to know what's playing).

## 3. Concepts

**Pitch is the most intuitive audio-to-visual mapping dimension in controlled studies of
cross-modal perception**, more intuitive than volume/duration for decoding structured data via
sound-to-visual mapping (general auditory-display/sonification research finding). This favors
`CUR_DEGREE_PA`/`PB`/`WV` (already-tracked scale-degree state) as a higher-confidence visual
driver than, say, raw onset count.

**Amplitude/timbre-to-intensity(brightness) mapping is a well-supported, general sonification
convention** — composed, deliberately-designed musical sound characteristics can be used to convey
intensity/brightness levels in a data-visualization context (general sonification-research
finding, corroborated across multiple independent sources found this pass). This directly
supports mapping `ONSET_WINDOW_COUNT`/density state to a visual-intensity axis (tile brightness or
animation rate), a signal Driftune already computes for `IP-9020`'s overload detection and could
reuse without new engine work.

**Perceptual sensitivity to color-channel changes is not uniform — green carries the most
perceived-brightness information per unit of change.** "The green color channel is often chosen as
human visual perception is more sensitive to contrasts in green since it has higher perceived
brightness than red or blue of equal power" (general color-perception/visualization-design
finding). This is directly actionable for CGB's own RGB15 palette format (R104): an
intensity-mapped visual signal should modulate the green channel preferentially, not scale all
three channels uniformly.

**Audio-visual synchronization is perceptually forgiving of small, consistent lag but sensitive to
inconsistency** — "human perception of rhythm is forgiving but sensitive to lag," and real
visualizers "compensate for processing delay by predicting beats or using beat-tracking algorithms
to anticipate timing" (general music-visualization-design finding). This directly corroborates
this project's own prior finding: `VR-0006` investigated a one-frame VBlank-write lag in the
shipped visualizer and judged it acceptable, self-healing, and not a defect — this topic confirms
that judgment matches the general literature's own tolerance threshold, not just this project's
own intuition.

### Sources
- General sonification/cross-modal-mapping findings (pitch as the most intuitive mapping
  dimension; amplitude/timbre-to-intensity mapping; green-channel perceptual sensitivity;
  lag-tolerance-with-consistency) — corroborated across multiple independent secondary sources
  found via search (auditory-display research on data sonification, color-perception literature,
  music-visualizer design writeups) but no single primary source was independently fetched this
  pass (WebFetch was unavailable for every attempted primary source in this research session).
  **Flagged needs fetch-verification** if a future pass wants primary-citation depth (e.g. the
  specific auditory-display papers on pitch-mapping intuitiveness, or the original green-channel
  perceptual-sensitivity study) beyond WebSearch's own synthesized summaries.
- Prior project evidence: [VR-0006](../../implementation/verification/VR-0006-minimal-visualizer.md)
  (the shipped one-frame VBlank lag, independently investigated and judged non-defective).

## 4. Operational Context

Every audio-side signal this topic recommends already exists in WRAM with no new generation logic
needed: `CUR_DEGREE_*` (pitch), `ONSET_WINDOW_COUNT`/`TEMPO_IDX`/`DENSITY_IDX` (intensity/rate),
`DISSONANCE_SCORE`/`BAD_ZONE_FLAGS` (already driving the shipped calm/bad-zone palette swap). This
is a read-and-map layer over existing engine state, the same "cheapest of the open threads" shape
R221 found for the emotional/energy mapping.

## 5. Implementation Guidance

- **Map pitch (scale degree) to a visual property before mapping amplitude/rate** — the citation
  base favors pitch as the higher-confidence, more-intuitive mapping; a future visualizer effect
  should prefer "tile color/position shifts with `CUR_DEGREE`" over "tile flashes with onset count"
  if only one new mapping can be built first.
- **Route any new intensity signal through the green channel preferentially** when writing CGB
  palette entries (`BCPS`/`BCPD`, R104) — a brightness-coded intensity map should scale green more
  than red/blue for the same perceived effect, concrete guidance for whoever eventually authors
  the palette math.
- **Do not build real-time audio analysis** (FFT, spectral beat-detection) — Driftune's engine
  already knows exactly what it is about to play one frame ahead (it generates the audio itself);
  every sync signal should read directly from engine WRAM state, never re-derive it by "listening"
  to the APU's own output, which would be redundant and SM83-cycle-expensive for no benefit.
- **A one-frame (or similarly small, consistent) sync lag is acceptable by the general
  literature's own tolerance threshold**, not just this project's own judgment — no VBlank-timing
  rework is motivated by this topic; `IP-0006`'s existing VBlank-gated write pattern (R102) is
  sufficient as-is.
- **Treat this as complementary to, not a replacement for, R222's palette-swap mechanism** — R222
  answers *what visual states exist*; this topic answers *which engine signal selects among them
  and how directly*. A shipped feature will need both.

## 6. Feature Mapping

No current `IP-xxxx`. Grounds `CAP-14` (Visual Engine)'s evolution tier and R9 alongside R222,
once picked up by `03-architecture-design-synthesis`.

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⚠️ **PARTIALLY TRACED — with one prior observation now corrected.** Audio-visual synchronization fed **[GDS-08](../../architecture/08-presentation-architecture.md)**, whose stateless re-render-every-frame contract is this topic's sync guidance made architectural, and it is one of the topics `ADS-104` drew on for `IP-1110`'s settings-indicator row (`VERIFIED`). Tempo-*synced motion* — a visual element whose timing follows the beat, the strongest form of the sync this topic describes — remains **unbuilt** and is recorded as Candidate Requirement `CR-0001` (`BL-0016`, `FR-1120`'s split). **Correction (2026-07-31, `BL-0069`):** this topic previously noted that `VR-0006`'s observed one-frame display lag sat comfortably inside the perceptual tolerance the literature describes. The *perceptual* claim stands and is unaffected — it is about human tolerance generally, not about this ROM. What has changed is that the one-frame lag this project kept observing was **not a real display lag at all**: it was a `pb.tick()` mid-frame sampling artifact in the harness (`R305` §3, `R308` §8.5). So the tolerance argument was sound but was being applied to a measurement that did not mean what it appeared to. Nothing in this topic's guidance changes; the example it was reassuring about was never real.

## 7. Related Topics

R222 (visual evolution conventions — the sibling half of the same roadmap release), R104 (CGB
palette system — RGB15/green-channel mechanics), R204 (bad-zone detection — the existing
`DISSONANCE_SCORE`/`BAD_ZONE_FLAGS` signals already driving the shipped visualizer), R205/R208
(existing visualizer conventions), R221 (emotional/energy mapping — a natural second-order signal
this topic's mappings could compose with), VR-0006 (the shipped lag finding this topic
independently corroborates).
