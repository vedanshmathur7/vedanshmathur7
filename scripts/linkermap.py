"""assets/stack-{dark,light}.svg — the stack as a linker map. Data: data/stack.yml."""
import yaml

from svgkit import ROOT, THEMES, T, document, esc, mono_w, write

W = 860
FS = 13.5
SEG = 0x1000
BOLD = 'font-weight="600"'


def build(mode: str, sections) -> str:
    t = THEMES[mode]
    dark = mode == "dark"
    n = len(sections)
    row0, rh = 166, 27
    H = row0 + n * rh + 46
    o = [f'<rect width="{W}" height="{H}" rx="6" fill="{t["bg"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="none" stroke="{t["line"]}"/>']
    o.append("<defs>"
             f'<pattern id="ha" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             f'<rect width="2" height="6" fill="{t["accent"]}"/></pattern>'
             f'<pattern id="hd" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             f'<rect width="1.4" height="6" fill="{t["dim"]}"/></pattern>'
             f'<pattern id="hd2" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">'
             f'<rect width="1.2" height="5" fill="{t["dim"]}"/></pattern>'
             "</defs>")

    o.append(f'<text x="20" y="32" font-size="{FS}" fill="{t["text"]}"><tspan fill="{t["accent"]}">$</tspan> '
             f'ld -M -T stack.ld -o vedansh.elf <tspan fill="{t["dim"]}">*.o</tspan></text>')
    o.append(T(W - 20, 32, "memory map", fill=t["dim"], size=12, anchor="end"))

    # memory strip
    sx, sy, sw, sh = 20, 54, W - 40, 34
    segw = sw / n
    for i, s in enumerate(sections):
        x = sx + i * segw
        fill = "url(#ha)" if i == 0 else ("url(#hd)" if i % 2 else "url(#hd2)")
        op = 1 if i == 0 else .55
        o.append(f'<g class="seg" style="animation-delay:{0.2 + i*0.12:.2f}s">'
                 f'<rect x="{x:.1f}" y="{sy}" width="{segw:.1f}" height="{sh}" fill="{fill}" opacity="{op}"/>'
                 f'<rect x="{x + segw/2 - mono_w(s["name"], 12)/2 - 6:.1f}" y="{sy + 9}" width="{mono_w(s["name"], 12) + 12:.1f}" height="17" fill="{t["bg"]}"/>'
                 f'{T(x + segw/2, sy + 22, s["name"], fill=t["text"], size=12, anchor="middle", extra=BOLD)}'
                 "</g>")
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="none" stroke="{t["dim"] if dark else t["text"]}"/>')
    ticks = []
    for i in range(n + 1):
        x = sx + i * segw
        ticks.append(f'<path d="M{x:.1f} {sy}v{sh + 6}" stroke="{t["dim"] if dark else t["text"]}"/>')
        anchor = "start" if i == 0 else ("end" if i == n else "middle")
        ticks.append(T(x, sy + sh + 19, f"0x{i*SEG:04x}", fill=t["dim"], size=11, anchor=anchor))
    o.append("".join(ticks))

    # table
    cx = [20, 120, 220, 330]
    hy = 140
    for x, h in zip(cx, ["section", "origin", "region", "symbols"]):
        o.append(T(x, hy, h, fill=t["dim"], size=12))
    o.append(f'<path d="M20 {hy+8}H{W-20}" stroke="{t["line"]}"/>')
    for i, s in enumerate(sections):
        y = row0 + i * rh
        syms = s["symbols"]
        parts = []
        for k, sym in enumerate(syms):
            if k:
                parts.append(f'<tspan fill="{t["mute"] if dark else t["dim"]}"> · </tspan>')
            parts.append(f'<tspan>{esc(sym)}</tspan>')
        o.append(f'<g class="row" style="animation-delay:{0.6 + i*0.09:.2f}s">'
                 f'{T(cx[0], y, s["name"], fill=t["accent"], size=FS, extra=BOLD)}'
                 f'{T(cx[1], y, f"0x{i*SEG:04x}", fill=t["text"], size=FS)}'
                 f'{T(cx[2], y, s["region"], fill=t["dim"], size=FS)}'
                 f'<text x="{cx[3]}" y="{y}" font-size="{FS}" fill="{t["text"]}">{"".join(parts)}</text></g>')

    fy = H - 18
    o.append(f'<path d="M20 {fy-20}H{W-20}" stroke="{t["line"]}" stroke-dasharray="2 4"/>')
    # the easter egg: grad year as an address
    o.append(f'<text x="20" y="{fy}" font-size="11.5" fill="{t["mute"] if dark else t["dim"]}">'
             f'.comment  0x2028  "finalizing voids"</text>')
    o.append(f'<text x="{W-20}" y="{fy}" font-size="11.5" fill="{t["dim"]}" text-anchor="end">entry point: '
             f'<tspan fill="{t["text"]}">main</tspan> -&gt; <tspan fill="{t["accent"]}">finalize()</tspan></text>')

    css = ".seg{animation:on .25s both}.row{animation:up .35s ease-out both}"
    desc = "; ".join(f'{s["name"]} ({s["region"]}): {", ".join(s["symbols"])}' for s in sections)
    return document(W, H, "".join(o), theme=t, fonts=("mono", "mono6"), css=css,
                    title="Stack as a linker map",
                    desc="Tech stack laid out like a linker memory map. " + desc)


def main():
    sections = yaml.safe_load((ROOT / "data" / "stack.yml").read_text())["sections"]
    for m in ("dark", "light"):
        write(f"stack-{m}.svg", build(m, sections))


if __name__ == "__main__":
    main()
