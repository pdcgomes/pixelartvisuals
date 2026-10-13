"""3.1 The arcade's route across Lisbon: the ten stages pinned on a map of the city, each numbered in
the order the single-player arcade visits them, with the list of stops and who waits at each beside
it. Animated: a tram travels the dashed route stop to stop in the arcade's order, each stop's tile
filling and its row in the list lighting as it arrives, from the Bairro Alto to the bridge and then
Santa Catarina for the boss; the whole route stays drawn throughout, then the last frame holds.

Numbers and sources (alfamafighterturbo at 74e2f64):
- The order: ROUTE in src/game/screens/run.ts (bairro, cais, comercio, alfama, castelo, rossio,
  chiado, belem), then BRIDGE (ponte), then BOSS (adamastor at catarina); bouts() leaves out the
  player's own home, so a run is 9 fights (the map screen's STAGE 1 OF 9, art/trailer/select-map.gif).
- Why that order: run.ts's comment and docs/studio/front-end.md, "The arcade": from the gentlest CPU
  to the fiercest (in CPU-against-CPU matches A Avó and A Varina lose the most, Camões and A Padeira
  win every one); decided by Pedro on 8 October (docs/studio/decisions.md, "The arcade's run is a
  fixed tour of the city along the tram 28").
- Each home's fighter and the pins' places: HOMES, BRIDGE and CATARINA in src/game/screens/lisbon.ts,
  on the game's 384x216 map of Lisbon, scaled here (wider apart vertically than the game's map) and
  not to scale with the real city. The river and the bridge are drawn after the game's map.
"""

from pixelkit import ease_in_out
from series import export, frame

# (place, who waits there, x and y on the game's 384x216 map, from lisbon.ts)
STOPS = [
    ("BAIRRO ALTO", "A AVÓ", 130, 70),
    ("CAIS DO SODRÉ", "A VARINA", 140, 124),
    ("PRAÇA DO COMÉRCIO", "ZÉ POVINHO", 212, 124),
    ("ALFAMA", "O FADISTA", 318, 104),
    ("CASTELO", "D. AFONSO", 290, 30),
    ("ROSSIO", "O CALCETEIRO", 202, 52),
    ("CHIADO", "CAMÕES", 172, 90),
    ("BELÉM", "A PADEIRA", 34, 108),
    ("PONTE 25 DE ABRIL", "YOUR DOUBLE", 90, 122),
    ("SANTA CATARINA", "ADAMASTOR", 104, 98),
]
BRIDGE, BOSS = 8, 9
MAP_W = 178
TRAM = ["....p......", ".yyyyyyyyy.", "ywwywwywwyy", "yyyyyyyyyyy", ".kk.....kk."]
TRAVEL, STAY, FIRST = 0.42, 0.5, 0.6          # seconds a leg, a stop, and before the tram leaves
SECONDS = FIRST + (len(STOPS) - 1) * (TRAVEL + STAY) + STAY


def to_map(x, y, top):
    return round(5 + x * 0.44), round(top + 6 + (y - 20) * 0.92)


def where(sec, pts):
    """The stop the tram has reached (or is leaving), and its position."""
    if sec < FIRST:
        return 0, pts[0]
    k = (sec - FIRST) / (TRAVEL + STAY)
    i = min(int(k), len(pts) - 2)
    p = min(1.0, (k - i) * (TRAVEL + STAY) / TRAVEL)
    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
    e = ease_in_out(p)
    reached = i + 1 if p >= 1 else i
    return reached, (round(x0 + (x1 - x0) * e), round(y0 + (y1 - y0) * e))


def dashed(c, a, b, color, step=3):
    (x0, y0), (x1, y1) = a, b
    n = max(1, max(abs(x1 - x0), abs(y1 - y0)))
    for k in range(0, n + 1):
        if k % step != 2:
            c.px(round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n), color)


