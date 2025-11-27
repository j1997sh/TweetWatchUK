import requests, json, os, time

BASE = "https://members-api.parliament.uk/api/Members/Search"
CONTACT_BASE = "https://members-api.parliament.uk/api/Members/{id}/Contact"

def extract_handle(value: str):
    """Extract @handle from full X/Twitter URL."""
    if not value:
        return None
    value = value.strip()
    # e.g. https://twitter.com/Name  OR  https://x.com/Name
    if "twitter.com" in value or "x.com" in value:
        return value.rstrip("/").split("/")[-1]
    return value  # if it's already just a username

def is_twitter_field(field_type: str):
    """Detect Twitter/X labels."""
    if not field_type:
        return False
    field_type = field_type.lower()
    return (
        "twitter" in field_type or
        field_type == "x" or
        "formerly twitter" in field_type
    )

all_mps = []
skip = 0
take = 20

print("Fetching MPs...")

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

        twitter = None

        # 1. Try new "latestTwitter" field
        raw_twitter = v.get("latestTwitter")
        if raw_twitter:
            twitter = extract_handle(raw_twitter)

        # 2. Fallback to contact info
        if not twitter:
            contact_url = CONTACT_BASE.format(id=mp_id)
            contact = requests.get(contact_url).json()

            for c in contact.get("value", []):
                if is_twitter_field(c.get("type")):
                    twitter = extract_handle(c.get("notes"))
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
