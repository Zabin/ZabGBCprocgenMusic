#!/usr/bin/env python3
"""
test_rom.py — Headless verification suite for Driftune.gbc.

Same shape as the reference project's own test_rom.py (repo-relative paths, PyBoy headless,
button-driven sequences, a PASS/FAIL ledger) — reused pattern, per docs/master/MSTR-001 SS0 and
docs/research/R300. The assertion *vocabulary* is new (MSTR-001 C9): every check here reads
sound-hardware registers and/or the WRAM engine-state mirror (GDS-07), not sprite/tilemap state.

Suites:
  T1  ROM header / build invariants (no emulator)
  T2  Boot + sound-hardware init (NR52 power, channel 1 active)
  T3  Generation produces changing register writes over time (not silent, not frozen)
  T4  Input steering: each of the 6 mapped controls edits exactly its own parameter index
  T5  Reset (Select): unconditionally returns all indices to the known-good preset
  T6  Pulse B + wave channel generation (IP-0002): independent walks, both channels active

Run from the repo root: python3 test_rom.py
Requires: pyboy (pinned 2.7.0, matching the reference project), numpy.
"""
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROM_PATH = str(BASE / 'Driftune.gbc')
RESULTS_PATH = BASE / 'test_results.txt'

# WRAM addresses (must match music_engine.py / input_map.py / GDS-07)
TEMPO_IDX = 0xC000; OCTAVE_IDX = 0xC001; SCALE_IDX = 0xC002
DENSITY_IDX = 0xC003; CHMIX_IDX = 0xC004
NOTE_TIMER_PA = 0xC00C; CUR_DEGREE_PA = 0xC010
NOTE_TIMER_PB = 0xC00D; NOTE_TIMER_WV = 0xC00E
CUR_DEGREE_PB = 0xC011; CUR_DEGREE_WV = 0xC012
NOISE_STEP_IDX = 0xC019
BAD_ZONE_FLAGS = 0xC005; DISSONANCE_SCORE = 0xC006
STALE_COUNT_PA = 0xC007; ONSET_WINDOW_COUNT = 0xC00A
LCDC = 0xFF40
CHANNEL_CELLS = [0x9800, 0x9801, 0x9802, 0x9803]
BCPD = 0xFF69

# Sound registers (I/O, 0xFF00+offset)
NR13 = 0xFF13; NR14 = 0xFF14; NR52 = 0xFF26

from music_engine import PRESET_TEMPO_IDX, PRESET_OCTAVE_IDX, PRESET_SCALE_IDX

results = []
PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    status = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    msg = f"[{status}] {name}"
    if detail:
        msg += f"  ({detail})"
    results.append(msg)
    print(msg)


def build_rom():
    subprocess.run([sys.executable, str(BASE / 'build_rom.py'), ROM_PATH], check=True, cwd=BASE)


BOOT_FRAMES = 100  # the GBC boot ROM's own logo animation runs for ~90 frames before jumping
                    # to cartridge code (0x0100) — confirmed empirically against this ROM;
                    # any check of boot-time state must wait this long first.


def fresh_boot(frames=BOOT_FRAMES):
    from pyboy import PyBoy
    pb = PyBoy(ROM_PATH, window='null', sound_emulated=True)
    pb.set_emulation_speed(0)
    for _ in range(frames):
        pb.tick()
    return pb


def tap(pb, button, hold_frames=1, settle_frames=2):
    """Press-then-release a button for exactly one rising edge, then let a few frames pass
    so any resulting state change lands before the caller reads it."""
    pb.button_press(button)
    for _ in range(hold_frames):
        pb.tick()
    pb.button_release(button)
    for _ in range(settle_frames):
        pb.tick()


# ── T1: ROM header / build invariants (no emulator) ──────────────────
def t1_header():
    build_rom()
    data = Path(ROM_PATH).read_bytes()
    check("T1.1 ROM size is exactly 32768 bytes", len(data) == 32768, f"got {len(data)}")
    check("T1.2 Title bytes match DRIFTUNE", data[0x134:0x134 + 8] == b'DRIFTUNE')
    check("T1.3 GBC compatibility flag set", data[0x143] == 0x80)
    check("T1.4 Cart type is ROM ONLY (no SRAM/battery, MSTR-001 C2)", data[0x147] == 0x00)
    chk = 0
    for a in range(0x134, 0x14D):
        chk = (chk - data[a] - 1) & 0xFF
    check("T1.5 Header checksum valid", data[0x14D] == chk)


