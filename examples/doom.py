"""DOOM, redrawn in the kit: the title screen over a burning base, the main menu with its skull cursor,
the episode and skill menus, the screen melt, and a first-person walk into a tech-base hangar rendered
with the kit's raycaster, framed by the status bar. Menu text, episode and skill names, the marine's face
and the map are original."""

import math
import random
from pathlib import Path

from pixelkit import Canvas, Raycaster, animate, blink, ease_in_out, phase

SECONDS, FPS = 14, 10
SPLASH, MAIN, EPISODE, SKILL, MELT = 3.2, 5.0, 6.6, 8.4, 9.2
KEY, INK = "#ff00ff", "#100404"
SKY = ["#1a0404", "#3a0808", "#6a1008", "#a02010", "#e05010"]
LOGO = ["#fff0a0", "#ffc040", "#e08020", "#a85010", "#6a3008"]
LOGO_HI, RUST, RUST_D = "#fff8d0", "#3a1804", "#1a0c04"
RED = ["#ff9070", "#ff3020", "#a01010", "#5a0808"]
BR = ["#2a1c10", "#4a3420", "#6b4c2e", "#8c6a44", "#ab8a5c"]
GR = ["#2c2c2c", "#4a4a4a", "#6a6a6a", "#8e8e8e", "#b8b8b8"]
SLIME = ["#1c5c10", "#38a020", "#7ce040"]
LAMP = ["#f0f0d8", "#ffffff"]
FIRE = ["#ffe080", "#ff9020", "#e04010"]
SKIN, SKIN_D, SKIN_L = "#c89870", "#8a5a3a", "#e0b890"
GOLD, VEST, CYAN = "#e0c040", "#4a6a30", "#40c0c0"
VIEW_H = 148

# --- sprites ---------------------------------------------------------------------------------------

SKULL = ["....kkkkkkkk....", "..kkwwwwwwwwkk..", ".kwwwwwwwwwwwwk.", "kwwwwwwwwwwwwwwk", "kwwwwwwwwwwwwwwk",
         "kwwkkkwwwwkkkwwk", "kwkkEkkwwkkEkkwk", "kwkkkkkwwkkkkkwk", "kwwkkkwwwwkkkwwk", ".kwwwwwkkwwwwwk.",
         "..kwwwwkkwwwwk..", "..kwwwwwwwwwwk..", "...kwkwkwkwkk...", "...kwkwkwkwk....", "....kkkkkkkk...."]

DEMON = ["k..........k..", "kk........kk..", ".kk.kkkk.kk...", "..kkkkkkkk....", "..kkrkkrkk....",
         "...kkkkkk.....", ".kkkkkkkkkk...", "kkkkkkkkkkkk..", "kk.kkkkkk.kk..", "kk.kkkkkk.kk..",
         "k..kkkkkk..k..", "...kkkkkk.....", "...kk..kk.....", "..kkk..kkk....", "..kk....kk....",
         ".kkk....kkk..."]

Z_TOP = ["....hhhh......", "...hhhhhh.....", "...hssssh.....", "...seesss.....", "...sssss......",
         "....mmm.......", "..vvvvvvvv....", ".vvvvvvvvvv...", "svvvvvvvvvvs..", "svvvvvbvvvvs..",
         "svvvvvvvvvvs..", "s.vvvvvvvv.s..", "srrrrrrrrrrrr.", "..vvvvvvvv....", "..bbbbbbbb...."]
Z_LEGS = (["..pppppppp....", "..ppp..ppp....", "..ppp..ppp....", "..ppp..ppp....", "..ppp..ppp....",
           "..pp....pp....", "..pp....pp....", ".kkk....kkk..."],
          ["..pppppppp....", "..ppp...pp....", "...pp...ppp...", "...pp....pp...", "..ppp....pp...",
           "..pp.....ppp..", "..pp......pp..", ".kkk......kkk."])
