# API Key Ring

Every AppADay app that calls Claude gets its Anthropic API key from one shared script, `keys.js`, at this repo's root. This file is the standing procedure, alongside ICONS.md and SAVE.md.

## How it works

Each app's key lives in localStorage under `appaday.key.NNN`. When an app has no key of its own it uses the default key, `appaday.key.default`. Per app keys exist so usage can be watched key by key in the Anthropic Console, where each one is named `appaday-NNN-slug`. The default key covers every app that has not been given its own.

All apps share the `augustineiacopelli.github.io` origin, so in a normal browser tab they share these keys. A home screen app on iPhone has its own isolated storage, and any browser can clear or evict storage, which is why keys used to disappear. The fix is the key ring file: `appaday-keys.json`, encrypted with a passphrase, holding the default key and every per app key. Restoring it writes every key back at once.

The key sheet slides up only when an app asks for a key and none is stored. It never appears just because an app opened. It offers **Enter a key** and **Restore from my key file**. Enter a key is the highlighted choice for a first time visitor; once a key file has been created, updated, or restored in this browser (flag `appaday.key.hasFile`), Restore moves to the top. Clearing site data also clears that flag, so after a wipe both buttons show and the text points returning users to Restore. If it is dismissed, it stays away for the rest of that browser session (a sessionStorage flag), and the app's Settings still works.

Entering a key checks it first with `GET https://api.anthropic.com/v1/models`. If that request cannot be made, it falls back to a one token message on the haiku tier from `config.json`. A rejected key is never saved. If Anthropic cannot be reached at all, the user may save without checking. After saving, the sheet offers **Add to my key file**, **Create a key file**, or **Not now**. The scope toggle, **This app only** or **All my apps** (default), is remembered under `appaday.key.scopePref`. Choosing All my apps saves the default key and removes this app's own key so the new one takes effect here.

On load, `keys.js` asks the browser to keep storage persistent (`navigator.storage.persist()`), and copies a key saved under the app's old storage name into `appaday.key.NNN` once. The old value is left in place for rollback, and a flag, `appaday.key.migrated.NNN`, stops the copy from running again after the user forgets the key.

To change the sheet, the Settings section, wording, or validation for every app at once, edit `keys.js` only.

## Required tag in every AI app

Put this line in the app's `<head>`, directly after the `save.js` tag. Replace `NNN` with the app number and `OLDNAME` with the app's previous key storage name. Set `data-accent` to the app's category color from ICONS.md.

```html
<script src="https://augustineiacopelli.github.io/appaday/keys.js" data-app="NNN" data-legacy-key="OLDNAME" data-accent="#RRGGBB" defer></script>
```

`data-app` is required. `data-accent` is optional and defaults to a neutral gray. `data-legacy-key` is optional, may list several names separated by commas, and accepts three forms:

| Form | Reads |
| --- | --- |
| `name` | a plain string, or a JSON string, stored under `name` |
| `name` holding JSON | the first of `apiKey`, `api_key`, `anthropicKey`, `anthropic_api_key`, `claudeKey`, `key` |
| `name:field` or `name:a.b` | that field inside the JSON object stored under `name` |

Validate exactly one keys.js tag per AI app, with `data-app` matching the repo number. New AI apps have no old name and omit `data-legacy-key`.

## API

`keys.js` is deferred, so it runs after the app's inline script and before `DOMContentLoaded`. Call it from event handlers or from a `DOMContentLoaded` listener, never at the top level of the inline script.

| Call | Does |
| --- | --- |
| `AppKeys.get()` | Promise of the key. Per app key first, then the default. With neither, opens the sheet and resolves when a key is entered or restored, or `null` if the sheet is dismissed (or was dismissed earlier this session). |
| `AppKeys.has()` | `true` when a per app or default key is stored. Never opens UI. |
| `AppKeys.mountSettings(el)` | Renders the key section into `el` inside the app's Settings modal: source (This app or Default), last four characters only, and Enter key, Restore from key file, Back up to key file, and Forget key. Safe to call every time Settings opens. |
| `AppKeys.forget(scope)` | `"app"` clears this app's key; `"default"` clears the shared default. |

