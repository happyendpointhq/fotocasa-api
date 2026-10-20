// Fotocasa API quickstart. Node 18+ (built-in fetch), no dependencies.
//   RAPIDAPI_KEY=... node quickstart.mjs madrid

const HOST = 'fotocasa3.p.rapidapi.com';

async function get(path, params = {}) {
  const url = new URL(`https://${HOST}${path}`);
  for (const [key, value] of Object.entries(params)) {
    if (value != null) url.searchParams.set(key, value);
  }
  const res = await fetch(url, {
    headers: { 'x-rapidapi-host': HOST, 'x-rapidapi-key': process.env.RAPIDAPI_KEY },
  });
  if (!res.ok) throw new Error(`Fotocasa API ${res.status}: ${await res.text()}`);
  return (await res.json()).data;
}

const query = process.argv[2] ?? 'madrid';
const [place] = await get('/suggestions', { query });
if (!place) throw new Error(`No Fotocasa location matches ${query}`);
console.log(`Using ${place.text} (${place.combinedLocationIds})`);

const results = await get('/searchads', {
  combinedLocations: place.combinedLocationIds,
  latitude: place.coordinates.latitude,
  longitude: place.coordinates.longitude,
  transactionType: 'BUY',
  propertyType: 'HOMES',
  sortType: 'LATEST',
  publicationDate: 'INDIFFERENT',
  pageNumber: 1,
  size: 10,
});
console.log(`${results.totalItems} homes for sale`);
for (const ad of results.items) {
  const area = ad.location?.level8Name ?? ad.location?.level7Name ?? '';
  console.log(`${String(ad.transaction.price).padStart(9)} EUR  ${String(ad.surface ?? '?').padStart(4)} m2  ${area}`);
}
