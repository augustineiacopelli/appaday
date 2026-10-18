# AppADay

**One complete, functional, mobile-friendly, visually polished web app, designed and shipped every single day.**

**Live portfolio:** https://augustineiacopelli.github.io/appaday/

AppADay is a daily discipline and public portfolio project by Augustine Iacopelli, inspired by Jonathan Mann's Song A Day. Every day one standalone app is designed, built, and published to GitHub Pages before midnight. Scope is always cut to fit the time; quality never is. Each app is single-purpose, usable on a 375px phone, intentionally designed, and live at its own URL the day it is built.

Every app is a single self-contained file of vanilla HTML, CSS, and JavaScript with no build step and no dependencies beyond Google Fonts. The AI-powered apps call the Anthropic API directly from the browser with the user's own key. Each carries a link back to this portfolio.

## The count

**All 164 shipped apps, numbered 001 through 164 with no gaps in the sequence.** Building since May 2026.

Of the 164, fifty-one are AI-powered. App 150, Saga Studio, is the latest milestone: it joins the four Saga forges of Days 146 to 149 into one studio that takes a classic RPG from its Charter to a game that plays on its own. The newest app, App 164, Brotherhood Check-In, gives a men's group or accountability partner a private weekly practice: editable questions on prayer, honesty, purity, work, family, and service, a check on whether last week's commitment was kept, eight weeks of patterns, and a copyable summary that leaves private answers out unless chosen. The nine categories are spread as follows.

| Category | Code | Shipped |
| --- | --- | --- |
| Creative | C | 19 |
| Data | D | 17 |
| Educational | E | 16 |
| Games | G | 19 |
| Health | H | 16 |
| Interactive | I | 14 |
| Productivity | P | 24 |
| Spirituality | S | 19 |
| Utility | U | 20 |

## How it is organized

The repository root holds this README and the portal `index.html`, which lists every app by number with its name, category, and live link. Each app lives in its own repository, `appaday-[NNN]-[name]`, published to GitHub Pages at `augustineiacopelli.github.io/appaday-[NNN]-[name]/`. The portal is the front door to the whole archive.

## Finding your way around

The portal opens with every app grouped by category, and a filter bar narrows the view to any single category. A search box in the same bar takes either a keyword or a plain question, such as a game for my kids or something to help me sleep, and returns the best matching apps ranked, each card showing which words it matched. It runs entirely in the browser with no AI: every app carries a hand-written set of keywords describing the problem it solves and who it is for, filler words are set aside, common synonyms are folded in, and apps are scored by where a word matched (name first, then keywords, category, and description), how distinctive the word is, and how much of the question they cover. It forgives a typo, finds apps by number, honors not or without to exclude a topic, and offers type-ahead suggestions. Clearing it returns you to whatever filter was active. A few standout builds are flagged as milestones and carry a small gold badge on the card. Every live app also has a star in its corner: tap it to save the app to a personal Starred view, which is kept in your browser so it persists between visits. Once you have starred anything, the portal opens to that Starred view on your next visit; otherwise it opens to the full archive. A New filter collects anything published since your last visit and shows a small count on the tab, which clears once you open it.

## The rules

One app ships every day, with no skip days and no carryover. An app counts only when it is functional, single-purpose, mobile-friendly, visually polished, and publicly live before midnight. If a build runs long, features are removed rather than the day extended. If something ships broken, it is fixed and republished the same day.

---

*Ship something every day. It compounds.*
