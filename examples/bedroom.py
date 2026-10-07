"""The sysop's bedroom, 1992: an isometric room at night with a beige PC, a 2400 bps modem, a 16-bit
console with a fighting game on the TV, posters, a lava lamp and a sleeping cat, beside the CRT up
close as it dials a BBS and starts a download."""

import math
import random
from pathlib import Path

from pixelkit import Canvas, animate, blink, reveal

OX, OY, W, D, HW = 91, 60, 56, 44, 46
SECONDS = 9
KEY = (255, 0, 255)
BEIGE = {"top": "#d8cca8", "left": "#b8ab88", "right": "#94886a"}
WOOD = {"top": "#8a5a36", "left": "#6a4428", "right": "#4e321e"}
DARK = {"top": "#4a4a56", "left": "#34343e", "right": "#24242c"}
TV = {"top": "#56565f", "left": "#3c3c46", "right": "#2a2a32"}
CONSOLE = {"top": "#c8c8d2", "left": "#a8a8b4", "right": "#88889a"}
RED = {"top": "#e0504a", "left": "#b03a36", "right": "#802824"}
QUILT = {"top": "#2a8a9a", "left": "#1e6a78", "right": "#154e5a"}
PILLOW = {"top": "#ece6d6", "left": "#cfc8b4", "right": "#aaa390"}
FLOOR, GRAIN = "#5a3a2c", "#4a2e22"
LEFT_WALL, RIGHT_WALL = "#3a3466", "#2c2752"
LEFT_STRIPE, RIGHT_STRIPE = "#433c74", "#332d5e"
PHOSPHOR = "#3cff6a"
RAINBOW = ["red", "orange", "gold", "lime", "cyan", "sky", "violet"]
CAT = ([".o.o......", ".ooo......", "oeooooooo.", "ooooooooo.", ".oooooooot"],
       [".o.o......", ".ooo......", "oeoooooooo", "oooooooooo", ".oooooooo."])
FIGHTER = (["rkk...", ".ss...", "wwww..", ".ww...", ".bw...", "w..w.."],
           ["rkk...", ".ss...", "wwwwws", ".ww...", ".bw...", "w..w.."])
BRAWLER = ([
    "...kkk......", "..kkkkk.....", ".rrrrrr.....", "r.sssse.....", "...ssss.....", "..wwwww.....",
    ".wwwwwwss...", ".wWwwww.s...", "..wwwww.....", "..bbbbb.....", "..ww.ww.....", ".ww...ww....",
    ".ww...ww....", "ww.....ww...", "ss.....ss..."], [
    "...kkk......", "..kkkkk.....", ".rrrrrr.....", "r.sssse.....", "...ssss.....", "..wwwww.....",
    ".wwwwwwwwss.", ".wWwww......", "..wwwww.....", "..bbbbb.....", "..ww.ww.....", ".ww...ww....",
    ".ww...ww....", "ww.....ww...", "ss.....ss..."])
LEDS = ["HS", "AA", "CD", "OH", "RD", "SD", "TR", "MR"]
FILE_BYTES, CPS = 65536, 236


def P(u, v, z=0):
    """Screen position of a point in the room: u along the right wall, v along the left, z up."""
    return round(OX + 2 * (u - v)), round(OY + u + v - z)


def box(c, u, v, w, d, h, z=0, look=BEIGE, **kw):
    x, y = P(u, v, z + h)
    return c.iso_box(x, y, w, d, h, top=look["top"], left=look["left"], right=look["right"], **kw)


def sheared(c, w, h, paint, x0, y0, *, down=True):
    """Paint a flat w×h picture and paste it with its top-left at (x0, y0), sheared 2:1 so it
    lies on a face running down-right (or up-right). Magenta is transparent."""
    sub = Canvas(w, h, theme=c.theme, bg="#ff00ff")
    paint(sub)
    for i in range(w):
        dy = i // 2 if down else -(i // 2)
        for j in range(h):
            px = sub.img.getpixel((i, j))
            if px != KEY:
                c.img.putpixel((x0 + i, y0 + dy + j), px)


def on_wall(c, w, h, paint, wall, a, z):
    """A flat picture on a wall: `a` is its left edge (u on the right wall, v on the left), z its top."""
    sheared(c, w, h, paint, *(P(a, 0, z) if wall == "right" else P(0, a, z)), down=wall == "right")


