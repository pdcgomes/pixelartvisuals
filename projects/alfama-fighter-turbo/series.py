"""Shared frame for Making Alfama Fighter Turbo, the badcoffee.dev devlog series: header, footer,
colour roles and the motion of a message along a path.

Every image is `PP-N_name.py` (part PP, image N), drawn as `draw(c, t)` and exported with
`export(draw, __file__, ...)`, which writes `PP-N_name.gif` and `PP-N_name-poster.png` beside it.
"""

from pathlib import Path

from pixelkit import animate, load_theme

SERIES = "MAKING ALFAMA FIGHTER TURBO"
GAME = "ALFAMA FIGHTER TURBO"
PARTS = 10
COMMIT = "74E2F64"
SOURCE = f"THE GAME'S REPOSITORY, 12 OCT 2026 16:00 (COMMIT {COMMIT})"

THEME = load_theme()
THEME.brand["name"] = "BADCOFFEE.DEV"

# One colour per role in the studio, the same in every image.
DIRECTOR, PRODUCER, ART, AUDIO, ENGINE, QA, NET, TOOLS = "gold", "cyan", "red", "violet", "green", "blue", "sky", "lime"

# The badcoffee gremlin at header size: the site's favicon (art/mascots/gremlin/favicon.txt in
# badcoffee.dev) with its horns' second row and its chin's last row taken out, 16 x 11.
GREMLIN = (
    [
        ".BB..........BB.",
        "..BBBB.BB.BBBB..",
        ".BBBBBBBBBBBBBB.",
        "BKKKKKBBBBBKKBBB",
        "BKWWWKBBKKKKKBBB",
        "BKWKWKBBBKWWKBBB",
        "BKWWWKBBBKKKKBBB",
        "BKKKKKBBBBBBBBBB",
        "BBBBBBWKKKBBBBBB",
        ".BBBBBBBWBBBBBB.",
        "..BBBBBBBBBBBB..",
    ],
    {"B": "orange", "K": "shadow", "W": "white"},
)


def frame(c, part: int, n: int, title: str, notes: str = "") -> tuple[int, int]:
    """Header and footer for image n of part `part` (n names the file; the header shows only the
    part). Returns the content's top and bottom rows."""
    bottom = c.footer(f"{notes} SOURCE: {SOURCE}." if notes else f"SOURCE: {SOURCE}.")
    top = c.header(f"{GAME} · {title}", right=[("PART ", "dim"), (str(part), "text"), (f" OF {PARTS}", "dim")], mark=GREMLIN)
    return top, bottom


def along(points, p: float) -> tuple[int, int]:
    """The point a share p of the way along an orthogonal path through `points`."""
    segs = list(zip(points, points[1:]))
    d = max(0.0, min(1.0, p)) * sum(abs(x1 - x0) + abs(y1 - y0) for (x0, y0), (x1, y1) in segs)
    for (x0, y0), (x1, y1) in segs:
        n = abs(x1 - x0) + abs(y1 - y0)
        if d <= n:
            k = d / n if n else 0
            return round(x0 + (x1 - x0) * k), round(y0 + (y1 - y0) * k)
        d -= n
    return points[-1]


def packet(c, x: int, y: int, color) -> None:
    """A message on its way, centred on (x, y): a 3px square with a dark rim so it stands out on a line."""
    c.rect(x - 2, y - 2, 5, 5, "shadow")
    c.rect(x - 1, y - 1, 3, 3, color)


def export(draw, script: str, *, preset: str = "wide", seconds: float = 5, fps: int = 20, **options) -> Path:
    """Render `draw` beside its script as a GIF and its poster, in the series' theme."""
    return animate(draw, Path(script).with_suffix(".gif"), preset=preset, theme=THEME, seconds=seconds, fps=fps,
                   **options)
