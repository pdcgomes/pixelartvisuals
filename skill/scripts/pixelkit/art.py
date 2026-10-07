"""Illustration helpers mixed into Canvas: sprites, icons, isometric boxes, imported images."""

from __future__ import annotations

import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

from .geometry import BAYER4, PATTERNS, Rect

# '#' takes the icon colour, '+' its light shade, '-' its dark shade.
ICONS = {
    "bolt": "....##./...##../..##.../.######/...##../..##.../.##....",
    "heart": ".##.##./#######/#######/.#####./..###../...#...",
    "star": "...#.../..###../#######/.#####./..###../.##.##./.#...#.",
    "clock": "..###../.#...#./#..#..#/#..##.#/#.....#/.#...#./..###..",
    "check": "......#/.....##/#...##./##.##../.###.../..#....",
    "cross": "##...##/.##.##./..###../.##.##./##...##",
    "note": "..#####/..#...#/..#...#/..#...#/.##..##/###.###/.#...#.",
    "play": "#..../##.../###../####./###../##.../#....",
    "warn": "...#.../..#.#../..#.#../.#.#.#./.#...#./#..#..#/#######",
    "cpu": "..#.#.#../.#######./##.....##/.#.###.#./##.###.##/.#.###.#./##.....##/.#######./..#.#.#..",
    "temp": "..#../.#.#./.#.#./.###./#####/#####/.###.",
    "disc": "..###../.#####./###.###/##.#.##/###.###/.#####./..###..",
    "invader": "..#.....#../...#...#.../..#######../.##.###.##./###########/#.#######.#/#.#.....#.#/...##.##...",
    "up": "..#../.###./#####",
    "down": "#####/.###./..#..",
    "file": "#####../#...##./#....##/#.....#/#.....#/#.....#/#.....#/#.....#/#######",
    "folder": "####...../#...####./#########/#.......#/#.......#/#.......#/#########",
    "package": ".#######./#+++#+++#/#########/#---#---#/#---#---#/#---#---#/.#######.",
    "lock": "..###../.#...#./.#...#./#######/###.###/##...##/###.###/#######",
}


def oklab(rgb):
    import numpy as np

    c = np.asarray(rgb, dtype=np.float64) / 255
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    lms = np.cbrt(c @ np.array([[0.4122214708, 0.2119034982, 0.0883024619],
                                [0.5363325363, 0.6806995451, 0.2817188376],
                                [0.0514459929, 0.1073969566, 0.6299787005]]))
    return lms @ np.array([[0.2104542553, 1.9779984951, 0.0259040371],
                           [0.7936177850, -2.4285922050, 0.7827717662],
                           [-0.0040720468, 0.4505937099, -0.8086757660]])


