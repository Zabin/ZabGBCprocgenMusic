---
name: 00-pipeline-manager
description: Run the documentation-driven-development pipeline with persistent memory — reconcile the pipeline journal (docs/pipeline/pipeline-journal.md) against the tree's real ledgers, triage the pipeline backlog (docs/pipeline/backlog.md — every finding/recommendation harvested from prior runs plus 00-intake-filed features/bugs, each needing an explicit disposition before the next step is chosen), determine the next step, execute it by invoking the owning numbered skill (01-vision through 11-release-readiness), harvest the invoked skill's findings into the backlog, append the run to the journal, and repeat. Modes: no args = iterate — keep advancing, one skill invocation at a time, each fully journaled, until every open thread and backlog item is genuinely blocked by something only the user can resolve (not by more research/architecture/requirements/planning work the pipeline can do itself), then report the whole run in one summary; "step" = advance exactly one step and report immediately; "status" = read-only survey + recommendation; "triage" = backlog triage only; "log" = show the journal; "sync" = reconcile only; "run <skill> [target]" = execute a specific step out of recommended order (journaled as an override). Use when asked to "run the pipeline," "run the pipeline skill," "do the next step," "continue where we left off," "iterate until blocked," "where are we / what's next," "triage the backlog," or "show the pipeline log." It always stops at genuine human-only gates (G3 package authorization for a package not already covered by the current, user-approved release plan, release GO/NO-GO, Vision-level tension, a ripe NEEDS-USER item, Critical review findings) and asks rather than proceeding; it performs no stage work itself beyond invoking the owning skill.
---

# Pipeline Manager

The **driver** for the documentation-driven-development pipeline. Where each numbered skill knows
how to do *its* stage, this skill knows *where the pipeline is* and *what is still owed*: it keeps
a persistent journal of position, a persistent backlog of findings and requests, reconciles both
against reality, executes the next step by invoking the owning skill, and logs what happened — so
"continue the pipeline" works across sessions without re-deriving everything, and nothing a
previous run surfaced is ever silently forgotten.

It performs **no stage work itself**. It reads ledgers, invokes exactly one owning skill per
internal step, and writes exactly two files of its own: the journal and the backlog. A manager
that starts doing the stages' work stops being trustworthy about where the pipeline is.

**Default behavior is to iterate, not to take one step and stop.** Every internal step is still
exactly one skill invocation, still fully journaled (its own run-log row, Position rewrite,
backlog harvest) before the next is chosen — nothing about the per-step discipline changes. What
changes is that the manager keeps choosing and executing the next step, across as many stage
skills as it takes, until every open thread and backlog item is **genuinely blocked by something
only the user can resolve** — not merely "big," "a lot of work," or "touches production code" —
and only *then* does it stop and report. A gap closeable by any pipeline stage's own automated
work (any of the three `02-research-*` tiers, `03` architecture, `04` requirements, `05`
decomposition, `06` spec, `07` planning) is never itself a reason to stop; the manager runs that
stage next instead of asking. The genuine stopping conditions are: **G3** package authorization,
**G4** release GO, a **Vision-level** tension only `01-vision`'s own user-facing judgment can
settle, a ripe **`NEEDS-USER`** backlog entry, an unadjudicated Critical/High review finding, or
the backlog/next-step queue being truly empty (nothing left to advance). See `step` mode below
for the old one-stage-at-a-time behavior when that's what's actually wanted.

## The journal — `docs/pipeline/pipeline-journal.md`

The manager's persistent memory of **position**. Two parts:

1. **Position block** (rewritten every run):

   ```markdown
   ## Position
   - **Updated:** <date> (run #N)
   - **Increment:** <what body of work the pipeline is currently driving>
   - **Pipeline state:** <one line per stage that isn't ✅ idle-and-current — what's open where>
   - **Backlog:** <N open entries (IDs), which are due at/before the next step — or "none open">
   - **Next step:** `<skill>` on <target> — <one-line why>
   - **Open gates:** <human decisions pending: authorizations, GO calls, unadjudicated findings — or "none">
   ```

