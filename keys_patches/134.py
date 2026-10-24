# Day 134 Anagram Alchemy. Key lives inside a JSON settings object (appaday-134-settings) as apiKey.
LEGACY = "appaday-134-settings:apiKey"

EDITS = [
    ('''    <p>Your key stays in this browser only. It is never shown on the main screen and never leaves this device except in requests to Anthropic.</p>
    <label>
      <span class="field">Anthropic API key</span>
      <input type="password" id="apiKey" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
    </label>
''', '''    <div id="keyMount"><p>The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''    return { apiKey: typeof s.apiKey === 'string' ? s.apiKey : '',
             sessionName:''', '''    return { sessionName:'''),
    ('''  function askClaude(promptText){
    var s = loadSettings();
    if(!s.apiKey){ return Promise.reject(new Error('Add your Anthropic API key in Settings first.')); }
    return postMessages(s.apiKey, promptText, allowThinkingFlag, MAX_TOKENS).then(function(res){''',
     '''  function askClaude(promptText){
    if(!window.AppKeys){ return Promise.reject(new Error('The key manager did not load. Check your connection and reload.')); }
    return window.AppKeys.get().then(function(apiKey){
      if(!apiKey){ throw new Error('Add your Claude API key with the gear button first.'); }
      return askClaudeKeyed(apiKey, promptText);
    });
  }

  function askClaudeKeyed(apiKey, promptText){
    return postMessages(apiKey, promptText, allowThinkingFlag, MAX_TOKENS).then(function(res){'''),
    ('          return postMessages(s.apiKey, promptText, false, 8000);', '          return postMessages(apiKey, promptText, false, 8000);'),
    ('''    var settings = loadSettings();
    if(!settings.apiKey){ setStatus('Add your Anthropic API key in Settings first.', 'warn'); openSettings(); return; }
''', '''    if(!window.AppKeys){ setStatus('The key manager did not load. Check your connection and reload.', 'warn'); return; }
    if(!window.AppKeys.has()){ window.AppKeys.get(); setStatus('Add your Claude API key, then tap again.', 'warn'); return; }
'''),
    ('''    var s = loadSettings();
    $('apiKey').value = s.apiKey;
    $('sessionName').value = s.sessionName;
    show(settingsModal);
    $('apiKey').focus();''', '''    var s = loadSettings();
    if(window.AppKeys){ window.AppKeys.mountSettings($('keyMount')); }
    $('sessionName').value = s.sessionName;
    show(settingsModal);'''),
    ("saveSettings({ apiKey: $('apiKey').value.trim(), sessionName:", "saveSettings({ sessionName:"),
]

FORBID = [r"\$\('apiKey'\)", r'settings\.apiKey', r's\.apiKey']
