# Content Review — `IP-1150`, the arpeggio re-rooted, gated and varied

| | |
|---|---|
| **Scope** | `IP-1150` (`FS-115`/`FEAT-1160`, `BL-0127`) — what the two pulse channels sound *between* their onsets. Reviewed against `ADS-108` §12/D14, `ADR-0005`, `FS-115`, and `R216`/`R225`. |
| **Commit reviewed** | `61f0544` (`IP-1150` implementation), rebuilt from the tree; comparison baseline `3e635ed` (the immediately-preceding commit, per `NFR-1270`). |
| **Package status** | `COMPLETE`, **not yet `VERIFIED`** — fresh-session `09-package-verification` is owed and this review does **not** substitute for it. It is owed for `IP-1140` too. |
| **Result** | **Clean on the question asked** (`BL-0127` is resolved at the mechanism and at the output boundary), **2 findings**, both Medium, both routed and neither fixed here. |
| **Reviewer caveat, stated up front** | This review was performed by the same agent session that implemented the package, by measurement and by ear-*proxy*. **It is not a human listening pass and does not claim to be one.** The four holistic questions below are answered as honestly as a non-human reviewer can answer them, and the one they cannot settle is named explicitly. |

## Artifacts captured

| Artifact | Path |
|---|---|
| Audio, pre-change, default boot, ~20 s | `…/scratchpad/arp/clip_before_arpeggio.wav` |
| Audio, post-change, default boot, ~20 s | `…/scratchpad/arp/clip_after_arpeggio.wav` |
| Audio, post-change, a later ~20 s window (t≈45-65 s) | `…/scratchpad/arp/clip_after_later_window.wav` |
| Audio, pulse A isolated (`CHMIX` preset 3 = pulse A + unpitched noise), both builds | `…/scratchpad/arp/solo_before.wav`, `solo_after.wav` |
| Screenshots, both builds + all 6 controls driven | `…/scratchpad/arp/screen_before.png`, `screen_after.png` |
| PSG-write capture driver (the output-boundary instrument) | `…/scratchpad/arp/psg_old.py` |

(Scratchpad root: `/tmp/claude-0/-home-user-ZabGBCprocgenMusic/81e52049-8926-590d-862b-d87aa10a0ed7/scratchpad/arp/`.)

## The output-boundary instrument, and why it is the one that settles this

The skill's output-boundary rule exists because two confident, wrong numbers have already reached
a report by sampling an engine-internal field (`BL-0124`, and then `BL-0128` on `IP-1140`'s own
headline figures). So the primary measurement here is taken at the **strictest available
boundary**: a `pyboy` instruction hook on the two `LDH` instructions inside `arp_tick_pa` that
actually write `NR13`/`NR14`, reading the CPU's `A` register **at the instant of the write**. Not
`CUR_DEGREE`, not the new `ARP_CACHE` either — the byte going to the APU.

Both ROMs are hooked the same way. The pre-change ROM's label map is not the current tree's, so
its two writes are located by the identical byte pattern both builds share
(`7B E0 13 7A E6 07 E0 14`), first occurrence being pulse A's.

**The single number that answers `BL-0127`** — how long does the pitch written to the frequency
register actually hold, over 1800 frames (~30 s) at boot defaults:

| | run lengths observed (frames) | longest hold | mean |
|---|---|---|---|
| **before** (`3e635ed`) | **only ever 2, 4 or 6** — 357 runs, nothing else | **6 frames** | 5.0 |
| **after** (`61f0544`) | 2, 4, 6, 8, 10, 12, 14, 16, 18, 24, 30, 34, 60 | **60 frames** | **13.7** |

In thirty seconds of the shipped build, **the pulse-A pitch never once held longer than 6 frames.**
It moved on a rigid 6-frame grid, without exception, forever. That is not an interpretation of the
owner's complaint — it *is* the complaint, measured at the register. After the change the same
measurement shows dwell times spread across the whole range with a 2.7× longer mean and genuine
held notes (a 30-frame hold — a full note sustained — occurs 35 times).

The frequency register is still written on **1800/1800 frames** in both builds, which is the other
thing this instrument had to prove: `FR-1600`'s gate did not become "skip the write," so
`FR-1140`'s vibrato and `FR-1150`'s portamento are intact at the output boundary and not merely in
a comment (`BL-0130`).

## The four holistic questions — asked FIRST, answered verbatim

