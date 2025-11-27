import requests
import json
import os
from bs4 import BeautifulSoup

DATA_DIR = "data/twitter"
MPS_FILE = "data/mps.json"

os.makedirs(DATA_DIR, exist_ok=True)


def extract_handle(twitter_url):
    """
    Convert full URL like https://twitter.com/DianeAbbottMP
    into 'DianeAbbottMP'
    """
    if not twitter_url:
        return None
    return twitter_url.rstrip("/").split("/")[-1]


def fetch_rss_for_handle(handle):
    """
    Uses Nitter RSS feed. If down, returns empty list.
    """
    rss_url = f"https://nitter.net/{handle}/rss"

    try:
        r = requests.get(rss_url, timeout=10)
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "xml")
        items = soup.find_all("item")

        tweets = []
        for item in items:
            text = item.description.text if item.description else ""
            pubdate = item.pubDate.text if item.pubDate else ""

            tweets.append({
                "text": text,
                "pub_date": pubdate,
                "like_count": 0,        # RSS does not include engagement
                "retweet_count": 0,
                "reply_count": 0,
                "age_minutes": 99999    # updated later in analytics
            })

        return tweets

    except Exception:
        return []


def main():
    with open(MPS_FILE, "r") as f:
        mps = json.load(f)

    for mp in mps:
        handle = mp.get("twitter_username")
        mp_id = str(mp["person_id"])

        if not handle:
            print(f"No Twitter for {mp['name']}")
            tweets = []
        else:
            print(f"Fetching tweets for {mp['name']} (@{handle})")
            tweets = fetch_rss_for_handle(handle)

        # save per MP
        out_path = os.path.join(DATA_DIR, f"{mp_id}.json")
        with open(out_path, "w") as f:
            json.dump(tweets, f, indent=2)

    print("Tweet fetching complete.")


if __name__ == "__main__":
    main()
