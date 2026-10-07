"""An isometric action RPG in the late-90s style: a boss fight in a torch-lit crypt. A necromancer and his
raised skeletons face a towering fire demon: a bone spear in flight, a curse ring round the boss, bone
shards orbiting the caster, loot on the floor with a unique item's tooltip, the boss's health bar, and the
bottom HUD with life and mana orbs, a potion belt and skill slots. Everything is made up."""

import math
import random
from pathlib import Path

from pixelkit import animate, blink, flicker, iso_xy, orbit, phase, shake

OX, OY, SIZE, TILE, WALL = 160, -40, 128, 16, 84
WORLD_H = 146
STONE = ["#4a4640", "#433f3a", "#3c3934", "#4f4a42"]
MORTAR, WALL_R, WALL_L, BRICK = "#25221f", "#4a443c", "#3a352f", "#24201c"
HUD, HUD_GRAIN, TRIM = "#2a2520", "#1c1915", "#7a6236"
MAGIC, UNIQUE = "#7a7aff", "#c8a85a"
INK, KEY = "#0c0a08", "#ff00ff"
BONE, BONE_D, SOUL, CURSE = "#e8e0c8", "#9a9078", "#8aff7a", "#ff2a4a"
FLESH = ["#2a0505", "#5e0c0a", "#9a1c10", "#ff6a2a"]
HORN = ["#4a3a26", "#a8987a", "#d8cca8", "#fff4d8"]
SPINE = ["#140404", "#3a0c08", "#6a2a1a", "#c86a3a"]
MARK, LIGHT = "#ff00fe", (-1, 1)

NECRO = ["..........kkkk..........", "........kkkkkkkk........", ".......kKKKKKKKkk.......",
         "......kKKqqqqKKKkk......", "......kKqqKKKKKKKk......", ".....kKqKKkkkkkKKkk.....",
         ".....kKqKkkkkkkkKKk.....", ".....kKKkkSSSSSSkKk.....", ".....kKKkSeesseeSkk.....",
         ".....kKKkSssssssSkk.....", ".....kKKkkSsSSsSkk......", "......kKkkkSsssSkk......",
         "......kKKkkkSSSkk.......", "......kKKKkkkkkkk.......", "..b..bbkKKKkkkkkbb..b...",
         "..bbbbbbbKKKkkkbbbbbb...", ".bBbbbbbbbvvvvbbbbbbBb..", ".BbBbBBbBbvqqvbBbBbBbB..",
         ".kBBBBBBkkvqqvkkBBBBBk..", "kkkKKKKkKKvqqvKKkKKKKkk.", "kkKKqKKkKKvqqvKKkKKqKkk.",
         "kkKKqKKkKKvqqvKKkKKqKKk.", "kkKKqKKkKKvqqvKKkKKqKKk.", "kkKKqKKkKKvqqvKKkKKqKKk.",
         "kkKKqKKkbbbbbbbbkKKqKKk.", "kkKKqKKkBbrBBrbBkKKqKKk.", "kkKKSSKkKKvqqvKKkKKqKKk.",
         "kkKSssSkKKvqqvKKkKKqKKk.", "kkKKrrKkKKvqqvKKkKKKKKkk", "kkKKddKKKKvqqvKKKKKKKKkk",
         "kkkKddKKKKvqqvKKKKKKKKkk", "kkkKdKKKKKvqqvKKKKKKKKkk", "kkkkdKKKKKvqqvKKKKKKKKkk",
         "kkkkKKKKKKvqqvKKKKKKKKKk", ".kkkKKKKKKvqqvKKKKKKKKKk", ".kkkKKKKKKvqqvKKKKKKKKKk",
         ".kkkKKKKKvqqqqvKKKKKKKKk", "kkkkKKKKKvqqqqvKKKKKKKKk", "kkkKKKKKKvqKKqvKKKKKKKKk",
         "kkkKKKKKvqKKKKqvKKKKKKKk", "kkkKKKKKvqKKKKqvKKKKKKKk", "kkKKKKKvqKKKKKKqvKKKKKKk",
         "kkKKKKKvKKKKKKKKvKKKKKKk", "kkKKKKvKKKKKKKKKKvKKKKKk", "kKKKKKvKKKKKKKKKKvKKKKKk",
         "kKKKKvKKKKKKKKKKKKvKKKKk", "kKKKbKbKKKKKKKKKKbKbKKKk", "kbKbKbKbKbKbKbKbKbKbKbKk",
         "b.b.b.llll..llll.b.b.b..", "....llllll..llllll......"]
