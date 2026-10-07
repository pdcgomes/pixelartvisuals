"""A late-80s parser adventure as an isometric diorama: a neon cocktail lounge at night with a long bar and
lit bottle shelves, a jukebox, a dance floor under a mirror ball, booths, palms, a mint machine, a payphone
and a bouncer at the door, a hopeful hero in a white polyester suit and a woman at the bar who doesn't
look up; framed by the status bar, a typed command and the narrator's reply. Everything is made up."""

import math
import random
from pathlib import Path

from pixelkit import FONTS, animate, blink, flicker, orbit, phase, reveal

EGA = {"k": "#000000", "b": "#0000aa", "g": "#00aa00", "c": "#00aaaa", "r": "#aa0000", "m": "#aa00aa",
       "n": "#aa5500", "l": "#aaaaaa", "d": "#555555", "B": "#5555ff", "G": "#55ff55", "C": "#55ffff",
       "R": "#ff5555", "M": "#ff55ff", "y": "#ffff55", "w": "#ffffff"}
OX, OY, U, V, HW = 168, 54, 72, 60, 40
TOP, BOTTOM = 9, 168
INK = "#08040c"
FLOOR, FLOOR_D = "#2a1430", "#22102a"
LEFT_WALL, RIGHT_WALL, STRIPE_L, STRIPE_R = "#24184a", "#3a1238", "#2c1e58", "#461844"
WOOD = {"top": "#8a4a2a", "left": "#6a3418", "right": "#4a2410"}
BRASS = "#e8c050"
RED_VINYL = {"top": "#c02a3a", "left": "#a01e2e", "right": "#781424"}
STEEL = {"top": "#8a8aa0", "left": "#6a6a80", "right": "#4a4a5e"}
JUKE = {"top": "#c87a2a", "left": "#a05a1e", "right": "#7a4214"}

HERO = (["...hhhh....", "..hhhhhh...", "..hssssh...", "..sssesss..", "..ssssssss.", "...sssss...", "....ss.....",
         "..wwyyww...", ".wwwyywww..", ".wwwwwwwww.", "wwww.www.ww", "ww.wwwww.ss", "ss.wwwww...", "...wwwww...",
         "...bbbbb...", "...ww.ww...", "...ww.ww...", "...ww.ww...", "...ww.ww...", "...ww.ww...", "..kkk.kkk.."],
        ["...hhhh....", "..hhhhhh...", "..hssssh...", "..sssesss..", "..ssssssss.", "...sssss.ss", "....ss..ss.",
         "..wwyyww.w.", ".wwwyywwww.", ".wwwwwwww..", "wwww.www...", "ww.wwwww...", "ss.wwwww...", "...wwwww...",
         "...bbbbb...", "...ww.ww...", "...ww.ww...", "...ww.ww...", "...ww.ww...", "...ww.ww...", "..kkk.kkk.."])
HERO_COLORS = {"h": "#6a3a1a", "s": "#f0b090", "e": "#101010", "w": "#f4f4f0", "y": "#ffd040", "b": "#202020",
               "k": "#202020"}
WOMAN = (["..yyyy...", ".yyyyyy..", "yyyyyyyy.", "yyyyyyys.", ".yyyyyss.", "..yyy.s..", "..rrrrs..", ".rrrrrr..",
          ".rrrrrr..", "..rrrr...", ".rrrrrr..", "rrrrrrrr.", "..ss.ss..", "..ss.ss..", "..kk.kk.."],
         ["..yyyy...", ".yyyyyy..", "yyyyyyyy.", "yyyyyyyss", ".yyyyyss.", "..yyy.s..", "..rrrr...", ".rrrrrr..",
          ".rrrrrr..", "..rrrr...", ".rrrrrr..", "rrrrrrrr.", "..ss.ss..", "..ss.ss..", "..kk.kk.."])
WOMAN_COLORS = {"y": "#ffe070", "s": "#f0b090", "r": "#e02a5a", "k": "#600a2a"}
BARKEEP = (["...ssss...", "..ssssss..", "..seesss..", "..ssssss..", "..skkkks..", "...ssss...", "..wwkkww..",
            ".vvwwwwvv.", ".vvwwwwvvs", ".vvwwwwvvg", ".vvwwwwvv.", "..vvvvvv..", "..pppppp..", "..pp..pp.."],
           ["...ssss...", "..ssssss..", "..seesss..", "..ssssss..", "..skkkks..", "...ssss...", "..wwkkww..",
            ".vvwwwwvv.", ".vvwwwwvsg", ".vvwwwwvv.", ".vvwwwwvv.", "..vvvvvv..", "..pppppp..", "..pp..pp.."])
