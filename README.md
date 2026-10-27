# AppADay

**One complete, functional, mobile-friendly, visually polished web app, designed and shipped every single day.**

**Live portfolio:** https://augustineiacopelli.github.io/appaday/

AppADay is a daily discipline and public portfolio project by Augustine Iacopelli, inspired by Jonathan Mann's Song A Day. Every day one standalone app is designed, built, and published to GitHub Pages before midnight. Scope is always cut to fit the time; quality never is. Each app is single-purpose, usable on a 375px phone, intentionally designed, and live at its own URL the day it is built.

Every app is a single self-contained file of vanilla HTML, CSS, and JavaScript with no build step and no dependencies beyond Google Fonts. The AI-powered apps call the Anthropic API directly from the browser with the user's own key. Each carries a link back to this portfolio.

## The count

**All 173 shipped apps, numbered 001 through 173 with no gaps in the sequence.** Building since May 2026.

Of the 173, fifty-five are AI-powered. App 150, Saga Studio, is the latest milestone: it joins the four Saga forges of Days 146 to 149 into one studio that takes a classic RPG from its Charter to a game that plays on its own. The newest app, App 173, Key Ring Inspector, opens your encrypted AppADay key file with its passphrase and compares every AI app's key against the keys saved in this browser, marking each as a match, a mismatch, only in the file, only in the browser, or missing. It can fix gaps in either direction, test a key with a one token request, and download a fresh encrypted backup, and no key leaves the device except an optional Test. The nine categories are spread as follows.

| Category | Code | Shipped |
| --- | --- | --- |
| Creative | C | 19 |
| Data | D | 18 |
| Educational | E | 17 |
| Games | G | 19 |
| Health | H | 17 |
| Interactive | I | 16 |
| Productivity | P | 25 |
| Spirituality | S | 20 |
| Utility | U | 22 |

## How it is organized

The repository root holds this README and the portal `index.html`, which lists every app by number with its name, category, and live link. Each app lives in its own repository, `appaday-[NNN]-[name]`, published to GitHub Pages at `augustineiacopelli.github.io/appaday-[NNN]-[name]/`. The portal is the front door to the whole archive.

## Finding your way around

The portal opens with every app grouped by category, and a filter bar narrows the view to any single category. A search box in the same bar takes either a keyword or a plain question, such as a game for my kids or something to help me sleep, and returns the best matching apps ranked, each card showing which words it matched. It runs entirely in the browser with no AI: every app carries a hand-written set of keywords describing the problem it solves and who it is for, filler words are set aside, common synonyms are folded in, and apps are scored by where a word matched (name first, then keywords, category, and description), how distinctive the word is, and how much of the question they cover. It forgives a typo, finds apps by number, honors not or without to exclude a topic, and offers type-ahead suggestions. Clearing it returns you to whatever filter was active. A few standout builds are flagged as milestones and carry a small gold badge on the card. Every live app also has a star in its corner: tap it to save the app to a personal Starred view, which is kept in your browser so it persists between visits. Once you have starred anything, the portal opens to that Starred view on your next visit; otherwise it opens to the full archive. A New filter collects anything published since your last visit and shows a small count on the tab, which clears once you open it.

## API key ring

Every app that calls Claude gets its Anthropic API key from one shared script, `keys.js`, at the repository root, instead of carrying its own key field. Each app keeps its own key (named `appaday-[NNN]-[name]` in the Anthropic Console so usage can be watched app by app) and falls back to a shared default key. A small sheet asks for a key only when an app needs one and none is stored, and the Settings gear in each app holds a key manager. An encrypted key file, `appaday-keys.json`, restores every key at once if a browser clears its storage, which is what used to make keys disappear. Keys never leave the browser except to go to Anthropic. The ring went live on October 24, 2026 and has covered all 54 AI apps since October 27, 2026, when the 13 that had been held were repaired and moved onto it. Every AI app carries exactly one `keys.js` tag with its own number, and `health_check.py` verifies it weekly along with the other head tags. The full procedure and API are in `KEYS.md`. The retrofit tooling is `apply_keys.py`, one recipe per app in `keys_patches/`, and `keys_inventory.json`.

Every AI app also gets its Claude model from one shared script, `models.js`, at the repository root. Apps ask for a tier (haiku, sonnet, opus, or fable) and never carry a model ID of their own, so moving the whole portfolio to a new model is one edit to `config.json` and the matching table in `models.js`, with no app commits. Model pickers store the tier and take their names from `models.js`, so they relabel themselves. `health_check.py` fails any AI app that carries its own model ID or lacks the `models.js` tag, fails when `models.js` and `config.json` disagree, and checks that every app's inline scripts parse. The procedure and API are in `MODELS.md`, and the retrofit tooling is `apply_models.py`.

## The rules

One app ships every day, with no skip days and no carryover. An app counts only when it is functional, single-purpose, mobile-friendly, visually polished, and publicly live before midnight. If a build runs long, features are removed rather than the day extended. If something ships broken, it is fixed and republished the same day.

---

*Ship something every day. It compounds.*
