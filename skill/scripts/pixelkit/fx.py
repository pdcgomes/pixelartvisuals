"""Effects mixed into Canvas: frame-pure particles, light and darkness, screen effects and water.

Everything here is a pure function of `t` and a seed: no state is carried between frames, so any frame
renders on its own and motion with whole-number cycles loops seamlessly.
"""

from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image

from .geometry import BAYER4, PATTERNS, Rect

_BAYER = (np.array(BAYER4, dtype=np.float64) + 0.5) / 16

# kind -> defaults. "fill" particles wrap around their area (weather, dust); "emit" particles leave
# their area and live for one cycle (fire, smoke, sparks). Speeds are px over a particle's life.
PARTICLES = {
    "rain": dict(mode="fill", fall=1, drift=-0.25, streak=3, rates=(2, 3), colors=("sky.light", "sky.dark")),
    "snow": dict(mode="fill", fall=1, sway=2, rates=(1, 2), colors=("white", "text")),
    "dust": dict(mode="fill", fall=-1, sway=1, rates=(1,), twinkle=0.6, colors=("muted", "dim")),
    "motes": dict(mode="fill", fall=-1, sway=3, rates=(1, 2), twinkle=0.7, colors=("gold.light", "cyan.light")),
    "embers": dict(mode="emit", angle=-90, spread=30, speed=26, sway=2, rates=(1, 2),
                   colors=("white", "gold.light", "gold", "orange", "red.dark")),
    "smoke": dict(mode="emit", angle=-90, spread=16, speed=28, wind=8, sway=1, size=(1, 3), pattern="checker",
                  rates=(1,), colors=("muted", "dim", "line")),
    "sparks": dict(mode="emit", angle=-90, spread=140, speed=16, gravity=20, rates=(2, 3),
                   colors=("white", "gold.light", "orange")),
    "wisps": dict(mode="emit", angle=-90, spread=24, speed=22, sway=2, rates=(1, 2),
                  colors=("white", "green.light", "green", "green.dark")),
}
RUNES = [["#.#", ".#.", "#.#"], ["###", "#..", "###"], [".#.", "###", ".#."], ["#..", "###", "..#"],
         ["##.", ".#.", ".##"], ["#.#", "###", "#.#"]]


def flicker(t: float, *, seed: int = 0, cycles=(5, 11, 17)) -> float:
    """A jittery 0..1 wobble for torches and lamps: summed sines with whole cycles, so loops stay seamless."""
    rnd = random.Random(seed)
    v = sum(math.sin(2 * math.pi * (k * t + rnd.random())) / (i + 1) for i, k in enumerate(cycles))
    return 0.5 + 0.5 * v / sum(1 / (i + 1) for i in range(len(cycles)))


def shake(t: float, amp: float = 1, *, seed: int = 0, cycles: int = 12) -> tuple[int, int]:
    """A whole-pixel screen-shake offset that jumps `cycles` times per loop; scale `amp` to decay it."""
    rnd = random.Random(seed * 7919 + int(t * cycles) % cycles)
    a = round(amp)
    return (rnd.randint(-a, a), rnd.randint(-a, a)) if a > 0 else (0, 0)


def orbit(cx: float, cy: float, rx: float, ry: float, t: float, n: int, *, cycles: int = 1,
          offset: float = 0.0) -> list[tuple[int, int, bool]]:
    """n evenly spaced points on an ellipse turning `cycles` times per loop, as whole pixels (x, y, front),
    sorted back to front: draw the ones with front=False before the thing they circle, the rest after."""
    pts = []
    for k in range(n):
        a = 2 * math.pi * (k / n + cycles * t + offset)
        pts.append((math.sin(a), round(cx + rx * math.cos(a)), round(cy + ry * math.sin(a))))
    return [(x, y, d > 0) for d, x, y in sorted(pts)]


