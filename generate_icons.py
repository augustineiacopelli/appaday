#!/usr/bin/env python3
"""
AppADay iOS icon generator.

Reads the LIVE portal app array, looks each app up in GLYPH_MAP, and writes
icons/NNN.png at 180x180 plus icons/portfolio.png.

Never edit the app list by hand here. Add one line to GLYPH_MAP when a new
app ships, then re-run. Apps present in the portal but missing from
GLYPH_MAP are reported and skipped rather than silently defaulted.

    pip install cairosvg --break-system-packages
    npm install lucide-static
    python3 generate_icons.py
"""

import io
import json
import os
import re
import sys
import urllib.request

import cairosvg
from PIL import Image

PORTAL = "https://raw.githubusercontent.com/augustineiacopelli/appaday/main/index.html"
LUCIDE = "node_modules/lucide-static/icons"
OUT = "icons"
SIZE = 180
GLYPH_SCALE = 0.52          # glyph occupies 52% of the square
STROKE = 2.35               # bumped from Lucide's default 2 for small-size legibility

# Nine-category palette. D and P are the portal's existing --gold and --accent.
CAT_COLOR = {
    "C": "#A63D9E",  # Creative
    "D": "#B8860B",  # Data Viz
    "E": "#1F7A8C",  # Educational
    "G": "#276EB7",  # Games
    "H": "#D14D72",  # Health & Wellness
    "I": "#5B4BC4",  # Interactive
    "P": "#C8401A",  # Productivity
    "S": "#6A4C93",  # Spirituality
    "U": "#289664",  # Utility Tools
}
FALLBACK = "#7A7468"         # portal --muted, used if a new category appears
PORTFOLIO_BG = "#0F0E0C"     # portal --ink
PORTFOLIO_FG = "#C8401A"     # portal --accent

# Optional per-app color override. Leave empty to use the category color.
# Populate this later if you move to per-app color without touching anything else.
COLOR_OVERRIDE = {}

GLYPH_MAP = {
    "001": "zap", "002": "droplets", "003": "book-open", "004": "test-tubes",
    "005": "laugh", "006": "layout-grid", "007": "trophy", "008": "grid-3x3",
    "009": "timer", "010": "help-circle", "011": "key-round", "012": "flame",
    "013": "pointer", "014": "hourglass", "015": "scroll-text", "016": "beer",
    "017": "pen-line", "018": "waves", "019": "languages", "020": "rainbow",
    "021": "shield", "022": "feather", "023": "clipboard-list", "024": "pie-chart",
    "025": "palette", "026": "receipt", "027": "calendar-check", "028": "gamepad-2",
    "029": "heart-handshake", "030": "moon", "031": "crown", "032": "crosshair",
    "033": "arrow-left-right", "034": "dices", "035": "file-text", "036": "flip-horizontal",
    "037": "bell", "038": "landmark", "039": "bug", "040": "cooking-pot",
    "041": "film", "042": "wind", "043": "list-checks", "044": "coins",
    "045": "droplet", "046": "wine-off", "047": "rabbit", "048": "car",
    "049": "footprints", "050": "dumbbell", "051": "activity", "052": "qr-code",
    "053": "split", "054": "moon-star", "055": "sunrise", "056": "filter",
    "057": "sparkles", "058": "scale", "059": "pencil", "060": "check-square",
    "061": "layers", "062": "battery-charging", "063": "cpu", "064": "flower",
    "065": "trending-up", "066": "hand-heart", "067": "hammer", "068": "graduation-cap",
    "069": "route", "070": "truck", "071": "banknote", "072": "wrench",
    "073": "columns-3", "074": "cup-soda", "075": "castle", "076": "clock",
    "077": "gauge", "078": "swords", "079": "flower-2", "080": "cross",
    "081": "armchair", "082": "grid-2x2", "083": "tag", "084": "circle-dollar-sign",
    "085": "star", "086": "mail", "087": "bell-ring", "088": "calculator",
    "089": "pen-tool", "090": "file-search", "091": "bar-chart-3", "092": "line-chart",
    "093": "message-square-warning", "094": "type", "095": "contrast", "096": "spade",
    "097": "binoculars", "098": "atom", "099": "message-circle", "100": "radar",
    "101": "calendar-heart", "102": "scissors", "103": "network", "104": "trees",
    "105": "book-marked", "106": "braces", "107": "link", "108": "telescope",
    "109": "credit-card", "110": "disc-3", "111": "file-check", "112": "notebook-pen",
    "113": "pause", "114": "person-standing", "115": "shopping-basket", "116": "scroll",
    "117": "heart-pulse",
}
PORTFOLIO_GLYPH = "shapes"


