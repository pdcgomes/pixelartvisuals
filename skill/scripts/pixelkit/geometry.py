"""Integer rectangles, span splitting and pixel patterns."""

from __future__ import annotations

from typing import NamedTuple

BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

# Pattern name -> test(x, y) for pixels that get ink. Coordinates are absolute so
# neighbouring fills line up.
PATTERNS = {
    "checker": lambda x, y: (x + y) % 2 == 0,
    "sparse": lambda x, y: x % 2 == 0 and y % 2 == 0,
    "dense": lambda x, y: not (x % 2 and y % 2),
    "hlines": lambda x, y: y % 2 == 0,
    "vlines": lambda x, y: x % 2 == 0,
    "diagonal": lambda x, y: (x + y) % 4 == 0,
    "mesh": lambda x, y: y % 2 == 1 and (x + (y // 2) % 2 * 2) % 4 < 2,
    "grille": lambda x, y: x % 3 != 2 and y % 3 != 2,
    "slots": lambda x, y: x % 4 < 2 and y % 3 < 2,
    "grain": lambda x, y: ((x * 73856093) ^ (y * 19349663)) % 7 == 0,
}


def split(start: int, length: int, parts, gap: int = 0) -> list[tuple[int, int]]:
    """Divide a span into (position, size) pieces; parts is a count or a list of weights."""
    weights = [1] * parts if isinstance(parts, int) else list(parts)
    avail = length - gap * (len(weights) - 1)
    raw = [avail * w / sum(weights) for w in weights]
    sizes = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: sizes[i] - raw[i])[: avail - sum(sizes)]:
        sizes[i] += 1
    out, pos = [], start
    for s in sizes:
        out.append((pos, s))
        pos += s + gap
    return out


class Rect(NamedTuple):
    x: int
    y: int
    w: int
    h: int

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2

    def intersects(self, r: Rect) -> bool:
        return self.x < r.x2 and r.x < self.x2 and self.y < r.y2 and r.y < self.y2

    def contains(self, r: Rect) -> bool:
        return self.x <= r.x and r.x2 <= self.x2 and self.y <= r.y and r.y2 <= self.y2

    def inset(self, dx: int, dy: int | None = None) -> Rect:
        dy = dx if dy is None else dy
        return Rect(self.x + dx, self.y + dy, self.w - 2 * dx, self.h - 2 * dy)

    def cols(self, parts, gap: int = 2) -> list[Rect]:
        return [Rect(x, self.y, w, self.h) for x, w in split(self.x, self.w, parts, gap)]

    def rows(self, parts, gap: int = 2) -> list[Rect]:
        return [Rect(self.x, y, self.w, h) for y, h in split(self.y, self.h, parts, gap)]

    def cut_top(self, h: int, gap: int = 0) -> tuple[Rect, Rect]:
        return Rect(self.x, self.y, self.w, h), Rect(self.x, self.y + h + gap, self.w, self.h - h - gap)

    def cut_bottom(self, h: int, gap: int = 0) -> tuple[Rect, Rect]:
        return Rect(self.x, self.y2 - h, self.w, h), Rect(self.x, self.y, self.w, self.h - h - gap)

    def cut_left(self, w: int, gap: int = 0) -> tuple[Rect, Rect]:
        return Rect(self.x, self.y, w, self.h), Rect(self.x + w + gap, self.y, self.w - w - gap, self.h)

    def cut_right(self, w: int, gap: int = 0) -> tuple[Rect, Rect]:
        return Rect(self.x2 - w, self.y, w, self.h), Rect(self.x, self.y, self.w - w - gap, self.h)
