# Day 124 Reframe. Key stored as a plain string under appaday124-reframe-apikey.
LEGACY = "appaday124-reframe-apikey"

EDITS = [
    ('''    <p>Your Anthropic API key stays on this device, in local storage. It is never sent anywhere but Anthropic.</p>
    <label for="apiKeyInput">API key</label>
    <input type="password" id="apiKeyInput" placeholder="sk-ant-...">
    <div class="modal-actions">
      <button class="btn-plain" id="modalCancel">Cancel</button>
      <button class="primary" id="modalSave">Save</button>
    </div>''', '''    <div id="keyMount"><p>The key manager is loading. If this stays, check your connection and reload.</p></div>
    <div class="modal-actions">
      <button class="primary" id="modalCancel">Close</button>
    </div>'''),
    ("  var KEY_STORE = 'appaday124-reframe-apikey';\n", ""),
    ("    apiKeyInput: document.getElementById('apiKeyInput'),\n", ""),
    ("    modalCancel: document.getElementById('modalCancel'),\n    modalSave: document.getElementById('modalSave')\n",
     "    modalCancel: document.getElementById('modalCancel')\n"),
    ('''  function getStoredKey(){
    try{
      return localStorage.getItem(KEY_STORE) || '';
    }catch(e){
      return '';
    }
  }

  function setStoredKey(val){
    try{
      localStorage.setItem(KEY_STORE, val);
    }catch(e){
      /* storage unavailable, continue silently */
    }
  }

  function openModal(){
    els.apiKeyInput.value = getStoredKey();
    els.modalOverlay.classList.remove('hidden');
    els.apiKeyInput.focus();
  }''', '''  function openModal(){
    if(window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
    els.modalOverlay.classList.remove('hidden');
  }'''),
    ('''  els.modalSave.addEventListener('click', function(){
    setStoredKey(els.apiKeyInput.value.trim());
    closeModal();
    setStatus('', false);
  });
''', ''),
    ("  els.sortBtn.addEventListener('click', function(){", "  els.sortBtn.addEventListener('click', async function(){"),
    ('''    var apiKey = getStoredKey();
    if(!apiKey){
      setStatus('Add your API key in Settings first.', true);
      openModal();
      return;
    }
''', '''    if(!window.AppKeys){
      setStatus('The key manager did not load. Check your connection and reload.', true);
      return;
    }
    var apiKey = await window.AppKeys.get();
    if(!apiKey){
      setStatus('Add your Claude API key with the gear button to continue.', true);
      return;
    }
'''),
]

FORBID = [r'getStoredKey', r'setStoredKey', r'apiKeyInput', r'modalSave']
