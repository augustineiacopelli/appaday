# Day 145 Story Seed. Key stored as a plain string under appaday-145-apikey.
# Planting a seed is a tap, so with no key the sheet opens and the user taps again.
LEGACY = "appaday-145-apikey"

EDITS = [
    ('''    <p class="sub">Stored only in this browser. Your key goes straight to Anthropic and nowhere else.</p>
    <label for="apiKey">Anthropic API key</label>
    <input class="text-input" id="apiKey" type="password" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
    <p class="small">Create one at console.anthropic.com.</p>
''', '''    <div id="keyMount"><p class="small">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''      <button class="ghost-btn" id="cancelSettings" type="button">Cancel</button>
      <button class="plant-btn" id="saveSettings" type="button">Save</button>''',
     '''      <button class="ghost-btn" id="cancelSettings" type="button">Cancel</button>
      <button class="plant-btn" id="saveSettings" type="button">Save</button>'''),
    ("const K_KEY = 'appaday-145-apikey';\n", ""),
    ("openSettings: $('openSettings'), apiKey: $('apiKey'), sessionName", "openSettings: $('openSettings'), sessionName"),
    ('''  els.apiKey.value = lsGet(K_KEY, '');
''', '''  if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));
'''),
    ("  setTimeout(() => (els.apiKey.value ? els.sessionName : els.apiKey).focus(), 50);\n", ""),
    ('''  const k = els.apiKey.value.trim();
  const s = els.sessionName.value.trim();
  if (k) lsSet(K_KEY, k); else lsDel(K_KEY);
''', '''  const s = els.sessionName.value.trim();
'''),
    ('''  const key = lsGet(K_KEY, '');
  if (!key) { const e = new Error('Add your Anthropic API key to plant a seed.'); e.settings = true; throw e; }''',
     '''  const key = window.AppKeys ? await window.AppKeys.get() : null;
  if (!key) { const e = new Error('Add your Claude API key to plant a seed.'); e.settings = true; throw e; }'''),
    ("  if (!lsGet(K_KEY, '')) { showNotice('Add your Anthropic API key to plant a seed.', true); return; }",
     "  if (!(window.AppKeys && window.AppKeys.has())) {\n    if (window.AppKeys) window.AppKeys.get();\n    showNotice('Add your Claude API key, then plant the seed again.', true);\n    return;\n  }"),
    ("[els.apiKey, els.sessionName].forEach(inp =>", "[els.sessionName].forEach(inp =>"),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'K_KEY', r'els\.apiKey', r"\$\('apiKey'\)"]
