const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const scope = 'https://example.test/okinawa-family-trip/';
const stores = new Map();
const listeners = {};
let offline = false;
const networkRequests = [];
const caches = {
  async open(name) {
    if (!stores.has(name)) stores.set(name, new Map());
    const entries = stores.get(name);
    const keyOf = request => typeof request === 'string' ? new URL(request, scope).href
      : request instanceof URL ? request.href : request.url;
    return {
      async addAll(paths) { for (const path of paths) entries.set(keyOf(path), new Response(`cached:${path}`)); },
      async match(request) { const response = entries.get(keyOf(request)); return response?.clone(); },
      async put(request, response) { entries.set(keyOf(request), response.clone()); }
    };
  },
  async keys() { return [...stores.keys()]; },
  async delete(name) { return stores.delete(name); }
};
const self = {
  location: new URL(scope),
  registration: { scope },
  clients: { claim: async () => {} },
  skipWaiting: async () => {},
  addEventListener(name, callback) { listeners[name] = callback; }
};
const fetch = async (request, init) => {
  networkRequests.push(init);
  if (offline) throw new Error('offline');
  return new Response(`network:${request.url || request}`);
};
vm.runInNewContext(fs.readFileSync('./sw.js', 'utf8'), { self, caches, fetch, URL, Promise, Response });

async function trigger(name) {
  const waits = [];
  listeners[name]({ waitUntil: promise => waits.push(promise) });
  await Promise.all(waits);
}

async function request(url, mode = 'cors') {
  let response;
  listeners.fetch({ request: { url, mode, method: 'GET' }, respondWith: promise => { response = promise; } });
  return response ? response : null;
}

(async () => {
  await stores.set('okinawa-trip-v0', new Map());
  await trigger('install');
  await trigger('activate');
  assert.equal(stores.has('okinawa-trip-v0'), false, 'activation removes old app caches');

  const onlinePage = await request(scope + 'index.html', 'navigate');
  assert.match(await onlinePage.text(), /^network:/, 'navigation prefers the current network page');
  assert.equal(networkRequests.at(-1)?.cache, 'no-cache', 'navigation revalidates the HTTP cache');
  offline = true;
  const page = await request(scope + 'ja.html?offline=1', 'navigate');
  assert.match(await page.text(), /cached:\.\/ja\.html/, 'offline Japanese navigation returns its cached page');
  const css = await request(scope + 'assets/trip.css');
  assert.match(await css.text(), /cached:\.\/assets\/trip\.css/, 'local assets are served from cache first');
  assert.equal(await request('https://maps.example.test/place', 'navigate'), null, 'external maps are not intercepted');
  console.log('Offline page fallback, local asset cache, and external pass-through checks passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