BARKEEP_COLORS = {"s": "#e8a880", "e": "#101010", "k": "#3a2010", "w": "#f0f0e8", "v": "#2a2a6a", "p": "#202030",
                  "g": "#a8e8ff"}
BOUNCER = ["....ssss....", "...ssssss...", "...kkkkkk...", "...ssssss...", "....ssss....", "..kkkwwkkk..",
           ".kkkkwwkkkk.", "kkkkkkkkkkkk", "kkssssssskkk", "kkkkkkkkkkkk", ".kkkkkkkkkk.", "..kkkkkkkk..",
           "..kkkkkkkk..", "..kkk..kkk..", "..kkk..kkk..", "..kkk..kkk..", "..kkk..kkk..", ".kkkk..kkkk."]
BOUNCER_COLORS = {"s": "#8a5a3a", "k": "#18181e", "w": "#f0f0e8"}
DANCER = ([".aaaa..s..", "aaaaaa.s..", "aassaa.s..", ".ssss.s...", "..ss.s....", ".oooooo...", "s.oooo....",
           "..oooo....", "..pppp....", ".pp..pp...", ".pp..pp...", "pp....pp..", "kk....kk.."],
          ["..aaaa....", ".aaaaaa...", ".aassaa...", "..ssss....", "...ss.....", "s.oooooo.s", ".soooooos.",
           "...oooo...", "...pppp...", "..pp..pp..", "..pp..pp..", ".pp....pp.", ".kk....kk."])
DANCER_COLORS = {"a": "#3a1a0a", "s": "#c8885a", "o": "#ff8a2a", "p": "#8a2aa8", "k": "#202020"}
COUPLE = (["..hhh....rrrr.", ".hssh...rrssr.", ".ssss...rsssr.", "..ss.....ss...", ".bbbbs..smmmm.",
           "bbbbbb..mmmmmm", "bbbbbb..mmmmmm"],
          ["..hhh....rrrr.", ".hssh...rrssr.", ".ssss...rsssr.", "..ss.....ss...", ".bbbb...mmmmm.",
           "bbbbbbsmmmmmmm", "bbbbbb..mmmmmm"])
COUPLE_COLORS = {"h": "#2a1a10", "s": "#e8b090", "r": "#c83a1a", "b": "#2a6a8a", "m": "#5aa86a"}
DRUNK = ["..nnnn....", ".nnnnnnss.", "nnnnnnnsss", "nnnnnnnnss", ".gggggg...", "gggggggg..", ".gg..gg..."]
COMMAND = "ORDER A DRINK"
REPLY = "THE BARTENDER SLIDES YOU A WARM MILK. SHE DOESN'T LOOK UP. SMOOTH, VINNIE. REAL SMOOTH."
DANCE = ["M", "C", "y", "R", "B", "G"]


def P(u, v, z=0):
    return round(OX + 2 * (u - v)), round(OY + u + v - z)


def box(c, u, v, w, d, h, z=0, look=WOOD, **kw):
    x, y = P(u, v, z + h)
    return c.iso_box(x, y, w, d, h, top=look["top"], left=look["left"], right=look["right"], **kw)


def on_wall(c, w, h, paint, wall, a, z):
    """A flat picture on a wall, sheared 2:1: `a` is its left edge (u on the right wall, v on the left), z its top."""
    s = c.sub(w, h, bg="#ff00ff")
    paint(s)
    x, y = P(a, 0, z) if wall == "right" else P(0, a, z)
    c.paste(s, x, y, key="#ff00ff", shear=1 if wall == "right" else -1)


