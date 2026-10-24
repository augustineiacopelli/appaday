# Day 111 Application Gap Analysis. Key lives inside a JSON settings object (CONFIG.STORAGE_KEY) as apiKey.
LEGACY = "appaday-111-gap-analysis:apiKey"

EDITS = [
    ('''      <label class="simple" for="api-key-input">Anthropic API Key</label>
      <input type="password" id="api-key-input" placeholder="sk-ant-...">
      <div class="masked-key" id="masked-key-display">No key saved</div>
''',
     '''      <div id="keyMount"><div class="masked-key">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ('No API key saved yet. Open Settings to add your Anthropic API key before analyzing.',
     'No API key saved yet. Open Settings to add your Claude API key before analyzing.'),
    ('''  var STATE = {
    apiKey: "",
    sessionName: "",''', '''  var STATE = {
    sessionName: "",'''),
    ('        STATE.apiKey = parsed.apiKey || "";\n', ''),
    ('        apiKey: STATE.apiKey,\n', ''),
    ('''  function maskKey(key) {
    if (!key) return "No key saved";
    if (key.length <= 8) return "Key saved (hidden)";
    return "Key saved: " + key.slice(0, 6) + "..." + key.slice(-4);
  }

''', '''  function hasKey() {
    return !!(window.AppKeys && window.AppKeys.has());
  }

'''),
    ('''    var banner = $("key-banner");
    if (STATE.apiKey) {''', '''    var banner = $("key-banner");
    if (hasKey()) {'''),
    ('    $("api-key-input").value = STATE.apiKey;\n', '    if (window.AppKeys) window.AppKeys.mountSettings($("keyMount"));\n'),
    ('    $("masked-key-display").textContent = maskKey(STATE.apiKey);\n', ''),
    ('    STATE.apiKey = $("api-key-input").value.trim();\n', ''),
    ('''  function callClaude(systemPrompt, userMessage, maxTokens, tools, model) {
    var body = {''', '''  function callClaude(systemPrompt, userMessage, maxTokens, tools, model) {
    if (!window.AppKeys) {
      return Promise.reject(new Error("The key manager did not load. Check your connection and reload."));
    }
    return window.AppKeys.get().then(function (apiKey) {
      if (!apiKey) throw new Error("Add your Claude API key with the Settings button first.");
      return callClaudeKeyed(apiKey, systemPrompt, userMessage, maxTokens, tools, model);
    });
  }

  function callClaudeKeyed(apiKey, systemPrompt, userMessage, maxTokens, tools, model) {
    var body = {'''),
    ('        "x-api-key": STATE.apiKey,', '        "x-api-key": apiKey,'),
    ('''    if (!STATE.apiKey) {
      setCoverLetterStage("error", "No API key saved. Open Settings and add your Anthropic API key.");
      return;
    }''', '''    if (!hasKey()) {
      if (window.AppKeys) window.AppKeys.get();
      setCoverLetterStage("error", "No API key saved. Add your Claude API key, then draft again.");
      return;
    }'''),
    ('''    if (!STATE.apiKey) {
      setStage("error-extract", "No API key saved. Open Settings and add your Anthropic API key.");
      return;
    }''', '''    if (!hasKey()) {
      if (window.AppKeys) window.AppKeys.get();
      setStage("error-extract", "No API key saved. Add your Claude API key, then analyze again.");
      return;
    }'''),
    ('''  function renderKeyBanner() {''', '''  window.addEventListener("appaday:keychange", function () { renderKeyBanner(); });
  document.addEventListener("DOMContentLoaded", function () { renderKeyBanner(); });

  function renderKeyBanner() {'''),
]

FORBID = [r'STATE\.apiKey', r'api-key-input', r'maskKey']
