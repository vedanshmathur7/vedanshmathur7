"""assets/hero-{dark,light}.svg — boot log -> void finalize(); -> name.

Timeline (s):  0.0 CRT power-on line · 0.35-2.6 boot log + modules [ OK ]
               3.1 log collapses · 3.7 name resolves (glitch settle)
               4.7 'finalizing voids.' types · 5.2-5.9 ruler, facts, exit 0
Then holds the final frame; only the cursor keeps blinking.
"""
from svgkit import THEMES, T, document, esc, mono_w, text_path, write

W, H = 900, 320
X0 = 36

BOOT = [
    ("0.000000", "finalize: booting vedansh-6.1.0 (b.tech cse, bmu, class of 2028)"),
    ("0.004096", "cmdline: root=/dev/gurugram ro quiet tz=Asia/Kolkata"),
    ("0.012288", "cpu0: systems-minded, tuned for low-end machines"),
    ("0.020480", "mem: 0x0000-0x5fff mapped, see stack linker map below"),
]
MODULES = ["fastapi", "celery", "rabbitmq", "redis", "mongodb", "vllm", "bedrock", "cpp_core"]
TAGLINE = "finalizing voids."
FACTS = ["sde intern @ witting ai", "ai infra / llm systems", "c++ on low-end machines", "gurugram, in"]


