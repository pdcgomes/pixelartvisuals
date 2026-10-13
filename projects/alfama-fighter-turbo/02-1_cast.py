"""2.1 The cast: Pedro, the director, at the top; the producer below him as the one line between him
and the studio; and the ten roles the producer briefs, in five columns, each with who reviews its work.
Animated, a seamless loop: a request goes from Pedro to the producer, a brief goes down to the
animators, their work goes up to the art director's check against the art bible, and the report comes
back up through the producer to Pedro, each node lighting as it passes; the six steps beside the top
light in turn. The reviewers are the studio plan's; in practice the leads' reviews were checks against
the bibles and the producer looked at every lane's previews itself (studio-model.md, The cast and Quality).

Numbers and sources (alfamafighterturbo at 74e2f64):
- The roles and who reviews each: docs/plans/2026-10-05-studio-design.md, Roles table (also
  docs/studio/studio-model.md, The cast). The animators answer to the art director for the look and
  the game director for the timing.
- "Talks only to the producer" and what each owns: docs/studio/studio-model.md, The cast.
- 17 of the 31 role agents on the board of 8 October played two or three roles: AGENT_CHATS in
  docs/studio/board.canvas.tsx (the 32 entries less the producer's own chat).
- The artist who drew Camões went on to Adamastor and O Calceteiro: docs/studio/studio-model.md, The cast.
"""

from pixelkit import ease_in_out, phase
from series import ART, AUDIO, DIRECTOR, ENGINE, PRODUCER, QA, along, export, frame, packet

DESIGN = "orange"
COLUMNS = [
    # accent, [(role, who reviews it)], the lead's index or None
    (DESIGN, [("GAME DIRECTOR", "PEDRO"), ("WRITER", "GAME DIRECTOR, PEDRO")]),
    (ART, [("ART DIRECTOR", "PEDRO"), ("CHARACTER ARTISTS", "ART DIRECTOR"), ("ANIMATORS", "ART AND GAME DIRECTORS"),
           ("BACKGROUND ARTISTS", "ART DIRECTOR")]),
    (AUDIO, [("COMPOSER", "PRODUCER, PEDRO"), ("SOUND DESIGNER", "PRODUCER")]),
    (ENGINE, [("ENGINE PROGRAMMER", "QA")]),
    (QA, [("QA", "PRODUCER")]),
]
STEPS = [
    "PEDRO ASKS FOR SOMETHING",
    "THE PRODUCER WRITES THE BRIEF",
    "THE ANIMATORS DRAW IT IN THEIR LANE",
    "IT'S CHECKED AGAINST THE ART BIBLE",
    "THE PRODUCER LOOKS AT IT AND MERGES IT",
    "PEDRO PLAYS IT AND DECIDES",
]
# The loop's windows: each step's span of t, and the packet's legs.
WINDOWS = [(0.0, 0.14), (0.14, 0.36), (0.36, 0.5), (0.5, 0.64), (0.64, 0.84), (0.84, 1.0)]
ASK, BRIEF, REVIEW, BACK, UP = (0.03, 0.12), (0.17, 0.34), (0.51, 0.58), (0.65, 0.8), (0.85, 0.92)
WEIGHTS = [96, 112, 80, 92, 56]
NODE_H, NODE_GAP = 19, 9


