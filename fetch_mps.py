import requests, json, os, time

BASE = "https://members-api.parliament.uk/api/Members/Search"
CONTACT_BASE = "https://members-api.parliament.uk/api/Members/{id}/Contact"

all_mps = []
skip = 0
take = 20

print("Fetching MP list...")

while True:
    url = f"{BASE}?House=Commons&IsCurrentMember=true&skip={skip}&take={take}"
    data = requests.get(url).json()

    items = data["items"]
    if not items:
        break

    for entry in items:
        v = entry["value"]

        mp_id = v["id"]
        name = v["nameDisplayAs"]
        party = v["latestParty"]["name"]
        constituency = v["latestHouseMembership"]["membershipFrom"]
        photo = v["thumbnailUrl"]

        # Default: no twitter
        twitter = None

        # Try to fetch contact info (may include twitter)
        contact_url = CONTACT_BASE.format(id=mp_id)
        contact = requests.get(contact_url).json()

        for c in contact.get("value", []):
            if c["type"] == "Twitter":
                twitter = c["notes"]
                break

        all_mps.append({
            "person_id": mp_id,
            "name": name,
            "party": party,
            "constituency": constituency,
            "thumbnail": photo,
            "twitter_username": twitter
        })

    skip += take
    time.sleep(0.2)  # polite delay

print(f"Downloaded {len(all_mps)} MPs.")

os.makedirs("data", exist_ok=True)

with open("data/mps.json", "w") as f:
    json.dump(all_mps, f, indent=2)

print("Saved data/mps.json")
