"""Export a Fotocasa search to CSV, and print listing counts by district.

    python search_to_csv.py madrid --type BUY --max-price 400000 --out madrid.csv
    python search_to_csv.py --combined-locations 724,14,28,173,0,28079,0,0,0 \
        --lat 40.4096 --lon -3.68624 --type RENT --max-pages 1

Every search response also carries `locationFacets`: listing counts for each district
(with the combinedLocations string to search that district on its own), so one call gives
you a city's breakdown.
"""

import argparse
import csv

from client import find_location, get, neighbourhood, price_per_m2, search_params

COLUMNS = [
    "propertyId", "transaction_type", "price", "price_drop", "surface", "price_per_m2", "rooms",
    "baths", "floorType", "rentalType", "advertiser_type", "zipCode", "district", "neighbourhood",
    "latitude", "longitude", "publicationDate", "alterDate", "photosCount", "url",
]


def flatten(ad):
    loc = ad.get("location") or {}
    deal = ad.get("transaction") or {}
    english = next((u["value"] for u in ad.get("uris") or [] if u["language"] == "en_US"), None)
    return {
        "propertyId": ad["propertyId"],
        "transaction_type": deal.get("type"),
        "price": deal.get("price"),
        "price_drop": deal.get("priceDrop"),
        "surface": ad.get("surface"),
        "price_per_m2": price_per_m2(ad),
        "rooms": ad.get("rooms"),
        "baths": ad.get("baths"),
        "floorType": ad.get("floorType"),
        "rentalType": ad.get("rentalType"),
        # "professional" (agency) or "particular" (private advertiser)
        "advertiser_type": (ad.get("agency") or {}).get("type"),
        "zipCode": ad.get("zipCode"),
        "district": loc.get("level7Name"),
        "neighbourhood": neighbourhood(ad),
        "latitude": loc.get("latitude"),
        "longitude": loc.get("longitude"),
        "publicationDate": ad.get("publicationDate"),
        "alterDate": ad.get("alterDate"),
        "photosCount": ad.get("photosCount"),
        "url": f"https://www.fotocasa.es{english}" if english else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("place", nargs="?", help="a place name, resolved with /suggestions")
    parser.add_argument("--combined-locations", help="skip the lookup: combinedLocations string")
    parser.add_argument("--lat", type=float)
    parser.add_argument("--lon", type=float)
    parser.add_argument("--type", default="BUY", choices=["BUY", "RENT"])
    parser.add_argument("--property-type", default="HOMES",
                        choices=["HOMES", "GARAGES", "LAND", "PREMISES", "OFFICE", "BOX_ROOM", "BUILDING"])
    parser.add_argument("--min-price", type=int)
    parser.add_argument("--max-price", type=int)
    parser.add_argument("--min-rooms", type=int)
    parser.add_argument("--page-size", type=int, default=30)
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--out", default="fotocasa.csv")
    args = parser.parse_args()

    if args.combined_locations:
        location = {"combinedLocations": args.combined_locations, "latitude": args.lat, "longitude": args.lon}
    elif args.place:
        location = search_params(find_location(args.place))
    else:
        parser.error("give a place name or --combined-locations with --lat and --lon")

    written, facets = 0, None
    with open(args.out, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for page in range(1, args.max_pages + 1):
            data = get(
                "/searchads",
                **location,
                transactionType=args.type,
                propertyType=args.property_type,
                sortType="LATEST",
                publicationDate="INDIFFERENT",
                minPrice=args.min_price,
                maxPrice=args.max_price,
                minRooms=args.min_rooms,
                pageNumber=page,
                size=args.page_size,
            )
            facets = facets or data.get("locationFacets")
            for ad in data["items"]:
                writer.writerow(flatten(ad))
                written += 1
            print(f"page {page}: {written} of {data['totalItems']:,} listings")
            if not data["items"] or written >= data["totalItems"]:
                break
    print(f"Wrote {written} rows to {args.out}\n")

    districts = sorted((facets or {}).get("districts") or [], key=lambda d: -d["counter"])
    if districts:
        print("Listings by district (from locationFacets):")
        for d in districts:
            print(f"  {d['counter']:>6,}  {d['literal']:<32} combinedLocations={d['combinedLocation']}")


if __name__ == "__main__":
    main()
