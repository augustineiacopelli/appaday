# Day 019 Tone Translator. Key stored as a plain string under tt_apiKey.
LEGACY = "tt_apiKey"

EDITS = [
    ('''    <div class="field">
      <label>Anthropic API Key</label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-…" autocomplete="off">
    </div>
''',
     '''    <div class="field"><div id="keyMount"><p style="font-size:.85rem;opacity:.75;margin:0">The key manager is loading. If this stays, check your connection and reload.</p></div></div>
'''),
    ("  let apiKey = localStorage.getItem('tt_apiKey') || '';\n", ""),
    ('''    if (apiKey) { document.getElementById('apiKeyInput').value = apiKey; updateConfigDot(); }
    if (email)  { document.getElementById('emailInput').value  = email; }''',
     '''    updateConfigDot();
    if (email)  { document.getElementById('emailInput').value  = email; }'''),
    ('''    if (apiKey) { btn.classList.add('configured'); dot.title = 'API key set'; }
    else        { btn.classList.remove('configured'); }
  }
''',
     '''    if (window.AppKeys && window.AppKeys.has()) { btn.classList.add('configured'); dot.title = 'API key set'; }
    else        { btn.classList.remove('configured'); }
  }
  window.addEventListener('appaday:keychange', updateConfigDot);
  document.addEventListener('DOMContentLoaded', updateConfigDot);
'''),
    ('''  function openSettings() {
    document.getElementById('settingsOverlay').classList.add('open');''',
     '''  function openSettings() {
    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
    document.getElementById('settingsOverlay').classList.add('open');'''),
    ('''    apiKey = document.getElementById('apiKeyInput').value.trim();
    email  = document.getElementById('emailInput').value.trim();
    localStorage.setItem('tt_apiKey', apiKey);
''',
     '''    email  = document.getElementById('emailInput').value.trim();
'''),
    ("    if (!apiKey) { document.getElementById('noKeyBanner').classList.add('show'); return; }",
     "    const apiKey = window.AppKeys ? await window.AppKeys.get() : null;\n    if (!apiKey) { document.getElementById('noKeyBanner').classList.add('show'); return; }"),
]

FORBID = [r'apiKeyInput', r'getItem\(.tt_apiKey']
