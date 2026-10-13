"""5.2 Where the memory went: the nine fighters' drawings on disk, as the game first held them once loaded,
and as SF2 held its own, at their sizes on one scale. Beside them, what each pixel cost in memory, and the
fighters' pictures the game measured itself holding at the arcade's last fight, before and after.

Animated: the three bars fill at the same speed, so the PNGs and SF2's way land at once while the loaded
bar runs on across the panel; then the bytes of one loaded pixel light one by one, and the measured
numbers count down. Holds.

Numbers, from alfamafighterturbo at 74e2f64:
- 1.8 MB of PNGs, 250 MB loaded, about 7.5 MB held SF2's way (palette indices, a byte a pixel), for all
  nine fighters: docs/plans/2026-10-05-studio-design.md ("The first numbers"); making-of.md, moment 17.
  They were the producer's estimate from the strips on disk, 9 October; the brief that opened the work
  (the game's chat transcript, 9 October 07:05) has the table, with Adamastor's five schemes at 62.3 MB;
- before: each strip a byte a pixel of palette indices plus two full-colour canvases, one a facing, for
  each colour scheme built, player 1's and player 2's built at load (1 + 2 x 2 x 4 = 17 bytes a pixel):
  docs/plans/2026-10-09-performance-and-resources.md (opening) and the fluidity report ("Size and memory");
- SF2 on the CPS1: every drawing as 4-bit tiles in ROM, recoloured by a palette swap and flipped by the
  hardware, in a few hundred KB of RAM: performance-and-resources.md (opening);
- measured by the game's own accounting at the arcade's ninth fight (Adamastor at Santa Catarina), the
  fighters' pictures: 248.7 MB before, 2.9 MB after; the indices are counted apart, 0.6 to 2.0 MB a
  fighter: performance-and-resources.md ("Before and after").
"""

from pixelkit import ease_out, phase
from series import ART, ENGINE, QA, TOOLS, export, frame

BARS = [
    # label, MB, colour, what it is
    ("ON DISK, AS PNG FILES", 1.8, TOOLS, "COMPRESSED. LOADED, ABOUT 140 TIMES BIGGER"),
    ("LOADED, AS THE GAME FIRST HELD THEM", 250, ART, "IN FULL COLOUR, FOR EACH FACING AND SCHEME"),
    ("AS COLOUR NUMBERS, SF2'S WAY", 7.5, ENGINE, "A BYTE A PIXEL: WHICH OF HIS 16 COLOURS"),
]
FILL = (0.06, 0.55)                     # the bars fill at one speed: 250 MB in this window
BYTES = (0.58, 0.78)                    # one loaded pixel's 17 bytes light in turn
COUNT = (0.62, 0.9)                     # the measured numbers count down
BEFORE, AFTER = 248.7, 2.9


def mb(v: float) -> str:
    return f"{v:.1f} MB" if v < 10 or v % 1 else f"{v:.0f} MB"


def draw(c, t):
    top, bottom = frame(c, 5, 2, "WHERE THE MEMORY WENT",
                        "BARS: ESTIMATES FROM THE FILES, 9 OCT.")
    left = c.panel(0, top + 1, 212, bottom - top - 3, "THE SAME DRAWINGS", color=c.light(ART),
                   sub="THREE WAYS TO HOLD THEM, ONE SCALE")
    arrived = 250 * ease_out(phase(t, *FILL)) if t < FILL[1] else 250
    track_w = left.w
    step = 31
    for i, (label, size, colour, what) in enumerate(BARS):
        y = left.y + i * step
        c.text(left.x, y, label, "white")
        shown = min(size, arrived)
        c.text(left.x2, y, mb(shown), c.light(colour), align="right")
        c.rect(left.x, y + 8, track_w, 5, "raised")
        w = max(1, round(track_w * shown / 250))
        c.rect(left.x, y + 8, w, 5, colour)
        c.hline(left.x, y + 8, w, c.light(colour))
        c.text(left.x, y + 16, what, "dim")

    # What one pixel of a drawing cost: before, 17 bytes; SF2's way, one.
    py = left.y + 3 * step + 1
    c.text(left.x, py, "ONE PIXEL, IN BYTES", "white")
    lit = round(17 * phase(t, *BYTES))
    cells = [("INDEX", TOOLS)] + [(f"P{1 + k // 8}", ART) for k in range(16)]
    x = left.x
    for k, (_, colour) in enumerate(cells):
        if k in (1, 5, 9, 13):
            x += 2
        c.rect(x, py + 8, 5, 5, colour if k < lit else "raised")
        x += 6
    c.text(x + 3, py + 8, "LOADED: 17", c.light(ART) if lit == 17 else "dim")
    c.spans(left.x, py + 16, [("1", c.light(TOOLS)), " WHICH COLOUR · ", ("4", c.light(ART)),
                              " × 2 FACINGS × 2 SCHEMES"], "dim")
    c.rect(left.x, py + 24, 5, 5, TOOLS)
    c.text(left.x + 9, py + 24, "SF2'S WAY: 1, PAINTED AND FLIPPED AS DRAWN", c.light(ENGINE))

    # Measured by the game itself, before and after it held them SF2's way.
    right = c.panel(214, top + 1, 106, bottom - top - 3, "MEASURED", color=c.light(QA), sub="IN THE GAME")
    k = ease_out(phase(t, *COUNT))
    now = BEFORE + (AFTER - BEFORE) * k
    c.paragraph(right.x, right.y, "FIGHTERS' PICTURES HELD AT THE ARCADE'S LAST FIGHT", right.w, "dim")
    c.text(right.x, right.y + 17, "BEFORE", "text")
    c.text(right.x2, right.y + 16, mb(BEFORE), c.light(ART), font="large", align="right")
    c.text(right.x, right.y + 29, "AFTER", "text")
    c.text(right.x, right.y + 37, mb(now), c.light(ENGINE) if k >= 1 else "white", font="large", scale=2,
           shadow="line")
    c.paragraph(right.x, right.y + 57, "BEFORE: EVERY FIGHTER MET IN THE RUN. AFTER: ONLY THE TWO IN THE "
                "FIGHT", right.w, "text")
    c.paragraph(right.x, right.y + 87, "SF2 READ ITS DRAWINGS FROM ROM, 4 BITS A PIXEL, WITH A FEW HUNDRED KB OF RAM", right.w, "dim")


export(draw, __file__, seconds=4, fps=20, hold=4)