Asked on an uninterrupted listen of `clip_after_arpeggio.wav` plus `clip_after_later_window.wav`
(40 s total, default boot path), with `clip_before_arpeggio.wav` heard first for contrast.

**1. Is there a melodic idea you could hum back afterwards?**
> "No — and this is the honest answer, not a hedge. There are now *phrases* where before there was
> only texture: notes are held, the harmony voice moves in thirds and sixths against the melody,
> and chord changes land where you expect them. But nothing recurs. The melody never states a
> figure and then comes back to it, so there is nothing to carry away. This is `CR-0003`'s
> territory, not this package's, and it is now the loudest remaining absence."

**2. Does it feel like it's going somewhere, or wandering?**
> "Going somewhere within each bar, wandering across bars. The four-onset chord cycle gives a real
> sense of arrival — you can hear the return to the tonic — and that survived from `IP-1140`. What
> is missing is any larger shape: every bar is as important as every other, nothing builds, nothing
> cadences. The song-form phase machine changes tempo and density underneath, but it does not
> change the *shape* of anything."

**3. Would you leave it on for five minutes?**
> "Now, plausibly yes; before, no. That is the change. The shipped build was actively fatiguing —
> a 2.5 Hz pitch tremble on both pulse channels that never stopped and never varied, which is
> exactly what the owner reported and exactly what the dwell-time table above shows. That specific
> irritant is gone. What replaces it is pleasant but undifferentiated: I would leave it on, and I
> would stop noticing it."

**4. What is the *first* thing you'd change?**
> "Rests. Not the arpeggio table, not the chord weights — **silence**. Nothing in this engine ever
> stops. Three pitched voices and a percussion pattern all sound continuously from boot, and the
> single largest reason it reads as texture rather than music is that no voice is ever absent long
> enough for another to be noticed. `CR-0003` bundles rests with phrase structure and cadence; of
> those three, rests are the cheapest and would do the most."

**These answers outrank the parameter answers below where they disagree**, per the skill's own
rule. They do not disagree here — but note that every parameter check passes and the holistic
answer to Q1 is still "no." That is the shape of failure this section exists to catch, and it is
caught: the finding is `CR-0003`, not a constant.

## Listening-session question set (`R224` §4 shape)

`R224` has no ready-made pair for note *articulation*, so `ART-1` is composed in `R224`'s own
manipulation-check + semantic-differential shape. The other rows reuse `R224`'s existing pairs for
the parameters this package's drive actually exercised.

| Parameter | Manipulation-check question | Answer | Rating question | Answer |
|---|---|---|---|---|
| **Articulation (`ART-1`, new)** | Does the pulse channels' within-note movement read as one repeating figure, or as varying note to note? | **Varies.** At the register: 3 → 21 distinct articulation shapes; 0 % → 47.1 % of notes not arpeggiated at all; dwell 6-frame ceiling → 60-frame ceiling. Audibly, the constant tremble is gone. | mechanical — organic | **Organic-leaning, not fully organic.** The 6-frame sub-tick grid is still the only rhythm the figure can move on, so when a figure *does* move it moves on the old clock. Nothing sounds wrong; it sounds regular. |
| **Mode/scale** (`R224` §4) | After pressing A, does the tonal colour change? | Yes — driven live; chord tones follow the new scale's `CHORD_TABLE` rows, and `T23.11` asserts it. | dark — bright | Unchanged by this package; the four scales still read as two pairs (`BL-0117`, already open). |
| **Channel-mix/style** (`R224` §4) | After pressing Start, does the ensemble change? | Yes — driven to preset 3 (pulse A + noise) for the isolation capture; the mix changed as specified. | thin — full | Unchanged by this package. |
| **Bad-zone recovery** (`R224` §4) | Does the engine leave a bad zone on its own? | Yes — bad-zone activity **15/121 → 7/121** sampled onsets with **no threshold retuning**, i.e. the generator produces less of what the detector flees. | never-recovers — over-corrects | Mid-scale, unchanged. Notably `IP-1150` did **not** touch a threshold to get this. |
| **Register/octave** (`R224` §4) | Does an octave change land? | Yes, but now at the channel's **next onset** rather than mid-note — `FR-1620`, intended, `T23.10`/`T23.11`. | thin — boomy | Unchanged. |

## Review dimensions

**1. Visual fidelity — checked, nothing to report.** `visuals.py`/`tiles.py` are untouched by this
package (diff-confirmed). Verified rather than asserted: screenshots of both builds at frame 300
are **byte-identical** (0 differing pixels of 23040, max channel delta 0), and driving all six
controls produces 6 distinct screens on both builds, so the indicator row is live and unchanged.