def fetch_portal():
    if os.path.exists("portal.html"):
        return open("portal.html", encoding="utf-8").read()
    with urllib.request.urlopen(PORTAL) as r:
        return r.read().decode("utf-8")


def parse_apps(html):
    apps = []
    for obj in re.findall(r"\{[^{}]*?num:\s*\"\d{3}\"[^{}]*?\}", html, re.S):
        def field(key):
            m = re.search(key + r':\s*"([^"]*)"', obj)
            return m.group(1) if m else ""
        apps.append({
            "num": field("num"),
            "cat": field("cat"),
            "name": field("name").replace("&amp;", "&"),
            "slug": field("url").rstrip("/").split("/")[-1],
        })
    return apps


def shade(hexc, factor):
    v = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(c * factor))) for c in v)


def glyph_inner(name):
    path = os.path.join(LUCIDE, name + ".svg")
    raw = open(path, encoding="utf-8").read()
    inner = re.sub(r"^.*?<svg[^>]*>", "", raw, flags=re.S)
    return re.sub(r"</svg>\s*$", "", inner, flags=re.S).strip()


def build_svg(glyph, top, bottom, stroke):
    scale = SIZE * GLYPH_SCALE / 24.0
    off = (SIZE - 24 * scale) / 2.0
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="0.3" y2="1">'
        '<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bot}"/>'
        "</linearGradient></defs>"
        '<rect width="{s}" height="{s}" fill="url(#g)"/>'
        '<g transform="translate({o:.3f},{o:.3f}) scale({sc:.5f})" fill="none" stroke="{st}" '
        'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{inner}</g>'
        "</svg>"
    ).format(s=SIZE, top=top, bot=bottom, o=off, sc=scale, st=stroke,
             sw=STROKE, inner=glyph_inner(glyph))


def write_png(svg, dest):
    png = cairosvg.svg2png(bytestring=svg.encode("utf-8"),
                           output_width=SIZE, output_height=SIZE)
    # Flatten to opaque RGB: iOS renders transparent pixels as black.
    Image.open(io.BytesIO(png)).convert("RGB").save(dest, "PNG", optimize=True)


def main():
    if not os.path.isdir(LUCIDE):
        sys.exit("Lucide not found. Run: npm install lucide-static")
    os.makedirs(OUT, exist_ok=True)

    apps = parse_apps(fetch_portal())
    if not apps:
        sys.exit("Parsed zero apps from the portal. Aborting rather than writing junk.")

    missing_glyph, unknown_cat, written = [], [], 0
    manifest = []

    for app in apps:
        num, cat = app["num"], app["cat"]
        glyph = GLYPH_MAP.get(num)
        if not glyph:
            missing_glyph.append("%s %s" % (num, app["name"]))
            continue
        if cat not in CAT_COLOR:
            unknown_cat.append("%s cat=%s" % (num, cat))
        color = COLOR_OVERRIDE.get(num, CAT_COLOR.get(cat, FALLBACK))
        svg = build_svg(glyph, shade(color, 1.20), shade(color, 0.82), "#FFFFFF")
        write_png(svg, os.path.join(OUT, num + ".png"))
        written += 1
        manifest.append({"num": num, "cat": cat, "name": app["name"],
                         "slug": app["slug"], "glyph": glyph, "color": color})

    svg = build_svg(PORTFOLIO_GLYPH, "#1A1815", PORTFOLIO_BG, PORTFOLIO_FG)
    write_png(svg, os.path.join(OUT, "portfolio.png"))

    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)

    print("apps in portal: %d   icons written: %d" % (len(apps), written))
    if missing_glyph:
        print("NO GLYPH MAPPED (add to GLYPH_MAP):")
        for m in missing_glyph:
            print("  " + m)
    if unknown_cat:
        print("UNKNOWN CATEGORY (add to CAT_COLOR):")
        for m in unknown_cat:
            print("  " + m)
    if not missing_glyph and not unknown_cat:
        print("clean run, every app covered")


if __name__ == "__main__":
    main()
