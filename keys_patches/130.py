# Day 130 Locus of Control. Key stored as a plain string under locus.apiKey.
LEGACY = "locus.apiKey"

EDITS = [
    ('''    <div class="field">
      <label class="field-label" for="apiKeyInput">Anthropic API key</label>
      <input type="password" id="apiKeyInput" autocomplete="off" placeholder="sk-ant-...">
      <p class="key-state" id="keyState"></p>
    </div>
''', '''    <div class="field" id="keyMount"><p class="key-state">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''      <button class="btn danger" id="btnClearKey">Clear key</button>
''', ''),
    ("var K_KEY = 'locus.apiKey';\n", ""),
    ('''  byId('apiKeyInput').value = '';
  byId('sessionInput').value = safeGet(K_SESSION, '');
  var has = safeGet(K_KEY, '');
  byId('keyState').textContent = has ? 'A key is saved in this browser. Leave this blank to keep it.' : 'No key saved yet.';
''', '''  if (window.AppKeys) { window.AppKeys.mountSettings(byId('keyMount')); }
  byId('sessionInput').value = safeGet(K_SESSION, '');
'''),
    ('''  byId('settingsOverlay').hidden = true;
  byId('apiKeyInput').value = '';
''', '''  byId('settingsOverlay').hidden = true;
'''),
    ('''function refreshKeyHint(){
  var has = safeGet(K_KEY, '');
''', '''window.addEventListener('appaday:keychange', function(){ refreshKeyHint(); });
document.addEventListener('DOMContentLoaded', function(){ refreshKeyHint(); });

function refreshKeyHint(){
  var has = !!(window.AppKeys && window.AppKeys.has());
'''),
    ('''    : 'Add an Anthropic API key in Settings before sorting a situation.';''',
     '''    : 'Add your Claude API key with the Settings button before sorting a situation.';'''),
    ('''function callClaude(text){
  var key = safeGet(K_KEY, '');
  if (!key) {
    return Promise.reject(new Error('No API key saved. Open Settings and add your Anthropic key.'));
  }
  return fetch(API_URL, {''', '''function callClaude(text){
  if (!window.AppKeys) {
    return Promise.reject(new Error('The key manager did not load. Check your connection and reload.'));
  }
  return window.AppKeys.get().then(function(key){
    if (!key) { throw new Error('No API key saved. Add your Claude API key with the Settings button.'); }
    return callClaudeKeyed(key, text);
  });
}

function callClaudeKeyed(key, text){
  return fetch(API_URL, {'''),
    ('''  var k = byId('apiKeyInput').value.trim();
  if (k) { safeSet(K_KEY, k); }
''', ''),
    ('''byId('btnClearKey').addEventListener('click', function(){
  safeRemove(K_KEY);
  byId('apiKeyInput').value = '';
  byId('keyState').textContent = 'No key saved yet.';
  refreshKeyHint();
});
''', ''),
]

FORBID = [r'K_KEY', r'apiKeyInput', r'btnClearKey']
