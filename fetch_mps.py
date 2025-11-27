import requests, json, os, time, re

# API endpoints
BASE = "https://members-api.parliament.uk/api/Members/Search"
CONTACT_BASE = "https://members-api.parliament.uk/api/Members/{id}/Contact"

def extract_handle(url):
    """Extract @username from any X/Twitter URL format."""
    if not url:
        return None

    url = url.strip()

    # Case: "@username"
    if url.startswith("@"):
        return url[1:].lower()

    # Case: https://twitter.com/username
    match = re.search(r"(twitter\.com|x\.com)/([A-Za-z0-9_]+)", url)
    if match:
        return match.group(2).lower()

    return None


def fetch_mps():
    all_mps = []
    skip = 0
    take = 20

    print("Fetching MP list...")

    while True:
        url = f"{BASE}?House=Commons&IsCurrentMember=true&skip={skip}&take={take}"
        print("Fetching:", url)

        try:
            data = requests.get(url).json()
        except Exception as e:
            print(f"ERROR fetching page: {e}")
            break

        items = data.get("items", [])
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

            # Get contact details
            contact_url = CONTACT_BASE.format(id=mp_id)
            try:
                contact = requests.get(contact_url).json()
            except:
                contact = {}

            # Search all contact entries
            for c in contact.get("value", []):
                ctype = c.get("type", "").lower()

                # Parliament labels X as:
                # - "Twitter"
                # - "X (formerly Twitter)"
                if "twitter" in ctype or "x" in ctype:
                    notes = c.get("notes")
                    twitter = extract_handle(notes)
                    break

            # Skip MPs without X accounts
            if not twitter:
                continue

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

    print(f"Found {len(all_mps)} MPs with Twitter/X accounts.")

    # Save results
    os.makedirs("data", exist_ok=True)
    with open("data/mps.json", "w") as f:
        json.dump(all_mps, f, indent=2)

    print("Saved data/mps.json")


if __name__ == "__main__":
    fetch_mps()