2. **Run log** (append-only, newest last — never rewrite or delete old rows):

   ```markdown
   | # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
   ```

   One row per manager run, including `status`/`sync`/`triage` runs (skill invoked = `—`) and runs
   that stopped at a gate (outcome = `GATE: <what's needed>`), so the log shows stalls, not just
   wins.

   **Archiving (`IP-8090`, 2026-07-20):** once the live run log passes roughly 200 rows, move the
   oldest rows to `docs/pipeline/pipeline-journal-archive.md` (verbatim, same table format,
   append-only there too) and leave a one-line pointer in their place. Never delete a row — only
   relocate it. This is a doc-scope refactoring package (`08-refactoring`), not something to do
   ad hoc mid-run.

## The backlog — `docs/pipeline/backlog.md`

The manager's persistent memory of **obligations**: every finding, recommendation, Outstanding
Issue, and Open Question a stage skill's run surfaced, plus every feature request and bug report
filed by the `00-intake` skill. One table, `BL-xxxx` IDs, append entries / update statuses in
place, never delete rows (rejected entries stay, marked `REJECTED` with the reason).

| Field | Content |
|---|---|
| **ID** | `BL-xxxx`, sequential |
| **Filed** | Date + source (which run/VR/report/intake produced it) |
| **Type** | `feature` / `bug` / `finding` / `recommendation` / `design-question` / `gate` / `research-gap` / `doc-defect` / `refactor` |
| **Summary** | One sentence; link the source artifact |
| **Sev/Pri** | The source's severity, or the user's stated priority for intake items |
| **Entry stage** | The pipeline stage where the item enters when worked (e.g. a code bug → `07`, a spec gap → `06`, a research gap → `02`) |
| **Disposition** | The manager's recorded decision on *when* it will be addressed (see lifecycle) |
| **Status** | `NEW` → `SCHEDULED` / `DEFERRED` / `NEEDS-USER` → `IN PIPELINE` → `DONE` / `REJECTED` |

**Writers:** this skill (harvest + triage + status flips) and `00-intake` (appends `NEW` entries).
Stage skills never write the backlog — their findings reach it through this skill's harvest step,
which is what guarantees a finding stated in a chat summary survives the session that stated it.

**Every open entry carries a live disposition.** `SCHEDULED` names the step it rides with;
`DEFERRED` names its revisit trigger; `NEEDS-USER` names the exact decision required. "We'll get
to it" with no trigger is not a disposition.

**Archiving (`IP-8100`, 2026-07-20):** once a row flips `DONE`/`REJECTED`, it moves to
`docs/pipeline/backlog-archive.md` (verbatim, same table format, in original ID order) at the
next triage sweep, rather than staying live indefinitely. Never delete a row — only relocate it.
This keeps the live backlog focused on what actually needs triage.

## Modes

| Invocation | Behavior |
|---|---|
| *(no args)* | **Iterate**: repeat {reconcile → triage backlog → determine next step → gate-check → invoke the owning skill → harvest + journal} for as many internal steps as it takes, advancing through every unblocked stage automatically, until a genuine human-only gate is hit or the backlog/next-step queue is truly empty. One skill invocation per internal step, each fully journaled — but the chat-facing report is composed once, at the very end (see "Pipeline position & completion summary" below). |
| `step` | **Advance exactly one step**: the loop body above, run once, then report immediately — the old default behavior, for when single-stage control is actually wanted. |
| `status` | Read-only: reconcile in-memory, print the stage survey + backlog summary + recommendation. No writes unless drift was found and the user confirms syncing it. |
| `triage` | Backlog only: harvest anything un-harvested from the last run, put a disposition on every `NEW` entry, re-check `DEFERRED` triggers and `NEEDS-USER` questions. No skill invoked. |
| `log` | Print the Position block, the last ~10 run-log rows, and open backlog entries; no writes. |
| `sync` | Reconcile journal + backlog against the ledgers; invoke nothing. Use after doing pipeline work outside the manager. |
| `run <skill> [target]` | Execute a specific step even if it isn't the recommendation (still gate-checked, never gate-bypassed). Journaled with mode `override` and the recommendation it superseded. Reports immediately, like `step`. |

## Workflow (the loop body — one internal step)

In `step` mode, run this once. In the default iterate mode, run this repeatedly — each pass is
one internal step, chosen and executed fresh from the post-previous-step state — until Step 4
stops at a genuine gate or Step 3 finds nothing left to advance. Do not skip or batch the journal
writes across iterations to save time: every internal step gets its own Step 6 (harvest + journal
row + Position rewrite + commit) before the next step is chosen, exactly as if it were run
standalone. The only thing iterate mode changes about Steps 1–6 is that they run in a loop; Step 7
(Report) is what changes shape — see its own section below.

