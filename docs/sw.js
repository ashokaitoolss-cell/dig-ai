/* dig.ai service worker — cache-first shell, network-first feed. */
var SHELL = "digai-shell-v1";
var ASSETS = [
  "./", "./index.html", "./app.css", "./app.js", "./manifest.webmanifest",
  "./icons/icon.svg", "./icons/icon-192.png", "./icons/icon-512.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(SHELL).then(function (c) { return c.addAll(ASSETS); }));
  self.skipWaiting();
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== SHELL; }).map(function (k) {
      return caches.delete(k);
    }));
  }));
  self.clients.claim();
});

self.addEventListener("fetch", function (e) {
  var url = new URL(e.request.url);
  if (url.pathname.endsWith("feed.json")) {
    e.respondWith(
      fetch(e.request).then(function (resp) {
        var copy = resp.clone();
        caches.open(SHELL).then(function (c) { c.put(e.request, copy); });
        return resp;
      }).catch(function () { return caches.match(e.request); })
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then(function (hit) {
      return hit || fetch(e.request);
    })
  );
});
