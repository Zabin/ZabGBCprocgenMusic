# VR-0006 — Verification Report: IP-0006

- **Package:** IP-0006 — Minimal visualizer
- **Commit verified:** `504deda` (branch `claude/iterate-pipeline-skill-04nvuc`)
- **Date:** 2026-07-21
- **Result:** ✅ **VERIFIED** (with one requirements-coherence finding)

## Independence note

Same session as runs #7-#10 (this session has implemented none of IP-0002-0007). Independence
intact.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| New `visuals.py`, read-only consumer (never writes engine-state or a PSG register) | `visuals.py:1-104` read in full — only writes are `LCDC` (`0xFF40`), `BCPS`/`BCPD` (`0xFF68`/`0xFF69`, PPU palette registers), tilemap cells (`0x9800`-`0x9803`, VRAM), and tile pixel data at boot — none are engine-state WRAM or a PSG (`NR1x`-`NR5x`) register | PASS |
| `init_visuals`: 2 tiles (off/on), 4 tilemap cells cleared, BG palette 0 calm theme, LCD on (`LCDC=0x91`) | `visuals.py:54-73` | PASS |
| `update_visuals`: 4 cells show tile 1/0 per `NR52` channel-active bits; palette 0 rewritten each frame (calm/bad-zone) per `BAD_ZONE_FLAGS` bit3 | `visuals.py:76-103` | PASS |
| `test_rom.py` T9 (3 checks) + full regression green | See Test run below | PASS |

## Verification Checklist audit (G5 gates)

| Gate | Command | Result |
|---|---|---|
| ROM builds, fixed size, valid header | `python3 build_rom.py <path>` | 32768 bytes; title `DRIFTUNE`, CGB flag `0x80` |
| Full suite green | `python3 test_rom.py` | **60 PASS, 0 FAIL out of 60** (T9.1-T9.3 all PASS) |

## Non-default-state live drive (this skill's own additional requirement)

T9 only asserts the channel-activity tiles (via WRAM cell reads, matching `NR52`) — it never
independently confirms the palette actually reacts to bad-zone state, only that the code branches
on `BAD_ZONE_FLAGS` bit3 (readable from the source). Drove this live via rendered screen pixels
(`pb.screen.ndarray`), independent of the suite:

- Sampled a pixel inside the channel-1 indicator tile (screen coords `(2,2)`) across a long run,
  logging every frame `BAD_ZONE_FLAGS` bit3 flips.
- **First pass showed an apparent inversion**: the sampled color at a bit3-set frame matched the
  *calm* palette's expected RGB, and vice versa. Investigated rather than assumed a defect —
  correlated each sample against the *previous* frame's flag value instead of the current one:
  every sample matched the **previous** frame's flag state exactly, with zero exceptions across
  ~30 transition events. This is the expected GBC PPU behavior — a BG palette write during one
  frame's VBlank affects the *next* frame's scanout, not the frame it was written in (the PPU has
  already begun rendering the current frame by the time the VBlank ISR runs `update_visuals`) —
  not a ROM defect. Re-verified: `sample(frame N) == palette_for(flag(frame N-1))` holds for every
  logged transition.
- This confirms the palette does correctly track `BAD_ZONE_FLAGS` bit3, with the one-frame lag
  inherent to LCD hardware timing (not something `FR-1120`/the package doc claims to avoid, and
  imperceptible at 60fps) — a genuine independent confirmation beyond what T9's WRAM-only checks
  provide, and a case where the live drive's first result needed investigation before being
  trusted either way.

## Requirements audit

| ID | Where implemented | Where tested | Result |
|---|---|---|---|
| FR-1120 | `visuals.py:76-103` (`update_visuals`) | T9.1-T9.3 (channel-activity tiles); this run's own palette/bad-zone live drive above | **PASS with a finding** — see below |

No RTM file exists yet as a separate document (`BL-0001`, `⛔ Planned`) — per the interim
convention prior VRs established, this table is the RTM-equivalent audit for IP-0006's
requirement.

## Scope audit

Files touched per the package doc: `visuals.py` (new). Confirmed the entire file is new and
self-contained — no excursion into `music_engine.py`, `build_rom.py`, `input_map.py`, or
`gbc_lib.py` beyond `visuals.py`'s own `from gbc_lib import ROM, rgb15` (an existing shared
utility import, not a modification).

## Findings

| Finding | Severity | Owner |
|---|---|---|
| `FR-1120`'s text requires the visualizer to "represent **tempo**, per-channel activity, and bad-zone status" — the shipped `visuals.py` implements per-channel activity and bad-zone status only; `TEMPO_IDX`/tempo is never read anywhere in the file (confirmed by grep — zero matches). The package doc's own "Explicit non-scope" section already names "tempo-synced motion" as an unbuilt, unscheduled follow-up — so this is a knowingly-scoped-down MVP simplification, not an oversight — but `FR-1120` itself still describes the full three-signal version, the same "doc says more than the shipped simplification" pattern already tracked for `IP-0004` (`BL-0013`/`FR-1090`). No functional defect — what's built works correctly for the two signals it does cover. | Low-Medium (doc-coherence only — same character as `BL-0013`, not a new category of problem) | `04-requirements-engineering` (reword `FR-1120` to scope tempo representation as a follow-up, or note it as unbuilt-v1) alongside `03-architecture-design-synthesis`'s still-pending GDS-08 (`BL-0001`) |

## Verdict

`IP-0006` satisfies its Definition of Done, both permanent gates, and its traced requirement's
built portion, with independent re-derivation of every claim — including a live rendered-pixel
drive of the palette/bad-zone reaction (which required investigating and correctly explaining an
initially-confusing result, a one-frame VBlank render lag, rather than either dismissing or
mis-reporting it as a defect). One new, low-severity doc-coherence finding (`FR-1120` overstates
the shipped tempo-representation scope). **Advancing to `VERIFIED`.**
