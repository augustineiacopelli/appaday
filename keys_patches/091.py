# Day 091 Grade Runway. Key stored as a plain string under appaday091-key.
# The file picker is gesture sensitive: tapping the drop zone with no key opens the sheet, then the user taps again.
LEGACY = "appaday091-key"

EDITS = [
    ('''    <label for="key">Anthropic API key</label>
    <input id="key" type="password" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
    <p style="margin:8px 0 0;font-size:12px">Stored in this browser only. Never sent anywhere but api.anthropic.com.</p>
''',
     '''    <div id="keyMount"><p style="margin:8px 0 0;font-size:12px">The key manager is loading. If this stays, check your connection and reload.</p></div>
'''),
    ('''      <button class="btn" id="set-cancel" type="button">Cancel</button>
      <button class="btn btn-go" id="set-save" type="button">Save</button>''',
     '''      <button class="btn btn-go" id="set-cancel" type="button">Close</button>'''),
    ('var K_KEY = "appaday091-key";\n', ''),
    ('''function getKey(){
  try{ return (localStorage.getItem(K_KEY) || "").trim(); }catch(e){ return ""; }
}
function setKey(v){
  try{ localStorage.setItem(K_KEY, v); }catch(e){}
}
function markGear(){
  var g = el("gear");
  g.className = getKey() ? "gear" : "gear dot";
}''', '''function hasKey(){ return !!(window.AppKeys && window.AppKeys.has()); }
function markGear(){
  var g = el("gear");
  g.className = hasKey() ? "gear" : "gear dot";
}
window.addEventListener("appaday:keychange", markGear);
document.addEventListener("DOMContentLoaded", markGear);'''),
    ('''  el("key").value = getKey();
  clear(el("testresult"));
  el("overlay").hidden = false;
  window.setTimeout(function(){ el("key").focus(); }, 40);''',
     '''  if(window.AppKeys) window.AppKeys.mountSettings(el("keyMount"));
  clear(el("testresult"));
  el("overlay").hidden = false;'''),
    ('''function acceptFile(file){
  if(!file) return;
  if(!getKey()){
    note("Add your Anthropic API key in Settings first.", "bad");
    openSettings();
    return;
  }''', '''async function acceptFile(file){
  if(!file) return;
  if(!window.AppKeys){
    note("The key manager did not load. Check your connection and reload.", "bad");
    return;
  }
  var apiKey = await window.AppKeys.get();
  if(!apiKey){
    note("Add your Claude API key with the gear button, then drop the file again.", "bad");
    return;
  }'''),
    ('      "x-api-key":getKey(),', '      "x-api-key":apiKey,'),
    ('function askClaude(blocks, label){', 'function askClaude(blocks, label, apiKey){'),
    ('media_type:"application/pdf", data:b64 } }], file.name);', 'media_type:"application/pdf", data:b64 } }], file.name, apiKey);'),
    ('t.slice(0, 60000) }], file.name);', 't.slice(0, 60000) }], file.name, apiKey);'),
    ('media_type:img, data:b64 } }], file.name);', 'media_type:img, data:b64 } }], file.name, apiKey);'),
    ('''  el("set-save").onclick = function(){
    setKey(el("key").value.trim());
    markGear();
    closeSettings();
  };
''', ''),
    ('''  el("set-test").onclick = function(){
    var btn = this, k = el("key").value.trim(), out = el("testresult");
    clear(out);
    if(!k){''', '''  el("set-test").onclick = async function(){
    var btn = this, out = el("testresult");
    clear(out);
    var k = hasKey() ? await window.AppKeys.get() : "";
    if(!k){'''),
    ('w.textContent = "Paste a key first.";', 'w.textContent = "Add a key above first.";'),
    ('''    if(!getKey()){
      note("Reading a syllabus needs an Anthropic API key. Add one here, then drop the file again.", "");
      openSettings();
      return;
    }
    el("file").click();''', '''    if(!hasKey()){
      note("Reading a syllabus needs a Claude API key. Add one here, then tap the drop zone again.", "");
      if(window.AppKeys) window.AppKeys.get();
      return;
    }
    el("file").click();'''),
]

FORBID = [r'getKey\b', r'K_KEY', r'setKey\b', r'el\("key"\)']
