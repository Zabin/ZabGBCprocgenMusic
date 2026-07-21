# R209 — Game Boy Music Driver Survey

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 2, items 16-21 (Game Boy music drivers,
  hUGEDriver, GBT Player, RGBDS audio examples, LSDJ internals, Nanoloop concepts)

## 1. Purpose
Survey existing GB music playback systems for architectural precedent — Driftune's engine is
*generative*, not a player of authored songs, but the same hardware-driving discipline (how a
driver actually gets bytes into `NRxx` each frame) transfers directly.

## 2. Scope
hUGEDriver, GBT Player, LSDJ, and Nanoloop — four different points on the
complexity/compactness/live-editability spectrum for GB sound software.

## 3. Concepts
- **hUGEDriver**: a tracker-based, public-domain sound driver for GB homebrew, playable via two
  calls (`hUGE_init` with a song descriptor, then `hUGE_dosound` each frame) — positioned as a
  middle ground between LSDJ's complexity/CPU cost and GBT Player's compactness
  [SuperDisk/hUGEDriver README](https://github.com/SuperDisk/hUGEDriver/blob/master/README.md); [Larold's Retro Gameyard — Playing Music with hUGE Driver](https://laroldsretrogameyard.com/tutorials/gb/playing-music-in-game-boy-games-with-huge-driver/).
- **GBT Player**: a compact playback library plus MOD/S3M-to-GBT converters — you compose in an
  ordinary PC tracker, convert, and the GB-side library just plays the converted data; smaller
  and simpler than hUGEDriver/LSDJ, at the cost of less runtime flexibility [gbt-player GitHub](https://github.com/AntonioND/gbt-player/); [GB Studio — GBT Player docs](https://www.gbstudio.dev/docs/assets/music/music-gbt/).
- **LSDJ**: the most complex/capable — a full on-device tracker+sequencer (not just a playback
  library), used by professional chiptune musicians; correspondingly the heaviest of the three on
  CPU time [Synthtopia — Making Music On A Game Boy With LSDj](https://www.synthtopia.com/content/2016/05/06/making-music-on-a-game-boy-with-lsdj/).
- **Nanoloop**: a *step sequencer*, not a linear tracker — a 16-step grid with per-step control
  over every parameter (no separate "instrument" concept), closer in spirit to a classic
  drum-machine/groovebox (303/808 lineage) than sheet-music-style composition; its synthesis
  engine combines square-wave duty/pulse-width modulation, simple FM, a percussive "click"
  generator, and noise [Nanoloop 2.7.9 manual](https://www.nanoloop.com/two/nanoloop27.html).

### Sources
- [SuperDisk/hUGEDriver — README](https://github.com/SuperDisk/hUGEDriver/blob/master/README.md)
- [Larold's Retro Gameyard — Playing Music in GB Games with hUGE Driver](https://laroldsretrogameyard.com/tutorials/gb/playing-music-in-game-boy-games-with-huge-driver/)
- [AntonioND/gbt-player — GitHub](https://github.com/AntonioND/gbt-player/)
- [GB Studio — GBT Player](https://www.gbstudio.dev/docs/assets/music/music-gbt/)
- [Synthtopia — Making Music On A Game Boy With LSDj](https://www.synthtopia.com/content/2016/05/06/making-music-on-a-game-boy-with-lsdj/)
- [nanoloop.com — 2.7.9 manual](https://www.nanoloop.com/two/nanoloop27.html)

## 4. Operational Context
None of these are used by Driftune — it has no song *data* to play, only a live generation
routine. This survey is architectural precedent only.

## 5. Implementation Guidance
- **Driftune's `engine_tick`/register-write discipline already matches every one of these
  drivers' actual hardware-facing half** (a per-frame routine that decides new register values
  and writes them) — this is convergent design, not something to imitate further.
- **Nanoloop's "no separate instrument concept, every parameter set per-step" model** is the
  closest existing precedent to Driftune's own flat, per-note-decided approach (R201) — worth
  citing in `IP-0002`+'s FS as prior art for "a generative engine doesn't need a heavyweight
  instrument-abstraction layer to sound intentional."
- **Do not adopt a driver dependency** (hUGEDriver/GBT Player/LSDJ playback code) — Driftune's
  generation logic *is* the "song," there is nothing for an external player to play; pulling in
  one of these would be net-negative complexity for zero benefit.

## 6. Feature Mapping
Background/precedent only — no direct `IP-xxxx` dependency.

## 7. Related Topics
R210 (tracker formats/sequencing techniques these drivers implement), R216 (sound-design
techniques these drivers all support, some applicable to Driftune's own generation).
