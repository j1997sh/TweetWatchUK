import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

def extract_handle(url):
    """Extract the handle from a Twitter/X URL."""
    if not url:
        return None
    url = url.strip()
    if "twitter.com" in url or "x.com" in url:
        return url.rstrip("/").split("/")[-1]
    return None

def build_twf_url(mp_name, constituency):
    """Build a TheyWorkForYou URL using name + constituency."""
    # convert "Shabana Mahmood" -> "shabana_mahmood"
    name_slug = mp_name.lower().replace(" ", "_")

    # convert "Ladywood" -> "ladywood"
    const_slug = constituency.lower().replace(" ", "_")

    return f"https://www.theyworkforyou.com/mp/?pid={name_slug}_{const_slug}"

def fallback_search(name):
    """Fallback: search MPs by name."""
    q = name.lower().replace(" ", "+")
    return f"https://www.theyworkforyou.com/search/?s={q}"

os.makedirs("data", exist_ok=True)

# Load the existing MP list
with open("data/mps.json") as f:
    mps = json.load(f)

updated = 0

for mp in mps:
    if mp.get("twitter_username"):
        continue  # already found

    name = mp["name"]
    constituency = mp["constituency"]

    # Build TheyWorkForYou MP page URL
    search_url = fallback_search(name)
    print(f"Searching for: {name}")

    try:
        html = requests.get(search_url, timeout=10).text
    except:
        continue

    soup = BeautifulSoup(html, "html.parser")

    # Find the first MP link with /mp/
    mp_link = None
    for a in soup.find_all("a", href=True):
        if "/mp/" in a["href"]:
            mp_link = "https://www.theyworkforyou.com" + a["href"]
            break

    if not mp_link:
        print(f"Could not find MP page for {name}")
        continue

    print(f"MP page: {mp_link}")

    try:
        html = requests.get(mp_link, timeout=10).text
    except:
        continue

    soup = BeautifulSoup(html, "html.parser")

    # Look for Twitter / X links
    twitter_url = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "twitter.com/" in href or "x.com/" in href:
            twitter_url = href
            break

    if twitter_url:
        handle = extract_handle(twitter_url)
        if handle:
            mp["twitter_username"] = handle
            updated += 1
            print(f"Found Twitter: @{handle}")
    else:
        print(f"No Twitter found for {name}")

    time.sleep(0.5)  # polite delay

# Write updated data
with open("data/mps.json", "w") as f:
    json.dump(mps, f, indent=2)

print(f"Done. Updated {updated} Twitter handles.")
