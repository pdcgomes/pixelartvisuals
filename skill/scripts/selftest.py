"""Sanity checks for pixelkit and a fresh render of every example. Run after editing the kit:

    python3 ~/.cursor/skills/pixel-graphics/scripts/selftest.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pixelkit import FONTS, Canvas, Raycaster, Rect, animate, flicker, iso_xy, orbit, shake  # noqa: E402


def notes(build) -> list[str]:
    c = Canvas(preset="wide")
    build(c)
    return c.check()


def expect(label: str, got: list[str], needle: str | None) -> bool:
    ok = any(needle in n for n in got) if needle else not got
    print(f"{'ok ' if ok else 'FAIL'} {label}" + ("" if ok else f": {got}"))
    return ok


cases = [
    ("clean layout", lambda c: (c.header("T"), c.panel(0, 14, 100, 40, "A"), c.footer("SRC")), None),
    ("side-by-side text collision", lambda c: (c.text(10, 20, "AB"), c.text(16, 20, "CD")), "collides"),
    ("stacked text touching", lambda c: (c.text(10, 20, "AB"), c.text(10, 25, "CD")), "touches"),
    ("text on a hero shadow row", lambda c: (c.text(10, 20, "8", font="large", scale=3, shadow="dim"),
                                             c.text(10, 42, "X")), "touches"),
    ("accent touching the line above", lambda c: (c.text(10, 20, "AB"), c.text(10, 27, "ÁB")), "touches"),
    ("text crossing a panel edge", lambda c: (c.panel(0, 20, 30, 20), c.text(20, 25, "OVERFLOW")), "crosses"),
    ("panels partly overlapping", lambda c: (c.panel(0, 20, 60, 30), c.panel(40, 30, 60, 30)), "overlap"),
    ("region nested in a panel", lambda c: (c.panel(0, 20, 100, 60), c.claim(Rect(4, 30, 20, 20), "part")), None),
    ("panel under the footer", lambda c: (c.panel(0, 20, 100, 170), c.footer("SRC")), "overlap"),
    ("off the canvas", lambda c: c.text(310, 20, "LONG LABEL"), "off the canvas"),
    ("nodes partly overlapping", lambda c: (c.node(0, 20, 60, 19, "A"), c.node(40, 30, 60, 19, "B")), "overlap"),
    ("node title too long for its box", lambda c: c.node(0, 20, 30, 19, "MUCH TOO LONG"), "crosses the edge of node"),
    ("connected nodes stay clean", lambda c: c.connect(c.node(0, 20, 60, 19, "A"), c.node(80, 60, 60, 19, "B"),
                                                         "line", label="USES"), None),
]
passed = all(expect(label, notes(build), needle) for label, build, needle in cases)


def expect_true(label: str, ok: bool, detail: str = "") -> bool:
    print(f"{'ok ' if ok else 'FAIL'} {label}" + ("" if ok else f": {detail}"))
    return ok


c = Canvas(preset="wide")
a, b = Rect(10, 20, 40, 19), Rect(90, 80, 40, 19)
pts = c.connect(a, b, "white")
passed &= expect_true("connect runs from a's bottom edge to a head on b's top edge",
                      pts[0] == (a.cx, a.y2) and pts[-1] == (b.cx, b.y - 1)
                      and c.img.getpixel((b.cx, b.y - 1)) == c.rgb("white"), str(pts))
rail = c.bus(0, 120, 200, "white", [Rect(20, 100, 30, 10), Rect(120, 140, 30, 10)])
passed &= expect_true("bus taps reach the rail from above and below",
                      c.img.getpixel((35, 119)) == c.rgb("white") and c.img.getpixel((135, 122)) == c.rgb("white"))
try:
    c.arrow(0, 0, 10, 10, "white")
    passed &= expect_true("diagonal arrows are refused", False, "no error")
except ValueError:
    passed &= expect_true("diagonal arrows are refused", True)

FONTS["small"].missing.clear()
FONTS["large"].missing.clear()
c = Canvas(preset="wide")
c.text(0, 0, "≈■≤≥ ÁÇÑ ✓€£ → ↑↓ °× ·…—")
c.text(0, 10, "≈■≤≥ ÁÇÑ ✓€£ → ↑↓ °× ·…—", font="large")
passed &= expect("every listed glyph exists", [n for n in c.check() if "glyph" in n], None)


def scene(t, kind):
    c = Canvas(80, 60)
    c.particles(10, 10, 60, 40, t, kind, n=30, seed=3)
    return c.img


for kind in ("rain", "snow", "embers", "smoke", "sparks", "dust"):
    a, b, mid = scene(0.0, kind), scene(1.0, kind), scene(0.37, kind)
    passed &= expect_true(f"{kind} particles are frame-pure and loop", scene(0.37, kind).tobytes() == mid.tobytes()
                          and a.tobytes() == b.tobytes() and a.tobytes() != mid.tobytes())
passed &= expect_true("flicker and shake loop over whole cycles",
                      abs(flicker(0.0, seed=2) - flicker(1.0, seed=2)) < 1e-9 and shake(0.0, 2) == shake(1.0, 2))

c = Canvas(80, 40, bg="white")
c.darkness([(20, 20, 10)], squash=1.0)
passed &= expect_true("darkness leaves the pool lit and darkens beyond it",
                      c.img.getpixel((20, 20)) == c.rgb("white") and c.img.getpixel((70, 5)) != c.rgb("white"))
c = Canvas(40, 40, bg="white")
c.dissolve(0.5, "red")
reds = {rgb: k for k, rgb in c.img.getcolors()}.get(c.rgb("red"), 0)
passed &= expect_true("dissolve swaps half the pixels and adds no colours",
                      reds == 800 and len(c.img.getcolors()) == 2, f"{reds} red")
c = Canvas(40, 40)
c.orb(20, 20, 10, 0.5, "red")
passed &= expect_true("orb fills the lower half with liquid",
                      c.img.getpixel((20, 26)) in {c.rgb(s) for s in ("red", "red.dark", "red.light")}
                      and c.img.getpixel((24, 14)) not in {c.rgb(s) for s in ("red", "red.dark")})
c = Canvas(20, 20, bg="white")
c.cooldown(0, 0, 20, 20, 0.25)
passed &= expect_true("cooldown shades only the last quarter of the sweep",
                      c.img.getpixel((5, 3)) != c.rgb("white") and c.img.getpixel((15, 3)) == c.rgb("white")
                      and c.img.getpixel((15, 15)) == c.rgb("white"))
c = Canvas(10, 10)
c.sprite(3, 3, ["##", "##"], {"#": "red"}, outline="white")
passed &= expect_true("sprite outline rings the silhouette",
                      c.img.getpixel((2, 3)) == c.rgb("white") and c.img.getpixel((3, 3)) == c.rgb("red")
                      and c.img.getpixel((2, 2)) == c.rgb("bg"))
c, s = Canvas(20, 20), Canvas(4, 2, bg="#ff00ff")
s.px(0, 0, "red")
s.px(3, 1, "lime")
c.paste(s, 5, 5, key="#ff00ff", shear=1)
passed &= expect_true("keyed, sheared paste", c.img.getpixel((5, 5)) == c.rgb("red")
                      and c.img.getpixel((8, 7)) == c.rgb("lime") and c.img.getpixel((6, 5)) == c.rgb("bg"))
passed &= expect_true("iso_xy matches iso_box's slope", iso_xy(10, 10, 3, 1, 2) == (14, 12))

c = Canvas(10, 10)
c.sprite(2, 2, ["###", "###", "###"], {"#": "red"}, shade=True)
passed &= expect_true("sprite shade lights the top edge and darkens the bottom",
                      c.img.getpixel((3, 2)) != c.rgb("red") and c.img.getpixel((3, 4)) != c.rgb("red")
                      and c.img.getpixel((3, 2)) != c.img.getpixel((3, 4)))
c, s = Canvas(12, 12), Canvas(4, 4, bg="#ff00ff")
s.rect(1, 1, 2, 2, "red")
c.paste(s, 4, 4, key="#ff00ff", outline="white")
passed &= expect_true("keyed paste outline rings the shape",
                      c.img.getpixel((4, 5)) == c.rgb("white") and c.img.getpixel((5, 5)) == c.rgb("red")
                      and c.img.getpixel((4, 4)) == c.rgb("bg"))
pts = orbit(20, 20, 10, 4, 0.3, 8)
passed &= expect_true("orbit returns whole pixels sorted back to front, and loops",
                      [p[1] for p in pts] == sorted(p[1] for p in pts) and all(isinstance(v, int) for p in pts for v in p[:2])
                      and orbit(20, 20, 10, 4, 0.0, 8) == orbit(20, 20, 10, 4, 1.0, 8))


def fx_frame(t, draw):
    c = Canvas(80, 60)
    draw(c, t)
    return c.img.tobytes()


for label, draw in (("wisps burst", lambda c, t: c.particles(10, 10, 60, 40, t, "wisps", n=20, burst=True)),
                    ("projectile", lambda c, t: c.projectile(5, 50, 75, 10, t, "white", trail=["gold", "red"])),
                    ("glyph", lambda c, t: c.glyph(40, 30, 20, t, "red", squash=2))):
    passed &= expect_true(f"{label} is frame-pure", fx_frame(0.43, draw) == fx_frame(0.43, draw)
                          and fx_frame(0.43, draw) != fx_frame(0.61, draw))
c = Canvas(20, 20)
passed &= expect_true("projectile returns its head in flight and None outside 0..1",
                      c.projectile(0, 0, 10, 0, 0.5) == (5, 0) and c.projectile(0, 0, 10, 0, 1.0) is None)
back, front = Canvas(40, 40), Canvas(40, 40)
back.glyph(20, 20, 12, half="back")
front.glyph(20, 20, 12, half="front")
passed &= expect_true("glyph halves draw only the far and near sides",
                      back.img.crop((0, 23, 40, 40)).getcolors() == [(40 * 17, back.rgb("bg"))]
                      and front.img.crop((0, 0, 40, 18)).getcolors() == [(40 * 18, front.rgb("bg"))])
shades = ["#200000", "#600000", "#a00000", "#ff6040"]
c = Canvas(30, 30)
c.circle(15.5, 15.5, 10, "#ff00fe")
c.form("#ff00fe", shades)
used = {rgb for _, rgb in c.img.getcolors()}
passed &= expect_true("form replaces the marker with its four shades only",
                      c.rgb("#ff00fe") not in used and used <= {c.rgb(s) for s in shades} | {c.rgb("bg")}
                      and c.img.getpixel((7, 15)) != c.img.getpixel((24, 15)))
c = Canvas(40, 20)
for i in range(40):
    c.vline(i, 0, 20, "red" if i % 3 else "gold")
before = sorted(c.img.getcolors())
c.heat(0, 0, 40, 20, 0.3, amp=2)
passed &= expect_true("heat moves pixels without adding colours", {rgb for _, rgb in c.img.getcolors()}
                      == {rgb for _, rgb in before})
old, new = Canvas(40, 30, bg="red"), Canvas(40, 30, bg="blue")
c = Canvas(40, 30)
c.melt(old, new, 0.0)
first = c.img.tobytes() == old.img.tobytes()
c.melt(old, new, 1.0)
last = c.img.tobytes() == new.img.tobytes()
c.melt(old, new, 0.6, seed=2)
mid = {rgb for _, rgb in c.img.getcolors()}
passed &= expect_true("melt runs from the old screen to the new, adding no colours",
                      first and last and mid == {c.rgb("red"), c.rgb("blue")}
                      and c.img.getpixel((0, 0)) == c.rgb("blue"))
c = Canvas(120, 60)
box = c.chunky(60, 10, "HI", ["gold", "red"], scale=3, depth=2, side="red.dark", outline="#000000",
               light="white", bow=0.3, weight=1)
inside = c.img.crop((box.x, box.y, box.x2, box.y2))
passed &= expect_true("chunky draws an outlined, extruded gradient title inside its box",
                      box.w > 3 * 9
                      and {c.rgb(k) for k in ("gold", "red", "#000000", "white", "red.dark")}
                      <= {rgb for _, rgb in inside.getcolors()}
                      and c.img.getpixel((box.x - 1, box.y)) == c.rgb("bg"))
world = Raycaster(["#####", "#...#", "#...#", "#...#", "#####"], {"#": "white"}, floor="green",
                  ceiling="blue", fog="#000000", fog_dist=50, dither=False)
c = Canvas(64, 40)
boxes = world.render(c, 0, 0, 64, 40, (2.5, 3.5), -90,
                     sprites=[{"x": 2.5, "y": 2.0, "img": Canvas(4, 8, bg="red"), "scale": 0.3},
                              {"x": 2.5, "y": 3.9, "img": Canvas(4, 8, bg="red"), "scale": 0.3}])
mid_col = [c.img.getpixel((32, j)) for j in range(40)]
passed &= expect_true("raycaster draws ceiling, wall, sprite and floor in order, and culls sprites behind",
                      mid_col[0] != mid_col[39] and c.rgb("red") in {p[:3] for p in mid_col}
                      and boxes[0] is not None and boxes[1] is None
                      and world.solid(0.5, 0.5) and not world.solid(2.5, 2.5))
views = [Canvas(64, 40), Canvas(64, 40)]
for v in views:
    world.render(v, 0, 0, 64, 40, (2.2, 2.7), -70)
passed &= expect_true("raycaster is frame-pure", views[0].img.tobytes() == views[1].img.tobytes()
                      and views[0].img.tobytes() != c.img.tobytes())


def tiny(c, t):
    c.bar3d(10, 60, 12, round(40 * t) + 1, "green")
    c.text(40, 20, f"{t:.2f}", "white")


with tempfile.TemporaryDirectory() as tmp:
    for ext in ("gif", "webp"):
        out = animate(tiny, Path(tmp) / f"a.{ext}", w=80, h=70, scale=2, seconds=0.5, fps=10, quiet=True)
        shown = [f.convert("RGB") for f in ImageSequence.Iterator(Image.open(out))]
        wrong = []
        for i in range(5):
            c = Canvas(80, 70)
            tiny(c, i / 4)
            if ImageChops.difference(c.img.resize((160, 140), Image.NEAREST), shown[i]).getbbox():
                wrong.append(i)
        passed &= expect(f"animated {ext} plays back every frame exactly",
                         [f"{len(shown)} frames, mismatches {wrong}"] if wrong or len(shown) != 5 else [], None)

env = {**os.environ, "PYTHONPATH": str(HERE)}
for example in sorted((HERE.parent / "examples").glob("*.py")):
    run = subprocess.run([sys.executable, str(example)], env=env, capture_output=True, text=True)
    clean = run.returncode == 0 and "warning" not in run.stdout
    passed &= expect(f"example {example.name}", [] if clean else [run.stdout + run.stderr], None)

print("all good" if passed else "something failed")
sys.exit(0 if passed else 1)
