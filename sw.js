// Bump the version whenever a file changes (and VER in index.html), so installed copies pick it up.
const CACHE = 'sleep-v6';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png', './bg-classroom.jpg'];

self.addEventListener('install', e => {
  // cache: 'reload' skips the browser's HTTP cache, so a new version never stores a stale page
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('sleep-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  const page = req.mode === 'navigate' || /\/(index\.html)?$/.test(new URL(req.url).pathname);
  if (page) {
    // the page itself: newest from the network when online (3 s at most), the saved copy when offline
    e.respondWith(caches.open(CACHE).then(async c => {
      const net = fetch(req, { cache: 'no-cache' }).then(res => { if (res && res.ok) c.put('./index.html', res.clone()); return res; });
      const slow = new Promise(r => setTimeout(r, 3000));
      try {
        const res = await Promise.race([net, slow.then(() => null)]);
        if (res && res.ok) return res;
      } catch (err) {}
      const hit = await c.match('./index.html');
      if (hit) { net.catch(() => {}); return hit; }
      try { return await net; } catch (err) {
        return new Response('离线中，且没有缓存', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
      }
    }));
    return;
  }
  // pictures and icons: saved copy first, refreshed in the background
  e.respondWith(
    caches.open(CACHE).then(async c => {
      const hit = await c.match(req, { ignoreSearch: true });
      const net = fetch(req).then(res => {
        if (res && res.ok) c.put(req, res.clone());
        return res;
      }).catch(() => null);
      if (hit) { e.waitUntil(net); return hit; }
      const res = await net;
      return res || new Response('', { status: 504 });
    })
  );
});
