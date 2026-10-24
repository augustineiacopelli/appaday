# Day 128 Sermon Note Catcher. Key lives inside a JSON settings object (sermonNoteCatcherSettings) as apiKey.
# The AI refine step is opt in, so a missing key skips it quietly instead of opening the key sheet.
LEGACY = "sermonNoteCatcherSettings:apiKey"

EDITS = [
    ('''    <div class="field-group">
      <label for="settingsApiKey">Claude API key</label>
      <input type="password" id="settingsApiKey" placeholder="sk-ant-...">
      <p class="small-note">Stored only on this device. Never shown on the main screen.</p>
    </div>
''', '''    <div class="field-group" id="keyMount"><p class="small-note">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("    var defaults = { email: '', apiKey: '', aiEnabled: false };", "    var defaults = { email: '', aiEnabled: false };"),
    ("        apiKey: parsed.apiKey || '',\n", ""),
    ('''    if (settings.aiEnabled && settings.apiKey) {
      refineWithAI(parsed, settings);''', '''    if (settings.aiEnabled && window.AppKeys && window.AppKeys.has()) {
      refineWithAI(parsed, settings);'''),
    ('''  async function refineWithAI(parsedText, settings) {
    setAIStatus('Refining with AI...');
    try {''', '''  async function refineWithAI(parsedText, settings) {
    setAIStatus('Refining with AI...');
    try {
      var apiKey = await window.AppKeys.get();
      if (!apiKey) { setAIStatus(''); return; }'''),
    ("          'x-api-key': settings.apiKey,", "          'x-api-key': apiKey,"),
    ('''  document.getElementById('btnSettingsHeader').addEventListener('click', openSettings);''',
     '''  document.getElementById('btnSettingsHeader').addEventListener('click', function () {
    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
    openSettings();
  });'''),
    ("      apiKey: document.getElementById('settingsApiKey').value.trim(),\n", ""),
    ("    document.getElementById('settingsApiKey').value = settings.apiKey;\n", ""),
]

FORBID = [r'settingsApiKey', r'settings\.apiKey']
