# GDS-01 — Concept of Interaction

- **Owned by:** `03-architecture-design-synthesis` · **Status:** ✅ Authored, 2026-07-21 · **Grounds:** GDS-03, GDS-05

(Named "Concept of Play" in the reference project's ladder for its game; Driftune has no "play" in
that sense, so this level is retitled "Concept of Interaction" here — same ladder position, same
role: the single-page description of what the player actually does, moment to moment.)

## The loop, end to end

There is exactly one state: **running**. No title screen, no menu, no win/lose screen. On power-on,
after a brief fixed init sequence (LCD/sound hardware setup, generator seeded to the same known-
good preset Select resets to — GDS-03), the engine starts generating and the visualizer starts
rendering, immediately and continuously, for as long as the ROM is powered.

Every frame:

1. Read the joypad; any newly-pressed (edge-triggered, not held-repeat) button/direction updates
   exactly one generation parameter (GDS-03's mapping table).
2. The generation routine advances (every frame it checks "has any channel's current note expired
   or state changed"; only on those less-frequent events does it compute new register values —
   R100's cycle-budget note).
3. The bad-zone score updates (on the same note-expiry cadence as generation, not every frame —
   GDS-03).
4. The visualizer reads current engine state (tempo, per-channel activity via `NR52`, bad-zone
   flag) and updates its tile/palette animation on its own budget-appropriate cadence.
5. Select, at any time, resets the generator to the known-good preset — usable whether or not the
   bad zone is currently flagged (it's a "start over" control, not conditionally gated).

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
