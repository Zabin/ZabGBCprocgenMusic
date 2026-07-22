# R205 — Generative Visualizer Conventions

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
  (lighter pass — grounds `IP-0006`/GDS-08, neither yet authored; deepen when that work starts)

## 1. Purpose

Ground the eventual visualizer (`visuals.py`, `IP-0006`, GDS-08 — none yet built) in real
audio-reactive-visual design convention, ahead of when it's actually specified.

## 2. Scope

Beat/tempo synchronization practice and palette-restraint convention from general audio-visual
design writing, translated to GBC's tile/palette constraints.

## 3. Concepts

- **Synchronization is the load-bearing property**: "accurate synchronization is critical —
  visuals must align with perceived rhythm, not just raw data... the strongest visualizers feel
  connected to the song rather than placed on top of it" [Interactive & Immersive HQ — Audio
  Reactive Visuals](https://interactiveimmersive.io/blog/technology/audio-reactive-visuals-and-how-to-use-them/).
  Directly actionable for GDS-08: the visualizer must read the *same* WRAM engine-state mirror
  (GDS-07) the engine itself updates on note-onset events (R108), not a separately-derived or
  approximated signal — any drift between "what's actually playing" and "what the visual shows"
  breaks exactly the property this source calls load-bearing.
- **Two visualizer architectures**: fully **procedural** (visuals computed from code/audio
  features each frame, maximum flexibility) vs. **template-based** (audio features modulate a
  predefined structure, lower complexity) [Echonos — Music Visualizer guide](https://echonos.ai/blog/music-visualizer-complete-guide).
  GBC's tile/palette model is inherently closer to template-based (a fixed tileset, animated by
  swapping tile indices/palette assignments per engine-state — not per-pixel procedural
  rendering), which is also the cheaper option for a VBlank-budgeted write, per R110.
- **Palette restraint**: "avoiding chaotic color palettes by sticking to 2-3 main tones per piece"
  [Interactive & Immersive HQ, same source as above] — directly relevant to CGB's 8 BG palettes
  (R208, not yet authored) being more than enough for a restrained design; the constraint here is
  taste-discipline, not hardware scarcity.

### Sources
- [Interactive & Immersive HQ — Audio Reactive Visuals and How They're Used](https://interactiveimmersive.io/blog/technology/audio-reactive-visuals-and-how-to-use-them/)
- [Echonos — Music Visualizer: Complete Guide to Audio-Reactive Visuals](https://echonos.ai/blog/music-visualizer-complete-guide)

## 4. Operational Context

Not yet implemented. `visuals.py` does not exist yet (`IP-0006`).

## 5. Implementation Guidance

- **GDS-08 (Presentation Architecture), when authored, should specify**: the visualizer reads
  `NR52` (channel-active) + the WRAM engine-state mirror only — never derives its own separate
  "is a note playing" signal (per the synchronization-is-load-bearing finding above, and
  consistent with R108's existing guidance that the WRAM mirror is the single readable source of
  truth).
- **Recommend a template-based (not per-pixel-procedural) visualizer**: a small set of prebuilt
  tiles, animated (which tile shown, which palette assigned) by engine state — cheapest to fit in
  the VBlank write budget (R110), and the architecturally natural fit for GBC's tile/palette
  hardware model.
- **Recommend limiting the active palette count** to 2-3 conceptually distinct "tones" (e.g. one
  hue family for calm/consonant state, a contrasting one for the bad-zone state) rather than
  using all 8 CGB BG palette slots decoratively — direct application of the palette-restraint
  convention above.

## 6. Feature Mapping

FR-1120 (visualizer reads engine state, read-only), `IP-0006` (not yet authored), GDS-08 (not yet
authored).

## 7. Related Topics

R108 (the WRAM mirror + NR52 this topic says the visualizer must read), R208 (now authored — CGB
palette mechanics plus a new accessibility finding on the shipped calm/bad-zone palette's
luminance gap), R110 (VBlank write-budget constraint favoring a template-based approach).
