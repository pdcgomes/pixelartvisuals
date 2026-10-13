"""7.2 What a combo is worth: the attract demo's combo, O Fadista's jump-in heavy kick, crouching medium
kick and Capa Negra (three turns of his cape, one hit a turn), scored hit by hit. Each hit is worth its
damage x 100 x the combo's multiplier, and the multiplier counts the moves linked so far, not the hits,
so the cape's three turns are one move: 1,300 + 1,600 + 3 x 1,500 = 7,400, where the same five hits
at x1 would be 3,600.

Animated intro, then a hold: the five hits land one after another; the count's digits heat from tram
yellow to orange as in the game, the multiplier tag ticks from x1 to x3, each hit's card lights with
its sum, the points bar grows a segment a hit and the total counts up to 7,400.

Numbers and sources (alfamafighterturbo at 74e2f64):
- Damage 13 (jumping heavy kick, jhk), 8 (crouching medium kick, cmk), 5 a turn (Capa Negra, capeSpin,
  three CAPE_TURNs): src/fighters/fadista.ts.
- Points = damage x 100 x min(8, moves linked): src/game/combos.ts, SCORING = { damage: 100,
  multiplier: 8 }; docs/plans/2026-10-09-feel-combos-design.md 1.3, its table (7,400; 3,600 today).
- The intro's combo is 5 hits, 3 moves, 36 damage, 7,400 points, with FIRST ATTACK 1,000:
  test/combos.test.ts ("the multiplier counts the moves linked, not the hits").
- FIRST ATTACK 1,000, COUNTER 500, REVERSAL 1,500: combos.ts CALLOUTS; front-end.md, "The feel".
- Heat: cream over tram yellow at 2 and 3 hits, orange from 4, warm white over red from 7; the count
  shows from the 2nd hit: front-end.md, "The feel"; feel-combos design 1.2.
"""

from pixelkit import ease_out, phase, stagger
from series import export, frame

HITS = [  # move, damage, moves linked after it
    ("JUMP-IN KICK", 13, 1),
    ("LOW KICK", 8, 2),
    ("CAPA NEGRA", 5, 3),
    ("CAPA NEGRA", 5, 3),
    ("CAPA NEGRA", 5, 3),
]
TOTAL = sum(d * 100 * m for _, d, m in HITS)
PLAIN = sum(d * 100 for _, d, _ in HITS)
assert (TOTAL, PLAIN) == (7400, 3600)


def heat(n: int) -> str:
    return "red" if n >= 7 else "orange" if n >= 4 else "yellow"


def draw(c, t):
    top, bottom = frame(c, 7, 2, "WHAT A COMBO IS WORTH",
                        "EACH HIT: ITS DAMAGE × 100 × THE MOVES LINKED SO FAR, AT MOST ×8.")
    land = [phase(t, 0.06 + i * 0.13, 0.12 + i * 0.13) for i in range(len(HITS))]
    done = sum(1 for p in land if p >= 1)

    top_row, rest = c.bounds._replace(y=top + 1, h=bottom - top - 3).cut_top(40, gap=2)
    left, right = top_row.cols([150, 168])

    # The count, as the game draws it from the second hit.
    count = c.panel(*left, "THE COUNT", color="yellow", sub="HEATS UP AS IT GROWS")
    if done >= 2:
        w = c.text(count.x, count.y + 2, str(done), heat(done), font="large", scale=2, shadow="dim")
        w += c.text(count.x + w + 3, count.y + 6, "HITS", "white", font="large") + 3
        c.tag(count.x + w + 4, count.y + 5, f"×{HITS[done - 1][2]}", "white", fill="shadow", border="yellow")
    else:
        c.text(count.x, count.y + 2, "SHOWN FROM", "dim")
        c.text(count.x, count.y + 9, "THE 2ND HIT", "dim")
    for i, (label, colour) in enumerate((("2-3 HITS", "yellow"), ("4-6", "orange"), ("7 AND UP", "red"))):
        lx, ly = count.x2 - 44, count.y - 1 + i * 8
        c.rect(lx, ly, 4, 5, colour)
        c.text(lx + 7, ly, label, "dim")

    # The total.
    pts = c.panel(*right, "THE COMBO'S POINTS", color="orange", sub="5 HITS · 3 MOVES")
    so_far = sum(d * 100 * m * min(1, land[i]) for i, (_, d, m) in enumerate(HITS))
    so_far = int(round(so_far / 100) * 100)
    c.text(pts.x, pts.y + 2, c.num(so_far), "white", font="large", scale=2, shadow="dim")
    c.text(pts.x2 - 1, pts.y + 1, "THE SAME HITS AT ×1", "dim", align="right")
    c.text(pts.x2 - 1, pts.y + 9, c.num(PLAIN), "text", align="right", font="large")

    # The hits.
    cards_row, bars = rest.cut_top(50, gap=2)
    for i, (rect, (move, dmg, links)) in enumerate(zip(cards_row.cols(len(HITS)), HITS)):
        on = land[i] >= 1
        accent = heat(i + 1) if i else "white"
        card = c.panel(*rect, f"HIT {i + 1}", color=accent if on else "dim", border="line")
        c.text(card.x, card.y, move, "white" if on else "dim")
        c.text(card.x, card.y + 8, f"DAMAGE {dmg}", "text" if on else "dim")
        c.text(card.x, card.y + 15, f"MOVES ×{links}", c.light("yellow") if on else "dim")
        c.text(card.x, card.y + 24, c.num(dmg * 100 * links), "white" if on else "raised", font="large")
    # The cape's three turns are one move.
    caps = cards_row.cols(len(HITS))[2:]
    bx0, bx1 = caps[0].x + 4, caps[-1].x2 - 5
    by = cards_row.y2 + 2
    c.hline(bx0, by, bx1 - bx0 + 1, "orange")
    c.vline(bx0, by - 2, 2, "orange")
    c.vline(bx1, by - 2, 2, "orange")
    c.text((bx0 + bx1) // 2, by + 3, "THREE TURNS OF THE CAPE, ONE MOVE", "orange", align="center")

    # The points, a segment a hit, against the same hits at x1.
    bars = c.panel(*bars._replace(y=by + 11, h=bars.y2 - by - 11), "THE SCORE", color="white",
                   sub="WITH THE MULTIPLIER, AND WITHOUT")
    scale = (bars.w - 40) / TOTAL
    x = bars.x
    for i, (_, d, m) in enumerate(HITS):
        seg = round(d * 100 * m * scale)
        grow = round(seg * ease_out(land[i]))
        if grow:
            c.rect(x, bars.y, grow, 6, heat(i + 1) if i else "white")
            c.vline(x, bars.y, 6, "bg")
        x += seg
    if done == len(HITS):
        c.text(bars.x2 - 1, bars.y, c.num(TOTAL), "white", align="right")
    x = bars.x
    for i, (_, d, _m) in enumerate(HITS):
        seg = round(d * 100 * scale)
        if land[i] >= 1:
            c.rect(x, bars.y + 10, seg, 6, "raised")
            c.vline(x, bars.y + 10, 6, "bg")
        x += seg
    if done == len(HITS):
        c.text(bars.x2 - 1, bars.y + 10, c.num(PLAIN), "dim", align="right")
    if t > 0.76:
        c.text(bars.x, bars.y + 20, "AND FIRST ATTACK, THE ROUND'S FIRST BLOW, PAYS 1,000 MORE: 8,400 ON THE SCORE",
               "yellow")


export(draw, __file__, preset="wide", seconds=5, fps=20, hold=3)
