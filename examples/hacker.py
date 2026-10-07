"""Cinematic hacker UI: a typing terminal, a dot-matrix world map tracing a proxy chain, a scrolling
hex dump, a radar sweep, an exfiltration bar, CRT scanlines and the odd glitch. Pure movie nonsense."""

import math
import random
from pathlib import Path

from PIL import Image, ImageChops

from pixelkit import Rect, animate, blink, phase, reveal

G = {"hi": "#3dff7a", "mid": "#1fa64c", "lo": "#0e5426", "faint": "#082c14", "amber": "#ffb22e",
     "red": "#ff3b4e", "cyan": "#3de8ff", "bg": "#010402"}
LINES = [
    ("> SSH ROOT@MAINFRAME.GIBSON", G["hi"]),
    ("> BYPASSING FIREWALL ........ OK", G["hi"]),
    ("> CRACKING RSA-4096 ......... OK", G["hi"]),
    ("> TRACE ROUTE VIA 4 PROXIES", G["amber"]),
    ("> INJECTING PAYLOAD.EXE", G["hi"]),
    ("> ENHANCE. ENHANCE. ENHANCE.", G["cyan"]),
]
LAND = [
    [(-166, 68), (-156, 71), (-130, 70), (-110, 73), (-90, 73), (-80, 68), (-75, 62), (-62, 58), (-55, 52),
     (-65, 45), (-70, 41), (-76, 35), (-81, 31), (-80, 25), (-85, 30), (-97, 27), (-97, 22), (-87, 21), (-88, 16),
     (-83, 15), (-78, 8), (-83, 8), (-92, 14), (-105, 20), (-115, 30), (-124, 40), (-124, 48), (-130, 55),
     (-140, 60), (-152, 59), (-165, 54), (-162, 60)],
    [(-73, 78), (-60, 82), (-30, 83), (-20, 76), (-22, 70), (-40, 65), (-45, 60), (-52, 64), (-58, 70), (-70, 76)],
    [(-80, 9), (-75, 11), (-62, 11), (-52, 5), (-35, -5), (-38, -13), (-40, -22), (-48, -28), (-58, -38), (-65, -42),
     (-68, -52), (-72, -54), (-75, -50), (-73, -40), (-71, -30), (-70, -18), (-76, -14), (-81, -5), (-80, 1)],
    [(-10, 36), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 55), (8, 58), (5, 61), (12, 66), (18, 70), (28, 71),
     (40, 68), (60, 70), (80, 73), (100, 77), (115, 73), (140, 72), (160, 70), (180, 68), (180, 65), (170, 60),
     (160, 58), (156, 51), (143, 55), (140, 48), (132, 43), (127, 40), (121, 40), (122, 31), (120, 25), (110, 20),
     (108, 12), (105, 9), (100, 13), (99, 7), (103, 1), (98, 8), (95, 16), (92, 21), (88, 22), (80, 15), (77, 8),
     (73, 18), (68, 23), (62, 25), (57, 25), (59, 22), (52, 16), (43, 12), (39, 20), (35, 28), (35, 36), (28, 37),
     (26, 40), (23, 37), (20, 40), (16, 38), (12, 44), (8, 44), (3, 42), (0, 38), (-6, 36)],
    [(-17, 21), (-16, 28), (-10, 33), (-6, 36), (10, 37), (11, 33), (20, 31), (32, 31), (43, 12), (51, 12), (48, 5),
     (40, -3), (40, -15), (35, -24), (26, -34), (18, -34), (12, -17), (13, -5), (9, 0), (9, 4), (5, 5), (-8, 4),
     (-13, 8), (-17, 14)],
    [(113, -22), (114, -33), (118, -35), (130, -32), (137, -35), (141, -38), (146, -39), (150, -37), (153, -28),
     (153, -25), (146, -19), (143, -11), (141, -12), (137, -12), (136, -15), (131, -11), (126, -14), (122, -18)],
    [(95, 5), (98, 4), (106, -6), (102, -5)], [(109, 2), (117, 7), (119, 1), (116, -4), (110, -3)],
    [(131, -1), (141, -3), (150, -10), (142, -9), (138, -8)], [(130, 31), (135, 34), (140, 36), (142, 40), (141, 45),
                                                                (139, 40), (133, 34)],
    [(-5, 50), (1, 51), (1, 53), (-2, 57), (-5, 58), (-6, 55), (-3, 54), (-5, 52)],
    [(44, -13), (50, -15), (47, -25), (44, -22)], [(172, -34), (178, -38), (174, -41), (171, -46), (167, -46)],
    [(-24, 65), (-14, 66), (-14, 64), (-22, 63)],
]
CHAIN = [("LIS", -9.1, 38.7), ("REK", -21.9, 64.1), ("NYC", -74.0, 40.7), ("TYO", 139.7, 35.7),
         ("SYD", 151.2, -33.9)]
