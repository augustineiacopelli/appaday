#!/usr/bin/env python3
"""
Adds the Save to Phone tags to an app's index.html (see SAVE.md):

    <link rel="manifest" href="https://augustineiacopelli.github.io/appaday/manifests/NNN.webmanifest">
    <script src="https://augustineiacopelli.github.io/appaday/save.js" defer></script>

Idempotent per tag. Inserts directly after the apple-mobile-web-app-status-bar-style
meta (the last home screen tag), else just before </head>.

    python3 apply_save.py --root DIR            dry run over DIR/NNN.html or DIR/<slug>/index.html
    python3 apply_save.py --root DIR --write    patch in place
"""

import argparse
import json
import os
import re
import sys

BASE = "https://augustineiacopelli.github.io/appaday"
MANIFEST_RE = re.compile(r'<link[^>]+rel=["\']?manifest["\']?[^>]*>', re.I)
SAVE_RE = re.compile(r'<script[^>]+src=["\'][^"\']*/appaday/save\.js["\'][^>]*>\s*</script>', re.I)
ANCHOR_RE = re.compile(r'<meta[^>]+name=["\']apple-mobile-web-app-status-bar-style["\'][^>]*>', re.I)


def tags(num):
    return ('<link rel="manifest" href="%s/manifests/%s.webmanifest">' % (BASE, num),
            '<script src="%s/save.js" defer></script>' % BASE)


def patch(html, num):
    """Return patched html, the same html if complete, or None if no anchor exists."""
    man, scr = tags(num)
    add = []
    if not MANIFEST_RE.search(html):
        add.append(man)
    if not SAVE_RE.search(html):
        add.append(scr)
    if not add:
        return html
    ins = "".join("\n" + t for t in add)
    m = ANCHOR_RE.search(html)
    if m:
        return html[:m.end()] + ins + html[m.end():]
    i = html.lower().find("</head>")
    if i < 0:
        return None
    return html[:i] + ins.lstrip("\n") + "\n" + html[i:]


def verify(html, num):
    man, _ = tags(num)
    return (len(MANIFEST_RE.findall(html)) == 1 and man in html
            and len(SAVE_RE.findall(html)) == 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--manifest", default="icons/manifest.json")
    args = ap.parse_args()
    apps = json.load(open(args.manifest, encoding="utf-8"))
    changed = bad = 0
    for a in apps:
        cands = [os.path.join(args.root, a["num"] + ".html"),
                 os.path.join(args.root, a["slug"], "index.html")]
        path = next((p for p in cands if os.path.exists(p)), None)
        if not path:
            print("%s missing" % a["num"]); bad += 1; continue
        html = open(path, encoding="utf-8").read()
        out = patch(html, a["num"])
        if out is None or not verify(out, a["num"]):
            print("%s FAILED" % a["num"]); bad += 1; continue
        if out != html:
            changed += 1
            if args.write:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(out)
    print("%s: %d   failed: %d" % ("patched" if args.write else "would patch", changed, bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
