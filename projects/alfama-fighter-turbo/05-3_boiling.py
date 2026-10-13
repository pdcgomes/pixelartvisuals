"""5.3 More drawings, more boiling: O Fadista's stance and heavy punch at three densities (A, the game's
drawings; B, about twice as many; C, Metal Slug's density), and how much of each change between drawings is
redrawn rather than moved. In the stance every change redraws about the same 680 pixels, so twice the
drawings is twice the boiling a second. In the heavy punch, where the poses are far apart, each change
boils less as drawings are added, but a second it still rises.

Animated: the bars rise in turn, A to C, in both panels, their values counting up; then the rows under
them light. Holds.

Numbers, from docs/plans/2026-10-08-fluidity-experiment.md (alfamafighterturbo at 74e2f64), "The stance"
and "The heavy punch" tables, and "Measuring boiling":
- drawings: the stance 6, 12, 16; the heavy punch 6, 10, 15 (counting the stance's drawing that ends it);
- residual a change, in visible pixels redrawn per change of drawing: the stance 678, 681, 682; the heavy
  punch 1,296, 1,124, 986;
- residual a second, in pixels a second: the stance 4,694, 9,433, 12,592 (over its 52-step loop); the
  heavy punch 13,327, 19,275, 25,363 (over 35 steps, from the stance's last 4 into the move and back);
- the residual is what tools/boil.py counts: pixels whose colour visibly changes (more than 0.06 apart in
  Oklab) once each 6x6 block is matched to its best place within 8 px, both ways. O Fadista's figure is
  about 4,000 pixels.
"""

from pixelkit import ease_out, phase, stagger
from series import ART, export, frame

MOVES = [
    # title, subtitle, drawings, a change, a second, the line under it
    ("THE STANCE", "A BREATH: POSES CLOSE", [6, 12, 16], [678, 681, 682], [4694, 9433, 12592],
     "EVERY CHANGE ALTERS ABOUT 680 PX, SO MORE DRAWINGS BOIL MORE"),
    ("THE HEAVY PUNCH", "A SWING: POSES FAR APART", [6, 10, 15], [1296, 1124, 986], [13327, 19275, 25363],
     "EACH CHANGE ALTERS LESS AS DRAWINGS ARE ADDED, BUT A SECOND STILL MORE"),
]
NAMES = ["A", "B", "C"]
YMAX = 30000
RISE = (0.05, 0.75)
ROWS = (0.8, 0.9)


def draw(c, t):
    top, bottom = frame(c, 5, 3, "MORE DRAWINGS, MORE BOILING",
                        "A: THE GAME'S DRAWINGS · B: ABOUT TWICE · C: AIMED AT METAL SLUG'S. HIS FIGURE IS "
                        "ABOUT 4,000 PX.")
    colours = [c.series(i) for i in range(3)]
    rows_on = phase(t, *ROWS)
    for m, (title, sub, drawings, change, second, line) in enumerate(MOVES):
        p = c.panel(m * 161, top + 1, 159, bottom - top - 3, title, color=c.light(ART), sub=sub)
        c.text(p.x, p.y, "PIXELS CHANGED A SECOND", "white")
        grow = [ease_out(stagger(t, i, 3, start=RISE[0], end=RISE[1], overlap=0.3)) for i in range(3)]
        bars = c.bar_chart(p.x + 22, p.y + 19, p.w - 22, 52, second, colors=colours, ymax=YMAX,
                           grow=grow, ticks=3, xlabels=NAMES)
        y = p.y + 82
        for row, (label, values) in enumerate((("DRAWINGS", drawings), ("PX A CHANGE", change))):
            c.text(p.x, y + row * 8, label, "muted")
            for bar, v, col in zip(bars, values, colours):
                c.text(bar.cx + 6, y + row * 8, c.num(v), "white" if rows_on > row / 2 else "dim",
                       align="center")
        c.paragraph(p.x, y + 19, line, p.w, c.light(ART) if rows_on >= 1 else "text")


export(draw, __file__, seconds=3, fps=20, hold=4)
