#!/usr/bin/env python3
"""
Inserts the apple-touch-icon and home-screen title tags into every AppADay app.

Each app is its own repo, so this expects a parent directory containing the
cloned repos, one folder per app, named by its slug:

    ~/appaday-repos/
        appaday/                       <- the portal repo (holds icons/)
        appaday-001-reaction-timer/
        appaday-002-stream-cleaner/
        ...

Run from inside the portal repo after generate_icons.py:

    python3 apply_icons.py --root ~/appaday-repos            # dry run
    python3 apply_icons.py --root ~/appaday-repos --write    # actually patch

Idempotent. An app that already has an apple-touch-icon link is left alone,
so re-running after shipping a new app only touches the new one.
"""

import argparse
import json
import os
import re
import sys
from html import escape

ICON_BASE = "https://augustineiacopelli.github.io/appaday/icons"

# apple-mobile-web-app-title truncates around 12 characters on the home screen.
# Anything longer than that needs a short form here.
TITLE = {
    "001": "Reaction", "002": "Stream", "003": "Scripture", "005": "Dad Jokes",
    "007": "Standing", "008": "Numbers", "011": "Password", "012": "Prayers",
    "016": "Chug", "017": "Scribe", "019": "Tone", "020": "Readers",
    "023": "Tasting", "029": "Advocate", "031": "Saints", "035": "Distiller",
    "038": "Relics", "039": "Fireflies", "040": "Kitchen", "041": "Frames",
    "044": "Quarters", "045": "Water", "046": "Sober", "049": "Pace",
    "053": "Decider", "055": "Offering", "057": "Liberty", "058": "Civics",
    "059": "Mad Libs", "061": "Flashcards", "063": "Bleeding", "066": "Confiteor",
    "067": "Chisel", "072": "Fix-It", "074": "Tap & Can", "077": "Sentinel",
    "078": "Red Team", "080": "Rosary", "083": "Label Lab", "084": "Mtg Cost",
    "085": "Stars", "086": "Subject Lab", "087": "Angelus", "090": "Syllabus",
    "092": "Forecast", "093": "Scam Bait", "094": "Monogram", "097": "Field Marks",
    "098": "Cradle", "099": "Post Reply", "101": "Liturgical", "102": "Reels",
    "103": "Brackets", "105": "Verse Cards", "106": "Python", "108": "Meteors",
    "109": "Subs", "110": "Album Art", "111": "Gap Analysis", "112": "Temptation",
    "114": "Posture", "115": "Basket", "116": "Latin", "117": "Mood Journal",
    "006": "Life Cal", "014": "Countdown", "022": "Haiku", "027": "Habits",
    "028": "Pixel Quest", "030": "Sleep", "036": "Sivam", "048": "Tilt Racer",
    "050": "Training", "051": "Pace + Log", "056": "Funnel", "062": "Restore",
    "064": "Zen Garden", "068": "Lessons", "071": "Payoff", "073": "3 Ways",
    "076": "Time Audit", "079": "Rosette", "081": "Desk Reset", "082": "Memory",
    "088": "Brew Math", "089": "Ink Trace", "091": "Grade Run", "095": "Contrast",
    "096": "Card Duel", "100": "Signal Desk", "104": "Giving Tree",
    "107": "Knot Locker", "113": "Pause",
    "118": "Mercy", "119": "Room Read", "120": "Chisel II", "121": "Vent + Burn",
    "122": "Cipher", "123": "Task Split", "124": "Reframe", "125": "Blockwork",
    "126": "Rubric", "127": "Nag Card", "128": "Sermon", "129": "Tap Color",
    "130": "Locus", "131": "Cloud Read", "132": "Brew Econ", "133": "Fasting",
    "134": "Anagram", "135": "Petal Post", "136": "Detour", "137": "Hurdles",
    "138": "Ferment Log", "139": "Sleep Mix", "140": "Delegate", "141": "Citation",
    "142": "Grain Garden", "143": "Commute", "144": "Bulletin", "145": "Story Seed",
    "146": "Saga Forge", "147": "Art Forge", "148": "World Forge", "149": "Story Forge",
    "150": "Saga Studio", "151": "Readers 2",
}

ANCHOR = re.compile(r"<meta[^>]*name=[\"']viewport[\"'][^>]*>", re.I)
HEAD_OPEN = re.compile(r"<head[^>]*>", re.I)
HEAD_CLOSE = re.compile(r"</head>", re.I)

