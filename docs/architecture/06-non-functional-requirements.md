# GDS-06 — Non-functional Requirements

- **Level:** GDS-06 of the global design-synthesis ladder · **Owned by:**
  `03-architecture-design-synthesis`
- **Status:** ✅ Authored 2026-07-26 · **§2.1/§2.2 corrected and §2.3 added 2026-07-31** (`BL-0069`) — §2.2's dropped-VRAM-write causal story was falsified by direct measurement; the judgement it supported survives on stronger evidence. See §2.2a.
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

**Standing (as recorded 2026-07-26):** ~~solid. The gate is structural — there is exactly one place
visualizer code runs, and it is inside the gated region by construction.~~

> **Correction — 2026-07-31 (`BL-0069`).** The sentence above is half right, and the half that is
> wrong is the half people read it for. Superseded text kept visible deliberately; the corrected
> standing follows.

**Standing (corrected 2026-07-31): sound in mechanism, marginal in budget — "solid" is the wrong
word.** The distinction this level failed to draw is between *entering* the window and *fitting
inside* it, and only the first is structural.

- **Vindicated.** The gating mechanism is exactly as described, and measurement confirms it:
  `HALT` wakes at `LY` = 144 — the first scanline of VBlank — on every frame, of every class,
  without exception. There is exactly one place visualizer code runs and it is inside the gated
  region by construction. Nothing about the main-loop design is wrong.
- **Refuted.** "Structural by construction" was written, and has since been cited, as though it
  implied the writes therefore *land* inside VBlank. That does not follow. The construction
  guarantees the window is **entered**; it guarantees nothing about the work **fitting**. Measured
  (`R308` §8.5): `read_joypad`+`apply_input`+`engine_tick` consume roughly **9 of VBlank's 10
  scanlines** before `update_visuals` begins, and the shipped ROM's `update_visuals` finishes at
  `LY` = **153 — the last scanline of the window**. Adding ~7 diagnostic stores per frame was
  enough to push the visualizer's writes past the boundary entirely. The head-room is measured in
  instructions, not scanlines, and **nothing in the build guards it**: there is no assertion, no
  budget check, and no test that would fail if the next package spent it.

A discipline whose margin is a handful of instructions and whose margin is unmonitored is not
"solid." The accurate statement is: **the gate is structurally entered and empirically, narrowly
met — and it is one careless package away from being silently violated.**

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

> ⚠️ **The two paragraphs immediately below were falsified on 2026-07-31 — see §2.2a. They are
> retained, struck through, as the record of what this level believed and why. This level's
> *judgement* — that `R101`'s revisit trigger had fired — survives; its *causal story* does not.**

~~`IP-1110` shipped with a disclosed, independently reproduced finding: **on the exact frame Select
is pressed, that frame's settings-indicator VRAM writes are silently dropped.** The root cause is
CPU cost — `apply_input`'s full `init_engine` reset on a Select edge is enough extra work that
`update_visuals`'s later writes fall outside the safe window. `VR-1110` reproduced it across three
distinct button sequences; the display self-heals the next frame, so no requirement is violated
and it was correctly accepted as shipped behavior.~~

~~**This level's judgement: that is the symptom `R101` described, arriving through a slightly
different door than expected.** Not "occasional dropped frames" under stress, but a *specific,
reproducible frame class* where per-frame work demonstrably exceeds what the VBlank window can
absorb. The project's per-frame budget is therefore known to be closer to its edge, on at least
one frame class, than the "generous budget, empirical proxy is adequate" posture assumed.~~

### §2.2a Correction — 2026-07-31: the trigger fired, but not for the stated reason (`BL-0069`)

`IP-9030` was planned to quantify the drop described above. Stage 08 built the diagnostic, took
the measurement, and the measurement falsified the premise; the package is `BLOCKED` and carries
the evidence, and `R308` §8.5 records the research-side correction. What follows is this level's
own re-derivation.

**What was wrong.** No VRAM write is dropped, on any frame class. Two independent lines of
evidence: PyBoy 2.7.0 applies no PPU-mode gating to VRAM writes at all (`R301` §3), so no
experiment in this harness could ever have observed a drop; and a WRAM mirror of each cell write
matches the VRAM byte on every frame of every class. The observed symptom was a `pb.tick()`
mid-frame sampling artifact producing a **uniform** one-frame display lag — on plain index steps
exactly as much as on Select, and on idle frames with no input at all. The Select-vs-`Up`
asymmetry that made the finding look decisive **does not exist**, and `VR-1110`'s independent
reproduction reproduced the sampling error rather than confirming the mechanism.

**What is right instead, and why the judgement stands.** `R101`'s revisit trigger fired — this
level's 2026-07-26 judgement was correct — but the symptom is broader and duller than a
"specific, reproducible frame class." On ROM-side live-`LY` evidence (`R308` §8.5), the per-frame
budget is **~exhausted on every frame, idle frames included**. `read_joypad`+`apply_input`+
`engine_tick` take ~9 of VBlank's 10 scanlines; `update_visuals` finishes on the last one.

**No frame class is special.** Select and Start are marginally more expensive, but they are not a
distinct category — they are a few instructions further along a budget that was already nearly
gone. This matters at this level because it changes the shape of the problem from *"one code path
is too heavy"* (fixable by shortening `init_engine`) to *"the per-frame budget is structurally
tight"* (not fixable by shortening any single routine). It is a worse finding than the one it
replaces, and it lands squarely on §2's own thesis: this is exactly the headroom nobody measured.

