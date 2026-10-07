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
]
passed = all(expect(label, notes(build), needle) for label, build, needle in cases)

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
