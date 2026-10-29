"""assets/scope-{dark,light}.svg — last year's contributions as an oscilloscope trace.

Why a scope and not a heatmap: the calendar grid is 53x7 tiny cells that turn to
mush at phone width; a single weekly trace keeps its shape at any size and shows
rhythm (bursts, gaps, ramp-ups) at a glance. The measurement panel on the right
is the one compact stats panel.

Data: GitHub GraphQL (GITHUB_TOKEN in Actions) -> data/contributions.json cache.
Without a token it renders from the cache, so local runs and forks still work.
"""
import datetime as dt
import json
import math
import os
import urllib.request

from svgkit import ROOT, THEMES, T, document, esc, mono_w, write

CACHE = ROOT / "data" / "contributions.json"
LOGIN = os.environ.get("GH_LOGIN", "vedanshmathur7")
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-scope"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])
    data = {"login": LOGIN, "source": "github graphql contributionCalendar", "days": days}
    CACHE.write_text(json.dumps(data, indent=0) + "\n")
    return data


def load():
    try:
        data = fetch()
    except Exception as e:  # network/API hiccup: keep yesterday's picture
        print(f"[scope] fetch failed, using cache: {e}")
        data = None
    return data or json.loads(CACHE.read_text())


def stats(days):
    counts = [d["count"] for d in days]
    total = sum(counts)
    active = sum(c > 0 for c in counts)
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    tail = counts[:-1] if counts and counts[-1] == 0 else counts  # today may not have started yet
    current = 0
    for c in reversed(tail):
        if not c:
            break
        current += 1
    weeks = [counts[i:i + 7] for i in range(0, len(counts), 7)]
    wsum = [sum(w) for w in weeks]
    best_day = max(days, key=lambda d: d["count"])
    return dict(total=total, active=active, n=len(days), longest=longest, current=current,
                weeks=wsum, best_day=best_day, avg=total / max(len(weeks), 1))


def smooth(pts):
    """Monotone cubic (Fritsch-Carlson) through pts: no overshoot below zero."""
    n = len(pts)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    dxs = [xs[i + 1] - xs[i] for i in range(n - 1)]
    ms = [(ys[i + 1] - ys[i]) / dxs[i] for i in range(n - 1)]
    tan = [ms[0]] + [0.0 if ms[i - 1] * ms[i] <= 0 else
                     3 * (dxs[i - 1] + dxs[i]) / ((2 * dxs[i] + dxs[i - 1]) / ms[i - 1] + (dxs[i] + 2 * dxs[i - 1]) / ms[i])
                     for i in range(1, n - 1)] + [ms[-1]]
    d = f"M{xs[0]:.1f} {ys[0]:.1f}"
    for i in range(n - 1):
        h = dxs[i] / 3
        d += (f"C{xs[i] + h:.1f} {ys[i] + tan[i] * h:.1f} {xs[i + 1] - h:.1f} {ys[i + 1] - tan[i + 1] * h:.1f} "
              f"{xs[i + 1]:.1f} {ys[i + 1]:.1f}")
    return d


