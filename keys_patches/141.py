# Day 141 Court of Honor Citation. Key stored as a plain string under appaday-141-apikey.
# The key is optional (built in templates without it), so a missing key never opens the sheet.
LEGACY = "appaday-141-apikey"

EDITS = [
    ('''    <label for="apiKey">Anthropic API key</label>
    <input type="password" id="apiKey" autocomplete="off" spellcheck="false">
    <p class="hint">Stored only in this browser. Without a key, citations come from built in templates.</p>
''', '''    <div id="keyMount"><p class="hint">The key manager is loading. If this stays, check your connection and reload.</p></div>
    <p class="hint">Without a key, citations come from built in templates.</p>
'''),
    ("const LS_KEY = 'appaday-141-apikey';\n", ""),
    ("settings:$('settings'), apiKey:$('apiKey'), sessionName:$('sessionName'),", "settings:$('settings'), sessionName:$('sessionName'),"),
    ("  const key = (lsGet(LS_KEY) || '').trim();\n  if (!key) {",
     "  const key = (window.AppKeys && window.AppKeys.has()) ? await window.AppKeys.get() : null;\n  if (!key) {"),
    ("Template citation. Add an API key in Settings for a personalized one.", "Template citation. Add a Claude API key in Settings for a personalized one."),
    ('''  el.apiKey.value = lsGet(LS_KEY) || '';
  el.sessionName.value = lsGet(LS_SESSION) || '';
  el.settings.hidden = false;
  el.apiKey.focus();''', '''  if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));
  el.sessionName.value = lsGet(LS_SESSION) || '';
  el.settings.hidden = false;'''),
    ("  const ok = lsSet(LS_KEY, el.apiKey.value.trim()) && lsSet(LS_SESSION, el.sessionName.value.trim());",
     "  const ok = lsSet(LS_SESSION, el.sessionName.value.trim());"),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'LS_KEY', r'el\.apiKey', r"\$\('apiKey'\)"]