def draw(c, t):
    top, bottom = frame(c, 2, 1, "WHO DOES WHAT IN THE STUDIO",
                        "ROLES AND REVIEWERS FROM THE STUDIO PLAN, 5 OCTOBER; ROLES PER AGENT FROM THE BOARD, 8 OCTOBER.")
    step = next(i for i, (a, b) in enumerate(WINDOWS) if a <= t < b) if t < 1 else 5
    lit = {0: {"PEDRO"}, 1: {"PRODUCER"}, 2: {"ANIMATORS"}, 3: {"ART DIRECTOR"}, 4: {"PRODUCER"}, 5: {"PEDRO"}}[step]

    def node(x, y, w, title, accent, sub):
        on = title in lit
        return c.node(x, y, w, NODE_H, title, color="white" if on else accent, sub=sub,
                      border="white" if on else "line")

    # Pedro and the producer, centred, with what each owns to the left and the six steps to the right.
    mid_w, mid_x = 132, 174
    pedro = node(mid_x, top + 4, mid_w, "PEDRO", DIRECTOR, "THE DIRECTOR · A PERSON")
    producer = node(mid_x, pedro.y2 + 12, mid_w, "PRODUCER", PRODUCER, "AN AGENT · REVIEWED BY PEDRO")
    c.vline(pedro.cx, pedro.y2, producer.y - pedro.y2, "white")
    c.paragraph(8, pedro.y + 1, "TALKS ONLY TO THE PRODUCER. DECIDES WHAT ONLY TASTE CAN: WHICH DESIGN "
                "WINS, WHETHER A MILESTONE PASSES", mid_x - 16, c.light(DIRECTOR))
    c.paragraph(8, producer.y + 1, "PLANS, BRIEFS, REVIEWS AND MERGES, AND MAKES EVERY CALL THAT CAN BE "
                "UNDONE, IS TECHNICAL OR FOLLOWS FROM THE BIBLES", mid_x - 16, c.light(PRODUCER))
    sx = pedro.x2 + 10
    for i, s in enumerate(STEPS):
        on = i == step
        c.text(sx, pedro.y + 1 + i * 8, str(i + 1), "white" if on else "muted")
        c.text(sx + 8, pedro.y + 1 + i * 8, s, "white" if on else "dim")

    # The rail every brief and report travels along, and the five columns hanging from it.
    rail = producer.y2 + 9
    c.text(c.w - 8, rail - 7, "UNDER EACH ROLE: WHO REVIEWS ITS WORK", "dim", align="right")
    xs = []
    x = 8
    total = c.w - 16 - 4 * 3
    widths = [round(total * w / sum(WEIGHTS)) for w in WEIGHTS]
    widths[-1] = total - sum(widths[:-1])
    nodes = {}
    spines = {}
    for (accent, roles), w in zip(COLUMNS, widths):
        spine = x + 1
        nx, nw = x + 6, w - 11
        y = rail + 9
        col = []
        for title, sub in roles:
            r = node(nx, y, nw, title, accent, sub)
            nodes[title] = r
            col.append(r)
            y += NODE_H + NODE_GAP
        c.vline(spine, rail, col[-1].cy - rail + 1, "line")
        for r in col:
            c.arrow(spine, r.cy, r.x - 1, r.cy, "line")
            spines[r] = spine
        if len(col) > 1 and accent in (ART, DESIGN):
            rx = nx + nw + 2
            lead = col[0]
            c.vdots(rx, lead.cy, col[-1].cy - lead.cy + 1, c.dark(accent))
            for r in col:
                c.hline(r.x2, r.cy, rx - r.x2, c.dark(accent))
        xs.append((x, w))
        x += w + 3
    c.hline(xs[0][0] + 1, rail, xs[-1][0] - xs[0][0] + 1, "line")
    c.vline(producer.cx, producer.y2, rail - producer.y2, "line")
    qa, eng = nodes["QA"], nodes["ENGINE PROGRAMMER"]
    c.arrow(qa.x - 4, qa.cy + 4, eng.x2 + 1, qa.cy + 4, c.dark(QA), dotted=True)

    # One agent, several roles.
    note_y = nodes["BACKGROUND ARTISTS"].y2 + 6
    note = c.panel(0, note_y, c.w, bottom - note_y - 2, "ONE AGENT, SEVERAL ROLES", color="white",
                   sub="A LANE OFTEN NEEDED TWO OR THREE")
    c.text(note.x, note.y, "17", c.light(ART), font="large", shadow="line")
    c.paragraph(note.x + 16, note.y, "OF THE 31 AGENTS ON THE BOARD AT 18:30 ON 8 OCTOBER PLAYED MORE THAN ONE ROLE: "
                "CHARACTER ARTIST, ANIMATOR AND ENGINE PROGRAMMER FOR ONE FIGHTER END TO END", 212, "text")
    c.paragraph(note.x + 240, note.y, "AGENTS WERE RESUMED FOR MORE WORK IN THEIR OWN AREA: THE ARTIST WHO DREW "
                "CAMÕES WENT ON TO DRAW ADAMASTOR AND O CALCETEIRO", note.w - 240, "text")

    # The message on its way.
    paths = {
        ASK: ([(pedro.cx, pedro.y2), (producer.cx, producer.y - 1)], c.light(DIRECTOR)),
        BRIEF: ([(producer.cx, producer.y2), (producer.cx, rail), (spines[nodes["ANIMATORS"]], rail),
                 (spines[nodes["ANIMATORS"]], nodes["ANIMATORS"].cy), (nodes["ANIMATORS"].x - 2, nodes["ANIMATORS"].cy)],
                c.light(PRODUCER)),
        REVIEW: ([(nodes["ANIMATORS"].x2 + 2, nodes["ANIMATORS"].cy), (nodes["ART DIRECTOR"].x2 + 2, nodes["ART DIRECTOR"].cy)],
                 c.light(ART)),
        BACK: ([(spines[nodes["ART DIRECTOR"]], nodes["ART DIRECTOR"].cy), (spines[nodes["ART DIRECTOR"]], rail),
                (producer.cx, rail), (producer.cx, producer.y2)], c.light(ART)),
        UP: ([(producer.cx, producer.y - 1), (pedro.cx, pedro.y2)], c.light(PRODUCER)),
    }
    for (a, b), (pts, colour) in paths.items():
        if a <= t < b:
            if (a, b) == REVIEW:
                x0 = pts[0][0]
                y = round(pts[0][1] + (pts[1][1] - pts[0][1]) * ease_in_out(phase(t, a, b)))
                packet(c, x0, y, colour)
            else:
                packet(c, *along(pts, ease_in_out(phase(t, a, b))), colour)


export(draw, __file__, preset="hd", seconds=7, fps=20, seamless=True, poster=0.9)