Z_PAIN = Z_TOP[:8] + ["svvxxvvvvvvs..", "svxxxvbvvvvs..", "svvxvvvvvvvs..", "s.vvvvvvvv.s..",
                      "srrrrrrrrrrrr.", "..vvvvvvvv....", "..bbbbbbbb...."]
Z_DIE = ["..............", "..hhhh........", ".hssssh.......", ".sxesss.xx....", ".xvvvvvvvvx...",
         "svvvxxvvvvvs..", "svvxxxvbvvvs..", "s.vvxvvvvv.s..", "...rrrrrr.....", "..bbbbbbbb....",
         "..pppppppp....", "..ppp..ppp....", "..pp....pp....", ".kkk....kkk..."]
Z_DOWN = ["....................", "......xx.....xx.....", "..hhss.xxx..........", ".hhsesvvvvvvvbbppkk..",
          ".hsssvvxxvvvvbbpppkk", "..xxvvvvvvvvvbbppp..", ".xxxxrrrrrrr.xx.....", "..xxxxxxxxxxxxx....."]
Z_COLORS = {"h": BR[0], "s": SKIN, "e": RED[1], "m": BR[0], "v": VEST, "b": BR[1], "r": GR[0], "p": GR[2],
            "k": INK, "x": RED[2]}

IMP_LEGS = ["....bBBBBb......", "....bbbbbb......", "...bbb..bbb.....", "...bb....bb.....", "..wbb....bbw....",
            "...bb....bb.....", "...bb....bb.....", "..bbb....bbb....", ".www......www...."]
IMP_IDLE = (["..w........w....", "..ww......ww....", "...wbbbbbbw.....", "...bbBBBBbb.....", "...bEbBBbEb.....",
             "...bbBBBBbb.....", "....bmmmmb......", "..w.bbbbbb.w....", ".wbbbBBBBbbbw...", "wbbbBBBBBBbbbw..",
             "bbb.BBBBBB.bbb..", "bb..BBBBBB..bb..", "bw..BBBBBB..wb.."],
            ["..w........w....", "..ww......ww....", "...wbbbbbbw.....", "...bbBBBBbb.....", "...bEbBBbEb.....",
             "...bbBBBBbb.....", "....bmmmmb......", "..w.bmMMmb.w....", ".wbbbBBBBbbbw...", "wbbbBBBBBBbbbw..",
             "bbb.BBBBBB.bbb..", ".bb.BBBBBB.bb...", ".bw.BBBBBB.wb..."])
IMP_UP = ["ff..........ff..", "fb..w....w..bf..", "bb..ww..ww..bb..", ".bb.wbbbbw.bb...", "..bbbBBBBbbb....",
          "...bEbBBbEb.....", "...bbBBBBbb.....", "....bmMMmb......", "....bbbbbb......", "..wbbBBBBbbw....",
          "..bbBBBBBBbb....", "....BBBBBB......", "....BBBBBB......"]
IMP_THROW = ["..w........w....", "..ww......ww....", "...wbbbbbbw.....", "...bbBBBBbb.....", "...bEbBBbEb.....",
             "...bbBBBBbb.....", "....bmMMmb......", "..w.bbbbbb.w....", ".wbbbBBBBbbbbbff", "wbbbBBBBBBbbbbff",
             "bbb.BBBBBB......", "bb..BBBBBB......", "bw..BBBBBB......"]
IMP_COLORS = {"w": "#d8d0b0", "b": BR[2], "B": BR[3], "E": RED[1], "m": RED[3], "M": FIRE[1], "f": FIRE[1]}

FIREBALL = ["..fFFf..", ".fFYYFf.", "fFYYYYFf", "fFYYYYFf", ".fFYYFf.", "..fFFf.."]
FLASK = ["..kk..", "..cc..", ".cBBc.", "cBLBBc", "cBBBBc", "cBBBBc", ".cccc."]
VEST_ART = ["..gg....gg..", ".gGGg..gGGg.", "gGGGGggGGGGg", "gGGLGGGGLGGg", "gGGGGGGGGGGg", "gGGGGGGGGGGg",
            ".gGGGGGGGGg.", ".gGGGGGGGGg.", "..gggggggg.."]
