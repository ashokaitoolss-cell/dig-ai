/* dig.ai feed app — vanilla JS, no build step. */
(function () {
  "use strict";

  var DEMO = new URLSearchParams(location.search).has("demo");
  var FEED_URL = DEMO ? "demo-feed.json" : "feed.json";
  var SEEN_KEY = "digai-seen-v1";
  var EMOJI = {
    "video-gen": "🎬", "image-gen": "🎨", "3d": "🧊",
    "audio-music": "🎵", "editing-vfx": "✂️",
    "avatar-lipsync": "🗣", "creative-platform": "🛠",
    "model-infra": "⚙️", "other": "📡"
  };
  // filter groups: which categories each chip shows
  var GROUPS = {
    "video-gen": ["video-gen", "avatar-lipsync"],
    "image-gen": ["image-gen"],
    "3d": ["3d"],
    "audio-music": ["audio-music"],
    "editing-vfx": ["editing-vfx"],
    "platform": ["creative-platform", "model-infra", "other"]
  };

  var feedEl = document.getElementById("feed");
  var statusEl = document.getElementById("status");
  var relToggle = document.getElementById("relToggle");
  var items = [];
  var filter = "all";
  var minRel = 0;
  var seen = loadSeen();
  var unreadAtLoad = {};

  function loadSeen() {
    try { return new Set(JSON.parse(localStorage.getItem(SEEN_KEY) || "[]")); }
    catch (e) { return new Set(); }
  }
  function saveSeen() {
    try { localStorage.setItem(SEEN_KEY, JSON.stringify(Array.from(seen).slice(-2000))); }
    catch (e) { /* private mode */ }
  }

  function timeAgo(iso) {
    var mins = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 60000));
    if (mins < 60) return mins + "M AGO";
    if (mins < 1440) return Math.round(mins / 60) + "H AGO";
    if (mins < 10080) return Math.round(mins / 1440) + "D AGO";
    var d = new Date(iso);
    return ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"][d.getMonth()] + " " + d.getDate();
  }

  function visible() {
    return items.filter(function (it) {
      if (it.relevance < minRel) return false;
      if (filter === "all") return true;
      return (GROUPS[filter] || []).indexOf(it.category) !== -1;
    });
  }

  function render() {
    var list = visible();
    feedEl.innerHTML = "";
    if (!list.length) {
      var empty = document.createElement("div");
      empty.className = "slide";
      empty.innerHTML = '<div class="card in"><div class="empty">' +
        '<span class="sig">// NOTHING DUG UP YET</span>' +
        '<span>' + (items.length ? "no launches match this filter" :
          "the radar runs every 3 hours — launches will appear here") + '</span>' +
        "</div></div>";
      feedEl.appendChild(empty);
      statusEl.textContent = "";
      return;
    }
    var unread = 0;
    list.forEach(function (it) {
      var isUnread = !!unreadAtLoad[it.id];
      if (isUnread) unread++;
      var slide = document.createElement("section");
      slide.className = "slide";
      var card = document.createElement("article");
      card.className = "card" + (isUnread ? " unread" : "");
      card.dataset.id = it.id;
      card.innerHTML =
        '<span class="corner"></span>' +
        '<div class="meta">' +
          '<span class="cat">' + (EMOJI[it.category] || "") + " " + esc(it.category) + "</span>" +
          (isUnread ? '<span class="new">● NEW</span>' : "") +
          '<span class="rel' + (it.relevance >= 8 ? " hot" : "") + '">REL ' +
            String(it.relevance).padStart(2, "0") + "</span>" +
        "</div>" +
        "<h2>" + esc(it.headline) + "</h2>" +
        '<p class="summary">' + esc(it.summary) + "</p>" +
        '<div class="dateline">' + esc(it.source) + " · " + timeAgo(it.timestamp) + "</div>";
      card.addEventListener("click", function () {
        window.open(it.url, "_blank", "noopener");
      });
      slide.appendChild(card);
      feedEl.appendChild(slide);
    });
    statusEl.classList.toggle("alert", unread > 0);
    statusEl.textContent = unread ? unread + " UNREAD" : "ALL READ";
    observeCards();
    var firstUnread = feedEl.querySelector(".card.unread");
    if (firstUnread) firstUnread.closest(".slide").scrollIntoView({ block: "start" });
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  var io = null;
  function observeCards() {
    if (io) io.disconnect();
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add("in");
        var id = e.target.dataset.id;
        if (id && !seen.has(id)) { seen.add(id); saveSeen(); }
      });
    }, { root: feedEl, threshold: 0.5 });
    feedEl.querySelectorAll(".card").forEach(function (c) { io.observe(c); });
  }

  function load(showPull) {
    if (showPull) setPull(true);
    return fetch(FEED_URL, { cache: "no-store" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        items = Array.isArray(data) ? data : [];
        unreadAtLoad = {};
        items.forEach(function (it) { if (!seen.has(it.id)) unreadAtLoad[it.id] = true; });
        render();
      })
      .catch(function () {
        if (!items.length) {
          feedEl.innerHTML = '<div class="slide"><div class="card in"><div class="empty">' +
            '<span class="sig">// SIGNAL LOST</span><span>could not load feed.json</span>' +
            "</div></div></div>";
        }
      })
      .finally(function () { setPull(false); });
  }

  /* pull-to-refresh */
  var pullEl = document.createElement("div");
  pullEl.className = "pull";
  pullEl.textContent = "// DIGGING…";
  document.body.appendChild(pullEl);
  function setPull(on) { pullEl.classList.toggle("show", on); }

  var startY = null;
  feedEl.addEventListener("touchstart", function (e) {
    startY = feedEl.scrollTop <= 0 ? e.touches[0].clientY : null;
  }, { passive: true });
  feedEl.addEventListener("touchmove", function (e) {
    if (startY !== null) setPull(e.touches[0].clientY - startY > 40);
  }, { passive: true });
  feedEl.addEventListener("touchend", function (e) {
    if (startY !== null && e.changedTouches[0].clientY - startY > 90) load(true);
    else setPull(false);
    startY = null;
  });

  /* filters */
  document.getElementById("filters").addEventListener("click", function (e) {
    var chip = e.target.closest(".chip");
    if (!chip) return;
    if (chip.id === "relToggle") {
      minRel = minRel ? 0 : 7;
      chip.classList.toggle("active", minRel > 0);
      chip.setAttribute("aria-pressed", String(minRel > 0));
    } else {
      filter = chip.dataset.filter;
      document.querySelectorAll(".chip[data-filter]").forEach(function (c) {
        c.classList.toggle("active", c === chip);
      });
    }
    render();
    feedEl.scrollTop = 0;
  });

  if ("serviceWorker" in navigator && !DEMO) {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  }

  load(false);
})();
