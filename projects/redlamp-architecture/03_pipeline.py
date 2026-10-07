"""3/6 From raw to screen: the stages a photo goes through, the fused kernel's order, and timings."""

from pathlib import Path

from pixelkit import Canvas
from series import APPS, ENGINE, GPU, UI, frame

STAGES = [
    # title, accent, two lines of detail
    ("RAW FILE", APPS, "ARW CR3 NEF RAF DNG", "JPEG HEIC TIFF PNG"),
    ("DECODER · XPC", APPS, "LIBRAW UNPACKS ONLY", "SANDBOXED, NO FILES"),
    ("GPU PREP", GPU, "LEVELS · AS-SHOT WB", "HOT PIXELS · HIGHLIGHTS"),
    ("DEMOSAIC", GPU, "BAYER OR X-TRANS", "MIP PYRAMID · CACHED"),
    ("DETAIL STAGE", GPU, "DENOISE · SHARPEN", "TEXTURE · CLARITY · CACHED"),
    ("FUSED KERNEL", GPU, "ONE METAL PASS: EVERY MASK, THEN", "EVERY SLIDER, FOR EACH PIXEL"),
    ("CANVAS", UI, "IOSURFACE, NO COPY", "DISPLAY-LINK THREAD"),
]
KERNEL = [
    # label, colour, width, details
    ("MASKS", "violet", 58, ["COVERAGE", "FIRST"]),
    ("SCENE-REFERRED · LINEAR REC.2020", "sky", 168, ["DEHAZE · WB RATIO · CAMERA MATRIX", "EXPOSURE · HALATION · BLOOM",
                                                       "TONE AS LOG GAINS"]),
    ("TONE CURVE", "gold", 62, ["ROLLS OFF TO", "WHITE AT +4 EV"]),
    ("DISPLAY-REFERRED", "orange", 118, ["BASE LOOK · OKLCH COLOR", "CURVE · VIGNETTE · GRAIN"]),
    ("OUTPUT", "white", 56, ["GAMUT FIT", "SRGB OR P3"]),
]
TIMES = [("70–250MS", "OPEN A 24–26 MP RAW", GPU), ("0.6–3MS", "RENDER AT FIT", ENGINE),
         ("~13MS", "RENDER AT 1:1, 26 MP", ENGINE), ("~45MS", "FULL-SIZE EXPORT", UI)]
MORE = [("~1.3MS", "FIT, TWO GRADIENT MASKS"), ("~100MS", "EXPORT WITH NOISE REDUCTION"),
        ("~5MS", "DETAIL STAGE, 1:1 REGION"), ("1.3GB", "DETAIL STAGE MEMORY AT 1:1")]

c = Canvas(preset="hd")
top, bottom = frame(c, 3, "FROM RAW TO SCREEN", "TIMINGS FROM THE README'S MEASURED PERFORMANCE TABLE.")


def stage(x, y, w, spec):
    title, accent, line1, line2 = spec
    n = c.node(x, y, w, 26, title, color=accent, sub=line1)
    c.text(n.x + 3, n.y + 18, line2, "dim")
    return n


row1 = [stage(9 + i * 118, top + 9, 108, s) for i, s in enumerate(STAGES[:4])]
for a, b in zip(row1, row1[1:]):
    c.arrow(a.x2, a.cy, b.x - 1, a.cy, "white")
decoder = row1[1]
for x, y, n, vertical in ((decoder.x, decoder.y, decoder.w, False), (decoder.x, decoder.y2 - 1, decoder.w, False),
                          (decoder.x, decoder.y, decoder.h, True), (decoder.x2 - 1, decoder.y, decoder.h, True)):
    c.dashes(x, y, n, "muted", vertical=vertical)
c.icon(decoder.x2 - 11, decoder.y + 5, "lock", "muted")
c.icon(row1[0].x2 - 10, row1[0].y + 5, "file", "muted")

y2 = row1[0].y2 + 18
detail = stage(9, y2, 108, STAGES[4])
kernel = stage(127, y2, 226, STAGES[5])
canvas = stage(363, y2, 108, STAGES[6])
c.connect(row1[-1], detail, "white", ax=row1[-1].cx, bx=detail.cx, via=row1[0].y2 + 8)
c.arrow(detail.x2, detail.cy, kernel.x - 1, detail.cy, "white")
c.arrow(kernel.x2, kernel.cy, canvas.x - 1, kernel.cy, "white")

# The fused kernel, opened up: one pass, in this order.
band_y = kernel.y2 + 30
c.line(kernel.x, kernel.y2 + 2, 9, band_y - 12, "dim")
c.line(kernel.x2 - 1, kernel.y2 + 2, 470, band_y - 12, "dim")
c.text(9, band_y - 10, "INSIDE THE FUSED KERNEL, IN ORDER", "white")
c.text(471, band_y - 10, "REC.2020 PRIMARIES UNTIL THE OUTPUT FIT", "dim", align="right")
x = 9
for label, colour, w, details in KERNEL:
    c.rect(x, band_y, w - 2, 6, colour)
    c.hline(x, band_y, w - 2, c.light(colour))
    c.text(x, band_y + 9, label, c.light(colour) if colour != "white" else "white")
    for k, line in enumerate(details):
        c.text(x, band_y + 17 + k * 7, line, "text")
    x += w

stats = c.panel(9, band_y + 44, 462, bottom - band_y - 46, "MEASURED", color="white",
                sub="APPLE M1 ULTRA · RELEASE BUILD")
for i, (value, caption, accent) in enumerate(TIMES):
    sx = stats.x + i * 116
    c.text(sx, stats.y + 1, value, c.light(accent), font="large", scale=2, shadow="line")
    c.text(sx, stats.y + 19, caption, "dim")
for i, (value, caption) in enumerate(MORE):
    sx = stats.x + i * 116
    c.text(sx, stats.y + 32, value, "white", font="large")
    c.text(sx, stats.y + 42, caption, "dim")

c.save(Path(__file__).with_suffix(".png"))
