# Day 144 Bulletin Brief. Key stored as a plain string under appaday-144-apikey.
LEGACY = "appaday-144-apikey"

EDITS = [
    ('''  <label class="field" for="apiKey">Anthropic API key</label>
  <input type="password" id="apiKey" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
  <p class="hint">Stored only in this browser's localStorage and sent only to api.anthropic.com.</p>
''', '''  <div id="keyMount"><p class="hint">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("const LS_KEY = 'appaday-144-apikey';\n", ""),
    ("  $('apiKey').value = lsGet(LS_KEY) || '';\n", "  if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ("  setTimeout(function(){ $('apiKey').focus(); }, 50);\n", ""),
    ('''  const key = lsGet(LS_KEY);
  if (!key) { openSettings('Add your Anthropic API key to generate a brief.'); return; }
  const pasted''', '''  if (!window.AppKeys) { setMsg('inputMsg', 'The key manager did not load. Check your connection and reload.', 'err'); return; }
  const key = await window.AppKeys.get();
  if (!key) { setMsg('inputMsg', 'Add your Claude API key with the Settings button to generate a brief.', 'err'); return; }
  const pasted'''),
    ('''    const k = $('apiKey').value.trim();
    const s = $('sessionName').value.trim();
    const ok1 = k ? lsSet(LS_KEY, k) : (function(){ try { localStorage.removeItem(LS_KEY); return true; } catch (e) { return false; } })();
    const ok2 = lsSet(LS_SESSION, s);
    if (!ok1 || !ok2) {''', '''    const s = $('sessionName').value.trim();
    const ok2 = lsSet(LS_SESSION, s);
    if (!ok2) {'''),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'LS_KEY', r"\$\('apiKey'\)"]
