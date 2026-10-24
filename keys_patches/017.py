# Day 017 Session Scribe. Key stored as a plain string under ss017_apikey.
LEGACY = "ss017_apikey"

EDITS = [
    ("const SK={apiKey:'ss017_apikey',confName:", "const SK={confName:"),
    ('''      <div class="settings-group">
        <label>Anthropic API Key</label>
        <div class="settings-key-row"><input type="password" id="s_apiKey" placeholder="sk-ant-..." autocomplete="off"><div class="key-dot" id="s_keyDot"></div></div>
        <span class="hint">Saved locally. Never sent anywhere except api.anthropic.com.</span>
      </div>
''',
     '''      <div class="settings-group"><div id="keyMount"><span class="hint">The key manager is loading. If this stays, check your connection and reload.</span></div></div>
'''),
    ('''const isValidKey=(v=gs(SK.apiKey))=>v.startsWith('sk-ant-')&&v.length>20;
const getKey=()=>gs(SK.apiKey);
''',
     '''const isValidKey=()=>!!(window.AppKeys&&window.AppKeys.has());
'''),
    ("  document.getElementById('s_apiKey').value=gs(SK.apiKey);\n", ""),
    ("  updateKeyDot();\n  const conf=gs(SK.confName);", "  const conf=gs(SK.confName);"),
    ('''const updateKeyDot=()=>document.getElementById('s_keyDot').className='key-dot'+(isValidKey(document.getElementById('s_apiKey').value.trim())?' ok':'');
document.getElementById('s_apiKey').addEventListener('input',updateKeyDot);
''',
     '''window.addEventListener('appaday:keychange',()=>updateGearDot());
document.addEventListener('DOMContentLoaded',()=>updateGearDot());
'''),
    ("function openSettings(){document.getElementById('settingsPanel').classList.add('open');",
     "function openSettings(){if(window.AppKeys)window.AppKeys.mountSettings(document.getElementById('keyMount'));document.getElementById('settingsPanel').classList.add('open');"),
    ("  const key=document.getElementById('s_apiKey').value.trim();\n  const conf=document.getElementById('s_confName').value.trim();",
     "  const conf=document.getElementById('s_confName').value.trim();"),
    ("  key?ss(SK.apiKey,key):rs(SK.apiKey);\n", ""),
    ("  [SK.apiKey,SK.confName,SK.email].forEach(rs);", "  [SK.confName,SK.email].forEach(rs);"),
    ("  ['s_apiKey','s_confName','s_email'].forEach(id=>document.getElementById(id).value='');",
     "  ['s_confName','s_email'].forEach(id=>document.getElementById(id).value='');"),
    ("  updateKeyDot();updateGearDot();showToast('Settings cleared','');", "  updateGearDot();showToast('Settings cleared','');"),
    ("  if(!isValidKey()){showToast('Add your API key in Settings first','error');return;}\n  hideSpeechError();",
     "  if(!isValidKey()){if(window.AppKeys)window.AppKeys.get();showToast('Add your Claude API key, then tap record again','error');return;}\n  hideSpeechError();"),
    ('''  if(!isValidKey()){showInlineError('No API key found.','Open Settings \\u2192',openSettings);return;}
  if(!gs(SK.email))showToast('No default email saved \\u2014 add one in Settings','');
  const key=getKey();
''',
     '''  const key=window.AppKeys?await window.AppKeys.get():null;
  if(!key){showInlineError('No API key found.','Open Settings \\u2192',openSettings);return;}
  if(!gs(SK.email))showToast('No default email saved \\u2014 add one in Settings','');
'''),
]

FORBID = [r's_apiKey', r'SK\.apiKey', r'updateKeyDot', r'getKey\(']
