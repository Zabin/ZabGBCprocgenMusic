# R202 — Rhythm & Tempo Generation

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose

Ground the density/rhythm generation `IP-0003` will need (noise channel + the currently-unwired
`DENSITY_IDX` parameter), and the discrete-tempo-step design decision GDS-03 SS3 already made.

## 2. Scope

Euclidean rhythm generation (the concrete algorithm recommended for `DENSITY_IDX`'s eventual
consumer), and frame-driven tempo stepping on a fixed ~59.7Hz clock (R110).

## 3. Concepts

- **Euclidean rhythms**: distributing `k` onsets as evenly as possible across `n` steps, via the
  same structure as Euclid's GCD algorithm. Discovered/formalized for music by Godfried Toussaint,
  "The Euclidean Algorithm Generates Traditional Musical Rhythms" (Bridges 2005, pp. 47–56;
  extended version also published) — shown to reproduce a large family of real-world ostinato
  timelines from Sub-Saharan African, Cuban, Persian, and Turkish traditional music, all sharing
  the "distributed as evenly as possible" onset property [Toussaint 2005, extended PDF](https://cgm.cs.mcgill.ca/~godfried/publications/banff-extended.pdf); [Wikipedia — Euclidean rhythm](https://en.wikipedia.org/wiki/Euclidean_rhythm).
  This is exactly the algorithm GDS-03 SS3 already named for `DENSITY_IDX` ("Euclidean-gated noise
  hits") — this topic confirms that choice against real literature rather than leaving it an
  unsourced assertion.
- Two small integers (k onsets, n steps) is a minimal, cheap-to-recompute parameterization —
  changing `k` for a fixed `n` (Driftune's `DENSITY_IDX`) smoothly moves from sparse to dense
  without needing a stored pattern per density level, matching the "cheap on-device" constraint
  R110/R108 establish for anything computed every tick.
- **Tempo as a small discrete BPM table** (already implemented, `music_engine.TEMPO_BPM`) rather
  than continuous stepping is consistent with a frame-driven clock: at ~59.7Hz, tempo is
  necessarily quantized to `frames_per_beat = round(3600/bpm)` integer values anyway — a
  continuous "tempo dial" would alias to the same handful of achievable frame counts across most
  of its range, so discrete named steps lose little precision while being exactly-testable
  (MSTR-001 C9), which continuous stepping is not.

### Sources
- [Toussaint — The Euclidean Algorithm Generates Traditional Musical Rhythms (extended PDF)](https://cgm.cs.mcgill.ca/~godfried/publications/banff-extended.pdf)
- [Wikipedia — Euclidean rhythm](https://en.wikipedia.org/wiki/Euclidean_rhythm)
- [Bridges Archive — 2005 paper listing](https://archive.bridgesmathart.org/2005/bridges2005-47.html)

## 4. Operational Context

Not yet implemented in code (`IP-0003`'s scope). `music_engine.py`'s `DENSITY_IDX` (GDS-07 SS1)
is wired end-to-end at the input-mapping layer (`IP-0001`) but has no consumer yet — this topic
is exactly the grounding `IP-0003`'s implementation package should cite when it adds one.

## 5. Implementation Guidance

- **Concrete `IP-0003` recommendation:** fix `n` (steps per bar, e.g. 16, matching a sixteenth-
  note grid at the current tempo) and let `DENSITY_IDX` select `k` from a small table (e.g.
  `[2, 3, 4, 5, 6, 8, 10, 12]` onsets per 16 steps) computed via the standard Bjorklund/Euclidean
  bit-distribution algorithm — either precomputed per-`k` bit patterns in ROM (16 bits = 2 bytes
  per density level, cheapest) or computed once whenever `DENSITY_IDX` changes (still cheap:
  small integer loop, not a per-tick cost).
- Gate the noise channel's onset off this same bit pattern, and consider gating pulse/wave
  channel onset *density* (not just noise) off it in a later increment if `BL-0005`'s eventual
  listening pass finds density feels noise-channel-only otherwise — flagged as an open design
  question for `IP-0003`'s own FS, not decided here.

## 6. Feature Mapping

FR-1050 (D-pad/B density stepping, shipped), `IP-0003` (noise channel + density consumer, not yet
authored), `BL-0005` (tuning deferral).

## 7. Related Topics

R201 (pitch-generation half), R108 (noise channel has no pitch register — onset timing is its
only generative axis), R204 (channel-overload scoring reads the same onset-rate concept this
topic's Euclidean k/n directly controls).
