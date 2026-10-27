#!/usr/bin/env python3
"""AppADay weekly health check.

Reads the APPS array from the portal index.html, then for every live app
checks that the app page loads, that its head carries exactly one of each
of the seven required tags (five home screen icon tags plus the two Save to
Phone tags) with the right app number, that its icon, install icons and
manifest are live, and that its portal entry carries kw search keywords.
Every AI app (listed in keys_inventory.json, or calling api.anthropic.com)
must also carry exactly one keys.js tag with data-app set to its number and
exactly one models.js tag, and must not carry a Claude model ID of its own
(models come from models.js by tier; see MODELS.md). The EMBED table in
models.js must match config.json. Where node is installed, every app's inline
scripts must also parse as classic scripts, which catches the top level await
that blanked eleven apps in October 2026.

Run by .github/workflows/health-check.yml every Monday, or by hand:
    python3 health_check.py            # check the live GitHub Pages site
    python3 health_check.py --offline  # app HTML from raw GitHub, assets from this repo
Exits 1 and writes health_report.md when anything fails.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://augustineiacopelli.github.io/appaday/"
OFFLINE = "--offline" in sys.argv
UA = {"User-Agent": "AppADay-health-check"}

REQUIRED = [
    ("apple-touch-icon", r'<link[^>]+rel="apple-touch-icon"[^>]*>'),
    ("apple-mobile-web-app-title", r'<meta[^>]+name="apple-mobile-web-app-title"[^>]*>'),
    ("apple-mobile-web-app-capable", r'<meta[^>]+name="apple-mobile-web-app-capable"[^>]*>'),
    ("mobile-web-app-capable", r'<meta[^>]+name="mobile-web-app-capable"[^>]*>'),
    ("apple-mobile-web-app-status-bar-style", r'<meta[^>]+name="apple-mobile-web-app-status-bar-style"[^>]*>'),
    ("manifest", r'<link[^>]+rel="manifest"[^>]*>'),
    ("save.js", r'<script[^>]+src="[^"]*/appaday/save\.js"[^>]*>'),
]


def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, b""
            last = e.code
        except Exception as e:  # network blip, retry
            last = str(e)
        time.sleep(2 * (i + 1))
    return last, b""

KEYS_TAG = r'<script[^>]+src="[^"]*/appaday/keys\.js"[^>]*>'


def ai_nums():
    try:
        inv = json.load(open(os.path.join(ROOT, "keys_inventory.json"), encoding="utf-8"))
        return {a["num"] for a in inv["apps"] if a.get("ai")}
    except (OSError, ValueError, KeyError):
        return set()


AI_NUMS = ai_nums()


def load_apps():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    start = html.index("const APPS = [")
    end = html.index("\n];", start)
    block = html[start:end]
    apps = []
    for chunk in re.split(r"\n  \{", block)[1:]:
        def field(name):
            m = re.search(r"\b" + name + r'\s*:\s*"([^"]*)"', chunk)
            return m.group(1) if m else ""
        apps.append({
            "num": field("num"),
            "name": field("name"),
            "url": field("url"),
            "kw": field("kw"),
            "soon": bool(re.search(r"coming_soon\s*:\s*true", chunk)),
        })
    return apps


MODELS_TAG = r'<script[^>]+src="[^"]*/appaday/models\.js"[^>]*>'
MODEL_ID = re.compile(r'claude-(?:haiku|sonnet|opus|fable)-[a-z0-9.-]*')
SCRIPT_RE = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)
NODE = shutil.which("node")


def script_errors(text):
    """Inline scripts that fail node --check, parsed the way the browser parses them."""
    if not NODE:
        return []
    out = []
    for i, m in enumerate(SCRIPT_RE.finditer(text)):
        attrs, body = m.group(1), m.group(2)
        if "src=" in attrs or not body.strip() or re.search(r'type=["\']?(importmap|application/(ld\+)?json)', attrs):
            continue
        fd, path = tempfile.mkstemp(suffix=".mjs" if "module" in attrs else ".cjs")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(body)
        r = subprocess.run([NODE, "--check", path], capture_output=True, text=True)
        os.unlink(path)
        if r.returncode:
            msg = [l for l in r.stderr.splitlines() if "Error" in l]
            out.append("inline script %d does not parse: %s" % (i, msg[0] if msg else "syntax error"))
    return out


def models_problems():
    """models.js EMBED must equal config.json, so first loads and offline loads are current."""
    try:
        if OFFLINE:
            js = open(os.path.join(ROOT, "models.js"), encoding="utf-8").read()
            cfg = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
        else:
            js = fetch(SITE + "models.js")[1].decode("utf-8", "replace")
            cfg = json.loads(fetch(SITE + "config.json")[1].decode("utf-8"))
    except Exception as e:
        return ["models.js or config.json could not be read: %s" % e]
    probs = []
    m = re.search(r"var EMBED = \{\s*lastUpdated: '([^']+)',\s*models: \{([^}]*)\},\s*labels: \{([^}]*)\}", js)
    if not m:
        return ["models.js has no EMBED table"]
    pairs = lambda t: dict(re.findall(r"(\w+): '([^']*)'", t))
    if m.group(1) != cfg.get("lastUpdated"):
        probs.append("models.js lastUpdated %s differs from config.json %s" % (m.group(1), cfg.get("lastUpdated")))
    if pairs(m.group(2)) != cfg.get("models"):
        probs.append("models.js EMBED models differ from config.json models")
    if pairs(m.group(3)) != cfg.get("labels"):
        probs.append("models.js EMBED labels differ from config.json labels")
    return probs


def asset_ok(path):
    if OFFLINE:
        return 200 if os.path.isfile(os.path.join(ROOT, path)) else 404
    return fetch(SITE + path)[0]


def check(app):
    num, url, problems = app["num"], app["url"], []
    if not app["kw"].strip():
        problems.append("portal entry has no kw search keywords")
    if not url:
        return num, app["name"], url, problems + ["no url in APPS entry"]

    if OFFLINE:
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        page = "https://raw.githubusercontent.com/augustineiacopelli/%s/main/index.html" % slug
    else:
        page = url
    status, body = fetch(page)
    if status != 200:
        problems.append("app page returned %s" % status)
    else:
        head = body.decode("utf-8", "replace").split("</head>", 1)[0]
        for label, pat in REQUIRED:
            n = len(re.findall(pat, head, re.I))
            if n != 1:
                problems.append("%s tag appears %d times" % (label, n))
        text = body.decode("utf-8", "replace")
        if num in AI_NUMS or "api.anthropic.com" in text:
            tags = re.findall(KEYS_TAG, head, re.I)
            if len(tags) != 1:
                problems.append("AI app: keys.js tag appears %d times" % len(tags))
            elif not re.search(r'data-app="%s"' % re.escape(num), tags[0]):
                problems.append("AI app: keys.js data-app does not match %s" % num)
            n = len(re.findall(MODELS_TAG, head, re.I))
            if n != 1:
                problems.append("AI app: models.js tag appears %d times" % n)
            ids = sorted(set(MODEL_ID.findall(text)))
            if ids:
                problems.append("AI app: carries its own model ID (%s) instead of asking models.js" % ", ".join(ids))
        problems.extend(script_errors(text))
        m = re.search(r'rel="apple-touch-icon"[^>]*href="([^"]+)"', head) or \
            re.search(r'href="([^"]+)"[^>]*rel="apple-touch-icon"', head)
        if m and not m.group(1).endswith("/icons/%s.png" % num):
            problems.append("apple-touch-icon points at " + m.group(1))
        m = re.search(r'rel="manifest"[^>]*href="([^"]+)"', head) or \
            re.search(r'href="([^"]+)"[^>]*rel="manifest"', head)
        if m and not m.group(1).endswith("/manifests/%s.webmanifest" % num):
            problems.append("manifest points at " + m.group(1))

    for path in ("icons/%s.png" % num, "icons/192/%s.png" % num,
                 "icons/512/%s.png" % num, "manifests/%s.webmanifest" % num):
        s = asset_ok(path)
        if s != 200:
            problems.append("%s returned %s" % (path, s))
    return num, app["name"], url, problems


def main():
    apps = [a for a in load_apps() if not a["soon"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = sorted(pool.map(check, apps))
    mp = models_problems()
    if mp:
        results.append(("000", "Portal models.js", SITE + "models.js", mp))
    bad = [r for r in results if r[3]]
    print("Checked %d apps, %d with problems." % (len(results), len(bad)))
    if not bad:
        if os.path.exists("health_report.md"):
            os.remove("health_report.md")
        return 0
    lines = ["%d of %d AppADay apps failed the weekly health check.\n" % (len(bad), len(results))]
    for num, name, url, problems in bad:
        lines.append("**%s %s** %s" % (num, name, url))
        lines.extend("  - " + p for p in problems)
        lines.append("")
    report = "\n".join(lines)
    open("health_report.md", "w").write(report)
    print(report)
    return 1


if __name__ == "__main__":
    sys.exit(main())
