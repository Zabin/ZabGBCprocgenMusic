# Pipeline Backlog

| ID | Filed | Type | Summary | Sev/Pri | Entry stage | Disposition | Status |
|---|---|---|---|---|---|---|---|
| BL-0001 | 2026-07-21, run #1 | research-gap | GDS-02 (System Context), GDS-04 (Domain Model), GDS-05/06 (FR/NFR at the GDS-ladder level — superseded in ordering by the direct `04-requirements-engineering` pass already done, but the ladder levels themselves are still unauthored), GDS-08 (Presentation Architecture/visualizer), GDS-09 (Interface Spec), GDS-10 (RTM level) remain `⛔ Planned`. | Medium | 03 | `SCHEDULED` — GDS-08 rides with `IP-0006` (visualizer); GDS-09 rides with whichever package first needs a formal interface contract (likely `IP-0002`); GDS-02/04/10 are lower-priority, scheduled opportunistically alongside those. | NEW |
| BL-0004 | 2026-07-21, run #1 | gate | `IP-0001` was built and self-tested in the same session/agent that authored it, not verified independently. Per this project's own adopted convention (mirroring the reference project's "verification ideally in a fresh session" practice), it is `COMPLETE` but not `VERIFIED`. | Medium | 09 | `DEFERRED` — run #2 attempted `09-package-verification` on `IP-0001`; the skill's own rules required explicit user acceptance of degraded (same-session) independence before proceeding, so the user was asked (`AskUserQuestion`) — they chose **"wait for a fresh session"** rather than accept the caveat. Revisit trigger: the first action of the next fresh session should be `09-package-verification` on `IP-0001`. | NEW |
| BL-0005 | 2026-07-21, run #1 | design-question | Preset table values (tempo BPM steps, octave root Hz values, scale semitone sets, Euclidean density k/n pairs — the last not yet implemented) and bad-zone thresholds (dissonance/stale/overload) are first-guess placeholders (GDS-03 SS3/SS4 say so explicitly), not yet tuned by ear. | Medium | 08 (content-authoring) / 09 (content-review) | `DEFERRED` — revisit trigger: once `IP-0002`/`IP-0003` land (pulse B/wave/noise all present) and there's enough sound surface for a real listening pass to be meaningful; tuning single-channel pulse A alone isn't representative. | NEW |
| BL-0006 | 2026-07-21, run #1 | feature | No FS-xxx (Feature Specification, stage 06) has been authored yet for any of FEAT-1000...1050 — the pipeline moved from the feature catalog straight to implementation planning for `IP-0001`'s narrow slice rather than writing full 20-field specs first. | Medium | 06 | `SCHEDULED` — author FS-100 (Core Generation Engine) and FS-101 (Input Steering) before `IP-0002` is planned, since `07-implementation-planning` should properly derive from a feature spec rather than skip it a second time. | NEW |
| BL-0007 | 2026-07-21, run #1 | design-question | Working title "Driftune" is explicitly open to revision (MSTR-001 SS1 flags it as such) — no user confirmation has been sought yet. | Low | 01 | `DEFERRED` — revisit trigger: surface it to the user the next time `01-vision` is naturally revisited (e.g. alongside BL-0001's GDS-08 visualizer work, where a name might matter more concretely), rather than interrupting this session's flow for a naming call alone. | NEW |

**Triage note (run #2, 2026-07-21):** `BL-0002`/`BL-0003` were `DONE` and relocated verbatim to
`docs/pipeline/backlog-archive.md`. `BL-0004` is due this run (rides `09-package-verification` on
`IP-0001`) — flipped to `IN PIPELINE`. `BL-0005`/`BL-0007`'s deferral triggers have not fired yet
(no `IP-0002`/`IP-0003`, no `01-vision` revisit in progress) — left `DEFERRED`. `BL-0001`/`BL-0006`
remain `SCHEDULED` for their named rides, not yet due. Still no `NEEDS-USER` entries.

**Triage note (run #1):** every entry above got an explicit disposition at filing time (no
separate later triage pass needed yet, since this is the project's first run). None are
`NEEDS-USER` — nothing here is a decision only the user can make right now; BL-0007 is the closest
candidate but is explicitly deferred rather than asked, since it's genuinely low-stakes and the
vision doc already names it as revisable later.
