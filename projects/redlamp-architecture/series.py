"""Shared frame for the Redlamp architecture series: header, footer, layer colours."""

TOTAL = 6
SOURCE = "REDLAMP AT COMMIT 49AE4A1F, 7 OCT 2026"

APPS, UI, API, ENGINE, GPU = "muted", "red", "blue", "green", "gold"

LAMP = (
    [
        "..ooooo..",
        ".orrrrro.",
        "orrlllrro",
        "orllwllro",
        "orlllllro",
        "orrlllrro",
        ".orrrrro.",
        "..ooooo..",
    ],
    {"o": "muted", "r": "red", "l": "red.light", "w": "white"},
)


def frame(c, n: int, title: str, notes: str = "") -> tuple[int, int]:
    """Header and footer for image n of the series. Returns the content's top and bottom rows."""
    bottom = c.footer(f"{notes} SOURCE: {SOURCE}." if notes else f"SOURCE: {SOURCE}.")
    top = c.header(f"REDLAMP · {title}", right=[("ARCHITECTURE ", "dim"), (f"{n}/{TOTAL}", "text")], mark=LAMP)
    return top, bottom
