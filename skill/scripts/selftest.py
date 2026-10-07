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

from pixelkit import FONTS, Canvas, Rect, animate  # noqa: E402


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
