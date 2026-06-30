# AppADay Portal

**Live:** https://augustineiacopelli.github.io/appaday/

The landing page and archive for the AppADay project — one complete, functional, mobile-friendly web app built and shipped every day, started May 7, 2026. Inspired by Jonathan Mann's Song A Day project.

---

## What This Is

This `index.html` is the root of the AppADay GitHub Pages portfolio. It displays every shipped app as a card, grouped by category, with filtering, live app count, and a streak counter calculated from the ship dates.

---

## Usage

Open `index.html` in any browser. No build step, no dependencies, no server required.

Use the sticky filter bar to narrow the view by category:

- **Games** — browser games, puzzles, scored experiences
- **Interactive** — experience-driven apps with no win state (meditative, generative, exploratory)
- **Utility** — converters, generators, formatters, single-function tools
- **Creative** — apps that make something: poems, jokes, palettes, presentations
- **Data** — charts, visualizations, dashboards
- **Productivity** — trackers, planners, task managers, life tools
- **Health & Wellness** — physical and mental wellbeing: sleep, breathing, hydration, training
- **Spirituality** — prayer, scripture, saints, and faith tools

Apps that use the Claude API display an **AI** badge on their card. AI is an attribute, not a category.

Click any card to open that app in a new tab.

---

## Adding a New App

Open `index.html` and find the `APPS` array near the top of the `<script>` block. Append a new object following this format:

```js
{
  num:  "054",
  name: "App Name",
  cat:  "G",           // G · I · U · C · D · P · H · S
  date: "2026-06-30",  // YYYY-MM-DD
  desc: "One sentence description of what the app does.",
  url:  "https://augustineiacopelli.github.io/appaday-054-app-name/",
  ai:   true           // include only if the app uses the Claude API
}
```

Save, commit, and push. The portal updates automatically — no other changes needed.

---

## Technical Notes

- Single-file vanilla HTML/CSS/JS. No frameworks, no external dependencies beyond Google Fonts.
- Category grouping, filtering, card rendering, streak calculation, and app count are all computed from the `APPS` array at runtime.
- Streak is calculated as the longest consecutive run counting backward from the most recently shipped app by sequential number.
- AI badge rendered automatically on any entry with `ai:true`.
- Cards animate in with staggered fade-up on each filter change.
- Fully responsive; tested on 375px mobile viewport and desktop.

---

## Definition of Complete

- [x] All 54 shipped apps listed with correct numbers, names, categories, dates, and URLs
- [x] Category filter works for all eight types (G · I · U · C · D · P · H · S)
- [x] AI badge displayed on all nine Claude API apps
- [x] App count and streak stats render correctly
- [x] Cards link to live GitHub Pages URLs
- [x] Mobile-friendly at 375px viewport
- [x] Visually polished — editorial paper aesthetic, DM Serif Display / DM Mono typography
- [x] Published at repo root as `index.html`

---

*Ship something every day. It compounds.*
