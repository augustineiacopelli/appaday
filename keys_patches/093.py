# Day 093 Scam Text Tormentor. Key stored as a plain string under appaday-093-key.
LEGACY = "appaday-093-key"

EDITS = [
    ('''    <div class="field">
      <label class="label" for="keyInput">Anthropic API key</label>
      <input type="password" id="keyInput" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
      <p class="hint">Stored only in this browser. It never leaves your device except to call Anthropic directly. Get one at <a href="https://console.anthropic.com/settings/keys">console.anthropic.com</a>.</p>
    </div>
''',
     '''    <div class="field" id="keyMount"><p class="hint">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''      <button class="ghost" id="clearKey" type="button">Forget key</button>
''', ''),
    ("  var K_KEY = 'appaday-093-key';\n", ""),
    ('''  function getKey(){
    var k = lsGet(K_KEY);
    return k ? k.trim() : '';
  }

  function callClaude(retakeFlag, onDone, onErr){
    var key = getKey();
    if (!key){ onErr('Add your Anthropic API key in settings first.'); return; }
''', '''  function callClaude(retakeFlag, onDone, onErr){
    if (!window.AppKeys){ onErr('The key manager did not load. Check your connection and reload.'); return; }
    window.AppKeys.get().then(function(key){
      if (!key){ onErr('Add your Claude API key with the gear button first.'); return; }
      callClaudeKeyed(key, retakeFlag, onDone, onErr);
    });
  }

  function callClaudeKeyed(key, retakeFlag, onDone, onErr){
'''),
    ('''    if (!getKey()){
      notice('setupNotice','Add your Anthropic API key in settings, then raise the curtain.');
      openSettings();
      return;
    }
''', '''    if (!window.AppKeys){
      notice('setupNotice','The key manager did not load. Check your connection and reload.');
      return;
    }
    if (!window.AppKeys.has()){
      window.AppKeys.get();
      notice('setupNotice','Add your Claude API key, then raise the curtain again.');
      return;
    }
'''),
    ("    $('keyInput').value = lsGet(K_KEY) || '';\n",
     "    if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ("    $('keyInput').focus();\n", ""),
    ('''    var k = $('keyInput').value.trim();
    var n = $('nameInput').value.trim();
    if (k) lsSet(K_KEY,k); else lsDel(K_KEY);
''', '''    var n = $('nameInput').value.trim();
'''),
    ('''  function forgetKey(){
    lsDel(K_KEY);
    $('keyInput').value = '';
    notice('setNotice','Key removed from this browser.',true);
  }
''', ''),
    ("    $('clearKey').addEventListener('click', forgetKey);\n", ""),
]

FORBID = [r'K_KEY', r'getKey\b', r'keyInput', r'forgetKey']
