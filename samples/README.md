# Sample responses

Example `200` responses for three Fotocasa API endpoints. The API's published
documentation has no example responses, and its schema for `/suggestions` and
`/property-details` does not match what the API returns, so these were captured from
live calls on 20 October 2026.

They are trimmed: long arrays are cut to their first few items and descriptions are
shortened. Phone numbers, email addresses and contact names are removed, and private
advertisers (`"type": "particular"`) keep only their type. Field names are unchanged.

| File | Request |
|---|---|
| `suggestions.json` | `GET /suggestions?query=madrid` |
| `searchads.json` | `GET /searchads?combinedLocations=724,14,28,173,0,28079,0,0,0&latitude=40.4096&longitude=-3.68624&transactionType=RENT&propertyType=HOMES&sortType=LATEST&publicationDate=INDIFFERENT&minRooms=2&pageNumber=1&size=10` |
| `property-details.json` | `GET /property-details?transactionType=RENT&propertyId=191160142&language=en` |

They are useful for writing parsers and tests before you subscribe. Live data changes
daily, so do not hard-code these values.
