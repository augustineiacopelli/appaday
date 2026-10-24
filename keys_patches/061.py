# Day 061 Language Flashcard Sprint. Key stored as a plain string under appaday-061-apikey.
# The first run setup used to disable Start until a key was saved. boot() runs before keys.js
# loads, so that gate is dropped; the first sprint asks for the key instead.
LEGACY = "appaday-061-apikey"

EDITS = [
    ('    apikey: "appaday-061-apikey",\n', ""),
    ('    var apikey = localStorage.getItem(LS.apikey) || "";\n', ""),
    ('''        '<div class="field-group">' +
          '<span class="field-label">Claude API Key</span>' +
          '<input type="password" id="apikeyInput" placeholder="sk-ant-..." value="' + esc(apikey) + '">' +
          '<span class="help-text">Stored only in this browser. Get a key at <a href="https://console.anthropic.com" target="_blank" rel="noopener">console.anthropic.com</a>.</span>' +
        '</div>' +
''',
     '''        '<div class="field-group" id="keyMount"><span class="help-text">The key manager is loading. If this stays, check your connection and reload.</span></div>' +
'''),
    ('''    document.body.appendChild(overlay);

    document.getElementById("closeSettings").addEventListener("click", function () {''',
     '''    document.body.appendChild(overlay);
    if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById("keyMount"));

    document.getElementById("closeSettings").addEventListener("click", function () {'''),
    ('      var key = document.getElementById("apikeyInput").value.trim();\n', ""),
    ('      localStorage.setItem(LS.apikey, key);\n', ""),
    ('    var hasKey = !!localStorage.getItem(LS.apikey);\n\n', "\n"),
    ('''        '<button class="btn btn-primary" id="setupStart"' + (hasKey ? '' : ' disabled') + '>Start My Streak</button>' +
        (hasKey ?
          '' :
          '<button class="btn btn-ghost" id="setupOpenSettings">Add API Key in Settings</button>' +
          '<p class="setup-note">Start My Streak unlocks once a Claude API key is saved in Settings.</p>'
        ) +
''',
     '''        '<button class="btn btn-primary" id="setupStart">Start My Streak</button>' +
        '<p class="setup-note">The app asks for your Claude API key the first time you start a sprint. You can also add it any time with the gear button.</p>' +
'''),
    ('      if (!localStorage.getItem(LS.apikey)) return;\n', ""),
    ('''    var setupOpenSettings = document.getElementById("setupOpenSettings");
    if (setupOpenSettings) {
      setupOpenSettings.addEventListener("click", openSettings);
    }
''', ""),
    ('''  function fetchCards() {
    var apikey = localStorage.getItem(LS.apikey);
    if (!apikey) {''',
     '''  async function fetchCards() {
    var apikey = window.AppKeys ? await window.AppKeys.get() : null;
    if (!apikey) {'''),
    ("Add a Claude API key in Settings before starting a sprint.", "Add your Claude API key with the gear button to start a sprint."),
]

FORBID = [r'apikeyInput', r'LS\.apikey', r'setupOpenSettings', r'hasKey']
