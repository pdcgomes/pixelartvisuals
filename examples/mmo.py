"""An MMORPG raid as an isometric diorama: a red-rock canyon hold at dusk with a spiked palisade, hide huts,
war banners, braziers, a war drum and a zeppelin tower, and a raid of orcs, a bull-man, a mohawked hunter
and a goblin trader facing a colossal magma lord rising from a lava lake, under the full interface: unit
frames with the boss targeted and casting, a minimap, a quest tracker, chat, action bars and an XP bar.
Everything is made up."""

import math
import random
from pathlib import Path

from pixelkit import animate, blink, flicker, phase

OX, OY = 160, 30
KEY, MARK, INK = "#ff00ff", "#ff00fe", "#0c0806"
BASALT = ["#1e0a06", "#4e2416", "#8a4428", "#ffc050"]
IRON = ["#16161c", "#3a3a46", "#6a6a78", "#ffa040"]
LAVA, LAVA_HI, LAVA_D, CRUST = "#f05a1a", "#ffd060", "#b02a0a", "#2a100a"
GROUND, GRAIN = "#3a1a10", "#2c120a"
ROCK_R, ROCK_L, STRATA = "#5a2214", "#36140c", "#260c06"
BANNER, CREST = "#8a1010", "#e8dcc0"
HIDE = {"top": "#a07a50", "left": "#8a6440", "right": "#6a4a2e"}
TIMBER = {"top": "#5a3a22", "left": "#6a4428", "right": "#4a2e1a"}

ORC = [".....hh........", "....gggg.......", "...gggggg......", "...geggeg......", "...gggggg......",
       "...gwggwg......", ".w..gggg..w....", "PPP.gggg.PPPx..", "PPPPaaaaPPPPxii", ".PPaaaaaaPPgxii",
       ".gg.aaaa.gg.xii", ".gg.aaaa.gg.x..", ".gg.bbbb.gg.x..", "....rrrr....x..", "....rrrr.......",
       "...gg..gg......", "...gg..gg......", "...kk..kk......", "..kkk..kkk....."]
GREEN_ORC = {"h": "#1a1a1a", "g": "#4a8a2a", "e": "#ff3a2a", "w": "#f0e8d0", "P": "#6a6a74", "a": "#4a2e1a",
             "b": "#2a1a10", "r": "#8a1010", "k": "#2a1a10", "x": "#5a3a1c", "i": "#b8b8c4"}
GREY_ORC = {**GREEN_ORC, "g": "#7a8070", "a": "#22222a", "P": "#3a3a44", "r": "#3a3a44", "i": "#c83a2a"}
TAUREN = ["w...............w.", "ww....ffff....ww..", ".www.ffffff.www...", "....ffeffeff......",
          "....ffffffff......", ".....fnnnnf.......", ".....nnyynn.......", "......nnnn....t...",
          "..ffffffffffff.t..", ".fffffffffffffft..", "fffffaaaaaafffft..", "fff.faaaaaaf.fft..",
          "ff..faaaaaaf..ft..", "ff..fbbbbbbf..ft..", "hh..frrrrrrf..ht..", "....frrrrrrf...t..",
          "....ffff.fff...t..", "....fff...ff...t..", "....fff...ff...t..", "....fff...fff..t..",
          "...kkkk...kkkk.t.."]
TAUREN_COLORS = {"w": "#e8dcc0", "f": "#7a4a2a", "e": "#101010", "n": "#c8a080", "y": "#e8c040", "a": "#3a5a8a",
                 "b": "#2a1a10", "r": "#c8a050", "h": "#5a3418", "k": "#2a1a10", "t": "#8a6a3a"}
TROLL = [".....rr.....", "....rrr.....", "....rr......", "...bbbb.....", "..bbebbb....", "..bbbbbbb...",
         "...wbbw.....", "....bb...o..", "..llllll.o..", ".bllllll.o..", ".b.llll.bo..", ".b.llll..o..",
         "...llll..o..", "...yyyy.....", "...bb.bb....", "...bb.bb....", "...bb..bb...", "...bb..bb...",
         "..kkk..kkk.."]
TROLL_COLORS = {"r": "#e02a2a", "b": "#3a7aa8", "e": "#ffd040", "w": "#f0e8d0", "l": "#5a4a2a", "o": "#8a5a2a",
                "y": "#c8a050", "k": "#2a1a10"}