NECRO_COLORS = {"k": "#16121c", "K": "#2a2234", "q": "#4a3e5a", "v": "#6a2a8a", "b": BONE, "B": BONE_D,
                "s": "#d0d4c8", "S": "#8a8e86", "e": SOUL, "d": "#c8d0d8", "r": "#7a1a1a", "l": "#3a2a22"}
BREATH = NECRO[:24] + [NECRO[24]] + NECRO[24:]
ARMS = {   # (art, dx, dy, hand): the casting arm per keyframe, placed against the necromancer's top-left
    "rest": (["KKK.", "KKKq", "KKKq", "KKKq", "kKKq", "kKKq", "kKKq", "kKKq", "vvvv", "bbbb", ".SSs", ".SsS",
              "..s."], 18, 18, (20, 30)),
    "mid": (["KKK.......", "KKKKq.....", ".KKKKKq...", "..kKKKKq..", "...kKKKvb.", ".....kvbSs", "......bSss",
             ".......sS."], 18, 17, (26, 23)),
    "raised": (["....sSs", "...sSss", "...SsS.", "....bb.", "...vvv.", "...KKq.", "..KKKq.", "..KKq..",
                ".KKKq..", ".KKq...", "KKKq...", "KKq....", "KKK....", "KKK...."], 18, 4, (22, 5)),
    "thrust": (["..........sSs", "KK.....qvbSss", "KKKKqKKKvbSs.", "KKKKKKKKvb...", "KKKKKKKq....."], 18, 14,
               (30, 15)),
}
SKELETON = [".......iiiii.....", "......iiiiiii....", ".....iwwwwwwwi...", ".....wwwwwwwww...",
            ".....wkkwwkkww...", ".....wkewwkeww...", ".....wwwwkwwww...", "......wwwwwww....",
            "......wkwkwkw....", ".......wwwww.....", "........www......", "...mmmmwwwwwmmmm.",
            "..mmmmm.www.mmmmm", "..ww..wwwwwww..ww", "..ww.w..www..w.ww", "..ww.wwwwwwwww.ww",
            "..ww.w..www..w.ww", "..ww..wwwwwww..ww", "..ww.w..www..w.ww", "..ww..wwwwwww..ww",
            "..ww.....w.....ww", "..ww.....w.....ww", ".www.....w.....ww", ".ww....mmmmm...ww",
            "ww....wwwwwww..ww", "......ww...ww....", "......ww...ww....", ".....www...www...",
            ".....ww.....ww...", ".....ww.....ww...", ".....mm.....mm...", ".....ww.....ww...",
            "....www.....www..", "....ww.......ww..", "....ww.......ww..", "...www.......www.",
            "..wwww.......wwww"]
NX, NY = 64, 77
SX, SY = 134, 84
RX, RFLOOR = 98, 130
GOLD = [".y.y..", "yyYyy.", "yyyyyy"]
SCIMITAR = ["......w", ".....w.", "....w..", "...w...", "g.w....", ".g.....", "g.g...."]
POTION = ["..c..", ".ccc.", ".lll.", "lllll", "lLlll", "lllll", ".lll."]
CURSOR = ["g....", "gg...", "gGg..", "gGGg.", "gGGGg", "gGgg.", "g..g."]
SHARD = ["bB", "Bb"]
ICONS = {
    "DAGGER": (["......d.", ".....dd.", "....dd..", "...dd...", "r.dd....", ".rr.....", ".rr.....", "r..r...."],
               {"d": "#c8d0d8", "r": "#8a2a2a"}),
    "SPEAR": (["......bb", ".....bB.", "....bB..", "...bB...", "..bB....", ".bB.....", "bb......", "b......."],
              {"b": BONE, "B": BONE_D}),
    "RAISE": ([".bbbb.", "bbbbbb", "bkbbkb", "bbbbbb", ".bkkb.", ".b.b.b", "..gg..", ".gggg."],
              {"b": BONE, "k": "#101014", "g": SOUL}),
    "ARMOR": (["b.bb.b", ".bbbb.", "bbBBbb", ".bBBb.", "bbBBbb", ".bbbb.", "b.bb.b"], {"b": BONE, "B": BONE_D}),
    "CURSE": ([".rrrr.", "r.rr.r", "rr..rr", "rr..rr", "r.rr.r", ".rrrr."], {"r": CURSE}),
}
TOOLTIP = [("THE EMBERWAKE", UNIQUE), ("GRAND SCIMITAR", UNIQUE), ("ONE-HAND DAMAGE: 14 TO 38", "white"),
           ("REQUIRED LEVEL: 24", "white"), ("+60% ENHANCED DAMAGE", MAGIC), ("ADDS 8-19 FIRE DAMAGE", MAGIC),
           ("+2 TO LIGHT RADIUS", MAGIC)]


