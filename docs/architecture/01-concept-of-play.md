# GDS-01 — Concept of Interaction

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored, 2026-07-21 · **Grounds:** GDS-03, GDS-05

(Named "Concept of Play" in the reference project's ladder for its game; Driftune has no "play" in
that sense, so this level is retitled "Concept of Interaction" here — same ladder position, same
role: the single-page description of what the player actually does, moment to moment.)

## The loop, end to end

There is exactly one state: **running**. No title screen, no menu, no win/lose screen. On power-on,
after a brief fixed init sequence (LCD/sound hardware setup, generator seeded to the same known-
good preset — GDS-03; boot is the only event that lands on it, see step 6), the engine starts generating and the visualizer starts
rendering, immediately and continuously, for as long as the ROM is powered.

Every frame:

1. Read the joypad; any newly-pressed (edge-triggered, not held-repeat) button/direction updates
   exactly one generation parameter (GDS-03's mapping table).
2. The generation routine advances (every frame it checks "has any channel's current note expired
   or state changed"; only on those less-frequent events does it compute new register values —
   R100's cycle-budget note).
3. The bad-zone score updates (on the same note-expiry cadence as generation, not every frame —
   GDS-03).
4. The generation routine itself reacts to the bad-zone score it just computed — biasing its next
   step toward the tonic when dissonant, forcing movement when stuck, spacing onsets out when
   overloaded (`IP-0007`, GDS-03 §5) — so the system can climb back out **on its own**, without
   requiring Select. Detection and recovery are both autonomous; the player never has to intervene
   for the music to keep sounding intentional.
5. The visualizer reads current engine state (tempo, per-channel activity via `NR52`, bad-zone
   flag) and updates its tile/palette animation on its own budget-appropriate cadence.
6. Select, at any time, is the listener's **reroll**: it randomizes each channel's melodic
   starting point (`IP-0007`) and clears the bad-zone counters, **while leaving every parameter
   the listener has set exactly where they set it** — usable whether or not the bad zone is
   currently flagged; a manual "give me different music, keep my settings" control, not the only
   recovery path and not conditionally gated on bad-zone state.

   > **Amended 2026-08-21** ([`ADR-0006`](adr/ADR-0006-select-becomes-reroll-not-reset.md)). This
   > step previously read *"resets the generator to the known-good preset and randomizes each
   > channel's melodic starting point."* The index reload dates from `IP-0001`, when Select was the
   > engine's **only** bad-zone escape; `IP-0007` made recovery autonomous in 2026-07 (step 4
   > above), and this document has said so ever since without anything re-examining the mechanism
   > that supersession obsoleted. The project owner settled it directly: *"The select-reset does
   > not need to bring it back to the boot default either, just course correct from a bad zone."*
   > **The flat single-state model is untouched** — a button press adds no menu, no mode and no
   > screen, so this is not the scope change `R217` §3 routed through `01-vision`; see that topic's
   > own 2026-08-21 addendum.

   The line this draws is worth stating once, plainly, because it is now the rule for every future
   mechanism: **what the listener chose survives a Select; what the engine wandered into does
   not.** Boot is unaffected and still lands on the known-good preset every time.

There is no pause, no save, no exit. Turning the device off is the only "stop."

## Why this is flatter than the reference project's state machine

GDS-00 already named this: there's no title/intro/save/map/victory shape to inherit because there
is no game to progress through. The entire "interaction model" is: one continuously-running
process, steered live, recoverable on demand. This keeps GDS-05 (feature decomposition) simple —
features are properties of the one running process (which parameters are steerable, what the
bad-zone metric measures, what the visualizer shows), not separate screens/modes.

## Non-features carried down from MSTR-001 §4

No pause state, no pref/settings menu, no save/load, no multiple "songs" to pick between (picking
*is* steering, live, per GDS-00). If a later increment wants any of these, it re-enters at
`01-vision` (a menu/pause state would be a scope change to this concept level, not a downstream
detail) or `00-intake` if it's additive without changing this flat shape (e.g. a cosmetic-only
visualizer mode toggle could plausibly be additive — judgment call for whichever future
`00-intake` triage actually receives that request).

**Gate:** closed 2026-07-21. Next: GDS-03 (Architecture).
