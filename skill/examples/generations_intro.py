"""Animated intro for the generations chart: bars rise in turn, values count up, deltas pop in, then hold.

Same data and layout as generations.py. The final frame is also written as generations_intro-poster.png.
"""

from pathlib import Path

from pixelkit import animate, ease_out, lerp, phase, stagger

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
SOURCE = ("METAL SCORES: GEEKBENCH 7 AVERAGES, AS MACRUMORS LISTED THEM 18 SEP 2026. "
          "×M6: ITS BEST RESULT BEFORE RELEASE. CORES: THE MOST EACH CHIP SHIPS WITH. "
          "GB/S: MEMORY BANDWIDTH. NODE: THE PROCESS, IN NANOMETRES.")


def draw(c, t):
    c.header("APPLE SILICON GPU · M1 → M6", right="GEEKBENCH 7 METAL")
    c.footer(SOURCE)
    scores = [d[1] for d in DATA]
    colors = [c.series(i) for i in range(len(DATA))]
    grow = [ease_out(stagger(t, i, len(DATA), start=0.08, end=0.85, overlap=0.6)) for i in range(len(DATA))]
    bars = c.bar_chart(0, 20, 314, 121, scores, colors=colors, deltas=True, grow=grow,
                       fmt=lambda v: c.num(v) + ("×" if v == scores[-1] and FOOTNOTE else ""))

    count = ease_out(phase(t, 0.08, 0.9))
    multiple = lerp(1, scores[-1] / scores[0], count)
    per_gen = (scores[-1] / scores[0]) ** (1 / (len(DATA) - 1)) - 1
    c.rect(27, 19, 124, 46, "bg")
    hero_w = c.text(31, 22, f"{multiple:.1f}X", "white", font="large", scale=3, shadow="dim")
    c.strip(31, 46, max(1, round(hero_w * count)), 2, colors)
    for i, (line, col) in enumerate((("THE GPU", "white"), ("SCORE", "white"),
                                     (f"{DATA[0][0]} → {DATA[-1][0]}", "dim"))):
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


animate(draw, Path(__file__).with_suffix(".gif"), preset="standard", seconds=2.4, fps=20, hold=3)
