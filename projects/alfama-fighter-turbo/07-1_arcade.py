"""7.1 The screens and an arcade run: from the boot card through the attract demo, the title and the
menu into the arcade, whose loop is the map of Lisbon, the VS screen, the fight and the winner's quote,
then the next fight; a second player's start cuts in with HERE COMES A NEW CHALLENGER!, and the
winner of that best of three carries on the run.

Animated, a seamless loop: player 1's run (a tram-yellow packet) goes boot, demo, title, menu, arcade,
select, map, VS, fight, quote, back round to the map and into the next fight; there player 2 breaks
in (a pale-blue packet) through the challenger's banner, his own select screen and the best of three,
and comes back up to the map as the run's new owner, who plays on to the ending and the credits.
Each screen lights as the packet passes. Every label stays on screen.

Numbers and sources (alfamafighterturbo at 74e2f64):
- Demo fight 22 s; title back to the demo after 30 s alone: docs/studio/front-end.md, section 1
  (the flow) and section 2 (the attract sequence, "22 s from the start").
- The boot card exists because browsers start audio only on a gesture: front-end.md section 2
  ("The boot card") and src/game/screens/boot.ts.
- VS screen stays until its stinger has played: front-end.md section 2 ("The VS screen").
- Map: the tram leaves on the jingle's first downbeat and arrives on its held last chord:
  front-end.md section 2 ("The map of Lisbon").
- Continue counted in the score's last digit: front-end.md ("Continue"); src/game/screens/run.ts.
- Challenger: a best of three on the run's stage, the winner carrying on the run: front-end.md
  ("The challenger"); decisions.md rows of 8 October.
- 9 fights with the full roster (7 homes, the bridge, the boss): src/game/screens/run.ts bouts()
  with src/fighters/index.ts FIGHTERS and BOSSES and the ten stages in assets/stages/.
- CPU half a level under the difficulty at the first fight, half a level over at the last:
  run.ts levelFor().
"""

from pixelkit import ease_in_out, phase
from series import along, export, frame, packet

P1, P2, FRONT = "yellow", "sky", "orange"
W, H = 84, 19
XS = [8, 104, 200, 296, 388]

# The timeline: (start, end, path name). The loop is seamless, so it starts and ends on the boot card.
LEGS = [
    (0.00, 0.14, "front"),
    (0.14, 0.20, "down"),
    (0.20, 0.36, "run"),
    (0.36, 0.44, "loop"),
    (0.44, 0.52, "run2"),
    (0.54, 0.72, "challenge"),
    (0.72, 0.78, "up"),
    (0.78, 0.92, "run3"),
    (0.92, 0.98, "end"),
]


