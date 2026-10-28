# Fotocasa API and Scraper

The Fotocasa API returns Spanish property listings from Fotocasa as JSON: homes, garages,
land, premises, offices and buildings for sale and rent across mainland Spain, the Balearic
Islands and Andorra, with prices in euros, surface in m2, rooms, photos, advertiser type
and district-level listing counts. Fotocasa does not offer a public developer API for its
listings, so this REST API is the way to use its data in your own code without building and
maintaining a Fotocasa scraper.

Built and maintained by [Happy Endpoint](https://happyendpoint.com/library/fotocasa-api?utm_source=github&utm_medium=readme&utm_campaign=fotocasa-api).

- Subscribe and test every endpoint on RapidAPI: https://rapidapi.com/happyendpoint/api/fotocasa3
- Product page: https://happyendpoint.com/library/fotocasa-api?utm_source=github&utm_medium=readme&utm_campaign=fotocasa-api
- Hosted docs: https://docs.happyendpoint.com/fotocasa/

---

## At a glance

| | |
|---|---|
| Base URL | `https://fotocasa3.p.rapidapi.com` |
| Auth | `x-rapidapi-key` and `x-rapidapi-host` headers |
| Endpoints | 4, all `GET` |
| Coverage | Spain (all regions), the Balearic Islands and Andorra |
| Property types | Homes, garages, land, premises, offices, box rooms, buildings |
| Deal types | Buy and rent |
| Format | JSON, every response wrapped in `{"success": true, "data": ...}` |

---

## What data you get

**Locations**
- Place suggestions for typed text, each with the `combinedLocationIds` string and centre point that searches need

**Search**
- Listings for a location, filtered by deal type, property type and subtype, price, surface, rooms, bathrooms, condition, new construction and listing age
- Six sort orders: relevance rating, latest, price, surface, price per m2 and online guided tour
- Per row: price and price drop, surface, rooms, baths, floor type, rental type, ZIP code, district and neighbourhood with coordinates, publication and update dates, photo count, agency or private advertiser, and the listing URL in four languages
- `locationFacets`: listing counts for every district of the searched area, with the location string to search each one

**Property details**
- The full listing: features (rooms, bathrooms, surface, heating, floor), extras such as terrace or fitted kitchen, every photo, descriptions per language, energy certificate values, address levels and coordinates

---

## Quick start

### 1. Get an API key

Subscribe on [RapidAPI](https://rapidapi.com/happyendpoint/api/fotocasa3). There is a free plan. Copy `.env.example` to `.env` and paste your key.

### 2. Make a request

Searches take a `combinedLocations` string plus a centre point, not a place name. Look it up first:

```bash
curl "https://fotocasa3.p.rapidapi.com/suggestions?query=madrid" \
  -H "x-rapidapi-host: fotocasa3.p.rapidapi.com" \
  -H "x-rapidapi-key: YOUR_RAPIDAPI_KEY"

curl "https://fotocasa3.p.rapidapi.com/searchads?combinedLocations=724,14,28,173,0,28079,0,0,0&latitude=40.4096&longitude=-3.68624&transactionType=RENT&propertyType=HOMES&sortType=LATEST&publicationDate=INDIFFERENT&pageNumber=1&size=10" \
  -H "x-rapidapi-host: fotocasa3.p.rapidapi.com" \
  -H "x-rapidapi-key: YOUR_RAPIDAPI_KEY"
```

### Python

```bash
pip install -r requirements.txt
cd examples/python
python quickstart.py madrid
```

```python
from client import find_location, get, search_params

place = find_location("madrid")
results = get(
    "/searchads",
    **search_params(place),
    transactionType="BUY",
    propertyType="HOMES",
    sortType="LATEST",
    publicationDate="INDIFFERENT",
    pageNumber=1,
)
for ad in results["items"]:
    print(ad["transaction"]["price"], ad["surface"], ad["propertyId"])
```

### JavaScript

```bash
RAPIDAPI_KEY=your_key node examples/javascript/quickstart.mjs madrid
```

---

## Example response

One row from `GET /searchads` for rentals in Madrid, trimmed. Taken from a live call on
20 October 2026; the full responses are in [`samples/`](samples/).

```json
{
  "success": true,
  "data": {
    "totalItems": 4150,
    "page": { "number": 1, "size": 10 },
    "items": [
      {
        "id": "3_191160142",
        "propertyId": "191160142",
        "transactionType": "3",
        "surface": 78,
        "rooms": 3,
        "baths": 1,
        "zipCode": "28021",
        "floorType": "INTERMEDIATE_FLOOR",
        "transaction": { "type": "RENT", "price": 990, "priceDrop": null },
        "location": {
          "level5Name": "Madrid",
          "level7Name": "Villaverde",
          "level8Name": "Villaverde Alto"
        },
        "agency": { "type": "professional", "alias": "Alquiler Seguro" },
        "publicationDate": "2026-10-20T15:02:22.413",
        "photosCount": 21
      }
    ],
    "locationFacets": {
      "districts": [
        { "literal": "Arganzuela", "counter": 231, "combinedLocation": "724,14,28,173,0,28079,0,671,0" }
      ]
    }
  }
}
```

---

## Endpoints

Base URL: `https://fotocasa3.p.rapidapi.com`

| Endpoint | Returns |
|---|---|
| `GET /suggestions` | Place suggestions with `combinedLocationIds` and coordinates |
| `GET /searchads` | Listings for a location with filters, sorting, paging and district counts |
| `GET /property-details` | The full listing for a `propertyId` and deal type, in `en`, `es`, `de` or `ca` |
| `GET /health` | Service health |

`/searchads` requires `combinedLocations`, `latitude`, `longitude`, `pageNumber`,
`transactionType` (`BUY` or `RENT`), `propertyType`, `sortType` and `publicationDate`
(`INDIFFERENT`, `TWO_DAYS`, `ONE_WEEK` or `ONE_MONTH`). Prices are in euros and surfaces
in m2.

---

## Things to know about the data

These come from running the API live. They are the ones that produce wrong numbers rather
than errors.

- **Search rows and the details record are different shapes.** A search row has
  `transaction.price`, `surface`, `rooms` and `baths` as plain fields. `/property-details`
  returns `transactions[0].value` as a list (`[990]`), and `features` as a list of one-key
  objects (`[{"rooms": 3}, {"bathrooms": 1}, {"surface": 78}]`). `client.feature_map()`
  merges them. Map each shape separately.
- **Location is a nine-part string, not a name.** `724,14,28,173,0,28079,0,0,0` is
  country, region, province, area and municipality (Madrid); a district fills the eighth
  slot (`...,0,671,0` is Arganzuela). Take it from `/suggestions` or from a search's
  `locationFacets`, and always send the matching `latitude` and `longitude`.
- **One search gives you a district breakdown.** `locationFacets.districts` lists every
  district with its listing count under your filters (in our live Madrid sale search, 21
  districts from 1,867 in Barrio de Salamanca down to 79 in Barajas). It is the cheapest
  way to map a city: one call, not one per district.
- **Codes are numeric strings.** Rows carry `transactionType: "3"` for a rental while you
  searched with `RENT`, and `transaction.type` repeats it as text. `propertyType`,
  `propertySubtype` and the feature ids are numeric codes too. `id` is
  `<transactionType>_<propertyId>`; `/property-details` takes the bare `propertyId` plus
  `BUY` or `RENT`.
- **Sorting by price brings out the odd listings first.** Cheapest-first rentals in Madrid
  started with a 12 m2 room at 360 EUR (`rentalType: "TEMPORARY"`) and a run of 400 EUR
  rows for 75 to 250 m2 homes, nearly all from private advertisers. A newest-first sale
  search had three of 30 rows under 100,000 EUR, including 98,905 EUR for 526 m2 in Aravaca,
  where typical rows ran 4,000 to 9,800 EUR per m2. Read the description and drop rows
  below a sensible floor before you take a median.
- **`rentalType` marks short lets.** `TEMPORARY` rows are temporary or room rentals. Keep
  them out of long-term rent comparisons.
- **Advertisers are agencies or private people.** `agency.type` is `professional` or
  `particular`. Private advertisers' rows carry their personal phone number; this repo's
  samples remove phone numbers and private advertisers' names, and so should anything
  you publish.
- **Facets follow your filters.** Arganzuela showed 400 rentals in an unfiltered rental
  search and 231 with `minRooms=2`. Compare district counts only between searches with the
  same filters.

---

## Examples in this repo

| File | What it does |
|---|---|
| [`examples/python/quickstart.py`](examples/python/quickstart.py) | Place lookup, newest rentals with price per m2, one full listing |
| [`examples/python/search_to_csv.py`](examples/python/search_to_csv.py) | Pages through a search into a flat CSV and prints listing counts by district |
| [`examples/javascript/quickstart.mjs`](examples/javascript/quickstart.mjs) | Place lookup and a sale search in Node 18+, no dependencies |
| [`samples/`](samples/) | Live example responses for three endpoints |

---

## API or your own Fotocasa scraper

A homemade Fotocasa scraper has to follow the site's page structure and bot protection,
and breaks when either changes. This API returns the same listings as JSON with documented
parameters, so the work you keep is the analysis. If you need a one-off national file or a
recurring export rather than API calls, [contact us](https://happyendpoint.com/contact?utm_source=github&utm_medium=readme&utm_campaign=fotocasa-api).

---

## Use it from Claude, Cursor or any MCP client

RapidAPI exposes every endpoint as an MCP tool, so an AI assistant can query Fotocasa
listings without code:

```json
{
  "mcpServers": {
    "fotocasa": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.rapidapi.com",
        "--header",
        "x-api-host: fotocasa3.p.rapidapi.com",
        "--header",
        "x-api-key: YOUR_RAPIDAPI_KEY"
      ]
    }
  }
}
```

| Client | Config path |
|---|---|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| Claude Code | `.mcp.json` in your project root |

---

## FAQ

### Is there a Fotocasa API?

Fotocasa does not publish a public developer API for its listings. This API, built and
maintained by Happy Endpoint and independent of Fotocasa, provides that access as REST and
JSON.

### Is there a free Fotocasa API?

Yes. The RapidAPI listing has a free plan, and every endpoint can be tried on it.

### Where is the Fotocasa API documentation?

At [docs.happyendpoint.com/fotocasa](https://docs.happyendpoint.com/fotocasa/) and on the
RapidAPI listing. The endpoint table above summarises it, and live example responses are in
[`samples/`](samples/).

### Is there a Fotocasa API example in Python?

Yes. [`examples/python/quickstart.py`](examples/python/quickstart.py) resolves a place,
searches it and opens a listing, using the small client in
[`client.py`](examples/python/client.py).

### How do I get a Fotocasa API key?

Subscribe to the API on RapidAPI; your key is shown in the RapidAPI dashboard and goes in
the `x-rapidapi-key` header.

### Can I scrape Fotocasa rental prices by district?

Yes. Run one search for the city and read `locationFacets.districts` for the counts, then
search any district with its own `combinedLocation` string.
[`search_to_csv.py`](examples/python/search_to_csv.py) does both.

### Do you cover other Spanish property sites?

Yes, including Idealista and Milanuncios. See the
[API library](https://happyendpoint.com/library?utm_source=github&utm_medium=readme&utm_campaign=fotocasa-api).

---

## Related repos

- [awesome-real-estate-apis](https://github.com/happyendpointhq/awesome-real-estate-apis) - real estate APIs and data sources by country, including official and free ones
- [rent-com-api](https://github.com/happyendpointhq/rent-com-api) - US rental listings with runnable Python examples
- [uae-real-estate-api](https://github.com/happyendpointhq/uae-real-estate-api) - Bayut and PropertyFinder through one API
- [yad2-api](https://github.com/happyendpointhq/yad2-api) - Israel listings with government-registered sale prices, and a comparables example
- [bayut-api-python-examples](https://github.com/happyendpointhq/bayut-api-python-examples) - more Python patterns for a property API

---

## Disclaimer

Happy Endpoint is an independent provider. This project is **not affiliated
with, endorsed by, sponsored by, or connected to** any of the websites,
platforms, retailers, or marketplaces referenced here or reachable through the
underlying APIs.

All product names, brands, trademarks, and registered trademarks are the
property of their respective owners. Any reference to them is descriptive only,
to identify the subject matter of the data, and does not imply any association
or endorsement.

Users are responsible for ensuring their use of any data complies with
applicable laws and the terms of service of the relevant source.

---

## About Happy Endpoint

[Happy Endpoint](https://happyendpoint.com) builds and maintains real-time data
APIs for property portals, retailers, and marketplaces. All APIs are available on
RapidAPI with a free tier.

- Catalogue: [happyendpoint.com/library](https://happyendpoint.com/library)
- Datasets: [happyendpoint.com/datasets](https://happyendpoint.com/datasets)
- Documentation: [docs.happyendpoint.com](https://docs.happyendpoint.com)
- Contact: happyendpointhq@gmail.com

## Licence

MIT. See [LICENSE](LICENSE).
