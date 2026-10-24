# Day 100 Signal Desk. Key stored as a plain string under signaldesk-key.
LEGACY = "signaldesk-key"

EDITS = [
    ('''    <div class="row">
      <label for="k">Anthropic API key</label>
      <input type="password" id="k" placeholder="sk-ant-..." autocomplete="off" spellcheck="false">
      <div class="hint">Stored in this browser only, used for the briefing, and never committed anywhere. Get one at console.anthropic.com.</div>
    </div>
''',
     '''    <div class="row" id="keyMount"><div class="hint">The key manager is loading. If this stays, check your connection and reload.</div></div>
'''),
    ('''      <button class="btn" id="kclear">Forget key</button>
''', ''),
    ("var K_KEY = 'signaldesk-key', K_SESS", "var K_SESS"),
    ('''function runBrief(){
  var key=lsGet(K_KEY);
  if(!key){ openSettings(); toast('Add an API key first.'); return; }
''', '''async function runBrief(){
  if(!window.AppKeys){ toast('The key manager did not load. Check your connection and reload.'); return; }
  var key=await window.AppKeys.get();
  if(!key){ toast('Add your Claude API key with the gear button first.'); return; }
'''),
    ("  $('k').value=lsGet(K_KEY);\n", "  if(window.AppKeys) window.AppKeys.mountSettings($('keyMount'));\n"),
    ('''    var v=$('k').value.trim();
    if(v) lsSet(K_KEY,v);
''', ''),
    ("  $('kclear').onclick=function(){ lsDel(K_KEY); $('k').value=''; toast('Key forgotten'); };\n", ""),
]

FORBID = [r'K_KEY', r"\$\('k'\)", r'kclear']