MAP = Rect(156, 23, 162, 69)
COLS, ROWS, CELL = 54, 23, 3


def inside(lon, lat, poly):
    hit = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > lat) != (y1 > lat) and lon < x0 + (lat - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


DOTS = [(i, j) for j in range(ROWS) for i in range(COLS)
        if any(inside(-180 + (i + 0.5) * 360 / COLS, 84 - (j + 0.5) * 6, p) for p in LAND)]


def project(lon, lat):
    return MAP.x + (lon + 180) / 360 * COLS * CELL, MAP.y + (84 - lat) / 6 * CELL


def frame_panel(c, x, y, w, h, title):
    c.rect(x, y, w, h, G["bg"])
    c.box(x, y, w, h, G["lo"])
    c.rect(x + 3, y - 3, c.measure(title) + 4, 7, G["bg"])
    c.text(x + 5, y - 2, title, G["mid"])


def draw(c, t):
    c.rect(0, 0, 320, 180, "#000000")
    c.text(4, 3, "◆ GIBSON/OS · ROOT SHELL", G["hi"])
    c.text(200, 3, "TRACE", G["red"] if blink(t, cycles=8) else G["lo"])
    c.meter(224, 4, 50, 3, 0.2 + 0.75 * phase(t, 0, 0.9), "red", track=G["faint"], rim=False)
    c.text(316, 3, f"03:1{int(t * 9)}:0{int(t * 60) % 10}", G["mid"], align="right")

    frame_panel(c, 2, 13, 150, 92, "TERMINAL")
    for i, (line, colour) in enumerate(LINES):
        p = phase(t, i * 0.1, i * 0.1 + 0.09)
        if p > 0:
            c.text(6, 18 + i * 9, reveal(line, p), colour, check=False)
    if phase(t, 0.62, 0.63) >= 1:
        if blink(t, cycles=10):
            c.rect(14, 76, 126, 15, G["red"])
            c.text(77, 81, "ACCESS GRANTED", "#000000", align="center")
        else:
            c.box(14, 76, 126, 15, G["red"])
            c.text(77, 81, "ACCESS GRANTED", G["red"], align="center")
    elif blink(t, cycles=12):
        typed = sum(1 for i in range(len(LINES)) if phase(t, i * 0.1, i * 0.1 + 0.09) > 0)
        c.rect(6, 18 + max(0, typed - 1) * 9 + 6, 4, 1, G["hi"])

    frame_panel(c, 2, 110, 150, 68, "MEMORY · 0X7FFE0000")
    scroll = int(t * 12)
    for k in range(8):
        row = scroll + k
        rnd = random.Random(row % 16)
        data = [rnd.randrange(256) for _ in range(6)]
        y = 116 + k * 7
        c.text(6, y, f"{0x7FFE0000 + row * 6:08X}", G["lo"], check=False)
        for b, v in enumerate(data):
            hot = (row * 6 + b) % 23 == scroll % 23
            c.text(44 + b * 12, y, f"{v:02X}", G["amber"] if hot else G["mid"], check=False)
        c.text(118, y, "".join(chr(65 + v % 26) for v in data[:6]), G["lo"], check=False)

    frame_panel(c, 154, 13, 164, 92, "PROXY CHAIN")
    for i, j in DOTS:
        c.rect(MAP.x + i * CELL, MAP.y + j * CELL, 2, 2, G["lo"])
    points = [project(lon, lat) for _, lon, lat in CHAIN]
    hop = phase(t, 0.1, 0.9) * (len(CHAIN) - 1)
    for k, ((x0, y0), (x1, y1)) in enumerate(zip(points, points[1:])):
        lift = max(8.0, abs(x1 - x0) * 0.25)
        cx, cy = (x0 + x1) / 2, min(y0, y1) - lift
        done = min(1.0, max(0.0, hop - k))
        for s in range(41):
            u = s / 40
            px = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1
            py = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1
            if u <= done and (s + int(t * 40)) % 3 == 0:
                c.px(round(px), round(py), G["amber"])
            if 0 < done < 1 and abs(u - done) < 0.03:
                c.rect(round(px) - 1, round(py) - 1, 3, 3, "white")
    for k, ((name, _, _), (x, y)) in enumerate(zip(CHAIN, points)):
        reached = hop >= k - 0.01
        c.rect(round(x) - 1, round(y) - 1, 3, 3, G["red"] if reached else G["mid"])
        if reached and blink(t, cycles=6, offset=k * 0.2):
            c.box(round(x) - 3, round(y) - 3, 7, 7, G["red"])
    c.text(158, 96, " → ".join(name for name, *_ in CHAIN[:1 + int(hop)]), G["amber"], check=False)

    frame_panel(c, 154, 110, 164, 68, "SIGNAL")
    rx, ry, r = 186, 144, 27
    for k in (1, 2, 3):
        c.circle(rx, ry, r * k / 3, G["bg"], outline=G["faint"])
    c.hline(rx - r, ry, 2 * r, G["faint"])
    c.vline(rx, ry - r, 2 * r, G["faint"])
    sweep = t * 2 * 2 * math.pi
    for k in range(12):
        a = sweep - k * 0.07
        c.line(rx, ry, round(rx + r * math.cos(a)), round(ry + r * math.sin(a)), G["hi"] if k == 0 else G["lo"])
    for bx, by in ((12, -9), (-15, 6), (6, 16), (-8, -18)):
        a = math.atan2(by, bx)
        age = (sweep - a) % (2 * math.pi)
        c.rect(rx + bx - 1, ry + by - 1, 3, 3, G["amber"] if age < 1.2 else G["lo"])
    c.text(222, 118, "EXFILTRATING", G["mid"])
    c.text(222, 125, "MAINFRAME.DB", "white")
    c.meter(222, 134, 90, 5, phase(t, 0.05, 0.95), G["hi"], track=G["faint"], rim=False)
    c.text(222, 142, f"{phase(t, 0.05, 0.95) * 2.3:.2f} OF 2.30 GB", G["mid"])
    c.text(222, 152, "PACKETS 4,096/S", G["lo"])
    c.text(222, 160, "HOPS  4", G["lo"])
    c.text(222, 168, "ENCRYPTION OFF", G["red"] if blink(t, cycles=4) else G["lo"])

    if 0.47 < t < 0.5 or 0.83 < t < 0.85:
        band = c.img.crop((0, 60, 320, 74))
        c.img.paste(band, (5 if t < 0.6 else -6, 60))
    lines = Image.new("RGB", (320, 180), (255, 255, 255))
    for y in range(1, 180, 2):
        lines.paste((205, 215, 205), (0, y, 320, y + 1))
    c.img.paste(ImageChops.multiply(c.img, lines))


animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=6, fps=10, poster=0.97)
