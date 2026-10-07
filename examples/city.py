"""An isometric city builder in the mid-90s style: a city on a slab of terrain with a bay and hills,
residential, commercial and industrial zones, roads with traffic, a smoking power plant, the tool bar,
an RCI demand meter, a news ticker and a blinking low-funds warning. Everything is made up."""

import random
from functools import lru_cache
from pathlib import Path

from pixelkit import Canvas, animate, blink, iso_xy

MAP = ["~~~~~TT..hhhhh",
       "~~~~TT...hhhhh",
       "~~~T..RRR=hhhT",
       "~~...RRRR=hhTT",
       "~~.RRRRRR=IIII",
       "~~.RRRRRR=IIPP",
       "~..=========PP",
       "~..CCCC=CC=III",
       "~~.CCCC=CC=III",
       "~~.CCCC=CC=...",
       "~~~.RR.=.RRRR.",
       "~~~~RR.=.RRRR.",
       "~~~~~R.=.RRTT.",
       "~~~~~~.=..TTT."]
N, U = 14, 5
VIEW_X, VIEW_Y, VIEW_W, VIEW_H = 31, 20, 289, 160
OX, OY = 144, 14
BASE, LAND, HILL = 4, 3, 6
WATER, GRASS, HILLTOP, DIRT, DIRT_DARK = "#2a5ab0", "#4a9a3a", "#5aaa42", "#8a6a3a", "#6a4e2a"
ZONES = {"R": "#7ad07a", "C": "#7aaae8", "I": "#e8d05a"}
SEAM = "#3a8a2e"
TICKER = "PIXELBURG TIMES · MAYOR OPENS THE NEW BAY BRIDGE · RESIDENTS DEMAND MORE PARKS · POWER PLANT AT 92% · "
TOOLS = ["BULL", "ROAD", "RAIL", "POWR", "WATR", "TREE", "R", "C", "I", "POLC", "FIRE", "PARK", "INFO", "ROTA",
         "ZOOM", "MAP"]


def cell(u, v):
    return MAP[v][u] if 0 <= u < N and 0 <= v < N else "~"


def height(ch):
    return BASE if ch == "~" else BASE + LAND + (HILL if ch == "h" else 0)


def P(u, v, z=0):
    return iso_xy(OX, OY, u * U, v * U, z)


def tool_icon(c, x, y, name, sel):
    c.bevel(x, y, 13, 13, "#b8b8b8", light="white", dark="#606060", sunk=sel)
    cx, cy = x + 6, y + 6
    if name == "BULL":
        c.rect(cx - 4, cy - 1, 8, 4, "#e8b020")
        c.rect(cx - 2, cy - 3, 4, 2, "#e8b020")
        c.rect(cx - 4, cy + 3, 8, 1, "#303030")
    elif name == "ROAD":
        c.rect(cx - 4, cy - 4, 8, 9, "#606060")
        c.vdots(cx, cy - 3, 7, "white")
    elif name == "RAIL":
        for k in range(-3, 5, 2):
            c.hline(cx - 4, cy + k, 9, "#8a5a2a")
        c.vline(cx - 2, cy - 4, 9, "#404040")
        c.vline(cx + 2, cy - 4, 9, "#404040")
    elif name == "POWR":
        c.icon(cx - 3, cy - 3, "bolt", "#e8a000")
    elif name == "WATR":
        c.sprite(cx - 2, cy - 4, ["..#..", ".###.", "#####", "#####", ".###."], {"#": "#2a6ad0"})
    elif name in ("TREE", "PARK"):
        c.circle(cx + 0.5, cy - 0.5, 3.5, "#2a8a2a")
        c.vline(cx, cy + 2, 3, "#6a4428")
        if name == "PARK":
            c.hline(cx - 4, cy + 4, 9, "#60c060")
    elif name in ZONES:
        c.rect(cx - 4, cy - 4, 9, 9, ZONES[name])
        c.text(cx + 1, cy - 2, name, "#202020", align="center")
    elif name == "POLC":
        c.icon(cx - 3, cy - 3, "star", "#2a4ab0")
    elif name == "FIRE":
        c.sprite(cx - 3, cy - 4, ["..#....", ".##.#..", "#####..", "##++##.", "#++++#.", ".####.."],
                 {"#": "#e03a20", "+": "#ffd040"})
    elif name == "INFO":
        c.text(cx + 1, cy - 2, "?", "#2a4ab0", align="center")
    elif name == "ROTA":
        c.sprite(cx - 3, cy - 3, [".###...", "#...#..", "#...#.#", "#....##", ".#..###", "..##..."],
                 {"#": "#303030"})
    elif name == "ZOOM":
        c.circle(cx - 0.5, cy - 0.5, 3.5, "#303030")
        c.circle(cx - 0.5, cy - 0.5, 2.5, "#a8c8e8")
        c.line(cx + 2, cy + 2, cx + 4, cy + 4, "#303030")
    elif name == "MAP":
        c.rect(cx - 4, cy - 3, 9, 7, "#4a9a3a")
        c.rect(cx - 4, cy - 3, 3, 7, "#2a5ab0")