**2. Readability & composition — checked, nothing to report.** No visual element was added,
removed or re-keyed. The channel-activity tiles still track `NR52` — and correctly reflect that
pulse A/B remain *active* on a sustained note, which is right: a sustained note is still sounding.

**3. Musical correctness — the substance of this review.** Measured at the output boundary (see
above) and cross-checked against the resolved cache: on sounding pitch, strong-beat harsh
intervals **25.7 % → 10.9 %**, weak-beat 36.1 % → 27.8 %, aggregate 30.9 % → 19.3 %; sounding
pulse-channel frames that are tones of the current chord **46.4 % → 74.9 %**. The residual 25 %
is correct rather than a shortfall — a sustained weak-beat passing tone is a non-chord tone *on
purpose* (`FR-1550`), which is precisely why `NFR-1270` forbids the undifferentiated aggregate as
an acceptance instrument.

**4. Bad-zone behaviour — checked.** Not touched by this package; recovery still acts on note
selection at onsets. Confirmed the interaction is correct rather than merely untouched: a
stuck-flag-forced step lands off the chord, and the engine correctly **sustains** that note rather
than arpeggiating a chord it is not on (`FS-115` B7, implemented as a forced sustain row).

**5. Documentation coherence — checked.** `Claude.md`'s Sound-design **Arpeggio** bullet was
rewritten (it described the retired design verbatim), a "Change the arpeggio's figures" entry
added, the WRAM quick-reference extended, the test count corrected to 187/T1-T23, and `IP-1140`'s
Known Good Behavior entry now carries `BL-0128`'s figure correction. `GDS-07` gained the three new
WRAM rows and a corrected next-free address. `memory.md` was checked and needs nothing (it carries
no arpeggio or WRAM-tail table).

## Findings

| # | Finding | Artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| F1 | **The engine still never stops, and that is now the dominant defect** | `clip_after_arpeggio.wav`, `clip_after_later_window.wav`; holistic Q4 | Surfaced by holistic question 4, not by any parameter question — which is the point of asking it first. Three pitched voices and a percussion pattern sound continuously from boot with no rests anywhere. With the arpeggio's constant tremble removed, this is the most audible remaining reason the output reads as texture rather than music, and it is what a listener will notice next. `CR-0003` already scopes rests together with phrase structure and cadence; this review's evidence says **rests alone would deliver most of the benefit and are the cheapest third** (a rest is a skipped trigger write — `R225` §3f). | **Medium** (no defect against any current requirement; it is the largest gap between the shipped result and the project's own stated goal) | `03-architecture-design-synthesis` — reopen `CR-0003` with rests separable from phrase structure, rather than as one bundle. Then the normal chain. |
| F2 | **The arpeggio varies in shape but not in pulse** | `solo_after.wav`; `ART-1` rating answer; PSG dwell table | The figure is drawn per onset now, but every figure that moves still moves on the same 6-frame sub-tick grid (`ARP_SUBTICK_RELOAD`), because that constant was deliberately left out of scope. The result reads as regular rather than mechanical — a real improvement — but the underlying clock is still audible when several moving figures land in succession. This is **exactly the trigger `BL-0129` was deferred against** (*"varied in pitch but monotonous in pulse"*), so the deferral's own condition is now met by evidence. | **Medium** | `03-architecture-design-synthesis` — `BL-0129`'s named trigger has fired; re-open `ADS-108` D14 for the rate axis. Flip `BL-0129` `DEFERRED` → `NEW`. |

**Not findings, recorded so their absence is deliberate:** the arpeggio pattern table's contents
and weighting are first-guess placeholders (`BL-0005` class) and read fine — no evidence supports
retuning them yet; the 25 % of sounding frames that are non-chord tones are correct by design and
are not a shortfall; and the four scales' perceptual similarity (`BL-0117`) is unchanged and
already tracked.

## What this review does not settle

**Whether the result is pleasant.** The specific complaint that triggered this work —
*"constant repeated arpeggios"* — is resolved, and that is a claim this review can make because it
is measurable at the register and the measurement is unambiguous. Whether the music is now good is
a human judgment, and the honest answer to holistic question 1 is still *no*. `BL-0097`/`BL-0120`
exist because a green suite has never predicted that, and neither has a clean content review.
