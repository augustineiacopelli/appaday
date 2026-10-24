# Day 078 Red Team This. Key stored as a plain string under redteam078_key.
LEGACY = "redteam078_key"

EDITS = [
    ('''    <label>
      <span class="field-label">Anthropic API key</span>
      <input id="keyInput" type="password" placeholder="sk-ant-&hellip;" autocomplete="off">
    </label>
    <div class="keylink">Get one at <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener">console.anthropic.com</a></div>
''',
     '''    <div id="keyMount"><p class="hint">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("const LS_KEY = 'redteam078_key';\n", ""),
    ("  $('gearBtn').classList.toggle('flag', !lsGet(LS_KEY));\n}",
     "  $('gearBtn').classList.toggle('flag', !(window.AppKeys && window.AppKeys.has()));\n}\n"
     "window.addEventListener('appaday:keychange', refreshGear);\n"
     "document.addEventListener('DOMContentLoaded', refreshGear);"),
    ("  $('keyInput').value = lsGet(LS_KEY);\n", "  if(window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ("  $('keyInput').focus();\n", ""),
    ("  lsSet(LS_KEY, $('keyInput').value.trim());\n", ""),
    ('''  var key = lsGet(LS_KEY);
  if(!key){ openModal(); return; }
''', '''  if(!window.AppKeys){ note('The key manager did not load. Check your connection and reload.'); return; }
  var key = await window.AppKeys.get();
  if(!key){ note('Add your Claude API key with the gear button to run a pass.'); return; }
'''),
]

# Pre-existing: top level await.
FIXES = [
    ("const CLAUDE_MODEL = await getModel();",
     "let CLAUDE_MODEL = 'claude-sonnet-5-5';\ngetModel().then(function (m) { if (m) CLAUDE_MODEL = m; });"),
]

FORBID = [r'keyInput', r'redteam078_key']
