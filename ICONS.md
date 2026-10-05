# Home Screen Icons

Every AppADay app ships with its own home screen icon and opens full screen, like a native app, when it is saved to a phone's home screen. This file is the standing procedure.

## How it works

Icons live in this repo at `icons/NNN.png` (180x180, opaque PNG) and are served from `https://augustineiacopelli.github.io/appaday/icons/NNN.png`. Each app's `index.html` points at its own icon. Nothing is copied into the app repos.

Design: a white Lucide glyph on a gradient of the app's category color. The glyph is 52 percent of the square with stroke 2.35. Category colors are C `#A63D9E`, D `#B8860B`, E `#1F7A8C`, G `#276EB7`, H `#D14D72`, I `#5B4BC4`, P `#C8401A`, S `#6A4C93`, U `#289664`. The portfolio icon is the terracotta A on ink.

## Required tags in every app

Put this block in the app's `<head>`, directly after the viewport meta. Replace `NNN` with the app number and `Short Name` with a home screen title of 12 characters or fewer.

```html
<link rel="apple-touch-icon" href="https://augustineiacopelli.github.io/appaday/icons/NNN.png">
<meta name="apple-mobile-web-app-title" content="Short Name">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
```

The first two give the icon and its label. The last three make the saved icon launch full screen without the Safari address bar, with a black status bar.

## Every time an app ships

1. Include the tag block above in the new app's `index.html` before it is pushed.
2. In this repo, add one line for the new app to `GLYPH_MAP` in `generate_icons.py` (a Lucide icon name from lucide.dev) and one line to `TITLE` in `apply_icons.py` if the app name is longer than 12 characters.
3. After the new app has been added to the portal `index.html`, run:

   ```
   pip install cairosvg --break-system-packages
   npm install lucide-static
   python3 generate_icons.py
   ```

   Commit only the new `icons/NNN.png` plus `icons/manifest.json`. If existing icons show as modified, discard those changes, because a newer Lucide release can redraw a glyph slightly.
4. Push this repo in the same commit as the portal update, so the icon URL is live before anyone saves the app.

## Checking or repairing apps

`apply_icons.py` patches local clones of the app repos and is idempotent per tag. It adds only the tags a file is missing and never duplicates one.

```
python3 apply_icons.py --root ~/appaday-repos            # dry run
python3 apply_icons.py --root ~/appaday-repos --write    # patch
```

`retrofit_icons.py` does the same through the GitHub Contents API with the GitHub CLI, with no cloning required. Pass `--push` to commit.

## Notes

iOS caches home screen icons aggressively. An app saved before its icon existed keeps the old screenshot until it is removed from the home screen and added again.

In full screen mode, links to other sites open in Safari. File downloads made from a Blob link can be unreliable on iOS. Apps that export files should be tested from the home screen as well as in the browser.
