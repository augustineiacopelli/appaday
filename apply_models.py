#!/usr/bin/env python3
"""
Moves every AI app onto models.js, so no app carries a Claude model ID of its own (see MODELS.md).
Modeled on apply_keys.py.

For every AI app in keys_inventory.json this:

    inserts the models.js tag directly after the save.js tag (not deferred, so window.AppModels
        exists before the app's inline script runs)
    removes the dead async getModel() boilerplate that fetched '../config.json' (that path is
        /config.json on GitHub Pages, which does not exist, so it always fell back), and puts back a
        one line shim on top of AppModels only when the app still calls getModel()
    rewrites model constants and literal model fields to ask AppModels by tier
    applies the app's recipe from RECIPES below for anything app specific
    rewrites model IDs in README.md to plain tier wording

Idempotent. Every recipe edit is assert guarded. Each patched app is validated before it is written:

    exactly one models.js tag, directly after the save.js tag
    no Claude model ID literal left anywhere in index.html
    no inline script gains a node --check error (classic scripts checked as classic scripts)
    no non ASCII characters beyond the ones the file already had

    python3 apply_models.py --root DIR                   dry run over DIR/<slug>/index.html
    python3 apply_models.py --root DIR --write           patch in place
    python3 apply_models.py --root DIR --only 063,072
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

BASE = "https://augustineiacopelli.github.io/appaday"
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS_TAG = '<script src="%s/models.js"></script>' % BASE
MODELS_RE = re.compile(r'<script[^>]+src=["\'][^"\']*/appaday/models\.js["\'][^>]*>\s*</script>', re.I)
SAVE_RE = re.compile(r'<script[^>]+src=["\'][^"\']*/appaday/save\.js["\'][^>]*>\s*</script>', re.I)
SCRIPT_RE = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)
MODEL_ID_RE = re.compile(r'claude-(?:haiku|sonnet|opus|fable)[a-z0-9.-]*')

BOILERPLATE_RE = re.compile(
    r"\n?[ \t]*async function getModel\(tier = '[a-z]+'\)\s*\{\s*try\s*\{[^{}]*?config\.json[^{}]*?\}\s*catch\s*(?:\([^)]*\)\s*)?\{[^{}]*?\}\s*\}[ \t]*\n?")
SHIM = ("async function getModel(tier) { return window.AppModels ? window.AppModels.get(tier || 'sonnet') : ''; }")

def guard(tier, q="'"):
    return "(window.AppModels ? window.AppModels.id(%s%s%s) : %s%s)" % (q, tier, q, q, q)

# ---------------------------------------------------------------- recipes
KIT_EDITS = [
    ("    Kit.getModel(tier): Settings tier override, then ../config.json, then the portal config.json, then fallback.\n",
     "    Kit.getModel(tier): Settings tier override, then the portal models.js (config.json) for that tier.\n", 1, "optional"),
    ("model is getModel(tier) (Settings override, then ../config.json, then fallback)",
     "model is getModel(tier) (Settings override, then the portal models.js)", 1, "optional"),
    (None, "KIT_MODELS"),
    ("Leave blank to use the portfolio config.json, then the built-in default.",
     "Leave blank to use the portfolio default for that tier."),
    ("placeholder=\"' + MODEL_FALLBACK[t] + '\">",
     "placeholder=\"' + (window.AppModels ? window.AppModels.id(t) : '') + '\">"),
]
KIT_MODELS_RE = re.compile(
    r"  var MODEL_FALLBACK = \{[^\n]*\};\n  var configPromise = null;\n  function loadConfig\(\) \{.*?\n  \}\n"
    r"  // Standard AppADay getModel\(tier\): Settings override, then \.\./config\.json, then fallback\.\n"
    r"  async function getModel\(tier\) \{\n    tier = tier \|\| 'sonnet';\n    var override = Kit\.settings\.get\(\)\.tiers\[tier\];\n"
    r"    if \(override\) return override;\n    try \{ var c = await loadConfig\(\);[^\n]*\n    return MODEL_FALLBACK\[tier\] \|\| MODEL_FALLBACK\.sonnet;\n  \}\n", re.S)
KIT_MODELS_NEW = (
    "  // Standard AppADay getModel(tier): Settings override, then the portal models.js (config.json).\n"
    "  async function getModel(tier) {\n    tier = tier || 'sonnet';\n    var override = Kit.settings.get().tiers[tier];\n"
    "    if (override) return override;\n    return window.AppModels ? window.AppModels.get(tier) : '';\n  }\n")

RECIPES = {
    "063": [
        ('  var CLAUDE_MODEL = "claude-sonnet-5";\n', '  var DEFAULT_TIER = "sonnet";\n'),
        ("  /* Output ceilings. Sonnet 5 and Opus 4.8 spend part of this budget on thinking\n",
         "  /* Output ceilings. Sonnet and Opus spend part of this budget on thinking\n"),
        ('''  var MODELS = [
    {
      id: "claude-sonnet-5",
      name: "Sonnet 5",
      cost: "Baseline cost",
      note: "The default. On search-and-reason benchmarks it lands within half a point of Opus, for a fraction of the price."
    },
    {
      id: "claude-opus-4-8",
      name: "Opus 4.8",
      cost: "About 2.5x",
      note: "Sharper judgment. Worth the money for a Researcher brief, or when the provenance grades have to be right."
    },
    {
      id: "claude-sonnet-4-6",
      name: "Sonnet 4.6",
      cost: "About 1.5x",
      note: "The previous default across AppADay. Kept for parity, and for keys without access to the newer models."
    }
  ];
''', '''  /* Entries are tiers. The model ID and the name shown come from the portal models.js, so a new
     model reaches this list without editing this file. */
  var MODELS = [
    {
      id: "sonnet",
      cost: "Baseline cost",
      note: "The default. Close to Opus on search-and-reason work, for a fraction of the price."
    },
    {
      id: "opus",
      cost: "About 2.5x",
      note: "Sharper judgment. Worth the money for a Researcher brief, or when the provenance grades have to be right."
    }
  ];
  function modelId(tier) { return window.AppModels ? window.AppModels.id(tier) : ""; }
'''),
        ('''  function getModel() {
    var v = lsGet(LS.model);
    return modelIds().indexOf(v) > -1 ? v : CLAUDE_MODEL;
  }
''', '''  /* Returns the chosen tier. Older versions saved a model ID; AppModels maps it to its tier. */
  function getModel() {
    var v = lsGet(LS.model) || DEFAULT_TIER;
    if (window.AppModels) { v = window.AppModels.tier(v); }
    return modelIds().indexOf(v) > -1 ? v : DEFAULT_TIER;
  }
'''),
        ('''    for (var i = 0; i < MODELS.length; i++) {
      if (MODELS[i].id === id) { return MODELS[i].name; }
    }
    return id || CLAUDE_MODEL;
''', '''    return window.AppModels ? window.AppModels.label(id || DEFAULT_TIER) : (id || DEFAULT_TIER);
'''),
        ("model: getModel(),", "model: modelId(getModel()),", 2),
        ("'<span class=\"m-head\"><span class=\"m-name\">' + esc(m.name) + \"</span>\" +",
         "'<span class=\"m-head\"><span class=\"m-name\">' + esc(modelName(m.id)) + \"</span>\" +"),
    ],
    "072": [
        ('''        <option value="claude-sonnet-5">Sonnet 5 &mdash; balanced (default)</option>
        <option value="claude-opus-4-8">Opus 4.8 &mdash; sharpest, for tricky jobs</option>
        <option value="claude-haiku-4-5-20251001">Haiku 4.5 &mdash; fastest, simplest fixes</option>
''', '''        <option value="sonnet" data-model-tier="sonnet" data-note="balanced (default)">Sonnet</option>
        <option value="opus" data-model-tier="opus" data-note="sharpest, for tricky jobs">Opus</option>
        <option value="haiku" data-model-tier="haiku" data-note="fastest, simplest fixes">Haiku</option>
'''),
        ("const CLAUDE_MODEL = 'claude-sonnet-5';\n", "const DEFAULT_TIER = 'sonnet';\n"),
        ("$('modelSel').value = localStorage.getItem(LS_MODEL) || CLAUDE_MODEL;", "$('modelSel').value = getTier();"),
        ("function getModel(){ return localStorage.getItem(LS_MODEL) || CLAUDE_MODEL; }\n",
         "/* The saved choice is a tier; older saves held a model ID, which AppModels maps to its tier. */\n"
         "function getTier(){ var t = localStorage.getItem(LS_MODEL) || DEFAULT_TIER; return window.AppModels ? window.AppModels.tier(t) : t; }\n"
         "function getModel(){ return window.AppModels ? window.AppModels.id(getTier()) : ''; }\n"),
        ("  job.model = getModel();\n", "  job.model = getTier();\n"),
    ],
    "086": [
        ('<div class="readout" id="modelReadout">claude-sonnet-5</div>', '<div class="readout" id="modelReadout" data-model-id="sonnet"></div>'),
    ],
    "126": [
        ("header set to true. The model is pinned in the CLAUDE_MODEL constant at the top of the\nscript block, currently claude-sonnet-5. ",
         "header set to true. The model comes from the portal models.js (the sonnet tier of\nconfig.json), so it follows the current model without editing this file. "),
    ],
    "146": KIT_EDITS, "147": KIT_EDITS, "148": KIT_EDITS, "149": KIT_EDITS,
    "153": [
        ("  var MODEL_FALLBACK = { haiku: 'claude-haiku-4-5-20251001', sonnet: 'claude-sonnet-5' };\n", ""),
        (None, "153_MODELS"),
    ],
    "160": [
        ('''async function getDefaultModel() {
  try { const r = await fetch('https://augustineiacopelli.github.io/appaday/config.json', { cache: 'no-cache' }); const c = await r.json(); return c.models.sonnet; }
  catch (e) { return 'claude-sonnet-5-5'; }
}''', '''async function getDefaultModel() {
  return window.AppModels ? window.AppModels.get('sonnet') : '';
}'''),
    ],
    "170": [
        ("var CONFIG_URL = 'https://augustineiacopelli.github.io/appaday/config.json';\n", ""),
        ('''async function getModel(tier) {
  tier = tier || 'sonnet';
  if (modelCache[tier]) return modelCache[tier];
  var m = 'claude-sonnet-5-5';
  try {
    var r = await fetch(CONFIG_URL, { cache: 'no-cache' });
    var c = await r.json();
    if (c && c.models && typeof c.models[tier] === 'string' && c.models[tier]) m = c.models[tier];
  } catch (e) { m = 'claude-sonnet-5-5'; }
  modelCache[tier] = m;
  return m;
}''', '''async function getModel(tier) {
  return window.AppModels ? window.AppModels.get(tier || 'sonnet') : '';
}'''),
        ("var modelCache = {};\n", ""),
    ],
}

RE_153 = re.compile(
    r"  // ---- model selection ----\n  var configPromise = null;\n  function loadConfig\(\) \{.*?\n  \}\n  async function getModel\(tier\) \{.*?\n  \}\n", re.S)
NEW_153 = ("  // ---- model selection ----\n  // The model for each tier comes from the portal models.js (config.json).\n"
           "  async function getModel(tier) {\n    return window.AppModels ? window.AppModels.get(tier || 'sonnet') : '';\n  }\n")

# ---------------------------------------------------------------- helpers
class PatchError(Exception):
    pass


def apply_recipe(num, s):
    for item in RECIPES.get(num, []):
        old, new = item[0], item[1]
        if old is None:
            if new == "KIT_MODELS":
                if "MODEL_FALLBACK" not in s:
                    continue
                s, n = KIT_MODELS_RE.subn(lambda m: KIT_MODELS_NEW, s)
                if n != 1:
                    raise PatchError("kit models block: expected 1 match, found %d" % n)
            elif new == "153_MODELS":
                if "loadConfig" not in s:
                    continue
                s, n = RE_153.subn(lambda m: NEW_153, s)
                if n != 1:
                    raise PatchError("153 models block: expected 1 match, found %d" % n)
            continue
        want = item[2] if len(item) > 2 else 1
        if new in s and old not in s:
            continue  # already applied
        if len(item) > 3 and item[3] == "optional" and old not in s:
            continue
        c = s.count(old)
        if c != want:
            raise PatchError("recipe edit: expected 1 match, found %d: %r" % (c, old[:70]))
        s = s.replace(old, new)
    return s


def generic(s):
    # 1. the promise fix left by the key ring retrofit, then dead boilerplate getModel() definitions
    s = re.sub(r"\n[ \t]*getModel\(\)\.then\(function \(m\) \{ if \(m\) CLAUDE_MODEL = m; \}\);", "", s)
    calls_before = len(re.findall(r'(?<!function )\bgetModel\(', s))
    pos = None
    m = BOILERPLATE_RE.search(s)
    while m:
        if pos is None:
            pos = m.start()
        s = s[:m.start()] + "\n" + s[m.end():]
        m = BOILERPLATE_RE.search(s)
    if pos is not None:
        still_called = re.search(r'(?<!function )(?<!\.)\bgetModel\(', s)
        has_def = re.search(r'function getModel\(', s)
        if still_called and not has_def:
            s = s[:pos] + "\n" + SHIM + "\n" + s[pos:].lstrip("\n")
    # 2. a shim nothing calls any more
    if SHIM in s and not re.search(r'(?<!function )(?<!\.)\bgetModel\(', s.replace(SHIM, '')):
        s = s.replace("\n" + SHIM + "\n", "\n").replace(SHIM, "")
    # 3. model constants: var/let/const CLAUDE_MODEL = 'claude-...'
    s = re.sub(r"\b(var|let|const)(\s+CLAUDE_MODEL\s*=\s*)(['\"])claude-(haiku|sonnet|opus|fable)[a-z0-9.-]*\3",
               lambda m: m.group(1) + m.group(2) + guard(m.group(4), m.group(3)), s)
    #    object properties: CLAUDE_MODEL_X: "claude-..."
    s = re.sub(r"\b(CLAUDE_MODEL[A-Z_]*\s*:\s*)(['\"])claude-(haiku|sonnet|opus|fable)[a-z0-9.-]*\2",
               lambda m: m.group(1) + guard(m.group(3), m.group(2)), s)
    # 4. literal model fields in request bodies
    s = re.sub(r"\b(model\s*:\s*)(['\"])claude-(haiku|sonnet|opus|fable)[a-z0-9.-]*\2",
               lambda m: m.group(1) + guard(m.group(3), m.group(2)), s)
    return s


def node_errors(s):
    errs = []
    for i, m in enumerate(SCRIPT_RE.finditer(s)):
        attrs, body = m.group(1), m.group(2)
        if 'src=' in attrs or not body.strip():
            continue
        if re.search(r'type=["\']?(importmap|application/json|text/plain|application/ld\+json)', attrs):
            continue
        ext = '.mjs' if 'module' in attrs else '.cjs'
        fd, p = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, 'w') as f:
            f.write(body)
        r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
        os.unlink(p)
        if r.returncode:
            msg = [l for l in r.stderr.splitlines() if 'Error' in l]
            errs.append('script %d: %s' % (i, msg[0] if msg else r.stderr.strip()[:120]))
    return errs


TIER_WORD = {"haiku": "Haiku", "sonnet": "Sonnet", "opus": "Opus", "fable": "Fable"}
README_SPAN_RE = re.compile(r"`(?:const CLAUDE_MODEL = )?'?(claude-(haiku|sonnet|opus|fable)[a-z0-9.-]*)'?`")
README_BARE_RE = re.compile(r"\bclaude-(haiku|sonnet|opus|fable)[a-z0-9.-]*")


def readme(s):
    s = README_SPAN_RE.sub(lambda m: "the current Claude %s model" % TIER_WORD[m.group(2)], s)
    s = README_BARE_RE.sub(lambda m: "the current Claude %s model" % TIER_WORD[m.group(1)], s)
    return s


def process(num, path, write):
    s0 = open(path, encoding='utf-8').read()
    s = s0
    if not SAVE_RE.search(s):
        raise PatchError("no save.js tag")
    if not MODELS_RE.search(s):
        m = SAVE_RE.search(s)
        s = s[:m.end()] + "\n" + MODELS_TAG + s[m.end():]
    s = apply_recipe(num, s)
    s = generic(s)
    # validation
    tags = MODELS_RE.findall(s)
    if len(tags) != 1:
        raise PatchError("models.js tag count %d" % len(tags))
    if not re.search(SAVE_RE.pattern + r"\s*" + MODELS_RE.pattern, s, re.I):
        raise PatchError("models.js tag is not directly after save.js")
    left = sorted(set(MODEL_ID_RE.findall(s)))
    if left:
        raise PatchError("model IDs left: %s" % ", ".join(left))
    before = set(e.split(':', 1)[1] for e in node_errors(s0))
    after = node_errors(s)
    new_errs = [e for e in after if e.split(':', 1)[1] not in before]
    if new_errs:
        raise PatchError("; ".join(new_errs))
    if after:
        raise PatchError("still broken: " + "; ".join(after))
    na0 = sum(1 for c in s0 if ord(c) > 127)
    na1 = sum(1 for c in s if ord(c) > 127)
    if na1 > na0:
        raise PatchError("non ASCII grew from %d to %d" % (na0, na1))
    changed = s != s0
    rpath = os.path.join(os.path.dirname(path), "README.md")
    r_changed = False
    if os.path.exists(rpath):
        r0 = open(rpath, encoding='utf-8').read()
        r1 = readme(r0)
        r_changed = r1 != r0
    if write:
        if changed:
            open(path, 'w', encoding='utf-8').write(s)
        if r_changed:
            open(rpath, 'w', encoding='utf-8').write(r1)
    return changed, r_changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    inv = json.load(open(os.path.join(HERE, "keys_inventory.json")))
    only = set(x.strip() for x in args.only.split(",") if x.strip())
    stats = {"patched": 0, "done": 0, "failed": 0}
    for a in inv["apps"]:
        num = a["num"]
        if only and num not in only:
            continue
        path = os.path.join(args.root, a["slug"], "index.html")
        if not os.path.exists(path):
            print("%s MISSING  %s" % (num, a["slug"])); stats["failed"] += 1; continue
        try:
            ch, rch = process(num, path, args.write)
        except PatchError as e:
            print("%s FAILED  %s" % (num, e)); stats["failed"] += 1; continue
        if ch or rch:
            stats["patched"] += 1
            print("%s %s %s%s" % (num, "patched" if args.write else "would patch", a["slug"], " (+README)" if rch else ""))
        else:
            stats["done"] += 1
    print("%s: %d   already done: %d   failed: %d" % ("patched" if args.write else "would patch", stats["patched"], stats["done"], stats["failed"]))
    sys.exit(1 if stats["failed"] else 0)


if __name__ == "__main__":
    main()
