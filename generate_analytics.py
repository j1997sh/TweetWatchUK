import json
import os
from datetime import datetime, timezone

DATA_DIR = "data"
TWITTER_DIR = os.path.join(DATA_DIR, "twitter")
ANALYTICS_DIR = os.path.join(DATA_DIR, "analytics")
MPS_FILE = os.path.join(DATA_DIR, "mps.json")
STATUS_FILE = "status.json"

os.makedirs(ANALYTICS_DIR, exist_ok=True)


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    print("Generating analytics...")

    mp_list = load_json(MPS_FILE)
    if not mp_list:
        print("ERROR: mps.json is empty or missing")
        return

    all_analytics = {}
    party_totals = {}

    for mp in mp_list:
        mp_id = str(mp["person_id"])
        party = mp["party"]
        twitter_file = os.path.join(TWITTER_DIR, f"{mp_id}.json")

        tweets = load_json(twitter_file) or []

        total_tweets = len(tweets)
        total_engagement = 0
        recent_engagement = 0

        for t in tweets:
            like = t.get("like_count", 0)
            rt = t.get("retweet_count", 0)
            reply = t.get("reply_count", 0)

            total_engagement += like + rt + reply

            # Rising/Falling scoreboard uses last 1 hour
            if t.get("age_minutes", 99999) <= 60:
                recent_engagement += like + rt + reply

        # Store analytics per MP
        all_analytics[mp_id] = {
            "mp_id": mp_id,
            "name": mp["name"],
            "party": party,
            "constituency": mp["constituency"],
            "tweets": total_tweets,
            "engagement": total_engagement,
            "engagement_last_hour": recent_engagement,
        }
        
        # Aggregate by party
        if party not in party_totals:
            party_totals[party] = {
                "party": party,
                "mps": 0,
                "total_tweets": 0,
                "total_engagement": 0,
                "avg_engagement_per_mp": 0,
            }

        party_totals[party]["mps"] += 1
        party_totals[party]["total_tweets"] += total_tweets
        party_totals[party]["total_engagement"] += total_engagement

    # Calculate averages
    for party, pdata in party_totals.items():
        mps = pdata["mps"]
        pdata["avg_engagement_per_mp"] = (
            pdata["total_engagement"] / mps if mps > 0 else 0
        )

    # Save per-MP analytics files
    for mp_id, data in all_analytics.items():
        save_json(os.path.join(ANALYTICS_DIR, f"{mp_id}.json"), data)

    # Save party-level summary file
    save_json(os.path.join(ANALYTICS_DIR, "party_summary.json"), party_totals)

    # Save system status (used for "Last updated X minutes ago")
    status = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat()
    }
    save_json(STATUS_FILE, status)

    print("Analytics complete.")


if __name__ == "__main__":
    main()
