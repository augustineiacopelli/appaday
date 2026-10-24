# Day 131 Cloud Reader. Key stored as a plain string under cloudreader-key.
LEGACY = "cloudreader-key"

EDITS = [
    ('''    <p>Cloud Reader calls Claude straight from this browser. Your key is stored only in this device's local storage and never leaves it except to reach Anthropic.</p>
    <label for="key-input">Key</label>
    <input type="password" id="key-input" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">
    <div class="modal-row">
      <button class="btn-solid" id="save-key" type="button">Save key</button>
      <button class="btn-ghost" id="close-key" type="button">Close</button>
    </div>''', '''    <div id="keyMount"><p>The key manager is loading. If this stays, check your connection and reload.</p></div>
    <div class="modal-row">
      <button class="btn-solid" id="close-key" type="button">Close</button>
    </div>'''),
    ("  var KEY_STORE = 'cloudreader-key';\n", ""),
    ('''  function loadKey() {
    try {
      return window.localStorage.getItem(KEY_STORE) || '';
    } catch (err) {
      return '';
    }
  }

  function saveKey(value) {
    try {
      if (value) {
        window.localStorage.setItem(KEY_STORE, value);
      } else {
        window.localStorage.removeItem(KEY_STORE);
      }
      return true;
    } catch (err) {
      return false;
    }
  }
''', '''  function hasKey() {
    return !!(window.AppKeys && window.AppKeys.has());
  }
'''),
    ('''    el.overlay.classList.add('on');
    el.keyInput.value = loadKey();
    window.setTimeout(function () { el.keyInput.focus(); }, 30);''', '''    el.overlay.classList.add('on');
    if (window.AppKeys) { window.AppKeys.mountSettings($('keyMount')); }'''),
    ('''    var key = loadKey();
    if (!key) {
      openSettings();
      throw new Error('Add your Anthropic API key in the key panel, then shoot the sky again.');
    }''', '''    if (!window.AppKeys) {
      throw new Error('The key manager did not load. Check your connection and reload.');
    }
    var key = await window.AppKeys.get();
    if (!key) {
      throw new Error('Add your Claude API key with the KEY button, then shoot the sky again.');
    }'''),
    ("      if (loadKey()) {\n        await runOutlook(hourly, label);", "      if (hasKey()) {\n        await runOutlook(hourly, label);"),
    ("    el.keyInput = $('key-input');\n", ""),
    ('''    $('save-key').addEventListener('click', function () {
      var value = el.keyInput.value.trim();
      saveKey(value);
      closeSettings();
      if (value && latestHourly) {
        runOutlook(latestHourly, el.geoStatus.textContent.replace('Model data for ', ''));
      }
    });
''', '''    window.addEventListener('appaday:keychange', function () {
      if (hasKey() && latestHourly) {
        runOutlook(latestHourly, el.geoStatus.textContent.replace('Model data for ', ''));
      }
    });
'''),
    ("    if (!loadKey()) { openSettings(); }", "    if (window.AppKeys && !hasKey()) { window.AppKeys.get(); }"),
]

FORBID = [r'loadKey', r'saveKey', r'key-input', r'KEY_STORE']