class Fx:
    # particles ---------------------------------------------------------------

    def particles(self, x: int, y: int, w: int, h: int, t: float, kind: str = "dust", *, n: int = 20,
                  colors=None, seed: int = 7, cycles: int = 1, draw: bool = True, **opts) -> list:
        """Seeded particles at time t (see PARTICLES for kinds and their options). "fill" kinds wrap inside
        the area; "emit" kinds start in it and travel out for one life. Each particle completes a whole
        number of lives per loop, so seamless loops need only whole `cycles`. burst=True fires an "emit"
        kind once instead: every particle leaves together just after t=0 and they are gone by t=1 (map a hit's
        window onto t with phase()). Returns (x, y, colour) for each live particle; draw=False only
        computes them."""
        o = {**PARTICLES[kind], **opts}
        cols = list(colors or o["colors"])
        rnd = random.Random(seed)
        out = []
        for i in range(n):
            sx, sy, off, pick = rnd.random(), rnd.random(), rnd.random(), rnd.random()
            rate = rnd.choice(o["rates"]) * cycles
            sway_off, twinkle_off = rnd.random(), rnd.random()
            if o["mode"] == "fill":
                pos = (sy + o.get("fall", 1) * rate * t) % 1
                px = x + (sx * w + o.get("drift", 0) * h * pos) % w
                py = y + pos * h
                px += o.get("sway", 0) * math.sin(2 * math.pi * (rate * t + sway_off))
                if o.get("twinkle") and (rate * 2 * t + twinkle_off) % 1 >= o["twinkle"]:
                    continue
                col = cols[int(pick * len(cols))]
                age = pos
            else:
                if o.get("burst"):
                    if not 0 < t < 1:
                        continue
                    age = t * (0.7 + 0.3 * off)
                else:
                    age = (off + rate * t) % 1
                ang = math.radians(o.get("angle", -90) + (sx - 0.5) * o.get("spread", 0))
                speed = o.get("speed", 20) * (0.6 + 0.4 * pick)
                px = x + sx * w + math.cos(ang) * speed * age + o.get("wind", 0) * age * age
                py = y + sy * h + math.sin(ang) * speed * age + o.get("gravity", 0) * age * age
                px += o.get("sway", 0) * math.sin(2 * math.pi * (age * 2 + sway_off))
                col = cols[min(len(cols) - 1, int(age * len(cols)))]
            px, py = round(px), round(py)
            out.append((px, py, col))
            if not draw:
                continue
            size = o.get("size", (1, 1))
            r = size[0] + (size[1] - size[0]) * age
            if o.get("streak"):
                s = o["streak"]
                self.line(px, py, round(px - o.get("drift", 0) * s), py - s + 1, col)
            elif r <= 1:
                self.px(px, py, col)
            else:
                test = PATTERNS[o["pattern"]] if o.get("pattern") else None
                for yy in range(int(py - r), int(py + r) + 1):
                    for xx in range(int(px - r), int(px + r) + 1):
                        if (xx - px) ** 2 + (yy - py) ** 2 <= r * r and (test is None or test(xx, yy)):
                            self.px(xx, yy, col)
        return out

    def projectile(self, x0: float, y0: float, x1: float, y1: float, p: float, color="white", *, trail=None,
                   length: int = 8, width: int = 1, shards: int = 12, life: float = 0.35, spread: float = 2.0,
                   gravity: float = 4.0, seed: int = 3) -> tuple[int, int] | None:
        """A streak flying from (x0, y0) to (x1, y1) as p goes 0..1: a `length`-px head along its path
        and a trail of debris, each shard dropped at a seeded point on the path and fading (through the
        `trail` colours) over `life` of the flight. Returns the head's position, or None outside 0 < p < 1.
        Map the flight's window onto p with phase(); shards still fall a little after impact."""
        dx, dy = x1 - x0, y1 - y0
        dist = math.hypot(dx, dy) or 1.0
        ux, uy = dx / dist, dy / dist
        cols = list(trail or [color])
        rnd = random.Random(seed)
        for _ in range(shards):
            f, side, drop = rnd.random(), rnd.uniform(-1, 1), rnd.random()
            age = (p - f) / life
            if not 0 < age < 1 or f > 1:
                continue
            sx = x0 + dx * f - uy * side * spread * (1 + age)
            sy = y0 + dy * f + ux * side * spread * (1 + age) + gravity * age * age * (0.5 + drop)
            self.px(round(sx), round(sy), cols[min(len(cols) - 1, int(age * len(cols)))])
        if not 0 < p < 1:
            return None
        hx, hy = x0 + dx * p, y0 + dy * p
        for w in range(width):
            o = w - (width - 1) / 2
            self.line(round(hx - ux * length - uy * o), round(hy - uy * length + ux * o), round(hx - uy * o),
                      round(hy + ux * o), color)
        return round(hx), round(hy)

    def glyph(self, cx: float, cy: float, r: float, t: float = 0.0, color="red", *, squash: float = 1.0,
              runes: int = 6, cycles: int = 1, inner: float = 0.72, accent=None, half=None) -> None:
        """A rune circle: two rings with rune marks between them, turning `cycles` times per loop.
        squash > 1 lays it flat (2 for iso floors). half="back" or "front" draws only the far or near
        side, so it can wrap around a figure drawn in between."""
        def keep(a):
            return half is None or (math.sin(a) >= 0) == (half == "front")
        for rad, col in ((r, color), (r * inner, accent or color)):
            steps = max(12, int(2 * math.pi * rad * 1.6))
            for k in range(steps):
                a = 2 * math.pi * k / steps
                if keep(a):
                    self.px(round(cx + rad * math.cos(a)), round(cy + rad * math.sin(a) / squash), col)
        mid = r * (1 + inner) / 2
        for k in range(runes):
            a = 2 * math.pi * (k / runes + cycles * t)
            if not keep(a):
                continue
            rx, ry = round(cx + mid * math.cos(a)) - 1, round(cy + mid * math.sin(a) / squash) - 1
            for j, row in enumerate(RUNES[k % len(RUNES)]):
                for i, ch in enumerate(row):
                    if ch == "#":
                        self.px(rx + i, ry + j, accent or color)

    def form(self, color, shades, *, light=(-1, -1), width: int = 2, depth: int | None = None,
             region=None) -> None:
        """Shade every pixel of exactly `color` as a lit volume: shades = (shadow, base, light, rim).
        Edges facing `light` (a step like (-1, 1) for light from the lower left) get the rim, then a
        `width`-px light band; edges facing away get a `depth`-px shadow (width by default) with a dithered
        fringe. Paint a part flat
        in a marker colour, call form, then paint the next part over it: each part rims against the last."""
        r = self._region(region)
        a = np.asarray(self.img)[r.y:r.y2, r.x:r.x2]
        m = np.all(a == np.array(self.rgb(color), dtype=a.dtype), axis=2)
        if not m.any():
            return
        lx, ly = int(np.sign(light[0])), int(np.sign(light[1]))
        h, w = m.shape

        def open_within(dx, dy, n):
            out = np.zeros_like(m)
            for k in range(1, n + 1):
                s = np.zeros_like(m)
                ys, xs = slice(max(0, -k * dy), min(h, h - k * dy)), slice(max(0, -k * dx), min(w, w - k * dx))
                yd, xd = slice(max(0, k * dy), min(h, h + k * dy)), slice(max(0, k * dx), min(w, w + k * dx))
                s[ys, xs] = m[yd, xd]
                out |= ~s
            return out & m

        yy, xx = np.mgrid[r.y:r.y2, r.x:r.x2]
        idx = np.full(m.shape, 1)
        depth = width if depth is None else depth
        fringe = open_within(-lx, -ly, depth + 2) & ((xx + yy) % 2 == 0)
        idx[fringe] = 0
        idx[open_within(-lx, -ly, depth)] = 0
        idx[open_within(lx, ly, width)] = 2
        idx[open_within(lx, ly, 1)] = 3
        pal = np.array([self.rgb(s) for s in shades], dtype=np.uint8)
        out = a.copy()
        out[m] = pal[idx[m]]
        self.img.paste(Image.fromarray(out, "RGB"), (r.x, r.y))

    # light and darkness ------------------------------------------------------

    def _shade(self, region, amount, color, levels: int) -> None:
        """Mix each pixel of `region` towards `color` by `amount` (an array, 0..1), quantised to
        `levels` steps with ordered dithering, so each source colour gains at most `levels` shades."""
        r = region
        a = np.asarray(self.img, dtype=np.float64)[r.y:r.y2, r.x:r.x2]
        yy, xx = np.mgrid[r.y:r.y2, r.x:r.x2]
        lv = np.clip(amount, 0, 1) * levels
        k = np.floor(lv)
        k = np.minimum(k + (lv - k > _BAYER[yy % 4, xx % 4]), levels) / levels
        target = np.array(self.rgb(color), dtype=np.float64)
        out = np.rint(a + (target - a) * k[..., None]).astype(np.uint8)
        self.img.paste(Image.fromarray(out, "RGB"), (r.x, r.y))

    def _region(self, region) -> Rect:
        r = Rect(*region) if region is not None else self.bounds
        x0, y0 = max(0, r.x), max(0, r.y)
        return Rect(x0, y0, min(self.w, r.x2) - x0, min(self.h, r.y2) - y0)

    def _distance(self, r: Rect, lights, squash: float):
        yy, xx = np.mgrid[r.y:r.y2, r.x:r.x2] + 0.5
        q = np.full(yy.shape, np.inf)
        for cx, cy, rad in lights:
            q = np.minimum(q, np.hypot((xx - cx) / squash, yy - cy) / max(rad, 0.01))
        return q

    def darkness(self, lights, *, region=None, color="shadow", amount: float = 0.85, levels: int = 3,
                 inner: float = 0.55, squash: float = 2.0) -> None:
        """Darken everything outside a set of light pools. `lights` are (cx, cy, r): clear inside
        `inner * r`, dithering to `amount` towards `color` at `r`. squash=2 matches iso floors."""
        r = self._region(region)
        q = self._distance(r, lights, squash)
        self._shade(r, amount * np.clip((q - inner) / max(1e-6, 1 - inner), 0, 1), color, levels)

    def glow(self, cx: float, cy: float, r: float, color="gold", *, amount: float = 0.35, levels: int = 2,
             squash: float = 1.0, region=None) -> None:
        """Tint towards `color` around a point, strongest in the middle, dithered out to radius r."""
        reg = self._region(region)
        q = self._distance(reg, [(cx, cy, r)], squash)
        self._shade(reg, amount * np.clip(1 - q, 0, 1) * 1.4, color, levels)

    def vignette(self, amount: float = 0.6, *, region=None, color="shadow", levels: int = 3,
                 inner: float = 0.6) -> None:
        """Darken towards the corners of a region (the canvas by default)."""
        r = self._region(region)
        yy, xx = np.mgrid[r.y:r.y2, r.x:r.x2] + 0.5
        q = np.hypot((xx - r.x - r.w / 2) / (r.w / 2), (yy - r.y - r.h / 2) / (r.h / 2))
        self._shade(r, amount * np.clip((q - inner) / (1.3 - inner), 0, 1), color, levels)

    # screen effects ----------------------------------------------------------

    def tint(self, amount: float, color="white", *, region=None, levels: int = 4) -> None:
        """Mix a whole region towards a colour, dithered: a flash, a night grade or a hit."""
        r = self._region(region)
        self._shade(r, np.full((r.h, r.w), float(amount)), color, levels)

    def dissolve(self, p: float, color="bg", *, region=None) -> None:
        """Ordered-dither fade: the share p of pixels becomes `color`, adding no new colours."""
        r = self._region(region)
        rgb = self.rgb(color)
        for y in range(r.y, r.y2):
            for x in range(r.x, r.x2):
                if _BAYER[y % 4, x % 4] < p:
                    self.img.putpixel((x, y), rgb)

    def scanlines(self, *, region=None, amount: float = 0.35, step: int = 2, color="shadow") -> None:
        """Darken every `step`-th row, CRT style."""
        r = self._region(region)
        rows = (np.arange(r.y, r.y2) % step == step - 1).astype(np.float64)
        self._shade(r, np.repeat(rows[:, None], r.w, axis=1) * amount, color, 1)

    # water -------------------------------------------------------------------

    def reflect(self, x: int, y: int, w: int, h: int, t: float = 0.0, *, amp: int = 1, cycles: int = 1,
                wavelength: float = 6.0, color="bg", amount: float = 0.45, gap: int = 0) -> None:
        """Mirror the h rows above row y into rows y .. y+h-1, each row shifted by a whole-pixel ripple
        and mixed towards `color`. Ripples loop with whole `cycles`. gap=n leaves every n-th row plain
        `color`, for broken bands of reflection."""
        src = self.img.crop((x, y - h, x + w, y)).transpose(Image.FLIP_TOP_BOTTOM)
        a = np.asarray(src)
        out = np.empty_like(a)
        for j in range(h):
            dx = round(amp * math.sin(2 * math.pi * (cycles * t + j / wavelength)) * min(1.0, (j + 1) / 3))
            out[j] = np.roll(a[j], dx, axis=0)
        self.img.paste(Image.fromarray(out, "RGB"), (x, y))
        if amount:
            self._shade(self._region(Rect(x, y, w, h)), np.full((h, w), float(amount)), color, 2)
        if gap:
            for j in range(gap - 1, h, gap):
                self.hline(x, y + j, w, color)

    def heat(self, x: int, y: int, w: int, h: int, t: float, *, amp: int = 1, cycles: int = 2,
             wavelength: float = 5.0) -> None:
        """Heat haze: slide each row of a region sideways by a whole-pixel ripple (above lava or fire).
        Whole `cycles` loop seamlessly."""
        r = self._region(Rect(x, y, w, h))
        a = np.asarray(self.img)[r.y:r.y2, r.x:r.x2].copy()
        for j in range(r.h):
            dx = round(amp * math.sin(2 * math.pi * (cycles * t + (r.y + j) / wavelength)))
            if dx:
                a[j] = np.roll(a[j], dx, axis=0)
        self.img.paste(Image.fromarray(a, "RGB"), (r.x, r.y))

    def melt(self, old, new, p: float, *, seed: int = 0, width: int = 2, spread: float = 0.4,
             region=None) -> None:
        """The column-melt screen wipe: the `old` screen slides down in `width`-px columns, each starting
        after a seeded delay (neighbours stay within a step of each other, so the edge ripples) and
        accelerating, revealing `new` behind it. old and new are Canvases or PIL images the size of the
        region (the whole canvas by default); p runs 0 (all old) to 1 (all new)."""
        r = self._region(region)
        o = np.asarray((old.img if hasattr(old, "img") else old).convert("RGB"))[:r.h, :r.w]
        out = np.asarray((new.img if hasattr(new, "img") else new).convert("RGB"))[:r.h, :r.w].copy()
        rnd = random.Random(seed)
        d = rnd.random() * spread
        for k in range((r.w + width - 1) // width):
            if k:
                d = min(spread, max(0.0, d + rnd.choice((-1, 0, 1)) * spread / 16))
            q = min(1.0, max(0.0, (p - d) / (1 - spread)))
            off = int(round(q ** 1.6 * r.h))
            if off < r.h:
                cols = slice(k * width, min(r.w, (k + 1) * width))
                out[off:, cols] = o[:r.h - off, cols]
        self.img.paste(Image.fromarray(out, "RGB"), (r.x, r.y))

    def chunky(self, x: int, y: int, text, colors, *, scale: int = 4, font: str = "large",
               outline="#000000", depth: int = 0, side=None, light=None, dark=None, bevel: int = 1,
               bow: float = 0.0, weight: int = 0, align: str = "center") -> Rect:
        """Big extruded title lettering in the style of early-90s game logos and menus: `text` in `font`
        at `scale`, filled with a dithered top-to-bottom gradient through `colors`, a `bevel`-px `light`
        top-left edge and `dark` bottom-right edge, extruded `depth` px down-right in `side` (a colour or
        a list from near to far) and ringed by `outline`. bow > 0 swells the letters towards both ends,
        like a logo seen in perspective; bow < 0 towards the middle. `weight` fattens every stroke by
        that many px on each side, closing the counters. x is the left, centre or right edge
        per align and y the top. Not layout-checked: it is artwork. Returns the box drawn."""
        from .fonts import FONTS
        f = FONTS[font]
        norm = f.normalize(text)
        tw, th = max(0, f.advance(norm) - f.tracking) * scale, f.cap * scale
        m = np.zeros((th, max(1, tw)), dtype=bool)
        pen = 0
        for ch in norm:
            g = f.glyph(ch)
            for gx, gy in g.px:
                if 0 <= gy < f.cap:
                    m[gy * scale:(gy + 1) * scale, pen + gx * scale:pen + (gx + 1) * scale] = True
            pen += (g.width + f.tracking) * scale
        if weight:
            p = np.pad(m, weight)
            m = np.zeros_like(p)
            for oy in range(2 * weight + 1):
                for ox in range(2 * weight + 1):
                    m |= np.roll(np.roll(p, oy - weight, axis=0), ox - weight, axis=1)
            th = m.shape[0]
        tw = m.shape[1]
        hh = int(math.ceil(th * (1 + abs(bow))))
        e = (2 * (np.arange(tw) + 0.5) / tw - 1) ** 2
        fac = 1 + (bow * e if bow >= 0 else -bow * (1 - e))
        src = np.floor((np.arange(hh)[:, None] + 0.5 - hh / 2) / fac[None, :] + th / 2).astype(int)
        valid = (src >= 0) & (src < th)
        face = m[np.clip(src, 0, th - 1), np.arange(tw)[None, :]] & valid
        pad = depth + 2
        full = np.zeros((hh + pad, tw + pad), dtype=bool)
        full[1:hh + 1, 1:tw + 1] = face
        lay = np.zeros(full.shape + (3,), dtype=np.uint8)
        ink = np.zeros(full.shape, dtype=bool)

        def shifted(a, dx, dy):
            out = np.zeros_like(a)
            out[dy:, dx:] = a[:a.shape[0] - dy, :a.shape[1] - dx]
            return out

        sides = side if isinstance(side, (list, tuple)) else [side or (dark or colors[-1])]
        solid = full.copy()
        for k in range(depth, 0, -1):
            sh = shifted(full, k, k) & ~full
            lay[sh] = self.rgb(sides[min(len(sides) - 1, (k - 1) * len(sides) // depth)])
            ink |= sh
            solid |= sh
        if outline is not None:
            p = np.pad(solid, 1)
            ring = np.zeros_like(solid)
            for oy in (0, 1, 2):
                for ox in (0, 1, 2):
                    ring |= p[oy:oy + solid.shape[0], ox:ox + solid.shape[1]]
            ring &= ~solid
            lay[ring] = self.rgb(outline)
            ink |= ring
        rgbs = [self.rgb(col) for col in colors]
        n = max(1, len(rgbs) - 1)
        pos = np.zeros(full.shape)
        pos[1:hh + 1, 1:tw + 1] = (np.clip(src, 0, th - 1) + 0.5) / th * n
        x0 = x - tw // 2 if align == "center" else x - tw if align == "right" else x
        yy, xx = np.mgrid[y - 1:y - 1 + full.shape[0], x0 - 1:x0 - 1 + full.shape[1]]
        kk = np.minimum(np.floor(pos).astype(int), n - 1) if len(rgbs) > 1 else np.zeros(full.shape, int)
        hit = (pos - kk) > _BAYER[yy % 4, xx % 4]
        idx = np.clip(kk + hit, 0, len(rgbs) - 1)
        lay[full] = np.array(rgbs, dtype=np.uint8)[idx[full]]
        ink |= full
        for edge_col, dirs in ((dark, ((-1, 0), (0, -1))), (light, ((1, 0), (0, 1)))):
            if edge_col is None:
                continue
            edge = np.zeros_like(full)
            for k in range(1, bevel + 1):
                for ex, ey in dirs:
                    nb = np.zeros_like(full)
                    if ex > 0:
                        nb[:, k:] = full[:, :-k]
                    elif ex < 0:
                        nb[:, :-k] = full[:, k:]
                    elif ey > 0:
                        nb[k:, :] = full[:-k, :]
                    else:
                        nb[:-k, :] = full[k:, :]
                    edge |= full & ~nb
            lay[edge] = self.rgb(edge_col)
        box = Rect(x0 - 1, y - 1, full.shape[1], full.shape[0])
        r = self._region(box)
        if r.w > 0 and r.h > 0:
            a = np.asarray(self.img)[r.y:r.y2, r.x:r.x2].copy()
            sl = (slice(r.y - box.y, r.y2 - box.y), slice(r.x - box.x, r.x2 - box.x))
            a[ink[sl]] = lay[sl][ink[sl]]
            self.img.paste(Image.fromarray(a, "RGB"), (r.x, r.y))
        return box

    def shimmer(self, x: int, y: int, w: int, h: int, t: float, color="white", *, n: int = 16, seed: int = 7,
                cycles: int = 1, length=(2, 5), on=None) -> None:
        """Glinting horizontal dashes on water: they drift and blink a whole number of times per loop.
        `on` limits them to pixels that are currently that colour (water inside a coastline)."""
        rnd = random.Random(seed)
        only = self.rgb(on) if on is not None else None
        for _ in range(n):
            sx, sy, off, dirn = rnd.random(), rnd.randrange(h), rnd.random(), rnd.choice((-1, 1))
            ln = rnd.randint(*length)
            if (2 * cycles * t + off) % 1 > 0.65:
                continue
            px = x + round((sx + dirn * cycles * t) % 1 * w)
            for k in range(min(ln, x + w - px)):
                if 0 <= px + k < self.w and 0 <= y + sy < self.h and (
                        only is None or self.img.getpixel((px + k, y + sy)) == only):
                    self.px(px + k, y + sy, color)
