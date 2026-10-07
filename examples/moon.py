"""Moon phases for October 2026: a calendar of computed moons, the four principal phases marked, and
tonight's moon drawn large with its maria."""

import calendar
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pixelkit import Canvas

SYNODIC = 29.530588853
NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
NOW = datetime(2026, 10, 7, 20, 15, tzinfo=timezone.utc)
MARIA = [(-0.32, -0.28, 0.26), (0.18, -0.12, 0.2), (-0.12, 0.22, 0.24), (0.36, 0.34, 0.12), (0.05, -0.45, 0.1)]
NAMES = [(0.03, "NEW MOON"), (0.22, "WAXING CRESCENT"), (0.28, "FIRST QUARTER"), (0.47, "WAXING GIBBOUS"),
         (0.53, "FULL MOON"), (0.72, "WANING GIBBOUS"), (0.78, "LAST QUARTER"), (0.97, "WANING CRESCENT"),
         (1.0, "NEW MOON")]


def phase(when: datetime) -> float:
    return ((when - NEW_MOON).total_seconds() / 86400 % SYNODIC) / SYNODIC


def events(year: int, month: int):
    """Date of each principal phase in the month, by interpolating between noons."""
    out = {}
    start = datetime(year, month, 1, tzinfo=timezone.utc) - timedelta(days=1)
    for k in range(33):
        a, b = start + timedelta(days=k), start + timedelta(days=k + 1)
        pa, pb = phase(a), phase(b)
        if pb < pa:
            pb += 1
        for q, name in ((0.0, "NEW"), (0.25, "1ST Q"), (0.5, "FULL"), (0.75, "LAST Q"), (1.0, "NEW")):
            if pa < q <= pb:
                when = a + (b - a) * ((q - pa) / (pb - pa))
                if when.month == month:
                    out[when.day] = name
    return out


def moon(c, cx, cy, r, p, *, detail=False):
    """A moon disc lit for phase p (0 new, 0.5 full), lit side on the right while waxing."""
    k = math.cos(2 * math.pi * p)
    for py in range(int(cy - r) - 1, int(cy + r) + 2):
        for px in range(int(cx - r) - 1, int(cx + r) + 2):
            dx, dy = (px + 0.5 - cx) / r, (py + 0.5 - cy) / r
            if dx * dx + dy * dy >= 1:
                continue
            edge = k * math.sqrt(1 - dy * dy)
            lit = dx > edge if p < 0.5 else dx < -edge
            if lit:
                sea = detail and any((dx - mx) ** 2 + (dy - my) ** 2 < mr * mr for mx, my, mr in MARIA)
                colour = "muted" if sea else "white" if detail and (dx + dy) < -0.6 else "text"
            else:
                colour = "raised" if detail else "line"
            c.px(px, py, colour)


c = Canvas(preset="wide")
top = c.header("MOON PHASES · OCTOBER 2026", right="AS SEEN FROM THE NORTH")
bottom = c.footer("PHASES FROM THE MEAN SYNODIC MONTH OF 29.53 DAYS, SO THE MARKED DAYS ARE ESTIMATES; THE REAL "
                  "MOON CAN RUN HALF A DAY EARLY OR LATE.")
cal = c.panel(0, top + 1, 206, bottom - top - 3, "OCTOBER", color="gold", sub="2026")
marks = events(2026, 10)
cw, ch = 28, 21
for i, day in enumerate(("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")):
    c.text(cal.x + i * cw + cw // 2, cal.y, day, "dim", align="center")
first = datetime(2026, 10, 1).weekday()
for day in range(1, calendar.monthrange(2026, 10)[1] + 1):
    slot = first + day - 1
    x, y = cal.x + (slot % 7) * cw, cal.y + 8 + (slot // 7) * ch
    noon = datetime(2026, 10, day, 12, tzinfo=timezone.utc)
    today = day == NOW.day
    if today:
        c.box(x, y - 1, cw - 1, ch - 1, "gold")
    c.text(x + 2, y + 1, str(day), "gold" if today else "white" if day in marks else "dim")
    moon(c, x + cw / 2 + 4, y + 9, 5.5, phase(noon))
    if day in marks:
        c.text(x + cw // 2, y + 15, marks[day], c.light("gold") if marks[day] == "FULL" else "text", align="center")

tonight = c.panel(208, top + 1, 112, bottom - top - 3, "TONIGHT", color="white", sub="7 OCT")
p = phase(NOW)
moon(c, tonight.cx, tonight.y + 34, 30, p, detail=True)
name = next(n for limit, n in NAMES if p < limit)
c.text(tonight.cx, tonight.y + 70, name, "white", align="center")
c.text(tonight.cx, tonight.y + 78, f"{(1 - math.cos(2 * math.pi * p)) / 2:.0%} LIT · DAY {p * SYNODIC:.0f} OF 29.5",
       "dim", align="center")
upcoming = sorted((d, n) for d, n in marks.items() if d > NOW.day and n in ("NEW", "FULL"))
c.text(tonight.cx, tonight.y + 88, "  ·  ".join(f"{n} {d} OCT" for d, n in upcoming), "gold", align="center")

c.save(Path(__file__).with_suffix(".png"))
