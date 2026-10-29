"""Regenerate every profile asset.  python scripts/build.py

Edit data/*.yml, never assets/*.svg. Each module also runs standalone.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import activity  # noqa: E402
import arch  # noqa: E402
import cards  # noqa: E402
import hero  # noqa: E402
import htop  # noqa: E402
import linkermap  # noqa: E402
import sections  # noqa: E402
from svgkit import ASSETS, ROOT  # noqa: E402

# files from the previous profile version; removed on first run
LEGACY = ["header.svg", "hd-about.svg", "hd-projects.svg", "hd-roadmap.svg", "hd-stack.svg",
          "hd-stats.svg", "stats.svg", "langs.svg", "year.svg", "github-profile-plan.md",
          "scripts/generate_profile.py", "scripts/fonts/jbmono-400.woff2",
          "scripts/fonts/jbmono-600.woff2", "scripts/fonts/jbmono-head.woff2", "scripts/fonts/OFL.txt"]


def main():
    for f in LEGACY:
        p = ROOT / f
        if p.exists():
            p.unlink()
            print(f"[legacy] removed {f}")
    for mod in (hero, htop, arch, cards, linkermap, activity, sections):
        mod.main()
    big = [(p.name, p.stat().st_size) for p in ASSETS.glob("*.svg") if p.stat().st_size > 150_000]
    if big:
        raise SystemExit(f"assets over 150 KB: {big}")
    print(f"[build] {len(list(ASSETS.glob('*.svg')))} svgs in assets/")


if __name__ == "__main__":
    main()
