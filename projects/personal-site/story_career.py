"""Personal site, the story's second chapter: the career as a game's world map. Lisbon and London are
two islands; a little Pedro walks from stop to stop, sails across in 2012, and ends at the castle.
The card on the right is each stop's quest: the role, the years, a highlight, the skill it unlocked."""

import math
from pathlib import Path

from pixelkit import Canvas, animate

# Each stop: where it sits on the map, the label beside it, and its card.
STOPS = [
    ((22, 146), "BANIF", "below", "red", "2003–05", "SOFTWARE ENGINEER",
     "STRAIGHT FROM UNIVERSITY, AND SOON LEADING DELIVERY OF A BANK'S HR AND PAYROLL PLATFORM.", "STAKEHOLDERS"),
    ((48, 134), "ONI", "right", "orange", "2005–06", "ENGINEER, CONSULTANT",
     "CRM AND BILLING FOR A TELCO. BROUGHT IN SOURCE CONTROL. NUMBER PORTABILITY.", "RELEASES"),
    ((26, 114), "PT", "left", "gold", "2006–07", "SOFTWARE ENGINEER",
     "ENTERPRISE MESSAGING, SMS AND A HEALTHCARE PLATFORM ON HL7.", "INTEGRATION"),
    ((66, 102), "SAPO", "below", "lime", "2007–12", "LEAD MOBILE ENGINEER",
     "BUILT THE IPHONE PROTOTYPE THAT TOOK SAPO NATIVE, AND CREATED MEO REMOTE.", "MOBILE"),
    ((120, 70), "EF", "below", "cyan", "2012–14", "SENIOR MOBILE ENGINEER",
     "A REAL-TIME CLASSROOM FOR TEACHERS AND STUDENTS ON IPADS, OVER RABBITMQ.", "REAL-TIME"),
    ((148, 80), "REUTERS", "below", "sky", "2014–16", "LEAD MOBILE ENGINEER",
     "COMMODITIES FOR EIKON, LIVE SPORTS, AND A VIDEO NEWS PRODUCT FROM IDEA TO LAUNCH.", "GREENFIELD"),
    ((172, 62), "PEAK", "below", "violet", "2016–18", "LEAD MOBILE ENGINEER",
     "RE-ARCHITECTED THE CORE APP BIT BY BIT, WITHOUT STOPPING DELIVERY.", "MIGRATIONS"),
    ((140, 44), "BLOOMBERG", "left", "orange", "2018–19", "SENIOR ENGINEER",
     "INSTANT BLOOMBERG: MOBILE FIRST, THEN THE BACKEND OF ENTERPRISE MESSAGING.", "BACKEND"),
    ((180, 30), "META", "below", "gold", "2019–NOW", "STAFF ENGINEER",
     "WHATSAPP MEDIA UPLOADS ACROSS 14 TEAMS AND BILLIONS OF MESSAGES. AUDIO FOR AR EFFECTS.", "PLATFORMS"),
]
CROSSING = 4
PLAYER = (["..hh..", ".hhhh.", "..ss..", ".bbbb.", "bbbbbb", "..bb..", ".b..b.", ".k..k."],
          ["..hh..", ".hhhh.", "..ss..", ".bbbb.", "bbbbbb", "..bb..", ".b.b..", ".k.k.."])
PLAYER_COLORS = {"h": "#3a2a20", "s": "#f0c8a0", "b": "sky", "k": "#202024"}
CASTLE = ["...g.........", "...gg........", "...#.........", "#.#.#...#.#.#", "#####...#####", "#####.#.#####",
          ".###########.", ".####...####.", ".####...####.", ".####...####."]
BOAT = ["...w...", "...ww..", "...www.", "...#...", "#######", ".#####."]
TOWER = ["..#..", ".###.", ".#w#.", ".###.", ".###.", ".#.#.", ".###.", ".#.#.", ".###.", ".###.", "#####"]
LISBON = [(2, 96), (40, 92), (92, 94), (98, 112), (90, 128), (100, 150), (80, 164), (30, 166), (2, 164)]
LONDON = [(104, 22), (150, 14), (204, 16), (204, 92), (170, 96), (134, 94), (106, 88), (112, 60), (100, 40)]
WALK, STAY = 0.45, 1.05


def ease(p):
    return p * p * (3 - 2 * p)


def timeline():
    """When the hero leaves and reaches each stop, in seconds; the crossing takes twice as long."""
    out, t = [], 0.0
    for i in range(len(STOPS)):
        walk = 0.0 if i == 0 else WALK * (2.4 if i == CROSSING else 1)
        out.append((t, t + walk))
        t += walk + STAY
    return out, t


TIMES, SECONDS = timeline()


