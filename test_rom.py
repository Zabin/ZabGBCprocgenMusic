#!/usr/bin/env python3
"""
test_rom.py — Headless verification suite for Driftune.gbc (IP-0001 scope).

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

    print(f"\n{PASS} PASS, {FAIL} FAIL out of {PASS + FAIL}")
    RESULTS_PATH.write_text("\n".join(results) + f"\n\n{PASS} PASS, {FAIL} FAIL\n")
    if os.path.exists(ROM_PATH):
        os.remove(ROM_PATH)
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
