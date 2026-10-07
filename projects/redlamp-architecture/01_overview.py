"""1/6 At a glance: Redlamp as a stack of layers, with the request and frame crossing the API."""

from pathlib import Path

from pixelkit import Canvas
from series import API, APPS, ENGINE, GPU, UI, frame

LAYERS = [
    # name, accent, slab height, title, qualifier, description, face pattern
    ("apps", APPS, 6, "APPS", "", "REDLAMP.APP · REDLAMP CLI · HARNESS", None),
    ("ui", UI, 8, "UI", "· MACOS", "APPKIT PANELS · EDITORMODEL · CANVAS", None),
    ("api", API, 3, "ENGINEAPI", "· THE ONLY DOOR", "VALUE TYPES: REQUESTS IN, FRAMES OUT", None),
    ("engine", ENGINE, 8, "ENGINE", "· MAC, IPAD, IPHONE", "RENDER LOOP · PYRAMID · DETAIL STAGE", "mesh"),
    ("gpu", GPU, 7, "METAL", "· EVERY PIXEL", "SHADERS · ONE FUSED DEVELOP KERNEL", "slots"),
]
FACTS = [("<16MS", "SLIDER TO SCREEN", UI), ("0", "PIXELS COPIED", API), ("14", "MODULES", ENGINE),
         ("1", "FUSED KERNEL", GPU)]
OX, OY, W, D, GAP = 74, 22, 22, 18, 10

c = Canvas(preset="wide")
top, bottom = frame(c, 1, "ARCHITECTURE AT A GLANCE")

ys, y = [], OY
for _, _, h, *_ in LAYERS:
    ys.append(y)
    y += h + GAP
boxes = {}
for (name, accent, h, title, qual, desc, pattern), y in reversed(list(zip(LAYERS, ys))):
    shades = ("text", "muted", "dim") if accent == APPS else (c.light(accent), accent, c.dark(accent))
    patterns = {"left": (pattern, c.dark(accent))} if pattern else None
    boxes[name] = c.iso_box(OX, y, W, D, h, top=shades[0], left=shades[1], right=shades[2],
                            edge="white" if accent == API else None, shadow="shadow", patterns=patterns)
for u, col in ((2, "red.light"), (9, "white"), (16, "violet.light")):
    c.iso_box(*boxes["apps"].top(u, 7), 5, 5, 2, top=col, left=c.dark(col) if col != "white" else "muted",
              right="dim")

for (name, accent, h, title, qual, desc, _), y in zip(LAYERS, ys):
    lx, ly = OX + 2 * W + 3, y + W + h // 2
    c.dots(lx, ly, 150 - lx, "dim")
    c.spans(153, ly - 6, [(title, "white" if accent == APPS else c.light(accent)), (f" {qual}" if qual else "", "dim")])
    c.text(153, ly + 1, desc, "text")

edit_top, edit_bottom = ys[1] + D + 4, ys[3] + D + 4
c.arrow(30, edit_top, 30, edit_bottom, UI)
c.arrow(35, edit_bottom, 35, edit_top, GPU)
c.text(26, edit_top, "EDIT", c.light(UI), align="right")
c.text(26, edit_bottom - 4, "FRAME", c.light(GPU), align="right")

fy = ys[-1] + W + D + LAYERS[-1][2] + 9
for i, (value, caption, accent) in enumerate(FACTS):
    fx = 8 + i * 78
    c.text(fx, fy, value, c.light(accent), font="large", scale=2, shadow="line")
    c.text(fx, fy + 17, caption, "dim")

c.save(Path(__file__).with_suffix(".png"))
