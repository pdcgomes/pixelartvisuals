"""When Redlamp gets built: 1,050 commits in nine days as a day-by-hour heatmap, with hourly and daily
totals in the margins. Real data from the git log of Redlamp's main branch."""

from datetime import date
from pathlib import Path

from pixelkit import Canvas

COMMITS = {
    "2026-09-29": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 2, 0],
    "2026-09-30": [0, 0, 0, 0, 0, 1, 3, 1, 3, 14, 4, 4, 2, 2, 3, 15, 10, 6, 4, 5, 10, 10, 6, 3],
    "2026-10-01": [0, 0, 0, 0, 1, 0, 0, 2, 3, 2, 5, 8, 4, 2, 6, 6, 3, 6, 4, 0, 7, 6, 2, 3],
    "2026-10-02": [4, 0, 0, 0, 0, 0, 2, 1, 0, 2, 1, 2, 1, 0, 7, 5, 7, 3, 9, 4, 2, 8, 11, 4],
    "2026-10-03": [0, 0, 0, 0, 0, 0, 0, 3, 9, 11, 15, 13, 6, 4, 24, 19, 12, 5, 8, 15, 8, 9, 5, 5],
    "2026-10-04": [3, 6, 5, 1, 0, 0, 9, 20, 34, 17, 14, 13, 6, 0, 0, 0, 0, 0, 0, 1, 0, 4, 5, 4],
    "2026-10-05": [0, 0, 0, 0, 0, 0, 4, 12, 27, 11, 13, 9, 2, 9, 10, 10, 12, 6, 9, 6, 5, 5, 6, 3],
    "2026-10-06": [7, 5, 3, 4, 7, 1, 4, 7, 6, 7, 11, 6, 8, 6, 3, 4, 11, 9, 18, 3, 0, 15, 13, 9],
    "2026-10-07": [14, 2, 0, 0, 0, 4, 20, 14, 16, 14, 12, 12, 15, 6, 7, 7, 4, 4, 6, 0, 0, 1, 0, 0],
}
RAMP = ["raised", "#3a1418", "red.dark", "red", "red.light", "white"]
CELL, GAP = 8, 1

days = sorted(COMMITS)
rows = [COMMITS[d] for d in days]
hours = [sum(r[h] for r in rows) for h in range(24)]
totals = [sum(r) for r in rows]
total = sum(totals)
peak_day, peak_hour = max(((d, h) for d in range(len(days)) for h in range(24)), key=lambda k: rows[k[0]][k[1]])

c = Canvas(preset="wide")
top = c.header("WHEN REDLAMP GETS BUILT", right="COMMITS BY HOUR")
bottom = c.footer("GIT LOG OF REDLAMP'S MAIN BRANCH, 29 SEP TO 7 OCT 2026, IN LOCAL TIME (UTC+1).")

hero_w = c.text(4, top + 3, c.num(total), "white", font="large", scale=3, shadow="dim")
c.strip(4, top + 26, hero_w, 2, RAMP[1:])
c.text(hero_w + 12, top + 3, "COMMITS IN NINE DAYS", "white")
c.text(hero_w + 12, top + 10, f"{total / len(days):.0f} A DAY · {max(totals)} ON THE BUSIEST", "dim")
facts = [("NIGHT SHIFT", sum(hours[:6]), "00–06"), ("LUNCH DIP", hours[13], "13:00"),
         ("PEAK HOUR", max(hours), f"{hours.index(max(hours)):02d}:00")]
for i, (label, n, when) in enumerate(facts):
    fx = hero_w + 12 + i * 72
    c.text(fx, top + 19, f"{n}", c.light("red") if i == 2 else "white", font="large")
    c.text(fx + c.measure(f"{n}", "large") + 3, top + 19, label, "text")
    c.text(fx + c.measure(f"{n}", "large") + 3, top + 26, when, "dim")

panel = c.panel(0, top + 35, 320, bottom - top - 37, "BY DAY AND HOUR", color=c.light("red"),
                sub="EVERY SQUARE IS ONE HOUR")
hx = panel.x + 40
bars_y = panel.y + 1
peak = max(hours)
for h, n in enumerate(hours):
    bh = round(n / peak * 13)
    c.rect(hx + h * (CELL + GAP), bars_y + 13 - bh, CELL, bh, "red" if n != peak else "red.light")
grid_y = bars_y + 20
for h in range(0, 24, 6):
    c.text(hx + h * (CELL + GAP), bars_y + 14, f"{h:02d}", "dim")
grid = c.heatmap(hx, grid_y, rows, cell=CELL, gap=GAP, colors=RAMP)
for j, d in enumerate(days):
    y = grid_y + j * (CELL + GAP) + 2
    when = date.fromisoformat(d)
    c.text(panel.x, y, when.strftime("%a %d").upper(), "white" if j == peak_day else "dim")
    tx = grid.x2 + 6
    c.rect(tx, y, round(totals[j] / max(totals) * 34), 5, "red" if totals[j] != max(totals) else "red.light")
    c.text(panel.x2, y, str(totals[j]), "white", align="right")
px = hx + peak_hour * (CELL + GAP)
py = grid_y + peak_day * (CELL + GAP)
c.box(px - 1, py - 1, CELL + 2, CELL + 2, "white")

c.save(Path(__file__).with_suffix(".png"))