def where(sec):
    """The stop the hero is at or heading to, how far along the walk, and the position."""
    for i in range(len(STOPS) - 1, -1, -1):
        leave, arrive = TIMES[i]
        if sec >= leave:
            break
    a = STOPS[max(0, i - 1)][0]
    b = STOPS[i][0]
    p = 1.0 if arrive == leave else min(1.0, (sec - leave) / (arrive - leave))
    k = ease(p)
    lift = -6 * math.sin(math.pi * p) if i == CROSSING else 0
    return i, p, (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k + lift)


def world(m, sec, t):
    m.rect(0, 0, m.w, m.h, "#12305a")
    for y in range(4, m.h, 7):
        for x in range((y * 5 + int(sec * 6)) % 12, m.w, 12):
            m.hline(x, y, 3, "#1e4a80")
    for shape, fill, rim in ((LISBON, "#c8a860", "#e8d090"), (LONDON, "#4a7a3a", "#6a9a50")):
        m.polygon(shape, fill=fill, outline=rim)
    m.polygon([(10, 150), (60, 152), (84, 160), (20, 162)], fill="#a08848")
    m.polygon([(120, 24), (190, 22), (196, 50), (150, 52), (118, 46)], fill="#3e6a30", pattern="checker")
    # Lisbon's red bridge over the river's mouth, and London's clock tower.
    m.hline(6, 128, 36, "#c8402a")
    for x in (14, 34):
        m.rect(x, 118, 2, 10, "#c8402a")
    for x0, x1 in ((6, 14), (16, 33), (36, 42)):
        mid = (x0 + x1) // 2
        m.line(x0, 127 if x0 == 6 else 119, mid, 126, "#e06a4a")
        m.line(mid, 126, x1, 119 if x1 != 42 else 127, "#e06a4a")
    m.sprite(190, 70, TOWER, {"#": "#c8b890", "w": "white"})
    m.text(80, 138, "LISBON", "#5a4420", align="center", check=False)
    m.text(200, 8, "LONDON", "#c8e0b0", align="right", check=False)

    for i in range(1, len(STOPS)):
        (x0, y0), (x1, y1) = STOPS[i - 1][0], STOPS[i][0]
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 4))
        for k in range(1, n):
            x, y = round(x0 + (x1 - x0) * k / n), round(y0 + (y1 - y0) * k / n)
            m.px(x, y, "white" if i == CROSSING else "#5a4420" if i < CROSSING else "#24401c")
    m.text(96, 88, "2012", "white", align="center", check=False)

    here, p, (hx, hy) = where(sec)
    for i, ((x, y), name, side, color, *_) in enumerate(STOPS):
        done = i < here or (i == here and p >= 1)
        if name == "META":
            m.sprite(x - 6, y - 9, CASTLE, {"#": "#d8d0c0" if done else "#9a9488", "g": color})
        else:
            m.circle(x + 0.5, y + 0.5, 3.5, color if done else "#000000", outline="white")
        lx, ly, align = {"below": (x, y + 6, "center"), "right": (x + 7, y - 2, "left"),
                         "left": (x - 6, y - 2, "right")}[side]
        m.text(lx, ly, name, "white" if i == here else "text", align=align, outline="#000000", check=False)

    if here == CROSSING and p < 1:
        m.sprite(round(hx) - 3, round(hy) - 2, BOAT, {"#": "#8a5a2a", "w": "white"})
    frame = int(sec * 6) % 2 if p < 1 else 0
    m.sprite(round(hx) - 3, round(hy) - 10, PLAYER[frame], PLAYER_COLORS)


def draw(c, t):
    sec = t * SECONDS
    top = c.header("PEDRO GOMES", sub="PDCGOMES", right="STORY · CHAPTER 2 OF 5")
    m = Canvas(206, c.h - top, theme=c.theme)
    world(m, sec, t)
    c.img.paste(m.img, (0, top))

    here, p, _ = where(sec)
    _, name, _, color, years, role, blurb, unlocked = STOPS[here]
    card = c.panel(208, top + 1, 112, 116, f"WORLD {here + 1} · {name}", color=color,
                   right="NOW" if years.endswith("NOW") else None, right_color="lime")
    c.text(card.x, card.y + 1, years, "white", font="large")
    c.text(card.x, card.y + 12, role, color)
    c.paragraph(card.x, card.y + 22, blurb, card.w, "text")
    if p >= 1:
        c.tag(card.x, card.y2 - 9, f"UNLOCKED: {unlocked}", "lime", fill="#000000")

    stats = c.panel(208, top + 119, 112, c.h - top - 121, "STATS", color="dim")
    c.kv(stats.x, stats.y + 1, stats.w, [("WORLDS", f"{here + 1} / {len(STOPS)}"), ("YEARS", "20+"),
                                         ("DESIGN INTERVIEWS", "150+")])


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=SECONDS, fps=10, hold=2.0,
            poster=0.62)
