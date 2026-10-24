# Shared edits for the Kit family (Days 146 to 149): Kit.settings held the key in the kit:settings JSON object.
# Every AI call goes through Kit.claude, so the key comes from AppKeys there. Silent background calls with no key
# skip the sheet and fail with NO_KEY exactly as before; user facing calls open the sheet.
LEGACY = "kit:settings:key"

EDITS = [
    ('          \'<div class="field span-all"><label class="field-label" for="setKey">Claude API key</label>\' +\n          \'<div class="ref-row"><input class="inp mono" id="setKey" type="password" autocomplete="off" spellcheck="false" placeholder="sk-ant-...">\' +\n          \'<button class="btn btn-icon" type="button" id="setKeyShow" aria-label="Show or hide key" title="Show or hide">\' + Kit.icon(\'key\') + \'</button></div>\' +\n          \'<div class="field-help">Stored only in this browser. AI features are optional; everything else works without a key.</div></div>\' +\n',
     '          \'<div class="field span-all" id="setKeyMount"></div>\' +\n'),
    ("        b.querySelector('#setKeyShow').addEventListener('click', function () { refs.key.type = refs.key.type === 'password' ? 'text' : 'password'; });\n", ''),
    ("        refs.key = b.querySelector('#setKey'); refs.key.value = s.key;\n", "        if (window.AppKeys) window.AppKeys.mountSettings(b.querySelector('#setKeyMount'));\n"),
    ("        settingsCache = { key: typeof s.key === 'string' ? s.key : '', session: typeof s.session === 'string' ? s.session : '', tiers: {} };", "        settingsCache = { key: '', session: typeof s.session === 'string' ? s.session : '', tiers: {} };"),
    ('      if (patch.key !== undefined) s.key = String(patch.key).trim();\n', ''),
    ('    hasKey: function () { return !!Kit.settings.get().key; },', '    hasKey: function () { return !!(window.AppKeys && window.AppKeys.has()); },'),
    ("        { label: 'Clear key', kind: 'ghost', onClick: function () { refs.key.value = ''; save(); Kit.ui.toast('API key removed from this browser.', 'ok'); return false; } },\n", ''),
    ('      Kit.settings.set({ key: refs.key.value, session: refs.session.value, tiers: tiers });', '      Kit.settings.set({ session: refs.session.value, tiers: tiers });'),
    ('    var key = Kit.settings.get().key;\n', '    var key = null;\n    if (window.AppKeys) key = (opts.silent && !window.AppKeys.has()) ? null : await window.AppKeys.get();\n'),
]

FORBID = [r'refs\.key\b', r'setKeyShow', r'settings\.get\(\)\.key']
