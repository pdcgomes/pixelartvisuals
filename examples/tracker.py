"""Pixeltrakker 8: a fantasy tracker, half Amiga ProTracker (grey bevels, counters, sample list) and
half Dirtywave M8 (black pattern view, coloured fields, a live scope). A 32-row pattern loops."""

import math
from pathlib import Path

from pixelkit import animate

ROWS, VISIBLE = 32, 11
GREY = {"face": "#a8a8b0", "hi": "#e2e2e8", "lo": "#5c5c66", "ink": "#16161c", "well": "#08080c"}
SAMPLES = ["01 KICK-909", "02 CLAP-808", "03 HAT-CLOSED", "04 BASS-ACID", "05 VIKING-VOX", "06 HOOVER"]
TRACKS = [("KICK", "red"), ("CLAP", "orange"), ("HATS", "gold"), ("ACID", "lime")]
NOTES = ["A-1", "A-1", "C-2", "A-1", "G-1", "A-1", "E-2", "D-2"]


def cell(track: int, row: int):
    """(note, instrument, effect) or None, for a four-on-the-floor pattern with an acid line."""
    if track == 0 and row % 4 == 0:
        return "C-2", "01", "C40"
    if track == 1 and row % 8 == 4:
        return "D-3", "02", "C38"
    if track == 1 and row == 30:
        return "D-3", "02", "C14"
    if track == 2 and row % 2 == 0:
        return "F#4", "03", "C30" if row % 4 == 2 else "C18"
    if track == 3 and row % 2 == 1:
        note = NOTES[(row // 2) % len(NOTES)]
        return note, "04", "301" if row % 8 == 7 else "E11" if row % 16 == 5 else "..."
    if track == 3 and row == 16:
        return "A-2", "05", "C40"
    return None


def bevel(c, x, y, w, h, *, sunk=False):
    c.rect(x, y, w, h, GREY["well"] if sunk else GREY["face"])
    top, bottom = (GREY["lo"], GREY["hi"]) if sunk else (GREY["hi"], GREY["lo"])
    c.hline(x, y, w, top)
    c.vline(x, y, h, top)
    c.hline(x, y + h - 1, w, bottom)
    c.vline(x + w - 1, y, h, bottom)


def draw(c, t):
    row = round(t * ROWS) % ROWS

    # Workbench title bar with a close gadget and drag stripes.
    bevel(c, 0, 0, 320, 11)
    bevel(c, 2, 2, 9, 7)
    c.rect(5, 4, 3, 3, GREY["ink"])
    c.text(15, 3, "PIXELTRAKKER 8 · TECHNO-VIKING.MOD", GREY["ink"])
    for k in range(6):
        c.hline(178, 3 + k, 96, GREY["lo"] if k % 2 else GREY["face"])
    c.icon(292, 2, "play", "#1a6a1a")
    c.text(316, 3, "PLAY", "#1a6a1a", align="right")

    # Counters, Amiga style: labels on grey, values in sunk LCD wells.
    bevel(c, 0, 12, 92, 62)
    for i, (label, value) in enumerate((("POS", "0003"), ("PATTERN", "0012"), ("LENGTH", "0024"),
                                        ("BPM", "0150"), ("SPEED", "0006"))):
        y = 16 + i * 11
        c.text(5, y + 1, label, GREY["ink"])
        bevel(c, 50, y - 1, 38, 9, sunk=True)
        c.text(85, y + 1, value, "gold" if label != "BPM" else "lime", align="right")

    bevel(c, 93, 12, 108, 62)
    c.text(97, 15, "SAMPLES", GREY["ink"])
    bevel(c, 96, 22, 102, 49, sunk=True)
    playing = {cell(k, row)[1] for k in range(4) if cell(k, row)}
    for i, name in enumerate(SAMPLES):
        y = 25 + i * 7
        if name[:2] in playing:
            c.rect(97, y - 1, 100, 7, "#2a2a6a")
        c.text(99, y, name, "white" if name[:2] in playing else "muted")

    # M8 side: the scope and the four VU meters.
    c.rect(202, 12, 118, 62, "#000000")
    c.box(202, 12, 118, 62, "#2a2a3a")
    c.text(206, 15, "SCOPE", "violet.light")
    c.text(316, 15, f"ROW {row:02X}", "dim", align="right")
    hit = [cell(k, row) is not None for k in range(4)]
    prev = 0
    for i in range(108):
        u = i / 108
        amp = 9 * (1 if hit[0] else 0.45)
        v = amp * math.sin(2 * math.pi * (3 * u + t * 6)) + 4 * math.sin(2 * math.pi * (11 * u - t * 9)) * (
            1 if hit[3] else 0.4)
        y = 42 + round(v)
        if i:
            c.line(207 + i - 1, prev, 207 + i, y, "cyan")
        prev = y
    for k, (name, colour) in enumerate(TRACKS):
        since = min(((row - r) % ROWS for r in range(ROWS) if cell(k, r)), default=ROWS)
        level = max(0.0, 1 - since * 0.22)
        c.seg_column(209 + k * 28, 57, 20, 13, level, colour, seg=1, gap=1, empty="#1a1a24")
    # Pattern view.
    c.rect(0, 75, 320, 105, "#000000")
    top = 79
    for k, (name, colour) in enumerate(TRACKS):
        x = 18 + k * 76
        c.text(x, top, f"TRACK {k + 1}", "white")
        c.text(x + 34, top, name, colour)
    mid = VISIBLE // 2
    y0 = top + 9
    c.rect(0, y0 + mid * 8 - 1, 320, 8, "#202058")
    for j in range(VISIBLE):
        r = (row + j - mid) % ROWS
        y = y0 + j * 8
        current = j == mid
        c.text(3, y, f"{r:02X}", "white" if current else "gold" if r % 4 == 0 else "dim")
        for k in range(4):
            x = 18 + k * 76
            entry = cell(k, r)
            if entry is None:
                c.text(x, y, "---", "#30303c")
                c.text(x + 16, y, "..", "#30303c")
                c.text(x + 28, y, "...", "#30303c")
                continue
            note, inst, fx = entry
            c.text(x, y, note, "white")
            c.text(x + 16, y, inst, "cyan")
            c.text(x + 28, y, fx, "orange" if fx != "..." else "#30303c")


animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=3.2, fps=10, seamless=True)
