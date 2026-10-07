"""A point-and-click adventure in the early-90s style, as an isometric diorama: a stilted harbour town at
night with a lamp-lit tavern, a crooked shack, a jetty and a rowing boat, palms on a sandbar and a ghost
ship glowing green in the fog behind. Its undead captain looms on the pier over a young hero while the
locals idle about, above the verb interface: a sentence line, nine verbs and an icon inventory.
Everything is made up."""

import math
import random
from pathlib import Path

from pixelkit import animate, blink, flicker, phase, reveal

SCENE_H = 120
OX, OY = 178, 34
HORIZON = 46
SKY = ["#0c0822", "#18104a", "#1e2c66", "#1c4866"]
SEA, SEA_D, SEA_HI = "#0e3440", "#0a2632", "#2e6a72"
LAMP, LAMP_HOT = "#ffa040", "#ffe08a"
GHOST, GHOST_HI, GHOST_D = "#5ae89a", "#c0ffd8", "#1e7a4e"
INK = "#0a0810"
DECK = {"top": "#8a5a30", "left": "#6a4220", "right": "#4a2e16"}
PLANK = {"top": "#7a4e2a", "left": "#5a3a1c", "right": "#3e2812"}
TAVERN = {"top": "#6a4a2a", "left": "#8a5432", "right": "#603a22"}
SHACK = {"top": "#4a5a48", "left": "#5a6a52", "right": "#3e4a3a"}
CRATE = {"top": "#b08048", "left": "#8a6034", "right": "#684424"}
SAND = {"top": "#c8a868", "left": "#a08048", "right": "#7a5e34"}
BOAT = {"top": "#3a2412", "left": "#7a4a26", "right": "#5a3418"}

HERO = (["...hhhh...", "..hhhhhh..", "..sssshhh.", ".sesssh.h.", ".ssssss.h.", "..dddds.h.", "..dddd....",
         "..cwwcc...", ".ccwwccc..", ".cccgccc..", ".cc.gc.cc.", ".cc.cc.cc.", ".ss.gc.ss.", "...cccc...",
         "...cccc...", "...tt.tt..", "...tt.tt..", "...tt.tt..", "..kkk.kkk."],
        ["...hhhh...", "..hhhhhh..", "..sssshhh.", ".sesssh..h", ".ssssss..h", "..dddds..h", "..dddd....",
         "..cwwcc...", ".ccwwccc..", ".cccgccc..", ".cc.gc.cc.", ".cc.cc.cc.", ".ss.gc.ss.", "...cccc...",
         "...cccc...", "...tt.tt..", "...tt.tt..", "...tt.tt..", "..kkk.kkk."])
HERO_COLORS = {"h": "#e8b850", "s": "#f0b88a", "e": "#101018", "d": "#9a6a30", "w": "#f0ece0", "c": "#2a50c0",
               "g": "#e8c050", "t": "#c0a070", "k": "#3a2010"}
FATTY = (["...rrrr.....", "..rrrrrrr...", "..ssssss.r..", "..kesses....", "..ssssss....", "..sbbbbs....",
          ".wawawawa...", "wawawawawa..", "wawawawawam.", "sawawawawam.", ".wawawawas..", ".awawawaw...",
          ".nnnnnnnn...", ".pppp.pppp..", ".pppp.pppp..", "..ppp..ppp..", "..kkk..kkk.."],
         ["...rrrr.....", "..rrrrrrr...", "..ssssss.r..", "..kesses.mm.", "..ssssss.mm.", "..sbbbbs.s..",
          ".wawawawas..", "wawawawawa..", "wawawawawa..", "sawawawawa..", ".wawawawa...", ".awawawaw...",
          ".nnnnnnnn...", ".pppp.pppp..", ".pppp.pppp..", "..ppp..ppp..", "..kkk..kkk.."])
FATTY_COLORS = {"r": "#d02a2a", "s": "#e8a878", "k": "#101010", "e": "#101010", "b": "#6a4a30", "w": "#f0ece0",
                "a": "#2a3a8a", "m": "#c8a050", "n": "#5a3418", "p": "#7a6a4a"}
SKINNY = ["..nnnnn...", ".nnnnnnn..", "nnnnnnnnnn", "..ssss....", "..kkss....", "..ssss....", "..sbbs....",
          "..gggg....", ".gggggg...", ".gg.gggs..", ".gg.ggg...", ".ss.ggg...", "...gggg...", "...yyyy...",
          "...pp.pp..", "...pp.pp..", "...pp.pp..", "...pp..p..", "..kkk.kk.."]
