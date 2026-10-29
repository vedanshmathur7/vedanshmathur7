"""assets/arch-{dark,light}.svg — DataVox-style query path, high level and generic.

Nothing here is proprietary: it is the textbook shape of an async
NL -> SQL -> chart pipeline on the stack listed in the profile.
Packets are SMIL <animateMotion> (works inside <img>); reduced-motion hides them.
"""
from svgkit import THEMES, T, document, esc, write

W, H = 860, 404
NH = 56

# id: (x, y, w, title, sub)
NODES = {
    "client":   (20, 48, 120, "client", "nl question"),
    "gateway":  (180, 48, 140, "api gateway", "fastapi · async"),
    "broker":   (360, 48, 124, "broker", "rabbitmq"),
    "workers":  (524, 48, 136, "workers", "celery pool"),
    "vllm":     (704, 48, 132, "vllm", "self-hosted"),
    "bedrock":  (704, 184, 132, "bedrock", "managed models"),
    "sql":      (524, 184, 136, "sql engine", "validate · execute"),
    "renderer": (360, 184, 124, "renderer", "charts · insights"),
    "mongodb":  (20, 184, 120, "mongodb", "state · history"),
    "redis":    (180, 316, 140, "redis", "cache · results"),
}

# (path d, kind) kind: main | both | state
EDGES = [
    ("M140 64H180", "main"),                 # 1 request
    ("M320 76H360", "main"),                 # 2 enqueue
    ("M484 76H524", "main"),                 # 3 consume
    ("M660 68H704", "both"),                 # 4 infer (vllm)
    ("M660 92H682V212H704", "both"),         # 4' infer (bedrock)
    ("M592 104V184", "main"),                # 5 execute
    ("M524 212H484", "main"),                # 6 rows -> spec
    ("M360 212H290V104", "main"),            # 7 render -> gateway
    ("M180 88H140", "main"),                 # 8 respond
    ("M200 104V212H140", "state"),           # state
    ("M240 104V316", "state"),               # cache
]

CALLOUTS = [(1, 160, 50), (2, 340, 60), (3, 504, 60), (4, 682, 52),
            (5, 608, 144), (6, 504, 196), (7, 322, 196), (8, 160, 104)]
LEGEND = ["POST /query", "enqueue task", "consume", "nl -> sql (llm)",
          "execute", "rows -> chart spec", "render", "respond"]

# packet routes through node centres (packets sit under the nodes = 'processing')
ROUTE_VLLM = ("M80 64H250V76H592V68H770H592V76V212H422H290V88H80")
ROUTE_BEDROCK = ("M80 64H250V76H592V92H682V212H770H682V92H592V212H422H290V88H80")
PINGS = [("M240 76V344", 2.6, 0.4), ("M200 76V212H80", 3.1, 1.7)]


def path_len(d: str) -> float:
    """Length of an M/H/V-only path."""
    import re
    toks = re.findall(r"[MHV]|-?\d+(?:\.\d+)?", d)
    x = y = 0.0
    total = 0.0
    cmd = None
    i = 0
    while i < len(toks):
        tk = toks[i]
        if tk in "MHV":
            cmd = tk
            i += 1
            continue
        if cmd == "M":
            x, y = float(toks[i]), float(toks[i + 1])
            i += 2
            cmd = "L?"
        elif cmd == "H":
            nx = float(tk); total += abs(nx - x); x = nx; i += 1
        elif cmd == "V":
            ny = float(tk); total += abs(ny - y); y = ny; i += 1
        else:
            i += 1
    return total