BARREL = ["..llllll..", ".lLLLLLLl.", ".gggggggg.", ".gGGGGGGg.", ".gGgggGGg.", ".gGGGGGGg.", ".dddddddd.",
          ".gGGGGGGg.", ".gGGgGGGg.", ".gGGGGGGg.", ".dddddddd.", ".gGGGGGGg.", ".gggggggg."]

PISTOL = [".......kkkk.......", "......kGGGgk......", "......kGkkgk......", "......kGGggk......",
          ".....kGGgggdk.....", ".....kGggggdk.....", ".....kGggggdk.....", ".....kGggggdk.....",
          "....kkGggggdkk....", "...kSSkGgggdkSk...", "..kSsSskkkkkksDk..", "..kSsDsSsDsSsDDk..",
          ".kSssDssDssDsDDk..", ".kSsssssssssDDDk..", "kSsssssssssDDDDk..", "kSssssssssDDDDk...",
          "kssssssssDDDDk....", ".kssssssDDDDk.....", "..kssssDDDDk......", "..kssssDDDk.......",
          "..kssssDDDk......."]
PISTOL_COLORS = {"k": INK, "G": GR[3], "g": GR[1], "d": GR[0], "s": SKIN, "S": SKIN_L, "D": SKIN_D}
FLASH = ["....YY....", "..Y.YY.Y..", "...YWWY...", ".YYWWWWYY.", "YYWWWWWWYY", ".YYWWWWYY.", "..YYWWYY..",
         "...FYYF...", "....FF...."]

FACE_TOP = ["......hhhhhhhhhh......", "....hhhhhhhhhhhhhh....", "...hhhhhhhhhhhhhhhh...", "..hhhhhhhhhhhhhhhhhh..",
            "..hhsssssssssssssshh..", "..hssssssssssssssssh..", ".hssssssssssssssssssh.", ".hsbbbbbssssssbbbbbsh."]
FACE_LOW = [".ssssssssssssssssssss.", "..ssssssssDDssssssss..", "..ssssssssDDssssssss..", "..sssssssDDDDsssssss..",
            "..sDssssssssssssssDs..", "{mouth}", "...ssssssssssssssss...", "....ssssssssssssss....",
            ".....ssssssssssss.....", "......DDDDDDDDDD......", ".......nnnnnnnn.......", ".......nnnnnnnn......."]
EYES = {"center": ".sswweewssssswweewss.", "left": ".sseewwwssssseewwwss.", "right": ".sswwweessssswwweess.",
        "ouch": ".ssDDDDsssssssDDDDss."}
MOUTH = {"calm": "..sDsssmmmmmmmmsssDs..", "ouch": "..sDssmwwwwwwwwmssDs.."}
FACE_COLORS = {"h": BR[1], "s": SKIN, "D": SKIN_D, "b": BR[0], "w": GR[4], "e": BR[0], "m": RED[3], "n": SKIN_D}

_SPR = {}


def spr(name, art, colors, outline=INK, shade=True):
    if name not in _SPR:
        w, h = max(map(len, art)), len(art)
        s = Canvas(w + 2, h + 2, bg=KEY)
        s.sprite(1, 1, [r.ljust(w, ".") for r in art], colors, outline=outline, shade=shade)
        _SPR[name] = s
    return _SPR[name]


def face(state, look):
    low = [MOUTH["ouch" if state == "ouch" else "calm"] if r == "{mouth}" else r for r in FACE_LOW]
    eyes = EYES["ouch" if state == "ouch" else look]
    return spr(f"face-{state}-{look}", FACE_TOP + [FACE_TOP[-1].replace("b", "s"), eyes] + low, FACE_COLORS,
               outline=None)


# --- title and menus -------------------------------------------------------------------------------

