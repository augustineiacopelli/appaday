# Day 083 Homebrew Label Lab. Key stored as a plain string under appaday083.key.
LEGACY = "appaday083.key"

EDITS = [
    ('''      <div class="field"><label for="apikey">Anthropic API key</label><input id="apikey" type="password" placeholder="sk-ant-..." autocomplete="off"></div>
''',
     '''      <div class="field" id="keyMount"><p>The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('KEY_KEY="appaday083.key", ', ''),
    ('  function getKey(){ try{ return localStorage.getItem(KEY_KEY)||""; }catch(e){ return ""; } }\n', ''),
    ('    document.getElementById("apikey").value=getKey();\n',
     '    if(window.AppKeys) window.AppKeys.mountSettings(document.getElementById("keyMount"));\n'),
    ('''    try{ localStorage.setItem(KEY_KEY, document.getElementById("apikey").value.trim());
         localStorage.setItem(KEY_SESSION,''', '''    try{ localStorage.setItem(KEY_SESSION,'''),
    ('aistatus(getKey() ? "Ready.', 'aistatus((window.AppKeys && window.AppKeys.has()) ? "Ready.'),
    ('''  function aiGenerate(){
    var key=getKey();
    if(!key){ openSettings("Add your Anthropic API key to art-direct labels with Claude."); return; }
    var desc=''', '''  function aiGenerate(){
    if(!window.AppKeys){ aistatus("The key manager did not load. Check your connection and reload."); return; }
    window.AppKeys.get().then(function(key){
      if(!key){ aistatus("Add your Claude API key with the Settings button to art-direct labels."); return; }
      aiGenerateKeyed(key);
    });
  }
  function aiGenerateKeyed(key){
    var desc='''),
    ('''    document.getElementById("openSettings").addEventListener("click", function(){ openSettings(); });''',
     '''    document.getElementById("openSettings").addEventListener("click", function(){ openSettings(); });
    window.addEventListener("appaday:keychange", refreshAiHint);
    document.addEventListener("DOMContentLoaded", refreshAiHint);'''),
]

FORBID = [r'getKey\b', r'KEY_KEY', r'"apikey"']
