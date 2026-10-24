# Day 045 Water Reminder. Key stored as a plain string under wr_apiKey.
LEGACY = "wr_apiKey"

EDITS = [
    ('''    <label for="apiKeyInput">Claude API Key</label>
    <input type="password" id="apiKeyInput" placeholder="sk-ant-...">
''',
     '''    <div id="keyMount"><p class="note">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("  var KEY_API = 'wr_apiKey';\n", ""),
    ("  var apiKeyInput = document.getElementById('apiKeyInput');\n", ""),
    ("    apiKeyInput.value = safeGet(KEY_API) || '';\n",
     "    if(window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));\n"),
    ("    var key = apiKeyInput.value.trim();\n    var name = sessionNameInput.value.trim();", "    var name = sessionNameInput.value.trim();"),
    ("    safeSet(KEY_API, key);\n", ""),
    ('''    var key = safeGet(KEY_API);
    if(!key){
      openSettings();
      return;
    }
''',
     '''    if(!(window.AppKeys && window.AppKeys.has())){
      if(window.AppKeys){ window.AppKeys.get(); } else { showError('The key manager did not load. Check your connection and reload.'); }
      return;
    }
''', 2),
    ('''  function callClaude(images, prompt, cb){
    var apiKey = safeGet(KEY_API);
    var content = [];''',
     '''  function callClaude(images, prompt, cb){
    var keyPromise = window.AppKeys ? window.AppKeys.get() : Promise.resolve(null);
    keyPromise.then(function(apiKey){
      if(!apiKey){ cb(new Error('Add your Claude API key with the gear button to continue.'), null); return; }
      callClaudeWithKey(apiKey, images, prompt, cb);
    });
  }

  function callClaudeWithKey(apiKey, images, prompt, cb){
    var content = [];'''),
    ('''  if(!safeGet(KEY_API)){
    setupCaptureBtnText.textContent = 'Set up API key to start';
    captureBtnText.textContent = 'Set up API key to start';
  }
})();''',
     '''  function refreshKeyHint(){
    if(window.AppKeys && window.AppKeys.has()){
      setupCaptureBtnText.textContent = 'Photograph your container';
      captureBtnText.textContent = 'Check in on your drink';
    } else {
      setupCaptureBtnText.textContent = 'Add your API key to start';
      captureBtnText.textContent = 'Add your API key to start';
    }
  }
  window.addEventListener('appaday:keychange', refreshKeyHint);
  document.addEventListener('DOMContentLoaded', refreshKeyHint);
})();'''),
]

FORBID = [r'apiKeyInput', r'KEY_API', r'wr_apiKey']
