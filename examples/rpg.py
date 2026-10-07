"""Character sheet for a developer RPG: portrait, HP/MP/XP, a stats radar, an inventory the cursor
browses, and a quest log. Entirely made up."""

from pathlib import Path

from pixelkit import animate
from pixelkit.art import ICONS

HERO = (["......h....o.",
         ".....hh...ooo",
         ".....hhh...o.",
         "....hhhh...t.",
         "...hhhhhh..t.",
         "..HHHHHHHH.t.",
         "...ssssss..t.",
         "...sesses..t.",
         "...ssssss..t.",
         "..rrrrrrrrst.",
         ".rrrRRrrrr.t.",
         ".rrrrRRrrr.t.",
         ".rrrrrRRrr.t.",
         ".rrrrrrRRr.t.",
         "..rrrrrrr..t.",
         "..bb...bb..t."],
        {"h": "violet", "H": "gold", "s": "#f0c8a0", "e": "#101018", "r": "sky", "R": "sky.light",
         "b": "#5a3a22", "t": "#8a5a2a"})
SPRITES = {
    "sword": (["......##", ".....#w#", "....#w#.", "...#w#..", "g.#w#...", ".gg#....", ".gg.....", "g..g...."],
              {"#": "muted", "w": "white", "g": "gold"}),
    "mug": (["..#.#...", "...#.#..", "........", "#######.", "#ccccc##", "#ccccc.#", "#ccccc##", ".#####.."],
            {"#": "white", "c": "#6a3a1a"}),
    "scroll": ([".######.", "#wwwwww#", ".w----w.", ".w----w.", ".w----w.", "#wwwwww#", ".######."],
               {"#": "#8a5a2a", "w": "#e8d8a8", "-": "muted"}),
}
INVENTORY = [("sword", None), ("mug", None), ("scroll", None), ("heart", "red"),
             ("bolt", "gold"), ("disc", "sky"), ("lock", "orange"), ("cpu", "lime"),
             ("note", "violet"), ("star", "gold"), ("package", "orange"), (None, None)]
BROWSE = [(0, "+3 KEYBOARD OF CLACKING", "ATK +12 · VERY CLACKY"),
          (1, "BOTTOMLESS COFFEE", "RESTORES 50 MP"),
          (2, "SCROLL OF DOCS", "INT +5 · NEVER READ"),
          (10, "BAG OF DEPENDENCIES", "WEIGHS 900 MB")]
STATS = [("CODE", 0.9), ("ART", 0.75), ("DEBUG", 0.8), ("COFFEE", 1.0), ("CALM", 0.35), ("LUCK", 0.55)]
QUESTS = [("check", "lime", "SLAY THE FLAKY TEST", "+300 XP", None),
          ("clock", "gold", "SHIP V1.0 BEFORE FRIDAY", "70%", 0.7),
          ("warn", "red", "FIND THE MISSING SEMICOLON", "OVERDUE", None)]
SLOT, SLOT_GAP = 20, 3


