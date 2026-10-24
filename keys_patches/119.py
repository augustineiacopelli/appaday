# Day 119 Room Read. Key lives inside a JSON settings object (roomread_settings) as apiKey.
LEGACY = "roomread_settings:apiKey"

EDITS = [
    ("    apiKey: '',\n    sessionName: '',", "    sessionName: '',"),
    ("        state.apiKey = parsed.apiKey || '';\n", ""),
    ("JSON.stringify({ apiKey: state.apiKey, sessionName: state.sessionName,", "JSON.stringify({ sessionName: state.sessionName,"),
    ('''        if(!state.apiKey){
          state.errorMsg = 'Add your Claude API key in Settings before analyzing.';
          render();
          return;
        }''', '''        if(!(window.AppKeys && window.AppKeys.has())){
          if(window.AppKeys){ window.AppKeys.get(); }
          state.errorMsg = 'Add your Claude API key, then tap Analyze again.';
          render();
          return;
        }'''),
    ('''  function callClaudeForRoom(room){
    var content''', '''  function callClaudeForRoom(room){
    if(!window.AppKeys){
      return Promise.reject(new Error('The key manager did not load. Check your connection and reload.'));
    }
    return window.AppKeys.get().then(function(apiKey){
      if(!apiKey){ throw new Error('Add your Claude API key with the Settings button first.'); }
      return callClaudeForRoomKeyed(room, apiKey);
    });
  }

  function callClaudeForRoomKeyed(room, apiKey){
    var content'''),
    ("        'x-api-key': state.apiKey,", "        'x-api-key': apiKey,"),
    ('''    sheet.appendChild(el('div', { class: 'field' }, [
      el('label', {}, ['Claude API Key']),
      el('input', { type: 'text', id: 'set-apikey', value: state.apiKey, placeholder: 'sk-ant-...' }, []),
      el('div', { class: 'hint' }, ['Stored only in this browser. Never sent anywhere except Anthropic\\u2019s API.'])
    ]));
''', '''    sheet.appendChild(el('div', { class: 'field', id: 'keyMount' }, []));
'''),
    ("      state.apiKey = document.getElementById('set-apikey').value.trim();\n", ""),
    ('''      modalRoot.appendChild(renderSettingsModal());
''', '''      modalRoot.appendChild(renderSettingsModal());
      if(window.AppKeys){ window.AppKeys.mountSettings(document.getElementById('keyMount')); }
'''),
]

# Pre-existing: the el() helper turns disabled: null into disabled="null", so Save Room and Analyze are always disabled.
FIXES = [
    ("      } else {\n        node.setAttribute(k, attrs[k]);\n      }\n    }\n    (children || [])",
     "      } else if(attrs[k] !== null && attrs[k] !== undefined){\n        node.setAttribute(k, attrs[k]);\n      }\n    }\n    (children || [])"),
]

FORBID = [r'state\.apiKey', r'set-apikey']