def build(mode, days, s):
    t = THEMES[mode]
    dark = mode == "dark"
    W, H = 860, 306
    sx, sy, sw, sh = 20, 20, 580, 232
    o = [f'<rect width="{W}" height="{H}" rx="6" fill="{t["bg"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="none" stroke="{t["line"]}"/>']
    o.append("<defs>"
             f'<clipPath id="scr"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}"/></clipPath>'
             '<filter id="ph" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="3.2"/></filter>'
             "</defs>")
    # screen + graticule (10 x 8 div)
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{t["panel"]}"/>')
    dx, dy = sw / 10, sh / 8
    grid = "".join(f"M{sx + i*dx:.1f} {sy}v{sh}" for i in range(1, 10))
    grid += "".join(f"M{sx} {sy + j*dy:.1f}h{sw}" for j in range(1, 8))
    o.append(f'<path d="{grid}" stroke="{t["line"]}" stroke-width="1" stroke-dasharray="1 3"/>')
    cxm, cym = sx + sw / 2, sy + sh / 2
    minor = "".join(f"M{sx + k*dx/5:.1f} {cym-3}v6" for k in range(1, 50))
    minor += "".join(f"M{cxm-3} {sy + k*dy/5:.1f}h6" for k in range(1, 40))
    o.append(f'<path d="M{cxm} {sy}v{sh}M{sx} {cym}h{sw}{minor}" stroke="{t["dim"]}" stroke-width=".8" opacity=".7"/>')
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="none" stroke="{t["dim"] if dark else t["text"]}"/>')

    # trace: weekly totals, sqrt-scaled so one burst week doesn't flatten the year
    wk = s["weeks"]
    vmax = max(max(wk), 1)
    base, top = sy + sh - 14, sy + 30
    pts = [(sx + 6 + i * (sw - 12) / (len(wk) - 1),
            base - math.sqrt(v) / math.sqrt(vmax) * (base - top)) for i, v in enumerate(wk)]
    d = smooth(pts)
    g = '<g clip-path="url(#scr)">'
    if dark:
        g += f'<path class="tr" d="{d}" pathLength="1000" fill="none" stroke="{t["accent"]}" stroke-width="5" opacity=".45" filter="url(#ph)"/>'
    g += f'<path class="tr" d="{d}" pathLength="1000" fill="none" stroke="{t["accent"]}" stroke-width="{1.7 if dark else 1.6}" stroke-linejoin="round"/>'
    ex, ey = pts[-1]
    g += (f'<circle class="beam" cx="{ex:.1f}" cy="{ey:.1f}" r="3.4" fill="{t["accent"]}"/>'
          f'<circle class="ring rm-hide" cx="{ex:.1f}" cy="{ey:.1f}" r="3.4" fill="none" stroke="{t["accent"]}"/>')
    g += "</g>"
    o.append(g)

    # on-screen labels
    o.append(f'<rect x="{sx+8}" y="{sy+8}" width="34" height="16" fill="{t["accent"]}"/>')
    o.append(T(sx + 25, sy + 20, "CH1", fill=t["on_accent"], size=11, anchor="middle", extra='font-weight="700"'))
    o.append(T(sx + 50, sy + 20, "√ contributions / week", fill=t["text"], size=11))
    o.append(T(sx + sw - 8, sy + 20, f"{len(wk)} wk · {len(wk)/10:.1f} wk/div", fill=t["dim"], size=11, anchor="end"))

    # month ticks under the screen
    start = dt.date.fromisoformat(days[0]["date"])
    seen = set()
    for i in range(len(wk)):
        wd = start + dt.timedelta(days=7 * i)
        for k in range(7):
            day = wd + dt.timedelta(days=k)
            if day.day == 1 and (day.year, day.month) not in seen and i > 0:
                seen.add((day.year, day.month))
                x = sx + 6 + i * (sw - 12) / (len(wk) - 1)
                o.append(f'<path d="M{x:.1f} {sy+sh}v5" stroke="{t["dim"]}"/>')
                o.append(T(x, sy + sh + 17, day.strftime("%b").lower(), fill=t["dim"], size=10.5, anchor="middle"))
    o.append(T(sx, H - 12, "src: github contribution calendar · redrawn daily by actions", fill=t["mute"] if dark else t["dim"], size=10.5))

    # measurement panel
    px = 624
    o.append(T(px, 36, "MEASURE", fill=t["dim"], size=11, extra='font-weight="600" letter-spacing="1.5"'))
    o.append(f'<path d="M{px} 46H{W-20}" stroke="{t["line"]}"/>')
    bd = s["best_day"]
    rows = [
        ("total", f'{s["total"]:,}', "contributions", True),
        ("active", f'{s["active"]}', f'/ {s["n"]} days', False),
        ("streak", f'{s["longest"]} d', f'max · {s["current"]} d now', False),
        ("peak", f'{bd["count"]}', f'on {bd["date"]}', False),
        ("mean", f'{s["avg"]:.1f}', "per week", False),
    ]
    for i, (lab, val, unit, hot) in enumerate(rows):
        y = 76 + i * 40
        o.append(T(px, y - 13, lab, fill=t["dim"], size=10.5))
        o.append(T(px, y + 5, val, fill=t["accent"] if hot else t["text"], size=17, extra='font-weight="600"'))
        o.append(T(px + mono_w(val, 17) + 8, y + 5, unit, fill=t["dim"], size=11))

    css = (".tr{stroke-dasharray:1000;animation:sweep 2.6s cubic-bezier(.4,0,.2,1) .3s both}"
           "@keyframes sweep{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}"
           ".beam{animation:on .2s 2.8s both}"
           ".ring{transform-box:fill-box;transform-origin:center;opacity:0;animation:ring 1.8s ease-out 3s infinite}"
           "@keyframes ring{0%{opacity:.9;transform:scale(1)}100%{opacity:0;transform:scale(4)}}")
    desc = (f'Oscilloscope-style trace of weekly GitHub contributions over the last year (square-root scale). '
            f'{s["total"]} contributions, {s["active"]} active days out of {s["n"]}, longest streak {s["longest"]} days, '
            f'current streak {s["current"]} days, peak day {bd["count"]} on {bd["date"]}, mean {s["avg"]:.1f} per week.')
    return document(W, H, "".join(o), theme=t, fonts=("mono", "mono6", "mono7"), css=css,
                    title="Contribution activity as an oscilloscope trace", desc=desc)


def main():
    data = load()
    days = data["days"][-371:]
    s = stats(days)
    for m in ("dark", "light"):
        write(f"scope-{m}.svg", build(m, days, s))
    print(f'[scope] {s["total"]} contributions, {len(s["weeks"])} weeks')


if __name__ == "__main__":
    main()
