# AppADay

**One complete, functional, mobile-friendly, visually polished web app, designed and shipped every single day.**

**Live portfolio:** https://augustineiacopelli.github.io/appaday/

AppADay is a daily discipline and public portfolio project by Augustine Iacopelli, inspired by Jonathan Mann's Song A Day. Every day one standalone app is designed, built, and published to GitHub Pages before midnight. Scope is always cut to fit the time; quality never is. Each app is single-purpose, usable on a 375px phone, intentionally designed, and live at its own URL the day it is built.

Every app is a single self-contained file of vanilla HTML, CSS, and JavaScript with no build step and no dependencies beyond Google Fonts. The AI-powered apps call the Anthropic API directly from the browser with the user's own key. Each carries a link back to this portfolio.

## The count

**All 80 shipped apps, numbered 001 through 080 with no gaps in the sequence.** Building since May 2026.

Of the 80, seventeen are AI-powered. The nine categories are spread as follows.

| Category | Code | Shipped |
| --- | --- | --- |
| Creative | C | 6 |
| Data | D | 7 |
| Educational | E | 7 |
| Games | G | 16 |
| Health | H | 9 |
| Interactive | I | 6 |
| Productivity | P | 10 |
| Spirituality | S | 8 |
| Utility | U | 11 |

## How it is organized

The repository root holds this README and the portal `index.html`, which lists every app by number with its name, category, and live link. Each app lives in its own repository, `appaday-[NNN]-[name]`, published to GitHub Pages at `augustineiacopelli.github.io/appaday-[NNN]-[name]/`. The portal is the front door to the whole archive.

## The rules

One app ships every day, with no skip days and no carryover. An app counts only when it is functional, single-purpose, mobile-friendly, visually polished, and publicly live before midnight. If a build runs long, features are removed rather than the day extended. If something ships broken, it is fixed and republished the same day.

---

*Ship something every day. It compounds.*
