# GDS-06 — Non-functional Requirements

- **Level:** GDS-06 of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26
- **Upstream:** [GDS-02 System Context](02-system-context.md) (§6's measured constraint table),
  [GDS-03 Architecture](03-architecture.md), research `R101`, `R102`, `R110`, `R113`, `R301`,
  `R302`, `R304`, `R305`, `R306`, `R308`
- **Downstream:** `docs/requirements/01-functional-requirements.md`'s `NFR-xxxx` leaf statements
  (see §0 for how the two relate), and `ADR-0002`'s cart-shape re-trigger conditions

## §0 What this level is — and how it differs from `NFR-xxxx`

This project already has 17 non-functional requirements (`NFR-1000`…`NFR-1160`) in the
requirements baseline, each individually testable and traced. So a fair question, which no
document currently answers, is what a *ladder-level* non-functional requirements document is even
for. Answering it is this level's first job, because getting it wrong would produce a duplicate of
the baseline with worse traceability.

**The answer this level records:**

| | **GDS-06 (here)** | **`NFR-xxxx` (requirements baseline)** |
|---|---|---|
| Grain | one **discipline** per category | one **testable statement** per requirement |
| Asks | *why does this ceiling exist, what does it protect, and what happens if it's breached?* | *is this specific property true, and how is it verified?* |
| Changes when | the system's constraints or their rationale change | a feature adds a new property to hold |
| Verified by | inspection and judgement — it is a standing posture | a named test, analysis, or demonstration |
| Owner | `03-architecture-design-synthesis` | `04-requirements-engineering` |

Concretely: `NFR-1010` says the per-frame work must complete without dropped frames and names the
stress-run method that checks it. GDS-06 §2 says *why* a per-frame ceiling exists at all, what the
project currently knows and does not know about its actual headroom, and what the project has
agreed to do when evidence suggests the ceiling is being approached. The baseline statement is
falsifiable; the ladder statement is the posture that decides whether the baseline statement is
still the right thing to be asserting.

**On GDS-05.** GDS-05 (Functional Requirements) stays `⛔ Planned` and is recorded as *superseded
in ordering*, not owed. On this increment the capability-level FR work was done directly by
`04-requirements-engineering` against GDS-01/03/04, and `FR-1000`…`FR-1380` now cover the shipped
capability set at leaf grain. Authoring a GDS-05 now would be reverse-engineering a
capability-level summary out of a leaf baseline that already traces cleanly — busywork producing a
second thing to keep in sync. It is deliberately not owed. GDS-06 *is* authored, despite the same
surface argument applying, because the table above shows it carries content the leaf baseline
genuinely does not hold: rationale, breach consequences, and the unquantified-headroom posture in
§2 that no `NFR` states and none could.

## §1 ROM budget

**The discipline:** Driftune fits in a single 32KB ROM bank with no bank switching, and every
package states its byte cost against that ceiling before it is built.

**Current measured state:** 4240 of 32768 bytes used — **28528 free, 87% headroom** (`ADR-0002`'s
own `rom.pos` instrumentation, the project's agreed measurement convention). Sixteen shipped
packages have consumed 13% of the budget between them.

**What it protects.** Not space for its own sake — it protects `ADR-0002`'s deferral of MBC and
bank-switching adoption. Single-bank is a *simplicity* commitment: no bank register, no far-call
convention, no split-across-banks data tables, no bank-aware build layout. Every one of those is
a real complexity the project has chosen not to carry, and the budget is what keeps that choice
honest rather than accidental.

**On breach.** `ADR-0002` names the re-trigger explicitly: if a genuinely wanted feature cannot
fit, the cart-shape decision reopens — the response is *reconsider the ADR*, not squeeze. `R308`
separately confirms that compression (the usual first reflex) would be pure cost at this scale,
and that the memory-mapped-in-place model this project already uses is the correct one; so
compression is a non-answer here, recorded so nobody reaches for it first.

**Practical margin.** At the historical rate — roughly 100–450 bytes per feature package — the
remaining headroom accommodates dozens more packages. The budget is not a near-term constraint
and should not be treated as one in design discussions.

## §2 Timing discipline — and the headroom nobody has measured

Two separate timing disciplines apply, and they have very different evidentiary standing.

### §2.1 VBlank gating (well-founded)

**The discipline:** all VRAM/visualizer writes happen inside the VBlank window. The main loop
`HALT`s until the VBlank ISR sets a flag, clears it, then runs `read_joypad` → `apply_input` →
`engine_tick` → `update_visuals` exactly once (`build_rom.py`; `R110`'s interrupt-driven
synchronization convention). Writing VRAM outside VBlank produces dropped or corrupted writes on
this hardware (`R102`), so this is a correctness discipline, not an optimization.

**Standing:** solid. The gate is structural — there is exactly one place visualizer code runs, and
it is inside the gated region by construction.

### §2.2 The per-frame CPU budget (unquantified — and now with contrary evidence)

**The discipline as stated:** all per-frame work — joypad, input application, four channels of
generation, bad-zone scoring, song-form tick, visualizer update — completes within one frame.

**What the project actually knows:** that no frame drop or hang has been *observed* across
repeated 8000–20000+ frame stress runs, in every `VR-000x` through `VR-1110`. That is the whole
evidence base. `NFR-1010` encodes exactly this empirical method and nothing stronger.

**What the project does not know:** how much headroom actually remains. **No cycle count has ever
been taken.** `R101` and `R308` both examined this and both concluded — reasonably, at the time —
that cycle-exact accounting would be over-engineering given a ~4MHz CPU and short per-frame
routines, with `R308` recording "no cycle-counting tooling exists yet" and `R101` recording that
"per-frame budget evidence is empirical, not derived from a cycle table."

**But `R101` also named the condition for revisiting**, and it is worth quoting because the
condition appears to have been met:

> *"Do revisit this topic with real per-instruction cycle tallying if a future package pushes
> per-frame work close to the VBlank budget (a symptom would be `R308`-style stress testing
> starting to show occasional frame drops)."*

`IP-1110` shipped with a disclosed, independently reproduced finding: **on the exact frame Select
is pressed, that frame's settings-indicator VRAM writes are silently dropped.** The root cause is
CPU cost — `apply_input`'s full `init_engine` reset on a Select edge is enough extra work that
`update_visuals`'s later writes fall outside the safe window. `VR-1110` reproduced it across three
distinct button sequences; the display self-heals the next frame, so no requirement is violated
and it was correctly accepted as shipped behavior.

**This level's judgement: that is the symptom `R101` described, arriving through a slightly
different door than expected.** Not "occasional dropped frames" under stress, but a *specific,
reproducible frame class* where per-frame work demonstrably exceeds what the VBlank window can
absorb. The project's per-frame budget is therefore known to be closer to its edge, on at least
one frame class, than the "generous budget, empirical proxy is adequate" posture assumed.

**The posture this level records, accordingly:**

1. The empirical stress-run method remains the primary check — it is cheap, it runs on every
   package, and it has caught real problems.
2. It is **no longer sufficient on its own** for any package that adds work to the Select-reset
   frame or to `update_visuals`. Such a package should state its per-frame cost impact
   explicitly rather than relying on "stress runs were clean," because stress runs without a
   Select press will not exercise the frame class already known to be tight.
3. The cycle-tallying follow-up `R101` describes (adding documented cycle costs to `gbc_lib.py`'s
   opcode emitters so `build_rom.py` can assert a static per-routine budget) is now a **grounded,
   triggered recommendation** rather than a hypothetical one — see §6 Open Question 1.

## §3 Save integrity — deliberately empty

**Driftune persists nothing.** Cart type is ROM-ONLY, there is no SRAM, no battery, and no save
file (`ADR-0002`; asserted by `test_rom.py` `T1.4`). Every session starts from the same boot
preset, and the only "persistence" in the system is the ROM's own immutable data tables.

This category is therefore **genuinely empty, not merely unaddressed** — there is no save format
to checksum, no corruption case to handle, no migration concern, and no integrity requirement to
state. Recorded explicitly rather than omitted, because an empty section and a forgotten section
look identical in a document, and the ladder table lists this category as one GDS-06 must cover.

`MSTR-001` C2 reopened persistence as a *question* (the prior blanket "no save" commitment was
withdrawn as an arbitrary decision mistaken for a firm one), and `ADR-0002` deferred adoption with
named re-triggers. So this section may stop being empty. If it does, the integrity requirements
that a save format needs — magic/version bytes, checksum, fresh-boot-on-invalid behavior — enter
here first and reach the baseline as `NFR-xxxx` afterward.

## §4 Build determinism

**The discipline:** the same source tree always produces the same ROM bytes. No timestamps, no
build IDs, no randomness at build time, no environment-dependent output.

**Why it is load-bearing here specifically:** `09-package-verification` runs in a genuinely fresh
session and independently rebuilds the ROM to check the implementing session's claims. If the
build were nondeterministic, that check would be meaningless — a byte difference could not be
distinguished from a build artifact. Determinism is what makes independent verification a real
check rather than a ritual. It is also what lets `ADR-0002`'s `rom.pos` measurement be compared
across packages at all (§1).

**Current state:** holds. The build is pure Python computation over fixed inputs (`R302`);
`gbc_lib.py`'s two-pass label resolution is deterministic; every data table is computed from
constants. Sixteen packages of independent rebuild-and-compare have found no discrepancy.

**One honest gap, inherited from GDS-02 §6:** determinism of *output* holds, but reproducibility
of the *environment* does not — there is still no dependency manifest, so a fresh session must
discover and install PyBoy by hand before it can run the suite at all (`R306` §4 documents this
happening on every independent verification run in project history; `BL-0023`). That is an
environment-reproducibility gap, not an output-determinism gap, but it lives in the same
discipline and is named here rather than being allowed to fall between the two.

## §5 Test-coverage bar

**The discipline:** every shipped behavior is covered by at least one headless test that drives
real input and asserts on real hardware/engine state — `MSTR-001` C9's generalization of the
reference project's gate, requiring **sound-register and engine-state assertions**, not merely
"does it boot."

**Current measured state:** 122 checks across 18 suites (`T1`–`T18`), all passing, run as a
permanent gate (G5) on every stage-08 package and re-run independently by every stage-09
verification.

**What it protects:** the ability to change a real-time audio engine at all. Sound is not
inspectable by reading code, and the PSG's frequency registers are write-only (`R108`/`R111`), so
without the WRAM state mirror and the assertions built on it there would be no way to distinguish
"the engine changed" from "the engine broke." The bar is what makes the whole pipeline's
downstream verification meaningful.

**Standing weaknesses, honestly named** (all currently accepted, none blocking): several shipped
tests are narrower than the claims they appear to support — `BL-0044` (a statistically weak
sample), `BL-0045` (a collision test whose fixture never actually collides), `BL-0052` (one of
three boundaries exercised), `BL-0057` (one of several sequences exercised). In each case an
independent verification run constructed the stronger check and confirmed the behavior; the
*shipped suite* is what remains narrower. The pattern is consistent enough to be worth stating as
a discipline-level observation rather than four separate findings: **this project's tests tend to
demonstrate a mechanism works once, where the claim being made is that it works generally.** The
standing correction is that stage-09 verification is expected to construct the general case
independently — which it has, every time.

## §6 Open Questions

1. **Should cycle-cost tallying be added now?** `R101`'s own revisit trigger appears to have
   fired (§2.2): `IP-1110`'s Select-frame write drop is reproducible evidence of per-frame work
   exceeding the window on a specific frame class. The follow-up `R101` itself specifies — cycle
   costs on `gbc_lib.py`'s opcode emitters, a static per-routine budget assertion in
   `build_rom.py` — is now grounded rather than hypothetical. Genuinely open because the cost is
   real (touching every opcode emitter) and the current symptom is cosmetic and self-healing.
   Owner: `02-research-tooling-and-testing` to re-derive the recommendation against this new
   evidence, then `07-implementation-planning` if it stands.
2. **Is the Select-frame drop the only tight frame class?** Nobody has looked. The same reasoning
   would apply to any frame combining heavy `apply_input` work with visualizer writes — a Start
   press triggers style application on the same frame as its own visualizer update, and a
   song-form phase transition writes two indices on a frame the visualizer then renders. Neither
   has been probed for dropped writes the way Select was, and both were only found *because*
   `IP-1110` gave the visualizer a value that visibly changes. Owner: `09-package-verification`
   or `10-integration-review` as a targeted probe; cheap to answer.
3. **Does the test-coverage bar need a stated generality standard?** §5's pattern (tests
   demonstrating a mechanism once where the claim is general) has recurred four times and been
   caught four times by independent verification. That is a working system — but it works because
   stage 09 is diligent, not because anything requires it. Whether to state the expectation
   explicitly (as an `NFR`, or as a stage-08 authoring rule) is open. Owner:
   `04-requirements-engineering` or the stage-08 skill's own conventions.
4. **When does the ROM budget stop being a non-constraint?** At 87% free it currently constrains
   nothing, and treating it as tight would distort design decisions. But `ADR-0002`'s re-triggers
   are stated in terms of features that *don't fit*, which is a lagging indicator. Whether a
   leading threshold is worth naming (e.g. "revisit cart shape when free space drops below 8KB")
   is open. Owner: `03-architecture-design-synthesis`, as a possible `ADR-0002` amendment.

## Merge gate

- [x] The previous level's gate (GDS-04) was verified closed before this level started — its own
      prose records "Gate: closed 2026-07-26."
- [x] All five categories the ladder table names are covered — ROM budget (§1), timing discipline
      (§2), save integrity (§3, **explicitly empty rather than omitted**), build determinism (§4),
      test-coverage bar (§5).
- [x] Grounded in measured numbers pulled forward from GDS-02 §6 and `ADR-0002`'s own
      instrumentation, not restated from a distance.
- [x] No production code, no byte layouts.
- [x] No new research claims originated — §2.2's judgement is `R101`'s own stated revisit trigger
      evaluated against `IP-1110`/`VR-1110`'s own reported evidence, and it is routed back to
      `02-research-tooling-and-testing` (§6 Q1) rather than being decided here.
- [x] `docs/architecture/INDEX.md` §1 and `ROADMAP.md`'s stage-03 row updated together.

**Merge decision.** No text moves out of `Claude.md`/`memory.md`; neither carries
non-functional-requirement content today (the build/test commands they hold are procedure, not
discipline). This level does **not** supersede `NFR-1000`…`NFR-1160` either — §0's table records
the two as different grains serving different questions, and both stay authoritative in their own
lane. The one relationship worth cross-linking: `NFR-1010` (the per-frame timing requirement) now
has a rationale-and-posture home in §2.2, including the evidence that its empirical method is no
longer sufficient on its own for a specific class of package. `04-requirements-engineering` should
consider whether `NFR-1010`'s own text wants a pointer here; that is its call, not this level's,
and it is recorded as such rather than pre-empted.

**Gate:** closed 2026-07-26. GDS-05 remains deliberately not owed (§0). Next unauthored level:
GDS-08 (Presentation Architecture).
