import requests, json, os, time, re

BASE = "https://members-api.parliament.uk/api/Members/Search"
CONTACT_BASE = "https://members-api.parliament.uk/api/Members/{id}/Contact"

def extract_handle(text):
    """Extract clean Twitter/X handle from any format."""
    if not text:
        return None

    text = text.strip()

    # @username
    if text.startswith("@"):
        return text[1:].lower()

    # Raw username with no URL
    if re.fullmatch(r"[A-Za-z0-9_]+", text):
        return text.lower()

    # URL formats
    match = re.search(r"(twitter\.com|x\.com)/([A-Za-z0-9_]+)", text)
    if match:
        return match.group(2).lower()

    return None


def fetch_mps():
    all_mps = []
    skip = 0
    take = 20

    while True:
        url = f"{BASE}?House=Commons&IsCurrentMember=true&skip={skip}&take={take}"
        print("Fetching:", url)

        try:
            data = requests.get(url).json()
        except:
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

            # Fetch contact info
            contact_url = CONTACT_BASE.format(id=mp_id)
            try:
                contact = requests.get(contact_url).json()
            except:
                contact = {}

            # Search all contact fields for any Twitter/X link
            for c in contact.get("value", []):
                notes = c.get("notes", "") or ""
                ctype = c.get("type", "").lower()

                # Detect via type
                if "twitter" in ctype or "x" in ctype:
                    twitter = extract_handle(notes)
                    if twitter:
                        break

                # Detect via content
                if "twitter.com" in notes or "x.com" in notes:
                    twitter = extract_handle(notes)
                    if twitter:
                        break

            # Skip MPs without X/Twitter accounts
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

    print(f"FOUND {len(all_mps)} MPs with Twitter/X accounts.")

    os.makedirs("data", exist_ok=True)
    with open("data/mps.json", "w") as f:
        json.dump(all_mps, f, indent=2)

    print("Saved data/mps.json")


if __name__ == "__main__":
    fetch_mps()
