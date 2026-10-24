# Day 086 Subject Line Lab. Key stored as a plain string under appaday086_key.
LEGACY = "appaday086_key"

EDITS = [
    ('''      <div class="field">
        <label class="lab" for="apiKey">Anthropic API key</label>
        <input type="text" id="apiKey" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
        <div class="keyhint">Get a key at <a href="https://console.anthropic.com/" target="_blank" rel="noopener">console.anthropic.com</a>.</div>
      </div>
''',
     '''      <div class="field" id="keyMount"><div class="keyhint">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ('''        <button class="btn btn-ghost" id="clearKeyBtn" type="button">Clear key</button>
''', ''),
    ('  var LS_KEY = "appaday086_key";\n', ''),
    ('    $("apiKey").value = lsGet(LS_KEY);\n',
     '    if (window.AppKeys) window.AppKeys.mountSettings($("keyMount"));\n'),
    ('  function run(){\n    if (running) return;', '  async function run(){\n    if (running) return;'),
    ('''    var key = lsGet(LS_KEY);

    if (!key){
      showNotice("Add your Anthropic API key in Settings to run the lab.", "info");
      openSettings();
      return;
    }
    if (body.length < 15){
      showNotice("Paste a bit more of the email body so the lab has something to work with.", "err");
      return;
    }
''', '''    if (body.length < 15){
      showNotice("Paste a bit more of the email body so the lab has something to work with.", "err");
      return;
    }
    if (!window.AppKeys){
      showNotice("The key manager did not load. Check your connection and reload.", "err");
      return;
    }
    var key = await window.AppKeys.get();
    if (!key){
      showNotice("Add your Claude API key with the gear button to run the lab.", "info");
      return;
    }
    if (running) return;
'''),
    ('''      var k = $("apiKey").value.trim();
      var s = $("sender").value.trim();
      if (k) lsSet(LS_KEY, k); else lsDel(LS_KEY);
''', '''      var s = $("sender").value.trim();
'''),
    ('''    $("clearKeyBtn").addEventListener("click", function(){
      lsDel(LS_KEY);
      $("apiKey").value = "";
    });
''', ''),
]

FORBID = [r'LS_KEY', r'"apiKey"', r'clearKeyBtn']
