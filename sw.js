/* The Lachie Index — offline shell.
   Haast has patchy coverage, so the app must open at the hut with no signal.
   Tides and moon are baked into the page, so a cached shell is a working app. */

const CACHE = "lachie-v1";
const SHELL = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png", "./favicon-32.png"
];

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
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  // Weather calls go straight to the network. The page has its own saved copy
  // and its own "no signal" handling, so caching them here would only serve
  // stale forecasts behind its back.
  if (e.request.method !== "GET" || url.origin !== self.location.origin) return;

  // Stale-while-revalidate: instant open, quietly updated for next time.
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