### Step 1 — Read the journal and backlog, then reconcile against the ledgers

Read `docs/pipeline/pipeline-journal.md` and `docs/pipeline/backlog.md` (create either with an
initialization entry if absent). Verify the Position block against the authoritative ledgers —
cheapest-first, always including the ledgers that bear on the recorded next step:

`ROADMAP.md` · `docs/architecture/INDEX.md` §1 (GDS ladder) · `docs/requirements/` +
`docs/reviews/` (baseline + findings state) · `docs/feature-planning/01-release-plan.md` +
`05-feature-review.md` · `docs/features/INDEX.md` ·
`docs/implementation/00-master-build-plan.md` + `packages/INDEX.md` ·
`docs/implementation/verification/` · `docs/reviews/integration-review-*` +
`release-assessment-*` · `docs/roadmap/04-release-roadmap.md` + `INDEX.md` (if present — read-only
cross-cutting sequencing input, see `README.md`'s "Product Roadmap" section; note drift here the
same as any other ledger, but never edit it — it isn't this skill's write scope).

Drift (a status the journal didn't expect, work done outside the manager, a `VERIFIED` with no
Verification Report, a backlog item the tree shows already resolved) is corrected now and noted in
this run's log row.

### Step 2 — Triage the backlog (review the last run's findings before choosing anything)

This step is **mandatory before Step 3**:

1. **Late harvest.** If the previous run's log row references findings that never became backlog
   entries, add them now (`NEW`, sourced to that run).
2. **Disposition every `NEW` entry.** For each, decide and record: fold into the upcoming step
   (`SCHEDULED`, naming the step), schedule at a named later point (`SCHEDULED`), defer with an
   explicit revisit trigger (`DEFERRED`), require a user decision (`NEEDS-USER`), or reject with a
   reason (`REJECTED`). Severity honesty applies: a Critical/High finding may not be quietly
   `DEFERRED` — that disposition needs the user's explicit agreement.
3. **Re-check standing entries.** Any `DEFERRED` trigger now fired → back to `NEW` for a fresh
   disposition. Any `SCHEDULED` entry whose ride is this run's likely next step → tag it so Step 4
   passes it into the invoked skill's target. Any entry the tree shows resolved → `DONE`.
4. **Batch the user questions — but only within the same tier.** Collect all ripe `NEEDS-USER`
   entries, sort them by **tier precedence** (below), and surface only the entries at the
   *highest* tier present. Before batching, check each lower-tier ripe entry for **tier
   dependency**: would a plausible answer to a higher-tier open question change, narrow, or
   moot this question? (E.g. a Vision-level tension about tone reframes what a Requirements-level
   economy question is even asking.) If yes, hold the lower-tier entry back this run — do not ask
   it alongside the higher-tier one — and re-derive whether it's still live once the higher-tier
   answer lands. If a lower-tier entry is genuinely independent of every open higher-tier question
   (touches a different, unrelated part of the tree), it may still batch into the same
   `AskUserQuestion` call rather than costing the user a second round-trip.

### Tier precedence for open threads

Open questions and gates form an altitude order — a decision at one tier can reshape or eliminate
a question at every tier below it, but never the reverse. When more than one tier has a ripe
`NEEDS-USER` entry or ungated question, address them **highest tier first, one tier per run**,
rather than surfacing all of them at once:

`01 Vision` > `03 Architecture (GDS ladder / ADS / ADR)` > `04 Requirements` >
`05 Feature Decomposition` > `06 Feature Specification` > `07 Implementation Planning` >
`08 Implementation` > `09 Verification` / `10 Integration` / `11 Release` (peers, gated by what
they review, not by further precedence among themselves). `02 Research` grounds `01`/`03` and is
asked only if the *specific* higher-tier question in front of it needs a domain fact — it does
not get its own precedence slot.

Applying this:

- **Don't ask a lower-tier question the tree hasn't earned yet.** If a Vision-level tension is
  still open (e.g. an unresolved Open Question in `00-vision.md`/`MSTR-001` bearing on the same
  feature), route there first — a downstream Architecture/Requirements-level question that
  depends on the answer is premature, not merely optional.
