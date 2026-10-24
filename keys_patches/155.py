# Day 155 Forecast Discussion Decoder. Key stored as a plain string under afd155.key.
LEGACY = "afd155.key"

EDITS = [
    ("key: 'afd155.key', ", ""),
    ('''    <label for="keyIn">Claude API key</label>
    <input id="keyIn" type="password" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
    <p class="hint">Stored only in this browser. The original text and glossary work without a key.</p>
''',
     '''    <div id="keyMount"></div>
    <p class="hint">The original text and glossary work without a key.</p>
'''),
    ('''  var key = lsGet(LS.key, '');
  if (!key) throw claudeError('nokey');''',
     '''  var key = window.AppKeys ? await window.AppKeys.get() : null;
  if (!key) throw claudeError('nokey');'''),
    ('''  if (!lsGet(LS.key, '')) { openSettings('Add your Claude API key to decode discussions.'); return; }
''',
     '''  if (!window.AppKeys || !(await window.AppKeys.get())) { S.decodeError = 'Add your Claude API key to decode discussions.'; render(); return; }
'''),
    ("(lsGet(LS.key, '') ? '' : '<span class=\"status\">Needs a Claude key</span>')",
     "((window.AppKeys && window.AppKeys.has()) ? '' : '<span class=\"status\">Needs a Claude key</span>')"),
    ('''  $('keyIn').value = lsGet(LS.key, '');
''',
     '''  if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));
'''),
    ("openOv('setOv'); $('keyIn').focus();", "openOv('setOv'); $('sessIn').focus();"),
    ("if (!d && hadDecode && lsGet(LS.key, '')) runDecode();",
     "if (!d && hadDecode && window.AppKeys && window.AppKeys.has()) runDecode();"),
    ('''  var k = $('keyIn').value.trim(), s = $('sessIn').value.trim();
  if (k) lsSet(LS.key, k); else lsDel(LS.key);
''',
     '''  var s = $('sessIn').value.trim();
'''),
    ("renderOptions();\n", "window.addEventListener('appaday:keychange', function () { render(); });\nrenderOptions();\n"),
]

FORBID = [r"LS\.key", r"getElementById\(.keyIn.\)", r"\$\('keyIn'\)"]