def P(u, v, z=0):
    return iso_xy(OX, OY, u, v, z)


def pose(t):
    """The necromancer's keyframe: rest (breathing), the arm rising, the raised cast held, the thrust held."""
    if 0.34 <= t < 0.38 or 0.72 <= t < 0.78:
        return "mid"
    if 0.38 <= t < 0.56:
        return "raised"
    if 0.56 <= t < 0.72:
        return "thrust"
    return "rest"


def walls(c):
    c.polygon([P(0, 0, WALL), P(SIZE, 0, WALL), P(SIZE, 0), P(0, 0)], fill=WALL_R)
    c.polygon([P(0, 0, WALL), P(0, SIZE, WALL), P(0, SIZE), P(0, 0)], fill=WALL_L)
    for row, z in enumerate(range(0, WALL, 10)):
        c.line(*P(0, 0, z), *P(SIZE, 0, z), BRICK)
        c.line(*P(0, 0, z), *P(0, SIZE, z), BRICK)
        for a in range(8 if row % 2 else 0, SIZE, 16):
            c.vline(*P(a, 0, z + 10), 10, BRICK)
            c.vline(*P(0, a, z + 10), 10, BRICK)
    for a in (44, 100):
        c.iso_block(OX, OY, a, 0, 8, 8, WALL, top="#55504a", left="#47423c", right="#36322d")
        c.iso_block(OX, OY, 0, a, 8, 8, WALL, top="#55504a", left="#47423c", right="#36322d")


def floor(c, t):
    rnd = random.Random(11)
    for u in range(0, SIZE, TILE):
        for v in range(0, SIZE, TILE):
            c.iso_tile(OX, OY, u, v, TILE, TILE, rnd.choice(STONE), outline=MORTAR)
    for _ in range(20):
        x, y = P(rnd.uniform(8, 120), rnd.uniform(8, 120))
        c.line(x, y, x + rnd.randint(-8, 8), y + rnd.randint(-3, 3), MORTAR)
    bone = {"w": "#b8b0a0", "k": "#101014"}
    c.sprite(30, 120, ["w....w", "ww..ww", ".wwww.", "ww..ww", "w....w"], bone)
    c.sprite(150, 128, [".wwww.", "wkwwkw", "wwwwww", ".wwww.", ".w.w.."], bone)
    rnd = random.Random(5)
    for k in range(9):
        x, y = 206 + rnd.randint(0, 92), 118 + rnd.randint(0, 20)
        hot = "#ffd860" if flicker(t, seed=k) > 0.5 else "#ff8a2a"
        for _ in range(4):
            nx, ny = x + rnd.randint(-9, 9), y + rnd.randint(-3, 3)
            c.line(x, y, nx, ny, "#ff6a1a")
            c.px(x, y, hot)
            x, y = nx, ny


def torch(c, t, x, y, seed):
    c.rect(x - 2, y + 4, 4, 8, "#3a2a1c")
    c.hline(x - 3, y + 4, 6, "#5a4a3a")
    f = flicker(t, seed=seed)
    h = 5 + round(f * 5)
    c.rect(x - 2, y + 4 - h, 4, h, "orange")
    c.rect(x - 1, y + 5 - h, 2, h - 1, "gold.light")


def limb(c, pts, w0, w1, color):
    """A tapering limb through points, as quads with round joints."""
    for k in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        a = w0 + (w1 - w0) * k / (len(pts) - 1)
        b = w0 + (w1 - w0) * (k + 1) / (len(pts) - 1)
        d = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / d, (x1 - x0) / d
        quad = [(x0 + nx * a, y0 + ny * a), (x1 + nx * b, y1 + ny * b), (x1 - nx * b, y1 - ny * b),
                (x0 - nx * a, y0 - ny * a)]
        c.polygon([(round(x), round(y)) for x, y in quad], fill=color)
        c.circle(x0, y0, a, color)
        c.circle(x1, y1, b, color)


