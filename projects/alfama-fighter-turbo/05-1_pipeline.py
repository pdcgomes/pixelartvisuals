"""5.1 From a generated sheet to a sprite in the game: the stations a fighter's drawing passes through,
and what each one checks or does. The model sheet, picked by the director from three designs, sits above
them: it's the reference every sheet is drawn from, the stance the drift check compares with, and the
picture the palette is fitted from.

Animated: a small figure travels along the lane under the stations. It starts big on a magenta ground with
a pink fringe, as the image generator draws it; the drift check lays the model sheet's outline over it; the
slicer takes the magenta away and shrinks it; the palette snaps its stray shades to the fighter's 16
colours; the boxes are drawn round it; the strip lays it out as frames; and it lands on the floor of a
small game screen. Each station lights while the figure is in it, and the three checks keep a tick once
passed. Holds.

Numbers, from alfamafighterturbo at 74e2f64:
- six figures on flat magenta (#FF00FF), figure 1 the stance, drawn about 400 px tall and shrunk about
  4 times to about 100 px: docs/plans/2026-10-04-alfama-fighter-turbo-design.md ("Art pipeline");
  art bible, rules on one page, 3;
- drift: shape at least 0.85, colour at most 0.09, size within 25% of the model sheet; the prop measured
  on every figure, 0.85 or more: art bible 10 (step 2) and 2.2;
- slicing: figures found by the empty columns between them, one scale factor, lined up on the feet and
  hips, palette-locked, written as an indexed PNG (index 0 transparent, 1 to 16 the palette) with its
  JSON frame data: tools/slice_sheet.py docstring; art bible 3.4;
- 16 colours fitted once from the model sheet by weighted k-means in Oklab, every later sheet locked to
  them: art bible 3.4;
- boxes suggested from the silhouettes, the hurt box and the reach box, attack boxes placed by hand on
  active frames: tools/boxes.py docstring; animation guide 9;
- in the game, held as palette indices, painted in a colour scheme and flipped as they're drawn:
  docs/plans/2026-10-09-performance-and-resources.md (Progress).
"""

from pixelkit import ease_in_out, phase
from series import ART, DIRECTOR, ENGINE, QA, TOOLS, export, frame

STATIONS = [
    # title, accent, is it a check, what it does
    ("GENERATE", ART, False, "SIX FIGURES ON FLAT MAGENTA, ABOUT 400 PX TALL. FIGURE 1 IS ALWAYS THE STANCE"),
    ("DRIFT", QA, True, "FIGURE 1 AGAINST THE MODEL SHEET: SHAPE, COLOUR AND SIZE CLOSE ENOUGH, OR DRAW AGAIN"),
    ("SLICE", TOOLS, False, "CUT AT THE GAPS, ALL SHRUNK TO ABOUT A QUARTER, LINED UP ON FEET AND HIPS"),
    ("PALETTE", TOOLS, True, "EVERY PIXEL SNAPPED TO HIS 16 COLOURS, PICKED ONCE FROM THE MODEL SHEET"),
    ("BOXES", QA, True, "SUGGESTED FROM THE OUTLINE: BLUE WHERE HE CAN BE HIT, RED WHERE HE HITS. SET BY HAND"),
    ("STRIP", TOOLS, False, "ONE NUMBER A PIXEL, SAYING WHICH OF HIS COLOURS, AND HOW LONG EACH FRAME SHOWS"),
    ("GAME", ENGINE, False, "KEPT AS NUMBERS, PAINTED IN HIS COLOURS AND FLIPPED AS HE'S DRAWN"),
]

# The figure: O Fadista in 8 x 12, facing right. K suit and hair, S skin, W shirt, R cape lining, G guitar.
FIGURE = [
    "..KKK...",
    "..KSSK..",
    "...SS...",
    ".KKWWK..",
    "RKKWKKS.",
    "RKKKK...",
    "RGKKK...",
    "GGGKK...",
    "GGKKKK..",
    ".RK..K..",
    ".RK..K..",
    ".KK..KK.",
]
# The same figure as sliced, before the palette: stray shades the generator drew (k, s).
STRAY = [
    "..KkK...",
    "..KSsK..",
    "...sS...",
    ".KkWWK..",
    "RKkWKkS.",
    "RkKKk...",
    "RGkKK...",
    "GGGKk...",
    "GGKkKK..",
    ".RK..k..",
    ".Rk..K..",
    ".kK..KK.",
]
COLOURS = {"K": "#1b1712", "S": "#cc823b", "W": "#e3dac5", "R": "#8a1a10", "G": "#e59843",
           "k": "#3a3328", "s": "#a86a3a"}
# A second drawing for the strip: the fist pulled back.
FIGURE2 = [row.replace("KS.", "K..") if i == 4 else row for i, row in enumerate(FIGURE)]
MAGENTA, FRINGE = "#ff00ff", "#c640b8"
PALETTE16 = ["#0b0708", "#160c0b", "#1b1712", "#3a0806", "#25221b", "#332c24", "#64110a", "#403a30",
             "#6c4427", "#835e3e", "#a67040", "#cc823b", "#b3a58f", "#e59843", "#f5b05d", "#e3dac5"]

# The timeline: the figure's stay at each station, and the hops between.
START, STAY, HOP = 0.04, 0.085, 0.042
TURNS = [(START + i * (STAY + HOP), START + i * (STAY + HOP) + STAY) for i in range(len(STATIONS))]


