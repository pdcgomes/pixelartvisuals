"""Game HUD parts mixed into Canvas: bevelled frames, liquid orbs and cooldown sweeps."""

from __future__ import annotations

import math

from PIL import Image

from .geometry import Rect


class Hud:
    def bevel(self, x: int, y: int, w: int, h: int, face="raised", *, light=None, dark=None, sunk: bool = False,
              border=None) -> Rect:
        """A raised (or sunk) block: lit top-left edges, shaded bottom-right ones, an optional outer border.
        Returns the face inside the edges."""
        if border is not None:
            self.box(x, y, w, h, border)
            x, y, w, h = x + 1, y + 1, w - 2, h - 2
        hi, lo = light or self.light(face), dark or self.dark(face)
        if sunk:
            hi, lo = lo, hi
        self.rect(x, y, w, h, face)
        self.hline(x, y, w, hi)
        self.vline(x, y, h, hi)
        self.hline(x, y + h - 1, w, lo)
        self.vline(x + w - 1, y + 1, h - 1, lo)
        return Rect(x + 1, y + 1, w - 2, h - 2)

    def orb(self, cx: float, cy: float, r: float, frac: float, color, *, empty="raised", rim="line",
            t: float = 0.0, waves: int = 1) -> Rect:
        """A glass globe filled to `frac` with a lit liquid whose surface ripples (whole `waves` per loop),
        a darker empty part, a rim ring and a glint. Returns its bounding Rect."""
        if rim is not None:
            self.circle(cx, cy, r + 1, rim)
        box = (int(cx - r) - 1, int(cy - r) - 1, int(cx + r) + 2, int(cy + r) + 2)
        self.sphere(cx, cy, r, empty)
        dry = self.img.crop(box)
        self.sphere(cx, cy, r, color)
        level = cy + r - 2 * r * max(0.0, min(1.0, frac))
        mask = Image.new("1", dry.size, 0)
        surf = self.light(color)
        for X in range(box[0], box[2]):
            wob = round(math.sin(2 * math.pi * (waves * t + (X - cx) / (r * 1.3))) * min(1.0, r / 8))
            top = round(level) + wob
            for Y in range(box[1], min(box[3], top)):
                mask.putpixel((X - box[0], Y - box[1]), 1)
            if 0 < frac < 1 and (X + 0.5 - cx) ** 2 + (top + 0.5 - cy) ** 2 < r * r:
                self.px(X, top, surf)
        self.img.paste(dry, box[:2], mask)
        gx, gy = round(cx - r * 0.45), round(cy - r * 0.5)
        self.rect(gx, gy, max(1, round(r / 6)), max(1, round(r / 5)), "white")
        self.px(gx + max(1, round(r / 6)) + 1, gy - 1, "white")
        return Rect(*box[:2], box[2] - box[0], box[3] - box[1])

    def cooldown(self, x: int, y: int, w: int, h: int, frac: float, *, color="shadow", amount: float = 0.6,
                 edge=None) -> None:
        """Shade the part of a slot still cooling down: a clockwise sweep from 12 o'clock, `frac` of the
        turn left. `edge` draws the sweep's leading pixel line."""
        if frac <= 0:
            return
        cx, cy = x + w / 2, y + h / 2
        done = 1 - min(1.0, frac)
        dark = self.rgb(color)
        for Y in range(y, y + h):
            for X in range(x, x + w):
                a = (math.atan2(X + 0.5 - cx, -(Y + 0.5 - cy)) / (2 * math.pi)) % 1
                if a >= done:
                    p = self.img.getpixel((X, Y))
                    self.img.putpixel((X, Y), tuple(round(v + (d - v) * amount) for v, d in zip(p, dark)))
        if edge is not None:
            ang = 2 * math.pi * done
            for k in range(2 * max(w, h)):
                X, Y = math.floor(cx + math.sin(ang) * k / 2), math.floor(cy - math.cos(ang) * k / 2)
                if not (x <= X < x + w and y <= Y < y + h):
                    break
                self.px(X, Y, edge)
