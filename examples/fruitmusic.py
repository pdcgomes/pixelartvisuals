"""Fruit Music: a Winamp-style player for the streaming era. Main window with LCD time, spectrum and
marquee, a ten-band equaliser, a playlist, and a modern now-playing pane with album art and lyrics."""

import math
from pathlib import Path

from pixelkit import Canvas, Rect, animate

SKIN = {"frame": "#23232e", "hi": "#4a4a5e", "lo": "#0e0e14", "lcd": "#030806", "green": "#2cf06a",
        "dimgreen": "#145c2c", "title": "#e8c35a"}
CHERRY = (["....gg", "...g..", "..g.g.", ".g...g", "rr..rr", "rrw.rrw", "rrr.rrr", ".r...r."],
          {"g": "lime", "r": "red", "w": "red.light"})
BUTTONS = {
    "prev": "#..#/#.##/####/#.##/#..#",
    "play": "#.../##../###./##../#...",
    "pause": "##.##/##.##/##.##/##.##/##.##",
    "stop": "####/####/####/####",
    "next": "#..#/##.#/####/##.#/#..#",
    "eject": "..#../.###./#####/...../#####",
}
TRACKS = [("NIGHT DRIVE", "4:12"), ("CHROME HEARTS", "3:48"), ("PIXEL RAIN", "5:01"), ("AFTER HOURS", "3:33"),
          ("MOTORWAY 88", "4:44"), ("SAFELIGHT", "3:57"), ("TECHNO VIKING", "6:06"), ("CAFE CENTRAL", "4:20"),
          ("LOW RES LOVE", "3:16"), ("ENDLESS SCROLL", "7:28")]
EQ = [("PRE", 0.55), ("60", 0.85), ("170", 0.75), ("310", 0.6), ("600", 0.45), ("1K", 0.4), ("3K", 0.48),
      ("6K", 0.6), ("12K", 0.72), ("14K", 0.78), ("16K", 0.8)]
LYRICS = ["CITY LIGHTS BEHIND US", "THE RADIO SINGS ALONG"]
MARQUEE = "NEON PARADISE - NIGHT DRIVE (2026) *** "


