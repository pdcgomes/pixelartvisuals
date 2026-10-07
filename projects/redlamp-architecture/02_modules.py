"""2/6 Modules and boundaries: the 14 modules of Module.swift, the API every module but two taps,
the allowed dependencies between them, and the apps on top."""

from pathlib import Path

from pixelkit import Canvas, Rect
from series import API, APPS, ENGINE, GPU, UI, frame

COL_W, GAP, LEFT = 60, 7, 9


def col(i: int, span: int = 1) -> tuple[int, int]:
    return LEFT + i * (COL_W + GAP), span * COL_W + (span - 1) * GAP


c = Canvas(preset="hd")
RULES = [
    (UI, "THE UI SEES THE ENGINE ONLY THROUGH ENGINEAPI, PLUS THE PURE-VALUE DOCUMENT AND RECIPES."),
    (ENGINE, "ENGINE MODULES IMPORT NO APPKIT, UIKIT OR SWIFTUI: CHECK-ENGINE-PURITY.SH FAILS THE BUILD."),
    (ENGINE, "GENERATIVE KEEPS MLX TO ITSELF, SO NOTHING ELSE LINKS IT. IT IS ALSO MAC ONLY."),
    (UI, "LAB SHIPS ONLY IN THE HARNESS; AUTOMATION COMPILES ONLY IN DEBUG AND PROFILING BUILDS."),
]

c = Canvas(preset="hd")
top, bottom = frame(c, 2, "MODULES AND BOUNDARIES",
                    "ALLOWED DEPENDENCIES FROM TUIST/PROJECTDESCRIPTIONHELPERS/MODULE.SWIFT; LAB AND AUTOMATION "
                    "ALSO LINK DESIGN, RECIPES AND MORE.")

# Apps.
c.text(LEFT, top + 4, "APPS", "muted")
app_y = top + 12
ax, aw = col(0, 2)
app = c.node(ax, app_y, aw, 19, "REDLAMP.APP", color=APPS, sub="THE MAC APP · LINKS 10 MODULES")
dx, dw = col(2, 2)
decoder = c.node(dx, app_y, dw, 19, "REDLAMPDECODER · XPC", color=APPS, sub="LIBRAW · NO FILE ACCESS", border=None)
for x, y, n, vertical in ((dx, app_y, dw, False), (dx, app_y + 18, dw, False), (dx, app_y, 19, True),
                          (dx + dw - 1, app_y, 19, True)):
    c.dashes(x, y, n, "muted", vertical=vertical)
c.icon(decoder.x2 - 11, app_y + 5, "lock", "muted")
c.arrow(app.x2, app.cy, decoder.x - 1, app.cy, "muted")
cli = c.node(col(4)[0], app_y, COL_W, 19, "REDLAMP CLI", color=APPS, sub="HEADLESS")
hx, hw = col(5, 2)
harness = c.node(hx, app_y, hw, 19, "HARNESS", color=APPS, sub="COMPONENT REVIEW · LAB")

# UI side.
ui_y = app_y + 40
c.text(LEFT, ui_y - 8, "UI SIDE · MACOS ONLY", c.light(UI))
design = c.node(col(0)[0], ui_y, COL_W, 19, "DESIGN", color=UI, sub="DESIGN TOKENS")
ui = c.node(col(1)[0], ui_y, COL_W, 19, "UI", color=UI, sub="PANELS · MODEL")
canvas = c.node(col(2)[0], ui_y, COL_W, 19, "CANVAS", color=UI, sub="METAL VIEW")
lab = c.node(col(4)[0], ui_y, COL_W, 19, "LAB", color=UI, sub="HARNESS ONLY")
automation = c.node(col(5)[0], ui_y, COL_W, 19, "AUTOMATION", color=UI, sub="DEBUG ONLY")
c.arrow(ui.x - 1, ui.cy, design.x2, ui.cy, "white")
c.arrow(ui.x2, ui.cy, canvas.x - 1, ui.cy, "white")
c.connect(lab, ui, "dim", side="top", ax=lab.cx, bx=ui.cx + 6, via=ui_y - 4, dotted=True)
c.connect(automation, ui, "dim", side="top", ax=automation.cx, bx=ui.cx + 12, via=ui_y - 4, dotted=True)

