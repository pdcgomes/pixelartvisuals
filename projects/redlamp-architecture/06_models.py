"""6/6 Models on the Mac: the on-device models behind the AI masks, by download size."""

from pathlib import Path

from pixelkit import Canvas
from series import API, ENGINE, GPU, UI, frame

MODELS = [
    # name, MB (0 = built in), colour, what it powers
    ("SAM 3", 988, "violet", "LANDSCAPE, HAIR, PEOPLE'S PARTS"),
    ("DEPTH ANYTHING 3", 336, "sky", "SKY EDGES, DEPTH RANGE"),
    ("VITMATTE", 109, "cyan", "STRAY STRANDS AT EDGES"),
    ("SAM 2.1", 80, "green", "OBJECTS: CLICK, BOX OR BRUSH"),
    ("APPLE VISION", 0, "gold", "SUBJECT, SKY, PEOPLE, BACKGROUND"),
]

c = Canvas(preset="wide")
top, bottom = frame(c, 6, "MODELS ON THE MAC",
                    "FROM THE README'S MASKING SECTION; OWLV2 (FIND) AND GENERATIVE FILL ON MLX ARE ALSO "
                    "ON-DEVICE, SIZES NOT LISTED.")

models = c.panel(0, top + 1, 206, bottom - top - 3, "AI MASKS", color=c.light(UI), sub="BY DOWNLOAD SIZE")
step = 23
c.hbars(models.x, models.y, models.w, [(name, mb, col) for name, mb, col, _ in MODELS], vmax=988,
        fmt=lambda mb: f"{mb} MB" if mb else "BUILT IN", label_w=70, bar_h=5, gap=step - 5)
for i, (_, _, _, use) in enumerate(MODELS):
    c.text(models.x + 70, models.y + i * step + 7, use, "dim")

side = c.panel(208, top + 1, 112, bottom - top - 3, "PRIVATE", color=c.light(ENGINE), sub="BY DESIGN")
c.text(side.x, side.y + 1, "0", c.light(ENGINE), font="large", scale=2, shadow="line")
c.paragraph(side.x + 14, side.y + 1, "PHOTOS EVER UPLOADED", side.w - 14, "white")
c.paragraph(side.x, side.y + 20, "EVERY MODEL RUNS ON THE MAC ITSELF, WITH NO CLOUD AND NO CREDITS.", side.w, "text")
total = sum(mb for _, mb, *_ in MODELS)
c.text(side.x, side.y + 52, f"{total / 1000:.1f} GB", c.light(GPU), font="large")
c.paragraph(side.x, side.y + 62, "FOR ALL FOUR DOWNLOADS. SETTINGS > MODELS LISTS AND REMOVES THEM, EACH WITH ITS "
            "LICENCE.", side.w, "dim")
c.icon(side.x2 - 7, side.y, "lock", c.light(API))
mac = c.iso_box(side.cx + 4, side.y2 - 31, 16, 14, 6, top=["white", "text", "muted"], left="muted",
                right=["muted", "dim"], edge="white", corner="white", shadow="shadow",
                patterns={"left": ("slots", "dim")})
c.px(*mac.right(11, 3), c.light(ENGINE))

c.save(Path(__file__).with_suffix(".png"))
