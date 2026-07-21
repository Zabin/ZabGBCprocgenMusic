# Pipeline Backlog Archive

Closed (`DONE`/`REJECTED`) backlog entries, relocated here verbatim from `docs/pipeline/backlog.md`
at a triage sweep once resolved — never deleted, only moved, per the archiving convention in
`00-pipeline-manager/SKILL.md`.

| ID | Filed | Type | Summary | Sev/Pri | Entry stage | Disposition | Status |
|---|---|---|---|---|---|---|---|
| BL-0002 | 2026-07-21, run #1 | finding | `NR13`/`NR23`/`NR33` (frequency low byte) and the frequency-high bits of `NR14`/`NR24`/`NR34` are write-only on real GBC hardware (confirmed empirically against PyBoy 2.7.0 during `IP-0001`) — readback is not a usable test/visualizer signal; only the WRAM engine-state mirror and `NR52`'s active-channel bits are readable. Already corrected into `docs/research/R100-gbc-sound-hardware.md`. | Low (already fixed at the doc level) | 02 | `DONE` — folded into R100 directly, no further action needed. | DONE |
| BL-0003 | 2026-07-21, run #1 | doc-defect | GDS-07 (Data Model) was missing `JOY_CUR`/`JOY_NEW`/`LFSR_STATE`/`VBLANK_FLAG` WRAM addresses, discovered necessary only once `IP-0001` actually implemented input reading and the LFSR. Already corrected in place (SS5/SS8 addenda). | Low (already fixed) | 03 | `DONE` — folded into GDS-07 directly. | DONE |