def draw(c, t):
    top = c.header("CHARACTER SHEET", right="PIXELKIT QUEST · SAVE SLOT 1")
    bottom = c.footer("A FICTIONAL HERO. ANY RESEMBLANCE TO REAL DEVELOPERS IS PURELY INTENTIONAL.")
    quest_h = 36
    upper = bottom - top - quest_h - 4

    hero = c.panel(0, top + 1, 106, upper, "HERO", color="violet.light", right="LVL 37", right_color="gold")
    stage_h = 54
    c.rect(hero.x, hero.y, hero.w, stage_h, "#14102a")
    c.sparkles(hero.x + 1, hero.y + 1, hero.w - 2, stage_h - 14, 14, ["dim", "white"], seed=4)
    c.rect(hero.x, hero.y + stage_h - 8, hero.w, 8, "#241c40")
    c.dots(hero.x, hero.y + stage_h - 8, hero.w, "violet.dark")
    bob = 1 if (t * 4) % 2 >= 1 else 0
    glow = "white" if (t * 4) % 2 >= 1 else "cyan.light"
    HERO[1]["o"] = glow
    c.sprite(hero.x + (hero.w - 39) // 2, hero.y + 3 + bob, HERO[0], HERO[1], scale=3)
    c.text(hero.x, hero.y + stage_h + 3, "BYTE THE WIZARD", "white")
    c.text(hero.x, hero.y + stage_h + 10, "SWIFT MAGE · NIGHT OWL", "dim")
    bars = [("HP", 84, 100, "red"), ("MP", 37, 60, "sky"), ("XP", 7420, 10000, "gold")]
    for i, (label, v, vmax, color) in enumerate(bars):
        y = hero.y + stage_h + 19 + i * 8
        c.text(hero.x, y, label, color)
        c.meter(hero.x + 11, y - 1, 52, 7, v / vmax, color)
        c.text(hero.x2, y, f"{c.num(v)}/{c.num(vmax)}", "text", align="right")
    shine = round((t % 1) * 60) - 4
    xp_y = hero.y + stage_h + 34
    fill = round(52 * 0.742)
    if 0 <= shine < fill - 1:
        c.rect(hero.x + 11 + shine, xp_y, 2, 6, "gold.light")

    stats = c.panel(108, top + 1, 104, upper, "STATS", color="cyan.light", right="6 / 6")
    c.radar(stats.cx, stats.y + 46, 27, [v for _, v in STATS], "cyan", labels=[n for n, _ in STATS],
            label_color="text")
    c.text(stats.cx, stats.y2 - 6, "COFFEE IS MAXED OUT", "dim", align="center")

    inv = c.panel(214, top + 1, 106, upper, "INVENTORY", color="gold", right="11/12")
    which = min(int(t * len(BROWSE)), len(BROWSE) - 1)
    pick, name, blurb = BROWSE[which]
    gx = inv.x + (inv.w - 4 * SLOT - 3 * SLOT_GAP) // 2
    for k, (item, color) in enumerate(INVENTORY):
        sx = gx + (k % 4) * (SLOT + SLOT_GAP)
        sy = inv.y + 1 + (k // 4) * (SLOT + SLOT_GAP)
        c.tile(sx, sy, SLOT, "raised")
        if item in SPRITES:
            art, colors = SPRITES[item]
            c.sprite(sx + (SLOT - 2 * len(art[0])) // 2, sy + (SLOT - 2 * len(art)) // 2, art, colors, scale=2)
        elif item:
            rows = ICONS[item].split("/")
            c.icon(sx + (SLOT - 2 * len(rows[0])) // 2, sy + (SLOT - 2 * len(rows)) // 2, item, color, scale=2)
        if k == pick:
            on = (t * 8) % 2 < 1.4
            c.box(sx - 1, sy - 1, SLOT + 2, SLOT + 2, "white" if on else "gold")
    desc_y = inv.y + 3 * (SLOT + SLOT_GAP) + 2
    c.text(inv.x, desc_y, name, "gold")
    c.text(inv.x, desc_y + 7, blurb, "text")

    quest = c.panel(0, bottom - quest_h - 2, 320, quest_h, "QUEST LOG", color="lime", right="GOLD 1,337",
                    right_color="gold")
    for i, (icon, color, title, note, frac) in enumerate(QUESTS):
        y = quest.y + 1 + i * 8
        c.icon(quest.x, y - 1, icon, color)
        c.text(quest.x + 10, y, title, "white" if i != 0 else "dim")
        if frac is not None:
            c.meter(quest.x + 130, y, 60, 5, frac, color)
        c.text(quest.x + 196, y, note, color)


if __name__ == "__main__":
    animate(draw, Path(__file__).with_suffix(".gif"), preset="wide", seconds=4, fps=8, seamless=True)
