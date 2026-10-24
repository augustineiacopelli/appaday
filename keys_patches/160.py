# Day 160 Procedure Scribe. The key was optional and held in page memory only, never stored.
# The key is still optional: the API panel only appears once the ring holds a key, and the sheet never opens by itself.
LEGACY = ""

EDITS = [
    ("template: 'training', outputText: '', apiKey: null,", "template: 'training', outputText: '',"),
    ('''    <p>The copy and paste path needs no key. Add an Anthropic API key only if you want to send the prompt directly. The key is held in page memory only, is never stored, and is wiped by Clear or by closing the tab.</p>
    <div><label class="lbl" for="apiKey">Anthropic API key (optional)</label><input type="password" id="apiKey" autocomplete="off" spellcheck="false" placeholder="sk-ant-..."></div>
''',
     '''    <p>The copy and paste path needs no key. Add a Claude API key only if you want to send the prompt directly. The key stays in this browser and is used only for that send.</p>
    <div id="keyMount"></div>
'''),
    ('''  const k = $('apiKey').value.trim();
  state.apiKey = k || null;
  show($('apiPanel'), !!state.apiKey);
''',
     '''  show($('apiPanel'), !!(window.AppKeys && window.AppKeys.has()));
'''),
    ("async function callClaude(model, prompt) {", "async function callClaude(model, prompt, apiKey) {"),
    ("'x-api-key': state.apiKey,", "'x-api-key': apiKey,"),
    ('''  if (!state.apiKey) return;
  if (!sendArmed)''',
     '''  if (!window.AppKeys || !window.AppKeys.has()) return;
  if (!sendArmed)'''),
    ('''    const j = await callClaude(model, promptText);''',
     '''    const apiKey = await window.AppKeys.get();
    if (!apiKey) throw new Error('No Claude API key is saved. Add one in Settings.');
    const j = await callClaude(model, promptText, apiKey);'''),
    ("state.template = 'training'; state.apiKey = null; ui.ext = null;", "state.template = 'training'; ui.ext = null;"),
    ("  $('apiKey').value = ''; syncApiPanel();\n", "  syncApiPanel();\n"),
    ("$('gearBtn').addEventListener('click', () => $('settingsDlg').showModal());",
     "$('gearBtn').addEventListener('click', () => { if (window.AppKeys) window.AppKeys.mountSettings($('keyMount')); $('settingsDlg').showModal(); });"),
    ("$('apiKey').addEventListener('input', syncApiPanel);", "window.addEventListener('appaday:keychange', syncApiPanel);"),
]

FORBID = [r"state\.apiKey", r"\$\('apiKey'\)"]
