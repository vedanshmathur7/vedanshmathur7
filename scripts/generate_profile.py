#!/usr/bin/env python3
"""Generate local SVG assets for the GitHub profile README."""
import base64
import functools
import json
import os
import urllib.request
from datetime import date, datetime, timedelta, timezone
from xml.sax.saxutils import escape

API = "https://api.github.com/graphql"
WIDTH = 680
LEFT = 34
MONO = "JBMono,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
OUT_DIR = os.environ.get("OUT_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGIN = os.environ.get("GH_LOGIN", "vedanshmathur7")

LIGHT = dict(data="#57606a", emph="#24292f", dim="#6e7781", rule="#d0d7de", bg="#ffffff")
DARK = dict(data="#c9d1d9", emph="#f0f6fc", dim="#8b949e", rule="#30363d", bg="#0d1117")
ACCENT = "#2f81f7"
GREEN = "#3fb950"
AMBER = "#d29922"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes {
        name
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


@functools.lru_cache(maxsize=None)
def font_face(filename, weight):
    with open(os.path.join(FONT_DIR, filename), "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (
        "@font-face{font-family:JBMono;font-style:normal;"
        f"font-weight:{weight};font-display:block;"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}"
    )


def font_text():
    return font_face("jbmono-400.woff2", 400) + font_face("jbmono-600.woff2", 600)


def style():
    def block(theme):
        return (
            f".data{{fill:{theme['data']}}}.emph{{fill:{theme['emph']}}}"
            f".dim{{fill:{theme['dim']}}}.rule{{stroke:{theme['rule']}}}"
            f".bg{{fill:{theme['bg']}}}"
        )
    return (
        f"<style>{font_text()}{block(LIGHT)}"
        f".blue{{fill:{ACCENT}}}.green{{fill:{GREEN}}}.amber{{fill:{AMBER}}}"
        f".bar{{fill:{ACCENT};opacity:.72}}.heat0{{fill:{LIGHT['rule']};opacity:.45}}"
        ".heat1{fill:#9be9a8}.heat2{fill:#40c463}.heat3{fill:#30a14e}.heat4{fill:#216e39}"
        f"@media(prefers-color-scheme:dark){{{block(DARK)}.heat0{{fill:{DARK['rule']};opacity:.58}}}}"
        "</style>"
    )


def svg_open(width, height):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" font-family="{MONO}">{style()}'
    )


def text(x, y, value, size=13, cls="data", weight=400, anchor="start"):
    return (
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'
    )


def line(x1, y1, x2, y2):
    return f'<path d="M{x1} {y1}H{x2}" class="rule" stroke-width="1"/>'


def safe_write(name, body):
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def window():
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=364)
    return f"{start.isoformat()}T00:00:00Z", f"{today.isoformat()}T23:59:59Z"


