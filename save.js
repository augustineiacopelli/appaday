/*
  AppADay Save to Phone helper. Loaded by every app:
    <link rel="manifest" href="https://augustineiacopelli.github.io/appaday/manifests/NNN.webmanifest">
    <script src="https://augustineiacopelli.github.io/appaday/save.js" defer></script>

  On a phone browser (not already running from the home screen) it shows a small
  bar offering to save the app. It appears automatically once per app per device,
  or right away and expanded when the URL carries ?save=1 (the portal's
  "Scan to save" QR). On Android Chrome with an installable manifest the bar
  offers a real one tap Install. Everything renders inside a shadow root so it
  never inherits or leaks app styles. Edit only here; see SAVE.md.
*/
(function () {
  "use strict";
  if (window.__appadaySave) return;
  window.__appadaySave = true;

  // Browser tab icon: point the favicon at the app's own home screen icon.
  (function () {
    var t = document.querySelector('link[rel="apple-touch-icon"]');
    if (!t || !t.href) return;
    var old = document.querySelectorAll('link[rel~="icon"]');
    for (var i = 0; i < old.length; i++) old[i].parentNode.removeChild(old[i]);
    var f = document.createElement("link");
    f.rel = "icon";
    f.type = "image/png";
    f.href = t.href;
    document.head.appendChild(f);
  })();

  var KEY_SEEN = "appaday-save-seen";
  var params;
  try { params = new URLSearchParams(location.search); } catch (e) { params = null; }
  var forced = !!(params && params.get("save") === "1");

  if (forced) {
    try {
      params.delete("save");
      var q = params.toString();
      history.replaceState(history.state, "", location.pathname + (q ? "?" + q : "") + location.hash);
    } catch (e) { /* ignore */ }
  }

  function standalone() {
    try {
      if (window.matchMedia && window.matchMedia("(display-mode: standalone)").matches) return true;
      if (window.matchMedia && window.matchMedia("(display-mode: fullscreen)").matches) return true;
    } catch (e) { /* ignore */ }
    return window.navigator.standalone === true;
  }
  if (standalone()) return;

  var ua = navigator.userAgent || "";
  var isIPad = /iPad/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  var isIOS = /iPhone|iPod/.test(ua) || isIPad;
  var isAndroid = /Android/i.test(ua);
  if (!isIOS && !isAndroid) return;
  var browser = isIOS
    ? (/CriOS/.test(ua) ? "chrome" : (/FxiOS|EdgiOS|OPiOS/.test(ua) ? "other" : "safari"))
    : (/SamsungBrowser/.test(ua) ? "samsung" : (/Firefox/.test(ua) ? "firefox" : "chrome"));
  var inApp = /FBAN|FBAV|Instagram|Line\/|LinkedInApp|Snapchat|GSA\//.test(ua);

  var m = location.pathname.match(/appaday-(\d{3})-/);
  var num = m ? m[1] : "";
  var appKey = num || location.pathname;

  function seenList() {
    try { return JSON.parse(localStorage.getItem(KEY_SEEN) || "[]"); } catch (e) { return []; }
  }
  function markSeen() {
    try {
      var s = seenList();
      if (s.indexOf(appKey) < 0) { s.push(appKey); localStorage.setItem(KEY_SEEN, JSON.stringify(s)); }
    } catch (e) { /* ignore */ }
  }
  if (!forced && seenList().indexOf(appKey) >= 0) return;

  function meta(name) {
    var el = document.querySelector('meta[name="' + name + '"]');
    return el ? el.getAttribute("content") : "";
  }
  var iconEl = document.querySelector('link[rel="apple-touch-icon"]');
  var icon = iconEl ? iconEl.href : "";
  var title = meta("apple-mobile-web-app-title") ||
    (document.title || "this app").split("|")[0].replace(/\s+$/, "");
  var accent = "#C8401A";

  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    if (ui) refresh();
  });
  window.addEventListener("appinstalled", function () { close(); });

  var I_SHARE = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path d="M12 15V3M7 8l5-5 5 5M5 12v8h14v-8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var I_MORE_H = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><circle cx="5" cy="12" r="2" fill="currentColor"/><circle cx="12" cy="12" r="2" fill="currentColor"/><circle cx="19" cy="12" r="2" fill="currentColor"/></svg>';
  var I_MORE_V = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><circle cx="12" cy="5" r="2" fill="currentColor"/><circle cx="12" cy="12" r="2" fill="currentColor"/><circle cx="12" cy="19" r="2" fill="currentColor"/></svg>';
  var I_MENU = '<svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  function chip(svg) { return '<span class="chip">' + svg + "</span>"; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function steps() {
    if (inApp) {
      return { arrow: "", list: [
        "Open this page in " + (isIOS ? "<b>Safari</b>" : "<b>Chrome</b>") + ". Tap the menu in this app and choose <b>Open in browser</b>.",
        "Then follow the save steps there."
      ] };
    }
    if (isIOS && browser === "safari") {
      return { arrow: isIPad ? "up" : "down", list: [
        "Tap " + chip(I_SHARE) + " <b>Share</b> in the Safari toolbar" + (isIPad ? " at the top." : " below.") +
          " If you do not see it, tap " + chip(I_MORE_H) + " first.",
        "Scroll down and tap <b>Add to Home Screen</b>.",
        "Keep <b>Open as Web App</b> on, then tap <b>Add</b>."
      ] };
    }
    if (isIOS && browser === "chrome") {
      return { arrow: "up", list: [
        "Tap " + chip(I_SHARE) + " <b>Share</b> beside the address bar.",
        "Tap <b>Add to Home Screen</b>, then <b>Add</b>."
      ] };
    }
    if (isIOS) {
      return { arrow: "", list: [
        "Open this page in <b>Safari</b>.",
        "Tap " + chip(I_SHARE) + " <b>Share</b>, then <b>Add to Home Screen</b>."
      ] };
    }
    if (browser === "samsung") {
      return { arrow: "down", list: [
        "Tap " + chip(I_MENU) + " the menu at the bottom right.",
        "Tap <b>Add page to</b>, then <b>Home screen</b>."
      ] };
    }
    if (browser === "firefox") {
      return { arrow: "", list: [
        "Tap " + chip(I_MORE_V) + " the menu.",
        "Tap <b>Add to Home screen</b> or <b>Install</b>."
      ] };
    }
    return { arrow: "up", list: [
      "Tap " + chip(I_MORE_V) + " the menu at the top right.",
      "Tap <b>Add to Home screen</b> or <b>Install app</b>, then confirm."
    ] };
  }

  var CSS = [
    ":host{all:initial}",
    "*{box-sizing:border-box}",
    ".wrap{position:fixed;left:0;right:0;bottom:0;z-index:2147483646;display:flex;justify-content:center;",
    "padding:0 10px calc(10px + env(safe-area-inset-bottom,0px));pointer-events:none;",
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%}",
    ".card{pointer-events:auto;width:440px;max-width:100%;background:#0F0E0C;color:#F5F0E8;border-radius:16px;",
    "box-shadow:0 12px 40px rgba(0,0,0,.45),0 0 0 1px rgba(255,255,255,.08);padding:12px;",
    "transform:translateY(130%);transition:transform .35s cubic-bezier(.2,.9,.3,1.1)}",
    ".card.in{transform:translateY(0)}",
    ".row{display:flex;align-items:center;gap:12px}",
    ".ico{width:44px;height:44px;border-radius:10px;flex:0 0 auto;background:#333;object-fit:cover}",
    ".txt{flex:1 1 auto;min-width:0;font-size:15px;line-height:1.3}",
    ".txt b{font-weight:600}",
    ".sub{display:block;font-size:12px;color:#B5AEA2;margin-top:2px}",
    "button{font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}",
    ".go{min-height:44px;padding:0 16px;border:0;border-radius:999px;background:var(--a);color:#fff;font-size:14px;font-weight:600;white-space:nowrap}",
    ".x{width:44px;height:44px;border:0;border-radius:50%;background:transparent;color:#B5AEA2;font-size:22px;line-height:1;flex:0 0 auto}",
    ".go:focus-visible,.x:focus-visible,.done:focus-visible{outline:2px solid #fff;outline-offset:2px}",
    "ol{list-style:none;margin:12px 0 4px;padding:0;counter-reset:s}",
    "li{counter-increment:s;position:relative;padding:2px 0 12px 36px;font-size:15px;line-height:1.45}",
    "li::before{content:counter(s);position:absolute;left:0;top:0;width:26px;height:26px;border-radius:50%;",
    "background:var(--a);color:#fff;font-size:13px;font-weight:700;line-height:26px;text-align:center}",
    "li b{font-weight:600}",
    ".chip{display:inline-flex;align-items:center;justify-content:center;vertical-align:-4px;width:24px;height:24px;",
    "border-radius:6px;background:rgba(255,255,255,.14);margin:0 1px}",
    ".done{display:block;width:100%;min-height:44px;border:1px solid rgba(255,255,255,.3);border-radius:10px;",
    "background:transparent;color:#F5F0E8;font-size:14px;font-weight:600}",
    ".arrow{position:fixed;z-index:2147483647;pointer-events:none;color:var(--a);filter:drop-shadow(0 2px 4px rgba(0,0,0,.5));",
    "animation:bob 1.1s ease-in-out infinite}",
    ".arrow.down{left:50%;margin-left:-18px;bottom:calc(4px + env(safe-area-inset-bottom,0px))}",
    ".arrow.up{top:calc(4px + env(safe-area-inset-top,0px));right:14px}",
    ".arrow.up svg{transform:rotate(180deg)}",
    ".wrap.open-down{padding-bottom:calc(56px + env(safe-area-inset-bottom,0px))}",
    "@keyframes bob{0%,100%{translate:0 0}50%{translate:0 6px}}",
    ".arrow.up{animation-name:bobup}",
    "@keyframes bobup{0%,100%{translate:0 0}50%{translate:0 -6px}}",
    "@media (prefers-reduced-motion:reduce){.card{transition:none}.arrow{animation:none}}"
  ].join("");

  var host = null, root = null, ui = null, expanded = false;

  function refresh() {
    if (!root) return;
    var card = root.querySelector(".card");
    var wrap = root.querySelector(".wrap");
    var oldArrow = root.querySelector(".arrow");
    if (oldArrow) oldArrow.parentNode.removeChild(oldArrow);
    wrap.className = "wrap";
    var img = icon ? '<img class="ico" alt="" src="' + esc(icon) + '">' : "";
    if (deferred) {
      card.innerHTML = '<div class="row">' + img +
        '<div class="txt">Install <b>' + esc(title) + '</b><span class="sub">Opens full screen from your home screen</span></div>' +
        '<button class="go" type="button" data-act="install">Install</button>' +
        '<button class="x" type="button" data-act="close" aria-label="Dismiss">&times;</button></div>';
    } else if (!expanded) {
      card.innerHTML = '<div class="row">' + img +
        '<div class="txt">Save <b>' + esc(title) + '</b> to your home screen<span class="sub">Opens full screen like an app</span></div>' +
        '<button class="go" type="button" data-act="show">Show me</button>' +
        '<button class="x" type="button" data-act="close" aria-label="Dismiss">&times;</button></div>';
    } else {
      var s = steps();
      var items = "";
      for (var i = 0; i < s.list.length; i++) items += "<li>" + s.list[i] + "</li>";
      card.innerHTML = '<div class="row">' + img +
        '<div class="txt">Save <b>' + esc(title) + '</b><span class="sub">Takes about ten seconds</span></div>' +
        '<button class="x" type="button" data-act="close" aria-label="Close">&times;</button></div>' +
        "<ol>" + items + "</ol>" +
        '<button class="done" type="button" data-act="close">Got it</button>';
      if (s.arrow) {
        var a = document.createElement("div");
        a.className = "arrow " + s.arrow;
        a.innerHTML = '<svg viewBox="0 0 24 24" width="36" height="36" aria-hidden="true"><path d="M12 3v16M5 12l7 7 7-7" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        root.appendChild(a);
        if (s.arrow === "down") wrap.className = "wrap open-down";
      }
    }
  }

  function close() {
    markSeen();
    if (!host) return;
    var card = root.querySelector(".card");
    if (card) card.classList.remove("in");
    var h = host; host = null; root = null; ui = null;
    setTimeout(function () { if (h.parentNode) h.parentNode.removeChild(h); }, 380);
  }

  function onClick(e) {
    var t = e.target;
    while (t && t !== root && !(t.getAttribute && t.getAttribute("data-act"))) t = t.parentNode;
    if (!t || t === root) return;
    var act = t.getAttribute("data-act");
    if (act === "close") close();
    else if (act === "show") { expanded = true; refresh(); }
    else if (act === "install" && deferred) {
      var p = deferred; deferred = null;
      p.prompt();
      if (p.userChoice) p.userChoice.then(function (r) { if (r && r.outcome === "accepted") close(); else refresh(); });
    }
  }

  function mount() {
    if (host || !document.body) return;
    host = document.createElement("div");
    host.setAttribute("data-appaday-save", "");
    root = host.attachShadow ? host.attachShadow({ mode: "open" }) : host;
    root.innerHTML = "<style>" + CSS + '</style><div class="wrap" role="dialog" aria-label="Save to home screen"><div class="card"></div></div>';
    ui = root.querySelector(".wrap");
    ui.style.setProperty("--a", accent);
    root.addEventListener("click", onClick);
    expanded = forced;
    refresh();
    document.body.appendChild(host);
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      var c = root && root.querySelector(".card"); if (c) c.classList.add("in");
    }); });
    markSeen();
  }

  function start() {
    var man = document.querySelector('link[rel="manifest"]');
    var go = function () { setTimeout(mount, forced ? 400 : 2500); };
    if (man && window.fetch) {
      fetch(man.href).then(function (r) { return r.json(); }).then(function (j) {
        if (j && /^#[0-9a-fA-F]{6}$/.test(j.theme_color || "")) accent = j.theme_color;
      }).catch(function () {}).then(go);
    } else { go(); }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