- **Re-check, don't re-ask, after a higher tier resolves.** Once a higher-tier answer lands, the
  triage step re-derives the lower-tier entry fresh (per Step 2.3) rather than replaying a
  question drafted before the higher-tier context existed — the answer may have already resolved
  it, changed its shape, or made it moot entirely.
- **Independent threads don't wait on each other.** Tier precedence governs questions that
  actually depend on one another (same feature/cluster, a plausible higher answer would change
  the lower question's premise) — it is not a rule that only one open thread in the whole tree
  may be asked about at a time. Unrelated threads at different tiers (e.g. a Release GO call for
  a shipped feature and a Vision question about an unrelated future one) can proceed in parallel.
- **Record the hold, not just the ask.** When a lower-tier entry is held back for this reason,
  note it in the entry's disposition (still `NEEDS-USER`, but annotate "held pending <higher-tier
  ID/question>") and in the run's journal row, so the next run knows to re-check it rather than
  treating it as forgotten.

### Step 3 — Determine the single next step

From the reconciled position **and the triaged backlog**, pick the highest-leverage unblocked
step, using the pipeline's ordering rules (see `README.md`) and the **tier precedence** above:
upstream findings before downstream work; a due backlog item outranks new scope at the same
stage; within a stage, critical-path first; the per-feature loop (06→07→08→09) drains before the
per-release stages (10→11) run. A ripe higher-tier open question (Vision/Architecture) always
outranks proceeding into a dependent lower-tier step, even one already `SCHEDULED`. If the
journal's recorded next step is still valid and no due backlog entry or higher-tier open question
outranks it, that's the default. If several steps are genuinely parallel (see above), pick one and
name the others in the report.

**When `docs/roadmap/04-release-roadmap.md` exists**, use its release sequence and dependency
graph as a **tie-breaker among already-unblocked, backlog-cleared candidates** — e.g. preferring
the step that advances the roadmap's named critical-path release, or picking one of several
genuinely-parallel roadmap streams to name as this run's choice while listing the others as
parallel options in the report (same as any other parallel-step case above). The roadmap **never**
overrides tier precedence, never skips a gate a roadmap release's own entry names as a precondition
(that precondition is gate-checked normally in Step 4, not specially), and never justifies invoking
a stage out of the pipeline's own upstream-before-downstream order. If the roadmap and the
backlog-derived recommendation genuinely conflict (the roadmap names one release as next but a
higher-tier open question or a due Critical/High backlog item points elsewhere), the backlog/tier-
precedence recommendation wins — note the conflict in the run's journal row so the roadmap can be
corrected by whichever skill owns the affected release entry.

**During the first, from-scratch increment**, the ordering is simply the first stage whose
artifacts don't exist yet, 01 upward — there is no as-built baseline to derive from, so `01-vision`
genuinely comes first and each stage waits on its real upstream input rather than mining a shipped
ROM.

### Step 4 — Gate check (hard stops — ask, never assume)

Before invoking anything, stop and ask the user (via `AskUserQuestion`) if the step requires:

- **G3 authorization** — the step would implement a package that is neither (a) already scheduled
  by the current, user-approved release plan in the shape the plan describes, nor (b) carrying its
  own explicit user go-ahead on record. Release-plan coverage satisfies G3 automatically — cite
  the matching release-plan section/row rather than asking again. A package not on the release
  plan, or diverging materially from what it describes (different scope/approach, or a plan the
  user hasn't actually approved), still requires a fresh per-package go-ahead before any
  `08-code-implementation`/`08-content-authoring`/`08-refactoring` run;
- **a release GO** — the step would flip baseline records;
- **adjudication** — the step builds on a review with unadjudicated Critical/High findings;
- **a ripe `NEEDS-USER` backlog entry** — the decision the entry is waiting on is needed now, and
  per tier precedence, only the highest-tier ripe entry (plus any tier-independent ones) is put
  to the user this run — lower-tier entries that depend on it are held, not asked;
- **spending judgment the user reserved** — anything a stage skill's own rules say needs the user.

A gate stop is a complete, successful step: journal it (`GATE: …`). In `step` mode this ends the
run immediately. **In iterate mode, a gate stop ends the whole loop** — this is the one thing
that terminates iteration before the backlog/next-step queue is empty. Record the user's answers
in the backlog/journal when they come; the next invocation (whichever mode) picks up from there.

### Step 5 — Execute by invoking the owning skill

Invoke the owning numbered skill via the `Skill` tool with the specific target — including any
`SCHEDULED` backlog entries riding this step. Follow that skill's own rules completely — the
manager adds no shortcuts and removes no obligations. One skill invocation per internal step —
in iterate mode, the next internal step gets its own fresh Step 5, never two invocations folded
into one.

### Step 6 — Harvest, then journal the run

**Harvest first, while the invoked skill's completion summary is still in context:** every
finding, recommendation, Outstanding Issue, and Open Question it reported becomes a backlog entry
(`NEW`, sourced to this run) unless one already exists (then update that entry). Flip to `DONE`
any backlog entry this step resolved.

Then append the run-log row and rewrite the Position block from the post-run state, including the
backlog line. Commit the journal + backlog together (and nothing else — the invoked skill
committed its own work per its own conventions).

### Step 7 — Report

In `step`/`status`/`triage`/`log`/`sync`/`run` modes: report immediately after this one step, per
the mandatory completion summary below.

**In iterate mode: do not report after each internal step.** The journal and backlog already carry
the durable record of every step taken (that's what makes them the persistent memory) — the
chat-facing report is a separate, one-time thing composed only once the loop actually stops
(genuine gate, or the queue is empty). Loop back to Step 1 instead of narrating progress
mid-run — see "Pipeline position & completion summary" below for what the single, end-of-loop
report contains.

## Refactoring — explicit scheduling conditions

Refactoring (behavior-preserving code restructuring, meaning-preserving doc restructuring —
executed only by `08-refactoring`, grounded in encyclopedia topic `R307`) is deliberate
housekeeping, not a default: the manager schedules it only under the conditions below, and never
lets it ride along with feature or fix work.

**When the manager PROPOSES refactoring** (files or recommends a `refactor`-type backlog entry —
via harvest, or by naming `00-intake` in its report; proposing is not scheduling):

- `10-integration-review` reports a structural finding (duplicated behavior, a module-boundary
  violation, index/doc incoherence spanning multiple owners) whose real fix is restructuring;
- three or more open backlog entries trace to the same structural cause (the manager names them
  on the new entry);
- a stage-08 run's Outstanding Issues repeatedly cite the same friction (a file too entangled to
  change safely, a doc too fragmented to update coherently);
- a release just went GO (stage 11 baseline flipped) and structural debt was noted during the
  release — the post-GO / pre-next-increment window is the preferred slot for refactoring.

**When the manager may SCHEDULE the planning step** (`07-implementation-planning` authoring an
`IP-8xx0` from a `refactor` backlog entry) — all of:

1. the `refactor` entry is dispositioned `SCHEDULED` with the user aware of it (it appeared in a
   run report or was filed by the user via `00-intake`);
2. no Critical/High `bug` entry is open at the same entry stage — correctness always outranks
   structure;
3. the debt is stated as an observable cost (what it blocks, slows, or keeps breaking), not as
   taste.

**When the manager may INVOKE `08-refactoring` on an authored package** — all of:

1. the package is `READY` (dependencies `VERIFIED`) **and** clears G3 — either it is already
   scheduled by the current, user-approved release plan in the shape described, or it carries an
   explicit per-package user go-ahead on record (see the gate check);
2. the pipeline is **quiescent where it matters**: no package `IN PROGRESS`, and no
   `COMPLETE`-but-unverified package touches any file the refactor names;
3. the tree is green: the G5 gates pass as-found (never schedule a refactor onto a red tree — a
   due remediation runs first);
4. no release bucket is mid-close (between a `10-integration-review` and its `11` GO call) whose
   reviewed set overlaps the refactor's files — refactoring under review invalidates the review.

After the run, the normal loop applies: `08-refactoring` → `09-package-verification` (which
re-checks the equivalence evidence) before anything downstream builds on the moved structure.

## Guardrails

- **One skill invocation per internal step, always.** Whether in `step` mode or mid-iteration,
  never fold two stages into one pass "while I'm here" — the journal makes stopping/resuming
  cheap, so there's no efficiency gain in skipping the per-step discipline.
- **Iterate mode stops only for a genuine gate, never for scope.** A step being large,
  production-code-touching, or multi-package is not a reason to pause — only G3, G4, a
  Vision-level tension, a ripe `NEEDS-USER` item, an unadjudicated Critical/High finding, or a
  truly empty queue stop the loop. If tempted to stop early because a step "feels like it should
  ask first," check: is this actually one of those five, or just unfamiliar/large? Only the
  former stops iteration.
- **Don't narrate mid-loop.** In iterate mode, no chat-facing report between internal steps —
  only the journal/backlog writes. The user sees one report, at the end.
- **Higher tier first.** Never put a lower-tier open question to the user while a higher-tier
  one it depends on (per tier precedence) is still ripe and unasked — resolve altitude before
  detail, so the user is never asked a question a Vision/Architecture answer would have changed.
- **No finding left in chat.** If a stage skill said it, the backlog holds it — harvest is part
  of the run, not an optional courtesy.
- **Never bypass a gate**, even in `run <skill>` override mode. Overrides change *which* step
  runs, never *whether* a human decision is required.
- **Never perform stage work inline.** If the next step looks "too small to bother invoking the
  skill for," invoke the skill anyway.
- **Never edit any ledger the stages own.** Drift between a ledger and reality is routed to the
  owning skill; the manager only corrects its *own* journal and backlog.
- **The journal and backlog are honest or they are useless.** A run that failed, stalled, or hit
  a gate is journaled as exactly that.

## Quality gate (every run)

- [ ] The journal and backlog were read first, and the Position block was verified against the
      real ledgers — not trusted blind.
- [ ] Every `NEW` backlog entry left this run with a recorded disposition, and no Critical/High
      entry was deferred without the user's explicit agreement.
- [ ] If more than one tier had a ripe open question, only the highest tier (plus genuinely
      tier-independent ones) was put to the user this run — no lower-tier question was asked
      while a higher-tier one it depends on was still unresolved.
- [ ] The invoked skill's findings were harvested into the backlog before the next step was chosen.
- [ ] Exactly one skill was invoked per internal step (or zero, for status/log/sync/triage/gate
      steps) — in iterate mode, this holds for *every* step in the loop, not just the first.
- [ ] Every gate touched by any step was stopped at and asked about — none assumed, and in
      iterate mode a gate hit anywhere in the loop actually ended the loop rather than being
      talked past.
- [ ] In iterate mode, the loop did not stop early for a step that merely looked large or
      unfamiliar — only for one of the five genuine gate conditions or a truly empty queue.
- [ ] Every run-log row, Position-block rewrite, and backlog update — one per internal step — was
      written and committed before the next step was chosen, and matches what actually happened.
- [ ] In iterate mode, no chat-facing report was produced between internal steps — the loop ran
      silently (from the user's perspective) until it actually stopped.
- [ ] Nothing outside `docs/pipeline/` was written by the manager itself.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 00 — the manager**; it can be run at any time and is the default entry point
for all pipeline work (its stage-00 peer `00-intake` files new features/bugs into the backlog this
skill triages).

**`step`/`status`/`triage`/`log`/`sync`/`run` modes:** end that single run with a chat summary
containing exactly these three parts:

1. **What happened** — mode, skill invoked (if any) and its outcome in one line, journal row
   appended, backlog deltas (harvested / dispositioned / closed, by ID), any drift corrected.
2. **Recommendations** — open gates awaiting the user, `NEEDS-USER` backlog entries and the exact
   decisions they need, parallel steps available, drift found and who owns it.
3. **Next step** — what the next invocation will execute (skill + target + any backlog entries
   riding along + why), or the exact decision needed if the pipeline is gated on the user.

**Iterate mode (no args): produce this same three-part summary exactly once, when the loop
actually stops** — not after every internal step. Since the loop may span many stages, the
summary's shape adapts to cover the whole run:

1. **What happened** — the full chain of internal steps taken this run, in order (skill invoked
   + one-line outcome for each — a compact list, not a re-narration of every stage's own detailed
   completion summary), every journal row appended, every backlog delta across the whole run
   (harvested / dispositioned / closed, by ID), any drift corrected along the way.
2. **Recommendations** — same as above, covering everything surfaced across the whole run, not
   just the last step.
3. **Next step** — **the exact gate that stopped the loop** (a specific `AskUserQuestion`-ready
   decision — G3 on named packages not covered by the release plan, a G4 GO/NO-GO call, a
   Vision-level question, a `NEEDS-USER`
   backlog item's exact decision) if a gate stopped it, or confirmation that the backlog/next-step
   queue is genuinely empty if nothing did.

Never end a run without naming the next step (or the gate that's blocking it) — that line is the
whole point of having a manager, in either mode.
