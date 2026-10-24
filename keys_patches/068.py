# Day 068 Ten Lessons. Key stored as a plain string under tl_api_key.
LEGACY = "tl_api_key"

EDITS = [
    ('''    <div class="field">
      <label>Claude API Key</label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-..." autocomplete="off">
      <div class="hint">Get one at <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">console.anthropic.com</a>. Stored locally, never uploaded anywhere but Anthropic.</div>
    </div>
''',
     '''    <div id="keyMount"><div class="hint">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ('''      <button class="btn-cancel" onclick="closeSettings()">Close</button>
      <button class="btn-save" onclick="saveSettings()">Save key</button>''',
     '''      <button class="btn-save" onclick="closeSettings()">Close</button>'''),
    ("const LS_KEY = 'tl_api_key';\n", ""),
    ("const getKey = () => { try { return localStorage.getItem(LS_KEY) || ''; } catch (e) { return ''; } };\n", ""),
    ('''  const key = getKey();
  if (!key) throw new Error('NO_KEY');''',
     '''  const key = window.AppKeys ? await window.AppKeys.get() : null;
  if (!key) throw new Error('NO_KEY');'''),
    ('''  if (!getKey()) { openSettings(); toast('Add your Claude API key to build a course.'); return; }''',
     '''  if (!window.AppKeys) { toast('The key manager did not load. Check your connection and reload.'); return; }
  if (!window.AppKeys.has()) { window.AppKeys.get(); toast('Add your Claude API key, then tap build again.'); return; }'''),
    ('''  if (!getKey()) { toast('Add your Claude API key to open a lesson.'); openSettings(); return; }''',
     '''  if (!window.AppKeys) { toast('The key manager did not load. Check your connection and reload.'); return; }
  if (!window.AppKeys.has()) { window.AppKeys.get(); toast('Add your Claude API key, then reopen the lesson.'); return; }'''),
    ('''  document.getElementById('apiKeyInput').value = getKey();
  document.getElementById('settingsModal').classList.add('open');''',
     '''  if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
  document.getElementById('settingsModal').classList.add('open');'''),
    ('''const saveSettings = () => {
  const v = document.getElementById('apiKeyInput').value.trim();
  try { if (v) localStorage.setItem(LS_KEY, v); else localStorage.removeItem(LS_KEY); } catch (e) {}
  closeSettings();
  toast(v ? 'Key saved.' : 'Key cleared.');
};
''', ''),
]

FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'getKey\b', r'apiKeyInput', r'saveSettings', r'LS_KEY']