SKINNY_COLORS = {"n": "#5a3a1c", "s": "#d8a070", "k": "#101010", "b": "#4a3a2a", "g": "#2a7a4a",
                 "y": "#e8c050", "p": "#b8a888"}
PARROT = ([".rr..", "rrry.", "brr..", "brb..", "..r.."], ["brr..", "brry.", ".rr..", ".rb..", "..r.."])
COOK = (["..wwww....", ".wwwwww...", "..wwww....", "..ssss....", "..sess....", "..ssss....", "...ss.....",
         "..wwwwss..", ".wwwwww.s.", ".wwwwwws..", ".wwaaww...", "..aaaa....", "..aaaa....", "..pp.pp...",
         "..pp.pp...", "..kk.kk..."],
        ["..wwww....", ".wwwwww...", "..wwww....", "..ssss....", "..sess....", "..ssss....", "...ss.....",
         "..wwwww...", ".wwwwwws..", ".wwwwww.s.", ".wwaaww...", "..aaaa....", "..aaaa....", "..pp.pp...",
         "..pp.pp...", "..kk.kk..."])
COOK_COLORS = {"w": "#f0f0e8", "s": "#e8b088", "e": "#101010", "a": "#c8c8d8", "p": "#4a4a6a", "k": "#2a1a10"}
MONKEY = ([".bbb....", "bfffb...", "bfkfb...", ".bffb...", ".bbbbb..", "bbbbbb.t", ".b..b.t.", "......t."],
          [".bbb....", "bfffb...", "bfkfb...", ".bffb..t", ".bbbbb.t", "bbbbbbt.", ".b..b...", "........"])
CAPTAIN = (["......kkkk........", "....kkkwwkkk......", "..kkkkkwwkkkkk....", "kkkkkkkkkkkkkkkk..",
            "yykkkkkkkkkkkkyy..", "....zzzzzzzz......", "....zeezzeez......", "....zzzzzzzz......",
            "...HGzkkkkzGH.....", "..HGGGGGGGGGGH....", ".HGGHGGGGGHGGGH...", ".GGGGGHGGGGGGG....",
            "ccGGHGGGGGHGGccc..", "cccGGGGGGGGGcccczz", "ccccGGGGGGGcccczzz", "cccccGGHGGccccc...",
            "cccccyGGGycccc....", "cccccrrrrrcccc....", "cccccyrrrycccc....", "ccccccccccccc.....",
            "cccccycccyccccc...", "ccccccccccccccc...", "cccccycccyccccc...", "ccccccccccccccc...",
            "ccccccccccccccc...", ".cccccc.ccccccc...", ".cccccc..cccccc...", "..bbbb....bbbb....",
            "..bbbb....bbbb....", ".bbbbb....bbbbb..."],
           ["......kkkk........", "....kkkwwkkk......", "..kkkkkwwkkkkk....", "kkkkkkkkkkkkkkkk..",
            "yykkkkkkkkkkkkyy..", "....zzzzzzzz......", "....zeezzeez......", "....zzzzzzzz......",
            "...GHzkkkkzHG.....", "..GHGGGGGGGGHG....", ".GGHGGGGHGGGHGG...", "..GGGHGGGGGHGGG...",
            "ccGHGGGGHGGGGccc..", "cccGGGGHGGGGcccczz", "ccccGGGGGGHcccczzz", "cccccGHGGGccccc...",
            "cccccyGGGycccc....", "cccccrrrrrcccc....", "cccccyrrrycccc....", "ccccccccccccc.....",
            "cccccycccyccccc...", "ccccccccccccccc...", "cccccycccyccccc...", "ccccccccccccccc...",
            "ccccccccccccccc...", ".cccccc.ccccccc...", ".cccccc..cccccc...", "..bbbb....bbbb....",
            "..bbbb....bbbb....", ".bbbbb....bbbbb..."])
CAPTAIN_COLORS = {"k": "#14101c", "w": "#e8e0c8", "y": "#e8c050", "z": "#7aa88a", "e": GHOST_HI, "H": GHOST_HI,
                  "G": GHOST, "c": "#241c3a", "r": "#8a1a2a", "b": "#0e0a14"}
