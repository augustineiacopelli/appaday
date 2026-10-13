#!/usr/bin/env python3
"""
AppADay "Save to Phone" asset generator.

For every app in icons/manifest.json (written by generate_icons.py) this writes:

    icons/192/NNN.png, icons/512/NNN.png     Android install icons (same art as icons/NNN.png)
    manifests/NNN.webmanifest                web app manifest that lets Chrome on Android
                                             offer a one tap Install for that app

plus icons/192/portfolio.png, icons/512/portfolio.png and manifests/portfolio.webmanifest
for the portal itself.

Each app's index.html links its manifest and loads save.js from this repo
(see SAVE.md). Run after generate_icons.py whenever an app ships:

    pip install cairosvg --break-system-packages
    npm install lucide-static
    python3 generate_icons.py
    python3 generate_save_assets.py

Idempotent: re-running rewrites identical files.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_icons as gi  # noqa: E402
from apply_icons import short_title  # noqa: E402

SITE = "https://augustineiacopelli.github.io"
PORTAL = SITE + "/appaday/"
SIZES = (192, 512)
BG = "#0F0E0C"


def render(glyph, top, bottom, stroke, size, dest):
    gi.SIZE = size
    gi.write_png(gi.build_svg(glyph, top, bottom, stroke), dest)


def manifest(name, short, url, num, theme):
    icons = []
    for s in SIZES:
        src = "%sicons/%d/%s.png" % (PORTAL, s, num)
        icons.append({"src": src, "sizes": "%dx%d" % (s, s), "type": "image/png", "purpose": "any"})
        icons.append({"src": src, "sizes": "%dx%d" % (s, s), "type": "image/png", "purpose": "maskable"})
    return {
        "name": name,
        "short_name": short,
        "id": url,
        "start_url": url,
        "scope": url,
        "display": "standalone",
        "background_color": BG,
        "theme_color": theme,
        "icons": icons,
    }


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=True)
        f.write("\n")


def main():
    if not os.path.isdir(gi.LUCIDE):
        sys.exit("Lucide not found. Run: npm install lucide-static")
    apps = json.load(open("icons/manifest.json", encoding="utf-8"))
    if not apps:
        sys.exit("icons/manifest.json is empty. Run generate_icons.py first.")
    for s in SIZES:
        os.makedirs("icons/%d" % s, exist_ok=True)
    os.makedirs("manifests", exist_ok=True)

    for a in apps:
        num, color = a["num"], a["color"]
        for s in SIZES:
            render(a["glyph"], gi.shade(color, 1.20), gi.shade(color, 0.82), "#FFFFFF",
                   s, "icons/%d/%s.png" % (s, num))
        url = "%s/%s/" % (SITE, a["slug"])
        write_json("manifests/%s.webmanifest" % num,
                   manifest(a["name"], short_title(num, a["name"]), url, num, color))

    for s in SIZES:
        render(gi.PORTFOLIO_GLYPH, "#1A1815", gi.PORTFOLIO_BG, gi.PORTFOLIO_FG,
               s, "icons/%d/portfolio.png" % s)
    write_json("manifests/portfolio.webmanifest",
               manifest("AppADay", "AppADay", PORTAL, "portfolio", "#C8401A"))
    gi.SIZE = 180
    print("apps: %d   manifests and %s icons written" % (len(apps), "/".join(map(str, SIZES))))


if __name__ == "__main__":
    main()
