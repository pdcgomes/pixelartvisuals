"""8.2 Who talks to whom: the two players' browsers, the Vercel functions (the matchmaker, the ICE servers'
function, the ranked services) with the key-value store they keep their state in, and on Cloudflare the TURN
relay and the tournament room. The matchmaker hears one offer and one answer; after that the two browsers
send each other their inputs directly, or through the relay when their networks can't connect. Ranked runs
and matches go to Vercel; a tournament night is one socket a game to the room. The only line between the
two clouds is the ICE function asking Cloudflare for the relay's short-lived credentials; the room calls
no other service.

Animated as a loop: your browser asks for its ICE servers and leaves its offer with the matchmaker, your
friend's leaves its answer, inputs go back and forth between the two browsers, then once through the relay,
then a ranked run goes to the ranked services and on to the store, then both browsers talk to the room.
Each service lights as its message arrives.

Numbers and facts, from alfamafighterturbo at 74e2f64:
- signalling once, rooms of ten minutes, inputs peer to peer at 60 packets a second each way, about
  2.5 kB/s; STUN, and Cloudflare's TURN with credentials that last 12 hours, from /api/ice
  (docs/plans/2026-10-07-network-play-design.md, "Architecture" and "The relay (TURN)");
- the matchmaker and the ranked services are Vercel functions over Upstash's key-value store
  (the same, and docs/plans/2026-10-10-leaderboards-design.md, 3.3 and 2.2's As built);
- the room is a Cloudflare Worker with a Durable Object for each group's link, one WebSocket a game for
  the night, calling no other service and sharing no secret with Vercel
  (docs/plans/2026-10-10-tournaments-design.md, 13 and 13.1).
"""

from pixelkit import ease_in_out, phase
from series import ENGINE, NET, along, export, frame, packet

ICE_W = (0.02, 0.09)
ICE_BACK = (0.09, 0.15)
OFFER = (0.17, 0.27)
ANSWER = (0.28, 0.38)
P2P = (0.40, 0.56)
RELAY = (0.58, 0.68)
RANKED = (0.70, 0.78)
STORE = (0.78, 0.84)
ROOM = (0.86, 0.97)


