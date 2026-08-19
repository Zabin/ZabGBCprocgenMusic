# R225 — Harmonic Coordination: A Shared Chord Context Across Independent Voices

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-08-19
- **Trigger:** `BL-0119` (High) — the user's own verdict ("the music doesn't sound good yet"),
  measured back to a single architectural cause: Driftune's three pitched channels random-walk
  independently with no shared harmonic state, so every note is *in key* and the vertical result
  is *uncoordinated*. `R211` §5's first bullet explicitly recommends **against** the work this
  topic grounds, so architecture could not proceed until that recommendation was re-grounded
  rather than silently contradicted. This topic supplies the replacement position;
  [`R211` §9](R211-melodic-harmonic-generation-techniques.md#9-addendum--2026-08-19-r211-5s-first-bullet-is-withdrawn-bl-0119)
  withdraws the superseded one at its own site, per this project's self-correction discipline
  (`R101` §8.5, `R102` §3b precedent).

## 1. Purpose

Answer, with citations and with this project's own measured cost reality, the question `R211` §5
deferred: **what is the cheapest mechanism by which several independently-generating voices on an
SM83 can agree on what harmony they are currently playing?** Five sub-questions, each of which
must land on something concrete enough for `03-architecture-design-synthesis` to design from:

1. What is a *shared harmonic context*, and what is its cheapest tractable representation?
2. What progression drives it — how many chords, what transitions, what harmonic rhythm?
3. How does the bass derive from it?
4. How does the melody derive from it without becoming a chord arpeggio?
5. What phrase structure (rests, contour, cadence) surrounds it?

Plus a sixth question this project cannot skip: **what does each of the above cost on a per-frame
budget that `R101` §8.5 measured as already ~exhausted?**

## 2. Scope

Runtime harmonic coordination between concurrently-sounding generative voices: chord state,
progression, and the per-voice note-selection rules that read that state. Includes the
phrase/rest/cadence layer, because the measured evidence (`BL-0119` (d): no rests anywhere,
nothing resolves) shows it is part of the same defect and `R212` already names it as its own
open gap.

**Out of scope:** the melodic-walk algorithm itself (`R201`), rhythm/Euclidean generation
(`R202`), bad-zone *detection* metrics (`R204` — though this topic must state its relationship to
them), timbre (`R216`), macro-form phase envelopes (`R220`, shipped as `IP-1100`), and anything
about *what the visualizer does with chord state* (`R205`/`R223`). This topic makes no scope
decision and specifies no feature — it grounds one.

## 3. Concepts

### 3a. Shared harmonic context: the coordination is the point, not the chord vocabulary

Multi-voice generative systems that sound coordinated do not coordinate by having each voice
listen to the others; they coordinate by having every voice read one shared harmonic state that a
single producer advances. Contemporary multi-agent music systems make this explicit as an
architecture: specialist components are separated by musical role — "a Transformer-based
Chord-Former, a generative Harmony-GPT, a recurrent Rhythm-Net" — with the harmonic component
*upstream* of the others rather than peer to them
[arXiv 2509.24463 — An Agent-Based Framework for Automated Higher-Voice Harmony Generation](https://arxiv.org/html/2509.24463).
The same ordering is stated flatly for jazz generation: "the harmonic framework serves as a central
guide for melodic invention"
[MDPI *Information* 16(6):504 — Generative Jazz Chord Progressions](https://www.mdpi.com/2078-2489/16/6/504).
In game audio specifically, the standard runtime shape is a state machine over music states with
Markov-chain transitions "where the likelihood of transitioning from one note or chord to another
is determined by probability"
[arXiv 2512.12834 — Procedural Music Generation Systems in Games](https://arxiv.org/pdf/2512.12834).

The load-bearing point for Driftune is *structural, not stylistic*: what makes the difference is
that a **single shared field exists and every voice reads it** — not the sophistication of what is
in it. Driftune currently has zero such fields; `BL-0119`'s near-uniform vertical interval
histogram is the direct, expected signature of that absence.

**How small can the shared state be?** Corpus evidence says: very. Machine learning over real
harmonic corpora "produced hidden Markov models with **three states** for songs in major and
minor that can be interpreted as harmonic functions," recovering the traditional
tonic/subdominant/dominant categorization from the data rather than assuming it
[Jacoby, Tishby & Tymoczko — An Information Theoretic Approach to Chord Categorization and
Functional Harmony, *JNMR* 44(3)](https://www.tandfonline.com/doi/abs/10.1080/09298215.2015.1036888).
A three-to-four-state shared context is not a simplification forced by the SM83 — it is close to
what corpus analysis says the information actually is.

#### Sources
- [arXiv 2509.24463 — An Agent-Based Framework for Automated Higher-Voice Harmony Generation](https://arxiv.org/html/2509.24463)
- [MDPI *Information* 16(6):504 — Generative Jazz Chord Progressions: A Statistical Approach to Harmonic Creativity](https://www.mdpi.com/2078-2489/16/6/504)
- [arXiv 2512.12834 — Procedural Music Generation Systems in Games](https://arxiv.org/pdf/2512.12834)
- [Jacoby, Tishby & Tymoczko, *Journal of New Music Research* 44(3) — An Information Theoretic Approach to Chord Categorization and Functional Harmony](https://www.tandfonline.com/doi/abs/10.1080/09298215.2015.1036888)
- **Fetch-verification gap (whole topic):** `WebFetch` was blocked by the egress proxy for every
  primary source attempted this pass (`journals.plos.org`, `davidtemperley.com`, `arxiv.org`,
  `en.wikipedia.org`, `littlesounddj.fandom.com`, `hermandong.com`, `norijacoby.com`,
  `studybass.com`). Every citation in this topic is therefore **search-result synthesis with the
  primary URL recorded**, at the same evidence grade as `R211` §8's own addendum, and is flagged
  **needs fetch-verification** if a later pass wants primary-document depth. The *measured*
  claims in §3h/§4/§5 are this project's own instrumentation and are not affected.

### 3b. Functional-harmony progression: a small, sparse, asymmetric transition table

Corpus analysis of tonal harmony finds that "transitions between the three functionally important
chords (tonic, dominant, and subdominant) are the most common," that "the transition matrix is
asymmetric" (transitions are direction-sensitive), and that it "is approximately a **sparse**
matrix with many entries close to zero"
[Statistical characteristics of tonal harmony: a corpus study of Beethoven's string quartets, *PLOS ONE*](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0217242).
Sparsity is the operative finding for this project: a transition table with most entries at zero
is exactly a small fixed lookup table, not a matrix.

Popular-music corpora give the same shape with different weights. De Clercq & Temperley's
100-song Rolling Stone corpus found that "IV is the most common chord after I and is especially
common preceding the tonic" — "the most common 'pre-tonic' harmony by a considerable margin," with
V next, and that "the much greater frequency of IV and V over other chords gives these chords a
privileged position among non-tonic harmonies"
[de Clercq & Temperley — A corpus analysis of rock harmony, *Popular Music* 30(1)](https://www.cambridge.org/core/journals/popular-music/article/abs/corpus-analysis-of-rock-harmony/C5210A8EC985DDF170B53124F4464DA4).
Notably for a generator, they also found rock "does not show strong asymmetries in root motion;
ascending and descending 5th motions are roughly equally common" [same] — so a rock-flavoured
table may be *more* symmetric than a common-practice one, and neither needs to be large.

Corpus work on hymnody adds the dwell-time observation a continuously-running generator needs:
harmony "tends to spend long periods of time on tonic-function chords, with brief forays away from
tonic, **more often to dominant-function chords than to subdominant**"
[A Corpus-Based Model of Harmonic Function in Shape-Note Hymnody](https://academia.edu/29766639).
Read as a generator rule: the transition table should be tonic-return-biased, not uniform over the
chord set — the same "the table's *distribution*, not extra arithmetic, encodes the bias" pattern
`R211` §8 already grounded for `DELTA_TABLE`.

#### Sources
- [*PLOS ONE* — Statistical characteristics of tonal harmony: A corpus study of Beethoven's string quartets](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0217242)
- [de Clercq & Temperley — A corpus analysis of rock harmony, *Popular Music* 30(1) (Cambridge Core)](https://www.cambridge.org/core/journals/popular-music/article/abs/corpus-analysis-of-rock-harmony/C5210A8EC985DDF170B53124F4464DA4)
- [A Corpus-Based Model of Harmonic Function in Shape-Note Hymnody](https://academia.edu/29766639)
- All three: **needs fetch-verification** (see §3a's blocked-egress note). No numeric transition
  probability was recoverable at fetch-blocked evidence grade this pass; the claims used here are
  *ordinal* ("IV is the most common pre-tonic; V next; the matrix is sparse and asymmetric"), which
  is what a 3-4 entry lookup table actually needs.

### 3c. Harmonic rhythm: chords change far more slowly than notes

Harmonic rhythm is "the rate at which the chords change in a musical composition, **in relation to
the rate of notes**" [Wikipedia — Harmonic rhythm](https://en.wikipedia.org/wiki/Harmonic_rhythm).
One chord per bar is the common baseline in popular music — cited examples include "(Sittin' On)
The Dock of the Bay," "Oye Como Va" (one-bar alternation of Am7/D7) and "Lively Up Yourself"
(C7/F7) [same] — and the standard compositional latitude around it is "one chord per bar as your
basic harmonic rhythm while allowing yourself moments where you might double that rhythm... or
halve it"
[The Essential Secrets of Songwriting — Making Sense of Harmonic Rhythm](https://www.secretsofsongwriting.com/2022/05/26/making-sense-of-harmonic-rhythm-in-your-songs/).

This is the single most important cost fact in the topic: **the shared harmonic state changes one
to two orders of magnitude less often than notes do.** Everything expensive about harmony happens
on an event that, in Driftune's measured terms (§3h), occurs roughly once every 120 frames.

#### Sources
- [Wikipedia — Harmonic rhythm](https://en.wikipedia.org/wiki/Harmonic_rhythm)
- [The Essential Secrets of Songwriting — Making Sense of Harmonic Rhythm In Your Songs](https://www.secretsofsongwriting.com/2022/05/26/making-sense-of-harmonic-rhythm-in-your-songs/)
- Both **needs fetch-verification** (§3a).

### 3d. Bass from the chord: root and fifth, and why that is the cheapest voice to fix

"The root and fifth of the chord are the most supportive sounding notes a bassist can play beneath
a chord," and root–fifth is one of the most common bass patterns there is; critically for a
table-driven generator, "roots and fifths are conveniently **the same pattern for almost every
chord** — it doesn't matter if it's a major chord, minor chord, or a power chord"
[StudyBass — Roots and Fifths](https://www.studybass.com/lessons/common-bass-patterns/roots-and-fifths/).
The general strategy is to "put chord roots on the strong beats," reaching the next root by step
in between, with thirds and sevenths used "decoratively on weak beats"
[No Treble — Mastering Country Bass Lines: Roots, Fifths, and Chord Function](https://www.notreble.com/buzz/2025/05/21/mastering-country-bass-lines-roots-fifths-and-chord-function-explained/).

Two consequences for Driftune specifically. First, this confirms `R211` §3's own bass note (which
had "no distinct citation found beyond general chord-tone-following convention") with real
sources. Second — and this is the cheap part — **root/fifth is mode-independent**: the bass voice
needs no per-scale chord-quality table at all, only the current chord's root degree and a
fixed +4-scale-degrees fifth. The wave channel, which `BL-0119` (c) measured doing the identical
stepwise drunk walk as the two melodic voices, is therefore the *lowest-cost, highest-impact* voice
to convert.

#### Sources
- [StudyBass — Roots and Fifths](https://www.studybass.com/lessons/common-bass-patterns/roots-and-fifths/)
- [No Treble — Mastering Country Bass Lines: Roots, Fifths, and Chord Function Explained](https://www.notreble.com/buzz/2025/05/21/mastering-country-bass-lines-roots-fifths-and-chord-function-explained/)
- Both **needs fetch-verification** (§3a).

### 3e. Chord-tone-biased melody: the strong/weak-beat rule is the whole mechanism

The convention that converts "in key" into "in harmony" is a single, cheap, local rule: **chord
tones on strong beats, non-chord tones on weak beats.** "Notes played on strong beats have more
emphasis, while notes played on weak beats have less emphasis," so "nonchord tones usually occur on
the weak beat"; the canonical figure is "chord tone – passing tone – chord tone, filling in a
third," which is also how scales arise "by joining up chord notes with passing notes"
[Fiveable — AP Music Theory 4.1: Harmony and Voice Leading I](https://fiveable.me/ap-music-theory/unit-4/harmony-voice-leading-i/study-guide/0m8OiGeqjebWSd6bMZ0W);
[Inquiry-Based Music Theory — 2:1 Counterpoint and Embellishing Shapes](https://smbutterfield.github.io/ibmt17-18/05-counterpoint-embell-shapes/c3-tx-2ndandembellshapes.html).
The named exceptions (suspension, retardation) are strong-beat dissonances that resolve downward
by step [same] — worth naming only so a future design does not treat *all* strong-beat dissonance
as a defect.

This is a **per-onset, per-voice, table-lookup-sized rule**. It requires no lookahead, no search,
no constraint solving, and no knowledge of what the other voices chose — exactly the property
`R215`'s constraint/scheduling survey found Driftune could *not* afford in its general form.

#### Sources
- [Fiveable — AP Music Theory 4.1: Harmony and Voice Leading I](https://fiveable.me/ap-music-theory/unit-4/harmony-voice-leading-i/study-guide/0m8OiGeqjebWSd6bMZ0W)
- [Inquiry-Based Music Theory (Butterfield) — Lesson 5c: 2:1 Counterpoint and Embellishing Shapes](https://smbutterfield.github.io/ibmt17-18/05-counterpoint-embell-shapes/c3-tx-2ndandembellshapes.html)
- [Classification of Nonchord Tones — Musical Harmony](https://sites.google.com/view/musicalharmonysite/part-i-general-music-theory/chords/classification-of-nonchord-tones)
- All **needs fetch-verification** (§3a).

### 3f. Phrase structure: cadence is a *chord* event, which is why it becomes affordable here

`R212` recorded "no SM83-tractable way to generate real cadential/formal structure cheaply" as an
open negative result. That result was reached *without* a chord context in the design. With one,
the standard phrase archetype is directly expressible over the chord state machine: a **period**
is "a phrase-level form consisting of an antecedent and a consequent," where the antecedent "is
often four measures long, and it ends with a weaker cadence, most often a half cadence (HC)," and
the consequent "ends with a stronger cadence than the antecedent, most often a perfect authentic
cadence (PAC)" — two phrases in a "question and answer" relationship
[Open Music Theory — The period](https://openmusictheory.github.io/period.html);
[Open Music Theory — The Phrase, Archetypes, and Unique Forms](https://viva.pressbooks.pub/openmusictheory/chapter/phrase-archetypes-unique-forms/).

In chord-state terms an HC is *"the phrase ends on the dominant"* and a PAC is *"the phrase ends
on the tonic"* — i.e. two constraints on **one byte** at two known positions of the progression
counter, not a new generative subsystem. Rests are the other half: automated-composition prior art
describes a valid cadence as one "at a long note or a note which is followed by a long rest,
probably preceded by shorter duration notes"
[USPTO 11430419 — automated music composition and generation](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11430419)
(cited for the category only, as `R220` already does for this patent family). A rest, in Driftune,
is a note-timer reload with the trigger write skipped — no new mechanism, one branch.

**This is a genuine, citable partial reversal of `R212`'s negative result** and should be recorded
as such: cadence was expensive because there was nothing to cadence *onto*; it is cheap once the
chord context exists. It is not a claim that full composed form is now solved — motif recurrence
and true developing variation remain where `R214` §8/`BL-0010` left them.

#### Sources
- [Open Music Theory — The period](https://openmusictheory.github.io/period.html)
- [Open Music Theory — The Phrase, Archetypes, and Unique Forms](https://viva.pressbooks.pub/openmusictheory/chapter/phrase-archetypes-unique-forms/)
- [Inquiry-Based Music Theory — 13a: The Period](https://smbutterfield.github.io/ibmt17-18/13-phrasing-texture/a2-tx-periods.html)
- [USPTO 11430419](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11430419) —
  category confirmation only, single-source, flagged, same grade as `R220`'s use of this family.
- All **needs fetch-verification** (§3a).

### 3g. The chiptune precedent: a chord *is* a small offset table — and Driftune already ships one

Game Boy practice represents chords exactly as an offset table. LSDJ's chord command notates a
chord as its scale-step members — "C47 is equivalent to a Major Chord, and C37 a Minor Chord," the
digits naming which scale degrees make up the chord — and chiptune "chords" are conventionally
faked by "rapidly cycling single notes on one channel," an arpeggio whose speed creates "the
illusion that more than one note is being played at a time"
[LSDJ Wiki — Chords using Tables](https://littlesounddj.fandom.com/wiki/Chords_using_Tables);
[chipmusic.org — LSDJ Chord Cheat Sheet](https://chipmusic.org/forums/topic/15949/lsdj-chord-cheat-sheet/);
[Noise Engineering — Emulating chiptune "chords"](https://noiseengineering.us/blogs/loquelic-literitas-the-blog/quick-patch-emulating-chiptune-chords-with-vox-digitalis-and-quantus-pax/).

**Driftune already implements this.** `music_data.py`'s `ARPEGGIO_OFFSETS = [0, 2, 4, 2]`
(`IP-1060`, grounded in `R216`) is a stack of scale-degree thirds — root, third, fifth, third —
cycled on pulse A/B every few frames. The chord-tone mechanism the project needs is *already
shipped, already tested, and already in the VBlank budget*. What is missing is one thing only:
those offsets are applied to **each channel's own independently-wandering `CUR_DEGREE`**, not to a
**shared chord root**. That is the entire delta, stated precisely.

#### Sources
- [Little Sound Dj Wiki — Chords using Tables](https://littlesounddj.fandom.com/wiki/Chords_using_Tables)
- [chipmusic.org — LSDJ Chord Cheat Sheet](https://chipmusic.org/forums/topic/15949/lsdj-chord-cheat-sheet/)
- [Noise Engineering — Emulating chiptune "chords" with Vox Digitalis and Quantus Pax](https://noiseengineering.us/blogs/loquelic-literitas-the-blog/quick-patch-emulating-chiptune-chords-with-vox-digitalis-and-quantus-pax/)
- Driftune's own shipped `ARPEGGIO_OFFSETS`/`_emit_arpeggio_tick` (`music_data.py`,
  `music_engine.py`), `R216`, `Claude.md` Known Good Behavior — internal evidence, not a citation.
- External three: **needs fetch-verification** (§3a).

### 3h. Cost realism: measured, this session, against the real budget

`R101` §8.5 measured `read_joypad`+`apply_input`+`engine_tick` consuming ~9 of VBlank's 10
scanlines on **every** frame, with `update_visuals` finishing at `LY` 153; `IP-9040` was abandoned
(`BL-0113`) because it could not add even a handful of instructions to the per-frame path. Any
mechanism recommended here has to survive that. New measurement taken this pass against the ROM
built at this branch's tip (headless PyBoy, 3600 frames, boot defaults, no input):

| Fact | Measured |
|---|---|
| `VIS_ENTRY_LY` sampled mid-run (frame 1200) | **152** — `R101` §8.5's budget finding still holds on this build |
| Pulse A onsets | 119 in 3600 frames — interval **30 frames** (mode and mean) |
| Pulse B onsets | 119 — interval **30 frames**, and **on the same frames as pulse A** |
| Wave onsets | 60 — interval **60 frames**, consistently landing **one frame after** the pulse pair |
| Noise onsets | 443 — interval **8 frames** |
| Frames with **zero** pitched onsets | **3422 / 3600 = 95.1 %** |
| Frames with 2 simultaneous pitched onsets | 118 (3.3 %) |
| Frames with 3 simultaneous pitched onsets | **1** (the boot frame only) |

Three conclusions follow, and they are the reason this whole topic is tractable at all:

1. **Onset-scoped work is nearly free.** 95.1 % of frames execute no pitched-onset branch. Work
   attached to an onset costs nothing on ~19 of every 20 frames, unlike anything attached to
   `engine_tick`'s unconditional path.
2. **The realistic worst case is two coincident onsets, not three.** Pulse A and pulse B are
   phase-locked and always fire together; the wave channel is offset by one frame and (after boot)
   never joins them. A per-onset addition is therefore budgeted at **2×**, not 3×.
3. **Chord-change work is rarer still.** At §3c's one-chord-per-bar convention mapped onto the
   measured 30-frame pulse onset (§5 derives 120 frames = 4 pulse onsets ≈ 2 s), the chord
   transition executes on **0.8 %** of frames.

There is also a **musical** finding hiding in the same measurement, not previously recorded
anywhere: pulse A and pulse B strike **simultaneously, every single onset**. Two melodic voices
attacking together on every note is the worst possible arrangement for uncoordinated pitch
selection — every clash is exposed at an attack transient rather than smeared across a sustain.
`BL-0119`'s 36.1 % harsh-interval figure is not merely present in the ROM, it is *foregrounded* by
the onset schedule.

#### Sources
- This project's own instrumentation: headless PyBoy driver over the ROM built from this branch's
  tip, reading `NOTE_TIMER_PA/PB/WV/NZ` (`0xC00C`-`0xC00F`), `CUR_DEGREE_*` (`0xC010`-`0xC012`) and
  `VIS_ENTRY_LY` (`0xC061`) once per `tick()` for 3600 frames. Throwaway scratchpad driver per
  `run-driftune`'s convention — not committed. Tier-A internal evidence, no external citation.
- `R101` §8.5, `R110` §3/§5, `R308` §8.5 (the budget measurements this corroborates);
  `BL-0113`/`IP-9040` (the abandonment this constraint caused).

## 4. Operational Context

Nothing in this topic is implemented. What *is* implemented and directly relevant:

- **Three independent walks.** `_emit_channel_gen` gives pulse A, pulse B and wave each its own
  `CUR_DEGREE_*`, `LFSR_STATE_*` and `NOTE_TIMER_*`; there is no field any two of them read in
  common. `BL-0119` measured the result: a near-uniform vertical interval histogram (P5 12.8 %,
  P4 11.7 %, m6 10.6 %, M2 10.6 %, uni/oct 10.0 %, m2 10.0 % …) and 36.1 % harsh pairs.
- **A chord-tone offset table, applied to the wrong root.** `ARPEGGIO_OFFSETS = [0, 2, 4, 2]`
  (§3g) already stacks thirds — over each channel's own wandering degree.
- **A reactive negative constraint.** `_emit_badzone_tick`/`IP-0004`/`IP-0007` score pairwise
  dissonance via `DISSONANCE_WEIGHT_BY_IC` and, when the score crosses threshold, override each
  channel's next step to pull toward the tonic. This *detects and flees* dissonance; it never
  *constructs* consonance — `BL-0119`'s own "negative constraint vs. positive generator" framing.
- **A macro-parameter state machine with no harmonic content.** `_emit_song_tick` (`IP-1100`)
  already runs a 4-phase timer that overwrites `TEMPO_IDX`/`DENSITY_IDX`. It is the closest
  existing structural precedent for a chord-progression scheduler, and `R220` §5 already flagged
  "should the bad-zone mechanism and a future state machine share meta-state?" as an open
  architecture question — now unavoidable.
- **Two note-selection schemes already exist.** Scheme W (LFSR walk) and Scheme E (Euclidean-gated
  motif, `IP-1070`/`IP-1090`) are selected per channel by spare bits of `CHMIX_MASKS`. Any new
  harmonic scheme has a precedent shape to follow and an existing extension point (`ADR-0001`).

### Sources
- `music_engine.py`, `music_data.py`, `wram_constants.py` as shipped at this branch's tip;
  `Claude.md` Known Good Behavior; `BL-0119`'s measurement record. Internal evidence.

## 5. Implementation Guidance

### 5a. The shared context is one to three WRAM bytes, and the WRAM exists

One byte — **current chord root as a scale degree** — is the minimum that makes every voice
coordinate, and it is what §3d's mode-independent root/fifth bass and §3g's already-shipped
`ARPEGGIO_OFFSETS` both consume directly. A second byte (progression position / phrase counter)
and a third (chord quality or cadence flag) are the plausible extent. `GDS-07` records the next free
address as `0xC077`, with further gaps at `0xC040`-`0xC04F` and `0xC062`-`0xC067` — no WRAM
pressure exists and none of this is a reason to compress the design. (`0xC020`-`0xC037` looks
free from `wram_constants.py` alone but is **not**: `GDS-07` §4 reserves it for the `HIST_PA`/
`HIST_PB`/`HIST_WV` repetition-history buffers — unused in the shipped ROM but deliberately not
reclaimed, per `BL-0013`'s own reconciliation. Do not take it.)

**Do not** make the shared field a derived expression recomputed by each reader (e.g. "chord =
`SONG_STATE_TIMER_HI` mod 4"). It costs arithmetic at every read site, on the exact per-onset paths
that already run twice on a busy frame, to save one byte of WRAM that is not scarce.

### 5b. Chord representation: a 3-entry degree table per chord, **not** degree arithmetic

The obvious implementation — "chord tones are root, root+2, root+4 in scale degrees" — has a
concrete bug on this project's actual data, and the ADS must not inherit it.
`SCALE_SEMITONES` rows are **8 entries whose 8th duplicates the 1st** (`major` =
`[0,2,4,5,7,9,11,12]`; degree 7 and degree 0 are both C), and degrees are masked `AND 0x07`
everywhere in `_emit_channel_gen`. So degree-stacking that crosses the seam lands one scale step
wrong: the V chord's fifth is root degree 4 + 4 = degree 8, which masks to degree 0 (C) where the
correct pitch is D. Verified by inspection of `music_data.py` and `music_engine.py`'s degree
masking; observed as a real distortion in this pass's own simulation (§5f) before it was corrected.

Two fixes, costed:

| Option | Cost | Assessment |
|---|---|---|
| **A. Widen the degree space** to 12+ entries per scale | `SEMITONE_TABLE_DATA` 4×8→4×12 (+16 B); the note-frequency tables are 4 scales × 4 octaves × 8 degrees × 2 B = 256 B and would grow to 384 B (+128 B); every `AND 0x07` mask site changes | Correct but touches a lot of shipped, tested surface for a problem the next option avoids entirely |
| **B. A `CHORD_TABLE` of N chords × 3 degree entries**, hand-chosen so every entry is already in 0-7 (inversions where needed) | ~12-24 B of ROM; zero changes to masking, note tables, or `SCALE_SEMITONES` | **Recommended.** It is also exactly the LSDJ representation (§3g) and exactly this project's established "extend the table, not the mechanism" pattern (`R211` §8) |

Octave-wrapped chord tones are *inversions*, which are harmonically valid — a hand-authored table
simply takes the octave decision at authoring time rather than paying for it at runtime.
`pentatonic` deserves an explicit call-out: its row (`[0,2,4,7,9,12,14,16]`) is a 5-note scale
packed into 8 slots, so third-stacking does not yield triads there at all — its chord rows must be
authored, not derived, or the scale must be excluded from chord-tone targeting.

### 5c. Progression, harmonic rhythm, and where the transition actually runs

- **Size the chord set at 3-4, not more.** §3a's corpus HMM converged on three functional states;
  §3b found the transition matrix sparse with IV and V "privileged" among non-tonic harmonies. A
  4-chord vocabulary (I, IV, V, vi) with a tonic-return-biased, asymmetric transition table is
  literature-shaped, not a concession. Shape it exactly like `DELTA_TABLE`/`MOTIF_VARIANT_SELECTOR`
  — a weighted lookup indexed by LFSR bits, distribution-in-the-table (`R211` §8), no arithmetic.
- **Harmonic rhythm: 4 pulse onsets per chord.** §3c's one-chord-per-bar, mapped onto §3h's
  measured 30-frame pulse-onset interval, is **120 frames ≈ 2 s** at the boot tempo. Express it in
  **onsets, not frames**, so it tracks `TEMPO_IDX`/`SONG_TABLE` automatically instead of drifting
  out of phase with them when tempo changes.
- **Advance the chord inside pulse A's existing onset branch, not on a new per-frame tick.** This
  is the load-bearing cost decision. A new `chord_tick` called unconditionally from `engine_tick`
  would add work to 100 % of frames — the exact thing `IP-9040`/`BL-0113` proved unaffordable. A
  counter decremented inside `gen_tick_pa`'s already-taken onset branch runs on 3.3 % of frames
  (§3h), and the transition body itself on ~0.8 %. `_emit_song_tick` is the wrong precedent to copy
  here **for this reason specifically** — it is per-frame, and it was affordable in 2026-07 because
  it predates the budget being measured as exhausted.
- **Do not couple the chord counter to `SONG_STATE`'s timer.** They are different cadences (§3c
  vs. `R220`'s minutes-scale envelopes) and `IP-1100`'s own docstring documents disjointness from
  every other mechanism as a deliberate property worth preserving.

### 5d. Per-voice rules, in ascending order of cost and descending order of impact

1. **Wave = bass = chord root, alternating to the fifth** (§3d). Mode-independent, one table read,
   replaces a walk rather than adding to it — plausibly *cheaper* than the LFSR path it displaces.
   This alone fixes `BL-0119` (c)'s "the bass wanders by step" finding.
2. **Pulse A = chord tone on strong onsets, stepwise passing/neighbour tone on weak onsets**
   (§3e). One parity bit distinguishes strong from weak; the strong branch is a `CHORD_TABLE`
   read, the weak branch is the existing `DELTA_TABLE` walk **constrained to ±1**. Both branches
   already exist in some form in `_emit_channel_gen`.
3. **Pulse B = a different member of the same chord, separated by a whole octave** (§5f measures
   why the octave matters), or `IP-1060`'s existing arpeggio re-rooted on the shared chord —
   the cheapest possible version of this voice, since §3g's mechanism is already shipped.
4. **Rests and cadence last** (§3f): skip the trigger write on the final onset of a phrase; force
   the chord to V at the antecedent boundary and to I at the consequent boundary. One branch and
   two forced table indices, on events that occur every few seconds.

Ordering matters because each step is independently shippable and independently audible; the ADS
should not treat this as one indivisible increment.

### 5e. Relationship to the bad-zone system — decide it, do not leave it implicit

`IP-0004`/`IP-0007`'s tonic-pull is a *reactive negative constraint*; everything above is a
*proactive positive generator*. Left unreconciled they will fight: the dissonance detector scores
`R204`'s interval classes across all three pitched channels regardless of channel-mix, and a
deliberate weak-beat passing tone (§3e) is, by construction, a dissonance the detector is designed
to flee. A tonic-pull that overrides a chord-tone target also silently un-harmonizes the very
mechanism this topic recommends.

Research position (the decision itself is `03`'s): the two are **not** redundant and neither should
be deleted. Chord targeting removes most *unintended* dissonance; bad-zone recovery remains the
safety net for states chord targeting cannot prevent (stuck/repeated notes, overload, and the
`DENSITY`/`CHMIX` corners). What must change is *precedence and scope* — at minimum the detector
should not treat a scheduled weak-beat non-chord tone as evidence of a bad zone, or its threshold
must be re-derived against the new, deliberately non-uniform interval distribution. Note also that
`DISSONANCE_THRESHOLD` was never tuned by ear (`BL-0005`) and `BL-0102` already reports a
bad-zone-at-boot condition — re-deriving it is owed regardless.

### 5f. Predicted effect, quantified — and the metric correction that comes with it

A design-space simulation was run this pass (throwaway scratchpad script, 36 000 simulated frames,
`SCALE_SEMITONES['major']`, the measured onset schedule from §3h, `DELTA_TABLE`'s real weighting).
Interval classes are counted mod 12 with `BL-0119`'s own harsh set (m2, M2, tritone, m7, M7), so
the numbers are directly comparable to its measurements:

| Configuration | harsh % | m2 | tritone | M7 |
|---|---|---|---|---|
| Shipped shape — three independent walks (**model**) | **32.6 %** | 6.1 % | 2.8 % | 4.8 % |
| Shipped shape — **live ROM**, `BL-0119`'s own measurement | **36.1 %** | 10.0 % | 3.3 % | 2.8 % |
| Chord-constrained, pulse B offset by +2 scale degrees, all onsets | 28.6 % | 1.1 % | 3.1 % | 5.0 % |
| Chord-constrained, pulse B offset by a whole octave, all onsets | 28.5 % | 1.1 % | 3.8 % | 4.0 % |
| Chord-constrained, octave-separated, **strong onsets only** | **14.9 %** | 1.3 % | 0.7 % | 1.9 % |

Three things to take from this, each of which changes what the ADS should specify:

- **The model reproduces the shipped ROM's measured distribution** (32.6 % modelled vs. 36.1 %
  measured), which is the only reason the other rows are worth quoting at all. It is still a
  model — not a claim about audio.
- **Voice separation must be by octave, not by scale degree.** Offsetting pulse B "+2 degrees from
  a chord tone" manufactures sevenths against the bass; +7 degrees (a whole octave) does not.
  Same cost, materially different result — a real design instruction, not a preference.
- **The aggregate histogram is the wrong success metric for this design, and the ADS must not
  adopt it as one.** A chord-tone/passing-tone melody *deliberately* sounds non-chord tones on weak
  beats — that is what a passing tone is. Measured over all onsets the improvement looks modest
  (32.6 %→28.5 %); measured over the **strong-beat sonorities**, which is where §3e says the
  harmony is perceived, it is 32.6 %→**14.9 %**, with m2 down 6.1 %→1.3 % and tritone 2.8 %→0.7 %.
  `BL-0119`'s aggregate figure was the right instrument for diagnosing *absence of coordination*
  and is the wrong instrument for verifying *presence* of it. This correction is carried into
  `R224` §7 as an evaluation-methodology finding as well.

### 5g. What this topic does not recommend

- **No constraint solving, search, or lookahead.** Every rule above is a per-onset table read.
  `R215`'s survey already found the general form unaffordable; nothing here needs it.
- **No inter-voice listening.** No voice reads another voice's `CUR_DEGREE`. Coordination is via
  the shared field only — this is what keeps the cost linear in voices and the code local.
- **No key modulation, no true developing variation, no L-system phrase rewriting.** `R212`'s
  modulation gap and `R214` §8/`BL-0010`'s motif-recurrence path stay exactly where they are.
- **No per-frame work of any kind.** If a future proposal needs a `chord_tick` in `engine_tick`,
  that is a budget question for `02-research-gbc-hardware`/`R101`, not something this topic
  clears.

### Sources
- §5's cost figures: this pass's own measurements (§3h) and the shipped tables in
  `music_data.py`/`music_engine.py`/`wram_constants.py`. `R101` §8.5, `R308` §8.5, `BL-0113`.
- §5f: throwaway scratchpad simulation, this pass; `BL-0119`'s live measurement for the
  comparison row.
- External grounding for the rules themselves: §3b, §3c, §3d, §3e, §3f, §3g above.

## 6. Feature Mapping

No `IP-xxxx` depends on this topic yet. It was authored to be consumed by
`03-architecture-design-synthesis` as the grounding for an `ADS` on harmonic coordination
(`BL-0119`'s own routing) — **which happened the same day: [`ADS-108`](../../architecture/ADS-108-harmonic-coordination.md)
and [`ADR-0003`](../../architecture/adr/ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md)** —
and would then feed `04`→`05`→`06`→`07` in the normal order. It
directly touches, if that work is ever authorized: `music_data.py` (a new `CHORD_TABLE` +
transition table), `music_engine.py` (`_emit_channel_gen`'s note-selection step, the wave
channel's role, `_emit_badzone_tick`'s relationship to it), and `wram_constants.py` (1-3 new
fields). It changes nothing by itself.

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

🟡 **PARTIAL — traced to architecture, not yet to code (authored and consumed the same day,
2026-08-19).** Consumed in full by
[`ADS-108` — Harmonic Coordination via a Shared Chord Context](../../architecture/ADS-108-harmonic-coordination.md)
and by [`ADR-0003`](../../architecture/adr/ADR-0003-scheme-selection-moves-to-a-parallel-scheme-table.md):
§3a→`ADS-108` D1, §5b→D3, §3a/§3b→D4, §3c/§5c→D5, §3h→D6 (the load-bearing cost decision),
§3d/§3e/§5f→D9, §5e→D8, §3f→D10, §5f→D12. **No code descends from it yet and none is authorized
(G3)** — the honest state is "grounded a design, has not yet grounded an implementation." Update
this row when/if an `FS`/`IP` chain ships.

## 7. Related Topics

`R211` (the topic whose §5 this supersedes — see its §9 withdrawal; its §3 chord/bass/countermelody
concepts are the direct ancestors of §3b/§3d here, and its §8 weighted-table technique is the
mechanism §5c reuses), `R212` (§3f is a partial, citable reversal of its cadence negative result),
`R201` (the walk that becomes the weak-beat passing-tone branch), `R203` (role differentiation —
satisfied in register/rate but, as `BL-0119` (c) measured, not in melodic behaviour), `R204`
(the reactive detector §5e must be reconciled with), `R207` (channel roles, the wave channel's
bass identity), `R215` (why constraint solving is out and per-onset table reads are in), `R216`
(`ARPEGGIO_OFFSETS` — the already-shipped chord-tone mechanism §3g re-roots), `R220` (song-form
state machine — the structural precedent, at a different cadence, and the source of §5e's open
"shared meta-state?" question), `R224` (§7 addendum carries §5f's strong-beat-sonority metric
correction into the evaluation methodology), `R101` §8.5 / `R308` §8.5 (the budget this topic is
costed against).
