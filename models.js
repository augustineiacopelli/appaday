/* AppADay models.js: the one place every AI app gets its Claude model from.
   https://augustineiacopelli.github.io/appaday/models.js  (procedure in MODELS.md)

   Loaded WITHOUT defer, directly after the save.js tag, so window.AppModels exists
   before the app's own inline script runs:

     <script src="https://augustineiacopelli.github.io/appaday/models.js"></script>

   Apps ask by tier, never by model ID. Tiers: haiku, sonnet (default), opus, fable.

     AppModels.id('sonnet')        -> 'claude-sonnet-5-5'   (sync, newest known value)
     await AppModels.get('opus')   -> waits briefly for config.json, then the ID
     AppModels.label('haiku')      -> 'Haiku 5.5'
     AppModels.tier('claude-opus-4-8') -> 'opus'   (old saved IDs map to their tier)
     AppModels.tiers()             -> ['haiku','sonnet','opus','fable']
     AppModels.onChange(fn)        -> fn() runs if config.json brings newer models

   Markup helpers, filled on load and again whenever the models change:
     <span data-model-label="sonnet"></span>           -> Sonnet 5.5
     <span data-model-id="sonnet"></span>              -> claude-sonnet-5-5
     <option value="opus" data-model-tier="opus" data-note="sharpest">  -> Opus 5.5 - sharpest

   config.json at the portal root is the source of truth. EMBED below mirrors it so the
   first load and offline loads are current too; health_check.py fails if they differ.
   To move every app to a new model: edit config.json and EMBED together, bump
   lastUpdated in both, push. No app file changes. */
(function () {
  'use strict';
  if (window.AppModels) return;

  var CONFIG_URL = 'https://augustineiacopelli.github.io/appaday/config.json';
  var CACHE_KEY = 'appaday.models';
  var TIERS = ['haiku', 'sonnet', 'opus', 'fable'];

  var EMBED = {
    lastUpdated: '2026-10-27',
    models: { haiku: 'claude-haiku-5-5', sonnet: 'claude-sonnet-5-5', opus: 'claude-opus-5-5', fable: 'claude-fable-5-1' },
    labels: { haiku: 'Haiku 5.5', sonnet: 'Sonnet 5.5', opus: 'Opus 5.5', fable: 'Fable 5.1' }
  };

  function valid(c) {
    if (!c || typeof c !== 'object' || !c.models || typeof c.lastUpdated !== 'string') return false;
    for (var i = 0; i < TIERS.length; i++) {
      var v = c.models[TIERS[i]];
      if (typeof v !== 'string' || !/^claude-[a-z0-9.-]+$/.test(v)) return false;
    }
    return true;
  }
  function clean(c) {
    var out = { lastUpdated: c.lastUpdated, models: {}, labels: {} };
    TIERS.forEach(function (t) {
      out.models[t] = c.models[t];
      out.labels[t] = (c.labels && typeof c.labels[t] === 'string' && c.labels[t]) || prettify(c.models[t]);
    });
    return out;
  }
  function prettify(id) {
    var m = /^claude-([a-z]+)-(\d+)(?:-(\d+))?/.exec(id || '');
    if (!m) return id || '';
    return m[1].charAt(0).toUpperCase() + m[1].slice(1) + ' ' + m[2] + (m[3] && m[3].length < 3 ? '.' + m[3] : '');
  }
  function readCache() {
    try { var c = JSON.parse(window.localStorage.getItem(CACHE_KEY) || 'null'); return valid(c) ? clean(c) : null; } catch (e) { return null; }
  }
  function writeCache(c) {
    try { window.localStorage.setItem(CACHE_KEY, JSON.stringify(c)); } catch (e) {}
  }
  function same(a, b) {
    for (var i = 0; i < TIERS.length; i++) {
      var t = TIERS[i];
      if (a.models[t] !== b.models[t] || a.labels[t] !== b.labels[t]) return false;
    }
    return true;
  }

  // Newest wins: the embedded table, or a cached config.json that is newer than it.
  var cur = clean(EMBED);
  var cached = readCache();
  if (cached && cached.lastUpdated > cur.lastUpdated) cur = cached;

  var listeners = [];

  function tier(x) {
    var s = String(x == null || x === '' ? 'sonnet' : x).toLowerCase();
    if (cur.models[s]) return s;
    for (var i = 0; i < TIERS.length; i++) if (s.indexOf(TIERS[i]) !== -1) return TIERS[i];
    return 'sonnet';
  }
  function id(t) { return cur.models[tier(t)]; }
  function label(t) { return cur.labels[tier(t)]; }

  function fill(root) {
    var doc = root || document;
    if (!doc || !doc.querySelectorAll) return;
    var i, n, list;
    list = doc.querySelectorAll('[data-model-label]');
    for (i = 0; i < list.length; i++) { n = list[i]; n.textContent = label(n.getAttribute('data-model-label')); }
    list = doc.querySelectorAll('[data-model-id]');
    for (i = 0; i < list.length; i++) { n = list[i]; n.textContent = id(n.getAttribute('data-model-id')); }
    list = doc.querySelectorAll('option[data-model-tier]');
    for (i = 0; i < list.length; i++) {
      n = list[i];
      var note = n.getAttribute('data-note');
      n.textContent = label(n.getAttribute('data-model-tier')) + (note ? ' \u2014 ' + note : '');
    }
  }

  var ready = (function () {
    if (typeof fetch !== 'function') return Promise.resolve();
    return fetch(CONFIG_URL, { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (c) {
        if (!valid(c)) return;
        c = clean(c);
        if (c.lastUpdated < cur.lastUpdated) return;
        writeCache(c);
        if (same(c, cur)) return;
        cur = c;
        fill();
        listeners.slice().forEach(function (fn) { try { fn(); } catch (e) {} });
      })
      .catch(function () {});
  })();

  function get(t) {
    var timeout = new Promise(function (res) { setTimeout(res, 2500); });
    return Promise.race([ready, timeout]).then(function () { return id(t); });
  }

  window.AppModels = {
    id: id,
    get: get,
    label: label,
    tier: tier,
    tiers: function () { return TIERS.slice(); },
    ready: ready,
    fill: fill,
    onChange: function (fn) { if (typeof fn === 'function') listeners.push(fn); },
    snapshot: function () { return JSON.parse(JSON.stringify(cur)); }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { fill(); });
  else fill();
})();