def draw(c, t):
    top, bottom = frame(c, 8, 2, "WHO TALKS TO WHOM",
                        "PEER TO PEER MEANS BROWSER TO BROWSER. THE ROOM IS A SMALL PROGRAM RUN BY CLOUDFLARE, WITH A "
                        "LITTLE SERVER OF ITS OWN FOR EACH GROUP OF FRIENDS.")
    lit = set()

    def arrived(name, window, tail=0.04):
        if window[1] - (window[1] - window[0]) * 0.15 <= t < window[1] + tail:
            lit.add(name)

    arrived("ICE", ICE_W)
    arrived("YOU", ICE_BACK)
    arrived("MATCHMAKER", OFFER)
    arrived("MATCHMAKER", ANSWER)
    arrived("TURN", (RELAY[0], (RELAY[0] + RELAY[1]) / 2))
    arrived("FRIEND", RELAY)
    arrived("RANKED", RANKED)
    arrived("STORE", STORE)
    arrived("ROOM", ROOM)

    def node(x, y, w, key, title, accent, sub):
        on = key in lit
        return c.node(x, y, w, 19, title, color="white" if on else accent, sub=sub, border="white" if on else "line")

    def boundary(x, y, w, h, label, colour):
        for bx, by, n, vertical in ((x, y, w, False), (x, y + h - 1, w, False), (x, y, h, True),
                                    (x + w - 1, y, h, True)):
            c.dashes(bx, by, n, colour, vertical=vertical)
        c.text(x + 5, y + 4, label, c.light(colour))

    box_y, box_h = top + 13, 166
    boundary(4, box_y, 150, box_h, "VERCEL FUNCTIONS", "muted")
    boundary(326, box_y, 150, box_h, "CLOUDFLARE", "muted")

    ice = node(13, box_y + 14, 133, "ICE", "CONNECTION HELP", NET, "WAYS TO CONNECT, RELAY LOGIN")
    match = node(13, box_y + 44, 133, "MATCHMAKER", "MATCHMAKER", NET, "AN OFFER KEPT UNDER A CODE")
    ranked = node(13, box_y + 74, 133, "RANKED", "RANKED SERVICES", NET, "NAMES · RUNS · MATCHES · BOARDS")
    store = node(13, box_y + 136, 133, "STORE", "THE STORE", "muted", "THE SITE'S DATABASE")
    turn = node(335, box_y + 14, 133, "TURN", "TURN RELAY", NET, "WHEN NETWORKS WON'T CONNECT")
    room = node(335, box_y + 74, 133, "ROOM", "TOURNAMENT ROOM", NET, "A SMALL SERVER FOR EACH GROUP")
    c.paragraph(335, room.y2 + 5, "CALLS NO OTHER SERVICE, SHARES NO SECRET WITH VERCEL", 133, "dim")

    you = node(176, box_y + 34, 128, "YOU", "YOUR BROWSER", ENGINE, "PLAYS THE WHOLE MATCH")
    friend = node(176, box_y + 118, 128, "FRIEND", "YOUR FRIEND'S BROWSER", ENGINE, "PLAYS IT TOO")

    # The store under every Vercel function.
    sx = 9
    c.vline(sx, ice.cy, store.cy - ice.cy, "dim")
    for n in (ice, match, ranked):
        c.hline(sx, n.cy, n.x - sx, "dim")
    c.arrow(sx, store.cy, store.x - 1, store.cy, "dim")
    c.text(sx + 5, ranked.y2 + 6, "ALL THREE USE THE STORE", "dim")

    # The rails the browsers reach the clouds by: HTTPS to Vercel, the relay and the room's socket to Cloudflare.
    lx, rx = 163, 317
    c.rect(lx, ice.cy, 2, friend.cy - ice.cy + 1, "line")
    c.rect(rx - 1, turn.cy, 2, friend.cy - turn.cy + 1, "line")
    for n in (ice, match, ranked):
        c.arrow(lx - 1, n.cy, n.x2, n.cy, "white")
    for n in (turn, room):
        c.arrow(rx - 1, n.cy, n.x - 1, n.cy, "white")
    for b in (you, friend):
        c.hline(lx + 2, b.cy, b.x - lx - 2, "white")
        c.hline(b.x2, b.cy, rx - 1 - b.x2, "white")
    c.text(lx + 4, you.y - 8, "WEB", "dim")
    c.text(rx - 3, you.y - 8, "RELAY · ROOM", "dim", align="right")

    # Inputs, peer to peer.
    px = you.cx
    c.rect(px, you.y2 + 1, 2, friend.y - you.y2 - 2, c.light(NET))
    c.text(px + 5, you.y2 + 9, "INPUTS ONLY,", "white")
    c.text(px + 5, you.y2 + 16, "PEER TO PEER", "white")
    c.text(px + 5, you.y2 + 26, "ABOUT 2.5 KB/S", c.light(NET))
    c.text(px + 5, you.y2 + 33, "EACH WAY", c.light(NET))
    c.text(px - 4, you.y2 + 9, "AFTER ONE", "dim", align="right")
    c.text(px - 4, you.y2 + 16, "OFFER AND", "dim", align="right")
    c.text(px - 4, you.y2 + 23, "ONE ANSWER", "dim", align="right")

    # The one line between the clouds: the ICE function asks Cloudflare for the relay's credentials.
    over = box_y - 4
    pts = [(ice.cx, ice.y - 1), (ice.cx, over), (turn.cx, over), (turn.cx, turn.y - 2)]
    c.polyline(pts[:-1], "dim")
    c.arrow(turn.cx, over, turn.cx, turn.y - 1, "dim", dotted=True)
    c.text(240, box_y + 1, "RELAY LOGINS, 12 HOURS:", "dim", align="center")
    c.text(240, box_y + 8, "THE ONLY LINK BETWEEN THE TWO", "dim", align="center")

    # The messages of one evening, in turn.
    def go(points, window, colour="white"):
        p = phase(t, *window)
        if 0 < p < 1:
            x, y = along(points, ease_in_out(p))
            packet(c, x, y, colour)

    def to_left(b, n):
        return [(b.x - 2, b.cy), (lx + 1, b.cy), (lx + 1, n.cy), (n.x2 + 2, n.cy)]

    def to_right(b, n):
        return [(b.x2 + 1, b.cy), (rx, b.cy), (rx, n.cy), (n.x - 3, n.cy)]

    go(to_left(you, ice), ICE_W)
    go(to_left(you, ice)[::-1], ICE_BACK, c.light(NET))
    go(to_left(you, match), OFFER)
    go(to_left(friend, match), ANSWER)
    for k in range(3):
        a = P2P[0] + k * 0.05
        go([(px + 1, you.y2 + 3), (px + 1, friend.y - 4)], (a, a + 0.06), c.light(NET))
        go([(px + 1, friend.y - 4), (px + 1, you.y2 + 3)], (a + 0.02, a + 0.08), c.light(NET))
    go(to_right(you, turn) + to_right(friend, turn)[::-1][1:], RELAY, c.light(NET))
    go(to_left(you, ranked), RANKED, "white")
    go([(ranked.x - 2, ranked.cy), (sx, ranked.cy), (sx, store.cy), (store.x - 3, store.cy)], STORE, "dim")
    go(to_right(you, room), ROOM, "white")
    go(to_right(friend, room), (ROOM[0] + 0.02, ROOM[1]), "white")

    # What each line is for.
    notes = c.panel(4, box_y + box_h + 3, 472, bottom - box_y - box_h - 5, "WHO HEARS WHAT", color="white",
                    sub="ONE EVENING")
    lines = [
        ("white", "1", "THE MATCHMAKER HOLDS ONE OFFER AND ONE ANSWER UNDER A SIX-CHARACTER CODE, THEN HEARS NOTHING MORE"),
        ("white", "2", "THE TWO BROWSERS SEND EACH OTHER THEIR INPUTS: DIRECTLY, OR THROUGH THE RELAY"),
        ("white", "3", "RANKED RUNS AND MATCHES GO TO VERCEL, STAMPED WITH A KEY ONLY THAT DEVICE HOLDS"),
        ("white", "4", "ON A TOURNAMENT NIGHT EACH GAME STAYS LINKED TO THE ROOM, WHICH SENDS EVERY MATCH'S INPUTS TO THOSE WATCHING"),
    ]
    for i, (accent, n, line) in enumerate(lines):
        y = notes.y + 1 + i * 9
        c.text(notes.x, y, n, accent)
        c.text(notes.x + 8, y, line, "text")


export(draw, __file__, preset="hd", seconds=9, fps=20, seamless=True, poster=0.45)
