# Architecture Decision Records — Index

[↑ Architecture index](../INDEX.md)

| ADR | Title | Date | Status |
|---|---|---|---|
| [ADR-0001](ADR-0001-scheme-selection-rides-chmix-preset-space.md) | Scheme selection rides the existing `CHMIX_IDX` preset space | 2026-07-22 | Accepted |
| [ADR-0002](ADR-0002-defer-mbc-adoption-single-bank-retained.md) | Defer MBC/bank-switching and SRAM/battery-save adoption; single 32KB bank retained | 2026-07-25 | Accepted |
| [ADR-0003](ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md) | Scheme selection moves out of `CHMIX_MASKS` into a parallel `SCHEME_TABLE` (amends `ADR-0001`'s packing, not its principle) | 2026-08-19 | ⚠️ **Superseded by `ADR-0004` (2026-08-20), before implementation — no `SCHEME_TABLE` was ever created** |
| [ADR-0004](ADR-0004-harmonic-coordination-replaces-the-default-walk-in-place.md) | Harmonic coordination replaces the default scheme's note selection **in place**; `ADR-0001`'s one-bit packing is reaffirmed and `ADR-0003`'s migration is not performed. Reachable scheme set stays at two values (harmonized default, Scheme E), so no second bit is needed. Supersedes `ADR-0003`; the boot sound changes deliberately, per the owner's 2026-08-20 release of `GDS-04` §4.1's historical-no-regression reading | 2026-08-20 | Accepted |
| [ADR-0005](ADR-0005-the-arpeggio-becomes-chord-aware-gated-and-varied.md) | The `IP-1060` arpeggio becomes **chord-aware** (traverses `CHORD_TABLE`'s own tones, not `AND 0x07` degree offsets from the sounding note), **gated** (only a chord tone arpeggiates — pulse A's passing tones sustain) and **varied** (the figure is drawn per onset from a weighted pattern table with a reserved "sustain" value, so gate and variation are one mechanism), and its per-frame cost must strictly **decrease** via an onset-resolved per-channel cache. Explicitly **not retired** — retirement was the strongest rival and is kept as a one-table-edit fallback. Answers the owner's measured "constant repeated arpeggios" (`BL-0127`); absorbs `CR-0006` and `BL-0125`; leaves `ADR-0001`/`ADR-0004` untouched | 2026-08-21 | Accepted |