def horn(c, pts, r0):
    n = 30
    for k in range(n):
        p = k / (n - 1)
        q = 1 - p
        x = q ** 3 * pts[0][0] + 3 * q * q * p * pts[1][0] + 3 * q * p * p * pts[2][0] + p ** 3 * pts[3][0]
        y = q ** 3 * pts[0][1] + 3 * q * q * p * pts[1][1] + 3 * q * p * p * pts[2][1] + p ** 3 * pts[3][1]
        c.circle(x, y, max(0.8, r0 * (1 - 0.8 * p)), MARK)
    c.form(MARK, HORN, light=LIGHT, width=2)


def claws(c, x, y, spread, base_ang):
    for k in range(4):
        a = math.radians(base_ang + (k - 1.5) * 22 * spread)
        mx, my = x + math.cos(a) * 6, y + math.sin(a) * 6
        tx, ty = mx + math.cos(a + 0.7) * 6, my + math.sin(a + 0.7) * 6
        c.line(round(x), round(y), round(mx), round(my), FLESH[0])
        c.line(round(mx), round(my), round(tx), round(ty), "#f0e4c8")
        c.px(round(mx), round(my), "#b0a080")


def part(d, shades=None, width=2, depth=None):
    d.form(MARK, shades or FLESH, light=LIGHT, width=width, depth=depth)


def demon(world, t):
    """The boss: parts painted flat and lit in turn on a keyed layer, pasted with an outline."""
    d = world.sub(320, WORLD_H, bg=KEY)
    heave = [0, 0, 1, 2, 2, 2, 1, 0][int(t * 16) % 8]
    u = -heave
    flex = [1.0, 0.7, 0.4, 0.7][int(t * 8) % 4]
    tail = [(286 + i * 1.3, 98 - i * 1.5 + 8 * (i / 25) * math.sin(2 * math.pi * (t - i / 40))) for i in range(26)]
    limb(d, [tuple(map(round, q)) for q in tail[::5]] + [tuple(map(round, tail[-1]))], 4, 1, MARK)
    tx, ty = map(round, tail[-1])
    d.polygon([(tx - 1, ty - 6), (tx + 6, ty), (tx - 1, ty + 5), (tx - 3, ty)], fill=MARK)
    part(d, width=1)
    limb(d, [(284, 44 + u), (304, 80 + u), (296, 110)], 9, 6, MARK)
    part(d, depth=5)
    claws(d, 296, 113, flex, 95)
    limb(d, [(270, 96), (292, 114), (282, 132)], 12, 6, MARK)
    part(d, depth=6)
    claws(d, 282, 134, 0.6, 10)
    horn(d, [(204, 52 + u), (228, 36 + u), (234, 10 + u), (214, 0 + u)], 5)
    d.polygon([(236, 102), (276, 102), (294, 80 + u), (290, 54 + u), (276, 28 + u), (252, 18 + u), (230, 26 + u),
               (210, 44 + u), (204, 70 + u), (220, 96)], fill=MARK)
    d.circle(256, 46 + u, 26, MARK)
    part(d, width=3, depth=9)
    for k in range(9):
        a = math.radians(-165 + k * 16)
        bx, by = 256 + 25 * math.cos(a), 46 + u + 25 * math.sin(a)
        ox, oy = math.cos(a - 0.45), math.sin(a - 0.45)
        ln = 9 + (k % 2) * 5
        d.polygon([(round(bx - oy * 3), round(by + ox * 3)), (round(bx + ox * ln), round(by + oy * ln)),
                   (round(bx + oy * 3), round(by - ox * 3))], fill=MARK)
    part(d, SPINE, width=1)
    for x0, y0, x1, y1 in ((214, 70, 232, 72), (232, 72, 238, 62), (220, 80, 234, 80), (222, 88, 234, 88),
                           (240, 40, 252, 58), (252, 58, 270, 60)):
        d.line(x0, y0 + u, x1, y1 + u, FLESH[0])
    limb(d, [(244, 98), (226, 116), (236, 132)], 12, 6, MARK)
    part(d)
    claws(d, 234, 135, 0.6, 175)
    limb(d, [(218, 50 + u), (196, 88 + u), (174, 114)], 11, 7, MARK)
    part(d, depth=4)
    claws(d, 170, 118, flex, 160)
    d.polygon([(176, 60 + u), (188, 52 + u), (204, 50 + u), (214, 58 + u), (212, 72 + u), (198, 78 + u),
               (184, 77 + u), (172, 70 + u)], fill=MARK)
    d.polygon([(174, 80 + u), (198, 80 + u), (194, 92 + u), (182, 96 + u), (170, 90 + u)], fill=MARK)
    part(d)
    d.polygon([(172, 72 + u), (200, 74 + u), (196, 82 + u), (174, 84 + u)], fill="#160202")
    for k in range(6):
        fx = 174 + k * 4
        d.polygon([(fx, 73 + u), (fx + 2, 73 + u), (fx + 1, 78 + u)], fill=BONE)
        d.polygon([(fx + 1, 84 + u), (fx + 3, 84 + u), (fx + 2, 79 + u)], fill=BONE)
    d.polygon([(176, 60 + u), (206, 56 + u), (208, 61 + u), (178, 64 + u)], fill=FLESH[0])
    hot = "#fff4a0" if blink(t, 4, duty=0.85) else "#ffd040"
    for ex in (184, 196):
        d.rect(ex - 1, 62 + u, 7, 4, "#ff6a1a")
        d.rect(ex, 63 + u, 5, 2, hot)
    d.px(175, 68 + u, "#160202")
    horn(d, [(190, 52 + u), (164, 42 + u), (158, 14 + u), (180, 2 + u)], 6)
    world.paste(d, 0, 0, key=KEY, outline=INK)


