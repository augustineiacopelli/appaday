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
}

ANCHOR = re.compile(r"<meta[^>]*name=[\"']viewport[\"'][^>]*>", re.I)
HAS_ICON = re.compile(r"apple-touch-icon", re.I)
HEAD_CLOSE = re.compile(r"</head>", re.I)


def short_title(num, name):
    if num in TITLE:
        return TITLE[num]
    return name if len(name) <= 12 else name.split()[0][:12]


def block(num, name):
    return (
        '\n<link rel="apple-touch-icon" href="%s/%s.png">'
        '\n<meta name="apple-mobile-web-app-title" content="%s">'
        % (ICON_BASE, num, short_title(num, name))
    )


def patch(html, num, name):
    """Insert after the viewport meta, or fall back to just before </head>."""
    tag = block(num, name)
    m = ANCHOR.search(html)
    if m:
        return html[:m.end()] + tag + html[m.end():]
    m = HEAD_CLOSE.search(html)
    if not m:
        return None
    return html[:m.start()] + tag + "\n" + html[m.start():]


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
        if HAS_ICON.search(html):
            skipped.append(num)
            continue
        out = patch(html, num, name)
        if out is None:
            failed.append("%s  %s  (no </head> found)" % (num, slug))
            continue
        assert out.count("apple-touch-icon") == 1, "%s: duplicate insert" % num
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