# ── T2: Boot + sound-hardware init ────────────────────────────────────
def t2_boot():
    pb = fresh_boot()
    nr52 = pb.memory[NR52]
    check("T2.1 Master sound power bit set (NR52 bit7)", (nr52 & 0x80) != 0, f"NR52={hex(nr52)}")
    check("T2.2 Channel 1 (pulse A) reports active in NR52", (nr52 & 0x01) != 0, f"NR52={hex(nr52)}")
    check("T2.3 Boot preset: TEMPO_IDX at known-good value", pb.memory[TEMPO_IDX] == PRESET_TEMPO_IDX)
    check("T2.4 Boot preset: OCTAVE_IDX at known-good value", pb.memory[OCTAVE_IDX] == PRESET_OCTAVE_IDX)
    check("T2.5 Boot preset: SCALE_IDX at known-good value", pb.memory[SCALE_IDX] == PRESET_SCALE_IDX)
    pb.stop(save=False)


# ── T3: Generation produces changing, live register writes ───────────
def t3_generation_live():
    # NR13/NR14's frequency bits are write-only on real GBC hardware (and in PyBoy's emulation
    # of it, confirmed empirically here) — reading them back is not a usable signal, which is
    # exactly why GDS-07 gives the engine a WRAM state mirror in the first place (GDS-00's
    # testability rationale). "Is the engine actually generating, not frozen" is asserted via
    # that WRAM mirror instead of trying to read the write-only PSG registers back.
    pb = fresh_boot()
    seen_degrees = set()
    seen_timers = set()
    for _ in range(400):
        pb.tick()
        seen_degrees.add(pb.memory[CUR_DEGREE_PA])
        seen_timers.add(pb.memory[NOTE_TIMER_PA])
    check("T3.1 CUR_DEGREE_PA changes over time (engine is walking, not frozen)",
          len(seen_degrees) > 1, f"distinct degrees seen: {sorted(seen_degrees)}")
    check("T3.2 NOTE_TIMER_PA counts down and reloads repeatedly (generation cadence is live)",
          len(seen_timers) > 1, f"distinct timer values seen: {len(seen_timers)}")
    check("T3.3 Channel 1 still reports active after sustained play",
          (pb.memory[NR52] & 0x01) != 0)
    pb.stop(save=False)


# ── T4: Input steering — one control, one parameter ───────────────────
def t4_input_steering():
    cases = [
        ("up", TEMPO_IDX, "T4.1 D-pad Up steps TEMPO_IDX"),
        ("down", TEMPO_IDX, "T4.2 D-pad Down steps TEMPO_IDX (back down)"),
        ("right", OCTAVE_IDX, "T4.3 D-pad Right steps OCTAVE_IDX"),
        ("left", OCTAVE_IDX, "T4.4 D-pad Left steps OCTAVE_IDX (back down)"),
        ("a", SCALE_IDX, "T4.5 A steps SCALE_IDX"),
        ("b", DENSITY_IDX, "T4.6 B steps DENSITY_IDX"),
        ("start", CHMIX_IDX, "T4.7 Start steps CHMIX_IDX"),
    ]
    pb = fresh_boot()
    for button, addr, label in cases:
        others = {a: pb.memory[a] for a in
                  (TEMPO_IDX, OCTAVE_IDX, SCALE_IDX, DENSITY_IDX, CHMIX_IDX) if a != addr}
        before = pb.memory[addr]
        tap(pb, button)
        after = pb.memory[addr]
        check(label, after != before, f"{hex(addr)}: {before} -> {after}")
        unaffected = all(pb.memory[a] == others[a] for a in others)
        check(label + " — no other parameter changed", unaffected)
    pb.stop(save=False)


