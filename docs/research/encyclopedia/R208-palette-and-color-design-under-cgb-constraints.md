# R208 — Palette & Color Design Under CGB Constraints for a Non-Game Display

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-22
  (deferred pending `IP-0006`/GDS-08 — `IP-0006` has since shipped and is independently `VERIFIED`;
  GDS-08 remains unauthored, `BL-0001` — this topic grounds the shipped `visuals.py` design ahead
  of that formal architecture pass, same as R102-R104 did for the hardware layer)

## 1. Purpose
Deepen R205 SS5's palette-restraint sketch into concrete guidance for `visuals.py`'s actual
two-palette design (`CALM_PALETTE` vs. `BAD_PALETTE`), and check that design against real
color-semiotic and accessibility convention rather than only against CGB's technical constraints.

## 2. Scope
Color semiotics for a state-indicator display (not a game world — no diegetic color meaning to
respect), CGB's RGB555 8-BG-palette hardware ceiling (already covered in depth by `R104`), and
color-vision-deficiency accessibility.

## 3. Concepts
- **Red-for-warning/green-for-calm is a strong, near-universal UI convention**: red is "the
  universal color for errors and warnings, leveraging its association with danger to capture
  attention," while green "universally signals success... and positive actions" [Medium/Bootcamp —
  Color Psychology in UX/UI Design](https://medium.com/design-bootcamp/the-psychology-of-colors-in-ux-ui-design-e66eabe40799).
  This is the exact semantic pairing `visuals.py`'s `CALM_PALETTE` (blue/green) vs. `BAD_PALETTE`
  (red) already uses — the shipped design independently landed on a real, well-established
  convention rather than an arbitrary one.
- **Restraint is the load-bearing discipline for pixel/tile-based palettes**: retro pixel art's
  entire aesthetic is a *response to* hardware color limits, and deliberately staying restrained
  (2-4 tones) is what makes a limited palette read as cohesive rather than cheap
  [ResetEra — Appreciating the Game Boy Color art palette](https://www.resetera.com/threads/appreciating-the-game-boy-color-art-palette-demonstration-of-how-limitations-can-create-cohesive-art-styles.598782/).
  This directly reinforces R205 SS5's "2-3 tones" recommendation — restraint is convention, not
  merely a fallback for scarce hardware (CGB has 8 BG palettes available; the shipped design uses
  only 1, by choice, not by necessity).
- **Red/green as the *only* distinguishing signal is a known accessibility hazard**: red-green
  color vision deficiency (protanopia/deuteranopia) affects a meaningful fraction of viewers (most
  commonly cited as ~8% of men), and the standard mitigation is to swap red-green pairs for
  blue-orange, or ensure a **luminance** difference survives even when hue doesn't
  [WebAIM — Visual Disabilities: Color-blindness](https://webaim.org/articles/visual/colorblind);
  [Colblindor — Deuteranopia](https://www.color-blindness.com/deuteranopia-red-green-color-blindness/).
  "Focus on the lightness of the color rather than the hue... even if two colors look similar in
  hue, their lightness difference will remain distinct."

### Sources
- [Medium/Bootcamp — The Psychology of Colors in UX/UI Design](https://medium.com/design-bootcamp/the-psychology-of-colors-in-ux-ui-design-e66eabe40799)
- [ResetEra — Appreciating the Game Boy Color art palette](https://www.resetera.com/threads/appreciating-the-game-boy-color-art-palette-demonstration-of-how-limitations-can-create-cohesive-art-styles.598782/)
- [WebAIM — Visual Disabilities: Color-blindness](https://webaim.org/articles/visual/colorblind)
- [Colblindor — Deuteranopia, Red-Green Color Blindness](https://www.color-blindness.com/deuteranopia-red-green-color-blindness/)

## 4. Operational Context
`visuals.py:43-44` (`R104`'s own operational-context section already confirms the `rgb15()`
encoding is correct): `CALM_PALETTE = [rgb15(0,0,0), rgb15(0,8,16), rgb15(4,16,24),
rgb15(10,28,20)]` (color index 3, the "on" tile color, is green-dominant: R10/G28/B20) vs.
`BAD_PALETTE = [rgb15(0,0,0), rgb15(16,0,0), rgb15(24,4,4), rgb15(31,10,6)]` (index 3 is
red-dominant: R31/G10/B6). Computing approximate perceived luminance (`0.3R + 0.59G + 0.11B` on
the shared 0-31 5-bit scale) for each palette's "on" color: **CALM idx3 ≈ 21.7, BAD idx3 ≈ 15.9**
— a real but modest (~27%) luminance gap. This means the design is **not** relying on hue alone
(there is a genuine brightness difference a red-green-colorblind viewer would still perceive),
but the gap is narrow enough on a small GBC screen that it may not read clearly at a glance —
this was not evaluated against accessibility convention when `IP-0006` shipped.

## 5. Implementation Guidance
- **The existing red/calm semantic choice is correct convention** — no change needed to which
  hue family means what.
- **The existing single-BG-palette restraint (1 of 8 available) is correct convention**, not
  merely acceptable — R205's "2-3 tones" guidance is satisfied by design, and GDS-08 (when
  authored) should preserve this restraint rather than treating the 8-palette ceiling as
  something to use up.
- **New finding for `visuals.py`/GDS-08**: the calm-vs-bad-zone luminance gap (~21.7 vs ~15.9 on
  the 0-31 scale) is real but narrow — a future visualizer revision should widen it (e.g. push
  `CALM_PALETTE`'s idx3 brighter, `BAD_PALETTE`'s idx3 darker, or add a second distinguishing
  signal such as a distinct "on" tile shape for the bad-zone state rather than only a palette
  swap) so the state reads clearly under red-green color vision deficiency, not only to
  full-color vision. This is genuinely new — nothing in `R205`, GDS-03, or the `IP-0006` package
  doc considered accessibility, and no test/VR checked for it (palette correctness was verified
  via rendered-pixel hue comparison in `VR-0006`, which doesn't test luminance-only legibility).
- Any future multi-scheme visualizer work (`BL-0020`) that adds more visual states must apply the
  same luminance-not-just-hue discipline from the start, rather than accumulating more
  hue-only-distinguished states.

## 6. Feature Mapping
FR-1120 (visualizer bad-zone-reactive palette), GDS-03 §6 (visualizer design intent), R205 SS5
(palette-restraint principle this topic deepens).

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** Grounds `visuals.py`'s red/calm bad-zone palette semantic and its single-palette restraint, confirming both against real CGB colour-design convention rather than taste. Shipped via `IP-0006` (`VERIFIED`). Requirements: `FR-1120`. **Carries one open forward thread**: this topic surfaced the accessibility finding that a state distinction should not rest on colour alone (`BL-0021`), which `GDS-08` §4.3 accepted at design altitude and which remains **unbuilt** — an honest partial, not a clean full trace.

## 7. Related Topics
R104 (CGB palette register mechanics — the "how," where this topic is the "what color and why"),
R205 (generative visualizer conventions this topic deepens specifically for color).
