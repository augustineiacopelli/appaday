# Day 063 Bleeding Edge. Key stored as a plain string under bleedingedge.apikey.
LEGACY = "bleedingedge.apikey"

EDITS = [
    ('    apikey: "bleedingedge.apikey",\n', ""),
    ('  function getKey() { return (lsGet(LS.apikey) || "").trim(); }\n',
     '  function hasKey() { return !!(window.AppKeys && window.AppKeys.has()); }\n'),
    ('    if (getKey()) {\n      keyNote.innerHTML = "Running on "', '    if (hasKey()) {\n      keyNote.innerHTML = "Running on "'),
    ('''    if (ek) { ek.addEventListener("click", openSettings); }
  }
''',
     '''    if (ek) { ek.addEventListener("click", openSettings); }
  }
  window.addEventListener("appaday:keychange", function () { paintKeyNote(); });
  document.addEventListener("DOMContentLoaded", function () { paintKeyNote(); });
'''),
    ('''  function callClaude(prompt, maxTokens, useSearch, onEvent, estChars) {
    var report = onEvent || function () {};''',
     '''  function callClaude(prompt, maxTokens, useSearch, onEvent, estChars) {
    var keyPromise = window.AppKeys ? window.AppKeys.get() : Promise.resolve(null);
    return keyPromise.then(function (apiKey) {
      if (!apiKey) { throw new Error("Add your Claude API key with the gear button to continue."); }
      return callClaudeKeyed(apiKey, prompt, maxTokens, useSearch, onEvent, estChars);
    });
  }

  function callClaudeKeyed(apiKey, prompt, maxTokens, useSearch, onEvent, estChars) {
    var report = onEvent || function () {};'''),
    ('        "x-api-key": getKey(),', '        "x-api-key": apiKey,'),
    ('  function runScan(forcedSubject, previous) {', '  async function runScan(forcedSubject, previous) {'),
    ('    if (!getKey()) { openSettings(); return; }\n',
     '''    if (!window.AppKeys) { showError("The key manager did not load. Check your connection and reload."); return; }
    if (!(await window.AppKeys.get())) { toast("Add your Claude API key with the gear button to run a scan"); return; }
'''),
    ('''        '<label for="apiKeyInput">Anthropic API key</label>' +
        '<input type="password" id="apiKeyInput" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">' +
        '<span class="help-text">Stored only in this browser, never sent anywhere but Anthropic. ' +
        'Get a key at <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">console.anthropic.com</a>.</span>' +
''',
     '''        '<div id="keyMount"><span class="help-text">The key manager is loading. If this stays, check your connection and reload.</span></div>' +
'''),
    ('''          '<button class="btn-save" id="saveSettings" type="button">Save key</button>' +
''', ""),
    ('''    var input = document.getElementById("apiKeyInput");
    input.value = getKey();
    input.focus();
''',
     '''    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById("keyMount"));
'''),
    ('''    document.getElementById("saveSettings").addEventListener("click", function () {
      var v = input.value.trim();
      if (v) { lsSet(LS.apikey, v); } else { lsDel(LS.apikey); }
      paintKeyNote();
      closeSettings();
      toast(v ? "Key saved" : "Key cleared");
    });
''', ""),
]

FORBID = [r'getKey\(', r'apiKeyInput', r'LS\.apikey', r'saveSettings']