# ── T6: Pulse B + wave channel generation (IP-0002) ───────────────────
def t6_pulse_b_and_wave():
    pb = fresh_boot()
    nr52 = pb.memory[NR52]
    check("T6.1 Channel 2 (pulse B) reports active in NR52", (nr52 & 0x02) != 0, f"NR52={hex(nr52)}")
    check("T6.2 Channel 3 (wave) reports active in NR52", (nr52 & 0x04) != 0, f"NR52={hex(nr52)}")

    seen_pb = set(); seen_wv = set()
    for _ in range(400):
        pb.tick()
        seen_pb.add(pb.memory[CUR_DEGREE_PB])
        seen_wv.add(pb.memory[CUR_DEGREE_WV])
    check("T6.3 CUR_DEGREE_PB changes over time (pulse B is walking independently)",
          len(seen_pb) > 1, f"distinct degrees: {sorted(seen_pb)}")
    check("T6.4 CUR_DEGREE_WV changes over time (wave channel is walking independently)",
          len(seen_wv) > 1, f"distinct degrees: {sorted(seen_wv)}")
    check("T6.5 All three pitched channels still report active after sustained play",
          (pb.memory[NR52] & 0x07) == 0x07, f"NR52={hex(pb.memory[NR52])}")
    pb.stop(save=False)


# ── T7: Noise channel + density (IP-0003) ─────────────────────────────
def t7_noise_density():
    from music_engine import DENSITY_K

    pb = fresh_boot()
    onset_counts = {}
    for density_idx in (0, len(DENSITY_K) - 1):  # sparsest and densest — non-default included
        # Drive DENSITY_IDX to the target value via B presses (wraps mod 8, starts at preset 0).
        for _ in range(density_idx):
            tap(pb, 'b')
        check(f"T7.setup DENSITY_IDX reached {density_idx}",
              pb.memory[DENSITY_IDX] == density_idx, f"got {pb.memory[DENSITY_IDX]}")

        onsets = 0
        seen_steps = set()
        for _ in range(600):
            pb.tick()
            seen_steps.add(pb.memory[NOISE_STEP_IDX])
            if pb.memory[NR52] & 0x08:
                onsets += 1
        onset_counts[density_idx] = onsets
        check(f"T7.{density_idx}.1 Noise step index cycles through all 16 steps at density {density_idx}",
              seen_steps == set(range(16)), f"seen: {sorted(seen_steps)}")
        check(f"T7.{density_idx}.2 Channel 4 (noise) triggers at least once at density {density_idx}",
              onsets > 0, f"onset-frame count: {onsets}")
        # Reset back to preset (density 0) before the next iteration's relative B-taps.
        tap(pb, 'select')

    check("T7.3 Denser preset (max DENSITY_IDX) produces more onset-frames than the sparsest",
          onset_counts[len(DENSITY_K) - 1] > onset_counts[0],
          f"onset_counts={onset_counts}")
    pb.stop(save=False)


# ── T8: Bad-zone detection (IP-0004) ──────────────────────────────────
def t8_bad_zone():
    pb = fresh_boot()
    check("T8.1 BAD_ZONE_FLAGS starts clean at boot", pb.memory[BAD_ZONE_FLAGS] == 0)
    check("T8.2 DISSONANCE_SCORE starts at 0 at boot", pb.memory[DISSONANCE_SCORE] == 0)

    seen_scores = set()
    seen_flags = set()
    for _ in range(2000):
        pb.tick()
        seen_scores.add(pb.memory[DISSONANCE_SCORE])
        seen_flags.add(pb.memory[BAD_ZONE_FLAGS])
    check("T8.3 DISSONANCE_SCORE varies over time (three independently-walking channels produce "
          "a changing interval mix)", len(seen_scores) > 1, f"distinct scores: {sorted(seen_scores)}")
    check("T8.4 BAD_ZONE_FLAGS bit3 (COMBINED) matches bit0 (DISSONANT) whenever either is set "
          "(no combination seen violates bit3 = OR of bits0-2)",
          all((f & 0x01) == 0 or (f & 0x08) != 0 for f in seen_flags), f"flags seen: {seen_flags}")

    check("T8.5 At least one bad-zone entry (DISSONANT or COMBINED) was observed over a long run",
          any(f != 0 for f in seen_flags), f"flags seen: {seen_flags}")

    # Select must clear bad-zone state unconditionally, same as the tested parameters (FR-1070).
    tap(pb, 'select')
    check("T8.6 Select clears BAD_ZONE_FLAGS", pb.memory[BAD_ZONE_FLAGS] == 0)
    check("T8.7 Select clears DISSONANCE_SCORE", pb.memory[DISSONANCE_SCORE] == 0)
    # Not necessarily 0: the same same-frame-fires-immediately effect as T8.9 above — the fresh
    # post-reset degree (0) can coincidentally equal the very next LFSR-picked degree, ticking
    # STALE_COUNT_PA to 1 within the same frame. What matters is it's reset to a fresh, tiny
    # count, not left at whatever it had accumulated across the preceding 2000-frame run.
    check("T8.8 Select resets STALE_COUNT_PA to a fresh count, not a stale accumulated one",
          pb.memory[STALE_COUNT_PA] <= 1, f"got {pb.memory[STALE_COUNT_PA]}")
    # Not 0: init_engine's own reset primes every NOTE_TIMER_* to 1, so the very next engine_tick
    # (same frame Select was processed, since apply_input runs before engine_tick in the main
    # loop) immediately fires a fresh onset per channel — a correct, intentional side effect of
    # "resume playing immediately," not leftover pre-reset accumulation. What T8.9 actually checks
    # is that the window wasn't left at a stale, accumulated-over-2000-frames count.
    check("T8.9 Select resets ONSET_WINDOW_COUNT to just this frame's fresh onsets, not a stale "
          "accumulated count", pb.memory[ONSET_WINDOW_COUNT] <= 4, f"got {pb.memory[ONSET_WINDOW_COUNT]}")
    pb.stop(save=False)


