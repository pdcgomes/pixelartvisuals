"""Generational comparison: hero multiple, striped bars with deltas, chip row, spec table.

Recreates the Apple Silicon GPU reference. Swap DATA for any "X across versions" story.
"""

from pathlib import Path

from pixelkit import Canvas

DATA = [
    # name, score, year, cores, node, bandwidth GB/s, what was new
    ("M1", 27277, 2020, 8, "5NM", 68, "UNIFIED/MEMORY"),
    ("M2", 40529, 2022, 10, "5NM", 100, "MORE/CORES"),
    ("M3", 46033, 2023, 10, "3NM", 100, "RAY/TRACING"),
    ("M4", 51818, 2024, 10, "3NM", 120, "DEBUTS/IN IPAD"),
    ("M5", 69563, 2025, 10, "3NM", 153, "NEURAL/ACCEL."),
    ("M6", 93217, 2026, 12, "2NM", 170, "+50%/GEOMETRY"),
]
FOOTNOTE = "M6"

c = Canvas(preset="standard")
c.header("APPLE SILICON GPU · M1 → M6", right="GEEKBENCH 7 METAL")
c.footer("METAL SCORES: GEEKBENCH 7 AVERAGES, AS MACRUMORS LISTED THEM 18 SEP 2026. "
         "×M6: ITS BEST RESULT BEFORE RELEASE. CORES: THE MOST EACH CHIP SHIPS WITH. "
         "GB/S: MEMORY BANDWIDTH. NODE: THE PROCESS, IN NANOMETRES.")

scores = [d[1] for d in DATA]
colors = [c.series(i) for i in range(len(DATA))]
bars = c.bar_chart(0, 20, 314, 121, scores, colors=colors, deltas=True,
                   fmt=lambda v: c.num(v) + ("×" if v == scores[-1] and FOOTNOTE else ""))

# Hero block sits over the top-left of the grid, so clear the dots behind it first.
multiple = scores[-1] / scores[0]
per_gen = multiple ** (1 / (len(DATA) - 1)) - 1
c.rect(27, 19, 124, 46, "bg")
hero_w = c.text(31, 22, f"{multiple:.1f}X", "white", font="large", scale=3, shadow="dim")
c.strip(31, 46, hero_w, 2, colors)
for i, (line, col) in enumerate((("THE GPU", "white"), ("SCORE", "white"), (f"{DATA[0][0]} → {DATA[-1][0]}", "dim"))):
    c.text(31 + hero_w + 8, 24 + i * 7, line, col)
c.text(31, 52, f"+{per_gen * 100:.0f}% A GENERATION ON AVERAGE", "text")
c.text(31, 59, f"{DATA[0][2]} → {DATA[-1][2]}, {len(DATA)} BASE CHIPS", "dim")

for bar, (name, _, year, cores, node, bw, new), col in zip(bars, DATA, colors):
    c.chip(bar.cx - 12, 144, 24, 20, name, col, cores=cores)
    for row, value in enumerate((year, cores, node, bw)):
        c.text(bar.cx, 168 + row * 7, str(value), "white", align="center")
    c.meter(bar.cx - 17, 195, 34, 2, bw / max(d[5] for d in DATA), col, rim=False)
    for k, line in enumerate(new.split("/")):
        c.text(bar.cx, 199 + k * 7, line, c.light(col), align="center")

for row, label in enumerate(("YEAR", "CORES", "NODE", "GB/S")):
    c.text(3, 168 + row * 7, label, "muted")
c.text(3, 199, "NEW", "muted")

c.save(Path(__file__).with_suffix(".png"))
