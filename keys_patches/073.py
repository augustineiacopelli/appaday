# Day 073 Three Ways (same code base as Day 72). Key stored as a plain string under fixlens_api_key.
LEGACY = "fixlens_api_key"

EDITS = [
    ('''    <div class="m-field">
      <label for="apiKey">Anthropic API key</label>
      <input type="password" id="apiKey" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
      <div class="m-hint">Get one at <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">console.anthropic.com</a>. Vision + reasoning uses a small amount of credit per diagnosis.</div>
    </div>
''',
     '''    <div class="m-field" id="keyMount"><div class="m-hint">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ("const LS_KEY = 'fixlens_api_key';\n", ""),
    ("function openModal(){ $('apiKey').value = localStorage.getItem(LS_KEY) || ''; $('modelSel').value",
     "function openModal(){ if(window.AppKeys) window.AppKeys.mountSettings($('keyMount')); $('modelSel').value"),
    ('''  const k = $('apiKey').value.trim();
  if(k) localStorage.setItem(LS_KEY, k); else localStorage.removeItem(LS_KEY);
  localStorage.setItem(LS_MODEL''', '''  localStorage.setItem(LS_MODEL'''),
    ("function getKey(){ return localStorage.getItem(LS_KEY) || ''; }\n", ""),
    ('''async function callClaude(userText){
  const key = getKey();
''', '''async function callClaude(userText){
  const key = window.AppKeys ? await window.AppKeys.get() : null;
  if(!key) throw new Error('Add your Claude API key to continue.');
'''),
    ('''  if(!getKey()){ showToast('Add your Anthropic API key in Settings first.', true); openModal(); return; }
  if(!imgData){ showToast('Add a photo of the problem first.', true); return; }
  runDiagnose();''',
     '''  if(!imgData){ showToast('Add a photo of the problem first.', true); return; }
  runDiagnose();'''),
    ('''if(!getKey()){
  setTimeout(function(){ showToast('Add your Anthropic API key in Settings to begin.'); }, 700);
}''', '''setTimeout(function(){ if(window.AppKeys && !window.AppKeys.has()) showToast('Add your Claude API key in Settings to begin.'); }, 900);'''),
]

FORBID = [r'getKey\b', r"\$\('apiKey'\)", r'LS_KEY']