LINES = [("YE CAN'T HIDE IN THERE FOREVER, WHELP! BLACKGRIM ALWAYS COLLECTS!", GHOST),
         ("I'M NOT HIDING. I'M... BROWSING THE GROG.", "white")]
VERBS = [["GIVE", "PICK UP", "USE"], ["OPEN", "LOOK AT", "PUSH"], ["CLOSE", "TALK TO", "PULL"]]
ITEMS = {
    "DOLL": (["..hhh..", ".hsssh.", ".sesesh", "..sss..", "pcccccp", ".ccccc.", ".cc.cc.", ".c...c."],
             {"h": "#3a2010", "s": "#c8a070", "e": "#101010", "c": "#5a7a3a", "p": "#c0c0c0"}),
    "MAP": (["pppppppp.", "p..x...p.", "p.--..pp.", "p...x.p..", "pppppp..."],
            {"p": "#e8d8a0", "x": "#c02a2a", "-": "#8a6a3a"}),
    "BONE": (["ww.....ww", ".wwwwwww.", "ww.....ww"], {"w": "#e8e0c8"}),
    "COIN": ([".yyy.", "yyYyy", "yYyYy", "yyYyy", ".yyy."], {"y": "#e8b830", "Y": "#fff0a0"}),
    "SHOVEL": (["......mm", ".....mm.", "....w...", "...w....", "..w.....", "mmm.....", "mmm.....", ".m......"],
               {"m": "#8a8a96", "w": "#7a4a22"}),
    "BOTTLE": (["..k..", "..g..", ".ggg.", "ggggg", "gGggg", "ggggg", "ggggg"], {"k": "#7a4a22", "g": "#2a8a4a",
                                                                                "G": "#8ae8a8"}),
}


def P(u, v, z=0):
    return round(OX + 2 * (u - v)), round(OY + u + v - z)


def box(c, u, v, w, d, h, z=0, look=DECK, **kw):
    x, y = P(u, v, z + h)
    return c.iso_box(x, y, w, d, h, top=look["top"], left=look["left"], right=look["right"], **kw)


