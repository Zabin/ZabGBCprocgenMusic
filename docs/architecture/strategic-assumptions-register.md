# Strategic Assumptions Register

- **Owned by:** `01-vision` · **Status:** ✅ Authored 2026-07-22 (first authoring — previously
  `⛔ Planned`; written now as part of a `01-vision` consistency check following the completion
  of the full 39-topic research encyclopedia, per `docs/architecture/INDEX.md`)

The explicit assumptions MSTR-001/GDS-00 rest on, each with a trigger condition — the point at
which the assumption should be revisited, not silently kept or silently broken. This register
does not itself change anything; when a trigger fires, that's a finding routed to `01-vision` (if
the assumption is genuinely load-bearing for what the project *is*) or to the owning downstream
skill (if it's a design-level consequence).

| # | Assumption | Basis | Trigger — revisit when |
|---|---|---|---|
| A1 | The GBC's four native sound channels (two pulse, one wave, one noise) are sufficient for the intended musical range without external chips or additional channels. | MSTR-001 C7; confirmed in practice — all 7 Foundation packages ship a full 4-channel generative mix within this constraint. | A future increment's design intent genuinely can't be expressed within 4 channels (e.g. wants true polyphony beyond 4 simultaneous voices) — no such need has surfaced through `BL-0020` or any other backlog entry to date. |
| A2 | PyBoy headless remains the sole verification target for both audio-register and visual (VRAM/tilemap/palette) state. | MSTR-001 C9; R301/R305 (PyBoy API + test-design grounding, both `✅`). | Real-hardware or a second-emulator (R309: SameBoy/BGB) cross-check becomes necessary — e.g. a PyBoy-specific timing quirk is suspected to diverge from real hardware behavior. No such divergence has been found; `BL-0015`'s one-frame `BAD_ZONE_FLAGS` transient remains an open, low-severity, not-fully-root-caused PyBoy-timing question that could someday motivate this. |
| A3 | The Python-assembler approach (no RGBDS or other external toolchain) remains the build strategy. | MSTR-001 C3; R302 (confirmed the label/fixup two-pass assembler pattern scales cleanly across 9 packages, including correctly surfacing `IP-0007`'s one `JR`-out-of-range incident rather than silently mis-assembling it). | The hand-rolled assembler's error surface (currently: duplicate labels, unresolved labels, out-of-range relative jumps) stops catching real mistakes, or a package needs an assembler feature (macros, conditional assembly) genuinely painful to hand-roll. No such need identified. |
| A4 | The generator runs entirely on-device, in real time, every frame — not selecting among pre-baked tracks. | MSTR-001 C6; the entire shipped `_emit_channel_gen`/`_emit_noise_gen`/`_emit_badzone_tick` design. | This is closer to a defining commitment than a revisitable assumption — see MSTR-001 §7's higher bar for changing §1-§4 directly, rather than this register, if it's ever questioned. Listed here for completeness, not as something with a plausible near-term trigger. |
| A5 | **Decided 2026-07-25 (R4.5 checkpoint) — re-confirmed single-bank, as a live evidence-based choice, not a default.** Current framing: "the ROM ships single-bank, no MBC, no SRAM, by deliberate deferral with named re-triggers — not by unexamined inertia." | Was based on MSTR-001 C1/C2/§4 v1.0-v1.1 non-goals; R106/R112 confirmed the *current shipped* ROM is single-bank, cart-type `0x00`. R106 (extended)/R302 §8-9 supplied the adoption-cost facts (MBC5 recommended if ever adopted, PyBoy not a blocker, bank-switching is real assembler-architecture work). **2026-07-25**: `03-architecture-design-synthesis` made the deferral call — [ADR-0002](ADR-0002-defer-mbc-adoption-single-bank-retained.md) — grounded in measured evidence (10.4% of the single 32KB bank used after R1-R4 shipped; 29349 bytes free; no roadmapped feature through Milestone D requires persisted state). | **Fired and resolved this cycle.** Next re-trigger: ROM usage crossing ~75% of the single bank (measured via the same `rom.pos`-instrumentation method ADR-0002 used), or a save-requiring feature reaching an approved FR in `04-requirements-engineering` — whichever comes first. Revisit this row when either fires. |
| A6 | Determinism (a fixed seed reproducing a fixed sequence) is a testing tool only, not a listening-experience requirement — the engine is expected to feel different across un-seeded runs. | MSTR-001 C6; R213 (PRNG/seed management, `✅`) — `IP-0007`'s `DIV`-seeded reload already implements exactly this split (deterministic preset values, randomized per-channel walk seed). | A future feature wants a *shareable* or *replayable* specific sequence (e.g. "show me what seed X sounds like") — would need an explicit seed-entry/display mechanism neither MSTR-001 nor any current package provides; no such request is on record (`R217`'s UX-conventions topic notes most of its own seed-entry-convention questions are already answered by existing decisions, i.e. by *not* having seed entry). |
| A7 | Dependency availability for the verification toolchain (`pyboy`) can be assumed present, without a pinned manifest. | Implicit in the original build — no `requirements.txt` was ever authored. | **This assumption no longer holds — the trigger has already fired.** `R306`/`BL-0023` (filed this session) document repeated, real friction: every fresh-session `09-package-verification` run this project has ever had needed an unplanned `pip install pyboy` before proceeding. This is not a vision-level concern on its own (it doesn't change what Driftune *is*), but is recorded here because it's exactly the kind of silently-assumed-true condition this register exists to catch, and its trigger is the first one in this table to have actually fired. Routed to `BL-0023`'s own disposition (a small toolchain addition), not a vision change. |

## How this register is used

- **Not itself authoritative** — MSTR-001 §1-§4 remain the source of truth; this table exists so
  "is X still true?" has one place to check rather than being re-derived from scattered code
  comments.
- **Reviewed whenever `01-vision` runs a consistency check** (this authoring is the first such
  pass) — each assumption's trigger is re-evaluated against the current tree/backlog state, the
  same way this authoring did for A7.
- **A fired trigger doesn't automatically change anything** — it's a finding, routed to whichever
  skill owns the actual response (vision, architecture, or a normal backlog item), per this
  register's own "when a trigger fires" rule above.
