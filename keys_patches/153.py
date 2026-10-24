# Day 153 Social Pulse. Key stored as a plain string under sp153-apikey.
LEGACY = "sp153-apikey"

EDITS = [
    ('''    <div class="field">
      <label class="lbl" for="keyIn">Anthropic API key</label>
      <input type="password" id="keyIn" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="sk-ant-...">
      <p class="small">Stored only in this browser. It is sent only to api.anthropic.com.</p>
    </div>
''', '''    <div class="field" id="keyMount"><p class="small">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ("var K_KEY = 'sp153-apikey', K_SESS", "var K_SESS"),
    ('''    var key = (lsGet(K_KEY) || '').trim();
    if (!key) { showMsg(msgNode, 'warn', 'Add your Anthropic API key with the gear button first.'); openSettings(); return; }
''', '''    if (!window.AppKeys) { showMsg(msgNode, 'warn', 'The key manager did not load. Check your connection and reload.'); return; }
    var key = await window.AppKeys.get();
    if (!key) { showMsg(msgNode, 'warn', 'Add your Claude API key with the gear button first.'); return; }
'''),
    ("    $('keyIn').value = lsGet(K_KEY) || '';\n", "    if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ("    $('keyIn').focus();\n", ""),
    ('''    var key = $('keyIn').value.trim();
    var sess = $('sessIn').value.trim();''', '''    var sess = $('sessIn').value.trim();'''),
    ("    var ok1 = key ? lsSet(K_KEY, key) : (lsDel(K_KEY), true);\n", "    var ok1 = true;\n"),
]

FORBID = [r'K_KEY', r"\$\('keyIn'\)"]
