# Day 126 Rubric Builder. Key stored as a plain string under rubricBuilder_apiKey.
LEGACY = "rubricBuilder_apiKey"

EDITS = [
    ('''    <p class="subtext">Stored only in this browser. Never leaves your device except in the request to Claude.</p>

    <div class="field">
      <label for="apiKeyInput">Claude API key</label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-...">
    </div>
''', '''    <div class="field" id="keyMount"><p class="subtext">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''      <button class="secondary-btn" id="closeSettingsBtn" type="button">Cancel</button>
      <button class="primary-btn" id="saveSettingsBtn" type="button" style="width:auto; margin-top:0;">Save</button>''',
     '''      <button class="secondary-btn" id="closeSettingsBtn" type="button">Cancel</button>
      <button class="primary-btn" id="saveSettingsBtn" type="button" style="width:auto; margin-top:0;">Save</button>'''),
    ("  const apiKeyInput = document.getElementById('apiKeyInput');\n", ""),
    ('''      const savedKey = localStorage.getItem('rubricBuilder_apiKey');
      const savedSession = localStorage.getItem('rubricBuilder_sessionName');
      if (savedKey) apiKeyInput.value = savedKey;
''', '''      const savedSession = localStorage.getItem('rubricBuilder_sessionName');
'''),
    ("      localStorage.setItem('rubricBuilder_apiKey', apiKeyInput.value.trim());\n", ""),
    ('''  function getApiKey() {
    try {
      return localStorage.getItem('rubricBuilder_apiKey') || '';
    } catch (err) {
      return '';
    }
  }

''', ''),
    ('''    const apiKey = getApiKey();
    if (!apiKey) {
      setStatus(generateStatus, 'error', 'Add your Claude API key in Settings first.');
      settingsOverlay.classList.add('open');
      return;
    }
''', '''    if (!window.AppKeys) {
      setStatus(generateStatus, 'error', 'The key manager did not load. Check your connection and reload.');
      return;
    }
    const apiKey = await window.AppKeys.get();
    if (!apiKey) {
      setStatus(generateStatus, 'error', 'Add your Claude API key with the Settings button to continue.');
      return;
    }
'''),
    ('''  settingsBtn.addEventListener('click', function () {
    loadSettings();
''', '''  settingsBtn.addEventListener('click', function () {
    loadSettings();
    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
'''),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\n  getModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'getApiKey', r'apiKeyInput', r'rubricBuilder_apiKey']
