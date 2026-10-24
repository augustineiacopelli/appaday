# Day 054 Daily Examen. Key stored as a plain string under examen-api-key.
LEGACY = "examen-api-key"

EDITS = [
    ('''    <label class="settings-field-label" for="api-key-input">Anthropic API key</label>
    <input class="settings-input" id="api-key-input" type="password" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
    <div class="settings-status" id="settings-status"></div>
    <div class="modal-close-row">
      <button class="btn-ghost" onclick="clearApiKey()">Remove key</button>
      <button class="btn-primary" onclick="saveApiKey()">Save</button>
    </div>''',
     '''    <div id="keyMount"><div class="settings-status">The key manager is loading. If this stays, check your connection and reload.</div></div>
    <div class="modal-close-row">
      <button class="btn-primary" onclick="closeSettings()">Close</button>
    </div>'''),
    ('''  function getApiKey(){
    try { return localStorage.getItem('examen-api-key') || ''; } catch (e) { return ''; }
  }
  function setApiKey(key){
    try { localStorage.setItem('examen-api-key', key); } catch (e) { /* unavailable, skip */ }
  }
  function removeApiKey(){
    try { localStorage.removeItem('examen-api-key'); } catch (e) { /* unavailable, skip */ }
  }

  window.openSettings = function(){
    var input = document.getElementById('api-key-input');
    input.value = getApiKey();
    document.getElementById('settings-status').textContent = getApiKey() ? 'A key is currently saved on this device.' : '';
    var overlay''',
     '''  window.openSettings = function(){
    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
    var overlay'''),
    ('''  window.saveApiKey = function(){
    var input = document.getElementById('api-key-input');
    var key = input.value.trim();
    setApiKey(key);
    document.getElementById('settings-status').textContent = key ? 'Key saved on this device.' : 'No key entered.';
    setTimeout(closeSettings, 600);
  };

  window.clearApiKey = function(){
    removeApiKey();
    document.getElementById('api-key-input').value = '';
    document.getElementById('settings-status').textContent = 'Key removed.';
  };

''', ''),
    ('''  window.reflectWithAI = function(){
    var key = getApiKey();''',
     '''  window.reflectWithAI = async function(){
    var key = window.AppKeys ? await window.AppKeys.get() : null;'''),
    ('''    if (!key){
      openSettings();
      return;
    }
''',
     '''    if (!key){
      errorEl.textContent = 'Add your Claude API key with the gear button to continue.';
      errorEl.classList.add('show');
      return;
    }
'''),
]

FORBID = [r'api-key-input', r'getApiKey', r'saveApiKey', r'clearApiKey', r'settings-status.\)\.textContent']