# Every tag an app needs so that "Add to Home Screen" gives it its own icon,
# its own short name, and launches it full screen instead of in a Safari tab.
# Each entry is (detector, builder). A tag is inserted only if its detector
# finds nothing, so the patch is idempotent per tag and safely upgrades apps
# that already carry some of them (App 001 had only the first two).
TAGS = [
    (re.compile(r"rel=[\"']apple-touch-icon[\"']", re.I),
     lambda n, t: '<link rel="apple-touch-icon" href="%s/%s.png">' % (ICON_BASE, n)),
    (re.compile(r"name=[\"']apple-mobile-web-app-title[\"']", re.I),
     lambda n, t: '<meta name="apple-mobile-web-app-title" content="%s">' % t),
    (re.compile(r"name=[\"']apple-mobile-web-app-capable[\"']", re.I),
     lambda n, t: '<meta name="apple-mobile-web-app-capable" content="yes">'),
    (re.compile(r"name=[\"']mobile-web-app-capable[\"']", re.I),
     lambda n, t: '<meta name="mobile-web-app-capable" content="yes">'),
    (re.compile(r"name=[\"']apple-mobile-web-app-status-bar-style[\"']", re.I),
     lambda n, t: '<meta name="apple-mobile-web-app-status-bar-style" content="black">'),
]
HAS_ICON = TAGS[0][0]


def short_title(num, name):
    if num in TITLE:
        return TITLE[num]
    return name if len(name) <= 12 else name.split()[0][:12]


def missing_tags(html, num, name):
    t = escape(short_title(num, name), quote=True)
    return [build(num, t) for det, build in TAGS if not det.search(html)]


def patch(html, num, name):
    """Return html with any missing home screen tags added, html unchanged if
    nothing is missing, or None if there is no <head> to anchor to.
    Inserts after the last existing home screen tag, else after the viewport
    meta, else just inside <head>, else just before </head>."""
    tags = missing_tags(html, num, name)
    if not tags:
        return html
    ins = "".join("\n" + x for x in tags)
    pos = None
    for det, _ in TAGS:
        for m in det.finditer(html):
            e = html.find(">", m.end()) + 1
            pos = e if pos is None else max(pos, e)
    if pos is None:
        m = ANCHOR.search(html) or HEAD_OPEN.search(html)
        if m:
            pos = m.end()
    if pos is None:
        m = HEAD_CLOSE.search(html)
        if not m:
            return None
        return html[:m.start()] + ins.lstrip("\n") + "\n" + html[m.start():]
    return html[:pos] + ins + html[pos:]


def verify(html):
    """Exactly one of each tag."""
    return all(len(det.findall(html)) == 1 for det, _ in TAGS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="parent dir holding all app repos")
    ap.add_argument("--write", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--manifest", default="icons/manifest.json")
    args = ap.parse_args()

    apps = json.load(open(args.manifest, encoding="utf-8"))
    root = os.path.expanduser(args.root)

    patched, skipped, missing, failed = [], [], [], []

    for app in apps:
        num, slug, name = app["num"], app["slug"], app["name"]
        path = os.path.join(root, slug, "index.html")
        if not os.path.exists(path):
            missing.append("%s  %s" % (num, slug))
            continue
        html = open(path, encoding="utf-8").read()
        out = patch(html, num, name)
        if out is None:
            failed.append("%s  %s  (no <head> found)" % (num, slug))
            continue
        if out == html:
            skipped.append(num)
            continue
        assert verify(out), "%s: tag count wrong after patch" % num
        assert len(out) > len(html), "%s: patch shrank the file" % num
        if args.write:
            open(path, "w", encoding="utf-8").write(out)
        patched.append("%s  %-38s -> %s" % (num, slug, short_title(num, name)))

    mode = "WROTE" if args.write else "DRY RUN"
    print("%s  patched:%d  already-had:%d  repo-missing:%d  failed:%d\n"
          % (mode, len(patched), len(skipped), len(missing), len(failed)))
    for p in patched:
        print("  " + p)
    if missing:
        print("\nREPO NOT FOUND LOCALLY (clone these, or ignore if intentional):")
        for m in missing:
            print("  " + m)
    if failed:
        print("\nFAILED:")
        for f in failed:
            print("  " + f)
        sys.exit(1)


if __name__ == "__main__":
    main()
