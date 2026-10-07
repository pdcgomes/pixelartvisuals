# Showcase

Each script draws one piece with `pixelkit` and writes it beside itself: a PNG for a still, or a
GIF and a `-poster.png` for an animation. From the repository's root:

```bash
PYTHONPATH=skill/scripts python3 examples/bedroom.py
```

| Script | What it draws | Data |
| --- | --- | --- |
| `bedroom.py` | The sysop's bedroom, 1992: an isometric room, a BBS session on the CRT, a street fight on the TV | Made up |
| `tracker.py` | Pixeltrakker 8, a music tracker in the Amiga and M8 traditions | Made up |
| `fruitmusic.py` | Fruit Music, a Winamp-style player with an equaliser, playlist and album art | Made up |
| `daw.py` | Pixel Loops Studio, a pattern-based DAW | Made up |
| `finance.py` | A trading terminal for a fictional $PIXL | Made up |
| `hacker.py` | A film's hacking scene | Made up |
| `rpg.py` | A developer's RPG character sheet | Made up |
| `arcade.py` | An arcade's attract screen and hall of fame | Made up |
| `skyline.py` | The ten tallest buildings, to scale | CTBUH, completed buildings as of 2025 |
| `planets.py` | The planets to scale | NASA's mean diameters |
| `moon.py` | The moon's phases in October 2026 | Computed from the mean synodic month |
| `commits.py` | Redlamp's commits by day and hour | Its git log, 29 September to 7 October 2026 |

They use a few shapes the templates don't: `circle`, `sphere` and `polygon` in the kit's art, and
`pie`, `radar` and `heatmap` among its widgets.