def hell(c, s, dim=False):
    s = math.floor(s * 5) / 5
    c.gradient(0, 0, 320, 134, SKY[:3] if dim else SKY)
    rnd = random.Random(5)
    for k in range(8):
        y, w, speed = 10 + k * 13, rnd.randint(50, 120), 3 + k % 3 * 2
        x = (rnd.randrange(400) + (0 if dim else s * speed)) % 440 - 80
        c.pattern(int(x), y, w, 2 + k % 2, SKY[1 if k < 4 or dim else 2], "checker")
    rnd = random.Random(9)
    pts, x = [(0, 180)], 0
    while x <= 330:
        pts.append((x, 106 + rnd.randint(-14, 8)))
        x += rnd.randint(8, 22)
    c.polygon(pts + [(330, 180)], fill="#0a0202", outline=SKY[1])
    if not dim:
        c.glow(160, 124, 80, SKY[4], amount=0.35, levels=2, squash=2.4)
    for x, w, h in ((94, 22, 30), (116, 10, 46), (126, 42, 22), (168, 12, 56), (180, 30, 28), (210, 18, 38)):
        c.rect(x, 134 - h, w, h, INK)
        for j in range(134 - h + 4, 130, 6):
            for i in range(x + 2, x + w - 2, 4):
                if (i * 7 + j * 3) % 5 == 0 and blink(s / 2, 3, offset=(i + j) % 7 / 7, duty=0.8):
                    c.px(i, j, FIRE[1])
    for i in range(14):
        x = 96 + i * 9
        h = 6 + round(4 * math.sin(s * 9 + i * 1.7)) + (i % 3) * 3
        base = 134 - (56 if 168 <= x < 180 else 46 if 116 <= x < 126 else 38 if 210 <= x < 228 else
                      30 if x < 116 else 28 if 180 <= x < 210 else 22)
        c.polygon([(x - 4, base), (x, base - h), (x + 4, base)], fill=FIRE[2])
        c.polygon([(x - 2, base), (x, base - h // 2), (x + 2, base)], fill=FIRE[1])
    c.rect(0, 134, 320, 46, "#0a0202")
    c.polygon([(0, 180), (0, 128), (14, 120), (34, 124), (56, 136), (70, 180)], fill=INK)
    c.polygon([(250, 180), (262, 134), (286, 122), (304, 126), (320, 118), (320, 180)], fill=INK)
    eyes = RED[1] if blink(s / 2, 2, duty=0.85) else RED[2]
    c.sprite(10, 88, DEMON, {"k": INK, "r": eyes}, scale=2)
    c.sprite(282, 92, DEMON, {"k": INK, "r": eyes}, scale=2, flip=True)
    c.particles(40, 96, 240, 40, s / 3.2, "embers", n=46, seed=11, colors=[FIRE[0], FIRE[1], FIRE[2], SKY[3]])


def logo(c, y, scale, weight):
    box = c.chunky(160, y, "DOOM", LOGO, scale=scale, weight=weight, depth=max(2, scale - 2),
                   side=[RUST, RUST_D], light=LOGO_HI, dark=RUST, bevel=max(1, scale // 3), bow=0.35)
    face_cols = {c.rgb(k) for k in LOGO + [LOGO_HI]}
    rnd = random.Random(3)
    x, yy = box.x + 6, box.y + box.h * 0.45
    while x < box.x2 - 6:
        x += 1
        yy += rnd.choice((-1, 0, 0, 1)) * 0.8
        for dy in (0, 1) if scale > 5 else (0,):
            if c.img.getpixel((x, int(yy) + dy)) in face_cols:
                c.px(x, int(yy) + dy, RUST_D)
    for _ in range(scale * 26):
        px, py = rnd.randrange(box.x, box.x2), rnd.randrange(box.y + box.h // 2, box.y2)
        if c.img.getpixel((px, py)) in face_cols:
            c.px(px, py, RUST)
    return box


def splash(c, s):
    hell(c, s)
    logo(c, 12, 7, 2)
    if blink(math.floor(s * 5) / 10, 3, duty=0.6):
        c.text(160, 164, "PRESS ANY KEY", GOLD, align="center", shadow=INK)


def item(c, x, y, label, colors=None, scale=2):
    cols = colors or RED[1:]
    c.chunky(x, y, label, cols, scale=scale, depth=1, side=RED[3], outline=INK, light=RED[0] if not colors else
             colors[0], align="left")


def skull(c, x, y, s):
    lit = blink(s, 32, duty=0.5)
    c.sprite(x, y, SKULL, {"k": INK, "w": LOGO[0], "E": RED[1] if lit else RED[3]}, shade=True)


def menu(c, s, items, x, y0, step, sel, title=None, sub=None):
    hell(c, s, dim=True)
    if title:
        item(c, 160 - c.measure(title, "large", 3) // 2, 10, title, scale=3)
    else:
        logo(c, 6, 4, 1)
    if sub:
        item(c, 160 - c.measure(sub, "large", 2) // 2, 44, sub, colors=[LOGO[1], LOGO[2], LOGO[3]])
    for k, label in enumerate(items):
        item(c, x, y0 + k * step, label)
    skull(c, x - 22, y0 + sel * step - 1, math.floor(s * 5) / 5 / SECONDS)


def main_menu(c, s):
    menu(c, s, ["NEW GAME", "OPTIONS", "LOAD GAME", "SAVE GAME", "QUIT GAME"], 116, 62, 18, 0)


def episode_menu(c, s):
    menu(c, s, ["THE MOON FOUNDRY", "SHORES OF CINDER", "THE BURNING CROWN"], 72, 76, 22, 0,
         title="EPISODE", sub="WHERE DO YOU START?")


def skill_menu(c, s):
    sel = 2 if s < SKILL - 1.0 else 3
    menu(c, s, ["I BRUISE EASILY.", "GO EASY ON ME.", "BRING IT ON.", "SHEER CARNAGE.", "NO MERCY!"], 72, 68, 18,
         sel, title="NEW GAME", sub="HOW MUCH CAN YOU TAKE?")


# --- the hangar ------------------------------------------------------------------------------------

MAP = ["BBBBBBBLLBBBBBBB", "BBBBBBD..DBBBBBB", "BG............GB", "BC............CB", "BG............GB",
       "BC....P..P....CB", "BG............GB", "B~~~~~~~~~~~~~~B", "B~~~~~~~~~~~~~~B", "BG............GB",
       "BC....P..P....CB", "BG............GB", "BG............GB", "BBBG........GBBB", "BBBBG......GBBBB",
       "BBBBBBBBBBBBBBBB"]
CEIL = [r for r in MAP]
for j, cols in ((1, (7, 8)), (3, (4, 11)), (11, (4, 11)), (8, (5, 10))):
    CEIL[j] = "".join("o" if i in cols else ch for i, ch in enumerate(CEIL[j]))
LIGHTS = [(8.0, 1.2, 4.5, 0.7), (4.5, 3.5, 2.6, 0.35), (11.5, 3.5, 2.6, 0.35), (4.5, 11.5, 2.6, 0.3),
          (11.5, 11.5, 2.6, 0.3), (8.0, 8.0, 7.0, 0.18)]
IMP_AT, ZOMBIE_AT = (11.6, 3.2), (5.0, 4.5)


def texture(w, h, paint):
    s = Canvas(w, h, bg=KEY)
    paint(s)
    return s


def brown(s):
    s.rect(0, 0, 16, 32, BR[3])
    s.rect(0, 0, 16, 3, GR[2])
    s.rect(0, 29, 16, 3, GR[2])
    s.rect(1, 13, 14, 2, BR[2])
    for y in (0, 16):
        s.hline(0, y, 16, BR[0])
        s.hline(0, y + 1, 16, BR[3])
    s.vline(0, 0, 32, BR[0])
    s.vline(15, 0, 32, BR[1])
    s.rect(4, 5, 8, 7, BR[1])
    for j in range(6, 12, 2):
        s.hline(5, j, 6, BR[0])
    s.rect(3, 20, 10, 8, BR[3])
    s.box(3, 20, 10, 8, BR[0])
    s.hline(4, 21, 8, BR[4])
    for x, y in ((2, 3), (13, 3), (2, 29), (13, 29)):
        s.px(x, y, BR[4])


def grey(s):
    s.rect(0, 0, 16, 32, GR[2])
    for k, y in enumerate((0, 8, 16)):
        s.hline(0, y, 16, GR[1])
        s.hline(0, y + 1, 16, GR[3])
        s.vline(4 + 6 * (k % 2), y, 8, GR[1])
    for i in range(16):
        for j in range(26, 32):
            s.px(i, j, GOLD if (i + j) // 2 % 2 else GR[0])
    s.hline(0, 25, 16, GR[0])


def computer(t):
    def paint(s):
        s.rect(0, 0, 16, 32, GR[2])
        s.box(1, 3, 14, 13, GR[0])
        s.rect(2, 4, 12, 11, INK)
        rnd = random.Random(8)
        for _ in range(14):
            x, y, col, off = rnd.randrange(3, 13), rnd.randrange(5, 14), rnd.choice((RED[1], GOLD, CYAN)), rnd.random()
            if blink(t, 6, offset=off, duty=0.6):
                s.px(x, y, col)
        for j in range(19, 30, 3):
            for i in range(2, 14, 3):
                s.rect(i, j, 2, 2, GR[3] if (i + j) % 2 else GR[1])
        s.hline(0, 0, 16, GR[3])
        s.hline(0, 31, 16, GR[0])
    return texture(16, 32, paint)


def lit(s):
    s.rect(0, 0, 16, 32, LAMP[0])
    for y in (0, 10, 21):
        s.hline(0, y, 16, GR[4])
    s.vline(0, 0, 32, GR[4])
    s.rect(6, 2, 4, 28, LAMP[1])


def jamb(s):
    s.rect(0, 0, 16, 32, GR[1])
    for i in range(4, 12):
        for j in range(32):
            s.px(i, j, GOLD if (i + j) // 3 % 2 else GR[0])
    s.vline(3, 0, 32, GR[3])
    s.vline(12, 0, 32, GR[0])


def pillar(s):
    s.rect(0, 0, 16, 32, BR[3])
    s.rect(0, 0, 16, 3, GR[2])
    s.rect(0, 29, 16, 3, GR[2])
    s.vline(0, 0, 32, BR[4])
    s.vline(15, 0, 32, BR[1])
    s.rect(5, 5, 6, 22, GR[1])
    s.rect(6, 6, 4, 20, GR[4])
    s.rect(7, 6, 2, 20, LAMP[0])


def floor_tile(s):
    s.rect(0, 0, 16, 16, GR[1])
    for k in (0, 8):
        s.rect(0, k, 16, 2, GR[0])
        s.rect(k, 0, 2, 16, GR[0])
    s.rect(3, 3, 3, 3, GR[2])
    s.rect(11, 11, 3, 3, GR[2])


def slime(t):
    def paint(s):
        s.rect(0, 0, 16, 16, SLIME[1])
        for j in range(0, 16, 3):
            off = (j * 5 + int(t * 64)) % 16
            for i in range(5):
                s.px((off + i) % 16, j, SLIME[2])
                s.px((off + i + 8) % 16, j + 1, SLIME[0])
    return texture(16, 16, paint)


def ceiling_tile(s):
    s.rect(0, 0, 16, 16, GR[1])
    s.rect(0, 0, 16, 3, GR[0])
    s.rect(0, 0, 3, 16, GR[0])


def lamp_tile(s):
    s.rect(0, 0, 16, 16, GR[3])
    s.rect(2, 2, 12, 12, LAMP[0])
    s.rect(4, 4, 8, 8, LAMP[1])


STATIC = {}


def static(name, w, h, paint):
    if name not in STATIC:
        STATIC[name] = texture(w, h, paint)
    return STATIC[name]


def camera(q):
    walk = ease_in_out(min(1.0, q / 0.92))
    return (8.0 + 0.25 * math.sin(math.pi * q), 13.2 - 2.5 * walk), -90 - 10 * math.sin(2 * math.pi * (q - 0.15))


def level(c, q):
    steps_per_s = 4
    n = round((SECONDS - MELT) * steps_per_s)
    q = math.floor(q * n + 1e-6) / n
    t = q * (SECONDS - MELT)
    pos, ang = camera(q)
    stride = math.sin(math.pi * min(1.0, q / 0.92)) * (q < 0.92)
    steps = t * 1.7
    pitch = round(1.5 * abs(math.sin(math.pi * steps)) * stride)
    world = Raycaster(MAP, {"B": static("brown", 16, 32, brown), "G": static("grey", 16, 32, grey),
                            "C": computer(t / 4), "L": static("lit", 16, 32, lit), "D": static("jamb", 16, 32, jamb),
                            "P": static("pillar", 16, 32, pillar)},
                      floor=static("floor", 16, 16, floor_tile), floors={"~": slime(t / 4)},
                      ceiling=static("ceil", 16, 16, ceiling_tile), ceilings={"o": static("lamp", 16, 16, lamp_tile)},
                      ceiling_grid=CEIL, bright="L~o", fog="#000000", fog_dist=18, levels=4, lights=LIGHTS,
                      dither=False)

    shots = (0.30, 0.45, 0.66)
    firing = any(a <= q < a + 0.04 for a in shots)
    if q < 0.30 or 0.36 <= q < 0.45:
        z = spr(f"z{int(t * 3) % 2}", Z_TOP + Z_LEGS[int(t * 3) % 2], Z_COLORS)
    elif q < 0.36:
        z = spr("zpain", Z_PAIN + Z_LEGS[0], Z_COLORS)
    elif q < 0.52:
        z = spr("zdie", Z_DIE, Z_COLORS)
    else:
        z = spr("zdown", Z_DOWN, Z_COLORS)
    zscale = 0.82 * z.h / (len(Z_TOP + Z_LEGS[0]) + 2)
    if 0.40 <= q < 0.50:
        imp = spr("impup", IMP_UP + IMP_LEGS, IMP_COLORS)
    elif 0.50 <= q < 0.56:
        imp = spr("impthrow", IMP_THROW + IMP_LEGS, IMP_COLORS)
    else:
        k = int(t * 3) % 2
        imp = spr(f"imp{k}", IMP_IDLE[k] + IMP_LEGS, IMP_COLORS)
    sprites = [
        {"x": ZOMBIE_AT[0], "y": ZOMBIE_AT[1], "img": z, "key": KEY, "scale": zscale},
        {"x": IMP_AT[0], "y": IMP_AT[1], "img": imp, "key": KEY, "scale": 0.86},
        {"x": 7.3, "y": 9.5, "img": spr("flask", FLASK, {"k": GR[3], "c": "#2030a0", "B": "#3050e0", "L": "#80a0ff"}),
         "key": KEY, "scale": 0.2},
        {"x": 9.2, "y": 9.3, "img": spr("vest", VEST_ART, {"g": SLIME[0], "G": SLIME[1], "L": SLIME[2]}),
         "key": KEY, "scale": 0.24},
        {"x": 12.4, "y": 11.6, "img": spr("barrel", BARREL, {"l": SLIME[2], "L": SLIME[1], "g": GR[1], "G": GR[2],
                                                               "d": GR[0]}), "key": KEY, "scale": 0.5},
        {"x": 3.0, "y": 2.6, "img": spr("barrel", BARREL, {}), "key": KEY, "scale": 0.5},
    ]
    fb = phase(q, 0.52, 0.80)
    if 0 < fb < 1:
        (cx, cy), _ = camera(0.80)
        f = fb * 0.92
        sprites.append({"x": IMP_AT[0] + (cx - IMP_AT[0]) * f, "y": IMP_AT[1] + (cy - IMP_AT[1]) * f,
                        "img": spr("fireball", FIREBALL, {"f": FIRE[2], "F": FIRE[1], "Y": FIRE[0]}, outline=None,
                                   shade=False),
                        "key": KEY, "scale": 0.2, "lift": 0.42, "bright": True})
    world.render(c, 0, 0, 320, VIEW_H, pos, ang, sprites=sprites, pitch=pitch)

    hit = 0.80 <= q < 0.88
    if 0.80 <= q < 0.84:
        c.pattern(0, 0, 320, VIEW_H, RED[2], "checker")
    elif 0.84 <= q < 0.88:
        c.pattern(0, 0, 320, VIEW_H, RED[2], "sparse")

    bx = round(10 * math.sin(math.pi * steps) * stride)
    by = round(5 * abs(math.cos(math.pi * steps)) * stride)
    gx, gy = 160 - 18 + bx, VIEW_H - 38 + by - (5 if firing else 0)
    if firing:
        c.sprite(gx + 8, gy - 18, FLASH, {"Y": FIRE[0], "W": LAMP[1], "F": FIRE[1]}, scale=2)
    c.sprite(gx, gy, PISTOL, PISTOL_COLORS, scale=2, shade=True)

    ammo = 50 - sum(q >= a for a in shots)
    health = 100 if q < 0.80 else 87
    look = ("center", "left", "center", "right")[int(t / 0.9) % 4]
    status(c, ammo, health, "ouch" if hit or 0.80 <= q < 0.92 else "calm", look)


def status(c, ammo, health, state, look):
    y = VIEW_H
    c.rect(0, y, 320, 180 - y, GR[1])
    c.pattern(0, y, 320, 180 - y, GR[2], "grain")
    rnd = random.Random(2)
    for _ in range(160):
        c.px(rnd.randrange(320), rnd.randrange(y + 1, 180), GR[0])
    c.hline(0, y, 320, GR[3])
    for x, w in ((2, 44), (48, 56), (106, 34), (143, 34), (179, 56), (237, 12), (251, 67)):
        c.hline(x, y + 2, w, GR[0])
        c.vline(x, y + 2, 28, GR[0])
        c.hline(x, y + 29, w, GR[3])
        c.vline(x + w - 1, y + 2, 28, GR[3])
    num = dict(scale=2, depth=1, side=RED[3], outline=INK, light=RED[0])
    c.chunky(24, y + 5, str(ammo), RED[1:], **num)
    c.chunky(76, y + 5, f"{health}%", RED[1:], **num)
    c.chunky(207, y + 5, "0%", RED[1:], **num)
    for cx, label in ((24, "AMMO"), (76, "HEALTH"), (123, "ARMS"), (207, "ARMOR")):
        c.text(cx, y + 22, label, GR[4], align="center")
    c.rect(107, y + 3, 32, 17, GR[1])
    for k, n in enumerate("234567"):
        c.text(112 + (k % 3) * 11, y + 5 + (k // 3) * 8, n, GOLD if n == "2" else GR[3])
    c.rect(144, y + 3, 32, 26, GR[0])
    c.paste(face(state, look), 149, y + 4, key=KEY)
    for k in range(3):
        c.rect(239, y + 4 + k * 8, 8, 6, INK)
        c.box(239, y + 4 + k * 8, 8, 6, GR[0])
    for k, (name, have, cap) in enumerate((("BULL", ammo, 200), ("SHEL", 0, 50), ("RCKT", 0, 50), ("CELL", 0, 300))):
        c.text(255, y + 3 + k * 7, name, GOLD)
        c.text(316, y + 3 + k * 7, f"{have}/{cap}", GOLD, align="right")


def draw(c, t):
    s = t * SECONDS
    if s < SPLASH:
        splash(c, s)
    elif s < MAIN:
        main_menu(c, s)
    elif s < EPISODE:
        episode_menu(c, s)
    elif s < SKILL:
        skill_menu(c, s)
    elif s < MELT:
        old, new = c.sub(320, 180), c.sub(320, 180)
        skill_menu(old, SKILL - 0.01)
        level(new, 0.0)
        c.melt(old, new, phase(s, SKILL, MELT - 0.1), seed=4, width=2, spread=0.3)
    else:
        level(c, phase(s, MELT, SECONDS))


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=SECONDS, fps=FPS, poster=0.893)
