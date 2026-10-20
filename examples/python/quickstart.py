"""Find a place, search rentals in it, then open the newest listing.

    python quickstart.py madrid
"""

import sys

from client import feature_map, find_location, get, neighbourhood, price_per_m2, search_params

query = sys.argv[1] if len(sys.argv) > 1 else "madrid"

# 1. Resolve the place. Searches take combinedLocations plus a centre point, not a name.
place = find_location(query)
print(f"Using {place['text']}  combinedLocations={place['combinedLocationIds']}")

# 2. Newest homes for rent with at least two rooms. Prices are euros (per month for rentals).
results = get(
    "/searchads",
    **search_params(place),
    transactionType="RENT",
    propertyType="HOMES",
    sortType="LATEST",
    publicationDate="INDIFFERENT",
    minRooms=2,
    pageNumber=1,
    size=10,
)
print(f"{results['totalItems']:,} listings, showing {len(results['items'])}\n")
for ad in results["items"]:
    price = ad["transaction"]["price"]
    per_m2 = price_per_m2(ad)
    print(
        f"{price:>7,} EUR  {ad.get('surface') or '?':>4} m2  {ad.get('rooms') or '?'} rooms  "
        f"{(str(per_m2) + ' EUR/m2') if per_m2 else '':<12} {neighbourhood(ad)}  (id {ad['propertyId']})"
    )

# 3. The full record for the first row. Details take the bare propertyId and the deal type,
#    and come back in a different shape from search rows (see the README).
if results["items"]:
    ad = results["items"][0]
    details = get("/property-details", transactionType="RENT", propertyId=ad["propertyId"], language="en")
    facts = feature_map(details)
    deal = (details.get("transactions") or [{}])[0]
    print(f"\n{facts.get('surface')} m2, {facts.get('rooms')} rooms, {facts.get('bathrooms')} bathrooms")
    print(f"Price: {deal.get('value')} EUR (periodicityId {deal.get('periodicityId')}, reduced {deal.get('reduced')})")
    print(f"Extras: {', '.join(v for item in details.get('otherFeatures') or [] for v in item.values())}")
    print(f"Photos: {len(details.get('multimedias') or [])}, energy rating id {details.get('energyCertificate')}")
    print(f"https://www.fotocasa.es{(details.get('detail') or {}).get('en', '')}")
