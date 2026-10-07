"""Architecture diagram: nodes, a bus several inputs tap, elbow connectors, a dashed boundary, icons.

Shows how pixelkit itself turns a script into files.
"""

from pathlib import Path

from pixelkit import Canvas

c = Canvas(preset="wide")
top = c.header("PIXELKIT · HOW A GRAPHIC IS MADE", right="DIAGRAM PARTS")
bottom = c.footer("NODE, BUS, CONNECT, ARROW AND DASHES. EVERY FRAME IS DRAWN AND CHECKED AT 1X, THEN SCALED.")

script = c.node(8, top + 6, 92, 19, "YOUR SCRIPT", color="cyan", sub="DRAW(C, T)")
theme = c.node(114, top + 6, 92, 19, "THEME.TOML", color="violet", sub="PALETTE · BRAND")
fonts = c.node(220, top + 6, 92, 19, "FONTS", color="gold", sub="3×5 · 5×7 · ACCENTS")
c.icon(script.x2 - 10, script.y + 4, "file", "cyan")
c.icon(theme.x2 - 12, theme.y + 5, "folder", "violet")

rail = c.bus(54, script.y2 + 8, 212, "line", [script, theme, fonts])
canvas = c.node(104, rail.y2 + 10, 112, 19, "CANVAS", color="green", sub="320×180 · WHOLE PIXELS", badge="1X")
c.arrow(canvas.cx, rail.y2, canvas.cx, canvas.y - 1, "line")
check = c.node(104, canvas.y2 + 10, 112, 19, "CHECK()", color="orange", sub="COLLISIONS · EDGES")
c.connect(canvas, check, "line")

frame = (canvas.x - 8, canvas.y - 5, canvas.w + 16, check.y2 - canvas.y + 9)
for x, y, w, vertical in ((frame[0], frame[1], frame[2], False), (frame[0], frame[1] + frame[3] - 1, frame[2], False),
                          (frame[0], frame[1], frame[3], True), (frame[0] + frame[2] - 1, frame[1], frame[3], True)):
    c.dashes(x, y, w, "dim", vertical=vertical)
c.text(frame[0] + frame[2] + 4, frame[1] + 2, "EVERY", "dim")
c.text(frame[0] + frame[2] + 4, frame[1] + 9, "FRAME", "dim")

gutter = check.y2 + 14
save = c.node(16, gutter + 8, 96, 19, "SAVE()", color="blue", sub="PNG · ×4 NEAREST")
anim = c.node(208, gutter + 8, 96, 19, "ANIMATE()", color="red", sub="GIF · WEBP · MP4")
c.icon(save.x2 - 10, save.y + 4, "file", "blue")
c.icon(anim.x2 - 12, anim.y + 5, "package", "red")
c.connect(check, save, "line", ax=check.x + 20, via=gutter)
c.connect(check, anim, "line", ax=check.x2 - 20, via=gutter, dotted=True, label="OR")

c.save(Path(__file__).with_suffix(".png"))
