# R207 — GB-Era Chiptune Composition & Channel-Usage Idioms

- **Tier:** R200 · **Owned by:** `02-research-game-design` · **Status:** ✅ Authored 2026-07-21

## 1. Purpose

Ground `IP-0002`/`IP-0003`'s channel-role design (what pulse A/B, wave, and noise are each
*for*) against real GB chiptune composition convention, not just hardware capability (R108).

## 2. Scope

Conventional channel roles in Game Boy tracker music (LSDJ and similar), and the arpeggio
technique used to fake polyphony on a channel-starved chip.

## 3. Concepts

- The four channels are conventionally named **PU1/PU2/WAV/NOI** in trackers like LSDJ, mirroring
  the hardware exactly (two pulse, one wave, one noise) [GameBrew — Little Sound Dj GB](https://www.gamebrew.org/wiki/Little_Sound_Dj_GB).
- **Conventional role split**: the **pulse channels** carry melody/lead and/or harmony, often
  processed or arranged to evoke traditional instrument timbre rather than embracing the raw
  square-wave sound; the **wave channel** is "what makes the Game Boy unique" — commonly used for
  **bass**, sample-like/voice-like tones, or a secondary lead with a distinct timbre from the
  pulse channels (via its custom 32-sample waveform, R108); the **noise channel** is used for
  **percussion** — "static... formed into bursts" standing in for drums, and other percussive/
  texture effects [Synthtopia — Making Music On A Game Boy With LSDj](https://www.synthtopia.com/content/2016/05/06/making-music-on-a-game-boy-with-lsdj/); [GB Studio Central — Tracker Lesson 1](https://gbstudiocentral.com/tips/gb-studio-tracker-lesson-1-terminology-and-basics-of-the-game-boy-sound-chip/).
- **Arpeggios as a polyphony workaround**: "due to the limited number of voices... one of the main
  challenges is to produce rich polyphonic music... usually via quick arpeggios," a defining
  feature of the genre [graphsearch.epfl.ch — chiptune concept summary](https://graphsearch.epfl.ch/concept/83463); this is the standard trick for a single monophonic
  pulse channel to *imply* a chord by cycling rapidly between its notes.

### Sources
- [GameBrew — Little Sound Dj GB](https://www.gamebrew.org/wiki/Little_Sound_Dj_GB)
- [Synthtopia — Making Music On A Game Boy With LSDj](https://www.synthtopia.com/content/2016/05/06/making-music-on-a-game-boy-with-lsdj/)
- [GB Studio Central — Tracker Lesson 1: Terminology & Basics](https://gbstudiocentral.com/tips/gb-studio-tracker-lesson-1-terminology-and-basics-of-the-game-boy-sound-chip/)
- [Soundfly — Chiptune Crash Course: Arranging in Four Channels](https://soundfly.com/courses/arranging-in-four-channels)

## 4. Operational Context

`IP-0001`'s pulse A is the melody voice, consistent with convention. GDS-03 SS3's architecture
does **not** yet assign wave/noise distinct *musical roles* — it only assigns them registers.
This is a real gap this topic surfaces (a `finding`, routed to the backlog): the current plan
would have `IP-0002` give the wave channel the *same* scale-constrained-walk melodic treatment as
pulse B, which convention says undersells the wave channel's distinctive value (bass/timbre role)
in genre-typical GB music.

## 5. Implementation Guidance

- **Recommend for `IP-0002`'s FS**: give the wave channel a **bass role** — same scale-degree
  walk mechanism as R201 describes, but anchored an octave (or two) below pulse A/B's home
  octave, and/or on a slower note-timer (bass lines conventionally move less often than melody).
  This is a data-only change (a different `OCTAVE_ROOT_HZ` anchor and/or `TEMPO_TABLE` divisor for
  the wave channel specifically) — no new mechanism needed, just not treating all three pitched
  channels identically.
- **Recommend for `IP-0003`'s FS**: the noise channel is percussion/texture, consistent with
  GDS-03's own "Euclidean-gated noise hits" framing — no change needed there, this topic confirms
  it rather than revising it.
- **Arpeggio technique** is a candidate v2+ enhancement (not v1 scope) for pulse A/B to imply
  richer harmony without more channels — flagged as a `feature`-type backlog candidate for after
  `IP-0002`/`IP-0003` ship, not decided here.

## 6. Feature Mapping

`IP-0002` (pulse B + wave — not yet authored; this topic's finding should inform its FS), `IP-0003`
(noise, confirmed consistent with plan).

## 7. Related Topics

R201 (the generation algorithm this topic recommends differentiating per channel), R108 (wave
channel's Wave-RAM timbre lever, the mechanism a bass-role wave channel would still use for
texture on top of octave placement).
