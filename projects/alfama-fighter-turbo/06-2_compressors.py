"""6.2 The band's compressors, before and after the mix polish of 12 October: how far they held the
music down and how much that hold moved, as two gain-reduction meters with their traces.

Animated, a seamless loop: each meter's level and its scrolling trace move as the compressors did,
pinned 8 to 13 dB down and swinging about 5 dB before, about 1 dB down and moving a dB or two after.
The readings are fixed; only the meters and traces move.

Every number is from docs/plans/2026-10-12-mix-polish.md at alfamafighterturbo 74e2f64 ("What changed,
and the numbers", its table and its section 1, "The band's compressors"):
- Before: the band's ceiling compressor at -24 dB with a 60 ms release held the band down 8 to 13 dB
  all the time, in every fight, menu and intro (over 1 dB 87 to 100% of the time); its gain moved 4.4 to
  5.3 dB, riding the bass's cycles (a buzz) and pumping; quiet moments came out lifted 8.9 to 12.6 dB
  over loud ones.
- After: the ceiling at -10 dB for the loudest strokes only, released over 200 ms; in a fight it holds
  0.4 to 1.9 dB on average; across the ten themes and the title the gain moves 1.1 to 2.0 dB; quiet
  moments lifted 2.4 to 5.3 dB.
- The fights' loudness: -16.0 LUFS on average before, -15.9 after.
- The title theme's quietest and loudest second, 6.2 dB apart as written: 1.7 dB apart as it came out
  of the old compressors, 5.0 after.
The meters' motion is drawn to those ranges, not recorded from the game.
"""

import math

from pixelkit import Rect
from series import export, frame

SECONDS, FPS = 4, 20
SCALE_DB = 15
SIDES = [
    {"title": "BEFORE", "sub": "UNTIL 12 OCTOBER", "colour": "orange", "lo": 8.0, "hi": 13.0,
     "rows": [("HELD DOWN", "8 TO 13 DB"), ("MOVING BY", "4.4 TO 5.3 DB"), ("QUIET BARS LIFTED", "8.9 TO 12.6 DB"),
              ("TITLE THEME'S RANGE", "6.2 → 1.7 DB"), ("A FIGHT'S LOUDNESS", "-16.0 LUFS")],
     "setting": "CEILING AT -24 DB, LET GO IN 60 MS", "pump": 2, "buzz": 23},
    {"title": "AFTER", "sub": "FROM 12 OCTOBER", "colour": "yellow", "lo": 0.4, "hi": 1.9,
     "rows": [("HELD DOWN", "0.4 TO 1.9 DB"), ("MOVING BY", "1.1 TO 2.0 DB"), ("QUIET BARS LIFTED", "2.4 TO 5.3 DB"),
              ("TITLE THEME'S RANGE", "6.2 → 5.0 DB"), ("A FIGHT'S LOUDNESS", "-15.9 LUFS")],
     "setting": "CEILING AT -10 DB, LET GO IN 200 MS", "pump": 2, "buzz": 0},
]


def gain(side, u):
    """Gain reduction in dB at loop position u (whole cycles, so the loop is seamless): a pump on the
    beat, a buzz riding the bass where there was one, kept inside the side's range."""
    lo, hi = side["lo"], side["hi"]
    mid, amp = (lo + hi) / 2, (hi - lo) / 2
    v = 0.75 * math.sin(2 * math.pi * side["pump"] * 4 * u) + 0.25 * math.sin(2 * math.pi * 3 * u + 1.1)
    if side["buzz"]:
        v = 0.85 * v + 0.15 * math.sin(2 * math.pi * side["buzz"] * 4 * u)
    return mid + amp * v


def meter(c, x, y, w, h, db, colour):
    """A gain-reduction meter: lit from the top down to db, on a 0 to 15 dB scale."""
    c.rect(x, y, w, h, "bg")
    lit = round(h * min(db, SCALE_DB) / SCALE_DB)
    for row in range(0, h, 2):
        c.hline(x + 1, y + row, w - 2, colour if row < lit else "raised")


def side_panel(c, t, side, r):
    body = c.panel(*r, side["title"], color=side["colour"], sub=side["sub"], right="DB HELD DOWN", right_color="dim")
    # The meter and its scale.
    mh = 66
    my = body.y + 2
    for db in range(0, SCALE_DB + 1, 3):
        yy = my + round(mh * db / SCALE_DB)
        c.text(body.x + 11, yy - 2, str(db), "white" if side["lo"] <= db <= side["hi"] else "dim", align="right")
        c.hline(body.x + 12, yy, 2, "dim")
    meter(c, body.x + 15, my, 12, mh + 1, gain(side, t), side["colour"])
    # The held range, marked beside the meter.
    ylo, yhi = my + round(mh * side["lo"] / SCALE_DB), my + round(mh * side["hi"] / SCALE_DB)
    c.vline(body.x + 29, ylo, yhi - ylo + 1, side["colour"])
    # The trace: the last few seconds of the gain, scrolling left.
    tr = Rect(body.x + 34, my, body.x2 - body.x - 34, mh + 1)
    c.rect(*tr, "bg")
    c.grid(*tr, rows=5, cols=0)
    for i in range(tr.w):
        depth = round(mh * gain(side, t + (i - tr.w) / (tr.w * 2)) / SCALE_DB)
        c.vline(tr.x + i, tr.y, depth, c.dark(side["colour"]))
        c.px(tr.x + i, tr.y + depth, side["colour"])
    # The readings.
    ky = my + mh + 5
    for k, (label, value) in enumerate(side["rows"]):
        c.text(body.x, ky + k * 7, label, "dim")
        c.text(body.x2 - 1, ky + k * 7, value, "white", align="right")
    c.text(body.x, ky + len(side["rows"]) * 7 + 2, side["setting"], side["colour"])


def draw(c, t):
    top, bottom = frame(c, 6, 2, "THE BAND'S COMPRESSORS, BEFORE AND AFTER",
                        "THE TITLE THEME'S RANGE: ITS QUIETEST TO LOUDEST SECOND, AS WRITTEN → AS HEARD. THE METERS MOVE WITHIN THE MEASURED RANGES.")
    area = Rect(0, top + 1, c.w, bottom - top - 3)
    for side, r in zip(SIDES, area.cols(2, gap=1)):
        side_panel(c, t, side, r)

if __name__ == "__main__":
    export(draw, __file__, preset="wide", seconds=SECONDS, fps=FPS, seamless=True)
