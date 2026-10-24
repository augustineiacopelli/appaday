# Day 005 Dad Joke Generator. Key stored as a plain string under dadJokeApiKey.
LEGACY = "dadJokeApiKey"

EDITS = [
    ('''    <label for="apiKeyInput">Anthropic API Key</label>
    <input type="password" id="apiKeyInput" placeholder="sk-ant-..." autocomplete="off">
    <p class="modal-hint">Your key is stored in your browser only and never sent anywhere except the Anthropic API.</p>
    <div class="modal-btns">
      <button class="modal-cancel" onclick="closeSettings()">Cancel</button>
      <button class="modal-save" onclick="saveSettings()">Save</button>
    </div>''',
     '''    <div id="keyMount"><p class="modal-hint">The key manager is loading. If this stays, check your connection and reload.</p></div>
    <div class="modal-btns">
      <button class="modal-save" onclick="closeSettings()">Close</button>
    </div>'''),
    ('''function openSettings() {
  var stored = '';
  try { stored = localStorage.getItem('dadJokeApiKey') || ''; } catch(e) {}
  document.getElementById('apiKeyInput').value = stored;
  document.getElementById('settingsOverlay').classList.add('open');
}''',
     '''function openSettings() {
  if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
  document.getElementById('settingsOverlay').classList.add('open');
}'''),
    ('''function saveSettings() {
  var key = document.getElementById('apiKeyInput').value.trim();
  try { localStorage.setItem('dadJokeApiKey', key); } catch(e) {}
  closeSettings();
}

function getApiKey() {
  try { return localStorage.getItem('dadJokeApiKey') || ''; } catch(e) { return ''; }
}

''', ''),
    ('''async function getJoke() {
  var apiKey = getApiKey();
  if (!apiKey) {
    openSettings();
    return;
  }
''',
     '''async function getJoke() {
  var keyMsg = document.getElementById('errorMsg');
  if (!window.AppKeys) {
    keyMsg.textContent = 'The key manager did not load. Check your connection and reload.';
    keyMsg.style.display = 'block';
    return;
  }
  var apiKey = await window.AppKeys.get();
  if (!apiKey) {
    keyMsg.textContent = 'Add your Claude API key with the gear button to continue.';
    keyMsg.style.display = 'block';
    return;
  }
'''),
]

FORBID = [r'getElementById\(.apiKeyInput.\)', r'getApiKey', r'saveSettings']