def build(mode: str) -> str:
    t = THEMES[mode]
    dark = mode == "dark"
    o = [f'<rect width="{W}" height="{H}" rx="6" fill="{t["bg"]}"/>']
    o.append("<defs>")
    o.append(f'<marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
             f'<path d="M0 .8L7 4L0 7.2z" fill="{t["dim"]}"/></marker>')
    if dark:
        o.append('<radialGradient id="pg"><stop offset="0" stop-color="#B6FF3B" stop-opacity=".55"/>'
                 '<stop offset="1" stop-color="#B6FF3B" stop-opacity="0"/></radialGradient>')
    o.append('<pattern id="g1" width="10" height="10" patternUnits="userSpaceOnUse">'
             f'<path d="M10 0H0V10" fill="none" stroke="{t["grid"]}" stroke-width=".6"/></pattern>')
    o.append("</defs>")
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="6" fill="url(#g1)" opacity="{.55 if dark else 1}"/>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="none" stroke="{t["line"]}"/>')

    # llm tier boundary
    o.append(f'<rect x="692" y="22" width="156" height="230" rx="3" fill="none" stroke="{t["dim"]}" '
             f'stroke-dasharray="4 4" opacity=".8"/>')
    o.append(T(702, 39, "llm tier · routed", fill=t["dim"], size=10.5))

    # edges
    stroke = t["dim"]
    for i, (d, kind) in enumerate(EDGES):
        L = path_len(d)
        dash = ' stroke-dasharray="3 4"' if kind == "state" else ""
        m_end = ' marker-end="url(#ah)"'
        m_start = ' marker-start="url(#ah)"' if kind in ("both", "state") else ""
        cls = "e" if kind != "state" else "e es"
        o.append(f'<path class="{cls}" style="--len:{L:.0f};animation-delay:{0.15 + i*0.08:.2f}s" d="{d}" fill="none" '
                 f'stroke="{stroke}" stroke-width="1.25"{dash}{m_end}{m_start}/>')
    o.append(T(232, 288, "cache", fill=t["dim"], size=10.5, anchor="end"))
    o.append(T(170, 205, "state", fill=t["dim"], size=10.5, anchor="middle"))

    # packets (under nodes)
    pk = []
    for route, dur, begins in ((ROUTE_VLLM, 7.0, (0, 3.5)), (ROUTE_BEDROCK, 8.4, (1.75, 5.95))):
        for b in begins:
            halo = (f'<circle r="9" fill="url(#pg)"/>' if dark else "")
            pk.append(f'<g class="pk rm-hide" opacity="0">{halo}<circle r="3.2" fill="{t["accent"]}"/>'
                      f'<animateMotion dur="{dur}s" begin="{1.6 + b}s" repeatCount="indefinite" path="{route}"/>'
                      f'<set attributeName="opacity" to="1" begin="{1.6 + b}s"/></g>')
    for route, dur, b in PINGS:
        pk.append(f'<g class="pk rm-hide" opacity="0"><circle r="2.4" fill="{t["accent"]}" opacity=".7"/>'
                  f'<animateMotion dur="{dur}s" begin="{1.6 + b}s" repeatCount="indefinite" '
                  f'keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear" path="{route}"/>'
                  f'<set attributeName="opacity" to="1" begin="{1.6 + b}s"/></g>')
    o.extend(pk)

    # nodes
    for i, (nid, (x, y, w, title, sub)) in enumerate(NODES.items()):
        g = [f'<g class="n" style="animation-delay:{0.05 + i*0.06:.2f}s">']
        g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{NH}" rx="3" fill="{t["panel"]}" stroke="{t["text"] if not dark else t["dim"]}" stroke-width="{1 if dark else .9}"/>')
        g.append(f'<path d="M{x} {y+6}V{y}H{x+6}" fill="none" stroke="{t["accent"]}" stroke-width="1.5"/>')
        g.append(T(x + 12, y + 24, title, fill=t["text"], size=13.5, extra='font-weight="600"'))
        g.append(T(x + 12, y + 42, sub, fill=t["dim"], size=11))
        g.append(T(x + w - 8, y + 14, f"n{i+1:02d}", fill=t["mute"] if dark else t["dim"], size=8.5, anchor="end"))
        g.append("</g>")
        o.append("".join(g))

    # callouts
    for num, cx, cy in CALLOUTS:
        o.append(f'<g class="co"><circle cx="{cx}" cy="{cy}" r="7.5" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="1.2"/>'
                 f'{T(cx, cy + 3.6, str(num), fill=t["accent"], size=10, anchor="middle", extra="font-weight=\"700\"")}</g>')

    # title block
    bx, by, bw, bh = 360, 278, 480, 112
    tb = [f'<g class="tb"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{t["bg"]}" stroke="{t["dim"]}"/>',
          f'<path d="M{bx} {by+24}H{bx+bw}M{bx} {by+bh-22}H{bx+bw}M{bx+bw-120} {by}V{by+24}" stroke="{t["dim"]}" stroke-width=".8"/>',
          T(bx + 10, by + 16, "fig.1  datavox-style query path", fill=t["text"], size=11.5, extra='font-weight="600"'),
          T(bx + bw - 110, by + 16, "scale: n.t.s.", fill=t["dim"], size=11)]
    for k, lab in enumerate(LEGEND):
        col, row = divmod(k, 4)
        lx, ly = bx + 12 + col * 235, by + 41 + row * 14.5
        tb.append(T(lx, ly, f"{k+1}", fill=t["accent"], size=10.5, extra='font-weight="700"'))
        tb.append(T(lx + 16, ly, lab, fill=t["dim"] if dark else t["text"], size=10.5))
    tb.append(f'<circle cx="{bx+16}" cy="{by+bh-11}" r="3" fill="{t["accent"]}"/>')
    tb.append(T(bx + 26, by + bh - 7.5, "message in flight", fill=t["dim"], size=10))
    tb.append(f'<path d="M{bx+148} {by+bh-11}h22" stroke="{t["dim"]}" stroke-width="1.25" stroke-dasharray="3 4"/>')
    tb.append(T(bx + 178, by + bh - 7.5, "state / cache", fill=t["dim"], size=10))
    tb.append(T(bx + bw - 10, by + bh - 7.5, "illustrative · not prod", fill=t["dim"], size=10, anchor="end"))
    tb.append("</g>")
    o.append("".join(tb))

    css = (".e{stroke-dasharray:var(--len);animation:draw .7s ease-out both}"
           ".es{stroke-dasharray:3 4;animation:on .6s both}"
           ".n{animation:up .4s ease-out both}"
           ".co{animation:on .4s 1.2s both}.tb{animation:on .5s 1.3s both}")
    return document(
        W, H, "".join(o), theme=t, fonts=("mono", "mono6", "mono7"), css=css,
        title="System diagram: natural-language query path (DataVox-style, high level)",
        desc=("Client sends a natural-language question to a FastAPI gateway, which enqueues a task on RabbitMQ. "
              "Celery workers consume it, call an LLM tier (self-hosted vLLM or managed AWS Bedrock) to turn the "
              "question into SQL, execute it on the SQL engine, and a renderer turns rows into charts and insights "
              "that return through the gateway. Redis caches results; MongoDB holds state and history. "
              "Illustrative and generic, not the production topology."),
    )


def main():
    for m in ("dark", "light"):
        write(f"arch-{m}.svg", build(m))


if __name__ == "__main__":
    main()
