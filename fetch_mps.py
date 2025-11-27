import requests, json, os, time, re

BASE = "https://members-api.parliament.uk/api/Members/Search"
CONTACT_BASE = "https://members-api.parliament.uk/api/Members/{id}/Contact"

def extract_handle(text):
    """Extract @username from any format."""
    if not text:
        return None

    text = text.strip()

    # @username
    if text.startswith("@"):
        return text[1:].lower()

    # Raw username
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

    print("Fetching MPs...")

    while True:
        url = f"{BASE}?House=Commons&IsCurrentMember=true&skip={skip}&take={take}"
        print("Fetching:", url)
        data = requests.get(url).json()

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
            contact = requests.get(contact_url).json()

            for c in contact.get("value", []):
                ctype = c.get("type", "").lower()

                # Detect Twitter/X via type
                if "twitter" in ctype or "x" in ctype:

                    # Parliament now puts URL in `line1`
                    line1 = c.get("line1")
                    notes = c.get("notes")

                    twitter = extract_handle(line1) or extract_handle(notes)

                    if twitter:
                        break

                # Also detect inside URLs (fallback)
                line1 = c.get("line1", "")
                notes = c.get("notes", "")

                if "twitter.com" in str(line1) or "x.com" in str(line1):
                    twitter = extract_handle(line1)
                    if twitter:
                        break

                if "twitter.com" in str(notes) or "x.com" in str(notes):
                    twitter = extract_handle(notes)
                    if twitter:
                        break

            if not twitter:
                continue  # skip MPs with no Twitter/X account

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
