"""Part-to-whole on a square: a 10x10 waffle (one tile = 1%), group totals beside their rows, context row.

The DGX Spark's unified memory, from its system monitor on 7 Oct 2026. Cache is reclaimable, so
"in use" is GPU + apps.
"""

from pathlib import Path

from pixelkit import Canvas, Rect

TITLE = "WHERE 122G GOES"
TOTAL = 121.7
PARTS = [("GPU", 20.8, "lime"), ("APPS", 76.8, "orange"), ("CACHE", 19.2, "sky"), ("FREE", 4.9, "raised")]
IN_USE = ("GPU", "APPS")
SWAP, SWAP_TOTAL = 9.2, 16.0
CORES = 20
UPTIME = ("31D", "17H 32M")
NOTE = "× CACHE IS RECLAIMABLE, SO IT COUNTS AS AVAILABLE."
SOURCE = "NUMBERS FROM THE SPARK'S SYSTEM MONITOR, 7 OCT 2026."
COLS, CELL, GAP = 10, 12, 2

c = Canvas(preset="square")
bottom = c.footer([NOTE, SOURCE])
top = c.header("DGX SPARK", sub="UNIFIED MEMORY")

tw = c.text(4, top + 5, TITLE, "white", font="large", scale=2, shadow="line")
c.stacked(4, top + 22, tw, 2, [(g, col) for _, g, col in PARTS], total=TOTAL)
c.text(c.w - 4, top + 6, "ONE POOL FOR", "dim", align="right")
c.text(c.w - 4, top + 13, "THE GPU AND CPU", "dim", align="right")

side = COLS * (CELL + GAP) - GAP
main, row = Rect(0, top + 26, c.w, bottom - 1 - (top + 26)).cut_top(side + 16, gap=1)
m = c.panel(*main, "MEMORY MAP", color="white", sub="1 SQUARE = 1%", right=f"{TOTAL}G TOTAL")
counts = c.waffle(m.x, m.y, [(g, col) for _, g, col in PARTS], cols=COLS, rows=COLS, cell=CELL, gap=GAP)

# Each group sits beside its rows of tiles, so the in-use tiles must fill whole rows.
info = Rect(m.x + side + 8, m.y, m.x2 - (m.x + side + 8), side)
used_rows = sum(n for (name, _, _), n in zip(PARTS, counts) if name in IN_USE) // COLS
use_band, free_band = info.cut_top(used_rows * (CELL + GAP) - GAP, gap=2)
used = sum(g for name, g, _ in PARTS if name in IN_USE)
pct_x = info.x + 55


def entry(y, name, g, col):
    c.tile(info.x, y + 1, 5, col)
    c.text(info.x + 8, y + 1, name, "text")
    c.text(pct_x, y + 1, f"{g / TOTAL:.0%}", "dim", align="right")
    vw = c.text(info.x2, y, f"{g:.1f}G", "white", font="large", align="right")
    c.dots(pct_x + 3, y + 5, info.x2 - vw - pct_x - 6, "line")


bx = m.x + side + 3
for band in (use_band, free_band):
    c.vline(bx, band.y, band.h, "line")
    c.hline(bx - 2, band.y, 2, "line")
    c.hline(bx - 2, band.y2 - 1, 2, "line")
    c.hline(bx + 1, band.cy, 2, "line")

y = use_band.y + (use_band.h - 58) // 2
c.spans(info.x, y, [("IN USE", "white"), f" · {used / TOTAL:.0%}"])
c.text(info.x, y + 9, f"{used:.1f}G", "white", font="large", scale=3, shadow="dim")
for k, (name, g, col) in enumerate(p for p in PARTS if p[0] in IN_USE):
    entry(y + 40 + k * 11, name, g, col)

avail = TOTAL - used
y = free_band.y + (free_band.h - 25) // 2
c.spans(info.x, y, [("AVAILABLE× ", "white"), (f"{avail:.1f}G", "white"), f" · {avail / TOTAL:.0%}"])
for k, (name, g, col) in enumerate(p for p in PARTS if p[0] not in IN_USE):
    entry(y + 8 + k * 10, name, g, col)

swap_r, cpu_r, up_r = row.cols(3, gap=1)
s = c.panel(*swap_r, "SWAP", color="violet")
vw = c.text(s.x, s.y + 4, f"{SWAP:.1f}G", "white", font="large")
c.text(s.x + vw + 4, s.y + 6, f"OF {SWAP_TOTAL:.1f}G", "dim")
c.meter(s.x, s.y + 16, s.w, 5, SWAP / SWAP_TOTAL, "violet")

p = c.panel(*cpu_r, "CPU", color="cyan", sub=f"{CORES} CORES")
c.chip(p.cx - 18, p.y + (p.h - 20) // 2, 37, 20, "ARM", "cyan", cores=CORES)

u = c.panel(*up_r, "UPTIME", color="gold")
c.icon(u.x, u.y + 5, "clock", "gold", scale=2)
c.text(u.x + 20, u.y + 4, UPTIME[0], "white", font="large")
c.text(u.x + 20, u.y + 14, UPTIME[1], "text")

c.save(Path(__file__).with_suffix(".png"))
