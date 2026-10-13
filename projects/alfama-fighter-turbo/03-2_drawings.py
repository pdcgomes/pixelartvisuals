"""3.2 Drawings per character: how many separate drawings one fighter takes at the density of Street
Fighter II Turbo, of our plan, of Street Fighter Alpha, of Street Fighter III, and what Street Fighter
III really had. Five extruded bars on one scale up to 1,200, so the plan's 155 sits beside SF3's 700 to
1,200. Animated: the bars rise in turn and their values count up, then the chart holds.

Numbers and sources (alfamafighterturbo at 74e2f64):
- Turbo-like 121, Alpha-like 183, SF3-like 280: docs/research/street-fighter-art.md, section 8.1, the
  "Total drawings" row. They are the research agent's estimates ("Everything in this section is my
  judgement"): our move list drawn at each game's density, new drawings after reuse.
- Ours 155: the budget, "fluid where it shows", in docs/plans/2026-10-04-alfama-fighter-turbo-design.md
  (O Fadista, "Budget") and docs/studio/animation-guide.md, section 2 (155 per fighter).
- Real SF3 700 to 1,200: docs/research/street-fighter-art.md, sections 1 and 4.1 (EGM, March 1997, as
  cited by Wikipedia; section 9 says the scan couldn't confirm it).
- Built by 8 October, 43 to 93 a fighter (O Fadista 93): docs/plans/2026-10-08-fluidity-experiment.md,
  "For the roster's 600 or so drawings (O Fadista's 93, the others 43–83)".
"""

from pixelkit import ease_out, phase, stagger
from series import ART, export, frame

ESTIMATE, SF3 = "purple", "orange"
BARS = [
    # label, second line, value (or (low, high)), colour
    ("TURBO-LIKE", "ESTIMATE", 121, ESTIMATE),
    ("OURS", "THE PLAN", 155, ART),
    ("ALPHA-LIKE", "ESTIMATE", 183, ESTIMATE),
    ("SF3-LIKE", "ESTIMATE", 280, ESTIMATE),
    ("REAL SF3", "MAGAZINE, 1997", (700, 1200), SF3),
]
YMAX = 1200
TICKS = (0, 400, 800, 1200)


def draw(c, t):
    top, bottom = frame(c, 3, 2, "DRAWINGS PER CHARACTER",
                        "ESTIMATES: THE RESEARCH AGENT'S, OUR MOVE LIST AT EACH GAME'S DENSITY. "
                        "REAL SF3: EGM, MARCH 1997.")
    axis_y = bottom - 19
    plot_top = top + 13
    plot_h = axis_y - plot_top
    x0, x1 = 30, c.w - 6
    scale = plot_h / YMAX

    for v in TICKS:
        y = axis_y - round(v * scale)
        c.text(x0 - 4, y - 2, c.num(v), "dim", align="right")
        if v:
            c.dots(x0, y, x1 - x0, "line")
    c.hline(x0, axis_y, x1 - x0, "line")

    slot = (x1 - x0) // len(BARS)
    bar_w = 22
    for i, (name, sub, value, col) in enumerate(BARS):
        g = ease_out(stagger(t, i, len(BARS), start=0.05, end=0.8, overlap=0.35))
        x = x0 + i * slot + (slot - bar_w) // 2 - 3
        cx = x + bar_w // 2
        if isinstance(value, tuple):
            low, high = value
            h_hi = max(1, round(high * scale * g))
            h_lo = max(1, round(low * scale * g))
            c.bar3d(x, axis_y, bar_w, h_hi, f"{col}.dark", depth=4, stripes=3)
            c.bar3d(x, axis_y, bar_w, h_lo, col, depth=4)
            shown = f"{c.num(round(low * g))}–{c.num(round(high * g))}"
            c.text(cx + 2, axis_y - h_hi - 12, shown, "white", align="center")
            if g >= 1:
                c.text(x + bar_w + 11, axis_y - h_lo - 4, "700", "text")
        else:
            h = max(1, round(value * scale * g))
            c.bar3d(x, axis_y, bar_w, h, col, depth=4)
            c.text(cx + 2, axis_y - h - 12, str(round(value * g)), "white", align="center")
        c.text(cx, axis_y + 4, name, "white" if col == ART else "text", align="center")
        c.text(cx, axis_y + 11, sub, c.light(col), align="center")

    # The headline, over the empty top of the short bars.
    p = ease_out(phase(t, 0.05, 0.7))
    hx, hy = x0 + 6, plot_top + 2
    c.rect(hx - 2, hy - 2, 196, 46, "bg")
    w = c.text(hx, hy, str(round(155 * p)), "white", font="large", scale=3, shadow="dim")
    c.strip(hx, hy + 24, max(1, round(w * p)), 2, [ART])
    c.text(hx + w + 8, hy + 2, "NEW DRAWINGS A FIGHTER:", "white")
    c.text(hx + w + 8, hy + 9, "OUR PLAN, \"FLUID WHERE", "white")
    c.text(hx + w + 8, hy + 16, "IT SHOWS\"", "white")
    c.text(hx, hy + 31, "BUILT BY 8 OCTOBER: 43 TO 93 A FIGHTER", "text")
    c.text(hx, hy + 38, "STREET FIGHTER III: 700 TO 1,200", c.light(SF3))


if __name__ == "__main__":
    export(draw, __file__, preset="wide", seconds=2.6, fps=20, hold=3, poster=1.0)
