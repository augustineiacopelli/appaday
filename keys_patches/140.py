# Day 140 Delegation Draft. Key lives inside a JSON settings object (appaday-140-settings) as apiKey.
LEGACY = "appaday-140-settings:apiKey"

EDITS = [
    ('''    <div class="field">
      <label for="s-key">Anthropic API key</label>
      <input type="password" id="s-key" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
    </div>
''', '''    <div class="field" id="keyMount"><p class="lede">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("settings: Object.assign({ apiKey: '', sessionName: '', signature: '' }, loadJSON(KEYS.settings, {})),",
     "settings: Object.assign({ sessionName: '', signature: '' }, loadJSON(KEYS.settings, {})),"),
    ('''  if (!state.settings.apiKey) {
    toast('Add your Anthropic API key in Settings to draft.');
    openSettings();
    return;
  }
  const i = state.intake;
  if (!i.task.trim()) { toast('Describe the task first.'); $('f-task').focus(); return; }
  if (!i.name.trim()) { toast("Add the recipient's first name."); $('f-name').focus(); return; }
''', '''  const i = state.intake;
  if (!i.task.trim()) { toast('Describe the task first.'); $('f-task').focus(); return; }
  if (!i.name.trim()) { toast("Add the recipient's first name."); $('f-name').focus(); return; }
  if (!window.AppKeys) { toast('The key manager did not load. Check your connection and reload.'); return; }
  const apiKey = await window.AppKeys.get();
  if (!apiKey) { toast('Add your Claude API key with the Settings button to draft.'); return; }
'''),
    ("        'x-api-key': state.settings.apiKey,", "        'x-api-key': apiKey,"),
    ('''  $('s-key').value = state.settings.apiKey || '';
''', '''  if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));
'''),
    ("  $('settings-scrim').hidden = false;\n  $('s-key').focus();\n", "  $('settings-scrim').hidden = false;\n"),
    ("  state.settings.apiKey = $('s-key').value.trim();\n", "  delete state.settings.apiKey;\n"),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r"\$\('s-key'\)", r'settings\.apiKey\b(?!;)']