GOBLIN = ["e........e", "ee.gggg.ee", ".eggyggye.", "..gggggg..", "..gwwwwg..", "...gggg...", "..vvvvvv..",
          ".gvvvvvvg.", "..vvvvvv..", "..bb..bb..", ".kkk..kkk."]
GOBLIN_COLORS = {"e": "#5a9a3a", "g": "#5a9a3a", "y": "#ffd040", "w": "#f0e8d0", "v": "#6a3a8a", "b": "#3a2a1a",
                 "k": "#2a1a10"}
WOLF = (["........gg...", "g.....ggggg..", "gg..ggggggegg", ".gggggggggggw", ".ggggggggggg.", ".gg.gg..gg.gg",
         ".gg.gg..gg.gg", ".kk.kk..kk.kk"],
        ["..............", "g.......gg...", ".g....ggggg..", ".gg.ggggggegg", ".gggggggggggw", ".gg.gg..gg.gg",
         ".gg.gg..gg.gg", ".kk.kk..kk.kk"])
WOLF_COLORS = {"g": "#5a5a62", "e": "#ffd040", "w": "#f0e8d0", "k": "#2a2a30"}
PLAYER = ["......hhh.........", ".....ggggg........", "....ggggggg.......", "....gggeggge......",
          "....ggggggg.......", "....ggwgggw.......", ".ww..ggggg..ww....", "PPPP.ggggg.PPPP...",
          "PPPPPaaaaaPPPPP...", ".PPPaaaaaaaPPPgx..", "..ggaaaaaaagg.gx..", "..gg.aaaaa.gg.gx..",
          "..gg.bbbbb.ggggxii", "..ss.rrrrr.....xiii", "....rrrrrrr....xiii", "....rr...rr....x.ii",
          "....gg...gg....x...", "....gg...gg....x...", "....gg...gg....x...", "....kk...kk........",
          "...kkk...kkk......."]
PLAYER_COLORS = {**GREEN_ORC, "g": "#3e7a24", "s": "#3e7a24", "i": "#d0d0dc", "P": "#8a8a96", "a": "#6a1a1a"}
CREST_ART = ["w.w.w", "wwwww", ".www.", "w.w.w", ".w.w."]


def P(u, v, z=0):
    return round(OX + 2 * (u - v)), round(OY + u + v - z)


def box(c, u, v, w, d, h, z=0, look=TIMBER, **kw):
    x, y = P(u, v, z + h)
    return c.iso_box(x, y, w, d, h, top=look["top"], left=look["left"], right=look["right"], **kw)


def breathe(art, row):
    """The idle-breath keyframe of a sprite: one row repeated, so everything above it rises a pixel."""
    return art[:row] + [art[row]] + art[row:]


