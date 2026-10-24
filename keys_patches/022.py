# Day 022 Haiku Engine. Key stored as a plain string under haiku_api_key.
LEGACY = "haiku_api_key"

EDITS = [
    ('''    <div class="settings-group">
      <span class="settings-group-label">Anthropic API Key</span>
      <input type="password" class="settings-input" id="apiKeyInput" placeholder="sk-ant-…" autocomplete="off">
      <p class="settings-hint">Your key is stored in session memory only and never sent anywhere except Anthropic's API.</p>
    </div>
''',
     '''    <div class="settings-group"><div id="keyMount"><p class="settings-hint">The key manager is loading. If this stays, check your connection and reload.</p></div></div>
'''),
    ("  const apiKeyInput    = document.getElementById('apiKeyInput');\n", ""),
    ("  const storedKey   = localStorage.getItem('haiku_api_key');\n", ""),
    ("  if (storedKey)   apiKeyInput.value   = storedKey;\n", ""),
    ('''  function openSettings() {
    settingsPanel.classList.add('open');''',
     '''  function openSettings() {
    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
    settingsPanel.classList.add('open');'''),
    ("    const key = apiKeyInput.value.trim();\n    const email = defaultEmailInput.value.trim();\n    if (key)   localStorage.setItem('haiku_api_key', key);\n",
     "    const email = defaultEmailInput.value.trim();\n"),
    ("    const apiKey = localStorage.getItem('haiku_api_key') || apiKeyInput.value.trim();\n", ""),
    ('''    if (!apiKey) {
      openSettings();
      return;
    }
''',
     '''    const apiKey = window.AppKeys ? await window.AppKeys.get() : null;
    if (!apiKey) {
      errorMsg.textContent = 'Add your Claude API key with the gear button to continue.';
      errorMsg.classList.add('active');
      return;
    }
'''),
]

FORBID = [r'apiKeyInput', r'storedKey', r'getItem\(.haiku_api_key']
