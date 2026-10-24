# Day 099 Social Post Responder. Key stored as a plain string under appaday099-key.
LEGACY = "appaday099-key"

EDITS = [
    ('''    <div class="field">
      <label for="apikey">Anthropic API key</label>
      <input id="apikey" type="password" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
      <p class="note">Stored only in this browser's local storage.</p>
    </div>
''',
     '''    <div class="field" id="keyMount"><p class="note">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("var K_KEY   = 'appaday099-key';\n", ""),
    ("  $('apikey').value = load(K_KEY, '') || '';\n",
     "  if(window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ("  window.setTimeout(function(){ $('apikey').focus(); }, 40);\n", ""),
    ('''  var key = $('apikey').value.replace(/^\\s+|\\s+$/g, '');
  if(key){ save(K_KEY, key); } else { drop(K_KEY); }
''', ''),
    ("  var has = !!load(K_KEY, '');\n", "  var has = !!(window.AppKeys && window.AppKeys.has());\n"),
    ('''function markKeyState(){''', '''window.addEventListener('appaday:keychange', function(){ markKeyState(); });
document.addEventListener('DOMContentLoaded', function(){ markKeyState(); });
function markKeyState(){'''),
    ('''function callClaude(system, userText, maxTokens){
  var key = load(K_KEY, '');
  if(!key) return Promise.reject(new Error('nokey'));''', '''async function callClaude(system, userText, maxTokens){
  var key = window.AppKeys ? await window.AppKeys.get() : null;
  if(!key) throw new Error('nokey');'''),
    ("Add your Anthropic API key in Settings first, then read the batch.' ;", "X"),
]
EDITS = EDITS[:-1] + [
    ('''  if(!load(K_KEY, '')){
    showError('Add your Anthropic API key in Settings first, then read the batch.', false);
    openSettings();
    return;
  }
''', '''  if(!(window.AppKeys && window.AppKeys.has())){
    if(window.AppKeys) window.AppKeys.get();
    showError('Add your Claude API key, then read the batch again.', false);
    return;
  }
'''),
    ("'Add your Anthropic API key in Settings first, then read the batch.'", "'Add your Claude API key with the gear button, then read the batch again.'"),
]

FORBID = [r'K_KEY', r"\$\('apikey'\)"]
