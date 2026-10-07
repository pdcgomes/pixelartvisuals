"""pixelkit: crisp pixel-art graphics drawn at low resolution and exported with nearest-neighbour scaling."""

from .art import ICONS, Iso, lock
from .canvas import PRESETS, Canvas
from .fonts import FONTS
from .geometry import PATTERNS, Rect, split
from .motion import (animate, blink, clamp01, ease_back, ease_in_out, ease_out, lerp, phase, reveal, stagger,
                     steps, wave)
from .theme import Theme, load_theme
from .widgets import bar_depth, compact, nice_max

__all__ = [
    "Canvas", "Rect", "split", "PRESETS", "PATTERNS", "FONTS", "ICONS", "Iso",
    "Theme", "load_theme", "lock", "compact", "nice_max", "bar_depth",
    "animate", "phase", "stagger", "ease_out", "ease_in_out", "ease_back", "steps", "wave", "blink",
    "reveal", "lerp", "clamp01",
]
