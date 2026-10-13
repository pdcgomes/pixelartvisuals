"""1.2 What nine days added up to: the counts from Alfama Fighter Turbo's repository at its last
commit of 12 October, and the art kept in the repository against what the game ships.

Animated: the commits count up, then the other figures in turn, then the two bars fill at the same
speed, so the small one lands first; then it holds.

Sources (alfamafighterturbo at 74e2f64):
- 1,548 commits, 348 on 10 October: git rev-list --count; git log --date=short | uniq -c.
- 114 lanes merged into main: the 116 merge commits on main's own line (git rev-list --first-parent
  --merges --count 74e2f64) less two that merged main into the front-end lane before it landed.
- 261 decisions: docs/studio/decisions.md, 263 table rows less 2 header rows.
- 1,362 tests in 128 files: rg -c '^\\s*test\\(' test/*.test.ts.
- 59,461 lines of game and server code: src/ (52,795 of TypeScript and 768 of JavaScript), api/ (3,531)
  and worker/ (2,367); 48,413 lines of tools in 155 files: wc -l at 74e2f64.
- 114 agent conversations: the studio's live board at 17:24, 12 October (AGENT_CHATS).
- About 1 GB of art (1,877 PNG and GIF files): git ls-tree -r -l 74e2f64 art. About 12 MB shipped:
  git ls-tree -r -l 74e2f64 assets, 11,781,240 bytes in 1,138 files.
"""

from pixelkit import ease_out, phase, stagger
from series import ART, ENGINE, PRODUCER, QA, TOOLS, export, frame

FACTS = [
    (114, "LANES MERGED", "PIECES OF WORK", PRODUCER),
    (261, "DECISIONS", "WRITTEN DOWN", "gold"),
    (114, "AGENT CHATS", "ON THE BOARD", PRODUCER),
    (1362, "TESTS", "IN 128 FILES", QA),
    (59461, "LINES OF GAME", "AND SERVERS", ENGINE),
    (48413, "LINES OF", "TOOLS", TOOLS),
]
ART_MB, SHIPPED_MB = 1000, 12


def draw(c, t):
    top, bottom = frame(c, 1, 2, "WHAT NINE DAYS ADDED UP TO", "AT THE LAST COMMIT OF 12 OCTOBER, 16:00; AGENT CHATS FROM THE BOARD AT 17:24.")

    # The hero: commits.
    p = ease_out(phase(t, 0.0, 0.35))
    hero = c.text(6, top + 6, c.num(round(1548 * p)), "white", font="large", scale=3, shadow="dim")
    hero = max(hero, c.measure("1,548", "large", 3))
    c.text(6 + hero + 8, top + 7, "COMMITS IN NINE DAYS", "white")
    c.text(6 + hero + 8, top + 14, "4 TO 12 OCTOBER 2026", "dim")
    c.text(6 + hero + 8, top + 21, "348 ON THE BUSIEST, SATURDAY", "dim")
    c.strip(6, top + 30, max(1, round(hero * p)), 2, c.theme.series)

    # Six figures, in turn.
    grid = c.panel(0, top + 38, c.w, 54, "WHAT THE STUDIO LEFT BEHIND", color=c.light(PRODUCER))
    cols = grid.cols(3, gap=6)
    for i, (value, first, second, accent) in enumerate(FACTS):
        q = ease_out(stagger(t, i, len(FACTS), start=0.25, end=0.65, overlap=0.4))
        col = cols[i % 3]
        y = grid.y + (i // 3) * 21
        w = c.text(col.x, y, c.num(round(value * q)), c.light(accent) if q >= 1 else "white", font="large")
        w = max(w, c.measure(c.num(value), "large"))
        c.text(col.x + w + 4, y, first, "text")
        c.text(col.x + w + 4, y + 7, second, "dim")

    # The art kept against what ships, filling at the same speed.
    art = c.panel(0, grid.y2 + 6, c.w, bottom - grid.y2 - 8, "ART KEPT AGAINST WHAT SHIPS", color=c.light(ART),
                  sub="SOURCES AND PREVIEWS STAY BEHIND")
    fill = ART_MB * phase(t, 0.6, 0.92)
    c.hbars(art.x, art.y + 1, art.w, [("IN THE REPOSITORY", min(ART_MB, fill), ART),
                                     ("WHAT THE GAME SHIPS", min(SHIPPED_MB, fill), "lime")],
            vmax=ART_MB, fmt=lambda v: "ABOUT 1 GB" if v >= ART_MB else f"{round(v)} MB" if v < 100 else f"{v / 1000:.1f} GB",
            label_w=86, value_w=46, bar_h=6, gap=5)


export(draw, __file__, preset="wide", seconds=3.6, fps=20, hold=3)
