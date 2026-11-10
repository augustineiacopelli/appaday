# Claude models for AppADay apps

Every AI app gets its Claude model from one shared script, `models.js`, at the portal root. No app carries a model ID of its own, so moving the whole portfolio to a new model is one edit here and no app commits.

## Changing models

1. Edit `config.json`: the model ID for each tier under `models`, the name people see under `labels`, and today's date in `lastUpdated`.
2. Make the same edit to the `EMBED` table near the top of `models.js`, including `lastUpdated`.
3. Run `python3 health_check.py --offline`. It fails if `models.js` and `config.json` disagree.
4. Push. Every app picks up the new models on its next load, and model pickers relabel themselves.

`config.json` is the source of truth and is fetched on every load. `EMBED` exists so a first visit, a slow connection, or an offline load still sends the current model. Whichever of the two has the newer `lastUpdated` wins, and a fetched `config.json` is cached in the browser under `appaday.models`.

## Tiers

| Tier | Use it for |
| --- | --- |
| `haiku` | Simple generation and classification where speed and cost matter most |
| `sonnet` | The default for general work |
| `opus` | Deep reasoning and analysis, or output that has to be right the first time |
| `fable` | Specialized tasks |

## Adding models.js to an app

Put the tag directly after the `save.js` tag and before `keys.js`. It is not deferred, so `window.AppModels` exists before the app's own inline script runs:

```html
<script src="https://augustineiacopelli.github.io/appaday/models.js"></script>
```

Then ask by tier:

```js
var CLAUDE_MODEL = window.AppModels ? window.AppModels.id('sonnet') : '';   // at load
body.model = window.AppModels.id('opus');                                    // at call time
const model = await window.AppModels.get('sonnet');                          // waits up to 2.5 s for config.json
```

Never write a model ID such as `claude-sonnet-5-5` into an app. The weekly health check fails any AI app that does.

## API

| Call | Returns |
| --- | --- |
| `AppModels.id(tier)` | The model ID for the tier, right away |
| `AppModels.get(tier)` | A promise of the model ID once `config.json` has loaded (or 2.5 s have passed) |
| `AppModels.label(tier)` | The display name, such as `Sonnet 5.5` |
| `AppModels.tier(x)` | The tier for a tier name or any model ID, so an old saved `claude-opus-4-8` becomes `opus` |
| `AppModels.tiers()` | `['haiku', 'sonnet', 'opus', 'fable']` |
| `AppModels.onChange(fn)` | Calls `fn` if `config.json` brings newer models during the visit |
| `AppModels.fill(root)` | Refills the markup helpers below inside `root` (run automatically on load and on change) |

| `AppModels.thinking(x)` | The lowest thinking setting the tier's (or model ID's) model accepts, such as `{type: 'between_tools'}`, or `undefined` when the field must be left out |
| `AppModels.text(data)` | Every text block of a Messages API reply joined, so a leading thinking block never hides the answer |

Unknown tiers fall back to `sonnet`.

## Thinking and max_tokens (added November 9, 2026)

Sonnet 5.5, Sonnet 5, Haiku 5.5 and Opus 5.5 all think by default when a request carries no `thinking` field, and thinking tokens count against `max_tokens`. A small budget can be spent entirely on thinking, so the reply arrives with no text block. The accepted way to turn thinking off differs by model: Sonnet 5.5 takes `{type: 'between_tools'}` and rejects `disabled` with a 400, Sonnet 5 and Haiku 5.5 take `disabled`, and Opus 5.5 always thinks. Every AI app request body therefore carries

```js
thinking: (window.AppModels && window.AppModels.thinking ? window.AppModels.thinking(MODEL_OR_TIER) : undefined),
```

which `JSON.stringify` drops when it is `undefined`. Read replies with `AppModels.text(data)` or by filtering for `type === 'text'`, never `content[0].text`. An app that calls the `opus` tier gets no thinking field, so its `max_tokens` must leave room for thinking (a few thousand at least). When a tier moves to a new model, add the new model to the `LEAN` table in `models.js` in the same commit as the `EMBED` edit. On November 9, 2026, the day sonnet moved to Sonnet 5.5, 42 apps were patched this way (37 gained the field, 029 on the opus tier got larger budgets instead, 136, 140, 141 and 144 had sent `disabled`, 140 also had a forced `tool_choice` that Sonnet 5.5 rejects, and 017, 022, 023 and 029 read `content[0].text`). Apps that already retried through the thinking forms (073, 134, 145, 146 to 150, 153, 155, 158, 160, 170, 176, 180, 186) were left as they were.

## Model names in the interface

Never type a model name into an app. Use the markup helpers and `models.js` fills them in:

```html
<span data-model-label="sonnet"></span>          <!-- Sonnet 5.5 -->
<span data-model-id="sonnet"></span>             <!-- claude-sonnet-5-5 -->
<select id="modelSel">
  <option value="sonnet" data-model-tier="sonnet" data-note="balanced (default)"></option>
  <option value="opus" data-model-tier="opus" data-note="deepest"></option>
</select>                                        <!-- Sonnet 5.5 - balanced (default) -->
```

A model picker stores the tier, not the model ID, and reads it back through `AppModels.tier()` so selections saved by older versions keep working. Markup built later by script calls `AppModels.fill(container)` or `AppModels.label(tier)` directly.

## Retrofit tooling

`apply_models.py` moved all 54 AI apps onto `models.js` on October 27, 2026, using `keys_inventory.json` for the list. It inserts the tag, removes the old `getModel()` boilerplate that fetched `'../config.json'` (that path resolves to `/config.json` on GitHub Pages, which does not exist, so it always fell back), rewrites model constants and literal `model:` fields to ask by tier, applies small per app recipes for the apps with pickers or custom loaders (063, 072, 086, 126, 146 to 149, 153, 160, 170), and rewrites model IDs in each README to tier wording. It is idempotent, assert guarded, and refuses to write a file that would gain a syntax error or keep a model ID.

```
python3 apply_models.py --root DIR             dry run over DIR/<slug>/index.html
python3 apply_models.py --root DIR --write     patch in place
```

Saga Studio (150) keeps its Claude call in core/kit.js, which `vendor.js` cuts from Day 146, so it was moved the same day by running `node vendor.js` against the retrofitted Day 146 and adding the two head tags. The Kit family (146 to 149) shares its model code through KIT:CORE, which 147 to 149 copy byte for byte from 146 at build time. Change it in 146 first, then rebuild the others. Their `build.js` head templates now carry the full tag block, including `models.js`, so a rebuild no longer drops the icon, Save to Phone, and key ring tags.

## Knowing when a new model ships

The weekly health check asks Anthropic's Models API which models exist and fails when `config.json` is not on the newest model of each tier, or names a model the API no longer offers. The report in the Weekly health check failures issue lists the proposed `config.json` models and labels, ready to copy. It never changes anything itself, because a new model can need request changes (as `thinking` did in October 2026), so test one AI app per changed tier before pushing.

The check needs a repository secret named `ANTHROPIC_API_KEY` (Settings, Secrets and variables, Actions). Listing models costs nothing, so a dedicated key with a very low spend cap is enough. Without the secret, this part of the check is skipped and the rest still runs.
