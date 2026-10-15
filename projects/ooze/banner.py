"""ooze's title for the top of its README: the Slime and the name, as on the video's end card, on
nothing, so it sits on GitHub's light and dark pages alike. 960x240, shown at 480 wide.

    PYTHONPATH=skill/scripts python3 projects/ooze/banner.py
"""

from pathlib import Path

import numpy as np
from PIL import Image

from ooze import INK, SLIME, SLIME_DARK, slime
from pixelkit import Canvas

KEY = (255, 0, 255)  # drawn on magenta, which then becomes see-through

c = Canvas(240, 60, scale=4, bg="#ff00ff")
slime(c, 6, 6, big=True)
c.chunky(170, 7, "OOZE", ["#9ff3e2", SLIME, SLIME_DARK], scale=5, depth=3, side=["#037a6d", "#02524a"],
         light="#d4fbf3", dark=INK, outline="shadow")
c.strip(112, 51, 116, 2, c.theme.series)

path = Path(__file__).with_name("banner.png")
c.save(path, quiet=True)
px = np.array(Image.open(path).convert("RGBA"))
px[(px[..., :3] == KEY).all(axis=-1)] = 0
img = Image.fromarray(px)
img.save(path, optimize=True)
print(path, img.size)
