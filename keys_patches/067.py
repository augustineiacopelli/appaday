# Day 067 Thought Chisel. Key stored as a plain string under tc_api_key.
# FIXES repairs a bug that predates the key ring: a top level await in a classic script
# is a syntax error, so the page script never ran.
LEGACY = "tc_api_key"

EDITS = [
    ('''    <div class="field">
      <label>Claude API Key</label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-..." autocomplete="off">
    </div>
''',
     '''    <div class="field"><div id="keyMount"><label>The key manager is loading. If this stays, check your connection and reload.</label></div></div>
'''),
    ('''async function callClaude(messages) {
  const apiKey = localStorage.getItem('tc_api_key') || '';
''',
     '''async function callClaude(messages) {
  const apiKey = window.AppKeys ? await window.AppKeys.get() : null;
'''),
    ('''  if (!speechSupported || !recognition) return;
  const apiKey = localStorage.getItem('tc_api_key') || '';
  if (!apiKey) {
    state.error = 'API key not set. Tap the gear icon to add your Claude API key.';
    render();
    return;
  }
''',
     '''  if (!speechSupported || !recognition) return;
  if (!(window.AppKeys && window.AppKeys.has())) {
    if (window.AppKeys) window.AppKeys.get();
    state.error = 'API key not set. Add your Claude API key, then tap the microphone again.';
    render();
    return;
  }
'''),
    ("  document.getElementById('apiKeyInput').value = localStorage.getItem('tc_api_key') || '';\n",
     "  if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));\n"),
    ('''  const key = document.getElementById('apiKeyInput').value.trim();
  if (key) localStorage.setItem('tc_api_key', key);
  else localStorage.removeItem('tc_api_key');

''', ""),
]

FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'apiKeyInput', r'tc_api_key']
