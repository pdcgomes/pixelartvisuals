# pixelartvisuals

Pixel-art infographics, charts, diagrams and animations for blog posts, drawn on a tiny grid and
exported crisp.

![A generational bar chart in the pixel style](skill/examples/generations.png)

Every graphic is drawn on a small logical canvas (320×180 by default) in whole pixels, then
scaled up with nearest-neighbour filtering, so each pixel becomes a sharp 4×4 block. Two bitmap
fonts, a navy-and-rainbow palette and a set of parts (striped 3D bars, LED meters, gauges,
sparklines, waffles, isometric devices) give everything the same retro look. The same drawing code
exports stills (PNG) and animations (GIF, WebP, MP4).

The repo holds two things:

- [`skill/`](skill/): the kit, `pixelkit` (Python), with its templates, its theme and the
  instructions an AI agent follows to make new graphics (a Cursor or Claude Code skill).
- [`projects/`](projects/): series made with it, starting with
  [Redlamp's architecture](projects/redlamp-architecture/).

## Gallery

| | |
| --- | --- |
| ![Dashboard](skill/examples/dashboard.png) | ![Live dashboard loop](skill/examples/dashboard_live.gif) |
| `dashboard.py`: the state of a machine | `dashboard_live.py`: the same, live, as a seamless loop |
| ![Ranking](skill/examples/ranking.png) | ![Bar chart intro](skill/examples/generations_intro.gif) |
| `ranking.py`: a hero total, a share bar and a top 10 | `generations_intro.py`: bars rise, values count up |
| ![Waffle](skill/examples/waffle.png) | ![Cover](skill/examples/cover.png) |
| `waffle.py`: parts of a whole | `cover.py`: a post cover and social card |
| ![Diagram](skill/examples/diagram.png) | ![Specimen](skill/examples/specimen.png) |
| `diagram.py`: nodes, a bus and connectors | `specimen.py`: every glyph, colour, icon and part |

## Showcase

What else the kit can draw, when nobody's asking for a bar chart. Each piece is one script in
[`examples/`](examples/); run any of them with `PYTHONPATH=skill/scripts python3 examples/<name>.py`.

[![The sysop's bedroom, 1992](examples/bedroom.gif)](examples/bedroom.py)

`bedroom.py`: the sysop's bedroom, 1992. An isometric room at night with a beige PC, a 2400 bps
modem, a 16-bit console with a street fight on the TV, a lava lamp and a sleeping cat, while the
CRT dials a BBS and starts a download that will take four and a half minutes.

| | |
| --- | --- |
| ![Pixeltrakker 8](examples/tracker.gif) | ![Fruit Music](examples/fruitmusic.gif) |
| `tracker.py`: a music tracker, half Amiga, half M8, playing a 32-row pattern | `fruitmusic.py`: a Winamp-style player for the streaming era |
| ![Pixel Loops Studio](examples/daw.gif) | ![$PIXL](examples/finance.gif) |
| `daw.py`: a pattern-based DAW with a channel rack, piano roll and mixer | `finance.py`: a trading terminal with candles, moving averages and a ticker tape |
| ![Hacker UI](examples/hacker.gif) | ![Character sheet](examples/rpg.gif) |
| `hacker.py`: a film's hacking scene, from the terminal to the trace to the glitch | `rpg.py`: a developer's character sheet, with stats, inventory and quests |
| ![Hall of fame](examples/arcade.gif) | ![Skyline](examples/skyline.gif) |
| `arcade.py`: an arcade's attract screen, with marching invaders | `skyline.py`: the world's ten tallest buildings, to scale, at dusk |
| ![Planets](examples/planets.png) | ![Moon phases](examples/moon.png) |
| `planets.py`: the planets to scale, with the sun too big to fit | `moon.py`: October 2026's moon phases, computed |
| ![Commits](examples/commits.png) | ![Isometric action RPG](examples/dungeon.gif) |
| `commits.py`: when Redlamp gets built, 1,050 commits by day and hour | `dungeon.py`: an isometric action RPG boss fight, with a necromancer and his raised skeletons |
| ![MMORPG raid](examples/mmo.gif) | ![City builder](examples/city.gif) |
| `mmo.py`: an MMORPG raid on a molten fire lord in a canyon hold, with unit frames, a minimap, quests, chat and action bars | `city.py`: an isometric city builder in the mid-90s style |
| ![Pirate adventure](examples/pirate.gif) | ![Lounge adventure](examples/lounge.gif) |
| `pirate.py`: a point-and-click pirate adventure: an isometric harbour, a ghostly captain, verbs and an inventory | `lounge.py`: a late-80s parser adventure, redrawn as an isometric neon lounge |
| ![DOOM, redrawn in the kit](examples/doom.gif) | |
| `doom.py`: DOOM, redrawn in the kit: the title screen, the menus, the melt and the first level | |

The trading data, the scores, the hero and the fight are made up; the planets, the buildings, the
moon and the commits are real. The game screens are homages in the kit's style with original names
(only `doom.py` keeps its game's logo). The kit's game primitives (particles, light, HUD frames, a
raycaster and a screen melt) make such scenes cheap to build.

## Projects

[**Redlamp's architecture, in six pictures**](projects/redlamp-architecture/): an open-source raw
photo editor's layers, modules, pipeline, frame timing, storage and on-device models, drawn with
the kit's diagram parts.

[![Redlamp at a glance](projects/redlamp-architecture/01_overview.png)](projects/redlamp-architecture/)

## Quick start

Requires Python 3.11 or later with Pillow and numpy. ffmpeg is needed only for MP4.

```python
from pixelkit import Canvas

c = Canvas(preset="wide")                          # 320x180, exported at 4x: 1280x720
bottom = c.footer("SOURCE: WHERE THE NUMBERS CAME FROM, 7 OCT 2026")
top = c.header("COFFEE · CUPS PER DAY", right="ONE WEEK")
p = c.panel(0, top + 1, 320, bottom - top - 3, "THIS WEEK", color="orange")
c.bar_chart(p.x, p.y + 8, p.w, p.h - 20, [3, 2, 4, 5, 6, 1, 0],
            xlabels=["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], ticks=3, ymax=6)
c.save("coffee.png")                               # prints any layout warnings
```

```bash
PYTHONPATH=skill/scripts python3 coffee.py
```

Wrap the drawing in `draw(c, t)` and call `animate(draw, "coffee.gif", seconds=2, hold=3)` to
animate it. [`skill/SKILL.md`](skill/SKILL.md) has the workflow and style rules, and
[`skill/reference.md`](skill/reference.md) the whole API. After changing the kit, run
`python3 skill/scripts/selftest.py`.

## Use it as an agent skill

The `skill/` folder is a skill for Cursor and Claude Code: it teaches the agent the style, the
templates and the review steps. Link it into place:

```bash
ln -s "$PWD/skill" ~/.cursor/skills/pixel-graphics    # Cursor
ln -s "$PWD/skill" ~/.claude/skills/pixel-graphics    # Claude Code
```

Then ask for a pixel graphic for a post. The skill's quick start expects it at
`~/.cursor/skills/pixel-graphics`. A link into a repo on an external disk disappears while that
disk is unplugged.

## Theme

[`skill/theme.toml`](skill/theme.toml) sets the palette (nine neutrals and eleven accents, each
with light and dark shades), the order series colours are used in, number separators, and the brand
name and mark printed in headers and footers. Change it to restyle every future graphic, or pass
`Canvas(theme="other.toml")`.

## Credits

The 5×7 title font comes from the author's Paradise Café remaster. The look follows two system
dashboards and charts drawn in this style, rebuilt with the kit as `dashboard.py` and
`generations.py`.

## Licence

[MIT](LICENSE).