**A methodological note this level should carry**, because it is about how the ladder gets its
facts: the falsified claim was carefully derived, internally consistent, cited to real hardware
documentation, and independently reproduced — and wrong, because it inferred a *hardware*
mechanism from an *emulator* observation without checking whether the emulator models that
mechanism. `R305` §3 now carries this as a standing test-design rule. Design levels that cite
harness evidence for hardware claims are exposed to the same error.

**The posture this level records, accordingly:**

1. The empirical stress-run method remains the primary check — it is cheap, it runs on every
   package, and it has caught real problems.
2. It is **no longer sufficient on its own for any package that adds per-frame work at all**
   (widened 2026-07-31, §2.2a — the original wording named only the Select-reset frame and
   `update_visuals`, which is now known to be too narrow: no frame class is special, and the
   budget is tight on every frame including idle ones). Any such package should state its
   per-frame cost impact explicitly rather than relying on "stress runs were clean." A stress run
   cannot detect this: exhausting the VBlank budget produces no hang, no slowdown and no dropped
   frame — the engine keeps perfect time and only the write *placement* moves.
3. The cycle-tallying follow-up `R101` describes (adding documented cycle costs to `gbc_lib.py`'s
   opcode emitters so `build_rom.py` can assert a static per-routine budget) is now a **grounded,
   triggered recommendation** rather than a hypothetical one — see §6 Open Question 1.

### §2.3 What the harness structurally cannot verify (added 2026-07-31)

Placed here, in the timing-discipline section, because it is not a general testing caveat — it is
a specific hole in the verification of *this* discipline, and §2.1/§2.2a both depend on it.

**The project's test harness cannot verify VRAM write acceptance, and never could.** PyBoy 2.7.0
accepts every VRAM write regardless of PPU mode (`R301` §3, with the source citation); real CGB
silicon does not (`R102` §3). `R305` §5 now carries a can/cannot-establish table bounding every
suite the project will ever write. The consequences for this level:

- **§2.1's discipline is verified only up to write *issuance*, not write *acceptance*.** Every
  check in `T1`-`T18` that reads a tilemap cell confirms the ROM issued the write it intended.
  None of them confirms the PPU would have taken it. On silicon, a write issued at `LY` 0-9 —
  which the instrumented build showed happens as soon as a few instructions are added — lands in
  mode 2 or mode 3 depending on sub-scanline position, and mode 3 discards it.
- **This converts `GDS-02` §7's hardware gap from an aspiration into a named question.** That
  section records that Driftune has never run on physical hardware (`BL-0058`), framed as a
  general fidelity concern. It now has one specific thing to answer that nothing here can:
  *does the shipped ROM's ~one-scanline VBlank margin actually hold on real silicon?* Note the
  answer could differ from any emulator's in either direction, and that the failure mode would be
  cosmetic and self-healing (`GDS-08` §3), not a correctness defect.
- **A cheaper partial substitute exists and should be tried first.** A mode-accurate emulator
  (SameBoy/BGB — `R309`, cross-checking already named in `R305` §5 as available-but-not-required)
  would answer the same question without hardware. This level recommends that as the next
  concrete step, ahead of any remediation.

**What this level asks of future work:** do not write, and do not accept in review, a test whose
name claims a property from the cannot-establish half of `R305` §5's table. A check that cannot
fail converts an open question into a false record of coverage — which is precisely the failure
chain that ran from `R308` §8 through `VR-1110` to `IP-9030`.

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

1. **Should cycle-cost tallying be added now?** *(Restated 2026-07-31 — the premise changed, the
   question got sharper.)* `R101`'s revisit trigger has fired, now on direct measurement rather
   than on the falsified drop finding (§2.2a): the shipped ROM finishes `update_visuals` on
   VBlank's last scanline, on every frame, with head-room measured in instructions and guarded by
   nothing. The follow-up `R101` specifies — cycle costs on `gbc_lib.py`'s opcode emitters, a
   static per-routine budget assertion in `build_rom.py` — is correspondingly better grounded.
   Still genuinely open because the cost is real (~150 opcode emitters) and **there is now a much
   cheaper first option**: a runtime `LY` budget assertion (have the ROM record `LY` at entry to
   `update_visuals`, assert 144-153 in `test_rom.py`) costs a handful of instructions and one
   check, and would catch the regression this level actually fears. The honest sequencing is
   *cheap runtime guard first, static cycle table only if that proves insufficient*.
   Owner: `07-implementation-planning` (the `LY` guard, folded into `IP-9030`'s re-scoping);
   `02-research-gbc-hardware` still owes `R101`'s own correction.
2. ~~**Is the Select-frame drop the only tight frame class?**~~ **ANSWERED 2026-07-31 — and the
   question was malformed.** There is no Select-frame drop, and no frame class is distinctly
   tight (§2.2a). Every frame — including idle frames with no input — finishes `update_visuals`
   on VBlank's last scanline; Select and Start are a few instructions further along the same
   nearly-spent budget, not a separate category. The probe this question asked for was run (it is
   what produced §2.2a), so this closes as answered rather than deferred. **Replacement question,
   which is the live one:** *how much head-room is there actually, in cycles, and what guards it?*
   — carried by Open Question 1 above and by §2.3's recommendation to cross-check on a
   mode-accurate emulator.
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
