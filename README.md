# AppADay

**One complete, functional, mobile-friendly, visually polished web app, designed and shipped every single day.**

**Live portfolio:** https://augustineiacopelli.github.io/appaday/

AppADay is a daily discipline and public portfolio project by Augustine Iacopelli, inspired by Jonathan Mann's Song A Day. Every day one standalone app is designed, built, and published to GitHub Pages before midnight. Scope is always cut to fit the time; quality never is. Each app is single-purpose, usable on a 375px phone, intentionally designed, and live at its own URL the day it is built.

Every app is a single self-contained file of vanilla HTML, CSS, and JavaScript with no build step and no dependencies beyond Google Fonts. The AI-powered apps call the Anthropic API directly from the browser with the user's own key. Each carries a link back to this portfolio.

## The count

**All 105 shipped apps, numbered 001 through 105 with no gaps in the sequence.** Building since May 2026.

Of the 104, twenty-six are AI-powered. The nine categories are spread as follows.

| Category | Code | Shipped |
| --- | --- | --- |
| Creative | C | 9 |
| Data | D | 10 |
| Educational | E | 9 |
| Games | G | 18 |
| Health | H | 10 |
| Interactive | I | 10 |
| Productivity | P | 13 |
| Spirituality | S | 12 |
| Utility | U | 14 |

## How it is organized

The repository root holds this README and the portal `index.html`, which lists every app by number with its name, category, and live link. Each app lives in its own repository, `appaday-[NNN]-[name]`, published to GitHub Pages at `augustineiacopelli.github.io/appaday-[NNN]-[name]/`. The portal is the front door to the whole archive.

## Finding your way around

The portal opens with every app grouped by category, and a filter bar narrows the view to any single category. A search box in the same bar finds any app by keyword, matching its number, name, description, and category, with type-ahead suggestions that complete what you type and light stemming so a word like brewing still finds brew. Clearing it returns you to whatever filter was active. A few standout builds are flagged as milestones and carry a small gold badge on the card. Every live app also has a star in its corner: tap it to save the app to a personal Starred view, which is kept in your browser so it persists between visits. Once you have starred anything, the portal opens to that Starred view on your next visit; otherwise it opens to the full archive. A New filter collects anything published since your last visit and shows a small count on the tab, which clears once you open it.

## The rules

One app ships every day, with no skip days and no carryover. An app counts only when it is functional, single-purpose, mobile-friendly, visually polished, and publicly live before midnight. If a build runs long, features are removed rather than the day extended. If something ships broken, it is fixed and republished the same day.

---

*Ship something every day. It compounds.*
