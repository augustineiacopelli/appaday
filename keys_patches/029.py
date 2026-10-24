# Day 029 Life Advocate. Key stored as a plain string under life_advocate_api_key,
# migrated from the older embrace_api_key by the app itself.
LEGACY = "life_advocate_api_key,embrace_api_key"

EDITS = [
    ('''      <div class="field-label">Anthropic API Key</div>
      <input type="password" id="api-key-input" class="settings-input" placeholder="sk-ant-..." autocomplete="off">
''',
     '''      <div id="keyMount"><div class="field-label">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ("const STORAGE_KEY_API  = 'life_advocate_api_key';\n", ""),
    ('''// Migrate from old key names if present
if (!localStorage.getItem(STORAGE_KEY_API) && localStorage.getItem('embrace_api_key')) {
  localStorage.setItem(STORAGE_KEY_API, localStorage.getItem('embrace_api_key'));
}
''',
     '''// Migrate from old name keys if present
'''),
    ("let apiKey       = localStorage.getItem(STORAGE_KEY_API)  || '';\n", ""),
    ("const apiKeyInput       = document.getElementById('api-key-input');\n", ""),
    ('''gearBtn.addEventListener('click', () => {
  apiKeyInput.value       = apiKey;
''',
     '''gearBtn.addEventListener('click', () => {
  if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
'''),
    ('''  apiKey       = apiKeyInput.value.trim();
  advocateName = advocateNameInput.value.trim();
  localStorage.setItem(STORAGE_KEY_API,  apiKey);
''',
     '''  advocateName = advocateNameInput.value.trim();
'''),
    ('''startBtn.addEventListener('click', () => {
  if (!apiKey) { keyWarning.style.display = 'block'; return; }
''',
     '''startBtn.addEventListener('click', async () => {
  const key = window.AppKeys ? await window.AppKeys.get() : null;
  if (!key) {
    keyWarning.textContent = window.AppKeys ? 'Add your Claude API key with the gear button to begin.' : 'The key manager did not load. Check your connection and reload.';
    keyWarning.style.display = 'block';
    return;
  }
'''),
    ("async function compressHistory() {", "async function compressHistory(apiKey) {"),
    ('''  if (isTyping || sessionEnded) return;
  isTyping = true;
  sendBtn.disabled = true;
''',
     '''  if (isTyping || sessionEnded) return;
  isTyping = true;
  sendBtn.disabled = true;

  const apiKey = window.AppKeys ? await window.AppKeys.get() : null;
  if (!apiKey) {
    isTyping = false;
    sendBtn.disabled = false;
    keyWarning.textContent = 'Add your Claude API key with the gear button to continue.';
    keyWarning.style.display = 'block';
    return;
  }
'''),
    ("    await compressHistory();", "    await compressHistory(apiKey);"),
    ("if (!apiKey) keyWarning.style.display = 'block';\n", ""),
]

FORBID = [r'apiKeyInput', r'STORAGE_KEY_API', r'api-key-input']
