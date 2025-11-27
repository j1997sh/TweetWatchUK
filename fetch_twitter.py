import json
import os
import aiohttp
import asyncio
import datetime

MPS_FILE = "data/mps.json"
OUT_DIR = "data/twitter"
os.makedirs(OUT_DIR, exist_ok=True)

API_TEMPLATE = "https://r.jina.ai/https://cdn.jina.ai/snscrape/twitter?handle={handle}&limit=1"

CONCURRENT_REQUESTS = 40  # speed vs rate limit
RECENT_THRESHOLD_HOURS = 48  # only save tweets newer than this


async def fetch_latest(session, mp):
    handle = mp.get("twitter_username")
    mp_id = str(mp["person_id"])

    if not handle:
        return mp_id, []

    url = API_TEMPLATE.format(handle=handle)

    try:
        async with session.get(url, timeout=10) as r:
            if r.status != 200:
                return mp_id, []

            data = await r.json()

            if not data:
                return mp_id, []

            tweet = data[0]

            # Check recency
            date_str = tweet.get("date")
            if date_str:
                dt = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                age_hours = (datetime.datetime.now(datetime.timezone.utc) - dt).total_seconds() / 3600

                # skip stale tweets
                if age_hours > RECENT_THRESHOLD_HOURS:
                    return mp_id, []

            cleaned = {
                "text": tweet.get("content", ""),
                "date": tweet.get("date", ""),
                "url": tweet.get("url", ""),
                "id": tweet.get("id", "")
            }
            return mp_id, [cleaned]

    except Exception:
        return mp_id, []


async def main():
    with open(MPS_FILE, "r") as f:
        mps = json.load(f)

    connector = aiohttp.TCPConnector(limit_per_host=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:

        tasks = [fetch_latest(session, mp) for mp in mps]
        results = await asyncio.gather(*tasks)

        for mp_id, tweets in results:
            with open(os.path.join(OUT_DIR, f"{mp_id}.json"), "w") as f:
                json.dump(tweets, f, indent=2)

    print("FAST SNScrape complete ✓")


if __name__ == "__main__":
    asyncio.run(main())
