#!/usr/bin/env python3
"""
AppADay icon retrofit, Windows-friendly, no cloning.

Patches index.html in all 117 app repos through the GitHub Contents API using
the GitHub CLI for authentication. Nothing is downloaded to your machine except
the file contents held in memory.

    gh auth status                          confirm you are logged in
    python retrofit_icons.py                DRY RUN, writes nothing
    python retrofit_icons.py --push         actually commit
    python retrofit_icons.py --push --only 001 007

Idempotent. Any repo whose index.html already contains apple-touch-icon is
skipped, so re-running after shipping a new app touches only the new one.

If you would rather have local clones, use --mode clone instead.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys

OWNER = "augustineiacopelli"
ICON_BASE = "https://augustineiacopelli.github.io/appaday/icons"
COMMIT_MSG = "Add apple-touch-icon and home screen title"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from apply_icons import patch, short_title, HAS_ICON  # noqa: E402


def gh(*args, check=True):
    """Run a gh command and return stdout. Uses shell=True on Windows so
    the gh.exe shim on PATH resolves the same way it does in a terminal."""
    proc = subprocess.run(
        ["gh"] + list(args),
        capture_output=True, text=True,
        shell=(os.name == "nt"),
    )
    if check and proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip())
    return proc.stdout


def preflight():
    try:
        gh("auth", "status")
    except FileNotFoundError:
        sys.exit("GitHub CLI not found. Install it with:  winget install GitHub.cli")
    except RuntimeError as e:
        sys.exit("GitHub CLI is installed but not authenticated.\n"
                 "Run:  gh auth login\n\n" + str(e))


def get_file(repo, path="index.html"):
    """Returns (text, sha) or (None, None) if the file or repo is absent."""
    out = gh("api", "repos/%s/%s/contents/%s" % (OWNER, repo, path), check=False)
    if not out.strip():
        return None, None
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return None, None
    if "content" not in data:
        return None, None
    return base64.b64decode(data["content"]).decode("utf-8"), data["sha"]


def put_file(repo, text, sha, path="index.html"):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    gh("api", "--method", "PUT",
       "repos/%s/%s/contents/%s" % (OWNER, repo, path),
       "-f", "message=" + COMMIT_MSG,
       "-f", "content=" + encoded,
       "-f", "sha=" + sha)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="commit (default is dry run)")
    ap.add_argument("--only", nargs="*", help="limit to these app numbers")
    ap.add_argument("--manifest", default="icons/manifest.json")
    args = ap.parse_args()

    preflight()

    apps = json.load(open(args.manifest, encoding="utf-8"))
    if args.only:
        apps = [a for a in apps if a["num"] in args.only]
    if not apps:
        sys.exit("No apps selected.")

    done, already, absent, failed = [], [], [], []

    for i, app in enumerate(apps, 1):
        num, slug, name = app["num"], app["slug"], app["name"]
        prefix = "[%3d/%d] %s" % (i, len(apps), num)
        try:
            html, sha = get_file(slug)
        except RuntimeError as e:
            failed.append("%s %s  (read error: %s)" % (num, slug, e)); continue

        if html is None:
            absent.append("%s  %s" % (num, slug))
            print("%s  no index.html found" % prefix); continue
        if HAS_ICON.search(html):
            already.append(num)
            print("%s  already has icon, skipped" % prefix); continue

        out = patch(html, num, name)
        if out is None:
            failed.append("%s %s  (no </head>)" % (num, slug)); continue
        if out.count("apple-touch-icon") != 1 or len(out) <= len(html):
            failed.append("%s %s  (sanity check failed)" % (num, slug)); continue

        if args.push:
            try:
                put_file(slug, out, sha)
            except RuntimeError as e:
                failed.append("%s %s  (write error: %s)" % (num, slug, e))
                print("%s  FAILED" % prefix); continue
            print("%s  committed -> %s" % (prefix, short_title(num, name)))
        else:
            print("%s  would patch -> %s" % (prefix, short_title(num, name)))
        done.append(num)

    verb = "committed" if args.push else "would patch"
    print("\n%s:%d  already-had:%d  no-file:%d  failed:%d"
          % (verb, len(done), len(already), len(absent), len(failed)))
    if absent:
        print("\nNO index.html AT REPO ROOT:")
        for a in absent:
            print("  " + a)
    if failed:
        print("\nFAILED:")
        for f in failed:
            print("  " + f)
        sys.exit(1)
    if not args.push:
        print("\nDry run. Nothing was written. Re-run with --push to commit.")


if __name__ == "__main__":
    main()
