# Day 035 Meeting Distiller. Key stored as a plain string under md_apikey.
LEGACY = "md_apikey"

EDITS = [
    ('''      <div class="modal-field">
        <label>Anthropic API Key</label>
        <input class="modal-input" type="password" id="apiKeyInput" placeholder="sk-ant-...">
      </div>
''',
     '''      <div class="modal-field"><div id="keyMount"><label>The key manager is loading. If this stays, check your connection and reload.</label></div></div>
'''),
    ("  var SK_APIKEY    = 'md_apikey';\n", ""),
    ("    document.getElementById('apiKeyInput').value = sGet(SK_APIKEY) || '';\n",
     "    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));\n"),
    ("    sSet(SK_APIKEY, document.getElementById('apiKeyInput').value.trim());\n", ""),
    ('''    var apiKey = sGet(SK_APIKEY);
    if (!apiKey) { showError('Add your Anthropic API key in \\u2699\\uFE0F Settings first.'); return; }
''',
     '''    var apiKey = window.AppKeys ? await window.AppKeys.get() : null;
    if (!apiKey) { showError('Add your Claude API key with the gear button to continue.'); return; }
'''),
]

FORBID = [r'apiKeyInput', r'SK_APIKEY']
