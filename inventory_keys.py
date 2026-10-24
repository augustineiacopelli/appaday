#!/usr/bin/env python3
"""
Inventory of AI apps for the API key ring retrofit (see KEYS.md).

For every app listed in icons/manifest.json this fetches the app's index.html
from raw.githubusercontent.com, marks it as an AI app when the source contains
api.anthropic.com, works out how the app stored its API key before the key
ring (the legacy storage name and whether the value is a plain string or a
JSON object with a field), and writes keys_inventory.json.

    python3 -I inventory_keys.py --cache /home/claude/apps
    python3 -I inventory_keys.py --cache /home/claude/apps --offline   # reuse the cache, no network

Apps that already carry the keys.js tag (Day 170) are recorded as done and
skipped by apply_keys.py. Anything the heuristics cannot read with confidence
gets needs_review true plus the reasons, and goes to the hand patch list.

The cache directory holds untrusted downloaded HTML. It is never the working
directory and nothing in it is executed.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "AppADay-inventory-keys"}
RAW = "https://raw.githubusercontent.com/augustineiacopelli/%s/main/index.html"
AUTO_FIELDS = ["apiKey", "api_key", "anthropicKey", "anthropic_api_key", "claudeKey", "key"]
KEYWORDS = re.compile(r"api[_\-\s]?key|anthropic|claude|x-api-key|apikey", re.I)
KEYS_TAG_RE = re.compile(r'<script[^>]+src=["\'][^"\']*/appaday/keys\.js["\'][^>]*>', re.I)

LS_LITERAL = re.compile(
    r"""localStorage\s*\.\s*(getItem|setItem|removeItem)\s*\(\s*(['"`])([^'"`$\\]+)\2""")
LS_IDENT = re.compile(
    r"""localStorage\s*\.\s*(getItem|setItem|removeItem)\s*\(\s*([A-Za-z_$][\w$.]*)\s*[,)]""")
CONST_STR = re.compile(r"""(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(['"`])([^'"`$\\]+)\2""")
CONST_PROP = re.compile(r"""\b([A-Za-z_$][\w$]*)\s*:\s*(['"`])([^'"`$\\]+)\2""")
XAPI = re.compile(r"""['"]x-api-key['"]\s*:\s*([^,}\n]+)""")
FETCH_ANTH = re.compile(r"fetch\s*\(\s*[^)]*api\.anthropic\.com[^)]*\)|api\.anthropic\.com")


def fetch(url, tries=3):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, b""
            last = e.code
        except Exception as e:
            last = str(e)
    return last, b""


def resolve_constants(src):
    """Map identifier -> string literal for const/var declarations and object properties."""
    consts = {}
    for m in CONST_STR.finditer(src):
        consts.setdefault(m.group(1), m.group(3))
    props = {}
    for m in CONST_PROP.finditer(src):
        props.setdefault(m.group(1), m.group(3))
    return consts, props


def storage_sites(src):
    """List of (op, name, position) for every localStorage access whose name can be resolved."""
    consts, props = resolve_constants(src)
    sites = []
    for m in LS_LITERAL.finditer(src):
        sites.append((m.group(1), m.group(3), m.start()))
    for m in LS_IDENT.finditer(src):
        ident = m.group(2)
        name = consts.get(ident)
        if name is None and "." in ident:
            name = props.get(ident.split(".")[-1])
        if name:
            sites.append((m.group(1), name, m.start()))
    return sites


def classify(src, name, sites):
    """Decide plain or json for a storage name, and the field if json."""
    form, field, notes = "unknown", None, []
    for op, n, pos in sites:
        if n != name:
            continue
        before = src[max(0, pos - 80):pos]
        after = src[pos:pos + 420]
        if op == "getItem":
            if "JSON.parse" in before:
                form = "json"
                m = re.search(r"\.\s*(%s)\b|\[\s*['\"](%s)['\"]\s*\]" %
                              ("|".join(AUTO_FIELDS), "|".join(AUTO_FIELDS)), after)
                if m:
                    field = m.group(1) or m.group(2)
                else:
                    m = re.search(r"\.\s*([A-Za-z_$][\w$]*[Kk]ey[\w$]*)\b", after)
                    if m:
                        field = m.group(1)
            else:
                # Plain read, unless the value is parsed on a following line.
                if re.search(r"JSON\.parse\s*\(\s*[A-Za-z_$][\w$]*\s*\)", after[:200]) and form == "unknown":
                    form = "json"
                elif form != "json":
                    form = "plain"
        elif op == "setItem":
            if re.match(r"localStorage\s*\.\s*setItem\s*\([^,]+,\s*JSON\.stringify", after):
                if form != "json":
                    form = "json"
            elif form == "unknown":
                form = "plain"
    return form, field, notes


def analyze(num, slug, src):
    rec = {"num": num, "slug": slug, "ai": False, "done": False,
           "legacy": [], "legacy_spec": "", "form": None,
           "needs_review": False, "reasons": [],
           "has_callClaude": False, "anthropic_fetches": 0,
           "x_api_key_exprs": [], "bytes": len(src.encode("utf-8"))}
    if "api.anthropic.com" not in src:
        return rec
    rec["ai"] = True
    rec["done"] = bool(KEYS_TAG_RE.search(src))
    if rec["done"]:
        return rec
    rec["has_callClaude"] = bool(re.search(r"function\s+callClaude\s*\(|callClaude\s*=\s*(async\s*)?(function|\()", src))
    rec["anthropic_fetches"] = len(FETCH_ANTH.findall(src))
    rec["x_api_key_exprs"] = sorted(set(x.strip() for x in XAPI.findall(src)))

    if re.search(r"sk-ant-[A-Za-z0-9_\-]{10,}", src):
        rec["needs_review"] = True
        rec["reasons"].append("source contains what looks like a literal API key")

    sites = storage_sites(src)
    names = {}
    for op, n, pos in sites:
        ctx = src[max(0, pos - 260):pos + 260]
        score = 0
        if KEYWORDS.search(n):
            score += 2
        if KEYWORDS.search(ctx):
            score += 1
        if score >= 2 or (score >= 1 and KEYWORDS.search(n)):
            names.setdefault(n, 0)
            names[n] += score
    # keep names whose accesses are really about the key (name has a key-like word, or strong context)
    strong = [n for n, s in names.items() if KEYWORDS.search(n) or s >= 6]
    strong = sorted(set(strong))
    specs = []
    forms = []
    for n in strong:
        form, field, _ = classify(src, n, sites)
        forms.append(form)
        if form == "json":
            if field and field not in AUTO_FIELDS:
                specs.append("%s:%s" % (n, field))
            elif field:
                specs.append(n)
            else:
                rec["needs_review"] = True
                rec["reasons"].append("JSON storage %r but no key field found" % n)
                specs.append(n)
        else:
            if form == "unknown":
                rec["needs_review"] = True
                rec["reasons"].append("storage %r form unclear" % n)
            specs.append(n)
    rec["legacy"] = strong
    rec["legacy_spec"] = ",".join(specs)
    rec["form"] = forms[0] if len(set(forms)) == 1 and forms else ("mixed" if forms else None)

    if not strong:
        rec["needs_review"] = True
        rec["reasons"].append("no legacy storage name found")
    if len(strong) > 1:
        rec["needs_review"] = True
        rec["reasons"].append("several candidate storage names: " + ", ".join(strong))
    if not rec["x_api_key_exprs"]:
        rec["needs_review"] = True
        rec["reasons"].append("no x-api-key header found")
    if not rec["has_callClaude"]:
        rec["needs_review"] = True
        rec["reasons"].append("no callClaude function")
    if rec["anthropic_fetches"] > 1:
        rec["needs_review"] = True
        rec["reasons"].append("%d references to api.anthropic.com" % rec["anthropic_fetches"])
    return rec


def load_one(args):
    a, cache, offline = args
    path = os.path.join(cache, a["slug"], "index.html")
    if offline:
        if not os.path.exists(path):
            return a, None, "missing from cache"
        return a, open(path, encoding="utf-8").read(), None
    status, body = fetch(RAW % a["slug"])
    if status != 200:
        return a, None, "fetch returned %s" % status
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(body)
    return a, body.decode("utf-8", "replace"), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="directory for DIR/<slug>/index.html copies")
    ap.add_argument("--manifest", default="icons/manifest.json")
    ap.add_argument("--out", default="keys_inventory.json")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    apps = json.load(open(args.manifest, encoding="utf-8"))
    os.makedirs(args.cache, exist_ok=True)
    jobs = [(a, args.cache, args.offline) for a in apps]
    with ThreadPoolExecutor(max_workers=8) as pool:
        loaded = list(pool.map(load_one, jobs))

    records, failures = [], []
    for a, src, err in loaded:
        if err:
            failures.append((a["num"], a["slug"], err))
            continue
        records.append(analyze(a["num"], a["slug"], src))
    records.sort(key=lambda r: r["num"])

    ai = [r for r in records if r["ai"]]
    todo = [r for r in ai if not r["done"]]
    review = [r for r in todo if r["needs_review"]]
    out = {"count_apps": len(apps), "count_fetched": len(records),
           "count_ai": len(ai), "count_done": len(ai) - len(todo),
           "count_todo": len(todo), "count_needs_review": len(review),
           "fetch_failures": [{"num": n, "slug": s, "error": e} for n, s, e in failures],
           "apps": ai}
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=True)
        f.write("\n")

    print("apps in manifest: %d   fetched: %d   AI apps: %d   already done: %d   to patch: %d   needs review: %d"
          % (len(apps), len(records), len(ai), len(ai) - len(todo), len(todo), len(review)))
    for n, s, e in failures:
        print("FETCH FAILED %s %s: %s" % (n, s, e))
    for r in review:
        print("REVIEW %s %s: %s" % (r["num"], r["slug"], "; ".join(r["reasons"])))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
