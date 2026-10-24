# Day 023 Beer Tasting Scorecard. Key stored as apiKey inside the JSON object beertasting_settings_v1.
LEGACY = "beertasting_settings_v1:apiKey"

EDITS = [
    ('''    <div class="field-group">
      <label class="field-label">Claude API Key</label>
      <input type="password" class="modal-input" id="settings-api-key" placeholder="sk-ant-…" autocomplete="off" oninput="checkSettingsKey()">
      <div class="api-status none" id="settings-api-status">Not set — beer lookup will be unavailable</div>
      <div class="field-hint">Stored in localStorage on this device only. Never committed or sent anywhere except the Anthropic API.</div>
    </div>
''',
     '''    <div class="field-group"><div id="keyMount"><div class="field-hint">The key manager is loading. If this stays, check your connection and reload.</div></div></div>
'''),
    ("let beers=[],currentIndex=0,scores=[],sessionName='',apiKey='',lookupCache={};",
     "let beers=[],currentIndex=0,scores=[],sessionName='',lookupCache={};"),
    ("    apiKey=s.apiKey||'';\n", ""),
    ('''    document.getElementById('settings-api-key').value=s.apiKey||'';
    checkSettingsKey();
  }catch(e){}
  document.getElementById('settings-modal').classList.add('open');''',
     '''  }catch(e){}
  if(window.AppKeys)window.AppKeys.mountSettings(document.getElementById('keyMount'));
  document.getElementById('settings-modal').classList.add('open');'''),
    ('''function checkSettingsKey(){
  const val=document.getElementById('settings-api-key').value.trim();
  const status=document.getElementById('settings-api-status');
  if(val.startsWith('sk-ant-')&&val.length>20){status.textContent='✓ Ready — beer lookup enabled';status.className='api-status ok';}
  else if(val.length>0){status.textContent='Looks invalid — double-check your key';status.className='api-status none';}
  else{status.textContent='Not set — beer lookup will be unavailable';status.className='api-status none';}
}

''', ''),
    ('''  const key=document.getElementById('settings-api-key').value.trim();
  const s={sessionName:sName,apiKey:key};''',
     '''  const s={sessionName:sName};'''),
    ("  sessionName=sName; apiKey=key;\n", "  sessionName=sName;\n"),
    ("  const hasKey=apiKey&&apiKey.startsWith('sk-ant-')&&apiKey.length>20;",
     "  const hasKey=!!(window.AppKeys&&window.AppKeys.has());"),
    ('''  btn.classList.add('loading');document.getElementById('lookup-btn-text').textContent='Looking up…';
  try{''',
     '''  const apiKey=window.AppKeys?await window.AppKeys.get():null;
  if(!apiKey){document.getElementById('lookup-btn-text').textContent='Add your Claude API key with the gear button';return;}
  btn.classList.add('loading');document.getElementById('lookup-btn-text').textContent='Looking up…';
  try{'''),
    ('''// ── URL SHARE IMPORT ──''',
     '''window.addEventListener('appaday:keychange',()=>{
  const b=document.getElementById('lookup-btn');
  if(b&&beers.length&&!lookupCache[currentIndex])b.style.display=(window.AppKeys&&window.AppKeys.has())?'flex':'none';
});

// ── URL SHARE IMPORT ──'''),
]

FORBID = [r'settings-api-key', r'checkSettingsKey', r'apiKey=s\.apiKey']