def glow(c, cx, cy, r, tints, *, squash=2.0):
    """Tint the listed colours inside an ellipse: solid in the middle, dithered towards the rim."""
    tints = {c.rgb(a): c.rgb(b) for a, b in tints.items()}
    for y in range(max(0, int(cy - r)), min(c.h, int(cy + r) + 1)):
        for x in range(max(0, int(cx - r * squash)), min(c.w, int(cx + r * squash) + 1)):
            d = ((x - cx) / squash) ** 2 + (y - cy) ** 2
            if d >= r * r or (d > r * r * 0.45 and (x + y) % 2):
                continue
            px = c.img.getpixel((x, y))
            if px in tints:
                c.img.putpixel((x, y), tints[px])


def modem_state(sec):
    """Which modem lights are on at `sec` seconds into the call."""
    rnd = random.Random(int(sec * 8))
    typing = 0.4 < sec < 1.6 or 5.4 < sec < 5.7
    on = {"MR": True, "TR": sec > 0.3, "OH": sec > 0.4, "HS": sec > 2.6, "CD": sec > 2.6, "AA": False,
          "SD": typing and rnd.random() < 0.7,
          "RD": sec > 2.6 and rnd.random() < (0.9 if sec > 6.4 else 0.5)}
    return on


# the room -----------------------------------------------------------------------------------------

def window(s):
    s.gradient(3, 2, 22, 18, ["#070a24", "#121a4c", "#222a66"])
    for k, (sx, sy) in enumerate([(5, 4), (9, 9), (12, 3), (6, 14), (16, 12), (21, 16), (8, 18)]):
        s.px(sx, sy, "white" if (k * 3) % 4 else "dim")
    s.circle(18.5, 6.5, 3, "#f4e6b8")
    s.circle(20, 5.5, 2.5, "#121a4c")
    s.box(3, 2, 22, 18, "#cbbf9a")
    s.vline(14, 2, 18, "#cbbf9a")
    s.hline(3, 11, 22, "#cbbf9a")
    for x0 in (0, 24):
        s.rect(x0, 0, 4, 22, "#b04a5a")
        s.vline(x0 + 1, 0, 22, "#8a3444")
    s.hline(0, 0, 28, "#6a4428")


def calendar(s):
    s.rect(0, 0, 9, 12, "#e8e2d0")
    s.rect(0, 0, 9, 3, "red")
    s.text(1, 5, "92", "#202024")


