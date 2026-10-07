"""Ranking card: hero total, language split, top-N horizontal bars, small daily bar chart.

Real data: the cafe-central repo (Paradise Café remaster) at commit 8edd94b.
"""

from pathlib import Path

from pixelkit import Canvas

LANGUAGES = [("JS", 5225, "yellow"), ("PY", 1075, "blue"), ("MD", 147, "muted"), ("HTML", 35, "orange"),
             ("JSON", 14, "green")]
FOLDERS = {"content": "orange", "engine": "cyan", "scenes": "purple", "tools": "blue", "root": "green"}
FILES = [
    ("ORIGINAIS.JS", 614, "content"), ("AUDIO.JS", 490, "engine"), ("STREET.JS", 382, "scenes"),
    ("FX.JS", 352, "engine"), ("MUSICA.JS", 296, "content"), ("MENUS.JS", 248, "scenes"),
    ("QUARTO.JS", 247, "scenes"), ("SLICE_SHEET.PY", 207, "tools"), ("MAIN.JS", 196, "root"),
    ("CREDITOS.JS", 185, "scenes"),
]
COMMITS = [("2 OCT", 10), ("3 OCT", 2), ("4 OCT", 2)]

c = Canvas(preset="standard")
c.header("PARADISE CAFÉ REMASTER · ANATOMY", right="GIT @ 8EDD94B")
bottom = c.footer("LINES COUNTED WITH WC -L OVER GIT LS-FILES, LEAVING OUT REFERENCE DUMPS, BUILDS AND ART. "
                  "CAFE-CENTRAL REPO AS OF 4 OCT 2026.")

total = sum(n for _, n, _ in LANGUAGES)
hero_w = c.text(6, 19, c.num(total), "white", font="large", scale=3, shadow="dim")
c.strip(6, 43, hero_w, 2, [col for *_, col in LANGUAGES])
cx = 6 + hero_w + 8
c.text(cx, 21, "LINES OF CODE", "white")
c.text(cx, 28, f"IN {len(LANGUAGES)} LANGUAGES", "dim")
c.text(cx, 35, f"{sum(n for _, n in COMMITS)} COMMITS, {len(COMMITS)} DAYS", "dim")

js_share = LANGUAGES[0][1] / total
lang = c.panel(170, 15, 150, 33, "LANGUAGES", color="yellow", right=f"JS {js_share:.0%}", right_color="yellow")
c.stacked(lang.x, lang.y, lang.w, 5, [(n, col) for _, n, col in LANGUAGES], total=total)
c.legend(lang.x, lang.y + 9, [(name, col) for name, _, col in LANGUAGES], gap=7)

files = c.panel(0, 50, 214, bottom - 52, "BIGGEST FILES", color="orange", sub="LINES EACH")
end = c.hbars(files.x, files.y + 1, files.w, [(name, n, FOLDERS[folder]) for name, n, folder in FILES],
              bar_h=8, gap=5)
c.legend(files.x, end + 5, [(name.upper(), col) for name, col in FOLDERS.items()], gap=8)

days = c.panel(216, 50, 104, bottom - 52, "COMMITS", color="green", sub="BY DAY")
c.bar_chart(days.x, days.y + 8, days.w, days.h - 20, [n for _, n in COMMITS], colors=["green"] * 3,
            ticks=2, ymax=10, xlabels=[d for d, _ in COMMITS])

c.save(Path(__file__).with_suffix(".png"))