# ── T9: Visualizer (IP-0006) ───────────────────────────────────────────
def t9_visualizer():
    pb = fresh_boot()
    check("T9.1 LCD is on with BG tile data at 0x8000 and BG display enabled",
          pb.memory[LCDC] == 0x91, f"LCDC={hex(pb.memory[LCDC])}")

    for _ in range(120):
        pb.tick()
    nr52 = pb.memory[NR52]
    cells = [pb.memory[addr] for addr in CHANNEL_CELLS]
    expected = [1 if (nr52 & (1 << i)) else 0 for i in range(4)]
    check("T9.2 Each channel-indicator tile matches its own NR52 active bit",
          cells == expected, f"cells={cells} expected={expected} NR52={bin(nr52)}")

    # Drive several frames and re-check the correspondence still holds as channels change state.
    still_matching = True
    for _ in range(300):
        pb.tick()
        nr52 = pb.memory[NR52]
        cells = [pb.memory[addr] for addr in CHANNEL_CELLS]
        expected = [1 if (nr52 & (1 << i)) else 0 for i in range(4)]
        if cells != expected:
            still_matching = False
            break
    check("T9.3 Indicator tiles keep tracking NR52 correctly over a sustained run", still_matching)
    pb.stop(save=False)


# ── T5: Select resets to the known-good preset unconditionally ───────
def t5_reset():
    pb = fresh_boot()
    # Drift several parameters away from preset first.
    for button in ("up", "up", "right", "a", "b", "start"):
        tap(pb, button)
    drifted = (pb.memory[TEMPO_IDX], pb.memory[OCTAVE_IDX], pb.memory[SCALE_IDX])
    check("T5.1 Setup: parameters actually drifted from preset before reset",
          drifted != (PRESET_TEMPO_IDX, PRESET_OCTAVE_IDX, PRESET_SCALE_IDX), f"drifted={drifted}")

    tap(pb, "select")

    check("T5.2 Select restores TEMPO_IDX to preset", pb.memory[TEMPO_IDX] == PRESET_TEMPO_IDX)
    check("T5.3 Select restores OCTAVE_IDX to preset", pb.memory[OCTAVE_IDX] == PRESET_OCTAVE_IDX)
    check("T5.4 Select restores SCALE_IDX to preset", pb.memory[SCALE_IDX] == PRESET_SCALE_IDX)
    check("T5.5 Select restores CUR_DEGREE_PA to 0", pb.memory[CUR_DEGREE_PA] == 0)
    pb.stop(save=False)


def main():
    t1_header()
    t2_boot()
    t3_generation_live()
    t4_input_steering()
    t5_reset()
    t6_pulse_b_and_wave()
    t7_noise_density()
    t8_bad_zone()
    t9_visualizer()

    print(f"\n{PASS} PASS, {FAIL} FAIL out of {PASS + FAIL}")
    RESULTS_PATH.write_text("\n".join(results) + f"\n\n{PASS} PASS, {FAIL} FAIL\n")
    if os.path.exists(ROM_PATH):
        os.remove(ROM_PATH)
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
