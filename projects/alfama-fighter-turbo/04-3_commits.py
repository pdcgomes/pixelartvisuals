"""4.3 When the game was made: all 1,548 commits of the nine days as a day-by-hour heatmap, with each hour's total
above it and each day's total beside it. The busiest hour of the day was the one after midnight.

Animated: the nine days fill in hour by hour, in order, while the totals and the hour bars count up; then it holds.
Hours before the first commit (4 October, before 22:00) and after the snapshot (12 October, after 16:00) are
dotted, so they don't read as hours with nothing done.

Numbers: `git -C alfamafighterturbo log --format=%ad --date=format:'%Y-%m-%d %H' 74e2f64`, every commit including
merges, in Lisbon time (UTC+1): 1,548 in all, 172 a day on average, 348 on the busiest day (10 October); 116 in
the hour from 00:00, the busiest hour, and 109 from 23:00; 418 between 00:00 and 06:00; 36 in the busiest single
hours (8 October from 01:00, 11 October from 23:00).
"""

from datetime import date

from pixelkit import ease_out, phase
from series import export, frame

COMMITS = {
    "2026-10-04": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 5],
    "2026-10-05": [0, 0, 0, 0, 0, 0, 2, 3, 1, 2, 4, 3, 1, 1, 3, 3, 1, 0, 0, 0, 2, 6, 5, 4],
    "2026-10-06": [0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 2, 5, 3, 7, 15, 1, 2, 0, 0, 0, 0, 0, 2, 5],
    "2026-10-07": [14, 4, 0, 0, 0, 0, 7, 6, 6, 4, 10, 6, 10, 3, 6, 4, 3, 2, 13, 22, 27, 7, 18, 9],
    "2026-10-08": [30, 36, 25, 6, 9, 4, 0, 24, 22, 15, 24, 32, 5, 3, 9, 17, 3, 5, 4, 0, 0, 0, 0, 9],
    "2026-10-09": [10, 0, 0, 0, 0, 0, 1, 3, 6, 7, 14, 7, 0, 0, 0, 11, 22, 17, 17, 34, 20, 19, 22, 17],
    "2026-10-10": [14, 10, 15, 26, 21, 18, 12, 8, 7, 16, 24, 7, 27, 14, 20, 11, 8, 10, 5, 8, 15, 11, 17, 24],
    "2026-10-11": [25, 21, 12, 24, 8, 30, 22, 2, 6, 22, 6, 2, 0, 0, 0, 0, 4, 14, 21, 24, 11, 5, 15, 36],
    "2026-10-12": [23, 29, 4, 0, 0, 0, 7, 4, 0, 2, 13, 4, 3, 5, 3, 10, 1, 0, 0, 0, 0, 0, 0, 0],
}
FIRST, LAST = (0, 22), (8, 16)  # the first commit's hour and the snapshot's
RAMP = ["raised", "#3a2310", "orange.dark", "orange", "orange.light", "white"]
CELL, GAP = 7, 1

days = sorted(COMMITS)
rows = [COMMITS[d] for d in days]
TOTAL = sum(map(sum, rows))
VMAX = max(max(r) for r in rows)
PEAK_HOURS = [sum(r[h] for r in rows) for h in range(24)]
PEAK = max(PEAK_HOURS)
BUSIEST = max(map(sum, rows))
FILL = (0.03, 0.75)


def outside(d: int, h: int) -> bool:
    return (d, h) < FIRST or (d, h) > LAST


def draw(c, t):
    top, bottom = frame(c, 4, 3, "WHEN THE GAME WAS MADE",
                        "EVERY COMMIT, MERGES INCLUDED, 4 OCT 22:32 TO 12 OCT 16:00, LISBON TIME.")
    shown = round(len(days) * 24 * ease_out(phase(t, *FILL)))
    seen = [[v if d * 24 + h < shown else 0 for h, v in enumerate(r)] for d, r in enumerate(rows)]
    total = sum(map(sum, seen))
    hours = [sum(r[h] for r in seen) for h in range(24)]
    totals = [sum(r) for r in seen]

    hero_w = c.text(4, top + 3, c.num(total), "white", font="large", scale=3, shadow="dim")
    hero_w = max(hero_w, c.measure(c.num(TOTAL), "large", 3))
    c.strip(4, top + 26, hero_w, 2, RAMP[1:])
    fx = hero_w + 12
    c.text(fx, top + 3, "COMMITS IN NINE DAYS", "white")
    c.text(fx, top + 10, f"{round(TOTAL / len(days))} A DAY · {BUSIEST} ON THE BUSIEST, 10 OCTOBER", "dim")
    facts = [(f"{sum(hours[:6])}", "AFTER MIDNIGHT", "00:00 TO 06:00", "white"),
             (f"{hours[0]}", "BUSIEST HOUR", "FROM 00:00", "orange.light"),
             (f"{hours[23]}", "NEXT BUSIEST", "FROM 23:00", "white")]
    x = fx
    for (n, label, when, colour), final in zip(facts, (sum(PEAK_HOURS[:6]), PEAK_HOURS[0], PEAK_HOURS[23])):
        w = c.measure(str(final), "large")
        c.text(x + w, top + 19, n, colour, font="large", align="right")
        c.text(x + w + 3, top + 19, label, "text")
        c.text(x + w + 3, top + 26, when, "dim")
        x += w + 3 + max(c.measure(label), c.measure(when)) + 6

    panel = c.panel(0, top + 35, 320, bottom - top - 37, "BY DAY AND HOUR", color="orange.light",
                    sub="EVERY SQUARE IS ONE HOUR", right=[("· ", "line"), ("OUTSIDE THE NINE DAYS", "dim")])
    hx = panel.x + 40
    bars_y = panel.y
    for h, n in enumerate(hours):
        bh = round(n / PEAK * 11)
        c.rect(hx + h * (CELL + GAP), bars_y + 11 - bh, CELL, bh, "orange.light" if h == 0 else "orange")
    for h in range(0, 24, 6):
        c.text(hx + h * (CELL + GAP), bars_y + 13, f"{h:02d}", "white" if h == 0 else "dim")
    grid_y = bars_y + 20
    grid = c.heatmap(hx, grid_y, seen, cell=CELL, gap=GAP, colors=RAMP, vmax=VMAX)
    for d in range(len(days)):
        for h in range(24):
            if outside(d, h):
                x, y = hx + h * (CELL + GAP), grid_y + d * (CELL + GAP)
                c.rect(x, y, CELL, CELL, "panel")
                c.px(x + CELL // 2, y + CELL // 2, "line")
    for j, d in enumerate(days):
        y = grid_y + j * (CELL + GAP) + 1
        c.text(panel.x, y, date.fromisoformat(d).strftime("%a %d").upper(), "white" if j == 6 else "dim")
        tx = grid.x2 + 6
        c.rect(tx, y, round(totals[j] / BUSIEST * 44), 5, "orange.light" if totals[j] == BUSIEST else "orange")
        c.text(panel.x2, y, str(totals[j]), "white", align="right")


export(draw, __file__, preset="wide", seconds=5, fps=20, hold=3)