# Engine side.
bus_y = ui_y + 35
eng_y = bus_y + 18
names = [("DOCUMENT", "SIDECARS"), ("RECIPES", "LOOKS · LUTS"), ("COLOR", "OKLAB · CAMERA"), ("MASKING", "AI MASKS"),
         ("SERVICES", "LIBRAW DECODE"), ("ENGINE", "RENDER LOOP"), ("GENERATIVE", "MLX · MAC ONLY")]
eng = {name: c.node(col(i)[0], eng_y, COL_W, 19, name, color=ENGINE, sub=sub) for i, (name, sub) in enumerate(names)}
kernels = c.node(eng["ENGINE"].x, eng_y + 40, COL_W, 19, "KERNELS", color=GPU, sub="METAL SHADERS")

c.arrow(eng["RECIPES"].x2, eng["RECIPES"].cy, eng["COLOR"].x - 1, eng["RECIPES"].cy, "white")
c.arrow(eng["MASKING"].x - 1, eng["MASKING"].cy, eng["COLOR"].x2, eng["MASKING"].cy, "white")
c.arrow(eng["ENGINE"].x - 1, eng["ENGINE"].cy, eng["SERVICES"].x2, eng["ENGINE"].cy, "white")
e = eng["ENGINE"]
c.connect(e, eng["MASKING"], "white", side="bottom", ax=e.x + 8, bx=eng["MASKING"].x2 - 10, via=e.y2 + 4)
c.connect(e, eng["COLOR"], "white", side="bottom", ax=e.x + 16, bx=eng["COLOR"].x2 - 10, via=e.y2 + 8)
c.connect(e, kernels, "white", ax=e.x2 - 12, bx=kernels.x2 - 12)
c.text(LEFT, eng_y + 30, "ENGINE SIDE · MAC, IPAD AND IPHONE · NO UI IMPORTS (CI CHECKS)", c.light(ENGINE))

# The API between the two sides, and the two pure-value modules the UI may also link.
taps = [design, ui, canvas, lab, automation] + [eng[n] for n, _ in names if n != "MASKING"] + [
    (eng["MASKING"], eng["MASKING"].x + 6)]
rail = c.bus(LEFT, bus_y, 462, API, taps, thick=2)
c.tag(col(3)[0] + COL_W // 2, bus_y - 4, "ENGINEAPI", c.light(API), border=API, align="center")
c.connect(ui, eng["DOCUMENT"], c.light(UI), ax=ui.x + 6, bx=eng["DOCUMENT"].x2 - 6, via=bus_y + 9, dotted=True)
c.connect(ui, eng["RECIPES"], c.light(UI), ax=ui.x2 - 8, bx=eng["RECIPES"].x2 - 8, dotted=True)

# The rules the graph encodes, and how to read the lines.
rules = c.panel(LEFT, kernels.y2 + 8, 462, bottom - kernels.y2 - 10, "RULES", color="white",
                sub="WHAT MODULE.SWIFT AND CI ENFORCE")
lx = rules.x2 - 150
c.hline(lx, rules.y - 6, 9, "white")
c.text(lx + 12, rules.y - 8, "DEPENDS ON", "dim")
c.dashes(lx + 64, rules.y - 6, 9, c.light(UI), on=1, off=1)
c.text(lx + 76, rules.y - 8, "EXCEPTION, DEV ONLY", "dim")
for i, (accent, rule) in enumerate(RULES):
    rx, ry = rules.x + (i % 2) * 230, rules.y + (i // 2) * 17
    c.text(rx, ry, str(i + 1), c.light(accent), font="large")
    c.paragraph(rx + 9, ry, rule, 212, "text")

c.save(Path(__file__).with_suffix(".png"))
