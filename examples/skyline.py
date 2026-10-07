"""The world's tallest buildings as an isometric city at dusk, to scale: twinkling windows, blinking
aircraft lights and a plane crossing the sky."""

import random
from pathlib import Path

from pixelkit import Canvas, animate, blink

TOWERS = [
    ("BURJ KHALIFA", "DUBAI", 828), ("MERDEKA 118", "KUALA LUMPUR", 679), ("SHANGHAI TOWER", "SHANGHAI", 632),
    ("CLOCK TOWER", "MECCA", 601), ("PING AN", "SHENZHEN", 599), ("LOTTE WORLD", "SEOUL", 555),
    ("ONE WTC", "NEW YORK", 541), ("CTF GUANGZHOU", "GUANGZHOU", 530), ("CTF TIANJIN", "TIANJIN", 530),
    ("CITIC TOWER", "BEIJING", 528),
]
GROUND, SCALE, W, D = 150, 104 / 828, 4, 4
GLASS = {"top": "#3a4f7a", "left": "#1f2c4c", "right": "#131c33", "lit": "gold", "dimlit": "#7a5a1e"}


def city(c, t, height):
    """The scene, drawn on its own canvas so the floor and towers stay out of the header and footer."""
    ground = GROUND - 13
    c.gradient(0, 0, 192, ground + 4, ["#07081c", "#1a1240", "#4a1d55", "#9a3a55", "#e0703a"])
    rnd = random.Random(3)
    for _ in range(40):
        sx, sy = rnd.randrange(192), rnd.randrange(60)
        c.px(sx, sy, "white" if blink(t, cycles=2, offset=rnd.random(), duty=0.8) else "dim")
    c.circle(160, 18, 7, "#f4e6b8")
    c.circle(163, 16, 6.5, "#0b0a24")
    plane_x = round(-10 + t * 212)
    c.px(plane_x, 30, "white")
    c.px(plane_x - 1, 30, "red" if blink(t, cycles=8) else "white")

    c.rect(0, ground + 1, 192, height - ground, "#0b0f1c")
    c.iso_floor(96, ground - 38, 48, 48, step=6, color="#141a30")
    for i, (name, place, metres) in enumerate(TOWERS):
        h = round(metres * SCALE)
        x = 14 + i * 18
        y = ground - (W + D) - h
        geo = c.iso_box(x, y, W, D, h, top=GLASS["top"], left=GLASS["left"], right=GLASS["right"], edge="#5a6f9a")
        tick = int(t * 4)
        win = random.Random(i * 100 + tick)
        for b in range(3, h - 2, 3):
            for u in (1, 3):
                lit = win.random() < 0.55
                c.px(*geo.left(u + 0.5, b), GLASS["lit"] if lit else GLASS["dimlit"])
            for v in (1, 3):
                if win.random() < 0.35:
                    c.px(*geo.right(v + 0.5, b), GLASS["dimlit"])
        sx, sy = geo.top(W / 2, D / 2)
        spire = 4 + round(h * 0.08)
        c.vline(sx, sy - spire, spire, "muted")
        if blink(t, cycles=2, offset=i * 0.13):
            c.px(sx, sy - spire - 1, "red.light")
        c.text(sx, sy - spire - 9, str(i + 1), "white" if i == 0 else "text", align="center")


def draw(c, t):
    top = c.header("THE WORLD'S TALLEST BUILDINGS", right="TO SCALE · ARCHITECTURAL HEIGHT")
    bottom = c.footer("HEIGHTS TO THE ARCHITECTURAL TOP, SPIRES INCLUDED, FROM THE CTBUH; COMPLETED BUILDINGS AS OF 2025.")
    scene = Canvas(192, bottom - top - 1, theme=c.theme)
    city(scene, t, scene.h)
    c.img.paste(scene.img, (0, top))

    rank = c.panel(194, top + 1, 126, bottom - top - 3, "TOP TEN", color="gold", sub="METRES")
    for i, (name, _, metres) in enumerate(TOWERS):
        y = rank.y + i * 11
        c.text(rank.x, y, f"{i + 1}", "gold" if i == 0 else "dim")
        c.text(rank.x + 10, y, name, "white" if i == 0 else "text")
        c.text(rank.x2, y, f"{metres}", "gold" if i == 0 else "white", align="right")
        c.meter(rank.x + 10, y + 7, rank.w - 10, 1, metres / 828, "gold" if i == 0 else "sky", track="raised", rim=False)


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=10, seamless=True)