def skeleton(c, x, y, t, art_rows=None, strike=False, flash=False):
    rows = art_rows or SKELETON
    bones = {"w": "white" if flash else "#d8d0bc", "k": "#101014", "e": "red", "m": "#6a5040", "i": "#5a5a62"}
    c.sprite(x, y, rows, bones, outline=INK, shade=not flash, flip=True)
    if len(rows) < 25:
        return
    hx, hy = x + 15, y + 24
    tip = (hx + 18, hy - 8) if strike else (hx + 12, hy - 26)
    for off, col in ((0, "#9a8a7a"), (1, "#6a5a4a")):
        c.line(hx + off, hy - 3, tip[0] + off, tip[1], col)
    c.rect(hx - 1, hy - 3, 2, 4, "#3a2a1c")


def necromancer(c, t):
    key = pose(t)
    b = 1 if key == "rest" and (t * 4) % 1 >= 0.5 else 0
    art = BREATH if b else NECRO
    y = NY - b
    shards = orbit(NX + 12, NY + 30, 18, 5, t, 6, cycles=2)
    for sx, sy, front in shards:
        if not front:
            c.sprite(sx - 1, sy - 1, SHARD, {"b": BONE, "B": BONE_D}, outline=INK)
    c.sprite(NX, y, art, NECRO_COLORS, outline=INK, shade=True)
    arm, dx, dy, hand = ARMS[key]
    c.sprite(NX + dx, y + dy, arm, NECRO_COLORS, outline=INK, shade=True)
    for sx, sy, front in shards:
        if front:
            c.sprite(sx - 1, sy - 1, SHARD, {"b": BONE, "B": BONE_D}, outline=INK)
    return key, (NX + hand[0], y + hand[1])


