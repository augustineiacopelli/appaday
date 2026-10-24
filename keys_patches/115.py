# Day 115 Basket Ledger. Key lives inside a JSON settings object (basketLedgerSettings) as apiKey.
LEGACY = "basketLedgerSettings:apiKey"

EDITS = [
    ('''    <p class="caption">Your API key is stored only in this browser's local storage and is used only to call Claude when you scan a receipt.</p>
''', ''),
    ('''      <label>
        Anthropic API Key
        <input type="password" id="apiKeyInput" placeholder="sk-ant-...">
      </label>
''', '''      <div id="keyMount"><p class="caption">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''      if(!raw) return { apiKey: "", sessionName: "" };
      var parsed = JSON.parse(raw);
      return {
        apiKey: typeof parsed.apiKey === "string" ? parsed.apiKey : "",
        sessionName: typeof parsed.sessionName === "string" ? parsed.sessionName : ""
      };
    }catch(err){
      return { apiKey: "", sessionName: "" };
    }''', '''      if(!raw) return { sessionName: "" };
      var parsed = JSON.parse(raw);
      return {
        sessionName: typeof parsed.sessionName === "string" ? parsed.sessionName : ""
      };
    }catch(err){
      return { sessionName: "" };
    }'''),
    ('    document.getElementById("apiKeyInput").value = settings.apiKey;\n',
     '    if(window.AppKeys) window.AppKeys.mountSettings(document.getElementById("keyMount"));\n'),
    ('''    var apiKey = document.getElementById("apiKeyInput").value.trim();
    var sessionName = document.getElementById("sessionNameInput").value.trim();
    saveSettings({ apiKey: apiKey, sessionName: sessionName });''', '''    var sessionName = document.getElementById("sessionNameInput").value.trim();
    saveSettings({ sessionName: sessionName });'''),
    ('''  function handleExtract(){
    var settings = loadSettings();
    if(!settings.apiKey){
      showScanStatus("Add your Anthropic API key in Settings first.", true);
      return;
    }
    if(!scannedImageBase64){
      showScanStatus("Choose a receipt photo first.", true);
      return;
    }
''', '''  async function handleExtract(){
    if(!scannedImageBase64){
      showScanStatus("Choose a receipt photo first.", true);
      return;
    }
    if(!window.AppKeys){
      showScanStatus("The key manager did not load. Check your connection and reload.", true);
      return;
    }
    var apiKey = await window.AppKeys.get();
    if(!apiKey){
      showScanStatus("Add your Claude API key with the Settings button, then scan again.", true);
      return;
    }
'''),
    ('        "x-api-key": settings.apiKey,', '        "x-api-key": apiKey,'),
]

FORBID = [r'apiKeyInput', r'settings\.apiKey']
