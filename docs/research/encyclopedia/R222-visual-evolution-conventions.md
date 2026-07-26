# R222 — Visual Evolution Conventions

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-26
- **Trigger:** `BL-0034` — MSTR-001 §9 (v1.2)'s still-open "visual evolution" thread (user's §16
  Visual Evolution: theme/palette/animation evolution, environmental/time-of-day/seasonal themes,
  music/mood/tempo/style-reactive visuals), named as a standing prerequisite by
  `docs/roadmap/02-capability-map.md`'s CAP-14 row and `docs/roadmap/04-release-roadmap.md`'s R9.

## 1. Purpose

Determine whether Driftune's visualizer (`visuals.py`, currently a fixed 4-tile channel-activity
display plus a 2-palette calm/bad-zone swap, `IP-0006`/`FEAT-1040`) can evolve its presentation
over time/style/mood **without a fundamentally new rendering mechanism** — i.e. whether the
cheapest real convention for "visual evolution" on constrained retro hardware is additional tile
art, or something already within the shipped palette-swap primitive.

## 2. Scope

Classic 8/16-bit palette-swap and color-cycling techniques for dynamic presentation (day/night,
seasonal, mood); how CGB's own palette system (R104) fits this convention; what a richer
reactive palette set would cost in VRAM/ROM (handed to `02-research-gbc-hardware`, not this
topic). Explicitly excludes audio-to-visual *synchronization* mapping (R223) — this topic is
about *what visual states exist and how they're switched*, not *what triggers the switch*.

## 3. Concepts

**Palette swapping — not new tile art — is the standard, cheapest technique for dynamic
presentation on indexed-color retro hardware.** "Palette swapping is a technique that works by
changing the color mappings of an indexed image... you can change the color that each number
corresponds to dynamically, which causes all the corresponding areas in the image to change too"
[GB Studio Central — Palette Swapping](https://gbstudiocentral.com/tips/palette-swapping/). This
is exactly Driftune's own shipped mechanism (`visuals.py`'s calm/bad-zone `_emit_write_palette`
swap, `IP-0006`) — evolution doesn't need a new primitive, it needs more palette entries and a
selection rule.

**Day/night and seasonal cycling via palette swap alone is an established, named convention on
exactly this class of hardware.** "You can combine variables with palette swapping to create day
& night cycles. A practical example comes from Pokemon Gold/Silver, where a day/night cycle...
can be implemented using just palette swap by replacing the palette and loading the new palette to
replace the tilemap palette" [GB Studio Central — Palette Swapping]. Pokemon Gold/Silver is a
real, shipped GBC title using this exact technique — direct hardware-precedent, not a
cross-platform generalization.

**Color cycling (not just discrete swapping) is the classic 8-bit technique for continuous
environmental animation** (water, fire) without redrawing tiles: "Color cycling was a technology
often used in 8-bit video games of the era, to achieve interesting visual effects by cycling
(shifting) the color palette. Most games used the technique to animate water, fire or other
environmental effects" [Prototypr — Color Cycling in Pixel Art](https://blog.prototypr.io/color-cycling-in-pixel-art-c8f20e61b4c4). This is a candidate mechanism for a continuously-drifting
(not just binary calm/bad-zone) mood palette, if a future style/emotion signal (R221) wants a
gradient rather than a discrete state.

**Palette color choice for mood/atmosphere is a deliberate, evidence-referenced design choice in
generative visual art generally**, not an arbitrary aesthetic pick: "Color palettes in generative
artworks are carefully selected to reflect the mood and atmosphere, ranging from warm earthy tones
to cool blues" (general generative-art-design convention). This supports treating Driftune's own
palette table (`CALM_PALETTE`/`BAD_PALETTE`, already grounded by R208's Helmholtz/warning-color
citations) as the correct place to extend, not a place to redesign.

### Sources
- [GB Studio Central — Palette Swapping](https://gbstudiocentral.com/tips/palette-swapping/)
- [Prototypr — Color Cycling in Pixel Art](https://blog.prototypr.io/color-cycling-in-pixel-art-c8f20e61b4c4)
- General generative-art palette/mood convention: multiple secondary sources agree but no single
  authoritative primary source was independently fetched this pass (WebFetch was unavailable for
  every attempted primary source in this research session — flagged **needs fetch-verification**
  if a future pass wants primary-source depth beyond WebSearch's own summaries).

## 4. Operational Context

Driftune already ships the two building blocks this convention needs: a working
`_emit_write_palette` palette-swap mechanism (`IP-0006`) and a table of engine state that could
select among more than 2 palettes (`TEMPO_IDX`/`SCALE_IDX`/`CHMIX_IDX`, plus R221's not-yet-built
valence-arousal derivation). No VBlank-timing change is implied — palette writes are already
correctly VBlank-gated (R102/R103).

## 5. Implementation Guidance

- **Extend the existing 2-entry palette table, don't build a second rendering path.** A "visual
  evolution" feature should add N palette entries selected by a small index (style/mood-region,
  time-elapsed-in-session, or an R221-derived valence bucket) written through the same
  `_emit_write_palette` call site `IP-0006` already established — this is a data-table extension
  plus a selection rule, the same shape as `CHMIX_MASKS`/`ARPEGGIO_OFFSETS`-style additions this
  project already has a proven pattern for.
- **Day/night or seasonal theming needs no new tile art** — Pokemon Gold/Silver's own precedent is
  palette-only. A ROM-budget-conscious first version should treat "environmental/time-of-day
  themes" (user's §16) as additional palette rows, not additional tiles, keeping this within
  `02-research-gbc-hardware`'s eventual VRAM-budget answer (`BL-0034`'s hardware half).
  "Real-time playback duration" (session-elapsed time, not wall-clock) is the natural
  time-of-day-style axis Driftune can access without an RTC, since GBC has no MBC3-style
  real-time clock this project has adopted (per `ADR-0002`'s single-bank, no-MBC decision).
- **Color-cycling (continuous palette shift) is the concrete mechanism for a smooth mood *drift***
  rather than a binary state, if R221's valence-arousal output or R220's style-drift state machine
  ever wants a continuous (not discrete) visual response — recommended as the follow-up technique
  once a discrete-state version ships and is judged too abrupt.
- **Do not invent a bespoke "visual mood taxonomy"** — same discipline R221 §5 already recommends
  for the *emotional* taxonomy: named visual themes (§16's "seasonal themes," "time of day") should
  be regions of the same underlying palette-selection index, not independent parallel mechanisms.

## 6. Feature Mapping

No current `IP-xxxx`. Grounds `CAP-14` (Visual Engine)'s "evolution" tier and
`docs/roadmap/04-release-roadmap.md`'s **R9 — Visual Evolution & Audio-Visual Synchronization**
once `02-research-gbc-hardware` supplies the VRAM/palette-budget half (`BL-0034`'s remaining
scope) and this topic's own palette-swap approach is carried into
`03-architecture-design-synthesis`.

## 7. Related Topics

R104 (CGB palette system — the hardware mechanism this topic reuses), R205/R208 (existing
visualizer/palette conventions — the shipped baseline this topic extends), R221 (emotional/energy
mapping — the most natural driver of a palette-selection index), R220 (style-evolution/song-form —
an alternate driver), R223 (audio-visual synchronization — the sibling topic on *what triggers* a
visual change, as opposed to this topic's *what visual states exist*).
