/*
  AppADay key ring. Loaded by every AI app, directly after save.js:
    <script src="https://augustineiacopelli.github.io/appaday/keys.js" data-app="NNN" data-legacy-key="OLDNAME" data-accent="#RRGGBB" defer></script>

  Keeps the app's Anthropic API key in localStorage under appaday.key.NNN, falling
  back to the shared default appaday.key.default, and backs keys up to a
  passphrase encrypted file (appaday-keys.json, AES-GCM with a PBKDF2-SHA256 key)
  that restores every app's key at once. The key is only ever sent to
  api.anthropic.com. It is never logged and never put in a URL.

  Public API (window.AppKeys):
    get()                 Promise of the key string, or null if the user dismisses the sheet
    has()                 true when a per-app or default key is stored
    mountSettings(el)     renders the key section inside the app's Settings modal
    forget(scope)         scope "app" or "default"
  Fires window event "appaday:keychange" whenever a stored key changes.
  Edit only here; see KEYS.md.
*/
(function () {
  "use strict";
  if (window.AppKeys) return;

  var VERSION = "1.0.0";
  var API = "https://api.anthropic.com/v1/";
  var FILE_NAME = "appaday-keys.json";
  var ITER = 600000;
  var MIN_PASS = 12;

  /* ---------- attributes ---------- */
  var me = document.currentScript;
  if (!me) {
    var all = document.getElementsByTagName("script");
    for (var si = all.length - 1; si >= 0; si--) {
      if (/\/keys\.js(\?|$)/.test(all[si].src || "")) { me = all[si]; break; }
    }
  }
  function attr(n) { return (me && me.getAttribute(n)) || ""; }

  var APP = (function () {
    var a = attr("data-app").replace(/\D/g, "");
    if (!a) { var m = location.pathname.match(/appaday-(\d{3})-/); a = m ? m[1] : ""; }
    if (!a) return "";
    while (a.length < 3) a = "0" + a;
    return a.length === 3 ? a : "";
  })();
  var LEGACY = attr("data-legacy-key").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
  var ACCENT = (function () {
    var c = attr("data-accent").trim();
    return /^#[0-9a-fA-F]{3,8}$/.test(c) ? c : "#5F6B7A";
  })();
  var BASE = (function () {
    var s = (me && me.src) || "";
    return s ? s.replace(/keys\.js(\?.*)?$/, "") : "https://augustineiacopelli.github.io/appaday/";
  })();
  var APP_NAME = (function () {
    var t = (document.title || "").split("|")[0].trim();
    return t || "This app";
  })();

  /* ---------- storage ---------- */
  var K_DEF = "appaday.key.default";
  var K_APP = APP ? "appaday.key." + APP : "";
  var K_SCOPE = "appaday.key.scopePref";
  var K_FILE = "appaday.key.hasFile";
  var K_MIG = APP ? "appaday.key.migrated." + APP : "";
  var S_DISMISS = "appaday.key.dismissed." + (APP || "x");
  var RE_APPKEY = /^appaday\.key\.(\d{3})$/;

  function lsGet(k) { try { return k ? localStorage.getItem(k) : null; } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
  function lsDel(k) { try { if (k) localStorage.removeItem(k); } catch (e) { /* ignore */ } }
  function ssGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* ignore */ } }
  function ssDel(k) { try { sessionStorage.removeItem(k); } catch (e) { /* ignore */ } }

  function plausible(k) { return typeof k === "string" && k.length >= 20 && k.length <= 400 && !/\s/.test(k); }
  function clean(k) { return typeof k === "string" ? k.trim() : ""; }
  function last4(k) { return k ? k.slice(-4) : ""; }

  function active() {
    var a = clean(lsGet(K_APP));
    if (plausible(a)) return { source: "app", key: a };
    var d = clean(lsGet(K_DEF));
    if (plausible(d)) return { source: "default", key: d };
    return { source: null, key: null };
  }

  function storedEntries() {
    var out = { default: null, apps: {} };
    var d = clean(lsGet(K_DEF));
    if (plausible(d)) out.default = d;
    try {
      for (var i = 0; i < localStorage.length; i++) {
        var name = localStorage.key(i), m = name && name.match(RE_APPKEY);
        if (!m) continue;
        var v = clean(localStorage.getItem(name));
        if (plausible(v)) out.apps[m[1]] = v;
      }
    } catch (e) { /* ignore */ }
    return out;
  }
  function entryCount(r) { return (r.default ? 1 : 0) + Object.keys(r.apps || {}).length; }

  /* ---------- migration from the app's old key name ---------- */
  function legacyValue(spec) {
    var parts = spec.split(":");
    var raw = lsGet(parts[0]);
    if (raw == null || raw === "") return "";
    var val = raw, parsed = null;
    try { parsed = JSON.parse(raw); } catch (e) { parsed = null; }
    if (parts.length > 1) {
      if (!parsed || typeof parsed !== "object") return "";
      val = parsed;
      var path = parts.slice(1).join(":").split(".");
      for (var i = 0; i < path.length; i++) val = (val && typeof val === "object") ? val[path[i]] : undefined;
    } else if (typeof parsed === "string") {
      val = parsed;
    } else if (parsed && typeof parsed === "object") {
      var f = ["apiKey", "api_key", "anthropicKey", "anthropic_api_key", "claudeKey", "key"];
      val = "";
      for (var j = 0; j < f.length; j++) if (typeof parsed[f[j]] === "string" && parsed[f[j]]) { val = parsed[f[j]]; break; }
    }
    val = clean(val);
    return plausible(val) ? val : "";
  }
  (function migrate() {
    if (!APP || lsGet(K_MIG)) return;
    if (!plausible(clean(lsGet(K_APP)))) {
      for (var i = 0; i < LEGACY.length; i++) {
        var v = legacyValue(LEGACY[i]);
        if (v) { lsSet(K_APP, v); break; }
      }
    }
    lsSet(K_MIG, "1");
  })();

  try { if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(function () {}); } catch (e) { /* ignore */ }

  /* ---------- change notification ---------- */
  var panels = [];
  function changed() {
    for (var i = 0; i < panels.length; i++) if (panels[i].isHome()) panels[i].home();
    try { window.dispatchEvent(new CustomEvent("appaday:keychange", { detail: { has: has() } })); } catch (e) { /* ignore */ }
  }
  window.addEventListener("storage", function (e) {
    if (!e || e.key == null || /^appaday\.key\./.test(e.key)) changed();
  });

  function storeKey(key, scope) {
    var ok;
    if (scope === "app" && APP) ok = lsSet(K_APP, key);
    else { ok = lsSet(K_DEF, key); if (ok) lsDel(K_APP); }
    if (!ok) return false;
    lsSet(K_SCOPE, scope === "app" && APP ? "app" : "all");
    ssDel(S_DISMISS);
    changed();
    return true;
  }
  function writeRing(r) {
    var n = 0;
    if (plausible(r.default) && lsSet(K_DEF, r.default)) n++;
    Object.keys(r.apps || {}).forEach(function (num) {
      if (/^\d{3}$/.test(num) && plausible(r.apps[num]) && lsSet("appaday.key." + num, r.apps[num])) n++;
    });
    if (APP) lsSet(K_MIG, "1");
    ssDel(S_DISMISS);
    changed();
    return n;
  }

  /* ---------- validation ---------- */
  function fetchT(url, opts, ms) {
    var ctl = window.AbortController ? new AbortController() : null;
    var t = ctl ? setTimeout(function () { ctl.abort(); }, ms) : null;
    if (ctl) opts.signal = ctl.signal;
    return fetch(url, opts).then(function (r) { clearTimeout(t); return r; }, function (e) { clearTimeout(t); throw e; });
  }
  function headersFor(key, json) {
    var h = { "x-api-key": key, "anthropic-version": "2023-06-01", "anthropic-dangerous-direct-browser-access": "true" };
    if (json) h["content-type"] = "application/json";
    return h;
  }
  async function haikuModel() {
    try {
      var r = await fetchT(BASE + "config.json", { cache: "no-cache" }, 8000);
      var c = await r.json();
      if (c && c.models && typeof c.models.haiku === "string" && c.models.haiku) return c.models.haiku;
    } catch (e) { /* fall through */ }
    return "claude-haiku-4-5-20251001";
  }
  /* "ok", "bad" (rejected), or "unknown" (could not reach Anthropic) */
  async function checkKey(key) {
    try {
      var r = await fetchT(API + "models?limit=1", { method: "GET", headers: headersFor(key, false) }, 15000);
      if (r.ok) return "ok";
      if (r.status === 401 || r.status === 403) return "bad";
    } catch (e) { /* CORS or network: try a one token message */ }
    try {
      var body = JSON.stringify({ model: await haikuModel(), max_tokens: 1, messages: [{ role: "user", content: "Hi" }] });
      var r2 = await fetchT(API + "messages", { method: "POST", headers: headersFor(key, true), body: body }, 20000);
      if (r2.status === 401 || r2.status === 403) return "bad";
      if (r2.ok || r2.status === 400 || r2.status === 404 || r2.status === 429) return "ok";
    } catch (e2) { /* unreachable */ }
    return "unknown";
  }

  /* ---------- key ring crypto ---------- */
  var enc = new TextEncoder(), dec = new TextDecoder();
  function b64e(u8) {
    var s = "";
    for (var i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return btoa(s);
  }
  function b64d(str) {
    var s = atob(str), u8 = new Uint8Array(s.length);
    for (var i = 0; i < s.length; i++) u8[i] = s.charCodeAt(i);
    return u8;
  }
  function normPass(p) { try { return p.normalize("NFC"); } catch (e) { return p; } }
  async function deriveAes(pass, salt, iter) {
    var base = await crypto.subtle.importKey("raw", enc.encode(normPass(pass)), "PBKDF2", false, ["deriveKey"]);
    return crypto.subtle.deriveKey({ name: "PBKDF2", salt: salt, iterations: iter, hash: "SHA-256" },
      base, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
  }
  async function sealRing(ring, pass) {
    var salt = crypto.getRandomValues(new Uint8Array(16));
    var iv = crypto.getRandomValues(new Uint8Array(12));
    var aes = await deriveAes(pass, salt, ITER);
    var plain = { default: ring.default || null, apps: ring.apps || {}, updated: new Date().toISOString() };
    var ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv: iv }, aes, enc.encode(JSON.stringify(plain)));
    return JSON.stringify({ format: "appaday-keyring", v: 1, kdf: "PBKDF2-SHA256", iter: ITER, salt: b64e(salt), iv: b64e(iv), ct: b64e(new Uint8Array(ct)) });
  }
  function fail(code) { var e = new Error(code); e.code = code; return e; }
  async function openRing(text, pass) {
    var env;
    try { env = JSON.parse(text); } catch (e) { throw fail("format"); }
    if (!env || env.format !== "appaday-keyring" || env.v !== 1 || env.kdf !== "PBKDF2-SHA256" ||
        typeof env.iter !== "number" || env.iter < 100000 || env.iter > 10000000 ||
        typeof env.salt !== "string" || typeof env.iv !== "string" || typeof env.ct !== "string") throw fail("format");
    var salt, iv, ct;
    try { salt = b64d(env.salt); iv = b64d(env.iv); ct = b64d(env.ct); } catch (e) { throw fail("format"); }
    var plain;
    try {
      var aes = await deriveAes(pass, salt, env.iter);
      plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, aes, ct);
    } catch (e) { throw fail("pass"); }
    var r;
    try { r = JSON.parse(dec.decode(plain)); } catch (e) { throw fail("format"); }
    var out = { default: plausible(r && r.default) ? r.default : null, apps: {} };
    if (r && r.apps && typeof r.apps === "object") {
      Object.keys(r.apps).forEach(function (n) { if (/^\d{3}$/.test(n) && plausible(r.apps[n])) out.apps[n] = r.apps[n]; });
    }
    return out;
  }
  function merge(ring, add) {
    var out = { default: ring.default || null, apps: {} };
    Object.keys(ring.apps || {}).forEach(function (n) { out.apps[n] = ring.apps[n]; });
    if (add.default) out.default = add.default;
    Object.keys(add.apps || {}).forEach(function (n) { out.apps[n] = add.apps[n]; });
    return out;
  }

  /* ---------- files ---------- */
  var ua = navigator.userAgent || "";
  var MOBILE = /iPhone|iPad|iPod|Android/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var JSON_TYPES = [{ description: "AppADay key file", accept: { "application/json": [".json"] } }];

  var fileInput = null;
  function pickFile() {
    if (window.showOpenFilePicker && !MOBILE) {
      return window.showOpenFilePicker({ types: JSON_TYPES, multiple: false }).then(function (hs) {
        return hs[0].getFile().then(function (f) { return f.text().then(function (t) { return { name: f.name, text: t, handle: hs[0] }; }); });
      }, function (e) { if (e && e.name === "AbortError") return null; throw e; });
    }
    return new Promise(function (resolve) {
      if (!fileInput) {
        fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.style.cssText = "position:fixed;left:-9999px;top:0;width:1px;height:1px;opacity:0";
        document.body.appendChild(fileInput);
      }
      fileInput.value = "";
      fileInput.onchange = function () {
        var f = fileInput.files && fileInput.files[0];
        if (!f) { resolve(null); return; }
        if (f.size > 262144) { resolve({ name: f.name, text: "" }); return; }
        var rd = new FileReader();
        rd.onload = function () { resolve({ name: f.name, text: String(rd.result || ""), handle: null }); };
        rd.onerror = function () { resolve({ name: f.name, text: "", handle: null }); };
        rd.readAsText(f);
      };
      fileInput.click();
    });
  }

  /* resolves "overwrite", "picker", "share", "download" or "cancel" */
  async function saveFile(text, handle) {
    if (handle && handle.createWritable) {
      try {
        if (handle.requestPermission && (await handle.requestPermission({ mode: "readwrite" })) !== "granted") throw new Error("denied");
        var w = await handle.createWritable();
        await w.write(text);
        await w.close();
        return "overwrite";
      } catch (e) { /* fall through to a fresh save */ }
    }
    if (window.showSaveFilePicker && !MOBILE) {
      try {
        var h = await window.showSaveFilePicker({ suggestedName: FILE_NAME, types: JSON_TYPES });
        var w2 = await h.createWritable();
        await w2.write(text);
        await w2.close();
        return "picker";
      } catch (e) {
        if (e && e.name === "AbortError") return "cancel";
      }
    }
    var file = null;
    try { file = new File([text], FILE_NAME, { type: "application/json" }); } catch (e) { file = null; }
    if (MOBILE && file && navigator.canShare && navigator.share) {
      var can = false;
      try { can = navigator.canShare({ files: [file] }); } catch (e) { can = false; }
      if (can) {
        try { await navigator.share({ files: [file], title: FILE_NAME }); return "share"; }
        catch (e) { if (e && e.name === "AbortError") return "cancel"; }
      }
    }
    var url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
    var a = document.createElement("a");
    a.href = url;
    a.download = FILE_NAME;
    a.rel = "noopener";
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(url); if (a.parentNode) a.parentNode.removeChild(a); }, 4000);
    return "download";
  }

  /* ---------- styles ---------- */
  var CSS = [
    ".ak-root{--ak-accent:#5F6B7A;--ak-line:rgba(128,128,128,.42);--ak-field:rgba(128,128,128,.14);--ak-danger:#D64545;line-height:1.45;text-align:left;letter-spacing:normal;text-transform:none}",
    ".ak-root,.ak-root *,.ak-root *::before,.ak-root *::after{box-sizing:border-box}",
    ".ak-inline{color:inherit;font:inherit;margin-top:4px}",
    ".ak-wrap{position:fixed;left:0;top:0;right:0;bottom:0;z-index:2147483000;display:none;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;font-size:16px;--ak-bg:#FFFFFF;--ak-fg:#17191E;--ak-line:#D5D9E0;--ak-field:#F2F4F7;--ak-danger:#B42318}",
    ".ak-wrap.ak-show{display:block}",
    ".ak-scrim{position:absolute;left:0;top:0;right:0;bottom:0;background:rgba(8,10,14,.55);opacity:0;transition:opacity .22s ease}",
    ".ak-sheet{position:absolute;left:0;right:0;bottom:0;margin:0 auto;width:100%;max-width:480px;max-height:calc(100% - 20px);overflow:auto;-webkit-overflow-scrolling:touch;background:var(--ak-bg);color:var(--ak-fg);border-radius:18px 18px 0 0;padding:10px 18px calc(18px + env(safe-area-inset-bottom));transform:translateY(105%);transition:transform .26s cubic-bezier(.2,.8,.2,1);box-shadow:0 -10px 40px rgba(0,0,0,.28)}",
    ".ak-wrap.ak-in .ak-scrim{opacity:1}",
    ".ak-wrap.ak-in .ak-sheet{transform:none}",
    ".ak-grab{width:40px;height:4px;border-radius:2px;background:var(--ak-line);margin:0 auto 12px}",
    "@media (min-width:600px){.ak-sheet{bottom:24px;border-radius:18px}}",
    "@media (prefers-color-scheme:dark){.ak-wrap{--ak-bg:#1B1E24;--ak-fg:#ECEEF2;--ak-line:#363B45;--ak-field:#252A32;--ak-danger:#FF8A80}}",
    "@media (prefers-reduced-motion:reduce){.ak-scrim,.ak-sheet{transition:none}}",
    ".ak-root .ak-h{display:block;margin:0 0 6px;padding:0;font-size:1.12em;font-weight:700;line-height:1.3;color:inherit;font-family:inherit}",
    ".ak-root .ak-sub{display:block;margin:0 0 6px;padding:0;font-size:.98em;font-weight:700;color:inherit}",
    ".ak-root .ak-p{margin:0 0 12px;padding:0;font-size:.94em;color:inherit;opacity:.82}",
    ".ak-root .ak-note{margin:12px 0 0;padding:0;font-size:.82em;color:inherit;opacity:.72}",
    ".ak-root .ak-status{margin:0 0 4px;font-size:.95em;color:inherit}",
    ".ak-root .ak-status b{font-weight:700}",
    ".ak-root .ak-mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:.04em}",
    ".ak-root .ak-col{display:flex;flex-direction:column;gap:10px;margin-top:12px}",
    ".ak-root .ak-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}",
    ".ak-root .ak-row > .ak-btn{flex:1 1 140px}",
    ".ak-root .ak-btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;min-width:44px;margin:0;padding:0 16px;border:1px solid var(--ak-line);border-radius:11px;background:transparent;color:inherit;font:inherit;font-size:.95em;font-weight:600;line-height:1.2;text-align:center;cursor:pointer;-webkit-appearance:none;appearance:none;text-decoration:none;box-shadow:none}",
    ".ak-root .ak-btn:hover{border-color:var(--ak-accent)}",
    ".ak-root .ak-btn:focus-visible,.ak-root .ak-in:focus-visible,.ak-root .ak-seg button:focus-visible{outline:2px solid var(--ak-accent);outline-offset:2px}",
    ".ak-root .ak-btn.ak-pri{background:var(--ak-accent);border-color:var(--ak-accent);color:#FFFFFF}",
    ".ak-root .ak-btn.ak-dng{border-color:var(--ak-danger)}",
    ".ak-root .ak-btn.ak-link{border-color:transparent;background:transparent;font-weight:500;opacity:.85}",
    ".ak-root .ak-btn[disabled]{opacity:.45;cursor:default}",
    ".ak-root .ak-lbl{display:block;margin:12px 0 6px;font-size:.86em;font-weight:600;color:inherit}",
    ".ak-root .ak-field{display:flex;gap:8px}",
    ".ak-root .ak-in{flex:1 1 auto;min-width:0;width:100%;min-height:44px;margin:0;padding:0 12px;border:1px solid var(--ak-line);border-radius:10px;background:var(--ak-field);color:inherit;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:16px;-webkit-appearance:none;appearance:none;box-shadow:none}",
    ".ak-root .ak-seg{display:flex;border:1px solid var(--ak-line);border-radius:11px;overflow:hidden}",
    ".ak-root .ak-seg button{flex:1 1 50%;min-height:44px;margin:0;padding:0 10px;border:0;background:transparent;color:inherit;font:inherit;font-size:.92em;font-weight:600;cursor:pointer;-webkit-appearance:none;appearance:none}",
    ".ak-root .ak-seg button[aria-pressed=\"true\"]{background:var(--ak-accent);color:#FFFFFF}",
    ".ak-root .ak-msg{margin:10px 0 0;font-size:.9em;font-weight:600;min-height:0}",
    ".ak-root .ak-msg.ak-err{color:var(--ak-danger)}",
    ".ak-root .ak-file{margin:8px 0 0;font-size:.88em;opacity:.8;word-break:break-all}"
  ].join("\n");
  function injectStyle() {
    if (document.getElementById("ak-style")) return;
    var st = document.createElement("style");
    st.id = "ak-style";
    st.textContent = CSS;
    (document.head || document.documentElement).appendChild(st);
  }

  /* ---------- tiny DOM helper ---------- */
  function h(tag, props, kids) {
    var el = document.createElement(tag);
    if (props) Object.keys(props).forEach(function (k) {
      var v = props[k];
      if (v == null || v === false) return;
      if (k === "text") el.textContent = v;
      else if (k === "cls") el.className = v;
      else if (k.slice(0, 2) === "on") el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? "" : v);
    });
    (kids || []).forEach(function (c) { if (c) el.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return el;
  }
  function empty(el) { while (el.firstChild) el.removeChild(el.firstChild); }
  function btn(label, cls, onclick, extra) {
    var p = { type: "button", cls: "ak-btn" + (cls ? " " + cls : ""), text: label, onclick: onclick };
    if (extra) Object.keys(extra).forEach(function (k) { p[k] = extra[k]; });
    return h("button", p);
  }
  var uid = 0;
  function nid(p) { uid++; return "ak-" + p + "-" + uid; }

  /* ---------- panel: every screen renders into a host element ---------- */
  /* mode "sheet" (slide up from get) or "settings" (inline in the app's Settings) */
  function Panel(host, mode, hooks) {
    var self = this, screen = "", busy = false;
    var ctx = {};          // per flow scratch: file text, handle, sealed text, entries to add
    hooks = hooks || {};

    function setBusy(b, el, label) {
      busy = b;
      var bs = host.querySelectorAll("button");
      for (var i = 0; i < bs.length; i++) bs[i].disabled = b;
      if (el) el.textContent = label;
    }
    function msg(el, text, err) { el.textContent = text || ""; el.className = "ak-msg" + (err ? " ak-err" : ""); }
    function msgEl() { return h("p", { cls: "ak-msg", role: "status", "aria-live": "polite" }); }
    function show(name, nodes) {
      screen = name;
      empty(host);
      nodes.forEach(function (n) { if (n) host.appendChild(n); });
      if (mode === "sheet") {
        var hd = host.querySelector("h2");
        if (hd && hooks.label) { if (!hd.id) hd.id = nid("t"); hooks.label(hd.id); }
        if (hooks.focus) hooks.focus();
      }
    }
    function homeName() { return mode === "sheet" ? "choose" : "status"; }
    this.isHome = function () { return screen === homeName(); };
    this.home = function () { ctx = {}; if (mode === "sheet") choose(); else status(); };
    function back() { return btn("Back", "ak-link", function () { self.home(); }); }
    function done(label) {
      return btn(label || "Done", "ak-pri", function () { if (mode === "sheet" && hooks.close) hooks.close(); else self.home(); });
    }
    function safety() {
      return h("p", { cls: "ak-note", text: "Keys stay in this browser and go only to Anthropic. A key with a spend cap is wise." });
    }

    /* settings home */
    function status() {
      var a = active();
      var line = a.key
        ? h("p", { cls: "ak-status" }, ["Using ", h("b", { text: a.source === "app" ? "This app" : "Default" }), " key ending in ", h("b", { cls: "ak-mono", text: last4(a.key) }), "."])
        : h("p", { cls: "ak-status", text: "No key saved in this browser." });
      var hasAny = entryCount(storedEntries()) > 0;
      show("status", [
        h("span", { cls: "ak-sub", text: "Claude API key" }),
        line,
        h("div", { cls: "ak-row" }, [
          btn("Enter key", a.key ? "" : "ak-pri", enter),
          btn("Restore from key file", "", restore),
          btn("Back up to key file", "", backup, { disabled: hasAny ? null : true }),
          btn("Forget key", "ak-dng", forgetScreen, { disabled: a.key ? null : true })
        ]),
        h("p", { cls: "ak-note", text: "Keys stay in this browser and go only to api.anthropic.com. Get a key at console.anthropic.com; a spend cap is wise." })
      ]);
    }

    /* sheet home */
    function choose() {
      var t = nid("t"), knownFile = !!lsGet(K_FILE);
      show("choose", [
        h("div", { cls: "ak-grab", "aria-hidden": "true" }),
        h("h2", { cls: "ak-h", id: t, text: "Connect your Claude API key" }),
        h("p", { cls: "ak-p", text: knownFile
          ? APP_NAME + " calls Claude with your own Anthropic API key. Restore your keys from your key file, or enter a key."
          : APP_NAME + " calls Claude with your own Anthropic API key. Enter a key to get started. If you saved an AppADay key file before, restore it instead to bring back every app's key." }),
        h("div", { cls: "ak-col" }, knownFile ? [
          btn("Restore from my key file", "ak-pri", restore),
          btn("Enter a key", "", enter),
          btn("Not now", "ak-link", function () { if (hooks.close) hooks.close(); })
        ] : [
          btn("Enter a key", "ak-pri", enter),
          btn("Restore from my key file", "", restore),
          btn("Not now", "ak-link", function () { if (hooks.close) hooks.close(); })
        ]),
        safety()
      ]);
    }

    /* manual entry */
    function enter() {
      var pref = lsGet(K_SCOPE) === "app" && APP ? "app" : "all";
      var inId = nid("key"), m = msgEl();
      var input = h("input", { id: inId, cls: "ak-in", type: "password", autocomplete: "off", autocapitalize: "off", spellcheck: "false", placeholder: "sk-ant-...", "aria-describedby": null });
      var eye = btn("Show", "", function () {
        var s = input.type === "password";
        input.type = s ? "text" : "password";
        eye.textContent = s ? "Hide" : "Show";
        eye.setAttribute("aria-pressed", s ? "true" : "false");
      }, { "aria-pressed": "false", "aria-label": "Show key" });
      var scope = pref;
      var segApp = h("button", { type: "button", text: "This app only", "aria-pressed": String(scope === "app") });
      var segAll = h("button", { type: "button", text: "All my apps", "aria-pressed": String(scope === "all") });
      var hint = h("p", { cls: "ak-note" });
      function paintScope() {
        segApp.setAttribute("aria-pressed", String(scope === "app"));
        segAll.setAttribute("aria-pressed", String(scope === "all"));
        hint.textContent = scope === "app"
          ? "Saved for " + APP_NAME + " only. Use this for a key made just for this app."
          : "Saved as your default key, used by every AppADay app without its own key.";
      }
      segApp.addEventListener("click", function () { scope = "app"; paintScope(); });
      segAll.addEventListener("click", function () { scope = "all"; paintScope(); });
      paintScope();
      var go = btn("Check and save", "ak-pri", submit);
      input.addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); submit(); } });
      var anyway = null;

      async function submit(force) {
        if (busy) return;
        var k = clean(input.value);
        if (!k) { msg(m, "Paste your API key first.", true); input.focus(); return; }
        if (!plausible(k)) { msg(m, "That does not look like an API key. Copy it again from the Anthropic Console.", true); return; }
        var verdict = "ok";
        if (force !== true) {
          setBusy(true, go, "Checking...");
          msg(m, "Checking the key with Anthropic...");
          verdict = await checkKey(k);
          setBusy(false, go, "Check and save");
        }
        if (verdict === "bad") { msg(m, "Anthropic rejected this key. Check that it was copied in full and is still active.", true); return; }
        if (verdict === "unknown") {
          msg(m, "Could not reach Anthropic to check this key. Check your connection, or save it without checking.", true);
          if (!anyway) { anyway = btn("Save without checking", "", function () { submit(true); }); go.parentNode.appendChild(anyway); }
          return;
        }
        var sc = APP ? scope : "all";
        if (!storeKey(k, sc)) { msg(m, "This browser is blocking storage, so the key cannot be saved here.", true); return; }
        input.value = "";
        if (hooks.got) hooks.got(active().key);
        saved(k, sc);
      }

      var nodes = [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Enter a key" }),
        h("label", { cls: "ak-lbl", "for": inId, text: "Anthropic API key" }),
        h("div", { cls: "ak-field" }, [input, eye])
      ];
      if (APP) {
        nodes.push(h("span", { cls: "ak-lbl", text: "Use it for" }));
        nodes.push(h("div", { cls: "ak-seg", role: "group", "aria-label": "Key scope" }, [segApp, segAll]));
        nodes.push(hint);
      }
      nodes.push(m, h("div", { cls: "ak-row" }, [back(), go]));
      if (mode === "sheet") nodes.push(safety());
      show("enter", nodes);
      setTimeout(function () { try { input.focus(); } catch (e) { /* ignore */ } }, 30);
    }

    function saved(k, sc) {
      var add = { default: null, apps: {} };
      if (sc === "app") add.apps[APP] = k; else add.default = k;
      show("saved", [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Key saved" }),
        h("p", { cls: "ak-p" }, ["Saved " + (sc === "app" ? "for this app" : "as your default") + ", ending in ", h("b", { cls: "ak-mono", text: last4(k) }), ". Add it to your key file so it can be restored if this browser forgets it."]),
        h("div", { cls: "ak-col" }, [
          btn("Add to my key file", "ak-pri", function () { addFlow(add); }),
          btn("Create a key file", "", createFlow),
          btn("Not now", "ak-link", function () { if (mode === "sheet" && hooks.close) hooks.close(); else self.home(); })
        ])
      ]);
    }

    /* file picker block shared by restore and add */
    function fileBlock(m) {
      var name = h("p", { cls: "ak-file", text: "No file chosen." });
      var pick = btn("Choose key file", "", function () {
        msg(m, "");
        pickFile().then(function (f) {
          if (!f) return;
          ctx.text = f.text; ctx.handle = f.handle || null;
          name.textContent = f.name || FILE_NAME;
          if (!f.text) msg(m, "That file could not be read.", true);
        }, function () { msg(m, "That file could not be opened.", true); });
      });
      return h("div", null, [pick, name]);
    }
    function passInput(id, label) {
      return [h("label", { cls: "ak-lbl", "for": id, text: label }),
        h("input", { id: id, cls: "ak-in", type: "password", autocomplete: "off", autocapitalize: "off", spellcheck: "false" })];
    }
    function openError(m, e) {
      if (e && e.code === "pass") msg(m, "This file cannot be opened without its passphrase. If the passphrase is lost, create a new key file by entering your keys again.", true);
      else if (e && e.code === "format") msg(m, "This is not an AppADay key file. Choose appaday-keys.json.", true);
      else msg(m, "This browser could not open the key file.", true);
    }

    /* restore */
    function restore() {
      ctx = {};
      var m = msgEl(), pid = nid("pass");
      var pf = passInput(pid, "Passphrase");
      var go = btn("Restore keys", "ak-pri", async function () {
        if (busy) return;
        if (!ctx.text) { msg(m, "Choose your key file first.", true); return; }
        var pass = pf[1].value;
        if (!pass) { msg(m, "Enter the passphrase for this file.", true); pf[1].focus(); return; }
        setBusy(true, go, "Unlocking...");
        msg(m, "Unlocking your key file...");
        try {
          var ring = await openRing(ctx.text, pass);
          pass = ""; pf[1].value = "";
          var n = writeRing(ring);
          lsSet(K_FILE, "1");
          var a = active();
          if (a.key && hooks.got) hooks.got(a.key);
          setBusy(false, go, "Restore keys");
          restored(n, a);
        } catch (e) {
          pass = "";
          setBusy(false, go, "Restore keys");
          openError(m, e);
        }
      });
      pf[1].addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); go.click(); } });
      show("restore", [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Restore from key file" }),
        h("p", { cls: "ak-p", text: "Choose appaday-keys.json and enter its passphrase. Every app's key is restored at once." }),
        fileBlock(m), pf[0], pf[1], m,
        h("div", { cls: "ak-row" }, [back(), go])
      ]);
    }
    function restored(n, a) {
      var line = a.key
        ? h("p", { cls: "ak-p" }, ["Restored " + n + (n === 1 ? " key" : " keys") + ". " + APP_NAME + " now uses the " + (a.source === "app" ? "app" : "default") + " key ending in ", h("b", { cls: "ak-mono", text: last4(a.key) }), "."])
        : h("p", { cls: "ak-p", text: "Restored " + n + (n === 1 ? " key" : " keys") + ", but the file has no key for this app and no default key. Enter a key to continue." });
      show("restored", [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Keys restored" }),
        line,
        h("div", { cls: "ak-row" }, a.key ? [done()] : [back(), btn("Enter a key", "ak-pri", enter)])
      ]);
    }

    /* backup chooser (settings) */
    function backup() {
      var all = storedEntries();
      show("backup", [
        h("span", { cls: "ak-sub", text: "Back up to key file" }),
        h("p", { cls: "ak-p", text: "This browser holds " + entryCount(all) + (entryCount(all) === 1 ? " key" : " keys") + ". Add them to your existing key file, or start a new file." }),
        h("div", { cls: "ak-col" }, [
          btn("Add to my key file", "ak-pri", function () { addFlow(all); }),
          btn("Create a new key file", "", createFlow),
          back()
        ])
      ]);
    }

    /* create */
    function createFlow() {
      ctx = {};
      var m = msgEl(), p1 = passInput(nid("p1"), "New passphrase (at least " + MIN_PASS + " characters)"), p2 = passInput(nid("p2"), "Type it again");
      var go = btn("Create key file", "ak-pri", async function () {
        if (busy) return;
        var a = p1[1].value, b = p2[1].value;
        if (a.length < MIN_PASS) { msg(m, "Use a passphrase of at least " + MIN_PASS + " characters.", true); p1[1].focus(); return; }
        if (a !== b) { msg(m, "The two passphrases do not match.", true); p2[1].focus(); return; }
        var ring = storedEntries();
        if (!entryCount(ring)) { msg(m, "There are no keys in this browser to back up yet.", true); return; }
        setBusy(true, go, "Encrypting...");
        msg(m, "Encrypting your keys...");
        try {
          ctx.sealed = await sealRing(ring, a);
          ctx.count = entryCount(ring);
          ctx.handle = null;
          a = b = ""; p1[1].value = ""; p2[1].value = "";
          setBusy(false, go, "Create key file");
          ready("created");
        } catch (e) {
          setBusy(false, go, "Create key file");
          msg(m, "This browser could not encrypt the file.", true);
        }
      });
      show("create", [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Create a key file" }),
        h("p", { cls: "ak-p", text: "Every key in this browser is encrypted with a passphrase you choose. The passphrase is never stored, so keep it somewhere safe." }),
        p1[0], p1[1], p2[0], p2[1], m,
        h("div", { cls: "ak-row" }, [back(), go])
      ]);
      setTimeout(function () { try { p1[1].focus(); } catch (e) { /* ignore */ } }, 30);
    }

    /* add to existing */
    function addFlow(add) {
      ctx = {};
      var m = msgEl(), pid = nid("pass");
      var pf = passInput(pid, "Passphrase for that file");
      var go = btn("Add to file", "ak-pri", async function () {
        if (busy) return;
        if (!ctx.text) { msg(m, "Choose your key file first.", true); return; }
        var pass = pf[1].value;
        if (!pass) { msg(m, "Enter the passphrase for this file.", true); pf[1].focus(); return; }
        setBusy(true, go, "Unlocking...");
        msg(m, "Unlocking and updating your key file...");
        try {
          var ring = merge(await openRing(ctx.text, pass), add);
          ctx.sealed = await sealRing(ring, pass);
          ctx.count = entryCount(ring);
          pass = ""; pf[1].value = "";
          setBusy(false, go, "Add to file");
          ready("updated");
        } catch (e) {
          pass = "";
          setBusy(false, go, "Add to file");
          openError(m, e);
        }
      });
      pf[1].addEventListener("keydown", function (e) { if (e.key === "Enter") { e.preventDefault(); go.click(); } });
      show("add", [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Add to my key file" }),
        h("p", { cls: "ak-p", text: "Choose your current appaday-keys.json and enter its passphrase. The key is added and the file is saved again with the same passphrase." }),
        fileBlock(m), pf[0], pf[1], m,
        h("div", { cls: "ak-row" }, [back(), go])
      ]);
    }

    /* save step: a fresh tap so the save dialog or share sheet is allowed to open */
    function ready(kind) {
      var m = msgEl();
      var save = btn(ctx.handle ? "Save over my key file" : "Save key file", "ak-pri", async function () {
        if (busy) return;
        setBusy(true, save, "Saving...");
        var how = "cancel";
        try { how = await saveFile(ctx.sealed, ctx.handle); } catch (e) { how = "error"; }
        setBusy(false, save, ctx.handle ? "Save over my key file" : "Save key file");
        if (how === "cancel") { msg(m, "Not saved yet. Tap Save key file to try again.", true); return; }
        if (how === "error") { msg(m, "The file could not be saved in this browser.", true); return; }
        lsSet(K_FILE, "1");
        var note = {
          overwrite: "Saved over your key file.",
          picker: "Key file saved. If you saved it under a new name, delete the older copy.",
          share: "If you chose Save to Files, the file is saved. Replace any older copy so you keep only the newest file.",
          download: "Downloaded as " + FILE_NAME + ". Replace your older copy with this one, since the newest file holds every key."
        }[how];
        ctx = {};
        show("savedfile", [
          mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
          h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Key file saved" }),
          h("p", { cls: "ak-p", text: note }),
          h("div", { cls: "ak-row" }, [done()])
        ]);
      });
      show("ready", [
        mode === "sheet" ? h("div", { cls: "ak-grab", "aria-hidden": "true" }) : null,
        h(mode === "sheet" ? "h2" : "span", { cls: mode === "sheet" ? "ak-h" : "ak-sub", text: "Your key file is ready" }),
        h("p", { cls: "ak-p", text: (kind === "created" ? "New file" : "Updated file") + " holds " + ctx.count + (ctx.count === 1 ? " key" : " keys") + "." }),
        m,
        h("div", { cls: "ak-row" }, [save])
      ]);
    }

    /* forget (settings) */
    function forgetScreen() {
      var hasApp = plausible(clean(lsGet(K_APP))), hasDef = plausible(clean(lsGet(K_DEF)));
      var kids = [];
      if (hasApp) kids.push(btn("Forget this app's key", "ak-dng", function () { forget("app"); self.home(); }));
      if (hasDef) kids.push(btn("Forget the default key", "ak-dng", function () { forget("default"); self.home(); }));
      kids.push(back());
      show("forget", [
        h("span", { cls: "ak-sub", text: "Forget key" }),
        h("p", { cls: "ak-p", text: (hasApp ? "Forgetting this app's key leaves " + (hasDef ? "the default key in use." : "no key until you enter or restore one.") + " " : "") +
          (hasDef ? "The default key is shared by every AppADay app in this browser that has no key of its own." : "") }),
        h("div", { cls: "ak-col" }, kids)
      ]);
    }

    this.screen = function () { return screen; };
  }

  /* ---------- the slide up sheet ---------- */
  var sheet = null;
  function buildSheet() {
    injectStyle();
    var wrap = h("div", { cls: "ak-root ak-wrap" });
    wrap.style.setProperty("--ak-accent", ACCENT);
    var scrim = h("div", { cls: "ak-scrim" });
    var box = h("div", { cls: "ak-sheet", role: "dialog", "aria-modal": "true", tabindex: "-1" });
    wrap.appendChild(scrim);
    wrap.appendChild(box);
    document.body.appendChild(wrap);
    var prevFocus = null, timer = null;

    function focusFirst() {
      setTimeout(function () {
        var f = box.querySelector("input,button:not([disabled])");
        try { (f || box).focus(); } catch (e) { /* ignore */ }
      }, 40);
    }
    function trap(e) {
      if (!wrap.classList.contains("ak-show")) return;
      if (e.key === "Escape") { e.preventDefault(); e.stopImmediatePropagation(); close(); return; }
      if (e.key === "Tab") {
        e.stopImmediatePropagation();
        var f = Array.prototype.filter.call(box.querySelectorAll("button,input,a[href]"), function (x) { return !x.disabled && x.offsetParent !== null; });
        if (!f.length) { e.preventDefault(); return; }
        var first = f[0], last = f[f.length - 1];
        if (!box.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
        else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    }
    var panel = new Panel(box, "sheet", {
      focus: focusFirst,
      label: function (id) { box.setAttribute("aria-labelledby", id); },
      got: function (k) { settle(k); },
      close: function () { close(); }
    });
    scrim.addEventListener("click", function () { close(); });

    function open() {
      clearTimeout(timer);
      prevFocus = document.activeElement;
      panel.home();
      wrap.classList.add("ak-show");
      window.addEventListener("keydown", trap, true);
      void wrap.offsetWidth;
      wrap.classList.add("ak-in");
      focusFirst();
    }
    function close() {
      if (!wrap.classList.contains("ak-show")) return;
      window.removeEventListener("keydown", trap, true);
      wrap.classList.remove("ak-in");
      timer = setTimeout(function () { wrap.classList.remove("ak-show"); empty(box); }, 280);
      if (!active().key) { ssSet(S_DISMISS, "1"); settle(null); }
      try { if (prevFocus && prevFocus.focus) prevFocus.focus(); } catch (e) { /* ignore */ }
    }
    return { open: open, close: close };
  }

  /* ---------- public API ---------- */
  var pending = null;
  function settle(v) {
    if (!pending) return;
    var p = pending; pending = null;
    p(v || null);
  }
  function has() { return !!active().key; }
  function get() {
    var a = active();
    if (a.key) return Promise.resolve(a.key);
    if (ssGet(S_DISMISS)) return Promise.resolve(null);
    if (pending) return pendingPromise;
    pendingPromise = new Promise(function (resolve) { pending = resolve; });
    if (!sheet) sheet = buildSheet();
    sheet.open();
    return pendingPromise;
  }
  var pendingPromise = null;
  function forget(scope) {
    if (scope === "default") lsDel(K_DEF);
    else if (APP) lsDel(K_APP);
    changed();
  }
  function mountSettings(el) {
    if (!el || !el.appendChild) return;
    injectStyle();
    if (el.__akPanel) { el.__akPanel.home(); return; }
    var holder = h("div", { cls: "ak-root ak-inline" });
    holder.style.setProperty("--ak-accent", ACCENT);
    empty(el);
    el.appendChild(holder);
    var p = new Panel(holder, "settings", { got: function (k) { settle(k); } });
    el.__akPanel = p;
    panels.push(p);
    p.home();
  }

  window.AppKeys = {
    version: VERSION,
    app: APP,
    get: get,
    has: has,
    mountSettings: mountSettings,
    forget: forget
  };
})();