def stand(c, art, colors, u, v, z=0, *, flip=False, up=0):
    x, y = P(u, v, z)
    c.sprite(x - len(art[0]) // 2, y - len(art) + 1 - up, art, colors, outline=INK, shade=True, flip=flip)
    return x, y - len(art)


def idle(t, k, n=2):
    return (t * n + k * 0.37) % 1 < 0.5


def canyon(c, t):
    c.gradient(0, 0, 320, 70, ["#0c040a", "#1e0810", "#3a1010", "#5a1a10"])
    rnd = random.Random(3)
    right = [P(0, 0, 0)]
    for u in range(0, 81, 5):
        right.append(P(u, 0, 34 + rnd.randint(0, 22)))
    right += [P(80, 0, 0)]
    c.polygon(right, fill=ROCK_R)
    left = [P(0, 0, 0)]
    for v in range(0, 61, 5):
        left.append(P(0, v, 30 + rnd.randint(0, 22)))
    left += [P(0, 60, 0)]
    c.polygon(left, fill=ROCK_L)
    for z in range(6, 50, 7):
        c.line(*P(0, 0, z), *P(80, 0, z + 2), STRATA)
        c.line(*P(0, 0, z), *P(0, 60, z + 3), STRATA)
    c.polygon([P(0, 0), P(80, 0), P(80, 60), P(0, 60)], fill=GROUND)
    c.polygon([P(0, 0), P(80, 0), P(80, 60), P(0, 60)], fill=GRAIN, pattern="grain")
    for _ in range(26):
        x, y = P(rnd.uniform(4, 76), rnd.uniform(4, 58))
        c.rect(x, y, rnd.randint(2, 4), 2, "#5e3020")
        c.px(x, y, "#7a4430")


def lava(c, t):
    lake = [(34, 6), (50, 2), (68, 8), (72, 20), (66, 32), (50, 35), (36, 29), (30, 18)]
    c.polygon([P(u + (1 if u > 50 else -1) * 2, v + (2 if v > 20 else -2)) for u, v in lake], fill=CRUST)
    c.polygon([P(u, v) for u, v in lake], fill=LAVA)
    river = [(62, 31), (66, 31), (80, 45), (80, 50), (76, 50)]
    c.polygon([P(u, v) for u, v in river], fill=LAVA)
    rnd = random.Random(8)
    for k in range(16):
        u0, v0 = rnd.uniform(36, 64), rnd.uniform(6, 30)
        dv = (v0 + t * 6) % 26 + 6
        x, y = P(u0, dv)
        c.polygon([(x - 4, y), (x, y - 2), (x + 5, y), (x, y + 2)], fill=LAVA_D, pattern="dense")
    c.shimmer(150, 60, 160, 90, t, LAVA_HI, n=40, seed=4, cycles=2, length=(1, 4), on=LAVA)


def palisade(c, t):
    for k, v in enumerate(range(18, 60, 3)):
        x, y = P(4, v)
        h = 16 + (k % 3) * 2
        c.rect(x - 1, y - h, 3, h, "#5a3a20")
        c.vline(x - 1, y - h, h, "#7a5230")
        c.polygon([(x - 1, y - h), (x + 1, y - h - 4), (x + 2, y - h)], fill="#b8b0a0")
    for z in (5, 12):
        c.line(*P(4, 18, z), *P(4, 59, z), "#2a2a30")


def tent(c, u, v, r, col, t):
    x, y = P(u, v)
    c.polygon([(x - r * 2, y), (x, y - r * 2), (x + r * 2, y)], fill=col)
    c.polygon([(x, y - r * 2), (x + r * 2, y), (x, y + r // 2)], fill="#6a4a2e")
    c.polygon([(x - r * 2, y), (x, y - r * 2), (x, y + r // 2)], fill=col)
    c.polygon([(x - 3, y + 1), (x, y - 6), (x + 3, y + 1)], fill="#1a0e08")
    for d in (-1, 1):
        c.line(x, y - r * 2, x + d * 4, y - r * 2 - 6, CREST)
        c.px(x + d * 4, y - r * 2 - 7, CREST)
    c.line(x - r * 2 + 3, y - 2, x - 2, y - r * 2 + 4, "#5a3a20")


def longhouse(c, t):
    hall = box(c, 6, 28, 12, 8, 10, look=TIMBER)
    for b in range(2, 10, 3):
        c.line(*hall.left(0, b), *hall.left(12, b), "#4a2e1a")
    c.polygon([hall.left(5, 4), hall.left(7, 4), hall.left(7, 10), hall.left(5, 10)], fill="#ff9a3a")
    c.polygon([P(5, 27, 10), P(19, 27, 10), P(19, 32, 18), P(5, 32, 18)], fill="#3a2418")
    c.polygon([P(5, 32, 18), P(19, 32, 18), P(19, 37, 10), P(5, 37, 10)], fill="#5a3a26")
    for u in range(6, 20, 3):
        x, y = P(u, 32, 18)
        c.line(x, y, x + 1, y - 5, CREST)


def banner(c, u, v, t, k):
    x, y = P(u, v)
    c.rect(x, y - 34, 2, 34, "#3a2a1a")
    c.polygon([(x - 3, y - 35), (x + 5, y - 35), (x + 1, y - 39)], fill="#9a9aa8")
    sway = 1 if idle(t, k) else 0
    c.polygon([(x + 2, y - 32), (x + 12, y - 32 + sway), (x + 12, y - 14 + sway), (x + 7, y - 17), (x + 2, y - 14)],
              fill=BANNER)
    c.line(x + 2, y - 32, x + 12, y - 32 + sway, "#1a0a0a")
    c.line(x + 12, y - 32 + sway, x + 12, y - 14 + sway, "#1a0a0a")
    c.sprite(x + 5, y - 29 + sway, CREST_ART, {"w": CREST})


def brazier(c, u, v, t, seed):
    x, y = P(u, v)
    c.line(x - 3, y, x, y - 6, "#2a2a30")
    c.line(x + 3, y, x, y - 6, "#2a2a30")
    c.rect(x - 4, y - 9, 9, 3, "#3a3a44")
    c.hline(x - 4, y - 9, 9, "#6a6a78")
    f = flicker(t, seed=seed)
    h = 4 + round(f * 4)
    c.polygon([(x - 3, y - 9), (x, y - 9 - h - 2), (x + 3, y - 9)], fill="#ff7a1a")
    c.polygon([(x - 1, y - 9), (x, y - 9 - h), (x + 2, y - 9)], fill=LAVA_HI)
    c.particles(x - 2, y - 14 - h, 4, 3, t, "embers", n=5, seed=seed, speed=16, spread=40)
    return x, y - 10


def drum(c, t):
    box(c, 14, 36, 8, 8, 3, look=TIMBER)
    x, y = P(18, 40, 3)
    c.rect(x - 6, y - 8, 13, 7, "#8a5a32")
    c.circle(x + 0.5, y - 9, 6, "#d8c0a0")
    c.circle(x + 0.5, y - 9, 6, "#d8c0a0")
    c.hline(x - 6, y - 4, 13, "#5a1a10")
    beat = (t * 4) % 1 < 0.3
    art = [r for r in ORC]
    stand(c, art, GREY_ORC, 16, 38, z=3, up=0 if beat else 1)
    if beat:
        c.particles(x - 4, y - 12, 8, 2, phase((t * 4) % 1, 0, 0.3), "dust", n=4, seed=2, colors=["#f0e8d0"])


def tower(c, t):
    x, y = P(2, 40)
    for dx in (-6, 6):
        c.line(x + dx, y, x + dx // 3, y - 46, "#4a3020")
    for k in range(5):
        yy = y - 8 - k * 9
        c.line(x - 6 + k, yy, x + 6 - k, yy - 8, "#3a2418")
        c.line(x + 6 - k, yy, x - 6 + k, yy - 8, "#3a2418")
    c.rect(x - 4, y - 48, 9, 3, "#5a3a22")
    c.polygon([(x - 7, y - 48), (x + 8, y - 48), (x + 6, y - 54), (x - 5, y - 54)], fill="#5a3a22")
    for k in range(5):
        c.polygon([(x - 6 + k * 3, y - 54), (x - 5 + k * 3, y - 59), (x - 4 + k * 3, y - 54)], fill=CREST)
    f = flicker(t, seed=9)
    c.polygon([(x - 3, y - 54), (x, y - 62 - round(f * 4)), (x + 3, y - 54)], fill="#ff7a1a")
    c.particles(x - 2, y - 66, 4, 3, t, "embers", n=6, seed=6, speed=18, spread=40)
    return x, y - 56


def stall(c, t):
    box(c, 12, 52, 8, 5, 6, look=TIMBER)
    c.polygon([P(11, 51, 14), P(21, 51, 14), P(21, 58, 10), P(11, 58, 10)], fill="#8a1a1a")
    for k in range(5):
        c.line(*P(11 + k * 2.5, 58, 10), *P(11 + k * 2.5, 58, 8), "#e8dcc0")
    for k, col in enumerate(("#e8c040", "#3aa8e8", "#c83a8a", "#e8e8e8")):
        x, y = P(13 + k * 2, 57, 6)
        c.rect(x - 1, y - 2, 3, 2, col)
    stand(c, breathe(GOBLIN, 7) if idle(t, 5, 4) else GOBLIN, GOBLIN_COLORS, 18, 60)
    x, y = P(16, 61)
    c.text(x - 6, y + 2, "WARES", "#ffd040", outline=INK, check=False)


def boss(world, t):
    """The magma lord, waist-deep in the lake: shaded parts on a keyed layer, pasted with an outline."""
    d = world.sub(320, 180, bg=KEY)
    heave = [0, 0, 1, 1, 2, 1, 1, 0][int(t * 8) % 8]
    u = -heave - 8

    def part(shades=BASALT, width=2, depth=3):
        d.form(MARK, shades, light=(0, 1), width=width, depth=depth)

    def limb(pts, w0, w1):
        for k in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[k], pts[k + 1]
            a = w0 + (w1 - w0) * k / (len(pts) - 1)
            b = w0 + (w1 - w0) * (k + 1) / (len(pts) - 1)
            ln = math.hypot(x1 - x0, y1 - y0) or 1
            nx, ny = -(y1 - y0) / ln, (x1 - x0) / ln
            d.polygon([(round(x0 + nx * a), round(y0 + ny * a)), (round(x1 + nx * b), round(y1 + ny * b)),
                       (round(x1 - nx * b), round(y1 - ny * b)), (round(x0 - nx * a), round(y0 - ny * a))],
                      fill=MARK)
            d.circle(x1, y1, b, MARK)
        d.circle(*pts[0], w0, MARK)

    def cracks(x, y, w, h, n, seed):
        rnd = random.Random(seed)
        for _ in range(n):
            cx, cy = x + rnd.uniform(0, w), y + rnd.uniform(0, h)
            for _ in range(rnd.randint(3, 5)):
                nx, ny = cx + rnd.uniform(-6, 6), cy + rnd.uniform(1, 6)
                d.line(round(cx), round(cy), round(nx), round(ny), "#ff7a1a")
                d.px(round(cx), round(cy), LAVA_HI)
                cx, cy = nx, ny

    limb([(250, 50 + u), (272, 66 + u), (264, 88 + u)], 11, 8)
    part()
    cracks(254, 56 + u, 14, 26, 3, 1)
    d.polygon([(196, 100), (248, 100), (262, 62 + u), (254, 42 + u), (222, 36 + u), (190, 42 + u), (182, 62 + u)],
              fill=MARK)
    part(depth=5)
    for k, (x0, y0) in enumerate(((186, 44), (196, 38), (248, 38), (258, 44))):
        d.polygon([(x0 - 4, y0 + 4 + u), (x0 + (-3 if k < 2 else 3), y0 - 10 + u), (x0 + 4, y0 + 4 + u)], fill=MARK)
    part(width=1, depth=1)
    cracks(192, 46 + u, 56, 50, 9, 2)
    d.polygon([(208, 24 + u), (236, 24 + u), (240, 34 + u), (234, 46 + u), (222, 50 + u), (210, 46 + u),
               (204, 34 + u)], fill=MARK)
    part()
    cracks(208, 26 + u, 26, 16, 2, 3)
    d.polygon([(186, 98 + u), (190, 96 + u), (166, 64 + u), (162, 66 + u)], fill=MARK)
    part(IRON, width=1, depth=1)
    d.polygon([(146, 62 + u), (166, 48 + u), (180, 66 + u), (160, 80 + u)], fill=MARK)
    part(IRON, width=2, depth=4)
    rune = LAVA_HI if blink(t, 2, duty=0.6) else "#ff7a1a"
    d.line(156, 62 + u, 168, 56 + u, rune)
    d.line(160, 68 + u, 172, 62 + u, rune)
    d.line(162, 58 + u, 166, 66 + u, rune)
    limb([(194, 50 + u), (174, 64 + u), (178, 82 + u)], 11, 8)
    part()
    cracks(176, 56 + u, 16, 24, 3, 4)
    d.circle(178, 82 + u, 6, MARK)
    part()
    world.paste(d, 0, 0, key=KEY, outline=INK)
    glow = LAVA_HI if blink(t, 4, duty=0.7) else "#ffe8a0"
    for pts in (((210, 52), (216, 62), (212, 76)), ((234, 50), (230, 62), (238, 74)), ((222, 78), (220, 96)),
                ((198, 66), (204, 80)), ((246, 64), (244, 82)), ((262, 70), (264, 80))):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            world.line(x0, y0 + u, x1, y1 + u, "#ff7a1a")
    world.circle(222, 62 + u, 4, glow)
    world.circle(222, 62 + u, 2, "white")
    for ex in (213, 226):
        world.rect(ex, 32 + u, 6, 2, "#fff4b0")
        world.line(ex - 1, 30 + u, ex + 6, 29 + u + (1 if ex > 220 else 0), "#ff9a2a")
    world.hline(216, 41 + u, 12, "#ff7a1a")
    for k in range(8):
        x = 207 + k * 4
        h = 8 + round(flicker(t, seed=k, cycles=(4, 8, 12)) * 8) + (4 if 2 < k < 6 else 0)
        world.polygon([(x - 2, 26 + u), (x + 1, 26 + u - h), (x + 3, 26 + u)], fill="#ff6a1a")
        world.polygon([(x - 1, 26 + u), (x + 1, 26 + u - h + 4), (x + 2, 26 + u)], fill=LAVA_HI)
    for k in range(6):
        x = 212 + k * 4
        h = 6 + round(flicker(t, seed=20 + k, cycles=(4, 8, 12)) * 7)
        world.polygon([(x - 2, 46 + u), (x + 1, 46 + u + h), (x + 3, 46 + u)], fill="#ff7a1a")
        world.polygon([(x - 1, 46 + u), (x + 1, 46 + u + h - 3), (x + 2, 46 + u)], fill=LAVA_HI)
    world.particles(190, 0, 70, 30, t, "embers", n=24, seed=5, speed=26, spread=50, cycles=2)
    for k in range(3):
        x0 = 196 + k * 22
        world.hline(x0, 100 + (k % 2), 14, LAVA_HI)
    world.circle(222, 101, 3, LAVA_HI)


SLOTS = [("sword", None), ("shield", None), ("fire", 0.0), ("heart", "red"), ("bolt", "gold"), ("star", "gold"),
         ("frost", 0.5), ("clock", "cyan"), ("disc", "sky"), ("note", "violet"), ("temp", "orange"),
         ("package", "orange")]
ICONS = {
    "sword": (["......w", ".....w.", "....w..", "g..w...", ".gw....", ".gg....", "g..g..."], {"w": "white", "g": "gold"}),
    "shield": (["sssssss", "swwswws", "swwswws", "sssssss", ".swwws.", "..sws..", "...s..."],
               {"s": "#c8ccd4", "w": "#2a5aa8"}),
    "fire": ([".o.....", ".oo.o..", "ooooo..", "ooyyoo.", "oyyyyo.", "oyyyyo.", ".oyyo.."], {"o": "orange", "y": "gold.light"}),
    "frost": (["...c...", ".c.c.c.", "..ccc..", "ccccccc", "..ccc..", ".c.c.c.", "...c..."], {"c": "cyan.light"}),
}
CHAT = [("[RAID] VRAKA: HEAL THE TANK!", "#ff7f00"), ("[GUILD] ZUL'KASH: WHO PULLED?!", "#40ff40"),
        ("[2. TRADE] GRIZZIK: EMBERSTEEL 5G", "#ffc0a0"), ("THE MAGMA KING YELLS: KNEEL!", "#ff4040"),
        ("YOUR CLEAVE HITS FOR 3,412.", "#ffff60")]
QUESTS = [("THE MOLTEN DEEP", [("- MAGMA KING: 0/1", "white")]),
          ("IRON FOR THE HOLD", [("- EMBERSTEEL: 6/10", "white")])]
XP = 0.68
HITS = [(0.05, "3,412", "#ffff60", 0), (0.3, "1,208", "white", 1), (0.55, "6,950", "#ffff60", 2),
        (0.8, "2,117", "white", 3)]


def unit_frame(c, x, y, name, level, hp, mp, *, hostile=False, portrait=None):
    c.circle(x + 12, y + 12, 12, "#c8a040")
    c.circle(x + 12, y + 12, 11, "#101418")
    if portrait:
        portrait(x + 8, y + 7)
    plate = c.bevel(x + 24, y + 2, 64, 22, "#14181e", light="#5a5040", dark="#0a0c10")
    c.rect(plate.x, plate.y, plate.w, 7, "#a07a20" if hostile else "#1a3a8a")
    c.text(plate.x + 2, plate.y + 1, name, "white")
    c.rect(plate.x, plate.y + 7, plate.w, 6, "#0a2a0a")
    c.rect(plate.x, plate.y + 7, round(plate.w * hp), 6, "#20c020")
    c.rect(plate.x, plate.y + 14, plate.w, 5, "#0a0a2a")
    if mp is not None:
        c.rect(plate.x, plate.y + 14, round(plate.w * mp), 5, "#2a4ae0")
    c.text(plate.x + plate.w // 2, plate.y + 8, f"{round(hp * 100)}%", "white", align="center")
    c.circle(x + 5, y + 21, 6, "#c8a040")
    c.circle(x + 5, y + 21, 5, "#101418")
    c.text(x + 5, y + 19, str(level), "gold", align="center")


def minimap(c, t):
    cx, cy, r = 288, 36, 26
    c.text(288, 2, "IRONTUSK HOLD", "gold", align="center", outline="#101418")
    c.circle(cx, cy, r + 2, "#c8a040")
    c.circle(cx, cy, r + 1, "#5a4a20")
    sub = c.sub(2 * r, 2 * r, bg="#ff00ff")
    sub.gradient(0, 0, 2 * r, 2 * r, ["#4a1e14", "#5e2a1a"])
    sub.polygon([(20, 52), (30, 52), (34, 10), (30, 10)], fill="#7a4a30")
    sub.rect(6, 30, 16, 12, "#6a4428")
    sub.circle(36, 16, 9, "#f05a1a")
    sub.circle(14, 22, 6, "#2a100a")
    for yy in range(2 * r):
        for xx in range(2 * r):
            if (xx + 0.5 - r) ** 2 + (yy + 0.5 - r) ** 2 >= r * r:
                sub.px(xx, yy, "#ff00ff")
    c.paste(sub, cx - r, cy - r, key="#ff00ff")
    c.text(cx + 4, cy - 26, "!", "gold" if blink(t, 2) else "gold.dark", font="large")
    c.rect(cx + 4, cy - 12, 3, 3, "red" if blink(t, 4) else "#ff9a5a")
    c.sprite(cx - 2, cy - 2, ["..#..", ".###.", "##.##"], {"#": "white"})
    c.text(262, 64, "21:40", "text", outline="#101418")
    c.text(318, 64, "N", "gold", align="right", outline="#101418")


def tracker(c):
    y = 76
    for title, lines in QUESTS:
        c.text(236, y, title, "#ffd200", outline="#101418")
        y += 8
        for line, col in lines:
            c.text(240, y, line, col, outline="#101418")
            y += 8
        y += 3


def chat(c):
    y = 113
    c.rect(2, y, 138, 44, "#101418")
    c.pattern(2, y, 138, 44, "#22303a", "checker")
    c.rect(2, y, 34, 8, "#20262e")
    c.text(5, y + 2, "GENERAL", "gold")
    c.text(42, y + 2, "COMBAT LOG", "dim")
    for k, (line, col) in enumerate(CHAT):
        c.text(4, y + 10 + k * 7, line, col)


def action_bar(c, t):
    x0, y0, slot = 84, 165, 13
    c.rect(x0 - 3, y0 - 6, 12 * slot + 5, 21, "#2a2622")
    c.hline(x0 - 3, y0 - 6, 12 * slot + 5, "#5a5040")
    c.rect(x0, y0 - 4, 12 * slot - 1, 3, "#1a0a2a")
    c.rect(x0, y0 - 4, round((12 * slot - 1) * XP), 3, "#8a3ad0")
    c.hline(x0, y0 - 4, round((12 * slot - 1) * XP), "#b07af0")
    for k in range(1, 20):
        c.px(x0 + k * (12 * slot - 1) // 20, y0 - 4, "#1a0a2a")
    for i, (name, extra) in enumerate(SLOTS):
        sx = x0 + i * slot
        r = c.bevel(sx, y0, 12, 12, "#101418", light="#6a6050", dark="#0a0a0a")
        if name in ICONS:
            art, cols = ICONS[name]
            c.sprite(r.x + 1, r.y + 1, art, cols)
        else:
            c.icon(r.x + 1, r.y + 1, name, extra or "white")
        if name in ("fire", "frost"):
            frac = 1 - (t * 2 + extra) % 1
            c.cooldown(r.x, r.y, r.w, r.h, frac, amount=0.75)
    for k, label in enumerate(("CHR", "SPL", "TAL", "QST", "MNU")):
        bx = 248 + k * 14
        c.bevel(bx, 168, 13, 10, "#5a2a1a", light="#c8a040", dark="#2a1408")
        c.text(bx + 7, 170, label[0], "gold.light", align="center")


def cast_bar(c, t):
    x, y, w = 118, 29, 66
    c.rect(x - 1, y - 1, w + 2, 9, "#0a0806")
    c.rect(x, y, w, 7, "#2a1a08")
    c.rect(x, y, round(w * ((t * 2) % 1)), 7, "#e8a020")
    c.hline(x, y, round(w * ((t * 2) % 1)), "#ffd060")
    c.text(x + w // 2, y + 1, "MOLTEN WRATH", "white", align="center")


def raid(c, t):
    for i, (u, v) in enumerate(((42, 47), (22, 47))):
        if i == 1:
            stand(c, WOLF[0 if idle(t, 4) else 1], WOLF_COLORS, u, v)
    stand(c, breathe(TROLL, 9) if idle(t, 1) else TROLL, TROLL_COLORS, 26, 34)
    stand(c, breathe(ORC, 10) if idle(t, 2) else ORC, GREEN_ORC, 36, 31)
    stand(c, breathe(TAUREN, 11) if idle(t, 3) else TAUREN, TAUREN_COLORS, 40, 42)
    stand(c, breathe(ORC, 10) if idle(t, 6) else ORC, GREY_ORC, 50, 42)
    stall(c, t)
    stand(c, breathe(PLAYER, 11) if idle(t, 7) else PLAYER, PLAYER_COLORS, 56, 52)


def spells(c, t):
    tx, ty = P(26, 34)
    for k in range(3):
        c.projectile(tx + 6, ty - 12, 214, 64, ((t * 3) + k / 3) % 1, "#f0e8d0", trail=["#c8b080", "#8a7a5a"],
                     length=5, shards=4, life=0.2, seed=k)
    hx, hy = P(40, 42)
    kx, ky = P(36, 31)
    if blink(t, 2, duty=0.7):
        c.line(hx + 6, hy - 18, kx, ky - 12, "#7aff7a")
        c.line(hx + 6, hy - 17, kx, ky - 11, "#2ac82a")
    c.particles(kx - 6, ky - 22, 12, 22, t, "wisps", n=10, seed=4, speed=14, colors=["white", "#7aff7a", "#2ac82a"])
    strike = (t * 4) % 1
    if strike < 0.3:
        c.particles(kx + 8, ky - 14, 4, 4, phase(strike, 0, 0.3), "sparks", n=10, seed=int(t * 4), burst=True,
                    speed=14)
    fb = phase(t, 0.62, 0.8)
    head = c.projectile(204, 50, kx + 2, ky - 10, fb, LAVA_HI, trail=["#ff9a2a", "#ff5a1a", "#8a2a0a"], length=6,
                        width=3, shards=20, life=0.4)
    if head:
        c.circle(*head, 3, "#ff7a1a")
        c.circle(*head, 1.5, "white")
    c.particles(kx - 8, ky - 16, 16, 12, phase(t, 0.8, 0.98), "embers", n=16, seed=9, burst=True, spread=160,
                speed=20)


def draw(c, t):
    canyon(c, t)
    c.glow(222, 100, 74, "#ff4a1a", amount=0.32, levels=2, squash=2.0)
    lava(c, t)
    palisade(c, t)
    beacon = tower(c, t)
    longhouse(c, t)
    tent(c, 12, 46, 6, HIDE["left"], t)
    tent(c, 6, 54, 5, "#9a7050", t)
    banner(c, 8, 24, t, 0)
    banner(c, 26, 20, t, 1)
    banner(c, 22, 54, t, 2)
    fires = [brazier(c, 22, 30, t, 1), brazier(c, 30, 46, t, 2), brazier(c, 46, 54, t, 3)]
    drum(c, t)
    boss(c, t)
    c.heat(150, 88, 140, 12, t, amp=1)
    c.glyph(222, 101, 36, t, "#ff2a2a", squash=4.5, runes=0, inner=0.93)
    raid(c, t)
    c.particles(150, 40, 140, 70, t, "embers", n=22, seed=11, speed=50, spread=30, cycles=2)
    spells(c, t)
    for start, text, col, k in HITS:
        p = phase((t - start) % 1, 0, 0.35)
        if 0 < p < 1:
            c.text(196 + k * 6, 82 - round(p * 26), text, col, align="center", outline=INK)
    if blink(t, 2, duty=0.75):
        c.text(160, 47, "THE MAGMA KING SUMMONS A FIRESTORM!", "#ff3a2a", font="large", align="center",
               outline=INK)

    def face(x, y):
        c.sprite(x, y, ["..hhh....", ".ggggg...", "ggegeggg.", "ggggggg..", "gwgggwg..", ".PgggP...",
                        "PPaaaPP.."], {**GREEN_ORC, "g": "#3e7a24"})

    def king(x, y):
        c.sprite(x - 1, y - 2, [".o.o.o.o.", "ooyoyoyo.", "kkkkkkkk.", "kyykkyyk.", "kkkkkkkk.", ".kooook..",
                                "..kkkk..."], {"o": "#ff6a1a", "y": LAVA_HI, "k": "#3a1a12"})

    unit_frame(c, 2, 2, "KRAGG", 60, 0.71, 0.58, portrait=face)
    unit_frame(c, 94, 2, "THE MAGMA KING", "??", 0.42, None, hostile=True, portrait=king)
    cast_bar(c, t)
    minimap(c, t)
    tracker(c)
    chat(c)
    action_bar(c, t)


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=8, seamless=True, poster=0.68)
