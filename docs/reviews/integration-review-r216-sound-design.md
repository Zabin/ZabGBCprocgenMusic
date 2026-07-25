# Integration Review — R216 Sound Design Techniques Tranche (`IP-1060` + `IP-1061`)

- **Scope:** `IP-1060` (arpeggio + duty-cycle variation) and `IP-1061` (vibrato + portamento) —
  the two packages implementing `BL-0024`/`FS-106` (R216 sound-design-techniques), the full
  `FEAT-1060` catalog entry.
- **Commit reviewed:** `5eebbf4` (branch `claude/iterate-pipeline-skill-houug0`)
- **Date:** 2026-07-25
- **Eligibility:** both packages confirmed `VERIFIED` before this review began —
  [VR-1060](../implementation/verification/VR-1060-arpeggio-and-duty-cycle.md),
  [VR-1061](../implementation/verification/VR-1061-vibrato-and-portamento.md).
- **Result:** ⚠️ **1 Medium finding** (documentation coherence). No Critical/High findings.

## Gates (re-run against the reviewed commit)

```
python3 build_rom.py Driftune.gbc   # 32768 bytes
python3 test_rom.py                 # 65 PASS, 0 FAIL out of 65
```

## Dimension 1 — Interface consistency

Both packages extend the same shared routines (`_emit_channel_gen`, the new
`_emit_arpeggio_tick`) and the same `CHANNELS` parameterization (`music_engine.py:137-148`) rather
than diverging into separate per-package code paths — this is the seam most likely to hide a
defect, since `IP-1061` was built second, directly modifying functions `IP-1060` had already
shipped. Traced the composition explicitly:

- `engine_tick`'s call order (`music_engine.py:717-725`) — `arp_tick` for every arpeggiating
  channel, then `gen_tick` for every channel, then noise, then bad-zone — matches both packages'
  own documented ordering rationale (`IP-1061`'s commit message, `music_engine.py:709-716`'s
  inline comment).
- `_emit_arpeggio_tick`'s single packed WRAM byte (`ARP_STATE_PA`/`PB`) is genuinely shared
  between `IP-1060`'s arpeggio-step bits (4-5) and `IP-1061`'s vibrato-phase bits (6-7) with no
  bit overlap — confirmed by reading the packing scheme end to end
  (`music_engine.py:381-396`'s own docstring plus the actual `AND`/`OR` mask literals used at each
  read/write site).
- `portamento=(arp_state is not None)` (`music_engine.py:730`) means both pulse A/B — the only two
  channels `IP-1060` gave an `arp_state` slot — automatically got `IP-1061`'s portamento
  treatment with no separate wiring; the wave channel (`arp_state=None`) correctly gets neither
  package's per-frame modulation, consistent with `IP-1060`'s own documented "wave excluded"
  scope decision.
- No `build_rom.py` patch-point or section-layout change was needed by either package (confirmed
  via each package's own scope audit in `VR-1060`/`VR-1061`) — both are pure `music_engine.py`
  data+code additions, so there is no cross-file interface to verify beyond the one already
  checked above.

**Clean** — no interface defect found.

## Dimension 2 — Invariant sweep

- **ROM budget:** 32768 bytes exactly, both packages' new tables (`ARPEGGIO_OFFSETS` 4 bytes,
  `DUTY_BY_DEGREE` 4 bytes, 0 bytes for vibrato — computed from phase bits, no table) fit within
  the committed single-bank budget with no bank-switching change, confirmed by this run's own
  rebuild.
