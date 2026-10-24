# Day 158 Gratitude Jar. Key stored as a plain string under appaday-158-apikey.
LEGACY = "appaday-158-apikey"

EDITS = [
    ('''    <label for="apiKey">Anthropic API key</label>
    <div class="keyrow">
      <input id="apiKey" class="field" type="password" spellcheck="false" autocapitalize="off" placeholder="sk-ant-...">
      <button type="button" class="btn ghost" id="keyToggle" aria-pressed="false">Show</button>
    </div>
    <p class="note">Used only for the reflection when a jar fills. Stored in this browser and sent only to the Anthropic API.</p>
''',
     '''    <div id="keyMount"></div>
    <p class="note">Used only for the reflection when a jar fills.</p>
'''),
    ("  const KEY_KEY = 'appaday-158-apikey';\n", ""),
    ("    const hasKey = !!(lsGet(KEY_KEY) || '').trim();\n",
     "    const hasKey = !!(window.AppKeys && window.AppKeys.has());\n"),
    ("r.addEventListener('click', function () { state.lastError = null; save(); requestReflection(); });",
     "r.addEventListener('click', function () { state.lastError = null; save(); requestReflection(true); });"),
    ('''      save();
      requestReflection();
    }
  }''',
     '''      save();
      requestReflection(true);
    }
  }'''),
    ('''  async function requestReflection() {
    if (busy || !jarIsWaiting() || state.reflection) return;
    const key = (lsGet(KEY_KEY) || '').trim();
''',
     '''  async function requestReflection(interactive) {
    if (busy || !jarIsWaiting() || state.reflection) return;
    const key = window.AppKeys ? ((interactive || window.AppKeys.has()) ? await window.AppKeys.get() : null) : null;
'''),
    ('''    $('apiKey').value = lsGet(KEY_KEY) || '';
    $('apiKey').type = 'password';
    $('keyToggle').textContent = 'Show';
    $('keyToggle').setAttribute('aria-pressed', 'false');
''',
     '''    if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));
'''),
    ('''  $('keyToggle').addEventListener('click', function () {
    const showing = $('apiKey').type === 'text';
    $('apiKey').type = showing ? 'password' : 'text';
    this.textContent = showing ? 'Show' : 'Hide';
    this.setAttribute('aria-pressed', showing ? 'false' : 'true');
  });
''',
     '''  window.addEventListener('appaday:keychange', function () { render(); });
'''),
    ('''    const k = $('apiKey').value.trim();
    const n = $('sessionName').value.trim();
    if (k) lsSet(KEY_KEY, k); else lsDel(KEY_KEY);
''',
     '''    const n = $('sessionName').value.trim();
'''),
]

FORBID = [r"KEY_KEY", r"\$\('apiKey'\)", r"keyToggle"]
