# Day 136 Detour. Key stored as a JSON encoded string under detour-key. The key is optional here:
# without one the stops are ranked locally, so a missing key never opens the sheet.
LEGACY = "detour-key"

EDITS = [
    ('''    <p>Stored only in this browser. Without a key the stops still load and get ranked locally, just without written pitches.</p>
    <label class="field">
      <span>Key</span>
      <input type="password" id="apikey" placeholder="sk-ant-..." autocomplete="off">
    </label>
    <div class="modal-row">
      <button type="button" class="go" id="save-key">Save key</button>
      <button type="button" class="ghost" id="close-settings">Close</button>
    </div>''', '''    <p>Without a key the stops still load and get ranked locally, just without written pitches.</p>
    <div id="keyMount"><p>The key manager is loading. If this stays, check your connection and reload.</p></div>
    <div class="modal-row">
      <button type="button" class="go" id="close-settings">Close</button>
    </div>'''),
    ("  var API_STORE_KEY = 'detour-key';\n", ""),
    ('''  function getKey() {
    var v = readStore(API_STORE_KEY, '');
    return typeof v === 'string' ? v : '';
  }

''', ''),
    ('''  function scoreWithClaude(candidates) {
    var trimmed''', '''  function scoreWithClaude(candidates) {
    if (window.AppKeys && window.AppKeys.has()) {
      return window.AppKeys.get().then(function (k) { return scoreWithClaudeKeyed(candidates, k || ''); });
    }
    return Promise.resolve().then(function () { return scoreWithClaudeKeyed(candidates, ''); });
  }

  function scoreWithClaudeKeyed(candidates, key) {
    var trimmed'''),
    ('''    var key = getKey();
    if (!key) {
      return Promise.resolve({ list: applyHeuristic(trimmed)''', '''    if (!key) {
      return Promise.resolve({ list: applyHeuristic(trimmed)'''),
    ("    el.apikey = document.getElementById('apikey');\n", ""),
    ('''      el.apikey.value = getKey();
      el.scrim.hidden = false;
      el.apikey.focus();''', '''      if (window.AppKeys) window.AppKeys.mountSettings(document.getElementById('keyMount'));
      el.scrim.hidden = false;'''),
    ('''    document.getElementById('save-key').addEventListener('click', function () {
      writeStore(API_STORE_KEY, el.apikey.value.trim());
      el.scrim.hidden = true;
      setStatus(el.apikey.value.trim() ? 'Key saved in this browser.' : 'Key cleared.');
    });

''', ''),
]

FORBID = [r'getKey\b', r'API_STORE_KEY', r'el\.apikey', r'save-key']
