---
name: 00-intake
description: File new work into the pipeline backlog (docs/pipeline/backlog.md) — feature requests, bug reports, observations, research gaps, doc defects — so it enters the documentation-driven-development pipeline at the right stage instead of being implemented ad hoc. Classifies the request, gathers cheap read-only evidence for bugs (reproduce in the emulator, capture the failing behavior — never fix), checks for duplicates, determines the pipeline entry stage (code bug → 07 remediation package; feature within the approved baseline → 06; feature needing new requirements → 04; architecture/vision-scope idea → 03/01; research gap → 02; doc defect → the owning doc's skill), and appends a BL-xxxx entry for 00-pipeline-manager to triage. Use when asked to "add a feature," "report/log a bug," "file this idea," "put X on the backlog," or when any request would otherwise bypass the pipeline. It writes only the backlog — no code, no fixes, no specs, no packages; and filing an item is not a decision to build it.
---

# Intake

The pipeline's **front door**. New work — a feature idea, a bug someone hit, an observation, a
gap — gets captured here as a structured backlog entry with a recommended pipeline entry stage,
so the `00-pipeline-manager` can weigh it against everything else the pipeline owes. What intake
prevents: the quiet side-channel where a "quick fix" or "small feature" skips the pipeline and
breaks the traceability the whole system is built on.

It writes **only** `docs/pipeline/backlog.md` (append + its own entry's fields). No code, no
fixes — not even one-liners. No specs, no packages, no requirement edits. Filing an entry is not
scheduling it, and scheduling is not authorizing it: triage belongs to the manager, gates belong
to the pipeline (G3).

## Workflow

### Step 1 — Capture

Record what the user actually asked for, in their terms — the request as stated, before your
classification of it. Ask for the missing essentials only (for a bug: what happened, what was
expected, how to see it; for a feature: what need it serves, in which engine state/visualizer
screen). Note the user's stated urgency/priority if they gave one; don't invent one.

### Step 2 — Evidence (bugs only, read-only)

Cheap confirmation only: reproduce it if a test run or a quick emulator drive shows it (the
`run-driftune` utility skill builds the ROM, runs the test suite, and can drive PyBoy
headlessly with button input, sound-register reads, and screenshots). Capture the failing test/behavior and
observed-vs-expected. Whether it reproduces or not is recorded either way — "reported, could not
reproduce" is a valid entry. **Never fix anything**, however trivial; a one-line fix filed through
the pipeline stays traceable, a one-line fix made here doesn't.

### Step 3 — Classify and route

Pick the type and the **entry stage** — where this item enters the pipeline when the manager
schedules it:

| The item is… | Type | Entry stage |
|---|---|---|
| Wrong behavior in the shipped ROM / build scripts | `bug` | `07-implementation-planning` — a remediation package (bugs get packages too; that's what keeps the fix traceable) |
| A capability already covered by approved requirements/catalog but unspecified or unbuilt | `feature` | `06-feature-specification` (or `07` if an approved spec already exists) |
| A capability with **no** home in the approved requirements baseline (a new generation mode, button mapping, bad-zone metric, visualizer effect…) | `feature` | `04-requirements-engineering` (candidate requirement first) — or `03`/`01` if it implies new architecture or a vision change |
| A missing/uncertain domain fact (GBC hardware behavior, design convention, tooling question) | `research-gap` | the owning `02-research-*` skill |
| A defect in documentation/trackers | `doc-defect` | the stage skill that owns the artifact |
| Structural debt — code or docs that need restructuring with **no** behavior/meaning change (entanglement, duplication, fragmentation, naming drift) | `refactor` | `07-implementation-planning` — a refactoring package (`IP-8xx0`, executed by `08-refactoring`; the manager's explicit scheduling conditions apply). State the debt as an observable cost, not taste. |
| A concern/idea that needs a decision before it's actionable | `design-question` | wherever the decision lives; usually `NEEDS-USER` at triage |

When genuinely unsure between two stages, pick the **more upstream** one and say why — entering
too early costs a pass-through; entering too late skips a gate.

### Step 4 — Dedupe and file

Check the backlog (and, for bugs, open findings) for an existing entry covering the same thing —
if found, note the new report on that entry instead of duplicating it. Otherwise append a new
`BL-xxxx` row (next sequential ID): Filed (date + "intake: <requester's ask, condensed>"), Type,
Summary (with evidence links), Sev/Pri, Entry stage, Disposition `—` (the manager decides),
Status `NEW`. Commit as `docs(pipeline): intake BL-xxxx — <summary>`.

## Rules

- **Backlog only.** The moment this skill wants to touch any other file, the work has left
  intake's scope — file the entry and route it.
- **Honest severity.** A user saying "urgent" is recorded as the user's priority; the evidence's
  severity is recorded separately if it differs. Neither is inflated to jump the queue.
- **No promises.** Intake's summary never says the item *will* be built or *when* — it says where
  it enters and that the manager triages it next.

## Pipeline position & completion summary (mandatory, every run)

This skill is a **Stage 00 peer of `00-pipeline-manager`** — the manager drives the pipeline;
intake feeds its backlog. It can be run at any time, mid-anything, without disturbing pipeline
position.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What was filed** — the `BL-xxxx` entry (or the existing entry updated), type, entry stage,
   and the evidence captured.
2. **Recommendations** — anything the entry needs before it can be scheduled (a missing decision,
   an unreproduced bug needing more info from the reporter).
3. **Next step** — run `00-pipeline-manager` (`triage`, or a normal advance, which triages first)
   to disposition the new entry; note that for urgent items the user can ask the manager for a
   `run <skill>` override, which still honors every gate.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each summary to know what to invoke next.
