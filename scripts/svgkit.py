"""Tiny SVG toolkit for the profile: themes, embedded font subsets, text-to-path.

Rules every asset follows (GitHub renders README SVGs as <img>):
  * no external requests: fonts are subset + base64-embedded, nothing else is loaded
  * the *default* styles are the final frame; animations start from hidden
    (fill-mode: both). If a renderer ignores CSS animation, you still see the
    finished picture.
  * prefers-reduced-motion kills every animation -> final frame, static.
"""
from __future__ import annotations

import base64
import io
import re
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- themes
# dark  = phosphor terminal. light = engineering blueprint (paper + cyan ink).
THEMES = {
    "dark": dict(
        bg="#0A0C0D", panel="#0E1112", line="#1E2427", grid="#14191B",
        text="#E6E6E1", dim="#5B6166", mute="#3A4044",
        accent="#B6FF3B", on_accent="#0A0C0D", glow=0.55,
    ),
    "light": dict(
        bg="#F4F7F5", panel="#FBFCFB", line="#B8CDD6", grid="#E2ECEF",
        text="#0B3B57", dim="#5F7F90", mute="#A9C0CA",
        accent="#0A7EA4", on_accent="#F4F7F5", glow=0.0,
    ),
}

# font key -> (file, css family, weight)
FONT_FILES = {
    "mono": ("plexmono-400.woff2", "PM", 400),
    "mono5": ("plexmono-500.woff2", "PM", 500),
    "mono6": ("plexmono-600.woff2", "PM", 600),
    "mono7": ("plexmono-700.woff2", "PM", 700),
    "disp": ("spacegrotesk-700.woff2", "SG", 700),
}
MONO_ADV = 0.6  # IBM Plex Mono advance = 600/1000 em


def mono_w(text: str, size: float) -> float:
    return len(text) * size * MONO_ADV


def esc(s: str) -> str:
    return escape(str(s), {'"': "&quot;"})


@lru_cache(maxsize=None)
def _font(key: str) -> TTFont:
    return TTFont(FONTS / FONT_FILES[key][0])


def font_face(key: str, chars: str) -> str:
    """@font-face rule with a woff2 subset containing only `chars`."""
    file, family, weight = FONT_FILES[key]
    ft = TTFont(FONTS / file, recalcTimestamp=False)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern"]
    opts.name_IDs = []
    opts.notdef_outline = False
    opts.hinting = False
    opts.desubroutinize = True
    s = subset.Subsetter(opts)
    s.populate(text=chars + " ")
    s.subset(ft)
    buf = io.BytesIO()
    ft.flavor = "woff2"
    ft.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:{family};font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


def text_width(text: str, key: str, size: float, tracking: float = 0) -> float:
    ft = _font(key)
    cmap, hmtx, upm = ft.getBestCmap(), ft["hmtx"], ft["head"].unitsPerEm
    w = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text) * size / upm
    return w + tracking * max(len(text) - 1, 0)


def text_path(text: str, key: str, size: float, x: float, y: float,
              tracking: float = 0) -> str:
    """Outline a string as one SVG path `d` (baseline at y)."""
    ft = _font(key)
    gs, cmap, hmtx = ft.getGlyphSet(), ft.getBestCmap(), ft["hmtx"]
    scale = size / ft["head"].unitsPerEm
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    cx = x
    for ch in text:
        g = cmap.get(ord(ch))
        if g is None:
            continue
        gs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
        cx += hmtx[g][0] * scale + tracking
    return pen.getCommands()


_TEXT_RE = re.compile(r"<text\b[^>]*>(.*?)</text>", re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def _used_chars(body: str) -> str:
    raw = "".join(_TAG_RE.sub("", m) for m in _TEXT_RE.findall(body))
    raw = (raw.replace("&lt;", "<").replace("&gt;", ">")
              .replace("&quot;", '"').replace("&amp;", "&"))
    return "".join(sorted(set(raw)))


BASE_CSS = """
text{font-family:PM,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-kerning:none}
.d{font-family:SG,'Space Grotesk',system-ui,sans-serif}
@keyframes on{from{opacity:0}to{opacity:1}}
@keyframes up{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes draw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.rm-hide{display:none}}
"""


def document(w: int, h: int, body: str, *, title: str, desc: str,
             fonts: tuple[str, ...] = ("mono",), css: str = "",
             theme: dict) -> str:
    chars = _used_chars(body)
    faces = "".join(font_face(k, chars) for k in fonts)
    t = theme
    root_css = (f"svg{{--bg:{t['bg']};--panel:{t['panel']};--line:{t['line']};"
                f"--grid:{t['grid']};--text:{t['text']};--dim:{t['dim']};"
                f"--mute:{t['mute']};--accent:{t['accent']};--on:{t['on_accent']}}}")
    style = faces + root_css + BASE_CSS + css
    style = re.sub(r"\s*\n\s*", "", style)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{esc(title)}</title><desc id="d">{esc(desc)}</desc>'
            f"<style>{style}</style>{body}</svg>\n")


def write(name: str, svg: str) -> Path:
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / name
    p.write_text(svg, encoding="utf-8")
    return p


def T(x, y, s, cls="", fill=None, size=None, anchor=None, extra="") -> str:
    """<text> helper. Coordinates rounded; fill/size optional."""
    a = [f'x="{x:g}"', f'y="{y:g}"']
    if cls:
        a.append(f'class="{cls}"')
    if fill:
        a.append(f'fill="{fill}"')
    if size:
        a.append(f'font-size="{size:g}"')
    if anchor:
        a.append(f'text-anchor="{anchor}"')
    if extra:
        a.append(extra)
    return f"<text {' '.join(a)}>{esc(s)}</text>"
