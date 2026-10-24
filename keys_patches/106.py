# Day 106 Python Discombobulator. Key stored as a plain string under pyExplainer_apiKey.
LEGACY = "pyExplainer_apiKey"

EDITS = [
    ('''    <div class="field">
      <label for="apiKeyInput">Anthropic API Key</label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-...">
    </div>
''',
     '''    <div class="field" id="keyMount"><label class="small-note">The key manager is loading. If this stays, check your connection and reload.</label></div>
'''),
    ("    <label class=\"small-note\">Your key is stored only in this browser's local storage. It is never sent anywhere except directly to Anthropic's API.</label>\n", ""),
    ("const apiKeyInput = document.getElementById('apiKeyInput');\n", ""),
    ('''    const key = localStorage.getItem('pyExplainer_apiKey');
    const session = localStorage.getItem('pyExplainer_sessionName');
    if (key) apiKeyInput.value = key;
''', '''    const session = localStorage.getItem('pyExplainer_sessionName');
'''),
    ("    localStorage.setItem('pyExplainer_apiKey', apiKeyInput.value.trim());\n", ""),
    ('''function getStoredKey() {
  try {
    return localStorage.getItem('pyExplainer_apiKey') || '';
  } catch (e) {
    console.error('localStorage read failed', e);
    return '';
  }
}

''', ''),
    ('''  const apiKey = getStoredKey();
  if (!apiKey) {
    renderOutput('No API key found. Open Settings (gear icon) and add your Anthropic API key first.', true);
    return;
  }
  if (!state.rawText || !state.rawText.trim()) {
    renderOutput('Paste some Python code or a traceback before submitting.', true);
    return;
  }
''', '''  if (!state.rawText || !state.rawText.trim()) {
    renderOutput('Paste some Python code or a traceback before submitting.', true);
    return;
  }
  const apiKey = window.AppKeys ? await window.AppKeys.get() : null;
  if (!apiKey) {
    renderOutput('Add your Claude API key with the gear button, then submit again.', true);
    return;
  }
'''),
    ('''gearBtn.addEventListener('click', function() {
  settingsOverlay.classList.add('show');''', '''gearBtn.addEventListener('click', function() {
  if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
  settingsOverlay.classList.add('show');'''),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'getStoredKey', r'apiKeyInput', r'pyExplainer_apiKey']