def stand(c, art, colors, u, v, z=6, *, flip=False, shade=True):
    """A sprite with its feet centred on the iso point (u, v, z)."""
    x, y = P(u, v, z)
    c.sprite(x - len(art[0]) // 2, y - len(art) + 1, art, colors, outline=INK, shade=shade, flip=flip)


def sky(c, t):
    c.gradient(0, 0, 320, HORIZON, SKY)
    rnd = random.Random(6)
    for _ in range(46):
        x, y = rnd.randrange(320), rnd.randrange(HORIZON - 10)
        c.px(x, y, "#f0e8ff" if blink(t, 2, offset=rnd.random(), duty=0.75) else "#5a5a8a")
    c.glow(292, 14, 20, "#a8b8a0", amount=0.3, levels=2, region=(0, 0, 320, HORIZON))
    c.circle(292, 14, 8, "#f0f0c8")
    c.circle(289, 12, 2, "#c8c8a0")
    c.circle(295, 17, 1.5, "#d0d0a8")


def ghost_ship(c, t):
    bob = 1 if blink(t, 2) else 0
    y = 44 + bob
    hull, edge, spar = "#235a50", GHOST_D, "#4a9a82"
    c.glow(66, 28, 44, GHOST, amount=0.2, levels=2, squash=1.5, region=(0, 0, 320, HORIZON + 6))
    c.polygon([(8, y - 12), (92, y - 12), (104, y - 20), (114, y - 21), (110, y - 10), (98, y), (20, y)],
              fill=hull, outline=edge)
    c.hline(12, y - 8, 86, edge)
    for k in range(7):
        c.rect(24 + k * 10, y - 6, 3, 2, GHOST_HI if blink(t, 3, offset=k * 0.21, duty=0.6) else GHOST)
    for mx, top, half in ((34, 6, 10), (58, 0, 12), (84, 10, 8)):
        c.vline(mx, top + bob, y - 12 - top, spar)
        for k, yy in enumerate((top + 3, top + 14)):
            hw = half - k * 2
            c.hline(mx - hw - 1, yy + bob, 2 * hw + 3, spar)
            c.polygon([(mx - hw, yy + 1 + bob), (mx + hw, yy + 1 + bob), (mx + hw + 2, yy + 9 + bob),
                       (mx + 1, yy + 7 + bob), (mx - hw - 1, yy + 9 + bob)], fill="#5aa88a", pattern="dense")
            c.rect(mx - hw // 2, yy + 4 + bob, 2, 2, "#183a3a")
    c.line(4, y - 14, 34, 6 + bob, spar)
    c.line(84, 10 + bob, 114, y - 21, spar)
    c.particles(10, 6, 100, 36, t, "motes", n=14, seed=4, colors=[GHOST_HI, GHOST])


def water(c, t):
    c.rect(0, HORIZON, 320, SCENE_H - HORIZON, SEA)
    c.pattern(0, HORIZON, 320, 3, "#3a6a6a", "checker")
    c.pattern(0, HORIZON + 3, 320, 4, "#3a6a6a", "sparse")
    for k in range(10):
        y = HORIZON + 10 + k * 7
        c.pattern(0, y, 320, 1, SEA_D, "checker")
    c.shimmer(0, HORIZON + 4, 320, SCENE_H - HORIZON - 4, t, SEA_HI, n=70, seed=5, cycles=1, length=(2, 6), on=SEA)


def lantern(c, x, y, t, seed, post=12):
    c.rect(x, y, 2, post, "#2a1a0e")
    c.hline(x - 1, y, 4, "#2a1a0e")
    c.rect(x - 1, y - 4, 4, 4, "#1a1010")
    c.rect(x, y - 3, 2, 2, LAMP_HOT if flicker(t, seed=seed) > 0.3 else LAMP)


def lamp_light(c, x, y, t, seed, r=9):
    c.glow(x, y, r + (1 if flicker(t, seed=seed) > 0.5 else 0), LAMP, amount=0.16, levels=2, squash=1.6)


def palms(c, t):
    box(c, 30, -18, 14, 10, 2, z=-2, look=SAND)
    for k, (u, v, lean) in enumerate(((34, -14, 1), (40, -12, -1))):
        x, y = P(u, v, 0)
        sway = 1 if blink(t, 2, offset=k * 0.5) else 0
        top = (x + lean * 8 + sway, y - 30)
        for j in range(12):
            p = j / 11
            c.rect(round(x + (top[0] - x) * p * p), round(y + (top[1] - y) * p), 2, 3,
                   "#7a5a34" if j % 2 else "#5a4024")
        for a in (-160, -125, -55, -20, 200, 30):
            r = math.radians(a)
            for j in range(11):
                fx = top[0] + math.cos(r) * j
                fy = top[1] + math.sin(r) * j * 0.6 + j * j * 0.05
                c.px(round(fx), round(fy), "#2a8a3a" if j < 8 else "#1e6a2e")
                c.px(round(fx), round(fy) + 1, "#1a5a28")
        c.circle(top[0], top[1] + 1, 1.5, "#6a4a20")


def tavern(c, t):
    tv = box(c, 4, 2, 18, 12, 22, z=6, look=TAVERN)
    for b in range(3, 22, 4):
        c.line(*tv.left(0, b), *tv.left(18, b), "#6a3e22")
        c.line(*tv.right(0, b), *tv.right(12, b), "#4a2c18")
    door = [tv.left(3, 9), tv.left(7, 9), tv.left(7, 22), tv.left(3, 22)]
    c.polygon(door, fill="#2a160a")
    c.polygon([tv.left(3.5, 10), tv.left(6.5, 10), tv.left(6.5, 21), tv.left(3.5, 21)], fill=LAMP, pattern="sparse")
    for u0 in (10, 14):
        c.polygon([tv.left(u0, 7), tv.left(u0 + 3, 7), tv.left(u0 + 3, 13), tv.left(u0, 13)], fill=LAMP)
        c.line(*tv.left(u0 + 1.5, 7), *tv.left(u0 + 1.5, 13), "#5a3418")
        c.px(*tv.left(u0 + 0.5, 8), LAMP_HOT)
    for v0 in (3, 7):
        c.polygon([tv.right(v0, 7), tv.right(v0 + 3, 7), tv.right(v0 + 3, 13), tv.right(v0, 13)],
                  fill=LAMP_HOT if flicker(t, seed=v0) > 0.2 else LAMP)
    for k in range(0, 9, 2):
        c.line(*tv.right(1 + k, 14), *tv.right(2 + k, 20), "#b8a070")
        c.line(*tv.right(2 + k, 14), *tv.right(1 + k, 20), "#b8a070")
    roof = "#5a2a52"
    c.polygon([P(3, 1, 28), P(23, 1, 28), P(23, 8, 37), P(3, 8, 37)], fill="#3a1a3a")
    c.polygon([P(23, 1, 28), P(23, 15, 28), P(23, 8, 37)], fill="#6a4a2a")
    c.polygon([P(3, 8, 37), P(23, 8, 37), P(23, 15, 28), P(3, 15, 28)], fill=roof)
    for k in range(1, 4):
        c.line(*P(3, 8 + k * 1.75, 37 - k * 2.25), *P(23, 8 + k * 1.75, 37 - k * 2.25), "#4a1e44")
    c.line(*P(3, 8, 37), *P(23, 8, 37), "#8a4a7a")
    box(c, 16, 4, 3, 3, 8, z=33, look={"top": "#3a3a40", "left": "#6a5a5a", "right": "#4a3a3a"})
    cx, cy = P(17.5, 5.5, 41)
    c.particles(cx - 2, cy - 4, 4, 3, t, "smoke", n=10, seed=2, speed=22, wind=10)
    bx, by = tv.left(0, 3)
    c.line(bx, by, bx - 8, by - 4, "#2a1a0e")
    for dx in (-7, -2):
        c.vline(bx + dx, by - 4 + (dx // 2) + 1, 3, "#8a7a5a")
    sx, sy = bx - 12, by - 1
    c.rect(sx, sy, 16, 8, "#7a4a22")
    c.box(sx, sy, 16, 8, "#3a2010")
    c.text(sx + 8, sy + 2, "GROG", "#ffd060", align="center", check=False)
    return tv


def shack(c, t):
    for u, v in ((50, 13), (61, 13), (61, 1)):
        x, y = P(u, v, 4)
        c.rect(x - 1, y, 2, 8, "#2a1a0e")
    box(c, 49, 0, 13, 13, 2, z=2, look=PLANK)
    sh = box(c, 51, 2, 9, 8, 13, z=4, look=SHACK)
    for b in range(2, 13, 3):
        c.line(*sh.left(0, b), *sh.left(9, b + 1), "#46543e")
    c.polygon([sh.left(2, 5), sh.left(5, 5), sh.left(5, 9), sh.left(2, 9)], fill=LAMP)
    c.polygon([sh.right(2, 4), sh.right(5, 5), sh.right(5, 12), sh.right(2, 11)], fill="#2a1a10")
    c.polygon([P(50, 1, 20), P(61, 1, 22), P(61, 11, 16), P(50, 11, 14)], fill="#6a6a7a")
    c.line(*P(50, 1, 20), *P(61, 1, 22), "#9a9aa8")
    for k in range(3):
        c.line(*P(53 + k * 3, 1, 20.5 + k * 0.5), *P(53 + k * 3, 11, 14.5 + k * 0.5), "#5a5a68")
    for k in range(3):
        box(c, 44 + k * 2, 5, 1, 3, 1, z=5, look=PLANK)


def barrel(c, x, y, top="#7a4a22"):
    c.rect(x - 3, y - 7, 7, 7, "#6a3e1c")
    c.vline(x - 3, y - 7, 7, "#8a5a2e")
    for yy in (y - 6, y - 2):
        c.hline(x - 3, yy, 7, "#3a3a44")
    c.rect(x - 2, y - 8, 5, 1, top)
    c.hline(x - 3, y - 1, 7, "#3a2210")


def bow(c, t):
    """A moored ship's bow in the foreground, cut by the frame."""
    b = 1 if blink(t, 2, offset=0.6) else 0
    hull = [(0, 66 + b), (34, 74 + b), (66, 94 + b), (78, 120), (0, 120)]
    c.polygon(hull, fill="#5a3418")
    for k, (y0, y1) in enumerate(((80, 104), (90, 112), (100, 118))):
        c.line(0, y0 + b, 70 - k * 2, y1 + b, "#7a4a24" if k % 2 == 0 else "#3e2410")
    c.polygon([(0, 66 + b), (34, 74 + b), (66, 94 + b), (64, 98 + b), (32, 78 + b), (0, 71 + b)], fill="#a07040")
    for k in range(6):
        x = 4 + k * 10
        y = 68 + b + round(k * 4.6)
        c.vline(x, y - 5, 5, "#4a2c14")
    c.line(4, 63 + b, 62, 89 + b, "#6a4220")
    c.line(64, 94 + b, 108, 66 + b, "#6a4220")
    c.line(64, 95 + b, 108, 67 + b, "#4a2c14")
    c.line(108, 66 + b, 20, 40, "#8a7a5a")
    c.line(108, 66 + b, 60, 50, "#8a7a5a")
    c.sprite(60, 86 + b, [".yy.", "yyyy", ".yy.", "yyy.", ".yy."], {"y": "#e8c050"}, outline=INK)
    c.line(30, 76 + b, 121, 100, "#c8b080")
    c.shimmer(0, 104, 90, 16, t, SEA_HI, n=10, seed=11, cycles=1, on=SEA)


def deck(c):
    for u in range(0, 45, 8):
        x, y = P(u, 28, 3)
        c.rect(x - 1, y, 2, 9, "#2a1a0e")
    for v in range(0, 28, 7):
        x, y = P(44, v, 3)
        c.rect(x - 1, y, 2, 9, "#2a1a0e")
    box(c, 0, 0, 44, 28, 3, z=3, look=DECK)
    for u in range(2, 44, 3):
        c.line(*P(u, 0, 6), *P(u, 28, 6), "#7a4c26")
    for u0, v0 in ((40, 26), (30, 6)):
        x, y = P(u0, v0, 6)
        c.circle(x, y - 1, 3, "#c8a860")
        c.circle(x, y - 1, 1.5, "#8a6a30")


def jetty(c, t):
    for v in (34, 40, 46):
        for u in (18, 24):
            x, y = P(u, v, 3)
            c.rect(x - 1, y, 2, 8, "#2a1a0e")
    box(c, 18, 28, 6, 19, 2, z=4, look=PLANK)
    for v in range(29, 47, 2):
        c.line(*P(18, v, 6), *P(24, v, 6), "#5a3a1c")
    bob = 1 if blink(t, 2, offset=0.3) else 0
    bx, by = P(26, 34, 2)
    by += bob
    c.polygon([(bx, by), (bx + 16, by + 8), (bx + 6, by + 15), (bx - 12, by + 6)], fill=BOAT["left"],
              outline="#2a160a")
    c.polygon([(bx, by + 2), (bx + 12, by + 8), (bx + 5, by + 12), (bx - 8, by + 6)], fill=BOAT["top"])
    c.line(bx - 2, by + 6, bx + 8, by + 3, "#8a6a40")
    c.line(bx + 2, by + 8, bx - 10, by + 12, "#a07a48")
    c.line(bx + 6, by + 6, bx + 20, by + 12, "#a07a48")
    x, y = P(21, 46, 6)
    c.line(x, y, bx - 10, by + 4, "#c8b080")


def crates(c, t):
    box(c, 30, 1, 5, 5, 5, z=6, look=CRATE, edge="#d0a060")
    box(c, 35, 1, 5, 5, 5, z=6, look=CRATE, edge="#d0a060")
    box(c, 32, 1, 5, 5, 5, z=11, look=CRATE, edge="#d0a060")
    x, y = P(38, 9, 6)
    barrel(c, x, y)
    barrel(c, x + 7, y + 3)
    mx, my = P(37, 3, 16)
    c.sprite(mx - 3, my - 7, MONKEY[int(t * 4) % 2], {"b": "#8a5a2a", "f": "#e8b888", "k": "#101010", "t": "#8a5a2a"}, outline=INK)


def cook(c, t):
    x, y = P(27, 12, 6)
    c.rect(x + 6, y - 8, 7, 5, "#3a3a44")
    c.hline(x + 5, y - 8, 9, "#6a6a74")
    c.rect(x + 7, y - 3, 1, 3, "#2a2a30")
    c.rect(x + 11, y - 3, 1, 3, "#2a2a30")
    c.rect(x + 7, y - 2, 5, 2, "#ff7a2a" if blink(t, 4) else "#ffb040")
    c.particles(x + 7, y - 12, 4, 3, t, "smoke", n=8, seed=7, speed=14, wind=4, colors=["#c8c8d0", "#8a8a9a"])
    stand(c, COOK[int(t * 4) % 2], COOK_COLORS, 27, 12)


def captain(c, t):
    x, y = P(3, 24, 6)
    c.glow(x, y - 16, 22, GHOST, amount=0.25, levels=2, squash=0.8)
    stand(c, CAPTAIN[int(t * 8) % 2], CAPTAIN_COLORS, 3.5, 24, shade=False)
    c.particles(x - 10, y - 34, 22, 34, t, "motes", n=16, seed=12, colors=[GHOST_HI, GHOST, GHOST_D], sway=2)


def scene(s, t):
    sky(s, t)
    ghost_ship(s, t)
    water(s, t)
    palms(s, t)
    deck(s)
    tv = tavern(s, t)
    shack(s, t)
    crates(s, t)
    stand(s, FATTY[0 if (t * 2) % 1 < 0.6 else 1], FATTY_COLORS, 5, 16)
    stand(s, SKINNY, SKINNY_COLORS, 16.5, 16.5)
    px, py = P(16.5, 16.5, 6)
    s.sprite(px + 1, py - 23, PARROT[int(t * 8) % 2], {"r": "#e02a2a", "y": "#ffd040", "b": "#2a6ad0"}, outline=INK)
    cook(s, t)
    captain(s, t)
    breathe = (t * 2) % 1 < 0.5
    stand(s, HERO[0 if breathe else 1], HERO_COLORS, 17, 26, flip=False)
    jetty(s, t)
    bow(s, t)
    for (u, v, z), seed in (((26, 27, 6), 1), ((43, 27, 6), 2), ((19, 46, 6), 3), ((48, 7, 5), 4)):
        x, y = P(u, v, z)
        lantern(s, x, y - 12, t, seed)
    for (u, v, z), seed in (((26, 27, 6), 1), ((43, 27, 6), 2), ((19, 46, 6), 3), ((48, 7, 5), 4)):
        x, y = P(u, v, z)
        lamp_light(s, x, y - 14, t, seed)
        s.shimmer(x - 6, max(y + 2, HORIZON), 12, 14, t, LAMP, n=6, seed=seed, cycles=2, length=(1, 3), on=SEA)
    dx, dy = tv.left(5, 15)
    s.glow(dx, dy, 10, LAMP, amount=0.2, levels=2, squash=1.6)
    s.particles(0, 50, 320, 66, t, "motes", n=14, seed=21, colors=["#e8ff8a", "#a8e85a"])
    s.particles(0, HORIZON - 4, 140, 10, t, "dust", n=20, seed=3, colors=["#5a8a8a", "#3a6a6a"], sway=4)
    return tv


def interface(c, t, sentence):
    c.rect(0, SCENE_H, 320, 180 - SCENE_H, "#000000")
    c.text(160, SCENE_H + 3, sentence, "#c8e0ff", align="center")
    for r, row in enumerate(VERBS):
        for k, verb in enumerate(row):
            c.text(6 + k * 48, SCENE_H + 14 + r * 11, verb, "#4a78b8", font="large")
    c.sprite(153, SCENE_H + 16, ["..#..", ".###.", "#####"], {"#": "#4a78b8"})
    c.sprite(153, SCENE_H + 48, ["#####", ".###.", "..#.."], {"#": "#4a78b8"})
    for k, (name, (art, cols)) in enumerate(ITEMS.items()):
        cx = 166 + (k % 3) * 52
        cy = SCENE_H + 13 + (k // 3) * 22
        w, h = len(art[0]) * 2, len(art) * 2
        c.sprite(cx + (48 - w) // 2, cy + (20 - h) // 2, art, cols, scale=2, shade=True)


def draw(c, t):
    s = c.sub(320, SCENE_H)
    tv = scene(s, t)
    c.paste(s, 0, 0)
    talking = 0 if t < 0.6 else 1
    line, col = LINES[talking]
    start = 0.0 if talking == 0 else 0.6
    shown = reveal(line, phase(t, start, start + 0.25))
    if shown:
        c.text(160, 3, shown, col, align="center", outline="#000000")
    hx, hy = tv.left(5, 15)
    c.sprite(hx - 3, hy - 3, ["...w...", "...w...", ".......", "ww...ww", ".......", "...w...", "...w..."],
             {"w": "white" if blink(t, 4) else "#c8e0ff"})
    interface(c, t, "WALK TO SALTY DOG TAVERN")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=6, fps=8, seamless=True, poster=0.4)