- **WRAM map:** grepped every `0xC0xx`-pattern WRAM constant in `music_engine.py`
  (`ARP_STATE_PA=0xC01D`, `ARP_STATE_PB=0xC01E`, `ARP_DEGREE_SCRATCH=0xC01F`) against
  `docs/architecture/07-data-model.md` §3 — all three present, each tagged with the package that
  added/extended it (`IP-1060` for the base entries, `IP-1061` for the vibrato-bit extension).
  No collision with the existing `0xC013`-`0xC015`/`0xC020`-`0xC037` reserved-but-unused
  history-buffer range (`BL-0013`/`BL-0018`), and no collision with any other channel's WRAM
  block — the full address list is contiguous and non-overlapping (0xC000-0xC01F fully mapped,
  checked address-by-address against `music_engine.py`'s own constant declarations).
- **APU register timing:** both packages write `NR11`/`NR21`/`NR13`/`NR14`/`NR23`/`NR24` only from
  within `gen_tick_*`/`arp_tick_*`, both called once per frame from `engine_tick`
  (VBlank-cadence, same frame-sequencer discipline every prior package already established) — no
  new timing source, no second write site for the same register introduced.
- **Combined stress run (this review's own live exercise):** 8000 frames with randomized input
  churn across all 8 buttons (tempo/octave/scale/density/channel-mix/select, seed 42) — bad-zone
  entry and the COMBINED flag both observed (`flags seen: [0, 8, 9, 10, 11]`), arpeggio step index
  and duty-cycle bits both cycled through all 4 values throughout, `NR52` stayed non-zero
  (channels active) for the entire run, no hang, no crash. Confirms the new per-frame
  arpeggio/vibrato/duty machinery coexists cleanly with `IP-0007`'s autonomous bad-zone
  avoidance/recovery under combined stress, not just each in isolation as the individual VRs
  checked.

**Clean** — no invariant violation found.

## Dimension 3 — Behavioral coherence

- No divergent reimplementation: both packages extend the *same* shared functions rather than
  each writing their own version of onset/frequency-write logic — there is exactly one
  `_emit_channel_gen` and one `_emit_arpeggio_tick`, not two competing paths.
- No dead-end: every new signal this tranche introduces has a real consumer — arpeggio steps and
  vibrato phase both feed directly into PSG register writes every frame (audible, not just
  computed-and-discarded); duty-cycle bits write to `NR11`/`NR21` every onset. Unlike `BL-0019`
  (an unrelated, pre-existing finding — `CHMIX_IDX` has no consumer anywhere), this tranche
  introduces nothing that goes unconsumed.
- Interaction with `IP-0004`/`IP-0007`'s bad-zone bookkeeping: re-confirmed (both individual VRs
  already checked this per-package) that `_emit_arpeggio_tick` never touches `cur_degree`,
  `stale_count`, `DISSONANCE_SCORE`, or `BAD_ZONE_FLAGS` — the combined stress run above is live
  confirmation this holds under realistic combined load, not just static code reading.

**Clean** — no behavioral coherence defect found.

## Dimension 4 — Traceability coherence

Checked the full chain both directions:

- `FR-1130`/`FR-1140`/`FR-1150`/`FR-1160`/`NFR-1040`/`NFR-1050`
  (`docs/requirements/01-functional-requirements.md`) → `FEAT-1060`
  (`docs/feature-planning/01-feature-catalog.md:16`) → `FS-106`
  (`docs/features/fs-106-sound-design-techniques.md`, indexed at `docs/features/INDEX.md:24`) →
  `IP-1060`/`IP-1061` (`docs/implementation/packages/INDEX.md:18-19`) → `VR-1060`/`VR-1061`
  (`docs/implementation/verification/INDEX.md`) — every link present and bidirectional, no
  orphaned ID, no broken cross-reference.
- Master Build Plan (`docs/implementation/00-master-build-plan.md`) correctly shows both packages
  `VERIFIED` with their VR links.

**One gap found:** `ROADMAP.md` — the project's own top-level per-stage status summary — has not
been touched for this entire thread. Its rows for **04 Requirements** ("FR-1000...FR-1120,
NFR-1000...NFR-1030"), **06 Feature Specification** ("FS-100...FS-105 planned, none formally
authored"), **07 Implementation Planning** ("TWBS (IP-0001...IP-0007 + remediation tranche...)"),
**08 Implementation** ("MVP complete... IP-0002-IP-0007 COMPLETE"), and **09 Verification** ("All
7 packages independently VERIFIED") all still describe only the original Foundation-bucket scope
— none mention `FR-1130`-`FR-1170`, `FEAT-1060`, `FS-106`, or `IP-1060`/`IP-1061` anywhere, despite
this work having been authored and built across runs #20-24 and independently verified this run
(#33). `ROADMAP.md`'s own header does state the indexes are authoritative on detail and it is "a
flat summary for a quick glance" — so no downstream skill was actually misled by this (every
skill's own Step 1 reconciliation reads the real indexes) — but a quick-glance summary that is
silently five stages out of date defeats its own stated purpose.

## Dimension 5 — Documentation coherence

- `Claude.md`/`memory.md`: both correctly carry the new WRAM addresses and Known-Good-Behavior
  bullets for arpeggio/vibrato/duty/portamento (confirmed present during both individual VRs,
  re-confirmed here).
- `docs/architecture/07-data-model.md` (GDS-07): correctly extended, tagged per package.
- `docs/reviews/INDEX.md`: did not yet list this review (expected — this review's own output adds
  it, below).
- Two package-level doc-coherence gaps (`IP-1060`'s table-size wording, `IP-1061`'s
  portamento-mechanism-vs-design-doc gap) were already caught and filed by the individual VRs
  (`BL-0025`/`BL-0026`/`BL-0027`) — not re-filed here as duplicates.

**Same `ROADMAP.md` gap as Dimension 4** — see Findings below.

## Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| `ROADMAP.md` stale for the entire `BL-0024`/`FS-106` thread | `ROADMAP.md` rows 04/06/07/08/09; `FR-1130`-`FR-1170`, `FEAT-1060`, `FS-106`, `IP-1060`, `IP-1061` | The project's top-level per-stage status summary has not been updated since run #19 for any of this thread's work — five rows each describe only the original 7-package Foundation-bucket scope, with no mention of the R216 sound-design-techniques requirements/feature/spec/packages authored and verified across runs #20-24 and #33. No functional or pipeline-logic impact (every stage's own Step 1 reconciliation reads the authoritative per-directory indexes, not this flat summary), but the summary's own stated purpose — a trustworthy quick-glance view — is defeated while it stays this far behind. | **Medium** (real, multi-run-old documentation drift on a load-bearing status artifact; zero functional impact, not blocking) | `00-pipeline-manager` to route each stale row to its owning stage skill's next natural touch (same pattern as `BL-0013`/`BL-0016`/`BL-0018`'s doc-coherence findings) — or a single consolidated pass reconciling all five rows against the real indexes at once, since the underlying facts are already fully documented elsewhere and this is pure transcription, not new judgment |

No Critical or High findings. `BL-0019` (High, `CHMIX_IDX` unconsumed) and `BL-0017`/`IP-9020`
(the overload-threshold gap) remain open from the earlier Foundation-bucket review — both are
pre-existing, unrelated to this tranche, and already tracked; not re-surfaced here as new findings.

## Verdict

The `BL-0024`/`FS-106` tranche integrates cleanly with itself and with the previously-verified
Foundation bucket: no interface defect, no invariant violation (including under a combined
8000-frame stress run with input churn re-confirming coexistence with `IP-0007`'s autonomous
bad-zone recovery), no behavioral dead-end, and a fully traceable chain from `FR-1130`-`FR-1170`
through to both `VR`s except for one stale top-level summary artifact. One Medium
documentation-coherence finding recorded (`ROADMAP.md`), routed for correction — does not block
this tranche from being considered ready. **No Critical/High findings — this scope may advance
toward `11-release-readiness` consideration**, though note the Foundation bucket's own
pre-existing `BL-0019` (High) still blocks that bucket's own release-readiness call independently
of this tranche's cleanliness; the two scopes' readiness are evaluated separately per
`ROADMAP.md`/backlog convention until the project decides to bundle them into one release.
