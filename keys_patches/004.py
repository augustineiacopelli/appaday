# Day 004 Tube Sort. The key was typed into Settings each visit and never stored.
LEGACY = ""

EDITS = [
    ('''    <label>ANTHROPIC API KEY</label>
    <div id="key-row">
      <input type="password" id="api-key-input" placeholder="sk-ant-..." autocomplete="off" spellcheck="false" oninput="updateGearState()"/>
      <button class="btn-ghost" id="toggle-key-btn" onclick="toggleKeyVis()">SHOW</button>
    </div>
    <p class="key-note">Used for screenshot analysis only. Never stored or committed.<br>Get one at <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>.</p>
''',
     '''    <div id="keyMount"><p class="key-note">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('function openSettings(){document.getElementById("settings-overlay").classList.add("open");}',
     'function openSettings(){if(window.AppKeys)window.AppKeys.mountSettings(document.getElementById("keyMount"));document.getElementById("settings-overlay").classList.add("open");}'),
    ('function updateGearState(){document.getElementById("settings-btn").classList.toggle("keyed",!!document.getElementById("api-key-input").value.trim());}\n'
     'function toggleKeyVis(){const i=document.getElementById("api-key-input"),b=document.getElementById("toggle-key-btn");if(i.type==="password"){i.type="text";b.textContent="HIDE";}else{i.type="password";b.textContent="SHOW";}}',
     'function updateGearState(){document.getElementById("settings-btn").classList.toggle("keyed",!!(window.AppKeys&&window.AppKeys.has()));}\n'
     'window.addEventListener("appaday:keychange",updateGearState);\n'
     'document.addEventListener("DOMContentLoaded",updateGearState);'),
    ('''function triggerUpload(){
  const apiKey=document.getElementById("api-key-input").value.trim();
  if(!apiKey||!tubeCountSet){setStatus("Set your API key and tube count in Settings first.");openSettings();return;}
  document.getElementById("file-input").click();
}''',
     '''function triggerUpload(){
  if(!window.AppKeys){setStatus("The key manager did not load. Check your connection and reload.");return;}
  if(!tubeCountSet){setStatus("Set your tube count in Settings first.");openSettings();return;}
  if(!window.AppKeys.has()){window.AppKeys.get();setStatus("Add your Claude API key, then tap upload again.");return;}
  document.getElementById("file-input").click();
}'''),
    ('''  document.getElementById("dropper-overlay").classList.remove("open");
  const apiKey=document.getElementById("api-key-input").value.trim();
  setStatus("AI is reading tube layout using your palette...");''',
     '''  document.getElementById("dropper-overlay").classList.remove("open");
  const apiKey=window.AppKeys?await window.AppKeys.get():null;
  if(!apiKey){setStatus("Add your Claude API key with the gear button to continue.");return;}
  setStatus("AI is reading tube layout using your palette...");'''),
]

FORBID = [r'getElementById\("api-key-input"\)', r'toggleKeyVis']
