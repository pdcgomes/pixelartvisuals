"""3.3 The roster by height: the eight fighters, tallest first, each with his fighting-game archetype,
his standing height drawn at the game's own scale (one pixel here is one pixel in the game) and his
jump, against the 112 px ceiling for anyone with the standard jump; Adamastor, the boss, at 130 px
below them, the one who never jumps. A prop that stands higher than the head (A Padeira's bread shovel,
A Varina's basket, Zé Povinho's hat) is a darker extension of the bar. Animated: the ceiling and the
labels are there from the start, the bars grow in turn and their heights count up, then it holds.

Numbers and sources (alfamafighterturbo at 74e2f64):
- Heights, props and jumps: docs/studio/roster-bible.md, section 3.2, the Bodies table (heights feet to
  crown in the stance, upright; jump heights by the jump formula, O Fadista's 84 as played). D. Afonso
  is shown as drawn and approved, 117 px, with his planned 108 marked (the same row, and
  docs/studio/decisions.md, "Every fighter is approved as he stands", 8 October).
- Adamastor 130 px, no jump: roster bible, section 5, "Body"; docs/studio/art-bible.md, section 2.1.
- The 112 px ceiling, props included, for the standard 84 px jump (200 - 84 - 112 = 4 px below the top
  of the screen): docs/studio/art-bible.md, section 2.1, "Limits".
- Archetypes: roster bible, section 1, the roster at a glance.
"""

from pixelkit import ease_out, stagger
from series import export, frame

FIGHTERS = [
    # name, archetype, height, (prop, its height) or None, jump px, planned height or None
    ("D. AFONSO", "CHARGE", 117, None, 72, 108),
    ("A PADEIRA", "SLOW AND STRONG", 108, ("SHOVEL", 118), 65, None),
    ("O CALCETEIRO", "CHARGE", 106, None, 65, None),
    ("O FADISTA", "ALL-ROUNDER", 100, None, 84, None),
    ("CAMÕES", "ZONER", 98, None, 81, None),
    ("A VARINA", "FAST AND FRAGILE", 90, ("BASKET", 102), 92, None),
    ("ZÉ POVINHO", "GRAPPLER", 90, ("HAT", 94), 61, None),
    ("A AVÓ", "RUSHDOWN", 86, None, 61, None),
]
BOSS = ("ADAMASTOR", "THE BOSS, A GIANT", 130, None, None, None)
CEILING = 112
FIGHTER, BOSS_COL, PROP = "orange", "purple", "orange.dark"
ROW = 14


def bar_row(c, x, y, row, g, color, bar_x, notes_x):
    name, kind, height, prop, jump, planned = row
    c.text(x, y, name, "white")
    c.text(x, y + 6, kind, "dim")
    by = y + 3
    c.rect(bar_x, by, CEILING + 20, 5, "raised")
    if prop:
        c.rect(bar_x, by, max(0, round(prop[1] * g)), 5, PROP)
    w = max(1, round(height * g))
    c.rect(bar_x, by, w, 5, color)
    c.hline(bar_x, by, w, f"{color}.light")
    if planned and g >= 1:
        c.vline(bar_x + planned - 1, by - 1, 7, "white")
    shown = round(height * g)
    line = f"{shown} PX"
    if g >= 1:
        line += f" · PLANNED {planned}" if planned else f" · {prop[0]} {prop[1]}" if prop else ""
    c.text(notes_x, y, line, "white")
    c.text(notes_x, y + 6, f"JUMPS {jump} PX" if jump else "NEVER JUMPS", "dim" if jump != 84 else "text")


def draw(c, t):
    top, bottom = frame(c, 3, 3, "THE ROSTER BY HEIGHT",
                        "112 PX IS THE CEILING, PROPS INCLUDED, FOR THE STANDARD 84 PX JUMP.")
    p = c.bounds._replace(x=4, y=top + 4, w=c.w - 8, h=bottom - top - 6)
    bar_x = p.x + 70
    notes_x = bar_x + 136
    ceiling_x = bar_x + CEILING
    c.text(p.x, p.y, "FIGHTER", "muted")
    c.text(bar_x, p.y, "STANDING HEIGHT, 1:1", "muted")
    c.text(ceiling_x, p.y, "112 PX", "white", align="center")
    c.text(notes_x, p.y, "HEIGHT · JUMP", "muted")
    rows_y = p.y + 9
    rows_end = rows_y + len(FIGHTERS) * ROW + 3 + ROW

    n = len(FIGHTERS) + 1
    for i, row in enumerate(FIGHTERS):
        g = ease_out(stagger(t, i, n, start=0.05, end=0.82, overlap=0.4))
        bar_row(c, p.x, rows_y + i * ROW, row, g, FIGHTER, bar_x, notes_x)
    sep = rows_y + len(FIGHTERS) * ROW
    c.dots(p.x, sep, p.w, "line")
    g = ease_out(stagger(t, n - 1, n, start=0.05, end=0.82, overlap=0.4))
    bar_row(c, p.x, sep + 3, BOSS, g, BOSS_COL, bar_x, notes_x)
    c.vdots(ceiling_x, p.y + 7, rows_end - p.y - 9, "white")


if __name__ == "__main__":
    export(draw, __file__, preset="wide", seconds=2.8, fps=20, hold=3, poster=1.0)
