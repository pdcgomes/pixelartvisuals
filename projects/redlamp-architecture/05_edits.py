"""5/6 Where an edit lives: the sidecar package beside the photo, its two version numbers, and the
promises that keep photos and edits safe."""

from pathlib import Path

from pixelkit import Canvas
from series import API, APPS, ENGINE, GPU, UI, frame

TREE = [
    # depth, icon, colour, name, what it is
    (0, "folder", APPS, "SHOOT/", "ANY FOLDER YOU ADD; NOTHING IS MOVED"),
    (1, "file", GPU, "IMG_1234.ARW", "THE RAW FILE, NEVER WRITTEN TO"),
    (1, "package", UI, "IMG_1234.ARW.REDLAMP", "THE EDIT: A PACKAGE, ONE FILE IN FINDER"),
    (2, "file", "text", "EDIT.JSON", "RECIPE + SNAPSHOTS, NON-DEFAULTS"),
    (2, "folder", "violet", "MASKS/", "AI MASK PNGS, NAMED BY SHA-256"),
    (2, "folder", "sky", "HISTORY/", "A JSON PATCH FOR EVERY STEP"),
]
FACTS = [("≤2S", "SAVED AFTER AN EDIT", ENGINE), ("SHA-256", "PINS EVERY LOOK", API), ("≤1GB", "THUMBNAIL CACHE", GPU),
         ("0", "PHOTOS OVERWRITTEN", UI)]

c = Canvas(preset="wide")
top, bottom = frame(c, 5, "WHERE AN EDIT LIVES", "FROM THE README'S STORAGE SECTION AND THE SIDECAR SCHEMA.")

tree = c.panel(0, top + 1, 184, 104, "NEXT TO THE PHOTO", color="white", sub="SIDECARS, NO CATALOGUE")
rows = []
for i, (depth, icon, colour, name, what) in enumerate(TREE):
    x, y = tree.x + depth * 11, tree.y + i * 14
    c.icon(x, y, icon, colour)
    c.text(x + 12, y, name, "white")
    c.text(x + 12, y + 7, what, "dim")
    rows.append((depth, x, y))
for i, (depth, x, y) in enumerate(rows):
    kids = []
    for d, kx, ky in rows[i + 1:]:
        if d <= depth:
            break
        if d == depth + 1:
            kids.append((kx, ky))
    if kids:
        c.vline(x + 3, y + 9, kids[-1][1] - y - 4, "line")
        for kx, ky in kids:
            c.hline(x + 3, ky + 4, kx - x - 4, "line")

ver = c.panel(186, top + 1, 134, 104, "TWO VERSIONS", color=c.light(API), sub="IN EVERY EDIT")
c.text(ver.x, ver.y + 1, "3", "white", font="large", scale=2, shadow="line")
c.text(ver.x + 14, ver.y + 1, "FORMAT", c.light(API))
c.paragraph(ver.x + 14, ver.y + 8, "THE FILE'S SYNTAX. OLDER ONES MIGRATE WHEN READ.", ver.w - 14, "text")
py = ver.y + 26
c.text(ver.x, py, "14", "white", font="large", scale=2, shadow="line")
c.text(ver.x + 26, py, "PROCESS", c.light(GPU))
c.paragraph(ver.x + 26, py + 7, "HOW IT RENDERS. AN EDIT KEEPS ITS OWN.", ver.w - 26, "text")
for k in range(14):
    c.tile(ver.x + k * 9, py + 25, 7, GPU if k == 13 else "raised")
c.text(ver.x, py + 35, "1", "dim")
c.text(ver.x + 13 * 9 + 6, py + 35, "14", "dim", align="right")
c.paragraph(ver.x, py + 45, "NEWER THAN THE APP? READ-ONLY, NEVER OVERWRITTEN.", ver.w, "dim")

safe = c.panel(0, tree.y2 + 6, 320, bottom - tree.y2 - 8, "SAFE BY DESIGN", color="white",
               sub="THE ORIGINAL IS NEVER HARMED")
for i, (value, caption, accent) in enumerate(FACTS):
    fx = safe.x + i * 79
    c.text(fx, safe.y, value, c.light(accent), font="large", shadow="line")
    c.text(fx, safe.y + 10, caption, "dim")

c.save(Path(__file__).with_suffix(".png"))
