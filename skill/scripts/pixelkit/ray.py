"""A small grid raycaster for first-person scenes: textured walls, textured floors and ceilings, billboard
sprites sorted by depth, and distance fog quantised to a few dithered light levels so palettes stay small."""

from __future__ import annotations

import math

import numpy as np
from PIL import Image

from .geometry import BAYER4

_BAYER = (np.array(BAYER4, dtype=np.float64) + 0.5) / 16


def _pixels(src) -> np.ndarray:
    img = src.img if hasattr(src, "img") else src
    return np.asarray(img.convert("RGB"), dtype=np.float64)


class Raycaster:
    """A map of grid cells seen from inside.

    grid: rows of characters; row j is world y in [j, j + 1), column i is world x. Characters in `walls`
    are solid and map to wall textures (a Canvas or PIL image, or a colour). Any other character is open
    floor, and looks its floor and ceiling up in `floors` and `ceilings` (falling back to `floor` and
    `ceiling`). `ceiling_grid` gives the ceiling its own layout (light panels, skylights). Characters in
    `bright` ignore the fog (light panels, lit doorways, glowing slime).
    Light falls off linearly to the fog colour at `fog_dist` cells, in `levels` dithered steps, so each
    texture colour gains at most `levels` shades. Walls whose faces run along x are dimmed by `side`.
    `lights` are (x, y, radius, amount) world points that brighten floors, walls and sprites near them.
    dither=False bands the light levels instead (the look of early-90s shooters, and smaller GIFs when
    the camera moves).
    """

    def __init__(self, grid, walls: dict, *, floor="#303030", ceiling="#202020", floors=None, ceilings=None,
                 ceiling_grid=None, bright: str = "", fog="#000000", fog_dist: float = 10.0, levels: int = 4,
                 side: float = 0.8, lights=(), dither: bool = True):
        self.grid = [str(r) for r in grid]
        self.ceiling_grid = [str(r) for r in (ceiling_grid or grid)]
        self.walls, self.floors, self.ceilings = dict(walls), dict(floors or {}), dict(ceilings or {})
        self.floor, self.ceiling, self.fog = floor, ceiling, fog
        self.bright, self.fog_dist, self.levels, self.side = set(bright), fog_dist, levels, side
        self.lights, self.dither = list(lights), dither
        self.rows, self.cols = len(self.grid), max(len(r) for r in self.grid)

    def cell(self, x: float, y: float) -> str:
        i, j = int(math.floor(x)), int(math.floor(y))
        if 0 <= j < self.rows and 0 <= i < len(self.grid[j]):
            return self.grid[j][i]
        return next(iter(self.walls))

    def solid(self, x: float, y: float) -> bool:
        return self.cell(x, y) in self.walls

    # ------------------------------------------------------------------------------------------

    def _texture(self, c, spec) -> np.ndarray:
        if isinstance(spec, (str, tuple)):
            return np.array([[c.rgb(spec)]], dtype=np.float64)
        return _pixels(spec)

    def _light(self, dist, wx, wy):
        lit = np.clip(1.0 - np.asarray(dist, dtype=np.float64) / self.fog_dist, 0.0, 1.0)
        for lx, ly, r, amount in self.lights:
            d = np.hypot(np.asarray(wx) - lx, np.asarray(wy) - ly)
            lit = lit + amount * np.clip(1.0 - d / r, 0.0, 1.0)
        return np.clip(lit, 0.0, 1.0)

    def render(self, c, x: int, y: int, w: int, h: int, pos, angle: float, *, fov: float = 66.0,
               sprites=(), pitch: float = 0.0, eye: float = 0.5) -> list:
        """Draw the view from `pos` (x, y) looking at `angle` degrees (0 = +x, 90 = +y, down the rows)
        into the w×h box at (x, y). `pitch` moves the horizon in px (a walking bob); `eye` is the
        camera's height in wall heights.

        sprites: dicts with x, y, img (a Canvas or PIL image), and optionally key (transparent colour),
        scale (height in wall heights, default 1), lift (base height off the floor) and bright (no fog).
        Returns each sprite's screen box (x, y, w, h) or None when it is behind the camera, in the
        order given."""
        px, py = pos
        a = math.radians(angle)
        dx, dy = math.cos(a), math.sin(a)
        half = math.tan(math.radians(fov) / 2)
        plx, ply = -dy * half, dx * half
        proj = (w / 2) / half
        horizon = h / 2 + pitch
        cam = 2 * (np.arange(w) + 0.5) / w - 1
        rgb = np.zeros((h, w, 3))
        lit = np.ones((h, w))
        bright = np.zeros((h, w), dtype=bool)
        fog = np.array(c.rgb(self.fog), dtype=np.float64)

        self._flats(c, rgb, lit, bright, w, h, px, py, dx, dy, plx, ply, cam, proj, horizon, eye)
        zbuf = self._walls(c, rgb, lit, bright, w, h, px, py, dx, dy, plx, ply, cam, proj, horizon, eye)
        boxes = self._sprites(c, rgb, lit, bright, w, h, px, py, dx, dy, plx, ply, proj, horizon, eye,
                              sprites, zbuf)

        lit[bright] = 1.0
        yy, xx = np.mgrid[y:y + h, x:x + w]
        lv = lit * self.levels
        if self.dither:
            k = np.floor(lv)
            k = np.minimum(k + (lv - k > _BAYER[yy % 4, xx % 4]), self.levels) / self.levels
        else:
            k = np.rint(lv) / self.levels
        out = np.rint(fog + (rgb - fog) * k[..., None]).astype(np.uint8)
        x0, y0 = max(0, x), max(0, y)
        crop = out[y0 - y:min(c.h, y + h) - y, x0 - x:min(c.w, x + w) - x]
        c.img.paste(Image.fromarray(crop, "RGB"), (x0, y0))
        return boxes

    def _flats(self, c, rgb, lit, bright, w, h, px, py, dx, dy, plx, ply, cam, proj, horizon, eye):
        rows = np.arange(h) + 0.5 - horizon
        for below, grid, table, default in ((True, self.grid, self.floors, self.floor),
                                            (False, self.ceiling_grid, self.ceilings, self.ceiling)):
            sel = rows > 0.25 if below else rows < -0.25
            if not sel.any():
                continue
            ys = np.nonzero(sel)[0]
            dist = (proj * (eye if below else 1 - eye) / np.abs(rows[ys]))[:, None]
            wx = px + dist * (dx + plx * cam)[None, :]
            wy = py + dist * (dy + ply * cam)[None, :]
            ci = np.clip(np.floor(wx).astype(int), 0, self.cols - 1)
            cj = np.clip(np.floor(wy).astype(int), 0, self.rows - 1)
            chars = np.array([list(r.ljust(self.cols)) for r in grid])[cj, ci]
            out = np.empty(wx.shape + (3,))
            glow = np.zeros(wx.shape, dtype=bool)
            for ch in np.unique(chars):
                m = chars == ch
                tex = self._texture(c, table.get(ch, default))
                th, tw = tex.shape[:2]
                tx = (np.floor((wx[m] % 1) * tw).astype(int)) % tw
                ty = (np.floor((wy[m] % 1) * th).astype(int)) % th
                out[m] = tex[ty, tx]
                glow[m] = ch in self.bright
            rgb[ys] = out
            lit[ys] = self._light(np.broadcast_to(dist, wx.shape), wx, wy)
            bright[ys] = glow

    def _walls(self, c, rgb, lit, bright, w, h, px, py, dx, dy, plx, ply, cam, proj, horizon, eye):
        zbuf = np.full(w, np.inf)
        textures = {ch: self._texture(c, spec) for ch, spec in self.walls.items()}
        for col in range(w):
            rx, ry = dx + plx * cam[col], dy + ply * cam[col]
            mx, my = int(math.floor(px)), int(math.floor(py))
            ddx = abs(1 / rx) if rx else 1e30
            ddy = abs(1 / ry) if ry else 1e30
            sx, sdx = (-1, (px - mx) * ddx) if rx < 0 else (1, (mx + 1 - px) * ddx)
            sy, sdy = (-1, (py - my) * ddy) if ry < 0 else (1, (my + 1 - py) * ddy)
            side, ch = 0, None
            for _ in range(4 * (self.rows + self.cols)):
                if sdx < sdy:
                    sdx += ddx
                    mx += sx
                    side = 0
                else:
                    sdy += ddy
                    my += sy
                    side = 1
                ch = self.cell(mx + 0.5, my + 0.5)
                if ch in self.walls:
                    break
            perp = max(1e-4, (sdx - ddx) if side == 0 else (sdy - ddy))
            zbuf[col] = perp
            hx, hy = px + perp * rx, py + perp * ry
            tex = textures[ch]
            th, tw = tex.shape[:2]
            u = (hy if side == 0 else hx) % 1
            if (side == 0 and rx < 0) or (side == 1 and ry > 0):
                u = 1 - u
            tx = min(tw - 1, int(u * tw))
            top = horizon - proj * (1 - eye) / perp
            bottom = horizon + proj * eye / perp
            y0, y1 = max(0, int(math.ceil(top - 0.5))), min(h, int(math.ceil(bottom - 0.5)))
            if y1 <= y0:
                continue
            ys = np.arange(y0, y1)
            ty = np.clip(((ys + 0.5 - top) / (bottom - top) * th).astype(int), 0, th - 1)
            rgb[y0:y1, col] = tex[ty, tx]
            light = float(self._light(perp, hx, hy))
            lit[y0:y1, col] = light * (self.side if side == 1 else 1.0)
            bright[y0:y1, col] = ch in self.bright
        return zbuf

    def _sprites(self, c, rgb, lit, bright, w, h, px, py, dx, dy, plx, ply, proj, horizon, eye, sprites, zbuf):
        inv = 1.0 / (plx * dy - dx * ply)
        placed = []
        for n, s in enumerate(sprites):
            rx, ry = s["x"] - px, s["y"] - py
            tx = inv * (dy * rx - dx * ry)
            depth = inv * (-ply * rx + plx * ry)
            placed.append((depth, tx, n, s))
        boxes = [None] * len(placed)
        for depth, tx, n, s in sorted(placed, key=lambda p: -p[0]):
            if depth <= 0.15:
                continue
            tex = _pixels(s["img"])
            th, tw = tex.shape[:2]
            key = s.get("key")
            solid = np.ones((th, tw), dtype=bool) if key is None else \
                np.any(tex != np.array(c.rgb(key), dtype=np.float64), axis=2)
            sh = proj * s.get("scale", 1.0) / depth
            sw = sh * tw / th
            cx = (w / 2) * (1 + tx / depth)
            base = horizon + proj * (eye - s.get("lift", 0.0)) / depth
            left, top = cx - sw / 2, base - sh
            boxes[n] = (int(round(left)), int(round(top)), int(round(sw)), int(round(sh)))
            x0, x1 = max(0, int(math.ceil(left - 0.5))), min(w, int(math.ceil(left + sw - 0.5)))
            y0, y1 = max(0, int(math.ceil(top - 0.5))), min(h, int(math.ceil(base - 0.5)))
            if x1 <= x0 or y1 <= y0:
                continue
            cols = np.arange(x0, x1)
            cols = cols[zbuf[cols] > depth]
            if not len(cols):
                continue
            ys = np.arange(y0, y1)
            u = np.clip(((cols + 0.5 - left) / sw * tw).astype(int), 0, tw - 1)
            v = np.clip(((ys + 0.5 - top) / sh * th).astype(int), 0, th - 1)
            m = solid[v[:, None], u[None, :]]
            yy, xx = np.nonzero(m)
            rgb[ys[yy], cols[xx]] = tex[v[yy], u[xx]]
            lit[ys[yy], cols[xx]] = float(self._light(depth, s["x"], s["y"]))
            bright[ys[yy], cols[xx]] = bool(s.get("bright", False))
        return boxes
