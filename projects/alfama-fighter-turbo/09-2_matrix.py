"""9.2 The balance lab's matchup matrix: the hard CPU playing itself with every pair of the eight
fighters you can pick, as a heatmap of the row fighter's share of wins, with each fighter's overall
share beside his row.

Moves: the rows fill in one after another, each fighter's overall bar growing as his row completes;
then a cursor visits the most lopsided matchups (8 in 10 or more) one by one while a readout under the
grid names each, and the picture holds on the last.

Numbers: docs/balance/results.json at alfamafighterturbo 74e2f64, "matchups" (the same as
docs/balance/report.md, section 4): the run of `node tools/balance.ts --before f09cb7e` at commit
e76362c, 10 October 2026, after the closing balance pass and the director's calls on it. 50 seeds
each way, so 100 matches a pair; a cell is the row fighter's share of the pair's matches (draws make
two pairs add up to 99%). Overall is the share against the other seven; Adamastor, the boss only the
CPU plays, is left out, as the report leaves him out of the overall.
"""

from pixelkit import ease_out, phase, stagger
from series import QA, export, frame

NAMES = ["O FADISTA", "D. AFONSO", "A VARINA", "A PADEIRA", "A AVÓ", "CAMÕES", "ZÉ POVINHO", "O CALCETEIRO"]
SHORT = ["FAD", "AFO", "VAR", "PAD", "AVÓ", "CAM", "ZÉ", "CAL"]
SHARE = [  # row fighter's % of the matches against the column fighter
    [None, 73, 91, 21, 83, 25, 100, 50],
    [27, None, 80, 6, 49, 6, 75, 2],
    [8, 20, None, 7, 27, 9, 92, 10],
    [79, 94, 93, None, 83, 43, 88, 55],
    [17, 51, 73, 17, None, 6, 37, 66],
    [75, 94, 91, 57, 94, None, 98, 52],
    [0, 25, 8, 12, 63, 2, None, 79],
    [50, 98, 90, 45, 33, 48, 21, None],
]
OVERALL = [63, 35, 25, 76, 38, 80, 27, 55]
BANDS = [(20, "blue"), (40, "blue.dark"), (60, "raised"), (80, "red.dark"), (101, "red")]
LEGEND = [("UNDER 20%", "blue"), ("20–39", "blue.dark"), ("40–59", "raised"), ("60–79", "red.dark"),
          ("80% AND UP", "red")]
LOPSIDED = [(i, j) for i in range(8) for j in range(8) if SHARE[i][j] is not None and SHARE[i][j] >= 80]
CW, CH, GAP = 17, 11, 1
FILL = (0.02, 0.42)
VISIT = (0.46, 0.96)


def band(v):
    return next(colour for limit, colour in BANDS if v < limit)


def draw(c, t):
    top, bottom = frame(c, 9, 2, "THE HARD CPU AGAINST ITSELF",
                        "THE BALANCE LAB'S RUN OF 10 OCT 2026, AFTER THE CLOSING BALANCE PASS. "
                        "THE BOSS, ONLY EVER THE CPU, LEFT OUT.")
    p = c.panel(0, top + 1, 320, bottom - top - 3, "WHO BEATS WHOM", color=c.light(QA),
                sub="ROW FIGHTER'S SHARE OF 100 MATCHES A PAIR", right="OVERALL", right_color="text")
    gx, gy = p.x + 54, p.y + 9
    for j, short in enumerate(SHORT):
        c.text(gx + j * (CW + GAP) + CW // 2 + 1, p.y + 1, short, "dim", align="center")

    rows = [ease_out(stagger(phase(t, *FILL), i, 8, overlap=0.3)) for i in range(8)]
    k = min(len(LOPSIDED) - 1, int(phase(t, *VISIT) * len(LOPSIDED))) if t >= VISIT[0] else None
    focus = LOPSIDED[k] if k is not None else None

    for i, name in enumerate(NAMES):
        y = gy + i * (CH + GAP)
        on_row = focus is not None and focus[0] == i
        c.text(p.x, y + 3, name, "white" if on_row else "text")
        shown = round(rows[i] * 8)
        for j in range(8):
            x = gx + j * (CW + GAP)
            v = SHARE[i][j]
            if v is None:
                c.rect(x, y, CW, CH, "panel")
                c.box(x, y, CW, CH, "line")
                continue
            if j >= shown:
                c.rect(x, y, CW, CH, "shadow")
                continue
            c.rect(x, y, CW, CH, band(v))
            c.text(x + CW // 2 + 1, y + 3, str(v), "white" if v >= 80 or v < 20 else "text", align="center")
        bx = gx + 8 * (CW + GAP) + 8
        bw = p.x2 - 18 - bx
        c.rect(bx, y + 3, bw, 5, "raised")
        c.rect(bx, y + 3, round(bw * OVERALL[i] / 100 * rows[i]), 5, band(OVERALL[i]))
        c.text(p.x2, y + 3, f"{round(OVERALL[i] * rows[i])}%", "white", align="right")

    if focus:
        i, j = focus
        x, y = gx + j * (CW + GAP), gy + i * (CH + GAP)
        c.box(x - 1, y - 1, CW + 2, CH + 2, "white")
        c.box(x - 2, y - 2, CW + 4, CH + 4, "shadow")

    ly = gy + 8 * (CH + GAP) + 3
    lx = p.x
    for label, colour in LEGEND:
        c.rect(lx, ly, 5, 5, colour)
        lx += 7 + c.text(lx + 7, ly, label, "dim") + 6
    ry = ly + 9
    if focus:
        i, j = focus
        c.spans(p.x, ry, [(NAMES[i], "white"), " BEATS ", (NAMES[j], "white"), f" {SHARE[i][j]}% OF THE TIME"], "text")
        c.text(p.x2, ry, f"{k + 1} OF {len(LOPSIDED)} AT 8 IN 10 OR MORE", "dim", align="right")
    else:
        c.text(p.x, ry, "THE LAB PLAYS EVERY PAIR, BOTH SIDES, 50 SEEDS EACH WAY", "text")


export(draw, __file__, preset="wide", seconds=9, fps=20, hold=3, poster=1.0)