def draw(c, t):
    top, bottom = frame(c, 5, 1, "FROM A GENERATED SHEET TO A SPRITE",
                        "O FADISTA'S NUMBERS: ART BIBLE AND ANIMATION GUIDE.")
    at = next((i for i, (a, b) in enumerate(TURNS) if a <= t < b), None)
    passed = sum(1 for _, b in TURNS if t >= b)          # stations the figure has left

    w, gap = 43, 3
    xs = [1 + i * (w + gap) for i in range(len(STATIONS))]

    # The model sheet, above everything it feeds.
    band = c.node(1, top + 2, 318, 12, "MODEL SHEET", color=DIRECTOR)
    c.spans(band.x + 52, band.y + 4, [("PICKED FROM THREE DESIGNS", c.light(DIRECTOR)),
                                     " · FIXES LOOK, SIZE, COLOURS"], "dim")

    node_y = band.y2 + 6
    lane_y = node_y + 14
    lane_h = 28
    nodes = []
    for i, (title, accent, check, _) in enumerate(STATIONS):
        on = i == at
        done = check and t >= TURNS[i][1]
        n = c.node(xs[i], node_y, w, 12, title, color="white" if on else accent,
                   border="white" if on else "line", badge="✓" if done else None,
                   badge_color=c.light(ENGINE))
        nodes.append(n)
    for i in (0, 1, 3):                                   # what the model sheet feeds
        c.vdots(nodes[i].cx, band.y2 + 1, node_y - band.y2 - 2, c.light(DIRECTOR) if at == i else "muted")
    for a, b in zip(nodes, nodes[1:]):
        c.arrow(a.x2, a.cy, b.x - 1, a.cy, "dim")

    # The lane: a cell under each station.
    cells = []
    for i, n in enumerate(nodes):
        cell = (n.x + 2, lane_y, w - 4, lane_h)
        c.rect(*cell, "panel")
        c.box(*cell, "white" if i == at else "raised")
        cells.append(cell)
    floor = lane_y + lane_h - 3

    # Each station's rule, under its cell.
    for i, (_, accent, _, what) in enumerate(STATIONS):
        c.paragraph(xs[i] + 1, lane_y + lane_h + 3, what, w - 1, "white" if i == at else "text")

    # The game screen in the last cell: a sky, the HUD's two bars and the floor.
    gx, gy, gw, gh = cells[-1]
    c.rect(gx + 2, gy + 2, gw - 4, gh - 4, "#1d2340")
    c.rect(gx + 2, floor, gw - 4, gy + gh - 2 - floor, "#3b2f4c")
    c.rect(gx + 4, gy + 4, 12, 2, "gold")
    c.rect(gx + gw - 16, gy + 4, 12, 2, "gold")

    # The figure in each station's cell once it has got there, and on its way between them.
    def centre(i):
        x, _, cw, _ = cells[i]
        return x + cw // 2

    def big(cx, overlay=False):
        # As the generator draws it: big, on magenta, with a pink fringe where the outline blends in.
        x0, y0 = cx - 9, lane_y + 2
        c.rect(x0, y0, 19, lane_h - 4, MAGENTA)
        c.sprite(x0 + 1, y0, FIGURE, COLOURS, scale=2, outline=FRINGE)
        if overlay:                                       # the model sheet's stance laid over it
            for y, row in enumerate(FIGURE):
                for x, ch in enumerate(row):
                    edge = x == 0 or row[x - 1] == "." or x == len(row) - 1 or row[x + 1] == "."
                    if ch != "." and edge and (x + y) % 2 == 0:
                        c.rect(x0 + 1 + x * 2, y0 + y * 2, 2, 2, c.light(DIRECTOR))

    def small(cx, art=FIGURE, boxes=False):
        x0, y0 = cx - 4, floor - 12
        c.sprite(x0, y0, art, COLOURS)
        if boxes:
            c.box(x0 - 2, y0 - 1, 11, 14, "blue")         # where he can be hit
            c.box(x0 + 5, y0 + 3, 5, 3, "red")            # where his fist hits

    def state(i, cx, arriving=1.0):
        if i == 0:
            big(cx)
        elif i == 1:
            big(cx, overlay=True)
        elif i == 2:
            small(cx, STRAY)
            c.hline(cx - 7, floor, 14, c.light(TOOLS))    # lined up on the feet
        elif i == 3:
            lit = round(16 * arriving)
            x, y, _, _ = cells[3]
            for k, col in enumerate(PALETTE16):
                c.rect(x + 3 + k * 2, y + 2, 2, 3, col if k < lit else "raised")
            small(cx, STRAY if lit < 16 else FIGURE)
        elif i == 4:
            small(cx, boxes=True)
        elif i == 5:
            x, y, _, ch = cells[5]
            for k, art in enumerate((FIGURE, FIGURE2, FIGURE)):
                c.box(x + 3 + k * 11, y + 3, 10, ch - 6, "raised")
                c.sprite(x + 4 + k * 11, floor - 12, art, COLOURS)
        else:
            small(cx)

    for i in range(len(STATIONS)):
        if t >= TURNS[i][0]:
            state(i, centre(i), phase(t, TURNS[i][0], TURNS[i][0] + STAY * 0.6))
    if t < TURNS[0][0]:
        big(centre(0))
    elif at is None and passed < len(STATIONS):
        # On its way from the station it left to the next, as that station left it.
        k = ease_in_out(phase(t, TURNS[passed - 1][1], TURNS[passed][0]))
        cx = round(centre(passed - 1) + (centre(passed) - centre(passed - 1)) * k)
        last = passed - 1
        if last <= 1:
            big(cx)
        else:
            small(cx, STRAY if last == 2 else FIGURE, boxes=last == 4)


export(draw, __file__, seconds=7, fps=20, hold=3)