def building(c, rnd, u, v, ch, z):
    x0, y0 = u * U, v * U
    if ch == "R":
        if rnd.random() < 0.18:
            return
        tall = rnd.random() < 0.25
        h = rnd.randint(8, 12) if tall else rnd.randint(3, 5)
        look = (["#c87a5a", "#a85a3a", "#7a3e28"] if tall else
                [rnd.choice(["#c83a2a", "#8a4a2a", "#3a5a8a"]), "#e8dcc0", "#b8a888"])
        c.iso_block(OX, OY, x0 + 1, y0 + 1, 3, 3, h, z=z, top=look[0], left=look[1], right=look[2],
                    patterns={"left": ("slots", "#4a3a3a")} if tall else None)
    elif ch == "C":
        if rnd.random() < 0.12:
            return
        h = rnd.randint(9, 26)
        c.iso_block(OX, OY, x0 + 0.5, y0 + 0.5, 4, 4, h, z=z, top="#9ab0c8", left="#5a7aa8", right="#3a5a88",
                    edge="#c8d8f0", patterns={"left": ("hlines", "#aac8f0"), "right": ("hlines", "#6a8ab8")})
    elif ch == "I":
        h = rnd.randint(4, 7)
        c.iso_block(OX, OY, x0 + 0.5, y0 + 0.5, 4, 4, h, z=z, top="#a8a090", left="#c8a83a", right="#98802a",
                    patterns={"left": ("vlines", "#a88a2a")})
        if rnd.random() < 0.5:
            stack = c.iso_block(OX, OY, x0 + 3, y0 + 1, 1, 1, h + 7, z=z, top="#505050", left="#707070",
                                right="#484848")
            return stack.top(0.5, 0.5)
    elif ch in "Th" and (ch == "T" or rnd.random() < 0.3):
        for _ in range(2 if ch == "T" else 1):
            x, y = P(u + rnd.uniform(0.25, 0.75), v + rnd.uniform(0.25, 0.75), z)
            c.vline(x, y - 2, 2, "#5a3a20")
            c.sphere(x + 0.5, y - 4, 2.6, "#2a7a2a", shades=["#1a4a1a", "#2a7a2a", "#4a9a3a"])


@lru_cache(maxsize=1)
def city_base():
    """The static map, drawn once: terrain, zones, roads and buildings in back-to-front order."""
    c = Canvas(VIEW_W, VIEW_H, bg="#101018")
    rnd = random.Random(9)
    for k in range(40):
        c.px(rnd.randrange(VIEW_W), rnd.randrange(VIEW_H), "#2a2a3a")
    order = sorted(((u, v) for u in range(N) for v in range(N)), key=lambda p: (p[0] + p[1], p[0]))
    for u, v in order:
        ch = cell(u, v)
        h = height(ch)
        top = WATER if ch == "~" else HILLTOP if ch == "h" else ZONES.get(ch, GRASS)
        if ch in "=PI":
            top = "#808080" if ch == "=" else "#9a9a9a" if ch == "P" else ZONES["I"]
        c.iso_block(OX, OY, u * U, v * U, U, U, h, top=top, left=DIRT if ch != "~" else "#1a3a80",
                    right=DIRT_DARK if ch != "~" else "#14306a")
        if ch in ZONES and ch != "I":
            c.iso_tile(OX, OY, u * U + 0.5, v * U + 0.5, U - 1, U - 1, ZONES[ch], z=h, pattern="sparse",
                       outline=None)
        if ch == "=":
            along_u = cell(u - 1, v) == "=" or cell(u + 1, v) == "="
            along_v = cell(u, v - 1) == "=" or cell(u, v + 1) == "="
            if along_u:
                for k in range(0, U, 2):
                    c.px(*P(u + k / U, v + 0.5, h), "white")
            if along_v:
                for k in range(0, U, 2):
                    c.px(*P(u + 0.5, v + k / U, h), "white")
    stacks = []
    for u, v in order:
        ch = cell(u, v)
        top = building(c, rnd, u, v, ch, height(ch))
        if top:
            stacks.append(top)
    z = height("P")
    c.iso_block(OX, OY, 12 * U + 1, 5 * U + 1, 8, 8, 7, z=z, top="#8a8a8a", left="#a0a0a0", right="#707070",
                patterns={"left": ("grille", "#808080")})
    towers = []
    for du in (2, 6):
        tower = c.iso_block(OX, OY, 12 * U + du, 5 * U + 2, 2, 2, 20, z=z, top="#404040", left="#e8e8e8",
                            right="#b8b8b8", patterns={"left": ("hlines", "#d04040"), "right": ("hlines", "#a03030")})
        towers.append(tower.top(1, 1))
    return c.img, towers, stacks


