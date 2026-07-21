# R203 — Voice-Leading & Density Control Across a Fixed Small Channel Count

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose

Ground how `IP-0002`/`IP-0003` should keep up to four independently-generating channels from
masking or clashing with each other, feeding directly into R204's channel-overload signal and
R207's per-channel role recommendation.

## 2. Scope

Masking/clutter risk when multiple independent generative voices run concurrently on a
channel-starved chip, and why per-channel role differentiation (R207) and a hard density ceiling
(R204's overload signal) are the two load-bearing mitigations available to this project.

## 3. Concepts

- With only four channels, none disposable to "just harmony padding," every channel's generative
  independence (R201: each has its own LFSR/timer/degree state) is also a clutter risk once more
  than one channel is active — four independently-walking melodic voices with no role
  differentiation is the literature-and-convention-confirmed failure mode R207 already names
  (chiptune convention explicitly assigns *different* roles — melody/bass/percussion — precisely
  because undifferentiated concurrent voices on a small channel count reads as noise rather than
  arrangement) [Soundfly — Chiptune Crash Course: Arranging in Four Channels](https://soundfly.com/courses/arranging-in-four-channels).
- General audio-visualizer design literature (R205) separately notes generic "avoid chaotic...
  stick to 2-3 main tones" guidance for *visual* clutter — the same *shape* of constraint (a small
  fixed number of simultaneously-active "channels" of attention, human perceptual limits on
  tracking more than a few independent concurrent streams) applies by direct analogy to the
  *audio* side: channel-overload (GDS-03 SS4c) is this project's own concrete operationalization
  of that same general principle for sound rather than sight.

### Sources
- [Soundfly — Chiptune Crash Course: Arranging in Four Channels](https://soundfly.com/courses/arranging-in-four-channels)
- (Cross-reference only, no new citation): R205's visualizer-clutter sources, cited there.

## 4. Operational Context

Not yet implemented — `IP-0001` only drives one channel, so no cross-channel masking is possible
yet. This topic's guidance is forward-looking for `IP-0002` (two more channels join) and `IP-0004`
(the overload signal that operationalizes this concern).

## 5. Implementation Guidance

- **`IP-0002`'s FS should adopt R207's role differentiation** (melody/bass, not two identical
  melodic walks) as its primary anti-masking mechanism — cheaper and more musically motivated than
  a runtime "clash detector" between pulse A and pulse B.
- **`CHMIX_IDX`'s preset table (GDS-03 SS3, not yet populated with real values) should include at
  least one low preset with only 1-2 channels active**, not just "all four" as the top of the
  range — this gives the density/mix dimension real headroom on the sparse end, consistent with
  R202's Euclidean-density spread and avoiding a mix table that's accidentally biased toward
  "more is denser/busier" only.
- **`IP-0004`'s overload threshold (R204... wait, GDS-03 SS4c)** should be derived from the
  *combination* of all active channels' own tempo/density presets at their fastest settings
  (already noted as an open derivation in GDS-03 SS4c) — this topic confirms that derivation
  approach is the right one (a literature-grounded fixed constant independent of the preset
  tables would either be too loose to ever trip, or would false-trip at legitimate dense-but-
  intentional preset combinations).

## 6. Feature Mapping

`IP-0002`/`IP-0003` (channel role assignment), `IP-0004` (overload threshold derivation), GDS-03
SS4c.

## 7. Related Topics

R207 (the role-differentiation mechanism this topic recommends as primary), R204 (the overload
signal this topic's threshold-derivation guidance feeds), R205 (the analogous visual-clutter
principle this topic's audio framing borrows from).
