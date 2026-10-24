# Day 040 Kitchen Tamer. Key stored as a plain string under kt_api_key.
LEGACY = "kt_api_key"

EDITS = [
    ('''    <div class="field-group">
      <label class="field-label" for="apiKeyInput">API Key <span class="hint">Stored only on this device</span></label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
    </div>
''',
     '''    <div class="field-group"><div id="keyMount"><span class="hint">The key manager is loading. If this stays, check your connection and reload.</span></div></div>
'''),
    ("  document.getElementById('apiKeyInput').value = localStorage.getItem('kt_api_key') || '';\n",
     "  if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));\n"),
    ("  var key = document.getElementById('apiKeyInput').value.trim();\n", ""),
    ("  if (key) { localStorage.setItem('kt_api_key', key); } else { localStorage.removeItem('kt_api_key'); }\n", ""),
    ('''  var apiKey = localStorage.getItem('kt_api_key');
  if (!apiKey) { showError('Add your Claude API key in \\u2699 Settings first.'); return; }
''',
     '''  var apiKey = window.AppKeys ? await window.AppKeys.get() : null;
  if (!apiKey) { showError('Add your Claude API key with the gear button to continue.'); return; }
'''),
]

FORBID = [r'apiKeyInput', r'kt_api_key']