def window(c, x, y, w, h, title):
    c.rect(x, y, w, h, SKIN["frame"])
    c.hline(x, y, w, SKIN["hi"])
    c.vline(x, y, h, SKIN["hi"])
    c.hline(x, y + h - 1, w, SKIN["lo"])
    c.vline(x + w - 1, y, h, SKIN["lo"])
    for k in range(3):
        c.hline(x + 3, y + 3 + k * 2, w - 6, "#3a3a50" if k != 1 else "#2e2e40")
    tw = c.measure(title)
    c.rect(x + (w - tw) // 2 - 3, y + 2, tw + 6, 7, SKIN["frame"])
    c.text(x + w // 2, y + 3, title, SKIN["title"], align="center")
    return Rect(x + 3, y + 11, w - 6, h - 14)


def clipped(c, x, y, w, h, paint, bg):
    """Draw with paint(sub) on a canvas of its own, then paste it in, so nothing spills out."""
    sub = Canvas(w, h, theme=c.theme, bg=bg)
    paint(sub)
    c.img.paste(sub.img, (x, y))


def sunset(c, x, y, size, t):
    """Synthwave album art: dithered sky, a striped sun, a grid floor rolling towards you."""
    horizon = y + size * 3 // 5
    c.gradient(x, y, size, horizon - y, ["#1b0b3a", "violet.dark", "#d0407a", "orange"])
    sun_r = size * 0.28
    cx, cy = x + size / 2, horizon - sun_r * 0.35
    c.circle(cx, cy, sun_r, "gold")
    for k in range(4):
        c.hline(x, round(cy) + 2 + k * 3, size, "#d0407a" if k < 2 else "orange")
    c.rect(x, horizon, size, y + size - horizon, "#12061e")
    for k in range(-5, 6):
        c.line(round(cx), horizon, round(cx + k * size / 4), y + size - 1, "violet")
    for k in range(5):
        f = ((k + t * 2) % 5) / 5
        gy = horizon + round(f * f * (y + size - horizon - 1))
        c.hline(x, gy, size, "violet")
    c.box(x, y, size, size, SKIN["lo"])


def draw(c, t):
    c.rect(0, 0, 320, 180, "#0a0a10")
    seconds = 102 + int(t * 4)

    main = window(c, 0, 0, 168, 84, "FRUIT MUSIC")
    c.sprite(main.x + 2, 2, CHERRY[0], CHERRY[1])
    lcd = Rect(main.x, main.y, main.w, 36)
    c.rect(*lcd, SKIN["lcd"])
    c.box(*lcd, SKIN["lo"])
    c.sprite(lcd.x + 4, lcd.y + 4, BUTTONS["play"].split("/"), {"#": SKIN["green"]})
    colon = SKIN["green"] if t * 8 % 2 < 1 else SKIN["dimgreen"]
    c.text(lcd.x + 10, lcd.y + 4, f"{seconds // 60:02d}", SKIN["green"], font="large", scale=2)
    c.text(lcd.x + 33, lcd.y + 4, ":", colon, font="large", scale=2)
    c.text(lcd.x + 38, lcd.y + 4, f"{seconds % 60:02d}", SKIN["green"], font="large", scale=2)
    for i in range(19):
        v = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 4 + i * 0.37)) * math.cos(2 * math.pi * (t * 2 + i * 0.11))
        level = max(0.08, min(1.0, v * (1.15 - i / 30)))
        bx = lcd.x + 68 + i * 4
        h = round(level * 16)
        for k in range(h):
            c.hline(bx, lcd.y + 21 - k, 3, "red" if k > 12 else "gold" if k > 8 else SKIN["green"])
    text_w = c.measure(MARQUEE) + 4
    shift = round(t * text_w)

    def marquee(sub):
        for k in range(2):
            sub.text(2 - shift + k * text_w, 1, MARQUEE, SKIN["green"], check=False)

    clipped(c, lcd.x + 4, lcd.y + 25, lcd.w - 8, 8, marquee, "#06140c")
    c.text(main.x, lcd.y2 + 3, "320 KBPS · 44 KHZ · STEREO", SKIN["green"])
    seek_y = lcd.y2 + 11
    c.rect(main.x, seek_y, main.w, 4, SKIN["lo"])
    pos = round(main.w * (seconds / 252))
    c.rect(main.x, seek_y + 1, pos, 2, SKIN["dimgreen"])
    c.rect(main.x + pos - 3, seek_y - 1, 7, 6, SKIN["title"])
    for i, name in enumerate(BUTTONS):
        bx = main.x + i * 15
        c.rect(bx, seek_y + 8, 13, 10, SKIN["hi"] if name == "play" else "#33334a")
        c.box(bx, seek_y + 8, 13, 10, SKIN["lo"])
        rows = BUTTONS[name].split("/")
        c.sprite(bx + (13 - len(rows[0])) // 2, seek_y + 8 + (10 - len(rows)) // 2, rows, {"#": "white"})
    c.text(main.x + 94, seek_y + 10, "VOL", "dim")
    c.rect(main.x + 108, seek_y + 12, 50, 2, SKIN["lo"])
    c.rect(main.x + 108, seek_y + 12, 38, 2, SKIN["green"])
    c.rect(main.x + 144, seek_y + 10, 4, 6, SKIN["title"])

    eq = window(c, 0, 86, 168, 94, "EQUALIZER")
    c.tag(eq.x, eq.y, "ON", SKIN["green"], fill=SKIN["lo"])
    c.tag(eq.x + 16, eq.y, "AUTO", "dim", fill=SKIN["lo"])
    c.tag(eq.x2, eq.y, "PRESET: NIGHT DRIVE", SKIN["title"], fill=SKIN["lo"], align="right")
    top, height = eq.y + 16, 46
    curve = []
    for i, (label, v) in enumerate(EQ):
        sx = eq.x + 6 + i * 14 + (6 if i else 0)
        c.rect(sx, top, 3, height, SKIN["lo"])
        knob = top + round((1 - v) * (height - 5))
        c.rect(sx - 2, knob, 7, 5, SKIN["title"] if i else "sky")
        c.hline(sx - 2, knob, 7, "white")
        c.text(sx + 1, top + height + 4, label, "dim", align="center")
        if i:
            curve.append((sx + 1, knob + 2))
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        c.line(x0, y0, x1, y1, "lime.light")

    pl = window(c, 170, 0, 150, 116, "PLAYLIST · NIGHT DRIVE")
    for i, (name, length) in enumerate(TRACKS):
        y = pl.y + 1 + i * 9
        if i == 0:
            c.rect(pl.x, y - 2, pl.w, 9, "#1c3a8a")
        colour = "white" if i == 0 else SKIN["green"]
        c.text(pl.x + 2, y, f"{i + 1}.", colour)
        c.text(pl.x + 14, y, name, colour)
        c.text(pl.x2 - 2, y, length, colour, align="right")
    c.text(pl.x2 - 2, pl.y2 - 6, "10 TRACKS · 46:25", "dim", align="right")

    now = window(c, 170, 118, 150, 62, "NOW PLAYING")
    clipped(c, now.x + 1, now.y + 1, 44, 44, lambda sub: sunset(sub, 0, 0, 44, t), "#12061e")
    c.box(now.x + 1, now.y + 1, 44, 44, SKIN["lo"])
    lx = now.x + 50
    c.text(lx, now.y + 1, "NEON PARADISE", "white")
    c.tag(lx, now.y + 9, "LOSSLESS", "sky.light", fill=SKIN["lo"])
    c.tag(lx + 42, now.y + 9, "SPATIAL", "violet.light", fill=SKIN["lo"])
    for k, line in enumerate(LYRICS):
        c.text(lx, now.y + 22 + k * 7, line, "white" if k == 1 else "dim")
    c.text(now.x2 - 2, now.y2 - 6, "AIRPLAY → KITCHEN", "dim", align="right")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=10, seamless=True)
