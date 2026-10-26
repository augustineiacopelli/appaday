# AppADay

**One complete, functional, mobile-friendly, visually polished web app, designed and shipped every single day.**

**Live portfolio:** https://augustineiacopelli.github.io/appaday/

AppADay is a daily discipline and public portfolio project by Augustine Iacopelli, inspired by Jonathan Mann's Song A Day. Every day one standalone app is designed, built, and published to GitHub Pages before midnight. Scope is always cut to fit the time; quality never is. Each app is single-purpose, usable on a 375px phone, intentionally designed, and live at its own URL the day it is built.

Every app is a single self-contained file of vanilla HTML, CSS, and JavaScript with no build step and no dependencies beyond Google Fonts. The AI-powered apps call the Anthropic API directly from the browser with the user's own key. Each carries a link back to this portfolio.

## The count

**All 172 shipped apps, numbered 001 through 172 with no gaps in the sequence.** Building since May 2026.

Of the 172, fifty-two are AI-powered. App 150, Saga Studio, is the latest milestone: it joins the four Saga forges of Days 146 to 149 into one studio that takes a classic RPG from its Charter to a game that plays on its own. The newest app, App 172, Slow Word, is a lectio divina companion for the daily Mass readings: it loads the Gospel of the day and paces you through four timed movements of reading, reflection, response, and rest with generated chimes, then keeps the word that stayed with you in a journal with a prayer streak. The nine categories are spread as follows.

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
| Utility | U | 21 |

## How it is organized

The repository root holds this README and the portal `index.html`, which lists every app by number with its name, category, and live link. Each app lives in its own repository, `appaday-[NNN]-[name]`, published to GitHub Pages at `augustineiacopelli.github.io/appaday-[NNN]-[name]/`. The portal is the front door to the whole archive.

## Finding your way around

The portal opens with every app grouped by category, and a filter bar narrows the view to any single category. A search box in the same bar takes either a keyword or a plain question, such as a game for my kids or something to help me sleep, and returns the best matching apps ranked, each card showing which words it matched. It runs entirely in the browser with no AI: every app carries a hand-written set of keywords describing the problem it solves and who it is for, filler words are set aside, common synonyms are folded in, and apps are scored by where a word matched (name first, then keywords, category, and description), how distinctive the word is, and how much of the question they cover. It forgives a typo, finds apps by number, honors not or without to exclude a topic, and offers type-ahead suggestions. Clearing it returns you to whatever filter was active. A few standout builds are flagged as milestones and carry a small gold badge on the card. Every live app also has a star in its corner: tap it to save the app to a personal Starred view, which is kept in your browser so it persists between visits. Once you have starred anything, the portal opens to that Starred view on your next visit; otherwise it opens to the full archive. A New filter collects anything published since your last visit and shows a small count on the tab, which clears once you open it.

## API key ring

Every app that calls Claude gets its Anthropic API key from one shared script, `keys.js`, at the repository root, instead of carrying its own key field. Each app keeps its own key (named `appaday-[NNN]-[name]` in the Anthropic Console so usage can be watched app by app) and falls back to a shared default key. A small sheet asks for a key only when an app needs one and none is stored, and the Settings gear in each app holds a key manager. An encrypted key file, `appaday-keys.json`, restores every key at once if a browser clears its storage, which is what used to make keys disappear. Keys never leave the browser except to go to Anthropic. The ring went live on October 24, 2026 and covers 40 of the 54 AI apps; the other 13 were already broken before the retrofit and are held until their fixes are approved. Every AI app carries exactly one `keys.js` tag with its own number, and `health_check.py` verifies it weekly along with the other head tags. The full procedure and API are in `KEYS.md`. The retrofit tooling is `apply_keys.py`, one recipe per app in `keys_patches/`, and `keys_inventory.json`.

## The rules

One app ships every day, with no skip days and no carryover. An app counts only when it is functional, single-purpose, mobile-friendly, visually polished, and publicly live before midnight. If a build runs long, features are removed rather than the day extended. If something ships broken, it is fixed and republished the same day.

---

*Ship something every day. It compounds.*
