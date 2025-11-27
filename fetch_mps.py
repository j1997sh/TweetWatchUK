import requests, json, os, time

BASE = "https://members-api.parliament.uk/api/Members/Search"
CONTACT_BASE = "https://members-api.parliament.uk/api/Members/{id}/Contact"

all_mps = []
skip = 0
take = 20

def is_twitter_field(field_type: str):
    """Detect Twitter/X fields in many formats."""
    if not field_type:
        return False
    field_type = field_type.lower()
    return (
        "twitter" in field_type or
        field_type == "x" or
        "formerly twitter" in field_type
    )

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

        # Try latestTwitter (many MPs use this field now)
        twitter = v.get("latestTwitter")

        # If not found, look in contact details
        if not twitter:
            contact_url = CONTACT_BASE.format(id=mp_id)
            contact = requests.get(contact_url).json()

            for c in contact.get("value", []):
                ctype = c.get("type", "")
                if is_twitter_field(ctype):
                    twitter = c.get("notes")
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
    time.sleep(0.1)

print(f"Downloaded {len(all_mps)} MPs.")

os.makedirs("data", exist_ok=True)
with open("data/mps.json", "w") as f:
    json.dump(all_mps, f, indent=2)

print("Saved data/mps.json")