def fetch_profile():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    since, until = window()
    payload = json.dumps({"query": QUERY, "variables": {"login": LOGIN, "from": since, "to": until}}).encode()
    request = urllib.request.Request(
        API,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{LOGIN}-profile-readme",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get("errors"):
        raise SystemExit(result["errors"])
    return result["data"]["user"]


def summarize(user):
    if not user:
        return {
            "total": 0,
            "active": 0,
            "weekly": [0] * 53,
            "days": [],
            "current": 0,
            "longest": 0,
            "languages": [("Python", 42), ("JavaScript", 27), ("Jupyter Notebook", 14), ("TypeScript", 10), ("C++", 7)],
            "repo_langs": [("Python", 5), ("JavaScript", 4), ("TypeScript", 2), ("Jupyter Notebook", 2), ("C++", 1)],
        }
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [day for week in weeks for day in week["contributionDays"]]
    weekly = [sum(day["contributionCount"] for day in week["contributionDays"]) for week in weeks]
    current, longest, run = 0, 0, 0
    streak_days = days[:-1] if days and days[-1]["contributionCount"] == 0 else days
    for day in days:
        if day["contributionCount"]:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    for day in reversed(streak_days):
        if not day["contributionCount"]:
            break
        current += 1
    size_totals, repo_totals = {}, {}
    for repo in user["repositories"]["nodes"]:
        edges = repo["languages"]["edges"]
        for edge in edges:
            name = edge["node"]["name"]
            size_totals[name] = size_totals.get(name, 0) + edge["size"]
        if edges:
            name = edges[0]["node"]["name"]
            repo_totals[name] = repo_totals.get(name, 0) + 1
    rank = lambda values: sorted(values.items(), key=lambda item: (-item[1], item[0]))[:5]
    return {
        "total": cal["totalContributions"],
        "active": sum(1 for day in days if day["contributionCount"]),
        "weekly": weekly,
        "days": days,
        "current": current,
        "longest": longest,
        "languages": rank(size_totals),
        "repo_langs": rank(repo_totals),
    }


def draw_header():
    art = [
        "      ________________________________",
        "     /  o  o  o     datavox bus     /|",
        "    /____AI_BACKEND_SYSTEMS_________/ |",
        "    |  [fastapi] [llm] [aws] [db]  |  |",
        "    |  async queues -> model APIs   |  |",
        "    |  audit loops -> real metrics  | /",
        "    |_______________________________|/",
    ]
    parts = [svg_open(760, 248), '<rect width="760" height="248" class="bg" rx="6"/>']
    parts.append(line(28, 202, 732, 202))
    for i, row in enumerate(art):
        parts.append(text(30, 42 + i * 18, row, 12, "green"))
    parts.append(text(360, 70, "Vedansh Mathur", 28, "emph", 600))
    parts.append(text(362, 101, "AI backend systems | LLM infra | AWS", 13, "data"))
    parts.append(text(362, 128, "models, data, services, and eval loops", 12, "dim"))
    parts.append(text(362, 156, "$ current_focus --trace", 12, "blue"))
    parts.append(text(362, 178, "FastAPI, async pipelines, RAG, inference", 12, "data"))
    parts.append('<rect x="362" y="188" width="9" height="15" class="green"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/></rect>')
    parts.append("</svg>")
    safe_write("header.svg", "".join(parts))


def draw_heading(filename, title):
    parts = [svg_open(WIDTH, 54)]
    parts.append(text(LEFT, 35, f"/{title}", 20, "emph", 600))
    parts.append(line(LEFT + len(title) * 14 + 24, 29, WIDTH - LEFT, 29))
    parts.append("</svg>")
    safe_write(filename, "".join(parts))


def draw_stats(summary):
    weekly = summary["weekly"] or [0]
    peak = max(weekly) or 1
    parts = [svg_open(WIDTH, 152)]
    parts.append(text(LEFT, 40, f"{summary['total']:,}", 34, "emph", 600))
    parts.append(text(LEFT, 64, "contributions in the last year", 12, "dim"))
    parts.append(text(292, 38, f"{summary['active']}", 24, "emph", 600))
    parts.append(text(292, 62, "active days", 12, "dim"))
    parts.append(text(430, 38, f"{summary['current']}", 24, "emph", 600))
    parts.append(text(430, 62, "current streak", 12, "dim"))
    parts.append(text(555, 38, f"{summary['longest']}", 24, "emph", 600))
    parts.append(text(555, 62, "longest streak", 12, "dim"))
    x0, y0, gap = LEFT, 122, 3
    bar_w = (WIDTH - LEFT * 2 - gap * (len(weekly) - 1)) / len(weekly)
    for idx, count in enumerate(weekly):
        h = 8 + (count / peak) * 45
        x = x0 + idx * (bar_w + gap)
        parts.append(f'<rect x="{x:.1f}" y="{y0 - h:.1f}" width="{bar_w:.1f}" height="{h:.1f}" rx="2" class="bar"/>')
    parts.append(text(LEFT, 145, "weekly contribution rhythm, generated locally from GitHub GraphQL", 10, "dim"))
    parts.append("</svg>")
    safe_write("stats.svg", "".join(parts))


def draw_langs(summary):
    parts = [svg_open(WIDTH, 166)]
    parts.append(text(LEFT, 32, "by bytes", 13, "dim", 600))
    parts.append(text(360, 32, "by primary repo language", 13, "dim", 600))
    for col, key in [(LEFT, "languages"), (360, "repo_langs")]:
        values = summary[key]
        peak = max([value for _, value in values] or [1])
        for i, (name, value) in enumerate(values):
            y = 58 + i * 20
            width = 150 * value / peak if peak else 0
            parts.append(text(col, y, name, 12, "data"))
            parts.append(f'<rect x="{col + 142}" y="{y - 10}" width="{width:.1f}" height="9" rx="2" class="bar"/>')
    parts.append("</svg>")
    safe_write("langs.svg", "".join(parts))


def draw_year(summary):
    days = summary["days"]
    if not days:
        today = date.today()
        days = [
            {"date": (today - timedelta(days=364 - i)).isoformat(), "weekday": i % 7, "contributionCount": 0}
            for i in range(365)
        ]
    max_count = max([day["contributionCount"] for day in days] or [0]) or 1
    parts = [svg_open(WIDTH, 118)]
    parts.append(text(LEFT, 24, "last 365 days", 12, "dim", 600))
    cell, gap, x0, y0 = 8, 3, LEFT + 40, 38
    for idx, day in enumerate(days):
        week = idx // 7
        weekday = int(day.get("weekday", idx % 7))
        level = min(4, int(day["contributionCount"] / max_count * 4 + 0.999)) if day["contributionCount"] else 0
        parts.append(f'<rect x="{x0 + week * (cell + gap)}" y="{y0 + weekday * (cell + gap)}" width="{cell}" height="{cell}" rx="2" class="heat{level}"/>')
    parts.append(text(LEFT, 55, "mon", 10, "dim"))
    parts.append(text(LEFT, 77, "wed", 10, "dim"))
    parts.append(text(LEFT, 99, "fri", 10, "dim"))
    parts.append("</svg>")
    safe_write("year.svg", "".join(parts))


def main():
    user = fetch_profile()
    summary = summarize(user)
    draw_header()
    for filename, title in [
        ("hd-about.svg", "about"),
        ("hd-stack.svg", "stack"),
        ("hd-projects.svg", "selected-projects"),
        ("hd-stats.svg", "signal"),
        ("hd-roadmap.svg", "build-roadmap"),
    ]:
        draw_heading(filename, title)
    draw_stats(summary)
    draw_langs(summary)
    draw_year(summary)


if __name__ == "__main__":
    main()
