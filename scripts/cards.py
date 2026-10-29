"""assets/cart-<slug>-{dark,light}.svg — flagship projects as ROM cartridges.

Data: data/projects.yml. Only real, repo-backed numbers go in `metric`.
"""
import yaml

from svgkit import ROOT, THEMES, T, document, esc, mono_w, text_width, write

W, H = 400, 192
OWNER = "vedanshmathur7"


def wrap(text: str, n: int, max_lines: int = 2):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= n:
            cur = f"{cur} {w}".strip()
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: n - 1].rstrip() + "…"
    return lines


def build(mode: str, p: dict, idx: int) -> str:
    t = THEMES[mode]
    dark = mode == "dark"
    o = []
    c = 18  # corner notch
    shape = f"M1 1H{W-c}L{W-1} {c}V{H-1}H1Z"
    o.append(f'<path d="{shape}" fill="{t["panel"]}" stroke="{t["dim"] if dark else t["text"]}" stroke-width="1"/>')
    # label window
    o.append(f'<rect x="12" y="24" width="{W-24}" height="120" fill="none" stroke="{t["line"]}" stroke-width="1"/>')
    # header strip
    o.append(T(14, 16, f"ROM 0x{idx:02X}", fill=t["dim"], size=10.5, extra='font-weight="600"'))
    lang = p.get("lang", "")
    lw = mono_w(lang, 10.5) + 12
    lx = W - c - 12 - lw
    o.append(f'<rect x="{lx}" y="5" width="{lw}" height="15" fill="none" stroke="{t["dim"]}" stroke-width=".8"/>')
    o.append(T(lx + 6, 16, lang, fill=t["text"], size=10.5))
    o.append(f'<circle class="led" cx="{lx - 10}" cy="12.5" r="2.6" fill="{t["accent"]}"/>')

    # name + problem
    o.append(f'<text class="d" x="24" y="55" font-size="24" font-weight="700" fill="{t["text"]}" letter-spacing="-.3">{esc(p["name"])}</text>')
    for i, ln in enumerate(wrap(p["problem"], 49)):
        o.append(T(24, 77 + i * 16, ln, fill=t["text"] if not dark else "#B9BDB8", size=12))

    # metric or clone line
    m = p.get("metric")
    if m:
        vw = text_width(m["value"], "disp", 21)
        o.append(f'<text class="d" x="24" y="130" font-size="21" font-weight="700" fill="{t["accent"]}">{esc(m["value"])}</text>')
        o.append(T(24 + vw + 10, 129, m["label"], fill=t["dim"], size=10.5))
    else:
        o.append(f'<text x="24" y="129" font-size="10.5" fill="{t["dim"]}"><tspan fill="{t["accent"]}">$</tspan> '
                 f'git clone github.com/{OWNER}/{esc(p["repo"])}</text>')

    # tags
    x = 12
    ty = H - 29
    for tag in p.get("tags", [])[:5]:
        w = mono_w(tag, 10.5) + 12
        if x + w > W - 12:
            break
        o.append(f'<rect x="{x}" y="{ty-12}" width="{w}" height="16" fill="{t["bg"]}" stroke="{t["line"]}" stroke-width="1"/>')
        o.append(T(x + 6, ty, tag, fill=t["dim"] if dark else t["text"], size=10.5))
        x += w + 6

    # edge connector pins
    pins_w, n = 236, 20
    px0 = (W - pins_w) / 2
    step = pins_w / n
    pins = "".join(f'<rect x="{px0 + k*step + 1:.1f}" y="{H-11}" width="{step-3:.1f}" height="10" fill="{t["line"]}"/>' for k in range(n))
    o.append(pins)
    o.append(f'<path d="M{px0-8} {H-1}V{H-13}H{px0+pins_w+8}V{H-1}" fill="none" stroke="{t["dim"] if dark else t["text"]}" stroke-width="1"/>')

    css = ".led{animation:blink 2.8s steps(1) infinite}"
    metric_desc = f' Metric: {m["value"]} — {m["label"]}.' if m else ""
    return document(W, H, "".join(o), theme=t, fonts=("mono", "mono6", "disp"), css=css,
                    title=f'{p["name"]} — {p["problem"]}',
                    desc=f'Project cartridge for {p["name"]} ({lang}). {p["problem"]} Stack: {", ".join(p.get("tags", []))}.{metric_desc}')


def load():
    return yaml.safe_load((ROOT / "data" / "projects.yml").read_text())["cartridges"]


def readme_block(carts) -> str:
    """Two cartridges per <p>: side by side on desktop, stacked on phones."""
    def one(p):
        m = p.get("metric")
        alt = f'{p["name"]}: {p["problem"]}' + (f' ({m["value"]}, {m["label"]})' if m else "")
        return (f'<a href="https://github.com/{OWNER}/{p["repo"]}">'
                f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/cart-{p["slug"]}-dark.svg">'
                f'<img src="./assets/cart-{p["slug"]}-light.svg" width="400" alt="{esc(alt)}"></picture></a>')
    rows = ["<p>\n" + "\n".join(one(p) for p in carts[i:i + 2]) + "\n</p>" for i in range(0, len(carts), 2)]
    return "\n".join(rows)


def sync_readme(carts):
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    s = readme.read_text()
    a, b = "<!-- carts:start (generated from data/projects.yml) -->", "<!-- carts:end -->"
    if a in s and b in s:
        head, rest = s.split(a, 1)
        _, tail = rest.split(b, 1)
        readme.write_text(f"{head}{a}\n{readme_block(carts)}\n{b}{tail}")


def main():
    carts = load()
    for i, p in enumerate(carts, 1):
        for mode in ("dark", "light"):
            write(f'cart-{p["slug"]}-{mode}.svg', build(mode, p, i))
    sync_readme(carts)


if __name__ == "__main__":
    main()
