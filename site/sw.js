const V = 'hist7-f86bf0ffc9';
const FILES = ["./", "./app.js", "./asia.html", "./england.html", "./europe.html", "./france.html", "./how.html", "./icon-maskable.svg", "./icon.svg", "./index.html", "./lenta.html", "./manifest.webmanifest", "./map.html", "./netherlands.html", "./style.css", "./timeline.html", "./video.css", "./p/01.html", "./p/02.html", "./p/03.html", "./p/04.html", "./p/05.html", "./p/06.html", "./p/07.html", "./p/08.html", "./p/09.html", "./p/10.html", "./p/11.html", "./p/12.html", "./p/13.html", "./p/14.html", "./p/15.html", "./p/16.html", "./p/17.html", "./p/18.html", "./p/19.html", "./p/20.html", "./p/21.html", "./rus/adverb.html", "./rus/cheat.html", "./rus/conjunction.html", "./rus/gerund.html", "./rus/index.html", "./rus/interjection.html", "./rus/language.html", "./rus/participle.html", "./rus/particle.html", "./rus/practice.html", "./rus/preposition.html", "./rus/rus.css", "./rus/rus.js", "./rus/state.html", "./rus/test.html"];
self.addEventListener('install', e => e.waitUntil(caches.open(V).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('hist7-') && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  e.respondWith(caches.match(r, {ignoreSearch: true}).then(hit => hit || fetch(r)));
});