def city(c, top, bottom):
    c.claim(c.bounds._replace(x=0, y=top, w=MAP_W + 2, h=bottom - top - 1), "map")
    c.rect(0, top, MAP_W + 2, bottom - top - 1, "#1c2a24")
    # The city's roofs, a sparse texture over the land; the castle hill a shade lighter.
    c.pattern(0, top, MAP_W + 2, bottom - top - 1, "#243429", kind="grain")
    c.polygon([(118, top + 4), (MAP_W + 1, top + 1), (MAP_W + 1, top + 34), (146, top + 32), (120, top + 22)],
              fill="#24362c")
    c.pattern(118, top + 1, MAP_W - 116, 33, "#2e4236", kind="grain")
    shore = [(0, top + 104), (40, top + 105), (66, top + 108), (112, top + 108), (150, top + 116),
             (MAP_W + 1, top + 124), (MAP_W + 1, bottom - 2), (0, bottom - 2)]
    c.polygon(shore, fill="blue.dark")
    for y in range(top + 114, bottom - 3, 5):
        for x in range((y * 7) % 13, MAP_W, 13):
            c.hline(x, y, 3, "#0a7aa8")
    c.text(150, bottom - 10, "TEJO", "blue.light", check=False)


def bridge(c, bx, by, bottom):
    """The Ponte 25 de Abril on the river below its stop, drawn side on as a symbol."""
    deck = by + 18
    x0, x1 = bx - 30, bx + 16
    t0, t1 = bx - 20, bx + 6
    for tx in (t0, t1):
        c.rect(tx, deck - 11, 2, 14, "red")
    for (a, ay), (b, byy), sag in (((x0, deck), (t0, deck - 11), 0), ((t0 + 1, deck - 11), (t1, deck - 11), 9),
                                   ((t1 + 1, deck - 11), (x1, deck), 0)):
        n = b - a
        for k in range(n + 1):
            p = k / n
            y = ay + (byy - ay) * p + sag * 4 * p * (1 - p) if sag else ay + (byy - ay) * (p ** 2 if a == x0 else
                                                                                   1 - (1 - p) ** 2)
            c.px(a + k, round(y), "red.light")
    c.hline(x0, deck, x1 - x0 + 1, "red")
    c.hline(x0, deck + 1, x1 - x0 + 1, "red.dark")


def draw(c, t):
    top, bottom = frame(c, 3, 1, "THE ARCADE, A TRAM RIDE ACROSS LISBON",
                        "PLACES AS ON THE GAME'S MAP OF LISBON, NOT TO SCALE.")
    sec = t * SECONDS
    pts = [to_map(x, y, top) for *_, x, y in STOPS]
    city(c, top, bottom)
    bridge(c, *pts[BRIDGE], bottom)
    reached, (tx, ty) = where(sec, pts)

    for i in range(len(pts) - 1):
        dashed(c, pts[i], pts[i + 1], "yellow" if i < reached else "dim")
    for i, (x, y) in enumerate(pts):
        done = i <= reached
        fill = ("red" if i == BOSS else "yellow") if done else "panel"
        c.rect(x - 2, y - 2, 5, 5, "shadow")
        c.rect(x - 1, y - 1, 3, 3, fill)
        c.box(x - 2, y - 2, 5, 5, "white" if i == reached else "text")
        label = str(i + 1)
        lx = x + 4 if i not in (BRIDGE, 1) else x - 3 - c.measure(label)
        c.text(lx, y - 2, label, "white" if done else "muted", outline="shadow", check=False)
    c.sprite(tx - 5, ty - 9, TRAM, {"y": "yellow", "w": "#fff3c4", "k": "shadow", "p": "muted"}, outline="shadow")

    list_x = MAP_W + 3
    stops = c.panel(list_x, top + 1, c.w - list_x, 103, "THE RUN", color="yellow", sub="IN ORDER")
    for i, (place, who, *_) in enumerate(STOPS):
        y = stops.y + 2 + i * 9
        on = i == reached
        done = i <= reached
        c.text(stops.x + 7, y, str(i + 1), "white" if done else "dim", align="right")
        c.text(stops.x + 10, y, place, "white" if on else "text" if done else "dim")
        c.text(stops.x + stops.w, y, who, ("red.light" if i == BOSS else "yellow") if done else "dim",
               align="right")
    why = c.panel(list_x, stops.y2 + 4, c.w - list_x, bottom - stops.y2 - 6, "WHY THIS ORDER", color="text")
    y = c.paragraph(why.x, why.y, "THE GENTLEST CPU FIRST, THE FIERCEST LAST.", why.w, "text")
    c.paragraph(why.x, y + 1, "YOUR OWN HOME IS SKIPPED: 9 FIGHTS.", why.w, "dim")


if __name__ == "__main__":
    export(draw, __file__, preset="wide", seconds=SECONDS, fps=20, hold=3, poster=1.0)