def boss_bar(c, t, hit):
    x, w = 90, 140
    c.rect(x - 2, 1, w + 4, 16, "#0a0606")
    c.box(x - 2, 1, w + 4, 16, "#5a1a10")
    c.text(160, 3, "THE LORD OF CINDERS", "#ff9a5a", align="center")
    c.rect(x, 10, w, 4, "#2a0606")
    c.rect(x, 10, round(w * 0.64), 4, "#b01810")
    c.hline(x, 10, round(w * 0.64), "#ff4a2a")
    if 0 < hit < 0.4:
        c.rect(x + round(w * 0.64), 10, round(w * 0.07), 4, "white" if hit < 0.2 else "#ffd860")
    for k in range(1, 4):
        c.vline(x + k * w // 4, 10, 4, "#0a0606")


def label(c, x, y, s, color, *, hover=False):
    w = c.measure(s) + 4
    c.rect(x - w // 2, y - 2, w, 9, "#20286a" if hover else "#0c0b0a")
    c.text(x, y, s, color, align="center")


def mana(t):
    if 0.38 <= t < 0.45:
        return 0.62 - 0.12 * phase(t, 0.38, 0.45)
    return 0.5 + 0.12 * ((t - 0.45) % 1) / 0.93


def slot(c, x, y, w, name, *, hot=False, key=None, scale=1):
    r = c.bevel(x, y, w, w, "#3a3228", border="gold.light" if hot else "#0c0a08")
    c.rect(r.x + 1, r.y + 1, w - 2, w - 2, "#3a2a10" if hot else "#1a1410")
    art, cols = ICONS[name]
    aw, ah = len(art[0]) * scale, len(art) * scale
    c.sprite(x + (w - aw) // 2, y + (w - ah) // 2, art, cols, scale=scale)
    if key:
        c.text(x + w - 4, y + w - 6, key, "#c8b890")
    return r


def hud(c, t, key):
    top = WORLD_H
    c.rect(0, top, 320, 180 - top, HUD)
    c.pattern(0, top, 320, 180 - top, HUD_GRAIN, "grain")
    c.hline(0, top, 320, TRIM)
    c.hline(0, top + 1, 320, "#3a3228")
    c.rect(46, top + 3, 228, 2, "#140f0c")
    c.rect(46, top + 3, round(228 * 0.62), 2, "#c8a85a")
    for k in range(1, 10):
        c.px(46 + k * 228 // 10, top + 3, "#140f0c")
    m = mana(t)
    for cx, frac, col in ((22, 0.79, "red"), (298, m, "blue")):
        c.circle(cx, 160, 21, "#3a3228")
        c.circle(cx, 160, 20, TRIM)
        c.orb(cx, 160, 18, frac, col, empty="#1a1414", rim="#0c0a08", t=t, waves=1)
    c.text(22, 136, "412/520", "red.light", align="center", outline="#0c0b0a")
    c.text(298, 136, f"{round(190 * m)}/190", "blue.light", align="center", outline="#0c0b0a")

    slot(c, 48, top + 8, 24, "DAGGER", scale=2)
    for k, liquid in enumerate(("red", "red", "blue", "violet")):
        sx = 76 + k * 13
        c.bevel(sx, top + 8, 12, 18, "#1a1410", sunk=True, border="#0c0a08")
        c.sprite(sx + 3, top + 10, POTION, {"c": "#8a6a4a", "l": liquid, "L": f"{liquid}.light"})
        c.text(sx + 6, top + 28, str(k + 1), "#a89a7a", align="center")
    casting = key in ("raised", "thrust")
    for k, (name, hk) in enumerate((("SPEAR", "Q"), ("RAISE", "W"), ("ARMOR", "E"), ("CURSE", "R"))):
        slot(c, 130 + k * 19, top + 8, 18, name, hot=name == "SPEAR" and casting, key=hk)
    for k, name in enumerate(("CHAR", "INV", "SKILL", "MAP")):
        bx = 208 + (k % 2) * 20
        by = top + 8 + (k // 2) * 12
        c.bevel(bx, by, 19, 10, "#3a3228", border="#0c0a08")
        c.text(bx + 10, by + 2, name if name != "SKILL" else "SKL", "#c8b890", align="center")
    r = slot(c, 249, top + 8, 24, "SPEAR", scale=2, hot=casting)
    since = (t - 0.56) % 1
    if since < 0.5:
        c.cooldown(r.x + 1, r.y + 1, 22, 22, 1 - since / 0.5, amount=0.7, edge="gold.light")


def draw(c, t):
    world = c.sub(320, WORLD_H, bg="#060505")
    walls(world)
    floor(world, t)
    for x, y, art, cols in ((14, 98, SCIMITAR, {"w": "#d8dce4", "g": "gold"}),
                            (20, 130, GOLD, {"y": "gold", "Y": "gold.light"})):
        world.sprite(x, y, art, cols, scale=2, outline=INK)

    hit = phase(t, 0.70, 0.92)
    world.glyph(248, 92, 34, t, CURSE, squash=3.2, runes=8, accent="#ff8a9a", half="back")
    demon(world, t)
    world.glyph(248, 92, 34, t, CURSE, squash=3.2, runes=8, accent="#ff8a9a", half="front")

    rise = phase(t, 0.04, 0.30)
    if t < 0.42:
        world.glyph(RX + 8, RFLOOR + 1, 13, t, SOUL, squash=2.2, runes=5, accent="green")
    if 0 < rise and t < 0.92:
        rows = max(1, round(rise * len(SKELETON)))
        skeleton(world, RX, RFLOOR - rows, t, art_rows=SKELETON[:rows], strike=False)
    strike = 0.35 <= (t * 2) % 1 < 0.6
    skeleton(world, SX + (2 if strike else 0), SY, t, strike=strike)
    key, hand = necromancer(world, t)

    tr, tl = P(64, 0, 20), P(0, 64, 20)
    world.glow(*tr, 34, "orange", amount=0.18, squash=1.4, levels=2)
    world.glow(*tl, 34, "orange", amount=0.18, squash=1.4, levels=2)
    world.darkness([(76, 108, 66), (246, 92, 98), (*tr, 46), (*tl, 46)], amount=0.9, levels=2,
                   inner=0.5)
    for (x, y), seed in ((tr, 2), (tl, 3)):
        torch(world, t, x, y, seed)
        world.particles(x - 2, y - 8, 4, 3, t, "embers", n=6, seed=seed, speed=18, spread=50)
    world.particles(180, 76, 120, 60, t, "embers", n=26, seed=8, speed=40, spread=40, cycles=2)

    if t < 0.42:
        world.particles(RX, RFLOOR - 30, 18, 30, phase(t, 0.02, 0.42), "wisps", n=20, seed=3, burst=True,
                        speed=26, colors=["white", SOUL, "green"])
    world.particles(RX + 2, RFLOOR - 30, 14, 26, phase(t, 0.92, 1.0), "sparks", n=18, seed=6, burst=True,
                    speed=18, gravity=30, colors=[BONE, BONE_D, SOUL])
    if key == "raised":
        flare = phase(t, 0.38, 0.5)
        world.glow(*hand, 6 + round(flare * 8), SOUL, amount=0.5, levels=2)
        world.particles(hand[0] - 2, hand[1] - 2, 4, 4, t, "wisps", n=10, seed=9, speed=12, cycles=4)
        world.rect(hand[0] - 1, hand[1] - 1, 3, 3, "white")
    elif key == "thrust":
        world.glow(*hand, 8, SOUL, amount=0.4, levels=2)
    world.glow(NX + 12, NY + 8, 6, SOUL, amount=0.3, levels=1)
    head = world.projectile(NX + 31, NY + 15, 222, 66, phase(t, 0.56, 0.70), BONE, trail=[BONE, BONE_D, "#5a5448"],
                            length=24, width=3, shards=40, life=0.45, spread=2.5, gravity=6)
    if head:
        a = math.atan2(66 - NY - 15, 222 - NX - 31)
        tipx, tipy = head[0] + math.cos(a) * 5, head[1] + math.sin(a) * 5
        world.polygon([(round(tipx), round(tipy)), (round(head[0] - math.sin(a) * 3), round(head[1] + math.cos(a) * 3)),
                       (round(head[0] + math.sin(a) * 3), round(head[1] - math.cos(a) * 3))], fill="white")
        world.particles(head[0] - 14, head[1] - 2, 14, 6, t, "wisps", n=8, seed=5, speed=6, cycles=8)
    world.particles(218, 60, 8, 8, hit, "sparks", n=26, seed=2, burst=True, angle=180, spread=200, speed=30,
                    gravity=14, colors=["white", BONE, SOUL, BONE_D])
    jolt = shake(t, 1 if 0 < hit < 0.15 else 0, seed=4, cycles=32)
    c.paste(world, *jolt)

    if 0 < hit < 1:
        c.text(214, 50 - round(hit * 16), "428", "#ffd84a", font="large", outline=INK)
    boss_bar(c, t, hit)
    label(c, 30, 88, "THE EMBERWAKE", UNIQUE, hover=True)
    label(c, 26, 122, "214 GOLD", "white")
    c.sprite(26, 104, CURSOR, {"g": "#8a6a2a", "G": "#e8c87a"})
    tip_w, tip_h = 116, len(TOOLTIP) * 7 + 5
    tx, ty = 4, 22
    c.rect(tx, ty, tip_w, tip_h, "#0a0908")
    c.box(tx, ty, tip_w, tip_h, "#3a3228")
    for k, (line, col) in enumerate(TOOLTIP):
        c.text(tx + tip_w // 2, ty + 3 + k * 7, line, col, align="center")
    hud(c, t, key)


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=8, seamless=True, poster=0.64)