def cube_poster(s):
    s.rect(0, 0, 18, 15, "#d8d0b0")
    s.rect(1, 1, 16, 13, "#1a2a5a")
    colors = ["red", "white", "sky", "gold", "lime", "orange", "white", "red", "sky"]
    for k, col in enumerate(colors):
        s.rect(4 + (k % 3) * 4, 2 + (k // 3) * 4, 3, 3, col)


def wargames(s):
    s.rect(0, 0, 36, 21, "#4a5a4a")
    s.rect(1, 1, 34, 19, "#060a06")
    for k, line in enumerate(["SHALL WE", "PLAY A", "GAME?"]):
        s.text(18, 2 + k * 6, line, PHOSPHOR, align="center", check=False)


def lava_lamp(c, t, bx, by):
    c.rect(bx - 3, by - 4, 7, 4, "#8a8a9a")
    c.hline(bx - 3, by - 4, 7, "#b4b4c0")
    c.rect(bx - 2, by - 16, 5, 12, "#5a1030")
    for k, phase in enumerate((0.0, 0.45)):
        y = by - 6 - 7 * (0.5 + 0.5 * math.sin(2 * math.pi * (t * 2 + phase)))
        c.circle(bx + 0.5, y, 1.6 if k else 2.1, "#ff7a3a")
    c.rect(bx - 1, by - 18, 3, 2, "#8a8a9a")


def fight(s, t):
    """A 16-bit street fight on the TV: white gi throws fireballs, red gi takes them."""
    s.rect(0, 0, 22, 11, "#101014")
    s.gradient(1, 1, 20, 7, ["#f0a050", "#e06a5a", "#7a3a7a"])
    s.rect(1, 8, 20, 2, "#5a3a2a")
    s.hline(1, 8, 20, "#8a5a3a")
    beat = t * SECONDS / 1.5
    p = beat % 1
    hits = int(beat) + (1 if p > 0.7 else 0)
    s.rect(2, 2, 7, 1, "red")
    s.rect(2, 2, 6, 1, "gold")
    s.rect(13, 2, 7, 1, "red")
    hp = max(1, 7 - hits)
    s.rect(20 - hp, 2, hp, 1, "gold")
    s.sprite(3, 3, FIGHTER[1 if p < 0.25 else 0], {"k": "#202024", "s": "#f0c8a0", "w": "white", "b": "#202024",
                                                     "r": "red"})
    hit = 0.7 < p < 0.8
    b_colors = {"k": "gold", "s": "#f0c8a0", "w": "red", "b": "#202024", "r": "gold"}
    if hit:
        b_colors = {k: "white" for k in b_colors}
    s.sprite(13 + (1 if hit else 0), 3, FIGHTER[0], b_colors, flip=True)
    if 0.15 < p < 0.7:
        fx = 9 + round((p - 0.15) / 0.55 * 4)
        s.rect(fx, 4, 2, 2, "sky.light")
        s.px(fx + 1, 4, "white")
    s.px(1, 1, "#101014")
    s.px(20, 1, "#101014")


def tv_closeup(c, t, x, y):
    """The TV's picture at a size you can read, in a bezel like the TV's, above the room."""
    c.rect(x, y, 64, 34, TV["left"])
    c.hline(x, y, 64, TV["top"])
    c.hline(x, y + 33, 64, TV["right"])
    s = Canvas(60, 30, theme=c.theme)
    s.gradient(0, 0, 60, 26, ["#f0a050", "#e06a5a", "#7a3a7a", "#3a2050"])
    s.polygon([(0, 22), (8, 15), (15, 19), (24, 12), (33, 18), (42, 13), (52, 19), (59, 16), (59, 26), (0, 26)],
              fill="#2a1838")
    s.rect(0, 26, 60, 4, "#5a3a2a")
    s.hline(0, 26, 60, "#8a5a3a")
    beat = t * SECONDS / 1.5
    p = beat % 1
    hits = int(beat) + (1 if p > 0.7 else 0)
    s.rect(2, 1, 24, 2, "red")
    s.rect(2, 1, 22, 2, "gold")
    hp = max(3, 24 - hits * 3)
    s.rect(34, 1, 24, 2, "red")
    s.rect(58 - hp, 1, hp, 2, "gold")
    s.text(2, 4, "BYTE", "white", check=False)
    s.text(58, 4, "NULL", "white", align="right", check=False)
    s.text(30, 3, str(99 - int(t * SECONDS)), "gold", align="center", check=False)
    s.sprite(10, 12, BRAWLER[1 if p < 0.25 else 0],
             {"k": "#202024", "r": "red", "s": "#f0c8a0", "e": "#202024", "w": "white", "W": "#c8c8d2",
              "b": "#202024"})
    hit = 0.7 < p < 0.8
    b = {"k": "gold", "r": "gold", "s": "#f0c8a0", "e": "#202024", "w": "red", "W": "#a02828", "b": "#202024"}
    if hit:
        b = {k: "white" for k in b}
    s.sprite(38 + (2 if hit else 0), 12, BRAWLER[0], b, flip=True)
    if 0.15 < p < 0.7:
        fx = 22 + round((p - 0.15) / 0.55 * 16)
        s.circle(fx + 2, 17.5, 2.6, "sky")
        s.circle(fx + 2.5, 17.5, 1.5, "white")
        s.hline(fx - 3, 17, 3, "sky.dark")
    c.img.paste(s.img, (x + 2, y + 2))


def room(c, t, sec):
    c.rect(0, 0, c.w, c.h, "#0a0a16")
    floor = [P(0, 0), P(W, 0), P(W, D), P(0, D)]
    c.polygon(floor, fill=FLOOR)
    c.polygon(floor, fill=GRAIN, pattern="grain")
    c.polygon([P(0, D), P(W, D), P(W, D, -5), P(0, D, -5)], fill="#2e1c16")
    c.polygon([P(W, 0), P(W, D), P(W, D, -5), P(W, 0, -5)], fill="#22140f")
    c.line(*P(0, D), *P(W, D), "#7a5040")
    c.line(*P(W, 0), *P(W, D), "#6a4434")
    c.polygon([P(30, 18), P(50, 18), P(50, 38), P(30, 38)], fill="#2a6a7a")
    c.polygon([P(32, 20), P(48, 20), P(48, 36), P(32, 36)], fill="#d06a4a")
    c.polygon([P(34, 22), P(46, 22), P(46, 34), P(34, 34)], fill="#2a6a7a", pattern="checker")

    c.polygon([P(0, 0, HW), P(0, D, HW), P(0, D), P(0, 0)], fill=LEFT_WALL)
    c.polygon([P(0, 0, HW), P(W, 0, HW), P(W, 0), P(0, 0)], fill=RIGHT_WALL)
    for v in range(2, D, 4):
        c.line(*P(0, v, 3), *P(0, v, HW - 1), LEFT_STRIPE)
    for u in range(2, W, 4):
        c.line(*P(u, 0, 3), *P(u, 0, HW - 1), RIGHT_STRIPE)
    c.polygon([P(0, 0, 3), P(0, D, 3), P(0, D), P(0, 0)], fill="#26223f")
    c.polygon([P(0, 0, 3), P(W, 0, 3), P(W, 0), P(0, 0)], fill="#1e1a36")
    c.vline(*P(0, 0, HW), HW, "#1e1a38")
    c.polyline([P(0, D, HW), P(0, 0, HW), P(W, 0, HW)], "#6a62a0")
    c.vline(*P(0, D, HW), HW + 1, "#6a62a0")
    c.vline(*P(W, 0, HW), HW + 1, "#4e4880")

    on_wall(c, 28, 22, window, "left", 42, 40)
    on_wall(c, 9, 12, calendar, "left", 8, 40)
    on_wall(c, 18, 15, cube_poster, "right", 6, 45)
    on_wall(c, 36, 21, wargames, "right", 21, 46)

    glow(c, *P(21, 16), 13, {FLOOR: "#4c4a6e", GRAIN: "#3e3c5c", "#2a6a7a": "#3a8aa0", "#d06a4a": "#c07a8a"})
    glow(c, *P(49, 0, 37), 9, {RIGHT_WALL: "#4a2a52", RIGHT_STRIPE: "#56305a"}, squash=1.4)
    glow(c, *P(49, 15), 8, {FLOOR: "#6a4a50", GRAIN: "#5a3c44", "#2a6a7a": "#3a7a8a", "#d06a4a": "#e08a6a"})

    shelf = box(c, 0, 12, 4, 11, 30, look=WOOD)
    rnd = random.Random(5)
    for b0 in (3, 11, 19):
        c.hline(*shelf.right(0, b0 + 6), 0, "#000000")
        for v in range(1, 11):
            x, y = shelf.right(v, b0)
            h = 5 - rnd.randrange(2)
            c.rect(x - 1, y + (5 - h), 2, h, rnd.choice(["red", "gold", "sky", "lime", "violet", "orange", "white"]))
    box(c, 10, 0, 2, 12, 12, look=WOOD)
    ped = box(c, 32, 0, 10, 12, 12, look=WOOD)
    for b in (3, 8):
        c.line(*ped.left(3, b), *ped.left(7, b), "#c9a46a")
    box(c, 10, 0, 32, 12, 2, z=12, look=WOOD)
    case = box(c, 13, 1, 17, 9, 5, z=14)
    c.line(*case.left(9, 2), *case.left(15, 2), "#3a3628")
    c.px(*case.left(3, 2), "lime" if sec < 6.4 or blink(t, 20) else "red")
    mon = box(c, 15, 2, 12, 8, 11, z=19)
    c.polygon([mon.left(1.5, 1.5), mon.left(10.5, 1.5), mon.left(10.5, 8.5), mon.left(1.5, 8.5)],
              fill="#08122a", outline="#4a4636")
    rows = 1 if sec < 1.8 else 2 if sec < 2.6 else 3 if sec < 3.2 else 5
    for k in range(rows):
        color = PHOSPHOR if sec < 3.2 else RAINBOW[k % len(RAINBOW)]
        length = [6, 4, 7, 5, 3][k]
        c.line(*mon.left(2.5, 2.5 + k * 1.3), *mon.left(2.5 + length, 2.5 + k * 1.3), color)
    box(c, 15, 10, 11, 2, 1, z=14, patterns={"top": ("checker", "#8a7e60")})
    modem = box(c, 31, 2, 8, 6, 2, z=14, look=DARK)
    state = modem_state(sec)
    for k, name in enumerate(LEDS):
        c.px(*modem.left(0.5 + k, 0.5), "#ff4a3a" if state[name] else "#3a1414")
    box(c, 34, 8.5, 5, 3, 2, z=14, look=RED)
    box(c, 34, 8.5, 5, 1, 1, z=16, look={"top": "#a0302c", "left": "#802824", "right": "#601c1a"})

    box(c, 44, 0, 10, 3, 1, z=27, look=WOOD)
    lava_lamp(c, t, *P(49, 1.5, 28))
    box(c, 42, 0, 14, 10, 5, look=WOOD)
    tv = box(c, 43, 1, 12, 8, 15, z=5, look=TV)
    sheared(c, 22, 11, lambda s: fight(s, t), *tv.left(1, 1))
    for u in (9.5, 11):
        c.px(*tv.left(u, 13), "#8a8a96")
    console = box(c, 44, 13, 7, 5, 2, look=CONSOLE)
    for u in (1.5, 5.5):
        c.px(*console.top(u, 1.5), "#6a4aa0")
    box(c, 46.5, 14, 2, 1, 2, z=2, look=DARK)
    for (u, v), port in zip(((38, 21), (43, 23)), (45.5, 49.5)):
        c.line(*P(u + 1.5, v, 0), *P(port, 18, 1), "#202024")
        pad = box(c, u, v, 3, 2, 1, look=CONSOLE)
        for (pu, pv), col in zip(((2.2, 0.4), (2.7, 0.9), (2.2, 1.4), (1.7, 0.9)), ("red", "gold", "lime", "sky")):
            c.px(*pad.top(pu, pv), col)
        c.px(*pad.top(0.7, 1), "#202024")

    box(c, 21, 18, 1, 1, 8, look=DARK)
    box(c, 18, 15, 7, 7, 2, z=8, look=DARK)
    box(c, 18, 22, 7, 1, 10, z=10, look=DARK)

    box(c, 0, 26, 1, 17, 14, look=WOOD)
    box(c, 1, 26, 26, 17, 5, look=WOOD)
    box(c, 1, 26, 26, 17, 2, z=5, look=QUILT, patterns={"top": ("diagonal", "#d06a8a")})
    box(c, 2, 28, 5, 13, 2, z=7, look=PILLOW)
    cx, cy = P(15, 34, 7)
    cat = CAT[int(t * SECONDS * 2) % 2]
    c.sprite(cx - 5, cy - 5, cat, {"o": "#e08a3a", "e": "#6a3010", "t": "#e08a3a"})
    for k in range(3):
        p = (t * SECONDS / 1.5 + k / 3) % 1
        c.text(cx + 4 + k * 2 + round(p * 4), cy - 9 - round(p * 10), "Z", "white" if p < 0.6 else "dim", check=False)

    for u, v, col in ((33, 30, "#202024"), (37, 34, "sky")):
        c.polygon([P(u, v), P(u + 3, v), P(u + 3, v + 3), P(u, v + 3)], fill=col)
        c.px(*P(u + 1.5, v + 1), "white")
    box(c, 47, 31, 1, 1, 4, look=RED)
    tv_closeup(c, t, 140, 2)


# the screen and the modem -----------------------------------------------------------------------

def screen(s, sec):
    def cursor(x, y):
        if blink(sec, 2):
            s.rect(x + 1, y, 3, 5, PHOSPHOR)

    if sec < 3.2:
        s.text(2, 2, "PIXELTERM 1.2 · COM1", "dim")
        typed = reveal("ATDT 555-0142", max(0.0, min(1.0, (sec - 0.4) / 1.2))) if sec > 0.4 else ""
        w = s.text(2, 11, "> " + typed, PHOSPHOR)
        last = (2 + w, 11)
        if sec >= 1.8:
            last = (2 + s.text(2, 18, "RINGING...", "text"), 18)
        if sec >= 2.6:
            last = (2 + s.text(2, 25, "CONNECT 2400", "lime"), 25)
        cursor(*last)
        return

    if sec < 6.0:
        x = 2
        for k, ch in enumerate("PIXEL PIT"):
            if ch != " ":
                s.text(x, 2, ch, RAINBOW[k % len(RAINBOW)], font="large")
            x += s.measure(ch + "A", "large") - s.measure("A", "large")
        s.strip(2, 11, 94, 1, RAINBOW)
        s.text(2, 14, "BBS · NODE 1 · EST 1987", "dim")
        s.text(2, 22, "SYSOP: BYTE", "text")
        s.text(2, 29, "YOU ARE CALLER 1,337", "gold")
        menu = [("M", "MESSAGES (3 NEW)"), ("F", "FILES"), ("D", "DOOR GAMES"), ("G", "GOODBYE")]
        shown = int((sec - 4.0) / 0.2) + 1 if sec >= 4.0 else 0
        for k, (key, label) in enumerate(menu[:shown]):
            s.text(2, 39 + k * 7, f"[{key}]", "sky")
            s.text(16, 39 + k * 7, label, "white")
        if sec >= 5.2:
            w = s.text(2, 70, "COMMAND: " + ("F" if sec >= 5.6 else ""), "gold")
            cursor(2 + w, 70)
        return

    s.text(2, 2, "FILES · PIXEL ART", "gold")
    s.hline(2, 9, 94, "line")
    for k, (name, size) in enumerate([("PIXELART.ARC", "64K"), ("SUNSET.PCX", "38K"), ("FONTS.ZIP", "12K")]):
        y = 13 + k * 7
        if k == 0:
            s.rect(0, y - 1, 98, 7, "#1c3a8a")
        s.text(2, y, name, "white" if k == 0 else "text")
        s.text(96, y, size, "white" if k == 0 else "text", align="right")
    done = max(0.0, sec - 6.4) * CPS
    s.text(2, 38, "ZMODEM DOWNLOAD", "sky")
    s.meter(2, 46, 94, 5, done / FILE_BYTES, "lime")
    eta = (FILE_BYTES - done) / CPS
    s.text(2, 54, f"{c_num(done)} OF 65,536 BYTES", "text")
    s.text(2, 61, f"{CPS} CPS · ETA {int(eta // 60)}:{int(eta % 60):02d}", "text")
    w = s.text(2, 71, "GO MAKE A SANDWICH", "dim")
    cursor(2 + w, 71)


def c_num(n):
    return f"{int(n):,}"


def crt(c, x, y, sec):
    c.rect(x, y, 112, 100, BEIGE["top"])
    c.hline(x, y, 112, "#efe6c8")
    c.vline(x, y, 100, "#efe6c8")
    c.hline(x, y + 99, 112, BEIGE["right"])
    c.vline(x + 111, y, 100, BEIGE["right"])
    c.rect(x + 5, y + 4, 102, 84, "#3a3628")
    scr = Canvas(98, 80, theme=c.theme, bg="#04060c")
    screen(scr, sec)
    for yy in range(0, 80, 2):
        for xx in range(98):
            r, g, b = scr.img.getpixel((xx, yy))
            scr.img.putpixel((xx, yy), (r * 3 // 4, g * 3 // 4, b * 3 // 4))
    c.img.paste(scr.img, (x + 7, y + 6))
    for cx, cy in ((x + 7, y + 6), (x + 104, y + 6), (x + 7, y + 85), (x + 104, y + 85)):
        c.px(cx, cy, "#3a3628")
    c.text(x + 6, y + 91, "PIXELTRON 12", "#6a5e44")
    c.rect(x + 100, y + 92, 4, 2, "lime")
    for k in range(2):
        c.rect(x + 82 + k * 7, y + 91, 4, 4, BEIGE["right"])


def modem_panel(c, x, y, sec):
    c.rect(x, y, 112, 30, "#2e2e36")
    c.hline(x, y, 112, "#4a4a56")
    c.hline(x, y + 29, 112, "#1a1a20")
    c.text(x + 5, y + 4, "PIXELMODEM 2400", "#a0a0b0")
    c.text(x + 107, y + 4, "V.22BIS", "dim", align="right")
    state = modem_state(sec)
    for k, name in enumerate(LEDS):
        lx = x + 6 + k * 13
        on = state[name]
        c.rect(lx, y + 14, 5, 3, "#ff4a3a" if on else "#3a1414")
        if on:
            c.hline(lx + 1, y + 14, 3, "#ffb0a0")
        c.text(lx + 2, y + 20, name, "text" if on else "dim", align="center")


def draw(c, t):
    sec = t * SECONDS
    top = c.header("THE SYSOP'S BEDROOM, 1992", right="NODE 1 · 2400 BPS")
    scene = Canvas(206, c.h - top, theme=c.theme)
    room(scene, t, sec)
    c.img.paste(scene.img, (0, top))

    crt(c, 208, top + 1, sec)
    modem_panel(c, 208, top + 104, sec)
    online = max(0, int(sec - 2.6)) if sec > 2.6 else None
    info_y = top + 138
    c.text(210, info_y, "PORT", "dim")
    c.text(240, info_y, "COM1 · 8N1", "white")
    c.text(210, info_y + 8, "LINE", "dim")
    c.text(240, info_y + 8, "THE FAMILY PHONE", "white")
    c.text(210, info_y + 16, "ONLINE", "dim")
    c.text(240, info_y + 16, f"00:00:{online:02d}" if online is not None else "--:--:--",
           "lime" if online is not None else "dim")


animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=SECONDS, fps=8, hold=2.5, poster=0.6)
