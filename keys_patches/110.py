# Day 110 Album Cover Generator. Key lives inside a JSON settings object next to the session name.
LEGACY = "appaday110-settings:apiKey"

EDITS = [
    ('''    <div class="field">
      <label for="apiKeyInput">Claude API Key</label>
      <input type="password" id="apiKeyInput" placeholder="sk-ant-...">
    </div>
''',
     '''    <div class="field" id="keyMount"><p class="modal-note">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''    <p class="modal-note">Your Claude API key is stored only in this browser's local storage and is sent directly to Anthropic's API. It is never saved anywhere else.</p>
''', ''),
    ('  var apiKeyInput = document.getElementById("apiKeyInput");\n', ''),
    ('''      if(!raw) return { apiKey:"", sessionName:"" };
      var parsed = JSON.parse(raw);
      return {
        apiKey: typeof parsed.apiKey === "string" ? parsed.apiKey : "",
        sessionName: typeof parsed.sessionName === "string" ? parsed.sessionName : ""
      };
    }catch(e){
      return { apiKey:"", sessionName:"" };
    }''', '''      if(!raw) return { sessionName:"" };
      var parsed = JSON.parse(raw);
      return {
        sessionName: typeof parsed.sessionName === "string" ? parsed.sessionName : ""
      };
    }catch(e){
      return { sessionName:"" };
    }'''),
    ('    apiKeyInput.value = s.apiKey;\n', '    if(window.AppKeys) window.AppKeys.mountSettings(document.getElementById("keyMount"));\n'),
    ('''      apiKey: apiKeyInput.value.trim(),
      sessionName:''', '''      sessionName:'''),
    ('''  function generate(mood, skipCooldown){
    var settings = loadSettings();
    if(!settings.apiKey){
      showNoKeyError();
      return;
    }
''', '''  function generate(mood, skipCooldown){
    if(!window.AppKeys){
      showNoKeyError();
      return;
    }
    window.AppKeys.get().then(function(apiKey){
      if(!apiKey){
        showNoKeyError();
        return;
      }
      generateKeyed(mood, skipCooldown, apiKey);
    });
  }

  function generateKeyed(mood, skipCooldown, apiKey){
'''),
    ('      callClaude(mood, settings.apiKey),', '      callClaude(mood, apiKey),'),
]

FORBID = [r'apiKeyInput', r'settings\.apiKey']