def lock(img: Image.Image, palette, *, dither: float = 0.0, alpha: int = 128) -> Image.Image:
    """Map every pixel to the perceptually nearest palette colour (Oklab). dither 0..1 adds
    an ordered Bayer pattern before matching; alpha below the threshold becomes transparent."""
    import numpy as np

    rgba = np.asarray(img.convert("RGBA"))
    h, w = rgba.shape[:2]
    lab = oklab(rgba[..., :3].reshape(-1, 3))
    if dither:
        yy, xx = np.mgrid[0:h, 0:w]
        offset = (np.array(BAYER4)[yy % 4, xx % 4] + 0.5) / 16 - 0.5
        lab[:, 0] += offset.reshape(-1) * dither * 0.12
    pal = np.array(palette, dtype=np.uint8)
    pal_lab = oklab(pal)
    idx = np.empty(len(lab), dtype=np.int64)
    for s in range(0, len(lab), 8192):
        chunk = lab[s:s + 8192]
        idx[s:s + 8192] = ((chunk[:, None, :] - pal_lab[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
    out = np.empty((h, w, 4), np.uint8)
    out[..., :3] = pal[idx].reshape(h, w, 3)
    out[..., 3] = np.where(rgba[..., 3] >= alpha, 255, 0)
    return Image.fromarray(out, "RGBA")


def iso_xy(ox: float, oy: float, u: float, v: float, z: float = 0) -> tuple[int, int]:
    """Screen point of grid point (u, v) raised z px, on an iso grid with origin (ox, oy): u runs
    down-right and v down-left, 2px across and 1px down per unit, as in iso_box."""
    return round(ox + 2 * (u - v)), round(oy + u + v - z)


class Iso:
    """Screen positions on an isometric box with 2:1 edges.

    (x, y) is the back corner of the top face. u runs down-right for w units, v runs
    down-left for d units (each unit is 2px across, 1px down); side faces are h px tall
    and b counts pixels down a side face from its top edge."""

    def __init__(self, x: int, y: int, w: int, d: int, h: int):
        self.x, self.y, self.w, self.d, self.h = x, y, w, d, h

    def top(self, u: float, v: float) -> tuple[int, int]:
        return round(self.x + 2 * (u - v)), round(self.y + u + v)

    def left(self, u: float, b: float) -> tuple[int, int]:
        return round(self.x + 2 * (u - self.d)), round(self.y + u + self.d + b)

    def right(self, v: float, b: float) -> tuple[int, int]:
        return round(self.x + 2 * (self.w - v)), round(self.y + self.w + v + b)

    @property
    def bounds(self) -> Rect:
        return Rect(self.x - 2 * self.d, self.y, 2 * (self.w + self.d), self.w + self.d + self.h)


class Art:
    def sprite(self, x: int, y: int, art, colors: dict, *, scale: int = 1, flip: bool = False,
               outline=None, shade: bool = False) -> tuple[int, int]:
        """Draw ASCII art: each character maps to a colour in `colors`; '.' and ' ' are transparent.
        `outline` rings the sprite's silhouette with a 1-cell border (it then reaches one cell further out).
        shade=True lights the top edge of every same-letter region and darkens its bottom edge (then
        left and right), so flat parts gain volume lit from the top left."""
        rows = textwrap.dedent(art).strip("\n").split("\n") if isinstance(art, str) else list(art)
        grid = {(i, j): ch for j, row in enumerate(rows) for i, ch in enumerate(row[::-1] if flip else row)
                if ch not in ". "}
        if outline is not None:
            for i, j in grid:
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (i + di, j + dj) not in grid:
                        self.rect(x + (i + di) * scale, y + (j + dj) * scale, scale, scale, outline)
        for (i, j), ch in grid.items():
            col = colors[ch]
            if shade:
                if grid.get((i, j - 1)) != ch:
                    col = self.light(col)
                elif grid.get((i, j + 1)) != ch:
                    col = self.dark(col)
                elif grid.get((i - 1, j)) != ch:
                    col = self.light(col)
                elif grid.get((i + 1, j)) != ch:
                    col = self.dark(col)
            self.rect(x + i * scale, y + j * scale, scale, scale, col)
        return max(map(len, rows)) * scale, len(rows) * scale

    def icon(self, x: int, y: int, name: str, color, *, scale: int = 1) -> tuple[int, int]:
        """One of ICONS in `color` (light/dark shades for '+'/'-')."""
        return self.sprite(x, y, ICONS[name].split("/"),
                           {"#": color, "+": self.light(color), "-": self.dark(color)}, scale=scale)

    def iso_box(self, x: int, y: int, w: int, d: int, h: int, *, top, left, right, edge=None, corner=None,
                outline=None, shadow=None, patterns=None) -> Iso:
        """Isometric box. A face colour can be a list for a dithered left-to-right gradient.
        `patterns` maps a face ("top"/"left"/"right") to (PATTERNS name, colour), evaluated in
        face rows so textures follow the slant and keep a 1px margin from the face edges.
        `edge` lights the top face's front rims, `corner` the vertical front edge."""
        geo = Iso(x, y, w, d, h)
        b = geo.bounds
        faces: dict[tuple[int, int], tuple[str, int, int]] = {}
        for Y in range(b.y, b.y2):
            q = Y + 0.5 - y
            for X in range(b.x, b.x2):
                p = X + 0.5 - x
                u, v = (q + p / 2) / 2, (q - p / 2) / 2
                if 0 <= u < w and 0 <= v < d:
                    faces[X, Y] = ("top", X, Y)
                    continue
                ul = p / 2 + d
                if 0 <= ul < w and 0 <= q - ul - d < h:
                    faces[X, Y] = ("left", X, int(q - ul - d))
                    continue
                vr = w - p / 2
                if 0 <= vr < d and 0 <= q - w - vr < h:
                    faces[X, Y] = ("right", X, int(q - w - vr))
        if shadow is not None:
            for (X, Y), (f, _, _) in faces.items():
                if f == "top":
                    self.px(X + 4, Y + h + 2, shadow)
        fills = {"top": top, "left": left, "right": right}
        spans = {}
        for (X, _), (f, _, _) in faces.items():
            lo, hi = spans.get(f, (X, X))
            spans[f] = (min(lo, X), max(hi, X))
        patterns = patterns or {}
        for (X, Y), (f, i, j) in faces.items():
            c = fills[f]
            if isinstance(c, (list, tuple)) and not isinstance(c[0], int):
                lo, hi = spans[f]
                pos = (X - lo + 0.5) / (hi - lo + 1) * (len(c) - 1)
                k = min(int(pos), len(c) - 2)
                c = c[k + 1] if pos - k > (BAYER4[Y % 4][X % 4] + 0.5) / 16 else c[k]
            inner = f == "top" or (0 < j < h - 1 and spans[f][0] < X < spans[f][1])
            if f in patterns and inner and PATTERNS[patterns[f][0]](i, j):
                c = patterns[f][1]
            self.px(X, Y, c)
        for (X, Y), (f, _, _) in faces.items():
            below = faces.get((X, Y + 1), ("",))[0]
            if edge is not None and f == "top" and below in ("left", "right"):
                self.px(X, Y, edge)
            if corner is not None and f == "left" and faces.get((X + 1, Y), ("",))[0] == "right":
                self.px(X, Y, corner)
        if outline is not None:
            for X, Y in faces:
                for n in ((X + 1, Y), (X - 1, Y), (X, Y + 1), (X, Y - 1)):
                    if n not in faces:
                        self.px(n[0], n[1], outline)
        return geo

    def iso_tile(self, ox: int, oy: int, u: float, v: float, w: float = 1, d: float = 1, color="line", *,
                 z: float = 0, unit: int = 1, pattern=None, outline=None) -> list[tuple[int, int]]:
        """A flat quad on an iso grid whose origin is (ox, oy): from (u, v) for w by d cells of `unit`
        iso units, raised z px. Returns its four corners."""
        pts = [iso_xy(ox, oy, a * unit, b * unit, z) for a, b in ((u, v), (u + w, v), (u + w, v + d), (u, v + d))]
        self.polygon(pts, fill=color, outline=outline, pattern=pattern)
        return pts

    def iso_block(self, ox: int, oy: int, u: float, v: float, w: int, d: int, h: int, *, z: float = 0,
                  unit: int = 1, top, left, right, **kw) -> Iso:
        """iso_box placed on an iso grid: its footprint starts at cell (u, v) and its base sits z px up."""
        x, y = iso_xy(ox, oy, u * unit, v * unit, z + h)
        return self.iso_box(x, y, w * unit, d * unit, h, top=top, left=left, right=right, **kw)

    def circle(self, cx: float, cy: float, r: float, color, *, outline=None) -> Rect:
        """Filled disc of every pixel whose centre lies within r of (cx, cy); `outline` rings its
        edge pixels. Use a .5 centre for odd diameters. Returns the bounding Rect."""
        x0, y0, x1, y1 = int(cx - r) - 1, int(cy - r) - 1, int(cx + r) + 2, int(cy + r) + 2

        def inside(px, py):
            return (px + 0.5 - cx) ** 2 + (py + 0.5 - cy) ** 2 < r * r

        for py in range(y0, y1):
            for px in range(x0, x1):
                if inside(px, py):
                    edge = outline is not None and not all(
                        inside(px + dx, py + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    self.px(px, py, outline if edge else color)
        return Rect(x0, y0, x1 - x0, y1 - y0)

    def sphere(self, cx: float, cy: float, r: float, color, *, light=(-0.55, -0.6), shades=None) -> Rect:
        """A lit ball: each pixel takes a shade from its surface's angle to `light` (x, y towards
        the viewer's left/top), with ordered dithering between shades (dark to light by default)."""
        shades = [self.rgb(s) for s in (shades or [self.dark(color), color, self.light(color)])]
        lx, ly = light
        lz = max(0.0, 1 - lx * lx - ly * ly) ** 0.5
        n = len(shades) - 1
        for py in range(int(cy - r) - 1, int(cy + r) + 2):
            for px in range(int(cx - r) - 1, int(cx + r) + 2):
                dx, dy = (px + 0.5 - cx) / r, (py + 0.5 - cy) / r
                if dx * dx + dy * dy >= 1:
                    continue
                dz = (1 - dx * dx - dy * dy) ** 0.5
                level = max(0.0, min(1.0, (dx * lx + dy * ly + dz * lz) * 0.9 + 0.1)) * n
                k = min(int(level), n - 1) if n else 0
                hit = n and level - k > (BAYER4[py % 4][px % 4] + 0.5) / 16
                self.px(px, py, shades[k + 1] if hit else shades[k])
        return Rect(int(cx - r), int(cy - r), int(2 * r) + 1, int(2 * r) + 1)

    def polygon(self, points, *, fill=None, outline=None, pattern=None) -> None:
        """Polygon through integer points. `pattern` (a PATTERNS name) inks only that share of the
        fill, for a see-through area."""
        pts = [tuple(p) for p in points]
        if fill is not None:
            if pattern is None:
                self._draw.polygon(pts, fill=self.rgb(fill))
            else:
                mask = Image.new("1", (self.w, self.h), 0)
                ImageDraw.Draw(mask).polygon(pts, fill=1)
                test, rgb = PATTERNS[pattern], self.rgb(fill)
                box = mask.getbbox()
                if box:
                    for py in range(box[1], box[3]):
                        for px in range(box[0], box[2]):
                            if mask.getpixel((px, py)) and test(px, py):
                                self.img.putpixel((px, py), rgb)
        if outline is not None:
            self.polyline(pts + pts[:1], outline)

    def iso_floor(self, x: int, y: int, w: int, d: int, *, step: int = 4, color="line", dots: bool = False) -> Iso:
        """Isometric floor grid in the same coordinates as iso_box (h=0), every `step` units.
        dots=True marks only the intersections."""
        geo = Iso(x, y, w, d, 0)
        b = geo.bounds
        for Y in range(b.y, b.y2 + 1):
            q = Y + 0.5 - y
            for X in range(b.x, b.x2 + 1):
                p = X + 0.5 - x
                u, v = (q + p / 2) / 2, (q - p / 2) / 2
                if not (0 <= u <= w and 0 <= v <= d):
                    continue
                on_u, on_v = abs(u - round(u / step) * step) < 0.5, abs(v - round(v / step) * step) < 0.5
                if (on_u and on_v) if dots else (on_u or on_v):
                    self.px(X, Y, color)
        return geo

    def sparkles(self, x: int, y: int, w: int, h: int, n: int, colors, *, seed: int = 7,
                 twinkle: float = 0.12) -> None:
        """Scatter single pixels (and a few plus-shaped glints) over an area."""
        rnd = random.Random(seed)
        for _ in range(n):
            sx, sy, c = x + rnd.randrange(w), y + rnd.randrange(h), rnd.choice(list(colors))
            self.px(sx, sy, c)
            if rnd.random() < twinkle:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    self.px(sx + dx, sy + dy, c)

    def image(self, src, x: int, y: int, w: int | None = None, h: int | None = None, *, colors=None,
              dither: float = 0.0, alpha: int = 128) -> tuple[int, int]:
        """Paste an image resized to w x h logical pixels and locked to the theme palette.
        colors: list of colour names to restrict the palette, or "keep" to skip locking."""
        img = src if isinstance(src, Image.Image) else Image.open(Path(src).expanduser())
        img = img.convert("RGBA")
        if w or h:
            w = w or round(img.width * h / img.height)
            h = h or round(img.height * w / img.width)
            img = img.resize((w, h), Image.BOX if w < img.width else Image.NEAREST)
        if colors == "keep":
            img.putalpha(img.getchannel("A").point(lambda a: 255 if a >= alpha else 0))
        else:
            img = lock(img, self.theme.palette(colors), dither=dither, alpha=alpha)
        self.img.paste(img.convert("RGB"), (x, y), img.getchannel("A"))
        return img.size
