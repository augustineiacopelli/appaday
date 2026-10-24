# Day 090 Syllabus Skimmer. Key stored as a plain string under appaday090-key.
LEGACY = "appaday090-key"

EDITS = [
    ('''    <div class="field">
      <label for="key">Anthropic API key</label>
      <input id="key" type="password" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
      <div class="hint">Get one at <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">console.anthropic.com</a>.</div>
    </div>
''',
     '''    <div class="field" id="keyMount"><div class="hint">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ("  var K_KEY = 'appaday090-key';\n", ""),
    ("var keyIn = $('key'), sessIn = $('session');", "var sessIn = $('session');"),
    ("  function hasKey() { return load(K_KEY, '').trim().length > 0; }",
     "  function hasKey() { return !!(window.AppKeys && window.AppKeys.has()); }"),
    ("    keyIn.value = load(K_KEY, '');\n",
     "    if (window.AppKeys) { window.AppKeys.mountSettings($('keyMount')); }\n"),
    ("    setTimeout(function () { keyIn.focus(); }, 40);\n", ""),
    ("    save(K_KEY, keyIn.value.trim());\n", ""),
    ('''  testBtn.addEventListener('click', function () {
    var key = keyIn.value.trim();
    if (!key) { testOut.innerHTML = '<div class="notice">Paste a key first.</div>'; return; }''',
     '''  testBtn.addEventListener('click', async function () {
    var key = hasKey() ? await window.AppKeys.get() : '';
    if (!key) { testOut.innerHTML = '<div class="notice">Add a key above first.</div>'; return; }'''),
    ('''  function skim() {
    var text = ta.value.trim();''', '''  async function skim() {
    var text = ta.value.trim();'''),
    ("    if (!hasKey()) { showNotice('Add your Anthropic API key in Settings first.'); openSettings(); return; }\n",
     '''    if (!window.AppKeys) { showNotice('The key manager did not load. Check your connection and reload.'); return; }
    var apiKey = await window.AppKeys.get();
    if (!apiKey) { showNotice('Add your Claude API key with the gear button to start skimming.'); return; }
'''),
    ("        'x-api-key': load(K_KEY, ''),", "        'x-api-key': apiKey,"),
    ('''    if (!hasKey()) {
      showNotice('Add your Anthropic API key in Settings (the gear, top right) to start skimming.', 'info');
    } else if (!storageOK) {
      showNotice('This browser is not letting the page save anything, so your key will be forgotten when the tab closes. ' +
        'Everything still works for this session.', 'info', 'Settings will not persist');
    }
    if (!storageOK && !hasKey()) {
      showNotice('This page cannot save to browser storage, which usually means it was opened straight from disk ' +
        'rather than over http. Your key will work for this session but will not be remembered. Add it in Settings ' +
        'to continue.', 'info', 'Storage unavailable');
    }
''', '''    window.addEventListener('appaday:keychange', markGear);
    document.addEventListener('DOMContentLoaded', function () {
      markGear();
      if (!hasKey()) {
        showNotice('Add your Claude API key with the gear button (top right) to start skimming.', 'info');
      }
    });
'''),
]

FORBID = [r'K_KEY', r'keyIn\b', r"\$\('key'\)"]
