"""Personal site, direction A: the home page is the 1992 bedroom, played like a point-and-click
adventure. Each object is a section; the cursor visits them in turn, and the card on the right says
what's there, with the verbs underneath."""

import importlib.util
import math
from pathlib import Path

from pixelkit import Canvas, animate

KIT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("bedroom", KIT / "examples/bedroom.py")
bedroom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bedroom)
P = bedroom.P


def iso(u, v, w, d, h, z=0):
    """Screen bounds (x0, y0, x1, y1) of a bedroom box, as bedroom.box draws it."""
    x, y = P(u, v, z + h)
    return x - 2 * d, y, x + 2 * w, y + w + d + h


def union(*boxes):
    return min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)


# Where each section sits in the room, the verb that opens it, and its card.
SPOTS = [
    ("USE", "PC", union(iso(13, 1, 17, 9, 5, 14), iso(15, 2, 12, 8, 11, 19)), "THE OUTLAND",
     "MY BLOG, AS A BBS YOU DIAL INTO. TEXT FIRST. NO TRACKERS, NO POPUPS.", "DIAL IN", "lime"),
    ("PLAY", "TV", union(iso(42, 0, 14, 10, 5), iso(43, 1, 12, 8, 15, 5)), "GAMES",
     "ALFAMA FIGHTER TURBO AND PARADISE CAFÉ, MADE IN THE EVENINGS.", "PRESS START", "red.light"),
    ("LOOK AT", "POSTERS", (103, 21, 169, 74), "PROJECTS",
     "REDLAMP, A RAW PHOTO EDITOR FOR THE MAC. PIXELKIT, WHICH DREW THIS ROOM. ALGOREASON.", "SEE ALL", "orange"),
    ("READ", "BOOKS", iso(0, 12, 4, 11, 30), "NOTES",
     "SHORTER THINGS: WHAT I'M LEARNING, READING AND HALF-FINISHING.", "BROWSE", "sky"),
    ("CALL", "PHONE", union(iso(34, 8.5, 5, 3, 2, 14), (134, 82, 154, 98)), "CONTACT",
     "GITHUB.COM/PDCGOMES, OR LEAVE A ONE-LINER ON THE BOARD.", "PICK UP", "gold"),
    ("PET", "CAT", (46, 94, 60, 104), "THE CAT",
     "ASLEEP ON THE QUILT. BEST NOT.", "PET ANYWAY", "violet.light"),
]
VERBS = ["LOOK AT", "USE", "PLAY", "READ", "CALL", "PET"]
CURSOR = ["#.......", "##......", "#w#.....", "#ww#....", "#www#...", "#wwww#..", "#www###.", "#w#w#...",
          "##.#w#..", "....##.."]
STAY = 1.0


def ease(p):
    return p * p * (3 - 2 * p)


def corners(c, x0, y0, x1, y1, color, arm=4):
    for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        c.hline(min(x, x + dx * arm), y, arm, color)
        c.vline(x, min(y, y + dy * arm), arm, color)


def draw(c, t):
    top = c.header("PEDRO GOMES", sub="PDCGOMES", right="POINT · CLICK · EXPLORE")
    scene = Canvas(206, c.h - top, theme=c.theme)
    bedroom.room(scene, t, 6.6 + 2.4 * t)
    phase = t * len(SPOTS)
    k = int(phase) % len(SPOTS)
    here = phase - int(phase)
    verb, noun, box, title, blurb, action, color = SPOTS[k]
    prev = SPOTS[k - 1][2]
    glide = ease(min(1.0, here / 0.35))
    centre = lambda b: ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    (ax, ay), (bx, by) = centre(prev), centre(box)
    cx, cy = round(ax + (bx - ax) * glide), round(ay + (by - ay) * glide)
    if glide >= 1:
        on = math.sin(2 * math.pi * here * 3) > -0.3
        corners(scene, box[0] - 2, box[1] - 2, box[2] + 1, box[3] + 1, "white" if on else color)
        label = noun
        lw = scene.measure(label) + 6
        lx = max(1, min(scene.w - lw - 1, round((box[0] + box[2]) / 2 - lw / 2)))
        ly = max(1, box[1] - 12)
        scene.rect(lx, ly, lw, 9, "#000000")
        scene.box(lx, ly, lw, 9, color)
        scene.text(lx + 3, ly + 2, label, "white", check=False)
    scene.sprite(cx, cy, CURSOR, {"#": "#000000", "w": "white"})
    c.img.paste(scene.img, (0, top))

    card = c.panel(208, top + 1, 112, 104, f"{verb} {noun}", color=color)
    c.text(card.x, card.y + 1, title, "white", font="large")
    c.paragraph(card.x, card.y + 14, blurb, card.w, "text")
    c.tag(card.x, card.y2 - 9, f"{action} →", color, fill="#000000")

    verbs = c.panel(208, top + 107, 112, c.h - top - 109, "VERBS", color="dim")
    for i, name in enumerate(VERBS):
        x = verbs.x + (i % 2) * 54
        y = verbs.y + 2 + (i // 2) * 10
        c.text(x, y, name, color if name == verb else "dim")


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=len(SPOTS) * STAY, fps=10,
            seamless=True, poster=0.12)
