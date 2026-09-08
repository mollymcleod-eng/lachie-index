/* The Lachie Index — offline shell.
   Haast has patchy coverage, so the app must open at the hut with no signal.
   Tides and moon are baked into the page, so a cached shell is a working app. */

const CACHE = "lachie-v3";
const FONTS = "lachie-fonts-v1";
const SHELL = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png", "./favicon-32.png"
];
const FONT_HOSTS = ["fonts.googleapis.com", "fonts.gstatic.com"];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL))
      .then(() => self.skipWaiting())
      .catch(() => self.skipWaiting())   // a single 404 must not brick the install
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE && k !== FONTS).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;

  // Webfonts are immutable once fetched: cache-first, and keep them in their own
  // bucket so bumping the app cache doesn't force a re-download at the hut.
  if (FONT_HOSTS.includes(url.hostname)){
    e.respondWith(
      caches.open(FONTS).then(c => c.match(e.request).then(hit =>
        hit || fetch(e.request).then(res => {
          // Opaque cross-origin responses are still worth keeping for the shell.
          if (res && (res.ok || res.type === "opaque")) c.put(e.request, res.clone());
          return res;
        })
      ))
    );
    return;
  }

  // Weather calls go straight to the network. The page has its own saved copy
  // and its own "no signal" handling, so caching them here would only serve
  // stale forecasts behind its back.
  if (url.origin !== self.location.origin) return;

  // The page itself is network-first: with signal you always open the current
  // version, with none you fall straight back to the cached copy. Serving the
  // cache first here would show a stale app for one whole load after every
  // update, which is how you end up fishing off last month's scoring.
  if (e.request.mode === "navigate" || e.request.destination === "document"){
    e.respondWith(
      fetch(e.request)
        .then(res => {
          if (res && res.ok) caches.open(CACHE).then(c => c.put(e.request, res.clone()));
          return res;
        })
        .catch(() => caches.match(e.request).then(hit => hit || caches.match("./index.html")))
    );
    return;
  }

  // Everything else is stale-while-revalidate: instant, quietly kept current.
  e.respondWith(
    caches.match(e.request).then(hit => {
      const fresh = fetch(e.request).then(res => {
        if (res && res.ok){
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return res;
      }).catch(() => hit);
      return hit || fresh;
    })
  );
});