def draw(c, t):
    top, bottom = frame(c, 7, 1, "THE SCREENS AND AN ARCADE RUN")
    ya = top + 27
    yb = ya + H + 43
    yc = yb + H + 47

    leg = next((name for a, b, name in LEGS if a <= t < b), None)
    p = 0.0
    for a, b, name in LEGS:
        if name == leg:
            p = ease_in_out(phase(t, a, b))
    lit = set()

    def node(x, y, title, accent, sub, key=None):
        on = key in lit
        return c.node(x, y, W, H, title, color="white" if on else accent, sub=sub, border="white" if on else "line")

    # Which screen the packet is at, lit as it passes.
    if leg == "front":
        lit.add(["boot", "intro", "title", "menu", "arcade"][min(4, int(p * 5))])
    elif leg in ("run", "run2", "run3"):
        seq = ["select", "map", "vs", "fight", "quote"] if leg == "run" else ["map", "vs", "fight", "quote"] if leg == "run3" else ["map", "vs", "fight"]
        lit.add(seq[min(len(seq) - 1, int(p * len(seq)))])
    elif leg == "challenge":
        lit.add(["challenger", "select2", "best"][min(2, int(p * 3))])
    elif leg == "end":
        lit.add("ending")
    elif leg is None and t >= 0.98:
        lit.add("boot")

    # The front end.
    c.text(XS[0], ya - 9, "THE FRONT END", c.light(FRONT))
    boot = node(XS[0], ya, "BOOT CARD", FRONT, "PRESS ANY KEY", "boot")
    intro = node(XS[1], ya, "ATTRACT DEMO", FRONT, "SCRIPTED, 22 S", "intro")
    title = node(XS[2], ya, "TITLE", FRONT, "PRESS START", "title")
    menu = node(XS[3], ya, "MAIN MENU", FRONT, "ARCADE, VERSUS ...", "menu")
    arcade = node(XS[4], ya, "ARCADE", P1, "ONE PLAYER", "arcade")
    for a, b in ((boot, intro), (intro, title), (title, menu), (menu, arcade)):
        c.arrow(a.x2, a.cy, b.x - 1, a.cy, "line")
    c.connect(title, intro, "dim", side="top", ax=title.cx, bx=intro.cx, via=ya - 5, dotted=True)
    c.text(intro.x2 + 2, ya - 13, "30 S ALONE: THE ATTRACT AGAIN", "dim", align="left")

    # The run.
    c.text(XS[0], yb - 9, "THE RUN", c.light(P1))
    select = node(XS[0], yb, "SELECT", P1, "A MAP OF LISBON", "select")
    mapn = node(XS[1], yb, "MAP", P1, "TRAM ON A JINGLE", "map")
    vs = node(XS[2], yb, "VS", P1, "AS LONG AS ITS TUNE", "vs")
    fight = node(XS[3], yb, "FIGHT", P1, "LOST? CONTINUE", "fight")
    quote = node(XS[4], yb, "WIN QUOTE", P1, "THE WINNER'S LINE", "quote")
    for a, b in ((select, mapn), (mapn, vs), (vs, fight), (fight, quote)):
        c.arrow(a.x2, a.cy, b.x - 1, a.cy, "line")
    g = ya + H + 14
    c.connect(arcade, select, "line", ax=arcade.x + 12, bx=select.cx, via=g)
    loop = c.connect(quote, mapn, c.light(P1), side="top", ax=quote.x2 - 12, bx=mapn.cx + 16, via=g + 8)
    c.text(quote.x2 - 15, g + 10, "WON: THE NEXT FIGHT", c.light(P1), align="right")

    # The challenger.
    c.text(XS[1], yc + H + 4, "A SECOND PLAYER BREAKS IN", c.light(P2))
    chal = node(XS[3], yc, "NEW CHALLENGER!", P2, "2P PRESSES START", "challenger")
    sel2 = node(XS[2], yc, "2P SELECT", P2, "1P LOCKED IN", "select2")
    best = node(XS[1], yc, "BEST OF THREE", P2, "ON THE RUN'S STAGE", "best")
    ending = node(XS[4], yc, "ENDING, CREDITS", P1, "AFTER THE LAST FIGHT", "ending")
    c.arrow(fight.cx, fight.y2, fight.cx, chal.y - 1, c.light(P2))
    c.arrow(chal.x - 1, chal.cy, sel2.x2, chal.cy, c.light(P2))
    c.arrow(sel2.x - 1, sel2.cy, best.x2, sel2.cy, c.light(P2))
    c.arrow(best.cx, best.y - 1, best.cx, mapn.y2, c.light(P2))
    c.text(best.cx + 4, mapn.y2 + 6, "THE WINNER", c.light(P2))
    c.text(best.cx + 4, mapn.y2 + 13, "CARRIES ON THE RUN", c.light(P2))
    c.arrow(quote.cx, quote.y2, quote.cx, ending.y - 1, "line")
    c.text(quote.cx - 4, quote.y2 + 9, "WON THE LAST", "dim", align="right")

    # The footnotes on the run.
    note = c.panel(0, yc + H + 14, c.w, bottom - yc - H - 16, "A RUN ACROSS LISBON", color=c.light(P1),
                   sub="ALL EIGHT FIGHTERS: 9 FIGHTS")
    c.paragraph(note.x, note.y, "SEVEN FIGHTERS AT THEIR HOMES, IN A FIXED TOUR OF THE CITY BY TRAM, THEN YOUR "
                "OWN DOUBLE ON THE BRIDGE, THEN ADAMASTOR. THE COMPUTER OPPONENT STARTS HALF A LEVEL UNDER THE DIFFICULTY "
                "SETTING AND ENDS HALF A LEVEL OVER IT. THE BOOT CARD IS THERE BECAUSE A BROWSER PLAYS NO "
                "SOUND UNTIL A KEY IS PRESSED OR THE SCREEN TAPPED.", 330, "text")
    kx = note.x2 - 100
    packet(c, kx + 2, note.y + 2, P1)
    c.text(kx + 8, note.y, "PLAYER 1'S RUN", "text")
    packet(c, kx + 2, note.y + 11, P2)
    c.text(kx + 8, note.y + 9, "PLAYER 2, WHO WINS IT", "text")

    # The packet.
    lane = g + 8
    paths = {
        "front": [(boot.cx, boot.cy), (arcade.cx, arcade.cy)],
        "down": [(arcade.x + 12, arcade.y2 + 2), (arcade.x + 12, g), (select.cx, g), (select.cx, select.y - 2)],
        "run": [(select.cx, select.cy), (quote.cx, quote.cy)],
        "loop": [(quote.x2 - 12, quote.y - 2), (quote.x2 - 12, lane), (mapn.cx + 16, lane), (mapn.cx + 16, mapn.y - 2)],
        "run2": [(mapn.cx, mapn.cy), (fight.cx, fight.cy)],
        "challenge": [(fight.cx, fight.y2 + 2), (fight.cx, chal.cy), (best.cx, best.cy)],
        "up": [(best.cx, best.y - 2), (best.cx, mapn.y2 + 2)],
        "run3": [(mapn.cx, mapn.cy), (quote.cx, quote.cy)],
        "end": [(quote.cx, quote.y2 + 2), (quote.cx, ending.y - 2)],
    }
    if leg:
        colour = P2 if leg in ("challenge", "up", "run3", "end") else P1
        x, y = along(paths[leg], p)
        packet(c, x, y, colour)


export(draw, __file__, preset="hd", seconds=10, fps=20, seamless=True, poster=0.6)
