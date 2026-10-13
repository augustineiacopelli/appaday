# Save to Phone

Every AppADay app helps a visitor save it to their phone's home screen. This file is the standing procedure, alongside ICONS.md.

## How it works

`save.js` at this repo's root is loaded by every app. On a phone browser, when the app is not already running from the home screen, it slides up a small bar offering to save that app. It renders inside a shadow root, so it never inherits or changes the app's styles.

The bar appears on its own once per app per device, after a short delay. When the URL carries `?save=1` it appears right away, already expanded into steps, and the parameter is removed from the address bar so it is never saved into the home screen icon. The portal's card share sheet has an **Open app / Scan to save** toggle that produces that `?save=1` link and QR code.

On iPhone and iPad the steps match the browser (Safari, Chrome, or another browser) and an arrow points at the toolbar. iOS never lets a page add itself, so guided steps are the ceiling there. On Android, Chrome uses the app's web app manifest to offer a real one tap **Install** button; other Android browsers get steps. In-app browsers (Instagram, Facebook, LinkedIn) are told to open the page in Safari or Chrome first.

Each app's manifest lives here at `manifests/NNN.webmanifest`, with install icons at `icons/192/NNN.png` and `icons/512/NNN.png`, all made by `generate_save_assets.py` from `icons/manifest.json`. The portal links `manifests/portfolio.webmanifest`, and its own Save to Phone sheet shows **Install now** when Android Chrome allows it.

To change the bar's wording, look, or behavior, edit `save.js` only. Every app picks up the change on its next load.

## Required tags in every app

Put these two lines in the app's `<head>`, directly after the `apple-mobile-web-app-status-bar-style` meta that ends the home screen block from ICONS.md. Replace `NNN` with the app number.

```html
<link rel="manifest" href="https://augustineiacopelli.github.io/appaday/manifests/NNN.webmanifest">
<script src="https://augustineiacopelli.github.io/appaday/save.js" defer></script>
```

Validate exactly one of each before shipping. `apply_save.py` checks and inserts them idempotently.

## Every time an app ships

1. Include the two tags above in the new app's `index.html` before it is pushed.
2. After the ICONS.md steps (`generate_icons.py` has written `icons/NNN.png` and `icons/manifest.json`), run:

   ```
   python3 generate_save_assets.py
   ```

   Commit the new `icons/192/NNN.png`, `icons/512/NNN.png`, and `manifests/NNN.webmanifest`. If existing files show as modified, discard those changes for the same Lucide reason given in ICONS.md.
3. Push in the same portal commit as the icon and portal update, so the manifest is live when the app goes up.

## Checking or repairing apps

```
python3 apply_save.py --root DIR            # dry run; DIR holds NNN.html files or <slug>/index.html clones
python3 apply_save.py --root DIR --write    # patch
```

## Notes

Apps keep working with or without `save.js`; if it fails to load, nothing breaks. All apps share the `augustineiacopelli.github.io` origin, so the "already shown" list (`appaday-save-seen` in localStorage) is shared across apps and the portal; it only stores app numbers.