Every change fires a window event, `appaday:keychange`, with `detail.has`. All injected DOM and styles use the `ak-` prefix. The Settings section inherits the app's text color and font; the sheet follows the system light or dark mode.

Apps whose Claude call sits in a script file of their own repository (150 Saga Studio, through core/kit.js) are found by `inventory_keys.py`, which follows an app's relative script files when its index.html never mentions api.anthropic.com. App 173 (Key Ring Inspector) no longer needs patching when an AI app ships: at load it reads the portal page and lists every APPS entry flagged `ai:true`, keeping an embedded list only as a fallback. The one manual step is therefore the `ai:true` flag on the new app's portal entry, and the weekly `health_check.py` fails when that flag and the app's real Claude call (in its index.html or in one of its own script files) disagree in either direction.

## Integrating an app

1. Add the tag above after `save.js`.
2. Replace the Settings key field, its show and save and clear buttons, and its key status line with one mount element, and mount it when Settings opens:

   ```html
   <div id="keyMount"></div>
   ```

   ```js
   function openSettings() {
     if (window.AppKeys) window.AppKeys.mountSettings($('keyMount'));
     openModal($('settingsScrim'), null, closeSettings);
   }
   ```

3. In `callClaude()`, drop the key parameter and get the key itself, returning quietly when there is none:

   ```js
   async function callClaude(model, prompt) {
     var apiKey = window.AppKeys ? await window.AppKeys.get() : null;
     if (!apiKey) return null;
     /* fetch as before, with 'x-api-key': apiKey */
   }
   ```

4. Where the app used to check for a saved key before working, ask instead, before any busy state:

   ```js
   if (!window.AppKeys) { setStatus('The key manager did not load. Check your connection and reload.', true); return; }
   if (!(await window.AppKeys.get())) { setStatus('Add your Claude API key with the gear button to continue.'); return; }
   ```

   Treat a `null` result from `callClaude()` the same way.
5. Remove the app's own key reads and writes (`settings.apiKey` and the like). Leave the old storage name in `data-legacy-key` so existing keys migrate.

## Key ring file

The file is `appaday-keys.json`:

```json
{"format":"appaday-keyring","v":1,"kdf":"PBKDF2-SHA256","iter":600000,"salt":"b64","iv":"b64","ct":"b64"}
```

`ct` is AES-GCM (256 bit) ciphertext of this JSON, under a key derived from the passphrase with PBKDF2-SHA256 at 600,000 iterations:

```json
{"default":"KEY or null","apps":{"NNN":"KEY"},"updated":"ISO date"}
```

The passphrase is at least 12 characters, typed twice when a file is created, normalized to NFC, and never stored. Every save uses a fresh 16 byte salt and 12 byte IV. A wrong passphrase gives one sentence: the file cannot be opened without its passphrase, and a new file can be made by entering the keys again.

**Create** builds a ring from every key in this browser's storage. **Add to existing** opens the user's file with its passphrase, merges in the new key (or, from Settings, every key in this browser), and saves it again with the same passphrase. **Restore** writes every entry in the file into storage.

Saving takes a separate tap after encryption, so the browser still counts it as a user action. On desktop Chrome and Edge, a file opened for Add is saved back over itself; otherwise the save dialog opens. On iPhone and Android the share sheet opens so the file can go to Files or Drive. Anywhere else the file downloads, with a note to replace the older copy.

## Every time an AI app ships

1. Include the keys.js tag in the new app's `index.html`, with `data-app` and `data-accent`, and build Settings and `callClaude()` as in Integrating an app.
2. In the Anthropic Console, create a key named `appaday-NNN-slug`, ideally with a spend cap.
3. In the live app, open Settings, Enter key, choose **This app only**, then **Add to my key file** and replace the old file with the saved one.

## Safety rules

The key is sent only to api.anthropic.com, in the `x-api-key` header. It is never logged and never placed in a URL. Settings shows only its last four characters. Keys stay in the browser; a key with a spend cap is the right protection against a lost device or a leaked file.

## Notes

Apps keep loading if `keys.js` fails; they report that the key manager did not load instead of calling the API. The key file is useless without its passphrase, but keep it somewhere private all the same.