def stand(c, art, colors, u, v, z=0, *, flip=False):
    x, y = P(u, v, z)
    c.sprite(x - len(art[0]) // 2, y - len(art) + 1, art, colors, outline=INK, shade=True, flip=flip)


def room(c, t):
    floor = [P(0, 0), P(U, 0), P(U, V), P(0, V)]
    c.polygon(floor, fill=FLOOR)
    for k in range(0, U, 6):
        c.line(*P(k, 0), *P(k, V), FLOOR_D)
    for k in range(0, V, 6):
        c.line(*P(0, k), *P(U, k), FLOOR_D)
    c.polygon([P(0, 0, HW), P(0, V, HW), P(0, V), P(0, 0)], fill=LEFT_WALL)
    c.polygon([P(0, 0, HW), P(U, 0, HW), P(U, 0), P(0, 0)], fill=RIGHT_WALL)
    for v in range(2, V, 4):
        c.line(*P(0, v, 2), *P(0, v, HW - 1), STRIPE_L)
    for u in range(2, U, 4):
        c.line(*P(u, 0, 2), *P(u, 0, HW - 1), STRIPE_R)
    c.polygon([P(0, 0, 10), P(0, V, 10), P(0, V), P(0, 0)], fill="#1a1036")
    c.polygon([P(0, 0, 10), P(U, 0, 10), P(U, 0), P(0, 0)], fill="#2a0c2a")
    c.line(*P(0, 0, 10), *P(0, V, 10), "#5a3a8a")
    c.line(*P(0, 0, 10), *P(U, 0, 10), "#8a3a7a")
    c.vline(*P(0, 0, HW), HW, "#140a28")
    c.polyline([P(0, V, HW), P(0, 0, HW), P(U, 0, HW)], "#8a62c0")


def shelves(s, t):
    s.rect(0, 0, 66, 24, "#3a1a10")
    rnd = random.Random(4)
    for k, y in enumerate((9, 21)):
        s.rect(0, y, 66, 2, "#8a5a2a")
        s.hline(0, y, 66, "#c8904a")
        x = 2
        while x < 64:
            h = rnd.choice((5, 6, 7))
            col = rnd.choice(["#2a8a4a", "#c87a2a", "#e8e8f0", "#8a1a2a", "#3a6ad0", "#e8c050"])
            s.rect(x, y - h, 2, h, col)
            s.px(x, y - h - 1, col)
            s.px(x, y - h + 1, "#ffffff")
            x += 3 + rnd.randrange(2)


def neon(s, t):
    on = blink(t, 6, duty=0.85)
    pink = EGA["M"] if on else "#7a2a6a"
    s.box(0, 0, 60, 13, pink)
    s.text(30, 4, "CLUB VELOUR", pink, align="center", check=False)
    cyan = EGA["C"] if blink(t, 3, offset=0.4, duty=0.7) else "#2a6a7a"
    s.line(64, 1, 72, 1, cyan)
    s.line(64, 1, 68, 6, cyan)
    s.line(72, 1, 68, 6, cyan)
    s.vline(68, 6, 5, cyan)
    s.hline(65, 11, 7, cyan)
    s.px(70, 3, EGA["y"])


def payphone(s, t):
    s.rect(0, 0, 10, 16, "#5a5a6e")
    s.box(0, 0, 10, 16, "#2a2a3a")
    s.rect(2, 2, 6, 4, "#1a1a2a")
    for k in range(6):
        s.px(3 + (k % 3) * 2, 8 + (k // 3) * 2, "#c8c8d8")
    s.rect(0, 3, 2, 8, "#202028")
    s.line(1, 11, 3, 18, "#202028")


def back_wall(c, t):
    on_wall(c, 66, 24, lambda s: shelves(s, t), "right", 12, 30)
    on_wall(c, 74, 13, lambda s: neon(s, t), "right", 14, 39)
    on_wall(c, 10, 18, lambda s: payphone(s, t), "left", 20, 28)
    door = [P(63, 0, 0), P(70, 0, 0), P(70, 0, 24), P(63, 0, 24)]
    c.polygon(door, fill="#0a0612")
    c.polygon([P(64, 0, 1), P(69, 0, 1), P(69, 0, 22), P(64, 0, 22)], fill="#3a2a5a", pattern="sparse")
    x, y = P(66.5, 0, 31)
    c.rect(x - 9, y - 1, 19, 8, "#2a0a0a")
    c.text(x, y + 1, "EXIT", EGA["R"] if blink(t, 2, duty=0.9) else "#8a2a2a", align="center")
    for k in range(3):
        on_wall(c, 8, 10, lambda s: (s.rect(0, 0, 8, 10, "#e8c050"), s.rect(1, 1, 6, 8, "#3a1a4a"),
                                     s.circle(4, 5, 2, ["#ff55ff", "#55ffff", "#ffff55"][k])), "left", 32 + k * 9, 30)


def glow_map(c, cx, cy, r, tints, *, squash=2.0):
    """Tint the listed colours inside an ellipse, solid in the middle and dithered at the rim."""
    tints = {c.rgb(a): c.rgb(b) for a, b in tints.items()}
    for y in range(max(0, int(cy - r)), min(c.h, int(cy + r) + 1)):
        for x in range(max(0, int(cx - r * squash)), min(c.w, int(cx + r * squash) + 1)):
            d = ((x - cx) / squash) ** 2 + (y - cy) ** 2
            if d >= r * r or (d > r * r * 0.45 and (x + y) % 2):
                continue
            px = c.img.getpixel((x, y))
            if px in tints:
                c.img.putpixel((x, y), tints[px])


def jukebox(c, t):
    jb = box(c, 1, 22, 5, 8, 18, look=JUKE)
    cycle = "MCyRBG"
    for k in range(3):
        col = EGA[cycle[(k + int(t * 12)) % len(cycle)]]
        c.line(*jb.right(1 + k, 2), *jb.right(1 + k, 16), col)
        c.line(*jb.right(7 - k, 2), *jb.right(7 - k, 16), col)
    c.polygon([jb.right(3, 4), jb.right(5, 4), jb.right(5, 9), jb.right(3, 9)], fill=EGA["y"])
    for b in (11, 13, 15):
        c.line(*jb.right(3, b), *jb.right(5, b), "#3a1a0a")
    x, y = jb.top(2.5, 4)
    for nx, ny, col in c.particles(x - 6, y - 16, 12, 12, t, "motes", n=4, seed=6, colors=["M", "C", "y"],
                                   draw=False):
        c.sprite(nx, ny, [".##", ".#.", "##.", "##."], {"#": EGA[col]})


def palm(c, u, v, t, k):
    x, y = P(u, v)
    c.rect(x - 3, y - 6, 7, 6, "#8a3a1a")
    c.hline(x - 3, y - 6, 7, "#c8603a")
    sway = 1 if blink(t, 2, offset=k * 0.3) else 0
    c.rect(x, y - 20, 2, 14, "#6a4a24")
    for a in (-150, -110, -60, -20, 160, 30):
        r = math.radians(a)
        for j in range(9):
            c.px(round(x + 1 + sway + math.cos(r) * j), round(y - 20 + math.sin(r) * j * 0.6 + j * j * 0.06),
                 "#2a9a3a" if j < 6 else "#1a6a2a")


def booths(c, t):
    box(c, 1, 36, 3, 15, 12, look=RED_VINYL)
    box(c, 7, 39, 5, 8, 7, look={"top": "#6a3a20", "left": "#4a2814", "right": "#3a1e0e"})
    stand(c, COUPLE[0 if blink(t, 2, offset=0.2, duty=0.6) else 1], COUPLE_COLORS, 6, 43, z=7)
    x, y = P(9, 43, 7)
    c.rect(x - 1, y - 4, 2, 4, "#ffd040")
    c.px(x, y - 5, "#ff5555" if flicker(t, seed=8) > 0.4 else "#ffd040")
    box(c, 13, 36, 3, 15, 6, look=RED_VINYL)


TABLE_GUY = (["..kkkk....", ".kssssk...", "..sesss...", "..skkks...", "...sss....", ".ccccccs..", "cccccccg..",
              "cccccc....", "cccccc...."],
             ["..kkkk....", ".kssssk...", "..sesss...", "..skkks.g.", "...sss..s.", ".cccccccs.", "cccccc....",
              "cccccc....", "cccccc...."])
LADY = (["..pppp....", ".pppppp...", ".pssssp...", "..sesss...", "...sss....", "..mmmm.s..", ".mmmmmms..",
         ".mmmmmm...", ".mmmmmm..."],
        [".pppp.....", "pppppp....", "pssssp....", ".sesss....", "..sss.....", "..mmmm....", ".mmmmmmss.",
         ".mmmmmm...", ".mmmmmm..."])


WAITRESS = (["..yyyy..ww.", ".yyyyyy.ww.", ".yssssy.s..", "..sesss.s..", "...sss..s..", "..kkkkks...",
             ".kkwwkk....", ".kkwwkk....", "..kwwk.....", ".kkkkkk....", "..s..s.....", "..s..s.....",
             "..s..s.....", ".kk..kk...."],
            ["..yyyy.....", ".yyyyyy.ww.", ".yssssy.ww.", "..sesss.s..", "...sss..s..", "..kkkkks...",
             ".kkwwkk....", ".kkwwkk....", "..kwwk.....", ".kkkkkk....", "..s..s.....", "..s..s.....",
             "..s..s.....", ".kk..kk...."])
WAITRESS_COLORS = {"y": "#c86a2a", "s": "#f0b890", "e": "#101010", "k": "#1a1a24", "w": "#f0f0e8"}


def cafe(c, u, v, who, colors, t, k):
    for du, dv in ((-3, 0), (3, 0)):
        x, y = P(u + du, v + dv)
        c.vline(x, y - 6, 6, "#6a6a7a")
        c.rect(x - 2, y - 7, 5, 2, "#a02a4a")
    for i, (art, cols) in enumerate(zip(who, colors)):
        stand(c, art[0 if blink(t, 2, offset=k * 0.3 + i * 0.5, duty=0.6) else 1], cols, u + (-3 if i == 0 else 3),
              v, z=6, flip=i == 1)
    x, y = P(u, v)
    c.vline(x, y - 8, 8, "#8a8a9a")
    c.hline(x - 3, y, 7, "#5a5a6a")
    c.polygon([(x - 7, y - 9), (x, y - 12), (x + 7, y - 9), (x, y - 6)], fill="#e8e0d0")
    c.rect(x - 1, y - 12, 2, 3, "#ffd040")
    c.px(x, y - 13, "#ff7a2a" if flicker(t, seed=k) > 0.4 else "#ffd040")


def stool(c, u, v):
    x, y = P(u, v)
    c.vline(x, y - 8, 8, "#c8c8d8")
    c.hline(x - 2, y, 5, "#8a8a9a")
    c.rect(x - 3, y - 10, 7, 2, "#c02a3a")
    c.hline(x - 3, y - 10, 7, "#ff5a6a")


def bar(c, t):
    stand(c, BARKEEP[int(t * 4) % 2], BARKEEP_COLORS, 26, 4, z=0)
    counter = box(c, 10, 8, 36, 5, 12, look=WOOD, edge="#c8804a")
    c.line(*counter.left(0, 9), *counter.left(36, 9), BRASS)
    for u in range(2, 36, 4):
        c.line(*counter.left(u, 1), *counter.left(u, 11), "#5a2a12")
    for k, (u, col) in enumerate(((16, "#a8e8ff"), (34, "#ff5aa8"), (40, "#ffe070"))):
        x, y = P(u, 10, 12)
        c.rect(x - 1, y - 4, 3, 4, col)
        c.px(x, y - 5, "#ffffff")
    for u in (14, 20, 26, 32, 38, 44):
        stool(c, u, 16)
    x, y = P(14, 16, 10)
    c.sprite(x - 5, y - 6, DRUNK, {"n": "#aa5500", "s": "#f0b090", "g": "#3a6a3a"}, outline=INK, shade=True)
    for k in range(3):
        p = (t * 2 + k / 3) % 1
        c.text(x - 2 + k * 2 + round(p * 4), y - 12 - round(p * 10), "Z", "#ffffff" if p < 0.6 else "#8a8aa8",
               check=False)
    sip = (t * 2) % 1 < 0.35
    stand(c, WOMAN[1 if sip else 0], WOMAN_COLORS, 38, 16, z=9)
    return counter


def mints(c, t):
    m = box(c, 54, 1, 6, 4, 22, look=STEEL)
    c.polygon([m.left(1, 2), m.left(5, 2), m.left(5, 10), m.left(1, 10)], fill="#3a8ae8" if blink(t, 4, duty=0.8)
              else "#2a6ac0")
    for k in range(4):
        c.line(*m.left(1, 12 + k * 2), *m.left(5, 12 + k * 2), EGA["y"] if k % 2 else EGA["R"])
    x, y = P(57, 0, 30)
    c.rect(x - 12, y - 1, 25, 8, "#10102a")
    c.text(x, y + 1, "MINTS", EGA["C"], align="center")


def dance_floor(c, t):
    for i in range(5):
        for j in range(5):
            col = EGA[DANCE[(i + j * 2 + int(t * 8)) % len(DANCE)]] if (i + j) % 2 == 0 else "#2a1a3a"
            u, v = 48 + i * 4, 24 + j * 4
            c.polygon([P(u, v), P(u + 4, v), P(u + 4, v + 4), P(u, v + 4)], fill=col)
    c.polyline([P(48, 24), P(68, 24), P(68, 44), P(48, 44), P(48, 24)], "#e8c050")


def mirror_ball(c, t):
    x, y = P(58, 34, 30)
    c.vline(x, y - 26, 21, "#8a8a9a")
    c.hline(x - 2, y - 26, 5, "#5a5a6a")
    c.sphere(x + 0.5, y + 0.5, 5, "#aaaaaa", shades=["#555566", "#aaaaaa", "#ffffff"])
    for k in range(4):
        if blink(t, 4, offset=k * 0.25, duty=0.3):
            c.px(x - 2 + k, y - 2 + (k % 2) * 3, "#ffffff")
    for sx, sy, front in orbit(x, y + 18, 80, 30, t, 20, cycles=1):
        if 0 <= sy < BOTTOM and 0 <= sx < 320:
            col = c.img.getpixel((sx, sy))
            if col != c.rgb("#000000"):
                c.rect(sx, sy, 2, 1, "#ffffff" if front else "#c8a8e8")


def scene(c, t):
    room(c, t)
    back_wall(c, t)
    palm(c, 3, 3, t, 0)
    jukebox(c, t)
    mints(c, t)
    stand(c, BOUNCER, BOUNCER_COLORS, 66, 5)
    counter = bar(c, t)
    booths(c, t)
    dance_floor(c, t)
    cafe(c, 26, 40, [TABLE_GUY, LADY], [{"k": "#2a1a10", "s": "#d8a070", "e": "#101010", "c": "#8a3a1a", "g": "#a8e8ff"},
                                         {"p": "#5a2a8a", "s": "#e8b090", "e": "#101010", "m": "#2aa8a8"}], t, 1)
    cafe(c, 38, 52, [TABLE_GUY, TABLE_GUY], [{"k": "#d0d0d0", "s": "#c8885a", "e": "#101010", "c": "#3a5a2a",
                                              "g": "#ffe070"},
                                             {"k": "#1a1a1a", "s": "#f0c0a0", "e": "#101010", "c": "#6a2a6a",
                                              "g": "#ff7aa8"}], t, 2)
    dancer = DANCER[int(t * 4) % 2]
    stand(c, dancer, DANCER_COLORS, 58, 32)
    stand(c, HERO[1 if (t * 2) % 1 < 0.25 else 0], HERO_COLORS, 30, 21)
    palm(c, 4, 54, t, 1)
    stand(c, WAITRESS[int(t * 4) % 2], WAITRESS_COLORS, 24, 54)
    palm(c, 70, 18, t, 2)
    glow_map(c, *P(5, 26), 12, {FLOOR: "#3a1a40", FLOOR_D: "#2e1636", LEFT_WALL: "#3a1a4a",
                                STRIPE_L: "#42205a"})
    glow_map(c, *P(58, 34), 18, {FLOOR: "#3a1a48", FLOOR_D: "#301640"})
    glow_map(c, *P(27, 0, 34), 10, {RIGHT_WALL: "#5a1a52", STRIPE_R: "#661c5c"}, squash=2.4)
    mirror_ball(c, t)
    return counter


def draw(c, t):
    c.rect(0, 0, 320, 180, "#000000")
    scene(c, t)

    c.rect(0, 0, 320, TOP - 1, EGA["w"])
    c.text(4, 1, "VINNIE VELOUR: NEON NIGHTS", EGA["k"])
    c.text(186, 1, "SCORE: 0 OF 222", EGA["k"], align="center")
    c.text(316, 1, "SOUND: ON", EGA["k"], align="right")
    c.hline(0, TOP - 1, 320, EGA["k"])

    c.rect(0, BOTTOM, 320, 180 - BOTTOM, EGA["k"])
    answered = t >= 0.4
    typed = "" if answered else reveal(COMMAND, phase(t, 0.06, 0.32))
    w = c.text(4, BOTTOM + 3, ">" + typed, EGA["w"], font="large")
    if blink(t, 8):
        c.rect(4 + w + 2, BOTTOM + 9, 5, 1, EGA["w"])

    if answered and t < 0.96:
        bx, by, bw = 6, 14, 140
        bh = len(FONTS["large"].wrap(REPLY, bw - 16)) * 10 + 13
        c.rect(bx, by, bw, bh, EGA["w"])
        c.box(bx + 2, by + 2, bw - 4, bh - 4, EGA["r"])
        c.box(bx + 3, by + 3, bw - 6, bh - 6, EGA["r"])
        c.paragraph(bx + 8, by + 8, REPLY, bw - 16, EGA["k"], font="large")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=6, fps=8, seamless=True, poster=0.7)
