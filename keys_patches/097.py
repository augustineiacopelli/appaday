# Day 097 Field Marks. Key stored as a plain string under fieldmarks-key.
LEGACY = "fieldmarks-key"

EDITS = [
    ('''    <div class="fieldrow">
      <label class="fl" for="key">Anthropic API key</label>
      <input type="text" id="key" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
      <p class="helper">Create one at console.anthropic.com under API Keys.</p>
    </div>
''',
     '''    <div class="fieldrow" id="keyMount"><p class="helper">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("  var K_KEY = 'fieldmarks-key';\n", ""),
    ('''  function run(){
    if(busy) return;
    var key = lsGet(K_KEY, '').trim();
    if(!key){
      openModal();
      setError('No API key saved', 'Add your Anthropic API key in Settings, then identify the specimen.');
      return;
    }
    if(!stagedFile){
      setError('No photo staged', 'Add a photograph first.');
      return;
    }
''', '''  async function run(){
    if(busy) return;
    if(!stagedFile){
      setError('No photo staged', 'Add a photograph first.');
      return;
    }
    if(!window.AppKeys){
      setError('Key manager did not load', 'Check your connection and reload the page.');
      return;
    }
    var key = await window.AppKeys.get();
    if(!key){
      setError('No API key saved', 'Add your Claude API key with the gear button, then identify the specimen.');
      return;
    }
    if(busy) return;
'''),
    ("    $('key').value = lsGet(K_KEY, '');\n", "    if(window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ("    $('key').focus();\n", ""),
    ("      lsSet(K_KEY, $('key').value.trim());\n", ""),
    ("    if(!lsGet(K_KEY, '')) $('dropmsg').textContent =\n      'Take a photo, choose one from your library, or drop a file here. You will need an Anthropic API key in Settings before the first identification.';",
     "    if(!(window.AppKeys && window.AppKeys.has())) $('dropmsg').textContent =\n      'Take a photo, choose one from your library, or drop a file here. You will need a Claude API key (the gear button) before the first identification.';"),
]

FORBID = [r'K_KEY', r"\$\('key'\)"]
