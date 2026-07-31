# GDS-08 — Presentation Architecture

- **Level:** GDS-08 of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26
- **Upstream:** [GDS-04 Domain Model](04-domain-model.md) (§8's indicator entity),
  [GDS-07 Data Model](07-data-model.md) (§9's tile/tilemap layout), research `R104` (+ its §7-8
  budget addendum), `R205`, `R208`, `R222`, `R223`, `R303`
- **Downstream:** any future visualizer `FS-xxx`; the four deferred reactive-signal questions
  `ADS-104` §9 unified, which this level now places architecturally (§6)
- **Closes at design altitude:** `BL-0001`'s long-standing "GDS-08 rides with the visualizer
  work" disposition; addresses `BL-0016` (§7) and `BL-0021` (§4.3)

## §0 Authored late, and better for it

`BL-0001` scheduled this level to ride with `IP-0006` back in run #1. It did not — `IP-0006`
shipped, then `IP-1110` shipped, and only now is the level being written. That delay turned out to
be an advantage rather than a cost: authoring GDS-08 before `IP-0006` would have produced a
forward synthesis of a visualizer nobody had built, and the two things this level can now say
that matter most — the stateless re-render contract (§5) and the indicator mechanism's
extensibility (§6) — are both conclusions drawn *from* two shipped packages, not predictions
about them.

Like GDS-02/04/06, this level describes the presentation layer **as built and measured**.

## §1 What the presentation layer is

**One BG tilemap and one BG palette. That is the entire visualizer.**

Everything the listener sees is produced by choosing which tile index appears in nine fixed
tilemap cells, and which four colors currently occupy BG palette 0. There is no other mechanism.

| Element | Count | Bound to | Package |
|---|---|---|---|
| Channel-activity cells | 4 | each channel's `NR52` active bit | `IP-0006` |
| Settings-indicator cells | 5 | `TEMPO_IDX`/`OCTAVE_IDX`/`SCALE_IDX`/`DENSITY_IDX`/`CHMIX_IDX` | `IP-1110` |
| Tile patterns | 10 | 2 on/off + 8 bar fill levels | `IP-0006`/`IP-1110` |
| BG palettes in use | 1 (palette 0) | swapped between calm and bad-zone color sets | `IP-0006` |

### §1.1 What it deliberately does not do

Naming these matters because each is an investment the project has *chosen* not to make, and each
would be easy to assume exists:

- **No sprites, no OAM, no DMA.** The visualizer never touches the sprite system at all. Every
  pixel is background. This is why `R105` (OAM/sprites/DMA) has no forward trace into shipped
  code — a real `MSTR-001` C10 exception rather than an oversight.
- **No text or font rendering.** There is no glyph table and no string drawing anywhere in the
  ROM. `ADS-104` considered and rejected building one for the settings legend, on the grounds
  that a font is a disproportionate new capability to add for a labelling problem a printed
  manual solves for free. The consequence is honest and worth stating: **the ROM cannot explain
  itself.** A listener sees five bars and must be told, externally, which is which.
- **No second VRAM bank, no per-tile palette attributes.** Using more than palette 0 requires
  writing tilemap attribute bytes in VRAM bank 1 via `VBK` — "a new mechanism this project's code
  has never exercised" (`R104` §5). Every visual state instead swaps palette 0's contents
  wholesale.
- **No animation with its own timebase.** Nothing tweens, fades, or scrolls. There is no frame
  counter driving motion independent of engine state (§5 explains why this follows structurally).

## §2 Composition

The nine cells occupy one contiguous run at the top-left of the tilemap: four channel-activity
cells, then five settings indicators immediately after. GDS-07 §9 owns the exact addresses; the
architectural points are that the layout is **static** (assigned at build time, never computed at
runtime), **contiguous** (so a future addition extends the run rather than scattering), and
**tiny** — nine cells of a 32×32 grid, using 10 of 256 available tile slots (`R104` §7).

**Two visual vocabularies coexist**, and the distinction is deliberate:

- **Binary presence** (channel activity): a cell is on or off. The question it answers is "is this
  voice sounding right now?" — inherently boolean.
- **Proportional magnitude** (settings): a bar filled 0–7 rows from the bottom. The question is
  "how much of this parameter is dialled in?" — inherently ordinal.

`R205`'s "a number becomes a shape" convention is what the second vocabulary implements. Keeping
them visually distinct (solid block vs. partial bar) means the two rows read as different kinds of
information without any labelling, which is the only self-explanation the display has (§1.1).

## §3 The sync scheme — and why it is stateless

**Contract: every frame, read current engine state and re-render every cell from scratch.**

There is no event system, no dirty-flag tracking, no invalidation, and no incremental update. The
visualizer does not know that anything changed; it simply recomputes all nine cells and the
palette from the current values, every single frame, forever.

This follows `R223`'s explicit guidance — Driftune generates its own audio and therefore already
knows exactly what it is about to play, so every sync signal reads directly from engine WRAM
rather than analysing output (no FFT, no beat detection, which would be redundant and expensive).
It also follows `R205`'s "the visualizer reads `NR52` + the WRAM mirror only, never derives its
own separate signal."

**Three consequences, all load-bearing:**

1. **The presentation layer holds no state of its own.** Nothing to initialize beyond boot, nothing
   to keep consistent, no possibility of the display and the engine disagreeing about what changed.
2. **It is self-healing.** This is not a nicety — it is the specific reason `IP-1110`'s disclosed
   Select-frame dropped write is a cosmetic one-frame artifact rather than a persistent
   corruption. A dropped write under an event-driven design would leave the cell wrong until the
   next event; under re-render-every-frame the very next frame repairs it unconditionally. The
   architecture absorbed a real timing failure without anyone having designed for that case.
3. **The cost is a fixed per-frame floor.** Nine reads and nine writes happen every frame whether
   anything changed or not. At current scale that is trivially affordable — but it is *not* free,
   and GDS-06 §2.2 records that the frame budget is tighter than assumed on at least one frame
   class. A future presentation feature that adds many cells inherits this multiplication.

**Sync lag is one frame at most**, and `R223` records that a small consistent lag is within the
general literature's own tolerance threshold — no rework is motivated.

## §4 Palette strategy

### §4.1 Two semantic states, one palette

Palette 0 holds four colors and is rewritten each frame with one of two sets: a calm blue/green
family, or a bad-zone red family, selected by the bad-zone combined flag. `R205` recommended
exactly this restraint — 2–3 conceptually distinct tones rather than decorating with all eight
CGB palette slots — and the shipped design follows it.

The calm/bad red semantic follows the near-universal warning-color convention (`R208` §3), so the
hue choice is grounded rather than arbitrary.

### §4.2 Why palette-swap is the extension mechanism

`R222` is unambiguous that future visual variety (themes, mood, time-of-session drift) should
extend the palette table rather than add a second rendering path or new tile art — and `R104` §7
quantifies why that is comfortable: each palette is 8 bytes, so six additional theme palettes cost
48 bytes, "under 0.2% of the *free* headroom." The mechanism already exists (`_emit_write_palette`);
a theme is a data row plus a selection rule, the same shape as every other table this project has.

**This level adopts that as the standing extension strategy**: new visual states are palette rows
selected by an index. Anything proposing a second rendering path, per-tile palette attributes, or
VRAM bank 1 needs to justify crossing a mechanism boundary the project has deliberately never
crossed.

### §4.3 Accessibility — `BL-0021`, addressed at design altitude

`R208` computed the perceived luminance of the two "on"-tile colors: calm ≈ 21.7, bad ≈ 15.9 on a
0–31 scale — a real but narrow ~27% gap. The concern `BL-0021` raised is that red-green color
vision deficiency affects a meaningful fraction of viewers, and a calm/bad distinction carried
*primarily* by hue with only a modest luminance difference may not read at a glance for those
viewers.

**This level's position:** the concern is valid and the current design is weaker than it should
be, but the right fix is **not** primarily a palette adjustment.

The principle: **a state distinction should never be carried by color alone.** Widening the
luminance gap (the obvious fix) helps, and is cheap, but still leaves color as the sole channel.
The structurally better answer is a **second, non-color signal** for bad-zone state — a distinct
tile shape, since the tile budget is effectively unlimited (10 of 256 slots used, `R104` §7) and
the display already uses shape as a vocabulary for magnitude (§2). A bad-zone state that changes
*what the cells look like*, not only what color they are, is legible regardless of color vision.

Recorded as design guidance rather than a decision, because choosing the actual shape is a
content-authoring judgement (`08-content-authoring`) and the legibility outcome needs
`09-content-review`'s eye. `BL-0021` stays open with that direction attached; this level's
contribution is the principle and the observation that the tile budget makes the better fix
affordable.

## §5 Presentation is strictly downstream — the read-only invariant

`visuals.py` never writes engine state. GDS-03 §1 established this as a module-boundary rule; the
16-package integration review confirmed it structurally by checking that every write in the module
targets VRAM, the palette ports, or `LCDC` — never a `0xC0xx` engine field, never a PSG register.

Architecturally this means **presentation can never be the cause of a musical behavior**. A
visualizer bug can make the display wrong; it cannot make the music wrong. That one-way dependency
is what allowed `IP-1110` to add five new per-frame cells to a shipped, verified engine with the
only integration risk being a timing one (§3.3) rather than a correctness one.

## §6 The four deferred reactive signals — placed, not scattered

Four separate feature specs each independently raised the same question and each deferred it
identically: should the visualizer gain a signal reactive to *this* feature? — `FS-107`
(generation scheme), `FS-108` (style identity), `FS-109` (motif variant), `FS-110` (song-form
phase). `ADS-104` §9 unified them into one deferred follow-on. This level places them
architecturally so that a future increment picks up a design rather than four loose threads.

**All four are the same shape**: an engine state value, small and enumerable, that a listener
currently cannot observe. Two mechanisms already exist that could carry them, and the choice
between them is the actual design question:

| Mechanism | Fits | Cost |
|---|---|---|
| **Another indicator cell** (§2's proportional-magnitude vocabulary, `IP-1110`'s bar tiles reused verbatim) | motif variant (0–3), song-form phase (0–3) — both are ordinal-ish small indices | 1 tilemap cell each, 0 new tiles |
| **A palette theme row** (§4.2's extension strategy, `R222`) | style identity, song-form phase — both are "the whole piece feels different now" states | 8 bytes each, 0 new tiles or cells |

**This level's architectural guidance:**

1. **Scheme selection should probably not get a signal at all.** It is per-channel, and the
   display has no per-channel real estate beyond the activity cells. Its listener-visible effect
   (patterned vs. drifting melody) is already audible. Adding a cell for it would cost real estate
   for the least legible of the four.
2. **Motif variant is the weakest candidate of the remaining three.** It changes at most every
   eight motif steps and its effect is a subtle contour difference; a bar that occasionally ticks
   between four values communicates little. Build it last, if at all.
3. **Song-form phase is the strongest candidate**, and it is the one that genuinely wants
   *both* mechanisms: a phase is simultaneously an ordinal position (indicator) and a whole-piece
   mood (palette theme). `R222`'s color-cycling note is directly relevant if the phase transition
   should read as a drift rather than a snap.
4. **Style identity is the natural first palette theme** — it is already a coordinated
   whole-ensemble change (GDS-04 §1.3), so a matching whole-screen color change is the honest
   visual analogue.

None of this is a commitment. It is the placement the four scattered questions never had.

## §7 `FR-1120`'s tempo claim — `BL-0016`, resolved honestly

`FR-1120` requires the visualizer to "represent tempo, per-channel activity, and bad-zone status."
`VR-0006` found in run #11 that tempo was represented nowhere — `visuals.py` did not read
`TEMPO_IDX` at all. That was true and remained true for fifteen packages.

**It is now partly true.** `IP-1110`'s first indicator cell is bound to `TEMPO_IDX` and renders it
as a proportional bar. A listener can now see the tempo *setting*.

**But `FR-1120`'s wording sits in a family that implies something else.** Read alongside
"per-channel activity" (which updates as notes sound) and in the context `R205`/`R223` establish
(audio-visual synchronization), "represent tempo" reads naturally as *tempo-synced motion* —
something pulsing at the beat — not as *a numeric tempo setting displayed as a bar*. `IP-0006`'s
own package doc named "tempo-synced motion" as its explicit non-scope, which confirms that reading
was the original intent.

**This level's honest resolution, three parts:**

1. `TEMPO_IDX` **is** now represented, and any claim that tempo is entirely absent from the
   display is out of date.
2. Tempo-**synced motion** — a visual element whose timing follows the beat — **does not exist**
   and remains unbuilt and unscheduled.
3. Therefore `FR-1120` is **satisfied on a narrow reading and overstated on the natural one**,
   and the wording should be split so a reader cannot mistake which is shipped.

The fix is `04-requirements-engineering`'s to make, not this level's — a ladder level does not
edit the requirements baseline. `BL-0016` stays open with this resolution recorded as its input,
and the recommended split is: keep the setting-display claim (now true, traced to `FR-1350`'s own
indicator requirement), and move the synced-motion claim to an explicitly-unbuilt candidate.

## §8 Open Questions

1. **Should bad-zone state gain a non-color signal?** §4.3's principle says a state distinction
   should not rest on color alone; the tile budget makes a shape-based signal affordable. Not
   decided here — the shape is a content-authoring choice and the legibility outcome needs
   review. Owner: `08-content-authoring` for the shape, `09-content-review` for the judgement.
2. **Which of the four deferred signals (§6), if any, is actually wanted?** This level ranks them
   and names the mechanism each would use, but whether the display *should* grow at all is a
   product question about how much the visualizer is meant to say. Owner: `01-vision` or a future
   `00-intake` request; `03` can design it once the appetite is known.
3. **Does the fixed per-frame render floor (§3.3) need a stated ceiling?** Nine cells is free;
   thirty might not be, given GDS-06 §2.2's finding that the frame budget is tighter than assumed.
   No threshold exists. Owner: `03`/`04` jointly, and it depends on `BL-0060`'s cycle-measurement
   question resolving first.
4. **Should the ROM be able to explain its own controls?** §1.1 records that it cannot — no font,
   by deliberate choice, so the control legend is external. `ADS-104` §9 left this genuinely open.
   A pause/help screen would need either a font (a large investment) or a pictographic tile set (a
   smaller one, and more in keeping with the existing shape vocabulary). Owner: `01-vision` on
   whether self-explanation is a goal; `03` on the mechanism if it is.

## Merge gate

- [x] The previous level's gate (GDS-06) was verified closed before this level started — its own
      prose records "Gate: closed 2026-07-26."
- [x] All three content areas the ladder table names are covered — composition (§2), palette
      assignment strategy (§4), and the sync scheme (§3, including its stateless/self-healing
      consequences).
- [x] Authored against the shipped `visuals.py`, read directly — the two vocabularies, the nine
      cells, the ten tile patterns, and the single-palette strategy are observations, not
      proposals.
- [x] No production code; no byte layouts (GDS-07 §9 keeps the addresses).
- [x] No new research claims originated — `R205`/`R208`/`R222`/`R223`/`R104` are cited for
      conclusions they already reached; §8's four Open Questions are routed to owners.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md`'s stage-03 row updated together.

**Merge decision.** `Claude.md`'s "Change settings-indicator tile patterns" subsection and
`memory.md`'s visualizer quick-reference both **stay authoritative** as the working
developer/edit-time reference — they say *how to change* the display, which is exactly what a
quick-reference is for and exactly what this level is not. GDS-08 says *why the display has the
shape it has* and *what its extension mechanism is*, which neither file has a place for. Nothing
moved.

Two backlog items are addressed here but **not closed**, because in both cases the remaining work
belongs to another skill: `BL-0021` gains a design principle and a recommended direction (§4.3)
but still needs a shape chosen and reviewed; `BL-0016` gains an honest three-part resolution (§7)
but still needs `04-requirements-engineering` to split `FR-1120`'s wording. Both dispositions
should be updated to point here rather than being marked done.

**Gate:** closed 2026-07-26. Next unauthored level: GDS-09 (Interface Specification) — whose
absence every `FS-1xx` authored so far has flagged.
