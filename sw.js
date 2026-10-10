// sw.js — แคชแอพไว้ใช้แบบออฟไลน์ (ต้องเปิดผ่าน https หรือ localhost เท่านั้น)
const CACHE = "chess-sf19-v1";
const FILES = [
  "./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-512.png",
  "lib/chess.js", "lib/stockfish.js", "lib/stockfish.wasm"
];
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
      return res;
    }).catch(() => caches.match("index.html")))
  );
});