def traffic(c, t):
    rnd = random.Random(4)
    z = height("=")
    for k in range(8):
        speed, off, way = rnd.choice((1, 2)), rnd.random(), rnd.choice((0, 1))
        s = (off + speed * t) % 1
        if k < 5:
            a = 3 + 10 * (s if way else 1 - s)
            x, y = P(a, 6.3 + 0.4 * way, z)
        else:
            a = 6 + 8 * (s if way else 1 - s)
            x, y = P(7.3 + 0.4 * way, a, z)
        c.rect(x, y - 1, 2, 1, rnd.choice(["#e03030", "#f0f0f0", "#3050d0", "#f0d020"]))


def toolbar(c, t):
    c.bevel(0, 19, 30, 161, "#a8a8a8", light="white", dark="#606060")
    for k, name in enumerate(TOOLS):
        tool_icon(c, 2 + (k % 2) * 13, 21 + (k // 2) * 14, name, name == "R")
    r = c.bevel(2, 135, 26, 43, "#202020", sunk=True, light="white", dark="#606060")
    mid = r.y + 22
    c.hline(r.x + 1, mid, r.w - 2, "#808080")
    wob = 1 if blink(t, 2) else 0
    for k, (name, dem) in enumerate((("R", 15 + wob), ("C", 6), ("I", -5 - wob))):
        bx = r.x + 2 + k * 8
        col = {"R": "#40d040", "C": "#4080f0", "I": "#f0d020"}[name]
        if dem > 0:
            c.rect(bx, mid - dem, 5, dem, col)
        else:
            c.rect(bx, mid + 1, 5, -dem, col)
        c.text(bx + 3, r.y2 - 6, name, col, align="center")


def menus(c, t):
    c.rect(0, 0, 320, 9, "#c8c8c8")
    c.hline(0, 8, 320, "#606060")
    x = 4
    for name in ("FILE", "SPEED", "OPTIONS", "DISASTERS", "WINDOWS", "NEWSPAPER", "HELP"):
        x += c.text(x, 2, name, "#101010") + 9
    c.text(316, 2, "PIXELBURG", "#2a2a8a", align="right")
    c.rect(0, 9, 320, 10, "#e8e0b8")
    c.hline(0, 18, 320, "#606060")
    c.text(4, 12, "JUN 14, 2027", "#101010")
    low = blink(t, 4)
    c.icon(58, 11, "warn", "red" if low else "#a08020")
    c.text(68, 12, "FUNDS $1,450", "red" if low else "#101010")
    c.text(126, 12, "POP 12,480", "#101010")
    sub = c.sub(160, 7, bg="#e8e0b8")
    tw = c.measure(TICKER)
    shift = round(t * tw)
    for k in range(2):
        sub.text(k * tw - shift, 1, TICKER, "#6a2a1a", check=False)
    c.rect(167, 10, 2, 8, "#a8a090")
    c.paste(sub, 172, 11)
    c.vline(172 + 160, 9, 9, "#606060")


def draw(c, t):
    view = c.sub(VIEW_W, VIEW_H)
    base, towers, stacks = city_base()
    view.paste(base, 0, 0)
    view.shimmer(0, 0, VIEW_W, VIEW_H, t, "#6a9ae0", n=60, seed=3, cycles=1, length=(2, 3), on=WATER)
    traffic(view, t)
    for k, (x, y) in enumerate(towers):
        view.particles(x - 1, y - 3, 3, 2, t, "smoke", n=7, seed=k, colors=["#e8e8e8", "#c8c8c8", "#a0a0a0"],
                       speed=22, wind=10, size=(1, 3))
    for k, (x, y) in enumerate(stacks):
        view.particles(x, y - 2, 1, 1, t, "smoke", n=4, seed=10 + k, colors=["#b0b0b0", "#888888"],
                       speed=14, wind=6, size=(1, 2))
    if blink(t, 2):
        view.iso_tile(OX, OY, 2 * U, 4 * U, U, U, None, z=height("R"), outline="white")
    c.paste(view, VIEW_X, VIEW_Y)
    menus(c, t)
    toolbar(c, t)


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=6, fps=8, seamless=True)
