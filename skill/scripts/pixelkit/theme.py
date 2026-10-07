"""Theme loading and colour resolution."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
DEFAULT_THEME = SKILL_DIR / "theme.toml"

RGB = tuple[int, int, int]


def hex_rgb(value: str) -> RGB:
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"bad hex colour {value!r}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: RGB, b: RGB, t: float) -> RGB:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


class Theme:
    def __init__(self, data: dict, path: Path | None = None):
        self.data = data
        self.path = path
        self.name = data.get("name", "theme")
        self.scale = int(data.get("scale", 4))
        self.series = list(data.get("series", []))
        self.brand = dict(data.get("brand", {}))
        self.thousands = data.get("thousands", ",")
        self.decimal = data.get("decimal", ".")
        self.colors: dict[str, RGB] = {}
        for name, value in data.get("colors", {}).items():
            self.colors[name] = hex_rgb(value)
        self.accents: list[str] = []
        for name, shades in data.get("accents", {}).items():
            self.accents.append(name)
            base = hex_rgb(shades["base"])
            self.colors[name] = base
            self.colors[f"{name}.dark"] = hex_rgb(shades["dark"]) if "dark" in shades else mix(base, (0, 0, 0), 0.4)
            self.colors[f"{name}.light"] = hex_rgb(shades["light"]) if "light" in shades else mix(base, (255, 255, 255), 0.42)
        if not self.series:
            self.series = self.accents[:6]

    def rgb(self, color) -> RGB:
        """Resolve a colour name ("green.dark"), hex string or RGB tuple."""
        if isinstance(color, tuple):
            return color[:3]
        if isinstance(color, str):
            if color.startswith("#"):
                return hex_rgb(color)
            if color in self.colors:
                return self.colors[color]
        raise KeyError(f"unknown colour {color!r}; theme {self.name!r} has: {', '.join(self.colors)}")

    def shade(self, color, which: str):
        """The dark/light variant of an accent name, or a mixed shade for any other colour."""
        if isinstance(color, str) and f"{color}.{which}" in self.colors:
            return f"{color}.{which}"
        base = self.rgb(color)
        return mix(base, (0, 0, 0), 0.4) if which == "dark" else mix(base, (255, 255, 255), 0.42)

    def series_color(self, i: int) -> str:
        return self.series[i % len(self.series)]

    def palette(self, names=None) -> list[RGB]:
        """Distinct RGB values for the named colours (all theme colours by default)."""
        out: list[RGB] = []
        for name in names or self.colors:
            rgb = self.rgb(name)
            if rgb not in out:
                out.append(rgb)
        return out

    def num(self, value: float, decimals: int = 0) -> str:
        s = f"{value:,.{decimals}f}"
        return s.replace(",", "\0").replace(".", self.decimal).replace("\0", self.thousands)


def load_theme(path=None) -> Theme:
    path = Path(path or os.environ.get("PIXELKIT_THEME") or DEFAULT_THEME).expanduser()
    with open(path, "rb") as f:
        return Theme(tomllib.load(f), path)
