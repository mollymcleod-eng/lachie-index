/* The Lachie Index — offline shell.
   Haast has patchy coverage, so the app must open at the hut with no signal.
   Tides and moon are baked into the page, so a cached shell is a working app. */

const CACHE = "lachie-v2";
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
