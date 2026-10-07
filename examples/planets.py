"""The planets to scale: lit, dithered spheres sized by equatorial diameter, Jupiter's bands and
Great Red Spot, Saturn's rings in front of and behind it, and the Sun's edge for scale."""

import math
from pathlib import Path

from pixelkit import Canvas

# name, equatorial diameter in km (NASA planetary fact sheet), shades dark to light
PLANETS = [
    ("MERCURY", 4879, ["dim", "muted", "text"]),
    ("VENUS", 12104, ["gold.dark", "gold", "gold.light"]),
    ("EARTH", 12756, ["blue.dark", "blue", "sky.light"]),
    ("MARS", 6792, ["red.dark", "orange", "orange.light"]),
    ("JUPITER", 142984, ["#6b4a2e", "#c99a6a", "#efd6b0"]),
    ("SATURN", 120536, ["#7d6a3c", "#d8bf7c", "#f4e6b8"]),
    ("URANUS", 51118, ["cyan.dark", "cyan", "cyan.light"]),
    ("NEPTUNE", 49528, ["#1d3f99", "#3f6ee8", "#9db6ff"]),
]
SUN_KM = 1392700
SCALE = 48 / 142984
SATURN_RINGS = 136775 * 2


def chord(cx, cy, r, y):
    half = r * r - (y + 0.5 - cy) ** 2
    if half <= 0:
        return None
    half = math.sqrt(half)
    return math.ceil(cx - half - 0.5), math.floor(cx + half - 0.5)


def ellipse_ring(c, cx, cy, rx, ry, inner, colour, front):
    for py in range(int(cy - ry) - 1, int(cy + ry) + 2):
        if (py + 0.5 > cy) != front:
            continue
        for px in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = math.hypot((px + 0.5 - cx) / rx, (py + 0.5 - cy) / ry)
            if inner <= d < 1:
                band = (d - inner) / (1 - inner)
                c.px(px, py, colour[0] if band < 0.35 else colour[1] if band < 0.8 else colour[2])


c = Canvas(preset="wide")
top = c.header("THE PLANETS, TO SCALE", right="SIZE ONLY · NOT DISTANCE")
bottom = c.footer(f"EQUATORIAL DIAMETERS FROM NASA'S PLANETARY FACT SHEET. AT THIS SCALE THE SUN IS "
                  f"{SUN_KM * SCALE:.0f} PX ACROSS, SO ONLY ITS EDGE FITS.")
sun_r = SUN_KM / 2 * SCALE
sun = Canvas(20, bottom - top - 1, theme=c.theme)
sun.sphere(-sun_r + 16, 92 - top, sun_r, "gold", shades=["orange.dark", "orange", "gold", "gold.light"],
           light=(0.7, -0.2))
c.img.paste(sun.img, (0, top))
c.sparkles(20, top, 300, bottom - top - 1, 70, ["line", "dim", "muted"], seed=4, twinkle=0.06)

mid = 92
x = 22
for i, (name, km, shades) in enumerate(PLANETS):
    r = km / 2 * SCALE
    span = SATURN_RINGS / 2 * SCALE if name == "SATURN" else r
    half = span if name == "SATURN" else max(r, 10)
    cx = x + half
    if name == "SATURN":
        ring_colours = ["#5c4f2e", "#b9a46a", "#e8d9a6"]
        ellipse_ring(c, cx, mid, span, span * 0.22, 0.62, ring_colours, front=False)
    c.sphere(cx, mid, max(r, 0.9), shades[1], shades=shades)
    if name in ("JUPITER", "SATURN"):
        for k, (dy, colour) in enumerate(((-0.55, shades[0]), (-0.2, shades[2]), (0.15, shades[0]), (0.45, shades[2]))):
            y = round(mid + dy * r)
            span_x = chord(cx, mid, r - 1, y)
            if span_x:
                for px in range(span_x[0], span_x[1] + 1):
                    if (px + k) % 2 == 0:
                        c.px(px, y, colour)
        if name == "JUPITER":
            c.circle(cx + r * 0.35, mid + r * 0.32, 3.5, "red.dark")
            c.circle(cx + r * 0.35, mid + r * 0.32, 2.2, "orange")
    if name == "SATURN":
        ellipse_ring(c, cx, mid, span, span * 0.22, 0.62, ring_colours, front=True)
    reach = max(r, 4)
    if i % 2 == 0:
        ly = round(mid - reach - 22)
        c.vline(round(cx), ly + 13, round(mid - reach) - 2 - (ly + 13), "line")
    else:
        ly = round(mid + reach + 9)
        c.vline(round(cx), round(mid + reach) + 2, ly - 2 - (round(mid + reach) + 2), "line")
    c.text(round(cx), ly, name, shades[2], align="center")
    c.text(round(cx), ly + 7, f"{km:,} KM", "dim", align="center")
    x = cx + half + 3

c.save(Path(__file__).with_suffix(".png"))
