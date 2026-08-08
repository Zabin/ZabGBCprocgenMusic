# R111 — APU Hardware Quirks & DMG vs. CGB Audio Differences

- **Tier:** R100 · **Owned by:** `02-research-gbc-hardware` · **Status:** ✅ Authored 2026-07-21
- **Maps to user-provided research list:** Phase 1, items 14 ("Hardware limitations and quirks"),
  15 ("DMG vs GBC audio differences")

## 1. Purpose
Ground `music_engine.py`'s wave-channel handling (`IP-0002`+) against a known, real hardware
erratum before it's hit in the field, and clarify what actually differs between DMG and CGB audio
(relevant since Driftune targets CGB but the APU itself is DMG-inherited).

## 2. Scope
The Channel 3 (wave) retrigger corruption bug, and the (small) list of genuine DMG/CGB audio
differences.

## 3. Concepts
- **Wave RAM corruption on retrigger (DMG only):** "retriggering CH3 while it's about to read a
  byte from wave RAM causes wave RAM to be corrupted in a generally unpredictable manner" — the
  first four bytes of Wave RAM get overwritten with whichever aligned 4-byte group was being read
  at the moment of retrigger. **Confirmed monochrome-only** — this is a DMG-specific erratum, not
  present on CGB hardware [Pan Docs — OAM Corruption Bug page's audio cross-reference; TLMBoy APU
  wave-channel writeup](https://www.chciken.com/tlmboy/2025/04/22/gameboy-apu-wave.html);
  [Pan Docs — Audio](https://gbdev.io/pandocs/Audio.html). The documented workaround: write 0
  then `$80` to `NR30` (power-cycle the channel's DAC) before retriggering, if a DMG target is
  ever in scope.
- **DMG vs. CGB audio**: the underlying PSG/APU model itself is unchanged between DMG and CGB —
  CGB does not add channels or registers. The practical differences that matter are (a) the wave-
  RAM corruption erratum above (CGB-immune), and (b) CGB's double-speed CPU mode (`KEY1`,
  irrelevant to Driftune v1, which runs single-speed).

### Sources
- [chciken.com — TLMBoy: The APU, Wave Channel](https://www.chciken.com/tlmboy/2025/04/22/gameboy-apu-wave.html)
- [Pan Docs — Audio](https://gbdev.io/pandocs/Audio.html)
- [gbdev.gg8.se — Gameboy sound hardware](https://gbdev.gg8.se/wiki/articles/Gameboy_sound_hardware)

## 4. Operational Context
Not yet implemented — `IP-0001` only drives pulse A, never touches Wave RAM. Relevant starting
with `IP-0002`.

## 5. Implementation Guidance
- **Driftune targets CGB only** (MSTR-001 C1) — the retrigger corruption bug does not apply, and
  `IP-0002`'s wave-channel implementation does **not** need the NR30-power-cycle workaround. This
  should be stated explicitly in `IP-0002`'s FS as a deliberately-skipped defensive measure (with
  this citation), not silently omitted, so a future DMG-compatibility push doesn't get bitten by
  it unknowingly.
- If Driftune is ever asked to also run correctly on real DMG hardware (currently out of scope),
  this workaround becomes mandatory before any Wave RAM rewrite-while-triggered technique (the
  live-timbre-swap idea from R108 SS5) is used.

## 6. Feature Mapping
`IP-0002` (wave channel, not yet authored) — a named, deliberate non-requirement.


## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`/`BL-0071`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

⚠️ **EXCEPTION — grounds a confirmed non-risk.** Its headline finding (the Channel-3 wave-RAM retrigger corruption erratum) is **confirmed DMG-only and absent on CGB**, so no shipped code needed a workaround. That is a genuine and useful result — it is the reason `music_engine.py`'s wave-channel handling needs no `NR30` power-cycle dance — but it produced no feature, so it is recorded as a C10 exception rather than a strained forward link. [GDS-02 §7](../../architecture/02-system-context.md) cites it as a reassurance, and separately notes the *unresearched* question this topic does not answer: whether PyBoy's APU emulation diverges from CGB silicon anywhere this engine would notice (`BL-0058`).

## 7. Related Topics
R108 (Wave RAM's live-rewrite capability, the exact mechanism this erratum affects), R114 (wave
channel programming guidance).