def build(mode: str) -> str:
    t = THEMES[mode]
    dark = mode == "dark"
    o = []

    # ---- background
    o.append(f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>')
    o.append("<defs>")
    if dark:
        o.append('<pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">'
                 f'<rect width="4" height="1" fill="{t["text"]}" opacity=".028"/></pattern>'
                 '<radialGradient id="vig" cx="50%" cy="50%" r="75%">'
                 '<stop offset="60%" stop-color="#000" stop-opacity="0"/>'
                 '<stop offset="100%" stop-color="#000" stop-opacity=".55"/></radialGradient>'
                 '<filter id="glow" x="-10%" y="-40%" width="120%" height="180%">'
                 '<feGaussianBlur stdDeviation="5" result="b"/>'
                 '<feComponentTransfer in="b" result="g"><feFuncA type="linear" slope=".38"/></feComponentTransfer>'
                 '<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    else:
        o.append('<pattern id="g1" width="12" height="12" patternUnits="userSpaceOnUse">'
                 f'<path d="M12 0H0V12" fill="none" stroke="{t["grid"]}" stroke-width=".6"/></pattern>'
                 '<pattern id="g2" width="60" height="60" patternUnits="userSpaceOnUse">'
                 f'<rect width="60" height="60" fill="url(#g1)"/><path d="M60 0H0V60" fill="none" stroke="{t["line"]}" stroke-width=".6" opacity=".55"/></pattern>')
    o.append("</defs>")
    if not dark:
        o.append(f'<rect width="{W}" height="{H}" fill="url(#g2)"/>')

    # ---- frame: corner brackets + header labels
    c, L = 12, 16
    for (x, y, dx, dy) in [(c, c, 1, 1), (W - c, c, -1, 1), (c, H - c, 1, -1), (W - c, H - c, -1, -1)]:
        o.append(f'<path d="M{x} {y + dy * L}V{y}H{x + dx * L}" fill="none" stroke="{t["dim"]}" stroke-width="1"/>')
    o.append(T(X0, 34, "tty0  /usr/bin/finalize", fill=t["dim"], size=11))
    o.append(T(W - X0, 34, "vedanshmathur7@github", fill=t["dim"], size=11, anchor="end"))

    # ---- boot log
    lh, y0, fs = 16.6, 60, 12
    lines = []
    for ts, msg in BOOT:
        lines.append(f'<tspan fill="{t["dim"]}">[{ts:>12}]</tspan> {esc(msg)}')
    for m in MODULES:
        lines.append(f'<tspan fill="{t["dim"]}">[</tspan><tspan fill="{t["accent"]}">  OK  </tspan>'
                     f'<tspan fill="{t["dim"]}">]</tspan> loaded <tspan fill="{t["text"]}">{m}.ko</tspan>')
    lines.append(f'<tspan fill="{t["dim"]}">[</tspan><tspan fill="{t["accent"]}">  OK  </tspan>'
                 f'<tspan fill="{t["dim"]}">]</tspan> reached target <tspan fill="{t["text"]}">datavox.service</tspan>')
    lines.append(f'<tspan fill="{t["accent"]}">$</tspan> ./init --exec <tspan fill="{t["text"]}">\'void finalize();\'</tspan>')
    o.append('<g id="log" class="rm-hide">')
    for i, ln in enumerate(lines):
        delay = 0.35 + 0.16 * i if i < len(lines) - 1 else 2.62
        o.append(f'<text class="ln" style="animation-delay:{delay:.2f}s" x="{X0}" y="{y0 + i * lh:.1f}" '
                 f'font-size="{fs}" fill="{t["dim"] if dark else t["text"]}" xml:space="preserve">{ln}</text>')
    o.append("</g>")

    # ---- CRT beams (power-on + collapse)
    o.append(f'<rect class="beam b1 rm-hide" x="0" y="{H/2 - 1}" width="{W}" height="2" fill="{t["accent"]}"/>')
    o.append(f'<rect class="beam b2 rm-hide" x="0" y="{H/2 - 1}" width="{W}" height="2" fill="{t["accent"]}"/>')

    # ---- final frame
    o.append(f'<text class="rem" x="{X0}" y="98" font-size="13" fill="{t["dim"]}" xml:space="preserve">'
             f'<tspan fill="{t["accent"]}">&gt;</tspan> void finalize();   '
             f'<tspan fill="{t["mute"]}">// returned </tspan><tspan fill="{t["accent"]}">0</tspan></text>')

    name_d = text_path("VEDANSH MATHUR", "disp", 76, X0 - 3, 170, tracking=-1.5)
    o.append(f'<defs><path id="nm" d="{name_d}"/></defs>')
    o.append(f'<use href="#nm" xlink:href="#nm" class="gA rm-hide" fill="{t["accent"]}"/>')
    o.append(f'<use href="#nm" xlink:href="#nm" class="gB rm-hide" fill="{t["dim"]}"/>')
    glow = ' filter="url(#glow)"' if dark else ""
    o.append(f'<g class="name"{glow}><use href="#nm" xlink:href="#nm" fill="{t["text"]}"/></g>')

    # tagline, one <text> per glyph so each can 'type' in
    tx, ty, tfs = X0, 210, 21
    cw = tfs * 0.6
    for i, ch in enumerate(TAGLINE):
        if ch == " ":
            continue
        o.append(f'<text class="ch" style="animation-delay:{4.7 + 0.055 * i:.3f}s" x="{tx + i * cw:.1f}" '
                 f'y="{ty}" font-size="{tfs}" font-weight="500" fill="{t["text"]}">{esc(ch)}</text>')
    o.append(f'<rect class="cur" x="{tx + len(TAGLINE) * cw + 4:.1f}" y="{ty - 17}" width="11" height="21" fill="{t["accent"]}"/>')

    # ruler + facts
    ry = 248
    ticks = "".join(f"M{x} {ry}v{5 if (x - X0) % 96 else 9}" for x in range(X0, W - X0 + 1, 12))
    o.append(f'<g class="ruler"><path d="M{X0} {ry}H{W - X0}" stroke="{t["line"] if dark else t["dim"]}" stroke-width="1"/>'
             f'<path d="{ticks}" stroke="{t["line"] if dark else t["mute"]}" stroke-width="1"/></g>')
    fx = X0
    facts = []
    for i, f in enumerate(FACTS):
        if i:
            facts.append(T(fx + 9, 284, "/", fill=t["mute"], size=12.5))
            fx += 26
        facts.append(T(fx, 284, f, fill=t["dim"] if dark else t["dim"], size=12.5))
        fx += mono_w(f, 12.5)
    o.append(f'<g class="facts">{"".join(facts)}</g>')
    o.append(f'<g class="exit">{T(W - X0, 284, "[ exit 0 ]", fill=t["accent"], size=12.5, anchor="end")}</g>')

    if dark:
        o.append(f'<rect width="{W}" height="{H}" fill="url(#scan)" pointer-events="none"/>')
        o.append(f'<rect width="{W}" height="{H}" fill="url(#vig)" pointer-events="none"/>')

    css = f"""
.ln{{opacity:0;animation:on 1ms linear both}}
#log{{transform-origin:{W/2}px {H/2}px;animation:collapse .45s cubic-bezier(.7,0,.9,.4) 3.1s both}}
@keyframes collapse{{0%{{transform:scaleY(1);opacity:1}}85%{{transform:scaleY(.004);opacity:1}}100%{{transform:scaleY(.004);opacity:0}}}}
.beam{{opacity:0;transform-origin:{W/2}px {H/2}px}}
.b1{{animation:pwr .45s ease-out 0s both}}
.b2{{animation:pwr2 .4s ease-in 3.5s both}}
@keyframes pwr{{0%{{opacity:1;transform:scaleX(0)}}55%{{opacity:1;transform:scaleX(1)}}100%{{opacity:0;transform:scaleX(1) scaleY(30)}}}}
@keyframes pwr2{{0%{{opacity:0}}2%{{opacity:.9;transform:scaleX(1)}}100%{{opacity:0;transform:scaleX(0)}}}}
.rem{{animation:on .3s 3.6s both}}
.name{{animation:nm .9s steps(1) 3.7s both}}
@keyframes nm{{0%{{opacity:0}}8%{{opacity:1;transform:translate(-9px,0) skewX(-10deg)}}18%{{opacity:.35;transform:translate(6px,0)}}28%{{opacity:1;transform:translate(-3px,0)}}42%{{opacity:.7;transform:translate(2px,0)}}56%{{opacity:1;transform:translate(-1px,0)}}70%,100%{{opacity:1;transform:none}}}}
.gA,.gB{{opacity:0}}
.gA{{animation:ga .9s steps(1) 3.7s both}}
.gB{{animation:gb .9s steps(1) 3.7s both}}
@keyframes ga{{0%{{opacity:0}}10%{{opacity:.9;transform:translate(7px,-2px)}}25%{{opacity:.6;transform:translate(-5px,1px)}}40%{{opacity:.5;transform:translate(3px,0)}}55%{{opacity:.3;transform:translate(-2px,0)}}70%,100%{{opacity:0}}}}
@keyframes gb{{0%{{opacity:0}}12%{{opacity:.7;transform:translate(-8px,2px)}}30%{{opacity:.5;transform:translate(4px,-1px)}}48%{{opacity:.3;transform:translate(-2px,0)}}64%,100%{{opacity:0}}}}
.ch{{animation:on 1ms linear both}}
.cur{{animation:on 1ms 4.7s both,blink 1.1s steps(1) 5.8s infinite}}
.ruler{{animation:on .6s 5.15s both}}
.facts{{animation:up .5s ease-out 5.35s both}}
.exit{{animation:on .3s 5.9s both}}
"""
    return document(
        W, H, "".join(o), theme=t, fonts=("mono", "mono5"), css=css,
        title="Vedansh Mathur — finalizing voids.",
        desc=("A terminal boot sequence loads modules (fastapi, celery, rabbitmq, redis, mongodb, vllm, bedrock, "
              "cpp_core), executes void finalize(), and resolves into the name Vedansh Mathur with the tagline "
              "'finalizing voids.' — SDE intern at Witting AI, AI infra / LLM systems, C++ on low-end machines, Gurugram."),
    )


def main():
    for m in ("dark", "light"):
        write(f"hero-{m}.svg", build(m))


if __name__ == "__main__":
    main()
