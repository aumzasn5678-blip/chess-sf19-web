// sw.js — แคชแอพไว้ใช้ออฟไลน์ (ต้องเปิดผ่าน https หรือ localhost)
// นโยบาย: หน้า index.html = ดึงจากเน็ตก่อน (ได้เวอร์ชันใหม่เสมอ), ไฟล์ lib = cache ก่อน (เร็ว/ออฟไลน์)
const CACHE = "chess-scan-v4";
const CORE = ["./", "index.html", "manifest.webmanifest", "icon-180.png", "icon-512.png"];
const LIBS = ["lib/chess.js", "lib/stockfish.js", "lib/stockfish.wasm"];
const ICONS = ["icons/book.png","icons/brilliant.png","icons/great.png","icons/best.png","icons/excellent.png","icons/good.png","icons/inaccuracy.png","icons/mistake.png","icons/blunder.png","icons/miss.png","icons/forced.png"];
const BOOK = ["book/openings.json"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE.concat(LIBS).concat(ICONS).concat(BOOK))).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys()
    .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // เอกสาร/หน้าเพจ → เน็ตก่อน แล้วค่อย fallback แคช
  if (req.mode === "navigate" || url.pathname.endsWith("/") || url.pathname.endsWith("index.html")) {
    e.respondWith(
      fetch(req).then((res) => {
        if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {}); }
        return res;
      }).catch(() => caches.match(req).then((h) => h || caches.match("index.html")))
    );
    return;
  }
  // ไฟล์อื่น (lib) → แคชก่อน
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {}); }
      return res;
    }))
  );
});
