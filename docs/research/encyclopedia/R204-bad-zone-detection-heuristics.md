# R204 — "Bad Zone" Detection Heuristics

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21
- **Supersedes:** part of `docs/research/R200-generative-music-design.md` SS2

## 1. Purpose

Ground GDS-03 SS4's bad-zone metric (dissonance + repetition + channel-overload, combined into
one flag) against real psychoacoustic and music-theory literature, and firm up the placeholder
dissonance-weight table `BL-0005` currently leaves untuned.

## 2. Scope

Interval-class dissonance/consonance ranking (the primary signal), and confirmation that
repetition-detection and onset-rate overload are reasonable secondary/tertiary signals absent a
literature-specific citation for the latter two (they are closer to engineering heuristics than
psychoacoustic theory, and are treated as such below).

## 3. Concepts

- **Helmholtz's roughness/sensory-dissonance theory** (1863, still the ancestor of essentially
  every modern consonance/dissonance model): dissonance arises from "roughness" — audible beating
  between nearby partials of two simultaneously sounding tones that stimulate overlapping regions
  of the inner ear; consonance is denoseness of that roughness [Terhardt — Sensory consonance](http://terhardt.userweb.mwn.de/ter/top/senscons.html).
  This ranking — from most to least consonant across the twelve chromatic intervals — "is also the
  result of almost all consonance theories known today," i.e. it has been robustly reproduced by
  a century-plus of follow-on psychoacoustic work, not just Helmholtz's own 19th-century claim
  [PMC — Neuromagnetic representation of musical roughness in chord progressions](https://pmc.ncbi.nlm.nih.gov/articles/PMC11034485/).
- For sine/harmonic-complex-tone dyads, measured consonance drops to its sharpest minimum around
  a **~1.5-semitone** interval and *recovers* continuously as the interval widens beyond that —
  i.e. the classic "roughness curve" is not monotonic in interval size; a minor 2nd (1 semitone)
  and a major 2nd (2 semitones) are both near the roughness peak, while wider dissonant intervals
  (e.g. a tritone, minor 7th) are audibly rough but measurably less so than a minor 2nd [search
  synthesis per multiple psychoacoustic sources — see Sources below].
- **Standard modern interval-class consonance ordering** (semitones, 0-11, octave-equivalent),
  consistent across the sources above and standard Western music-theory pedagogy: most consonant
  → least: **unison/octave (0) > perfect 5th (7) > perfect 4th (5) > major/minor 3rd (4, 3) >
  major/minor 6th (9, 8) > major 2nd (2) > minor 7th (10) > major 7th (11) > tritone (6) >
  minor 2nd (1)**. (The 4th's consonance is context-dependent in full common-practice theory —
  treated as "mildly consonant" here, which is the conventional simplification for a *pairwise*
  interval-class model like this project's, as opposed to a full contrapuntal-context model.)

### Sources
- [Terhardt — Sensory consonance](http://terhardt.userweb.mwn.de/ter/top/senscons.html)
- [PMC — Neuromagnetic representation of musical roughness in chord progressions](https://pmc.ncbi.nlm.nih.gov/articles/PMC11034485/)
- [AIP Publishing — From roughness to coincidence: Concepts of dissonance and consonance](https://pubs.aip.org/asa/poma/article/56/1/035009/3373057/From-roughness-to-coincidence-Concepts-of)
- [Frequency ratios and the perception of tone patterns](https://link.springer.com/content/pdf/10.3758/bf03200773.pdf)
- Repetition-detection and onset-rate-overload: no specific psychoacoustic literature claim is
  made for these two — they are engineering heuristics for "stuck" and "cluttered" respectively,
  named as such in GDS-03 SS4b/SS4c and not overstated as literature-grounded here.

## 4. Operational Context

GDS-03 SS4a already specifies "a 12-entry dissonance weight table... consonant intervals... score
low, dissonant ones... score high" as a *shape*, explicitly leaving weight values as a tuning
placeholder (`BL-0005`). This topic upgrades that from an unsourced plausible ordering to a
literature-grounded one.

## 5. Implementation Guidance

**Concrete `DISSONANCE_WEIGHT` table proposal** (12 entries, indexed by interval mod 12,
octave-equivalent, weight 0-15 to fit the existing byte-sum design in GDS-03 SS4a), derived from
the consonance ordering in SS3 above (lower interval-class number ≠ lower weight — the ordering is
by *measured roughness*, not semitone count):

| Semitones | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Interval | unison/8ve | m2 | M2 | m3 | M3 | P4 | tritone | P5 | m6 | M6 | m7 | M7 |
| Weight (proposed) | 0 | 15 | 11 | 3 | 2 | 4 | 13 | 1 | 5 | 4 | 9 | 12 |

This is still a **v1 proposal, not a final tuned value** (per `BL-0005`'s own honest deferral —
real tuning needs a listening pass once pulse B/wave exist to actually form intervals against
pulse A), but it is now derived from the cited roughness ordering rather than asserted from
taste: minor 2nd/major 7th (both adjacent-to-unison, near the roughness peak) get the two highest
weights; the tritone is high but below the minor 2nd (matches the "roughness peaks near ~1.5
semitones, not at maximum interval width" finding in SS3); perfect 5th/4th/major-minor 3rds get
the lowest non-zero weights, matching their conventional treatment as the most consonant non-
unison intervals.

**`08-content-authoring`/`09-content-review`** should treat this table as the concrete artifact
`BL-0005`'s deferred tuning pass adjusts, not something to re-derive from scratch.

## 6. Feature Mapping

FR-1080 (`DISSONANCE_SCORE` computation, GDS-03 SS4a), `IP-0004` (bad-zone implementation, not
yet authored), `BL-0005` (tuning deferral — now has a concrete starting table to tune from).

## 6b. Forward trace (`MSTR-001` C10)

*Convention established 2026-07-26 (`BL-0067`), per [GDS-10 §4](../../architecture/10-requirements-traceability-matrix.md): every research topic records, at the topic itself, either the shipped code it fed or an explicitly-named exception. Maintained where the topic lives rather than in a central matrix.*

✅ **TRACED.** The tier's strongest trace. Grounds all three limbs of the shipped bad-zone detector — `DISSONANCE_SCORE`, `STALE_COUNT_*` repetition detection, and channel overload — in `music_engine.py`'s `_emit_badzone_tick`. Shipped via `IP-0004` (`VERIFIED`), extended by `IP-0007`'s autonomous avoidance/recovery and recalibrated by `IP-9020`. Architecture: `GDS-03` §4a, `GDS-04` §5. Requirements: `FR-1080`-`FR-1110`. Tests: `T6`-`T8`.

## 7. Related Topics

R201 (the generation algorithm whose output this topic scores), R108 (only the three pitched
channels participate — no dissonance scoring for noise).
