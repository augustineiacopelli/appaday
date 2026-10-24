# Day 123 Two Minute Task Splitter. Key stored as a plain string under appaday123-apikey.
LEGACY = "appaday123-apikey"

EDITS = [
    ('''    <div class="modal-field">
      <label for="apiKeyInput">Claude API key</label>
      <input type="password" id="apiKeyInput" autocomplete="off" placeholder="sk-ant-...">
    </div>
''', '''    <div class="modal-field" id="keyMount"><p>The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("  const API_KEY_STORAGE = 'appaday123-apikey';\n", ""),
    ("    apiKeyInput: document.getElementById('apiKeyInput'),\n", ""),
    ('''    try{
      const key = localStorage.getItem(API_KEY_STORAGE);
      if(key) els.apiKeyInput.value = key;
    }catch(e){}
''', ''),
    ('''    try{
      localStorage.setItem(API_KEY_STORAGE, els.apiKeyInput.value.trim());
    }catch(e){}
''', ''),
    ('''  function getApiKey(){
    try{
      return localStorage.getItem(API_KEY_STORAGE) || '';
    }catch(e){
      return '';
    }
  }

  function openModal(){ els.modalOverlay.classList.add('show'); }''', '''  function openModal(){
    if(window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
    els.modalOverlay.classList.add('show');
  }'''),
    ('''  function callClaude(){
    const apiKey = getApiKey();
    if(!apiKey){
      showError('Add your Claude API key in Settings before splitting a task.');
      return Promise.reject(new Error('missing key'));
    }
''', '''  async function callClaude(){
    if(!window.AppKeys){
      showError('The key manager did not load. Check your connection and reload.');
      return;
    }
    const apiKey = await window.AppKeys.get();
    if(!apiKey){
      showError('Add your Claude API key with the gear button, then split the task again.');
      return;
    }
'''),
]

FORBID = [r'getApiKey', r'apiKeyInput', r'API_KEY_STORAGE']
