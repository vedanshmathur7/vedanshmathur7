"""Section rules (assets/sec-NN-*.svg) and the closing brace (assets/return-*.svg).

Drawn at 560px so they stay legible when GitHub mobile scales them down.
"""
from svgkit import THEMES, T, document, esc, mono_w, write

SECTIONS = [
    ("01", "whoami", "identity"),
    ("02", "htop", "data/now.yml"),
    ("03", "dot -Tsvg pipeline.dot", "system"),
    ("04", "ls /dev/cart*", "projects"),
    ("05", "cat stack.ld", "stack"),
    ("06", "scope --ch1 activity", "signal"),
    ("07", "./connect", "contact"),
]
W, H = 560, 34


def rule(mode, num, cmd, tag):
    t = THEMES[mode]
    o = [T(0, 22, num, fill=t["accent"], size=12, extra='font-weight="700"'),
         f'<text x="30" y="22" font-size="16" font-weight="500" fill="{t["text"]}">'
         f'<tspan fill="{t["accent"]}">$</tspan> {esc(cmd)}</text>']
    x0 = 30 + mono_w(f"$ {cmd}", 16) + 14
    x1 = W - mono_w(tag, 11) - 12
    o.append(f'<path d="M{x0:.1f} 17H{x1:.1f}" stroke="{t["line"] if mode == "dark" else t["mute"]}" stroke-width="1"/>')
    o.append(f'<path d="M{x1:.1f} 13v8" stroke="{t["dim"]}"/>')
    o.append(T(W, 21, tag, fill=t["dim"], size=11, anchor="end"))
    return document(W, H, "".join(o), theme=t, fonts=("mono", "mono5", "mono7"),
                    title=f"$ {cmd}", desc=f"Section {num}: {cmd} ({tag})")


def ret(mode):
    t = THEMES[mode]
    w, h = 560, 74
    o = [f'<text x="0" y="24" font-size="20" font-weight="600" fill="{t["accent"]}" xml:space="preserve">    return 0;</text>',
         f'<rect class="cur" x="{mono_w("    return 0;", 20) + 6:.1f}" y="8" width="10" height="20" fill="{t["accent"]}"/>',
         T(0, 52, "}", fill=t["text"], size=20, extra='font-weight="600"'),
         T(26, 51, "// process exited normally. voids finalized.", fill=t["dim"], size=12)]
    css = ".cur{animation:blink 1.1s steps(1) infinite}"
    return document(w, h, "".join(o), theme=t, fonts=("mono", "mono6"), css=css,
                    title="return 0;", desc="Closing line: return 0; — process exited normally.")


def main():
    for m in ("dark", "light"):
        for num, cmd, tag in SECTIONS:
            write(f"sec-{num}-{m}.svg", rule(m, num, cmd, tag))
        write(f"return-{m}.svg", ret(m))


if __name__ == "__main__":
    main()
