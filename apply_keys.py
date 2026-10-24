#!/usr/bin/env python3
"""
Moves an AI app onto the API key ring (see KEYS.md). Modeled on apply_save.py.

For every AI app in keys_inventory.json this inserts the keys.js tag directly
after the save.js tag and applies the app's recipe from keys_patches/NNN.py:

    LEGACY = "old_storage_name"       value for data-legacy-key ("" when the app never stored a key)
    EDITS  = [(old, new), ...]        exact replacements; each old must occur exactly once
    FIXES  = [(old, new), ...]        fixes for bugs that predate the key ring; applied only with --with-fixes
    FORBID = [r"regex", ...]          patterns that must be gone from the final file

Idempotent: an app that already carries the keys.js tag is left alone. Every
edit is assert guarded, so a recipe that no longer matches the file fails loudly
and changes nothing. Each patched app is validated before it is written:

    the keys.js tag appears exactly once and data-app matches the number
    data-accent is the category color from icons/manifest.json
    no inline script gains a node --check error (classic scripts are checked as
        classic scripts, so a top level await is caught; errors the app already had
        are reported as "still broken" until a FIXES entry repairs them)
    no non ASCII characters beyond the ones the file already had
    the old plain string storage name no longer appears as a quoted literal
    none of the recipe's FORBID patterns match

    python3 apply_keys.py --root DIR                     dry run over DIR/<slug>/index.html
    python3 apply_keys.py --root DIR --write             patch in place
    python3 apply_keys.py --root DIR --only 004,005      limit to some apps
    python3 apply_keys.py --root DIR --with-fixes        also apply FIXES

Apps with no recipe are listed as NO RECIPE and are never touched.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import importlib.util

BASE = "https://augustineiacopelli.github.io/appaday"
HERE = os.path.dirname(os.path.abspath(__file__))
KEYS_RE = re.compile(r'<script[^>]+src=["\'][^"\']*/appaday/keys\.js["\'][^>]*>\s*</script>', re.I)
SAVE_RE = re.compile(r'<script[^>]+src=["\'][^"\']*/appaday/save\.js["\'][^>]*>\s*</script>', re.I)
MANIFEST_RE = re.compile(r'<link[^>]+rel=["\']?manifest["\']?[^>]*>', re.I)
SCRIPT_RE = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)


class PatchError(Exception):
    pass


def tag(num, color, legacy):
    parts = ['<script src="%s/keys.js"' % BASE, 'data-app="%s"' % num]
    if legacy:
        parts.append('data-legacy-key="%s"' % legacy)
    parts.append('data-accent="%s"' % color)
    parts.append("defer></script>")
    return " ".join(parts)


def load_recipe(num):
    path = os.path.join(HERE, "keys_patches", num + ".py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("recipe_" + num, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def inline_scripts(html):
    out = []
    for m in SCRIPT_RE.finditer(html):
        attrs, body = m.group(1), m.group(2)
        if re.search(r"\bsrc\s*=", attrs, re.I):
            continue
        t = re.search(r'type\s*=\s*["\']?([\w/+\-]+)', attrs, re.I)
        t = t.group(1).lower() if t else ""
        if t and t not in ("text/javascript", "module", "application/javascript"):
            continue
        out.append((t == "module", body))
    return out


def syntax_errors(html):
    errs = []
    for i, (is_module, body) in enumerate(inline_scripts(html)):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "b%d.%s" % (i, "mjs" if is_module else "js"))
            with open(p, "w", encoding="utf-8") as f:
                f.write(body)
            cmd = ["node"] + ([] if is_module else ["--no-experimental-detect-module"]) + ["--check", p]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode:
                lines = [l for l in r.stderr.strip().split("\n") if l.strip()]
                errs.append("script %d: %s" % (i, " | ".join(lines[:4])[:300]))
    return errs


def non_ascii_count(s):
    return sum(1 for c in s if ord(c) > 127)


def apply_edits(html, edits, label):
    for n, e in enumerate(edits, 1):
        old, new = e[0], e[1]
        want = e[2] if len(e) > 2 else 1
        have = html.count(old)
        if have != want:
            raise PatchError("%s edit %d: expected %d match, found %d: %r" % (label, n, want, have, old[:80]))
        html = html.replace(old, new)
    return html


def insert_tag(html, num, color, legacy):
    t = tag(num, color, legacy)
    m = SAVE_RE.search(html)
    if m:
        return html[:m.end()] + "\n" + t + html[m.end():]
    m = MANIFEST_RE.search(html)
    if m:
        return html[:m.end()] + "\n" + t + html[m.end():]
    i = html.lower().find("</head>")
    if i < 0:
        raise PatchError("no save.js tag, manifest link, or </head> to anchor the keys.js tag")
    return html[:i] + t + "\n" + html[i:]


def validate(html, original, num, color, recipe):
    problems = []
    tags = KEYS_RE.findall(html)
    if len(tags) != 1:
        problems.append("keys.js tag appears %d times" % len(tags))
    else:
        m = re.search(r'data-app="(\d+)"', tags[0])
        if not m or m.group(1) != num:
            problems.append("data-app does not match %s" % num)
        m = re.search(r'data-accent="([^"]+)"', tags[0])
        if not m or m.group(1).lower() != color.lower():
            problems.append("data-accent is not %s" % color)
    if len(SAVE_RE.findall(html)) != 1:
        problems.append("save.js tag count changed")
    # Only syntax errors the patch introduced count. An app that was already broken keeps
    # its old error until a FIXES entry repairs it, and apply_keys reports that separately.
    before = set(syntax_errors(original))
    problems.extend(e for e in syntax_errors(html) if e not in before)
    if non_ascii_count(html) > non_ascii_count(original):
        problems.append("new non ASCII characters: %d" % (non_ascii_count(html) - non_ascii_count(original)))
    stripped = KEYS_RE.sub("", html)
    # Plain string keys must be gone. A name:field spec points into a JSON object that
    # usually keeps other settings, so the recipe's FORBID patterns cover those instead.
    legacy = [s.strip() for s in recipe.LEGACY.split(",") if s.strip() and ":" not in s]
    for name in legacy:
        if re.search(r"""['"`]%s['"`]""" % re.escape(name), stripped):
            problems.append("old storage name %r is still referenced" % name)
    for pat in getattr(recipe, "FORBID", []):
        if re.search(pat, stripped):
            problems.append("forbidden pattern still present: %s" % pat)
    if "AppKeys" not in stripped:
        problems.append("app never calls AppKeys")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--with-fixes", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--inventory", default=os.path.join(HERE, "keys_inventory.json"))
    ap.add_argument("--manifest", default=os.path.join(HERE, "icons", "manifest.json"))
    args = ap.parse_args()

    inv = json.load(open(args.inventory, encoding="utf-8"))["apps"]
    colors = {a["num"]: a["color"] for a in json.load(open(args.manifest, encoding="utf-8"))}
    only = set(x.strip() for x in args.only.split(",") if x.strip())
    changed = skipped = bad = norecipe = 0
    for a in inv:
        num = a["num"]
        if only and num not in only:
            continue
        path = os.path.join(args.root, a["slug"], "index.html")
        if not os.path.exists(path):
            print("%s missing" % num); bad += 1; continue
        with open(path, encoding="utf-8", newline="") as f:
            html = f.read()
        if KEYS_RE.search(html):
            skipped += 1
            continue
        recipe = load_recipe(num)
        if recipe is None:
            print("%s NO RECIPE  %s" % (num, a["slug"])); norecipe += 1; continue
        try:
            out = apply_edits(html, recipe.EDITS, "recipe")
            if args.with_fixes:
                out = apply_edits(out, getattr(recipe, "FIXES", []), "fix")
            out = insert_tag(out, num, colors[num], recipe.LEGACY)
            problems = validate(out, html, num, colors[num], recipe)
        except PatchError as e:
            print("%s FAILED  %s" % (num, e)); bad += 1; continue
        if problems:
            print("%s FAILED  %s" % (num, "; ".join(problems))); bad += 1; continue
        changed += 1
        left = syntax_errors(out)
        if left:
            print("%s NOTE  still broken after patch (pre-existing): %s" % (num, left[0][:140]))
        if args.write:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(out)
    print("%s: %d   already done: %d   no recipe: %d   failed: %d"
          % ("patched" if args.write else "would patch", changed, skipped, norecipe, bad))
    sys.exit(1 if bad or norecipe else 0)


if __name__ == "__main__":
    main()
